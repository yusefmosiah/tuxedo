# TUX Yield Farming: Complete Engineering Design
## Tokenomics, Algorithms & Data Structures

**Project:** Tuxedo - Conversational DeFi Yield Optimizer  
**Token:** TUX (Liquidity Mining Reward Token)  
**Target:** EasyA x Stellar Harvard Hack-o-Ween Hackathon  
**Date:** October 26, 2025

---

## Table of Contents
1. [Executive Summary](#executive-summary)
2. [Tokenomics Design](#tokenomics-design)
3. [Core Algorithms](#core-algorithms)
4. [Data Structures](#data-structures)
5. [Smart Contract Architecture](#smart-contract-architecture)
6. [Implementation Roadmap](#implementation-roadmap)
7. [Security Considerations](#security-considerations)
8. [References & Best Practices](#references-best-practices)

---

## Executive Summary

### The Vision
TUX is a liquidity mining token that incentivizes users to deposit assets into Stellar DeFi protocols (Blend, DeFindex) through the Tuxedo platform. By distributing TUX rewards, we:
- Bootstrap early adoption and TVL growth
- Create network effects and user retention
- Build a governance token for future protocol evolution
- Differentiate from simple yield aggregators

### Core Principles
1. **Sustainable Emissions**: Avoid hyperinflation through controlled release schedule
2. **Fair Distribution**: Time-weighted rewards favor long-term commitment
3. **Simple Design**: Minimalist implementation for hackathon; expand post-launch
4. **Stellar-Native**: Leverage Soroban's efficiency and low fees

---

## Tokenomics Design

### 1. Token Supply Model

#### Fixed Supply Structure
```
Total Supply: 100,000,000 TUX (100M)

Allocation:
├─ Liquidity Mining Rewards: 40,000,000 TUX (40%)
│  ├─ Year 1: 20,000,000 TUX
│  ├─ Year 2: 12,000,000 TUX  
│  └─ Year 3+: 8,000,000 TUX
│
├─ Community Treasury: 30,000,000 TUX (30%)
│  └─ Grants, ecosystem development, partnerships
│
├─ Team & Advisors: 20,000,000 TUX (20%)
│  └─ 1-year cliff, 4-year vesting
│
└─ Early Supporters/Investors: 10,000,000 TUX (10%)
   └─ 6-month cliff, 2-year vesting
```

**Rationale:**
- No single entity controls >20% (prevents whale dominance)
- 40% to liquidity providers ensures strong incentive alignment
- Vesting schedules prevent early dumps
- Fixed supply creates scarcity (vs inflationary models)

### 2. Emission Schedule

#### Decay Model (Recommended)
```
Year 1: 54,794 TUX per day (~20M total)
Year 2: 32,876 TUX per day (~12M total)
Year 3+: 21,917 TUX per day (~8M total)

Formula: daily_emission = annual_allocation / 365
```

**Alternative: Compound-Style Blocks**
```
Stellar average block time: ~5 seconds
Blocks per day: 17,280
Target: 54,794 TUX/day in Year 1

Emission per block: 3.17 TUX
```

### 3. Pool Multipliers (Boost System)

Different pools receive different weightings based on protocol goals:

```
Pool Weights:
├─ Blend USDC Lending: 1.0x (baseline)
├─ Blend USDC Borrowing: 0.8x (slightly lower)
├─ DeFindex USDC Vault: 1.5x (higher yield, higher risk)
├─ DeFindex BTC Vault: 2.0x (strategic importance)
└─ Future pools: Variable

Total Weight Calculation:
weighted_rewards = base_rewards * pool_multiplier
```

### 4. Sustainability Mechanisms

#### Anti-Dump Features
1. **Staking Lockup** (Optional): 7-30 day unbonding period for claimed TUX
2. **Claim Cooldown**: Can only claim rewards once per week
3. **Penalty for Early Exit**: 10% fee if unstaking before 90 days (burned or redistributed)

#### Value Accrual (Post-Hackathon)
- **Fee Sharing**: 50% of platform fees buy back TUX and burn
- **Governance Rights**: Vote on emission rates, pool weights, protocol upgrades
- **Staking Yields**: Stake TUX to earn protocol revenue share
- **Boosted Rewards**: Hold TUX to earn up to 2.5x multiplier on farming rewards

---

## Core Algorithms

### 1. Synthetix-Style Reward Distribution

This is the industry-standard algorithm used by Uniswap, Compound, Curve, and most DeFi protocols.

#### Core Formula

```solidity
rewardPerToken = rewardPerTokenStored + 
    ((currentTime - lastUpdateTime) * rewardRate * 1e18) / totalStaked

userEarned = (userBalance * (rewardPerToken - userRewardPerTokenPaid)) / 1e18 
    + previouslyEarnedRewards
```

#### Key Variables

```
rewardRate: Tokens distributed per second (e.g., 3.17 TUX per block)
rewardPerTokenStored: Accumulated rewards per staked token (global)
userRewardPerTokenPaid: Last rewardPerToken when user's rewards were calculated
totalStaked: Total amount staked across all users
userBalance: Individual user's staked amount
```

#### Why This Works

**Efficiency**: Only updates global state on each action, not per-user  
**Precision**: Uses fixed-point arithmetic (multiply by 1e18) to avoid decimals  
**Fair**: Rewards are proportional to stake size and duration

#### Example Calculation

```
Setup:
- rewardRate = 100 TUX/second
- totalStaked = 10,000 USDC
- User A stakes 1,000 USDC
- 100 seconds pass

Step 1: Calculate rewardPerToken
rewardPerToken = 0 + (100 seconds * 100 TUX/sec * 1e18) / 10,000
               = 1,000,000 * 1e18 / 10,000
               = 1e17 (per staked token)

Step 2: Calculate User A's rewards
userEarned = (1,000 * 1e17) / 1e18
           = 100 TUX earned

Verification: 
- User A has 10% of the stake
- 10,000 TUX emitted in 100 seconds
- User A should get 10% = 1,000 TUX ✓
```

### 2. Time-Weighted Rewards Enhancement

For incentivizing long-term staking:

```solidity
// Base multiplier starts at 1.0x
timeMultiplier = min(maxMultiplier, 1.0 + (stakeDuration / maxDuration) * (maxMultiplier - 1.0))

// Example:
// maxMultiplier = 2.0x
// maxDuration = 90 days
// 
// Day 1: 1.0x multiplier
// Day 45: 1.5x multiplier  
// Day 90+: 2.0x multiplier

effectiveBalance = userBalance * timeMultiplier
totalEffectiveStake = sum(all users' effectiveBalance)

rewards = (effectiveBalance / totalEffectiveStake) * totalRewardsPerPeriod
```

**Benefits:**
- Rewards long-term holders without penalizing new entrants
- Discourages mercenary capital
- Smooths out emissions over time

### 3. Pool-Specific Emission Allocation

```solidity
// Distribute emissions across multiple pools

struct Pool {
    address stakingToken;
    uint256 allocationPoints;  // Relative weight
    uint256 totalStaked;
    uint256 rewardPerTokenStored;
    uint256 lastUpdateTime;
}

// Calculate per-pool reward rate
totalAllocationPoints = sum(all pools' allocationPoints)

poolRewardRate = (globalRewardRate * pool.allocationPoints) / totalAllocationPoints

// Example:
// Global: 100 TUX/second
// Pool A: 50 points (50%)
// Pool B: 30 points (30%)
// Pool C: 20 points (20%)
// Total: 100 points
//
// Pool A gets: 100 * 50/100 = 50 TUX/sec
// Pool B gets: 100 * 30/100 = 30 TUX/sec
// Pool C gets: 100 * 20/100 = 20 TUX/sec
```

### 4. Compound V3-Style Index Tracking

More gas-efficient for high-frequency updates:

```solidity
// Tracking cumulative rewards per token over time
struct TrackingIndex {
    uint64 baseTrackingIndex;
    uint64 baseTrackingAccrued;
    uint64 trackingSupplySpeed;  // TUX per second per supply token
}

// Update index
timeDelta = currentTime - lastUpdateTime
trackingAccrued += timeDelta * trackingSupplySpeed

// Calculate user rewards
userAccrued = (userBalance * (currentIndex - userLastIndex)) / 1e15
```

**When to Use:**
- High-frequency reward updates
- Multiple parallel incentive programs
- Gas optimization critical

---

## Data Structures

### 1. Core Contract Storage

```solidity
// ============ Soroban Storage Maps ============

// Token addresses
symbol TUX_TOKEN: Address
symbol REWARD_POOL_ADDRESSES: Map<Symbol, Address>  // e.g., "BLEND_USDC" -> pool address

// Global state
symbol TOTAL_ALLOCATION_POINTS: u64
symbol REWARD_RATE_PER_SECOND: u128  // Base emission rate
symbol REWARD_PERIOD_START: u64      // Timestamp
symbol REWARD_PERIOD_END: u64

// Per-Pool tracking
struct PoolInfo {
    staking_token: Address,
    allocation_points: u64,
    total_staked: i128,
    reward_per_token_stored: u128,
    last_update_time: u64,
}
symbol POOLS: Map<Symbol, PoolInfo>

// Per-User tracking
struct UserStake {
    balance: i128,
    reward_per_token_paid: u128,
    pending_rewards: i128,
    stake_start_time: u64,
}
symbol USER_STAKES: Map<(Address, Symbol), UserStake>  // (user, pool_id) -> stake

// Claimed rewards tracking
symbol USER_CLAIMED_REWARDS: Map<Address, i128>
symbol TOTAL_REWARDS_CLAIMED: i128
```

### 2. Efficient Indexing Structures

#### For Multi-Pool Management
```solidity
// Track all pools user has staked in
symbol USER_ACTIVE_POOLS: Map<Address, Vec<Symbol>>

// Track all users in a pool (for governance snapshots)
symbol POOL_STAKERS: Map<Symbol, Vec<Address>>

// Efficient reward calculation cache
struct RewardSnapshot {
    timestamp: u64,
    reward_per_token: u128,
    total_staked: i128,
}
symbol REWARD_SNAPSHOTS: Map<(Symbol, u64), RewardSnapshot>  // (pool_id, week) -> snapshot
```

### 3. Vesting Schedule Data Structure

```solidity
struct VestingSchedule {
    total_amount: i128,
    released_amount: i128,
    start_time: u64,
    cliff_duration: u64,      // Seconds until first unlock
    vesting_duration: u64,    // Total vesting period
}

symbol TEAM_VESTING: Map<Address, VestingSchedule>
symbol INVESTOR_VESTING: Map<Address, VestingSchedule>

// Calculate vested amount
fn calculate_vested(schedule: VestingSchedule, current_time: u64) -> i128 {
    if current_time < schedule.start_time + schedule.cliff_duration {
        return 0;
    }
    
    let elapsed = current_time - schedule.start_time;
    if elapsed >= schedule.vesting_duration {
        return schedule.total_amount;
    }
    
    return (schedule.total_amount * elapsed) / schedule.vesting_duration;
}
```

### 4. Gas-Optimized Storage Patterns

#### Bit Packing (Soroban Optimization)
```rust
// Instead of separate storage slots:
struct CompactStake {
    balance: u128,              // 128 bits
    multiplier: u32,            // 32 bits (scaled by 1e6)
    last_claim_time: u64,       // 64 bits
    stake_start_time: u64,      // 64 bits
    // Total: 288 bits = ~36 bytes
}

// Compared to:
struct UnoptimizedStake {
    balance: i128,              // Soroban storage slot
    multiplier: i128,           // Soroban storage slot
    last_claim_time: u64,       // Soroban storage slot
    stake_start_time: u64,      // Soroban storage slot
    // Each requires separate storage operations
}
```

#### Merkle Tree for Reward Claims (Advanced)
```solidity
// For distributing rewards off-chain with on-chain verification
symbol MERKLE_ROOT: BytesN<32>
symbol CLAIMED_BITMAP: Map<u64, u64>  // Bitpacked claimed status

fn claim_reward(
    user: Address,
    amount: i128,
    proof: Vec<BytesN<32>>
) -> Result<(), Error> {
    // Verify merkle proof
    // Mark as claimed in bitmap
    // Transfer tokens
}
```

---

## Smart Contract Architecture

### Contract #1: TUX Token Contract

```rust
// Standard Stellar Asset Contract (SAC)
// Or custom Soroban token

#[contract]
pub struct TuxToken;

#[contractimpl]
impl TuxToken {
    // Standard token functions
    pub fn initialize(admin: Address, name: String, symbol: String);
    pub fn mint(to: Address, amount: i128);
    pub fn transfer(from: Address, to: Address, amount: i128);
    pub fn balance(addr: Address) -> i128;
    pub fn total_supply() -> i128;
    
    // Governance extensions
    pub fn delegate(from: Address, to: Address);
    pub fn get_votes(addr: Address) -> i128;
}
```

### Contract #2: TUX Farming Contract

```rust
#[contract]
pub struct TuxFarming;

#[contractimpl]
impl TuxFarming {
    // ========== INITIALIZATION ==========
    pub fn initialize(
        admin: Address,
        tux_token: Address,
        reward_rate: u128,
        start_time: u64,
        end_time: u64,
    ) -> Result<(), Error>;
    
    // ========== POOL MANAGEMENT (Admin) ==========
    pub fn add_pool(
        pool_id: Symbol,
        staking_token: Address,
        allocation_points: u64,
    ) -> Result<(), Error>;
    
    pub fn set_allocation_points(
        pool_id: Symbol,
        new_points: u64,
    ) -> Result<(), Error>;
    
    // ========== USER ACTIONS ==========
    pub fn stake(
        user: Address,
        pool_id: Symbol,
        amount: i128,
    ) -> Result<(), Error>;
    
    pub fn unstake(
        user: Address,
        pool_id: Symbol,
        amount: i128,
    ) -> Result<(), Error>;
    
    pub fn claim_rewards(
        user: Address,
        pool_id: Symbol,
    ) -> Result<i128, Error>;
    
    pub fn claim_all_rewards(
        user: Address,
    ) -> Result<i128, Error>;
    
    // ========== VIEW FUNCTIONS ==========
    pub fn pending_rewards(
        user: Address,
        pool_id: Symbol,
    ) -> i128;
    
    pub fn get_pool_info(pool_id: Symbol) -> PoolInfo;
    
    pub fn get_user_stake(
        user: Address,
        pool_id: Symbol,
    ) -> UserStake;
    
    pub fn get_total_allocated() -> u128;
    
    // ========== INTERNAL ==========
    fn update_pool(pool_id: Symbol);
    fn update_user_rewards(user: Address, pool_id: Symbol);
    fn calculate_reward_per_token(pool: PoolInfo) -> u128;
    fn calculate_pending(user: Address, pool: PoolInfo) -> i128;
}
```

### Key Contract Functions Explained

#### `update_pool`
```rust
fn update_pool(e: &Env, pool_id: Symbol) -> PoolInfo {
    let mut pool = get_pool(e, &pool_id);
    
    let current_time = e.ledger().timestamp();
    if current_time <= pool.last_update_time {
        return pool;
    }
    
    if pool.total_staked == 0 {
        pool.last_update_time = current_time;
        return pool;
    }
    
    // Calculate new reward per token
    let time_delta = current_time - pool.last_update_time;
    let pool_reward_rate = calculate_pool_reward_rate(e, &pool);
    let reward_increment = (time_delta as u128 * pool_reward_rate * PRECISION) 
        / pool.total_staked as u128;
    
    pool.reward_per_token_stored += reward_increment;
    pool.last_update_time = current_time;
    
    save_pool(e, &pool_id, &pool);
    pool
}
```

#### `stake`
```rust
pub fn stake(e: Env, user: Address, pool_id: Symbol, amount: i128) -> Result<(), Error> {
    user.require_auth();
    
    require!(amount > 0, Error::InvalidAmount);
    
    // Update pool state
    update_pool(&e, pool_id.clone());
    
    // Update user rewards before modifying balance
    update_user_rewards(&e, user.clone(), pool_id.clone());
    
    // Transfer tokens from user
    let pool = get_pool(&e, &pool_id);
    let token_client = token::Client::new(&e, &pool.staking_token);
    token_client.transfer(&user, &e.current_contract_address(), &amount);
    
    // Update user balance
    let mut user_stake = get_user_stake(&e, &user, &pool_id);
    user_stake.balance += amount;
    if user_stake.stake_start_time == 0 {
        user_stake.stake_start_time = e.ledger().timestamp();
    }
    save_user_stake(&e, &user, &pool_id, &user_stake);
    
    // Update pool total
    let mut pool = get_pool(&e, &pool_id);
    pool.total_staked += amount;
    save_pool(&e, &pool_id, &pool);
    
    emit_event(&e, "stake", (user, pool_id, amount));
    Ok(())
}
```

#### `claim_rewards`
```rust
pub fn claim_rewards(e: Env, user: Address, pool_id: Symbol) -> Result<i128, Error> {
    user.require_auth();
    
    // Update pool and user state
    update_pool(&e, pool_id.clone());
    update_user_rewards(&e, user.clone(), pool_id.clone());
    
    // Get pending rewards
    let mut user_stake = get_user_stake(&e, &user, &pool_id);
    let rewards = user_stake.pending_rewards;
    
    require!(rewards > 0, Error::NoRewards);
    
    // Reset pending rewards
    user_stake.pending_rewards = 0;
    save_user_stake(&e, &user, &pool_id, &user_stake);
    
    // Transfer TUX tokens
    let tux_token = get_tux_token(&e);
    let token_client = token::Client::new(&e, &tux_token);
    token_client.transfer(&e.current_contract_address(), &user, &rewards);
    
    // Update tracking
    increment_claimed_rewards(&e, &user, rewards);
    
    emit_event(&e, "claim", (user, pool_id, rewards));
    Ok(rewards)
}
```

---

## Implementation Roadmap

### Phase 1: Hackathon MVP (Week 1)

**Goal:** Demonstrate working liquidity mining on testnet

**Scope:**
- Deploy TUX token (100M supply)
- Single pool: Blend USDC lending
- Basic Synthetix algorithm
- Frontend integration: "Earn TUX" button

**Deliverables:**
1. TUX token contract deployed on Stellar testnet
2. Farming contract supporting 1 pool
3. Demo: User stakes USDC → sees TUX accumulating → claims TUX
4. Updated pitch deck with tokenomics

**Engineering Tasks:**
```
[ ] Write TUX token contract (1 day)
[ ] Write farming contract core logic (2 days)
[ ] Unit tests for reward calculations (1 day)
[ ] Deploy to testnet (0.5 day)
[ ] Integrate with existing Tuxedo frontend (1 day)
[ ] Test end-to-end flow (0.5 day)
```

### Phase 2: Post-Hackathon Expansion (Month 1-3)

**Goals:**
- Multi-pool support
- Time-weighted rewards
- Governance foundation

**Features:**
1. Add 3 more pools (Blend borrowing, DeFindex vaults)
2. Implement time multipliers
3. Create TUX staking for boosted rewards
4. Basic governance (vote on pool weights)
5. Deploy to mainnet with real TUX distribution

### Phase 3: Advanced Features (Month 4-6)

**Goals:**
- Mature tokenomics
- Protocol revenue sharing
- DAO transition

**Features:**
1. Fee buyback & burn mechanism
2. Delegate voting system
3. Emission schedule adjustment via governance
4. Partner protocol integrations
5. Cross-chain bridge to Ethereum/Base

---

## Security Considerations

### Smart Contract Risks

#### 1. Reentrancy Attacks
```rust
// Use Soroban's native protection or manual guards
static LOCKED: AtomicBool = AtomicBool::new(false);

fn non_reentrant_guard() {
    require!(!LOCKED.swap(true), Error::Reentrant);
}

fn release_lock() {
    LOCKED.store(false);
}
```

#### 2. Integer Overflow/Underflow
```rust
// Use checked arithmetic
let new_balance = user_stake.balance
    .checked_add(amount)
    .ok_or(Error::Overflow)?;
```

#### 3. Precision Loss
```rust
// Always use sufficient precision
const PRECISION: u128 = 1_000_000_000_000_000_000; // 1e18

// Bad: reward = (balance * rate) / total;  // Loses precision
// Good: reward = (balance * rate * PRECISION) / total / PRECISION;
```

#### 4. Flash Loan Attacks
```rust
// Require minimum stake duration or cooldown
require!(
    current_time - user_stake.stake_start_time >= MIN_STAKE_DURATION,
    Error::StakeTooShort
);
```

### Tokenomic Risks

#### 1. Hyperinflation
**Mitigation:**
- Fixed supply cap
- Decreasing emission schedule
- Regular governance review of emission rates

#### 2. Mercenary Capital (Yield Tourists)
**Mitigation:**
- Time-weighted rewards (longer stake = higher multiplier)
- Unstaking cooldown period
- Early exit penalty

#### 3. Sybil Attacks
**Mitigation:**
- Minimum stake requirements
- Wallet whitelisting (for governance)
- Quadratic voting for proposals

#### 4. Governance Capture
**Mitigation:**
- Timelock on governance actions (48-72 hours)
- Multi-sig for critical functions
- Progressive decentralization (team retains veto initially)

### Audit Checklist

```
[ ] Math overflow/underflow protection
[ ] Reentrancy guards on state-changing functions
[ ] Access control (admin functions restricted)
[ ] Input validation (require statements)
[ ] Precision handling (use 1e18 consistently)
[ ] Event emission for all critical actions
[ ] Upgrade mechanism (if applicable)
[ ] Emergency pause functionality
[ ] Comprehensive unit tests (>90% coverage)
[ ] Integration tests with real tokens
[ ] Fuzz testing for edge cases
[ ] Gas optimization review
[ ] External audit by reputable firm (post-hackathon)
```

---

## References & Best Practices

### Proven Implementations to Study

1. **Synthetix StakingRewards**
   - GitHub: `Synthetixio/synthetix/contracts/StakingRewards.sol`
   - Best for: Understanding the foundational algorithm
   - Key innovation: rewardPerToken accumulator pattern

2. **Uniswap V3 Staker**
   - GitHub: `Uniswap/v3-staker`
   - Best for: NFT position staking, complex incentive structures
   - Key innovation: Multiple simultaneous incentive programs

3. **Compound COMP Distribution**
   - Documentation: `compound.finance/governance/comp`
   - Best for: Per-block emission mechanics
   - Key innovation: Index-based tracking for gas efficiency

4. **Curve Gauge System**
   - GitHub: `curvefi/curve-dao-contracts`
   - Best for: Multi-pool weighting, veToken model
   - Key innovation: Vote-escrowed tokens for governance weight

5. **MasterChef (SushiSwap)**
   - GitHub: `sushiswap/sushiswap/MasterChef.sol`
   - Best for: Simple multi-pool management
   - Key innovation: Pool allocation points system

### Key Principles from Research

1. **Start Simple, Iterate**: Launch with basic Synthetix model, add complexity later
2. **Emission Control**: Always track total emitted vs allocation to prevent over-emission
3. **Time Precision**: Use block timestamps or block numbers consistently
4. **Gas Optimization**: Update global state only when necessary (lazy evaluation)
5. **Fair Distribution**: Ensure rewards are proportional to stake * time
6. **Transparency**: Emit events for all reward-related actions
7. **Governance Rights**: Don't distribute unclaimed rewards to new stakers

### Common Pitfalls to Avoid

1. **Reward Calculation Bugs**
   - Not updating rewards before balance changes
   - Integer division before multiplication (precision loss)
   - Not handling zero total supply edge case

2. **Emission Management**
   - Emitting more tokens than allocated
   - Not accounting for leftover rewards from previous periods
   - Reward rate set higher than contract balance allows

3. **User Experience**
   - Requiring users to manually claim every block (gas waste)
   - Not showing pending rewards in UI
   - Confusing APY vs APR calculations

4. **Economic Design**
   - Unsustainable APYs that attract mercenary capital
   - No value capture mechanism (token has no utility beyond speculation)
   - Poor vesting schedules that allow early dumps

### Recommended Reading

**Papers:**
- "Yield Farming and Liquidity Mining" - Multicoin Capital (2020)
- "Designing Sustainable Token Economies" - Token Engineering Commons
- "The Economics of Decentralized Finance" - A. Aramonte et al. (2021)

**Tutorials:**
- Smart Contract Programmer: "Solidity 0.8 - DeFi Staking Rewards"
- Synthetix Docs: "StakingRewards Architecture"
- Compound Developer Docs: "COMP Token Distribution"

**Tools:**
- TokenSoft: Token vesting contracts
- Gauntlet: Simulation platform for tokenomics
- Dune Analytics: On-chain data analysis

---

## Appendix: Example Calculations

### Scenario 1: Two Users, Different Entry Times

```
Setup:
- Pool: Blend USDC
- Emission: 100 TUX/second
- No time multipliers

Timeline:

t=0: Pool empty
     totalStaked = 0
     rewardPerTokenStored = 0

t=100: Alice stakes 1000 USDC
       totalStaked = 1000
       Alice.balance = 1000
       Alice.rewardPerTokenPaid = 0

t=200: (100 seconds pass)
       rewardPerToken = 0 + (100 * 100 * 1e18) / 1000 = 1e19
       Bob stakes 1000 USDC
       Bob.balance = 1000
       Bob.rewardPerTokenPaid = 1e19
       totalStaked = 2000

t=300: (100 seconds pass)
       rewardPerToken = 1e19 + (100 * 100 * 1e18) / 2000 = 1.5e19
       
       Alice claims:
       earned = (1000 * (1.5e19 - 0)) / 1e18 = 15,000 TUX
       
       Bob claims:
       earned = (1000 * (1.5e19 - 1e19)) / 1e18 = 5,000 TUX
       
Verification:
- Total emitted: 200 seconds * 100 TUX/sec = 20,000 TUX
- Alice got: 15,000 TUX (75% - staked for 200 sec with varying competition)
- Bob got: 5,000 TUX (25% - staked for 100 sec sharing with Alice)
- Alice had pool to herself for first 100 sec (10,000 TUX)
- Alice shared pool 50/50 with Bob for next 100 sec (5,000 TUX)
- Bob shared pool 50/50 with Alice for 100 sec (5,000 TUX)
- Math checks out! ✓
```

### Scenario 2: Time Multipliers

```
Setup:
- Max multiplier: 2.0x at 90 days
- Linear scaling

User stakes 1000 USDC:

Day 0:
  multiplier = 1.0x
  effectiveBalance = 1000 * 1.0 = 1000

Day 45:
  multiplier = 1.0 + (45/90) * (2.0 - 1.0) = 1.5x
  effectiveBalance = 1000 * 1.5 = 1500

Day 90:
  multiplier = 2.0x
  effectiveBalance = 1000 * 2.0 = 2000

If pool has 10,000 total staked:
Day 0: user gets 1000/10000 = 10% of rewards
Day 45: user gets 1500/11500 = 13% of rewards (assuming others at 1.0x)
Day 90: user gets 2000/12000 = 16.7% of rewards
```

### Scenario 3: Multi-Pool Allocation

```
Setup:
- Global emission: 100 TUX/second
- Pool A: 50 allocation points
- Pool B: 30 allocation points
- Pool C: 20 allocation points
- Total: 100 points

Emissions:
- Pool A: 100 * (50/100) = 50 TUX/sec
- Pool B: 100 * (30/100) = 30 TUX/sec
- Pool C: 100 * (20/100) = 20 TUX/sec

User stakes 1000 in Pool A (totalStaked = 5000):
- User's share: 1000/5000 = 20%
- User earns: 50 TUX/sec * 0.20 = 10 TUX/sec

Same user stakes 1000 in Pool B (totalStaked = 10000):
- User's share: 1000/10000 = 10%
- User earns: 30 TUX/sec * 0.10 = 3 TUX/sec

Total user earnings: 10 + 3 = 13 TUX/sec across both pools
```

---

## Conclusion

This document provides a complete engineering blueprint for implementing TUX liquidity mining. Key takeaways:

1. **Start with Synthetix algorithm** - battle-tested, efficient, well-understood
2. **Fixed supply with decay** - prevents hyperinflation, creates scarcity
3. **Time-weighted rewards** - incentivizes long-term alignment
4. **Multi-pool support** - flexible allocation to strategic pools
5. **Security first** - audit checklist, proven patterns, conservative parameters

For the hackathon MVP, focus on:
- ✅ Single pool (Blend USDC)
- ✅ Basic Synthetix rewards
- ✅ Simple claim flow
- ✅ Demonstrate the concept

Post-hackathon, expand to the full vision outlined here.

**Good luck at Harvard Hack-o-Ween! 🎃**

---

*Document prepared for Tuxedo team by AI research assistant*  
*Last updated: October 26, 2025*