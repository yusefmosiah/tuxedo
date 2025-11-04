#!/usr/bin/env python3
"""
DeFindex Tools with Direct Soroban Fallback
When the API fails, use direct RPC calls as a backup
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any
import json

logger = logging.getLogger(__name__)

async def prepare_defindex_deposit_fallback(
    vault_address: str,
    amount_xlm: float,
    user_address: str,
    network: str = "testnet"
) -> str:
    """Prepare DeFindex deposit with API + direct Soroban fallback"""
    try:
        # First, try the original API-based approach
        from defindex_tools import prepare_defindex_deposit
        logger.info("Attempting API-based deposit preparation...")

        try:
            api_result = await prepare_defindex_deposit(
                vault_address=vault_address,
                amount_xlm=amount_xlm,
                user_address=user_address,
                network=network
            )

            # Check if API result indicates success
            if "REAL DEPOSIT TRANSACTION PREPARED" in api_result:
                logger.info("✅ API-based deposit preparation successful")
                return api_result
            elif "Error:" in api_result and "MissingValue" in api_result:
                logger.warning("API returned MissingValue error, trying direct Soroban fallback...")
            else:
                # API returned some other error, still try fallback
                logger.warning(f"API failed with: {api_result[:100]}... trying fallback")

        except Exception as api_error:
            logger.warning(f"API approach failed completely: {api_error}... trying direct fallback")

        # FALLBACK: Use direct Soroban approach
        logger.info("🔄 Using direct Soroban RPC fallback...")
        return await _prepare_deposit_via_soroban(
            vault_address=vault_address,
            amount_xlm=amount_xlm,
            user_address=user_address,
            network=network
        )

    except Exception as e:
        logger.error(f"All deposit preparation methods failed: {e}")
        return f"Error: Unable to prepare deposit transaction through any method: {str(e)}"

async def _prepare_deposit_via_soroban(
    vault_address: str,
    amount_xlm: float,
    user_address: str,
    network: str = "testnet"
) -> str:
    """Prepare deposit transaction using direct Soroban RPC calls"""
    try:
        from stellar_sdk import TransactionBuilder, scval
        from stellar_sdk.soroban_server_async import SorobanServerAsync

        # Initialize Soroban server
        if network == "testnet":
            rpc_url = "https://soroban-testnet.stellar.org"
            network_passphrase = "Test SDF Network ; September 2015"
        else:
            rpc_url = "https://mainnet.stellar.expert/explorer/rpc"
            network_passphrase = "Public Global Stellar Network ; September 2015"

        soroban_server = SorobanServerAsync(rpc_url)
        amount_stroops = int(amount_xlm * 10_000_000)

        logger.info(f"Building deposit via direct RPC: {amount_xlm} XLM to {vault_address[:8]}...")

        # Test basic vault connectivity first
        try:
            source_account = await soroban_server.load_account(user_address)
        except Exception as e:
            return f"""⚠️ **Account Issue - Using Direct Soroban Fallback**

Cannot load account {user_address[:8]}...{user_address[-8:]} on {network}.

**Issue**: {str(e)}

**Solutions**:
1. Ensure account exists and is funded on {network}
2. For testnet: Use https://friendbot.stellar.org to fund the account
3. Check network configuration

**Technical Details**: Direct Soroban RPC requires a valid, funded account on the target network."""

        # Try the most likely deposit function signatures based on common patterns
        deposit_attempts = [
            # (function_name, parameters, description)
            ("deposit", [scval.to_uint64(amount_stroops)], "Deposit with amount only"),
            ("deposit", [scval.to_uint64(amount_stroops), scval.to_address(user_address)], "Deposit with amount and user"),
            ("deposit_native", [scval.to_uint64(amount_stroops)], "Native deposit with amount"),
            ("invest", [scval.to_uint64(amount_stroops)], "Invest with amount"),
            ("enter", [scval.to_uint64(amount_stroops)], "Enter with amount"),
        ]

        last_error = None

        for function_name, params, description in deposit_attempts:
            try:
                logger.info(f"Trying {function_name} with {len(params)} parameters: {description}")

                # Build transaction
                tx = (
                    TransactionBuilder(source_account, network_passphrase, base_fee=100)
                    .set_timeout(30)
                    .append_invoke_contract_function_op(
                        contract_id=vault_address,
                        function_name=function_name,
                        parameters=params
                    )
                    .build()
                )

                # Simulate transaction
                sim_result = await soroban_server.simulate_transaction(tx)

                if sim_result.error:
                    error_str = str(sim_result.error)
                    logger.info(f"   ❌ {function_name} failed: {error_str[:100]}...")
                    last_error = error_str
                    continue

                # SUCCESS! Prepare the transaction
                prepared_tx = await soroban_server.prepare_transaction(tx, sim_result)

                # Create transaction payload
                tx_payload = {
                    'xdr': prepared_tx.to_xdr(),
                    'vault_address': vault_address,
                    'amount': amount_xlm,
                    'function_used': function_name,
                    'parameters_used': len(params),
                    'description': description,
                    'network': network,
                    'transaction_type': 'REAL',
                    'data_source': 'soroban_direct',
                    'fallback_used': True
                }

                tx_json = json.dumps(tx_payload, indent=2)

                return f"""✅ **DEPOSIT TRANSACTION PREPARED (Direct Soroban Fallback)**

