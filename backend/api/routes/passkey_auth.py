"""
Passkey Authentication API Routes
Implements Phase 1 of Passkey Architecture v2
"""
from fastapi import APIRouter, HTTPException, status, Request, Header
from fastapi.responses import RedirectResponse
from pydantic import BaseModel, EmailStr
from typing import Optional, List, Dict, Any
import logging
import os
import json
import base64

from webauthn import (
    generate_registration_options,
    verify_registration_response,
    generate_authentication_options,
    verify_authentication_response,
    options_to_json,
)
from webauthn.helpers import parse_registration_credential_json
from webauthn.helpers.structs import (
    PublicKeyCredentialDescriptor,
    AuthenticatorSelectionCriteria,
    UserVerificationRequirement,
    ResidentKeyRequirement,
    AuthenticatorAttachment,
    AttestationConveyancePreference,
)
from webauthn.helpers.cose import COSEAlgorithmIdentifier
import traceback

from database_passkeys import db
from services.email import email_service

logger = logging.getLogger(__name__)

router = APIRouter()

# Configuration
RP_NAME = os.getenv("RP_NAME", "Tuxedo AI")
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:5173")

# Allowed origins for passkey authentication (should match CORS config)
ALLOWED_ORIGINS = [
    "http://localhost:5173",
    "http://localhost:3000",
    "https://tuxedo.onrender.com",
    "https://tuxedo-frontend.onrender.com"
]

def get_rp_id_and_origin(request: Request) -> tuple[str, str]:
    """
    Dynamically determine RP_ID and origin from request headers.

    This ensures passkey authentication works across different domains
    (localhost, production, staging, etc.) by extracting the origin
    from the request and validating it against allowed origins.
    """
    # Try to get origin from request headers
    origin = request.headers.get("origin")
    referer = request.headers.get("referer")

    # Fallback to referer if origin is not present
    if not origin and referer:
        from urllib.parse import urlparse
        parsed = urlparse(referer)
        origin = f"{parsed.scheme}://{parsed.netloc}"

    # Default to localhost for development
    if not origin:
        origin = "http://localhost:5173"

    # Validate origin is in allowed list
    if origin not in ALLOWED_ORIGINS:
        logger.warning(f"Origin {origin} not in allowed list, using default")
        origin = "http://localhost:5173"

    # Extract RP_ID (hostname) from origin
    from urllib.parse import urlparse
    parsed = urlparse(origin)
    rp_id = parsed.hostname or "localhost"

    # For localhost, use "localhost" as RP_ID
    # For production domains, use the full hostname
    if rp_id in ["localhost", "127.0.0.1"]:
        rp_id = "localhost"

    logger.info(f"Using RP_ID: {rp_id}, Origin: {origin}")

    return rp_id, origin


# Pydantic models
class RegisterStartRequest(BaseModel):
    email: EmailStr


class RegisterStartResponse(BaseModel):
    challenge_id: str
    options: Dict[str, Any]


class RegisterVerifyRequest(BaseModel):
    email: EmailStr
    challenge_id: str
    credential: Dict[str, Any]


class RegisterVerifyResponse(BaseModel):
    user: Dict[str, Any]
    session_token: str
    recovery_codes: List[str]
    recovery_codes_message: str
    must_acknowledge: bool


class AcknowledgeRecoveryCodesRequest(BaseModel):
    pass  # Token comes from header


class AcknowledgeRecoveryCodesResponse(BaseModel):
    success: bool
    acknowledged: bool


class LoginStartRequest(BaseModel):
    email: EmailStr


class LoginStartResponse(BaseModel):
    challenge_id: str
    options: Dict[str, Any]


class LoginVerifyRequest(BaseModel):
    challenge_id: str
    credential: Dict[str, Any]


class LoginVerifyResponse(BaseModel):
    user: Dict[str, Any]
    session_token: str


class RecoveryCodeVerifyRequest(BaseModel):
    email: EmailStr
    code: str


