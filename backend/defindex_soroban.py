#!/usr/bin/env python3
"""
DeFindex integration using Soroban smart contracts
"""

import logging
from typing import Dict, List, Optional
from stellar_sdk import Server
from stellar_sdk.soroban_server import SorobanServer
from stellar_ssl import create_soroban_client_with_ssl

logger = logging.getLogger(__name__)

# Real DeFindex contract addresses from GitHub
MAINNET_VAULTS = {
    'USDC_Blend_Fixed': 'CDB2WMKQQNVZMEBY7Q7GZ5C7E7IAFSNMZ7GGVD6WKTCEWK7XOIAVZSAP',
    'USDC_Blend_Yieldblox': 'CCSRX5E4337QMCMC3KO3RDFYI57T5NZV5XB3W3TWE4USCASKGL5URKJL',
    'USDC_Palta': 'CCFWKCD52JNSQLN5OS4F7EG6BPDT4IRJV6KODIEIZLWPM35IKHOKT6S2',
    'EURC_Blend_Fixed': 'CC5CE6MWISDXT3MLNQ7R3FVILFVFEIH3COWGH45GJKL6BD2ZHF7F7JVI',
    'EURC_Blend_Yieldblox': 'CA33NXYN7H3EBDSA3U2FPSULGJTTL3FQRHD2ADAAPTKS3FUJOE73735A',
    'XLM_Blend_Fixed': 'CDPWNUW7UMCSVO36VAJSQHQECISPJLCVPDASKHRC5SEROAAZDUQ5DG2Z',
    'XLM_Blend_Yieldblox': 'CBDOIGFO2QOOZTWQZ7AFPH5JOUS2SBN5CTTXR665NHV6GOCM6OUGI5KP',
    'Cetes': 'CBTSRJLN5CVVOWLTH2FY5KNQ47KW5KKU3VWGASDN72STGMXLRRNHPRIL',
    'Aqua': 'CCMJUJW6Z7I3TYDCJFGTI3A7QA3ASMYAZ5PSRRWBBIJQPKI2GXL5DW5D',
    'Ustry': 'CDDXPBOF727FDVTNV4I3G4LL4BHTJHE5BBC4W6WZAHMUPFDPBQBL6K7Y',
    'USDglo': 'CCTLQXYSIUN3OSZLZ7O7MIJC6YCU3QLLS6TUM3P2CD6DAVELMWC3QV4E'
}

TESTNET_VAULTS = {
    'XLM_HODL_1': 'CAHWRPKBPX4FNLXZOAD565IBSICQPL5QX37IDLGJYOPWX22WWKFWQUBA',
    'XLM_HODL_2': 'CCSPRGGUP32M23CTU7RUAGXDNOHSA6O2BS2IK4NVUP5X2JQXKTSIQJKE',
    'XLM_HODL_3': 'CBLXUUHUL7TA3LF3U5G6ZTU7EACBBOSJLR4AYOM5YJKJ4APZ7O547R5T',
    'XLM_HODL_4': 'CCGKL6U2DHSNFJ3NU4UPRUKYE2EUGYR4ZFZDYA7KDJLP3TKSPHD5C4UP'
}

# Mock APY data for demonstration (in a real implementation, this would come from on-chain data or oracle)
MOCK_APY_DATA = {
    'USDC_Blend_Fixed': 45.2,
    'USDC_Blend_Yieldblox': 52.8,
    'USDC_Palta': 38.5,
    'EURC_Blend_Fixed': 42.1,
    'EURC_Blend_Yieldblox': 48.7,
    'XLM_Blend_Fixed': 35.4,
    'XLM_Blend_Yieldblox': 41.2,
    'Cetes': 28.9,
    'Aqua': 33.7,
    'Ustry': 31.5,
    'USDglo': 29.8
}

