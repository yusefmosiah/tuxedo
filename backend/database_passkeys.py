"""
Database models for passkey authentication and user management
Implements Phase 1 of Passkey Architecture v2
"""
import sqlite3
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
import json
import secrets
import hashlib
import logging

logger = logging.getLogger(__name__)

class PasskeyDatabaseManager:
    def __init__(self, db_path: str = "tuxedo_passkeys.db"):
        self.db_path = db_path
        self.init_database()

    def init_database(self):
        """Initialize the database with passkey authentication tables"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            # Create users table (with email required)
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    id TEXT PRIMARY KEY,
                    email TEXT UNIQUE NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_login TIMESTAMP,
                    is_active BOOLEAN DEFAULT TRUE
                )
            ''')

            # Store WebAuthn credentials
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

            # Store active sessions (with sliding expiration)
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

            # Store recovery codes (8 per user)
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

            # Create threads table (for chat history)
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS threads (
                    id TEXT PRIMARY KEY,
                    user_id TEXT NOT NULL,
                    title TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    is_archived BOOLEAN DEFAULT FALSE,
                    FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
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

            # Create indexes
            self._create_indexes(cursor)

            conn.commit()

    def _create_indexes(self, cursor):
        """Create database indexes for better performance"""
        indexes = [
            'CREATE INDEX IF NOT EXISTS idx_passkey_credentials_user_id ON passkey_credentials(user_id)',
            'CREATE INDEX IF NOT EXISTS idx_passkey_credentials_credential_id ON passkey_credentials(credential_id)',
            'CREATE INDEX IF NOT EXISTS idx_passkey_sessions_user_id ON passkey_sessions(user_id)',
            'CREATE INDEX IF NOT EXISTS idx_passkey_sessions_token ON passkey_sessions(session_token)',
            'CREATE INDEX IF NOT EXISTS idx_recovery_codes_user_id ON recovery_codes(user_id)',
            'CREATE INDEX IF NOT EXISTS idx_email_recovery_tokens_user_id ON email_recovery_tokens(user_id)',
            'CREATE INDEX IF NOT EXISTS idx_email_recovery_tokens_token ON email_recovery_tokens(token)',
            'CREATE INDEX IF NOT EXISTS idx_recovery_attempts_user_id ON recovery_attempts(user_id)',
            'CREATE INDEX IF NOT EXISTS idx_recovery_attempts_attempted_at ON recovery_attempts(attempted_at)',
            'CREATE INDEX IF NOT EXISTS idx_threads_user_id ON threads(user_id)',
            'CREATE INDEX IF NOT EXISTS idx_threads_updated_at ON threads(updated_at DESC)',
            'CREATE INDEX IF NOT EXISTS idx_messages_thread_id ON messages(thread_id)'
        ]

        for index_sql in indexes:
            cursor.execute(index_sql)

    # User management
    def create_user(self, email: str) -> Dict[str, Any]:
        """Create a new user"""
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

    def update_last_login(self, user_id: str):
        """Update user's last login timestamp"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE users SET last_login = ? WHERE id = ?
            ''', (datetime.now(), user_id))
            conn.commit()

    # Passkey credential management
    def store_passkey_credential(self, user_id: str, credential_id: str,
                                 public_key: str, sign_count: int = 0,
                                 backup_eligible: bool = False, transports: List[str] = None,
                                 friendly_name: str = None) -> str:
        """Store a new passkey credential"""
        cred_id = f"cred_{secrets.token_urlsafe(16)}"
        transports_json = json.dumps(transports) if transports else None

        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO passkey_credentials
                (id, user_id, credential_id, public_key, sign_count,
                 backup_eligible, transports, friendly_name, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (cred_id, user_id, credential_id, public_key, sign_count,
                  backup_eligible, transports_json, friendly_name, datetime.now()))
            conn.commit()

        return cred_id

    def get_passkey_credential(self, credential_id: str) -> Optional[Dict[str, Any]]:
        """
        Get passkey credential by credential_id.

        Handles both padded and unpadded base64url encoding for backward compatibility.
        """
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()

            # Try exact match first (unpadded, per WebAuthn spec)
            cursor.execute('''
                SELECT * FROM passkey_credentials WHERE credential_id = ?
            ''', (credential_id,))
            cred = cursor.fetchone()

            # If not found, try with padding for backward compatibility
            if not cred:
                # Add padding to match old format
                padding_needed = (4 - len(credential_id) % 4) % 4
                if padding_needed:
                    padded_id = credential_id + ('=' * padding_needed)
                    cursor.execute('''
                        SELECT * FROM passkey_credentials WHERE credential_id = ?
                    ''', (padded_id,))
                    cred = cursor.fetchone()

            if cred:
                result = dict(cred)
                if result.get('transports'):
                    result['transports'] = json.loads(result['transports'])
                return result
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

            credentials = cursor.fetchall()
            results = []
            for cred in credentials:
                result = dict(cred)
                if result.get('transports'):
                    result['transports'] = json.loads(result['transports'])
                results.append(result)
            return results

    def update_passkey_sign_count(self, credential_id: str, sign_count: int):
        """
        Update passkey sign count and last used timestamp.

        Handles both padded and unpadded base64url encoding for backward compatibility.
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            # Try unpadded first
            cursor.execute('''
                UPDATE passkey_credentials
                SET sign_count = ?, last_used_at = ?
                WHERE credential_id = ?
            ''', (sign_count, datetime.now(), credential_id))

            # If no rows updated, try with padding for backward compatibility
            if cursor.rowcount == 0:
                padding_needed = (4 - len(credential_id) % 4) % 4
                if padding_needed:
                    padded_id = credential_id + ('=' * padding_needed)
                    cursor.execute('''
                        UPDATE passkey_credentials
                        SET sign_count = ?, last_used_at = ?
                        WHERE credential_id = ?
                    ''', (sign_count, datetime.now(), padded_id))

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

    def invalidate_all_user_passkeys(self, user_id: str):
        """Invalidate all passkeys for a user (used during email recovery)"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                DELETE FROM passkey_credentials WHERE user_id = ?
            ''', (user_id,))
            conn.commit()

    # Challenge management
    def create_challenge(self, user_id: str = None, expires_minutes: int = 15) -> tuple[str, str]:
        """Create a new WebAuthn challenge"""
        challenge_id = f"challenge_{secrets.token_urlsafe(16)}"
        challenge = secrets.token_urlsafe(32)
        expires_at = datetime.now() + timedelta(minutes=expires_minutes)

        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO passkey_challenges (id, challenge, user_id, expires_at)
                VALUES (?, ?, ?, ?)
            ''', (challenge_id, challenge, user_id, expires_at))
            conn.commit()

        return challenge_id, challenge

    def get_challenge(self, challenge_id: str) -> Optional[Dict[str, Any]]:
        """Get and validate a challenge"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()

            cursor.execute('''
                SELECT * FROM passkey_challenges
                WHERE id = ? AND expires_at > ? AND used = FALSE
            ''', (challenge_id, datetime.now()))

            challenge = cursor.fetchone()
            return dict(challenge) if challenge else None

    def mark_challenge_used(self, challenge_id: str):
        """Mark a challenge as used"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE passkey_challenges SET used = TRUE WHERE id = ?
            ''', (challenge_id,))
            conn.commit()

    def cleanup_expired_challenges(self):
        """Remove expired challenges"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                DELETE FROM passkey_challenges WHERE expires_at < ?
            ''', (datetime.now(),))
            conn.commit()

    # Session management (with sliding expiration)
    def create_session(self, user_id: str) -> str:
        """Create a new session with sliding expiration"""
        session_id = f"session_{secrets.token_urlsafe(16)}"
        session_token = secrets.token_urlsafe(64)

        # 7 days absolute timeout
        expires_at = datetime.now() + timedelta(days=7)

        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO passkey_sessions (id, user_id, session_token, expires_at, created_at, last_active_at)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (session_id, user_id, session_token, expires_at, datetime.now(), datetime.now()))
            conn.commit()

        return session_token

    def validate_session(self, session_token: str) -> Optional[Dict[str, Any]]:
        """Validate session and return user info (with sliding expiration)"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()

            # Check absolute timeout (7 days)
            cursor.execute('''
                SELECT s.*, u.email
                FROM passkey_sessions s
                JOIN users u ON s.user_id = u.id
                WHERE s.session_token = ? AND s.expires_at > ? AND u.is_active = TRUE
            ''', (session_token, datetime.now()))

            session = cursor.fetchone()
            if not session:
                return None

            session_dict = dict(session)

            # Check idle timeout (24 hours)
            last_active = datetime.fromisoformat(session_dict['last_active_at'])
            idle_timeout = last_active + timedelta(hours=24)

            if datetime.now() > idle_timeout:
                # Session expired due to inactivity
                cursor.execute('DELETE FROM passkey_sessions WHERE id = ?', (session_dict['id'],))
                conn.commit()
                return None

            # Update last_active_at (sliding expiration)
            cursor.execute('''
                UPDATE passkey_sessions SET last_active_at = ? WHERE id = ?
            ''', (datetime.now(), session_dict['id']))
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

    # Recovery code management
    def generate_recovery_codes(self, user_id: str, count: int = 8) -> List[str]:
        """Generate recovery codes for a user"""
        codes = []

        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            # Delete any existing recovery codes
            cursor.execute('DELETE FROM recovery_codes WHERE user_id = ?', (user_id,))

            for _ in range(count):
                # Generate 24-character code (128-bit entropy)
                code = secrets.token_urlsafe(18)[:24]
                code_hash = hashlib.sha256(code.encode()).hexdigest()

                code_id = f"recovery_{secrets.token_urlsafe(8)}"
                cursor.execute('''
                    INSERT INTO recovery_codes (id, user_id, code_hash, created_at)
                    VALUES (?, ?, ?, ?)
                ''', (code_id, user_id, code_hash, datetime.now()))

                codes.append(code)

            conn.commit()

        return codes

    def verify_recovery_code(self, user_id: str, code: str) -> tuple[bool, int]:
        """Verify a recovery code and mark it as used. Returns (success, remaining_codes)"""
        code_hash = hashlib.sha256(code.encode()).hexdigest()

        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()

            # Find unused code
            cursor.execute('''
                SELECT * FROM recovery_codes
                WHERE user_id = ? AND code_hash = ? AND used = FALSE
            ''', (user_id, code_hash))

            recovery_code = cursor.fetchone()

            if recovery_code:
                # Mark as used
                cursor.execute('''
                    UPDATE recovery_codes
                    SET used = TRUE, used_at = ?
                    WHERE id = ?
                ''', (datetime.now(), recovery_code['id']))

                # Count remaining codes
                cursor.execute('''
                    SELECT COUNT(*) as count FROM recovery_codes
                    WHERE user_id = ? AND used = FALSE
                ''', (user_id,))
                remaining = cursor.fetchone()['count']

                conn.commit()
                return True, remaining

            return False, 0

    def get_remaining_recovery_codes(self, user_id: str) -> int:
        """Get count of remaining unused recovery codes"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT COUNT(*) as count FROM recovery_codes
                WHERE user_id = ? AND used = FALSE
            ''', (user_id,))
            return cursor.fetchone()[0]

    # Recovery attempt rate limiting
    def log_recovery_attempt(self, user_id: str, success: bool, ip_address: str = None):
        """Log a recovery code attempt"""
        attempt_id = f"attempt_{secrets.token_urlsafe(8)}"

        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO recovery_attempts (id, user_id, attempted_at, success, ip_address)
                VALUES (?, ?, ?, ?, ?)
            ''', (attempt_id, user_id, datetime.now(), success, ip_address))
            conn.commit()

    def check_rate_limit(self, user_id: str, max_attempts: int = 5, window_hours: int = 1) -> tuple[bool, int]:
        """Check if user is rate limited. Returns (is_limited, seconds_until_reset)"""
        cutoff_time = datetime.now() - timedelta(hours=window_hours)

        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            # Count failed attempts in window
            cursor.execute('''
                SELECT COUNT(*) as count, MIN(attempted_at) as first_attempt
                FROM recovery_attempts
                WHERE user_id = ? AND success = FALSE AND attempted_at > ?
            ''', (user_id, cutoff_time))

            result = cursor.fetchone()
            count = result[0]
            first_attempt = result[1]

            if count >= max_attempts and first_attempt:
                # Calculate seconds until rate limit expires
                first_attempt_dt = datetime.fromisoformat(first_attempt)
                reset_time = first_attempt_dt + timedelta(hours=window_hours)
                seconds_until_reset = int((reset_time - datetime.now()).total_seconds())
                return True, max(seconds_until_reset, 0)

            return False, 0

    # Email recovery tokens
    def create_email_recovery_token(self, user_id: str, expires_hours: int = 1) -> str:
        """Create email recovery token"""
        token_id = f"email_recovery_{secrets.token_urlsafe(16)}"
        token = secrets.token_urlsafe(32)
        expires_at = datetime.now() + timedelta(hours=expires_hours)

        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO email_recovery_tokens (id, user_id, token, expires_at)
                VALUES (?, ?, ?, ?)
            ''', (token_id, user_id, token, expires_at))
            conn.commit()

        return token

    def validate_email_recovery_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Validate email recovery token"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()

            cursor.execute('''
                SELECT * FROM email_recovery_tokens
                WHERE token = ? AND expires_at > ? AND used = FALSE
            ''', (token, datetime.now()))

            token_data = cursor.fetchone()
            return dict(token_data) if token_data else None

    def mark_email_recovery_token_used(self, token: str):
        """Mark email recovery token as used"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE email_recovery_tokens SET used = TRUE WHERE token = ?
            ''', (token,))
            conn.commit()

    # Thread management (for chat history)
    def create_thread(self, user_id: str, title: str) -> str:
        """Create a new chat thread"""
        thread_id = f"thread_{secrets.token_urlsafe(16)}"

        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO threads (id, user_id, title, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?)
            ''', (thread_id, user_id, title, datetime.now(), datetime.now()))
            conn.commit()

        return thread_id

    def get_user_threads(self, user_id: str, limit: int = 50) -> List[Dict[str, Any]]:
        """Get all threads for a user"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()

            cursor.execute('''
                SELECT * FROM threads
                WHERE user_id = ? AND is_archived = FALSE
                ORDER BY updated_at DESC
                LIMIT ?
            ''', (user_id, limit))

            threads = cursor.fetchall()
            return [dict(thread) for thread in threads]

    def add_message(self, thread_id: str, role: str, content: str, metadata: Dict[str, Any] = None) -> str:
        """Add a message to a thread"""
        message_id = f"msg_{secrets.token_urlsafe(16)}"

        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO messages (id, thread_id, role, content, metadata, created_at)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (message_id, thread_id, role, content,
                  json.dumps(metadata) if metadata else None, datetime.now()))

            # Update thread's updated_at
            cursor.execute('''
                UPDATE threads SET updated_at = ? WHERE id = ?
            ''', (datetime.now(), thread_id))

            conn.commit()

        return message_id

    def get_thread_messages(self, thread_id: str) -> List[Dict[str, Any]]:
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
            for msg in messages:
                msg_dict = dict(msg)
                if msg_dict.get('metadata'):
                    try:
                        msg_dict['metadata'] = json.loads(msg_dict['metadata'])
                    except json.JSONDecodeError:
                        msg_dict['metadata'] = {}
                result.append(msg_dict)

            return result

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

    def update_thread_from_chat_messages(self, thread_id: str, messages: List[Dict[str, Any]]) -> bool:
        """Update thread with chat messages from the current session"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            # Clear existing messages for this thread
            cursor.execute('DELETE FROM messages WHERE thread_id = ?', (thread_id,))

            # Add all messages
            for message in messages:
                message_id = f"msg_{int(datetime.now().timestamp() * 1000)}_{message.get('id', secrets.token_urlsafe(8))}"

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
db = PasskeyDatabaseManager()
