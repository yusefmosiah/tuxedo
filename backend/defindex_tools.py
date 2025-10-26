#!/usr/bin/env python3
"""
DeFindex LangChain tools for Stellar vault operations
"""

import json
import logging
from typing import Optional
from langchain_core.tools import tool
from defindex_client import get_defindex_client

logger = logging.getLogger(__name__)

# Hardcoded testnet vault addresses for demo purposes
# TODO: Update with real testnet vault addresses from DeFindex docs
TESTNET_VAULTS = {
    'TEST_XLM_VAULT': 'CAQEPGA3XDBZSWHYLBUSH2UIP2SHHTEMXMHFPLIEN6RYH7G6GEGJWHGN',
    'TEST_USDC_VAULT': 'CBGJ7RZKJSRXL5QWG7V7QD6XSTJ6J5E2X7ZQKX7YJ5J2X7ZQKX7YJ5J',
}

@tool
async def discover_high_yield_vaults(min_apy: Optional[float] = 50.0) -> str:
    """Discover DeFindex vaults with high yields on mainnet.

    Use this when users ask about:
    - High yield opportunities
    - Where to invest or earn yield
    - Best APY rates on Stellar
    - DeFi yield opportunities

    This tool queries mainnet for real yields but executes transactions on testnet for safety.

    Args:
        min_apy: Minimum APY threshold as percentage (default 50.0%)

    Returns:
        Formatted list of vaults with their APYs and details
    """
    try:
        # Query mainnet for REAL yields
        client = get_defindex_client(network='mainnet')

        vaults_data = []
        vaults = client.get_vaults(limit=20)

        for vault in vaults:
            try:
                # Extract vault info
                apy = vault.get('apy', 0)

                if apy >= min_apy:
                    vaults_data.append({
                        'name': vault.get('name', 'Unknown Vault'),
                        'address': vault.get('address', ''),
                        'apy': apy,
                        'tvl': vault.get('tvl', 0),
                        'symbol': vault.get('symbol', 'N/A'),
                        'description': vault.get('description', 'High yield strategy')
                    })
            except Exception as e:
                logger.warning(f"Failed to process vault {vault.get('address', 'unknown')}: {e}")
                continue

        if not vaults_data:
            return f"No vaults found with APY above {min_apy}% on mainnet"

        # Sort by APY descending
        vaults_data.sort(key=lambda v: v['apy'], reverse=True)

        # Format response
        result = f"Found {len(vaults_data)} high-yield vaults on Stellar mainnet:\n\n"
        for i, v in enumerate(vaults_data[:5], 1):  # Top 5
            result += f"{i}. {v['name']} ({v['symbol']})\n"
            result += f"   APY: {v['apy']:.2f}%\n"
            result += f"   TVL: ${v['tvl']:,.0f}\n"
            result += f"   Address: {v['address'][:8]}...{v['address'][-8:]}\n"
            result += f"   {v['description']}\n\n"

        result += "\n💡 Note: These are real mainnet yields. For testing, I can prepare demo deposits on testnet."

        return result

    except ValueError as e:
        if "authentication failed" in str(e):
            return "Error: DeFindex API key authentication failed. Please check DEFINDEX_API_KEY."
        elif "not found" in str(e):
            return "Error: DeFindex API endpoint not found. The base URL may be incorrect."
        else:
            return f"Error discovering vaults: {str(e)}"
    except Exception as e:
        logger.error(f"Error in discover_high_yield_vaults: {e}")
        return "Error: Unable to fetch vault data from DeFindex. Please try again later."

@tool
async def get_defindex_vault_details(vault_address: str) -> str:
    """Get detailed information about a specific DeFindex vault on mainnet.

    Use this when users want more details about a vault they're interested in.

    Args:
        vault_address: The contract address of the vault

    Returns:
        Detailed vault information including strategies and performance
    """
    try:
        client = get_defindex_client(network='mainnet')
        vault_info = client.get_vault_info(vault_address)

        result = f"Vault Details: {vault_info.get('name', 'Unknown')}\n"
        result += f"Symbol: {vault_info.get('symbol', 'N/A')}\n"
        result += f"Current APY: {vault_info.get('apy', 0):.2f}%\n"
        result += f"Total Value Locked: ${vault_info.get('tvl', 0):,.0f}\n\n"

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

        # Assets
        assets = vault_info.get('assets', [])
        if assets:
            result += f"\n💰 Supported Assets: {len(assets)}\n"
            for asset in assets[:5]:  # Show first 5
                result += f"• {asset.get('symbol', 'Unknown')} ({asset.get('name', 'Unknown')})\n"

        # Performance metrics
        if 'historical_apy' in vault_info:
            result += f"\n📈 Historical Performance:\n"
            result += f"1 Month APY: {vault_info['historical_apy'].get('1m', 0):.2f}%\n"
            result += f"3 Month APY: {vault_info['historical_apy'].get('3m', 0):.2f}%\n"
            result += f"1 Year APY: {vault_info['historical_apy'].get('1y', 0):.2f}%\n"

        result += f"\n🔗 Contract: {vault_address[:8]}...{vault_address[-8:]}"

        return result

    except ValueError as e:
        if "not found" in str(e):
            return f"Error: Vault not found at address {vault_address}"
        elif "authentication failed" in str(e):
            return "Error: DeFindex API authentication failed"
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
    """Prepare a deposit transaction for a DeFindex vault on testnet.

    This builds an UNSIGNED transaction that the frontend must sign.
    Use this when a user wants to deposit funds into a vault for testing.

    This uses testnet for safe demo transactions even though vault data comes from mainnet.

    Args:
        vault_address: The vault contract address (from mainnet discovery)
        amount_xlm: Amount to deposit in XLM (e.g., 10.5)
        user_address: User's Stellar public key (G...)

    Returns:
        JSON string with transaction details for frontend to sign
    """
    try:
        # Convert XLM to stroops (1 XLM = 10,000,000 stroops)
        amount_stroops = int(amount_xlm * 10_000_000)

        # Use testnet client for SAFE demo transactions
        client = get_defindex_client(network='testnet')

        # For demo, we'll use a testnet vault address
        # In real implementation, you'd map mainnet vault to testnet equivalent
        testnet_vault = TESTNET_VAULTS.get('TEST_XLM_VAULT')

        if not testnet_vault:
            return "Error: Testnet vault addresses not configured"

        try:
            tx_data = client.build_deposit_transaction(
                vault_address=testnet_vault,
                amount_stroops=amount_stroops,
                caller=user_address,
                invest=True
            )

            # Return structured data for backend to handle
            return json.dumps({
                'action': 'SIGN_TRANSACTION',
                'xdr': tx_data['xdr'],
                'vault_address': testnet_vault,
                'amount': amount_xlm,
                'estimated_shares': tx_data.get('estimatedShares', '0'),
                'description': f"Deposit {amount_xlm} XLM to DeFindex testnet vault",
                'note': 'This is a testnet transaction for demonstration purposes'
            })

        except Exception as e:
            return f"Error building deposit transaction: {str(e)}"

    except ValueError as e:
        if "authentication failed" in str(e):
            return "Error: DeFindex API authentication failed"
        else:
            return f"Error preparing deposit: {str(e)}"
    except Exception as e:
        logger.error(f"Error in prepare_defindex_deposit: {e}")
        return "Error: Unable to prepare deposit transaction. Please check your inputs and try again."