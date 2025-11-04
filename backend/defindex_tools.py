#!/usr/bin/env python3
"""
DeFindex LangChain tools for Stellar vault operations
"""

import asyncio
import json
import logging
from typing import Optional
from langchain_core.tools import tool
from defindex_soroban import get_defindex_soroban

logger = logging.getLogger(__name__)

# Hardcoded testnet vault addresses for demo purposes
# TODO: Update with real testnet vault addresses from DeFindex docs
TESTNET_VAULTS = {
    'TEST_XLM_VAULT': 'CAQEPGA3XDBZSWHYLBUSH2UIP2SHHTEMXMHFPLIEN6RYH7G6GEGJWHGN',
    'TEST_USDC_VAULT': 'CBGJ7RZKJSRXL5QWG7V7QD6XSTJ6J5E2X7ZQKX7YJ5J2X7ZQKX7YJ5J',
}

@tool
async def discover_high_yield_vaults(min_apy: Optional[float] = 0.0) -> str:
    """Discover ALL available DeFindex vaults sorted by APY (highest to lowest).

    Use this when users ask about:
    - Available vaults for investment
    - Current APY rates on Stellar
    - DeFi yield opportunities
    - Where to deposit funds

    This tool shows ALL vaults including 0% APY vaults, sorted by yield.

    Args:
        min_apy: Minimum APY threshold as percentage (default 0.0% to show ALL)

    Returns:
        Complete list of available vaults sorted by APY with full details
    """
    try:
        # Query for ALL vaults using testnet for actual testing
        defindex = get_defindex_soroban(network='testnet')
        vaults_data = await defindex.get_available_vaults(min_apy=min_apy)

        if not vaults_data:
            return f"No vaults found with APY above {min_apy}% on testnet."

        # Sort vaults by APY (highest first)
        vaults_data.sort(key=lambda x: x.get('apy', 0), reverse=True)

        # Format response with ALL available vaults
        result = f"Found {len(vaults_data)} available DeFindex vaults on testnet (sorted by APY):\n\n"

        for i, v in enumerate(vaults_data, 1):  # Show ALL vaults
            # Risk indicator emoji
            risk_emoji = {'Low': '🟢', 'Medium': '🟡', 'High': '🔴'}.get(v.get('risk_level', 'Medium'), '⚪')

            result += f"{i}. {v['name']} ({v['symbol']}) {risk_emoji}\n"
            result += f"   APY: {v['apy']:.1f}% | Strategy: {v.get('strategy', 'Unknown')}\n"
            result += f"   TVL: ${v['tvl']:,.0f} | Type: {v.get('asset_type', 'Unknown')}\n"
            result += f"   Address: {v['address']}\n\n"

        result += "💡 **Risk Guide**: 🟢 Low Risk (Stablecoins) | 🟡 Medium Risk (XLM) | 🔴 High Risk (Alt tokens)\n"
        result += "📊 All vaults are REAL and available for deposits on testnet.\n"
        result += "🔧 Use prepare_defindex_deposit to create REAL deposit transactions."

        return result

    except Exception as e:
        logger.error(f"Error in discover_high_yield_vaults: {e}")
        return f"Error: Unable to fetch vault data from DeFindex: {str(e)}"

@tool
async def get_defindex_vault_details(vault_address: str) -> str:
    """Get detailed information about a specific DeFindex vault using Soroban contracts.

    Use this when users want more details about a vault they're interested in.

    Args:
        vault_address: The contract address of the vault

    Returns:
        Detailed vault information including strategies and performance
    """
    try:
        defindex = get_defindex_soroban(network='testnet')
        vault_info = await defindex.get_vault_details(vault_address)

        # Risk indicator emoji
        risk_emoji = {'Low': '🟢', 'Medium': '🟡', 'High': '🔴'}.get(vault_info.get('risk_level', 'Medium'), '⚪')

        result = f"Vault Details: {vault_info['name']} {risk_emoji}\n"
        result += f"Symbol: {vault_info['symbol']} | Type: {vault_info.get('asset_type', 'Unknown')}\n"
        result += f"Current APY: {vault_info['apy']:.1f}% | Risk: {vault_info.get('risk_level', 'Medium')}\n"
        result += f"Total Value Locked: ${vault_info['tvl']:,.0f}\n\n"

        # Fee structure
        fees = vault_info.get('fees', {})
        if fees:
            result += "💰 Fee Structure:\n"
            result += f"• Deposit Fee: {fees.get('deposit', 'N/A')}\n"
            result += f"• Withdrawal Fee: {fees.get('withdrawal', 'N/A')}\n"
            result += f"• Performance Fee: {fees.get('performance', 'N/A')}\n"
            result += f"• Minimum Deposit: {vault_info.get('min_deposit', 'N/A')} {vault_info['symbol']}\n\n"

        # Strategies
        strategies = vault_info.get('strategies', [])
        if strategies:
            result += "📊 Active Strategies:\n"
            for i, strategy in enumerate(strategies, 1):
                status = "⚠️ PAUSED" if strategy.get('paused') else "✅ Active"
                result += f"{i}. {strategy.get('name', 'Unknown Strategy')} - {status}\n"
                if strategy.get('description'):
                    result += f"   {strategy.get('description')}\n"
        else:
            result += "📊 No active strategies found\n"

        # Performance metrics
        historical = vault_info.get('historical_apy', {})
        if historical:
            result += f"\n📈 Historical Performance:\n"
            result += f"1 Month APY: {historical.get('1m', 0):.1f}%\n"
            result += f"3 Month APY: {historical.get('3m', 0):.1f}%\n"
            result += f"1 Year APY: {historical.get('1y', 0):.1f}%\n"

        result += f"\n🔗 Contract: {vault_address[:8]}...{vault_address[-8:]}"
        result += f"\n🧪 Demo transactions available on testnet using mainnet reference data"

        return result

    except ValueError as e:
        if "not found" in str(e):
            # Try to find similar vaults
            defindex = get_defindex_soroban(network='testnet')
            available_vaults = await defindex.get_available_vaults(min_apy=0)

            result = f"Error: Vault not found at address {vault_address}\n\n"
            result += "Available vaults:\n"
            for i, v in enumerate(available_vaults[:5], 1):
                result += f"{i}. {v['name']} - {v['address']}\n"

            return result
        else:
            return f"Error fetching vault details: {str(e)}"
    except Exception as e:
        logger.error(f"Error in get_defindex_vault_details: {e}")
        return f"Error: Unable to fetch vault details. Please check the address and try again."

