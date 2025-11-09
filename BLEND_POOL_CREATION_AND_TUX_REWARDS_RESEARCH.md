# Creating Yield Opportunities on Blend Testnet: Research Report

**Date:** November 9, 2025
**Project:** Tuxedo AI Agent for Blend Protocol
**Status:** Research & Strategy Document

---

## Executive Summary

This report investigates two approaches to providing yield opportunities for Tuxedo users on Stellar testnet:

1. **Option A:** Deploy a custom Blend Capital pool with configured yield
2. **Option B:** Implement TUX token rewards as an incentive layer on top of existing pools

**Key Finding:** The current Blend testnet pools show 0% APY because they lack borrowing demand and/or proper interest rate configuration. Both solutions are viable, with Option B (TUX rewards) being significantly easier to implement and more aligned with common DeFi testnet practices.

---

## Problem Statement

### Current Situation

From the chat logs, we can see:
- Users attempt to deposit XLM to earn yield
- `blend_find_best_yield` returns "No yield opportunities found for XLM with APY above 0.0% on testnet"
- `blend_supply_to_pool` fails because the pool doesn't accept the asset for yield
- Even USDC shows 0% APY on testnet

### Root Cause

Blend pools generate yield through a two-sided market:
1. **Suppliers** deposit assets and earn interest
2. **Borrowers** borrow assets and pay interest
3. Interest rates adjust based on **utilization** (borrowed/supplied ratio)

**On testnet:** There are likely no active borrowers, so utilization = 0%, which means supply APY = 0%.

Even if reserves are configured properly, without borrowing demand, there's no yield to distribute to suppliers.

---

## Option A: Deploy Custom Blend Pool with Yield

### Overview

Create a new Blend pool on testnet with properly configured reserves and interest rates. This would give us full control over the pool parameters.

### Architecture

Blend consists of three main contracts:
- **Pool Factory**: Permissionless pool creation
- **Pool Contract**: Core lending logic (supply, borrow, liquidations)
- **Backstop**: Insurance layer (80/20 BLND:USDC AMM)

### Technical Requirements

#### 1. Setup Dependencies

```bash
# Clone blend-utils repository
git clone https://github.com/blend-capital/blend-utils
cd blend-utils

# Install dependencies
npm install

# Build scripts
npm run build

# Configure environment
cp .env.example .env
```

**Required .env variables:**
```
ADMIN=<keypair_with_sufficient_XLM_for_fees>
NETWORK_PASSPHRASE=Test SDF Network ; September 2015
RPC_ENDPOINT=https://soroban-testnet.stellar.org
```

#### 2. Create Network Configuration

Create `testnet.contracts.json` with:
```json
{
  "oracle": "<mock_oracle_address>",
  "tokens": {
    "xlm": "CDLZFC3SYJYDZT7K67VZ75HPJVIEUVNIXF47ZG2FB2RMQQVU2HHGCYSC",
    "usdc": "CAQCFVLOBK5GIULPNZRGATJJMIZL5BSP7X5YJVMCPTUEPFM4AVSRCJU",
    "blnd": "CB22KRA3YZVCNCQI64JQ5WE7UY2VAV7WFLK5A2JN3HEX56T2EDAFO7QF"
  }
}
```

#### 3. Configure Pool Parameters

**Pool-Level Settings:**
```javascript
{
  name: "Tuxedo Yield Pool",
  backstop_take_rate: 0.05,  // 5% of interest to backstop
  max_positions: 8            // Recommended default
}
```

**Reserve Configuration (per asset):**

Each reserve needs:
- **Collateral Factor** (0 to 1e7): How much can be borrowed against this asset
- **Liability Factor** (0 to 1e7): Maximum borrowing allowed
- **Interest Rate Curve**: Defines how rates change with utilization

Example for XLM reserve:
```javascript
{
  asset: "CDLZFC3SYJYDZT7K67VZ75HPJVIEUVNIXF47ZG2FB2RMQQVU2HHGCYSC", // XLM
  collateral_factor: 7500000,  // 75% (0.75 * 1e7)
  liability_factor: 8000000,   // 80%

  // Interest rate curve (low risk)
  // Formula: rate = R1 + (utilization/U_T) * R2 + rate_modifier
  utilization_target: 9000000,  // 90% target utilization
  r_base: 300000,               // 3% base rate (0.03 * 1e7)
  r_one: 2000000,              // 20% rate at target utilization
  r_two: 10000000,             // 100% rate above target

  supply_cap: 100000000000000,  // 10M XLM (in stroops)
  enabled: true
}
```

**Interest Rate Model Explanation:**

Blend uses a reactive interest rate curve with three parameters:
- **U_T (Utilization Target)**: Optimal utilization point (e.g., 90%)
- **R_1 (Base Rate)**: Interest rate at 0% utilization
- **R_2 (Target Rate)**: Interest rate at U_T utilization
- **R_3 (Max Rate)**: Interest rate at 100% utilization
- **Rate Modifier**: Reactive value that adjusts over time (bounded [0.1, 100])

Common configurations:
- **Low Risk Curve**: U_T=0.9, R_1=0.03, R_2=0.2, R_3=1.0
- **Medium Risk**: U_T=0.75, R_1=0.05, R_2=0.5, R_3=1.5
- **High Risk**: U_T=0.6, R_1=0.07, R_2=1.0, R_3=2.0

#### 4. Deploy Pool

```bash
# Deploy the pool
node ./lib/v2/user-scripts/deploy-pool.js testnet false

# This will:
# 1. Create a new pool via pool factory
# 2. Initialize reserves with your configuration
# 3. Set up emission metadata
# 4. Return pool contract address
```

