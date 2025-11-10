# DeFindex Integration Restoration Guide
## Incremental & Iterative Implementation Plan

**Document Version:** 1.0
**Date:** 2025-11-10
**Status:** Ready for execution
**Network:** Mainnet only (real funds)

---

## Overview

This guide provides a step-by-step, incremental approach to restoring DeFindex integration in Tuxedo. Each phase includes:
- Clear implementation steps
- Configuration checkpoints (⏸️ STOP for user input)
- Verification tests
- Success criteria
- Rollback instructions

**Total Estimated Time:** 2-4 hours (with breaks for configuration)

---

## Prerequisites Checklist

Before starting, verify:
- [ ] Git repository is clean (no uncommitted changes)
- [ ] Backend virtual environment is active (`source backend/.venv/bin/activate`)
- [ ] Current working directory is project root (`/home/user/tuxedo`)
- [ ] Backend server is NOT running (we'll restart it after changes)

---

## Phase 0: API Verification (15 minutes)

### Goal
Verify DeFindex API is accessible and responding before restoring any code.

### Steps

**0.1 Test API Health**
```bash
# Test basic connectivity
curl -v https://api.defindex.io/health

# Expected: {"status":{"reachable":true}}
# Status code: 200
```

**0.2 Test Factory Endpoint (no auth required)**
```bash
# Test factory address endpoint
curl -v https://api.defindex.io/factory/address

# Expected: Returns factory contract address
# Status code: 200
```

**0.3 Create Minimal Test Script**
```bash
cat > backend/test_defindex_phase0.py << 'EOF'
#!/usr/bin/env python3
"""Phase 0: Basic API connectivity test"""
import requests

def test_api_health():
    """Test DeFindex API health endpoint"""
    try:
        response = requests.get("https://api.defindex.io/health", timeout=10)
        print(f"Health endpoint: {response.status_code}")
        print(f"Response: {response.json()}")
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_factory_endpoint():
    """Test factory address endpoint"""
    try:
        response = requests.get("https://api.defindex.io/factory/address", timeout=10)
        print(f"Factory endpoint: {response.status_code}")
        print(f"Response: {response.json()}")
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    print("=== Phase 0: DeFindex API Verification ===\n")

    health_ok = test_api_health()
    print()
    factory_ok = test_factory_endpoint()

    print("\n=== Results ===")
    print(f"Health endpoint: {'✅ PASS' if health_ok else '❌ FAIL'}")
    print(f"Factory endpoint: {'✅ PASS' if factory_ok else '❌ FAIL'}")

    if health_ok and factory_ok:
        print("\n✅ Phase 0 complete - API is accessible")
        print("📋 Next: Proceed to Phase 1 (restore API client)")
    else:
        print("\n❌ Phase 0 failed - API may be down")
        print("🛑 STOP: Contact PaltaLabs team before proceeding")
EOF

chmod +x backend/test_defindex_phase0.py
```

**0.4 Run Test**
```bash
cd backend
python test_defindex_phase0.py
```

### Success Criteria
- ✅ Health endpoint returns 200 with `{"status":{"reachable":true}}`
- ✅ Factory endpoint returns 200 with contract address
- ✅ No connection errors or timeouts

### ⏸️ STOP: Phase 0 Decision Point

**If tests PASS:** Proceed to Phase 1
**If tests FAIL:** Stop and investigate:
- Check internet connectivity
- Verify API URL hasn't changed
- Contact PaltaLabs team for API status
- Consider postponing restoration

### Rollback
```bash
# Clean up test file if stopping
rm backend/test_defindex_phase0.py
```

---

## Phase 1: Restore API Client (30 minutes)

### Goal
Restore the DeFindex API client with modern configuration and test authentication.

### Steps

**1.1 Restore API Client File**
```bash
# Extract defindex_client.py from working commit
git show e89fd86:backend/defindex_client.py > backend/defindex_client.py

# Verify file was created
ls -lh backend/defindex_client.py
```

**1.2 Review and Update Configuration**
```bash
# Open file and verify base URL
grep "base_url" backend/defindex_client.py

# Expected: self.base_url = "https://api.defindex.io"
```

**1.3 Create Environment Variable Template**
```bash
cat >> backend/.env.example << 'EOF'

# DeFindex API Configuration
DEFINDEX_API_KEY=sk_your_api_key_here_contact_paltalabs
DEFINDEX_BASE_URL=https://api.defindex.io
EOF
```

### ⏸️ STOP: API Key Required

**Action Required:** Obtain DeFindex API key

**Option A - Have existing key:**
```bash
# Add to backend/.env
echo "DEFINDEX_API_KEY=sk_your_actual_key_here" >> backend/.env
echo "DEFINDEX_BASE_URL=https://api.defindex.io" >> backend/.env
```

**Option B - Need new key:**
1. Contact PaltaLabs team:
   - Email: team@paltalabs.io (or via their Discord)
   - Request: "API key for Tuxedo AI agent DeFindex integration"
   - Mention: Mainnet operations for yield farming
2. Wait for API key response
3. Add to `backend/.env` as shown in Option A

**Option C - Test without key first (limited functionality):**
```bash
# Use placeholder for now
echo "DEFINDEX_API_KEY=sk_placeholder_testing_only" >> backend/.env
echo "DEFINDEX_BASE_URL=https://api.defindex.io" >> backend/.env

# Note: Most endpoints will fail without real key
```

**📋 Configuration Checklist:**
- [ ] `DEFINDEX_API_KEY` added to `backend/.env`
- [ ] `DEFINDEX_BASE_URL` added to `backend/.env`
- [ ] API key starts with `sk_` (standard format)
- [ ] No extra spaces or quotes in .env file

### Steps (continued)

**1.4 Create Phase 1 Test Script**
```bash
cat > backend/test_defindex_phase1.py << 'EOF'
#!/usr/bin/env python3
"""Phase 1: API client authentication test"""
import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import the restored client
try:
    from defindex_client import DeFindexClient
    print("✅ DeFindexClient imported successfully")
except ImportError as e:
    print(f"❌ Failed to import DeFindexClient: {e}")
    sys.exit(1)

def test_client_creation():
    """Test client instantiation"""
    api_key = os.getenv('DEFINDEX_API_KEY')
    if not api_key:
        print("❌ DEFINDEX_API_KEY not found in environment")
        return False

    if api_key == "sk_placeholder_testing_only":
        print("⚠️  Using placeholder API key - authenticated endpoints will fail")

    try:
        client = DeFindexClient(api_key=api_key, network="mainnet")
        print(f"✅ Client created for network: {client.network}")
        print(f"   Base URL: {client.base_url}")
        return True
    except Exception as e:
        print(f"❌ Failed to create client: {e}")
        return False

def test_connection():
    """Test API connection with authentication"""
    api_key = os.getenv('DEFINDEX_API_KEY')
    client = DeFindexClient(api_key=api_key, network="mainnet")

    try:
        connected = client.test_connection()
        if connected:
            print("✅ API connection successful (authenticated)")
            return True
        else:
            print("❌ API connection failed")
            return False
    except Exception as e:
        print(f"❌ Connection error: {e}")
        return False

if __name__ == "__main__":
    print("=== Phase 1: DeFindex API Client Test ===\n")

    creation_ok = test_client_creation()
    print()

    if creation_ok:
        connection_ok = test_connection()
    else:
        connection_ok = False

    print("\n=== Results ===")
    print(f"Client creation: {'✅ PASS' if creation_ok else '❌ FAIL'}")
    print(f"API connection: {'✅ PASS' if connection_ok else '❌ FAIL'}")

    if creation_ok and connection_ok:
        print("\n✅ Phase 1 complete - API client authenticated")
        print("📋 Next: Proceed to Phase 2 (test vault queries)")
    else:
        print("\n⚠️  Phase 1 incomplete")
        if not creation_ok:
            print("   - Check defindex_client.py was restored correctly")
        if not connection_ok:
            print("   - Verify DEFINDEX_API_KEY is correct")
            print("   - Check API key has proper permissions")
EOF

chmod +x backend/test_defindex_phase1.py
```

**1.5 Run Test**
```bash
cd backend
python test_defindex_phase1.py
```

### Success Criteria
- ✅ DeFindexClient imports without errors
- ✅ Client instantiates with mainnet configuration
- ✅ `test_connection()` returns True with authenticated endpoints

### Troubleshooting

**Import Error:**
```bash
# Check file exists and has content
ls -lh backend/defindex_client.py
head -20 backend/defindex_client.py
```

**Authentication Error (403/401):**
- Verify API key is correct (starts with `sk_`)
- Check API key hasn't expired
- Contact PaltaLabs if key seems valid but fails

**Connection Error:**
- Verify internet connectivity
- Check if corporate firewall blocks api.defindex.io
- Try with different network

### Rollback
```bash
# Remove restored files
rm backend/defindex_client.py
rm backend/test_defindex_phase1.py

# Remove env vars (optional)
sed -i '/DEFINDEX_API_KEY/d' backend/.env
sed -i '/DEFINDEX_BASE_URL/d' backend/.env
```

---

## Phase 2: Test Vault Queries (30 minutes)

### Goal
Verify we can query vault data from the API without contract interaction errors.

### Steps

**2.1 Create Vault Query Test**
```bash
cat > backend/test_defindex_phase2.py << 'EOF'
#!/usr/bin/env python3
"""Phase 2: Vault query testing"""
import os
import sys
from dotenv import load_dotenv

load_dotenv()

from defindex_client import DeFindexClient

# Known mainnet vault address (USDC_Blend_Fixed from previous integration)
TEST_VAULT = "CDB2WMKQQNVZMEBY7Q7GZ5C7E7IAFSNMZ7GGVD6WKTCEWK7XOIAVZSAP"

def test_vault_query():
    """Test querying a specific vault"""
    api_key = os.getenv('DEFINDEX_API_KEY')
    client = DeFindexClient(api_key=api_key, network="mainnet")

    print(f"Testing vault: {TEST_VAULT}")

    try:
        vaults = client.get_vaults([TEST_VAULT])

        if vaults:
            print(f"✅ Retrieved {len(vaults)} vault(s)")
            for vault in vaults:
                print(f"\nVault Details:")
                print(f"  Name: {vault.get('name', 'N/A')}")
                print(f"  Symbol: {vault.get('symbol', 'N/A')}")
                print(f"  APY: {vault.get('apy', 0)}%")
                print(f"  TVL: ${vault.get('tvl', 0):,.0f}")
                print(f"  Address: {vault.get('address', 'N/A')}")
            return True
        else:
            print("⚠️  No vault data returned (may be uninitialized)")
            return False

    except Exception as e:
        print(f"❌ Vault query error: {e}")

        # Check if it's the old "MissingValue" error
        if "MissingValue" in str(e):
            print("\n⚠️  KNOWN ISSUE: Vault contract not initialized")
            print("   This is the same error from previous integration")
            print("   API is working, but vault contracts may need initialization")
            return False

        return False

def test_factory_vaults():
    """Test getting vault list from factory (if available)"""
    api_key = os.getenv('DEFINDEX_API_KEY')
    client = DeFindexClient(api_key=api_key, network="mainnet")

    print("\nTesting factory vault discovery...")

    try:
        # Try to get all vaults (no specific addresses)
        # Note: This may not be supported by API
        vaults = client.get_vaults([])

        if vaults:
            print(f"✅ Discovered {len(vaults)} vaults from factory")
            return True
        else:
            print("ℹ️  Factory vault listing not available")
            print("   (API requires specific vault addresses)")
            return None  # Not a failure, just not supported

    except Exception as e:
        if "requires specific vault addresses" in str(e).lower():
            print("ℹ️  Factory listing not supported (expected)")
            return None
        else:
            print(f"⚠️  Factory query error: {e}")
            return False

if __name__ == "__main__":
    print("=== Phase 2: DeFindex Vault Query Test ===\n")

    vault_ok = test_vault_query()
    print()
    factory_result = test_factory_vaults()

    print("\n=== Results ===")
    print(f"Vault query: {'✅ PASS' if vault_ok else '❌ FAIL'}")
    print(f"Factory discovery: {'✅ PASS' if factory_result else 'ℹ️  NOT AVAILABLE' if factory_result is None else '❌ FAIL'}")

    if vault_ok:
        print("\n✅ Phase 2 complete - Vault queries working")
        print("📋 Next: Proceed to Phase 3 (restore Soroban integration)")
    else:
        print("\n⚠️  Phase 2 incomplete - Vault queries failing")
        print("\n🔍 Diagnosis:")
        print("   - If 'MissingValue' error: Vault contracts may not be initialized")
        print("   - If 403/401 error: Check API key permissions")
        print("   - If 404 error: Vault address may be wrong")

        print("\n📋 Options:")
        print("   A) Contact PaltaLabs for current working vault addresses")
        print("   B) Proceed to Phase 3 anyway (may work with different vaults)")
        print("   C) Stop and wait for vault initialization")
EOF

chmod +x backend/test_defindex_phase2.py
```

**2.2 Run Test**
```bash
cd backend
python test_defindex_phase2.py
```

### Success Criteria
- ✅ Vault query returns data (name, APY, TVL)
- ✅ No "MissingValue" contract errors
- ✅ APY data is reasonable (0-50% range)

### ⏸️ STOP: Phase 2 Decision Point

**If vault query SUCCEEDS:**
- ✅ Proceed to Phase 3 (restore full Soroban integration)

**If vault query FAILS with "MissingValue":**
- ⚠️ This is the SAME issue from the previous integration
- **Decision Required:**
  - **Option A:** Contact PaltaLabs for initialized vault addresses
  - **Option B:** Proceed with Phase 3 but expect limited functionality
  - **Option C:** Stop restoration and document API limitations

**If vault query FAILS with 403/401:**
- ❌ API key issue
- Check key permissions with PaltaLabs
- May need different key tier for vault queries

### ⏸️ USER INPUT REQUIRED

**Question:** Did Phase 2 vault query succeed?

**If YES:**
```bash
# Document working vault address
echo "# Working vault addresses verified $(date)" >> backend/.env
echo "# Test vault: CDB2WMKQQNVZMEBY7Q7GZ5C7E7IAFSNMZ7GGVD6WKTCEWK7XOIAVZSAP" >> backend/.env
```

**If NO (MissingValue error):**
```bash
# Document the issue
echo "# NOTE: Vault contracts have initialization issues (MissingValue)" >> backend/.env
echo "# May need updated vault addresses from PaltaLabs team" >> backend/.env
```

**Prompt for user:**
> "Should we proceed to Phase 3 even with vault query issues? (y/n)"

### Rollback
```bash
rm backend/test_defindex_phase2.py
# Phase 1 files remain for retry
```

---

## Phase 3: Restore Soroban Integration (45 minutes)

### Goal
Restore Soroban contract integration layer for on-chain vault interactions.

### Prerequisites
- Phase 1 completed (API client working)
- Decision made on Phase 2 results (proceed even if limited)

### Steps

**3.1 Restore Soroban Integration File**
```bash
# Extract defindex_soroban.py from working commit
git show e89fd86:backend/defindex_soroban.py > backend/defindex_soroban.py

# Verify file was created
ls -lh backend/defindex_soroban.py
```

**3.2 Update Network Configuration**
```bash
# Review mainnet vault addresses in the file
grep -A 10 "MAINNET_VAULTS" backend/defindex_soroban.py

# Review testnet vault addresses
grep -A 10 "TESTNET_VAULTS" backend/defindex_soroban.py
```

### ⏸️ STOP: Vault Address Configuration

**Action Required:** Update vault addresses if Phase 2 revealed issues

**Option A - Phase 2 succeeded (use existing addresses):**
```bash
# No changes needed
echo "✅ Using vault addresses from restored file"
```

**Option B - Phase 2 failed (update addresses):**
```bash
# Manual edit required
nano backend/defindex_soroban.py

# Update MAINNET_VAULTS dictionary with working addresses
# Example:
# MAINNET_VAULTS = {
#     'USDC_Blend_Fixed': 'CDB2WMKQQNVZMEBY7Q7GZ5C7E7IAFSNMZ7GGVD6WKTCEWK7XOIAVZSAP',
#     # Add other confirmed working addresses...
# }
```

**Option C - Unknown working addresses:**
```bash
# Leave file as-is for now
# Document that addresses may need updates
echo "# TODO: Update vault addresses in defindex_soroban.py" >> backend/DEFINDEX_NOTES.md
```

**📋 Configuration Checklist:**
- [ ] Reviewed `MAINNET_VAULTS` dictionary
- [ ] Reviewed `TESTNET_VAULTS` dictionary (optional, we're mainnet-only)
- [ ] Updated addresses if needed based on Phase 2 results
- [ ] Documented any address issues

### Steps (continued)

**3.3 Create Phase 3 Test Script**
```bash
cat > backend/test_defindex_phase3.py << 'EOF'
#!/usr/bin/env python3
"""Phase 3: Soroban integration test"""
import os
import sys
import asyncio
from dotenv import load_dotenv

load_dotenv()

# Import the restored Soroban integration
try:
    from defindex_soroban import DeFindexSoroban, MAINNET_VAULTS
    print("✅ DeFindexSoroban imported successfully")
except ImportError as e:
    print(f"❌ Failed to import DeFindexSoroban: {e}")
    sys.exit(1)

async def test_soroban_creation():
    """Test Soroban client instantiation"""
    try:
        defindex = DeFindexSoroban(network="mainnet")
        print(f"✅ DeFindexSoroban created for network: {defindex.network}")
        print(f"   Available vaults: {len(defindex.vaults)}")
        for name in list(defindex.vaults.keys())[:3]:  # Show first 3
            print(f"   - {name}")
        return True
    except Exception as e:
        print(f"❌ Failed to create DeFindexSoroban: {e}")
        return False

async def test_vault_discovery():
    """Test vault discovery with APY data"""
    defindex = DeFindexSoroban(network="mainnet")

    print("\nTesting vault discovery with APY data...")

    try:
        # Try to get vaults with 0% minimum APY (show all)
        vaults = await defindex.get_available_vaults(min_apy=0.0)

        if vaults:
            print(f"✅ Discovered {len(vaults)} vaults")
            for vault in vaults[:3]:  # Show first 3
                print(f"\n  {vault['name']}")
                print(f"    APY: {vault['apy']:.1f}%")
                print(f"    TVL: ${vault['tvl']:,.0f}")
                print(f"    Strategy: {vault.get('strategy', 'Unknown')}")
            return True
        else:
            print("⚠️  No vaults discovered")
            return False

    except ValueError as e:
        print(f"❌ Vault discovery error: {e}")
        if "API client not available" in str(e):
            print("   - DeFindex API client failed to initialize")
            print("   - Check DEFINDEX_API_KEY in .env")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

async def test_vault_details():
    """Test getting details for a specific vault"""
    defindex = DeFindexSoroban(network="mainnet")

    # Use first vault from MAINNET_VAULTS
    test_vault_address = list(MAINNET_VAULTS.values())[0]
    test_vault_name = list(MAINNET_VAULTS.keys())[0]

    print(f"\nTesting vault details for: {test_vault_name}")
    print(f"Address: {test_vault_address[:8]}...{test_vault_address[-8:]}")

    try:
        details = await defindex.get_vault_details(test_vault_address)

        print(f"✅ Retrieved vault details")
        print(f"  Name: {details['name']}")
        print(f"  Symbol: {details['symbol']}")
        print(f"  APY: {details['apy']:.1f}%")
        print(f"  TVL: ${details['tvl']:,.0f}")

        strategies = details.get('strategies', [])
        if strategies:
            print(f"  Strategies: {len(strategies)} active")

        return True

    except Exception as e:
        print(f"⚠️  Vault details error: {e}")
        return False

async def run_tests():
    """Run all Phase 3 tests"""
    print("=== Phase 3: DeFindex Soroban Integration Test ===\n")

    creation_ok = await test_soroban_creation()
    print()

    if creation_ok:
        discovery_ok = await test_vault_discovery()
        print()
        details_ok = await test_vault_details()
    else:
        discovery_ok = False
        details_ok = False

    print("\n=== Results ===")
    print(f"Soroban creation: {'✅ PASS' if creation_ok else '❌ FAIL'}")
    print(f"Vault discovery: {'✅ PASS' if discovery_ok else '❌ FAIL'}")
    print(f"Vault details: {'✅ PASS' if details_ok else '⚠️  PARTIAL' if not details_ok and discovery_ok else '❌ FAIL'}")

    if creation_ok and discovery_ok:
        print("\n✅ Phase 3 complete - Soroban integration working")
        print("📋 Next: Proceed to Phase 4 (restore account tools)")
    elif creation_ok:
        print("\n⚠️  Phase 3 partial - Soroban created but queries limited")
        print("📋 Options:")
        print("   A) Proceed to Phase 4 with limited functionality")
        print("   B) Update vault addresses and retry Phase 3")
    else:
        print("\n❌ Phase 3 failed - Check dependencies")

if __name__ == "__main__":
    asyncio.run(run_tests())
EOF

chmod +x backend/test_defindex_phase3.py
```

**3.4 Run Test**
```bash
cd backend
python test_defindex_phase3.py
```

### Success Criteria
- ✅ DeFindexSoroban instantiates for mainnet
- ✅ Vault discovery returns at least 1 vault
- ✅ Vault details query succeeds for at least 1 vault
- ✅ APY and TVL data is present and reasonable

### Troubleshooting

**Import errors:**
```bash
# Check dependencies (stellar-sdk, etc.)
pip list | grep -i stellar
pip install stellar-sdk  # If missing
```

**API client not available:**
- Verify Phase 1 completed successfully
- Check `defindex_client.py` exists and has no syntax errors

**No vaults discovered:**
- Check vault addresses in `MAINNET_VAULTS`
- Try updating with addresses from PaltaLabs docs

### ⏸️ STOP: Phase 3 Decision Point

**Question:** Did Phase 3 tests pass?

**If FULL PASS (all 3 tests):**
- ✅ Proceed to Phase 4

**If PARTIAL PASS (creation OK, queries limited):**
- ⚠️ Decide: Proceed with limited functionality or pause?
- Document limitations in `backend/DEFINDEX_NOTES.md`

**If FAIL:**
- ❌ Review errors and troubleshoot
- May need to contact PaltaLabs for support

### Rollback
```bash
rm backend/defindex_soroban.py
rm backend/test_defindex_phase3.py
# Phase 1-2 files remain for retry
```

---

## Phase 4: Restore Account Tools (45 minutes)

### Goal
Restore LangChain tool wrappers that integrate with AccountManager for user isolation.

### Prerequisites
- Phase 1-3 completed (at least partially)
- AccountManager system is working (already exists in codebase)

### Steps

**4.1 Restore Account Tools File**
```bash
# Extract defindex_account_tools.py from working commit
git show e89fd86:backend/defindex_account_tools.py > backend/defindex_account_tools.py

# Verify file was created
ls -lh backend/defindex_account_tools.py
```

**4.2 Review User Isolation Implementation**
```bash
# Check that tools use user_id parameter
grep "user_id" backend/defindex_account_tools.py | head -10

# Check AccountManager integration
grep "AccountManager" backend/defindex_account_tools.py | head -5
```

**4.3 Verify Testnet Vault Constants Match Soroban**
```bash
# Compare TESTNET_VAULTS in both files
echo "=== defindex_soroban.py ==="
grep -A 5 "TESTNET_VAULTS = {" backend/defindex_soroban.py

echo ""
echo "=== defindex_account_tools.py ==="
grep -A 5 "TESTNET_VAULTS = {" backend/defindex_account_tools.py
```

**If they differ:**
```bash
# Update defindex_account_tools.py to match defindex_soroban.py
nano backend/defindex_account_tools.py
# Manually sync the TESTNET_VAULTS dictionary
```

**4.4 Create Phase 4 Test Script**
```bash
cat > backend/test_defindex_phase4.py << 'EOF'
#!/usr/bin/env python3
"""Phase 4: Account tools test (read-only functions)"""
import os
import sys
import asyncio
from dotenv import load_dotenv

load_dotenv()

# Import the restored account tools
try:
    from defindex_account_tools import (
        _defindex_discover_vaults,
        _defindex_get_vault_details
    )
    print("✅ Account tools imported successfully")
except ImportError as e:
    print(f"❌ Failed to import account tools: {e}")
    sys.exit(1)

async def test_discover_function():
    """Test vault discovery function with user_id"""
    test_user_id = "test_user_phase4"

    print(f"Testing vault discovery for user: {test_user_id}")

    try:
        result = await _defindex_discover_vaults(
            min_apy=0.0,
            user_id=test_user_id
        )

        print(f"✅ Discovery function executed")
        print(f"\nResult preview (first 500 chars):")
        print(result[:500])

        # Check for expected content
        if "vault" in result.lower() or "apy" in result.lower():
            print("\n✅ Result contains expected vault/APY data")
            return True
        elif "error" in result.lower() or "unable" in result.lower():
            print("\n⚠️  Result indicates error condition")
            print(f"Full result:\n{result}")
            return False
        else:
            print("\n⚠️  Unexpected result format")
            return False

    except Exception as e:
        print(f"❌ Discovery function error: {e}")
        return False

async def test_vault_details_function():
    """Test vault details function with user_id"""
    test_user_id = "test_user_phase4"

    # Use a known vault address
    from defindex_soroban import MAINNET_VAULTS
    test_vault = list(MAINNET_VAULTS.values())[0]
    test_name = list(MAINNET_VAULTS.keys())[0]

    print(f"\nTesting vault details for: {test_name}")
    print(f"Address: {test_vault[:8]}...{test_vault[-8:]}")

    try:
        result = await _defindex_get_vault_details(
            vault_address=test_vault,
            user_id=test_user_id
        )

        print(f"✅ Details function executed")
        print(f"\nResult preview (first 500 chars):")
        print(result[:500])

        # Check for expected content
        if "vault details" in result.lower() or "apy" in result.lower():
            print("\n✅ Result contains expected vault details")
            return True
        elif "error" in result.lower() or "not found" in result.lower():
            print("\n⚠️  Result indicates error condition")
            return False
        else:
            print("\n⚠️  Unexpected result format")
            return False

    except Exception as e:
        print(f"❌ Details function error: {e}")
        return False

async def run_tests():
    """Run all Phase 4 tests"""
    print("=== Phase 4: DeFindex Account Tools Test ===\n")

    discovery_ok = await test_discover_function()
    details_ok = await test_vault_details_function()

    print("\n=== Results ===")
    print(f"Discover function: {'✅ PASS' if discovery_ok else '❌ FAIL'}")
    print(f"Details function: {'✅ PASS' if details_ok else '❌ FAIL'}")

    if discovery_ok and details_ok:
        print("\n✅ Phase 4 complete - Account tools working")
        print("📋 Next: Proceed to Phase 5 (integrate with AI agent)")
    elif discovery_ok or details_ok:
        print("\n⚠️  Phase 4 partial - Some tools working")
        print("📋 Options:")
        print("   A) Proceed to Phase 5 with working tools only")
        print("   B) Debug failing tools before continuing")
    else:
        print("\n❌ Phase 4 failed - Account tools not functional")
        print("📋 Review previous phases for underlying issues")

if __name__ == "__main__":
    asyncio.run(run_tests())
EOF

chmod +x backend/test_defindex_phase4.py
```

**4.5 Run Test**
```bash
cd backend
python test_defindex_phase4.py
```

### Success Criteria
- ✅ Account tools import without errors
- ✅ `_defindex_discover_vaults` returns formatted vault list
- ✅ `_defindex_get_vault_details` returns formatted vault details
- ✅ Both functions accept `user_id` parameter

### Troubleshooting

**Import errors:**
```bash
# Check dependencies exist
python -c "from defindex_soroban import DeFindexSoroban"
python -c "from account_manager import AccountManager"
```

**Function execution errors:**
- Check that Phase 3 Soroban integration is working
- Verify API client from Phase 1 is functional

### Rollback
```bash
rm backend/defindex_account_tools.py
rm backend/test_defindex_phase4.py
```

---

## Phase 5: AI Agent Integration (1 hour)

### Goal
Integrate DeFindex tools into the AI agent's tool factory.

### Prerequisites
- Phase 1-4 completed successfully
- Backend server is stopped (we'll restart it)

### Steps

**5.1 Backup Current Tool Factory**
```bash
# Create backup before modifications
cp backend/agent/tool_factory.py backend/agent/tool_factory.py.backup.$(date +%Y%m%d_%H%M%S)

echo "✅ Backed up tool_factory.py"
ls -lh backend/agent/tool_factory.py.backup.*
```

**5.2 Review DeFindex Integration in Old Version**
```bash
# Extract relevant sections from working commit
git show e89fd86:backend/agent/tool_factory.py | grep -A 100 "defindex_discover" > /tmp/defindex_tool_example.txt

# Review the integration pattern
less /tmp/defindex_tool_example.txt
```

**5.3 Add DeFindex Tools to Tool Factory**

This requires manual editing. Open the file:
```bash
nano backend/agent/tool_factory.py
```

**Add these imports at the top (after existing imports):**
```python
# DeFindex integration
from defindex_account_tools import (
    _defindex_discover_vaults,
    _defindex_get_vault_details,
    _defindex_deposit
)
```

**Add these tool definitions inside `create_tools_for_user()` function:**
```python
    # === DeFindex Yield Farming Tools ===

    @tool
    def defindex_discover_vaults(min_apy: Optional[float] = 0.0):
        """
        Discover DeFindex vaults sorted by APY (highest to lowest).

        Use this when users ask about:
        - Available DeFindex vaults for investment
        - Current APY rates on DeFindex strategies
        - DeFi yield opportunities beyond basic Blend pools
        - Where to deposit funds for maximum yield

        This tool shows vaults with strategy-based yield optimization.

        Args:
            min_apy: Minimum APY threshold as percentage (default 0.0% to show ALL)

        Returns:
            Complete list of available vaults sorted by APY with full details
        """
        import asyncio

        # Handle async function call properly
        try:
            loop = asyncio.get_running_loop()
            import concurrent.futures
            with concurrent.futures.ThreadPoolExecutor() as executor:
                future = executor.submit(
                    asyncio.run,
                    _defindex_discover_vaults(min_apy=min_apy, user_id=user_id)
                )
                return future.result()
        except RuntimeError:
            return asyncio.run(
                _defindex_discover_vaults(min_apy=min_apy, user_id=user_id)
            )

    @tool
    def defindex_get_vault_details(vault_address: str):
        """
        Get detailed information about a specific DeFindex vault.

        Use this when users want more details about a vault they're interested in.

        Args:
            vault_address: The contract address of the vault (56 characters starting with 'C')

        Returns:
            Detailed vault information including strategies, fees, and performance
        """
        import asyncio

        try:
            loop = asyncio.get_running_loop()
            import concurrent.futures
            with concurrent.futures.ThreadPoolExecutor() as executor:
                future = executor.submit(
                    asyncio.run,
                    _defindex_get_vault_details(vault_address=vault_address, user_id=user_id)
                )
                return future.result()
        except RuntimeError:
            return asyncio.run(
                _defindex_get_vault_details(vault_address=vault_address, user_id=user_id)
            )
```

**Add DeFindex tools to the return list (find existing tools list):**
```python
    tools = [
        stellar_account_manager,
        stellar_trading,
        stellar_trustline_manager,
        stellar_market_data,
        stellar_utilities,
        stellar_soroban,
        # Blend Capital tools (existing)
        blend_discover_pools,
        blend_find_best_yield,
        blend_get_pool_apy,
        blend_supply_to_pool,
        blend_withdraw_from_pool,
        blend_check_my_positions,
        # NEW - DeFindex tools
        defindex_discover_vaults,
        defindex_get_vault_details,
    ]
```

**Update the logger count:**
```python
    logger.info(f"Created {len(tools)} tools for user_id: {user_id}")
```

**Save and exit (Ctrl+X, Y, Enter)**

**5.4 Create Phase 5 Test Script**
```bash
cat > backend/test_defindex_phase5.py << 'EOF'
#!/usr/bin/env python3
"""Phase 5: Tool factory integration test"""
import os
import sys
from dotenv import load_dotenv

load_dotenv()

# Import tool factory
try:
    from agent.tool_factory import create_tools_for_user
    print("✅ Tool factory imported successfully")
except ImportError as e:
    print(f"❌ Failed to import tool factory: {e}")
    sys.exit(1)

def test_tool_creation():
    """Test creating tools for a test user"""
    test_user_id = "test_user_phase5"

    try:
        tools = create_tools_for_user(test_user_id)
        print(f"✅ Created {len(tools)} tools for user: {test_user_id}")

        # Find DeFindex tools
        defindex_tools = [t for t in tools if 'defindex' in t.name.lower()]

        print(f"\nDeFindex tools found: {len(defindex_tools)}")
        for tool in defindex_tools:
            print(f"  - {tool.name}")
            print(f"    Description: {tool.description[:100]}...")

        if len(defindex_tools) >= 2:
            print("\n✅ DeFindex tools integrated successfully")
            return True
        else:
            print("\n⚠️  Expected at least 2 DeFindex tools")
            return False

    except Exception as e:
        print(f"❌ Tool creation error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_tool_invocation():
    """Test invoking a DeFindex tool"""
    test_user_id = "test_user_phase5"

    try:
        tools = create_tools_for_user(test_user_id)

        # Find discover tool
        discover_tool = None
        for tool in tools:
            if 'defindex_discover' in tool.name.lower():
                discover_tool = tool
                break

        if not discover_tool:
            print("⚠️  Discover tool not found")
            return False

        print(f"\nInvoking {discover_tool.name}...")
        result = discover_tool.invoke({"min_apy": 0.0})

        print(f"✅ Tool invocation successful")
        print(f"\nResult preview (first 300 chars):")
        print(result[:300])

        # Check result quality
        if "vault" in result.lower() and ("apy" in result.lower() or "error" in result.lower()):
            print("\n✅ Tool returned expected format")
            return True
        else:
            print("\n⚠️  Unexpected result format")
            return False

    except Exception as e:
        print(f"❌ Tool invocation error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("=== Phase 5: AI Agent Integration Test ===\n")

    creation_ok = test_tool_creation()
    print()

    if creation_ok:
        invocation_ok = test_tool_invocation()
    else:
        invocation_ok = False

    print("\n=== Results ===")
    print(f"Tool creation: {'✅ PASS' if creation_ok else '❌ FAIL'}")
    print(f"Tool invocation: {'✅ PASS' if invocation_ok else '❌ FAIL'}")

    if creation_ok and invocation_ok:
        print("\n✅ Phase 5 complete - DeFindex integrated with AI agent")
        print("📋 Next: Proceed to Phase 6 (end-to-end testing)")
    else:
        print("\n❌ Phase 5 failed - Check tool_factory.py integration")
        print("📋 Review backup: backend/agent/tool_factory.py.backup.*")

EOF

chmod +x backend/test_defindex_phase5.py
```

**5.5 Run Test**
```bash
cd backend
python test_defindex_phase5.py
```

### Success Criteria
- ✅ Tool factory imports without errors
- ✅ DeFindex tools are created (at least 2)
- ✅ Tool invocation succeeds and returns formatted data
- ✅ No import or execution errors

### Troubleshooting

**Import errors in tool_factory.py:**
```bash
# Check syntax
python -m py_compile backend/agent/tool_factory.py

# If errors, review the edits
nano backend/agent/tool_factory.py
```

**Tools not found:**
- Verify you added tools to the return list
- Check tool names match the @tool decorator names

**Tool invocation fails:**
- Check that Phase 4 account tools are working
- Verify async handling is correct

### ⏸️ STOP: Phase 5 Decision Point

**Question:** Did Phase 5 tests pass?

**If YES:**
- ✅ Proceed to Phase 6 (end-to-end testing)

**If NO:**
- ❌ Restore backup:
```bash
cp backend/agent/tool_factory.py.backup.* backend/agent/tool_factory.py
```
- Review errors and retry Phase 5

### Rollback
```bash
# Restore backup
latest_backup=$(ls -t backend/agent/tool_factory.py.backup.* | head -1)
cp $latest_backup backend/agent/tool_factory.py
echo "✅ Restored tool_factory.py from backup"

rm backend/test_defindex_phase5.py
```

---

## Phase 6: End-to-End Testing (30 minutes)

### Goal
Test the complete integration with the running AI agent.

### Prerequisites
- Phase 1-5 completed successfully
- Ready to start backend server

### Steps

**6.1 Update System Prompt (Optional)**

Add DeFindex to the AI agent's system knowledge:
```bash
# Edit backend/system_prompt.md
nano backend/system_prompt.md
```

**Add section about DeFindex:**
```markdown
### DeFindex Yield Farming Tools (3 tools)

DeFindex provides strategy-based yield optimization across multiple DeFi protocols:

1. **defindex_discover_vaults**: Find highest APY opportunities across DeFindex strategies
2. **defindex_get_vault_details**: Get detailed information about a specific vault
3. **defindex_deposit**: Supply assets to a vault (autonomous execution, REAL FUNDS)

**Key Differences from Blend:**
- Higher yields through multi-protocol strategies
- Auto-rebalancing across Blend, Soroswap, and others
- Vault abstraction simplifies DeFi interaction
- Strategy-based risk management
```

**6.2 Start Backend Server**
```bash
cd backend
source .venv/bin/activate
python main.py
```

**Wait for server to start. Look for:**
```
INFO:     Uvicorn running on http://0.0.0.0:8000
INFO:     Created XX tools for user...
```

**Check logs for DeFindex tool count:**
- Should see tool count increased by 2 (defindex_discover and defindex_get_vault_details)

**6.3 Test Health Endpoint**

In another terminal:
```bash
curl http://localhost:8000/health | jq
```

**Expected:**
```json
{
  "status": "healthy",
  "tools_available": true,
  "defindex_enabled": true  // <-- Look for this
}
```

**6.4 Create End-to-End Test Script**
```bash
cat > backend/test_defindex_phase6.py << 'EOF'
#!/usr/bin/env python3
"""Phase 6: End-to-end AI agent test"""
import requests
import json

API_URL = "http://localhost:8000"

def test_health():
    """Test health endpoint includes DeFindex"""
    try:
        response = requests.get(f"{API_URL}/health", timeout=5)
        data = response.json()

        print(f"Health status: {data.get('status')}")
        print(f"Tools available: {data.get('tools_available')}")

        # Check for DeFindex indication (may not be in health endpoint)
        return data.get('status') == 'healthy'

    except Exception as e:
        print(f"❌ Health check error: {e}")
        return False

def test_chat_query(message: str, expected_in_response: list):
    """Test AI agent with a chat query"""
    print(f"\n{'='*60}")
    print(f"Query: {message}")
    print(f"{'='*60}")

    try:
        response = requests.post(
            f"{API_URL}/chat",
            json={
                "message": message,
                "history": [],
                "wallet_address": None
            },
            timeout=60  # Allow time for AI processing
        )

        data = response.json()

        if data.get('success'):
            result = data.get('response', '')
            print(f"\nResponse preview (first 500 chars):")
            print(result[:500])

            # Check for expected content
            found_all = all(keyword.lower() in result.lower() for keyword in expected_in_response)

            if found_all:
                print(f"\n✅ Response contains expected keywords: {expected_in_response}")
                return True
            else:
                print(f"\n⚠️  Response missing some keywords: {expected_in_response}")
                return False
        else:
            print(f"❌ Agent error: {data.get('error')}")
            return False

    except Exception as e:
        print(f"❌ Chat query error: {e}")
        return False

if __name__ == "__main__":
    print("=== Phase 6: End-to-End AI Agent Test ===\n")
    print("⚠️  Make sure backend server is running on port 8000\n")

    # Test 1: Health check
    print("Test 1: Health endpoint")
    health_ok = test_health()
    print(f"Result: {'✅ PASS' if health_ok else '❌ FAIL'}\n")

    if not health_ok:
        print("❌ Server not responding. Start backend with: python main.py")
        exit(1)

    # Test 2: DeFindex discovery query
    print("\nTest 2: DeFindex vault discovery")
    discovery_ok = test_chat_query(
        "What DeFindex vaults are available?",
        expected_in_response=["vault", "apy"]
    )
    print(f"Result: {'✅ PASS' if discovery_ok else '❌ FAIL'}")

    # Test 3: Comparison query (DeFindex vs Blend)
    print("\nTest 3: Yield comparison query")
    comparison_ok = test_chat_query(
        "Compare DeFindex vaults to Blend pools for USDC yield",
        expected_in_response=["usdc", "yield"]
    )
    print(f"Result: {'✅ PASS' if comparison_ok else '❌ FAIL'}")

    print("\n" + "="*60)
    print("=== Phase 6 Results ===")
    print(f"Health check: {'✅ PASS' if health_ok else '❌ FAIL'}")
    print(f"Discovery query: {'✅ PASS' if discovery_ok else '❌ FAIL'}")
    print(f"Comparison query: {'✅ PASS' if comparison_ok else '❌ FAIL'}")

    if discovery_ok:
        print("\n✅ Phase 6 complete - DeFindex fully integrated!")
        print("\n📋 Next steps:")
        print("   1. Update CLAUDE.md documentation")
        print("   2. Test with frontend UI")
        print("   3. Document any limitations found")
        print("   4. Commit changes to git")
    else:
        print("\n⚠️  Phase 6 incomplete - AI agent not using DeFindex tools")
        print("\n📋 Troubleshooting:")
        print("   - Check backend logs for tool loading errors")
        print("   - Verify system_prompt.md includes DeFindex guidance")
        print("   - Test tools directly with test_defindex_phase5.py")
EOF

chmod +x backend/test_defindex_phase6.py
```

**6.5 Run Test (with server running)**

In a separate terminal:
```bash
cd backend
python test_defindex_phase6.py
```

### Success Criteria
- ✅ Health endpoint responds
- ✅ AI agent successfully queries DeFindex vaults
- ✅ Agent provides meaningful yield comparison
- ✅ No tool execution errors in backend logs

### ⏸️ STOP: Phase 6 Decision Point

**Question:** Did end-to-end tests pass?

**If YES:**
- ✅ DeFindex restoration is COMPLETE!
- Proceed to Phase 7 (documentation and finalization)

**If PARTIAL (some queries work):**
- ⚠️ Document which queries work and which don't
- May proceed to Phase 7 with known limitations

**If NO:**
- ❌ Review backend logs for errors
- Check that AI agent is actually using DeFindex tools (not just Blend)
- May need to adjust system prompt to guide tool selection

### Troubleshooting

**Agent not using DeFindex tools:**
- Check system_prompt.md includes DeFindex
- Verify tools are loaded (check startup logs)
- Try more explicit queries: "Use DeFindex to show vaults"

**Tool execution errors:**
- Check Phase 4-5 tests still pass
- Review backend logs for detailed error messages

**Timeout errors:**
- Increase timeout in test script
- Check network connectivity to DeFindex API

---

## Phase 7: Documentation & Finalization (30 minutes)

### Goal
Document the restored functionality and commit changes.

### Steps

**7.1 Update CLAUDE.md**
```bash
# Edit main documentation
nano CLAUDE.md
```

**Add DeFindex section after Blend Capital section:**
```markdown
### DeFindex Yield Farming Tools (3 tools) - MAINNET:

1. **defindex_discover_vaults**: Find highest APY opportunities across DeFindex strategies
2. **defindex_get_vault_details**: Get detailed information about a specific vault including strategies and fees
3. **defindex_deposit**: Supply assets to vault (autonomous execution, real funds) [Optional if implemented]

**Key Features:**
- Strategy-based yield optimization across multiple DeFi protocols
- Auto-rebalancing between Blend, Soroswap, and other integrations
- Typically offers higher yields than direct Blend pool interaction
- Vault abstraction simplifies complex DeFi strategies

**Comparison to Blend:**
- Blend: Direct pool interaction, ~5-15% APY, simpler, more control
- DeFindex: Strategy-managed, potentially higher APY, automated, less control
```

**7.2 Create Summary Document**
```bash
cat > DEFINDEX_RESTORATION_SUMMARY.md << 'EOF'
# DeFindex Restoration Summary

**Date Restored:** $(date +%Y-%m-%d)
**Restored By:** Coding Agent + Human Oversight
**Restoration Method:** Incremental & Iterative (Approach C)

## What Was Restored

### Core Files (from commit e89fd86)
1. `backend/defindex_client.py` - DeFindex API client with Bearer auth
2. `backend/defindex_soroban.py` - Soroban contract integration
3. `backend/defindex_account_tools.py` - LangChain tool wrappers
4. `backend/agent/tool_factory.py` - Added 2-3 DeFindex tools

### Configuration Added
- `DEFINDEX_API_KEY` - API authentication
- `DEFINDEX_BASE_URL` - https://api.defindex.io
- Updated vault addresses (if needed)

## Phase Results

- ✅ Phase 0: API Verification - [PASS/FAIL]
- ✅ Phase 1: API Client - [PASS/FAIL]
- ✅ Phase 2: Vault Queries - [PASS/FAIL]
- ✅ Phase 3: Soroban Integration - [PASS/FAIL]
- ✅ Phase 4: Account Tools - [PASS/FAIL]
- ✅ Phase 5: AI Agent Integration - [PASS/FAIL]
- ✅ Phase 6: End-to-End Testing - [PASS/FAIL]

## Known Limitations

[Document any issues found during testing]
- Example: Some vault addresses may return "MissingValue" errors
- Example: API rate limiting may affect rapid queries

## Testing Performed

### Automated Tests
- Phase 0-6 test scripts executed
- All test scripts available in `backend/test_defindex_phase*.py`

### Manual Tests
- [List any manual testing done via frontend or direct API calls]

## Future Work

- [ ] Add deposit functionality (if not included)
- [ ] Add withdrawal functionality
- [ ] Update frontend to show DeFindex vaults
- [ ] Monitor API stability over time
- [ ] Update vault addresses as new strategies deploy

## Rollback Instructions

If DeFindex needs to be disabled:

```bash
# Remove restored files
rm backend/defindex_client.py
rm backend/defindex_soroban.py
rm backend/defindex_account_tools.py

# Restore tool_factory.py from backup
cp backend/agent/tool_factory.py.backup.* backend/agent/tool_factory.py

# Remove env vars
sed -i '/DEFINDEX/d' backend/.env

# Restart backend
cd backend && python main.py
```

## Contact Information

**DeFindex Team:**
- Website: https://defindex.io
- Docs: https://docs.defindex.io
- GitHub: https://github.com/paltalabs/defindex
- Support: team@paltalabs.io

**API Issues:**
- Report at GitHub or contact PaltaLabs team directly
- Include error messages and vault addresses

EOF
```

**7.3 Clean Up Test Files (Optional)**
```bash
# Decide whether to keep or remove phase test files
# Recommend keeping for future debugging

# Option A: Keep all test files
echo "✅ Keeping test files for future reference"

# Option B: Move to tests directory
mkdir -p backend/tests/defindex_restoration
mv backend/test_defindex_phase*.py backend/tests/defindex_restoration/
echo "✅ Moved test files to tests/defindex_restoration/"

# Option C: Remove test files
# rm backend/test_defindex_phase*.py
```

**7.4 Git Commit**

⏸️ **STOP: Review before committing**

Review all changes:
```bash
git status
git diff backend/
```

**If everything looks good:**
```bash
# Stage restored files
git add backend/defindex_client.py
git add backend/defindex_soroban.py
git add backend/defindex_account_tools.py
git add backend/agent/tool_factory.py
git add backend/.env.example
git add CLAUDE.md
git add DEFINDEX_RESTORATION_SUMMARY.md
git add DEFINDEX_RESTORATION_GUIDE.md

# Create commit
git commit -m "Restore DeFindex integration - Strategy-based yield farming

- Restore DeFindex API client with Bearer auth
- Restore Soroban contract integration for vault queries
- Restore account tools with user isolation
- Integrate 2 DeFindex tools into AI agent (discover, details)
- Add configuration for DEFINDEX_API_KEY
- Update documentation with DeFindex capabilities

DeFindex provides higher yields through multi-protocol strategies vs direct Blend pools.
Tested incrementally through Phase 0-6 verification.

Refs: Previous integration at e89fd86, removed at fadb7b7"

# Push to remote
git push -u origin claude/review-defindex-api-011CUyq5z6KQGMgdMP7VU7Eq
```

### Success Criteria
- ✅ All documentation updated
- ✅ Test files organized
- ✅ Changes committed to git
- ✅ Summary document captures results

---

## Phase 8: Frontend Integration (Optional, 1 hour)

### Goal
Add DeFindex vaults to the frontend dashboard (optional enhancement).

### Prerequisites
- Phase 1-7 completed
- Frontend development environment set up

### Steps

**8.1 Create DeFindex Contract Definitions**
```bash
# Create or update contract file
cat > src/contracts/defindex.ts << 'EOF'
/**
 * DeFindex Mainnet Vault Addresses
 * Updated: [DATE]
 * Source: api.defindex.io
 */

export const DEFINDEX_VAULTS = {
  USDC_Blend_Fixed: 'CDB2WMKQQNVZMEBY7Q7GZ5C7E7IAFSNMZ7GGVD6WKTCEWK7XOIAVZSAP',
  USDC_Blend_Yieldblox: 'CCSRX5E4337QMCMC3KO3RDFYI57T5NZV5XB3W3TWE4USCASKGL5URKJL',
  EURC_Blend_Fixed: 'CC5CE6MWISDXT3MLNQ7R3FVILFVFEIH3COWGH45GJKL6BD2ZHF7F7JVI',
  EURC_Blend_Yieldblox: 'CA33NXYN7H3EBDSA3U2FPSULGJTTL3FQRHD2ADAAPTKS3FUJOE73735A',
  // Add more as discovered
} as const;

export type VaultName = keyof typeof DEFINDEX_VAULTS;
EOF
```

**8.2 Add DeFindex Section to Dashboard (Optional)**

This requires React/TypeScript knowledge. Basic approach:
1. Add new tab or section to `src/components/dashboard/PoolsDashboard.tsx`
2. Fetch DeFindex vault data via chat API
3. Display alongside Blend pools with yield comparison

**Simplified approach:**
- Just use the chat interface for DeFindex queries
- No dedicated dashboard needed initially

### Decision Point

**Question:** Add frontend dashboard for DeFindex?

**Option A - Yes:**
- Continue with Phase 8 implementation
- Create dedicated DeFindex view in dashboard

**Option B - No (Recommended):**
- Use chat interface for DeFindex interactions
- Dashboard enhancement can be added later
- Skip to completion

---

## Completion Checklist

### Restored Files
- [ ] `backend/defindex_client.py`
- [ ] `backend/defindex_soroban.py`
- [ ] `backend/defindex_account_tools.py`
- [ ] `backend/agent/tool_factory.py` (modified)

### Configuration
- [ ] `DEFINDEX_API_KEY` in `backend/.env`
- [ ] `DEFINDEX_BASE_URL` in `backend/.env`
- [ ] API key obtained from PaltaLabs team
- [ ] Vault addresses verified

### Testing
- [ ] Phase 0: API verification - PASS
- [ ] Phase 1: API client - PASS
- [ ] Phase 2: Vault queries - PASS
- [ ] Phase 3: Soroban integration - PASS
- [ ] Phase 4: Account tools - PASS
- [ ] Phase 5: AI agent integration - PASS
- [ ] Phase 6: End-to-end testing - PASS

### Documentation
- [ ] `CLAUDE.md` updated with DeFindex section
- [ ] `DEFINDEX_RESTORATION_SUMMARY.md` created
- [ ] `DEFINDEX_RESTORATION_GUIDE.md` (this file) saved
- [ ] Known limitations documented

### Git
- [ ] All changes committed
- [ ] Pushed to feature branch
- [ ] Commit message describes restoration

### Operational
- [ ] Backend server runs without errors
- [ ] AI agent responds to DeFindex queries
- [ ] No regression in existing Blend functionality

---

## Quick Reference Commands

### Start Backend Server
```bash
cd backend
source .venv/bin/activate
python main.py
```

### Run All Phase Tests
```bash
cd backend
for i in {0..6}; do
  echo "=== Running Phase $i ==="
  python test_defindex_phase${i}.py
  echo ""
done
```

### Check Backend Logs
```bash
# Follow logs in real-time
tail -f backend/logs/app.log  # If logging to file

# Or watch uvicorn output in terminal
```

### Test API Directly
```bash
# Health check
curl https://api.defindex.io/health

# Chat query
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "What DeFindex vaults are available?", "history": []}'
```

### Rollback Everything
```bash
# Remove all restored files
rm backend/defindex_*.py
rm backend/test_defindex_*.py

# Restore tool_factory.py
cp backend/agent/tool_factory.py.backup.* backend/agent/tool_factory.py

# Remove env vars
sed -i '/DEFINDEX/d' backend/.env

# Restart backend
cd backend && python main.py
```

---

## Troubleshooting Guide

### API Connection Issues

**Symptom:** `test_connection()` returns False

**Fixes:**
1. Check internet connectivity: `ping api.defindex.io`
2. Verify API key format: `echo $DEFINDEX_API_KEY` (should start with `sk_`)
3. Test with curl: `curl -H "Authorization: Bearer $DEFINDEX_API_KEY" https://api.defindex.io/health`
4. Contact PaltaLabs if API is down

### Import Errors

**Symptom:** `ImportError: cannot import name 'DeFindexClient'`

**Fixes:**
1. Check file exists: `ls backend/defindex_client.py`
2. Check syntax: `python -m py_compile backend/defindex_client.py`
3. Check Python path: `echo $PYTHONPATH`
4. Try direct import: `cd backend && python -c "from defindex_client import DeFindexClient"`

### Vault Query Failures

**Symptom:** "MissingValue" or "trying to get non-existing value"

**Meaning:** Vault contract not initialized on-chain

**Fixes:**
1. Try different vault addresses from PaltaLabs docs
2. Verify network (mainnet vs testnet)
3. Contact PaltaLabs for initialized vault list
4. Document as known limitation and proceed

### AI Agent Not Using Tools

**Symptom:** Agent responds but doesn't use DeFindex tools

**Fixes:**
1. Check tools loaded: Review backend startup logs
2. Update system prompt: Add explicit DeFindex guidance
3. Use explicit queries: "Use DeFindex to find vaults"
4. Check tool descriptions: May need to improve tool docstrings

### Rate Limiting (429 errors)

**Symptom:** "Too Many Requests" from API

**Fixes:**
1. Add delays between API calls
2. Check retry logic in `defindex_client.py`
3. Contact PaltaLabs for rate limit increase
4. Implement caching for frequently queried data

---

## Support Contacts

### DeFindex/PaltaLabs
- Email: team@paltalabs.io
- GitHub: https://github.com/paltalabs/defindex/issues
- Docs: https://docs.defindex.io

### Stellar Community
- Discord: https://discord.gg/stellar
- Stack Exchange: https://stellar.stackexchange.com

---

## Appendix: File Manifest

### Restored Files (from git commit e89fd86)
```
backend/defindex_client.py         - API client (~300 lines)
backend/defindex_soroban.py        - Soroban integration (~500 lines)
backend/defindex_account_tools.py  - LangChain tools (~400 lines)
```

### Modified Files
```
backend/agent/tool_factory.py      - Added DeFindex tools (~50 lines added)
backend/.env                       - Added 2 env vars
CLAUDE.md                          - Added DeFindex section
```

### New Files (created during restoration)
```
DEFINDEX_RESTORATION_GUIDE.md      - This file
DEFINDEX_RESTORATION_SUMMARY.md    - Results summary
backend/test_defindex_phase0.py    - Phase 0 test
backend/test_defindex_phase1.py    - Phase 1 test
backend/test_defindex_phase2.py    - Phase 2 test
backend/test_defindex_phase3.py    - Phase 3 test
backend/test_defindex_phase4.py    - Phase 4 test
backend/test_defindex_phase5.py    - Phase 5 test
backend/test_defindex_phase6.py    - Phase 6 test
backend/.env.example               - Updated with DeFindex vars
src/contracts/defindex.ts          - Optional frontend addresses
```

---

**End of Guide**

This guide is designed to be passed to a coding agent for automated execution with user input at configuration checkpoints. Each phase is self-contained with clear success criteria and rollback instructions.

Good luck with the restoration! 🚀
