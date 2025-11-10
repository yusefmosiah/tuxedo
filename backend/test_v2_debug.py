#!/usr/bin/env python3
"""
Debug V2 implementation to understand the error
"""

import asyncio
import os
import logging
from dotenv import load_dotenv
from stellar_sdk.soroban_server_async import SorobanServerAsync
from account_manager import AccountManager
from stellar_soroban import soroban_operations

# Load environment variables from .env file
load_dotenv()

# Set up logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def test_v2_debug():
    """Debug the V2 implementation step by step"""

    # Initialize
    rpc_url = os.getenv('ANKR_STELLER_RPC', 'https://rpc.ankr.com/stellar_soroban')
    soroban_server = SorobanServerAsync(rpc_url)
    account_manager = AccountManager()

    pool_address = 'CAS3FL6TLZKDGGSISDBWGGPXT3NRR4DYTZD7YOD3HMYO6LTJUVGRVEAM'
    usdc_address = 'CCW67TSZV3SSS2HXMBQ5JFGCKJNXKZM7UQUWUZPUTHXSTZLEO7SJMI75'

    user_id = "test"

    try:
        logger.info("Testing soroban_operations with get_ledger_entries...")

        # Construct ledger keys exactly as in V2
        ledger_keys = [
            {
                "type": "contract_data",
                "contract_id": pool_address,
                "key": {
                    "vec": [
                        {"type": "symbol", "value": "ResData"},
                        {"type": "address", "value": usdc_address}
                    ]
                },
                "durability": "PERSISTENT"
            },
            {
                "type": "contract_data",
                "contract_id": pool_address,
                "key": {
                    "vec": [
                        {"type": "symbol", "value": "ResConfig"},
                        {"type": "address", "value": usdc_address}
                    ]
                },
                "durability": "PERSISTENT"
            }
        ]

        logger.info(f"Ledger keys: {ledger_keys}")

        result = await soroban_operations(
            action="get_ledger_entries",
            user_id=user_id,
            soroban_server=soroban_server,
            account_manager=account_manager,
            ledger_keys=ledger_keys,
            network_passphrase="Public Global Stellar Network ; September 2015"
        )

        logger.info(f"Result: {result}")

        if result.get('success'):
            logger.info("✅ Success!")
            return True
        else:
            logger.error(f"❌ Failed: {result}")
            return False

    except Exception as e:
        logger.error(f"Exception: {e}", exc_info=True)
        return False
    finally:
        await soroban_server.close()

if __name__ == "__main__":
    success = asyncio.run(test_v2_debug())
    print(f"\nTest {'PASSED' if success else 'FAILED'}")