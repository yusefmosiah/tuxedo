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
async def discover_high_yield_vaults(min_apy: Optional[float] = 15.0) -> str:
    """Discover DeFindex vaults with high yields using enhanced data sources.

    Use this when users ask about:
    - High yield opportunities
    - Where to invest or earn yield
    - Best APY rates on Stellar
    - DeFi yield opportunities

    This tool provides realistic yield data and vault information with enhanced
    details about risk levels, strategies, and asset types.

    Args:
        min_apy: Minimum APY threshold as percentage (default 15.0%)

    Returns:
        Formatted list of vaults with their APYs, TVL, and detailed information
    """
    try:
        # Query for vault yields using testnet for safe demo/testing
        defindex = get_defindex_soroban(network='testnet')
        vaults_data = await defindex.get_available_vaults(min_apy=min_apy)

        if not vaults_data:
            return f"No vaults found with APY above {min_apy}%."

        # Format response with enhanced information
        result = f"Found {len(vaults_data)} high-yield DeFindex vaults on Stellar:\n\n"

        for i, v in enumerate(vaults_data[:8], 1):  # Top 8 vaults
            # Risk indicator emoji
            risk_emoji = {'Low': '🟢', 'Medium': '🟡', 'High': '🔴'}.get(v.get('risk_level', 'Medium'), '⚪')

            result += f"{i}. {v['name']} ({v['symbol']}) {risk_emoji}\n"
            result += f"   APY: {v['apy']:.1f}% | Strategy: {v.get('strategy', 'Unknown')}\n"
            result += f"   TVL: ${v['tvl']:,.0f} | Type: {v.get('asset_type', 'Unknown')}\n"
            result += f"   Address: {v['address']}\n\n"

        # Add helpful context
        if len(vaults_data) > 8:
            result += f"... and {len(vaults_data) - 8} more vaults available.\n\n"

        result += "💡 **Risk Guide**: 🟢 Low Risk (Stablecoins) | 🟡 Medium Risk (XLM) | 🔴 High Risk (Alt tokens)\n"
        result += "📊 Data includes realistic market-based APY and TVL calculations.\n"
        result += "🧪 For testing, I can prepare demo transactions on testnet using these mainnet vault references."

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
    When the API is available, creates a real deposit transaction. Falls back to demo transaction
    only when the API is unavailable.

    Args:
        vault_address: The vault contract address (can be testnet or mainnet)
        amount_xlm: Amount to deposit in XLM (e.g., 10.5)
        user_address: User's Stellar public key (G...)
        network: Network to use ('testnet' or 'mainnet', default 'testnet')

    Returns:
        Transaction details indicating whether it's a REAL or DEMO transaction
    """
    try:
        # Convert XLM to stroops (1 XLM = 10,000,000 stroops)
        amount_stroops = int(amount_xlm * 10_000_000)

        # Use specified network for transactions
        defindex = get_defindex_soroban(network=network)

        # Build the deposit transaction (real or demo based on API availability)
        tx_data = defindex.build_deposit_transaction(
            vault_address=vault_address,
            amount_stroops=amount_stroops,
            user_address=user_address
        )

        # Create transaction payload
        is_real_transaction = tx_data.get('data_source') == 'api'
        transaction_type = "REAL" if is_real_transaction else "DEMO"

        tx_payload = {
            'xdr': tx_data['xdr'],
            'vault_address': vault_address,
            'amount': amount_xlm,
            'estimated_shares': tx_data.get('estimated_shares', '0'),
            'description': tx_data['description'],
            'network': network,
            'transaction_type': transaction_type,
            'data_source': tx_data.get('data_source', 'demo')
        }

        # Add additional fields for demo transactions
        if not is_real_transaction:
            tx_payload['demo_destination'] = tx_data.get('demo_destination', 'N/A')
            tx_payload['note'] = tx_data.get('note', 'Demo transaction for testing')

        # Return transaction details
        tx_json = json.dumps(tx_payload, indent=2)

        if is_real_transaction:
            return f"""✅ **REAL DEPOSIT TRANSACTION PREPARED**

I've prepared a **real vault deposit transaction** for {amount_xlm:,.0f} XLM to the {vault_address[:8]}... vault on {network}.

**Transaction Details:**
```json
{tx_json}
```

🎯 **This is a real DeFindex vault deposit** that will interact with the smart contract. The transaction can be signed and submitted to the {network} network."""
        else:
            return f"""🎭 **DEMO TRANSACTION PREPARED** (API Unavailable)

I've prepared a **demo deposit transaction** for {amount_xlm:,.0f} XLM to simulate depositing to the {vault_address[:8]}... vault on {network}.

**Transaction Details:**
```json
{tx_json}
```

⚠️ **Note:** The DeFindex API is currently unavailable, so this is a testnet demo transaction that simulates a vault deposit using a simple XLM payment. For real vault deposits, the API needs to be accessible."""

    except Exception as e:
        logger.error(f"Error in prepare_defindex_deposit: {e}")
        logger.error(f"Vault address: {vault_address}, Amount: {amount_xlm} XLM, Network: {network}")
        return f"Error: Unable to prepare deposit transaction: {str(e)}"