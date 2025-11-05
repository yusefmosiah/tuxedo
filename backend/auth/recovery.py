"""
Recovery Code System for Passkey Authentication
Generate and validate backup recovery codes
"""

import secrets
import hashlib
import sqlite3
from datetime import datetime
from typing import List, Optional


class RecoveryCodeService:
    """Generate and validate recovery codes"""

    CODE_LENGTH = 16
    NUM_CODES = 8

    @staticmethod
    def generate_codes() -> List[str]:
        """Generate 8 recovery codes"""
        codes = []
        for _ in range(RecoveryCodeService.NUM_CODES):
            # Format: XXXX-XXXX-XXXX-XXXX
            code = secrets.token_hex(8).upper()
            formatted = f"{code[0:4]}-{code[4:8]}-{code[8:12]}-{code[12:16]}"
            codes.append(formatted)
        return codes

    @staticmethod
    def hash_code(code: str) -> str:
        """Hash recovery code for storage"""
        clean_code = code.replace("-", "")
        return hashlib.sha256(clean_code.encode()).hexdigest()

    @staticmethod
    async def store_codes(db, user_id: str, codes: List[str]):
        """Store hashed recovery codes in database"""
        for code in codes:
            code_hash = RecoveryCodeService.hash_code(code)
            code_id = f"rc_{secrets.token_urlsafe(16)}"

            # Use direct database connection for simplicity
            # In production, this should use async database operations
            conn = sqlite3.connect(db.db_path)
            try:
                conn.execute(
                    """INSERT INTO recovery_codes (id, user_id, code_hash)
                       VALUES (?, ?, ?)""",
                    (code_id, user_id, code_hash)
                )
                conn.commit()
            finally:
                conn.close()

    @staticmethod
    async def validate_code(db, user_id: str, code: str) -> bool:
        """Validate and mark recovery code as used"""
        code_hash = RecoveryCodeService.hash_code(code)

        conn = sqlite3.connect(db.db_path)
        try:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()

            result = cursor.execute(
                """SELECT id FROM recovery_codes
                   WHERE user_id = ? AND code_hash = ? AND used = FALSE""",
                (user_id, code_hash)
            )

            row = result.fetchone()
            if not row:
                return False

            # Mark as used
            cursor.execute(
                """UPDATE recovery_codes SET used = TRUE, used_at = CURRENT_TIMESTAMP
                   WHERE id = ?""",
                (row['id'],)
            )
            conn.commit()
            return True
        finally:
            conn.close()

    @staticmethod
    async def get_remaining_count(db, user_id: str) -> int:
        """Get count of unused recovery codes"""
        conn = sqlite3.connect(db.db_path)
        try:
            cursor = conn.cursor()
            result = cursor.execute(
                """SELECT COUNT(*) as count FROM recovery_codes
                   WHERE user_id = ? AND used = FALSE""",
                (user_id,)
            )
            return result.fetchone()[0]
        finally:
            conn.close()

    @staticmethod
    def format_codes_for_display(codes: List[str]) -> str:
        """Format codes for user display (e.g., PDF download)"""
        formatted = "RECOVERY CODES - SAVE THESE SECURELY\n"
        formatted += "=" * 40 + "\n\n"

        for i, code in enumerate(codes, 1):
            formatted += f"{i}. {code}\n"

        formatted += "\n" + "=" * 40 + "\n"
        formatted += "Each code can only be used once.\n"
        formatted += "Store these in a secure location.\n"

        return formatted