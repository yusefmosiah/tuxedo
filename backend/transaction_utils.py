#!/usr/bin/env python3
"""
Transaction signing utilities for autonomous DeFindex operations
"""

import logging
from typing import Optional
from stellar_sdk.transaction_envelope import TransactionEnvelope
from stellar_sdk.network import Network
from stellar_sdk.keypair import Keypair

logger = logging.getLogger(__name__)

def sign_transaction_with_agent_key(unsigned_xdr: str, agent_keypair: Keypair, network: str = "mainnet") -> str:
    """
    Sign a transaction XDR with agent keypair for autonomous execution (MAINNET ONLY).

    Args:
        unsigned_xdr: Unsigned transaction XDR from DeFindex API
        agent_keypair: Agent's Keypair object for signing
        network: Network to use (always 'mainnet' in this version)

    Returns:
        Signed transaction XDR ready for submission
    """
    try:
        # Get network passphrase
        network_passphrase = create_transaction_builder_for_network(network)

        # Parse the unsigned XDR
        envelope = TransactionEnvelope.from_xdr(unsigned_xdr, network_passphrase=network_passphrase)

        # Sign with agent keypair
        envelope.sign(agent_keypair)

        # Return signed XDR
        return envelope.to_xdr()

    except Exception as e:
        logger.error(f"Failed to sign transaction: {e}")
        raise ValueError(f"Transaction signing failed: {str(e)}")

def create_transaction_builder_for_network(network: str = "mainnet"):
    """
    Create a transaction builder configured for the specified network (MAINNET ONLY).

    Args:
        network: Network to use (always 'mainnet' in this version)

    Returns:
        Network object for transaction building
    """
    # Mainnet-only configuration
    return Network.PUBLIC_NETWORK_PASSPHRASE

def validate_transaction_amount(amount_xlm: float, min_balance: float = 1.0) -> bool:
    """
    Validate transaction amount meets minimum requirements.

    Args:
        amount_xlm: Amount in XLM
        min_balance: Minimum balance required

    Returns:
        True if amount is valid
    """
    return amount_xlm >= min_balance and amount_xlm > 0