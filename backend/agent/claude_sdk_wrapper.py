"""
Claude Agent SDK Wrapper
Provides integration between Claude Agent SDK and Tuxedo's existing system.

This module enables hybrid agent capabilities:
- LangChain for tool execution (existing Stellar/Blend/Vault operations)
- Claude SDK for research, analysis, and advanced reasoning
"""

import os
import asyncio
import logging
from typing import Optional, Dict, Any, List, AsyncIterator
from pathlib import Path

# Claude SDK imports
from claude_agent_sdk import query, ClaudeAgentOptions
from claude_agent_sdk.client import ClaudeSDKClient, Message

logger = logging.getLogger(__name__)

# SDK instance (singleton pattern)
_claude_sdk_client: Optional[ClaudeSDKClient] = None


class ClaudeSDKAgent:
    """
    Wrapper for Claude Agent SDK providing research and analysis capabilities.

    Use this for:
    - Strategy research and analysis
    - Market insights and trends
    - Document generation
    - Complex reasoning tasks

    Use LangChain core.py for:
    - Stellar tool execution
    - Blend Capital operations
    - Vault management
    - Real-time blockchain interactions
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        working_directory: Optional[str] = None,
        allowed_tools: Optional[List[str]] = None,
        use_bedrock: bool = False
    ):
        """
        Initialize Claude SDK Agent.

        Supports both direct Anthropic API and AWS Bedrock authentication.

        Args:
            api_key: Anthropic API key (defaults to ANTHROPIC_API_KEY env var)
                    For Bedrock, this can be None (uses AWS credentials)
            working_directory: Working directory for file operations
            allowed_tools: List of allowed tools (defaults to Read, Write, Bash, WebSearch)
            use_bedrock: Use AWS Bedrock instead of direct Anthropic API
        """
        self.use_bedrock = use_bedrock or os.getenv("CLAUDE_SDK_USE_BEDROCK", "false").lower() == "true"

        # Authentication setup
        if self.use_bedrock:
            # AWS Bedrock authentication via environment variables
            # Supports two methods:
            # 1. Single-key: AWS_BEARER_TOKEN_BEDROCK (recommended, simpler)
            # 2. Traditional: AWS_ACCESS_KEY_ID + AWS_SECRET_ACCESS_KEY
            self.aws_region = os.getenv("AWS_REGION", "us-east-1")
            self.aws_bearer_token = os.getenv("AWS_BEARER_TOKEN_BEDROCK")
            self.aws_access_key_id = os.getenv("AWS_ACCESS_KEY_ID")
            self.aws_secret_access_key = os.getenv("AWS_SECRET_ACCESS_KEY")

            if self.aws_bearer_token:
                # New single-key authentication method (July 2025+)
                logger.info(f"✅ Using AWS Bedrock API Key authentication (region: {self.aws_region})")
            elif self.aws_access_key_id and self.aws_secret_access_key:
                # Traditional access key + secret key method
                logger.info(f"✅ Using AWS Bedrock IAM credentials (region: {self.aws_region})")
            else:
                logger.warning(
                    "AWS Bedrock enabled but credentials not found. "
                    "Set either:\n"
                    "  1. AWS_BEARER_TOKEN_BEDROCK (single API key, recommended)\n"
                    "  2. AWS_ACCESS_KEY_ID + AWS_SECRET_ACCESS_KEY (traditional method)"
                )

            self.api_key = None  # Not used for Bedrock
        else:
            # Direct Anthropic API authentication
            self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
            if not self.api_key:
                logger.warning(
                    "No ANTHROPIC_API_KEY found - Claude SDK features will be limited. "
                    "Set ANTHROPIC_API_KEY or enable AWS Bedrock with CLAUDE_SDK_USE_BEDROCK=true"
                )

        self.working_directory = working_directory or os.getcwd()

        # Default allowed tools for research/analysis
        self.allowed_tools = allowed_tools or [
            "Read",
            "Write",
            "WebSearch",
            "Bash"
        ]

        # Configure options
        self.options = ClaudeAgentOptions(
            allowed_tools=self.allowed_tools,
            permission_mode='acceptEdits',  # Auto-accept edits for seamless operation
            cwd=self.working_directory
        )

        auth_method = "AWS Bedrock" if self.use_bedrock else "Direct Anthropic API"
        logger.info(f"Claude SDK Agent initialized with {auth_method}")
        logger.info(f"Allowed tools: {self.allowed_tools}")

    async def query_simple(self, prompt: str) -> str:
        """
        Simple query interface - single turn conversation.

        Args:
            prompt: User prompt/query

        Returns:
            Agent response as string
        """
        try:
            response_text = ""
            async for message in query(prompt=prompt):
                if hasattr(message, 'content'):
                    response_text += str(message.content)

            return response_text
        except Exception as e:
            logger.error(f"Error in Claude SDK simple query: {e}")
            raise

    async def analyze_strategy(
        self,
        strategy_description: str,
        market_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Analyze a DeFi strategy using Claude SDK's advanced reasoning.

        Args:
            strategy_description: Description of the strategy to analyze
            market_context: Optional market data/context

        Returns:
            Analysis results with recommendations
        """
        context_str = ""
        if market_context:
            context_str = f"\n\nMarket Context:\n{self._format_market_context(market_context)}"

        prompt = f"""
Analyze the following DeFi strategy for the Stellar ecosystem:

Strategy: {strategy_description}
{context_str}

Provide a comprehensive analysis including:
1. Risk assessment
2. Expected returns
3. Potential issues
4. Recommendations for optimization
5. Comparison to alternative strategies

Focus on Stellar-specific considerations (Soroban contracts, Blend Capital, etc.)
"""

        try:
            analysis = await self.query_simple(prompt)

            return {
                "success": True,
                "strategy": strategy_description,
                "analysis": analysis,
                "market_context": market_context
            }
        except Exception as e:
            logger.error(f"Error analyzing strategy: {e}")
            return {
                "success": False,
                "error": str(e),
                "strategy": strategy_description
            }

    async def research_yield_opportunities(
        self,
        asset: str = "USDC",
        min_apy: float = 0.0
    ) -> Dict[str, Any]:
        """
        Research yield opportunities across Stellar DeFi protocols.

        Args:
            asset: Asset to find yield for (e.g., "USDC", "XLM")
            min_apy: Minimum APY threshold

        Returns:
            Research findings and recommendations
        """
        prompt = f"""
Research current yield farming opportunities for {asset} on Stellar blockchain.

Requirements:
- Minimum APY: {min_apy}%
- Focus on: Blend Capital, Soroswap, other major Stellar DeFi protocols
- Consider: Safety, liquidity, historical performance

Provide:
1. Top 3-5 opportunities ranked by risk-adjusted returns
2. Brief analysis of each opportunity
3. Risk factors to consider
4. Recommended allocation strategy

Use web search to find current APY rates and market conditions.
"""

        try:
            research = await self.query_simple(prompt)

            return {
                "success": True,
                "asset": asset,
                "min_apy": min_apy,
                "research": research,
                "timestamp": asyncio.get_event_loop().time()
            }
        except Exception as e:
            logger.error(f"Error researching yield opportunities: {e}")
            return {
                "success": False,
                "error": str(e),
                "asset": asset
            }

    async def generate_strategy_report(
        self,
        user_positions: List[Dict[str, Any]],
        performance_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Generate a comprehensive strategy performance report.

        Args:
            user_positions: User's current DeFi positions
            performance_data: Historical performance metrics

        Returns:
            Generated report
        """
        prompt = f"""
Generate a comprehensive DeFi strategy performance report for a Stellar user.

Current Positions:
{self._format_positions(user_positions)}

Performance Data:
{self._format_performance(performance_data)}

Please provide:
1. Executive summary
2. Position-by-position analysis
3. Overall portfolio performance
4. Risk assessment
5. Optimization recommendations
6. Next steps and action items

Format the report in clear, professional markdown.
"""

        try:
            report = await self.query_simple(prompt)

            return {
                "success": True,
                "report": report,
                "positions_analyzed": len(user_positions),
                "timestamp": asyncio.get_event_loop().time()
            }
        except Exception as e:
            logger.error(f"Error generating strategy report: {e}")
            return {
                "success": False,
                "error": str(e)
            }

    def _format_market_context(self, market_context: Dict[str, Any]) -> str:
        """Format market context for prompts"""
        lines = []
        for key, value in market_context.items():
            lines.append(f"- {key}: {value}")
        return "\n".join(lines)

    def _format_positions(self, positions: List[Dict[str, Any]]) -> str:
        """Format user positions for prompts"""
        if not positions:
            return "No active positions"

        lines = []
        for i, pos in enumerate(positions, 1):
            lines.append(f"\nPosition {i}:")
            for key, value in pos.items():
                lines.append(f"  {key}: {value}")
        return "\n".join(lines)

    def _format_performance(self, performance: Dict[str, Any]) -> str:
        """Format performance data for prompts"""
        lines = []
        for key, value in performance.items():
            lines.append(f"- {key}: {value}")
        return "\n".join(lines)


# Global instance management
async def get_claude_sdk_agent() -> ClaudeSDKAgent:
    """
    Get or create global Claude SDK Agent instance.
    Reads configuration from settings to determine authentication method.

    Returns:
        Initialized ClaudeSDKAgent
    """
    # For now, create a new instance each time
    # In production, you might want to implement proper singleton pattern
    try:
        from config.settings import settings

        agent = ClaudeSDKAgent(
            use_bedrock=settings.claude_sdk_use_bedrock
        )
        return agent
    except ImportError:
        # Fallback if settings not available
        logger.warning("Settings not available, using environment variables directly")
        agent = ClaudeSDKAgent()
        return agent
    except Exception as e:
        logger.error(f"Error creating Claude SDK agent: {e}")
        raise


async def initialize_claude_sdk():
    """
    Initialize Claude SDK integration.
    Called during app startup.

    Supports both direct Anthropic API and AWS Bedrock authentication.
    """
    try:
        from config.settings import settings

        use_bedrock = settings.claude_sdk_use_bedrock

        # Check authentication method and credentials
        if use_bedrock:
            # AWS Bedrock authentication
            # Supports two methods:
            # 1. Single-key: AWS_BEARER_TOKEN_BEDROCK (recommended, simpler)
            # 2. Traditional: AWS_ACCESS_KEY_ID + AWS_SECRET_ACCESS_KEY
            aws_bearer_token = os.getenv("AWS_BEARER_TOKEN_BEDROCK")
            aws_access_key = os.getenv("AWS_ACCESS_KEY_ID")
            aws_secret_key = os.getenv("AWS_SECRET_ACCESS_KEY")
            aws_region = os.getenv("AWS_REGION", "us-east-1")

            if aws_bearer_token:
                logger.info(f"Initializing Claude SDK with AWS Bedrock API Key (region: {aws_region})")
            elif aws_access_key and aws_secret_key:
                logger.info(f"Initializing Claude SDK with AWS Bedrock IAM credentials (region: {aws_region})")
            else:
                logger.warning(
                    "CLAUDE_SDK_USE_BEDROCK=true but AWS credentials not found. "
                    "Set either:\n"
                    "  1. AWS_BEARER_TOKEN_BEDROCK (single API key, recommended)\n"
                    "  2. AWS_ACCESS_KEY_ID + AWS_SECRET_ACCESS_KEY (traditional method)"
                )
                return
        else:
            # Direct Anthropic API authentication
            api_key = os.getenv("ANTHROPIC_API_KEY")
            if not api_key:
                logger.warning(
                    "ANTHROPIC_API_KEY not set - Claude SDK features will be limited. "
                    "Set ANTHROPIC_API_KEY or configure AWS Bedrock to enable advanced research and analysis."
                )
                return

            logger.info("Initializing Claude SDK with direct Anthropic API")

        # Test basic functionality
        agent = await get_claude_sdk_agent()
        logger.info("✅ Claude SDK initialized successfully")
        auth_method = "AWS Bedrock" if use_bedrock else "Anthropic API"
        logger.info(f"   Authentication: {auth_method}")
        logger.info(f"   Allowed tools: {agent.allowed_tools}")
        logger.info(f"   Working directory: {agent.working_directory}")

    except ImportError:
        logger.warning("Settings not available, Claude SDK initialization skipped")
    except Exception as e:
        logger.error(f"Failed to initialize Claude SDK: {e}")
        logger.warning("Claude SDK features will be unavailable")


async def cleanup_claude_sdk():
    """
    Cleanup Claude SDK resources.
    Called during app shutdown.
    """
    logger.info("Claude SDK cleaned up")


# Example usage and testing
async def test_claude_sdk():
    """Test Claude SDK integration"""
    print("🧪 Testing Claude SDK Integration...")

    agent = await get_claude_sdk_agent()

    # Test 1: Simple query
    print("\n1️⃣ Testing simple query...")
    result = await agent.query_simple("What is Stellar blockchain?")
    print(f"Result: {result[:200]}...")

    # Test 2: Strategy analysis
    print("\n2️⃣ Testing strategy analysis...")
    analysis = await agent.analyze_strategy(
        strategy_description="Supply USDC to Blend Capital and stake BLND tokens",
        market_context={
            "usdc_supply_apy": "8.5%",
            "blnd_staking_apy": "15%",
            "usdc_price": "$1.00",
            "blnd_price": "$0.35"
        }
    )
    print(f"Analysis success: {analysis['success']}")
    if analysis['success']:
        print(f"Analysis preview: {analysis['analysis'][:200]}...")

    # Test 3: Yield research
    print("\n3️⃣ Testing yield research...")
    research = await agent.research_yield_opportunities(
        asset="USDC",
        min_apy=5.0
    )
    print(f"Research success: {research['success']}")
    if research['success']:
        print(f"Research preview: {research['research'][:200]}...")

    print("\n✅ All tests completed!")


if __name__ == "__main__":
    # Run tests if executed directly
    asyncio.run(test_claude_sdk())