#### 5. Fund Backstop

**Critical:** Pools require backstop deposits to activate.

```bash
# Mint BLND:USDC LP tokens
node ./lib/v2/user-scripts/mint-lp.js testnet <admin_address> usdc 10000

# Deposit to backstop for your pool
node ./lib/v2/user-scripts/fund-backstop.js testnet <admin_address> <pool_address> 10000

# Check if threshold met
node ./lib/v2/user-scripts/get-backstop-threshold.js testnet <admin_address>
```

#### 6. Integrate with Tuxedo

Update `backend/blend_pool_tools.py`:
```python
BLEND_TESTNET_CONTRACTS = {
    # ... existing contracts ...
    'tuxedoPool': '<your_deployed_pool_address>',
}
```

Update pool discovery to include your custom pool.

### Critical Challenge: Generating Yield

**The fundamental problem remains:** Even with a perfectly configured pool, you need borrowers to generate yield.

#### Artificial Yield Strategies

1. **Self-Borrowing Loop**
   - Create bot accounts that borrow from the pool
   - Pay interest from a treasury account
   - This simulates real borrowing demand

   **Pros:** Creates real on-chain yield via Blend's native mechanisms
   **Cons:** Requires continuous funding; artificial/unsustainable

2. **Manipulated Interest Rates**
   - Set R_1 (base rate) to non-zero (e.g., 5%)
   - Even at 0% utilization, suppliers earn 5%

   **Pros:** Simple configuration change
   **Cons:** Economically nonsensical; still requires someone to pay the interest

3. **Treasury-Funded Rewards**
   - Manually transfer tokens to suppliers periodically
   - Track positions via `get_positions()`
   - Calculate proportional rewards

   **Pros:** Full control over reward distribution
   **Cons:** Requires off-chain tracking; not automated by Blend protocol

### Complexity Assessment

**High Complexity:**
- Requires Node.js tooling setup (blend-utils)
- Must deploy and manage smart contracts
- Need BLND tokens for backstop (must acquire on testnet)
- Backstop has 21-day withdrawal period (protocol constraint)
- Must fund artificial borrowing or manually distribute rewards
- Ongoing operational overhead to maintain yields

**Estimated Effort:** 3-5 days of development + ongoing maintenance

---

## Option B: TUX Token Reward System

### Overview

Instead of fighting Blend's economic model on testnet, create a parallel incentive system using a native TUX token. Users earn TUX rewards for depositing to existing Blend pools, regardless of the pool's native APY.

This is the **standard approach** for testnet DeFi protocols and early-stage mainnet projects.

### How It Works

```
User deposits 100 USDC to Blend Pool
  ↓
Tuxedo backend tracks deposit via get_positions()
  ↓
TUX rewards accrue over time (e.g., 10 TUX/day per 100 USDC deposited)
  ↓
User can claim TUX rewards anytime
  ↓
TUX tokens can be used for:
  - Governance (vote on pool integrations, features)
  - Fee discounts (future premium features)
  - Airdrops/rewards when Tuxedo launches mainnet
  - Early access to new features
```

### Architecture

#### 1. TUX Token Contract

Deploy a simple Soroban token contract:

```rust
// TUX Token Contract (Soroban)
#[contract]
pub struct TuxToken;

#[contractimpl]
impl TuxToken {
    // Standard token interface
    pub fn initialize(admin: Address, decimal: u32, name: String, symbol: String);
    pub fn mint(to: Address, amount: i128);
    pub fn balance(id: Address) -> i128;
    pub fn transfer(from: Address, to: Address, amount: i128);
    pub fn burn(from: Address, amount: i128);
}
```

**Deployment:**
```bash
# Build the token contract
cd tux-token
cargo build --target wasm32-unknown-unknown --release

# Optimize WASM
stellar contract optimize --wasm target/wasm32-unknown-unknown/release/tux_token.wasm

# Deploy to testnet
stellar contract deploy \
  --wasm target/wasm32-unknown-unknown/release/tux_token.wasm \
  --source-account tuxedo-admin \
  --network testnet

# Initialize token
stellar contract invoke \
  --id <TUX_CONTRACT_ID> \
  --source-account tuxedo-admin \
  --network testnet \
  -- initialize \
  --admin <ADMIN_ADDRESS> \
  --decimal 7 \
  --name "Tuxedo" \
  --symbol "TUX"
```

#### 2. Rewards Tracking Backend

Create a new module `backend/tux_rewards.py`:

