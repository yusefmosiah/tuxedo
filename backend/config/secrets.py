"""
Secrets Management
Loads secrets from environment variables only.
NEVER commit this file's values to git.
"""

import os
from typing import Optional


class Secrets:
    """Secrets loaded from environment variables"""

    def __init__(self):
        # AI Service Secrets
        self.openai_api_key = os.getenv("OPENAI_API_KEY", "")

        # RPC API Keys (for services requiring authentication)
        self.ankr_stellar_rpc = os.getenv("ANKR_STELLER_RPC")

        # Encryption Secrets
        self.encryption_master_key = os.getenv("ENCRYPTION_MASTER_KEY")
        self.encryption_salt = os.getenv("ENCRYPTION_SALT", "tuxedo-agent-accounts-v1")

        # Database Secrets (for future use)
        self.database_url = os.getenv("DATABASE_URL")
        self.database_password = os.getenv("DATABASE_PASSWORD")

        # Optional: External Service Keys
        self.defindex_api_key = os.getenv("DEFINDEX_API_KEY")
        self.render_api_key = os.getenv("RENDER_API_KEY")

    def validate_required(self) -> list[str]:
        """Check if required secrets are set, return list of missing ones"""
        missing = []

        if not self.openai_api_key:
            missing.append("OPENAI_API_KEY")

        if not self.encryption_master_key:
            missing.append("ENCRYPTION_MASTER_KEY")

        return missing


# Global secrets instance
secrets = Secrets()
