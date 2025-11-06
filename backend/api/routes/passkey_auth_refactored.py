"""
Passkey Authentication API Routes - Refactored
Implements Phase 1 of Passkey Architecture v2

This is a refactored version that uses:
- Separate schema definitions (api/schemas/passkey_schemas.py)
- Helper functions (api/utils/passkey_helpers.py)
- Service layer (services/passkey_service.py)

Reducing the file from 1148 lines to ~400 lines for better maintainability.
"""
from fastapi import APIRouter, Request, Header
from typing import Optional
import logging

# Import schemas
from api.schemas.passkey_schemas import (
    RegisterStartRequest, RegisterStartResponse,
    RegisterVerifyRequest, RegisterVerifyResponse,
    AcknowledgeRecoveryCodesResponse,
    LoginStartRequest, LoginStartResponse,
    LoginVerifyRequest, LoginVerifyResponse,
    RecoveryCodeVerifyRequest, RecoveryCodeVerifyResponse,
    EmailRecoveryRequest,
    SessionValidateResponse,
    PasskeyListResponse, PasskeyCredential,
    PasskeyAddRequest,
)

# Import helpers
from api.utils.passkey_helpers import (
    get_rp_id_and_origin,
    get_session_token,
    create_error_response,
    FRONTEND_URL,
)

# Import services
from services.passkey_service import PasskeyService
from services.email import email_service
from database_passkeys import db

logger = logging.getLogger(__name__)

router = APIRouter()

# Initialize passkey service
passkey_service = PasskeyService(db)


# ============================================================================
# REGISTRATION ENDPOINTS
# ============================================================================

@router.post("/auth/passkey/register/start", response_model=RegisterStartResponse)
async def register_start(req: Request, request: RegisterStartRequest):
    """Start passkey registration flow"""
    logger.info(f"📝 Registration start request for {request.email}")

    try:
        # Get dynamic RP_ID and origin
        rp_id, origin = get_rp_id_and_origin(req)

        # Generate challenge via service
        challenge_id, options = passkey_service.generate_registration_challenge(
            email=request.email,
            rp_id=rp_id,
            origin=origin
        )

        logger.info(f"✅ Registration started for {request.email}")
        return RegisterStartResponse(
            challenge_id=challenge_id,
            options=options
        )

    except ValueError as e:
        # User already exists
        create_error_response(
            "USER_EXISTS",
            str(e),
            status_code=409
        )
    except Exception as e:
        logger.error(f"❌ Error starting registration: {e}", exc_info=True)
        create_error_response(
            "REGISTRATION_START_FAILED",
            "Failed to start registration",
            status_code=500
        )


@router.post("/auth/passkey/register/verify", response_model=RegisterVerifyResponse)
async def register_verify(req: Request, request: RegisterVerifyRequest):
    """Verify passkey registration and create user"""
    logger.info(f"📝 Registration verify request for {request.email}")

    try:
        # Get dynamic RP_ID and origin
        rp_id, origin = get_rp_id_and_origin(req)

        # Verify and complete registration via service
        user, session_token, recovery_codes = passkey_service.verify_and_complete_registration(
            email=request.email,
            challenge_id=request.challenge_id,
            credential=request.credential,
            rp_id=rp_id,
            origin=origin
        )

        # Send welcome email (async, don't block response)
        try:
            await email_service.send_welcome_email(user['email'], recovery_codes)
            logger.info(f"📧 Welcome email sent to {user['email']}")
        except Exception as e:
            logger.error(f"❌ Failed to send welcome email: {e}")

        logger.info(f"✅ Registration completed for {user['email']}")
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

    except ValueError as e:
        # Verification or user creation failed
        error_msg = str(e)
        if "already exists" in error_msg.lower():
            status_code = 409
            error_code = "USER_EXISTS"
        else:
            status_code = 401
            error_code = "INVALID_CREDENTIAL"

        create_error_response(error_code, error_msg, status_code=status_code)
    except Exception as e:
        logger.error(f"❌ Error verifying registration: {e}", exc_info=True)
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
    logger.info("📝 Recovery codes acknowledgment request")

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

        logger.info(f"✅ Recovery codes acknowledged for user {session['user_id']}")
        return AcknowledgeRecoveryCodesResponse(
            success=True,
            acknowledged=True
        )

    except Exception as e:
        logger.error(f"❌ Error acknowledging recovery codes: {e}", exc_info=True)
        create_error_response(
            "ACKNOWLEDGMENT_FAILED",
            "Failed to acknowledge recovery codes",
            status_code=500
        )


