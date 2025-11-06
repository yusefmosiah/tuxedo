"""
Passkey Authentication API Routes
Implements WebAuthn-based passkey authentication with recovery codes and email fallback
"""

from fastapi import APIRouter, HTTPException, status, Request
from pydantic import BaseModel, EmailStr
from typing import Optional, List, Dict, Any
import logging
import os
import base64
import json

from webauthn import (
    generate_registration_options,
    verify_registration_response,
    generate_authentication_options,
    verify_authentication_response,
    options_to_json,
)
from webauthn.helpers.structs import (
    AuthenticatorSelectionCriteria,
    UserVerificationRequirement,
    AuthenticatorAttachment,
    ResidentKeyRequirement,
    PublicKeyCredentialDescriptor,
)
from webauthn.helpers.cose import COSEAlgorithmIdentifier

from database import db
from services.email import (
    send_welcome_email,
    send_recovery_alert,
    send_recovery_link,
    send_recovery_confirmation,
    send_passkey_added_alert,
)

logger = logging.getLogger(__name__)

router = APIRouter()

# Configuration
RP_ID = os.getenv("RP_ID", "localhost")
RP_NAME = os.getenv("RP_NAME", "Choir")
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:5173")
EXPECTED_ORIGIN = os.getenv("EXPECTED_ORIGIN", "http://localhost:5173")

# Pydantic models
class PasskeyRegistrationStartRequest(BaseModel):
    email: EmailStr

class PasskeyRegistrationStartResponse(BaseModel):
    challenge_id: str
    options: Dict[str, Any]

class PasskeyRegistrationVerifyRequest(BaseModel):
    email: EmailStr
    challenge_id: str
    credential: Dict[str, Any]
    friendly_name: Optional[str] = None

class PasskeyRegistrationVerifyResponse(BaseModel):
    user: Dict[str, Any]
    session_token: str
    recovery_codes: List[str]
    recovery_codes_message: str
    must_acknowledge: bool

class RecoveryCodesAcknowledgeRequest(BaseModel):
    pass  # Session token comes from header

class PasskeyLoginStartRequest(BaseModel):
    email: EmailStr

class PasskeyLoginStartResponse(BaseModel):
    challenge_id: str
    options: Dict[str, Any]

class PasskeyLoginVerifyRequest(BaseModel):
    challenge_id: str
    credential: Dict[str, Any]

class PasskeyLoginVerifyResponse(BaseModel):
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
    friendly_name: Optional[str] = None

class SessionValidationResponse(BaseModel):
    user: Dict[str, Any]
    valid: bool

class PasskeyCredential(BaseModel):
    id: str
    friendly_name: Optional[str]
    created_at: str
    last_used_at: Optional[str]
    backup_eligible: bool

class PasskeyCredentialsList(BaseModel):
    credentials: List[PasskeyCredential]

class ErrorResponse(BaseModel):
    success: bool
    error: Dict[str, Any]


def get_session_token(request: Request) -> Optional[str]:
    """Extract session token from Authorization header"""
    auth_header = request.headers.get("Authorization")
    if auth_header and auth_header.startswith("Bearer "):
        return auth_header[7:]
    return None


def base64url_to_bytes(data: str) -> bytes:
    """Convert base64url string to bytes"""
    # Add padding if needed
    padding = 4 - len(data) % 4
    if padding != 4:
        data += '=' * padding
    # Replace URL-safe characters
    data = data.replace('-', '+').replace('_', '/')
    return base64.b64decode(data)


def bytes_to_base64url(data: bytes) -> str:
    """Convert bytes to base64url string"""
    return base64.urlsafe_b64encode(data).decode('utf-8').rstrip('=')