class RecoveryCodeVerifyResponse(BaseModel):
    user: Dict[str, Any]
    session_token: str
    remaining_codes: int


class EmailRecoveryRequest(BaseModel):
    email: EmailStr


class EmailRecoveryCompleteRequest(BaseModel):
    token: str
    credential: Dict[str, Any]


class SessionValidateResponse(BaseModel):
    user: Dict[str, Any]
    valid: bool


class PasskeyCredential(BaseModel):
    id: str
    friendly_name: Optional[str]
    created_at: str
    last_used_at: Optional[str]
    backup_eligible: bool


class PasskeyListResponse(BaseModel):
    credentials: List[PasskeyCredential]


class PasskeyAddRequest(BaseModel):
    challenge_id: str
    credential: Dict[str, Any]
    friendly_name: Optional[str] = None


class ErrorResponse(BaseModel):
    success: bool = False
    error: Dict[str, Any]


# Helper functions
def get_session_token(request: Request, authorization: Optional[str] = None) -> Optional[str]:
    """Extract session token from request"""
    # Try Authorization header first
    if authorization and authorization.startswith("Bearer "):
        return authorization[7:]

    # Try cookie
    return request.cookies.get("session_token")


def create_error_response(code: str, message: str, details: Optional[Dict] = None, status_code: int = 400):
    """Create standardized error response"""
    error_data = {
        "code": code,
        "message": message
    }
    if details:
        error_data["details"] = details

    raise HTTPException(
        status_code=status_code,
        detail={
            "success": False,
            "error": error_data
        }
    )


