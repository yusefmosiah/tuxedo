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
        # ⚠️ TODO: Verify correct base URL from official docs
        self.base_url = "https://api.defindex.io"
        self.session = self._create_session()

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
            # Try to get vaults as a connection test
            response = self.session.get(
                f"{self.base_url}/vaults",
                params={'network': self.network, 'limit': 1},
                timeout=10
            )
            return response.status_code == 200
        except Exception as e:
            logger.error(f"DeFindex API connection failed: {e}")
            return False

    def get_vaults(self, limit: int = 50) -> List[Dict]:
        """Get list of available vaults

        Returns:
            List of vault objects with basic info
        """
        try:
            # Try different endpoint patterns based on documentation
            endpoints_to_try = [
                f"{self.base_url}/vaults",
                f"{self.base_url}/api/vaults",
                f"{self.base_url}/v1/vaults"
            ]

            for endpoint in endpoints_to_try:
                try:
                    response = self.session.get(
                        endpoint,
                        params={'network': self.network, 'limit': limit},
                        timeout=15
                    )
                    response.raise_for_status()
                    data = response.json()

                    # Handle different response formats
                    if isinstance(data, dict) and 'vaults' in data:
                        return data['vaults']
                    elif isinstance(data, list):
                        return data
                    elif isinstance(data, dict) and 'data' in data:
                        return data['data']
                    else:
                        logger.warning(f"Unexpected response format from {endpoint}: {type(data)}")
                        continue

                except requests.HTTPError as e:
                    if e.response.status_code == 404:
                        continue  # Try next endpoint
                    else:
                        raise

            raise ValueError("All vault endpoints returned 404 - API structure may have changed")

        except requests.HTTPError as e:
            if e.response.status_code == 403:
                raise ValueError("DeFindex API authentication failed - check API key")
            raise
        except requests.Timeout:
            raise ValueError("DeFindex API timeout - please try again")
        except Exception as e:
            logger.error(f"Error fetching vaults: {e}")
            raise ValueError(f"Error fetching vaults: {str(e)}")

    def get_vault_info(self, vault_address: str) -> Dict:
        """Get detailed information about a specific vault

        Args:
            vault_address: Contract address of the vault

        Returns:
            Vault details including APY, TVL, strategies, etc.
        """
        try:
            # Try different endpoint patterns
            endpoints_to_try = [
                f"{self.base_url}/vault/{vault_address}",
                f"{self.base_url}/api/vault/{vault_address}",
                f"{self.base_url}/v1/vault/{vault_address}"
            ]

            for endpoint in endpoints_to_try:
                try:
                    response = self.session.get(
                        endpoint,
                        params={'network': self.network},
                        timeout=10
                    )
                    response.raise_for_status()
                    return response.json()

                except requests.HTTPError as e:
                    if e.response.status_code == 404:
                        continue  # Try next endpoint
                    else:
                        raise

            raise ValueError(f"Vault not found with any endpoint: {vault_address}")

        except requests.HTTPError as e:
            if e.response.status_code == 403:
                raise ValueError("DeFindex API authentication failed")
            raise
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
                'from': caller,  # Based on docs example
                'invest': invest,
                'slippageBps': 50  # 0.5% slippage tolerance
            }

            # Try different endpoint patterns
            endpoints_to_try = [
                f"{self.base_url}/vault/{vault_address}/deposit",
                f"{self.base_url}/api/vault/{vault_address}/deposit",
                f"{self.base_url}/v1/vault/{vault_address}/deposit"
            ]

            for endpoint in endpoints_to_try:
                try:
                    response = self.session.post(
                        endpoint,
                        json=data,
                        params={'network': self.network},
                        timeout=30
                    )
                    response.raise_for_status()
                    return response.json()

                except requests.HTTPError as e:
                    if e.response.status_code == 404:
                        continue  # Try next endpoint
                    else:
                        raise

            raise ValueError(f"Deposit endpoint not found for vault: {vault_address}")

        except Exception as e:
            raise ValueError(f"Error building deposit transaction: {str(e)}")

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
                params={'network': self.network},
                timeout=30
            )
            response.raise_for_status()
            return response.json()

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