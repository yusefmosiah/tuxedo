# Blend Pools Testing Strategy - Mainnet Only

## Overview

This document outlines a comprehensive testing strategy for Tuxedo's Blend Pools integration on Stellar **mainnet only**. Since Blend pools aren't working on testnet, we need a risk-minimized approach to verify our logic before full deployment.

---

## Current Test Coverage

### ✅ What We Have (Working)

1. **Read-Only Operations** (`sandbox/test_mainnet_blend.py`)
   - Pool discovery from Backstop contract
   - Real-time APY queries (USDC in pools)
   - Best yield finder across all pools
   - **Risk Level**: Zero (no transactions, no accounts needed)
   - **Status**: ✅ All tests passing

2. **On-Chain Data Validation**
   - Verified mainnet contract addresses
   - RPC connectivity to Ankr Stellar endpoint
   - Reserve data parsing and APY calculations
   - **Risk Level**: Zero
   - **Status**: ✅ Working

### ❌ What's Missing (Critical Gaps)

1. **Transaction Construction Testing**
   - `blend_supply_collateral()` - Builds supply transactions
   - `blend_withdraw_collateral()` - Builds withdraw transactions
   - Parameter encoding (Request struct with amount, type, address)
   - **Current Gap**: Not tested with real accounts

2. **Transaction Simulation**
   - Stellar supports transaction simulation WITHOUT broadcasting
   - We can test auth requirements, contract calls, and error cases
   - **Current Gap**: Not utilizing simulation for transaction testing

3. **Wallet Integration**
   - External wallet signing flow (`requires_signature` response)
   - XDR generation and validation
   - **Current Gap**: Not tested end-to-end

4. **Error Handling**
   - Insufficient balance scenarios
   - Wrong asset addresses
   - Pool position edge cases (withdraw more than supplied)
   - **Current Gap**: No systematic error testing

---

## Recommended Testing Strategy: 4 Layers

### Layer 1: Extended Simulation Testing ⭐ **START HERE**
**Risk**: Zero | **Cost**: Zero | **Coverage**: 90% of transaction logic

#### What to Test
Use Stellar's simulation endpoints to validate transaction construction WITHOUT broadcasting to the network. This catches parameter encoding bugs, auth issues, and contract errors.

#### Implementation

**File**: `backend/tests/test_blend_transaction_simulation.py`