# ============================================================================
# AUTHENTICATION ENDPOINTS
# ============================================================================

@router.post("/auth/passkey/login/start", response_model=LoginStartResponse)
async def login_start(req: Request, request: LoginStartRequest):
    """Start passkey login flow"""
    logger.info(f"🔐 Login start request for {request.email}")

    try:
        # Get dynamic RP_ID and origin
        rp_id, origin = get_rp_id_and_origin(req)

        # Generate login challenge via service
        challenge_id, options, user_id = passkey_service.generate_login_challenge(
            email=request.email,
            rp_id=rp_id,
            origin=origin
        )

        logger.info(f"✅ Login started for {request.email}")
        return LoginStartResponse(
            challenge_id=challenge_id,
            options=options
        )

    except ValueError as e:
        # User not found or no passkeys
        error_msg = str(e)
        status_code = 404 if "not found" in error_msg.lower() else 400
        create_error_response(
            "USER_NOT_FOUND" if status_code == 404 else "NO_PASSKEYS",
            error_msg,
            status_code=status_code
        )
    except Exception as e:
        logger.error(f"❌ Error starting login: {e}", exc_info=True)
        create_error_response(
            "LOGIN_START_FAILED",
            "Failed to start login",
            status_code=500
        )


@router.post("/auth/passkey/login/verify", response_model=LoginVerifyResponse)
async def login_verify(req: Request, request: LoginVerifyRequest):
    """Verify passkey login"""
    logger.info(f"🔐 Login verify request")

    try:
        # Get dynamic RP_ID and origin
        rp_id, origin = get_rp_id_and_origin(req)

        # Verify and complete login via service
        user, session_token = passkey_service.verify_and_complete_login(
            challenge_id=request.challenge_id,
            credential=request.credential,
            rp_id=rp_id,
            origin=origin
        )

        logger.info(f"✅ Login completed for {user['email']}")
        return LoginVerifyResponse(
            user={
                "id": user['id'],
                "email": user['email']
            },
            session_token=session_token
        )

    except ValueError as e:
        # Verification failed
        create_error_response(
            "INVALID_CREDENTIAL",
            str(e),
            status_code=401
        )
    except Exception as e:
        logger.error(f"❌ Error verifying login: {e}", exc_info=True)
        create_error_response(
            "LOGIN_VERIFY_FAILED",
            "Failed to verify login",
            status_code=500
        )


# ============================================================================
# RECOVERY CODE AUTHENTICATION
# ============================================================================

@router.post("/auth/passkey/recovery/verify", response_model=RecoveryCodeVerifyResponse)
async def verify_recovery_code(request: RecoveryCodeVerifyRequest, req: Request):
    """Verify recovery code and authenticate user"""
    logger.info(f"🔑 Recovery code verification request for {request.email}")

    try:
        # Get user
        user = db.get_user_by_email(request.email)
        if not user:
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
        db.update_last_login(user['id'])

        # Send security alert email (async, don't block response)
        try:
            await email_service.send_recovery_alert(user['email'], remaining_codes)
            logger.info(f"📧 Recovery alert sent to {user['email']}")
        except Exception as e:
            logger.error(f"❌ Failed to send recovery alert: {e}")

        logger.info(f"✅ Recovery code authenticated for {user['email']}")
        return RecoveryCodeVerifyResponse(
            user={
                "id": user['id'],
                "email": user['email']
            },
            session_token=session_token,
            remaining_codes=remaining_codes
        )

    except Exception as e:
        logger.error(f"❌ Error verifying recovery code: {e}", exc_info=True)
        create_error_response(
            "RECOVERY_VERIFY_FAILED",
            "Failed to verify recovery code",
            status_code=500
        )


