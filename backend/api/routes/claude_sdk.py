"""
Claude SDK API Routes
Provides endpoints for research, analysis, and advanced reasoning using Claude Agent SDK.

These routes complement the existing LangChain-based chat endpoint with
specialized research and analysis capabilities.
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import logging

from agent.claude_sdk_wrapper import get_claude_sdk_agent

logger = logging.getLogger(__name__)

router = APIRouter()


# Request/Response Models
class SimpleQueryRequest(BaseModel):
    """Simple query request"""
    prompt: str


class StrategyAnalysisRequest(BaseModel):
    """Strategy analysis request"""
    strategy_description: str
    market_context: Optional[Dict[str, Any]] = None


class YieldResearchRequest(BaseModel):
    """Yield research request"""
    asset: str = "USDC"
    min_apy: float = 0.0


class StrategyReportRequest(BaseModel):
    """Strategy report request"""
    user_positions: List[Dict[str, Any]]
    performance_data: Dict[str, Any]


class ApiResponse(BaseModel):
    """Standard API response"""
    success: bool
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None


# Endpoints
@router.post("/query", response_model=ApiResponse)
async def claude_query(request: SimpleQueryRequest):
    """
    Simple query endpoint using Claude SDK.

    Use this for:
    - General research questions
    - Strategy brainstorming
    - Market insights
    - Complex reasoning tasks
    """
    try:
        agent = await get_claude_sdk_agent()
        result = await agent.query_simple(request.prompt)

        return ApiResponse(
            success=True,
            data={"response": result}
        )
    except Exception as e:
        logger.error(f"Error in Claude SDK query: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/analyze-strategy", response_model=ApiResponse)
async def analyze_strategy(request: StrategyAnalysisRequest):
    """
    Analyze a DeFi strategy using Claude SDK's advanced reasoning.

    This endpoint provides:
    - Risk assessment
    - Expected returns analysis
    - Potential issues identification
    - Optimization recommendations
    - Strategy comparison

    Example:
    ```json
    {
      "strategy_description": "Supply USDC to Blend Capital and stake BLND tokens",
      "market_context": {
        "usdc_supply_apy": "8.5%",
        "blnd_staking_apy": "15%"
      }
    }
    ```
    """
    try:
        agent = await get_claude_sdk_agent()
        result = await agent.analyze_strategy(
            strategy_description=request.strategy_description,
            market_context=request.market_context
        )

        if not result["success"]:
            raise HTTPException(status_code=500, detail=result.get("error", "Analysis failed"))

        return ApiResponse(
            success=True,
            data=result
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error analyzing strategy: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/research-yield", response_model=ApiResponse)
async def research_yield(request: YieldResearchRequest):
    """
    Research yield farming opportunities using Claude SDK.

    This endpoint:
    - Searches for current yield opportunities
    - Analyzes risk-adjusted returns
    - Provides recommendations
    - Considers historical performance

    Example:
    ```json
    {
      "asset": "USDC",
      "min_apy": 5.0
    }
    ```
    """
    try:
        agent = await get_claude_sdk_agent()
        result = await agent.research_yield_opportunities(
            asset=request.asset,
            min_apy=request.min_apy
        )

        if not result["success"]:
            raise HTTPException(status_code=500, detail=result.get("error", "Research failed"))

        return ApiResponse(
            success=True,
            data=result
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error researching yield: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/generate-report", response_model=ApiResponse)
async def generate_report(request: StrategyReportRequest):
    """
    Generate a comprehensive strategy performance report.

    This endpoint provides:
    - Executive summary
    - Position-by-position analysis
    - Overall portfolio performance
    - Risk assessment
    - Optimization recommendations

    Example:
    ```json
    {
      "user_positions": [
        {
          "protocol": "Blend Capital",
          "asset": "USDC",
          "amount": 1000,
          "apy": 8.5
        }
      ],
      "performance_data": {
        "total_invested": 1000,
        "current_value": 1085,
        "roi": 8.5,
        "time_period": "30 days"
      }
    }
    ```
    """
    try:
        agent = await get_claude_sdk_agent()
        result = await agent.generate_strategy_report(
            user_positions=request.user_positions,
            performance_data=request.performance_data
        )

        if not result["success"]:
            raise HTTPException(status_code=500, detail=result.get("error", "Report generation failed"))

        return ApiResponse(
            success=True,
            data=result
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating report: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/status", response_model=ApiResponse)
async def claude_sdk_status():
    """
    Get Claude SDK integration status.

    Returns information about:
    - Whether Claude SDK is available
    - Configured tools
    - API key status
    """
    try:
        import os
        from config.settings import settings

        api_key_configured = bool(os.getenv("ANTHROPIC_API_KEY"))

        return ApiResponse(
            success=True,
            data={
                "enabled": settings.enable_claude_sdk,
                "api_key_configured": api_key_configured,
                "features": [
                    "simple_query",
                    "strategy_analysis",
                    "yield_research",
                    "report_generation"
                ],
                "status": "ready" if api_key_configured else "api_key_required"
            }
        )
    except Exception as e:
        logger.error(f"Error getting Claude SDK status: {e}")
        return ApiResponse(
            success=False,
            error=str(e)
        )
