#!/usr/bin/env python3
"""
Test enhanced DeFindex functions directly
"""

import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import the actual function definitions (not the @tool decorated versions)
from defindex_soroban import get_defindex_soroban

async def test_vault_discovery():
    """Test vault discovery functionality"""
    print('Testing vault discovery functionality...')

    defindex = get_defindex_soroban('mainnet')
    vaults = await defindex.get_available_vaults(min_apy=20.0)

    print(f'Found {len(vaults)} vaults with APY >= 20%')
    print('\nTop 5 vaults:')
    for i, vault in enumerate(vaults[:5], 1):
        print(f'{i}. {vault["name"]} ({vault["symbol"]})')
        print(f'   APY: {vault["apy"]:.1f}% | TVL: ${vault["tvl"]:,.0f}')
        print(f'   Strategy: {vault.get("strategy", "Unknown")} | Type: {vault.get("asset_type", "Unknown")}')
        print(f'   Address: {vault["address"][:16]}...{vault["address"][-8:]}')
        print()

async def test_vault_details():
    """Test vault details functionality"""
    print('Testing vault details functionality...')

    # Use a known vault address
    vault_address = 'CCSRX5E4337QMCMC3KO3RDFYI57T5NZV5XB3W3TWE4USCASKGL5URKJL'  # USDC Blend Yieldblox

    defindex = get_defindex_soroban('mainnet')
    details = await defindex.get_vault_details(vault_address)

    print(f'Vault Details: {details["name"]}')
    print(f'Symbol: {details["symbol"]} | Type: {details.get("asset_type", "Unknown")}')
    print(f'Current APY: {details["apy"]:.1f}% | Risk: {details.get("risk_level", "Unknown")}')
    print(f'Total Value Locked: ${details["tvl"]:,.0f}')

    # Fee structure
    fees = details.get('fees', {})
    if fees:
        print(f'\nFee Structure:')
        print(f'• Deposit Fee: {fees.get("deposit", "N/A")}')
        print(f'• Withdrawal Fee: {fees.get("withdrawal", "N/A")}')
        print(f'• Performance Fee: {fees.get("performance", "N/A")}')
        print(f'• Minimum Deposit: {details.get("min_deposit", "N/A")} {details["symbol"]}')

    # Strategies
    strategies = details.get('strategies', [])
    if strategies:
        print(f'\nActive Strategies:')
        for i, strategy in enumerate(strategies, 1):
            status = "PAUSED" if strategy.get('paused') else "Active"
            print(f'{i}. {strategy.get("name", "Unknown Strategy")} - {status}')
            if strategy.get('description'):
                print(f'   {strategy.get("description")}')

    # Historical performance
    historical = details.get('historical_apy', {})
    if historical:
        print(f'\nHistorical Performance:')
        print(f'1 Month APY: {historical.get("1m", 0):.1f}%')
        print(f'3 Month APY: {historical.get("3m", 0):.1f}%')
        print(f'1 Year APY: {historical.get("1y", 0):.1f}%')

async def main():
    await test_vault_discovery()
    await test_vault_details()

if __name__ == "__main__":
    asyncio.run(main())