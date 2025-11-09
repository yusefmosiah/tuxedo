#!/usr/bin/env python3
"""Manual test of DeFindex API with provided key"""

import requests
import json

API_KEY = "sk_3ecdd83da4f0120a69bc6b21c238b0fa924ff32a39c867de6d77d76272a0f672"
BASE_URL = "https://api.defindex.io"

# Test 1: Health check
print("=== Test 1: Health Check ===")
response = requests.get(f"{BASE_URL}/health", timeout=10)
print(f"Status: {response.status_code}")
print(f"Response: {response.text}\n")

# Test 2: Factory address
print("=== Test 2: Factory Address ===")
response = requests.get(
    f"{BASE_URL}/factory/address",
    headers={'Authorization': f'Bearer {API_KEY}'},
    timeout=10
)
print(f"Status: {response.status_code}")
print(f"Response: {response.text}\n")

# Test 3: Get vault info for XLM_HODL_1 on testnet
vault_address = "CAHWRPKBPX4FNLXZOAD565IBSICQPL5QX37IDLGJYOPWX22WWKFWQUBA"
print(f"=== Test 3: Vault Info for {vault_address[:8]}... on TESTNET ===")
response = requests.get(
    f"{BASE_URL}/vault/{vault_address}",
    headers={'Authorization': f'Bearer {API_KEY}'},
    params={'network': 'testnet'},
    timeout=15
)
print(f"Status: {response.status_code}")
print(f"Response: {json.dumps(response.json(), indent=2) if response.status_code == 200 else response.text}\n")

# Test 4: Get vault APY
print(f"=== Test 4: Vault APY for {vault_address[:8]}... on TESTNET ===")
response = requests.get(
    f"{BASE_URL}/vault/{vault_address}/apy",
    headers={'Authorization': f'Bearer {API_KEY}'},
    params={'network': 'testnet'},
    timeout=10
)
print(f"Status: {response.status_code}")
print(f"Response: {json.dumps(response.json(), indent=2) if response.status_code == 200 else response.text}\n")

# Test 5: All 4 testnet vaults
testnet_vaults = {
    'XLM_HODL_1': 'CAHWRPKBPX4FNLXZOAD565IBSICQPL5QX37IDLGJYOPWX22WWKFWQUBA',
    'XLM_HODL_2': 'CCSPRGGUP32M23CTU7RUAGXDNOHSA6O2BS2IK4NVUP5X2JQXKTSIQJKE',
    'XLM_HODL_3': 'CBLXUUHUL7TA3LF3U5G6ZTU7EACBBOSJLR4AYOM5YJKJ4APZ7O547R5T',
    'XLM_HODL_4': 'CCGKL6U2DHSNFJ3NU4UPRUKYE2EUGYR4ZFZDYA7KDJLP3TKSPHD5C4UP'
}

print("=== Test 5: All Testnet Vaults ===")
for name, address in testnet_vaults.items():
    response = requests.get(
        f"{BASE_URL}/vault/{address}",
        headers={'Authorization': f'Bearer {API_KEY}'},
        params={'network': 'testnet'},
        timeout=15
    )
    print(f"{name}: Status {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"  TVL: ${data.get('tvl', 0):,.0f}, APY: {data.get('apy', 0):.2f}%")
    else:
        print(f"  Error: {response.text[:100]}")

