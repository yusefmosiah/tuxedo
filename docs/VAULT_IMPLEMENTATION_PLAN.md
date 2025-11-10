# Tuxedo Vault Implementation Plan
## Practical Roadmap: From Wallet Import to Agent Vault Ecology

**Date:** 2025-11-10
**Branch:** claude/rethink-wallet-import-011CUz2ZBhrY5tPXZMH53F6C
**Status:** Implementation Planning
**Goal:** Replace wallet import with vault-based collateral system

---

## 🎯 Implementation Philosophy

**Incremental Migration Strategy:**
1. Build vault system alongside existing wallet import
2. Test thoroughly on testnet
3. Migrate users with incentives
4. Deprecate wallet import gracefully
5. Launch multi-agent vault ecology

**Do NOT break existing functionality while building new system.**

---

## 📐 System Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           TUXEDO VAULT ECOLOGY                               │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────┐
│   USER      │
│  (Wallet)   │
└──────┬──────┘
       │
       │ 1. Deposit 100 USDC
       ↓
┌──────────────────────────────────────────────────────────────┐
│                  VAULT SMART CONTRACT                         │
│  ┌────────────────────────────────────────────────────────┐ │
│  │  TUX-CORE (Conservative Vault)                         │ │
│  │  • TVL: $1.2M                                          │ │
│  │  • Shares: 1,000,000 TUX-CORE                         │ │
│  │  • Share Value: $1.20                                  │ │
│  │  • APY: 9.2%                                           │ │
│  └────────────────────────────────────────────────────────┘ │
│                                                               │
│  Assets Held:                                                 │
│  ├─ 500,000 USDC (42%)                                       │
│  ├─ 400,000 XLM  (33%)                                       │
│  ├─ 300,000 EURC (25%)                                       │
│  └─ 60,000 USDC  (5% reserve)                                │
│                                                               │
│  User Share: 100 TUX-CORE tokens                             │
│  User Value: 100 × $1.20 = $120                              │
└───────────────────────┬───────────────────────────────────────┘
                        │
                        │ 2. Agent manages assets
                        ↓
┌──────────────────────────────────────────────────────────────┐
│                  AI AGENT OPERATIONS                          │
│  ┌────────────────────────────────────────────────────────┐ │
│  │  Agent Strategy Engine                                  │ │
│  │  • Monitors DeFi opportunities                          │ │
│  │  • Executes yield farming operations                    │ │
│  │  • Generates research reports                           │ │
│  │  • Maintains risk limits                                │ │
│  └────────────────────────────────────────────────────────┘ │
│                                                               │
│  Recent Operations:                                           │
│  ├─ Lend 100K USDC to Blend @ 8.5% APY                      │
│  ├─ Provide 50K XLM/USDC liquidity @ 12% APY                │
│  ├─ Swap 10K USDC → EURC for arbitrage (+0.3%)              │
│  └─ Compound yield back into vault (+$1,200)                │
└───────────────────────┬───────────────────────────────────────┘
                        │
                        │ 3. Performance tracked
                        ↓
┌──────────────────────────────────────────────────────────────┐
│                STELLAR DEX (Trading)                          │
│  ┌────────────────────────────────────────────────────────┐ │
│  │  TUX-CORE / TUX-AGGRESSIVE Trading Pair                │ │
│  │  • Price: 0.92 (AGGRESSIVE outperforming)              │ │
│  │  • 24h Volume: $15,000                                  │ │
│  │  • Liquidity: $100,000                                  │ │
│  └────────────────────────────────────────────────────────┘ │
│                                                               │
│  User Options:                                                │
│  ├─ Hold TUX-CORE (compound yield)                           │
│  ├─ Trade TUX-CORE → TUX-AGGRESSIVE (if bullish)            │
│  ├─ Withdraw USDC (burn TUX-CORE)                            │
│  └─ Use TUX-CORE as collateral elsewhere                     │
└──────────────────────────────────────────────────────────────┘


┌─────────────────────────────────────────────────────────────┐
│               GOVERNANCE & ECONOMICS                         │
│  ┌────────────────────────────────────────────────────────┐│
│  │  TUX Governance Token                                   ││
│  │  • Stake TUX to vote on vault parameters               ││
│  │  • Earn revenue share from vault fees                  ││
│  │  • Tier access: Bronze/Silver/Gold                     ││
│  └────────────────────────────────────────────────────────┘│
│                                                              │
│  Fee Flow:                                                   │
│  Vault Yield → 90% to users, 10% to fees                   │
│  Fees → 50% dev, 30% TUX stakers, 20% treasury             │
└─────────────────────────────────────────────────────────────┘
```

---

## 🗓️ Phase-by-Phase Implementation

### Phase 0: Foundation & Planning (Week 1)
**Goal:** Set up development environment and finalize architecture

**Tasks:**
- [x] Review and refine vault architecture document
- [ ] Create detailed smart contract specifications
- [ ] Set up testnet development environment
- [ ] Design database schema for vault tracking
- [ ] Create UI/UX mockups for vault interface
- [ ] Write comprehensive test plan

**Deliverables:**
- Architecture document (VAULT_COLLATERAL_ARCHITECTURE.md)
- Smart contract spec (TuxedoVault.rs specification)
- UI mockups (Figma or similar)
- Test plan document

**Success Criteria:**
- All stakeholders aligned on architecture
- Smart contract spec peer-reviewed
- Test coverage plan approved

---

### Phase 1: Core Vault Smart Contract (Weeks 2-3)
**Goal:** Build and test foundational vault contract

#### Week 2: Basic Vault Contract

**Smart Contract Development:**

```rust
// File: contracts/tuxedo_vault/src/lib.rs

