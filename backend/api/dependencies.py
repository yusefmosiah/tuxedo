"""
API dependencies for authentication and authorization
"""
from fastapi import Header, HTTPException
from typing import Optional
import logging
from database_passkeys import db

logger = logging.getLogger(__name__)


async def get_current_user(authorization: Optional[str] = Header(None)) -> dict:
    """
    Dependency to get current authenticated user from session token

    Usage:
        @router.get("/protected")
        async def protected_route(current_user: dict = Depends(get_current_user)):
            user_id = current_user['id']
            ...
    """
    if not authorization:
        raise HTTPException(
            status_code=401,
            detail="Missing authorization header"
        )

    # Extract token from "Bearer <token>" format
    if not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=401,
            detail="Invalid authorization format. Expected 'Bearer <token>'"
        )

    session_token = authorization.replace("Bearer ", "")

    # Validate session
    session = db.validate_session(session_token)
    if not session:
        raise HTTPException(
            status_code=401,
            detail="Invalid or expired session"
        )

    # Get user details
    user = db.get_user_by_id(session['user_id'])
    if not user:
        raise HTTPException(
            status_code=401,
            detail="User not found"
        )

    logger.info(f"Authenticated user: {user['id']} ({user['email']})")
    return user