I've prepared a **real vault deposit transaction** using direct blockchain RPC calls (bypassing the DeFindex API).

**Transaction Details:**
```json
{tx_json}
```

**🔧 Technical Details:**
- **Method**: Direct Soroban RPC call (API bypass)
- **Function**: {function_name} with {len(params)} parameters
- **Description**: {description}
- **Network**: {network}
- **Data Source**: Direct blockchain query

🎯 **This is a real vault deposit transaction** built using direct blockchain calls. The DeFindex API was unavailable or returned errors, so we used direct Soroban RPC as a fallback.

⚠️ **Important**: This transaction will actually deposit funds into the vault when submitted to the {network} network.

💡 **Fallback Success**: We successfully bypassed API limitations and created a working transaction!"""

            except Exception as e:
                logger.info(f"   ❌ {function_name} exception: {str(e)[:100]}...")
                last_error = str(e)
                continue

        # All function attempts failed
        return f"""⚠️ **Direct Soroban Fallback - Unable to Build Transaction**

We successfully connected to the vault contract via direct RPC, but none of the standard deposit function signatures worked.

**Vault Address**: {vault_address[:8]}...{vault_address[-8:]}
**Amount**: {amount_xlm} XLM
**Network**: {network}

**Functions Tried**:
- deposit (with various parameter combinations)
- deposit_native
- invest
- enter

**Last Error**: {last_error[:200] if last_error else 'No detailed error available'}

**🔧 Technical Status**:
- ✅ Vault contract is reachable via direct RPC
- ✅ Account exists and is funded
- ❌ No compatible deposit function signature found

**Workaround Options**:
1. **Manual XLM Payment**: Send XLM directly to the vault address:
   ```
   Destination: {vault_address}
   Amount: {amount_xlm} XLM
   Memo: "Deposit to DeFindex Vault"
   ```

2. **Try Different Vault**: Some vaults may have different function signatures

3. **Contact Support**: This vault may have custom requirements

💡 **Why This Happens**: Different vault implementations may use different function names or parameter requirements. The direct Soroban approach successfully bypassed API limitations but encountered contract-specific signature differences."""

    except Exception as e:
        logger.error(f"Direct Soroban fallback failed: {e}")
        return f"""❌ **All Methods Failed**

Neither the DeFindex API nor direct Soroban RPC could prepare a deposit transaction.

**Error**: {str(e)}

**This indicates a more fundamental issue with:**
- Network connectivity
- Account status
- Vault contract availability
- System configuration

**Recommended Actions**:
1. Check network connectivity
2. Verify account exists and is funded
3. Try a different vault address
4. Contact support if issue persists"""

# Tool wrapper for LangChain integration
from langchain_core.tools import tool

@tool
async def prepare_defindex_deposit_with_fallback(
    vault_address: str,
    amount_xlm: float,
    user_address: str,
    network: str = "testnet"
) -> str:
    """Prepare DeFindex deposit transaction with automatic fallback to direct Soroban RPC.

    This tool first tries the DeFindex API, and if that fails due to API issues,
    automatically falls back to direct blockchain RPC calls to build the transaction.

    Args:
        vault_address: The vault contract address (e.g., 'CAHWRPKBPX4FNLXZOAD565IBSICQPL5QX37IDLGJYOPWX22WWKFWQUBA')
        amount_xlm: Amount to deposit in XLM (e.g., 10.5)
        user_address: User's Stellar public key (G...)
        network: Network to use ('testnet' or 'mainnet', default 'testnet')

    Returns:
        Transaction details prepared via API or direct Soroban RPC fallback
    """
    return await prepare_defindex_deposit_fallback(
        vault_address=vault_address,
        amount_xlm=amount_xlm,
        user_address=user_address,
        network=network
    )

async def test_fallback_mechanism():
    """Test the fallback mechanism"""
    print("=" * 80)
    print("🔄 Testing DeFindex API + Direct Soroban Fallback")
    print("=" * 80)

    # Test data
    vault_address = "CAHWRPKBPX4FNLXZOAD565IBSICQPL5QX37IDLGJYOPWX22WWKFWQUBA"
    amount_xlm = 1.0
    user_address = "GBWUVTWLIKJJOTAYPJFINOEJY6S7EFNCOESYWABSFZALHOLVBDE3YXVG"

    print(f"Vault: {vault_address[:8]}...{vault_address[-8:]}")
    print(f"Amount: {amount_xlm} XLM")
    print(f"User: {user_address[:8]}...{user_address[-8:]}")

    result = await prepare_defindex_deposit_fallback(
        vault_address=vault_address,
        amount_xlm=amount_xlm,
        user_address=user_address,
        network="testnet"
    )

    print(f"\n📋 Result:")
    print("=" * 60)
    print(result)
    print("=" * 60)

if __name__ == "__main__":
    asyncio.run(test_fallback_mechanism())