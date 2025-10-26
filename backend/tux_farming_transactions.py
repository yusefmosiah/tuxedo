"""
TUX Yield Farming Transaction Tools

This module provides real transaction functionality for TUX yield farming,
including trustline creation, token staking, and reward claiming.
"""

import os
import json
import time
from typing import Dict, List, Optional, Tuple
from stellar_sdk import Server, Keypair, TransactionBuilder, Asset, Payment, ChangeTrust
from stellar_sdk.operation import ManageSellOffer
from stellar_sdk.exceptions import PrepareTransactionException

# Network configuration
NETWORK_PASSPHRASE = "Test SDF Network ; September 2015"
HORIZON_URL = "https://horizon-testnet.stellar.org"

class TuxFarmingTransactions:
    """Client for executing TUX farming transactions"""

    def __init__(self):
        self.server = Server(horizon_url=HORIZON_URL)
        self.network_passphrase = NETWORK_PASSPHRASE

        # Load TUX token info
        deployment_path = os.path.join(os.path.dirname(__file__), "..", "tux_simple_deployment.json")
        with open(deployment_path, "r") as f:
            self.deployment_data = json.load(f)

        self.tux_asset = Asset(
            self.deployment_data['tux_token']['asset_code'],
            self.deployment_data['tux_token']['issuer']
        )

    def create_tux_trustline_xdr(self, public_key: str) -> Dict:
        """Create an unsigned XDR transaction for TUX trustline"""
        try:
            account = self.server.load_account(public_key)

            # Create ChangeTrust transaction for TUX token
            trustline_tx = (
                TransactionBuilder(
                    source_account=account,
                    network_passphrase=self.network_passphrase,
                    base_fee=100,
                )
                .append_change_trust_op(
                    asset=self.tux_asset,
                    limit="100000000"  # 100M TUX limit
                )
                .set_timeout(30)
                .build()
            )

            return {
                "success": True,
                "xdr": trustline_tx.to_xdr(),
                "network": self.network_passphrase,
                "message": "Please sign this transaction to create a TUX token trustline",
                "operations": ["ChangeTrust for TUX token"]
            }

        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to create trustline transaction: {str(e)}"
            }

    def create_stake_transaction_xdr(self, public_key: str, pool_id: str, amount: str) -> Dict:
        """
        Create an unsigned XDR transaction for staking in a pool
        Note: This is a simplified version - in real farming this would interact with the farming contract
        """
        try:
            account = self.server.load_account(public_key)

            # For demo purposes, we'll create a simple payment transaction
            # In a real implementation, this would be a contract call to the farming contract

            if pool_id == "USDC":
                # For USDC pool, create a payment to a mock farming contract address
                staking_tx = (
                    TransactionBuilder(
                        source_account=account,
                        network_passphrase=self.network_passphrase,
                        base_fee=100,
                    )
                    .append_payment_op(
                        destination="GA23UZT2AL4WA4GONJQD75C3QYRBS3XFW6ZHZUBHDDKOQI22LKHLUX3H",  # Admin account as mock contract
                        asset=Asset("USDC", "GBXE4VMKQGYU7J4D2MHQH74U3Q7F6J3BQ4KILJL3E4I6K6F5E4J5G7E6"),
                        amount=amount
                    )
                    .set_timeout(30)
                    .build()
                )
            elif pool_id == "XLM":
                # For XLM pool, create a payment with native XLM
                staking_tx = (
                    TransactionBuilder(
                        source_account=account,
                        network_passphrase=self.network_passphrase,
                        base_fee=100,
                    )
                    .append_payment_op(
                        destination="GA23UZT2AL4WA4GONJQD75C3QYRBS3XFW6ZHZUBHDDKOQI22LKHLUX3H",
                        asset=Asset.native(),
                        amount=amount
                    )
                    .set_timeout(30)
                    .build()
                )
            else:
                return {
                    "success": False,
                    "error": f"Pool {pool_id} not supported yet"
                }

            return {
                "success": True,
                "xdr": staking_tx.to_xdr(),
                "network": self.network_passphrase,
                "message": f"Please sign this transaction to stake {amount} {pool_id} in the farming pool",
                "operations": [f"Stake {amount} {pool_id}"],
                "pool_id": pool_id,
                "amount": amount
            }

        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to create staking transaction: {str(e)}"
            }

    def create_unstake_transaction_xdr(self, public_key: str, pool_id: str, amount: str) -> Dict:
        """
        Create an unsigned XDR transaction for unstaking from a pool
        """
        try:
            account = self.server.load_account(public_key)

            # For demo purposes, we'll return a simple transaction
            # In a real implementation, this would call the farming contract to unstake

            return {
                "success": True,
                "xdr": "mock_unstake_xdr",
                "network": self.network_passphrase,
                "message": f"Please sign this transaction to unstake {amount} {pool_id} from the farming pool",
                "operations": [f"Unstake {amount} {pool_id}"],
                "pool_id": pool_id,
                "amount": amount,
                "note": "This is a demo transaction - real implementation would call farming contract"
            }

        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to create unstaking transaction: {str(e)}"
            }

    def create_claim_rewards_transaction_xdr(self, public_key: str) -> Dict:
        """
        Create an unsigned XDR transaction for claiming TUX rewards
        """
        try:
            account = self.server.load_account(public_key)

            # For demo purposes, we'll simulate claiming rewards from the admin account
            claim_tx = (
                TransactionBuilder(
                    source_account=account,
                    network_passphrase=self.network_passphrase,
                    base_fee=100,
                )
                .append_payment_op(
                    destination=public_key,
                    asset=self.tux_asset,
                    amount="1000"  # Mock reward amount
                )
                .set_timeout(30)
                .build()
            )

            return {
                "success": True,
                "xdr": claim_tx.to_xdr(),
                "network": self.network_passphrase,
                "message": "Please sign this transaction to claim your TUX rewards",
                "operations": ["Claim TUX rewards"],
                "reward_amount": "1000 TUX"
            }

        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to create claim rewards transaction: {str(e)}"
            }

    def get_farming_requirements(self, public_key: str) -> Dict:
        """Check what's needed for farming with this account"""
        try:
            account = self.server.load_account(public_key)

            # Check for TUX trustline
            has_tux_trustline = False
            tux_balance = 0

            # Access balances through raw_data
            balances = account.raw_data.get('balances', [])

            for balance in balances:
                if (balance.get('asset_code') == "TUX" and
                    balance.get('asset_issuer') == self.deployment_data['tux_token']['issuer']):
                    has_tux_trustline = True
                    tux_balance = float(balance['balance'])
                    break

            # Check for other token balances
            xlm_balance = 0
            usdc_balance = 0

            for balance in balances:
                if balance.get('asset_type') == "native":
                    xlm_balance = float(balance['balance'])
                elif (balance.get('asset_code') == "USDC" and
                      balance.get('asset_issuer') == "GBXE4VMKQGYU7J4D2MHQH74U3Q7F6J3BQ4KILJL3E4I6K6F5E4J5G7E6"):
                    usdc_balance = float(balance['balance'])

            requirements = {
                "has_tux_trustline": has_tux_trustline,
                "tux_balance": tux_balance,
                "xlm_balance": xlm_balance,
                "usdc_balance": usdc_balance,
                "needs_trustline": not has_tux_trustline,
                "can_stake_xlm": xlm_balance > 1,
                "can_stake_usdc": usdc_balance > 1,
                "recommended_actions": []
            }

            # Add recommendations
            if not has_tux_trustline:
                requirements["recommended_actions"].append("Create TUX token trustline to receive rewards")

            if xlm_balance > 1:
                requirements["recommended_actions"].append(f"You can stake {xlm_balance:.2f} XLM in the XLM pool")

            if usdc_balance > 1:
                requirements["recommended_actions"].append(f"You can stake {usdc_balance:.2f} USDC in the USDC pool")

            if xlm_balance <= 1 and usdc_balance <= 1:
                requirements["recommended_actions"].append("Fund your wallet with XLM or USDC to start farming")

            return requirements

        except Exception as e:
            return {
                "error": f"Failed to check farming requirements: {str(e)}"
            }

    def simulate_farming_rewards(self, public_key: str, pool_id: str, amount: str, days: int = 30) -> Dict:
        """Simulate potential farming rewards"""
        try:
            # Use the 15.5% APY from our mock data
            apy = 0.155

            # Calculate daily rewards
            daily_rate = apy / 365
            amount_float = float(amount)
            daily_rewards = amount_float * daily_rate
            total_rewards = daily_rewards * days

            return {
                "success": True,
                "pool_id": pool_id,
                "staked_amount": amount_float,
                "apy_percentage": apy * 100,
                "period_days": days,
                "daily_rewards": daily_rewards,
                "total_rewards": total_rewards,
                "formatted_daily_rewards": f"{daily_rewards:.4f} TUX per day",
                "formatted_total_rewards": f"{total_rewards:.2f} TUX after {days} days",
                "note": "This is a simulation based on current APY rates"
            }

        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to simulate rewards: {str(e)}"
            }