# ============================================================================
# EMAIL RECOVERY (for lost passkeys + codes)
# ============================================================================

@router.post("/auth/passkey/email-recovery/request")
async def request_email_recovery(request: EmailRecoveryRequest):
    """Request email recovery link"""
    logger.info(f"📧 Email recovery request for {request.email}")

    try:
        # Get user
        user = db.get_user_by_email(request.email)
        if not user:
            # Always return success to prevent email enumeration
            logger.info(f"⚠️ Recovery requested for non-existent user: {request.email}")
            return {"success": True, "message": "If an account exists, a recovery link has been sent"}

        # Create recovery token
        token = db.create_email_recovery_token(user['id'])

        # Send email (async, don't block response)
        try:
            await email_service.send_recovery_link(user['email'], token)
            logger.info(f"📧 Recovery link sent to {user['email']}")
        except Exception as e:
            logger.error(f"❌ Failed to send recovery link: {e}")

        return {"success": True, "message": "If an account exists, a recovery link has been sent"}

    except Exception as e:
        logger.error(f"❌ Error requesting email recovery: {e}", exc_info=True)
        create_error_response(
            "EMAIL_RECOVERY_FAILED",
            "Failed to send recovery link",
            status_code=500
        )


# ============================================================================
# SESSION MANAGEMENT
# ============================================================================

@router.post("/auth/validate-passkey-session", response_model=SessionValidateResponse)
async def validate_passkey_session(
    request: Request,
    authorization: Optional[str] = Header(None)
):
    """Validate passkey session"""
    logger.info("🔍 Session validation request")

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

        logger.info(f"✅ Session validated for user {session['user_id']}")
        return SessionValidateResponse(
            user={
                "id": session['user_id'],
                "email": session['email']
            },
            valid=True
        )

    except Exception as e:
        logger.error(f"❌ Error validating session: {e}", exc_info=True)
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
    logger.info("👋 Logout request")

    try:
        session_token = get_session_token(request, authorization)
        if session_token:
            db.delete_session(session_token)
            logger.info("✅ Session deleted")

        return {"success": True, "message": "Logged out successfully"}

    except Exception as e:
        logger.error(f"❌ Error during logout: {e}", exc_info=True)
        create_error_response(
            "LOGOUT_FAILED",
            "Failed to logout",
            status_code=500
        )


# ============================================================================
# PASSKEY MANAGEMENT (multiple passkeys)
# ============================================================================

@router.get("/auth/passkey/credentials", response_model=PasskeyListResponse)
async def list_passkeys(
    request: Request,
    authorization: Optional[str] = Header(None)
):
    """List user's passkeys"""
    logger.info("📋 List passkeys request")

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

        logger.info(f"✅ Listed {len(credentials)} passkeys for user {session['user_id']}")
        return PasskeyListResponse(credentials=credentials)

    except Exception as e:
        logger.error(f"❌ Error listing passkeys: {e}", exc_info=True)
        create_error_response(
            "LIST_PASSKEYS_FAILED",
            "Failed to list passkeys",
            status_code=500
        )


@router.delete("/auth/passkey/credentials/{passkey_id}")
async def remove_passkey(
    passkey_id: str,
    request: Request,
    authorization: Optional[str] = Header(None)
):
    """Remove a passkey from user's account"""
    logger.info(f"🗑️  Remove passkey request: {passkey_id}")

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

        logger.info(f"✅ Passkey {passkey_id} removed for user {session['user_id']}")
        return {"success": True, "message": "Passkey removed successfully"}

    except Exception as e:
        logger.error(f"❌ Error removing passkey: {e}", exc_info=True)
        create_error_response(
            "REMOVE_PASSKEY_FAILED",
            "Failed to remove passkey",
            status_code=500
        )
