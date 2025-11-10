# 🎩 The Playful Path to Vaults
## A 1.6-Hour Sprint from Wallet Custody to Vault Sovereignty

**Date:** 2025-11-10
**Status:** Active Sprint
**Energy Level:** YOLO (but testnet first)
**Goal:** Ship MVP vault architecture TODAY

---

## 🎯 The Vision (in 30 seconds)

**Current:** Users paste private keys → Agent holds keys → Feels wrong (and it is!)
**Future:** Users deposit USDC → Get vault shares → Agent manages vault → Users keep keys → Performance becomes tradeable

**Why this matters:** We're building the pattern for all agentic DeFi. Non-custodial. Transparent. Composable.

---

## 💰 Performance Fee Structure (The Fair Split)

**Yield Distribution:**
- **User:** 75% of yield (you provide capital)
- **Agent:** 15% of yield (AI does the work)
- **Platform:** 10% of yield (infrastructure & development)

**Example:** Vault earns 100 USDC yield over a week
```
User receives:    75 USDC (keeps 75% of gains)
Agent receives:   15 USDC (performance fee)
Platform receives: 10 USDC (protocol fee)
Total:           100 USDC
```

**Competitive Analysis:**
- Yearn Finance: 20% performance fee
- Enzyme Finance: 20% performance fee
- Index Coop: 0.95% streaming fee
- **Tuxedo MVP:** 25% total fees (15% agent + 10% platform) - competitive with top DeFi protocols

**No management fee for MVP.** Just performance-based. Align incentives.

---

## 🏗️ MVP Vault Architecture

### Core Components

```
┌──────────────────────────────────────────────────────┐
│  TuxedoVault Smart Contract (Soroban)                │
│  ┌────────────────────────────────────────────────┐ │
│  │  State                                          │ │
│  │  • total_assets: Map<AssetId, i128>            │ │
│  │  • total_shares: i128                           │ │
│  │  • agent_address: Address                       │ │
│  │  │  platform_address: Address                   │ │
│  │  • share_token: Address (Stellar Asset)        │ │
│  └────────────────────────────────────────────────┘ │
│                                                       │
│  ┌────────────────────────────────────────────────┐ │
│  │  Functions                                      │ │
│  │  • initialize(admin, agent, platform)          │ │
│  │  • deposit(user, asset, amount) → shares       │ │
│  │  • withdraw(user, shares) → assets             │ │
│  │  • agent_execute(strategy) [agent only]        │ │
│  │  • distribute_yield() [anyone can call]        │ │
│  │  • get_share_value() → i128                    │ │
│  └────────────────────────────────────────────────┘ │
└──────────────────────────────────────────────────────┘
```

### Vault Share Token (TUX-CORE)

**Type:** Stellar Asset (SEP-41 compatible)
**Issuer:** TuxedoVault contract address
**Properties:**
- Immediately tradeable on Stellar DEX
- Represents proportional claim on vault assets
- Price reflects agent performance (TVL / total_shares)

### Agent Custody Model

**Agent Address:**
- Backend creates ONE dedicated Stellar keypair for the vault agent
- Agent address is authorized in vault contract to execute strategies
- Agent can interact with: Blend pools, Stellar DEX, Soroban contracts
- Agent CANNOT: Withdraw user funds (only users can via `withdraw()`)

**Multiple Addresses (Future):**
- Different agents = different vault contracts
- TUX-CORE agent, TUX-AGGRESSIVE agent, TUX-RESEARCH agent
- Each with its own strategy and performance tracking

**No Timelock (MVP):**
- Agent can execute immediately
- Future: Add governance-controlled timelock for parameter changes
- Future: Add emergency pause mechanism

---

## 🚀 The 1.6-Hour Sprint Breakdown

### Hour 0.0 - 0.3: Vault Contract (Rust/Soroban)

**File:** `contracts/vault/src/lib.rs`

**Core Logic:**
```rust
#[contract]
pub struct TuxedoVault;

#[contractimpl]
impl TuxedoVault {
    // Initialize vault
    pub fn initialize(
        env: Env,
        admin: Address,
        agent: Address,
        platform: Address,
        share_token: Address,
    ) -> Result<(), Error>;

    // User deposits USDC, receives vault shares
    pub fn deposit(
        env: Env,
        user: Address,
        asset: Address,
        amount: i128,
    ) -> Result<i128, Error>; // Returns shares minted

    // User burns shares, receives proportional assets
    pub fn withdraw(
        env: Env,
        user: Address,
        shares: i128,
    ) -> Result<i128, Error>; // Returns asset amount

    // Agent executes strategy (Blend supply/withdraw)
    pub fn agent_execute(
        env: Env,
        strategy: Strategy,
    ) -> Result<(), Error>;

    // Calculate current share value
    pub fn get_share_value(env: Env) -> i128;

    // Distribute yield to agent & platform
    pub fn distribute_yield(env: Env) -> Result<(), Error>;
}
```

