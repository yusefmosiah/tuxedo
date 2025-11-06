"""
Database models for user accounts and chat thread persistence
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
        """Initialize the database with required tables"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            # Create users table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    id TEXT PRIMARY KEY,
                    email TEXT UNIQUE NOT NULL,
                    encrypted_private_key TEXT,
                    public_key TEXT UNIQUE,
                    stellar_public_key TEXT,
                    recovery_method TEXT DEFAULT 'email',
                    recovery_data TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_login TIMESTAMP,
                    is_active BOOLEAN DEFAULT TRUE
                )
            ''')

            # Passkey authentication tables
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
                    FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
                )
            ''')

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

            cursor.execute('''
                CREATE TABLE IF NOT EXISTS passkey_sessions (
                    id TEXT PRIMARY KEY,
                    user_id TEXT NOT NULL,
                    session_token TEXT UNIQUE NOT NULL,
                    expires_at TIMESTAMP NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
                )
            ''')

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

            # Create agents table (updated for multi-agent architecture)
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
                    FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
                )
            ''')

            # Update threads table to support agent-based architecture
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS threads (
                    id TEXT PRIMARY KEY,
                    user_id TEXT NOT NULL,
                    agent_id TEXT,
                    title TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    is_archived BOOLEAN DEFAULT FALSE,
                    FOREIGN KEY (user_id) REFERENCES users (id),
                    FOREIGN KEY (agent_id) REFERENCES agents (id) ON DELETE CASCADE
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
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_messages_thread_id ON messages (thread_id)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_threads_user_id ON threads (user_id)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_threads_agent_id ON threads (agent_id)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_threads_updated_at ON threads (updated_at DESC)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_agents_user_id ON agents (user_id)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_passkey_credentials_user_id ON passkey_credentials(user_id)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_passkey_credentials_credential_id ON passkey_credentials(credential_id)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_passkey_sessions_user_id ON passkey_sessions(user_id)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_passkey_sessions_token ON passkey_sessions (session_token)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_recovery_codes_user_id ON recovery_codes (user_id)')

            conn.commit()

    # Passkey session validation
    def validate_passkey_session(self, session_token: str) -> Optional[Dict[str, Any]]:
        """Validate passkey session token and return user info"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()

            cursor.execute('''
                SELECT ps.*, u.email, u.public_key, u.stellar_public_key
                FROM passkey_sessions ps
                JOIN users u ON ps.user_id = u.id
                WHERE ps.session_token = ? AND ps.expires_at > ? AND u.is_active = TRUE
            ''', (session_token, datetime.now()))

            session = cursor.fetchone()
            if not session:
                return None

            return dict(session)

    def get_user_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        """Get user by email"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()

            cursor.execute("SELECT * FROM users WHERE email = ?", (email,))
            user = cursor.fetchone()
            return dict(user) if user else None

    # Create user session (for backward compatibility)
    def create_user_session(self, user_id: str, days: int = 7) -> str:
        """Create an authenticated user session"""
        session_id = f"session_{secrets.token_urlsafe(32)}"
        session_token = secrets.token_urlsafe(64)
        expires_at = datetime.now() + timedelta(days=days)

        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO user_sessions (id, user_id, session_token, expires_at)
                VALUES (?, ?, ?, ?)
            ''', (session_id, user_id, session_token, expires_at))
            conn.commit()

        return session_token

    def validate_user_session(self, session_token: str) -> Optional[Dict[str, Any]]:
        """Validate user session token and return user info"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()

            cursor.execute('''
                SELECT us.*, u.email, u.public_key
                FROM user_sessions us
                JOIN users u ON us.user_id = u.id
                WHERE us.session_token = ? AND us.expires_at > ? AND u.is_active = TRUE
            ''', (session_token, datetime.now()))

            session = cursor.fetchone()
            if not session:
                return None

            # Update last accessed
            cursor.execute('''
                UPDATE user_sessions
                SET last_accessed = ?
                WHERE id = ?
            ''', (datetime.now(), session['id']))
            conn.commit()

            return dict(session)

    def create_or_get_user(self, email: str) -> Dict[str, Any]:
        """Create new user or get existing user by email"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()

            # Check if user exists
            cursor.execute('SELECT * FROM users WHERE email = ?', (email,))
            user = cursor.fetchone()

            if user:
                return dict(user)

            # Create new user
            user_id = f"user_{secrets.token_urlsafe(16)}"
            cursor.execute('''
                INSERT INTO users (id, email, recovery_method)
                VALUES (?, ?, ?)
            ''', (user_id, email, 'email'))
            conn.commit()

            cursor.execute('SELECT * FROM users WHERE id = ?', (user_id,))
            return dict(cursor.fetchone())

    # Updated thread methods to use user_id
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