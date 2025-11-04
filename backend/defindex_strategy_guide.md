# DeFindex Strategy Creation Complete Guide

**Date:** 2025-11-04
**Purpose:** Comprehensive guide for creating and deploying DeFindex strategies on Stellar

## Executive Summary

Based on extensive research of DeFindex documentation, GitHub repository, and API testing, here's what we discovered:

**✅ Strategy Creation is POSSIBLE** - but requires direct contract deployment, not API calls
**❌ No API endpoints** for strategy creation - must use smart contract deployment
**✅ Multiple strategy examples** available in the DeFindex repository

## Key Findings

### 1. Strategy Architecture

**DeFindex Strategy Contracts** follow this structure:

```
Strategy Contract (Proxy)
├── Protocol-Specific Integration
├── Single Underlying Asset Management
└── Core Functions:
    ├── initialization()
    ├── get_assets()
    ├── deposit(amount)
    ├── withdraw(amount)
    ├── harvest() - Yield Collection
    └── balance() - Current Position
```

### 2. Available Strategy Types

From the GitHub repository (`apps/contracts/strategies/`):

1. **`hodl`** - Simple hold strategy (easiest to implement)
2. **`blend`** - Blend protocol integration
3. **`soroswap`** - Soroswap DEX integration
4. **`xycloans`** - XY Finance lending protocol
5. **`fixed_apr`** - Fixed APR strategy
6. **`external_wasms`** - External contract integration
7. **`unsafe_hodl`** - Advanced hold strategy

### 3. Core Interface: `DeFindexStrategyTrait`

**Required Methods:**
```rust
pub trait DeFindexStrategyTrait {
    // Core Functions
    fn deposit(env: Env, amount: i128) -> Result<(), Error>;
    fn withdraw(env: Env, amount: i128) -> Result<(), Error>;
    fn balance(env: Env) -> Result<i128, Error>;
    fn harvest(env: Env) -> Result<(), Error>;

    // Asset Management
    fn get_assets(env: Env) -> Result<Address, Error>;

    // Strategy Information
    fn name(env: Env) -> Result<String, Error>;
    fn asset_address(env: Env) -> Result<Address, Error>;
}
```

### 4. Deployment Requirements

**No API Endpoints Available** - Strategy creation requires:

1. **Direct Smart Contract Deployment** via Soroban
2. **Stellar CLI Tools** for contract compilation and deployment
3. **Network Configuration** (testnet/mainnet)
4. **Gas/Transaction Fees** for deployment

### 5. Build and Deployment Process

**From Repository README:**

```bash
# Clone the repository
git clone https://github.com/paltalabs/defindex.git
cd defindex

# Build contracts
bash run
cd apps/contracts
make build

# Deploy to testnet (requires .env configuration)
yarn deploy-strategy <strategy_name> testnet

# Verify deployment
# Compare WASM hashes with Stellar.Expert
```

## Implementation Options

### Option 1: Use Existing HODL Strategy (Recommended)

**Easiest Path - Modify existing HODL strategy:**

1. **Clone DeFindex Repository:**
   ```bash
   git clone https://github.com/paltalabs/defindex.git
   cd defindex/apps/contracts/strategies/hodl
   ```

2. **Modify for Your Needs:**
   - Change strategy name
   - Update metadata
   - Customize any specific logic

3. **Deploy to Testnet:**
   ```bash
   # Set up .env with testnet configuration
   # Requires Stellar secret key for deployment
   make deploy-testnet
   ```

### Option 2: Create Custom Strategy

**Advanced Path - Build from scratch:**

1. **Implement `DeFindexStrategyTrait`:**
   ```rust
   #[contract]
   pub struct CustomStrategy;

   #[contractimpl]
   impl DeFindexStrategyTrait for CustomStrategy {
       // Implement all required methods
   }
   ```

2. **Build and Deploy:**
   ```bash
   cargo build --target wasm32-unknown-unknown --release
   soroban contract deploy --wasm target/wasm32-unknown-unknown/release/custom_strategy.wasm --network testnet
   ```

### Option 3: Use Pre-deployed Strategy Addresses

**Contact DeFindex Team** for:
- Available testnet strategy contracts
- Pre-deployed strategy addresses
- Documentation of existing strategies

## Strategy Creation Workflow

### Step 1: Setup Development Environment