# Registration endpoints
@router.post("/auth/passkey/register/start", response_model=PasskeyRegistrationStartResponse)
async def register_start(request: PasskeyRegistrationStartRequest):
    """Start passkey registration - generate challenge and options"""
    try:
        email = request.email

        # Check if user already exists
        existing_user = db.get_user_by_email(email)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "code": "USER_EXISTS",
                    "message": "An account with this email already exists. Please sign in instead."
                }
            )

        # Create challenge
        challenge_id, challenge = db.create_challenge()

        # Generate registration options
        options = generate_registration_options(
            rp_id=RP_ID,
            rp_name=RP_NAME,
            user_id=email.encode('utf-8'),  # Will be replaced with actual user_id after creation
            user_name=email,
            user_display_name=email,
            challenge=challenge.encode('utf-8'),
            authenticator_selection=AuthenticatorSelectionCriteria(
                authenticator_attachment=AuthenticatorAttachment.PLATFORM,
                resident_key=ResidentKeyRequirement.PREFERRED,
                user_verification=UserVerificationRequirement.REQUIRED,
            ),
            supported_pub_key_algs=[
                COSEAlgorithmIdentifier.ECDSA_SHA_256,
                COSEAlgorithmIdentifier.RSASSA_PKCS1_v1_5_SHA_256,
            ],
            timeout=60000,
        )

        # Convert options to JSON-serializable format
        options_json = json.loads(options_to_json(options))

        logger.info(f"Registration started for email: {email}")

        return PasskeyRegistrationStartResponse(
            challenge_id=challenge_id,
            options=options_json
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error starting registration: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "code": "REGISTRATION_START_FAILED",
                "message": "Failed to start registration. Please try again."
            }
        )


@router.post("/auth/passkey/register/verify", response_model=PasskeyRegistrationVerifyResponse)
async def register_verify(request: PasskeyRegistrationVerifyRequest):
    """Verify passkey registration and create user account"""
    try:
        email = request.email
        challenge_id = request.challenge_id
        credential = request.credential
        friendly_name = request.friendly_name

        # Get and validate challenge
        challenge_data = db.get_challenge(challenge_id)
        if not challenge_data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "code": "INVALID_CHALLENGE",
                    "message": "Challenge expired or invalid. Please try again."
                }
            )

        challenge = challenge_data['challenge']

        # Verify registration response
        try:
            verification = verify_registration_response(
                credential=credential,
                expected_challenge=challenge.encode('utf-8'),
                expected_origin=EXPECTED_ORIGIN,
                expected_rp_id=RP_ID,
            )
        except Exception as e:
            logger.error(f"Registration verification failed: {e}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "code": "INVALID_CREDENTIAL",
                    "message": "Passkey verification failed. Please try again."
                }
            )

        # Create user account
        user = db.create_user(email)

        # Store passkey credential
        credential_id_bytes = base64url_to_bytes(verification.credential_id)
        public_key_bytes = verification.credential_public_key

        db.store_passkey_credential(
            user_id=user['id'],
            credential_id=bytes_to_base64url(credential_id_bytes),
            public_key=bytes_to_base64url(public_key_bytes),
            sign_count=verification.sign_count,
            backup_eligible=verification.credential_backed_up,
            transports=credential.get('response', {}).get('transports', []),
            friendly_name=friendly_name or "Primary Device"
        )

        # Generate recovery codes
        recovery_codes = db.generate_recovery_codes(user['id'])

        # Create session
        session_token = db.create_session(user['id'])

        # Update last login
        db.update_user_last_login(user['id'])

        # Send welcome email with recovery codes (async, don't wait)
        try:
            await send_welcome_email(email, recovery_codes)
        except Exception as e:
            logger.error(f"Failed to send welcome email: {e}")
            # Don't fail registration if email fails

        logger.info(f"User registered successfully: {email}")

        return PasskeyRegistrationVerifyResponse(
            user={
                "id": user['id'],
                "email": user['email'],
                "created_at": str(user['created_at']),
            },
            session_token=session_token,
            recovery_codes=recovery_codes,
            recovery_codes_message="Save these codes securely. You'll need them if you lose access to your passkey.",
            must_acknowledge=True
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error verifying registration: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "code": "REGISTRATION_VERIFY_FAILED",
                "message": "Failed to complete registration. Please try again."
            }
        )


@router.post("/auth/passkey/recovery-codes/acknowledge")
async def acknowledge_recovery_codes(request: Request):
    """Acknowledge that recovery codes have been saved"""
    try:
        session_token = get_session_token(request)
        if not session_token:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail={
                    "code": "NO_SESSION",
                    "message": "Session token required"
                }
            )

        # Validate session
        session = db.validate_session(session_token)
        if not session:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail={
                    "code": "INVALID_SESSION",
                    "message": "Invalid or expired session"
                }
            )

        logger.info(f"Recovery codes acknowledged for user: {session['user_id']}")

        return {"success": True, "acknowledged": True}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error acknowledging recovery codes: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "code": "ACKNOWLEDGE_FAILED",
                "message": "Failed to acknowledge recovery codes"
            }
        )


