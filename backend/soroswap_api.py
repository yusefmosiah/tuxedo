"""
Soroswap API Client
Provides integration with Soroswap API for quotes and routing on Stellar mainnet.

Soroswap is the first DEX and exchange aggregator built on Stellar, powered by Soroban smart contracts.
"""

import asyncio
import aiohttp
from typing import Dict, Any, Optional, List
import json
import logging
from urllib.parse import urljoin

logger = logging.getLogger(__name__)


class SoroswapAPIClient:
    """Client for interacting with Soroswap API"""

    def __init__(self, base_url: str = "https://api.soroswap.finance"):
        self.base_url = base_url
        self.session = None

    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()

    async def _make_request(self, endpoint: str, params: Optional[Dict] = None) -> Dict[str, Any]:
        """Make HTTP request to Soroswap API"""
        if not self.session:
            raise RuntimeError("Client not initialized. Use async context manager.")

        url = urljoin(self.base_url, endpoint)

        logger.info(f"🔗 Soroswap API request: {url}")
        if params:
            logger.info(f"📋 Parameters: {params}")

        try:
            async with self.session.get(url, params=params, timeout=aiohttp.ClientTimeout(total=10)) as response:
                status = response.status
                logger.info(f"📡 Soroswap API response status: {status}")

                if status == 404:
                    raise Exception(f"Soroswap API request failed: {status}, message='Not Found', url='{url}'")

                response.raise_for_status()
                result = await response.json()
                logger.info(f"✅ Soroswap API response received")
                return result
        except aiohttp.ClientError as e:
            logger.error(f"❌ Soroswap API error: {e}")
            raise Exception(f"Soroswap API request failed: {str(e)}")
        except asyncio.TimeoutError:
            logger.error(f"⏱️  Soroswap API timeout")
            raise Exception(f"Soroswap API request timed out after 10 seconds")

    async def get_contracts(self, network: str = "mainnet") -> Dict[str, str]:
        """Get contract addresses for specified network"""
        return await self._make_request(f"/api/{network}/contracts")

    async def get_quote(
        self,
        token_in: str,
        token_out: str,
        amount_in: str,
        network: str = "mainnet"
    ) -> Dict[str, Any]:
        """
        Get swap quote from Soroswap

        Args:
            token_in: Input token contract address or "native" for XLM
            token_out: Output token contract address
            amount_in: Amount to swap (in smallest units)
            network: Network (mainnet/testnet)
        """
        params = {
            "tokenIn": token_in,
            "tokenOut": token_out,
            "amountIn": amount_in
        }

        return await self._make_request(f"/api/{network}/quote", params)

    async def build_transaction(
        self,
        token_in: str,
        token_out: str,
        amount_in: str,
        slippage: float = 0.5,
        deadline: int = 3600,
        network: str = "mainnet"
    ) -> Dict[str, Any]:
        """
        Build transaction for swap

        Args:
            token_in: Input token contract address or "native"
            token_out: Output token contract address
            amount_in: Amount to swap
            slippage: Slippage tolerance in percent (default 0.5%)
            deadline: Transaction deadline in seconds (default 1 hour)
            network: Network (mainnet/testnet)
        """
        params = {
            "tokenIn": token_in,
            "tokenOut": token_out,
            "amountIn": amount_in,
            "slippage": str(slippage),
            "deadline": str(deadline)
        }

        return await self._make_request(f"/api/{network}/quote/build", params)

    async def get_pools(self, network: str = "mainnet") -> List[Dict[str, Any]]:
        """Get all available pools"""
        return await self._make_request(f"/api/{network}/pools")

    async def get_pool_info(self, pool_address: str, network: str = "mainnet") -> Dict[str, Any]:
        """Get specific pool information"""
        return await self._make_request(f"/api/{network}/pool/{pool_address}")
