"""
Network Configuration Manager
Loads network configs from JSON files, supporting multiple chains and networks.
"""

import json
import os
from pathlib import Path
from typing import Dict, Optional, List


class NetworkConfig:
    """Configuration for a specific network"""

    def __init__(self, config_dict: dict):
        self.network_id: str = config_dict["network_id"]
        self.chain: str = config_dict["chain"]
        self.name: str = config_dict["name"]
        self.description: str = config_dict["description"]
        self.enabled: bool = config_dict.get("enabled", True)

        # RPC/Horizon URLs
        self.horizon_url: str = config_dict["horizon_url"]
        self.rpc_url_public: Optional[str] = config_dict.get("rpc_url_public")
        self.rpc_url_env_key: Optional[str] = config_dict.get("rpc_url_env_key")

        # Network identifiers
        self.passphrase: str = config_dict["passphrase"]
        self.explorer_url: str = config_dict.get("explorer_url", "")
        self.friendbot_url: Optional[str] = config_dict.get("friendbot_url")

        # Contracts and tokens
        self.contracts: Dict = config_dict.get("contracts", {})
        self.tokens: Dict = config_dict.get("tokens", {})
        self.features: Dict = config_dict.get("features", {})

    def get_rpc_url(self) -> str:
        """Get RPC URL, checking env var first if specified"""
        if self.rpc_url_env_key:
            env_url = os.getenv(self.rpc_url_env_key)
            if env_url:
                return env_url

        if self.rpc_url_public:
            return self.rpc_url_public

        raise ValueError(
            f"No RPC URL configured for {self.network_id}. "
            f"Set {self.rpc_url_env_key} environment variable or configure rpc_url_public."
        )

    def get_contract_address(self, protocol: str, contract_name: str) -> Optional[str]:
        """Get contract address for a protocol"""
        return self.contracts.get(protocol, {}).get(contract_name)

    def supports_feature(self, feature: str) -> bool:
        """Check if network supports a feature"""
        return self.features.get(feature, False)


class NetworkRegistry:
    """Registry of all available networks"""

    def __init__(self, config_dir: Optional[Path] = None):
        if config_dir is None:
            config_dir = Path(__file__).parent / "networks"

        self.config_dir = config_dir
        self.networks: Dict[str, NetworkConfig] = {}
        self._load_networks()

    def _load_networks(self):
        """Load all network configs from JSON files"""
        if not self.config_dir.exists():
            return

        for config_file in self.config_dir.glob("*.json"):
            try:
                with open(config_file, 'r') as f:
                    config_dict = json.load(f)
                    network_config = NetworkConfig(config_dict)
                    self.networks[network_config.network_id] = network_config
            except Exception as e:
                print(f"Warning: Failed to load network config {config_file}: {e}")

    def get(self, network_id: str) -> Optional[NetworkConfig]:
        """Get network config by ID"""
        return self.networks.get(network_id)

    def get_by_chain(self, chain: str) -> List[NetworkConfig]:
        """Get all networks for a specific chain"""
        return [
            net for net in self.networks.values()
            if net.chain == chain and net.enabled
        ]

    def list_networks(self) -> List[str]:
        """List all available network IDs"""
        return [net.network_id for net in self.networks.values() if net.enabled]

    def list_chains(self) -> List[str]:
        """List all supported chains"""
        return list(set(net.chain for net in self.networks.values()))


# Global registry instance
network_registry = NetworkRegistry()
