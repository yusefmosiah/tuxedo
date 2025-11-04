#!/usr/bin/env python3
"""
Debug script to systematically test DeFindex API endpoints
"""

import os
import sys
import json
import time
from datetime import datetime

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from backend.defindex_client import DeFindexClient, get_defindex_client

def test_api_endpoints():
    """Test each DeFindex API endpoint individually"""

    print("=" * 80)
    print("🔍 DeFindex API Debugging Script")
    print("=" * 80)
    print(f"Timestamp: {datetime.now().isoformat()}")

    # Test configuration
    api_key = os.getenv('DEFINDEX_API_KEY')
    if not api_key:
        print("❌ DEFINDEX_API_KEY not found in environment")
        return

    print(f"✅ API Key found: {api_key[:10]}...{api_key[-10:]}")

    # Initialize client
    try:
        client = get_defindex_client(network='testnet')
        print(f"✅ Client initialized for network: {client.network}")
        print(f"✅ Base URL: {client.base_url}")
        print(f"✅ Factory Address: {client.factory_address}")
    except Exception as e:
        print(f"❌ Failed to initialize client: {e}")
        return

    # Test endpoints one by one
    endpoints_to_test = [
        {
            'name': 'Health Check',
            'method': 'GET',
            'url': '/health',
            'test_func': lambda: test_health_endpoint(client)
        },
        {
            'name': 'Factory Address',
            'method': 'GET',
            'url': '/factory/address',
            'test_func': lambda: test_factory_endpoint(client)
        },
        {
            'name': 'Vault Info (XLM Blend Yieldblox)',
            'method': 'GET',
            'url': '/vault/CBDOIGFO2QOOZTWQZ7AFPH5JOUS2SBN5CTTXR665NHV6GOCM6OUGI5KP',
            'test_func': lambda: test_vault_info_endpoint(client)
        },
        {
            'name': 'Vault APY (XLM Blend Yieldblox)',
            'method': 'GET',
            'url': '/vault/CBDOIGFO2QOOZTWQZ7AFPH5JOUS2SBN5CTTXR665NHV6GOCM6OUGI5KP/apy',
            'test_func': lambda: test_vault_apy_endpoint(client)
        },
        {
            'name': 'Deposit Transaction Build',
            'method': 'POST',
            'url': '/vault/CBDOIGFO2QOOZTWQZ7AFPH5JOUS2SBN5CTTXR665NHV6GOCM6OUGI5KP/deposit',
            'test_func': lambda: test_deposit_endpoint(client)
        }
    ]

    print("\n" + "=" * 80)
    print("🧪 Testing API Endpoints")
    print("=" * 80)

    results = {}

    for i, endpoint in enumerate(endpoints_to_test, 1):
        print(f"\n{i}. Testing {endpoint['name']}")
        print(f"   Method: {endpoint['method']}")
        print(f"   URL: {endpoint['url']}")

        try:
            result = endpoint['test_func']()
            results[endpoint['name']] = result
            print(f"   Status: ✅ {result}")
        except Exception as e:
            results[endpoint['name']] = f"❌ ERROR: {str(e)}"
            print(f"   Status: ❌ ERROR: {str(e)}")

            # Try to capture more error details
            if hasattr(e, 'response') and e.response:
                print(f"   Response Status: {e.response.status_code}")
                print(f"   Response Headers: {dict(e.response.headers)}")
                try:
                    error_json = e.response.json()
                    print(f"   Response Body: {json.dumps(error_json, indent=2)}")
                except:
                    print(f"   Response Text: {e.response.text[:500]}")

        # Add delay to avoid rate limiting
        time.sleep(2)

    # Summary
    print("\n" + "=" * 80)
    print("📊 Test Results Summary")
    print("=" * 80)

    success_count = 0
    for name, result in results.items():
        status = "✅ PASS" if not result.startswith("❌") else "❌ FAIL"
        print(f"{status} {name}: {result}")
        if not result.startswith("❌"):
            success_count += 1

    print(f"\nOverall: {success_count}/{len(endpoints_to_test)} endpoints working")

    if success_count < len(endpoints_to_test):
        print("\n🚨 Issues Found:")
        print("1. Check if API key has correct permissions")
        print("2. Verify network (testnet vs mainnet) compatibility")
        print("3. Check rate limiting patterns")
        print("4. Validate vault addresses for testnet")

def test_health_endpoint(client):
    """Test the health endpoint"""
    response = client.session.get(f"{client.base_url}/health", timeout=10)
    response.raise_for_status()
    data = response.json()
    return f"OK - {json.dumps(data)}"

def test_factory_endpoint(client):
    """Test the factory address endpoint"""
    response = client.session.get(f"{client.base_url}/factory/address", timeout=10)
    response.raise_for_status()
    data = response.json()
    return f"OK - Factory: {data.get('address', 'N/A')}"

def test_vault_info_endpoint(client):
    """Test vault info endpoint"""
    vault_address = "CBDOIGFO2QOOZTWQZ7AFPH5JOUS2SBN5CTTXR665NHV6GOCM6OUGI5KP"
    response = client.session.get(f"{client.base_url}/vault/{vault_address}", timeout=15)
    response.raise_for_status()
    data = response.json()
    return f"OK - Vault exists, Name: {data.get('name', 'N/A')}"

def test_vault_apy_endpoint(client):
    """Test vault APY endpoint"""
    vault_address = "CBDOIGFO2QOOZTWQZ7AFPH5JOUS2SBN5CTTXR665NHV6GOCM6OUGI5KP"
    response = client.session.get(f"{client.base_url}/vault/{vault_address}/apy", timeout=10)
    response.raise_for_status()
    data = response.json()
    return f"OK - APY: {data.get('apy', 'N/A')}%"

def test_deposit_endpoint(client):
    """Test deposit transaction building endpoint"""
    vault_address = "CBDOIGFO2QOOZTWQZ7AFPH5JOUS2SBN5CTTXR665NHV6GOCM6OUGI5KP"
    test_user = "GBWUVTWLIKJJOTAYPJFINOEJY6S7EFNCOESYWABSFZALHOLVBDE3YXVG"

    data = {
        'amounts': [10000000],  # 1 XLM in stroops
        'from': test_user,
        'invest': True,
        'slippageBps': 50
    }

    response = client.session.post(
        f"{client.base_url}/vault/{vault_address}/deposit",
        json=data,
        timeout=30
    )
    response.raise_for_status()
    result = response.json()
    return f"OK - Transaction built, XDR length: {len(result.get('xdr', ''))}"

if __name__ == "__main__":
    # Set environment
    os.environ.setdefault('DEFINDEX_API_KEY', 'sk_3ecdd83da4f0120a69bc6b21c238b0fa924ff32a39c867de6d77d76272a0f672')

    test_api_endpoints()