```python
"""
TUX Token Rewards System

Tracks user deposits in Blend pools and calculates TUX rewards.
"""

import asyncio
import logging
from typing import Dict, List, Any
from datetime import datetime, timedelta
from stellar_sdk.soroban_server_async import SorobanServerAsync
from account_manager import AccountManager
from blend_pool_tools import blend_get_my_positions
import json

logger = logging.getLogger(__name__)

# TUX Reward Configuration
TUX_REWARDS_CONFIG = {
    'contract_id': '<TUX_TOKEN_CONTRACT_ID>',

    # Reward rates (TUX per day per 1 unit of asset)
    'reward_rates': {
        'USDC': 0.1,   # 0.1 TUX per USDC per day (10% daily for testnet)
        'XLM': 0.01,   # 0.01 TUX per XLM per day (1% daily)
        'WETH': 1.0,   # 1.0 TUX per WETH per day (higher value asset)
        'WBTC': 10.0,  # 10.0 TUX per WBTC per day
    },

    # Pool multipliers (encourage specific pools)
    'pool_multipliers': {
        'CCQ74HNBMLYICEFUGNLM23QQJU7BKZS7CXC7OAOX4IHRT3LDINZ4V3AF': 1.0,  # Comet pool
        # Add more pools with higher multipliers for incentives
    },

    # Minimum deposit time for rewards (prevent gaming)
    'min_deposit_duration': 3600,  # 1 hour in seconds
}

class TuxRewardsTracker:
    """Tracks and calculates TUX rewards for Blend deposits."""

    def __init__(self, db_path: str = "tux_rewards.db"):
        """Initialize rewards tracker with database."""
        import sqlite3
        self.db = sqlite3.connect(db_path)
        self._init_db()

    def _init_db(self):
        """Create rewards tracking tables."""
        self.db.execute("""
            CREATE TABLE IF NOT EXISTS deposits (
                user_id TEXT,
                account_id TEXT,
                pool_address TEXT,
                asset_symbol TEXT,
                amount REAL,
                deposit_time INTEGER,
                last_claim_time INTEGER,
                PRIMARY KEY (user_id, account_id, pool_address, asset_symbol)
            )
        """)

        self.db.execute("""
            CREATE TABLE IF NOT EXISTS claims (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT,
                account_id TEXT,
                tux_amount REAL,
                claim_time INTEGER,
                tx_hash TEXT
            )
        """)
        self.db.commit()

    def update_positions(
        self,
        user_id: str,
        account_id: str,
        pool_address: str,
        positions: Dict[str, Any]
    ):
        """
        Update tracked positions from blend_get_my_positions() result.

        Args:
            user_id: User identifier
            account_id: Account ID
            pool_address: Pool contract address
            positions: Result from blend_get_my_positions()
        """
        current_time = int(datetime.now().timestamp())

        for asset_symbol, position in positions.items():
            supplied_amount = position['supplied']

            if supplied_amount > 0:
                # Check if position exists
                existing = self.db.execute(
                    "SELECT deposit_time, last_claim_time FROM deposits "
                    "WHERE user_id=? AND account_id=? AND pool_address=? AND asset_symbol=?",
                    (user_id, account_id, pool_address, asset_symbol)
                ).fetchone()

                if existing:
                    # Update amount (keep original deposit time)
                    self.db.execute(
                        "UPDATE deposits SET amount=? "
                        "WHERE user_id=? AND account_id=? AND pool_address=? AND asset_symbol=?",
                        (supplied_amount, user_id, account_id, pool_address, asset_symbol)
                    )
                else:
                    # New deposit
                    self.db.execute(
                        "INSERT INTO deposits VALUES (?, ?, ?, ?, ?, ?, ?)",
                        (user_id, account_id, pool_address, asset_symbol,
                         supplied_amount, current_time, current_time)
                    )
            else:
                # Position closed, remove from tracking
                self.db.execute(
                    "DELETE FROM deposits "
                    "WHERE user_id=? AND account_id=? AND pool_address=? AND asset_symbol=?",
                    (user_id, account_id, pool_address, asset_symbol)
                )

        self.db.commit()

    def calculate_pending_rewards(
        self,
        user_id: str,
        account_id: str = None
    ) -> Dict[str, Any]:
        """
        Calculate pending TUX rewards for user.

        Args:
            user_id: User identifier
            account_id: Optional specific account (None = all accounts)

        Returns:
            {
                'total_pending': 123.45,
                'by_pool': {
                    'Comet Pool': {
                        'USDC': 50.0,
                        'XLM': 73.45
                    }
                }
            }
        """
        query = "SELECT * FROM deposits WHERE user_id=?"
        params = [user_id]

        if account_id:
            query += " AND account_id=?"
            params.append(account_id)

        deposits = self.db.execute(query, params).fetchall()

        current_time = int(datetime.now().timestamp())
        total_pending = 0.0
        by_pool = {}

        for deposit in deposits:
            (user_id, account_id, pool_address, asset_symbol,
             amount, deposit_time, last_claim_time) = deposit

            # Calculate time since last claim
            time_elapsed = current_time - last_claim_time

            # Skip if below minimum duration
            if time_elapsed < TUX_REWARDS_CONFIG['min_deposit_duration']:
                continue

            # Get reward rate for this asset
            rate = TUX_REWARDS_CONFIG['reward_rates'].get(asset_symbol, 0.0)

            # Get pool multiplier
            multiplier = TUX_REWARDS_CONFIG['pool_multipliers'].get(pool_address, 1.0)

            # Calculate rewards: amount * rate * days * multiplier
            days_elapsed = time_elapsed / 86400
            pending = amount * rate * days_elapsed * multiplier

            total_pending += pending

            # Organize by pool
            # (In production, fetch pool name)
            pool_name = f"Pool {pool_address[:8]}"
            if pool_name not in by_pool:
                by_pool[pool_name] = {}
            by_pool[pool_name][asset_symbol] = pending

        return {
            'total_pending': round(total_pending, 7),
            'by_pool': by_pool
        }

    async def claim_rewards(
        self,
        user_id: str,
        account_id: str,
        tux_recipient_address: str,
        soroban_server: SorobanServerAsync,
        account_manager: AccountManager
    ) -> Dict[str, Any]:
        """
        Claim pending TUX rewards for a user.

        Args:
            user_id: User identifier
            account_id: Account to claim for
            tux_recipient_address: Stellar address to receive TUX
            soroban_server: SorobanServerAsync instance
            account_manager: AccountManager instance

        Returns:
            {
                'success': True,
                'tux_claimed': 123.45,
                'tx_hash': 'abc123...',
                'message': 'Claimed 123.45 TUX'
            }
        """
        # Calculate pending
        pending = self.calculate_pending_rewards(user_id, account_id)

        if pending['total_pending'] == 0:
            return {
                'success': False,
                'error': 'No pending rewards to claim'
            }

        # Mint TUX tokens to user
        # (Requires admin account to mint)
        from stellar_soroban import soroban_operations

        amount_scaled = int(pending['total_pending'] * 1e7)  # 7 decimals

        parameters = json.dumps([
            {"type": "address", "value": tux_recipient_address},
            {"type": "int128", "value": str(amount_scaled)}
        ])

        result = await soroban_operations(
            action="invoke",
            user_id="tuxedo_admin",  # Admin user for minting
            soroban_server=soroban_server,
            account_manager=account_manager,
            contract_id=TUX_REWARDS_CONFIG['contract_id'],
            function_name="mint",
            parameters=parameters,
            account_id="tuxedo_admin_account",  # Admin account
            auto_sign=True,
            network_passphrase="Test SDF Network ; September 2015"
        )

        if not result.get('success'):
            return {
                'success': False,
                'error': f"Failed to mint TUX: {result.get('error')}"
            }

        # Record claim
        current_time = int(datetime.now().timestamp())
        self.db.execute(
            "INSERT INTO claims VALUES (NULL, ?, ?, ?, ?, ?)",
            (user_id, account_id, pending['total_pending'],
             current_time, result.get('hash'))
        )

        # Update last_claim_time for all deposits
        self.db.execute(
            "UPDATE deposits SET last_claim_time=? WHERE user_id=? AND account_id=?",
            (current_time, user_id, account_id)
        )

        self.db.commit()

        return {
            'success': True,
            'tux_claimed': pending['total_pending'],
            'tx_hash': result.get('hash'),
            'ledger': result.get('ledger'),
            'message': f"✅ Claimed {pending['total_pending']} TUX! Tx: {result.get('hash')[:16]}..."
        }

# Global tracker instance
_rewards_tracker = None

def get_rewards_tracker() -> TuxRewardsTracker:
    """Get or create global rewards tracker instance."""
    global _rewards_tracker
    if _rewards_tracker is None:
        _rewards_tracker = TuxRewardsTracker()
    return _rewards_tracker
```