**Key Calculations:**
```rust
// Share value = Total Assets / Total Shares
fn calculate_share_value(env: &Env) -> i128 {
    let total_assets = get_total_vault_assets(env);
    let total_shares = get_total_shares(env);
    if total_shares == 0 { return INITIAL_SHARE_VALUE; }
    total_assets / total_shares
}

// Shares to mint on deposit
fn calculate_shares_to_mint(deposit_amount: i128, share_value: i128) -> i128 {
    deposit_amount / share_value
}

// Assets to return on withdrawal
fn calculate_assets_to_return(shares: i128, share_value: i128) -> i128 {
    shares * share_value
}
```

**Yield Distribution:**
```rust
fn distribute_yield(env: &Env) -> Result<(), Error> {
    let total_assets = get_total_vault_assets(env);
    let initial_deposits = get_initial_deposits(env);
    let yield_earned = total_assets - initial_deposits;

    if yield_earned <= 0 { return Ok(()); }

    // Split: 75% stays in vault, 15% to agent, 10% to platform
    let agent_fee = (yield_earned * 15) / 100;
    let platform_fee = (yield_earned * 10) / 100;

    transfer_to_agent(env, agent_fee)?;
    transfer_to_platform(env, platform_fee)?;

    Ok(())
}
```

### Hour 0.3 - 0.5: Deploy & Test on Testnet

**Commands:**
```bash
cd contracts/vault

# Build the contract
stellar contract build

# Deploy to testnet
stellar contract deploy \
  --wasm target/wasm32-unknown-unknown/release/tuxedo_vault.wasm \
  --source AGENT_SECRET_KEY \
  --network testnet

# Outputs: CONTRACT_ID

# Initialize the vault
stellar contract invoke \
  --id $CONTRACT_ID \
  --source ADMIN_SECRET \
  --network testnet \
  -- initialize \
  --admin $ADMIN_ADDRESS \
  --agent $AGENT_ADDRESS \
  --platform $PLATFORM_ADDRESS \
  --share_token $SHARE_TOKEN_ADDRESS
```

**Test Deposit/Withdraw:**
```bash
# Deposit 100 USDC
stellar contract invoke \
  --id $CONTRACT_ID \
  --source USER_SECRET \
  --network testnet \
  -- deposit \
  --user $USER_ADDRESS \
  --asset $USDC_ADDRESS \
  --amount 1000000000 # 100 USDC (7 decimals)

# Check share balance
stellar contract invoke \
  --id $CONTRACT_ID \
  --network testnet \
  -- get_share_value

# Withdraw shares
stellar contract invoke \
  --id $CONTRACT_ID \
  --source USER_SECRET \
  --network testnet \
  -- withdraw \
  --user $USER_ADDRESS \
  --shares 1000000000
```

### Hour 0.5 - 0.8: Backend Integration (Python)

**File:** `backend/vault_manager.py`

```python
from stellar_sdk import SorobanServer, Keypair, TransactionBuilder, Network
from stellar_sdk.soroban_rpc import GetTransactionStatus

class VaultManager:
    def __init__(self, contract_id: str, agent_keypair: Keypair):
        self.contract_id = contract_id
        self.agent = agent_keypair
        self.server = SorobanServer(RPC_URL)

    async def deposit_to_vault(
        self,
        user_address: str,
        asset_address: str,
        amount: int
    ) -> dict:
        """User deposits assets, receives vault shares"""
        # Build transaction calling vault.deposit()
        tx = (TransactionBuilder(...)
              .append_invoke_contract_function_op(
                  contract_id=self.contract_id,
                  function_name="deposit",
                  parameters=[user_address, asset_address, amount]
              )
              .build())

        # User signs and submits
        return await self._submit_transaction(tx)

    async def agent_execute_strategy(
        self,
        strategy: str,
        params: dict
    ) -> dict:
        """Agent executes yield strategy (Blend supply)"""
        # Build transaction calling vault.agent_execute()
        tx = (TransactionBuilder(...)
              .append_invoke_contract_function_op(
                  contract_id=self.contract_id,
                  function_name="agent_execute",
                  parameters=[strategy, params]
              )
              .build())

        # Agent signs with its keypair
        tx.sign(self.agent)
        return await self._submit_transaction(tx)

    async def get_vault_stats(self) -> dict:
        """Get current vault TVL, share value, APY"""
        share_value = await self._call_contract("get_share_value")
        total_assets = await self._call_contract("get_total_assets")
        total_shares = await self._call_contract("get_total_shares")

        return {
            "tvl": total_assets,
            "share_value": share_value,
            "total_shares": total_shares,
            "apy": self._calculate_apy()
        }
```

