"""
Account API Routes - Chain-agnostic wallet management
Provides primitives for agents to manage user accounts
"""
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import logging

from api.dependencies import get_current_user
from account_manager import AccountManager

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/accounts", tags=["accounts"])

# Pydantic request/response models
class GenerateAccountRequest(BaseModel):
    chain: str
    name: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

class ImportAccountRequest(BaseModel):
    chain: str
    private_key: str
    name: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

class ExportAccountRequest(BaseModel):
    account_id: str

class DeleteAccountRequest(BaseModel):
    account_id: str

@router.post("/generate")
async def generate_account(
    request: GenerateAccountRequest,
    current_user: dict = Depends(get_current_user)
):
    """Generate new blockchain account for user"""
    try:
        manager = AccountManager()
        result = manager.generate_account(
            user_id=current_user['id'],
            chain=request.chain,
            name=request.name,
            metadata=request.metadata
        )

        if not result.get("success"):
            raise HTTPException(
                status_code=400,
                detail=result.get("error", "Failed to generate account")
            )

        return result

    except Exception as e:
        logger.error(f"Error generating account: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/import")
async def import_account(
    request: ImportAccountRequest,
    current_user: dict = Depends(get_current_user)
):
    """
    Import existing wallet for user
    KILLER FEATURE: Bridges existing DeFi users into Tuxedo
    """
    try:
        manager = AccountManager()
        result = manager.import_account(
            user_id=current_user['id'],
            chain=request.chain,
            private_key=request.private_key,
            name=request.name,
            metadata=request.metadata
        )

        if not result.get("success"):
            raise HTTPException(
                status_code=400,
                detail=result.get("error", "Failed to import account")
            )

        return result

    except Exception as e:
        logger.error(f"Error importing account: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/export")
async def export_account(
    request: ExportAccountRequest,
    current_user: dict = Depends(get_current_user)
):
    """
    Export wallet private key
    KILLER FEATURE: Users maintain full custodial control
    """
    try:
        manager = AccountManager()
        result = manager.export_account(
            user_id=current_user['id'],
            account_id=request.account_id
        )

        if not result.get("success"):
            raise HTTPException(
                status_code=400,
                detail=result.get("error", "Failed to export account")
            )

        # Log export for security audit
        logger.warning(
            f"User {current_user['id']} exported account {request.account_id}"
        )

        return result

    except Exception as e:
        logger.error(f"Error exporting account: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("")
async def list_user_accounts(
    chain: Optional[str] = None,
    current_user: dict = Depends(get_current_user)
):
    """
    List all accounts for user, optionally filtered by chain
    Agent constructs portfolio views from this data
    """
    try:
        manager = AccountManager()
        accounts = manager.get_user_accounts(
            user_id=current_user['id'],
            chain=chain
        )

        return {
            "user_id": current_user['id'],
            "accounts": accounts,
            "count": len(accounts)
        }

    except Exception as e:
        logger.error(f"Error listing accounts: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("")
async def delete_account(
    request: DeleteAccountRequest,
    current_user: dict = Depends(get_current_user)
):
    """
    Delete an account
    """
    try:
        manager = AccountManager()
        result = manager.delete_account(
            user_id=current_user['id'],
            account_id=request.account_id
        )

        if not result.get("success"):
            raise HTTPException(
                status_code=400,
                detail=result.get("error", "Failed to delete account")
            )

        # Log deletion for security audit
        logger.warning(
            f"User {current_user['id']} deleted account {request.account_id}"
        )

        return result

    except Exception as e:
        logger.error(f"Error deleting account: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/chains")
async def list_supported_chains(
    current_user: dict = Depends(get_current_user)
):
    """
    List all supported blockchain networks
    """
    try:
        manager = AccountManager()
        chains = list(manager.chains.keys())

        return {
            "chains": chains,
            "count": len(chains)
        }

    except Exception as e:
        logger.error(f"Error listing chains: {e}")
        raise HTTPException(status_code=500, detail=str(e))
