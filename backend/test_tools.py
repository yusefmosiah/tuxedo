#!/usr/bin/env python3
"""
Test enhanced DeFindex tools
"""

import asyncio
from defindex_tools import discover_high_yield_vaults, get_defindex_vault_details

async def test_tools():
    print('Testing enhanced DeFindex tools...')

    # Test vault discovery tool
    print('\n=== Testing discover_high_yield_vaults ===')
    result = await discover_high_yield_vaults.run({'min_apy': 25.0})
    print(result)

    # Test vault details tool (using a known vault address)
    print('\n\n=== Testing get_defindex_vault_details ===')
    vault_address = 'CCSRX5E4337QMCMC3KO3RDFYI57T5NZV5XB3W3TWE4USCASKGL5URKJL'  # USDC Blend Yieldblox
    result = await get_defindex_vault_details.run({'vault_address': vault_address})
    print(result)

if __name__ == "__main__":
    asyncio.run(test_tools())