"""
Base interface for blockchain interactions
All chain implementations must follow this interface
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
from dataclasses import dataclass

@dataclass
class ChainKeypair:
    """Chain-agnostic keypair representation"""
    public_key: str
    private_key: str
    chain: str
    metadata: Optional[Dict[str, Any]] = None

@dataclass
class ChainAccount:
    """Chain-agnostic account representation"""
    address: str
    chain: str
    balance: float
    balances: List[Dict[str, Any]]  # For multi-asset chains

class ChainAdapter(ABC):
    """Abstract base class for chain-specific implementations"""

    @property
    @abstractmethod
    def chain_name(self) -> str:
        """Returns chain identifier (e.g., 'stellar', 'solana', 'ethereum')"""
        pass

    @abstractmethod
    def generate_keypair(self) -> ChainKeypair:
        """Generate new keypair for this chain"""
        pass

    @abstractmethod
    def import_keypair(self, private_key: str) -> ChainKeypair:
        """Import existing keypair from private key"""
        pass

    @abstractmethod
    def export_keypair(self, keypair: ChainKeypair) -> str:
        """Export keypair in chain-specific format"""
        pass

    @abstractmethod
    def validate_address(self, address: str) -> bool:
        """Validate if address is valid for this chain"""
        pass

    @abstractmethod
    def get_account(self, address: str) -> ChainAccount:
        """Get account information from blockchain"""
        pass

    @abstractmethod
    def get_balance(self, address: str) -> float:
        """Get native token balance"""
        pass