#### 3. LangChain Tools Integration

Create `backend/tux_rewards_tools.py`:

```python
"""
LangChain tools for TUX rewards system.
"""

from langchain.tools import tool
from typing import Optional
from stellar_sdk.soroban_server_async import SorobanServerAsync
from account_manager import AccountManager
from blend_pool_tools import blend_get_my_positions
from tux_rewards import get_rewards_tracker, TUX_REWARDS_CONFIG

@tool
async def tux_check_rewards(
    user_id: str,
    account_id: Optional[str] = None
) -> str:
    """
    Check pending TUX rewards for user's Blend deposits.

    Args:
        user_id: User identifier
        account_id: Optional specific account ID

    Returns:
        Human-readable summary of pending rewards
    """
    tracker = get_rewards_tracker()
    pending = tracker.calculate_pending_rewards(user_id, account_id)

    if pending['total_pending'] == 0:
        return "You have no pending TUX rewards. Supply assets to a Blend pool to start earning!"

    message = f"💰 **Pending TUX Rewards: {pending['total_pending']} TUX**\n\n"
    message += "Breakdown by pool:\n"

    for pool_name, assets in pending['by_pool'].items():
        message += f"\n**{pool_name}:**\n"
        for asset, amount in assets.items():
            message += f"  - {asset}: {amount:.4f} TUX\n"

    message += f"\n💡 Use `tux_claim_rewards` to claim your TUX tokens!"

    return message

@tool
async def tux_claim_rewards(
    user_id: str,
    account_id: str,
    account_manager: AccountManager,
    soroban_server: SorobanServerAsync
) -> str:
    """
    Claim pending TUX rewards and receive them to your account.

    Args:
        user_id: User identifier
        account_id: Account ID to claim for
        account_manager: AccountManager instance
        soroban_server: SorobanServerAsync instance

    Returns:
        Claim confirmation message
    """
    # Get recipient address from account
    account_data = account_manager._get_account_by_id(account_id)
    recipient_address = account_data['public_key']

    tracker = get_rewards_tracker()
    result = await tracker.claim_rewards(
        user_id,
        account_id,
        recipient_address,
        soroban_server,
        account_manager
    )

    if not result['success']:
        return f"❌ Claim failed: {result.get('error')}"

    return result['message']

@tool
async def tux_update_positions(
    user_id: str,
    account_id: str,
    pool_address: str,
    account_manager: AccountManager,
    soroban_server: SorobanServerAsync
) -> str:
    """
    Update reward tracking based on current Blend positions.

    This is called automatically after supply/withdraw operations.

    Args:
        user_id: User identifier
        account_id: Account ID
        pool_address: Pool contract address
        account_manager: AccountManager instance
        soroban_server: SorobanServerAsync instance

    Returns:
        Confirmation message
    """
    # Get current positions
    positions_result = await blend_get_my_positions(
        pool_address,
        user_id,
        account_id,
        account_manager,
        soroban_server
    )

    if 'error' in positions_result:
        return f"Failed to update rewards tracking: {positions_result['error']}"

    # Update tracker
    tracker = get_rewards_tracker()
    tracker.update_positions(
        user_id,
        account_id,
        pool_address,
        positions_result['positions']
    )

    return "✅ Rewards tracking updated based on current positions"

@tool
def tux_get_reward_rates() -> str:
    """
    Get current TUX reward rates for each asset.

    Returns:
        Human-readable summary of reward rates
    """
    rates = TUX_REWARDS_CONFIG['reward_rates']

    message = "🎁 **TUX Reward Rates** (per day per 1 unit deposited):\n\n"
    for asset, rate in rates.items():
        apy = rate * 365 * 100  # Annualized percentage
        message += f"- **{asset}**: {rate} TUX/day ({apy:.1f}% APY in TUX)\n"

    message += "\n💡 Supply assets to any Blend pool to start earning TUX rewards!"
    message += "\n📊 Check your rewards anytime with `tux_check_rewards`"

    return message
```

