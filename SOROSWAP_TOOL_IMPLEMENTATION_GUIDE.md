# Soroswap Tool Implementation Guide

## Overview

This guide provides a comprehensive approach to integrating Soroswap functionality into the existing Tuxedo AI agent system. Soroswap is the first DEX and exchange aggregator built on Stellar, powered by Soroban smart contracts. This guide covers both API-based and direct RPC integration methods.

## Architecture Overview

### Soroswap Components

1. **Soroswap API** - RESTful API for quotes and routing
2. **Smart Contracts** - On-chain AMM implementation
3. **SDK Integration** - TypeScript/Python libraries
4. **Aggregation** - Routes across multiple Stellar DEXs

### Mainnet Contract Addresses

```
SoroswapFactory: CA4HEQTL2WPEUYKYKCDOHCDNIV4QHNJ7EL4J4NQ6VADP7SYHVRYZ7AW2
SoroswapRouter:  CAG5LRYQ5JVEUI5TEID72EYOVX44TTUJT5BQR2J6J77FH65PCCFAJDDH
Deployer:        GAYPUMZFDKUEUJ4LPTHVXVG2GD5B6AV5GGLYDMSZXCSI4QILQKSY25JI
```

## Integration Approaches

### Approach 1: Soroswap API Integration (Recommended)

**Pros:**

- Simplified integration
- Built-in routing and aggregation
- Reduced complexity
- Handles edge cases

**Cons:**

- External dependency
- Rate limiting
- Less control

### Approach 2: Direct Smart Contract Interaction

**Pros:**

- Full control
- No external API dependency
- Direct blockchain interaction
- Better for advanced use cases

**Cons:**

- More complex implementation
- Need to handle routing manually
- More error cases to manage

## Implementation Plan

### Phase 1: API Integration

#### 1.1 Install Dependencies

```bash
# Backend Python dependencies
cd backend
source .venv/bin/activate
uv add requests
uv add aiohttp  # For async HTTP requests
```

#### 1.2 Create Soroswap API Client

Create `backend/soroswap_api.py`:

```python
"""
Soroswap API Client
Provides integration with Soroswap API for quotes and routing
"""

import asyncio
import aiohttp
from typing import Dict, Any, Optional, List
import json
from urllib.parse import urljoin

class SoroswapAPIClient:
    """Client for interacting with Soroswap API"""

    def __init__(self, base_url: str = "https://api.soroswap.finance"):
        self.base_url = base_url
        self.session = None

    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()

    async def _make_request(self, endpoint: str, params: Optional[Dict] = None) -> Dict[str, Any]:
        """Make HTTP request to Soroswap API"""
        if not self.session:
            raise RuntimeError("Client not initialized. Use async context manager.")

        url = urljoin(self.base_url, endpoint)

        try:
            async with self.session.get(url, params=params) as response:
                response.raise_for_status()
                return await response.json()
        except aiohttp.ClientError as e:
            raise Exception(f"Soroswap API request failed: {str(e)}")

    async def get_contracts(self, network: str = "mainnet") -> Dict[str, str]:
        """Get contract addresses for specified network"""
        return await self._make_request(f"/api/{network}/contracts")

    async def get_quote(
        self,
        token_in: str,
        token_out: str,
        amount_in: str,
        network: str = "mainnet"
    ) -> Dict[str, Any]:
        """
        Get swap quote from Soroswap

        Args:
            token_in: Input token contract address or "native" for XLM
            token_out: Output token contract address
            amount_in: Amount to swap (in smallest units)
            network: Network (mainnet/testnet)
        """
        params = {
            "tokenIn": token_in,
            "tokenOut": token_out,
            "amountIn": amount_in
        }

        return await self._make_request(f"/api/{network}/quote", params)

    async def build_transaction(
        self,
        token_in: str,
        token_out: str,
        amount_in: str,
        slippage: float = 0.5,
        deadline: int = 3600,
        network: str = "mainnet"
    ) -> Dict[str, Any]:
        """
        Build transaction for swap

        Args:
            token_in: Input token contract address or "native"
            token_out: Output token contract address
            amount_in: Amount to swap
            slippage: Slippage tolerance in percent (default 0.5%)
            deadline: Transaction deadline in seconds (default 1 hour)
            network: Network (mainnet/testnet)
        """
        params = {
            "tokenIn": token_in,
            "tokenOut": token_out,
            "amountIn": amount_in,
            "slippage": str(slippage),
            "deadline": str(deadline)
        }

        return await self._make_request(f"/api/{network}/quote/build", params)

    async def get_pools(self, network: str = "mainnet") -> List[Dict[str, Any]]:
        """Get all available pools"""
        return await self._make_request(f"/api/{network}/pools")

    async def get_pool_info(self, pool_address: str, network: str = "mainnet") -> Dict[str, Any]:
        """Get specific pool information"""
        return await self._make_request(f"/api/{network}/pool/{pool_address}")
```

