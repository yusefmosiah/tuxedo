"""
Passkey Authentication Routes
Handles registration and authentication with WebAuthn passkeys
"""

from fastapi import APIRouter, HTTPException, Response, Request, Depends
from pydantic import BaseModel, EmailStr
import secrets
import json
import sqlite3
from datetime import datetime, timedelta
from webauthn import (
    generate_registration_options,
    verify_registration_response,
    generate_authentication_options,
    verify_authentication_response,
)
from webauthn.helpers.structs import (
    PublicKeyCredentialRpEntity,
    PublicKeyCredentialUserEntity,
)
from webauthn.helpers.exceptions import (
    InvalidRegistrationResponse,
    InvalidAuthenticationResponse,
)
from auth.recovery import RecoveryCodeService

router = APIRouter(prefix="/auth/passkey", tags=["passkey"])

# Request models
class RegistrationStartRequest(BaseModel):
    email: EmailStr

class RegistrationVerifyRequest(BaseModel):
    email: EmailStr
    challenge_id: str
    credential: dict  # WebAuthn credential response

class AuthenticationStartRequest(BaseModel):
    email: EmailStr | None = None  # Username-less if None

class AuthenticationVerifyRequest(BaseModel):
    challenge_id: str
    credential: dict  # WebAuthn credential response

class RecoveryCodeRequest(BaseModel):
    code: str

# RP configuration
RP_ID = "localhost"  # Change for production
RP_NAME = "Tuxedo AI"
RP_ORIGIN = "http://localhost:5173"

async def get_db(request: Request):
    """Get database instance from app state"""
    return request.app.state.db

@router.post("/register/start")
async def start_registration(req: RegistrationStartRequest, request: Request):
    """Start passkey registration"""
    db = await get_db(request)

    # Check if user exists
    conn = sqlite3.connect(db.db_path)
    try:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM users WHERE email = ?", (req.email,))
        if cursor.fetchone():
            raise HTTPException(400, "User already exists")

        # Generate challenge
        challenge = secrets.token_bytes(32)
        challenge_id = f"ch_{secrets.token_urlsafe(16)}"

        # Store challenge
        cursor.execute(
            """INSERT INTO passkey_challenges (id, challenge, expires_at)
               VALUES (?, ?, ?)""",
            (challenge_id, challenge.hex(), datetime.utcnow() + timedelta(minutes=15))
        )
        conn.commit()

        # Generate registration options
        options = generate_registration_options(
            rp_id=RP_ID,
            rp_name=RP_NAME,
            user_id=req.email.encode(),
            user_name=req.email,
            user_display_name=req.email,
            challenge=challenge,
            authenticator_selection={
                "authenticatorAttachment": "platform",
                "userVerification": "required",
                "residentKey": "required",
            }
        )

        return {
            "challenge_id": challenge_id,
            "options": json.loads(options.to_json())
        }

    except sqlite3.Error as e:
        raise HTTPException(500, f"Database error: {str(e)}")
    finally:
        conn.close()

