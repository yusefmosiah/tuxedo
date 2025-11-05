"""
Key Derivation for Passkey Authentication
Handles both PRF-based and server-based key derivation for Stellar accounts
"""

import secrets
import hashlib
import os
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from stellar_sdk.keypair import Keypair


class KeyDerivation:
    """Handles both PRF-based and server-based key derivation"""

    @staticmethod
    def derive_from_prf(prf_output: bytes, user_id: str) -> Keypair:
        """Derive Stellar keypair from WebAuthn PRF extension"""
        hkdf = HKDF(
            algorithm=hashes.SHA256(),
            length=32,
            salt=b'tuxedo-prf-v1',
            info=user_id.encode()
        )
        seed = hkdf.derive(prf_output)
        return Keypair.from_raw_ed25519_seed(seed)

    @staticmethod
    def derive_from_server(user_id: str, credential_id: str, server_secret: bytes) -> Keypair:
        """Fallback: Server-side deterministic derivation (no PRF)"""
        # Deterministic but server-dependent
        material = f"{user_id}:{credential_id}".encode()

        hkdf = HKDF(
            algorithm=hashes.SHA256(),
            length=32,
            salt=server_secret,  # From environment
            info=b'tuxedo-fallback-v1'
        )
        seed = hkdf.derive(material)
        return Keypair.from_raw_ed25519_seed(seed)

    @staticmethod
    def generate_agent_keypair(user_keypair: Keypair, agent_index: int) -> Keypair:
        """Derive agent keypairs from user's master keypair"""
        # Agent accounts derived from user account
        material = user_keypair.secret.raw_seed() + agent_index.to_bytes(4, 'big')

        seed = hashlib.sha256(material).digest()
        return Keypair.from_raw_ed25519_seed(seed)

    @staticmethod
    def get_server_secret() -> bytes:
        """Get or create server secret for fallback derivation"""
        # Store server secret in environment or generate one
        secret = os.environ.get('TUXEDO_SERVER_SECRET')
        if secret:
            return secret.encode()

        # Generate and store a new secret (in production, this should be more secure)
        new_secret = secrets.token_bytes(32)
        print("WARNING: Generated new server secret. Set TUXEDO_SERVER_SECRET environment variable for persistence.")
        return new_secret