#### 1.3 Create Soroswap Tools

Create `backend/soroswap_tools.py`:

```python
"""
Soroswap DEX Tools for AI Agent
Provides swap, pool, and liquidity operations using Soroswap API
"""

import asyncio
from typing import Dict, Any, Optional, List
from stellar_sdk import Asset, Address
from soroswap_api import SoroswapAPIClient
from account_manager import AccountManager
from agent.context import AgentContext
from stellar_soroban import soroban_operations
import json

# Mainnet Contract Addresses
SOROSWAP_MAINNET_CONTRACTS = {
    "factory": "CA4HEQTL2WPEUYKYKCDOHCDNIV4QHNJ7EL4J4NQ6VADP7SYHVRYZ7AW2",
    "router": "CAG5LRYQ5JVEUI5TEID72EYOVX44TTUJT5BQR2J6J77FH65PCCFAJDDH"
}

def _parse_asset_to_address(asset: str, issuer: Optional[str] = None) -> str:
    """Convert asset specification to Soroswap format"""
    if asset.upper() == "XLM":
        return "native"
    elif issuer:
        return f"{asset}:{issuer}"
    else:
        return asset  # Assume it's already a contract address

async def soroswap_dex(
    action: str,
    agent_context: AgentContext,
    account_manager: AccountManager,
    soroban_server,
    account_id: Optional[str] = None,
    token_in: Optional[str] = None,
    token_out: Optional[str] = None,
    amount_in: Optional[str] = None,
    amount_out_min: Optional[str] = None,
    slippage: float = 0.5,
    network: str = "mainnet"
) -> Dict[str, Any]:
    """
    Unified Soroswap DEX operations tool

    Actions:
        - "quote": Get swap quote without executing
        - "swap": Execute token swap
        - "pools": Get available pools
        - "pool_info": Get specific pool information

    Args:
        action: Operation to perform
        agent_context: Agent execution context
        account_manager: AccountManager instance
        soroban_server: SorobanServerAsync instance
        account_id: Account ID (required for swap)
        token_in: Input token (symbol, contract address, or "native")
        token_out: Output token (symbol, contract address, or "native")
        amount_in: Amount to swap (in smallest units)
        amount_out_min: Minimum output amount (slippage protection)
        slippage: Slippage tolerance in percent
        network: Network (mainnet/testnet)
    """

    try:
        async with SoroswapAPIClient() as api:

            if action == "quote":
                if not token_in or not token_out or not amount_in:
                    return {"error": "token_in, token_out, and amount_in required for quote"}

                # Get quote from API
                quote_result = await api.get_quote(
                    token_in=_parse_asset_to_address(token_in),
                    token_out=token_out,  # Assume contract address for simplicity
                    amount_in=amount_in,
                    network=network
                )

                return {
                    "success": True,
                    "quote": quote_result,
                    "token_in": token_in,
                    "token_out": token_out,
                    "amount_in": amount_in
                }

            elif action == "swap":
                if not account_id:
                    return {"error": "account_id required for swap"}
                if not token_in or not token_out or not amount_in:
                    return {"error": "token_in, token_out, and amount_in required for swap"}

                # Get transaction from API
                tx_result = await api.build_transaction(
                    token_in=_parse_asset_to_address(token_in),
                    token_out=token_out,
                    amount_in=amount_in,
                    slippage=slippage,
                    network=network
                )

                # Parse the transaction XDR and invoke via Soroban
                if "transaction" in tx_result:
                    # Extract contract call details from the transaction
                    # This would need to decode the XDR to get the actual contract invocation
                    # For now, we'll simulate a direct contract call

                    # Build parameters for swap_exact_assets_for_assets
                    swap_params = json.dumps([
                        {"type": "i128", "value": amount_in},
                        {"type": "i128", "value": amount_out_min or "0"},
                        {"type": "vec", "value": [
                            {"type": "address", "value": token_in},
                            {"type": "address", "value": token_out}
                        ]},
                        {"type": "address", "value": account_id},
                        {"type": "u64", "value": str(int(asyncio.get_event_loop().time()) + 3600)}  # deadline
                    ])

                    # Invoke the router contract
                    result = await soroban_operations(
                        action="invoke",
                        soroban_server=soroban_server,
                        account_manager=account_manager,
                        agent_context=agent_context,
                        account_id=account_id,
                        contract_id=SOROSWAP_MAINNET_CONTRACTS["router"],
                        function_name="swap_exact_assets_for_assets",
                        parameters=swap_params,
                        network_passphrase="Public Global Stellar Network ; September 2015"
                    )

                    if result.get("success"):
                        result.update({
                            "swap_details": {
                                "token_in": token_in,
                                "token_out": token_out,
                                "amount_in": amount_in,
                                "slippage": slippage
                            }
                        })

                    return result
                else:
                    return {"error": "Failed to build transaction", "details": tx_result}

            elif action == "pools":
                # Get all available pools
                pools = await api.get_pools(network=network)

                return {
                    "success": True,
                    "pools": pools,
                    "count": len(pools),
                    "network": network
                }

            elif action == "pool_info":
                if not token_out:  # Use token_out as pool identifier
                    return {"error": "pool address required for pool_info"}

                pool_info = await api.get_pool_info(token_out, network=network)

                return {
                    "success": True,
                    "pool_info": pool_info,
                    "pool_address": token_out
                }

            else:
                return {
                    "error": f"Unknown action: {action}",
                    "valid_actions": ["quote", "swap", "pools", "pool_info"]
                }

    except Exception as e:
        return {"error": f"Soroswap operation failed: {str(e)}", "success": False}
```

