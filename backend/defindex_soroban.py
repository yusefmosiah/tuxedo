#!/usr/bin/env python3
"""
DeFindex integration using Soroban smart contracts
"""

import logging
import asyncio
from typing import Dict, List, Optional
from stellar_sdk import Server
from stellar_sdk.soroban_server import SorobanServer
# from stellar_ssl import create_soroban_client_with_ssl  # Temporarily disabled for testing

logger = logging.getLogger(__name__)

# Real DeFindex contract addresses from official docs (Updated 2025-11-04)
MAINNET_VAULTS = {
    'USDC_Blend_Fixed': 'CDB2WMKQQNVZMEBY7Q7GZ5C7E7IAFSNMZ7GGVD6WKTCEWK7XOIAVZSAP',
    'USDC_Blend_Yieldblox': 'CCSRX5E4337QMCMC3KO3RDFYI57T5NZV5XB3W3TWE4USCASKGL5URKJL',
    'EURC_Blend_Fixed': 'CC5CE6MWISDXT3MLNQ7R3FVILFVFEIH3COWGH45GJKL6BD2ZHF7F7JVI',
    'EURC_Blend_Yieldblox': 'CA33NXYN7H3EBDSA3U2FPSULGJTTL3FQRHD2ADAAPTKS3FUJOE73735A',
    'XLM_Blend_Fixed': 'CDPWNUW7UMCSVO36VAJSQHQECISPJLCVPDASKHRC5SEROAAZDUQ5DG2Z',
    'XLM_Blend_Yieldblox': 'CBDOIGFO2QOOZTWQZ7AFPH5JOUS2SBN5CTTXR665NHV6GOCM6OUGI5KP'
}

# Testnet vaults - ONLY real testnet HODL vaults (verified working)
# NOTE: Mainnet vault addresses do NOT work on testnet (MissingValue errors)
TESTNET_VAULTS = {
    # Real testnet HODL vaults (0% APY - just hold XLM)
    # These are verified working testnet contracts
    'XLM_HODL_1': 'CAHWRPKBPX4FNLXZOAD565IBSICQPL5QX37IDLGJYOPWX22WWKFWQUBA',
    'XLM_HODL_2': 'CCSPRGGUP32M23CTU7RUAGXDNOHSA6O2BS2IK4NVUP5X2JQXKTSIQJKE',
    'XLM_HODL_3': 'CBLXUUHUL7TA3LF3U5G6ZTU7EACBBOSJLR4AYOM5YJKJ4APZ7O547R5T',
    'XLM_HODL_4': 'CCGKL6U2DHSNFJ3NU4UPRUKYE2EUGYR4ZFZDYA7KDJLP3TKSPHD5C4UP'
}

# Removed: REALISTIC_APY_DATA - now fetched from DeFindex API