#### 4. Integrate into AI Agent

Update `backend/agent/tool_factory.py`:

```python
from tux_rewards_tools import (
    tux_check_rewards,
    tux_claim_rewards,
    tux_update_positions,
    tux_get_reward_rates
)

def create_tools_for_user(user_id: str, ...) -> List[Tool]:
    """Create tool instances for a specific user."""

    tools = [
        # ... existing Blend tools ...

        # TUX Rewards tools
        tux_get_reward_rates,
        tux_check_rewards,
        tux_claim_rewards,
    ]

    return tools
```

#### 5. Auto-Update Rewards After Operations

Modify `blend_supply_collateral()` and `blend_withdraw_collateral()` in `blend_pool_tools.py`:

```python
async def blend_supply_collateral(...) -> Dict[str, Any]:
    # ... existing supply logic ...

    if result.get('success'):
        # Update rewards tracking
        from tux_rewards import get_rewards_tracker

        positions_result = await blend_get_my_positions(
            pool_address, user_id, account_id, account_manager, soroban_server
        )

        if 'positions' in positions_result:
            tracker = get_rewards_tracker()
            tracker.update_positions(
                user_id,
                account_id,
                pool_address,
                positions_result['positions']
            )

    return result
```

### User Experience Flow

```
User: "Deposit 100 USDC to Blend"
  ↓
Tuxedo: ✅ Deposited 100 USDC to Comet Pool
        🎁 You're now earning 10 TUX per day!
        💡 Check rewards anytime with "check my TUX rewards"

---

[3 days later]

User: "Check my TUX rewards"
  ↓
Tuxedo: 💰 Pending TUX Rewards: 30.0 TUX

        Breakdown by pool:

        **Comet Pool:**
          - USDC: 30.0 TUX

        💡 Use "claim my TUX rewards" to receive them!

---

User: "Claim my TUX rewards"
  ↓
Tuxedo: ✅ Claimed 30.0 TUX! Tx: abc123...

        Your TUX balance: 30.0 TUX

        🎯 TUX tokens can be used for:
        - Governance voting (coming soon)
        - Premium features discount
        - Mainnet airdrop eligibility
```

### Frontend Integration

Update `src/components/dashboard/PoolsDashboard.tsx` to show TUX rewards:

```tsx
interface TuxRewards {
  total_pending: number;
  by_pool: Record<string, Record<string, number>>;
}

function TuxRewardsCard({ rewards }: { rewards: TuxRewards }) {
  return (
    <Card>
      <CardHeader>
        <CardTitle>TUX Rewards</CardTitle>
        <CardDescription>Earn TUX by supplying to Blend pools</CardDescription>
      </CardHeader>
      <CardContent>
        <div className="text-3xl font-bold">
          {rewards.total_pending.toFixed(4)} TUX
        </div>
        <div className="text-sm text-muted-foreground mt-2">
          Pending rewards
        </div>

        <Button
          onClick={handleClaimRewards}
          className="w-full mt-4"
        >
          Claim Rewards
        </Button>

        {/* Breakdown by pool */}
        <div className="mt-4 space-y-2">
          {Object.entries(rewards.by_pool).map(([pool, assets]) => (
            <div key={pool} className="border-t pt-2">
              <div className="font-medium text-sm">{pool}</div>
              {Object.entries(assets).map(([asset, amount]) => (
                <div key={asset} className="flex justify-between text-sm text-muted-foreground">
                  <span>{asset}</span>
                  <span>{amount.toFixed(4)} TUX</span>
                </div>
              ))}
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  );
}
```

### TUX Tokenomics

**Total Supply:** 100,000,000 TUX (100M)

**Distribution:**
- **Testnet Rewards:** 1,000,000 TUX (1%) - for testnet yield farming participants
- **Team/Development:** 20,000,000 TUX (20%) - vested over 2 years
- **Community Airdrop:** 10,000,000 TUX (10%) - early adopters, community contributors
- **Liquidity Incentives:** 30,000,000 TUX (30%) - mainnet liquidity mining
- **Treasury:** 20,000,000 TUX (20%) - partnerships, grants, ecosystem development
- **Investors/Advisors:** 19,000,000 TUX (19%) - vested over 18 months

**Utility:**
- **Governance:** Vote on protocol parameters, pool integrations, feature priorities
- **Fee Discounts:** Reduce fees for premium features (priority support, advanced analytics)
- **Staking Rewards:** Stake TUX to earn a share of protocol revenue (future)
- **Mainnet Airdrop Multiplier:** Testnet TUX holders receive bonus mainnet tokens
- **Early Access:** Beta access to new features and integrations

### Implementation Complexity

**Low-Medium Complexity:**
- Deploy standard Soroban token contract (template available)
- Python backend for tracking (SQLite database)
- Simple reward calculation (no complex DeFi math)
- Straightforward LangChain tools integration
- No ongoing operational overhead after launch

**Estimated Effort:** 1-2 days of development

---

## Option Comparison Matrix

