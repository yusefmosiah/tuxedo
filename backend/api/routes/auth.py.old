"""
Authentication API Routes
Handles magic link authentication and user sessions.
"""

from fastapi import APIRouter, HTTPException, status, Response, Request
from fastapi.responses import RedirectResponse
from pydantic import BaseModel, EmailStr
from typing import Optional
import logging
import os
import sqlite3
from datetime import datetime

logger = logging.getLogger(__name__)

router = APIRouter()

# Import database
from database import db

# Import SendGrid for email sending
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

# Pydantic models
class MagicLinkRequest(BaseModel):
    email: EmailStr

class MagicLinkResponse(BaseModel):
    success: bool
    message: str

class AuthResponse(BaseModel):
    success: bool
    session_token: Optional[str] = None
    user: Optional[dict] = None
    message: str

class UserResponse(BaseModel):
    id: str
    email: str
    created_at: str
    last_login: Optional[str] = None

# Email configuration (will be populated from environment)
SENDGRID_API_KEY = os.getenv("SENDGRID_API_KEY")
FROM_EMAIL = os.getenv("FROM_EMAIL", "noreply@tuxedo.ai")
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:5173")

async def send_magic_link_email(email: str, token: str) -> bool:
    """Send magic link email using SendGrid"""
    try:
        magic_link = f"{FRONTEND_URL}/auth/magic-link?token={token}"
        logger.info(f"Magic link for {email}: {magic_link}")

        # Send email using SendGrid if configured
        if SENDGRID_API_KEY:
            try:
                sg = SendGridAPIClient(SENDGRID_API_KEY)

                # Create HTML email content
                html_content = f"""
                <!DOCTYPE html>
                <html>
                <head>
                    <meta charset="utf-8">
                    <meta name="viewport" content="width=device-width, initial-scale=1.0">
                    <title>Sign in to Tuxedo AI</title>
                </head>
                <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333; max-width: 600px; margin: 0 auto; padding: 20px;">
                    <div style="background-color: #f8f9fa; padding: 30px; border-radius: 10px; text-align: center;">
                        <h1 style="color: #2c3e50; margin-bottom: 20px;">🤖 Tuxedo AI</h1>
                        <h2 style="color: #34495e; margin-bottom: 30px;">Welcome to Your AI Agent!</h2>

                        <p style="font-size: 18px; margin-bottom: 30px;">
                            Your AI agents are ready to help you with DeFi operations on Stellar.
                        </p>

                        <div style="background-color: white; padding: 20px; border-radius: 8px; margin: 30px 0; border-left: 4px solid #3498db;">
                            <p style="margin: 0; font-weight: bold; color: #2c3e50;">
                                Click the button below to sign in securely:
                            </p>
                        </div>

                        <a href="{magic_link}"
                           style="background-color: #3498db; color: white; padding: 15px 30px; text-decoration: none; border-radius: 5px; font-size: 18px; font-weight: bold; display: inline-block; margin: 20px 0;">
                            🚀 Sign In to Tuxedo AI
                        </a>

                        <div style="background-color: #fff3cd; border: 1px solid #ffeaa7; border-radius: 5px; padding: 15px; margin: 20px 0;">
                            <p style="margin: 0; color: #856404;">
                                <strong>⏰ This link expires in 15 minutes</strong>
                            </p>
                        </div>

                        <p style="color: #7f8c8d; font-size: 14px; margin-top: 30px;">
                            If you didn't request this sign-in link, you can safely ignore this email.
                        </p>

                        <div style="margin-top: 40px; padding-top: 20px; border-top: 1px solid #ecf0f1;">
                            <p style="color: #95a5a6; font-size: 12px; margin: 0;">
                                Tuxedo AI - Your Autonomous DeFi Agents<br>
                                Built on Stellar Testnet
                            </p>
                        </div>
                    </div>
                </body>
                </html>
                """

                message = Mail(
                    from_email=FROM_EMAIL,
                    to_emails=email,
                    subject="🤖 Sign in to Tuxedo AI - Your AI Agents Await",
                    html_content=html_content
                )

                response = sg.send(message)

                if response.status_code == 202:
                    logger.info(f"Magic link email sent successfully to {email}")
                    return True
                else:
                    logger.warning(f"SendGrid response status: {response.status_code}")
                    return False

            except Exception as e:
                logger.error(f"SendGrid API error: {e}")
                # Fallback to console logging for hackathon
                logger.warning(f"Falling back to console magic link: {magic_link}")
                return True
        else:
            logger.warning("SendGrid not configured, magic link sent to console only")
            logger.info(f"Magic link for {email}: {magic_link}")
            return True

    except Exception as e:
        logger.error(f"Failed to send magic link email: {e}")
        # For hackathon, don't fail the auth flow even if email fails
        return True