class DeFindexSoroban:
    """DeFindex integration using Soroban smart contracts"""

    def __init__(self, network: str = "mainnet"):
        self.network = network
        if network == "mainnet":
            self.horizon = Server("https://horizon.stellar.org")
            # self.soroban = create_soroban_client_with_ssl("https://mainnet.stellar.expert/explorer/rpc")  # Temporarily disabled
            self.vaults = MAINNET_VAULTS
        else:
            self.horizon = Server("https://horizon-testnet.stellar.org")
            # self.soroban = create_soroban_client_with_ssl("https://soroban-testnet.stellar.org")  # Temporarily disabled
            self.vaults = TESTNET_VAULTS

        # Initialize API client for real data
        self.api_client = None
        try:
            from defindex_client import get_defindex_client
            self.api_client = get_defindex_client(network)
            logger.info(f"DeFindex API client initialized for {network}")
        except Exception as e:
            logger.warning(f"Failed to initialize DeFindex API client: {e}")
            self.api_client = None

    async def get_available_vaults(self, min_apy: float = 15.0) -> List[Dict]:
        """Get available vaults with their real APY and TVL data"""
        vaults_data = []

        # Use appropriate vaults for the network
        vaults_to_use = self.vaults
        vault_addresses = list(vaults_to_use.values())

        # Try to get real data from API first with rate limiting
        real_vault_data = {}
        if self.api_client:
            try:
                import time
                logger.info("Fetching vault data from API with rate limiting...")

                # Get vault info and APY data from API with delays
                api_vaults = self.api_client.get_vaults(vault_addresses)

                for i, vault_info in enumerate(api_vaults):
                    address = vault_info.get('address')
                    if address:
                        real_vault_data[address] = vault_info

                        # Rate limiting: Add delay between API calls
                        if i > 0:  # No delay for first call
                            time.sleep(0.5)  # 500ms delay between calls

                        # Try to get APY data separately for more accurate info
                        try:
                            apy_data = self.api_client.get_vault_apy(address)
                            real_vault_data[address]['apy'] = apy_data.get('apy', 0)
                        except Exception as e:
                            logger.debug(f"Could not get APY for {address}: {e}")
                            real_vault_data[address]['apy'] = vault_info.get('apy', 0)

            except Exception as e:
                logger.error(f"Failed to get vault data from API: {e}")
                raise ValueError(f"Unable to fetch vault data from DeFindex API: {str(e)}. Please check DEFINDEX_API_KEY and network connectivity.")

        # Require API client - no fallback data
        if not self.api_client:
            raise ValueError("DeFindex API client not available - cannot fetch vault data. Please set DEFINDEX_API_KEY environment variable.")

        # Process vaults with real API data only
        for name, address in vaults_to_use.items():
            vault_info = real_vault_data.get(address)

            if not vault_info:
                # Skip vaults without API data
                logger.warning(f"Skipping vault {name} ({address}) - no API data available")
                continue

            # Use real data from API only
            apy = vault_info.get('apy', 0)
            tvl = vault_info.get('tvl', 0)

            # Extract real symbol and strategy
            symbol = vault_info.get('symbol', name.split('_')[0])
            strategy = vault_info.get('strategy', name.split('_')[1] if '_' in name else 'HODL')
            asset_type = vault_info.get('asset_type',
                'stablecoin' if symbol in ['USDC', 'EURC', 'USDglo'] else
                'volatile' if symbol == 'XLM' else 'tokenized')

            # Filter by minimum APY
            if apy >= min_apy:
                vaults_data.append({
                    'name': name.replace('_', ' '),
                    'address': address,
                    'apy': apy,
                    'tvl': tvl,
                    'symbol': symbol,
                    'network': self.network,
                    'strategy': strategy,
                    'asset_type': asset_type,
                    'data_source': 'api'
                })

        # Sort by APY descending, then by TVL descending
        vaults_data.sort(key=lambda v: (v['apy'], v['tvl']), reverse=True)

        if not vaults_data:
            raise ValueError(f"No vault data available from API. Please check DEFINDEX_API_KEY and network connectivity.")

        logger.info(f"Returning {len(vaults_data)} vaults from API only (no fallback data)")
        return vaults_data

    async def get_vault_details(self, vault_address: str) -> Dict:
        """Get detailed information about a vault using real API data"""
        # Find vault name from address (check both mainnet and testnet)
        vault_name = None
        all_vaults = {**MAINNET_VAULTS, **TESTNET_VAULTS}
        for name, address in all_vaults.items():
            if address == vault_address:
                vault_name = name
                break

        if not vault_name:
            raise ValueError(f"Vault not found: {vault_address}")

        # Require API client - no fallback data
        if not self.api_client:
            raise ValueError("DeFindex API client not available - cannot fetch vault details. Please set DEFINDEX_API_KEY environment variable.")

        # Get real data from API
        vault_info = {}
        try:
            vault_info = self.api_client.get_vault_info(vault_address)

            # Try to get APY data separately for more accurate info
            try:
                apy_data = self.api_client.get_vault_apy(vault_address)
                vault_info['apy'] = apy_data.get('apy', 0)
            except Exception as e:
                logger.debug(f"Could not get APY for {vault_address}: {e}")
                vault_info['apy'] = vault_info.get('apy', 0)

            logger.info(f"Retrieved real vault data for {vault_name}")
        except Exception as e:
            logger.error(f"Failed to get vault details from API for {vault_name}: {e}")
            raise ValueError(f"Unable to fetch vault details from DeFindex API: {str(e)}. Please check DEFINDEX_API_KEY and network connectivity.")

        if vault_info:
            # Use real data from API
            apy = vault_info.get('apy', 0)
            tvl = vault_info.get('tvl', 0)
            symbol = vault_info.get('symbol', vault_name.split('_')[0])
            strategy = vault_info.get('strategy', vault_name.split('_')[1] if '_' in vault_name else 'HODL')
            strategies = vault_info.get('strategies', [])
            historical_apy = vault_info.get('historical_apy', {})
            asset_type = vault_info.get('asset_type',
                'stablecoin' if symbol in ['USDC', 'EURC', 'USDglo'] else
                'volatile' if symbol == 'XLM' else 'tokenized')
            risk_level = vault_info.get('risk_level',
                'Low' if symbol in ['USDC', 'EURC'] else
                'Medium' if symbol == 'XLM' else 'High')
            min_deposit = vault_info.get('min_deposit', 100 if symbol in ['USDC', 'EURC'] else 1)
            fees = vault_info.get('fees', {
                'deposit': '0.1%',
                'withdrawal': '0.1%',
                'performance': '10% of profits'
            })

        else:
            # No API data available - fail with clear error
            raise ValueError(f"API data not available for vault {vault_name}. Please set DEFINDEX_API_KEY environment variable and check network connectivity.")

        return {
            'name': vault_name.replace('_', ' '),
            'address': vault_address,
            'apy': apy,
            'tvl': tvl,
            'symbol': symbol,
            'strategies': strategies,
            'historical_apy': historical_apy,
            'asset_type': asset_type,
            'risk_level': risk_level,
            'min_deposit': min_deposit,
            'fees': fees,
            'data_source': 'api'
        }

    def build_deposit_transaction(
        self,
        vault_address: str,
        amount_stroops: int,
        user_address: str
    ) -> Dict:
        """Build a REAL deposit transaction using DeFindex API ONLY.

        NO DEMO TRANSACTIONS - fails if API unavailable.
        """
        # Require API client - no fallbacks
        if not self.api_client:
            raise ValueError("DeFindex API client not available - cannot build real transactions")

        try:
            logger.info(f"Building REAL deposit transaction for vault {vault_address[:8]}...")
            logger.info(f"Amount: {amount_stroops / 10_000_000:.2f} XLM, User: {user_address[:8]}...")

            # Build REAL deposit transaction via API
            tx_data = self.api_client.build_deposit_transaction(
                vault_address=vault_address,
                amount_stroops=amount_stroops,
                caller=user_address,
                invest=True
            )

            amount_xlm = amount_stroops / 10_000_000
            logger.info(f"✅ Successfully built REAL deposit transaction")

            return {
                'xdr': tx_data.get('xdr', ''),
                'description': f'✅ REAL: Deposit {amount_xlm:.2f} XLM to DeFindex vault',
                'amount': amount_xlm,
                'estimated_shares': tx_data.get('estimated_shares', str(int(amount_stroops * 0.95))),
                'vault_address': vault_address,
                'user_address': user_address,
                'transaction_data': tx_data,
                'data_source': 'api'
            }

        except Exception as e:
            logger.error(f"Failed to build real deposit transaction: {e}")
            logger.error(f"Vault address: {vault_address}, Network: {self.network}")
            raise ValueError(f"Cannot build real deposit transaction: {str(e)}")

    # DEMO TRANSACTION METHODS REMOVED - ONLY REAL TRANSACTIONS SUPPORTED

def get_defindex_soroban(network: str = 'mainnet') -> DeFindexSoroban:
    """Get DeFindex Soroban client"""
    return DeFindexSoroban(network=network)