#!/usr/bin/env python3
"""
Test enhanced DeFindex system
"""

import asyncio
from defindex_soroban import get_defindex_soroban

async def test_enhanced_system():
    print('Testing enhanced DeFindex system...')

    # Test vault discovery
    defindex = get_defindex_soroban('mainnet')
    vaults = await defindex.get_available_vaults(min_apy=20.0)

    print(f'Found {len(vaults)} vaults with APY >= 20%')
    print('\nTop 3 vaults:')
    for i, vault in enumerate(vaults[:3], 1):
        print(f'{i}. {vault["name"]} ({vault["symbol"]})')
        print(f'   APY: {vault["apy"]:.1f}% | TVL: ${vault["tvl"]:,.0f}')
        print(f'   Strategy: {vault.get("strategy", "Unknown")} | Type: {vault.get("asset_type", "Unknown")}')

    # Test vault details
    if vaults:
        vault_address = vaults[0]['address']
        details = await defindex.get_vault_details(vault_address)
        print(f'\nSample vault details for {details["name"]}:')
        print(f'   Risk Level: {details.get("risk_level", "Unknown")}')
        print(f'   Fees: {details.get("fees", {})}')
        print(f'   Strategies: {len(details.get("strategies", []))} active')

if __name__ == "__main__":
    asyncio.run(test_enhanced_system())