"""
Database models for passkey authentication and chat thread persistence
Implements WebAuthn-based authentication with recovery codes and email fallback
"""
import sqlite3
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
import json
import secrets
import hashlib

class DatabaseManager:
    def __init__(self, db_path: str = "tuxedo.db"):
        self.db_path = db_path
        self.init_database()

    def init_database(self):
        """Initialize the database with required tables for passkey authentication"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            # Create users table (email required for passkey auth)
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    id TEXT PRIMARY KEY,
                    email TEXT UNIQUE NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_login TIMESTAMP,
                    is_active BOOLEAN DEFAULT TRUE
                )
            ''')

            # Store WebAuthn credentials (passkeys)
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS passkey_credentials (
                    id TEXT PRIMARY KEY,
                    user_id TEXT NOT NULL,
                    credential_id TEXT UNIQUE NOT NULL,
                    public_key TEXT NOT NULL,
                    sign_count INTEGER DEFAULT 0,
                    backup_eligible BOOLEAN DEFAULT FALSE,
                    transports TEXT,
                    friendly_name TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_used_at TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
                )
            ''')

            # Store authentication challenges (short-lived)
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS passkey_challenges (
                    id TEXT PRIMARY KEY,
                    challenge TEXT UNIQUE NOT NULL,
                    user_id TEXT,
                    expires_at TIMESTAMP NOT NULL,
                    used BOOLEAN DEFAULT FALSE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')

            # Store active sessions (token-based with sliding expiration)
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS passkey_sessions (
                    id TEXT PRIMARY KEY,
                    user_id TEXT NOT NULL,
                    session_token TEXT UNIQUE NOT NULL,
                    expires_at TIMESTAMP NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_active_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
                )
            ''')

            # Store recovery codes (8 per user, single-use)
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS recovery_codes (
                    id TEXT PRIMARY KEY,
                    user_id TEXT NOT NULL,
                    code_hash TEXT NOT NULL,
                    used BOOLEAN DEFAULT FALSE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    used_at TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
                )
            ''')

            # Store email recovery tokens (for lost passkeys + codes)
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS email_recovery_tokens (
                    id TEXT PRIMARY KEY,
                    user_id TEXT NOT NULL,
                    token TEXT UNIQUE NOT NULL,
                    expires_at TIMESTAMP NOT NULL,
                    used BOOLEAN DEFAULT FALSE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
                )
            ''')

            # Store recovery code attempts (rate limiting)
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS recovery_attempts (
                    id TEXT PRIMARY KEY,
                    user_id TEXT NOT NULL,
                    attempted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    success BOOLEAN DEFAULT FALSE,
                    ip_address TEXT,
                    FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
                )
            ''')

            # Create agents table (for future multi-agent feature)
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS agents (
                    id TEXT PRIMARY KEY,
                    user_id TEXT NOT NULL,
                    agent_name TEXT NOT NULL,
                    stellar_address TEXT UNIQUE NOT NULL,
                    encrypted_private_key TEXT NOT NULL,
                    permissions TEXT DEFAULT 'trade',
                    auto_approve_limit REAL DEFAULT 100.0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    is_active BOOLEAN DEFAULT TRUE,
                    FOREIGN KEY (user_id) REFERENCES users (id)
                )
            ''')

            # Create threads table (chat conversations)
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS threads (
                    id TEXT PRIMARY KEY,
                    user_id TEXT NOT NULL,
                    title TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    is_archived BOOLEAN DEFAULT FALSE,
                    FOREIGN KEY (user_id) REFERENCES users (id)
                )
            ''')

            # Create messages table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS messages (
                    id TEXT PRIMARY KEY,
                    thread_id TEXT NOT NULL,
                    role TEXT NOT NULL,
                    content TEXT NOT NULL,
                    metadata TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (thread_id) REFERENCES threads (id) ON DELETE CASCADE
                )
            ''')

            # Create indexes for better performance
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_passkey_credentials_user_id
                ON passkey_credentials(user_id)
            ''')
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_passkey_credentials_credential_id
                ON passkey_credentials(credential_id)
            ''')
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_passkey_sessions_user_id
                ON passkey_sessions(user_id)
            ''')
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_passkey_sessions_token
                ON passkey_sessions(session_token)
            ''')
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_recovery_codes_user_id
                ON recovery_codes(user_id)
            ''')
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_email_recovery_tokens_user_id
                ON email_recovery_tokens(user_id)
            ''')
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_email_recovery_tokens_token
                ON email_recovery_tokens(token)
            ''')
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_recovery_attempts_user_id
                ON recovery_attempts(user_id)
            ''')
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_recovery_attempts_attempted_at
                ON recovery_attempts(attempted_at)
            ''')
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_messages_thread_id
                ON messages (thread_id)
            ''')
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_threads_user_id
                ON threads (user_id)
            ''')
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_threads_updated_at
                ON threads (updated_at DESC)
            ''')
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_agents_user_id
                ON agents (user_id)
            ''')

            conn.commit()

    # User management methods
    def create_user(self, email: str) -> Dict[str, Any]:
        """Create new user account"""
        user_id = f"user_{secrets.token_urlsafe(16)}"

        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()

            cursor.execute('''
                INSERT INTO users (id, email, created_at)
                VALUES (?, ?, ?)
            ''', (user_id, email, datetime.now()))
            conn.commit()

            cursor.execute('SELECT * FROM users WHERE id = ?', (user_id,))
            return dict(cursor.fetchone())

    def get_user_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        """Get user by email"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()

            cursor.execute('SELECT * FROM users WHERE email = ? AND is_active = TRUE', (email,))
            user = cursor.fetchone()
            return dict(user) if user else None

    def get_user_by_id(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get user by ID"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()

            cursor.execute('SELECT * FROM users WHERE id = ? AND is_active = TRUE', (user_id,))
            user = cursor.fetchone()
            return dict(user) if user else None

    def update_user_last_login(self, user_id: str):
        """Update user's last login timestamp"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE users SET last_login = ? WHERE id = ?
            ''', (datetime.now(), user_id))
            conn.commit()

    # Passkey credential methods
    def store_passkey_credential(self, user_id: str, credential_id: str, public_key: str,
                                 sign_count: int = 0, backup_eligible: bool = False,
                                 transports: Optional[List[str]] = None,
                                 friendly_name: Optional[str] = None) -> str:
        """Store a new passkey credential"""
        cred_id = f"cred_{secrets.token_urlsafe(16)}"
        transports_json = json.dumps(transports) if transports else None

        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO passkey_credentials
                (id, user_id, credential_id, public_key, sign_count, backup_eligible, transports, friendly_name)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (cred_id, user_id, credential_id, public_key, sign_count, backup_eligible,
                  transports_json, friendly_name))
            conn.commit()

        return cred_id

    def get_passkey_credential(self, credential_id: str) -> Optional[Dict[str, Any]]:
        """Get passkey credential by credential_id"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()

            cursor.execute('''
                SELECT * FROM passkey_credentials WHERE credential_id = ?
            ''', (credential_id,))

            cred = cursor.fetchone()
            if cred:
                cred_dict = dict(cred)
                if cred_dict.get('transports'):
                    cred_dict['transports'] = json.loads(cred_dict['transports'])
                return cred_dict
            return None

    def get_user_passkeys(self, user_id: str) -> List[Dict[str, Any]]:
        """Get all passkeys for a user"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()

            cursor.execute('''
                SELECT * FROM passkey_credentials
                WHERE user_id = ?
                ORDER BY created_at DESC
            ''', (user_id,))

            passkeys = cursor.fetchall()
            result = []
            for passkey in passkeys:
                passkey_dict = dict(passkey)
                if passkey_dict.get('transports'):
                    passkey_dict['transports'] = json.loads(passkey_dict['transports'])
                result.append(passkey_dict)
            return result

    def update_passkey_sign_count(self, credential_id: str, sign_count: int):
        """Update passkey sign count and last used timestamp"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE passkey_credentials
                SET sign_count = ?, last_used_at = ?
                WHERE credential_id = ?
            ''', (sign_count, datetime.now(), credential_id))
            conn.commit()

    def delete_passkey(self, passkey_id: str, user_id: str) -> bool:
        """Delete a passkey (cannot delete last passkey)"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            # Check if this is the last passkey
            cursor.execute('''
                SELECT COUNT(*) as count FROM passkey_credentials WHERE user_id = ?
            ''', (user_id,))
            count = cursor.fetchone()[0]

            if count <= 1:
                return False  # Cannot delete last passkey

            cursor.execute('''
                DELETE FROM passkey_credentials WHERE id = ? AND user_id = ?
            ''', (passkey_id, user_id))
            conn.commit()
            return cursor.rowcount > 0

    def invalidate_all_passkeys(self, user_id: str):
        """Invalidate all passkeys for a user (during account recovery)"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                DELETE FROM passkey_credentials WHERE user_id = ?
            ''', (user_id,))
            conn.commit()

    # Challenge management methods
    def create_challenge(self, user_id: Optional[str] = None) -> tuple[str, str]:
        """Create a new WebAuthn challenge"""
        challenge_id = f"chal_{secrets.token_urlsafe(16)}"
        challenge = secrets.token_urlsafe(32)
        expires_at = datetime.now() + timedelta(minutes=15)

        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO passkey_challenges (id, challenge, user_id, expires_at)
                VALUES (?, ?, ?, ?)
            ''', (challenge_id, challenge, user_id, expires_at))
            conn.commit()

        return challenge_id, challenge

    def get_challenge(self, challenge_id: str) -> Optional[Dict[str, Any]]:
        """Get and mark challenge as used"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()

            cursor.execute('''
                SELECT * FROM passkey_challenges
                WHERE id = ? AND expires_at > ? AND used = FALSE
            ''', (challenge_id, datetime.now()))

            challenge = cursor.fetchone()
            if not challenge:
                return None

            # Mark as used
            cursor.execute('''
                UPDATE passkey_challenges SET used = TRUE WHERE id = ?
            ''', (challenge_id,))
            conn.commit()

            return dict(challenge)

    # Session management methods
    def create_session(self, user_id: str) -> str:
        """Create a new session token (sliding expiration: 24h idle, 7d absolute)"""
        session_id = f"session_{secrets.token_urlsafe(16)}"
        session_token = secrets.token_urlsafe(64)
        expires_at = datetime.now() + timedelta(days=7)  # Absolute timeout

        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO passkey_sessions (id, user_id, session_token, expires_at)
                VALUES (?, ?, ?, ?)
            ''', (session_id, user_id, session_token, expires_at))
            conn.commit()

        return session_token

    def validate_session(self, session_token: str) -> Optional[Dict[str, Any]]:
        """Validate session and update last_active_at (sliding expiration)"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()

            cursor.execute('''
                SELECT ps.*, u.email
                FROM passkey_sessions ps
                JOIN users u ON ps.user_id = u.id
                WHERE ps.session_token = ? AND ps.expires_at > ? AND u.is_active = TRUE
            ''', (session_token, datetime.now()))

            session = cursor.fetchone()
            if not session:
                return None

            session_dict = dict(session)

            # Check sliding expiration (24h idle timeout)
            last_active = datetime.fromisoformat(session_dict['last_active_at'])
            if datetime.now() - last_active > timedelta(hours=24):
                # Session expired due to inactivity
                return None

            # Update last active timestamp
            cursor.execute('''
                UPDATE passkey_sessions
                SET last_active_at = ?
                WHERE session_token = ?
            ''', (datetime.now(), session_token))
            conn.commit()

            return session_dict

    def delete_session(self, session_token: str):
        """Delete a session (logout)"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                DELETE FROM passkey_sessions WHERE session_token = ?
            ''', (session_token,))
            conn.commit()

    def delete_all_user_sessions(self, user_id: str):
        """Delete all sessions for a user"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                DELETE FROM passkey_sessions WHERE user_id = ?
            ''', (user_id,))
            conn.commit()

    # Recovery code methods
    def generate_recovery_codes(self, user_id: str) -> List[str]:
        """Generate 8 recovery codes for a user"""
        # First, delete any existing codes
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('DELETE FROM recovery_codes WHERE user_id = ?', (user_id,))
            conn.commit()

        codes = []
        for _ in range(8):
            # Generate 24-character code (128-bit entropy)
            code = secrets.token_urlsafe(18)[:24]
            code_hash = hashlib.sha256(code.encode()).hexdigest()
            code_id = f"rc_{secrets.token_urlsafe(8)}"

            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO recovery_codes (id, user_id, code_hash)
                    VALUES (?, ?, ?)
                ''', (code_id, user_id, code_hash))
                conn.commit()

            codes.append(code)

        return codes

    def verify_recovery_code(self, user_id: str, code: str) -> bool:
        """Verify and consume a recovery code"""
        code_hash = hashlib.sha256(code.encode()).hexdigest()

        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()

            cursor.execute('''
                SELECT * FROM recovery_codes
                WHERE user_id = ? AND code_hash = ? AND used = FALSE
            ''', (user_id, code_hash))

            recovery_code = cursor.fetchone()
            if not recovery_code:
                return False

            # Mark as used
            cursor.execute('''
                UPDATE recovery_codes
                SET used = TRUE, used_at = ?
                WHERE id = ?
            ''', (datetime.now(), recovery_code['id']))
            conn.commit()

            return True

    def count_remaining_recovery_codes(self, user_id: str) -> int:
        """Count remaining unused recovery codes"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT COUNT(*) as count FROM recovery_codes
                WHERE user_id = ? AND used = FALSE
            ''', (user_id,))
            return cursor.fetchone()[0]

    # Recovery attempt tracking (rate limiting)
    def log_recovery_attempt(self, user_id: str, success: bool, ip_address: Optional[str] = None):
        """Log a recovery code attempt"""
        attempt_id = f"attempt_{secrets.token_urlsafe(8)}"

        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO recovery_attempts (id, user_id, success, ip_address)
                VALUES (?, ?, ?, ?)
            ''', (attempt_id, user_id, success, ip_address))
            conn.commit()

    def check_recovery_rate_limit(self, user_id: str) -> tuple[bool, int]:
        """Check if user has exceeded recovery attempt rate limit
        Returns: (is_limited, retry_after_seconds)
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            # Count failed attempts in last hour
            one_hour_ago = datetime.now() - timedelta(hours=1)
            cursor.execute('''
                SELECT COUNT(*) as count FROM recovery_attempts
                WHERE user_id = ? AND attempted_at > ? AND success = FALSE
            ''', (user_id, one_hour_ago))

            failed_count = cursor.fetchone()[0]

            if failed_count >= 5:
                # Get time of 5th failed attempt
                cursor.execute('''
                    SELECT attempted_at FROM recovery_attempts
                    WHERE user_id = ? AND attempted_at > ? AND success = FALSE
                    ORDER BY attempted_at ASC
                    LIMIT 1
                ''', (user_id, one_hour_ago))

                first_attempt = cursor.fetchone()
                if first_attempt:
                    first_attempt_time = datetime.fromisoformat(first_attempt[0])
                    unlock_time = first_attempt_time + timedelta(hours=1)
                    retry_after = int((unlock_time - datetime.now()).total_seconds())
                    return True, max(0, retry_after)

            return False, 0

    # Email recovery methods
    def create_email_recovery_token(self, user_id: str) -> str:
        """Create an email recovery token"""
        token_id = f"recovery_{secrets.token_urlsafe(16)}"
        token = secrets.token_urlsafe(32)
        expires_at = datetime.now() + timedelta(hours=1)

        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO email_recovery_tokens (id, user_id, token, expires_at)
                VALUES (?, ?, ?, ?)
            ''', (token_id, user_id, token, expires_at))
            conn.commit()

        return token

    def validate_email_recovery_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Validate and consume email recovery token"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()

            cursor.execute('''
                SELECT * FROM email_recovery_tokens
                WHERE token = ? AND expires_at > ? AND used = FALSE
            ''', (token, datetime.now()))

            recovery_token = cursor.fetchone()
            if not recovery_token:
                return None

            # Mark as used
            cursor.execute('''
                UPDATE email_recovery_tokens SET used = TRUE WHERE id = ?
            ''', (recovery_token['id'],))
            conn.commit()

            return dict(recovery_token)

    # Thread management methods (for chat functionality)
    def create_thread(self, title: str, user_id: str) -> str:
        """Create a new chat thread for a user"""
        thread_id = f"thread_{int(datetime.now().timestamp() * 1000)}"

        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO threads (id, user_id, title, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?)
            ''', (thread_id, user_id, title, datetime.now(), datetime.now()))
            conn.commit()

        return thread_id

    def get_thread(self, thread_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific thread by ID"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()

            cursor.execute('''
                SELECT * FROM threads WHERE id = ? AND is_archived = FALSE
            ''', (thread_id,))

            thread = cursor.fetchone()
            return dict(thread) if thread else None

    def get_threads(self, user_id: Optional[str] = None, limit: int = 50) -> List[Dict[str, Any]]:
        """Get all threads for a user, sorted by updated_at"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()

            if user_id:
                cursor.execute('''
                    SELECT * FROM threads
                    WHERE user_id = ? AND is_archived = FALSE
                    ORDER BY updated_at DESC
                    LIMIT ?
                ''', (user_id, limit))
            else:
                cursor.execute('''
                    SELECT * FROM threads
                    WHERE is_archived = FALSE
                    ORDER BY updated_at DESC
                    LIMIT ?
                ''', (limit,))

            threads = cursor.fetchall()
            return [dict(thread) for thread in threads]

    def update_thread(self, thread_id: str, title: Optional[str] = None) -> bool:
        """Update thread title and updated_at timestamp"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            if title:
                cursor.execute('''
                    UPDATE threads
                    SET title = ?, updated_at = ?
                    WHERE id = ?
                ''', (title, datetime.now(), thread_id))
            else:
                cursor.execute('''
                    UPDATE threads
                    SET updated_at = ?
                    WHERE id = ?
                ''', (datetime.now(), thread_id))

            conn.commit()
            return cursor.rowcount > 0

    def archive_thread(self, thread_id: str) -> bool:
        """Archive a thread (soft delete)"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE threads
                SET is_archived = TRUE, updated_at = ?
                WHERE id = ?
            ''', (datetime.now(), thread_id))
            conn.commit()
            return cursor.rowcount > 0

    def delete_thread(self, thread_id: str) -> bool:
        """Delete a thread and all its messages"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('DELETE FROM messages WHERE thread_id = ?', (thread_id,))
            cursor.execute('DELETE FROM threads WHERE id = ?', (thread_id,))
            conn.commit()
            return cursor.rowcount > 0

    def add_message(self, thread_id: str, role: str, content: str,
                   metadata: Optional[Dict[str, Any]] = None) -> str:
        """Add a message to a thread"""
        message_id = f"msg_{int(datetime.now().timestamp() * 1000)}"

        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO messages (id, thread_id, role, content, metadata, created_at)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (message_id, thread_id, role, content,
                   json.dumps(metadata) if metadata else None, datetime.now()))

            # Update thread's updated_at timestamp
            cursor.execute('''
                UPDATE threads SET updated_at = ? WHERE id = ?
            ''', (datetime.now(), thread_id))

            conn.commit()

        return message_id

    def get_messages(self, thread_id: str) -> List[Dict[str, Any]]:
        """Get all messages for a thread"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()

            cursor.execute('''
                SELECT * FROM messages
                WHERE thread_id = ?
                ORDER BY created_at ASC
            ''', (thread_id,))

            messages = cursor.fetchall()
            result = []

            for message in messages:
                msg_dict = dict(message)
                if msg_dict['metadata']:
                    try:
                        msg_dict['metadata'] = json.loads(msg_dict['metadata'])
                    except json.JSONDecodeError:
                        msg_dict['metadata'] = {}
                result.append(msg_dict)

            return result

    def update_thread_from_chat_messages(self, thread_id: str, messages: List[Dict[str, Any]]) -> bool:
        """Update thread with chat messages from the current session"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            # Clear existing messages for this thread
            cursor.execute('DELETE FROM messages WHERE thread_id = ?', (thread_id,))

            # Add all messages
            for message in messages:
                message_id = f"msg_{int(datetime.now().timestamp() * 1000)}_{message['id']}"

                cursor.execute('''
                    INSERT INTO messages (id, thread_id, role, content, metadata, created_at)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (message_id, thread_id, message['role'], message['content'],
                       json.dumps({
                           'type': message.get('type'),
                           'toolName': message.get('toolName'),
                           'iteration': message.get('iteration'),
                           'isStreaming': message.get('isStreaming'),
                           'summary': message.get('summary')
                       }) if message.get('type') or message.get('toolName') else None,
                       datetime.now()))

            # Update thread's updated_at timestamp
            cursor.execute('''
                UPDATE threads SET updated_at = ? WHERE id = ?
            ''', (datetime.now(), thread_id))

            conn.commit()
            return True

# Global database instance
db = DatabaseManager()
