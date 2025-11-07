"""
Agent API Routes
Endpoints for AI agent account management (User-Authenticated)
"""

import asyncio
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional, List
import logging
import requests

from api.dependencies import get_current_user
from agent_account_manager import AgentAccountManager
from stellar_sdk.server import Server
import os

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

# Initialize Stellar server
HORIZON_URL = os.getenv("HORIZON_URL", "https://horizon-testnet.stellar.org")
FRIENDBOT_URL = os.getenv("FRIENDBOT_URL", "https://friendbot.stellar.org")
server = Server(HORIZON_URL)

@router.post("/create-account")
async def create_account(
    request: AccountCreateRequest,
    current_user: dict = Depends(get_current_user)
):
    """Create new agent account for authenticated user"""
    try:
        manager = AgentAccountManager()
        result = manager.create_account(
            user_id=current_user['id'],
            name=request.name
        )

        if not result.get("success"):
            raise HTTPException(
                status_code=400,
                detail=result.get("error", "Failed to create account")
            )

        # Fund with friendbot (testnet only)
        try:
            response = requests.get(f"{FRIENDBOT_URL}?addr={result['address']}")
            result['funded'] = response.status_code == 200
        except Exception as e:
            logger.warning(f"Friendbot funding failed: {e}")
            result['funded'] = False

        # Get balance
        try:
            account = server.load_account(result['address'])
            balance = 0
            for bal in account.raw_data.get('balances', []):
                if bal.get('asset_type') == 'native':
                    balance = float(bal.get('balance', 0))
                    break
            result['balance'] = balance
        except Exception as e:
            logger.warning(f"Could not load account balance: {e}")
            result['balance'] = 0

        result['network'] = 'testnet'
        return result

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating agent account: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/accounts")
async def list_accounts(
    current_user: dict = Depends(get_current_user)
):
    """List agent accounts for authenticated user only"""
    try:
        manager = AgentAccountManager()
        accounts = manager.get_user_accounts(current_user['id'])

        # Enhance with Stellar network data
        enhanced_accounts = []
        for account in accounts:
            try:
                stellar_account = server.load_account(account['address'])
                balance = 0
                for bal in stellar_account.raw_data.get('balances', []):
                    if bal.get('asset_type') == 'native':
                        balance = float(bal.get('balance', 0))
                        break
                account['balance'] = balance
                account['network'] = 'testnet'
            except Exception as e:
                logger.warning(f"Could not load account {account['address']}: {e}")
                account['balance'] = 0
                account['network'] = 'testnet'

            enhanced_accounts.append(account)

        return enhanced_accounts

    except Exception as e:
        logger.error(f"Error listing accounts: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/accounts/{address}")
async def get_account_info(
    address: str,
    current_user: dict = Depends(get_current_user)
):
    """Get detailed account information (only if owned by user)"""
    try:
        manager = AgentAccountManager()

        # Permission check
        if not manager.has_account(current_user['id'], address):
            raise HTTPException(
                status_code=404,
                detail="Account not found or not owned by user"
            )

        # Get Stellar account data
        try:
            account = server.load_account(address)
            balance = 0
            for bal in account.raw_data.get('balances', []):
                if bal.get('asset_type') == 'native':
                    balance = float(bal.get('balance', 0))
                    break

            accounts = manager.get_user_accounts(current_user['id'])
            account_info = next((a for a in accounts if a['address'] == address), None)

            return {
                "address": address,
                "balance": balance,
                "name": account_info['name'] if account_info else "Unknown",
                "created_at": account_info['created_at'] if account_info else None,
                "network": "testnet",
                "success": True
            }

        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting agent account info: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/accounts/{address}")
async def delete_account(
    address: str,
    current_user: dict = Depends(get_current_user)
):
    """Delete agent account (only if owned by user)"""
    try:
        manager = AgentAccountManager()
        success = manager.delete_account(current_user['id'], address)

        if not success:
            raise HTTPException(
                status_code=404,
                detail="Account not found or not owned by user"
            )

        return {"success": True, "message": "Account deleted"}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting account: {e}")
        raise HTTPException(status_code=500, detail=str(e))