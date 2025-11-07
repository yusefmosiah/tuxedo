"""
FastAPI dependencies for authentication and authorization
"""
from fastapi import Depends, HTTPException, Header
from typing import Optional
from database_passkeys import PasskeyDatabaseManager
import logging

logger = logging.getLogger(__name__)

db = PasskeyDatabaseManager()


async def get_current_user(
    authorization: Optional[str] = Header(None)
) -> dict:
    """
    Get current authenticated user from Bearer token
    Raises 401 if not authenticated
    """
    if not authorization:
        raise HTTPException(
            status_code=401,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"}
        )

    # Extract token from "Bearer <token>"
    try:
        scheme, token = authorization.split()
        if scheme.lower() != "bearer":
            raise ValueError("Invalid authentication scheme")
    except ValueError:
        raise HTTPException(
            status_code=401,
            detail="Invalid authentication header format"
        )

    # Validate session
    session = db.validate_session(token)
    if not session:
        raise HTTPException(
            status_code=401,
            detail="Invalid or expired session"
        )

    # Get user
    user = db.get_user_by_id(session['user_id'])
    if not user:
        raise HTTPException(
            status_code=401,
            detail="User not found"
        )

    return user


async def get_optional_user(
    authorization: Optional[str] = Header(None)
) -> Optional[dict]:
    """Get user if authenticated, None otherwise (no error)"""
    if not authorization:
        return None

    try:
        return await get_current_user(authorization)
    except HTTPException:
        return None


async def get_session_token(
    authorization: Optional[str] = Header(None)
) -> dict:
    """
    Get session token from Authorization header
    Used by endpoints that need to validate sessions
    """
    if not authorization:
        raise HTTPException(
            status_code=401,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"}
        )

    # Extract token from "Bearer <token>"
    try:
        scheme, token = authorization.split()
        if scheme.lower() != "bearer":
            raise ValueError("Invalid authentication scheme")
    except ValueError:
        raise HTTPException(
            status_code=401,
            detail="Invalid authentication header format"
        )

    # Validate session
    session = db.validate_session(token)
    if not session:
        raise HTTPException(
            status_code=401,
            detail="Invalid or expired session"
        )

    return {"session_token": token, "user_id": session['user_id']}