#### 1.4 Update Tool Factory

Update `backend/agent/tool_factory.py` to include Soroswap tools:

```python
# Add to existing tool factory
from soroswap_tools import soroswap_dex

def create_soroswap_tools(agent_context: AgentContext, account_manager: AccountManager, soroban_server):
    """Create Soroswap DEX tools"""

    tools = [
        Tool(
            name="soroswap_dex",
            description="Interact with Soroswap DEX for quotes, swaps, and pool information",
            func=partial(
                soroswap_dex,
                agent_context=agent_context,
                account_manager=account_manager,
                soroban_server=soroban_server
            )
        )
    ]

    return tools

# Update get_available_tools() function
def get_available_tools(agent_context: AgentContext, account_manager: AccountManager, soroban_server):
    """Get all available tools for the agent"""

    tools = []

    # Add existing Stellar tools
    tools.extend(create_stellar_tools(agent_context, account_manager))

    # Add Blend tools
    tools.extend(create_blend_tools(agent_context, account_manager, soroban_server))

    # Add Soroswap tools
    tools.extend(create_soroswap_tools(agent_context, account_manager, soroban_server))

    return tools
```

### Phase 2: Direct Smart Contract Integration (Advanced)

#### 2.1 Router Contract Interface

Create `backend/soroswap_contracts.py`:

```python
"""
Direct Soroswap Smart Contract Integration
For advanced users who want direct contract interaction
"""

from typing import Dict, Any, List, Optional
from stellar_sdk import Address, scval
from stellar_soroban import soroban_operations
import json

# Mainnet contract addresses
SOROSWAP_ROUTER = "CAG5LRYQ5JVEUI5TEID72EYOVX44TTUJT5BQR2J6J77FH65PCCFAJDDH"
SOROSWAP_FACTORY = "CA4HEQTL2WPEUYKYKCDOHCDNIV4QHNJ7EL4J4NQ6VADP7SYHVRYZ7AW2"

class SoroswapContractInterface:
    """Direct interaction with Soroswap smart contracts"""

    @staticmethod
    async def swap_exact_assets_for_assets(
        agent_context,
        account_manager,
        soroban_server,
        account_id: str,
        amount_in: str,
        amount_out_min: str,
        path: List[str],
        to: str,
        deadline: int
    ) -> Dict[str, Any]:
        """
        Direct contract call for swapping tokens

        Args:
            amount_in: Amount of input token
            amount_out_min: Minimum amount of output token (slippage)
            path: List of token addresses for swap path
            to: Recipient address
            deadline: Unix timestamp for deadline
        """

        # Convert path to addresses
        path_addresses = [Address(addr) for addr in path]

        # Build parameters
        params = json.dumps([
            {"type": "i128", "value": amount_in},
            {"type": "i128", "value": amount_out_min},
            {"type": "vec", "value": [
                {"type": "address", "value": addr.to_xdr_sc_address().to_xdr()}
                for addr in path_addresses
            ]},
            {"type": "address", "value": to},
            {"type": "u64", "value": str(deadline)}
        ])

        return await soroban_operations(
            action="invoke",
            soroban_server=soroban_server,
            account_manager=account_manager,
            agent_context=agent_context,
            account_id=account_id,
            contract_id=SOROSWAP_ROUTER,
            function_name="swap_exact_assets_for_assets",
            parameters=params,
            network_passphrase="Public Global Stellar Network ; September 2015"
        )

    @staticmethod
    async def get_pair(
        soroban_server,
        token_a: str,
        token_b: str
    ) -> Dict[str, Any]:
        """Get pair address for two tokens"""

        params = json.dumps([
            {"type": "address", "value": token_a},
            {"type": "address", "value": token_b}
        ])

        return await soroban_operations(
            action="simulate",
            soroban_server=soroban_server,
            account_manager=None,
            agent_context=None,
            contract_id=SOROSWAP_FACTORY,
            function_name="get_pair",
            parameters=params,
            network_passphrase="Public Global Stellar Network ; September 2015"
        )

    @staticmethod
    async def create_pair(
        agent_context,
        account_manager,
        soroban_server,
        account_id: str,
        token_a: str,
        token_b: str
    ) -> Dict[str, Any]:
        """Create new trading pair"""

        params = json.dumps([
            {"type": "address", "value": token_a},
            {"type": "address", "value": token_b}
        ])

        return await soroban_operations(
            action="invoke",
            soroban_server=soroban_server,
            account_manager=account_manager,
            agent_context=agent_context,
            account_id=account_id,
            contract_id=SOROSWAP_FACTORY,
            function_name="create_pair",
            parameters=params,
            network_passphrase="Public Global Stellar Network ; September 2015"
        )
```

## Usage Examples

### Example 1: Getting a Swap Quote

```python
# Agent can ask: "What's the best rate to swap 1000 XLM for USDC?"
result = await soroswap_dex(
    action="quote",
    agent_context=agent_context,
    account_manager=account_manager,
    soroban_server=soroban_server,
    token_in="native",  # XLM
    token_out="USDC_CONTRACT_ADDRESS",
    amount_in="1000000000"  # 1000 XLM in stroops
)
```

### Example 2: Executing a Swap

```python
# Agent can ask: "Swap 500 XLM for USDC with 0.5% slippage"
result = await soroswap_dex(
    action="swap",
    agent_context=agent_context,
    account_manager=account_manager,
    soroban_server=soroban_server,
    account_id="user_account_id",
    token_in="native",
    token_out="USDC_CONTRACT_ADDRESS",
    amount_in="500000000",  # 500 XLM
    slippage=0.5
)
```

### Example 3: Getting Pool Information

```python
# Agent can ask: "Show me available Soroswap pools"
result = await soroswap_dex(
    action="pools",
    agent_context=agent_context,
    account_manager=account_manager,
    soroban_server=soroban_server
)
```

## Testing Implementation

### Unit Tests

Create `backend/test_soroswap.py`:

```python
"""
Tests for Soroswap integration
"""

import pytest
import asyncio
from unittest.mock import AsyncMock, patch
from soroswap_tools import soroswap_dex
from soroswap_api import SoroswapAPIClient

@pytest.mark.asyncio
async def test_soroswap_quote():
    """Test getting a swap quote"""

    # Mock API response
    mock_response = {
        "amountOut": "950000000",
        "priceImpact": "0.5",
        "route": [{"pool": "POOL_ADDRESS", "percent": 100}]
    }

    with patch.object(SoroswapAPIClient, 'get_quote', return_value=mock_response):
        result = await soroswap_dex(
            action="quote",
            agent_context=mock_agent_context,
            account_manager=mock_account_manager,
            soroban_server=mock_soroban_server,
            token_in="native",
            token_out="USDC_ADDRESS",
            amount_in="1000000000"
        )

        assert result["success"] is True
        assert "quote" in result
        assert result["token_in"] == "native"

@pytest.mark.asyncio
async def test_soroswap_pools():
    """Test getting available pools"""

    mock_pools = [
        {
            "address": "POOL1_ADDRESS",
            "token0": "XLM",
            "token1": "USDC",
            "reserve0": "1000000000",
            "reserve1": "500000000"
        }
    ]

    with patch.object(SoroswapAPIClient, 'get_pools', return_value=mock_pools):
        result = await soroswap_dex(
            action="pools",
            agent_context=mock_agent_context,
            account_manager=mock_account_manager,
            soroban_server=mock_soroban_server
        )

        assert result["success"] is True
        assert len(result["pools"]) == 1
```