**File:** `backend/vault_tools.py` (LangChain tools)

```python
from langchain_core.tools import tool

@tool
def deposit_to_vault(amount: float, asset: str = "USDC") -> str:
    """
    Deposit assets to the Tuxedo vault and receive vault shares.

    Args:
        amount: Amount to deposit (e.g., 100.0)
        asset: Asset to deposit (default: USDC)

    Returns:
        Number of vault shares minted
    """
    vault = VaultManager(CONTRACT_ID, AGENT_KEYPAIR)
    result = await vault.deposit_to_vault(
        user_address=get_user_address(),
        asset_address=ASSET_ADDRESSES[asset],
        amount=int(amount * 10**7)
    )
    return f"Deposited {amount} {asset}. Received {result['shares']} TUX-CORE shares."

@tool
def withdraw_from_vault(shares: float) -> str:
    """
    Withdraw assets from vault by burning vault shares.

    Args:
        shares: Number of vault shares to burn

    Returns:
        Amount of assets withdrawn
    """
    vault = VaultManager(CONTRACT_ID, AGENT_KEYPAIR)
    result = await vault.withdraw_from_vault(
        user_address=get_user_address(),
        shares=int(shares * 10**7)
    )
    return f"Withdrew {result['amount']} USDC. Burned {shares} TUX-CORE shares."

@tool
def get_vault_performance() -> str:
    """
    Get current vault performance metrics.

    Returns:
        TVL, share value, APY
    """
    vault = VaultManager(CONTRACT_ID, AGENT_KEYPAIR)
    stats = await vault.get_vault_stats()
    return f"""
    TUX-CORE Vault Performance:
    - TVL: ${stats['tvl']:,.2f}
    - Share Value: ${stats['share_value']:.4f}
    - Current APY: {stats['apy']:.2f}%
    """
```

### Hour 0.8 - 1.2: Frontend UI (React/TypeScript)

**File:** `src/components/vault/VaultDashboard.tsx`

```typescript
import { useState } from 'react';
import { Card, Button, Input } from '@stellar/design-system';
import { useVaultStats } from '@/hooks/useVaultStats';

export function VaultDashboard() {
  const { tvl, shareValue, apy, userShares } = useVaultStats();
  const [depositAmount, setDepositAmount] = useState('');

  const handleDeposit = async () => {
    const response = await fetch('/api/vault/deposit', {
      method: 'POST',
      body: JSON.stringify({ amount: depositAmount, asset: 'USDC' })
    });
    // Handle response
  };

  return (
    <div className="vault-dashboard">
      <Card>
        <h2>TUX-CORE Vault</h2>
        <div className="vault-stats">
          <Stat label="TVL" value={`$${tvl.toLocaleString()}`} />
          <Stat label="Share Value" value={`$${shareValue.toFixed(4)}`} />
          <Stat label="Current APY" value={`${apy.toFixed(2)}%`} />
        </div>

        <div className="vault-actions">
          <Input
            label="Deposit Amount (USDC)"
            value={depositAmount}
            onChange={(e) => setDepositAmount(e.target.value)}
          />
          <Button onClick={handleDeposit}>
            Deposit to Vault
          </Button>
        </div>

        <div className="user-position">
          <h3>Your Position</h3>
          <p>Vault Shares: {userShares.toLocaleString()} TUX-CORE</p>
          <p>Value: ${(userShares * shareValue).toFixed(2)}</p>
          <Button variant="secondary" onClick={handleWithdraw}>
            Withdraw
          </Button>
        </div>
      </Card>
    </div>
  );
}
```

**File:** `src/hooks/useVaultStats.ts`

```typescript
import { useQuery } from '@tanstack/react-query';

export function useVaultStats() {
  return useQuery({
    queryKey: ['vaultStats'],
    queryFn: async () => {
      const response = await fetch('/api/vault/stats');
      return response.json();
    },
    refetchInterval: 30_000, // Update every 30s
  });
}
```

### Hour 1.2 - 1.6: Integration Testing & Bug Fixes

**Test Scenarios:**

1. **Basic Deposit/Withdraw Flow:**
   ```bash
   # User deposits 100 USDC
   curl -X POST localhost:8000/vault/deposit \
     -d '{"amount": 100, "asset": "USDC"}'

   # Check vault shares minted
   curl localhost:8000/vault/user/shares

   # Withdraw 50 shares
   curl -X POST localhost:8000/vault/withdraw \
     -d '{"shares": 50}'
   ```

2. **Agent Strategy Execution:**
   ```bash
   # Agent supplies 50 USDC to Blend Comet pool
   curl -X POST localhost:8000/vault/agent/execute \
     -d '{
       "strategy": "blend_supply",
       "pool": "comet",
       "asset": "USDC",
       "amount": 50
     }'

   # Check vault TVL increased
   curl localhost:8000/vault/stats
   ```

