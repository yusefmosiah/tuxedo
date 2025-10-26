"""
Database models for chat thread persistence
"""
import sqlite3
from datetime import datetime
from typing import List, Optional, Dict, Any
import json

class DatabaseManager:
    def __init__(self, db_path: str = "chat_threads.db"):
        self.db_path = db_path
        self.init_database()

    def init_database(self):
        """Initialize the database with required tables"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            # Create threads table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS threads (
                    id TEXT PRIMARY KEY,
                    title TEXT NOT NULL,
                    wallet_address TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    is_archived BOOLEAN DEFAULT FALSE
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
                CREATE INDEX IF NOT EXISTS idx_messages_thread_id
                ON messages (thread_id)
            ''')

            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_threads_wallet_address
                ON threads (wallet_address)
            ''')

            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_threads_updated_at
                ON threads (updated_at DESC)
            ''')

            conn.commit()

    def create_thread(self, title: str, wallet_address: Optional[str] = None) -> str:
        """Create a new chat thread"""
        thread_id = f"thread_{int(datetime.now().timestamp() * 1000)}"

        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO threads (id, title, wallet_address, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?)
            ''', (thread_id, title, wallet_address, datetime.now(), datetime.now()))
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

    def get_threads(self, wallet_address: Optional[str] = None, limit: int = 50) -> List[Dict[str, Any]]:
        """Get all threads for a wallet, sorted by updated_at"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()

            if wallet_address:
                cursor.execute('''
                    SELECT * FROM threads
                    WHERE wallet_address = ? AND is_archived = FALSE
                    ORDER BY updated_at DESC
                    LIMIT ?
                ''', (wallet_address, limit))
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