class DeFindexSoroban:
    """DeFindex integration using Soroban smart contracts"""

    def __init__(self, network: str = "mainnet"):
        self.network = network
        if network == "mainnet":
            self.horizon = Server("https://horizon.stellar.org")
            self.soroban = create_soroban_client_with_ssl("https://mainnet.stellar.expert/explorer/rpc")
            self.vaults = MAINNET_VAULTS
        else:
            self.horizon = Server("https://horizon-testnet.stellar.org")
            self.soroban = create_soroban_client_with_ssl("https://soroban-testnet.stellar.org")
            self.vaults = TESTNET_VAULTS

    async def get_available_vaults(self, min_apy: float = 30.0) -> List[Dict]:
        """Get available vaults with their APY data"""
        vaults_data = []

        # Use mainnet data for APY information
        apy_source = MOCK_APY_DATA if self.network == "testnet" else MOCK_APY_DATA

        for name, address in (MAINNET_VAULTS.items() if self.network == "mainnet" else TESTNET_VAULTS.items()):
            apy = apy_source.get(name.replace('XLM_HODL_', 'XLM_Blend_'), 0)

            if apy >= min_apy:
                vaults_data.append({
                    'name': name.replace('_', ' '),
                    'address': address,
                    'apy': apy,
                    'tvl': 1000000 + hash(name) % 5000000,  # Mock TVL data
                    'symbol': name.split('_')[0] if '_' in name else 'XLM',
                    'network': self.network
                })

        # Sort by APY descending
        vaults_data.sort(key=lambda v: v['apy'], reverse=True)
        return vaults_data

    async def get_vault_details(self, vault_address: str) -> Dict:
        """Get detailed information about a vault"""
        # Find vault name from address
        vault_name = None
        for name, address in MAINNET_VAULTS.items():
            if address == vault_address:
                vault_name = name
                break

        if not vault_name:
            raise ValueError(f"Vault not found: {vault_address}")

        apy = MOCK_APY_DATA.get(vault_name, 0)

        return {
            'name': vault_name.replace('_', ' '),
            'address': vault_address,
            'apy': apy,
            'tvl': 1000000 + hash(vault_name) % 5000000,
            'symbol': vault_name.split('_')[0] if '_' in vault_name else 'XLM',
            'strategies': [
                {'name': f'{vault_name.split("_")[1]} Strategy', 'paused': False, 'description': 'Automated yield generation'}
            ],
            'historical_apy': {
                '1m': apy * 0.95,
                '3m': apy * 1.05,
                '1y': apy * 1.12
            }
        }

    def build_deposit_transaction(
        self,
        vault_address: str,
        amount_stroops: int,
        user_address: str
    ) -> Dict:
        """Build a demo deposit transaction for testnet purposes

        This creates a simple XLM payment to a testnet address to demonstrate
        the wallet signing flow. The vault_address parameter is used for metadata
        only - the actual transaction sends to a known testnet account.
        """
        from stellar_sdk import TransactionBuilder, Network, Account
        from stellar_sdk.operation import Payment
        from stellar_sdk import Asset

        # Use a valid testnet destination (Stellar testnet friendbot address)
        # This ensures the transaction is always valid for demo purposes
        demo_destination = 'GAIH3ULLFQ4DGSECF2AR555KZ4KNDGEKN4AFI4SU2M7B43MGK3QJZNSR'

        try:
            # Fetch user account from network to get sequence number
            account = self.horizon.accounts().account_id(user_address).call()
            sequence = int(account['sequence'])  # Convert sequence to int
            source_account = Account(user_address, sequence)

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
                    amount=f"{amount_xlm:.7f}",  # Format as string with 7 decimal places
                    asset=Asset.native(),
                )
                .set_timeout(300)  # 5 minute timeout
                .add_text_memo(f"Demo deposit to {vault_address[:8]}...")
                .build()
            )

            # Get XDR
            xdr = transaction.to_xdr()

            return {
                'xdr': xdr,
                'description': f'🎭 DEMO: Deposit {amount_xlm:.2f} XLM to DeFindex vault (testnet simulation)',
                'amount': amount_xlm,
                'estimated_shares': str(int(amount_stroops * 0.95)),  # Mock share calculation
                'vault_address': vault_address,  # Original mainnet vault for reference
                'demo_destination': demo_destination,
                'user_address': user_address,
                'note': 'This is a testnet demo transaction that simulates a mainnet vault deposit'
            }

        except Exception as e:
            logger.error(f"Error building deposit transaction: {e}")
            raise ValueError(f"Could not build demo transaction: {str(e)}")

def get_defindex_soroban(network: str = 'mainnet') -> DeFindexSoroban:
    """Get DeFindex Soroban client"""
    return DeFindexSoroban(network=network)