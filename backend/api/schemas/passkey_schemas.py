"""
Pydantic schemas for passkey authentication endpoints
Extracted from passkey_auth.py for better organization
"""
from pydantic import BaseModel, EmailStr
from typing import Optional, List, Dict, Any


# Registration schemas
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


# Recovery codes acknowledgment schemas
class AcknowledgeRecoveryCodesRequest(BaseModel):
    pass  # Token comes from header


class AcknowledgeRecoveryCodesResponse(BaseModel):
    success: bool
    acknowledged: bool


# Login schemas
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


# Recovery code authentication schemas
class RecoveryCodeVerifyRequest(BaseModel):
    email: EmailStr
    code: str


class RecoveryCodeVerifyResponse(BaseModel):
    user: Dict[str, Any]
    session_token: str
    remaining_codes: int


# Email recovery schemas
class EmailRecoveryRequest(BaseModel):
    email: EmailStr


class EmailRecoveryCompleteRequest(BaseModel):
    token: str
    credential: Dict[str, Any]


# Session management schemas
class SessionValidateResponse(BaseModel):
    user: Dict[str, Any]
    valid: bool


# Passkey management schemas
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


# Error response schema
class ErrorResponse(BaseModel):
    success: bool = False
    error: Dict[str, Any]
