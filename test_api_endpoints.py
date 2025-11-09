#!/usr/bin/env python3
"""
Test different DeFindex API endpoints to understand authentication requirements
"""

import requests
import json

API_KEY = 'sk_5808bde3d41aeef6bc224a2342ed181309376585c700528b8a18f21abe30fbf8'
BASE_URL = 'https://api.defindex.io'

def test_endpoint(name, url, params=None, auth=True):
    """Test an endpoint with optional auth"""
    print(f"\n📡 Testing: {name}")
    print(f"   URL: {url}")
    if params:
        print(f"   Params: {params}")

    headers = {'Content-Type': 'application/json'}
    if auth:
        headers['Authorization'] = f'Bearer {API_KEY}'
        print(f"   Auth: Bearer {API_KEY[:15]}...")
    else:
        print(f"   Auth: None")

    try:
        response = requests.get(url, headers=headers, params=params, timeout=10)
        print(f"   ✅ Status: {response.status_code}")

        if response.status_code == 200:
            try:
                data = response.json()
                print(f"   📋 Response: {json.dumps(data, indent=6)[:500]}")
            except:
                print(f"   📋 Response: {response.text[:200]}")
        else:
            print(f"   ❌ Error: {response.text[:200]}")

        return response.status_code, response
    except Exception as e:
        print(f"   ❌ Exception: {str(e)}")
        return None, None

print("=" * 80)
print("🔬 DeFindex API Endpoint Discovery")
print("=" * 80)

# Test 1: Health endpoint (no auth)
test_endpoint("Health (no auth)", f"{BASE_URL}/health", auth=False)

# Test 2: Health endpoint (with auth)
test_endpoint("Health (with auth)", f"{BASE_URL}/health", auth=True)

# Test 3: Factory address
test_endpoint("Factory address", f"{BASE_URL}/factory/address", auth=True)

# Test 4: Try mainnet vault (known working)
MAINNET_VAULT = 'CDB2WMKQQNVZMEBY7Q7GZ5C7E7IAFSNMZ7GGVD6WKTCEWK7XOIAVZSAP'  # USDC_Blend_Fixed
test_endpoint("Mainnet vault (testnet param)", f"{BASE_URL}/vault/{MAINNET_VAULT}",
              params={'network': 'testnet'}, auth=True)

test_endpoint("Mainnet vault (mainnet param)", f"{BASE_URL}/vault/{MAINNET_VAULT}",
              params={'network': 'mainnet'}, auth=True)

test_endpoint("Mainnet vault (no network param)", f"{BASE_URL}/vault/{MAINNET_VAULT}",
              auth=True)

# Test 5: Testnet vault
TESTNET_VAULT = 'CAHWRPKBPX4FNLXZOAD565IBSICQPL5QX37IDLGJYOPWX22WWKFWQUBA'  # XLM_HODL_1
test_endpoint("Testnet vault (testnet param)", f"{BASE_URL}/vault/{TESTNET_VAULT}",
              params={'network': 'testnet'}, auth=True)

test_endpoint("Testnet vault (mainnet param)", f"{BASE_URL}/vault/{TESTNET_VAULT}",
              params={'network': 'mainnet'}, auth=True)

test_endpoint("Testnet vault (no network param)", f"{BASE_URL}/vault/{TESTNET_VAULT}",
              auth=True)

print("\n" + "=" * 80)