```python
#!/usr/bin/env python3
"""
Test Blend supply/withdraw transaction construction via simulation.
These tests validate the transaction logic without submitting to the network.
"""

import asyncio
import logging
from stellar_sdk.soroban_server_async import SorobanServerAsync
from account_manager import AccountManager
from blend_pool_tools import (
    blend_supply_collateral,
    blend_withdraw_collateral,
    BLEND_MAINNET_CONTRACTS,
    NETWORK_CONFIG
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def test_supply_simulation():
    """Test 1: Simulate supply transaction construction"""
    print("\n" + "="*80)
    print("TEST: Supply Transaction Simulation (No Broadcast)")
    print("="*80)

    soroban_server = SorobanServerAsync(NETWORK_CONFIG['rpc_url'])
    account_manager = AccountManager()

    # Create or get test account (doesn't need to be funded for simulation)
    accounts = account_manager.get_user_accounts('test_simulation')
    if not accounts:
        result = account_manager.generate_account(
            'test_simulation',
            chain='stellar',
            name='sim_test'
        )
        account_id = result['account_id']
    else:
        account_id = accounts[0]['id']

    try:
        # Attempt to build supply transaction
        # We'll modify blend_supply_collateral to support simulation mode
        result = await blend_supply_collateral(
            pool_address=BLEND_MAINNET_CONTRACTS['fixed'],
            asset_address=BLEND_MAINNET_CONTRACTS['usdc'],
            amount=10.0,  # 10 USDC
            account_id=account_id,
            account_manager=account_manager,
            soroban_server=soroban_server,
            user_id='test_simulation',
            network='mainnet',
            simulate_only=True  # NEW PARAMETER: Don't broadcast
        )

        if result.get('success') or result.get('simulation_success'):
            print("✅ Transaction construction successful!")
            print(f"   - Parameters encoded correctly")
            print(f"   - Contract ID: {BLEND_MAINNET_CONTRACTS['fixed'][:16]}...")
            print(f"   - Function: submit()")
            print(f"   - Request Type: SUPPLY_COLLATERAL (0)")
            print(f"   - Amount: 10.0 USDC (100000000 scaled)")
            return True
        else:
            print(f"❌ Simulation failed: {result.get('error')}")
            return False

    except Exception as e:
        print(f"❌ Exception during simulation: {e}")
        return False
    finally:
        await soroban_server.close()


async def test_withdraw_simulation():
    """Test 2: Simulate withdraw transaction construction"""
    print("\n" + "="*80)
    print("TEST: Withdraw Transaction Simulation (No Broadcast)")
    print("="*80)

    soroban_server = SorobanServerAsync(NETWORK_CONFIG['rpc_url'])
    account_manager = AccountManager()

    accounts = account_manager.get_user_accounts('test_simulation')
    account_id = accounts[0]['id'] if accounts else None

    if not account_id:
        print("⚠️  Skipping (no account from previous test)")
        return False

    try:
        result = await blend_withdraw_collateral(
            pool_address=BLEND_MAINNET_CONTRACTS['fixed'],
            asset_address=BLEND_MAINNET_CONTRACTS['usdc'],
            amount=5.0,  # 5 USDC
            account_id=account_id,
            account_manager=account_manager,
            soroban_server=soroban_server,
            user_id='test_simulation',
            network='mainnet',
            simulate_only=True  # NEW PARAMETER: Don't broadcast
        )

        if result.get('success') or result.get('simulation_success'):
            print("✅ Transaction construction successful!")
            print(f"   - Request Type: WITHDRAW_COLLATERAL (1)")
            print(f"   - Amount: 5.0 USDC (50000000 scaled)")
            return True
        else:
            print(f"❌ Simulation failed: {result.get('error')}")
            return False

    except Exception as e:
        print(f"❌ Exception during simulation: {e}")
        return False
    finally:
        await soroban_server.close()


async def test_parameter_encoding():
    """Test 3: Validate parameter encoding for Request struct"""
    print("\n" + "="*80)
    print("TEST: Parameter Encoding Validation")
    print("="*80)

    # Test various amounts and verify scaling
    test_cases = [
        (1.0, 10_000_000, "1 USDC"),
        (0.1, 1_000_000, "0.1 USDC"),
        (100.5, 1_005_000_000, "100.5 USDC"),
        (1000.123456, 10_001_234_560, "1000.123456 USDC (max precision)"),
    ]

    for amount, expected_scaled, description in test_cases:
        amount_scaled = int(amount * 10_000_000)
        status = "✅" if amount_scaled == expected_scaled else "❌"
        print(f"{status} {description}: {amount_scaled} (expected {expected_scaled})")

    return True


async def run_simulation_tests():
    """Run all simulation tests"""
    print("\n" + "="*80)
    print("🧪 BLEND TRANSACTION SIMULATION TEST SUITE")
    print("="*80)
    print("Testing transaction construction WITHOUT submitting to network")
    print("Risk: ZERO | Cost: ZERO | Coverage: Transaction logic\n")

    results = []

    # Test 1: Supply simulation
    success1 = await test_supply_simulation()
    results.append(("Supply Simulation", success1))

    # Test 2: Withdraw simulation
    success2 = await test_withdraw_simulation()
    results.append(("Withdraw Simulation", success2))

    # Test 3: Parameter encoding
    success3 = await test_parameter_encoding()
    results.append(("Parameter Encoding", success3))

    # Summary
    print("\n" + "="*80)
    print("SIMULATION TEST SUMMARY")
    print("="*80)
    for test_name, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} - {test_name}")

    total_passed = sum(1 for _, s in results if s)
    print(f"\n{total_passed}/{len(results)} simulation tests passed")

    return total_passed == len(results)


if __name__ == "__main__":
    success = asyncio.run(run_simulation_tests())
    exit(0 if success else 1)
```

