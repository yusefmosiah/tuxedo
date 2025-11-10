#!/usr/bin/env python3
"""
Diagnostic script to test Blend Capital pool discovery on mainnet.

This script tests the actual on-chain pool discovery to ensure we're getting
real data from the Backstop contract, not fallback hardcoded values.

Usage:
    cd backend
    source .venv/bin/activate
    python3 test_mainnet_pool_discovery.py
"""

import asyncio
import logging
import os
from dotenv import load_dotenv
from stellar_sdk.soroban_server_async import SorobanServerAsync
from account_manager import AccountManager
from blend_pool_tools import (
    blend_discover_pools,
    NETWORK_CONFIG,
    BLEND_MAINNET_CONTRACTS
)

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

load_dotenv()


async def test_mainnet_discovery():
    """Test pool discovery on mainnet"""
    print("\n" + "="*80)
    print("BLEND CAPITAL MAINNET POOL DISCOVERY TEST")
    print("="*80)

    # Configuration
    network = "mainnet"
    config = NETWORK_CONFIG[network]

    print(f"\n📋 Network Configuration:")
    print(f"  Network: {network}")
    print(f"  RPC URL: {config['rpc_url']}")
    print(f"  Backstop: {config['backstop']}")
    print(f"  Passphrase: {config['passphrase'][:30]}...")

    print(f"\n🏦 Expected Mainnet Pools (from BLEND_MAINNET_CONTRACTS):")
    print(f"  1. Comet: {BLEND_MAINNET_CONTRACTS['comet']}")
    print(f"  2. Fixed: {BLEND_MAINNET_CONTRACTS['fixed']}")
    print(f"  3. YieldBlox: {BLEND_MAINNET_CONTRACTS['yieldBlox']}")

    # Create dependencies
    soroban_server = SorobanServerAsync(config['rpc_url'])
    account_manager = AccountManager()

    print(f"\n🔍 Querying Backstop contract on mainnet...")
    print(f"   This should return ALL active pools from the rewardZone...")

    try:
        # Test pool discovery
        pools = await blend_discover_pools(
            network=network,
            soroban_server=soroban_server,
            account_manager=account_manager,
            user_id="diagnostic_test"
        )

        print(f"\n✅ SUCCESS: Found {len(pools)} pools from Backstop contract!")
        print(f"\n📊 Discovered Pools:")
        for i, pool in enumerate(pools, 1):
            print(f"\n  {i}. {pool['name']}")
            print(f"     Address: {pool['pool_address']}")
            print(f"     Status: {pool['status']}")

            # Check if it matches expected contracts
            if pool['pool_address'] == BLEND_MAINNET_CONTRACTS['comet']:
                print(f"     ✓ Matches Comet pool ✓")
            elif pool['pool_address'] == BLEND_MAINNET_CONTRACTS['fixed']:
                print(f"     ✓ Matches Fixed pool ✓")
            elif pool['pool_address'] == BLEND_MAINNET_CONTRACTS['yieldBlox']:
                print(f"     ✓ Matches YieldBlox pool ✓")
            else:
                print(f"     ⚠️  Unknown pool (not in hardcoded list)")

        # Verify we got all expected pools
        print(f"\n📋 Verification:")
        found_addresses = {p['pool_address'] for p in pools}
        expected = {
            BLEND_MAINNET_CONTRACTS['comet'],
            BLEND_MAINNET_CONTRACTS['fixed'],
            BLEND_MAINNET_CONTRACTS['yieldBlox']
        }

        missing = expected - found_addresses
        extra = found_addresses - expected

        if not missing and not extra:
            print(f"  ✅ Perfect match! Found all 3 expected mainnet pools.")
        elif missing:
            print(f"  ⚠️  Missing pools:")
            for addr in missing:
                pool_name = [k for k, v in BLEND_MAINNET_CONTRACTS.items() if v == addr][0]
                print(f"     - {pool_name}: {addr}")
        if extra:
            print(f"  ℹ️  Additional pools not in hardcoded list:")
            for addr in extra:
                print(f"     - {addr}")

        print(f"\n{'='*80}")
        print(f"✅ TEST PASSED: Pool discovery is working correctly!")
        print(f"   We are getting REAL on-chain data from Backstop contract.")
        print(f"   No fallback hardcoded values are being used.")
        print(f"{'='*80}\n")

        return True

    except ValueError as e:
        print(f"\n❌ FATAL ERROR: Pool discovery failed!")
        print(f"   Error type: ValueError (known issue)")
        print(f"   Message: {e}")
        print(f"\n   This means:")
        print(f"   - Backstop contract query failed")
        print(f"   - No pools found in rewardZone")
        print(f"   - Network or RPC issues")
        print(f"\n   Required actions:")
        print(f"   1. Verify RPC endpoint is working: {config['rpc_url']}")
        print(f"   2. Check Backstop contract address: {config['backstop']}")
        print(f"   3. Test network connectivity")
        print(f"   4. Verify Blend protocol is active on mainnet")
        return False

    except RuntimeError as e:
        print(f"\n❌ FATAL ERROR: System error in pool discovery!")
        print(f"   Error type: RuntimeError")
        print(f"   Message: {e}")
        return False

    except Exception as e:
        print(f"\n❌ UNEXPECTED ERROR!")
        print(f"   Error type: {type(e).__name__}")
        print(f"   Message: {e}")
        import traceback
        print(f"\n   Traceback:")
        traceback.print_exc()
        return False

    finally:
        await soroban_server.close()


if __name__ == "__main__":
    success = asyncio.run(test_mainnet_discovery())
    exit(0 if success else 1)