#[contract]
pub struct TuxedoVault {
    // Identity
    vault_id: Symbol,
    vault_name: String,
    admin: Address,

    // Assets
    accepted_assets: Vec<Address>,  // Asset contract addresses
    asset_balances: Map<Address, i128>,
    total_value_usd: i128,

    // Shares
    share_token: Address,  // Stellar asset for vault shares
    total_shares: i128,
    user_shares: Map<Address, i128>,

    // State
    paused: bool,
    initialized: bool,
}

#[contractimpl]
impl TuxedoVault {
    // Core functions to implement:
    pub fn initialize(
        env: Env,
        admin: Address,
        vault_id: Symbol,
        vault_name: String,
        share_token: Address
    ) -> Result<(), Error>;

    pub fn deposit(
        env: Env,
        user: Address,
        asset: Address,
        amount: i128
    ) -> Result<i128, Error>;

    pub fn withdraw(
        env: Env,
        user: Address,
        shares: i128
    ) -> Result<Vec<(Address, i128)>, Error>;

    pub fn get_share_value(env: Env) -> Result<f64, Error>;

    pub fn get_user_balance(env: Env, user: Address) -> Result<i128, Error>;
}
```

**Testing:**
- [ ] Unit tests for all vault functions
- [ ] Edge case testing (zero deposits, full withdrawal, etc.)
- [ ] Rounding error testing
- [ ] Gas optimization testing

**Tasks:**
```bash
# Development tasks
cd contracts/tuxedo_vault

# 1. Set up Soroban project
soroban contract init --name tuxedo_vault

# 2. Implement core contract
# Edit src/lib.rs with vault logic

# 3. Build contract
soroban contract build

# 4. Write unit tests
# Edit src/test.rs

# 5. Run tests
cargo test

# 6. Deploy to testnet
soroban contract deploy \
  --wasm target/wasm32-unknown-unknown/release/tuxedo_vault.wasm \
  --network testnet \
  --source ADMIN_SECRET
```

#### Week 3: Share Token & Advanced Features

**Share Token Integration:**
```rust
// Stellar Asset Token (SEP-41)
// Created per vault: TUX-CORE, TUX-AGGRESSIVE, etc.

impl TuxedoVault {
    pub fn create_share_token(
        env: Env,
        vault_id: Symbol
    ) -> Result<Address, Error> {
        // Use Stellar Asset Contract
        let token = create_stellar_asset(
            &env,
            admin,
            format!("TUX-{}", vault_id.to_string())
        );

        Ok(token)
    }

    pub fn mint_shares(&self, env: Env, user: Address, amount: i128) {
        // Mint vault share tokens to user
        self.share_token.mint(&env, &user, &amount);
        self.total_shares += amount;
        self.user_shares.set(&user,
            self.user_shares.get(&user).unwrap_or(0) + amount
        );
    }

    pub fn burn_shares(&self, env: Env, user: Address, amount: i128) {
        // Burn user's vault share tokens
        self.share_token.burn(&env, &user, &amount);
        self.total_shares -= amount;
        self.user_shares.set(&user,
            self.user_shares.get(&user).unwrap_or(0) - amount
        );
    }
}
```

**Risk Limits:**
```rust
pub struct RiskLimits {
    max_single_asset_pct: u32,      // e.g., 40%
    max_protocol_exposure_pct: u32,  // e.g., 25%
    min_liquid_reserve_pct: u32,     // e.g., 5%
}

impl TuxedoVault {
    pub fn verify_risk_limits(&self, env: &Env) -> Result<(), Error> {
        // Check asset concentration
        for (asset, balance) in self.asset_balances.iter() {
            let asset_pct = (balance * 100) / self.total_value_usd;
            if asset_pct > self.risk_limits.max_single_asset_pct {
                return Err(Error::RiskLimitViolation);
            }
        }

        // Check liquidity reserve
        let liquid_balance = self.get_liquid_balance(env);
        let liquid_pct = (liquid_balance * 100) / self.total_value_usd;
        if liquid_pct < self.risk_limits.min_liquid_reserve_pct {
            return Err(Error::InsufficientLiquidity);
        }

        Ok(())
    }
}
```

**Emergency Functions:**
```rust
impl TuxedoVault {
    pub fn pause(env: Env, admin: Address) -> Result<(), Error> {
        admin.require_auth();
        self.paused = true;
        env.events().publish((symbol_short!("paused"),), admin);
        Ok(())
    }

    pub fn unpause(env: Env, admin: Address) -> Result<(), Error> {
        admin.require_auth();
        self.paused = false;
        env.events().publish((symbol_short!("unpaused"),), admin);
        Ok(())
    }
}
```

**Deliverables:**
- Fully functional vault smart contract
- Comprehensive test suite (>90% coverage)
- Testnet deployment
- Contract audit report (self-audit checklist)

---

### Phase 2: Backend Integration (Weeks 4-5)
**Goal:** Connect vault to existing AI agent system

#### Week 4: Backend Vault Management

**Database Schema:**
```sql
-- File: backend/migrations/005_vault_system.sql

