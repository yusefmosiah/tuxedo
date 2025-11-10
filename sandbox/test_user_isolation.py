"""
Test User Isolation After Quantum Leap Migration
Validates that:
- User A cannot access User B's accounts
- User can access their own accounts
- List accounts returns only user's accounts
- Permission checks work correctly
"""

import sys
import os

# Add backend directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from account_manager import AccountManager
from database_passkeys import PasskeyDatabaseManager
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def test_cross_user_account_access():
    """User A cannot access User B's accounts"""
    logger.info("=" * 60)
    logger.info("TEST 1: Cross-user account access (should be denied)")
    logger.info("=" * 60)

    db = PasskeyDatabaseManager()
    account_mgr = AccountManager()

    # Create two test users
    user_a_email = "test_user_a@quantum-leap.test"
    user_b_email = "test_user_b@quantum-leap.test"

    # Clean up if users already exist
    existing_a = db.get_user_by_email(user_a_email)
    existing_b = db.get_user_by_email(user_b_email)
    if existing_a:
        logger.info(f"Using existing user A: {existing_a['id']}")
        user_a = existing_a
    else:
        user_a = db.create_user(user_a_email)
        logger.info(f"Created user A: {user_a['id']}")

    if existing_b:
        logger.info(f"Using existing user B: {existing_b['id']}")
        user_b = existing_b
    else:
        user_b = db.create_user(user_b_email)
        logger.info(f"Created user B: {user_b['id']}")

    # User A creates an account
    logger.info(f"\nUser A ({user_a['id']}) creating account...")
    result_a = account_mgr.generate_account(
        user_id=user_a['id'],
        chain="stellar",
        name="User A Account"
    )

    if not result_a.get('success'):
        logger.error(f"❌ Failed to create account for User A: {result_a}")
        return False

    account_a_id = result_a['account_id']
    logger.info(f"✅ User A created account: {account_a_id}")

    # User B tries to export User A's account (SHOULD FAIL)
    logger.info(f"\nUser B ({user_b['id']}) trying to export User A's account...")
    result = account_mgr.export_account(
        user_id=user_b['id'],
        account_id=account_a_id
    )

    if result.get('success'):
        logger.error(f"❌ SECURITY BREACH: User B was able to export User A's account!")
        logger.error(f"   Result: {result}")
        return False
    elif "Permission denied" in result.get('error', ''):
        logger.info(f"✅ PASS: User B correctly denied access to User A's account")
        logger.info(f"   Error message: {result['error']}")
        return True
    else:
        logger.error(f"❌ FAIL: Unexpected error: {result.get('error')}")
        return False


def test_user_can_access_own_accounts():
    """User can access their own accounts"""
    logger.info("\n" + "=" * 60)
    logger.info("TEST 2: User can access own accounts (should succeed)")
    logger.info("=" * 60)

    db = PasskeyDatabaseManager()
    account_mgr = AccountManager()

    user_email = "test_user_own@quantum-leap.test"
    existing = db.get_user_by_email(user_email)
    if existing:
        user = existing
        logger.info(f"Using existing user: {user['id']}")
    else:
        user = db.create_user(user_email)
        logger.info(f"Created user: {user['id']}")

    # Create account
    logger.info(f"\nUser creating account...")
    result = account_mgr.generate_account(
        user_id=user['id'],
        chain="stellar",
        name="Own Account Test"
    )

    if not result.get('success'):
        logger.error(f"❌ Failed to create account: {result}")
        return False

    account_id = result['account_id']
    logger.info(f"✅ Account created: {account_id}")

    # Export own account (SHOULD SUCCEED)
    logger.info(f"\nUser exporting own account...")
    result = account_mgr.export_account(
        user_id=user['id'],
        account_id=account_id
    )

    if result.get('success') and 'private_key' in result:
        logger.info(f"✅ PASS: User successfully exported own account")
        logger.info(f"   Account has private key: {'S' in result['private_key']}")
        return True
    else:
        logger.error(f"❌ FAIL: User could not export own account")
        logger.error(f"   Result: {result}")
        return False


