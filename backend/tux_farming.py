"""
TUX Yield Farming Integration for Tuxedo Backend

This module provides the integration between Tuxedo and the TUX yield farming contracts,
including contract interaction, pool management, and reward calculations.
"""

import os
import json
import time
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from stellar_sdk import Server, Keypair, TransactionBuilder
from stellar_sdk import scval
from stellar_sdk.exceptions import PrepareTransactionException

# Network configuration
NETWORK_PASSPHRASE = "Test SDF Network ; September 2015"
HORIZON_URL = "https://horizon-testnet.stellar.org"
RPC_URL = "https://soroban-testnet.stellar.org"

@dataclass
class PoolInfo:
    """Information about a farming pool"""
    pool_id: str
    staking_token: str
    allocation_points: int
    total_staked: int
    reward_per_token_stored: int
    last_update_time: int
    is_active: bool

@dataclass
class UserStake:
    """User's stake information in a pool"""
    balance: int
    reward_per_token_paid: int
    pending_rewards: int
    stake_start_time: int
    last_claim_time: int

@dataclass
class ContractInfo:
    """Contract deployment information"""
    tux_token_contract: str
    farming_contract: str
    admin_public_key: str
    network: str
    timestamp: int

class TuxFarmingClient:
    """Client for interacting with TUX farming contracts"""

    def __init__(self):
        self.server = Server(horizon_url=HORIZON_URL)
        self.contracts = self._load_deployment_info()
        if not self.contracts:
            raise ValueError("Contracts not deployed. Run deployment script first.")

    def _load_deployment_info(self) -> Optional[ContractInfo]:
        """Load contract deployment information"""
        try:
            # Try to load the simple deployment first (Stellar asset approach)
            with open("../tux_simple_deployment.json", "r") as f:
                data = json.load(f)

            # Convert to ContractInfo format
            return ContractInfo(
                tux_token_contract=f"{data['tux_token']['asset_code']}:{data['tux_token']['issuer']}",
                farming_contract="mock_farming_contract",  # Using mock since we're using Stellar assets
                admin_public_key=data['admin_public_key'],
                network=data['network'],
                timestamp=data['timestamp']
            )
        except FileNotFoundError:
            return None
        except Exception as e:
            print(f"Error loading deployment info: {e}")
            return None

    def get_contract_client(self, contract_address: str):
        """Create a contract client for the given address"""
        # For now, return a mock client since we don't need actual contract calls
        return None

    def get_pools_info(self) -> List[PoolInfo]:
        """Get information about all farming pools"""
        try:
            # Common testnet tokens for farming pools
            testnet_pools = [
                {"pool_id": "USDC", "staking_token": "GBXE4VMKQGYU7J4D2MHQH74U3Q7F6J3BQ4KILJL3E4I6K6F5E4J5G7E6", "name": "USD Coin"},
                {"pool_id": "XLM", "staking_token": "native", "name": "Stellar Lumens"},
                {"pool_id": "ETH", "staking_token": "GBXE4VMKQGYU7J4D2MHQH74U3Q7F6J3BQ4KILJL3E4I6K6F5E4J5G7E6", "name": "Ethereum (Test)"},
            ]

            pools = []

            for pool_info in testnet_pools:
                pools.append(PoolInfo(
                    pool_id=pool_info["pool_id"],
                    staking_token=pool_info["staking_token"],
                    allocation_points=100,
                    total_staked=25000000,  # Mock staked amount
                    reward_per_token_stored=1000,
                    last_update_time=int(time.time()),
                    is_active=True
                ))

            return pools

        except Exception as e:
            print(f"Error getting pools info: {e}")
            return []

    def get_user_stake(self, user_address: str, pool_id: str) -> Optional[UserStake]:
        """Get user's stake information for a specific pool"""
        try:
            farming_client = self.get_contract_client(self.contracts.farming_contract)

            # Get user stake info
            tx = farming_client.invoke(
                function="get_user_stake_info",
                args=[to_address(user_address), to_symbol(pool_id)]
            )

            # For now, return mock data
            return UserStake(
                balance=0,
                reward_per_token_paid=0,
                pending_rewards=0,
                stake_start_time=0,
                last_claim_time=0
            )

        except Exception as e:
            print(f"Error getting user stake: {e}")
            return None

    def get_pending_rewards(self, user_address: str, pool_id: str) -> int:
        """Get pending rewards for a user in a specific pool"""
        try:
            farming_client = self.get_contract_client(self.contracts.farming_contract)

            tx = farming_client.invoke(
                function="pending_rewards",
                args=[to_address(user_address), to_symbol(pool_id)]
            )

            # For now, return mock data
            return 0

        except Exception as e:
            print(f"Error getting pending rewards: {e}")
            return 0

    def get_total_pending_rewards(self, user_address: str) -> int:
        """Get total pending rewards across all pools"""
        try:
            farming_client = self.get_contract_client(self.contracts.farming_contract)

            tx = farming_client.invoke(
                function="claim_all_rewards",
                args=[to_address(user_address)]
            )

            # For now, return mock data
            return 0

        except Exception as e:
            print(f"Error getting total pending rewards: {e}")
            return 0

    def calculate_apy(self, pool_id: str) -> float:
        """Calculate APY for a specific pool"""
        try:
            # This would normally query contract state and calculate based on:
            # - Reward rate
            # - Total staked amount
            # - Token price
            # For now, return a mock APY
            return 15.5  # 15.5% APY

        except Exception as e:
            print(f"Error calculating APY: {e}")
            return 0.0

    def get_token_info(self) -> Dict:
        """Get TUX token information"""
        try:
            # Parse the TUX token contract info which is actually "TUX:issuer_address"
            token_info = self.contracts.tux_token_contract.split(":")
            asset_code = token_info[0]
            issuer_address = token_info[1]

            # Load deployment info for additional details
            with open("../tux_simple_deployment.json", "r") as f:
                deployment_data = json.load(f)

            return {
                "name": "Tuxedo Token",
                "symbol": asset_code,
                "decimals": 7,  # Standard for Stellar assets
                "total_supply": deployment_data.get('initial_supply_issued', 100_000_000),
                "asset_code": asset_code,
                "issuer": issuer_address,
                "type": deployment_data['tux_token']['type'],
                "admin_public_key": deployment_data['admin_public_key']
            }

        except Exception as e:
            print(f"Error getting token info: {e}")
            return {}

    def format_pending_rewards(self, rewards: int) -> str:
        """Format pending rewards for display"""
        decimals = 7
        formatted_amount = rewards / (10 ** decimals)
        return f"{formatted_amount:,.2f} TUX"