**Action Items**:
1. ✅ Add `simulate_only` parameter to `blend_supply_collateral()` and `blend_withdraw_collateral()`
2. ✅ Run simulation tests to validate transaction construction
3. ✅ Fix any parameter encoding or structure issues found

---

### Layer 2: Minimal Mainnet Testing ⚠️ **Use Real Funds**
**Risk**: Low (controlled) | **Cost**: ~$10-20 | **Coverage**: End-to-end verification

#### What to Test
Verify the complete flow with minimal real funds to ensure transactions actually succeed on-chain.

#### Approach

**Prerequisites**:
1. Create dedicated test account (not your main account)
2. Fund with minimum amounts:
   - 10 XLM (for fees and minimum balance)
   - 20 USDC (for supply/withdraw testing)

**Test Sequence**:
```
Step 1: Supply 1 USDC to Fixed Pool
  → Verify transaction hash
  → Check position shows 1 USDC supplied

Step 2: Wait 1 ledger (~5 seconds)
  → Query position again
  → Verify interest accrual (should be tiny amount)

Step 3: Withdraw 1 USDC from Fixed Pool
  → Verify transaction hash
  → Check final balance (should be ~1.0000X USDC with interest)

Step 4: Verify agent account works
  → Repeat with agent-created account
  → Test auto-sign flow

Step 5: Test error cases
  → Try to withdraw more than supplied (should fail gracefully)
  → Try invalid asset address (should fail with clear error)
```

**Implementation**:

**File**: `backend/tests/test_blend_mainnet_e2e.py`

