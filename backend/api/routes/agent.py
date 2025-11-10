"""
Agent API Routes
Endpoints for AI agent account management

✅ QUANTUM LEAP COMPLETE - USER-ISOLATED ✅
All agent accounts are now user-specific and authenticated
"""

import asyncio
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import logging

from api.dependencies import get_current_user

logger = logging.getLogger(__name__)

router = APIRouter()

# Pydantic models
class AccountCreateRequest(BaseModel):
    name: Optional[str] = None

class AccountResponse(BaseModel):
    address: str
    name: str
    balance: float
    network: str
    created_at: Optional[str] = None
    funded: Optional[bool] = None

class ErrorResponse(BaseModel):
    error: str
    success: bool = False

class ImportWalletRequest(BaseModel):
    private_key: str
    name: Optional[str] = None
    chain: str = "stellar"

class ExportAccountRequest(BaseModel):
    account_id: str

class ExportAccountResponse(BaseModel):
    chain: str
    address: str
    private_key: str
    export_format: str
    warning: str
    success: bool = True

# Import agent account management tools
try:
    from tools.agent.account_management import create_agent_account, list_agent_accounts, get_agent_account_info
    AGENT_TOOLS_AVAILABLE = True
    logger.info("✅ Agent account management tools loaded successfully")
except ImportError as e:
    logger.error(f"❌ Agent account management tools not available: {e}")
    AGENT_TOOLS_AVAILABLE = False

@router.post("/create-account")
async def create_account(
    request: AccountCreateRequest,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Create new agent-controlled account (user-authenticated)"""
    if not AGENT_TOOLS_AVAILABLE:
        raise HTTPException(status_code=503, detail="Agent account management tools not available")

    try:
        user_id = current_user['id']
        result = create_agent_account(user_id=user_id, account_name=request.name)

        if not result.get("success", True):
            raise HTTPException(status_code=400, detail=result.get("error", "Failed to create account"))

        # Get balance for the created account
        try:
            from tools.agent.account_management import get_agent_account_info
            account_info = get_agent_account_info(user_id=user_id, address=result["address"])
            balance = account_info.get("balance", 0) if account_info.get("success") else 0
        except:
            balance = 0

        return {
            "address": result["address"],
            "name": result["name"],
            "balance": balance,
            "network": result["network"],
            "funded": result.get("funded", False),
            "success": True
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating agent account: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.get("/accounts")
async def list_accounts(
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """List all agent-controlled accounts for authenticated user"""
    if not AGENT_TOOLS_AVAILABLE:
        raise HTTPException(status_code=503, detail="Agent account management tools not available")

    try:
        user_id = current_user['id']
        accounts = list_agent_accounts(user_id=user_id)

        # Handle error case
        if len(accounts) == 1 and "error" in accounts[0]:
            raise HTTPException(status_code=500, detail=accounts[0]["error"])

        return accounts

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error listing agent accounts: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.get("/accounts/{address}", response_model=AccountResponse)
async def get_account_info(
    address: str,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Get detailed account information for authenticated user"""
    if not AGENT_TOOLS_AVAILABLE:
        raise HTTPException(status_code=503, detail="Agent account management tools not available")

    try:
        user_id = current_user['id']
        result = get_agent_account_info(user_id=user_id, address=address)

        if not result.get("success", True):
            raise HTTPException(status_code=404, detail=result.get("error", "Account not found"))

        return AccountResponse(**result)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting agent account info: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.post("/import-wallet")
async def import_wallet(
    request: ImportWalletRequest,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Import external wallet into agent management

    This allows users to import their Freighter/xBull wallet into Tuxedo
    for autonomous agent signing.

    Security:
    - Requires authentication
    - Private key is encrypted with user-specific key
    - Metadata tracks import source
    """
    try:
        from account_manager import AccountManager

        user_id = current_user['id']
        account_manager = AccountManager()

        # Import account
        result = account_manager.import_account(
            user_id=user_id,
            chain=request.chain,
            private_key=request.private_key,
            name=request.name,
            network="mainnet",
            metadata={
                "type": "imported",
                "source": "external_wallet",
                "imported_at": "now"
            }
        )

        if not result.get("success"):
            raise HTTPException(status_code=400, detail=result.get("error", "Failed to import wallet"))

        logger.info(f"✅ User {user_id} imported wallet: {result['address'][:8]}...")

        return {
            "success": True,
            "account_id": result["account_id"],
            "address": result["address"],
            "name": result["name"],
            "chain": result["chain"],
            "network": result["network"],
            "message": "Wallet imported successfully. Your account is now managed by Tuxedo."
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error importing wallet: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.post("/export-account", response_model=ExportAccountResponse)
async def export_account(
    request: ExportAccountRequest,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Export agent account private key

    Allows users to export their agent-managed account to use in
    external wallets (Freighter, xBull, etc.)

    Security:
    - Requires authentication
    - Includes security warning
    - Audit logged (via logger)
    - User must confirm they understand the risks
    """
    try:
        from account_manager import AccountManager
        from agent.context import AgentContext

        user_id = current_user['id']
        account_manager = AccountManager()

        # Create agent context for permission checking
        agent_context = AgentContext(user_id=user_id)

        # Export account
        result = account_manager.export_account(
            agent_context=agent_context,
            account_id=request.account_id
        )

        if not result.get("success"):
            if "not found" in result.get("error", "").lower():
                raise HTTPException(status_code=404, detail=result.get("error", "Account not found"))
            elif "permission denied" in result.get("error", "").lower():
                raise HTTPException(status_code=403, detail=result.get("error", "Permission denied"))
            else:
                raise HTTPException(status_code=400, detail=result.get("error", "Failed to export account"))

        logger.warning(f"⚠️  User {user_id} exported account: {result['address'][:8]}...")

        return ExportAccountResponse(**result)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error exporting account: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")