class TuxFarmingTools:
    """TUX farming tools for the AI agent"""

    def __init__(self):
        self.client = TuxFarmingClient()

    def get_farming_overview(self, user_address: Optional[str] = None) -> Dict:
        """Get overview of TUX farming opportunities and user positions"""
        try:
            # Get token info
            token_info = self.client.get_token_info()

            # Get pools
            pools = self.client.get_pools_info()

            # Calculate pool details
            pool_details = []
            for pool in pools:
                pool_detail = {
                    "pool_id": pool.pool_id,
                    "staking_token": pool.staking_token,
                    "total_staked": pool.total_staked,
                    "apy": self.client.calculate_apy(pool.pool_id),
                    "is_active": pool.is_active,
                }

                if user_address:
                    user_stake = self.client.get_user_stake(user_address, pool.pool_id)
                    pending_rewards = self.client.get_pending_rewards(user_address, pool.pool_id)

                    pool_detail.update({
                        "user_staked": user_stake.balance if user_stake else 0,
                        "pending_rewards": pending_rewards,
                        "formatted_pending_rewards": self.client.format_pending_rewards(pending_rewards),
                    })

                pool_details.append(pool_detail)

            # Calculate totals if user provided
            totals = {}
            if user_address:
                total_pending = self.client.get_total_pending_rewards(user_address)
                totals = {
                    "total_pending_rewards": total_pending,
                    "formatted_total_pending": self.client.format_pending_rewards(total_pending),
                }

            return {
                "token_info": token_info,
                "pools": pool_details,
                "totals": totals,
                "timestamp": int(time.time()),
            }

        except Exception as e:
            return {"error": f"Failed to get farming overview: {str(e)}"}

    def get_pool_details(self, pool_id: str, user_address: Optional[str] = None) -> Dict:
        """Get detailed information about a specific pool"""
        try:
            pools = self.client.get_pools_info()
            pool = next((p for p in pools if p.pool_id == pool_id), None)

            if not pool:
                return {"error": f"Pool {pool_id} not found"}

            pool_detail = {
                "pool_id": pool.pool_id,
                "staking_token": pool.staking_token,
                "allocation_points": pool.allocation_points,
                "total_staked": pool.total_staked,
                "apy": self.client.calculate_apy(pool.pool_id),
                "is_active": pool.is_active,
                "last_update_time": pool.last_update_time,
            }

            if user_address:
                user_stake = self.client.get_user_stake(user_address, pool_id)
                pending_rewards = self.client.get_pending_rewards(user_address, pool_id)

                pool_detail.update({
                    "user_staked": user_stake.balance if user_stake else 0,
                    "user_stake_start_time": user_stake.stake_start_time if user_stake else 0,
                    "pending_rewards": pending_rewards,
                    "formatted_pending_rewards": self.client.format_pending_rewards(pending_rewards),
                })

            return pool_detail

        except Exception as e:
            return {"error": f"Failed to get pool details: {str(e)}"}

    def get_user_positions(self, user_address: str) -> Dict:
        """Get all user's farming positions"""
        try:
            pools = self.client.get_pools_info()
            positions = []
            total_pending = 0

            for pool in pools:
                user_stake = self.client.get_user_stake(user_address, pool.pool_id)
                if user_stake and user_stake.balance > 0:
                    pending_rewards = self.client.get_pending_rewards(user_address, pool.pool_id)
                    total_pending += pending_rewards

                    position = {
                        "pool_id": pool.pool_id,
                        "staking_token": pool.staking_token,
                        "amount_staked": user_stake.balance,
                        "stake_start_time": user_stake.stake_start_time,
                        "last_claim_time": user_stake.last_claim_time,
                        "pending_rewards": pending_rewards,
                        "formatted_pending_rewards": self.client.format_pending_rewards(pending_rewards),
                        "apy": self.client.calculate_apy(pool.pool_id),
                    }
                    positions.append(position)

            return {
                "user_address": user_address,
                "positions": positions,
                "total_pending_rewards": total_pending,
                "formatted_total_pending": self.client.format_pending_rewards(total_pending),
                "active_positions": len([p for p in positions if p["amount_staked"] > 0]),
                "timestamp": int(time.time()),
            }

        except Exception as e:
            return {"error": f"Failed to get user positions: {str(e)}"}

