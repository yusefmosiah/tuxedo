#!/usr/bin/env python3
"""
DeFindex Account Tools - AccountManager Integration
Implements DeFindex tools that work with the established tool_factory pattern
using user_id injection and AccountManager for private key access.
"""

import asyncio
import json
import logging
from typing import Optional, Dict, Any
from account_manager import AccountManager

logger = logging.getLogger(__name__)

# Testnet vault addresses for validation
TESTNET_VAULTS = {
    'XLM_HODL_1': 'CAHWRPKBPX4FNLXZOAD565IBSICQPL5QX37IDLGJYOPWX22WWKFWQUBA',
    'XLM_HODL_2': 'CCSPRGGUP32M23CTU7RUAGXDNOHSA6O2BS2IK4NVUP5X2JQXKTSIQJKE',
    'XLM_HODL_3': 'CBLXUUHUL7TA3LF3U5G6ZTU7EACBBOSJLR4AYOM5YJKJ4APZ7O547R5T',
    'XLM_HODL_4': 'CCGKL6U2DHSNFJ3NU4UPRUKYE2EUGYR4ZFZDYA7KDJLP3TKSPHD5C4UP'
}

async def _defindex_discover_vaults(
    min_apy: float,
    user_id: str
) -> str:
    """Discover DeFindex vaults sorted by APY"""
    try:
        from defindex_soroban import get_defindex_soroban

        defindex = get_defindex_soroban(network='testnet')
        vaults_data = await defindex.get_available_vaults(min_apy=min_apy)

        if not vaults_data:
            return f"No vaults found with APY above {min_apy}% on testnet."

        vaults_data.sort(key=lambda x: x.get('apy', 0), reverse=True)

        result = f"Found {len(vaults_data)} available DeFindex vaults on testnet (sorted by APY):\n\n"

        for i, v in enumerate(vaults_data, 1):
            risk_emoji = {'Low': '🟢', 'Medium': '🟡', 'High': '🔴'}.get(v.get('risk_level', 'Medium'), '⚪')

            result += f"{i}. {v['name']} ({v['symbol']}) {risk_emoji}\n"
            result += f"   APY: {v['apy']:.1f}% | Strategy: {v.get('strategy', 'Unknown')}\n"
            result += f"   TVL: ${v['tvl']:,.0f} | Type: {v.get('asset_type', 'Unknown')}\n"
            result += f"   Address: {v['address']}\n\n"

        result += "💡 **Risk Guide**: 🟢 Low Risk (Stablecoins) | 🟡 Medium Risk (XLM) | 🔴 High Risk (Alt tokens)\n"
        result += "📊 All vaults are REAL and available for deposits on testnet.\n"
        result += f"🔧 Use defindex_deposit to execute REAL deposit transactions for user {user_id[:8]}..."

        return result

    except Exception as e:
        logger.error(f"Error in _defindex_discover_vaults: {e}")
        return f"Error: Unable to fetch vault data from DeFindex: {str(e)}"

async def _defindex_get_vault_details(
    vault_address: str,
    user_id: str
) -> str:
    """Get detailed information about a DeFindex vault"""
    try:
        from defindex_soroban import get_defindex_soroban

        defindex = get_defindex_soroban(network='testnet')
        vault_info = await defindex.get_vault_details(vault_address)

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

        result += f"\n🔗 Contract: {vault_address[:8]}...{vault_address[-8:]}"
        result += f"\n👤 Available for user {user_id[:8]}... to deposit via defindex_deposit"

        return result

    except ValueError as e:
        if "not found" in str(e):
            return f"Error: Vault not found at address {vault_address[:8]}...{vault_address[-8:]}\n\nAvailable vaults:\n" + \
                   "\n".join([f"{i}. {name} - {addr[:8]}...{addr[-8:]}"
                             for i, (name, addr) in enumerate(TESTNET_VAULTS.items(), 1)])
        else:
            return f"Error fetching vault details: {str(e)}"
    except Exception as e:
        logger.error(f"Error in _defindex_get_vault_details: {e}")
        return f"Error: Unable to fetch vault details. Please check the address and try again."

