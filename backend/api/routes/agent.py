"""
Agent API Routes
Endpoints for AI agent account management
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, List
import logging

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

# Import agent account management tools
try:
    from tools.agent.account_management import create_agent_account, list_agent_accounts, get_agent_account_info
    AGENT_TOOLS_AVAILABLE = True
    logger.info("Agent account management tools loaded successfully")
except ImportError as e:
    logger.warning(f"Agent account management tools not available: {e}")
    AGENT_TOOLS_AVAILABLE = False

@router.post("/create-account")
async def create_account(request: AccountCreateRequest):
    """Create new agent-controlled account"""
    if not AGENT_TOOLS_AVAILABLE:
        raise HTTPException(status_code=503, detail="Agent account management tools not available")

    try:
        result = create_agent_account(request.name)

        if not result.get("success", True):
            raise HTTPException(status_code=400, detail=result.get("error", "Failed to create account"))

        # Get balance for the created account
        try:
            from tools.agent.account_management import get_agent_account_info
            account_info = get_agent_account_info(result["address"])
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
async def list_accounts():
    """List all agent-controlled accounts"""
    if not AGENT_TOOLS_AVAILABLE:
        raise HTTPException(status_code=503, detail="Agent account management tools not available")

    try:
        accounts = list_agent_accounts()

        # Handle error case
        if len(accounts) == 1 and "error" in accounts[0]:
            raise HTTPException(status_code=500, detail=accounts[0]["error"])

        # Enhance accounts with metadata names
        enhanced_accounts = []
        for account in accounts:
            if "error" in account:
                enhanced_accounts.append(account)
                continue

            # Get account metadata for name
            try:
                from tools.agent.account_management import get_agent_account_info
                account_info = get_agent_account_info(account["address"])
                if account_info.get("success") and account_info.get("metadata"):
                    account["name"] = account_info["metadata"].get("name", "Unnamed Account")
                else:
                    account["name"] = "Unnamed Account"
            except:
                account["name"] = "Unnamed Account"

            enhanced_accounts.append(account)

        return enhanced_accounts

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error listing agent accounts: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.get("/accounts/{address}", response_model=AccountResponse)
async def get_account_info(address: str):
    """Get detailed account information"""
    if not AGENT_TOOLS_AVAILABLE:
        raise HTTPException(status_code=503, detail="Agent account management tools not available")

    try:
        result = get_agent_account_info(address)

        if not result.get("success", True):
            raise HTTPException(status_code=404, detail=result.get("error", "Account not found"))

        return AccountResponse(**result)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting agent account info: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")