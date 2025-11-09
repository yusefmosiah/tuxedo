#!/usr/bin/env python3
"""
Test DeFindex API with our 4 testnet vaults to see why discover_high_yield_vaults is failing
"""

import os
import sys
import requests
import json

# Hardcoded testnet vault addresses from defindex_tools.py
TESTNET_VAULTS = {
    'XLM_HODL_1': 'CAHWRPKBPX4FNLXZOAD565IBSICQPL5QX37IDLGJYOPWX22WWKFWQUBA',
    'XLM_HODL_2': 'CCSPRGGUP32M23CTU7RUAGXDNOHSA6O2BS2IK4NVUP5X2JQXKTSIQJKE',
    'XLM_HODL_3': 'CBLXUUHUL7TA3LF3U5G6ZTU7EACBBOSJLR4AYOM5YJKJ4APZ7O547R5T',
    'XLM_HODL_4': 'CCGKL6U2DHSNFJ3NU4UPRUKYE2EUGYR4ZFZDYA7KDJLP3TKSPHD5C4UP'
}

def test_api_key():
    """Test if we have a valid API key"""
    api_key = os.getenv('DEFINDEX_API_KEY', 'sk_3ecdd83da4f0120a69bc6b21c238b0fa924ff32a39c867de6d77d76272a0f672')

    print("=" * 80)
    print("🔑 Testing DeFindex API Key")
    print("=" * 80)
    print(f"API Key (masked): {api_key[:10]}...{api_key[-10:]}")
    print()

    return api_key

def test_vault_endpoint(vault_name, vault_address, api_key, network='testnet'):
    """Test individual vault endpoint"""
    base_url = "https://api.defindex.io"

    print(f"\n📊 Testing: {vault_name}")
    print(f"   Address: {vault_address}")
    print(f"   Network: {network}")

    session = requests.Session()
    session.headers.update({
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json'
    })

    # Test 1: Get vault info
    try:
        print(f"\n   → GET /vault/{vault_address[:8]}...?network={network}")
        response = session.get(
            f"{base_url}/vault/{vault_address}",
            params={'network': network},
            timeout=15
        )

        print(f"   ✅ Status: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Response received")
            print(f"   📋 Keys: {list(data.keys())}")

            # Display key fields
            if 'name' in data:
                print(f"   📛 Name: {data.get('name')}")
            if 'symbol' in data:
                print(f"   💱 Symbol: {data.get('symbol')}")
            if 'apy' in data:
                print(f"   📈 APY: {data.get('apy')}%")
            if 'tvl' in data:
                print(f"   💰 TVL: ${data.get('tvl'):,.2f}")

            return True, data
        else:
            print(f"   ❌ Error: {response.status_code}")
            print(f"   📄 Response: {response.text[:200]}")
            return False, None

    except Exception as e:
        print(f"   ❌ Exception: {str(e)}")
        return False, None

def test_health_endpoint(api_key):
    """Test health endpoint"""
    base_url = "https://api.defindex.io"

    print("\n🏥 Testing Health Endpoint")
    print(f"   → GET /health")

    try:
        session = requests.Session()
        session.headers.update({
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json'
        })

        response = session.get(f"{base_url}/health", timeout=10)
        print(f"   ✅ Status: {response.status_code}")

        if response.status_code == 200:
            print(f"   ✅ API is healthy")
            return True
        else:
            print(f"   ❌ API health check failed")
            return False

    except Exception as e:
        print(f"   ❌ Exception: {str(e)}")
        return False

def main():
    print("\n" + "=" * 80)
    print("🔬 DeFindex API Manual Test - Testnet Vault Discovery")
    print("=" * 80)

    # Get API key
    api_key = test_api_key()

    # Test health endpoint
    test_health_endpoint(api_key)

    # Test each testnet vault
    print("\n" + "=" * 80)
    print("🏦 Testing All 4 Testnet Vaults")
    print("=" * 80)

    results = {}
    for vault_name, vault_address in TESTNET_VAULTS.items():
        success, data = test_vault_endpoint(vault_name, vault_address, api_key, network='testnet')
        results[vault_name] = {
            'success': success,
            'data': data
        }

    # Summary
    print("\n" + "=" * 80)
    print("📊 SUMMARY")
    print("=" * 80)

    successful = sum(1 for r in results.values() if r['success'])
    total = len(results)

    print(f"\n✅ Successful: {successful}/{total}")
    print(f"❌ Failed: {total - successful}/{total}")

    if successful > 0:
        print(f"\n🎉 API can access {successful} testnet vault(s)")
        print("\n💡 The issue is likely in the tool's error handling or fallback logic")
    else:
        print("\n⚠️  API cannot access any testnet vaults")
        print("\n💡 Possible reasons:")
        print("   1. API key doesn't have testnet access")
        print("   2. Testnet vaults are not registered in DeFindex API")
        print("   3. Network parameter not working correctly")
        print("   4. These addresses are not valid DeFindex vaults")

    # Show detailed vault data if available
    if successful > 0:
        print("\n" + "=" * 80)
        print("📋 VAULT DATA (First successful vault)")
        print("=" * 80)

        for vault_name, result in results.items():
            if result['success'] and result['data']:
                print(f"\n{vault_name}:")
                print(json.dumps(result['data'], indent=2))
                break

    print("\n" + "=" * 80)

if __name__ == "__main__":
    main()