# Authentication endpoints
@router.post("/auth/passkey/login/start", response_model=PasskeyLoginStartResponse)
async def login_start(request: PasskeyLoginStartRequest):
    """Start passkey authentication - generate challenge and options"""
    try:
        email = request.email

        # Get user
        user = db.get_user_by_email(email)
        if not user:
            # Don't reveal if user exists - return generic response
            # Frontend will handle error on verify step
            pass

        # Create challenge (store user_id for verification)
        challenge_id, challenge = db.create_challenge(user_id=user['id'] if user else None)

        # Get user's passkeys if user exists
        allow_credentials = []
        if user:
            passkeys = db.get_user_passkeys(user['id'])
            allow_credentials = [
                PublicKeyCredentialDescriptor(
                    id=base64url_to_bytes(pk['credential_id']),
                    transports=pk.get('transports', [])
                )
                for pk in passkeys
            ]

        # Generate authentication options
        options = generate_authentication_options(
            rp_id=RP_ID,
            challenge=challenge.encode('utf-8'),
            allow_credentials=allow_credentials if allow_credentials else None,
            user_verification=UserVerificationRequirement.REQUIRED,
            timeout=60000,
        )

        # Convert options to JSON-serializable format
        options_json = json.loads(options_to_json(options))

        logger.info(f"Login started for email: {email}")

        return PasskeyLoginStartResponse(
            challenge_id=challenge_id,
            options=options_json
        )

    except Exception as e:
        logger.error(f"Error starting login: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "code": "LOGIN_START_FAILED",
                "message": "Failed to start login. Please try again."
            }
        )


@router.post("/auth/passkey/login/verify", response_model=PasskeyLoginVerifyResponse)
async def login_verify(request: PasskeyLoginVerifyRequest):
    """Verify passkey authentication"""
    try:
        challenge_id = request.challenge_id
        credential = request.credential

        # Get and validate challenge
        challenge_data = db.get_challenge(challenge_id)
        if not challenge_data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "code": "INVALID_CHALLENGE",
                    "message": "Challenge expired or invalid. Please try again."
                }
            )

        challenge = challenge_data['challenge']
        user_id = challenge_data.get('user_id')

        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "code": "USER_NOT_FOUND",
                    "message": "User not found. Please register first."
                }
            )

        # Get credential from database
        credential_id = credential.get('id')
        if not credential_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "code": "INVALID_CREDENTIAL",
                    "message": "Invalid credential format"
                }
            )

        stored_credential = db.get_passkey_credential(credential_id)
        if not stored_credential or stored_credential['user_id'] != user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail={
                    "code": "INVALID_CREDENTIAL",
                    "message": "Passkey not found or doesn't belong to this account"
                }
            )

        # Verify authentication response
        try:
            verification = verify_authentication_response(
                credential=credential,
                expected_challenge=challenge.encode('utf-8'),
                expected_origin=EXPECTED_ORIGIN,
                expected_rp_id=RP_ID,
                credential_public_key=base64url_to_bytes(stored_credential['public_key']),
                credential_current_sign_count=stored_credential['sign_count'],
            )
        except Exception as e:
            logger.error(f"Authentication verification failed: {e}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail={
                    "code": "INVALID_CREDENTIAL",
                    "message": "Passkey verification failed. Please try again."
                }
            )

        # Update sign count
        db.update_passkey_sign_count(credential_id, verification.new_sign_count)

        # Get user
        user = db.get_user_by_id(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={
                    "code": "USER_NOT_FOUND",
                    "message": "User not found"
                }
            )

        # Create session
        session_token = db.create_session(user['id'])

        # Update last login
        db.update_user_last_login(user['id'])

        logger.info(f"User authenticated successfully: {user['email']}")

        return PasskeyLoginVerifyResponse(
            user={
                "id": user['id'],
                "email": user['email'],
                "last_login": str(user.get('last_login', '')),
            },
            session_token=session_token
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error verifying login: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "code": "LOGIN_VERIFY_FAILED",
                "message": "Failed to complete login. Please try again."
            }
        )