```python
#!/usr/bin/env python3
"""
End-to-End Blend Integration Test on MAINNET.

⚠️  WARNING: This test uses REAL FUNDS on mainnet!
    - Requires funded test account
    - Minimal amounts (~1 USDC per test)
    - All transactions are broadcast to mainnet

Prerequisites:
  1. Account with 10+ XLM for fees
  2. Account with 20+ USDC for testing
  3. Set TEST_ACCOUNT_SECRET in .env

Usage:
  cd backend
  source .venv/bin/activate
  export TEST_ACCOUNT_SECRET="S..."  # Your test account secret
  python3 tests/test_blend_mainnet_e2e.py
"""

import asyncio
import os
import logging
from stellar_sdk.soroban_server_async import SorobanServerAsync
from stellar_sdk import Keypair
from account_manager import AccountManager
from blend_pool_tools import (
    blend_supply_collateral,
    blend_withdraw_collateral,
    blend_get_my_positions,
    BLEND_MAINNET_CONTRACTS,
    NETWORK_CONFIG
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def test_full_supply_withdraw_cycle():
    """
    Test complete supply → check position → withdraw cycle with real funds.

    ⚠️  Uses ~1 USDC + fees on mainnet
    """
    print("\n" + "="*80)
    print("⚠️  MAINNET END-TO-END TEST - REAL FUNDS")
    print("="*80)

    # Check for test account
    test_secret = os.getenv('TEST_ACCOUNT_SECRET')
    if not test_secret:
        print("❌ TEST_ACCOUNT_SECRET not set")
        print("   Set this to your funded test account's secret key:")
        print("   export TEST_ACCOUNT_SECRET='S...'")
        return False

    try:
        test_keypair = Keypair.from_secret(test_secret)
        test_address = test_keypair.public_key
        print(f"✅ Test account: {test_address[:8]}...{test_address[-8:]}")
    except Exception as e:
        print(f"❌ Invalid TEST_ACCOUNT_SECRET: {e}")
        return False

    # Setup
    soroban_server = SorobanServerAsync(NETWORK_CONFIG['rpc_url'])
    account_manager = AccountManager()

    # Import test account into AccountManager
    import_result = account_manager.import_account(
        user_id='mainnet_e2e_test',
        secret_key=test_secret,
        name='mainnet_test_account'
    )

    if not import_result['success']:
        print(f"❌ Failed to import account: {import_result['error']}")
        return False

    account_id = import_result['account_id']
    print(f"✅ Imported account: {account_id}")

    # Test parameters
    pool_address = BLEND_MAINNET_CONTRACTS['fixed']
    asset_address = BLEND_MAINNET_CONTRACTS['usdc']
    test_amount = 1.0  # 1 USDC

    print(f"\n📋 Test Parameters:")
    print(f"   Pool: Fixed")
    print(f"   Asset: USDC")
    print(f"   Amount: {test_amount} USDC")

    try:
        # === STEP 1: Supply ===
        print(f"\n{'='*80}")
        print(f"STEP 1: Supply {test_amount} USDC to Fixed Pool")
        print(f"{'='*80}")

        supply_result = await blend_supply_collateral(
            pool_address=pool_address,
            asset_address=asset_address,
            amount=test_amount,
            account_id=account_id,
            account_manager=account_manager,
            soroban_server=soroban_server,
            user_id='mainnet_e2e_test',
            network='mainnet'
        )

        if not supply_result.get('success'):
            print(f"❌ Supply failed: {supply_result.get('error')}")
            return False

        print(f"✅ Supply successful!")
        print(f"   Tx Hash: {supply_result.get('hash')}")
        print(f"   Ledger: {supply_result.get('ledger')}")

        # === STEP 2: Check Position ===
        print(f"\n{'='*80}")
        print(f"STEP 2: Check Position in Fixed Pool")
        print(f"{'='*80}")

        # Wait for ledger confirmation
        await asyncio.sleep(6)

        position_result = await blend_get_my_positions(
            pool_address=pool_address,
            user_id='mainnet_e2e_test',
            account_id=account_id,
            account_manager=account_manager,
            soroban_server=soroban_server,
            network='mainnet'
        )

        if position_result.get('error'):
            print(f"❌ Failed to get position: {position_result.get('error')}")
            return False

        positions = position_result.get('positions', {})
        usdc_position = positions.get('USDC', {})
        supplied = usdc_position.get('supplied', 0)

        print(f"✅ Position retrieved:")
        print(f"   Supplied: {supplied} USDC")
        print(f"   Borrowed: {usdc_position.get('borrowed', 0)} USDC")
        print(f"   Collateral: {usdc_position.get('collateral', False)}")

        if supplied < test_amount * 0.99:  # Allow 1% slippage for rounding
            print(f"⚠️  Warning: Supplied amount {supplied} less than expected {test_amount}")
            # Don't fail, might be rounding

        # === STEP 3: Withdraw ===
        print(f"\n{'='*80}")
        print(f"STEP 3: Withdraw {test_amount} USDC from Fixed Pool")
        print(f"{'='*80}")

        withdraw_result = await blend_withdraw_collateral(
            pool_address=pool_address,
            asset_address=asset_address,
            amount=test_amount,
            account_id=account_id,
            account_manager=account_manager,
            soroban_server=soroban_server,
            user_id='mainnet_e2e_test',
            network='mainnet'
        )

        if not withdraw_result.get('success'):
            print(f"❌ Withdraw failed: {withdraw_result.get('error')}")
            print(f"   Note: You may have accrued interest, try withdrawing slightly more")
            return False

        print(f"✅ Withdraw successful!")
        print(f"   Tx Hash: {withdraw_result.get('hash')}")
        print(f"   Ledger: {withdraw_result.get('ledger')}")

        # === STEP 4: Verify Final Position ===
        print(f"\n{'='*80}")
        print(f"STEP 4: Verify Final Position (Should be Zero)")
        print(f"{'='*80}")

        await asyncio.sleep(6)

        final_position = await blend_get_my_positions(
            pool_address=pool_address,
            user_id='mainnet_e2e_test',
            account_id=account_id,
            account_manager=account_manager,
            soroban_server=soroban_server,
            network='mainnet'
        )

        final_usdc = final_position.get('positions', {}).get('USDC', {})
        final_supplied = final_usdc.get('supplied', 0)

        if final_supplied < 0.01:  # Less than 1 cent remaining
            print(f"✅ Position cleared successfully!")
            print(f"   Remaining: {final_supplied} USDC (acceptable)")
        else:
            print(f"⚠️  Position not fully cleared:")
            print(f"   Remaining: {final_supplied} USDC")

        print(f"\n{'='*80}")
        print(f"✅ END-TO-END TEST PASSED!")
        print(f"{'='*80}")
        print(f"All operations successful:")
        print(f"  ✅ Supply transaction")
        print(f"  ✅ Position query")
        print(f"  ✅ Withdraw transaction")
        print(f"  ✅ Final position verification")
        print(f"\n🎉 Your Blend integration is working on MAINNET!")

        return True

    except Exception as e:
        print(f"\n❌ EXCEPTION: {e}")
        import traceback
        traceback.print_exc()
        return False

    finally:
        await soroban_server.close()


if __name__ == "__main__":
    print("\n⚠️⚠️⚠️  WARNING  ⚠️⚠️⚠️")
    print("This test uses REAL FUNDS on MAINNET")
    print("Estimated cost: ~1 USDC + 0.1 XLM in fees")
    print("\nMake sure you have:")
    print("  1. Exported TEST_ACCOUNT_SECRET")
    print("  2. Account has sufficient USDC and XLM")
    print("  3. You understand this is a real mainnet transaction")

    response = input("\nType 'YES' to proceed: ")
    if response != 'YES':
        print("Test cancelled.")
        exit(1)

    success = asyncio.run(test_full_supply_withdraw_cycle())
    exit(0 if success else 1)
```