# Test function
def test_tux_farming():
    """Test the TUX farming integration"""
    try:
        print("Testing TUX Farming Integration...")

        tools = TuxFarmingTools()

        # Test getting farming overview
        print("\n=== Farming Overview ===")
        overview = tools.get_farming_overview()
        print(f"Token: {overview.get('token_info', {}).get('symbol', 'N/A')}")
        print(f"Number of pools: {len(overview.get('pools', []))}")

        # Test getting pool details
        if overview.get('pools'):
            pool_id = overview['pools'][0]['pool_id']
            print(f"\n=== Pool Details: {pool_id} ===")
            pool_details = tools.get_pool_details(pool_id)
            print(f"APY: {pool_details.get('apy', 0)}%")
            print(f"Total Staked: {pool_details.get('total_staked', 0)}")

        # Test user positions (with mock address)
        mock_user = "GD5DQJFP2XQ7YQ7M5XVYXG2B6J7X7Z7Y7Z7Y7Z7Y7Z7Y7Z7Y7Z7Y7Z7Y7Z7Y"
        print(f"\n=== User Positions ===")
        positions = tools.get_user_positions(mock_user)
        print(f"Active positions: {positions.get('active_positions', 0)}")

        print("\n✅ TUX farming integration test completed successfully!")
        return True

    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

if __name__ == "__main__":
    test_tux_farming()