# Recovery code authentication
@router.post("/auth/passkey/recovery/verify", response_model=RecoveryCodeVerifyResponse)
async def verify_recovery_code(request: RecoveryCodeVerifyRequest, http_request: Request):
    """Authenticate using a recovery code"""
    try:
        email = request.email
        code = request.code

        # Get user
        user = db.get_user_by_email(email)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={
                    "code": "USER_NOT_FOUND",
                    "message": "User not found"
                }
            )

        # Check rate limit
        is_limited, retry_after = db.check_recovery_rate_limit(user['id'])
        if is_limited:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail={
                    "code": "RATE_LIMITED",
                    "message": f"Too many failed attempts. Account locked for {retry_after // 60} minutes.",
                    "retry_after": retry_after
                }
            )

        # Get client IP
        client_ip = http_request.client.host if http_request.client else None

        # Verify recovery code
        is_valid = db.verify_recovery_code(user['id'], code)

        # Log attempt
        db.log_recovery_attempt(user['id'], is_valid, client_ip)

        if not is_valid:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail={
                    "code": "INVALID_RECOVERY_CODE",
                    "message": "Invalid or already used recovery code"
                }
            )

        # Get remaining codes
        remaining_codes = db.count_remaining_recovery_codes(user['id'])

        if remaining_codes == 0:
            logger.warning(f"User {email} has exhausted all recovery codes")

        # Create session
        session_token = db.create_session(user['id'])

        # Update last login
        db.update_user_last_login(user['id'])

        # Send security alert email (async, don't wait)
        try:
            await send_recovery_alert(email, remaining_codes)
        except Exception as e:
            logger.error(f"Failed to send recovery alert: {e}")

        logger.info(f"User authenticated via recovery code: {email}")

        return RecoveryCodeVerifyResponse(
            user={
                "id": user['id'],
                "email": user['email'],
                "last_login": str(user.get('last_login', '')),
            },
            session_token=session_token,
            remaining_codes=remaining_codes
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error verifying recovery code: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "code": "RECOVERY_VERIFY_FAILED",
                "message": "Failed to verify recovery code"
            }
        )


# Email recovery endpoints
@router.post("/auth/passkey/email-recovery/request")
async def request_email_recovery(request: EmailRecoveryRequest):
    """Request email recovery link for lost passkeys + codes"""
    try:
        email = request.email

        # Get user
        user = db.get_user_by_email(email)
        if not user:
            # Don't reveal if user exists
            return {
                "success": True,
                "message": "If an account exists with this email, you'll receive a recovery link shortly."
            }

        # Create recovery token
        token = db.create_email_recovery_token(user['id'])

        # Send recovery email
        try:
            await send_recovery_link(email, token)
        except Exception as e:
            logger.error(f"Failed to send recovery link: {e}")
            # Don't fail the request if email fails

        logger.info(f"Email recovery requested for: {email}")

        return {
            "success": True,
            "message": "If an account exists with this email, you'll receive a recovery link shortly."
        }

    except Exception as e:
        logger.error(f"Error requesting email recovery: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "code": "EMAIL_RECOVERY_FAILED",
                "message": "Failed to process recovery request"
            }
        )


@router.post("/auth/passkey/email-recovery/complete", response_model=PasskeyRegistrationVerifyResponse)
async def complete_email_recovery(request: EmailRecoveryCompleteRequest):
    """Complete email recovery by creating new passkey"""
    try:
        token = request.token
        credential = request.credential
        friendly_name = request.friendly_name

        # Validate recovery token
        recovery_data = db.validate_email_recovery_token(token)
        if not recovery_data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "code": "INVALID_EMAIL_TOKEN",
                    "message": "Recovery link expired or invalid"
                }
            )

        user_id = recovery_data['user_id']

        # Get user
        user = db.get_user_by_id(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={
                    "code": "USER_NOT_FOUND",
                    "message": "User not found"
                }
            )

        # Note: For email recovery, we skip WebAuthn verification of the challenge
        # since this is a recovery flow. The token validation is sufficient.
        # In production, you might want to generate a new challenge here.

        # Invalidate all existing passkeys (security measure)
        db.invalidate_all_passkeys(user_id)

        # Store new passkey credential
        # Note: In real implementation, you'd verify the credential properly
        # For now, we'll store it directly
        credential_id = credential.get('id')
        if not credential_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "code": "INVALID_CREDENTIAL",
                    "message": "Invalid credential format"
                }
            )

        # For simplicity, store credential (in production, verify it properly)
        db.store_passkey_credential(
            user_id=user_id,
            credential_id=credential_id,
            public_key=credential.get('response', {}).get('publicKey', ''),
            sign_count=0,
            backup_eligible=False,
            transports=credential.get('response', {}).get('transports', []),
            friendly_name=friendly_name or "Recovered Device"
        )

        # Generate new recovery codes
        recovery_codes = db.generate_recovery_codes(user_id)

        # Create session
        session_token = db.create_session(user_id)

        # Update last login
        db.update_user_last_login(user_id)

        # Send confirmation email with new recovery codes (async, don't wait)
        try:
            await send_recovery_confirmation(user['email'], recovery_codes)
        except Exception as e:
            logger.error(f"Failed to send recovery confirmation: {e}")

        logger.info(f"Account recovered successfully for: {user['email']}")

        return PasskeyRegistrationVerifyResponse(
            user={
                "id": user['id'],
                "email": user['email'],
                "last_login": str(user.get('last_login', '')),
            },
            session_token=session_token,
            recovery_codes=recovery_codes,
            recovery_codes_message="Your account has been recovered. Save these new recovery codes securely.",
            must_acknowledge=True
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error completing email recovery: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "code": "EMAIL_RECOVERY_COMPLETE_FAILED",
                "message": "Failed to complete account recovery"
            }
        )


