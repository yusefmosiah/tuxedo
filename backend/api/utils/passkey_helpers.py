"""
Helper functions for passkey authentication
Extracted from passkey_auth.py for better organization
"""
import os
import logging
from fastapi import HTTPException, Request, status
from typing import Optional, Dict, Any
from urllib.parse import urlparse

logger = logging.getLogger(__name__)

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

    Args:
        request: FastAPI Request object

    Returns:
        tuple: (rp_id, origin)
    """
    # Try to get origin from request headers
    origin = request.headers.get("origin")
    referer = request.headers.get("referer")

    # Fallback to referer if origin is not present
    if not origin and referer:
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
    parsed = urlparse(origin)
    rp_id = parsed.hostname or "localhost"

    # For localhost, use "localhost" as RP_ID
    # For production domains, use the full hostname
    if rp_id in ["localhost", "127.0.0.1"]:
        rp_id = "localhost"

    logger.info(f"🔍 Dynamic RP config - RP_ID: {rp_id}, Origin: {origin}")

    return rp_id, origin


def get_session_token(request: Request, authorization: Optional[str] = None) -> Optional[str]:
    """
    Extract session token from request.

    Tries Authorization header first, then falls back to cookie.

    Args:
        request: FastAPI Request object
        authorization: Optional Authorization header value

    Returns:
        Session token if found, None otherwise
    """
    # Try Authorization header first
    if authorization and authorization.startswith("Bearer "):
        token = authorization[7:]
        logger.debug(f"🎫 Session token from Authorization header (length: {len(token)})")
        return token

    # Try cookie
    token = request.cookies.get("session_token")
    if token:
        logger.debug(f"🍪 Session token from cookie (length: {len(token)})")
    else:
        logger.debug("⚠️ No session token found in request")

    return token


def create_error_response(
    code: str,
    message: str,
    details: Optional[Dict] = None,
    status_code: int = 400
):
    """
    Create standardized error response with comprehensive logging.

    Args:
        code: Error code (e.g., "USER_EXISTS")
        message: Human-readable error message
        details: Optional additional details
        status_code: HTTP status code

    Raises:
        HTTPException with structured error response
    """
    error_data = {
        "code": code,
        "message": message
    }
    if details:
        error_data["details"] = details

    # Log with appropriate level
    log_message = f"❌ Error {status_code}: {code} - {message}"
    if details:
        log_message += f" | Details: {details}"

    if status_code >= 500:
        logger.error(log_message)
    elif status_code >= 400:
        logger.warning(log_message)
    else:
        logger.info(log_message)

    raise HTTPException(
        status_code=status_code,
        detail={
            "success": False,
            "error": error_data
        }
    )
