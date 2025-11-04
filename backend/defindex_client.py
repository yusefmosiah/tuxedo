#!/usr/bin/env python3
"""
DeFindex API client for Stellar vault operations
"""

import os
import requests
import logging
from typing import Dict, List, Optional
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import json

logger = logging.getLogger(__name__)

class DeFindexClient:
    """Client for DeFindex REST API - server-side only"""

    def __init__(self, api_key: str, network: str = "mainnet"):
        self.api_key = api_key
        self.network = network
        # ✅ CONFIRMED: Correct base URL from official API docs
        self.base_url = "https://api.defindex.io"
        self.session = self._create_session()

        # Factory contract address for vault operations
        self.factory_address = "CDZKFHJIET3A73A2YN4KV7NSV32S6YGQMUFH3DNJXLBWL4SKEGVRNFKI"

    def _create_session(self):
        """Create session with retry logic and Bearer auth"""
        session = requests.Session()

        # Retry on failures
        retry = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504]
        )
        session.mount("https://", HTTPAdapter(max_retries=retry))

        # CRITICAL: Bearer token format
        session.headers.update({
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        })

        return session

    def test_connection(self) -> bool:
        """Test if API key works with base URL"""
        try:
            # Use health endpoint and factory address for connection test
            health_response = self.session.get(
                f"{self.base_url}/health",
                timeout=10
            )
            factory_response = self.session.get(
                f"{self.base_url}/factory/address",
                timeout=10
            )
            return health_response.status_code == 200 and factory_response.status_code == 200
        except Exception as e:
            logger.error(f"DeFindex API connection failed: {e}")
            return False

    def get_vaults(self, vault_addresses: List[str] = None) -> List[Dict]:
        """Get information about specific vaults

        Args:
            vault_addresses: List of vault contract addresses to query.
                           If None, returns empty list (API requires specific addresses)

        Returns:
            List of vault objects with basic info
        """
        if not vault_addresses:
            logger.warning("DeFindex API requires specific vault addresses - no addresses provided")
            return []

        vaults = []
        for address in vault_addresses:
            try:
                vault_info = self.get_vault_info(address)
                if vault_info:
                    vaults.append(vault_info)
            except Exception as e:
                logger.warning(f"Failed to fetch vault {address}: {e}")
                continue

        return vaults

    def get_vault_info(self, vault_address: str) -> Dict:
        """Get detailed information about a specific vault

        Args:
            vault_address: Contract address of the vault

        Returns:
            Vault details including APY, TVL, strategies, etc.
        """
        try:
            # ✅ CONFIRMED: Correct endpoint format from API spec
            response = self.session.get(
                f"{self.base_url}/vault/{vault_address}",
                timeout=15
            )
            response.raise_for_status()
            return response.json()

        except requests.HTTPError as e:
            if e.response.status_code == 403:
                raise ValueError("DeFindex API authentication failed")
            elif e.response.status_code == 404:
                raise ValueError(f"Vault not found: {vault_address}")
            elif e.response.status_code == 429:
                raise ValueError("DeFindex API rate limit exceeded - please wait before trying again")
            else:
                raise ValueError(f"DeFindex API error: {e.response.status_code} - {e.response.text}")
        except requests.Timeout:
            raise ValueError("DeFindex API timeout - please try again")
        except Exception as e:
            raise ValueError(f"Error fetching vault info: {str(e)}")

    def get_vault_balance(self, vault_address: str, user_address: str) -> Dict:
        """Get user's balance in a specific vault

        Args:
            vault_address: Contract address of the vault
            user_address: Stellar public key (G...)

        Returns:
            User's vault shares and underlying asset value
        """
        try:
            response = self.session.get(
                f"{self.base_url}/vault/{vault_address}/balance",
                params={'from': user_address, 'network': self.network},
                timeout=10
            )
            response.raise_for_status()
            return response.json()

        except Exception as e:
            raise ValueError(f"Error fetching vault balance: {str(e)}")

    def build_deposit_transaction(
        self,
        vault_address: str,
        amount_stroops: int,
        caller: str,
        invest: bool = True
    ) -> Dict:
        """Build unsigned deposit transaction

        Args:
            vault_address: Contract address of the vault
            amount_stroops: Amount in stroops (1 XLM = 10,000,000 stroops)
            caller: User's Stellar public key (G...)
            invest: Whether to auto-invest after deposit

        Returns:
            Transaction data including unsigned XDR
        """
        try:
            data = {
                'amounts': [amount_stroops],
                'from': caller,  # Based on API docs
                'invest': invest,
                'slippageBps': 50  # 0.5% slippage tolerance
            }

            # ✅ CONFIRMED: Correct endpoint format from API spec
            response = self.session.post(
                f"{self.base_url}/vault/{vault_address}/deposit",
                json=data,
                timeout=30
            )
            response.raise_for_status()
            return response.json()

        except requests.HTTPError as e:
            if e.response.status_code == 403:
                raise ValueError("DeFindex API authentication failed")
            elif e.response.status_code == 404:
                raise ValueError(f"Deposit endpoint not found for vault: {vault_address}")
            elif e.response.status_code == 429:
                raise ValueError("DeFindex API rate limit exceeded - please wait before trying again")
            else:
                raise ValueError(f"DeFindex API error: {e.response.status_code} - {e.response.text}")
        except requests.Timeout:
            raise ValueError("DeFindex API timeout - please try again")
        except Exception as e:
            raise ValueError(f"Error building deposit transaction: {str(e)}")

    def get_vault_apy(self, vault_address: str) -> Dict:
        """Get APY information for a specific vault

        Args:
            vault_address: Contract address of the vault

        Returns:
            APY data for the vault
        """
        try:
            # ✅ CONFIRMED: Dedicated APY endpoint from API spec
            response = self.session.get(
                f"{self.base_url}/vault/{vault_address}/apy",
                timeout=10
            )
            response.raise_for_status()
            return response.json()

        except requests.HTTPError as e:
            if e.response.status_code == 403:
                raise ValueError("DeFindex API authentication failed")
            elif e.response.status_code == 404:
                raise ValueError(f"APY endpoint not found for vault: {vault_address}")
            elif e.response.status_code == 429:
                raise ValueError("DeFindex API rate limit exceeded - please wait before trying again")
            else:
                raise ValueError(f"DeFindex API error: {e.response.status_code} - {e.response.text}")
        except requests.Timeout:
            raise ValueError("DeFindex API timeout - please try again")
        except Exception as e:
            raise ValueError(f"Error fetching vault APY: {str(e)}")

    def submit_transaction(self, signed_xdr: str, use_launchtube: bool = False) -> Dict:
        """Submit signed transaction to Stellar network

        Args:
            signed_xdr: Signed transaction XDR from Freighter
            use_launchtube: Whether to use gasless transactions

        Returns:
            Transaction result with hash and status
        """
        try:
            data = {
                'xdr': signed_xdr,
                'launchtube': use_launchtube
            }

            response = self.session.post(
                f"{self.base_url}/send",
                json=data,
                timeout=30
            )
            response.raise_for_status()
            return response.json()

        except requests.HTTPError as e:
            if e.response.status_code == 403:
                raise ValueError("DeFindex API authentication failed")
            elif e.response.status_code == 429:
                raise ValueError("DeFindex API rate limit exceeded - please wait before trying again")
            else:
                raise ValueError(f"DeFindex API error: {e.response.status_code} - {e.response.text}")
        except requests.Timeout:
            raise ValueError("DeFindex API timeout - please try again")
        except Exception as e:
            raise ValueError(f"Error submitting transaction: {str(e)}")

