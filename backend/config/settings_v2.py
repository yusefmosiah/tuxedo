"""
Unified Configuration System
Combines secrets, application config, and network registry.

Usage:
    from config.settings_v2 import settings, get_network

    # Get secrets
    api_key = settings.secrets.openai_api_key

    # Get app config
    port = settings.app.port

    # Get network config
    mainnet = get_network("stellar-mainnet")
    rpc_url = mainnet.get_rpc_url()
    contract = mainnet.get_contract_address("blend", "backstop")
"""

from typing import Optional
from .secrets import secrets
from .application import app_config
from .networks import network_registry, NetworkConfig


class UnifiedSettings:
    """Unified settings combining all config sources"""

    def __init__(self):
        self.secrets = secrets
        self.app = app_config
        self.networks = network_registry

        # Validate required secrets
        missing = self.secrets.validate_required()
        if missing:
            print(f"Warning: Missing required secrets: {', '.join(missing)}")

    def get_network(self, network_id: Optional[str] = None) -> NetworkConfig:
        """
        Get network configuration.

        Args:
            network_id: Network ID (e.g., "stellar-mainnet"). If None, uses default.

        Returns:
            NetworkConfig instance

        Raises:
            ValueError: If network not found
        """
        if network_id is None:
            network_id = self.app.default_network

        network = self.networks.get(network_id)
        if not network:
            available = self.networks.list_networks()
            raise ValueError(
                f"Network '{network_id}' not found. "
                f"Available networks: {', '.join(available)}"
            )

        return network

    # Backward compatibility helpers
    @property
    def openai_api_key(self) -> str:
        """Legacy: Use settings.secrets.openai_api_key"""
        return self.secrets.openai_api_key

    @property
    def openai_base_url(self) -> str:
        """Legacy: Use settings.app.openai_base_url"""
        return self.app.openai_base_url

    @property
    def primary_model(self) -> str:
        """Legacy: Use settings.app.primary_model"""
        return self.app.primary_model

    @property
    def port(self) -> int:
        """Legacy: Use settings.app.port"""
        return self.app.port

    @property
    def host(self) -> str:
        """Legacy: Use settings.app.host"""
        return self.app.host

    @property
    def debug(self) -> bool:
        """Legacy: Use settings.app.debug"""
        return self.app.debug

    @property
    def cors_origins(self) -> list:
        """Legacy: Use settings.app.cors_origins"""
        return self.app.cors_origins


# Global unified settings instance
settings = UnifiedSettings()


def get_network(network_id: Optional[str] = None) -> NetworkConfig:
    """
    Convenience function to get network config.

    Args:
        network_id: Network ID or None for default

    Returns:
        NetworkConfig instance
    """
    return settings.get_network(network_id)


def list_networks() -> list[str]:
    """List all available network IDs"""
    return settings.networks.list_networks()


def list_chains() -> list[str]:
    """List all supported blockchain chains"""
    return settings.networks.list_chains()
