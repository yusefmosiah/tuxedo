"""
Test Phase 1: Database schema, chain abstraction, and encryption
"""
import sys
import os

# Add backend directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from database_passkeys import PasskeyDatabaseManager
from encryption import EncryptionManager
from chains.stellar import StellarAdapter
from chains.base import ChainKeypair
import sqlite3

def test_database_schema():
    """Test that new tables are created"""
    print("\n=== Testing Database Schema ===")

    db = PasskeyDatabaseManager("test_phase1.db")

    # Check if portfolios table exists
    with db.get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT name FROM sqlite_master
            WHERE type='table' AND name='portfolios'
        """)
        result = cursor.fetchone()
        assert result is not None, "portfolios table should exist"
        print("✅ portfolios table created")

        # Check if wallet_accounts table exists
        cursor.execute("""
            SELECT name FROM sqlite_master
            WHERE type='table' AND name='wallet_accounts'
        """)
        result = cursor.fetchone()
        assert result is not None, "wallet_accounts table should exist"
        print("✅ wallet_accounts table created")

        # Check indexes
        cursor.execute("""
            SELECT name FROM sqlite_master
            WHERE type='index' AND name='idx_portfolios_user_id'
        """)
        result = cursor.fetchone()
        assert result is not None, "portfolio index should exist"
        print("✅ Portfolio indexes created")

    # Clean up
    os.remove("test_phase1.db")
    print("✅ Database schema test passed!\n")

def test_encryption():
    """Test encryption manager"""
    print("=== Testing Encryption Manager ===")

    # Set a test encryption key
    os.environ['ENCRYPTION_MASTER_KEY'] = 'test-key-for-development-only-123456'
    os.environ['ENCRYPTION_SALT'] = 'test-salt'

    encryption = EncryptionManager()

    # Test encryption/decryption
    user_id = "test_user_123"
    secret_key = "SAMPLESTELLARSECRETKEY1234567890ABCDEFGHIJK"

    encrypted = encryption.encrypt(secret_key, user_id)
    print(f"✅ Encrypted: {encrypted[:50]}...")

    decrypted = encryption.decrypt(encrypted, user_id)
    assert decrypted == secret_key, "Decryption should return original value"
    print(f"✅ Decrypted successfully")

    # Test user isolation (different user_id should produce different encryption)
    user_id_2 = "test_user_456"
    encrypted_2 = encryption.encrypt(secret_key, user_id_2)
    assert encrypted != encrypted_2, "Different users should have different encrypted values"
    print(f"✅ User isolation verified")

    print("✅ Encryption test passed!\n")

def test_stellar_adapter():
    """Test Stellar chain adapter"""
    print("=== Testing Stellar Chain Adapter ===")

    adapter = StellarAdapter(network="testnet")

    # Test chain name
    assert adapter.chain_name == "stellar", "Chain name should be 'stellar'"
    print(f"✅ Chain name: {adapter.chain_name}")

    # Test keypair generation
    keypair = adapter.generate_keypair()
    assert keypair.chain == "stellar", "Keypair should be for stellar chain"
    assert keypair.public_key.startswith("G"), "Stellar public keys start with G"
    assert keypair.private_key.startswith("S"), "Stellar secret keys start with S"
    print(f"✅ Generated keypair: {keypair.public_key[:8]}...")

    # Test keypair import
    imported = adapter.import_keypair(keypair.private_key)
    assert imported.public_key == keypair.public_key, "Imported keypair should match"
    print(f"✅ Imported keypair successfully")

    # Test address validation
    assert adapter.validate_address(keypair.public_key), "Valid address should pass"
    assert not adapter.validate_address("invalid_address"), "Invalid address should fail"
    print(f"✅ Address validation working")

    # Test export
    exported = adapter.export_keypair(keypair)
    assert exported == keypair.private_key, "Exported key should match private key"
    print(f"✅ Export working")

    print("✅ Stellar adapter test passed!\n")

def test_integration():
    """Test integration of all Phase 1 components"""
    print("=== Testing Phase 1 Integration ===")

    # Setup
    os.environ['ENCRYPTION_MASTER_KEY'] = 'integration-test-key-123456'
    db = PasskeyDatabaseManager("test_integration.db")
    encryption = EncryptionManager()
    adapter = StellarAdapter(network="testnet")

    # Create a user
    user = db.create_user("test@example.com")
    user_id = user['id']
    print(f"✅ Created user: {user_id}")

    # Create a portfolio (manual SQL for now, will be in PortfolioManager)
    with db.get_connection() as conn:
        cursor = conn.cursor()
        portfolio_id = "portfolio_test123"
        cursor.execute("""
            INSERT INTO portfolios (id, user_id, name, created_at)
            VALUES (?, ?, ?, datetime('now'))
        """, (portfolio_id, user_id, "Test Portfolio"))
        conn.commit()
        print(f"✅ Created portfolio: {portfolio_id}")

    # Generate a keypair
    keypair = adapter.generate_keypair()
    print(f"✅ Generated keypair: {keypair.public_key[:8]}...")

    # Encrypt the private key
    encrypted_key = encryption.encrypt(keypair.private_key, user_id)
    print(f"✅ Encrypted private key")

    # Store in database
    with db.get_connection() as conn:
        cursor = conn.cursor()
        account_id = "account_test123"
        cursor.execute("""
            INSERT INTO wallet_accounts
            (id, portfolio_id, chain, public_key, encrypted_private_key, name, source)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (account_id, portfolio_id, "stellar", keypair.public_key,
              encrypted_key, "Test Account", "generated"))
        conn.commit()
        print(f"✅ Stored encrypted account in database")

    # Retrieve and decrypt
    with db.get_connection() as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("""
            SELECT * FROM wallet_accounts WHERE id = ?
        """, (account_id,))
        row = cursor.fetchone()
        account = dict(row)

    decrypted_key = encryption.decrypt(account['encrypted_private_key'], user_id)
    assert decrypted_key == keypair.private_key, "Decrypted key should match original"
    print(f"✅ Retrieved and decrypted successfully")

    # Verify we can use the decrypted key
    recovered_keypair = adapter.import_keypair(decrypted_key)
    assert recovered_keypair.public_key == keypair.public_key, "Recovered keypair should match"
    print(f"✅ Verified recovered keypair")

    # Clean up
    os.remove("test_integration.db")
    print("✅ Integration test passed!\n")

if __name__ == "__main__":
    print("\n" + "="*60)
    print("PHASE 1 TESTING: Database Schema, Encryption, Chain Abstraction")
    print("="*60)

    try:
        test_database_schema()
        test_encryption()
        test_stellar_adapter()
        test_integration()

        print("="*60)
        print("🎉 ALL PHASE 1 TESTS PASSED! 🎉")
        print("="*60)
        print("\nPhase 1 Complete:")
        print("✅ Database schema with portfolios and wallet_accounts tables")
        print("✅ Encryption manager with user-specific key derivation")
        print("✅ Chain abstraction layer (base classes)")
        print("✅ Stellar chain adapter")
        print("✅ Full integration: user → portfolio → encrypted wallet → storage")
        print("\nReady for Phase 2: Portfolio Manager implementation")
        print("="*60 + "\n")

    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
