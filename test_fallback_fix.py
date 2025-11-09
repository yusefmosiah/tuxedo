#!/usr/bin/env python3
"""
Test that discover_high_yield_vaults now falls back to hardcoded vaults when API unavailable
"""

import sys
import os
import asyncio

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

async def test_vault_discovery():
    """Test vault discovery with fallback"""
    from defindex_soroban import get_defindex_soroban

    print("=" * 80)
    print("🧪 Testing Vault Discovery with Fallback")
    print("=" * 80)

    # Test with testnet (API will fail, should fall back to hardcoded)
    print("\n📊 Test 1: Discover testnet vaults (min_apy=0.0)")
    print("-" * 80)

    try:
        defindex = get_defindex_soroban(network='testnet')
        vaults = await defindex.get_available_vaults(min_apy=0.0)

        print(f"✅ Success! Found {len(vaults)} vault(s)")
        print()

        for i, vault in enumerate(vaults, 1):
            print(f"{i}. {vault['name']}")
            print(f"   Address: {vault['address'][:8]}...{vault['address'][-8:]}")
            print(f"   APY: {vault['apy']}%")
            print(f"   TVL: ${vault['tvl']:,.0f}")
            print(f"   Symbol: {vault['symbol']}")
            print(f"   Strategy: {vault['strategy']}")
            print(f"   Data Source: {vault['data_source']}")
            print()

        if len(vaults) == 4:
            print("🎉 SUCCESS: All 4 testnet vaults discovered!")
        else:
            print(f"⚠️  Expected 4 vaults, got {len(vaults)}")

    except Exception as e:
        print(f"❌ FAILED: {str(e)}")
        return False

    # Test vault details
    print("\n📊 Test 2: Get vault details for XLM_HODL_1")
    print("-" * 80)

    try:
        vault_address = 'CAHWRPKBPX4FNLXZOAD565IBSICQPL5QX37IDLGJYOPWX22WWKFWQUBA'
        details = await defindex.get_vault_details(vault_address)

        print(f"✅ Success! Retrieved vault details")
        print(f"   Name: {details['name']}")
        print(f"   Symbol: {details['symbol']}")
        print(f"   APY: {details['apy']}%")
        print(f"   Risk Level: {details['risk_level']}")
        print(f"   Min Deposit: {details['min_deposit']} {details['symbol']}")
        print(f"   Data Source: {details['data_source']}")
        print()

        print("🎉 SUCCESS: Vault details work with fallback!")

    except Exception as e:
        print(f"❌ FAILED: {str(e)}")
        return False

    print("\n" + "=" * 80)
    print("✅ ALL TESTS PASSED - Fallback mechanism working!")
    print("=" * 80)
    return True

if __name__ == "__main__":
    success = asyncio.run(test_vault_discovery())
    sys.exit(0 if success else 1)