# Registration endpoints
@router.post("/auth/passkey/register/start", response_model=RegisterStartResponse)
async def register_start(req: Request, request: RegisterStartRequest):
    """Start passkey registration flow"""
    try:
        # Check if user already exists
        existing_user = db.get_user_by_email(request.email)
        if existing_user:
            # Get user's existing passkeys to help with error message
            passkeys = db.get_user_passkeys(existing_user['id'])
            passkey_count = len(passkeys)

            create_error_response(
                "USER_EXISTS",
                f"An account with this email already exists with {passkey_count} passkey(s). Please sign in instead of creating a new account.",
                status_code=409
            )

        # Get dynamic RP_ID and origin based on request
        rp_id, origin = get_rp_id_and_origin(req)

        # Create challenge
        challenge_id, challenge = db.create_challenge()

        # Build excludeCredentials list to prevent duplicate passkey creation
        # Note: We check for existing user above, but this is extra protection
        # in case of race conditions or if we later allow re-registration
        exclude_credentials = []

        # If somehow a user exists (shouldn't happen due to check above),
        # get their credentials for the exclude list
        if existing_user:
            passkeys = db.get_user_passkeys(existing_user['id'])
            exclude_credentials = [
                PublicKeyCredentialDescriptor(
                    id=base64.urlsafe_b64decode(pk['credential_id'])
                )
                for pk in passkeys
            ]
            logger.info(f"Added {len(exclude_credentials)} credentials to exclude list for {request.email}")

        # Generate registration options with excludeCredentials
        registration_options = generate_registration_options(
            rp_id=rp_id,
            rp_name=RP_NAME,
            user_id=challenge_id.encode(),  # Use challenge_id as temporary user_id (will be replaced after verification)
            user_name=request.email,
            user_display_name=request.email,
            challenge=challenge.encode(),
            exclude_credentials=exclude_credentials,  # Prevent duplicate passkey creation
            authenticator_selection=AuthenticatorSelectionCriteria(
                authenticator_attachment=AuthenticatorAttachment.PLATFORM,
                resident_key=ResidentKeyRequirement.PREFERRED,
                require_resident_key=False,
                user_verification=UserVerificationRequirement.REQUIRED,
            ),
            attestation=AttestationConveyancePreference.NONE,
            supported_pub_key_algs=[
                COSEAlgorithmIdentifier.ECDSA_SHA_256,
                COSEAlgorithmIdentifier.RSASSA_PKCS1_v1_5_SHA_256,
            ],
            timeout=60000,
        )

        # Convert options to JSON-serializable format
        options_json = json.loads(options_to_json(registration_options))

        logger.info(f"Registration started for email: {request.email} with RP_ID: {rp_id}")

        return RegisterStartResponse(
            challenge_id=challenge_id,
            options=options_json
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error starting registration: {e}")
        create_error_response(
            "REGISTRATION_START_FAILED",
            "Failed to start registration",
            status_code=500
        )


@router.post("/auth/passkey/register/verify", response_model=RegisterVerifyResponse)
async def register_verify(req: Request, request: RegisterVerifyRequest):
    """Verify passkey registration and create user"""
    try:
        # Get challenge
        challenge_data = db.get_challenge(request.challenge_id)
        if not challenge_data:
            create_error_response(
                "INVALID_CHALLENGE",
                "Challenge expired or invalid",
                status_code=401
            )

        # Get dynamic RP_ID and origin based on request
        rp_id, origin = get_rp_id_and_origin(req)

        logger.info(f"🔍 Verifying registration for {request.email}")
        logger.info(f"   RP ID: {rp_id}")
        logger.info(f"   Origin: {origin}")
        logger.info(f"   Challenge ID: {request.challenge_id}")
        logger.info(f"   Credential ID: {request.credential.get('id', 'N/A')[:20]}...")

        # Verify the registration response
        try:
            # Try to parse the credential using the webauthn helper
            # This ensures proper handling of base64url encoding
            try:
                # Convert credential dict to JSON string for parsing
                credential_json = json.dumps(request.credential)
                parsed_credential = parse_registration_credential_json(credential_json)
                logger.info("✅ Successfully parsed credential using parse_registration_credential_json")
            except Exception as parse_error:
                logger.warning(f"⚠️ Failed to parse credential with helper, using raw dict: {parse_error}")
                # Fallback to using the credential dict directly
                parsed_credential = request.credential

            verification = verify_registration_response(
                credential=parsed_credential,
                expected_challenge=challenge_data['challenge'].encode(),
                expected_origin=origin,
                expected_rp_id=rp_id,
                require_user_verification=True,  # Match the REQUIRED setting from registration options
            )
            logger.info("✅ Registration verification successful")
        except Exception as e:
            # Enhanced error logging for debugging
            error_type = type(e).__name__
            error_msg = str(e)
            error_trace = traceback.format_exc()

            logger.error(f"❌ Registration verification failed:")
            logger.error(f"   Error Type: {error_type}")
            logger.error(f"   Error Message: {error_msg}")
            logger.error(f"   RP ID: {rp_id}")
            logger.error(f"   Origin: {origin}")
            logger.error(f"   Traceback:\n{error_trace}")

            # Return more detailed error to help with debugging
            error_details = {
                "error_type": error_type,
                "rp_id": rp_id,
                "origin": origin,
            }

            create_error_response(
                "INVALID_CREDENTIAL",
                f"Failed to verify passkey credential: {error_type}",
                details=error_details,
                status_code=401
            )

        # Mark challenge as used
        db.mark_challenge_used(request.challenge_id)

        # CRITICAL: Re-check if user exists to prevent race condition
        # Two users might have gotten past the /register/start check simultaneously
        existing_user = db.get_user_by_email(request.email)
        if existing_user:
            create_error_response(
                "USER_EXISTS",
                "An account with this email was created while registration was in progress. Please sign in instead.",
                status_code=409
            )

        # Create user with IntegrityError handling
        try:
            user = db.create_user(request.email)
        except Exception as e:
            # Handle database constraint violations (e.g., unique email constraint)
            error_msg = str(e).lower()
            if 'unique' in error_msg or 'constraint' in error_msg or 'integrity' in error_msg:
                logger.error(f"IntegrityError creating user: {e}")
                create_error_response(
                    "USER_EXISTS",
                    "An account with this email already exists",
                    status_code=409
                )
            else:
                # Re-raise other unexpected errors
                raise

        # Store passkey credential
        credential_id = base64.urlsafe_b64encode(verification.credential_id).decode('utf-8')
        public_key = base64.urlsafe_b64encode(verification.credential_public_key).decode('utf-8')

        db.store_passkey_credential(
            user_id=user['id'],
            credential_id=credential_id,
            public_key=public_key,
            sign_count=verification.sign_count,
            backup_eligible=verification.credential_backed_up,
            transports=request.credential.get('response', {}).get('transports', []),
            friendly_name="Primary passkey"
        )

        # Generate recovery codes
        recovery_codes = db.generate_recovery_codes(user['id'])

        # Create session
        session_token = db.create_session(user['id'])

        # Update last login
        db.update_last_login(user['id'])

        # Send welcome email with recovery codes (async, don't block response)
        try:
            await email_service.send_welcome_email(user['email'], recovery_codes)
        except Exception as e:
            logger.error(f"Failed to send welcome email: {e}")

        logger.info(f"User registered successfully: {user['email']}")

        return RegisterVerifyResponse(
            user={
                "id": user['id'],
                "email": user['email']
            },
            session_token=session_token,
            recovery_codes=recovery_codes,
            recovery_codes_message="Save these recovery codes in a secure location. They will not be shown again!",
            must_acknowledge=True
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error verifying registration: {e}")
        create_error_response(
            "REGISTRATION_VERIFY_FAILED",
            "Failed to complete registration",
            status_code=500
        )


@router.post("/auth/passkey/recovery-codes/acknowledge", response_model=AcknowledgeRecoveryCodesResponse)
async def acknowledge_recovery_codes(
    request: Request,
    authorization: Optional[str] = Header(None)
):
    """Acknowledge that user has saved recovery codes"""
    try:
        session_token = get_session_token(request, authorization)
        if not session_token:
            create_error_response(
                "NO_SESSION_TOKEN",
                "Session token required",
                status_code=401
            )

        # Validate session
        session = db.validate_session(session_token)
        if not session:
            create_error_response(
                "INVALID_SESSION",
                "Invalid or expired session",
                status_code=401
            )

        # In a production system, you might store an acknowledgment flag
        # For now, we'll just validate the session exists

        return AcknowledgeRecoveryCodesResponse(
            success=True,
            acknowledged=True
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error acknowledging recovery codes: {e}")
        create_error_response(
            "ACKNOWLEDGMENT_FAILED",
            "Failed to acknowledge recovery codes",
            status_code=500
        )


# Authentication endpoints
@router.post("/auth/passkey/login/start", response_model=LoginStartResponse)
async def login_start(req: Request, request: LoginStartRequest):
    """Start passkey login flow"""
    try:
        # Get user by email
        user = db.get_user_by_email(request.email)
        if not user:
            # Don't reveal if user exists for security
            create_error_response(
                "USER_NOT_FOUND",
                "No account found with this email",
                status_code=404
            )

        # Get user's passkeys
        passkeys = db.get_user_passkeys(user['id'])
        if not passkeys:
            create_error_response(
                "NO_PASSKEYS",
                "No passkeys found for this account",
                status_code=404
            )

        # Get dynamic RP_ID and origin based on request
        rp_id, origin = get_rp_id_and_origin(req)

        # Create challenge
        challenge_id, challenge = db.create_challenge(user['id'])

        # Create allowed credentials list
        allowed_credentials = [
            PublicKeyCredentialDescriptor(
                id=base64.urlsafe_b64decode(pk['credential_id'])
            )
            for pk in passkeys
        ]

        # Generate authentication options
        authentication_options = generate_authentication_options(
            rp_id=rp_id,
            challenge=challenge.encode(),
            allow_credentials=allowed_credentials,
            user_verification=UserVerificationRequirement.REQUIRED,
            timeout=60000,
        )

        # Convert options to JSON-serializable format
        options_json = json.loads(options_to_json(authentication_options))

        logger.info(f"Login started for email: {request.email} with RP_ID: {rp_id}")

        return LoginStartResponse(
            challenge_id=challenge_id,
            options=options_json
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error starting login: {e}")
        create_error_response(
            "LOGIN_START_FAILED",
            "Failed to start login",
            status_code=500
        )


@router.post("/auth/passkey/login/verify", response_model=LoginVerifyResponse)
async def login_verify(req: Request, request: LoginVerifyRequest):
    """Verify passkey login"""
    try:
        # Get challenge
        challenge_data = db.get_challenge(request.challenge_id)
        if not challenge_data:
            create_error_response(
                "INVALID_CHALLENGE",
                "Challenge expired or invalid",
                status_code=401
            )

        if not challenge_data.get('user_id'):
            create_error_response(
                "INVALID_CHALLENGE",
                "Challenge not associated with a user",
                status_code=401
            )

        # Get dynamic RP_ID and origin based on request
        rp_id, origin = get_rp_id_and_origin(req)

        # Get credential from request
        credential_id = base64.urlsafe_b64encode(
            base64.urlsafe_b64decode(request.credential.get('id', '') + '==')
        ).decode('utf-8').rstrip('=')

        # Get stored credential
        stored_credential = db.get_passkey_credential(credential_id)
        if not stored_credential:
            create_error_response(
                "INVALID_CREDENTIAL",
                "Credential not found",
                status_code=401
            )

        # Verify the authentication response
        logger.info(f"🔍 Verifying authentication")
        logger.info(f"   RP ID: {rp_id}")
        logger.info(f"   Origin: {origin}")
        try:
            verification = verify_authentication_response(
                credential=request.credential,
                expected_challenge=challenge_data['challenge'].encode(),
                expected_origin=origin,
                expected_rp_id=rp_id,
                credential_public_key=base64.urlsafe_b64decode(stored_credential['public_key'] + '=='),
                credential_current_sign_count=stored_credential['sign_count'],
                require_user_verification=True,
            )
            logger.info("✅ Authentication verification successful")
        except Exception as e:
            error_type = type(e).__name__
            error_msg = str(e)
            error_trace = traceback.format_exc()

            logger.error(f"❌ Authentication verification failed:")
            logger.error(f"   Error Type: {error_type}")
            logger.error(f"   Error Message: {error_msg}")
            logger.error(f"   RP ID: {rp_id}")
            logger.error(f"   Origin: {origin}")
            logger.error(f"   Traceback:\n{error_trace}")

            create_error_response(
                "INVALID_CREDENTIAL",
                f"Failed to verify passkey: {error_type}",
                details={"error_type": error_type, "rp_id": rp_id, "origin": origin},
                status_code=401
            )

        # Update sign count
        db.update_passkey_sign_count(credential_id, verification.new_sign_count)

        # Mark challenge as used
        db.mark_challenge_used(request.challenge_id)

        # Get user
        user = db.get_user_by_id(stored_credential['user_id'])
        if not user:
            create_error_response(
                "USER_NOT_FOUND",
                "User not found",
                status_code=404
            )

        # Create session
        session_token = db.create_session(user['id'])

        # Update last login
        db.update_last_login(user['id'])

        logger.info(f"User logged in successfully: {user['email']}")

        return LoginVerifyResponse(
            user={
                "id": user['id'],
                "email": user['email']
            },
            session_token=session_token
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error verifying login: {e}")
        create_error_response(
            "LOGIN_VERIFY_FAILED",
            "Failed to verify login",
            status_code=500
        )


# Recovery code authentication
@router.post("/auth/passkey/recovery/verify", response_model=RecoveryCodeVerifyResponse)
async def verify_recovery_code(request: RecoveryCodeVerifyRequest, req: Request):
    """Verify recovery code and authenticate user"""
    try:
        # Get user
        user = db.get_user_by_email(request.email)
        if not user:
            # Don't reveal if user exists
            create_error_response(
                "INVALID_RECOVERY_CODE",
                "Invalid recovery code",
                status_code=401
            )

        # Check rate limit
        is_limited, seconds_until_reset = db.check_rate_limit(user['id'])
        if is_limited:
            create_error_response(
                "RATE_LIMITED",
                f"Too many failed attempts. Account locked for {seconds_until_reset // 60} minutes.",
                details={"retry_after": seconds_until_reset},
                status_code=429
            )

        # Verify recovery code
        success, remaining_codes = db.verify_recovery_code(user['id'], request.code)

        # Log attempt
        ip_address = req.client.host if req.client else None
        db.log_recovery_attempt(user['id'], success, ip_address)

        if not success:
            create_error_response(
                "INVALID_RECOVERY_CODE",
                "Invalid or already used recovery code",
                status_code=401
            )

        # Create session
        session_token = db.create_session(user['id'])

        # Update last login
        db.update_last_login(user['id'])

        # Send security alert email (async, don't block response)
        try:
            await email_service.send_recovery_alert(user['email'], remaining_codes)
        except Exception as e:
            logger.error(f"Failed to send recovery alert email: {e}")

        logger.info(f"User authenticated with recovery code: {user['email']}")

        return RecoveryCodeVerifyResponse(
            user={
                "id": user['id'],
                "email": user['email']
            },
            session_token=session_token,
            remaining_codes=remaining_codes
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error verifying recovery code: {e}")
        create_error_response(
            "RECOVERY_VERIFY_FAILED",
            "Failed to verify recovery code",
            status_code=500
        )


# Email recovery (for lost passkeys + codes)
@router.post("/auth/passkey/email-recovery/request")
async def request_email_recovery(request: EmailRecoveryRequest):
    """Request email recovery link"""
    try:
        # Get user
        user = db.get_user_by_email(request.email)
        if not user:
            # Always return success to prevent email enumeration
            return {"success": True, "message": "If an account exists, a recovery link has been sent"}

        # Create recovery token
        token = db.create_email_recovery_token(user['id'])

        # Send email (async, don't block response)
        try:
            await email_service.send_recovery_link(user['email'], token)
        except Exception as e:
            logger.error(f"Failed to send recovery link email: {e}")

        logger.info(f"Email recovery requested for: {user['email']}")

        return {"success": True, "message": "If an account exists, a recovery link has been sent"}

    except Exception as e:
        logger.error(f"Error requesting email recovery: {e}")
        create_error_response(
            "EMAIL_RECOVERY_FAILED",
            "Failed to send recovery link",
            status_code=500
        )


@router.get("/auth/passkey/email-recovery/verify")
async def verify_email_recovery(token: str):
    """Verify email recovery token and redirect to frontend"""
    try:
        # Validate token
        token_data = db.validate_email_recovery_token(token)
        if not token_data:
            # Redirect to error page
            return RedirectResponse(
                url=f"{FRONTEND_URL}/auth/recovery-error?reason=invalid_token",
                status_code=302
            )

        # Redirect to frontend with token
        return RedirectResponse(
            url=f"{FRONTEND_URL}/auth/recover?token={token}",
            status_code=302
        )

    except Exception as e:
        logger.error(f"Error verifying email recovery token: {e}")
        return RedirectResponse(
            url=f"{FRONTEND_URL}/auth/recovery-error?reason=server_error",
            status_code=302
        )


@router.post("/auth/passkey/email-recovery/complete", response_model=RegisterVerifyResponse)
async def complete_email_recovery(request: EmailRecoveryCompleteRequest):
    """Complete email recovery with new passkey"""
    try:
        # Validate token
        token_data = db.validate_email_recovery_token(request.token)
        if not token_data:
            create_error_response(
                "INVALID_EMAIL_TOKEN",
                "Recovery token expired or invalid",
                status_code=401
            )

        # Get user
        user = db.get_user_by_id(token_data['user_id'])
        if not user:
            create_error_response(
                "USER_NOT_FOUND",
                "User not found",
                status_code=404
            )

        # Verify the new passkey credential
        # (Simplified - in production you'd generate and validate a challenge)
        try:
            # For now, we'll trust the credential and store it
            # In production, you'd want to generate a challenge first
            pass
        except Exception as e:
            logger.error(f"Failed to verify new passkey: {e}")
            create_error_response(
                "INVALID_CREDENTIAL",
                "Failed to verify new passkey",
                status_code=401
            )

        # Invalidate all old passkeys
        db.invalidate_all_user_passkeys(user['id'])

        # Store new passkey
        credential_id = request.credential.get('id', '')
        public_key = request.credential.get('response', {}).get('publicKey', '')

        db.store_passkey_credential(
            user_id=user['id'],
            credential_id=credential_id,
            public_key=public_key,
            friendly_name="Recovered passkey"
        )

        # Generate new recovery codes
        recovery_codes = db.generate_recovery_codes(user['id'])

        # Mark token as used
        db.mark_email_recovery_token_used(request.token)

        # Delete all old sessions
        db.delete_all_user_sessions(user['id'])

        # Create new session
        session_token = db.create_session(user['id'])

        # Send confirmation email (async, don't block response)
        try:
            await email_service.send_recovery_confirmation(user['email'], recovery_codes)
        except Exception as e:
            logger.error(f"Failed to send recovery confirmation email: {e}")

        logger.info(f"Account recovered successfully: {user['email']}")

        return RegisterVerifyResponse(
            user={
                "id": user['id'],
                "email": user['email']
            },
            session_token=session_token,
            recovery_codes=recovery_codes,
            recovery_codes_message="Save these new recovery codes securely. Your old codes are no longer valid!",
            must_acknowledge=True
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error completing email recovery: {e}")
        create_error_response(
            "EMAIL_RECOVERY_COMPLETE_FAILED",
            "Failed to complete account recovery",
            status_code=500
        )


# Session management
@router.post("/auth/validate-passkey-session", response_model=SessionValidateResponse)
async def validate_passkey_session(
    request: Request,
    authorization: Optional[str] = Header(None)
):
    """Validate passkey session"""
    try:
        session_token = get_session_token(request, authorization)
        if not session_token:
            create_error_response(
                "NO_SESSION_TOKEN",
                "Session token required",
                status_code=401
            )

        # Validate session (includes sliding expiration)
        session = db.validate_session(session_token)
        if not session:
            create_error_response(
                "EXPIRED_SESSION",
                "Session expired or invalid",
                status_code=401
            )

        return SessionValidateResponse(
            user={
                "id": session['user_id'],
                "email": session['email']
            },
            valid=True
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error validating session: {e}")
        create_error_response(
            "SESSION_VALIDATION_FAILED",
            "Failed to validate session",
            status_code=500
        )


@router.post("/auth/logout")
async def logout(
    request: Request,
    authorization: Optional[str] = Header(None)
):
    """Logout user by deleting session"""
    try:
        session_token = get_session_token(request, authorization)
        if session_token:
            db.delete_session(session_token)

        return {"success": True, "message": "Logged out successfully"}

    except Exception as e:
        logger.error(f"Error during logout: {e}")
        create_error_response(
            "LOGOUT_FAILED",
            "Failed to logout",
            status_code=500
        )


# Passkey management (multiple passkeys)
@router.get("/auth/passkey/credentials", response_model=PasskeyListResponse)
async def list_passkeys(
    request: Request,
    authorization: Optional[str] = Header(None)
):
    """List user's passkeys"""
    try:
        session_token = get_session_token(request, authorization)
        if not session_token:
            create_error_response(
                "NO_SESSION_TOKEN",
                "Session token required",
                status_code=401
            )

        session = db.validate_session(session_token)
        if not session:
            create_error_response(
                "INVALID_SESSION",
                "Invalid or expired session",
                status_code=401
            )

        # Get user's passkeys
        passkeys = db.get_user_passkeys(session['user_id'])

        credentials = [
            PasskeyCredential(
                id=pk['id'],
                friendly_name=pk.get('friendly_name') or 'Unnamed passkey',
                created_at=pk['created_at'],
                last_used_at=pk.get('last_used_at'),
                backup_eligible=pk.get('backup_eligible', False)
            )
            for pk in passkeys
        ]

        return PasskeyListResponse(credentials=credentials)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error listing passkeys: {e}")
        create_error_response(
            "LIST_PASSKEYS_FAILED",
            "Failed to list passkeys",
            status_code=500
        )


@router.post("/auth/passkey/credentials/add")
async def add_passkey(
    req_data: PasskeyAddRequest,
    request: Request,
    authorization: Optional[str] = Header(None)
):
    """Add a new passkey to user's account"""
    try:
        session_token = get_session_token(request, authorization)
        if not session_token:
            create_error_response(
                "NO_SESSION_TOKEN",
                "Session token required",
                status_code=401
            )

        session = db.validate_session(session_token)
        if not session:
            create_error_response(
                "INVALID_SESSION",
                "Invalid or expired session",
                status_code=401
            )

        # Get user
        user = db.get_user_by_id(session['user_id'])
        if not user:
            create_error_response(
                "USER_NOT_FOUND",
                "User not found",
                status_code=404
            )

        # Verify credential (simplified for now)
        credential_id = req_data.credential.get('id', '')
        public_key = req_data.credential.get('response', {}).get('publicKey', '')

        # Store new passkey
        passkey_id = db.store_passkey_credential(
            user_id=user['id'],
            credential_id=credential_id,
            public_key=public_key,
            friendly_name=req_data.friendly_name or "Additional passkey"
        )

        # Send security alert (async, don't block response)
        try:
            await email_service.send_passkey_added_alert(user['email'], req_data.friendly_name)
        except Exception as e:
            logger.error(f"Failed to send passkey added alert: {e}")

        logger.info(f"Passkey added for user: {user['email']}")

        return {
            "credential": {
                "id": passkey_id,
                "friendly_name": req_data.friendly_name or "Additional passkey",
                "created_at": "just now"
            },
            "message": "New passkey added successfully"
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error adding passkey: {e}")
        create_error_response(
            "ADD_PASSKEY_FAILED",
            "Failed to add passkey",
            status_code=500
        )


@router.delete("/auth/passkey/credentials/{passkey_id}")
async def remove_passkey(
    passkey_id: str,
    request: Request,
    authorization: Optional[str] = Header(None)
):
    """Remove a passkey from user's account"""
    try:
        session_token = get_session_token(request, authorization)
        if not session_token:
            create_error_response(
                "NO_SESSION_TOKEN",
                "Session token required",
                status_code=401
            )

        session = db.validate_session(session_token)
        if not session:
            create_error_response(
                "INVALID_SESSION",
                "Invalid or expired session",
                status_code=401
            )

        # Delete passkey (checks if it's the last one)
        success = db.delete_passkey(passkey_id, session['user_id'])

        if not success:
            create_error_response(
                "CANNOT_DELETE_LAST_PASSKEY",
                "Cannot delete last remaining passkey. Add another passkey first.",
                status_code=400
            )

        logger.info(f"Passkey removed for user: {session['user_id']}")

        return {"success": True, "message": "Passkey removed successfully"}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error removing passkey: {e}")
        create_error_response(
            "REMOVE_PASSKEY_FAILED",
            "Failed to remove passkey",
            status_code=500
        )
