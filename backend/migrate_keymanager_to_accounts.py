"""
Migrate existing KeyManager accounts to AccountManager
Imports all existing Stellar accounts directly to user
NO portfolio table or portfolio_id - accounts belong to users
"""
import json
from pathlib import Path
from account_manager import AccountManager
from database_passkeys import PasskeyDatabaseManager
import shutil
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def migrate():
    """
    Migrate accounts from KeyManager (.stellar_keystore.json) to AccountManager
    """
    keystore_path = Path(".stellar_keystore.json")

    if not keystore_path.exists():
        logger.info("No existing keystore found. Nothing to migrate.")
        return

    # Backup
    backup_path = keystore_path.with_suffix('.json.backup')
    shutil.copy(keystore_path, backup_path)
    logger.info(f"✅ Backed up keystore to {backup_path}")

    # Load existing accounts
    with open(keystore_path) as f:
        accounts = json.load(f)

    logger.info(f"Found {len(accounts)} Stellar accounts to migrate")

    # Get or create default migration user
    db = PasskeyDatabaseManager()
    user = db.get_user_by_email("migration@tuxedo.local")
    if not user:
        logger.info("Creating migration user...")
        user = db.create_user("migration@tuxedo.local")

    logger.info(f"Using user: {user['email']} (ID: {user['id']})")

    # Import each account directly to user (NO portfolio!)
    manager = AccountManager()
    success_count = 0
    failed_count = 0

    for public_key, secret_key in accounts.items():
        try:
            result = manager.import_account(
                user_id=user['id'],
                chain="stellar",
                private_key=secret_key,
                name=f"Migrated {public_key[:8]}..."
            )

            if result.get("success"):
                logger.info(f"✅ Migrated {public_key}")
                success_count += 1
            else:
                logger.error(f"❌ Failed to migrate {public_key}: {result.get('error')}")
                failed_count += 1

        except Exception as e:
            logger.error(f"❌ Failed to migrate {public_key}: {e}")
            failed_count += 1

    logger.info(f"\n{'='*60}")
    logger.info("✅ Migration complete!")
    logger.info(f"   User: {user['email']}")
    logger.info(f"   Accounts migrated: {success_count}")
    logger.info(f"   Accounts failed: {failed_count}")
    logger.info(f"   Agent can now construct portfolio views from these accounts")
    logger.info(f"{'='*60}")

if __name__ == "__main__":
    migrate()
