"""
Vault Manager - Python interface for TuxedoVault smart contract
Handles user deposits, withdrawals, and agent strategy execution
"""

import os
from typing import Dict, Optional
from stellar_sdk import (
    SorobanServer,
    Keypair,
    TransactionBuilder,
    Network,
    scval,
    Address,
    Asset,
    Server,
)
from stellar_sdk.soroban_rpc import GetTransactionStatus
from stellar_sdk.exceptions import NotFoundError

from config.settings import Settings

settings = Settings()


class VaultManager:
    """Manager for TuxedoVault contract interactions"""

    def __init__(self, contract_id: str, agent_keypair: Keypair):
        """
        Initialize VaultManager

        Args:
            contract_id: The deployed vault contract address
            agent_keypair: The agent's Stellar keypair for signing transactions
        """
        self.contract_id = contract_id
        self.agent = agent_keypair
        self.server = SorobanServer(settings.ANKR_STELLER_RPC)
        self.horizon = Server(settings.MAINNET_HORIZON_URL)
        self.network = Network.PUBLIC_NETWORK_PASSPHRASE

    async def deposit_to_vault(
        self, user_address: str, amount: int, user_keypair: Optional[Keypair] = None
    ) -> Dict:
        """
        User deposits USDC to vault and receives TUX0 shares

        Args:
            user_address: User's Stellar address
            amount: Amount of USDC to deposit (with 7 decimals)
            user_keypair: User's keypair for signing (if available)

        Returns:
            dict: Transaction result with shares minted
        """
        try:
            # Build deposit transaction
            source_account = self.server.load_account(user_address)

            # Create contract function call
            tx = (
                TransactionBuilder(
                    source_account=source_account,
                    network_passphrase=self.network,
                    base_fee=100000,
                )
                .append_invoke_contract_function_op(
                    contract_id=self.contract_id,
                    function_name="deposit",
                    parameters=[
                        scval.to_address(user_address),  # user
                        scval.to_int128(amount),  # amount
                    ],
                )
                .set_timeout(300)
                .build()
            )

            # Prepare transaction (get footprint)
            prepared_tx = self.server.prepare_transaction(tx)

            if user_keypair:
                # Sign with user keypair if provided
                prepared_tx.sign(user_keypair)
                response = self.server.send_transaction(prepared_tx)

                return {
                    "status": "success",
                    "tx_hash": response.hash,
                    "message": f"Deposit of {amount / 1e7} USDC initiated",
                }
            else:
                # Return unsigned transaction for user to sign
                return {
                    "status": "needs_signature",
                    "unsigned_tx": prepared_tx.to_xdr(),
                    "message": "Transaction ready for user signature",
                }

        except Exception as e:
            return {"status": "error", "message": str(e)}

    async def withdraw_from_vault(
        self, user_address: str, shares: int, user_keypair: Optional[Keypair] = None
    ) -> Dict:
        """
        User burns TUX0 shares and withdraws USDC

        Args:
            user_address: User's Stellar address
            shares: Number of shares to burn (with 7 decimals)
            user_keypair: User's keypair for signing (if available)

        Returns:
            dict: Transaction result with assets withdrawn
        """
        try:
            # Build withdraw transaction
            source_account = self.server.load_account(user_address)

            tx = (
                TransactionBuilder(
                    source_account=source_account,
                    network_passphrase=self.network,
                    base_fee=100000,
                )
                .append_invoke_contract_function_op(
                    contract_id=self.contract_id,
                    function_name="withdraw",
                    parameters=[
                        scval.to_address(user_address),  # user
                        scval.to_int128(shares),  # shares
                    ],
                )
                .set_timeout(300)
                .build()
            )

            # Prepare transaction
            prepared_tx = self.server.prepare_transaction(tx)

            if user_keypair:
                prepared_tx.sign(user_keypair)
                response = self.server.send_transaction(prepared_tx)

                return {
                    "status": "success",
                    "tx_hash": response.hash,
                    "message": f"Withdrawal of {shares / 1e7} TUX0 initiated",
                }
            else:
                return {
                    "status": "needs_signature",
                    "unsigned_tx": prepared_tx.to_xdr(),
                    "message": "Transaction ready for user signature",
                }

        except Exception as e:
            return {"status": "error", "message": str(e)}

    async def agent_execute_strategy(
        self, strategy: str, pool: str, asset: str, amount: int
    ) -> Dict:
        """
        Agent executes a yield strategy (Blend supply/withdraw)

        Args:
            strategy: "supply" or "withdraw"
            pool: Blend pool contract address
            asset: Asset contract address (USDC)
            amount: Amount to supply/withdraw (with 7 decimals)

        Returns:
            dict: Transaction result
        """
        try:
            # Build agent execute transaction
            source_account = self.server.load_account(self.agent.public_key)

            # Create Strategy struct
            strategy_struct = scval.to_struct(
                {
                    "action": scval.to_symbol(strategy),
                    "pool": scval.to_address(pool),
                    "asset": scval.to_address(asset),
                    "amount": scval.to_int128(amount),
                }
            )

            tx = (
                TransactionBuilder(
                    source_account=source_account,
                    network_passphrase=self.network,
                    base_fee=100000,
                )
                .append_invoke_contract_function_op(
                    contract_id=self.contract_id,
                    function_name="agent_execute",
                    parameters=[strategy_struct],
                )
                .set_timeout(300)
                .build()
            )

            # Prepare and sign transaction
            prepared_tx = self.server.prepare_transaction(tx)
            prepared_tx.sign(self.agent)

            # Submit transaction
            response = self.server.send_transaction(prepared_tx)

            return {
                "status": "success",
                "tx_hash": response.hash,
                "message": f"Agent executed {strategy} of {amount / 1e7} USDC",
            }

        except Exception as e:
            return {"status": "error", "message": str(e)}

    async def distribute_yield(self, caller_keypair: Keypair) -> Dict:
        """
        Distribute yield: 98% stays in vault, 2% to platform
        Anyone can call this function

        Args:
            caller_keypair: Keypair of the address calling this function

        Returns:
            dict: Transaction result
        """
        try:
            source_account = self.server.load_account(caller_keypair.public_key)

            tx = (
                TransactionBuilder(
                    source_account=source_account,
                    network_passphrase=self.network,
                    base_fee=100000,
                )
                .append_invoke_contract_function_op(
                    contract_id=self.contract_id,
                    function_name="distribute_yield",
                    parameters=[],
                )
                .set_timeout(300)
                .build()
            )

            # Prepare and sign transaction
            prepared_tx = self.server.prepare_transaction(tx)
            prepared_tx.sign(caller_keypair)

            # Submit transaction
            response = self.server.send_transaction(prepared_tx)

            return {
                "status": "success",
                "tx_hash": response.hash,
                "message": "Yield distribution completed",
            }

        except Exception as e:
            return {"status": "error", "message": str(e)}

    async def get_vault_stats(self) -> Dict:
        """
        Get current vault statistics

        Returns:
            dict: TVL, share value, total shares, initial deposits
        """
        try:
            # Call get_vault_stats on the contract
            source_account = self.server.load_account(self.agent.public_key)

            tx = (
                TransactionBuilder(
                    source_account=source_account,
                    network_passphrase=self.network,
                    base_fee=100,
                )
                .append_invoke_contract_function_op(
                    contract_id=self.contract_id,
                    function_name="get_vault_stats",
                    parameters=[],
                )
                .set_timeout(30)
                .build()
            )

            # Simulate transaction to get result
            prepared_tx = self.server.prepare_transaction(tx)
            response = self.server.simulate_transaction(prepared_tx)

            # Parse the result
            if response.results and len(response.results) > 0:
                result = response.results[0]
                # Parse VaultStats struct
                # This is a simplified version - actual parsing depends on result format
                return {
                    "status": "success",
                    "tvl": 0,  # Parse from result
                    "share_value": 1.0,  # Parse from result
                    "total_shares": 0,  # Parse from result
                    "initial_deposits": 0,  # Parse from result
                }
            else:
                return {"status": "error", "message": "No results returned"}

        except Exception as e:
            return {"status": "error", "message": str(e)}

    async def get_user_shares(self, user_address: str) -> Dict:
        """
        Get user's share balance

        Args:
            user_address: User's Stellar address

        Returns:
            dict: User's share balance
        """
        try:
            source_account = self.server.load_account(self.agent.public_key)

            tx = (
                TransactionBuilder(
                    source_account=source_account,
                    network_passphrase=self.network,
                    base_fee=100,
                )
                .append_invoke_contract_function_op(
                    contract_id=self.contract_id,
                    function_name="get_user_shares",
                    parameters=[scval.to_address(user_address)],
                )
                .set_timeout(30)
                .build()
            )

            # Simulate transaction
            prepared_tx = self.server.prepare_transaction(tx)
            response = self.server.simulate_transaction(prepared_tx)

            if response.results and len(response.results) > 0:
                # Parse share balance from result
                # Simplified - actual parsing depends on result format
                shares = 0  # Parse from result

                return {"status": "success", "shares": shares}
            else:
                return {"status": "error", "message": "No results returned"}

        except Exception as e:
            return {"status": "error", "message": str(e)}

    def calculate_apy(self, initial_deposits: int, total_assets: int, days: int = 30) -> float:
        """
        Calculate estimated APY based on yield earned

        Args:
            initial_deposits: Total initial deposits
            total_assets: Current total assets
            days: Number of days to extrapolate

        Returns:
            float: Estimated APY percentage
        """
        if initial_deposits == 0:
            return 0.0

        yield_earned = total_assets - initial_deposits
        daily_return = (yield_earned / initial_deposits) / days
        apy = daily_return * 365 * 100  # Convert to annual percentage

        return round(apy, 2)


# Singleton instance configuration
_vault_manager_instance: Optional[VaultManager] = None


def get_vault_manager() -> Optional[VaultManager]:
    """
    Get or create VaultManager singleton instance

    Returns:
        VaultManager instance if configured, None otherwise
    """
    global _vault_manager_instance

    if _vault_manager_instance is None:
        # Check if vault is configured in environment
        contract_id = os.getenv("VAULT_CONTRACT_ID")
        agent_secret = os.getenv("VAULT_AGENT_SECRET")

        if contract_id and agent_secret:
            agent_keypair = Keypair.from_secret(agent_secret)
            _vault_manager_instance = VaultManager(contract_id, agent_keypair)

    return _vault_manager_instance