### Integration Tests

```python
# Add to existing test suite
async def test_soroswap_integration():
    """Test Soroswap integration with mainnet"""

    # Test API connectivity
    async with SoroswapAPIClient() as api:
        contracts = await api.get_contracts()
        assert "factory" in contracts
        assert "router" in contracts

    # Test quote functionality
    result = await soroswap_dex(
        action="quote",
        agent_context=test_context,
        account_manager=test_account_manager,
        soroban_server=test_soroban_server,
        token_in="native",
        token_out="USDC_CONTRACT_ADDRESS",
        amount_in="100000000"
    )

    assert result["success"] is True
```

## Security Considerations

### 1. Smart Contract Audits

- Soroswap contracts have been audited by reputable firms
- Verify audit reports before mainnet deployment
- Consider implementing additional safety checks

### 2. Slippage Protection

- Always use slippage parameters for swaps
- Implement deadline checks for time-sensitive operations
- Validate minimum output amounts

### 3. Permission Checks

- Enforce user ownership of accounts before executing swaps
- Use AgentContext for proper authorization
- Implement transaction signing controls

### 4. Rate Limiting

- Implement rate limiting for API calls
- Cache quotes where appropriate
- Handle API failures gracefully

## Error Handling

### Common Error Scenarios

1. **Insufficient Liquidity**

   ```python
   if "error" in result and "liquidity" in result["error"].lower():
       return {"error": "Insufficient liquidity in pool", "suggestion": "Try smaller amount or different pool"}
   ```

2. **Slippage Exceeded**

   ```python
   if "error" in result and "slippage" in result["error"].lower():
       return {"error": "Slippage protection triggered", "suggestion": "Increase slippage tolerance"}
   ```

3. **Invalid Token Address**
   ```python
   if "error" in result and "invalid" in result["error"].lower():
       return {"error": "Invalid token address", "suggestion": "Verify token contract address"}
   ```

## Performance Optimization

### 1. Caching Strategy

- Cache pool data for 30-60 seconds
- Cache contract addresses permanently
- Implement quote caching for small amounts

### 2. Async Operations

- Use async/await for all API calls
- Implement concurrent requests where possible
- Use connection pooling for HTTP requests

### 3. Batch Operations

- Support multiple token queries in single requests
- Batch pool information requests
- Aggregate quotes from multiple sources

## Future Enhancements

### Phase 3: Advanced Features

1. **Multi-DEX Aggregation**
   - Integrate with other Stellar DEXs
   - Cross-DEX routing
   - Advanced split routing

2. **Yield Farming Integration**
   - Add liquidity provision tools
   - LP token management
   - Reward harvesting

3. **Advanced Trading Features**
   - Limit orders
   - Stop-loss orders
   - Portfolio management

4. **Analytics and Insights**
   - Price history analysis
   - Volume tracking
   - LP yield analytics

## Deployment Checklist

### Pre-Deployment

- [ ] Test all functionality on testnet
- [ ] Verify contract addresses for mainnet
- [ ] Implement proper error handling
- [ ] Add logging and monitoring
- [ ] Security audit of integration code

### Post-Deployment

- [ ] Monitor transaction success rates
- [ ] Track API response times
- [ ] User feedback collection
- [ ] Performance optimization based on usage

## Conclusion

This guide provides a comprehensive framework for integrating Soroswap functionality into the Tuxedo AI agent system. The implementation follows the existing patterns in the codebase and provides both simple API-based integration and advanced direct contract interaction options.

The phased approach allows for incremental development and testing, ensuring robust integration while maintaining the existing system's architecture and security model.

**Recommendation:** Start with Phase 1 (API Integration) for immediate functionality, then progress to Phase 2 (Direct Integration) for advanced features and reduced external dependencies.