async def _defindex_deposit(
    vault_address: str,
    amount_xlm: float,
    user_id: str,
    account_id: str,
    account_manager: AccountManager
) -> str:
    """Execute autonomous deposit to DeFindex vault using user's account from AccountManager"""
    try:
        logger.info(f"Starting DeFindex deposit for user {user_id[:8]}..., account {account_id}")
        logger.info(f"Amount: {amount_xlm} XLM to vault {vault_address[:8]}...")

        # 1. Validate vault address
        vault_info = None
        for name, address in TESTNET_VAULTS.items():
            if address == vault_address:
                vault_info = {'name': name, 'address': address}
                break

        if not vault_info:
            return f"""❌ **Invalid Vault Address**

The vault address `{vault_address[:8]}...{vault_address[-8:]}` is not recognized.

**Available testnet vaults:**
1. XLM_HODL_1: `{TESTNET_VAULTS['XLM_HODL_1'][:8]}...{TESTNET_VAULTS['XLM_HODL_1'][-8:]}`
2. XLM_HODL_2: `{TESTNET_VAULTS['XLM_HODL_2'][:8]}...{TESTNET_VAULTS['XLM_HODL_2'][-8:]}`
3. XLM_HODL_3: `{TESTNET_VAULTS['XLM_HODL_3'][:8]}...{TESTNET_VAULTS['XLM_HODL_3'][-8:]}`
4. XLM_HODL_4: `{TESTNET_VAULTS['XLM_HODL_4'][:8]}...{TESTNET_VAULTS['XLM_HODL_4'][-8:]}`

Please use one of these verified vault addresses."""

        # 2. Get user's keypair from AccountManager
        try:
            keypair = account_manager.get_keypair_for_signing(user_id, account_id)
            logger.info(f"Retrieved user keypair: {keypair.public_key}")
        except Exception as e:
            return f"""❌ **Account Access Error**

Could not access account '{account_id}' for user {user_id[:8]}...

This could mean:
- Account ID doesn't exist
- Account doesn't belong to this user
- Database access issue

Please check your account ID and try again.

Error details: {str(e)}"""

        # 3. Check user's XLM balance
        try:
            from stellar_sdk.server import Server
            server = Server("https://horizon-testnet.stellar.org")

            account = server.load_account(keypair.public_key)
            xlm_balance = 0.0

            for balance in account.balances:
                if balance.asset_type == "native":
                    xlm_balance = float(balance.balance)
                    break

            # Reserve 2 XLM for minimum balance + transaction fees
            available_balance = xlm_balance - 2.0

            if amount_xlm > available_balance:
                return f"""❌ **Insufficient Balance**

Account balance: {xlm_balance:.2f} XLM
Available for deposit: {available_balance:.2f} XLM
Requested deposit: {amount_xlm:.2f} XLM

Need additional {amount_xlm - available_balance:.2f} XLM

Note: 2 XLM is reserved for account minimum balance and fees."""

            logger.info(f"Balance check passed: {xlm_balance:.2f} XLM available, {available_balance:.2f} XLM for deposit")

        except Exception as e:
            logger.warning(f"Could not check balance: {e}")
            # Continue anyway, let the transaction fail if insufficient funds

        # 4. Build transaction via DeFindex API
        try:
            from defindex_client import get_defindex_client

            client = get_defindex_client(network='testnet')
            amount_stroops = int(amount_xlm * 10_000_000)  # Convert XLM to stroops

            logger.info(f"Building deposit transaction: {amount_xlm} XLM to {vault_info['name']}")

            tx_data = client.build_deposit_transaction(
                vault_address=vault_address,
                amount_stroops=amount_stroops,
                caller=keypair.public_key,
                invest=True
            )

            unsigned_xdr = tx_data.get('xdr')
            if not unsigned_xdr:
                return "❌ **Transaction Build Failed**: No XDR returned from DeFindex API"

            logger.info("Transaction built successfully")

        except ImportError:
            return """❌ **DeFindex Client Not Available**

The DeFindex client library is not installed or not accessible.

Please install the required dependencies:
- defindex_client
- Related Stellar SDK libraries

This is a development environment issue, not a user account issue."""

        except Exception as e:
            return f"❌ **Transaction Build Failed**: {str(e)}"

        # 5. Sign with user's private key using keypair
        try:
            logger.info("Signing transaction with user's keypair")

            from stellar_sdk.transaction_envelope import TransactionEnvelope
            from stellar_sdk.network import Network

            # Parse the unsigned XDR and sign it
            envelope = TransactionEnvelope.from_xdr(unsigned_xdr, Network.TESTNET_NETWORK_PASSPHRASE)
            envelope.sign(keypair)

            signed_tx = envelope.to_xdr()

            if not signed_tx:
                return "❌ **Transaction Signing Failed**: Empty signed transaction"

            logger.info("Transaction signed successfully")

        except Exception as e:
            return f"❌ **Transaction Signing Failed**: {str(e)}"

        # 6. Submit transaction to Stellar network
        try:
            logger.info("Submitting transaction to Stellar network")

            result = client.submit_transaction(signed_tx)

            if result.get('success'):
                return f"""✅ **Deposit Successful**

🏦 **Vault**: {vault_info['name']} ({vault_info['name']})
💰 **Amount**: {amount_xlm} XLM
🔗 **Transaction Hash**: `{result.get('hash', 'N/A')}`
📊 **Ledger**: {result.get('ledger', 'N/A')}

Your deposit has been submitted to the Stellar network and should be confirmed shortly.
You can check the status using the transaction hash above.

**Account**: {user_account['public_key'][:8]}...{user_account['public_key'][-8:]}
**User**: {user_id[:8]}..."""
            else:
                error_msg = result.get('error', 'Unknown error')
                return f"❌ **Transaction Failed**: {error_msg}"

        except Exception as e:
            return f"❌ **Transaction Submission Failed**: {str(e)}"

    except Exception as e:
        logger.error(f"Unexpected error in _defindex_deposit: {e}")
        return f"❌ **Unexpected Error**: {str(e)}"

# Export functions for tool factory integration
__all__ = [
    '_defindex_discover_vaults',
    '_defindex_get_vault_details',
    '_defindex_deposit'
]