| Criteria | Option A: Custom Blend Pool | Option B: TUX Rewards |
|----------|----------------------------|---------------------|
| **Implementation Time** | 3-5 days | 1-2 days |
| **Technical Complexity** | High | Low-Medium |
| **Ongoing Maintenance** | High (must sustain yields) | Low (automated) |
| **Blockchain Alignment** | Uses Blend's native mechanisms | Overlay reward system |
| **Economic Sustainability** | Requires artificial demand | Controlled token emissions |
| **User Education** | Familiar (standard DeFi APY) | Requires explanation of TUX |
| **Flexibility** | Limited by Blend protocol | Full control over rates |
| **Mainnet Readiness** | Complex (needs real borrowers) | Easy (just reward rates) |
| **Testnet Appropriateness** | Awkward (fighting lack of demand) | Standard practice |
| **Community Building** | No | Yes (token holders = community) |
| **Future Value** | Testnet only | Mainnet airdrop potential |

---

## Recommendation

### Primary Recommendation: Option B (TUX Rewards)

**Rationale:**

1. **Industry Standard:** Major DeFi protocols use native token rewards on testnet
   - Examples: Uniswap (UNI), Compound (COMP), Aave (AAVE), Blur, friend.tech
   - Typically allocate ~1% of token supply to testnet incentives

2. **Solves the Real Problem:** Users want yield. TUX provides it without fighting Blend's economics.

3. **Lower Risk:** No complex smart contract deployments beyond a simple token

4. **Community Building:** TUX token holders become invested community members
   - More likely to provide feedback, evangelize, and contribute
   - Creates early adopters for mainnet launch

5. **Marketing Opportunity:** "Earn TUX by testing Tuxedo on testnet!"
   - Attracts users to try the product
   - Generates content and social proof
   - Builds anticipation for mainnet

6. **Flexibility:** Easy to adjust reward rates, add new pools, or bonus campaigns

7. **Mainnet Bridge:** Testnet TUX can be convertible to mainnet TUX at a ratio (e.g., 10:1)

### Secondary Consideration: Hybrid Approach

Deploy a custom Blend pool (Option A) **AND** add TUX rewards (Option B) for extra incentives:

- Provides the best of both worlds
- Users get native Blend APY + TUX rewards
- Demonstrates full technical capability
- More complex but more impressive

**When to use this:**
- If showcasing technical depth is important
- If you plan to deploy Blend pools on mainnet
- If you have 1-2 weeks for implementation

---

## Implementation Roadmap

### Phase 1: TUX Token Launch (Week 1)

**Day 1-2: Token Contract**
- Deploy Soroban token contract to testnet
- Initialize with 100M TUX supply
- Test mint/transfer/balance functions
- Document contract address

**Day 3-4: Rewards Backend**
- Implement `tux_rewards.py` module
- Create SQLite database schema
- Write reward calculation logic
- Test with sample data

**Day 5: AI Integration**
- Create LangChain tools
- Integrate with agent tool factory
- Update supply/withdraw hooks
- Test conversational flow

**Day 6-7: Frontend + Testing**
- Add TUX rewards card to dashboard
- Implement claim button
- End-to-end testing
- Bug fixes and polish

### Phase 2: Community Launch (Week 2)

**Day 1-3: Documentation & Marketing**
- Write TUX tokenomics doc
- Create user guide
- Announce on social media
- Create demo video

**Day 4-5: Onboarding Campaign**
- "Get your first 10 TUX" tutorial
- Discord/Telegram community setup
- Leaderboard for top earners
- Weekly reward summaries

**Day 6-7: Monitoring & Iteration**
- Track reward distribution
- Monitor user feedback
- Adjust rates if needed
- Plan next features

### Phase 3: Advanced Features (Week 3+)

- **TUX Staking:** Earn bonus rewards by staking TUX
- **Referral Rewards:** Earn TUX for inviting new users
- **Achievement System:** Bonus TUX for milestones
- **Governance:** Vote on which pools to integrate next
- **Leaderboards:** Top yield farmers get bonus multipliers

---

## Technical Deep Dive: TUX Token Contract

### Complete Soroban Token Implementation

```rust
#![no_std]
use soroban_sdk::{contract, contractimpl, contracttype, Address, Env, String, symbol_short};

#[contract]
pub struct TuxToken;

#[contracttype]
#[derive(Clone)]
pub struct TokenMetadata {
    pub decimal: u32,
    pub name: String,
    pub symbol: String,
}

const ADMIN: symbol_short!("ADMIN");
const BALANCE: symbol_short!("BALANCE");
const METADATA: symbol_short!("METADATA");

#[contractimpl]
impl TuxToken {
    pub fn initialize(
        env: Env,
        admin: Address,
        decimal: u32,
        name: String,
        symbol: String
    ) {
        if env.storage().instance().has(&ADMIN) {
            panic!("already initialized");
        }

        env.storage().instance().set(&ADMIN, &admin);

        let metadata = TokenMetadata {
            decimal,
            name,
            symbol,
        };
        env.storage().instance().set(&METADATA, &metadata);
    }

    pub fn mint(env: Env, to: Address, amount: i128) {
        let admin: Address = env.storage().instance().get(&ADMIN).unwrap();
        admin.require_auth();

        let balance = Self::balance(env.clone(), to.clone());
        env.storage().persistent().set(&(BALANCE, to.clone()), &(balance + amount));
    }

    pub fn balance(env: Env, id: Address) -> i128 {
        env.storage()
            .persistent()
            .get(&(BALANCE, id))
            .unwrap_or(0)
    }

    pub fn transfer(env: Env, from: Address, to: Address, amount: i128) {
        from.require_auth();

        let from_balance = Self::balance(env.clone(), from.clone());
        let to_balance = Self::balance(env.clone(), to.clone());

        if from_balance < amount {
            panic!("insufficient balance");
        }

        env.storage().persistent().set(&(BALANCE, from), &(from_balance - amount));
        env.storage().persistent().set(&(BALANCE, to), &(to_balance + amount));
    }

    pub fn burn(env: Env, from: Address, amount: i128) {
        from.require_auth();

        let balance = Self::balance(env.clone(), from.clone());
        if balance < amount {
            panic!("insufficient balance");
        }

        env.storage().persistent().set(&(BALANCE, from), &(balance - amount));
    }

    pub fn decimals(env: Env) -> u32 {
        let metadata: TokenMetadata = env.storage().instance().get(&METADATA).unwrap();
        metadata.decimal
    }

    pub fn name(env: Env) -> String {
        let metadata: TokenMetadata = env.storage().instance().get(&METADATA).unwrap();
        metadata.name
    }

    pub fn symbol(env: Env) -> String {
        let metadata: TokenMetadata = env.storage().instance().get(&METADATA).unwrap();
        metadata.symbol
    }
}
```