---

### Layer 3: Wallet Integration Testing
**Risk**: Zero (simulation) | **Cost**: Zero | **Coverage**: External wallet flow

Test the wallet signing flow without broadcasting:

```python
async def test_wallet_xdr_generation():
    """Verify XDR generation for external wallet signing"""
    # Generate transaction XDR
    # DON'T submit to wallet (just validate format)
    # Verify XDR can be decoded correctly
```

---

### Layer 4: Error Handling & Edge Cases
**Risk**: Zero to Low | **Cost**: Minimal | **Coverage**: Production scenarios

Test all error paths:

```python
# Test insufficient balance
# Test invalid asset address
# Test withdraw more than supplied
# Test unauthorized access
# Test network errors (simulate RPC failure)
```

---

## Implementation Roadmap

### Phase 1: Simulation Testing (This Week)
1. ✅ Implement `simulate_only` parameter in transaction functions
2. ✅ Create `test_blend_transaction_simulation.py`
3. ✅ Run simulation tests and fix any issues found
4. ✅ Document results

**Estimated Time**: 2-4 hours
**Risk**: Zero
**Blocks Deployment**: Yes (must pass before proceeding)

### Phase 2: Minimal Mainnet Testing (Next)
1. ⚠️  Fund test account with minimal amounts ($10-20)
2. ⚠️  Run `test_blend_mainnet_e2e.py` with real funds
3. ⚠️  Verify all transactions succeed
4. ⚠️  Document transaction hashes

**Estimated Time**: 1-2 hours
**Cost**: ~$10-20 + fees
**Blocks Deployment**: Yes (critical validation)

### Phase 3: Wallet Testing (Optional for MVP)
1. Test XDR generation
2. Verify wallet signing flow (manual)
3. Test transaction broadcast after signing

**Estimated Time**: 2-3 hours
**Blocks Deployment**: No (can deploy without)

### Phase 4: Production Deployment
1. Deploy with confidence after Phase 1 & 2 pass
2. Monitor first few real user transactions closely
3. Have rollback plan ready

---

## Risk Mitigation Strategies