@router.post("/auth/magic-link", response_model=MagicLinkResponse)
async def request_magic_link(request: MagicLinkRequest):
    """Request a magic link for email authentication"""
    try:
        # Create magic link session
        token = db.create_magic_link_session(request.email)

        # Send email with magic link
        email_sent = await send_magic_link_email(request.email, token)

        if not email_sent:
            logger.error(f"Failed to send magic link email to {request.email}")
            # For hackathon, we'll still return success even if email fails
            # In production, you'd want to handle this differently

        logger.info(f"Magic link requested for email: {request.email}")

        return MagicLinkResponse(
            success=True,
            message=f"If an account exists with {request.email}, you'll receive a magic link shortly."
        )

    except Exception as e:
        logger.error(f"Error requesting magic link: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to send magic link"
        )

@router.get("/auth/magic-link/validate")
async def validate_magic_link(token: str, response: Response):
    """Validate magic link token and create user session"""
    try:
        # Debug logging
        logger.info(f"Received magic link validation request with token: {token[:16] if token else 'None'}...")

        if not token:
            logger.warning("No token provided in magic link validation")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Token is required"
            )

        # Validate the magic link token
        magic_session = db.validate_magic_link(token)

        if not magic_session:
            logger.warning(f"Invalid or expired magic link token: {token[:8]}...")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid or expired magic link"
            )

        # Get or create user
        user = db.create_or_get_user(magic_session['email'])

        # Create user session
        session_token = db.create_user_session(user['id'])

        # Update user's last login
        from database import DatabaseManager
        db_manager = DatabaseManager()
        with sqlite3.connect(db_manager.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE users SET last_login = ? WHERE id = ?
            ''', (datetime.now(), user['id']))
            conn.commit()

        logger.info(f"User authenticated: {user['email']}")

        # Return JSON response with session token for CORS requests
        return {
            "success": True,
            "message": "Magic link validated successfully",
            "session_token": session_token,
            "user": {
                "id": user['id'],
                "email": user['email'],
                "public_key": user.get('public_key'),
                "last_login": user.get('last_login')
            }
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error validating magic link: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to validate magic link"
        )

@router.post("/auth/validate-session", response_model=AuthResponse)
async def validate_session(request: Request, session_token: Optional[str] = None):
    """Validate user session token"""
    try:
        # Get session token from multiple sources
        original_token = session_token
        if not session_token:
            session_token = request.cookies.get("session_token")
            logger.info(f"Trying cookie token: {session_token[:16] if session_token else 'None'}...")

        if not session_token:
            session_token = request.headers.get("Authorization")
            if session_token and session_token.startswith("Bearer "):
                session_token = session_token[7:]  # Remove "Bearer " prefix
                logger.info(f"Trying header token: {session_token[:16] if session_token else 'None'}...")

        logger.info(f"Session validation request: token_source={'header' if original_token else 'cookie' if request.cookies.get('session_token') else 'none'}, token_preview={session_token[:16] if session_token else 'None'}...")

        if not session_token:
            logger.warning("No session token provided in request")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="No session token provided"
            )

        # Validate session
        session = db.validate_user_session(session_token)
        logger.info(f"Database session validation result: {session is not None}")

        if not session:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired session"
            )

        # Return user info (excluding sensitive data)
        user_info = {
            "id": session['user_id'],
            "email": session['email'],
            "public_key": session.get('public_key'),
            "last_login": session.get('last_login')
        }

        return AuthResponse(
            success=True,
            session_token=session_token,
            user=user_info,
            message="Session valid"
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error validating session: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to validate session"
        )

@router.post("/auth/logout")
async def logout(response: Response):
    """Logout user by clearing session cookie"""
    try:
        # Clear session cookie
        response.delete_cookie(key="session_token")

        return {"success": True, "message": "Logged out successfully"}

    except Exception as e:
        logger.error(f"Error during logout: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to logout"
        )

@router.get("/auth/me", response_model=UserResponse)
async def get_current_user(session_token: Optional[str] = None):
    """Get current authenticated user info"""
    try:
        if not session_token:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="No session token provided"
            )

        session = db.validate_user_session(session_token)

        if not session:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired session"
            )

        return UserResponse(
            id=session['user_id'],
            email=session['email'],
            created_at=session.get('created_at', ''),
            last_login=session.get('last_login')
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting current user: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get user info"
        )