"""
Encryption utilities for wallet private keys
Uses Fernet symmetric encryption with key derivation from user_id
Chain-agnostic implementation
"""
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.backends import default_backend
import base64
import os
import logging

logger = logging.getLogger(__name__)


class EncryptionManager:
    """Manages encryption/decryption of wallet private keys"""

    def __init__(self):
        # Get master key from environment (generate if not exists)
        self.master_key = os.getenv('ENCRYPTION_MASTER_KEY')
        if not self.master_key:
            raise ValueError(
                "ENCRYPTION_MASTER_KEY not set in environment. "
                "Generate with: python -c 'from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())'"
            )

        # Fixed salt for key derivation (stored separately in production)
        self.salt = os.getenv('ENCRYPTION_SALT', 'tuxedo-agent-portfolios').encode()
        logger.info("EncryptionManager initialized successfully")

    def _derive_key(self, user_id: str) -> bytes:
        """Derive encryption key from master key + user_id"""
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=self.salt + user_id.encode(),
            iterations=100000,
            backend=default_backend()
        )
        key = base64.urlsafe_b64encode(kdf.derive(self.master_key.encode()))
        return key

    def encrypt(self, plaintext: str, user_id: str) -> str:
        """Encrypt private key for storage"""
        key = self._derive_key(user_id)
        fernet = Fernet(key)
        encrypted = fernet.encrypt(plaintext.encode())
        return encrypted.decode()

    def decrypt(self, encrypted: str, user_id: str) -> str:
        """Decrypt private key for use"""
        key = self._derive_key(user_id)
        fernet = Fernet(key)
        decrypted = fernet.decrypt(encrypted.encode())
        return decrypted.decode()