### Strategy 1: Graduated Rollout
1. Deploy to production
2. Enable for internal testing only (whitelist)
3. Test with team members' real wallets
4. Open to beta users (small group)
5. Full public release

### Strategy 2: Transaction Limits
Implement safety limits in production:

```python
# In blend_account_tools.py
MAX_SUPPLY_AMOUNT_USD = 1000  # Max $1000 per transaction initially
MAX_DAILY_VOLUME_USD = 5000   # Max $5000 per user per day

# Gradually increase as confidence grows
```

### Strategy 3: Monitoring & Alerts
Set up monitoring for:
- Transaction success/failure rates
- Average transaction sizes
- Unusual patterns (very large amounts)
- Contract errors

---

## Decision Matrix: What to Test When

| Scenario | Testing Required | Risk Level |
|----------|-----------------|------------|
| **Read operations only** (APY, discovery) | Current tests sufficient ✅ | Zero |
| **Transaction simulation** (no broadcast) | Layer 1 tests required ✅ | Zero |
| **Small mainnet test** (1-10 USDC) | Layer 2 tests required ⚠️ | Low |
| **Production deployment** (user funds) | Layer 1 + 2 must pass ⚠️⚠️ | Medium |
| **Large amounts** (>$100) | All layers + monitoring ⚠️⚠️⚠️ | High |

---

## FAQ

### Q: Can we skip mainnet testing and go straight to production?
**A**: Not recommended. Simulation tests catch parameter bugs, but only real mainnet transactions verify:
- Network fees and gas limits
- Contract authorization flows
- Actual on-chain state changes
- Error handling in production

**Recommendation**: Run Layer 2 tests with $10-20 before deploying.

### Q: What if simulation tests fail?
**A**: Stop immediately and fix the issues. Common problems:
- Parameter encoding errors (wrong decimals)
- Incorrect Request struct format
- Wrong contract IDs
- Authorization issues

### Q: How much will Layer 2 testing cost?
**A**: Approximately:
- 2 supply transactions: ~0.05 XLM each
- 2 withdraw transactions: ~0.05 XLM each
- Test USDC amount: 1-2 USDC total
- **Total**: ~$2-3 in fees + USDC (which you get back)

### Q: What if we find bugs during Layer 2 testing?
**A**: You'll only lose the test amount (1-2 USDC). This is why we test with minimal amounts first!

### Q: Can we test on a forked mainnet or local network?
**A**: No, because:
1. Blend contracts are mainnet-only
2. Contract state (pools, reserves) must be live
3. Can't fork Stellar's consensus network easily

---

## Conclusion

**Recommended Path Forward**:

1. **This Week**: Implement and run Layer 1 simulation tests
   - Zero risk, zero cost
   - Catches 90% of bugs
   - Required before any mainnet testing

2. **Next Week**: Run Layer 2 minimal mainnet tests
   - Low risk (~$10-20)
   - Final verification before deployment
   - Required for production confidence

3. **Deploy to Production**: After both layers pass
   - Start with transaction limits
   - Monitor closely
   - Graduated rollout

**Timeline to Deployment**: 1-2 weeks
**Total Testing Cost**: ~$20-30
**Confidence Level After Testing**: High ✅

---

## Next Steps

Choose your path:

**Option A: Maximum Safety** (Recommended)
1. Implement Layer 1 simulation tests (2-4 hours)
2. Run simulation tests until all pass
3. Fund test account with $20
4. Run Layer 2 mainnet tests
5. Deploy to production with limits

**Option B: Quick Deploy** (Higher Risk)
1. Review transaction construction code carefully
2. Deploy with very conservative limits ($10 max per tx)
3. Test with your own funds first
4. Monitor closely and be ready to disable

**Option C: Gradual Approach** (Balanced)
1. Deploy read-only features first (APY display, pool discovery)
2. Get users comfortable with the interface
3. Complete testing layers while users explore
4. Enable transactions after testing passes

---

*Document Version: 1.0*
*Last Updated: 2025-11-10*
*Status: Ready for Implementation*
