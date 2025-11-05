#!/usr/bin/env python3
"""
Passkey Migration Script
Drops old magic link tables and creates new passkey-based authentication schema
"""

import sqlite3
import os
from datetime import datetime

def migrate_to_passkeys(db_path: str = "tuxedo.db"):
    """Migrate database from magic links to passkey authentication"""

    if not os.path.exists(db_path):
        print(f"Database {db_path} does not exist. Creating new passkey database.")
        # We'll let the new database.py handle creation
        return

    print(f"Migrating database {db_path} to passkey authentication...")

    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()

        # Drop old magic link tables
        print("Dropping old magic link tables...")
        cursor.execute("DROP TABLE IF EXISTS magic_link_sessions")
        cursor.execute("DROP TABLE IF EXISTS user_sessions")

        # Check if passkey tables exist, create them if not
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='passkey_credentials'")
        if cursor.fetchone():
            print("Passkey tables already exist. Skipping table creation.")
        else:
            print("Creating passkey authentication tables...")

            # Create passkey tables
            cursor.execute('''
                CREATE TABLE passkey_credentials (
                    id TEXT PRIMARY KEY,
                    user_id TEXT NOT NULL,
                    credential_id TEXT UNIQUE NOT NULL,
                    public_key TEXT NOT NULL,
                    sign_count INTEGER DEFAULT 0,
                    backup_eligible BOOLEAN DEFAULT FALSE,
                    transports TEXT,
                    friendly_name TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
                )
            ''')

            cursor.execute('''
                CREATE TABLE passkey_challenges (
                    id TEXT PRIMARY KEY,
                    challenge TEXT UNIQUE NOT NULL,
                    user_id TEXT,
                    expires_at TIMESTAMP NOT NULL,
                    used BOOLEAN DEFAULT FALSE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')

            cursor.execute('''
                CREATE TABLE passkey_sessions (
                    id TEXT PRIMARY KEY,
                    user_id TEXT NOT NULL,
                    session_token TEXT UNIQUE NOT NULL,
                    expires_at TIMESTAMP NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
                )
            ''')

            # Update threads table to support agent-based architecture
            cursor.execute('''
                ALTER TABLE threads ADD COLUMN agent_id TEXT
            ''')

            # Add recovery codes table
            cursor.execute('''
                CREATE TABLE recovery_codes (
                    id TEXT PRIMARY KEY,
                    user_id TEXT NOT NULL,
                    code_hash TEXT NOT NULL,
                    used BOOLEAN DEFAULT FALSE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    used_at TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
                )
            ''')

            # Add stellar_public_key to users table if not exists
            try:
                cursor.execute('ALTER TABLE users ADD COLUMN stellar_public_key TEXT')
            except sqlite3.OperationalError:
                print("stellar_public_key column already exists")

            # Create indexes for better performance
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_passkey_credentials_user_id ON passkey_credentials(user_id)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_passkey_credentials_credential_id ON passkey_credentials(credential_id)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_passkey_sessions_user_id ON passkey_sessions(user_id)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_passkey_sessions_token ON passkey_sessions(session_token)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_threads_agent_id ON threads(agent_id)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_recovery_codes_user_id ON recovery_codes(user_id)')

        conn.commit()
        print("Migration completed successfully!")

if __name__ == "__main__":
    migrate_to_passkeys()