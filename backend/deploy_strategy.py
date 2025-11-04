#!/usr/bin/env python3
"""
DeFindex Strategy Deployment Helper

This script provides guidance and helper functions for deploying
DeFindex strategies to Stellar testnet.
"""

import os
import sys
import subprocess
import json
import logging
from pathlib import Path

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class StrategyDeployer:
    """Helper class for DeFindex strategy deployment"""

    def __init__(self):
        self.project_root = Path(__file__).parent
        self.defindex_dir = self.project_root / "defindex_repo"

    def check_prerequisites(self) -> dict:
        """Check if all prerequisites are installed"""
        prerequisites = {
            "rust": False,
            "soroban_cli": False,
            "stellar_cli": False,
            "git": False,
            "cargo": False
        }

        try:
            # Check Rust/Cargo
            result = subprocess.run(["cargo", "--version"], capture_output=True, text=True)
            if result.returncode == 0:
                prerequisites["rust"] = True
                prerequisites["cargo"] = True
                logger.info(f"✅ Rust/Cargo: {result.stdout.strip()}")
        except FileNotFoundError:
            logger.warning("❌ Rust/Cargo not found")

        try:
            # Check Soroban CLI
            result = subprocess.run(["soroban", "--version"], capture_output=True, text=True)
            if result.returncode == 0:
                prerequisites["soroban_cli"] = True
                logger.info(f"✅ Soroban CLI: {result.stdout.strip()}")
        except FileNotFoundError:
            logger.warning("❌ Soroban CLI not found")

        try:
            # Check Git
            result = subprocess.run(["git", "--version"], capture_output=True, text=True)
            if result.returncode == 0:
                prerequisites["git"] = True
                logger.info(f"✅ Git: {result.stdout.strip()}")
        except FileNotFoundError:
            logger.warning("❌ Git not found")

        return prerequisites

    def setup_development_environment(self) -> bool:
        """Guide through setting up the development environment"""
        logger.info("🚀 Setting up DeFindex Strategy Development Environment")

        # Step 1: Clone repository if not exists
        if not self.defindex_dir.exists():
            logger.info("📥 Cloning DeFindex repository...")
            try:
                subprocess.run([
                    "git", "clone",
                    "https://github.com/paltalabs/defindex.git",
                    str(self.defindex_dir)
                ], check=True)
                logger.info("✅ Repository cloned successfully")
            except subprocess.CalledProcessError as e:
                logger.error(f"❌ Failed to clone repository: {e}")
                return False
        else:
            logger.info("✅ Repository already exists")

        # Step 2: Navigate to contracts directory
        contracts_dir = self.defindex_dir / "apps" / "contracts"
        if not contracts_dir.exists():
            logger.error(f"❌ Contracts directory not found: {contracts_dir}")
            return False

        logger.info(f"📂 Contracts directory: {contracts_dir}")
        return True

    def create_custom_strategy(self, strategy_name: str, base_strategy: str = "hodl") -> bool:
        """Create a custom strategy based on an existing one"""
        logger.info(f"🏗️  Creating custom strategy: {strategy_name} based on {base_strategy}")

        strategies_dir = self.defindex_dir / "apps" / "contracts" / "strategies"
        base_dir = strategies_dir / base_strategy
        custom_dir = strategies_dir / strategy_name

        if not base_dir.exists():
            logger.error(f"❌ Base strategy not found: {base_dir}")
            return False

        if custom_dir.exists():
            logger.warning(f"⚠️  Strategy already exists: {custom_dir}")
            response = input("Overwrite? (y/N): ")
            if response.lower() != 'y':
                return False

        try:
            # Copy the base strategy
            subprocess.run(["cp", "-r", str(base_dir), str(custom_dir)], check=True)
            logger.info(f"✅ Strategy template created: {custom_dir}")

            # Update strategy name in configuration files
            self._update_strategy_config(custom_dir, strategy_name)
            logger.info(f"✅ Strategy configuration updated")

            return True
        except subprocess.CalledProcessError as e:
            logger.error(f"❌ Failed to create strategy: {e}")
            return False

    def _update_strategy_config(self, strategy_dir: Path, strategy_name: str):
        """Update configuration files with new strategy name"""
        # Update Cargo.toml
        cargo_file = strategy_dir / "Cargo.toml"
        if cargo_file.exists():
            with open(cargo_file, 'r') as f:
                content = f.read()
            content = content.replace("name = \"hodl\"", f"name = \"{strategy_name}\"")
            with open(cargo_file, 'w') as f:
                f.write(content)

        # Update lib.rs if it exists
        lib_file = strategy_dir / "src" / "lib.rs"
        if lib_file.exists():
            with open(lib_file, 'r') as f:
                content = f.read()
            # Replace contract name if present
            content = content.replace("pub struct HODLStrategy;", f"pub struct {strategy_name.title()}Strategy;")
            with open(lib_file, 'w') as f:
                f.write(content)

    def build_strategy(self, strategy_name: str) -> bool:
        """Build the strategy contract"""
        logger.info(f"🔨 Building strategy: {strategy_name}")

        contracts_dir = self.defindex_dir / "apps" / "contracts"
        strategy_dir = contracts_dir / "strategies" / strategy_name

        if not strategy_dir.exists():
            logger.error(f"❌ Strategy not found: {strategy_dir}")
            return False

        try:
            # Navigate to strategy directory and build
            os.chdir(strategy_dir)
            subprocess.run(["cargo", "build", "--target", "wasm32-unknown-unknown", "--release"], check=True)

            # Check if WASM file was created
            wasm_file = strategy_dir / "target" / "wasm32-unknown-unknown" / "release" / f"{strategy_name}.wasm"
            if wasm_file.exists():
                logger.info(f"✅ Strategy built successfully: {wasm_file}")
                return True
            else:
                logger.error("❌ WASM file not found after build")
                return False

        except subprocess.CalledProcessError as e:
            logger.error(f"❌ Build failed: {e}")
            return False

    def generate_deployment_commands(self, strategy_name: str, network: str = "testnet") -> str:
        """Generate deployment commands for the user"""
        strategy_dir = self.defindex_dir / "apps" / "contracts" / "strategies" / strategy_name
        wasm_file = strategy_dir / "target" / "wasm32-unknown-unknown" / "release" / f"{strategy_name}.wasm"

        commands = f"""
# 🚀 DeFindex Strategy Deployment Commands
# Strategy: {strategy_name}
# Network: {network}
# WASM File: {wasm_file}

# 1. Set up environment variables
export SECRET_KEY="your_stellar_secret_key_here"
export NETWORK="{network}"
export FACTORY_ADDRESS="CDKFHFJIET3A73A2YN4KV7NSV32S6YGQMUFH3DNJXLBWL4SKEGVRNFKI"

# 2. Deploy the strategy contract
soroban contract deploy \\
    --wasm {wasm_file} \\
    --network {network} \\
    --source-account $SECRET_KEY

# 3. Note the deployed contract address
# This address will be used in vault creation

# 4. Verify deployment on Stellar.Expert
# https://stellar.expert/explorer/{network}/contract/DEPLOYED_ADDRESS

# 5. Update your vault creation with the new strategy address:
# strategy_address = "DEPLOYED_ADDRESS_HERE"
"""
        return commands