```bash
# Install Rust and Soroban
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
source ~/.cargo/env

# Install Soroban CLI
cargo install soroban-cli

# Clone DeFindex
git clone https://github.com/paltalabs/defindex.git
cd defindex
```

### Step 2: Create/Modify Strategy

```bash
# Copy HODL strategy as template
cp -r apps/contracts/strategies/hodl apps/contracts/strategies/my_strategy

# Modify the strategy files
cd apps/contracts/strategies/my_strategy
# Edit src/lib.rs with your custom logic
```

### Step 3: Configure Environment

```bash
# Set up .env file in contracts directory
echo "SECRET_KEY=your_stellar_secret_key" > .env
echo "NETWORK=testnet" >> .env
echo "FACTORY_ADDRESS=CDKFHFJIET3A73A2YN4KV7NSV32S6YGQMUFH3DNJXLBWL4SKEGVRNFKI" >> .env
```

### Step 4: Build and Deploy

```bash
# Build the strategy
make build

# Deploy to testnet
make deploy-testnet

# Note the deployed contract address
# This will be your strategy address for vault creation
```

## Integration with Existing System

### 1. Update Vault Creation Helper

Once you have a deployed strategy address, update `create_testnet_vault.py`:

```python
def create_vault_with_custom_strategy(strategy_address):
    config = {
        'roles': {
            '0': caller_address,
            '1': caller_address,
            '2': caller_address,
            '3': caller_address
        },
        'vault_fee_bps': 100,
        'assets': [{
            'address': 'CDLZFC3SYJYDZT7K67VZ75HPJVIEUVNIXF47ZG2FB2RMQQVU2HHGCYSC',  # XLM
            'strategies': [{
                'address': strategy_address,  # Your deployed strategy!
                'name': 'My Custom Strategy',
                'paused': False
            }]
        }],
        'name_symbol': {
            'name': 'Tuxedo Custom Vault',
            'symbol': 'tCUSTOM'
        },
        'upgradable': True,
        'caller': caller_address,
        'network': 'testnet'
    }
    return config
```

### 2. Test the Complete Flow

```python
# After deploying your strategy
strategy_address = "YOUR_DEPLOYED_STRATEGY_ADDRESS"
vault_config = create_vault_with_custom_strategy(strategy_address)

# Create vault using our helper
creator = DeFindexVaultCreator()
result = creator.create_vault(vault_config)
```

## Prerequisites Summary

**Required Tools:**
- ✅ Rust toolchain
- ✅ Soroban CLI
- ✅ Stellar CLI
- ✅ Git
- ✅ Testnet XLM for deployment fees

**Required Knowledge:**
- ✅ Rust programming
- ✅ Soroban smart contracts
- ✅ Stellar transaction signing
- ✅ Contract deployment

**Required Resources:**
- ✅ Stellar testnet account with XLM
- ✅ DeFindex repository access
- ✅ Contract compilation environment

## Time and Cost Estimates

**Time Commitment:**
- Environment Setup: 1-2 hours
- Strategy Development: 4-8 hours (depending on complexity)
- Deployment and Testing: 1-2 hours
- Integration: 1-2 hours
- **Total: 7-14 hours**

**Cost:**
- Testnet XLM: ~100 XLM for deployment fees
- Development Time: Engineer hours as above
- **Total Cost: Minimal (testnet is free)**

## Recommended Next Steps

1. **Immediate: Use Existing HODL Strategy**
   - Fastest path to working vaults
   - Minimal development required
   - Proven functionality

2. **Short-term: Deploy Custom Strategy**
   - Follow the workflow above
   - Test with simple modifications first
   - Gradually add complexity

3. **Long-term: Full Strategy Development**
   - Implement custom DeFi integrations
   - Add advanced yield farming logic
   - Optimize for specific use cases

## Documentation References

- **Repository:** https://github.com/paltalabs/defindex
- **Strategy Examples:** https://github.com/paltalabs/defindex/tree/main/apps/contracts/strategies
- **Whitepaper:** https://docs.defindex.io/whitepaper/10-whitepaper/02-contracts/02-strategy-contract
- **Build Instructions:** Repository README.md

---

**Status:** ✅ **Research Complete - Ready for Implementation**
**Next Action:** Deploy HODL strategy to testnet and create working vault