-- Vault registry
CREATE TABLE vaults (
    id TEXT PRIMARY KEY,
    vault_contract_address TEXT NOT NULL UNIQUE,
    vault_name TEXT NOT NULL,
    vault_type TEXT NOT NULL,  -- 'core', 'aggressive', 'research', 'stable', 'personal'
    agent_address TEXT NOT NULL,
    share_token_address TEXT NOT NULL,

    -- Configuration
    accepted_assets TEXT[],  -- JSON array of asset codes
    risk_limits JSONB,
    fee_structure JSONB,

    -- State
    status TEXT DEFAULT 'active',  -- 'active', 'paused', 'closed'
    tvl_usd DECIMAL(20,2) DEFAULT 0,
    total_shares BIGINT DEFAULT 0,
    share_value_usd DECIMAL(20,8) DEFAULT 1.0,

    -- Performance
    inception_date TIMESTAMP DEFAULT NOW(),
    current_apy DECIMAL(10,2),
    total_yield_generated DECIMAL(20,2) DEFAULT 0,

    -- Metadata
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- User vault positions
CREATE TABLE user_vault_positions (
    id SERIAL PRIMARY KEY,
    user_id TEXT NOT NULL,
    vault_id TEXT NOT NULL REFERENCES vaults(id),

    -- Position
    shares BIGINT NOT NULL DEFAULT 0,
    initial_deposit_usd DECIMAL(20,2),
    current_value_usd DECIMAL(20,2),

    -- Tracking
    first_deposit_at TIMESTAMP DEFAULT NOW(),
    last_transaction_at TIMESTAMP DEFAULT NOW(),

    UNIQUE(user_id, vault_id)
);

-- Vault operations log
CREATE TABLE vault_operations (
    id SERIAL PRIMARY KEY,
    vault_id TEXT NOT NULL REFERENCES vaults(id),
    operation_type TEXT NOT NULL,  -- 'deposit', 'withdraw', 'agent_operation'

    -- Transaction details
    tx_hash TEXT,
    user_address TEXT,

    -- Operation data
    operation_data JSONB,  -- Asset amounts, operation details, etc.

    -- Impact
    vault_value_before DECIMAL(20,2),
    vault_value_after DECIMAL(20,2),
    impact_usd DECIMAL(20,2),

    -- Research
    research_citation TEXT,
    research_report_url TEXT,

    timestamp TIMESTAMP DEFAULT NOW()
);

-- Vault performance snapshots
CREATE TABLE vault_performance_snapshots (
    id SERIAL PRIMARY KEY,
    vault_id TEXT NOT NULL REFERENCES vaults(id),

    snapshot_date DATE NOT NULL,
    share_value_usd DECIMAL(20,8),
    tvl_usd DECIMAL(20,2),
    apy_1d DECIMAL(10,2),
    apy_7d DECIMAL(10,2),
    apy_30d DECIMAL(10,2),
    apy_ytd DECIMAL(10,2),

    UNIQUE(vault_id, snapshot_date)
);

CREATE INDEX idx_vaults_status ON vaults(status);
CREATE INDEX idx_user_positions_user ON user_vault_positions(user_id);
CREATE INDEX idx_vault_ops_vault_time ON vault_operations(vault_id, timestamp DESC);
CREATE INDEX idx_performance_vault_date ON vault_performance_snapshots(vault_id, snapshot_date DESC);
```

**Backend API:**
```python
# File: backend/api/routes/vaults.py

from fastapi import APIRouter, Depends, HTTPException
from typing import List, Optional
from pydantic import BaseModel

router = APIRouter(prefix="/vaults", tags=["vaults"])

class DepositRequest(BaseModel):
    vault_id: str
    asset_code: str
    amount: float

class WithdrawRequest(BaseModel):
    vault_id: str
    shares: int

class VaultInfo(BaseModel):
    vault_id: str
    vault_name: str
    vault_type: str
    tvl_usd: float
    current_apy: float
    share_value_usd: float
    total_shares: int
    user_shares: Optional[int] = None
    user_value_usd: Optional[float] = None

@router.get("/", response_model=List[VaultInfo])
async def get_vaults(user_id: Optional[str] = None):
    """Get all available vaults, optionally with user positions"""
    # Query database for vaults
    # If user_id provided, join with user_vault_positions
    pass

@router.get("/{vault_id}", response_model=VaultInfo)
async def get_vault(vault_id: str, user_id: Optional[str] = None):
    """Get specific vault details"""
    pass

@router.post("/{vault_id}/deposit")
async def deposit_to_vault(vault_id: str, request: DepositRequest, user_id: str):
    """
    Deposit assets into vault and receive share tokens

    Flow:
    1. Verify user has sufficient balance
    2. Build Stellar transaction: Transfer asset to vault
    3. Vault contract mints share tokens to user
    4. Return transaction for user to sign (or agent signs if delegated)
    """
    pass

@router.post("/{vault_id}/withdraw")
async def withdraw_from_vault(vault_id: str, request: WithdrawRequest, user_id: str):
    """
    Burn share tokens and withdraw assets

    Flow:
    1. Verify user has sufficient shares
    2. Calculate withdrawal amount based on current share value
    3. Build transaction: Burn shares, transfer assets to user
    4. Return transaction for user to sign
    """
    pass

@router.get("/{vault_id}/operations")
async def get_vault_operations(vault_id: str, limit: int = 50):
    """Get recent vault operations for activity feed"""
    pass

@router.get("/{vault_id}/performance")
async def get_vault_performance(vault_id: str, period: str = "30d"):
    """Get vault performance metrics over time"""
    pass
```

#### Week 5: Agent Integration

**Agent Vault Manager:**
```python
# File: backend/agent/vault_manager.py

from stellar_sdk import Keypair, TransactionBuilder, Network, Asset
from typing import Dict, List, Optional
import logging

logger = logging.getLogger(__name__)

class AgentVaultManager:
    """
    Manages agent operations within vaults
    Replaces direct wallet management
    """

    def __init__(self, vault_contract_address: str, agent_keypair: Keypair):
        self.vault_address = vault_contract_address
        self.agent_keypair = agent_keypair

    async def execute_operation(
        self,
        operation_type: str,
        params: Dict
    ) -> Dict:
        """
        Execute agent operation through vault contract

        Examples:
        - Lend USDC to Blend
        - Provide liquidity to Soroswap
        - Swap assets for arbitrage
        - Compound yield
        """

        # Verify operation is allowed by vault risk limits
        if not await self.verify_operation_allowed(operation_type, params):
            raise ValueError(f"Operation {operation_type} violates risk limits")

        # Build transaction
        tx_builder = self.build_operation_transaction(operation_type, params)

        # Sign with agent key
        tx = tx_builder.build()
        tx.sign(self.agent_keypair)

        # Submit to network
        response = await self.submit_transaction(tx)

        # Log operation
        await self.log_vault_operation(operation_type, params, response)

        # Update performance metrics
        await self.update_vault_metrics()

        return response

    async def verify_operation_allowed(
        self,
        operation_type: str,
        params: Dict
    ) -> bool:
        """Check if operation complies with vault risk limits"""

        # Get current vault state
        vault_state = await self.get_vault_state()

        # Simulate operation
        simulated_state = self.simulate_operation(vault_state, operation_type, params)

        # Check against risk limits
        risk_limits = await self.get_vault_risk_limits()

        # Check asset concentration
        for asset, balance in simulated_state.asset_balances.items():
            asset_pct = (balance / simulated_state.total_value) * 100
            if asset_pct > risk_limits.max_single_asset_pct:
                logger.warning(f"Operation would violate asset concentration limit")
                return False

        # Check liquidity reserve
        liquid_pct = (simulated_state.liquid_balance / simulated_state.total_value) * 100
        if liquid_pct < risk_limits.min_liquid_reserve_pct:
            logger.warning(f"Operation would violate liquidity reserve requirement")
            return False

        return True

    async def generate_research_report(
        self,
        operation_type: str,
        params: Dict,
        result: Dict
    ) -> str:
        """Generate research report explaining operation"""

        # Use LLM to generate explanation
        prompt = f"""
        Generate a research report explaining this DeFi operation:

        Operation: {operation_type}
        Parameters: {params}
        Result: {result}

        Explain:
        1. Why this operation was chosen
        2. Expected yield/risk
        3. How it fits into overall strategy
        4. Any research/citations that informed this decision
        """

        report = await self.llm.generate(prompt)

        # Store report
        report_url = await self.store_research_report(report)

        return report_url
```

**Integration with Existing Agent Tools:**
```python
# File: backend/agent/tool_factory.py

# Modify existing agent tools to use vault manager

@tool
async def agent_lend_to_blend(
    asset: str,
    amount: float,
    pool: str,
    vault_id: str  # NEW: Specify which vault
) -> str:
    """
    Lend assets to Blend protocol through vault
    """

    # Get vault manager
    vault_manager = get_vault_manager(vault_id)

    # Execute operation through vault
    result = await vault_manager.execute_operation(
        operation_type="lend_blend",
        params={
            "asset": asset,
            "amount": amount,
            "pool": pool
        }
    )

    # Generate research report
    report_url = await vault_manager.generate_research_report(
        "lend_blend",
        params,
        result
    )

    return f"Lent {amount} {asset} to Blend {pool}. Report: {report_url}"
```

**Deliverables:**
- Database migrations applied
- Vault API endpoints functional
- Agent vault manager integrated
- Existing agent tools updated to work with vaults

---

### Phase 3: Frontend Vault Interface (Weeks 6-7)
**Goal:** Build user-facing vault dashboard and deposit/withdraw UI

#### Week 6: Vault Dashboard

**Components:**
```typescript
// File: src/pages/VaultDashboard.tsx

import React, { useEffect, useState } from 'react';
import { useVaults } from '../hooks/useVaults';
import { VaultCard } from '../components/vaults/VaultCard';
import { PerformanceChart } from '../components/vaults/PerformanceChart';
import { ActivityFeed } from '../components/vaults/ActivityFeed';

export const VaultDashboard: React.FC = () => {
  const { vaults, userPositions, loading } = useVaults();

  return (
    <div className="vault-dashboard">
      <header>
        <h1>Tuxedo Vaults</h1>
        <p>AI-managed yield farming vaults on Stellar</p>
      </header>

      {/* User Portfolio Summary */}
      <section className="portfolio-summary">
        <div className="stat">
          <h3>Total Portfolio Value</h3>
          <p>${userPositions.totalValue.toLocaleString()}</p>
        </div>
        <div className="stat">
          <h3>Total Yield (24h)</h3>
          <p className="positive">+${userPositions.yield24h.toLocaleString()}</p>
        </div>
        <div className="stat">
          <h3>Average APY</h3>
          <p>{userPositions.avgApy.toFixed(1)}%</p>
        </div>
      </section>

      {/* Available Vaults */}
      <section className="vault-grid">
        <h2>Available Vaults</h2>
        <div className="grid">
          {vaults.map(vault => (
            <VaultCard
              key={vault.id}
              vault={vault}
              userPosition={userPositions.find(p => p.vaultId === vault.id)}
            />
          ))}
        </div>
      </section>

      {/* Performance Charts */}
      <section className="performance">
        <h2>Performance History</h2>
        <PerformanceChart vaults={vaults} period="30d" />
      </section>

      {/* Activity Feed */}
      <section className="activity">
        <h2>Recent Activity</h2>
        <ActivityFeed vaultId={null} limit={20} />
      </section>
    </div>
  );
};
```

```typescript
// File: src/components/vaults/VaultCard.tsx

interface VaultCardProps {
  vault: VaultInfo;
  userPosition?: UserPosition;
}

export const VaultCard: React.FC<VaultCardProps> = ({ vault, userPosition }) => {
  const [showDepositModal, setShowDepositModal] = useState(false);
  const [showWithdrawModal, setShowWithdrawModal] = useState(false);

  return (
    <div className="vault-card">
      {/* Header */}
      <div className="vault-header">
        <h3>{vault.name}</h3>
        <span className={`badge ${vault.type}`}>{vault.type}</span>
      </div>

      {/* Stats */}
      <div className="vault-stats">
        <div className="stat">
          <label>APY</label>
          <value className="highlight">{vault.currentApy.toFixed(1)}%</value>
        </div>
        <div className="stat">
          <label>TVL</label>
          <value>${vault.tvlUsd.toLocaleString()}</value>
        </div>
        <div className="stat">
          <label>Share Value</label>
          <value>${vault.shareValueUsd.toFixed(4)}</value>
        </div>
      </div>

      {/* User Position (if any) */}
      {userPosition && (
        <div className="user-position">
          <div className="position-row">
            <span>Your Shares:</span>
            <span>{userPosition.shares.toLocaleString()}</span>
          </div>
          <div className="position-row">
            <span>Current Value:</span>
            <span>${userPosition.currentValueUsd.toLocaleString()}</span>
          </div>
          <div className="position-row">
            <span>Profit:</span>
            <span className={userPosition.profitUsd >= 0 ? 'positive' : 'negative'}>
              ${userPosition.profitUsd.toLocaleString()} ({userPosition.profitPct.toFixed(1)}%)
            </span>
          </div>
        </div>
      )}

      {/* Actions */}
      <div className="vault-actions">
        <button onClick={() => setShowDepositModal(true)}>
          Deposit
        </button>
        {userPosition && (
          <button onClick={() => setShowWithdrawModal(true)}>
            Withdraw
          </button>
        )}
        <button variant="secondary" onClick={() => navigate(`/vaults/${vault.id}`)}>
          Details
        </button>
      </div>

      {/* Modals */}
      {showDepositModal && (
        <DepositModal
          vault={vault}
          onClose={() => setShowDepositModal(false)}
        />
      )}
      {showWithdrawModal && userPosition && (
        <WithdrawModal
          vault={vault}
          userPosition={userPosition}
          onClose={() => setShowWithdrawModal(false)}
        />
      )}
    </div>
  );
};
```

#### Week 7: Deposit/Withdraw Modals

```typescript
// File: src/components/vaults/DepositModal.tsx

export const DepositModal: React.FC<{ vault: VaultInfo; onClose: () => void }> = ({
  vault,
  onClose
}) => {
  const { walletAddress, stellarKit } = useWallet();
  const [asset, setAsset] = useState('USDC');
  const [amount, setAmount] = useState('');
  const [estimatedShares, setEstimatedShares] = useState(0);

  useEffect(() => {
    // Calculate estimated shares based on amount and current share value
    const shares = parseFloat(amount) / vault.shareValueUsd;
    setEstimatedShares(shares || 0);
  }, [amount, vault.shareValueUsd]);

  const handleDeposit = async () => {
    try {
      // Build deposit transaction
      const tx = await buildDepositTransaction(
        vault.id,
        asset,
        parseFloat(amount),
        walletAddress
      );

      // Sign with user wallet
      const signedTx = await stellarKit.sign({
        xdr: tx.toXDR(),
        network: 'mainnet'
      });

      // Submit transaction
      await submitTransaction(signedTx);

      // Show success
      toast.success(`Deposited ${amount} ${asset} to ${vault.name}`);
      onClose();
    } catch (error) {
      toast.error(`Deposit failed: ${error.message}`);
    }
  };

  return (
    <Modal isOpen onClose={onClose}>
      <h2>Deposit to {vault.name}</h2>

      <div className="deposit-form">
        {/* Asset Selector */}
        <div className="form-group">
          <label>Asset</label>
          <select value={asset} onChange={(e) => setAsset(e.target.value)}>
            {vault.acceptedAssets.map(a => (
              <option key={a} value={a}>{a}</option>
            ))}
          </select>
        </div>

        {/* Amount Input */}
        <div className="form-group">
          <label>Amount</label>
          <input
            type="number"
            value={amount}
            onChange={(e) => setAmount(e.target.value)}
            placeholder="0.00"
          />
        </div>

        {/* Estimated Output */}
        <div className="estimate">
          <p>You will receive:</p>
          <p className="highlight">{estimatedShares.toFixed(2)} {vault.shareToken}</p>
          <p className="subtext">
            At current share value of ${vault.shareValueUsd.toFixed(4)}
          </p>
        </div>

        {/* Fee Info */}
        <div className="fee-info">
          <p>Management Fee: {vault.managementFeePct}% annually</p>
          <p>Performance Fee: {vault.performanceFeePct}% on profits</p>
        </div>

        {/* Actions */}
        <div className="modal-actions">
          <button variant="secondary" onClick={onClose}>Cancel</button>
          <button onClick={handleDeposit} disabled={!amount || parseFloat(amount) <= 0}>
            Deposit
          </button>
        </div>
      </div>
    </Modal>
  );
};
```

**Deliverables:**
- Vault dashboard with portfolio summary
- Vault cards showing key metrics
- Deposit/withdraw modals functional
- Activity feed showing agent operations
- Performance charts

---

### Phase 4: Multi-Vault Deployment (Week 8)
**Goal:** Deploy 3-4 different vault types on testnet

**Vaults to Deploy:**

1. **TUX-CORE** (Conservative)
   - Strategy: 60% stablecoin lending, 30% low-vol LP, 10% reserves
   - Target APY: 8-12%
   - Risk: Low

2. **TUX-STABLE** (Ultra-Conservative)
   - Strategy: 100% stablecoin lending
   - Target APY: 5-8%
   - Risk: Very Low

3. **TUX-AGGRESSIVE** (High-Yield)
   - Strategy: Active trading, high-APY lending, volatile LPs
   - Target APY: 15-30%
   - Risk: High

4. **TUX-RESEARCH** (Knowledge-Backed)
   - Strategy: Citation-driven, research report generation
   - Target APY: 10-20% + CHOIR rewards
   - Risk: Medium

**Deployment Checklist per Vault:**
- [ ] Deploy vault smart contract
- [ ] Create vault share token (Stellar asset)
- [ ] Configure risk limits
- [ ] Set up agent with strategy parameters
- [ ] Seed initial liquidity (if applicable)
- [ ] Configure fee structure
- [ ] Add to database registry
- [ ] Test deposit/withdraw flows
- [ ] Create liquidity pools for share tokens on DEX
- [ ] Document vault in user guide

---

### Phase 5: Migration from Wallet Import (Weeks 9-10)
**Goal:** Migrate existing users to vault system

#### Week 9: Migration Tool Development

**Migration Flow:**
```python
# File: backend/api/routes/migration.py

@router.post("/migrate-to-vault")
async def migrate_wallet_to_vault(
    user_id: str,
    target_vault_id: str = "TUX-CORE"
):
    """
    Migrate user from wallet import model to vault model

    Steps:
    1. Calculate user's current position value in agent-managed wallet
    2. Transfer all assets from agent wallet to vault
    3. Mint equivalent vault shares to user
    4. Archive old wallet
    5. Award migration bonus (TUX tokens)
    """

    # 1. Get current wallet value
    account_manager = AccountManager()
    user_accounts = account_manager.get_user_accounts(user_id, chain="stellar")

    total_value_usd = 0
    assets_to_transfer = []

    for account in user_accounts:
        for balance in account['balances']:
            asset_value = get_asset_usd_value(balance['asset'], balance['amount'])
            total_value_usd += asset_value
            assets_to_transfer.append({
                'asset': balance['asset'],
                'amount': balance['amount']
            })

    # 2. Transfer assets to vault
    vault_manager = get_vault_manager(target_vault_id)

    for asset_transfer in assets_to_transfer:
        await vault_manager.receive_migration_deposit(
            user_address=user_accounts[0]['public_key'],
            asset=asset_transfer['asset'],
            amount=asset_transfer['amount']
        )

    # 3. Calculate and mint shares
    vault_info = await get_vault_info(target_vault_id)
    shares_to_mint = total_value_usd / vault_info.share_value_usd

    await vault_manager.mint_shares(
        user_address=user_accounts[0]['public_key'],
        shares=shares_to_mint
    )

    # 4. Archive old wallet
    for account in user_accounts:
        await account_manager.archive_account(user_id, account['id'])

    # 5. Award migration bonus
    bonus_tux = 10  # 10 TUX tokens for early migration
    await tux_token.mint(user_accounts[0]['public_key'], bonus_tux)

    return {
        "success": True,
        "migrated_value_usd": total_value_usd,
        "vault_shares": shares_to_mint,
        "bonus_tux": bonus_tux,
        "vault_id": target_vault_id
    }
```

#### Week 10: User Communication & Execution

**Communication Timeline:**

**Week 10, Day 1-2: Announcement**
- Email blast to all users
- In-app banner notification
- Blog post explaining benefits
- Tutorial video

**Week 10, Day 3-5: Education**
- Live Q&A session
- Updated documentation
- FAQ section
- Support team briefing

**Week 10, Day 6-14: Migration Period**
- In-app migration wizard
- One-click migration button
- Progress tracking
- Support tickets handled

**Incentive Structure:**
```
Week 1: Migrate now, get 10 TUX + 0% fees for 30 days
Week 2: Migrate now, get 8 TUX + 0% fees for 20 days
Week 3: Migrate now, get 5 TUX + 0% fees for 10 days
Week 4+: Migrate now, get 3 TUX
```

**Deliverables:**
- Migration API endpoint functional
- Frontend migration wizard
- User communication materials
- Support documentation
- Monitoring dashboard for migration progress

---

### Phase 6: DEX Integration & Secondary Markets (Week 11)
**Goal:** Enable trading of vault share tokens

**Tasks:**

1. **Create Liquidity Pools:**
```bash
# For each vault token pair
# TUX-CORE / USDC
# TUX-AGGRESSIVE / USDC
# TUX-CORE / TUX-AGGRESSIVE

stellar-cli liquidity-pool create \
  --asset-a TUX-CORE:VAULT_ADDRESS \
  --asset-b USDC:ISSUER_ADDRESS \
  --fee 30 \
  --network mainnet
```

2. **Seed Liquidity:**
```python
# Protocol-owned liquidity for bootstrapping
async def seed_vault_token_liquidity():
    pools = [
        {"asset_a": "TUX-CORE", "asset_b": "USDC", "amount_a": 10000, "amount_b": 10000},
        {"asset_a": "TUX-AGGRESSIVE", "asset_b": "USDC", "amount_a": 5000, "amount_b": 5000},
        {"asset_a": "TUX-CORE", "asset_b": "TUX-AGGRESSIVE", "amount_a": 5000, "amount_b": 5000},
    ]

    for pool in pools:
        await provide_liquidity(
            asset_a=pool["asset_a"],
            asset_b=pool["asset_b"],
            amount_a=pool["amount_a"],
            amount_b=pool["amount_b"]
        )
```

3. **Market Making Bot:**
```python
# File: backend/market_maker/vault_token_mm.py

class VaultTokenMarketMaker:
    """
    Provides liquidity and maintains spreads for vault tokens
    Ensures vault tokens track underlying asset value
    """

    async def run(self):
        while True:
            for pair in self.trading_pairs:
                # Get current vault share value
                intrinsic_value = await self.get_vault_share_value(pair.vault_id)

                # Get current market price
                market_price = await self.get_market_price(pair.asset_a, pair.asset_b)

                # If divergence > threshold, place corrective orders
                divergence = abs(market_price - intrinsic_value) / intrinsic_value

                if divergence > 0.02:  # 2% threshold
                    await self.place_corrective_orders(pair, intrinsic_value, market_price)

            await asyncio.sleep(60)  # Run every minute
```

4. **Frontend Trading Interface:**
```typescript
// Add to VaultCard component
<button onClick={() => navigate(`/trade/${vault.shareToken}`)}>
  Trade Shares
</button>

// Create trading page
// File: src/pages/VaultTokenTrade.tsx
export const VaultTokenTrade: React.FC = () => {
  // Integrate with Stellar DEX
  // Show order book
  // Allow limit/market orders
  // Show price charts
};
```

**Deliverables:**
- Liquidity pools created for all vault tokens
- Market making bot deployed
- Trading interface in frontend
- Price oracle integration

---

### Phase 7: TUX Governance Token (Weeks 12-13)
**Goal:** Launch TUX token with governance and staking

**Week 12: Token Contract & Distribution**

```rust
// File: contracts/tux_token/src/lib.rs

#[contract]
pub struct TuxToken {
    admin: Address,
    total_supply: i128,
    balances: Map<Address, i128>,
    allowances: Map<(Address, Address), i128>,

    // Staking
    staked_balances: Map<Address, i128>,
    stake_timestamps: Map<Address, u64>,

    // Governance
    proposals: Map<u64, Proposal>,
    votes: Map<(u64, Address), Vote>,

    // Tiers
    tier_requirements: TierRequirements,
}

pub struct TierRequirements {
    bronze: i128,   // 100 TUX
    silver: i128,   // 1,000 TUX
    gold: i128,     // 10,000 TUX
}

#[contractimpl]
impl TuxToken {
    // Standard token functions (transfer, approve, etc.)

    // Staking
    pub fn stake(env: Env, user: Address, amount: i128) -> Result<(), Error>;
    pub fn unstake(env: Env, user: Address, amount: i128) -> Result<(), Error>;
    pub fn claim_staking_rewards(env: Env, user: Address) -> Result<i128, Error>;

    // Governance
    pub fn create_proposal(
        env: Env,
        proposer: Address,
        description: String,
        parameter: String,
        new_value: String
    ) -> Result<u64, Error>;

    pub fn vote(
        env: Env,
        voter: Address,
        proposal_id: u64,
        support: bool
    ) -> Result<(), Error>;

    pub fn execute_proposal(env: Env, proposal_id: u64) -> Result<(), Error>;

    // Tier system
    pub fn get_user_tier(env: Env, user: Address) -> Tier;
}
```

**Distribution:**
```python
# Initial distribution
TOTAL_SUPPLY = 1_000_000

distribution = {
    "community": 400_000,      # 40% - Airdrops, rewards
    "protocol_treasury": 300_000,  # 30% - Development, partnerships
    "team": 200_000,          # 20% - Vested over 2 years
    "liquidity_reserve": 100_000   # 10% - DEX liquidity
}

# Airdr op to early users
early_users = get_users_before_date("2025-11-10")
airdrop_per_user = 100  # 100 TUX per early user

# Migration bonus already distributed
```

**Week 13: Governance & Staking UI**

```typescript
// File: src/pages/Governance.tsx

export const GovernancePage: React.FC = () => {
  const { tuxBalance, stakedBalance } = useTuxToken();
  const { activeProposals, pastProposals } = useGovernance();

  return (
    <div className="governance-page">
      <section className="user-tux">
        <h2>Your TUX</h2>
        <div className="balances">
          <div>Wallet: {tuxBalance.toLocaleString()} TUX</div>
          <div>Staked: {stakedBalance.toLocaleString()} TUX</div>
          <div>Tier: {getUserTier(stakedBalance)}</div>
        </div>
        <button onClick={() => setShowStakeModal(true)}>Stake TUX</button>
      </section>

      <section className="proposals">
        <h2>Active Proposals</h2>
        {activeProposals.map(proposal => (
          <ProposalCard key={proposal.id} proposal={proposal} />
        ))}
      </section>
    </div>
  );
};
```

**Deliverables:**
- TUX token contract deployed
- Token distribution executed
- Staking functionality live
- Governance interface functional
- First community vote executed

---

### Phase 8: Mainnet Launch & Marketing (Weeks 14-16)

**Week 14: Security Audit & Bug Bounty**
- [ ] Professional smart contract audit
- [ ] Penetration testing
- [ ] Bug bounty program (up to $10K rewards)
- [ ] Security review by community
- [ ] Final code freeze

**Week 15: Mainnet Deployment**
- [ ] Deploy all vault contracts to mainnet
- [ ] Deploy TUX token to mainnet
- [ ] Migrate testnet users (optional)
- [ ] Seed initial liquidity
- [ ] Launch monitoring and alerting

**Week 16: Marketing & Growth**
- [ ] Official launch announcement
- [ ] Press release
- [ ] Community events (AMAs, workshops)
- [ ] Partnership announcements
- [ ] Influencer outreach
- [ ] Educational content series

---

## 📊 Success Metrics & Monitoring

### Phase 1-2 (Smart Contracts & Backend)
- [ ] All vault functions working
- [ ] Test coverage > 90%
- [ ] No critical security issues
- [ ] Performance benchmarks met

### Phase 3-4 (Frontend & Multi-Vault)
- [ ] Deposit/withdraw flows functional
- [ ] All vaults deployed
- [ ] User testing completed
- [ ] UI/UX feedback positive

### Phase 5-6 (Migration & DEX)
- [ ] > 80% users migrated
- [ ] Vault tokens trading on DEX
- [ ] Liquidity pools healthy
- [ ] No major issues reported

### Phase 7-8 (TUX & Launch)
- [ ] TUX token distributed
- [ ] Governance active
- [ ] Mainnet TVL > $100K
- [ ] > 50 active users

---

## 🚨 Risk Mitigation

### Technical Risks
- **Smart contract bugs**: Professional audit, bug bounty
- **Oracle failures**: Multiple price sources, circuit breakers
- **Agent errors**: Risk limits, manual override capability
- **Network congestion**: Retry logic, fee management

### Economic Risks
- **Low liquidity**: Protocol-owned liquidity, market making
- **Vault underperformance**: Transparent metrics, easy exit
- **TUX token dump**: Vesting, staking incentives
- **Fee sustainability**: Dynamic fee adjustment, governance

### Operational Risks
- **Server downtime**: Redundant infrastructure, monitoring
- **Key compromise**: Multi-sig, hardware security
- **Regulatory issues**: Legal review, compliance framework
- **User confusion**: Clear documentation, support team

---

## 🎯 Conclusion

This implementation plan provides a clear roadmap from the current wallet import model to a sophisticated multi-agent vault ecology. The phased approach allows for:

1. **Incremental development** - No big-bang deployment
2. **Continuous testing** - Each phase validated before next
3. **User migration** - Smooth transition with incentives
4. **Risk management** - Security and economics considered throughout

**Timeline Summary:**
- Weeks 1-3: Core vault contract
- Weeks 4-5: Backend integration
- Weeks 6-7: Frontend interface
- Week 8: Multi-vault deployment
- Weeks 9-10: User migration
- Week 11: DEX integration
- Weeks 12-13: TUX governance
- Weeks 14-16: Mainnet launch

**Total Time: 16 weeks (~4 months)**

**The result:** A secure, transparent, AI-managed vault system that sets a new standard for DeFi on Stellar. 🚀
