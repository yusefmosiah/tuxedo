#!/usr/bin/env python3
"""
Blend Reserve APY Query - Version 2 (Using get_ledger_entries)

This version uses direct ledger entry queries instead of simulation,
which means NO ACCOUNT NEEDED! Much more efficient.

Key discovery: Reserves are stored with enum keys PoolDataKey::ResData(Address)
which encodes as a Vec of [Symbol("ResData"), Address(asset)]
"""

import json
import logging
from typing import Dict, Any
from stellar_sdk.soroban_server_async import SorobanServerAsync
from account_manager import AccountManager
from stellar_soroban import soroban_operations

logger = logging.getLogger(__name__)

NETWORK_CONFIG = {
    'passphrase': 'Public Global Stellar Network ; September 2015',
}


async def blend_get_reserve_apy_v2(
    pool_address: str,
    asset_address: str,
    user_id: str,
    soroban_server: SorobanServerAsync,
    account_manager: AccountManager,
    network: str = "mainnet"
) -> Dict[str, Any]:
    """
    Get reserve APY using get_ledger_entries (NO ACCOUNT NEEDED!)

    This version queries ledger entries directly using the storage key pattern:
    PoolDataKey::ResData(Address) -> Vec[Symbol("ResData"), Address(asset)]

    Args:
        pool_address: Pool contract ID
        asset_address: Asset contract ID
        user_id: User identifier (not used for queries, but required by soroban_operations)
        soroban_server: SorobanServerAsync instance
        account_manager: AccountManager instance
        network: "mainnet"

    Returns:
        Dictionary with APY and reserve metrics
    """
    try:
        logger.info(f"[V2] Fetching reserve data for {asset_address[:8]}... from pool {pool_address[:8]}...")

        # Construct ledger keys for ReserveData and ReserveConfig
        # Format: Vec of [Symbol("ResData"), Address(asset)]
        ledger_keys = [
            {
                "type": "contract_data",
                "contract_id": pool_address,
                "key": {
                    "vec": [
                        {"type": "symbol", "value": "ResData"},
                        {"type": "address", "value": asset_address}
                    ]
                },
                "durability": "PERSISTENT"
            },
            {
                "type": "contract_data",
                "contract_id": pool_address,
                "key": {
                    "vec": [
                        {"type": "symbol", "value": "ResConfig"},
                        {"type": "address", "value": asset_address}
                    ]
                },
                "durability": "PERSISTENT"
            }
        ]

        # Query ledger entries (NO ACCOUNT NEEDED!)
        result = await soroban_operations(
            action="get_ledger_entries",
            user_id=user_id,
            soroban_server=soroban_server,
            account_manager=account_manager,
            ledger_keys=ledger_keys,
            network_passphrase=NETWORK_CONFIG['passphrase']
        )

        if not result.get('success'):
            raise ValueError(f"Failed to get ledger entries: {result.get('error')}")

        entries = result.get('entries', [])
        if len(entries) < 2:
            raise ValueError(f"Expected 2 entries (ResData + ResConfig), got {len(entries)}")

        # Parse entries - order depends on which came back first
        reserve_data = None
        reserve_config = None

        for entry in entries:
            value = entry.get('value', {})
            # Check if this is ResData (has b_rate/d_rate) or ResConfig (has decimals)
            if 'b_rate' in value or 'd_rate' in value:
                reserve_data = value
            elif 'decimals' in value or 'index' in value:
                reserve_config = value

        if not reserve_data:
            raise ValueError("Could not find ReserveData in ledger entries")

        # Calculate APY from rates
        # Blend v2 uses 12 decimals (1e12) for b_rate/d_rate
        # These are cumulative exchange rates (e.g., 1.05e12 = 5% accumulated interest)
        b_rate = reserve_data.get('b_rate', 0)
        d_rate = reserve_data.get('d_rate', 0)

        logger.info(f"  b_rate (raw): {b_rate}")
        logger.info(f"  d_rate (raw): {d_rate}")

        # Convert to decimal and extract interest component
        supply_rate = b_rate / 1e12 if b_rate > 0 else 1.0
        supply_apr = supply_rate - 1 if supply_rate > 1 else 0
        supply_apy = ((1 + supply_apr / 365) ** 365 - 1) * 100

        borrow_rate = d_rate / 1e12 if d_rate > 0 else 1.0
        borrow_apr = borrow_rate - 1 if borrow_rate > 1 else 0
        borrow_apy = ((1 + borrow_apr / 365) ** 365 - 1) * 100

        # Calculate metrics
        total_supplied = reserve_data.get('b_supply', 0)
        total_borrowed = reserve_data.get('d_supply', 0)
        available = total_supplied - total_borrowed if total_supplied > total_borrowed else 0
        utilization = total_borrowed / total_supplied if total_supplied > 0 else 0

        # Get asset symbol (simple lookup)
        asset_symbol = _get_asset_symbol_simple(asset_address)

        logger.info(f"  Supply APY: {supply_apy:.2f}%")
        logger.info(f"  Borrow APY: {borrow_apy:.2f}%")

        return {
            'asset_address': asset_address,
            'asset_symbol': asset_symbol,
            'supply_apy': supply_apy,
            'borrow_apy': borrow_apy,
            'total_supplied': total_supplied,
            'total_borrowed': total_borrowed,
            'utilization': utilization,
            'available_liquidity': available,
            'data_source': 'ledger_entries_v2',
            'latest_ledger': result.get('latest_ledger'),
            'b_rate': b_rate,
            'd_rate': d_rate
        }

    except Exception as e:
        logger.error(f"Error in blend_get_reserve_apy_v2: {e}")
        raise ValueError(f"Failed to get reserve APY: {str(e)}")


def _get_asset_symbol_simple(asset_address: str) -> str:
    """Get asset symbol from known contracts"""
    known_assets = {
        'CCW67TSZV3SSS2HXMBQ5JFGCKJNXKZM7UQUWUZPUTHXSTZLEO7SJMI75': 'USDC',
        'CAS3J7GYLGXMF6TDJBBYYSE3HQ6BBSMLNUQ34T6TZMYMW2EVH34XOWMA': 'XLM',
        'CDMLFMKMMD7MWZP76FZCMGK3DQCV6VLPBR5DD2WWWKLBUQZLQJFUQJSK': 'wETH',
        'CBMR5J4LZ5QUCFPQQ6YWJ4UUQISOOJJGQ7IMQX36C2V7LC2EDNDODJ7F': 'wBTC',
        'CDCQP3LVDYYHVUIHW6BMVYJQWC7QPFTIZAYOQJYFHGFQHVNLTQAMV6TX': 'EURC',
        'CD25MNVTZDL4Y3XBCPCJXGXATV5WUHHOWMYFF4YBEGU5FCPGMYTVG5JY': 'BLND',
    }
    return known_assets.get(asset_address, f"{asset_address[:4]}...{asset_address[-4:]}")
