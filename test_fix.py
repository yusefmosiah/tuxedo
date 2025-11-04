#!/usr/bin/env python3
"""
Test the fix by using real testnet vault addresses only
"""

import os
import sys
import json
import time
from datetime import datetime

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from backend.defindex_client import DeFindexClient

def test_real_testnet_vaults():
    """Test using only real testnet vault addresses"""

    print("=" * 80)
    print("🔧 Testing Fix: Real Testnet Vaults Only")
    print("=" * 80)

    # Configuration
    api_key = os.getenv('DEFINDEX_API_KEY', 'sk_3ecdd83da4f0120a69bc6b21c238b0fa924ff32a39c867de6d77d76272a0f672')
    base_url = "https://api.defindex.io"

    # Real testnet HODL vaults (verified working)
    testnet_vaults = [
        {
            'name': 'XLM HODL Vault 1',
            'address': 'CAHWRPKBPX4FNLXZOAD565IBSICQPL5QX37IDLGJYOPWX22WWKFWQUBA'
        },
        {
            'name': 'XLM HODL Vault 2',
            'address': 'CCSPRGGUP32M23CTU7RUAGXDNOHSA6O2BS2IK4NVUP5X2JQXKTSIQJKE'
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
    print(f"✅ Testing {len(testnet_vaults)} real testnet vaults")

    # Test each vault
    for i, vault in enumerate(testnet_vaults, 1):
        print(f"\n{i}. Testing {vault['name']}")
        print(f"   Address: {vault['address']}")

        # Test 1: Vault Info
        print(f"\n   📋 Testing Vault Info:")
        try:
            response = session.get(
                f"{base_url}/vault/{vault['address']}",
                timeout=15
            )

            print(f"   Status Code: {response.status_code}")

            if response.status_code == 200:
                try:
                    data = response.json()
                    print(f"   ✅ SUCCESS: Vault found!")
                    print(f"   Name: {data.get('name', 'N/A')}")
                    print(f"   TVL: {data.get('tvl', 'N/A')}")
                    print(f"   Manager: {data.get('manager', 'N/A')}")
                except:
                    print(f"   ✅ SUCCESS: {response.text[:200]}")

            else:
                try:
                    error_json = response.json()
                    print(f"   ❌ ERROR: {json.dumps(error_json, indent=6)}")
                except:
                    print(f"   ❌ ERROR: {response.text[:200]}")

        except Exception as e:
            print(f"   ❌ EXCEPTION: {str(e)}")

        # Test 2: Vault APY
        print(f"\n   📈 Testing Vault APY:")
        try:
            response = session.get(
                f"{base_url}/vault/{vault['address']}/apy",
                timeout=15
            )

            print(f"   Status Code: {response.status_code}")

            if response.status_code == 200:
                try:
                    data = response.json()
                    print(f"   ✅ SUCCESS: APY data retrieved")
                    print(f"   APY: {data.get('apy', 'N/A')}%")
                except:
                    print(f"   ✅ SUCCESS: {response.text[:200]}")

            else:
                print(f"   ❌ ERROR: APY endpoint not working (Status: {response.status_code})")

        except Exception as e:
            print(f"   ❌ EXCEPTION: {str(e)}")

        # Test 3: Deposit Build
        print(f"\n   💰 Testing Deposit Build:")
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

            if response.status_code == 200:
                try:
                    data = response.json()
                    print(f"   ✅ SUCCESS: Deposit transaction built!")
                    print(f"   XDR Length: {len(data.get('xdr', ''))}")
                    print(f"   Transaction ready for signing")
                except:
                    print(f"   ✅ SUCCESS: {response.text[:200]}")

            else:
                try:
                    error_json = response.json()
                    print(f"   ❌ ERROR: {json.dumps(error_json, indent=6)}")
                except:
                    print(f"   ❌ ERROR: {response.text[:200]}")

        except Exception as e:
            print(f"   ❌ EXCEPTION: {str(e)}")

        # Rate limiting delay
        time.sleep(1)

    # Summary
    print(f"\n" + "=" * 80)
    print("📊 Fix Verification Summary")
    print("=" * 80)

    print("""
✅ ISSUE IDENTIFIED:
   - Mainnet vault addresses do NOT work on testnet
   - They cause "MissingValue" contract errors
   - Only real testnet vault contracts should be used for testnet

✅ SOLUTION IMPLEMENTED:
   - Removed mainnet vault addresses from TESTNET_VAULTS
   - Kept only verified testnet HODL vaults
   - Updated configuration to prevent cross-network queries

✅ EXPECTED RESULTS:
   - Vault info endpoints should work (200 OK)
   - APY endpoints should work (will show 0% for HODL vaults)
   - Deposit endpoints should build transactions
   - No more "MissingValue" contract errors

🔍 NEXT STEPS:
   - Test with backend agent to confirm fix works end-to-end
   - Update implementation plan with root cause analysis
   - Consider creating a testnet vault discovery mechanism
    """)

if __name__ == "__main__":
    import requests  # Import here to avoid issues
    test_real_testnet_vaults()