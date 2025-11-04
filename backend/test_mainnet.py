#!/usr/bin/env python3
import sys
import os
from dotenv import load_dotenv

# Load environment and set path
sys.path.insert(0, '.')
load_dotenv()

from defindex_client import get_defindex_client

def test_mainnet_vaults():
    """Test mainnet vault addresses to confirm they work"""
    mainnet_vaults = {
        'USDC_Blend_Fixed': 'CDB2WMKQQNVZMEBY7Q7GZ5C7E7IAFSNMZ7GGVD6WKTCEWK7XOIAVZSAP',
        'XLM_Blend_Fixed': 'CDPWNUW7UMCSVO36VAJSQHQECISPJLCPDASKHRC5SEROAAZDUQ5DG2Z'
    }

    client = get_defindex_client('mainnet')
    print('Testing mainnet vault addresses...')

    results = {}

    for token, address in mainnet_vaults.items():
        print(f'\nTesting {token} vault: {address}')
        try:
            vault_info = client.get_vault_info(address)
            print(f'✅ {token} vault info retrieved:')
            print(f'   Name: {vault_info.get("name", "Unknown")}')
            print(f'   APY: {vault_info.get("apy", 0):.1f}%')
            print(f'   TVL: ${vault_info.get("tvl", 0):,.0f}')
            print(f'   Symbol: {vault_info.get("symbol", "Unknown")}')
            results[token] = 'SUCCESS'
        except Exception as e:
            print(f'❌ {token} vault failed: {e}')
            results[token] = f'FAILED: {str(e)[:100]}...'

    return results

if __name__ == "__main__":
    test_mainnet_vaults()