**Project Structure:**
```
tux-token/
├── Cargo.toml
├── src/
│   └── lib.rs (above code)
└── README.md
```

**Cargo.toml:**
```toml
[package]
name = "tux-token"
version = "0.1.0"
edition = "2021"

[lib]
crate-type = ["cdylib"]

[dependencies]
soroban-sdk = "21.0.0"

[dev-dependencies]
soroban-sdk = { version = "21.0.0", features = ["testutils"] }

[profile.release]
opt-level = "z"
overflow-checks = true
debug = 0
strip = "symbols"
debug-assertions = false
panic = "abort"
codegen-units = 1
lto = true

[profile.release-with-logs]
inherits = "release"
debug-assertions = true
```

**Build & Deploy Script:**
```bash
#!/bin/bash
# deploy-tux-token.sh

set -e

echo "Building TUX token contract..."
cd tux-token
cargo build --target wasm32-unknown-unknown --release

echo "Optimizing WASM..."
stellar contract optimize --wasm target/wasm32-unknown-unknown/release/tux_token.wasm

echo "Deploying to testnet..."
CONTRACT_ID=$(stellar contract deploy \
  --wasm target/wasm32-unknown-unknown/release/tux_token.optimized.wasm \
  --source-account tuxedo-admin \
  --network testnet)

echo "Contract deployed: $CONTRACT_ID"

echo "Initializing token..."
stellar contract invoke \
  --id "$CONTRACT_ID" \
  --source-account tuxedo-admin \
  --network testnet \
  -- initialize \
  --admin "$(stellar keys address tuxedo-admin)" \
  --decimal 7 \
  --name "Tuxedo" \
  --symbol "TUX"

echo "TUX token ready!"
echo "Contract ID: $CONTRACT_ID"
echo ""
echo "Update backend/tux_rewards.py with:"
echo "TUX_REWARDS_CONFIG = {"
echo "    'contract_id': '$CONTRACT_ID',"
echo "    ..."
echo "}"
```

---

## Economic Model: TUX Rewards Math

### Reward Rate Calculation

**Goal:** Provide attractive APY to incentivize testnet usage without depleting token supply.

**Testnet Budget:** 1,000,000 TUX (1% of total supply)

**Expected Testnet Duration:** 6 months (180 days)

**Daily Distribution Budget:** 1,000,000 / 180 = 5,555 TUX/day

**Assumptions:**
- Average TVL: $50,000 (in testnet terms)
- Mix: 40% USDC, 30% XLM, 20% WETH, 10% WBTC

**Distribution:**
```
USDC: $20,000 → 0.1 TUX/USDC/day → 2,000 TUX/day
XLM:  $15,000 → 0.01 TUX/XLM/day → 150 TUX/day (at $0.10/XLM)
WETH: $10,000 → 1.0 TUX/WETH/day → 5 TUX/day (at $2,000/WETH)
WBTC: $5,000  → 10.0 TUX/WBTC/day → 1.25 TUX/day (at $40,000/WBTC)

Total: ~2,156 TUX/day
```

**Safety Margin:** 2,156 / 5,555 = 39% of daily budget

This leaves 61% buffer for:
- Growth in TVL
- Bonus campaigns
- Referral rewards
- Unexpected spikes

**Effective APY (in TUX terms):**
```
USDC: (0.1 * 365 / 1) * 100 = 3,650% APY
XLM:  (0.01 * 365 / 1) * 100 = 365% APY
```

**Rationale for high testnet APY:**
- Testnet tokens have no monetary value
- High APY attracts more testers
- Demonstrates product experience
- Creates excitement and social proof

**Mainnet Conversion:**
- Testnet TUX → Mainnet TUX at 10:1 ratio
- Effective mainnet APY: 365% / 10 = 36.5% (still very attractive for early adopters)

---

## Risk Analysis

### Option A: Custom Blend Pool Risks

1. **Economic Unsustainability:** Requires constant funding to sustain artificial yields
2. **Protocol Violation:** Using Blend in unintended ways may cause unexpected behavior
3. **Complexity:** High chance of bugs or misconfigurations
4. **Mainnet Gap:** Testnet setup doesn't translate to mainnet (still no borrowers)
5. **Time Sink:** Ongoing maintenance takes focus away from core product

### Option B: TUX Rewards Risks

1. **Token Value Perception:** Users may view TUX as "fake" or "worthless"
   - **Mitigation:** Clear messaging about mainnet conversion and utility

2. **Gaming/Sybil Attacks:** Users create multiple accounts to farm rewards
   - **Mitigation:** Minimum deposit duration, rate limits, KYC for large claims

3. **Emission Rate Miscalculation:** Rewards distributed too fast or too slow
   - **Mitigation:** Start conservative, monitor daily, adjust rates dynamically

4. **Smart Contract Bugs:** Token contract has vulnerability
   - **Mitigation:** Use audited template, testnet-only deployment, security review