def get_defindex_client(network: str = 'mainnet') -> DeFindexClient:
    """Get configured DeFindex client"""
    api_key = os.getenv('DEFINDEX_API_KEY')
    if not api_key:
        raise ValueError("DEFINDEX_API_KEY environment variable not set")
    return DeFindexClient(api_key=api_key, network=network)

async def get_vault_data_with_fallback(network: str = 'mainnet', min_apy: float = 15.0):
    """Get vault data with API fallback to enhanced mock data"""
    try:
        # Try to get real API data first
        client = get_defindex_client(network)
        if client.test_connection():
            vaults = client.get_vaults()
            if vaults:
                return vaults, "api"
    except Exception as e:
        logger.warning(f"API fallback triggered: {e}")

    # Fallback to enhanced mock data
    from defindex_soroban import get_defindex_soroban
    defindex = get_defindex_soroban(network)
    vaults = await defindex.get_available_vaults(min_apy=min_apy)
    return vaults, "enhanced_mock"

async def get_vault_details_with_fallback(vault_address: str, network: str = 'mainnet'):
    """Get vault details with API fallback to enhanced mock data"""
    try:
        # Try to get real API data first
        client = get_defindex_client(network)
        if client.test_connection():
            vault_info = client.get_vault_info(vault_address)
            if vault_info:
                return vault_info, "api"
    except Exception as e:
        logger.warning(f"API fallback triggered for vault details: {e}")

    # Fallback to enhanced mock data
    from defindex_soroban import get_defindex_soroban
    defindex = get_defindex_soroban(network)
    vault_info = await defindex.get_vault_details(vault_address)
    return vault_info, "enhanced_mock"