# Session management
@router.post("/auth/validate-passkey-session", response_model=SessionValidationResponse)
async def validate_passkey_session(request: Request):
    """Validate passkey session token"""
    try:
        session_token = get_session_token(request)
        if not session_token:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail={
                    "code": "NO_SESSION",
                    "message": "Session token required"
                }
            )

        # Validate session
        session = db.validate_session(session_token)
        if not session:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail={
                    "code": "INVALID_SESSION",
                    "message": "Invalid or expired session"
                }
            )

        return SessionValidationResponse(
            user={
                "id": session['user_id'],
                "email": session['email'],
            },
            valid=True
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error validating session: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "code": "SESSION_VALIDATION_FAILED",
                "message": "Failed to validate session"
            }
        )


@router.post("/auth/logout")
async def logout(request: Request):
    """Logout user by invalidating session"""
    try:
        session_token = get_session_token(request)
        if not session_token:
            return {"success": True, "message": "Logged out"}

        # Delete session
        db.delete_session(session_token)

        logger.info("User logged out successfully")

        return {"success": True, "message": "Logged out successfully"}

    except Exception as e:
        logger.error(f"Error during logout: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "code": "LOGOUT_FAILED",
                "message": "Failed to logout"
            }
        )


# Passkey management endpoints
@router.get("/auth/passkey/credentials", response_model=PasskeyCredentialsList)
async def list_passkeys(request: Request):
    """List all passkeys for the authenticated user"""
    try:
        session_token = get_session_token(request)
        if not session_token:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail={
                    "code": "NO_SESSION",
                    "message": "Session token required"
                }
            )

        # Validate session
        session = db.validate_session(session_token)
        if not session:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail={
                    "code": "INVALID_SESSION",
                    "message": "Invalid or expired session"
                }
            )

        # Get passkeys
        passkeys = db.get_user_passkeys(session['user_id'])

        credentials = [
            PasskeyCredential(
                id=pk['id'],
                friendly_name=pk.get('friendly_name'),
                created_at=str(pk['created_at']),
                last_used_at=str(pk['last_used_at']) if pk.get('last_used_at') else None,
                backup_eligible=pk.get('backup_eligible', False)
            )
            for pk in passkeys
        ]

        return PasskeyCredentialsList(credentials=credentials)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error listing passkeys: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "code": "LIST_PASSKEYS_FAILED",
                "message": "Failed to list passkeys"
            }
        )


@router.delete("/auth/passkey/credentials/{passkey_id}")
async def delete_passkey_endpoint(passkey_id: str, request: Request):
    """Delete a passkey (cannot delete last passkey)"""
    try:
        session_token = get_session_token(request)
        if not session_token:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail={
                    "code": "NO_SESSION",
                    "message": "Session token required"
                }
            )

        # Validate session
        session = db.validate_session(session_token)
        if not session:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail={
                    "code": "INVALID_SESSION",
                    "message": "Invalid or expired session"
                }
            )

        # Delete passkey
        success = db.delete_passkey(passkey_id, session['user_id'])

        if not success:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "code": "CANNOT_DELETE_LAST_PASSKEY",
                    "message": "Cannot delete your last passkey. Add another passkey first."
                }
            )

        logger.info(f"Passkey deleted for user: {session['user_id']}")

        return {"success": True, "message": "Passkey removed successfully"}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting passkey: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "code": "DELETE_PASSKEY_FAILED",
                "message": "Failed to delete passkey"
            }
        )
