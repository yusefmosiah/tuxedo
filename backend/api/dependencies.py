"""
FastAPI dependencies for authentication and authorization
"""
from fastapi import Header, HTTPException, status
from typing import Optional, Dict, Any
from database_passkeys import db
import logging

logger = logging.getLogger(__name__)

async def get_current_user(
    authorization: Optional[str] = Header(None)
) -> Dict[str, Any]:
    """
    Dependency to get current authenticated user from session token

    Usage in routes:
        @router.get("/protected")
        async def protected_route(current_user: dict = Depends(get_current_user)):
            user_id = current_user['id']
            ...
    """
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing authorization header"
        )

    # Extract token from "Bearer <token>" format
    try:
        scheme, token = authorization.split()
        if scheme.lower() != "bearer":
            raise ValueError("Invalid authorization scheme")
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authorization header format. Expected 'Bearer <token>'"
        )

    # Validate session token
    session = db.validate_session(token)
    if not session:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired session token"
        )

    # Get user info
    user = db.get_user_by_id(session['user_id'])
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )

    return user


async def get_optional_user(
    authorization: Optional[str] = Header(None)
) -> Optional[Dict[str, Any]]:
    """
    Optional authentication - returns user if authenticated, None otherwise
    Useful for routes that work differently for authenticated vs anonymous users
    """
    logger.info(f"🔍 get_optional_user called - Authorization header present: {authorization is not None}")
    if authorization:
        logger.info(f"🔑 Authorization header: {authorization[:20]}...")

    if not authorization:
        logger.warning("⚠️ No authorization header - treating as anonymous")
        return None

    try:
        user = await get_current_user(authorization)
        logger.info(f"✅ User authenticated: {user.get('id', 'unknown')[:8]}... (email: {user.get('email', 'N/A')})")
        return user
    except HTTPException as e:
        logger.warning(f"❌ Authentication failed: {e.detail}")
        return None