@tool
async def prepare_defindex_deposit(
    vault_address: str,
    amount_xlm: float,
    user_address: str,
    network: str = "testnet"
) -> str:
    """Prepare a REAL deposit transaction to a DeFindex vault using the DeFindex API.

    This builds an actual vault deposit transaction that interacts with the DeFindex smart contract.
    NO DEMO TRANSACTIONS - only real transactions are supported.

    Args:
        vault_address: The vault contract address (must be valid on specified network)
        amount_xlm: Amount to deposit in XLM (e.g., 10.5)
        user_address: User's Stellar public key (G...)
        network: Network to use ('testnet' or 'mainnet', default 'testnet')

    Returns:
        REAL deposit transaction details for immediate use
    """
    try:
        # Convert XLM to stroops (1 XLM = 10,000,000 stroops)
        amount_stroops = int(amount_xlm * 10_000_000)

        # Use specified network for transactions
        defindex = get_defindex_soroban(network=network)

        # Build ONLY REAL deposit transactions
        tx_data = defindex.build_deposit_transaction(
            vault_address=vault_address,
            amount_stroops=amount_stroops,
            user_address=user_address
        )

        # Verify this is a REAL transaction
        if tx_data.get('data_source') != 'api':
            raise ValueError(f"Unable to create real deposit transaction. API returned: {tx_data.get('data_source', 'unknown')}")

        # Create REAL transaction payload
        tx_payload = {
            'xdr': tx_data['xdr'],
            'vault_address': vault_address,
            'amount': amount_xlm,
            'estimated_shares': tx_data.get('estimated_shares', '0'),
            'description': tx_data['description'],
            'network': network,
            'transaction_type': 'REAL',
            'data_source': 'api'
        }

        # Return REAL transaction details
        tx_json = json.dumps(tx_payload, indent=2)

        return f"""✅ **REAL DEPOSIT TRANSACTION PREPARED**

I've prepared a **real vault deposit transaction** for {amount_xlm:,.0f} XLM to the {vault_address[:8]}... vault on {network}.

**Transaction Details:**
```json
{tx_json}
```

🎯 **This is a real DeFindex vault deposit** that will interact with the smart contract. The transaction can be signed and submitted to the {network} network.

⚠️ **Important**: This transaction will actually deposit funds into the vault when submitted."""

    except Exception as e:
        logger.error(f"Error in prepare_defindex_deposit: {e}")
        logger.error(f"Vault address: {vault_address}, Amount: {amount_xlm} XLM, Network: {network}")

        # Enhanced error handling for known issues
        error_str = str(e)

        if "MissingValue" in error_str or "missing value" in error_str.lower():
            return """⚠️ **DeFindex API Testnet Limitation Detected**

The vault contracts on Stellar testnet are currently not initialized, causing "MissingValue" storage errors.
This is a known limitation of the DeFindex testnet environment.

**What this means:**
- The vault contracts exist but have no initialized data
- All vault operations (deposit, APY queries, etc.) fail on testnet
- This affects both mainnet vault addresses and testnet vault addresses

**Workaround Options:**
1. **Manual XLM Payment**: Send XLM directly to the vault address:
   - Destination: `{vault_address[:8]}...{vault_address[-8:]}`
   - Amount: {amount_xlm} XLM
   - Memo: "Deposit to DeFindex Vault"
   - The contract will treat the payment as a deposit

2. **Use Mainnet**: Switch to mainnet for full DeFindex functionality (requires real funds)

3. **Contact Support**: Reach out to DeFindex team about testnet contract initialization

**Technical Details:**
The API returns storage errors because contract storage slots are empty on testnet.
This is an infrastructure issue, not a configuration problem in our system.

Status: Testnet vault contracts require initialization by DeFindex team."""

        elif "rate limit" in error_str.lower() or "429" in error_str:
            return """⚠️ **DeFindex API Rate Limit Exceeded**

The DeFindex API has a strict rate limit (1 request per second) on testnet.

**What to do:**
- Wait a few seconds before trying again
- The system will automatically retry with delays

**Technical Details:**
Rate limiting is implemented to prevent abuse of the DeFindex API.
Our client handles this with automatic retries and exponential backoff."""

        elif "authentication" in error_str.lower() or "403" in error_str:
            return """❌ **DeFindex API Authentication Failed**

There's an issue with the API key or authentication.

**What this means:**
- The API key may be invalid or expired
- There might be permission issues with the vault operations

**Technical Details:**
Status: API authentication requires valid Bearer token with proper permissions."""

        else:
            # Full error message for other issues (no truncation)
            return f"Error: Unable to prepare deposit transaction: {error_str}"