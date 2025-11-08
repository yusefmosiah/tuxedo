"""
Stellar blockchain adapter
Migrates existing KeyManager functionality to chain-agnostic interface
"""
from stellar_sdk import Keypair, Server
from typing import Dict, Any, Optional
from .base import ChainAdapter, ChainKeypair, ChainAccount

class StellarAdapter(ChainAdapter):
    """Stellar blockchain implementation"""

    def __init__(self, network: str = "testnet"):
        self.network = network
        if network == "testnet":
            self.horizon_url = "https://horizon-testnet.stellar.org"
        else:
            self.horizon_url = "https://horizon.stellar.org"
        self.server = Server(self.horizon_url)

    @property
    def chain_name(self) -> str:
        return "stellar"

    def generate_keypair(self) -> ChainKeypair:
        """Generate new Stellar keypair"""
        keypair = Keypair.random()
        return ChainKeypair(
            public_key=keypair.public_key,
            private_key=keypair.secret,
            chain=self.chain_name,
            metadata={"network": self.network}
        )

    def import_keypair(self, private_key: str) -> ChainKeypair:
        """Import Stellar keypair from secret key"""
        keypair = Keypair.from_secret(private_key)
        return ChainKeypair(
            public_key=keypair.public_key,
            private_key=keypair.secret,
            chain=self.chain_name,
            metadata={"network": self.network}
        )

    def export_keypair(self, keypair: ChainKeypair) -> str:
        """Export keypair in Stellar format (secret key)"""
        return keypair.private_key

    def validate_address(self, address: str) -> bool:
        """Validate Stellar public key"""
        try:
            Keypair.from_public_key(address)
            return True
        except Exception:
            return False

    def get_account(self, address: str) -> ChainAccount:
        """Get Stellar account information"""
        try:
            account = self.server.load_account(address)
            balances = account.raw_data.get('balances', [])
            native_balance = 0

            for bal in balances:
                if bal.get('asset_type') == 'native':
                    native_balance = float(bal.get('balance', 0))

            return ChainAccount(
                address=address,
                chain=self.chain_name,
                balance=native_balance,
                balances=balances
            )
        except Exception as e:
            raise ValueError(f"Failed to load Stellar account: {e}")

    def get_balance(self, address: str) -> float:
        """Get XLM balance"""
        account = self.get_account(address)
        return account.balance
