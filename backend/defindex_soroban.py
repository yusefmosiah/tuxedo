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

# Testnet vaults - real addresses discovered from Blend protocol
# Note: Limited testnet vault availability - these are primarily XLM HODL vaults
TESTNET_VAULTS = {
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

        # Try to get real data from API first
        real_vault_data = {}
        if self.api_client:
            try:
                # Get vault info and APY data from API
                api_vaults = self.api_client.get_vaults(vault_addresses)
                for vault_info in api_vaults:
                    address = vault_info.get('address')
                    if address:
                        real_vault_data[address] = vault_info

                        # Try to get APY data separately for more accurate info
                        try:
                            apy_data = self.api_client.get_vault_apy(address)
                            real_vault_data[address]['apy'] = apy_data.get('apy', 0)
                        except Exception as e:
                            logger.debug(f"Could not get APY for {address}: {e}")
                            real_vault_data[address]['apy'] = vault_info.get('apy', 0)

            except Exception as e:
                logger.warning(f"Failed to get vault data from API: {e}")

        # Process vaults with real or fallback data
        for name, address in vaults_to_use.items():
            vault_info = real_vault_data.get(address, {})

            if vault_info:
                # Use real data from API
                apy = vault_info.get('apy', 0)
                tvl = vault_info.get('tvl', 0)

                # Extract real symbol and strategy
                symbol = vault_info.get('symbol', name.split('_')[0])
                strategy = vault_info.get('strategy', name.split('_')[1] if '_' in name else 'HODL')
                asset_type = vault_info.get('asset_type',
                    'stablecoin' if symbol in ['USDC', 'EURC', 'USDglo'] else
                    'volatile' if symbol == 'XLM' else 'tokenized')

            else:
                # Fallback to basic data if API fails
                logger.warning(f"Using fallback data for vault {name} ({address})")
                apy = 0  # No APY data available without API
                tvl = 0  # No TVL data available without API
                symbol = name.split('_')[0]
                strategy = name.split('_')[1] if '_' in name else 'HODL'
                asset_type = 'stablecoin' if symbol in ['USDC', 'EURC', 'USDglo'] else 'volatile' if symbol == 'XLM' else 'tokenized'

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
                    'data_source': 'api' if vault_info else 'fallback'
                })

        # Sort by APY descending, then by TVL descending
        vaults_data.sort(key=lambda v: (v['apy'], v['tvl']), reverse=True)

        # Log data source summary
        api_count = sum(1 for v in vaults_data if v.get('data_source') == 'api')
        fallback_count = len(vaults_data) - api_count
        logger.info(f"Returning {len(vaults_data)} vaults: {api_count} from API, {fallback_count} from fallback")

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

        # Try to get real data from API first
        vault_info = {}
        if self.api_client:
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
                logger.warning(f"Failed to get vault details from API for {vault_name}: {e}")

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
            # Fallback to basic data if API fails
            logger.warning(f"Using fallback data for vault details: {vault_name}")
            apy = 0
            tvl = 0
            symbol = vault_name.split('_')[0]
            strategy = vault_name.split('_')[1] if '_' in vault_name else 'HODL'
            strategies = [{'name': f'{strategy} Strategy', 'paused': False, 'description': 'Data unavailable - API required'}]
            historical_apy = {'1m': 0, '3m': 0, '1y': 0}
            asset_type = 'stablecoin' if symbol in ['USDC', 'EURC', 'USDglo'] else 'volatile' if symbol == 'XLM' else 'tokenized'
            risk_level = 'Low' if symbol in ['USDC', 'EURC'] else 'Medium' if symbol == 'XLM' else 'High'
            min_deposit = 100 if symbol in ['USDC', 'EURC'] else 1
            fees = {
                'deposit': '0.1%',
                'withdrawal': '0.1%',
                'performance': '10% of profits'
            }

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
            'data_source': 'api' if vault_info else 'fallback'
        }

    def build_deposit_transaction(
        self,
        vault_address: str,
        amount_stroops: int,
        user_address: str
    ) -> Dict:
        """Build a real deposit transaction using DeFindex API

        If API is available, builds a real vault deposit transaction.
        Falls back to demo transaction for testnet if API fails.
        """
        # Try to use real API client first
        if self.api_client:
            try:
                logger.info(f"Attempting to build REAL deposit transaction for vault {vault_address[:8]}...")
                logger.info(f"Amount: {amount_stroops / 10_000_000:.2f} XLM, User: {user_address[:8]}...")

                # Build real deposit transaction via API
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
                logger.warning(f"Failed to build real deposit transaction: {e}")
                logger.warning(f"Vault address: {vault_address}")
                logger.warning(f"This might be a mainnet vault on testnet network or API connectivity issue")
                logger.info("Falling back to demo transaction")

        else:
            logger.warning("DeFindex API client not available - using demo transaction")

        # Fallback to demo transaction
        return self._build_demo_transaction(vault_address, amount_stroops, user_address)

    def _build_demo_transaction(self, vault_address: str, amount_stroops: int, user_address: str) -> Dict:
        """Build a demo deposit transaction for testnet purposes

        This creates a simple XLM payment to demonstrate the wallet signing flow.
        The vault_address parameter is used for metadata only.
        """
        from stellar_sdk import TransactionBuilder, Network, Account
        from stellar_sdk.operation import Payment
        from stellar_sdk import Asset
        from stellar_sdk.exceptions import NotFoundError

        # Use a valid testnet destination (Stellar testnet friendbot address)
        demo_destination = 'GAIH3ULLFQ4DGSECF2AR555KZ4KNDGEKN4AFI4SU2M7B43MGK3QJZNSR'

        try:
            # Fetch user account from network to get sequence number
            try:
                account = self.horizon.accounts().account_id(user_address).call()
                sequence = int(account['sequence'])
                source_account = Account(user_address, sequence)
                logger.info(f"Successfully loaded account {user_address[:8]}... with sequence {sequence}")
            except Exception as e:
                logger.error(f"Account {user_address} not found on {self.network}: {e}")
                logger.info("Creating demo transaction without account validation")
                # Skip transaction building if account is invalid
                return self._create_simple_transaction_response(vault_address, amount_stroops, user_address)

            # Calculate amount in XLM
            amount_xlm = amount_stroops / 10_000_000

            # Build a simple payment transaction for demo
            transaction = (
                TransactionBuilder(
                    source_account=source_account,
                    network_passphrase=Network.TESTNET_NETWORK_PASSPHRASE,
                    base_fee=100000,  # 0.01 XLM base fee
                )
                .append_payment_op(
                    destination=demo_destination,
                    amount=f"{amount_xlm:.7f}",
                    asset=Asset.native(),
                )
                .set_timeout(300)  # 5 minute timeout
                .add_text_memo(f"Demo deposit to {vault_address[:8]}...")
                .build()
            )

            # Check if account was found and add appropriate note
            account_status = "valid" if 'account' in locals() and sequence != 1 else "not_found"

            return {
                'xdr': transaction.to_xdr(),
                'description': f'🎭 DEMO: Deposit {amount_xlm:.2f} XLM to DeFindex vault (testnet simulation)',
                'amount': amount_xlm,
                'estimated_shares': str(int(amount_stroops * 0.95)),
                'vault_address': vault_address,
                'demo_destination': demo_destination,
                'user_address': user_address,
                'account_status': account_status,
                'data_source': 'demo',
                'note': 'This is a testnet demo transaction that simulates a vault deposit'
            }

        except Exception as e:
            logger.error(f"Error building demo transaction: {e}")
            # Fallback to simple response without real transaction
            return self._create_simple_transaction_response(vault_address, amount_stroops, user_address)

    def _create_simple_transaction_response(self, vault_address: str, amount_stroops: int, user_address: str) -> Dict:
        """Create a simple response when transaction building fails"""
        amount_xlm = amount_stroops / 10_000_000

        return {
            'xdr': '',
            'description': f'🎭 DEMO: Deposit {amount_xlm:.2f} XLM to DeFindex vault (simulation only)',
            'amount': amount_xlm,
            'estimated_shares': str(int(amount_stroops * 0.95)),
            'vault_address': vault_address,
            'demo_destination': 'N/A - account validation failed',
            'user_address': user_address,
            'account_status': 'invalid',
            'data_source': 'demo',
            'note': f'Account {user_address[:8]}... not found on {self.network} - demo simulation only'
        }

def get_defindex_soroban(network: str = 'mainnet') -> DeFindexSoroban:
    """Get DeFindex Soroban client"""
    return DeFindexSoroban(network=network)