@router.post("/register/verify")
async def verify_registration(req: RegistrationVerifyRequest, request: Request):
    """Verify passkey registration and create user"""
    db = await get_db(request)

    try:
        conn = sqlite3.connect(db.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        # Get challenge
        cursor.execute(
            """SELECT * FROM passkey_challenges
               WHERE id = ? AND used = FALSE AND expires_at > ?""",
            (req.challenge_id, datetime.utcnow())
        )
        challenge_row = cursor.fetchone()
        if not challenge_row:
            raise HTTPException(400, "Invalid or expired challenge")

        # Mark challenge as used
        cursor.execute(
            "UPDATE passkey_challenges SET used = TRUE WHERE id = ?",
            (req.challenge_id,)
        )

        # Verify WebAuthn response
        expected_challenge = bytes.fromhex(challenge_row['challenge'])

        verification = verify_registration_response(
            credential=req.credential,
            expected_challenge=expected_challenge,
            expected_origin=RP_ORIGIN,
            expected_rp_id=RP_ID,
        )

        # For now, we'll use server-side derivation (PRF not supported in current library)
        has_prf = False

        # Create user
        user_id = f"user_{secrets.token_urlsafe(16)}"
        cursor.execute(
            """INSERT INTO users (id, email) VALUES (?, ?)""",
            (user_id, req.email)
        )

        # Store credential
        cred_id = f"cred_{secrets.token_urlsafe(16)}"
        cursor.execute(
            """INSERT INTO passkey_credentials
               (id, user_id, credential_id, public_key, backup_eligible, transports)
               VALUES (?, ?, ?, ?, ?, ?)""",
            (
                cred_id,
                user_id,
                verification.credential_id,
                verification.credential_public_key,
                verification.credential_backed_up,
                ",".join(verification.transports) if verification.transports else None
            )
        )

        # Derive Stellar account using server-side fallback
        from crypto.key_derivation import KeyDerivation
        server_secret = KeyDerivation.get_server_secret()
        keypair = KeyDerivation.derive_from_server(
            user_id, verification.credential_id, server_secret
        )

        # Update user with Stellar public key
        cursor.execute(
            """UPDATE users SET stellar_public_key = ? WHERE id = ?""",
            (keypair.public_key, user_id)
        )

        # Generate recovery codes
        from auth.recovery import RecoveryCodeService
        recovery_codes = RecoveryCodeService.generate_codes()
        await RecoveryCodeService.store_codes(db, user_id, recovery_codes)

        # Create session
        session_token = secrets.token_urlsafe(32)
        session_id = f"sess_{secrets.token_urlsafe(16)}"
        cursor.execute(
            """INSERT INTO passkey_sessions (id, user_id, session_token, expires_at)
               VALUES (?, ?, ?, ?)""",
            (
                session_id,
                user_id,
                session_token,
                datetime.utcnow() + timedelta(days=7)
            )
        )

        conn.commit()

        return {
            "success": True,
            "session_token": session_token,
            "user": {"id": user_id, "email": req.email, "stellar_public_key": keypair.public_key},
            "recovery_codes": recovery_codes,  # Show once
            "has_prf": has_prf,
            "recovery_codes_message": RecoveryCodeService.format_codes_for_display(recovery_codes)
        }

    except InvalidRegistrationResponse as e:
        raise HTTPException(400, f"Invalid registration response: {str(e)}")
    except sqlite3.Error as e:
        raise HTTPException(500, f"Database error: {str(e)}")
    finally:
        conn.close()

@router.post("/login/start")
async def start_authentication(req: AuthenticationStartRequest, request: Request):
    """Start passkey authentication"""
    db = await get_db(request)

    # Generate challenge
    challenge = secrets.token_bytes(32)
    challenge_id = f"ch_{secrets.token_urlsafe(16)}"

    conn = sqlite3.connect(db.db_path)
    try:
        # Store challenge
        conn.execute(
            """INSERT INTO passkey_challenges (id, challenge, expires_at)
               VALUES (?, ?, ?)""",
            (challenge_id, challenge.hex(), datetime.utcnow() + timedelta(minutes=15))
        )
        conn.commit()

        # Get user's credentials (if email provided)
        allow_credentials = []
        if req.email:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()

            cursor.execute("SELECT * FROM users WHERE email = ?", (req.email,))
            user = cursor.fetchone()
            if user:
                cursor.execute(
                    """SELECT credential_id FROM passkey_credentials WHERE user_id = ?""",
                    (user['id'],)
                )
                credentials = cursor.fetchall()
                allow_credentials = [{"id": c['credential_id'], "type": "public-key", "transports": []}
                                      for c in credentials]

        # Generate authentication options
        options = generate_authentication_options(
            rp_id=RP_ID,
            challenge=challenge,
            allow_credentials=allow_credentials,
            user_verification="required"
        )

        return {
            "challenge_id": challenge_id,
            "options": json.loads(options.to_json())
        }

    except sqlite3.Error as e:
        raise HTTPException(500, f"Database error: {str(e)}")
    finally:
        conn.close()

@router.post("/login/verify")
async def verify_authentication(req: AuthenticationVerifyRequest, request: Request):
    """Verify passkey authentication"""
    db = await get_db(request)

    try:
        conn = sqlite3.connect(db.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        # Get challenge
        cursor.execute(
            """SELECT * FROM passkey_challenges
               WHERE id = ? AND used = FALSE AND expires_at > ?""",
            (req.challenge_id, datetime.utcnow())
        )
        challenge_row = cursor.fetchone()
        if not challenge_row:
            raise HTTPException(400, "Invalid or expired challenge")

        # Mark challenge as used
        cursor.execute(
            "UPDATE passkey_challenges SET used = TRUE WHERE id = ?",
            (req.challenge_id,)
        )

        # Get credential from DB
        credential_id = req.credential.get('id')
        cursor.execute(
            """SELECT * FROM passkey_credentials WHERE credential_id = ?""",
            (credential_id,)
        )
        cred_row = cursor.fetchone()
        if not cred_row:
            raise HTTPException(401, "Invalid credential")

        # Verify WebAuthn response
        expected_challenge = bytes.fromhex(challenge_row['challenge'])

        verification = verify_authentication_response(
            credential=req.credential,
            expected_challenge=expected_challenge,
            expected_origin=RP_ORIGIN,
            expected_rp_id=RP_ID,
            credential_public_key=cred_row['public_key'],
            credential_current_sign_count=cred_row['sign_count'],
        )

        # Update sign count
        cursor.execute(
            """UPDATE passkey_credentials SET sign_count = ? WHERE id = ?""",
            (verification.new_sign_count, cred_row['id'])
        )

        # Get user
        cursor.execute(
            """SELECT * FROM users WHERE id = ?""",
            (cred_row['user_id'],)
        )
        user_row = cursor.fetchone()

        # Create session
        session_token = secrets.token_urlsafe(32)
        session_id = f"sess_{secrets.token_urlsafe(16)}"
        cursor.execute(
            """INSERT INTO passkey_sessions (id, user_id, session_token, expires_at)
               VALUES (?, ?, ?, ?)""",
            (
                session_id,
                user_row['id'],
                session_token,
                datetime.utcnow() + timedelta(days=7)
            )
        )

        conn.commit()

        return {
            "success": True,
            "session_token": session_token,
            "user": {
                "id": user_row['id'],
                "email": user_row['email'],
                "stellar_public_key": user_row.get('stellar_public_key')
            }
        }

    except InvalidAuthenticationResponse as e:
        raise HTTPException(401, f"Authentication failed: {str(e)}")
    except sqlite3.Error as e:
        raise HTTPException(500, f"Database error: {str(e)}")
    finally:
        conn.close()

@router.post("/recovery/verify")
async def verify_recovery_code(req: RecoveryCodeRequest, request: Request):
    """Verify recovery code and create session"""
    db = await get_db(request)

    try:
        conn = sqlite3.connect(db.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        # Find user by recovery code
        cursor.execute(
            """SELECT rc.*, u.email, u.id as user_id FROM recovery_codes rc
               JOIN users u ON rc.user_id = u.id
               WHERE rc.code_hash = ? AND rc.used = FALSE""",
            (RecoveryCodeService.hash_code(req.code),)
        )
        row = cursor.fetchone()

        if not row:
            raise HTTPException(401, "Invalid recovery code")

        # Mark code as used
        cursor.execute(
            """UPDATE recovery_codes SET used = TRUE, used_at = CURRENT_TIMESTAMP
               WHERE id = ?""",
            (row['id'],)
        )

        # Create session
        session_token = secrets.token_urlsafe(32)
        session_id = f"sess_{secrets.token_urlsafe(16)}"
        cursor.execute(
            """INSERT INTO passkey_sessions (id, user_id, session_token, expires_at)
               VALUES (?, ?, ?, ?)""",
            (
                session_id,
                row['user_id'],
                session_token,
                datetime.utcnow() + timedelta(days=7)
            )
        )

        conn.commit()

        return {
            "success": True,
            "session_token": session_token,
            "user": {"id": row['user_id'], "email": row['email']}
        }

    except sqlite3.Error as e:
        raise HTTPException(500, f"Database error: {str(e)}")
    finally:
        conn.close()