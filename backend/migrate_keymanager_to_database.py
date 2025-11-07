"""
Migrate existing KeyManager accounts to database-backed AgentAccountManager
WARNING: This is a one-way migration. Back up .stellar_keystore.json first!
"""
import json
from pathlib import Path
from agent_account_manager import AgentAccountManager
from database_passkeys import PasskeyDatabaseManager
from encryption import EncryptionManager
import sys


def migrate():
    """Migrate KeyManager accounts to AgentAccountManager"""
    keystore_path = Path(".stellar_keystore.json")

    if not keystore_path.exists():
        print("No existing keystore found. Nothing to migrate.")
        return

    # Backup existing keystore
    backup_path = keystore_path.with_suffix('.json.backup')
    import shutil
    shutil.copy(keystore_path, backup_path)
    print(f"✅ Backed up keystore to {backup_path}")

    # Load existing accounts
    with open(keystore_path) as f:
        accounts = json.load(f)

    print(f"Found {len(accounts)} accounts to migrate")

    if len(accounts) == 0:
        print("No accounts to migrate.")
        return

    # Get or create a default user for migration
    db = PasskeyDatabaseManager()

    # Check if migration user exists
    user = db.get_user_by_email("migration@tuxedo.local")
    if not user:
        print("Creating migration user...")
        user = db.create_user("migration@tuxedo.local")

    print(f"Migrating to user: {user['id']} ({user['email']})")

    # Migrate each account
    encryption = EncryptionManager()

    migrated_count = 0
    failed_count = 0

    for public_key, secret_key in accounts.items():
        try:
            # Encrypt secret key
            encrypted = encryption.encrypt(secret_key, user['id'])

            # Store in database
            db.create_agent_account(
                user_id=user['id'],
                stellar_public_key=public_key,
                stellar_secret_key_encrypted=encrypted,
                name=f"Migrated Account"
            )

            print(f"✅ Migrated {public_key}")
            migrated_count += 1

        except Exception as e:
            print(f"❌ Failed to migrate {public_key}: {e}")
            failed_count += 1

    print("\n" + "="*60)
    print(f"✅ Migration complete!")
    print(f"   Migrated: {migrated_count} accounts")
    print(f"   Failed: {failed_count} accounts")
    print(f"   Backup saved to: {backup_path}")
    print(f"   Accounts migrated to user: {user['email']}")
    print("="*60)


if __name__ == "__main__":
    print("="*60)
    print("KeyManager to AgentAccountManager Migration")
    print("="*60)
    print()
    print("This script will migrate existing Stellar accounts from")
    print("KeyManager (.stellar_keystore.json) to the new secure")
    print("AgentAccountManager with user isolation and encryption.")
    print()
    print("WARNING: This is a one-way migration!")
    print()

    response = input("Continue? (yes/no): ")
    if response.lower() != "yes":
        print("Migration cancelled.")
        sys.exit(0)

    try:
        migrate()
    except Exception as e:
        print(f"\n❌ Migration failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