def main():
    """Main deployment helper"""
    print("🏗️  DeFindex Strategy Deployment Helper")
    print("=" * 50)

    deployer = StrategyDeployer()

    # Check prerequisites
    print("\n📋 Checking prerequisites...")
    prerequisites = deployer.check_prerequisites()

    missing = [k for k, v in prerequisites.items() if not v]
    if missing:
        print(f"\n❌ Missing prerequisites: {', '.join(missing)}")
        print("\n🔧 Installation commands:")

        if "rust" in missing or "cargo" in missing:
            print("curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh")
            print("source ~/.cargo/env")

        if "soroban_cli" in missing:
            print("cargo install soroban-cli")

        if "git" in missing:
            print("# Install git for your platform")
            print("# Ubuntu/Debian: sudo apt-get install git")
            print("# macOS: brew install git")

        print("\n❌ Please install missing prerequisites and run again")
        return

    print("✅ All prerequisites installed!")

    # Setup development environment
    if not deployer.setup_development_environment():
        print("❌ Failed to setup development environment")
        return

    # Get strategy details from user
    print("\n" + "="*50)
    strategy_name = input("Enter strategy name (e.g., my_custom_hodl): ").strip()
    if not strategy_name:
        strategy_name = "my_custom_hodl"

    base_strategy = input("Base strategy to copy [hodl]: ").strip() or "hodl"

    # Create custom strategy
    if not deployer.create_custom_strategy(strategy_name, base_strategy):
        print("❌ Failed to create custom strategy")
        return

    # Build strategy
    if not deployer.build_strategy(strategy_name):
        print("❌ Failed to build strategy")
        return

    # Generate deployment commands
    print("\n" + "="*50)
    print("🎉 Strategy created successfully!")
    print("\n📝 Deployment Commands:")
    print(deployer.generate_deployment_commands(strategy_name))

    print(f"\n💡 Next Steps:")
    print(f"1. Set up your Stellar secret key")
    print(f"2. Run the deployment commands above")
    print(f"3. Note the deployed contract address")
    print(f"4. Use the address in vault creation with create_testnet_vault.py")
    print(f"5. Test your vault with the new strategy!")

if __name__ == "__main__":
    main()