"""
Vault API Routes
FastAPI routes for TuxedoVault operations
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
import logging

from vault_manager import get_vault_manager

logger = logging.getLogger(__name__)

router = APIRouter()


# Request/Response Models
class DepositRequest(BaseModel):
    """Deposit request model"""

    amount: float
    asset: str = "USDC"
    wallet_address: str


class WithdrawRequest(BaseModel):
    """Withdraw request model"""

    shares: float
    wallet_address: str


class VaultStatsResponse(BaseModel):
    """Vault statistics response"""

    tvl: float
    share_value: float
    total_shares: float
    apy: float
    initial_deposits: float


class UserSharesResponse(BaseModel):
    """User shares response"""

    shares: float
    wallet_address: str


# Vault Stats Endpoint
@router.get("/vault/stats", response_model=VaultStatsResponse)
async def get_vault_stats():
    """
    Get current vault statistics

    Returns:
        VaultStatsResponse: Current vault TVL, share value, APY, etc.
    """
    vault = get_vault_manager()
    if not vault:
        raise HTTPException(
            status_code=503,
            detail="Vault not configured. Please set VAULT_CONTRACT_ID and VAULT_AGENT_SECRET environment variables.",
        )

    try:
        stats = await vault.get_vault_stats()

        if stats["status"] == "error":
            raise HTTPException(status_code=500, detail=stats["message"])

        # Convert from stroops to decimal
        tvl = stats.get("tvl", 0) / 1e7
        share_value = stats.get("share_value", 10_000_000) / 1e7
        total_shares = stats.get("total_shares", 0) / 1e7
        initial_deposits = stats.get("initial_deposits", 0) / 1e7

        # Calculate APY
        apy = vault.calculate_apy(
            int(initial_deposits * 1e7), int(tvl * 1e7), days=30
        )

        return VaultStatsResponse(
            tvl=tvl,
            share_value=share_value,
            total_shares=total_shares,
            apy=apy,
            initial_deposits=initial_deposits,
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching vault stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# User Shares Endpoint
@router.get("/vault/user/{wallet_address}/shares", response_model=UserSharesResponse)
async def get_user_shares(wallet_address: str):
    """
    Get user's vault share balance

    Args:
        wallet_address: User's Stellar address

    Returns:
        UserSharesResponse: User's share balance
    """
    vault = get_vault_manager()
    if not vault:
        raise HTTPException(
            status_code=503,
            detail="Vault not configured. Please set VAULT_CONTRACT_ID and VAULT_AGENT_SECRET environment variables.",
        )

    try:
        result = await vault.get_user_shares(wallet_address)

        if result["status"] == "error":
            raise HTTPException(status_code=500, detail=result["message"])

        shares = result.get("shares", 0) / 1e7

        return UserSharesResponse(shares=shares, wallet_address=wallet_address)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching user shares: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Deposit Endpoint
@router.post("/vault/deposit")
async def deposit_to_vault(request: DepositRequest):
    """
    Deposit assets to vault (returns unsigned transaction)

    Args:
        request: Deposit request with amount, asset, and wallet address

    Returns:
        dict: Transaction status and details
    """
    vault = get_vault_manager()
    if not vault:
        raise HTTPException(
            status_code=503,
            detail="Vault not configured. Please set VAULT_CONTRACT_ID and VAULT_AGENT_SECRET environment variables.",
        )

    try:
        # Convert to stroops
        amount_stroops = int(request.amount * 1e7)

        result = await vault.deposit_to_vault(
            user_address=request.wallet_address,
            amount=amount_stroops,
            user_keypair=None,  # User will sign via wallet
        )

        if result["status"] == "error":
            raise HTTPException(status_code=500, detail=result["message"])

        return {
            "status": result["status"],
            "message": result["message"],
            "unsigned_tx": result.get("unsigned_tx"),
            "amount": request.amount,
            "asset": request.asset,
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing deposit: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Withdraw Endpoint
@router.post("/vault/withdraw")
async def withdraw_from_vault(request: WithdrawRequest):
    """
    Withdraw assets from vault (returns unsigned transaction)

    Args:
        request: Withdraw request with shares and wallet address

    Returns:
        dict: Transaction status and details
    """
    vault = get_vault_manager()
    if not vault:
        raise HTTPException(
            status_code=503,
            detail="Vault not configured. Please set VAULT_CONTRACT_ID and VAULT_AGENT_SECRET environment variables.",
        )

    try:
        # Convert to stroops
        shares_stroops = int(request.shares * 1e7)

        result = await vault.withdraw_from_vault(
            user_address=request.wallet_address,
            shares=shares_stroops,
            user_keypair=None,  # User will sign via wallet
        )

        if result["status"] == "error":
            raise HTTPException(status_code=500, detail=result["message"])

        return {
            "status": result["status"],
            "message": result["message"],
            "unsigned_tx": result.get("unsigned_tx"),
            "shares": request.shares,
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing withdrawal: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Distribute Yield Endpoint (Admin/Agent only in production)
@router.post("/vault/distribute-yield")
async def distribute_yield():
    """
    Distribute accumulated yield in the vault
    Fee structure: 98% stays with users, 2% to platform

    Returns:
        dict: Transaction status and details
    """
    vault = get_vault_manager()
    if not vault:
        raise HTTPException(
            status_code=503,
            detail="Vault not configured. Please set VAULT_CONTRACT_ID and VAULT_AGENT_SECRET environment variables.",
        )

    try:
        # Call with agent keypair
        result = await vault.distribute_yield(vault.agent)

        if result["status"] == "error":
            raise HTTPException(status_code=500, detail=result["message"])

        return {
            "status": result["status"],
            "message": result["message"],
            "tx_hash": result.get("tx_hash"),
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error distributing yield: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Agent Strategy Execution Endpoint (Agent only)
@router.post("/vault/agent/execute")
async def agent_execute_strategy(
    strategy: str, pool: str, asset: str, amount: float
):
    """
    Agent executes a yield strategy (Blend supply/withdraw)
    This endpoint should be restricted to agent operations only

    Args:
        strategy: "supply" or "withdraw"
        pool: Blend pool contract address
        asset: Asset contract address
        amount: Amount to supply/withdraw

    Returns:
        dict: Transaction status and details
    """
    vault = get_vault_manager()
    if not vault:
        raise HTTPException(
            status_code=503,
            detail="Vault not configured. Please set VAULT_CONTRACT_ID and VAULT_AGENT_SECRET environment variables.",
        )

    # Validate strategy
    if strategy not in ["supply", "withdraw"]:
        raise HTTPException(
            status_code=400, detail="Invalid strategy. Must be 'supply' or 'withdraw'"
        )

    try:
        # Convert to stroops
        amount_stroops = int(amount * 1e7)

        result = await vault.agent_execute_strategy(
            strategy=strategy, pool=pool, asset=asset, amount=amount_stroops
        )

        if result["status"] == "error":
            raise HTTPException(status_code=500, detail=result["message"])

        return {
            "status": result["status"],
            "message": result["message"],
            "tx_hash": result.get("tx_hash"),
            "strategy": strategy,
            "amount": amount,
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error executing agent strategy: {e}")
        raise HTTPException(status_code=500, detail=str(e))
