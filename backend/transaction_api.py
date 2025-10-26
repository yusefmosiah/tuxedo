#!/usr/bin/env python3
"""
Direct Transaction API for automatic wallet triggering
"""

from fastapi import HTTPException
from pydantic import BaseModel
from typing import Optional
import logging
from tux_mining import TuxMining

logger = logging.getLogger(__name__)

class TransactionRequest(BaseModel):
    action: str  # 'deposit', 'mining', 'claim'
    user_address: str
    amount: Optional[float] = None
    vault_address: Optional[str] = None

class TransactionResponse(BaseModel):
    success: bool
    transaction: Optional[dict] = None
    error: Optional[str] = None
    message: Optional[str] = None

class TransactionAPI:
    """Direct API for transaction generation and wallet triggering"""

    def __init__(self):
        self.tux_mining = TuxMining()

    async def prepare_deposit_transaction(
        self,
        user_address: str,
        amount: float,
        vault_address: str = None
    ) -> TransactionResponse:
        """Prepare a deposit transaction with tux mining"""
        try:
            if not user_address.startswith('G'):
                raise ValueError("Invalid Stellar address")

            if amount <= 0:
                raise ValueError("Amount must be positive")

            # Generate mining transaction
            transaction_data = self.tux_mining.generate_mining_transaction(
                user_address=user_address,
                deposit_amount=amount,
                vault_address=vault_address
            )

            return TransactionResponse(
                success=True,
                transaction=transaction_data,
                message=f"Ready to deposit {amount} XLM and mine {transaction_data['tux_rewards']:.1f} TUX"
            )

        except Exception as e:
            logger.error(f"Error preparing deposit transaction: {e}")
            return TransactionResponse(
                success=False,
                error=str(e),
                message="Failed to prepare deposit transaction"
            )

    async def get_mining_status(self, user_address: str) -> dict:
        """Get current mining status"""
        try:
            return self.tux_mining.get_mining_status(user_address)
        except Exception as e:
            logger.error(f"Error getting mining status: {e}")
            return {
                'error': str(e),
                'user_address': user_address,
                'total_tux_mined': 0.0,
                'active_mining_sessions': 0
            }

    async def simulate_mining_completion(
        self,
        user_address: str,
        deposit_amount: float
    ) -> dict:
        """Simulate mining completion for demo purposes"""
        try:
            return self.tux_mining.simulate_mining_completion(
                user_address=user_address,
                deposit_amount=deposit_amount
            )
        except Exception as e:
            logger.error(f"Error simulating mining completion: {e}")
            return {
                'error': str(e),
                'message': 'Failed to simulate mining completion'
            }

# Create global instance
transaction_api = TransactionAPI()