5. **User Confusion:** Don't understand how TUX works
   - **Mitigation:** Clear documentation, in-app tutorials, AI agent explanations

---

## Success Metrics

### Option B: TUX Rewards KPIs

**Week 1:**
- 50+ unique users earning TUX
- 100+ supply transactions
- $10,000+ TVL (testnet terms)
- 500+ TUX claimed

**Month 1:**
- 200+ unique users
- 1,000+ transactions
- $50,000+ TVL
- 50,000+ TUX distributed

**Month 3:**
- 500+ users
- 5,000+ transactions
- $100,000+ TVL
- 300,000+ TUX distributed
- Active Discord community (100+ members)
- 10+ community-contributed tutorials or guides

**Qualitative:**
- Positive user feedback on UX
- Social media mentions and content creation
- Feature requests and engagement
- Community governance participation

---

## Conclusion

While creating a custom Blend pool (Option A) is technically possible, it fights against the economic reality of testnet: there's no natural borrowing demand to generate yield.

**The TUX rewards system (Option B)** solves this elegantly by:
1. Providing immediate, sustainable yield
2. Following industry best practices
3. Building a token-holding community
4. Creating mainnet transition path
5. Minimizing technical complexity and risk

**Recommendation: Implement Option B (TUX Rewards) as the primary solution.**

If additional technical demonstration is desired, Option A can be pursued later as a secondary enhancement, but it should not be the primary yield mechanism.

---

## Next Steps

1. **Decision:** Approve TUX rewards approach
2. **Token Design:** Finalize tokenomics and utility
3. **Development:** Follow Phase 1 implementation roadmap (Week 1)
4. **Testing:** Internal testing with team accounts
5. **Launch:** Community announcement and onboarding
6. **Iterate:** Monitor, gather feedback, adjust rates

---

## Appendix A: Blend Pool Deployment Checklist

*If pursuing Option A, use this checklist:*

- [ ] Clone and setup blend-utils repository
- [ ] Configure testnet environment variables
- [ ] Create pool configuration JSON
- [ ] Define reserve parameters (collateral factor, interest rates)
- [ ] Deploy pool contract via pool factory
- [ ] Acquire BLND tokens for backstop
- [ ] Mint BLND:USDC LP tokens
- [ ] Fund backstop with LP tokens
- [ ] Verify backstop threshold met
- [ ] Test supply operation
- [ ] Test borrow operation (requires second account)
- [ ] Verify interest accrual
- [ ] Integrate pool address into Tuxedo backend
- [ ] Update pool discovery to include custom pool
- [ ] Implement artificial borrowing bot (optional)
- [ ] Monitor and fund ongoing yields

---

## Appendix B: TUX Token Resources

**Soroban Token Examples:**
- https://github.com/stellar/soroban-examples/tree/main/token
- https://soroban.stellar.org/docs/built-in-contracts/stellar-asset-contract

**Liquidity Mining References:**
- Uniswap V3 Liquidity Mining: https://docs.uniswap.org/contracts/v3/guides/liquidity-mining/overview
- Compound Governance: https://compound.finance/governance/comp
- Synthetix Rewards: https://docs.synthetix.io/integrations/staking/

**Testnet Incentive Programs:**
- Sei Network Testnet: https://www.sei.io/incentivized-testnet
- Berachain Testnet: https://www.berachain.com/testnet
- NuCypher Testnet: https://blog.nucypher.com/incentivized-testnet/

**Soroban Development:**
- Soroban Docs: https://soroban.stellar.org/docs
- Stellar CLI: https://developers.stellar.org/docs/tools/stellar-cli
- Soroban SDK: https://docs.rs/soroban-sdk

---

## Appendix C: Reward Rate Simulator

Use this formula to model different reward scenarios:

```python
def calculate_tux_apy(
    asset_price: float,
    tux_per_day: float,
    tux_price: float = 0.0  # Set to 0 for testnet
) -> dict:
    """
    Calculate effective APY from TUX rewards.

    Args:
        asset_price: USD price of deposited asset (e.g., 1.0 for USDC)
        tux_per_day: TUX earned per 1 unit deposited per day
        tux_price: USD price of TUX (0 for testnet)

    Returns:
        {
            'tux_per_year': TUX earned annually,
            'nominal_apy': APY in TUX terms (percentage),
            'usd_apy': APY in USD terms (percentage, 0 for testnet)
        }
    """
    tux_per_year = tux_per_day * 365
    nominal_apy = (tux_per_year / 1) * 100  # Per 1 unit deposited

    if tux_price > 0:
        tux_value_per_year = tux_per_year * tux_price
        usd_apy = (tux_value_per_year / asset_price) * 100
    else:
        usd_apy = 0

    return {
        'tux_per_year': tux_per_year,
        'nominal_apy': nominal_apy,
        'usd_apy': usd_apy
    }

# Example usage
usdc_apy = calculate_tux_apy(asset_price=1.0, tux_per_day=0.1)
print(f"USDC: {usdc_apy['nominal_apy']:.0f}% APY in TUX")
# Output: USDC: 3650% APY in TUX

xlm_apy = calculate_tux_apy(asset_price=0.10, tux_per_day=0.01)
print(f"XLM: {xlm_apy['nominal_apy']:.0f}% APY in TUX")
# Output: XLM: 365% APY in TUX
```

---

**End of Report**

*This report provides comprehensive research and implementation guidance for creating yield opportunities on Blend testnet through either custom pool deployment or TUX token rewards. The recommendation strongly favors the TUX rewards approach (Option B) due to lower complexity, better alignment with testnet economics, and proven industry practices.*