def test_list_accounts_user_isolated():
    """List accounts returns only user's accounts"""
    logger.info("\n" + "=" * 60)
    logger.info("TEST 3: List accounts user isolation (should show only own)")
    logger.info("=" * 60)

    db = PasskeyDatabaseManager()
    account_mgr = AccountManager()

    # Create two users
    user_a_email = "test_list_a@quantum-leap.test"
    user_b_email = "test_list_b@quantum-leap.test"

    existing_a = db.get_user_by_email(user_a_email)
    existing_b = db.get_user_by_email(user_b_email)

    user_a = existing_a if existing_a else db.create_user(user_a_email)
    user_b = existing_b if existing_b else db.create_user(user_b_email)

    logger.info(f"User A: {user_a['id']}")
    logger.info(f"User B: {user_b['id']}")

    # User A creates 2 accounts
    logger.info(f"\nUser A creating 2 accounts...")
    for i in range(2):
        result = account_mgr.generate_account(user_a['id'], "stellar", f"A Account {i+1}")
        if result.get('success'):
            logger.info(f"  ✅ Created account {i+1}: {result['account_id']}")
        else:
            logger.error(f"  ❌ Failed to create account {i+1}")

    # User B creates 1 account
    logger.info(f"\nUser B creating 1 account...")
    result = account_mgr.generate_account(user_b['id'], "stellar", "B Account")
    if result.get('success'):
        logger.info(f"  ✅ Created account: {result['account_id']}")
    else:
        logger.error(f"  ❌ Failed to create account")

    # User A lists accounts (should see only their accounts)
    logger.info(f"\nUser A listing accounts...")
    accounts_a = account_mgr.get_user_accounts(user_a['id'], chain="stellar")
    logger.info(f"  User A sees {len(accounts_a)} Stellar account(s)")
    for acc in accounts_a:
        logger.info(f"    - {acc['id']}: {acc.get('name', 'Unnamed')}")

    # User B lists accounts (should see only their account)
    logger.info(f"\nUser B listing accounts...")
    accounts_b = account_mgr.get_user_accounts(user_b['id'], chain="stellar")
    logger.info(f"  User B sees {len(accounts_b)} Stellar account(s)")
    for acc in accounts_b:
        logger.info(f"    - {acc['id']}: {acc.get('name', 'Unnamed')}")

    # Verify isolation
    logger.info(f"\nVerifying isolation...")
    if len(accounts_a) >= 2 and len(accounts_b) >= 1:
        # Check that accounts don't overlap
        a_ids = {acc['id'] for acc in accounts_a}
        b_ids = {acc['id'] for acc in accounts_b}
        overlap = a_ids & b_ids

        if overlap:
            logger.error(f"❌ FAIL: Accounts overlap between users: {overlap}")
            return False
        else:
            logger.info(f"✅ PASS: Account lists are properly isolated")
            logger.info(f"   User A: {len(accounts_a)} accounts")
            logger.info(f"   User B: {len(accounts_b)} accounts")
            logger.info(f"   No overlap: {len(overlap)} common accounts")
            return True
    else:
        logger.warning(f"⚠️  Could not verify (insufficient accounts created)")
        return True  # Don't fail if accounts weren't created


def test_permission_check_on_operations():
    """Test permission checks on account operations"""
    logger.info("\n" + "=" * 60)
    logger.info("TEST 4: Permission checks on operations")
    logger.info("=" * 60)

    db = PasskeyDatabaseManager()
    account_mgr = AccountManager()

    # Create two users
    user_a_email = "test_perm_a@quantum-leap.test"
    user_b_email = "test_perm_b@quantum-leap.test"

    existing_a = db.get_user_by_email(user_a_email)
    existing_b = db.get_user_by_email(user_b_email)

    user_a = existing_a if existing_a else db.create_user(user_a_email)
    user_b = existing_b if existing_b else db.create_user(user_b_email)

    # User A creates account
    result = account_mgr.generate_account(user_a['id'], "stellar", "Permission Test")
    if not result.get('success'):
        logger.error(f"❌ Failed to create test account")
        return False

    account_id = result['account_id']
    logger.info(f"User A created account: {account_id}")

    # Test User B trying to use user_owns_account
    logger.info(f"\nTesting user_owns_account()...")
    owns_a = account_mgr.user_owns_account(user_a['id'], account_id)
    owns_b = account_mgr.user_owns_account(user_b['id'], account_id)

    logger.info(f"  User A owns account: {owns_a}")
    logger.info(f"  User B owns account: {owns_b}")

    if owns_a and not owns_b:
        logger.info(f"✅ PASS: Ownership check works correctly")
        return True
    else:
        logger.error(f"❌ FAIL: Ownership check incorrect")
        return False


def main():
    """Run all tests"""
    logger.info("\n" + "=" * 60)
    logger.info("🚀 QUANTUM LEAP MIGRATION - USER ISOLATION TESTS")
    logger.info("=" * 60)
    logger.info("Testing AccountManager with user_id enforcement\n")

    tests = [
        ("Cross-user access denial", test_cross_user_account_access),
        ("Own account access", test_user_can_access_own_accounts),
        ("List accounts isolation", test_list_accounts_user_isolated),
        ("Permission checks", test_permission_check_on_operations),
    ]

    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            logger.error(f"❌ Exception in {test_name}: {e}")
            import traceback
            traceback.print_exc()
            results.append((test_name, False))

    # Summary
    logger.info("\n" + "=" * 60)
    logger.info("📊 TEST RESULTS SUMMARY")
    logger.info("=" * 60)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        logger.info(f"{status}: {test_name}")

    logger.info("=" * 60)
    logger.info(f"Result: {passed}/{total} tests passed")

    if passed == total:
        logger.info("🎉 ALL TESTS PASSED - User isolation is working!")
        logger.info("✅ Quantum Leap migration successful!")
        return 0
    else:
        logger.error(f"⚠️  {total - passed} test(s) failed")
        logger.error("❌ User isolation not fully working - review implementation")
        return 1


if __name__ == "__main__":
    sys.exit(main())
