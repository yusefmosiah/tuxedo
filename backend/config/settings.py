"""
Application Configuration
Simplified configuration using environment variables.
"""

import os
from typing import Optional

class Settings:
    """Simple settings class using environment variables"""

    def __init__(self):
        # API Configuration
        self.openai_api_key = os.getenv("OPENAI_API_KEY", "")
        self.openai_base_url = os.getenv("OPENAI_BASE_URL", "https://openrouter.ai/api/v1")
        self.primary_model = os.getenv("PRIMARY_MODEL", "openai/gpt-oss-120b:exacto")
        self.summarization_model = os.getenv("SUMMARIZATION_MODEL", "openai/gpt-oss-120b:exacto")

        # Stellar Network Configuration - MAINNET ONLY
        self.stellar_network = "mainnet"

        # Mainnet Configuration
        self.horizon_url = os.getenv(
            "MAINNET_HORIZON_URL",
            "https://horizon.stellar.org"
        )
        self.soroban_rpc_url = os.getenv(
            "ANKR_STELLER_RPC",
            os.getenv("MAINNET_SOROBAN_RPC_URL", "https://rpc.ankr.com/stellar_soroban")
        )
        self.network_passphrase = "Public Global Stellar Network ; September 2015"

        # Agent Configuration
        self.max_accounts_per_agent = int(os.getenv("MAX_ACCOUNTS_PER_AGENT", "10"))
        self.default_account_funding = float(os.getenv("DEFAULT_ACCOUNT_FUNDING", "10000"))
        self.agent_conversation_limit = int(os.getenv("AGENT_CONVERSATION_LIMIT", "100"))

        # Server Configuration
        self.host = os.getenv("HOST", "0.0.0.0")
        self.port = int(os.getenv("PORT", "8000"))
        self.debug = os.getenv("DEBUG", "false").lower() == "true"
        self.cors_origins = [
            "http://localhost:5173",
            "http://localhost:3000",
            "https://tuxedo.onrender.com",
            "https://tuxedo-frontend.onrender.com"
        ]

        # Security Configuration
        self.encryption_key_path = os.getenv("ENCRYPTION_KEY_PATH", ".encryption_key")
        self.keystore_path = os.getenv("KEYSTORE_PATH", ".agent_keystore.json")

    def get_network_config(self) -> dict:
        """
        Get mainnet configuration (mainnet-only system).

        Returns:
            dict with horizon_url, rpc_url, and passphrase for mainnet

        Raises:
            ValueError: If mainnet RPC URL is not configured
        """
        if not self.soroban_rpc_url:
            raise ValueError(
                "Mainnet RPC URL not configured. "
                "Please set ANKR_STELLER_RPC or MAINNET_SOROBAN_RPC_URL environment variable."
            )
        return {
            'network': 'mainnet',
            'horizon_url': self.horizon_url,
            'rpc_url': self.soroban_rpc_url,
            'passphrase': self.network_passphrase,
        }

# Create global settings instance
settings = Settings()
