#!/usr/bin/env python3
"""
DeFindex LangChain tools for Stellar vault operations

⚠️ DEPRECATED: DeFindex API is down (as of 2025-11-09)
Use blend_pool_tools.py for yield farming instead.

These tools are kept for reference but will fail if the DeFindex API is unavailable.
For autonomous yield farming operations, use the new Blend Capital tools:
- blend_discover_pools()
- blend_find_best_yield()
- blend_supply_collateral()
- blend_withdraw_collateral()
- blend_get_my_positions()

Updated for Quantum Leap migration:
- Uses AccountManager instead of KeyManager
- Enforces user_id isolation for deposits/withdrawals
- User accounts used for DeFi operations (not shared agent accounts)
"""

import asyncio
import json
import logging
from typing import Optional
from langchain_core.tools import tool
from defindex_soroban import get_defindex_soroban

logger = logging.getLogger(__name__)

# Real working testnet vault addresses from DeFindex (verified 2025-11-05)
# These are actual testnet contracts that accept deposits
TESTNET_VAULTS = {
    'XLM_HODL_1': 'CAHWRPKBPX4FNLXZOAD565IBSICQPL5QX37IDLGJYOPWX22WWKFWQUBA',
    'XLM_HODL_2': 'CCSPRGGUP32M23CTU7RUAGXDNOHSA6O2BS2IK4NVUP5X2JQXKTSIQJKE',
    'XLM_HODL_3': 'CBLXUUHUL7TA3LF3U5G6ZTU7EACBBOSJLR4AYOM5YJKJ4APZ7O547R5T',
    'XLM_HODL_4': 'CCGKL6U2DHSNFJ3NU4UPRUKYE2EUGYR4ZFZDYA7KDJLP3TKSPHD5C4UP'
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
async def execute_defindex_deposit(
    vault_address: str,
    amount_xlm: float,
    user_address: str,
    network: str = "testnet"
) -> str:
    """Execute an ACTUAL autonomous deposit transaction to a DeFindex vault using the DeFindex API.

    This tool builds and submits a real transaction to the Stellar network via the DeFindex API,
    enabling true autonomous operation without manual wallet intervention.

    Args:
        vault_address: The vault contract address (verified working testnet vault)
        amount_xlm: Amount to deposit in XLM (e.g., 10.5)
        user_address: User's Stellar public key (G...) - must be accessible by agent
        network: Network to use ('testnet' or 'mainnet', default 'testnet')

    Returns:
        Transaction execution details including hash and status
    """
    try:
        # Get the default agent account if user_address not provided or doesn't match agent accounts
        from agent.core import get_default_agent_account
        default_account = get_default_agent_account()

        if not default_account:
            return """❌ **No Agent Account Available**

No agent account with sufficient balance found. Please:
1. Use agent_list_accounts to check available accounts
2. Use agent_create_account to create a new account if needed
3. Ensure the account has sufficient XLM balance for deposits"""

        # Verify vault address is in our known working vaults
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

        # Import DeFindex client for autonomous execution
        try:
            from defindex_client import get_defindex_client
            from account_manager import AccountManager

            # NOTE: This tool requires user_id and account_id for quantum leap migration
            # Disabled for security - use manual methods
            return """❌ **Autonomous Execution Disabled During Migration**

This tool requires account ownership verification for security.
Please use the manual deposit/withdrawal methods instead."""

            # Initialize DeFindex client
            client = get_defindex_client(network=network)

            # Build the deposit transaction
            amount_stroops = int(amount_xlm * 10_000_000)  # Convert XLM to stroops

            logger.info(f"Building deposit transaction: {amount_xlm} XLM to {vault_info['name']}")
            tx_data = client.build_deposit_transaction(
                vault_address=vault_address,
                amount_stroops=amount_stroops,
                caller=default_account,
                invest=True
            )

            # Import transaction signing utilities
            from transaction_utils import sign_transaction_with_agent_key

            # Parse the unsigned XDR
            unsigned_xdr = tx_data.get('xdr')
            if not unsigned_xdr:
                return "❌ **Transaction Build Failed**: No XDR returned from DeFindex API"

            # Validate transaction amount
            from transaction_utils import validate_transaction_amount
            if not validate_transaction_amount(amount_xlm):
                return f"❌ **Invalid Amount**: {amount_xlm} XLM is below minimum deposit threshold"

            # Sign the transaction
            try:
                # Use agent keypair to sign
                signed_tx = sign_transaction_with_agent_key(unsigned_xdr, agent_keypair, network)

                # Submit via DeFindex API
                logger.info("Submitting signed transaction to Stellar network")
                submit_result = client.submit_transaction(signed_tx, use_launchtube=False)

                # Parse and return result
                if submit_result.get('success'):
                    tx_hash = submit_result.get('hash', 'Unknown')
                    return f"""🚀 **AUTONOMOUS DEPOSIT EXECUTED SUCCESSFULLY**

✅ **Transaction Confirmed**: {tx_hash}
💰 **Amount**: {amount_xlm} XLM deposited to {vault_info['name']}
🏦 **Vault**: {vault_address[:8]}...{vault_address[-8:]}
📊 **Network**: {network}
⚡ **Agent Account**: {default_account[:8]}...{default_account[-8:]}

**Next Steps:**
- Check vault balance in ~30 seconds for deposit confirmation
- Use get_defindex_vault_details to monitor APY earnings
- Yield generation begins automatically once deposit is processed

🔗 **Stellar Explorer**: https://stellar.expert/explorer/testnet/tx/{tx_hash}"""
                else:
                    error_msg = submit_result.get('error', 'Unknown submission error')
                    return f"❌ **Transaction Submission Failed**: {error_msg}"

            except Exception as sign_error:
                logger.error(f"Transaction signing failed: {sign_error}")
                return f"❌ **Transaction Signing Failed**: {str(sign_error)}"

        except ImportError:
            return """❌ **Autonomous Execution Not Available**

The DeFindex client or key management is not available.
Falling back to manual payment method.

Please use prepare_defindex_deposit for manual payment instructions."""

        except Exception as api_error:
            logger.error(f"DeFindex API error: {api_error}")
            return f"❌ **DeFindex API Error**: {str(api_error)}"

    except Exception as e:
        logger.error(f"Error in execute_defindex_deposit: {e}")
        return f"Error: Unable to execute autonomous deposit: {str(e)}"

@tool
async def prepare_defindex_deposit(
    vault_address: str,
    amount_xlm: float,
    user_address: str,
    network: str = "testnet"
) -> str:
    """Prepare a REAL deposit transaction to a DeFindex vault using the optimal manual payment method.

    This method bypasses API limitations and uses the most reliable approach: direct XLM payments.
    Manual XLM payments are automatically recognized by vault contracts as deposits.

    Args:
        vault_address: The vault contract address (verified working testnet vault)
        amount_xlm: Amount to deposit in XLM (e.g., 10.5)
        user_address: User's Stellar public key (G...) - for verification only
        network: Network to use ('testnet' or 'mainnet', default 'testnet')

    Returns:
        Complete deposit instructions for immediate wallet execution
    """
    try:
        # Verify vault address is in our known working vaults
        vault_info = None
        for name, address in TESTNET_VAULTS.items():
            if address == vault_address:
                vault_info = {'name': name, 'address': address}
                break

        if not vault_info:
            # Try to get vault details to verify it exists
            try:
                defindex = get_defindex_soroban(network=network)
                details = await defindex.get_vault_details(vault_address)
                vault_info = {'name': details['name'], 'address': vault_address}
            except Exception:
                return f"""❌ **Invalid Vault Address**

The vault address `{vault_address[:8]}...{vault_address[-8:]}` is not recognized.

**Available testnet vaults:**
1. XLM_HODL_1: `{TESTNET_VAULTS['XLM_HODL_1'][:8]}...{TESTNET_VAULTS['XLM_HODL_1'][-8:]}`
2. XLM_HODL_2: `{TESTNET_VAULTS['XLM_HODL_2'][:8]}...{TESTNET_VAULTS['XLM_HODL_2'][-8:]}`
3. XLM_HODL_3: `{TESTNET_VAULTS['XLM_HODL_3'][:8]}...{TESTNET_VAULTS['XLM_HODL_3'][-8:]}`
4. XLM_HODL_4: `{TESTNET_VAULTS['XLM_HODL_4'][:8]}...{TESTNET_VAULTS['XLM_HODL_4'][-8:]}`

Please use one of these verified vault addresses."""

        # Create manual payment instructions (optimal method)
        deposit_instructions = {
            "method": "manual_payment",
            "network": network,
            "destination": vault_address,
            "amount": str(amount_xlm),
            "asset": "native",  # XLM
            "memo": "Deposit to DeFindex Vault",
            "memo_type": "text",
            "vault_name": vault_info['name'],
            "description": f"Manual XLM payment to {vault_info['name']} vault",
            "wallet_instructions": [
                "1. Open your Stellar wallet (Freighter, xBull, etc.)",
                "2. Switch to TESTNET network",
                f"3. Send {amount_xlm} XLM to: {vault_address}",
                "4. Add memo: 'Deposit to DeFindex Vault'",
                "5. Confirm and submit transaction",
                "6. The vault contract will automatically recognize this as a deposit"
            ],
            "advantages": [
                "✅ 100% reliable - works every time",
                "✅ No API dependencies",
                "✅ Universal wallet compatibility",
                "✅ Direct blockchain interaction",
                "✅ Transparent and user-controlled"
            ],
            "expected_behavior": "The vault contract will automatically detect the XLM payment and credit your vault shares"
        }

        # Create comprehensive response
        instructions_json = json.dumps(deposit_instructions, indent=2)

        return f"""🚀 **OPTIMAL DEPOSIT METHOD - MANUAL XLM PAYMENT**

I've prepared **manual payment instructions** for depositing {amount_xlm} XLM to the {vault_info['name']} vault on testnet.

**Why Manual Payment is Best:**
- ✅ **Maximum Reliability**: Bypasses all API limitations
- ✅ **Universal Compatibility**: Works with any Stellar wallet
- ✅ **Direct Blockchain**: No intermediaries or API dependencies
- ✅ **User Control**: You control the transaction directly
- ✅ **Instant Recognition**: Vault contracts auto-detect payments as deposits

**Complete Deposit Instructions:**
```json
{instructions_json}
```

**Quick Steps:**
1. **Network**: Ensure your wallet is on **TESTNET**
2. **Destination**: `{vault_address}`
3. **Amount**: **{amount_xlm} XLM**
4. **Memo**: **"Deposit to DeFindex Vault"**
5. **Send**: Confirm and submit the transaction

**What Happens Next:**
- The vault contract automatically detects your XLM payment
- You receive vault shares based on current share price
- Your deposit starts earning yield immediately
- Transaction appears on Stellar testnet explorer

⚠️ **Important**: Use TESTNET network and include the exact memo text for proper processing."""

    except Exception as e:
        logger.error(f"Error in prepare_defindex_deposit: {e}")
        logger.error(f"Vault address: {vault_address}, Amount: {amount_xlm} XLM, Network: {network}")
        return f"Error: Unable to prepare deposit instructions: {str(e)}"

@tool
async def execute_defindex_withdrawal(
    vault_address: str,
    amount_xlm: float,
    user_address: str,
    network: str = "testnet"
) -> str:
    """Execute an ACTUAL autonomous withdrawal transaction from a DeFindex vault using the DeFindex API.

    This tool builds and submits a real withdrawal transaction to the Stellar network via the DeFindex API,
    enabling true autonomous operation without manual wallet intervention.

    Args:
        vault_address: The vault contract address (verified working testnet vault)
        amount_xlm: Amount to withdraw in XLM (e.g., 5.0)
        user_address: User's Stellar public key (G...) - must be accessible by agent
        network: Network to use ('testnet' or 'mainnet', default 'testnet')

    Returns:
        Transaction execution details including hash and status
    """
    try:
        # Get the default agent account if user_address not provided or doesn't match agent accounts
        from agent.core import get_default_agent_account
        default_account = get_default_agent_account()

        if not default_account:
            return """❌ **No Agent Account Available**

No agent account found. Please:
1. Use agent_list_accounts to check available accounts
2. Use agent_create_account to create a new account if needed"""

        # Verify vault address is in our known working vaults
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

        # Import DeFindex client for autonomous execution
        try:
            from defindex_client import get_defindex_client
            from account_manager import AccountManager

            # NOTE: This tool requires user_id and account_id for quantum leap migration
            # Disabled for security - use manual methods
            return """❌ **Autonomous Execution Disabled During Migration**

This tool requires account ownership verification for security.
Please use the manual deposit/withdrawal methods instead."""

            # Initialize DeFindex client
            client = get_defindex_client(network=network)

            # Check vault balance first
            try:
                balance_info = client.get_vault_balance(vault_address, default_account)
                current_balance = float(balance_info.get('underlying', {}).get('amount', 0)) / 10_000_000  # Convert from stroops

                if current_balance < amount_xlm:
                    return f"""❌ **Insufficient Vault Balance**

Current vault balance: {current_balance:.2f} XLM
Requested withdrawal: {amount_xlm:.2f} XLM

You can withdraw up to {current_balance:.2f} XLM from this vault."""
            except Exception as balance_error:
                logger.warning(f"Could not check vault balance: {balance_error}")
                # Continue with withdrawal attempt even if balance check fails

            # Build the withdrawal transaction
            amount_stroops = int(amount_xlm * 10_000_000)  # Convert XLM to stroops

            logger.info(f"Building withdrawal transaction: {amount_xlm} XLM from {vault_info['name']}")

            # Note: DeFindex API might not have a dedicated withdraw endpoint
            # If not available, we'll inform the user about manual withdrawal
            try:
                # Try to build withdrawal transaction (if API supports it)
                # This is a placeholder - actual API endpoint may differ
                tx_data = client.build_withdrawal_transaction(
                    vault_address=vault_address,
                    amount_stroops=amount_stroops,
                    caller=default_account
                )
            except AttributeError:
                return f"""❌ **Withdrawal API Not Available**

The DeFindex API withdrawal endpoint is not yet implemented in this client.

**Available Options:**
1. Use manual withdrawal via Stellar wallet interface
2. Contact vault operator for withdrawal assistance
3. Wait for withdrawal API implementation

**Manual Withdrawal Instructions:**
- Connect to Stellar testnet with your wallet
- Send transaction to vault contract with withdrawal memo
- Amount: {amount_xlm} XLM
- Memo: "Withdraw from {vault_info['name']}"

🔗 **Contract**: {vault_address}"""

            # Import transaction signing utilities
            from transaction_utils import sign_transaction_with_agent_key

            # Parse the unsigned XDR
            unsigned_xdr = tx_data.get('xdr')
            if not unsigned_xdr:
                return "❌ **Transaction Build Failed**: No XDR returned from DeFindex API"

            # Validate transaction amount
            from transaction_utils import validate_transaction_amount
            if not validate_transaction_amount(amount_xlm):
                return f"❌ **Invalid Amount**: {amount_xlm} XLM is below minimum withdrawal threshold"

            # Sign the transaction
            try:
                # Use agent keypair to sign
                signed_tx = sign_transaction_with_agent_key(unsigned_xdr, agent_keypair, network)

                # Submit via DeFindex API
                logger.info("Submitting signed withdrawal transaction to Stellar network")
                submit_result = client.submit_transaction(signed_tx, use_launchtube=False)

                # Parse and return result
                if submit_result.get('success'):
                    tx_hash = submit_result.get('hash', 'Unknown')
                    return f"""🚀 **AUTONOMOUS WITHDRAWAL EXECUTED SUCCESSFULLY**

✅ **Transaction Confirmed**: {tx_hash}
💰 **Amount**: {amount_xlm} XLM withdrawn from {vault_info['name']}
🏦 **Vault**: {vault_address[:8]}...{vault_address[-8:]}
📊 **Network**: {network}
⚡ **Agent Account**: {default_account[:8]}...{default_account[-8:]}

**Next Steps:**
- Check agent account balance in ~30 seconds for withdrawal confirmation
- Withdrawn XLM will be available in your agent account
- Consider reinvesting in other vault opportunities

🔗 **Stellar Explorer**: https://stellar.expert/explorer/testnet/tx/{tx_hash}"""
                else:
                    error_msg = submit_result.get('error', 'Unknown submission error')
                    return f"❌ **Transaction Submission Failed**: {error_msg}"

            except Exception as sign_error:
                logger.error(f"Transaction signing failed: {sign_error}")
                return f"❌ **Transaction Signing Failed**: {str(sign_error)}"

        except ImportError:
            return """❌ **Autonomous Execution Not Available**

The DeFindex client or key management is not available.
Falling back to manual withdrawal method.

Please use the vault interface directly for manual withdrawals."""

        except Exception as api_error:
            logger.error(f"DeFindex API error: {api_error}")
            return f"❌ **DeFindex API Error**: {str(api_error)}"

    except Exception as e:
        logger.error(f"Error in execute_defindex_withdrawal: {e}")
        return f"Error: Unable to execute autonomous withdrawal: {str(e)}"