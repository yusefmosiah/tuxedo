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

        # Stellar Network Configuration
        # Default network for read operations (queries, pool data, etc.)
        self.default_network = os.getenv("STELLAR_NETWORK", "mainnet")

        # Mainnet Configuration
        self.mainnet_horizon_url = os.getenv(
            "MAINNET_HORIZON_URL",
            "https://horizon.stellar.org"
        )
        self.mainnet_rpc_url = os.getenv(
            "ANKR_STELLER_RPC",  # Using Ankr RPC for mainnet
            os.getenv("MAINNET_SOROBAN_RPC_URL", "")  # Fallback to generic env var
        )
        self.mainnet_passphrase = "Public Global Stellar Network ; September 2015"

        # Testnet Configuration (used for account creation and testing)
        self.testnet_horizon_url = os.getenv(
            "TESTNET_HORIZON_URL",
            "https://horizon-testnet.stellar.org"
        )
        self.testnet_rpc_url = os.getenv(
            "TESTNET_SOROBAN_RPC_URL",
            "https://soroban-testnet.stellar.org"
        )
        self.testnet_passphrase = "Test SDF Network ; September 2015"
        self.friendbot_url = os.getenv(
            "FRIENDBOT_URL",
            "https://friendbot.stellar.org"
        )

        # Legacy configuration (for backward compatibility)
        # These will be removed once all code uses get_network_config()
        self.stellar_network = self.default_network
        self.horizon_url = os.getenv("HORIZON_URL", self.testnet_horizon_url)
        self.soroban_rpc_url = os.getenv("SOROBAN_RPC_URL", self.testnet_rpc_url)

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

    def get_network_config(self, network: Optional[str] = None) -> dict:
        """
        Get configuration for specified network.

        Args:
            network: "mainnet" or "testnet". If None, uses default_network.

        Returns:
            dict with horizon_url, rpc_url, and passphrase for the network

        Raises:
            ValueError: If mainnet RPC URL is not configured
        """
        net = network or self.default_network

        if net == "mainnet":
            if not self.mainnet_rpc_url:
                raise ValueError(
                    "Mainnet RPC URL not configured. "
                    "Please set ANKR_STELLER_RPC or MAINNET_SOROBAN_RPC_URL environment variable."
                )
            return {
                'network': 'mainnet',
                'horizon_url': self.mainnet_horizon_url,
                'rpc_url': self.mainnet_rpc_url,
                'passphrase': self.mainnet_passphrase,
            }
        else:  # testnet
            return {
                'network': 'testnet',
                'horizon_url': self.testnet_horizon_url,
                'rpc_url': self.testnet_rpc_url,
                'passphrase': self.testnet_passphrase,
            }

# Create global settings instance
settings = Settings()