3. **Yield Distribution:**
   ```bash
   # Simulate 10 USDC yield earned
   # Call distribute_yield()
   curl -X POST localhost:8000/vault/distribute_yield

   # Verify:
   # - Agent received 1.5 USDC (15%)
   # - Platform received 1.0 USDC (10%)
   # - Vault retained 7.5 USDC (75%)
   ```

4. **Multi-User Isolation:**
   ```bash
   # User A deposits 100 USDC
   # User B deposits 200 USDC
   # Verify share values calculated correctly
   # Verify withdrawals proportional to shares
   ```

**Common Bugs to Watch For:**
- Share value calculation when total_shares = 0
- Rounding errors in yield distribution
- Agent authorization checks
- Asset address validation
- Transaction failures (insufficient balance, etc.)

---

## 🎯 Success Criteria

**MVP Complete When:**
- ✅ User can deposit USDC, receive TUX-CORE shares
- ✅ User can withdraw USDC by burning shares
- ✅ Agent can execute Blend supply strategy
- ✅ Yield distribution works (75/15/10 split)
- ✅ Frontend displays vault stats in real-time
- ✅ All operations work on testnet

**Stretch Goals (if time permits):**
- 📊 Performance chart showing share value over time
- 🔔 Notifications when agent executes strategies
- 📈 APY calculation from historical data
- 🎨 Vault token visualization (shows agent activity)

---

## 🚦 Mainnet Deployment Checklist

**Before YOLO Mainnet:**
- [ ] Testnet testing complete (all scenarios pass)
- [ ] Smart contract code reviewed
- [ ] Agent keypair generated securely
- [ ] Platform fee address configured
- [ ] Initial USDC liquidity ready (~$1000 for testing)
- [ ] Frontend connected to mainnet endpoints
- [ ] Monitoring/alerting configured
- [ ] Emergency pause mechanism understood
- [ ] Bug bounty program announced

**Deployment Steps:**
```bash
# 1. Deploy contract to mainnet
stellar contract deploy \
  --wasm target/wasm32-unknown-unknown/release/tuxedo_vault.wasm \
  --source ADMIN_SECRET_KEY \
  --network mainnet

# 2. Initialize vault
stellar contract invoke \
  --id $MAINNET_CONTRACT_ID \
  --source ADMIN_SECRET \
  --network mainnet \
  -- initialize \
  --admin $ADMIN_ADDRESS \
  --agent $AGENT_ADDRESS \
  --platform $PLATFORM_ADDRESS \
  --share_token $SHARE_TOKEN_ADDRESS

# 3. Test with small amounts first
# Deposit 10 USDC, verify shares minted correctly

# 4. Monitor for 24 hours before announcing
# Watch for any unexpected behavior

# 5. Gradual rollout
# Announce to early testers, then wider community
```

---

## 🎉 Post-Launch: The Migration Plan

**Week 1-2: Dual System**
- Wallet import still works
- Vault available as "beta"
- Users can try both

**Week 3-4: Incentive Campaign**
- Bonus TUX tokens for vault deposits
- "Migrate your funds, earn 2x rewards"
- Educational content (blog, videos, demos)

**Week 5-6: Graceful Deprecation**
- Wallet import marked "legacy"
- Encourage migration with in-app prompts
- Support team helps users transition

**Week 7+: Vault-Only**
- Wallet import disabled for new users
- Existing users can still export keys
- Full focus on vault experience

---

## 📝 Open Questions (Resolve During Sprint)

1. **Share token symbol:** TUX-CORE or TUXCORE or tuxCORE?
2. **Initial share value:** 1.0 USDC or 0.01 USDC?
3. **Minimum deposit:** 1 USDC or 10 USDC or none?
4. **Agent strategy:** Just Blend or include Stellar DEX?
5. **Yield distribution timing:** Daily, weekly, or on-demand?

---

## 🎨 The Vibe

**Energy:** Move fast, ship working code, iterate based on feedback
**Philosophy:** Perfect is the enemy of good. MVP first, complexity later.
**Goal:** Prove the vault model works, then expand

**Remember:**
- Testnet first (but don't overthink it)
- User experience > Feature completeness
- On-chain transparency > Off-chain complexity
- Tradeable performance > Custody trust

---

## 🚀 Let's Build

**Ready to vault into action?**

The playful path awaits. Let's make agentic DeFi feel right.

---

**Timeline:** 1.6 hours (or until the vibe is right)
**Outcome:** Working MVP vault on testnet, ready for mainnet YOLO
**Next Steps:** Start with `contracts/vault/src/lib.rs`

🎩 **Tuxedo** | From wallet custody to vault sovereignty, one sprint at a time
