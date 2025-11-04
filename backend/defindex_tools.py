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
async def discover_high_yield_vaults(min_apy: Optional[float] = 30.0) -> str:
    """Discover DeFindex vaults with high yields using Soroban smart contracts.

    Use this when users ask about:
    - High yield opportunities
    - Where to invest or earn yield
    - Best APY rates on Stellar
    - DeFi yield opportunities

    This tool queries mainnet vault data but executes transactions on testnet for safety.

    Args:
        min_apy: Minimum APY threshold as percentage (default 30.0%)

    Returns:
        Formatted list of vaults with their APYs and details
    """
    try:
        # Query mainnet for vault yields using Soroban contracts
        defindex = get_defindex_soroban(network='mainnet')
        vaults_data = defindex.get_available_vaults(min_apy=min_apy)

        if not vaults_data:
            return f"No vaults found with APY above {min_apy}% on mainnet"

        # Format response
        result = f"Found {len(vaults_data)} high-yield DeFindex vaults on Stellar mainnet:\n\n"
        for i, v in enumerate(vaults_data[:5], 1):  # Top 5
            result += f"{i}. {v['name']} ({v['symbol']})\n"
            result += f"   APY: {v['apy']:.1f}%\n"
            result += f"   TVL: ${v['tvl']:,.0f}\n"
            result += f"   Address: {v['address']}\n\n"

        result += "\n💡 Note: These are real mainnet vaults with live yields. For testing, I can prepare demo deposits on testnet."

        return result

    except Exception as e:
        logger.error(f"Error in discover_high_yield_vaults: {e}")
        return f"Error: Unable to fetch vault data from DeFindex contracts: {str(e)}"

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
        defindex = get_defindex_soroban(network='mainnet')
        vault_info = defindex.get_vault_details(vault_address)

        result = f"Vault Details: {vault_info['name']}\n"
        result += f"Symbol: {vault_info['symbol']}\n"
        result += f"Current APY: {vault_info['apy']:.1f}%\n"
        result += f"Total Value Locked: ${vault_info['tvl']:,.0f}\n\n"

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

        return result

    except ValueError as e:
        if "not found" in str(e):
            # Try to find similar vaults
            defindex = get_defindex_soroban(network='mainnet')
            available_vaults = defindex.get_available_vaults(min_apy=0)

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
    user_address: str
) -> str:
    """Prepare a DEMO deposit transaction that simulates depositing into a DeFindex vault.

    This builds a testnet transaction that demonstrates the wallet signing flow.
    The transaction is a simple XLM payment to a testnet address (not a real vault deposit).

    NOTE: Wallet integration has been removed. This tool now returns readable transaction details
    without automatic wallet parsing. Users would need to manually use the transaction data if
    wallet integration was available.

    Args:
        vault_address: The mainnet vault contract address (used for metadata/reference only)
        amount_xlm: Amount to deposit in XLM (e.g., 10.5)
        user_address: User's Stellar public key (G...)

    Returns:
        Readable transaction details in formatted JSON without wallet integration
    """
    try:
        # Convert XLM to stroops (1 XLM = 10,000,000 stroops)
        amount_stroops = int(amount_xlm * 10_000_000)

        # Use testnet for SAFE demo transactions
        defindex = get_defindex_soroban(network='testnet')

        # Build the demo transaction
        tx_data = defindex.build_deposit_transaction(
            vault_address=vault_address,  # Pass mainnet address for metadata
            amount_stroops=amount_stroops,
            user_address=user_address
        )

        # Create transaction payload
        tx_payload = {
            'xdr': tx_data['xdr'],
            'vault_address': vault_address,  # Mainnet vault for reference
            'amount': amount_xlm,
            'estimated_shares': tx_data.get('estimated_shares', '0'),
            'description': tx_data['description'],
            'network': 'testnet',
            'note': tx_data.get('note', 'Testnet demo transaction')
        }

        # Return transaction details without wallet integration tags
        tx_json = json.dumps(tx_payload, indent=2)  # Formatted JSON for readability
        return f"""I've prepared a demo deposit transaction for {amount_xlm:,.0f} XLM to the {vault_address[:8]}... vault.

**Transaction Details:**
```json
{tx_json}
```

⚠️ **Note:** This is a testnet demo transaction that simulates a mainnet vault deposit. The actual transaction sends XLM to a testnet address for demonstration purposes. No wallet integration is available."""

    except Exception as e:
        logger.error(f"Error in prepare_defindex_deposit: {e}")
        return f"Error: Unable to prepare demo deposit transaction: {str(e)}"