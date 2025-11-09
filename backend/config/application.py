"""
Application Configuration
Non-secret application settings that can be version-controlled.
"""

import os
from typing import List


class AppConfig:
    """Application configuration (non-secrets)"""

    def __init__(self):
        # AI Model Configuration
        self.openai_base_url = os.getenv(
            "OPENAI_BASE_URL",
            "https://openrouter.ai/api/v1"
        )
        self.primary_model = os.getenv(
            "PRIMARY_MODEL",
            "openai/gpt-oss-120b:exacto"
        )
        self.summarization_model = os.getenv(
            "SUMMARIZATION_MODEL",
            "openai/gpt-oss-120b:exacto"
        )

        # Network Selection
        # Which network to use by default for queries
        self.default_network = os.getenv("DEFAULT_NETWORK", "stellar-mainnet")

        # Server Configuration
        self.host = os.getenv("HOST", "0.0.0.0")
        self.port = int(os.getenv("PORT", "8000"))
        self.debug = os.getenv("DEBUG", "false").lower() == "true"
        self.log_level = os.getenv("LOG_LEVEL", "info")

        # CORS Configuration
        cors_origins_env = os.getenv("CORS_ORIGINS")
        if cors_origins_env:
            # Parse JSON array from env
            import json
            try:
                self.cors_origins = json.loads(cors_origins_env)
            except:
                self.cors_origins = [cors_origins_env]
        else:
            # Default CORS origins
            self.cors_origins = [
                "http://localhost:5173",
                "http://localhost:3000",
                "https://tuxedo.onrender.com",
                "https://tuxedo-frontend.onrender.com",
            ]

        # Agent Configuration
        self.max_accounts_per_agent = int(
            os.getenv("MAX_ACCOUNTS_PER_AGENT", "10")
        )
        self.default_account_funding = float(
            os.getenv("DEFAULT_ACCOUNT_FUNDING", "10000")
        )
        self.agent_conversation_limit = int(
            os.getenv("AGENT_CONVERSATION_LIMIT", "100")
        )

        # Feature Flags
        self.enable_testnet = os.getenv("ENABLE_TESTNET", "true").lower() == "true"
        self.enable_mainnet = os.getenv("ENABLE_MAINNET", "true").lower() == "true"
        self.enable_account_creation = os.getenv(
            "ENABLE_ACCOUNT_CREATION", "true"
        ).lower() == "true"

        # Storage Configuration
        self.keystore_path = os.getenv("KEYSTORE_PATH", ".agent_keystore.json")
        self.encryption_key_path = os.getenv("ENCRYPTION_KEY_PATH", ".encryption_key")


# Global app config instance
app_config = AppConfig()
