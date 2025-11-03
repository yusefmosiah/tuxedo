"""
Application Configuration
Centralized configuration management using Pydantic settings.
"""

from pydantic import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    """Application settings"""

    # API Configuration
    openai_api_key: str
    openai_base_url: str = "https://api.redpill.ai/v1"
    primary_model: str = "deepseek/deepseek-v3.1-terminus:exacto"

    # Stellar Configuration
    stellar_network: str = "testnet"
    horizon_url: str = "https://horizon-testnet.stellar.org"
    soroban_rpc_url: str = "https://soroban-testnet.stellar.org"
    friendbot_url: str = "https://friendbot.stellar.org"

    # Agent Configuration
    max_accounts_per_agent: int = 10
    default_account_funding: float = 10000  # stroops
    agent_conversation_limit: int = 100

    # Server Configuration
    host: str = "0.0.0.0"
    port: int = 8000
    debug: bool = False
    cors_origins: list = [
        "http://localhost:5173",
        "http://localhost:3000",
        "https://tuxedo.onrender.com",
        "https://tuxedo-frontend.onrender.com"
    ]

    # Security Configuration
    encryption_key_path: str = ".encryption_key"
    keystore_path: str = ".agent_keystore.json"

    class Config:
        env_file = ".env"
        case_sensitive = False

# Create global settings instance
settings = Settings()