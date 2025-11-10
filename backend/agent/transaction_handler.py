"""
Transaction Handler - Dual-Mode Transaction Signing

Handles transaction signing based on wallet mode:
- Agent mode: Signs transactions autonomously using AccountManager
- External mode: Returns unsigned XDR for frontend wallet signing
- Imported mode: Treats like agent mode (agent has custody)
"""

from typing import Dict, Any, Optional
import logging
from stellar_sdk import TransactionBuilder, Network, Keypair
from agent.context import AgentContext

logger = logging.getLogger(__name__)


class TransactionHandler:
    """
    Handle transaction signing based on wallet mode.

    This class provides a unified interface for transaction signing
    that adapts based on the AgentContext wallet_mode.
    """

    def __init__(self, account_manager):
        """
        Initialize transaction handler.

        Args:
            account_manager: AccountManager instance for agent signing
        """
        self.account_manager = account_manager

    async def sign_and_submit(
        self,
        tx_builder: TransactionBuilder,
        agent_context: AgentContext,
        account_id: str,
        horizon_server,
        description: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Sign and submit transaction based on wallet mode.

        Args:
            tx_builder: Stellar SDK TransactionBuilder instance
            agent_context: Agent execution context with wallet mode
            account_id: Account ID for signing (agent-managed accounts)
            horizon_server: Stellar Horizon server instance
            description: Human-readable transaction description

        Returns:
            For agent/imported mode:
                {
                    "success": bool,
                    "hash": str,
                    "ledger": int,
                    "message": str
                }

            For external mode:
                {
                    "requires_signature": True,
                    "xdr": str,
                    "network_passphrase": str,
                    "description": str,
                    "message": str
                }
        """
        try:
            # Build transaction
            tx = tx_builder.set_timeout(30).build()

            # Check wallet mode
            if agent_context.requires_user_signing():
                # External wallet mode - return unsigned XDR
                logger.info(f"External mode: Returning unsigned XDR for user approval")
                return {
                    "requires_signature": True,
                    "xdr": tx.to_xdr(),
                    "network_passphrase": Network.PUBLIC_NETWORK_PASSPHRASE,
                    "description": description or self._describe_transaction(tx),
                    "message": "Please approve this transaction in your wallet",
                    "wallet_address": agent_context.wallet_address
                }

            else:
                # Agent/imported mode - sign and submit automatically
                logger.info(f"Agent mode: Signing and submitting transaction for account {account_id}")

                # Get signing keypair from AccountManager
                keypair = self.account_manager.get_keypair_for_signing(
                    agent_context,
                    account_id
                )

                # Sign transaction
                stellar_keypair = Keypair.from_secret(keypair.private_key)
                tx.sign(stellar_keypair)

                # Submit to network
                response = horizon_server.submit_transaction(tx)

                logger.info(f"Transaction submitted successfully: {response.get('hash')}")

                return {
                    "success": response.get("successful", False),
                    "hash": response.get("hash"),
                    "ledger": response.get("ledger"),
                    "message": "Transaction submitted successfully",
                    "description": description or self._describe_transaction(tx)
                }

        except Exception as e:
            logger.error(f"Error in transaction handling: {e}")
            return {
                "success": False,
                "error": str(e),
                "message": f"Failed to process transaction: {str(e)}"
            }

    def _describe_transaction(self, tx) -> str:
        """
        Generate human-readable transaction description.

        Args:
            tx: Stellar SDK Transaction instance

        Returns:
            Human-readable description string
        """
        try:
            ops = tx.transaction.operations

            if len(ops) == 1:
                op = ops[0]
                op_type = op.__class__.__name__

                # Format based on operation type
                if op_type == "Payment":
                    amount = getattr(op, 'amount', 'unknown')
                    asset = getattr(op, 'asset', 'XLM')
                    dest = getattr(op, 'destination', 'unknown')
                    return f"Payment: Send {amount} {asset} to {dest[:8]}..."

                elif op_type == "CreateAccount":
                    starting_balance = getattr(op, 'starting_balance', 'unknown')
                    dest = getattr(op, 'destination', 'unknown')
                    return f"Create Account: Fund {dest[:8]}... with {starting_balance} XLM"

                elif op_type == "InvokeHostFunction":
                    return "Soroban Contract: Invoke smart contract function"

                else:
                    return f"{op_type} operation"

            else:
                return f"Multi-operation transaction ({len(ops)} operations)"

        except Exception as e:
            logger.error(f"Error describing transaction: {e}")
            return "Transaction"

    async def submit_signed_transaction(
        self,
        signed_xdr: str,
        horizon_server
    ) -> Dict[str, Any]:
        """
        Submit a transaction that was signed by external wallet.

        Args:
            signed_xdr: XDR string of signed transaction
            horizon_server: Stellar Horizon server instance

        Returns:
            {
                "success": bool,
                "hash": str,
                "ledger": int,
                "message": str
            }
        """
        try:
            from stellar_sdk import TransactionEnvelope

            # Parse signed transaction
            tx_envelope = TransactionEnvelope.from_xdr(
                signed_xdr,
                Network.PUBLIC_NETWORK_PASSPHRASE
            )

            # Submit to network
            response = horizon_server.submit_transaction(tx_envelope)

            logger.info(f"External wallet transaction submitted: {response.get('hash')}")

            return {
                "success": response.get("successful", False),
                "hash": response.get("hash"),
                "ledger": response.get("ledger"),
                "message": "Transaction submitted successfully"
            }

        except Exception as e:
            logger.error(f"Error submitting signed transaction: {e}")
            return {
                "success": False,
                "error": str(e),
                "message": f"Failed to submit transaction: {str(e)}"
            }
