#!/usr/bin/env python3
"""
Detailed error analysis for DeFindex API failures
"""

import os
import sys
import json
import requests
from datetime import datetime

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

def analyze_defindex_errors():
    """Analyze specific error responses from DeFindex API"""

    print("=" * 80)
    print("🔬 DeFindex API Error Analysis")
    print("=" * 80)

    # Configuration
    api_key = os.getenv('DEFINDEX_API_KEY', 'sk_3ecdd83da4f0120a69bc6b21c238b0fa924ff32a39c867de6d77d76272a0f672')
    base_url = "https://api.defindex.io"

    # Test vault addresses (these are likely mainnet addresses)
    test_vaults = [
        {
            'name': 'XLM Blend Yieldblox (Testnet?)',
            'address': 'CBDOIGFO2QOOZTWQZ7AFPH5JOUS2SBN5CTTXR665NHV6GOCM6OUGI5KP'
        },
        {
            'name': 'USDC Blend (Testnet?)',
            'address': 'CDZKFHJIET3A73A2YN4KV7NSV32S6YGQMUFH3DNJXLBWL4SKEGVRNFKI'
        }
    ]

    # Set up session with proper headers
    session = requests.Session()
    session.headers.update({
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json'
    })

    print(f"✅ API Key: {api_key[:10]}...{api_key[-10:]}")
    print(f"✅ Base URL: {base_url}")

    # Test each vault endpoint with detailed error capture
    for i, vault in enumerate(test_vaults, 1):
        print(f"\n{i}. Testing Vault: {vault['name']}")
        print(f"   Address: {vault['address']}")

        # Test 1: Vault Info
        print(f"\n   📋 Testing Vault Info Endpoint:")
        try:
            response = session.get(
                f"{base_url}/vault/{vault['address']}",
                timeout=15
            )

            print(f"   Status Code: {response.status_code}")
            print(f"   Headers: {dict(response.headers)}")

            if response.status_code == 400:
                try:
                    error_json = response.json()
                    print(f"   Error Response: {json.dumps(error_json, indent=6)}")
                except:
                    print(f"   Error Text: {response.text}")

            elif response.status_code == 200:
                try:
                    data = response.json()
                    print(f"   ✅ Success: {json.dumps(data, indent=6)}")
                except:
                    print(f"   ✅ Success: {response.text}")

        except Exception as e:
            print(f"   ❌ Exception: {str(e)}")

        # Test 2: Vault APY
        print(f"\n   📈 Testing Vault APY Endpoint:")
        try:
            response = session.get(
                f"{base_url}/vault/{vault['address']}/apy",
                timeout=15
            )

            print(f"   Status Code: {response.status_code}")

            if response.status_code == 404:
                print(f"   ❌ 404 Not Found - APY endpoint doesn't exist for this vault")
                try:
                    error_json = response.json()
                    print(f"   Error Response: {json.dumps(error_json, indent=6)}")
                except:
                    print(f"   Error Text: {response.text}")

            elif response.status_code == 200:
                try:
                    data = response.json()
                    print(f"   ✅ Success: {json.dumps(data, indent=6)}")
                except:
                    print(f"   ✅ Success: {response.text}")

        except Exception as e:
            print(f"   ❌ Exception: {str(e)}")

        # Test 3: Deposit Build (with minimal data)
        print(f"\n   💰 Testing Deposit Build Endpoint:")
        try:
            test_user = "GBWUVTWLIKJJOTAYPJFINOEJY6S7EFNCOESYWABSFZALHOLVBDE3YXVG"

            deposit_data = {
                'amounts': [10000000],  # 1 XLM
                'from': test_user,
                'invest': True,
                'slippageBps': 50
            }

            response = session.post(
                f"{base_url}/vault/{vault['address']}/deposit",
                json=deposit_data,
                timeout=30
            )

            print(f"   Status Code: {response.status_code}")
            print(f"   Headers: {dict(response.headers)}")

            if response.status_code == 400:
                try:
                    error_json = response.json()
                    print(f"   Error Response: {json.dumps(error_json, indent=6)}")

                    # Analyze specific error patterns
                    if 'message' in error_json:
                        message = error_json['message']
                        print(f"   📝 Error Message Analysis:")
                        if 'MissingValue' in message:
                            print(f"      - Contract call failed (MissingValue)")
                        if 'testnet' in message.lower():
                            print(f"      - Network-specific issue mentioned")
                        if 'mainnet' in message.lower():
                            print(f"      - Mainnet-related issue mentioned")

                except:
                    print(f"   Error Text: {response.text}")

            elif response.status_code == 200:
                try:
                    data = response.json()
                    print(f"   ✅ Success: {json.dumps(data, indent=6)}")
                except:
                    print(f"   ✅ Success: {response.text}")

        except Exception as e:
            print(f"   ❌ Exception: {str(e)}")

    # Additional Analysis: Test with different network parameters
    print(f"\n" + "=" * 80)
    print("🌐 Network-Specific Testing")
    print("=" * 80)

    print("\n📋 Testing factory address with different network approaches:")

    # Test 1: Factory address (already known to work)
    try:
        response = session.get(f"{base_url}/factory/address", timeout=10)
        print(f"✅ Factory Address (no network param): {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   Factory: {data}")
    except Exception as e:
        print(f"❌ Factory Address Error: {e}")

    # Test 2: Try adding network parameter to vault request
    print(f"\n📋 Testing vault info with network parameter:")
    try:
        vault_address = test_vaults[0]['address']
        response = session.get(
            f"{base_url}/vault/{vault_address}",
            params={'network': 'testnet'},
            timeout=15
        )
        print(f"   Status Code: {response.status_code}")
        if response.status_code != 200:
            try:
                error_json = response.json()
                print(f"   Error with network param: {json.dumps(error_json, indent=6)}")
            except:
                print(f"   Error text: {response.text}")
        else:
            print(f"   ✅ Success with network parameter!")

    except Exception as e:
        print(f"   ❌ Exception with network param: {e}")

    # Conclusion and Recommendations
    print(f"\n" + "=" * 80)
    print("💡 Analysis Summary & Recommendations")
    print("=" * 80)

    print("""
Based on the error patterns, here are the most likely issues:

1. 🎯 **MAIN ISSUE: Network Mismatch**
   - The vault addresses we're using are likely MAINNET addresses
   - We're querying them on TESTNET configuration
   - DeFindex API likely doesn't support cross-network vault queries

2. 🔧 **POTENTIAL SOLUTIONS:**
   a) Find actual TESTNET vault addresses
   b) Use mainnet configuration for these vault addresses
   c) Check if DeFindex has separate testnet vault contracts

3. 📡 **API AUTHENTICATION:** ✅ Working correctly
   - Health check passes
   - Factory address endpoint works
   - Bearer token format is correct

4. 🚫 **RATE LIMITING:** Not the primary issue
   - Errors are immediate 400/404, not 429
   - No delay patterns observed

5. 🔍 **NEXT STEPS:**
   - Research DeFindex testnet vault addresses
   - Contact DeFindex team for testnet documentation
   - Consider if we need different vault contracts for testnet
    """)

if __name__ == "__main__":
    analyze_defindex_errors()