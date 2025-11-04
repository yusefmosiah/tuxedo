#!/usr/bin/env python3
"""
DeFindex Testnet Vault Creation Helper

This script helps create DeFindex vaults on Stellar testnet using the factory API.
Note: Valid strategy addresses are required for vault creation.
"""

import os
import sys
import json
import time
import logging
from dotenv import load_dotenv
import requests

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment
sys.path.insert(0, '.')
load_dotenv()

class DeFindexVaultCreator:
    """Helper class for creating DeFindex vaults on testnet"""

    def __init__(self):
        self.api_key = os.getenv('DEFINDEX_API_KEY')
        self.base_url = os.getenv('DEFINDEX_BASE_URL', 'https://api.defindex.io')

        if not self.api_key:
            raise ValueError("DEFINDEX_API_KEY not set in environment")

        self.session = requests.Session()
        self.session.headers.update({
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        })

    def test_connection(self):
        """Test API connection"""
        try:
            response = self.session.get(f"{self.base_url}/health", timeout=10)
            return response.status_code == 200
        except Exception as e:
            logger.error(f"Connection test failed: {e}")
            return False

    def create_vault(self, config: dict) -> dict:
        """
        Create a DeFindex vault using the factory API

        Args:
            config: Vault configuration dictionary

        Returns:
            Creation response or error information
        """
        if not self.test_connection():
            return {"error": "API connection failed"}

        try:
            logger.info("Creating vault with configuration...")
            logger.info(f"Vault: {config.get('name_symbol', {}).get('name', 'Unknown')}")

            response = self.session.post(
                f"{self.base_url}/factory/create-vault",
                json=config,
                timeout=60
            )

            if response.status_code == 200:
                result = response.json()
                logger.info("✅ Vault created successfully!")
                return {
                    "success": True,
                    "data": result
                }
            elif response.status_code == 400:
                error_data = response.json()
                logger.error(f"❌ Validation error: {error_data.get('message', 'Unknown error')}")
                return {
                    "success": False,
                    "error": "validation",
                    "details": error_data
                }
            elif response.status_code == 429:
                logger.warning("⚠️ Rate limited - please wait")
                return {
                    "success": False,
                    "error": "rate_limited",
                    "message": "Too many requests - please wait before trying again"
                }
            else:
                logger.error(f"❌ Unexpected error: {response.status_code}")
                return {
                    "success": False,
                    "error": "api_error",
                    "status": response.status_code,
                    "message": response.text
                }

        except Exception as e:
            logger.error(f"❌ Exception during vault creation: {e}")
            return {
                "success": False,
                "error": "exception",
                "message": str(e)
            }

def create_sample_vault_config(caller_address: str, strategy_address: str = None) -> dict:
    """
    Create a sample vault configuration

    Args:
        caller_address: Stellar address of the vault creator
        strategy_address: Valid strategy contract address (required!)

    Returns:
        Vault configuration dictionary
    """
    config = {
        'roles': {
            '0': caller_address,  # Emergency Manager
            '1': caller_address,  # Fee Receiver
            '2': caller_address,  # Vault Manager
            '3': caller_address   # Rebalance Manager
        },
        'vault_fee_bps': 100,  # 1% fee
        'assets': [{
            'address': 'CDLZFC3SYJYDZT7K67VZ75HPJVIEUVNIXF47ZG2FB2RMQQVU2HHGCYSC',  # XLM on testnet
            'strategies': []
        }],
        'name_symbol': {
            'name': 'Tuxedo Test XLM Vault',
            'symbol': 'tXLM'
        },
        'upgradable': True,
        'caller': caller_address,
        'network': 'testnet'
    }

    # Add strategy if provided
    if strategy_address:
        config['assets'][0]['strategies'].append({
            'address': strategy_address,
            'name': 'Test Strategy',
            'paused': False
        })

    return config

def main():
    """Main vault creation example"""
    print("🏗️  DeFindex Vault Creation Helper")
    print("=" * 50)

    # Initialize creator
    try:
        creator = DeFindexVaultCreator()
        print("✅ API connection initialized")
    except Exception as e:
        print(f"❌ Initialization failed: {e}")
        return

    # Test connection
    if not creator.test_connection():
        print("❌ API connection test failed")
        return
    print("✅ API connection test passed")

    # Sample configuration (needs valid strategy address)
    caller_address = "GD5PM5BJYECMWFKXE2GF6L6WXXYPJ3CFO6R5VKJCEKRFSZXCZQTHWARF"

    print("\n📋 Vault Creation Requirements:")
    print("1. ✅ Valid API key")
    print("2. ✅ Valid caller address")
    print("3. ❌ VALID STRATEGY ADDRESS (REQUIRED)")
    print("\n⚠️  To create a vault, you need a valid strategy contract address.")
    print("   Contact DeFindex team or check their documentation for available strategies.")

    # Show what would be sent
    config = create_sample_vault_config(caller_address)

    print(f"\n📄 Sample Configuration (missing valid strategy):")
    print(json.dumps(config, indent=2))

    print(f"\n🔗 API Endpoint: {creator.base_url}/factory/create-vault")
    print("📖 Method: POST")
    print("🔐 Authentication: Bearer token")

if __name__ == "__main__":
    main()