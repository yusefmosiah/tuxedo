"""
Portfolio API Routes - Chain-agnostic wallet management
"""
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional, List
import logging

from api.dependencies import get_current_user
from portfolio_manager import PortfolioManager

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/portfolio", tags=["portfolio"])


# Request/Response Models
class CreatePortfolioRequest(BaseModel):
    name: str = "Main Portfolio"


class GenerateAccountRequest(BaseModel):
    portfolio_id: str
    chain: str
    name: Optional[str] = None


class ImportAccountRequest(BaseModel):
    portfolio_id: str
    chain: str
    private_key: str
    name: Optional[str] = None


class ExportAccountRequest(BaseModel):
    account_id: str


# Routes
@router.post("/portfolios")
async def create_portfolio(
    request: CreatePortfolioRequest,
    current_user: dict = Depends(get_current_user)
):
    """Create new portfolio for authenticated user"""
    try:
        manager = PortfolioManager()
        result = manager.create_portfolio(
            user_id=current_user['id'],
            name=request.name
        )

        if not result.get("success"):
            raise HTTPException(
                status_code=400,
                detail=result.get("error", "Failed to create portfolio")
            )

        return result

    except Exception as e:
        logger.error(f"Error creating portfolio: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/portfolios")
async def list_portfolios(current_user: dict = Depends(get_current_user)):
    """List all portfolios for authenticated user"""
    try:
        manager = PortfolioManager()
        portfolios = manager.get_user_portfolios(current_user['id'])

        return {
            "portfolios": portfolios,
            "count": len(portfolios)
        }

    except Exception as e:
        logger.error(f"Error listing portfolios: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/accounts/generate")
async def generate_account(
    request: GenerateAccountRequest,
    current_user: dict = Depends(get_current_user)
):
    """Generate new blockchain account in portfolio"""
    try:
        manager = PortfolioManager()
        result = manager.generate_account(
            user_id=current_user['id'],
            portfolio_id=request.portfolio_id,
            chain=request.chain,
            name=request.name
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


@router.post("/accounts/import")
async def import_account(
    request: ImportAccountRequest,
    current_user: dict = Depends(get_current_user)
):
    """
    Import existing wallet into portfolio
    KILLER FEATURE: Bridges existing DeFi users into Tuxedo
    """
    try:
        manager = PortfolioManager()
        result = manager.import_account(
            user_id=current_user['id'],
            portfolio_id=request.portfolio_id,
            chain=request.chain,
            private_key=request.private_key,
            name=request.name
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


@router.post("/accounts/export")
async def export_account(
    request: ExportAccountRequest,
    current_user: dict = Depends(get_current_user)
):
    """
    Export wallet private key
    KILLER FEATURE: Users maintain full custodial control
    """
    try:
        manager = PortfolioManager()
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


@router.get("/portfolios/{portfolio_id}/accounts")
async def list_portfolio_accounts(
    portfolio_id: str,
    chain: Optional[str] = None,
    current_user: dict = Depends(get_current_user)
):
    """List all accounts in portfolio, optionally filtered by chain"""
    try:
        manager = PortfolioManager()
        accounts = manager.get_portfolio_accounts(
            user_id=current_user['id'],
            portfolio_id=portfolio_id,
            chain=chain
        )

        return {
            "portfolio_id": portfolio_id,
            "accounts": accounts,
            "count": len(accounts)
        }

    except Exception as e:
        logger.error(f"Error listing accounts: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/supported-chains")
async def get_supported_chains():
    """Get list of supported blockchain networks"""
    manager = PortfolioManager()
    return {
        "chains": list(manager.chains.keys()),
        "count": len(manager.chains)
    }
