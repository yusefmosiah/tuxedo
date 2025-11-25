# Multichain EVM Migration Plan: Stellar → Base + Multichain

**Status**: Planning Phase
**Created**: 2025-11-20
**Goal**: Transition from Stellar-only to multichain architecture, starting with Base (EVM)

---

## Executive Summary

Tuxedo is evolving from a Stellar-specific DeFi agent to a truly multichain platform. While keeping our proven passkey account system and non-custodial vault architecture, we're migrating to Base (Ethereum L2) as the primary chain, with plans for additional EVM chains.

### Key Decisions

- ✅ **Keep**: Passkey authentication, vault shares model, AI agent framework, non-custodial security
- 🔄 **Migrate**: Stellar → Base (EVM), Blend → Aave/Compound/Morpho, Soroban → Solidity
- 🆕 **Add**: Agent SDK integration (Claude or OpenHands), container isolation, multichain support

### Migration Approach

**Non-breaking**: We'll build the new system alongside the current one, allowing gradual transition without disrupting existing users.

---

## Current Architecture (Stellar-Based)

### Tech Stack

**Backend**:
- FastAPI + Python 3.11+
- LangChain for AI agent orchestration
- Stellar SDK 13.1.0+ (async support)
- Soroban for smart contracts
- SQLite database with passkey tables
- OpenAI-compatible LLM (via Redpill AI/OpenRouter)

**Smart Contracts** (Soroban/Rust):
- TUX0 Vault contract (627 lines, production-ready but undeployed)
- TUX token contract (SEP-41 compatible)
- Farming contract (yield distribution)

**Frontend**:
- React 19 + TypeScript 5.9
- Vite 7.1
- Stellar Wallets Kit (@creit.tech/stellar-wallets-kit)
- Stellar Design System
- TanStack React Query

**DeFi Integrations**:
- Blend Capital (Comet, Fixed, YieldBlox pools)
- Mainnet-only operations
- Real-time APY from on-chain data

**Account System**:
- WebAuthn passkey authentication ✅ Production-proven
- Multi-user isolation
- Session-based authorization
- Recovery codes + email recovery
- Per-user encrypted Stellar keys

### What Works Well ✅

1. **Passkey System**: Fully functional, production-tested, handles auth/sessions/recovery
2. **Vault Architecture**: Non-custodial shares model with dual-authority security
3. **AI Agent**: 19 tools, multi-step reasoning, context management
4. **User Isolation**: Each user has separate accounts, encrypted keys
5. **Frontend UX**: Chat interface, vault dashboard, pool visualization

### Current Limitations ❌

1. **Chain-locked**: Stellar-only, can't access EVM DeFi ecosystem
2. **Limited DeFi**: Only Blend Capital, missing major protocols (Aave, Morpho, etc.)
3. **Smart contract language**: Soroban/Rust vs industry-standard Solidity
4. **Wallet ecosystem**: Stellar wallets vs dominant MetaMask/WalletConnect
5. **No container isolation**: Agent tools run in main process (security risk)

---

## Target Architecture (Base/EVM + Multichain)

### Why Base?

1. **Low fees**: Ethereum L2 with ~$0.01 transaction costs
2. **EVM compatible**: Access to entire Ethereum DeFi ecosystem
3. **Fast**: ~2 second block times
4. **Coinbase backed**: Strong institutional support, easy onramps
5. **Growing ecosystem**: Aave, Compound, Morpho, Uniswap all deployed

### New Tech Stack

**Backend Core** (Unchanged):
- FastAPI + Python 3.11+
- SQLite database
- Passkey authentication (keep as-is)
- Agent orchestration framework

**Blockchain Integration** (New):
- **ethers.js** or **viem** (TypeScript/JavaScript)
- **web3.py** (Python) for backend
- Base (Ethereum L2) as primary chain
- RPC: Base mainnet (`https://mainnet.base.org`)
- **Account abstraction**: Smart contract wallets for users

**Smart Contracts** (Rewrite in Solidity):
- **CHIP Token**: ERC-20 contract for the fixed-supply CHIP token.
- **Deposit Vault**: A contract to manage user USDC deposits, handle unlocks (time or novelty-based), and serve as the lending pool.
- **Internal Lending Protocol**: Contracts that allow the Treasury to borrow from the Deposit Vault, using its CHIP holdings as collateral.
- **CHIP Redemption Contract**: Logic to allow users to redeem their CHIP for a proportional share of the Treasury's Net Asset Value (NAV).
- **Novelty Oracle**: An interface or contract that can receive off-chain novelty scores to trigger CHIP distribution.
- **Target**: Solidity 0.8.20+, OpenZeppelin libraries

**Frontend** (Updated):
- Replace Stellar Wallets Kit → **wagmi** + **viem** (Base/EVM)
- **RainbowKit** or **ConnectKit** for wallet connections
- Support MetaMask, Coinbase Wallet, WalletConnect
- **EVM-native**: Sign transactions with user wallets

**DeFi Integrations** (New):
- **Aave V3** on Base (lending/borrowing)
- **Compound V3** (if available on Base)
- **Morpho** (optimized lending)
- **Uniswap V3** (DEX/swaps)
- Future: Moonwell, Seamless Protocol

**Agent SDK** (New):
- **Option A**: Claude Agent SDK (filesystem-native, research-focused)
- **Option B**: OpenHands SDK (Docker containers, LiteLLM multi-model)
- **Container isolation**: Separate sandboxes per agent/user
- **Tool safety**: Read-only by default, write operations require approval

### Multichain Design Pattern

```
┌────────────────────────────────────────────────────┐
│              User Account (Passkey)                 │
│  - email + WebAuthn credentials                     │
│  - session tokens                                   │
│  - recovery codes                                   │
└─────────────────────┬──────────────────────────────┘
                      │
        ┌─────────────┼─────────────┐
        ▼             ▼             ▼
  ┌──────────┐  ┌──────────┐  ┌──────────┐
  │Base Agent│  │Arb Agent │  │OP Agent  │  (Future)
  │  (EVM)   │  │  (EVM)   │  │  (EVM)   │
  └──────────┘  └──────────┘  └──────────┘
        │             │             │
        ▼             ▼             ▼
  ┌──────────┐  ┌──────────┐  ┌──────────┐
  │Base Vault│  │Arb Vault │  │OP Vault  │
  │TUX0-BASE │  │TUX0-ARB  │  │TUX0-OP   │
  └──────────┘  └──────────┘  └──────────┘
        │             │             │
        ▼             ▼             ▼
  ┌──────────┐  ┌──────────┐  ┌──────────┐
  │Base DeFi │  │Arb DeFi  │  │OP DeFi   │
  │Aave/     │  │Aave/     │  │Aave/     │
  │Compound  │  │GMX       │  │Velodrome │
  └──────────┘  └──────────┘  └──────────┘
```

**Key principles**:
- One passkey account → Multiple chain agents
- Each chain has its own vault contract
- Cross-chain bridging (future): LayerZero or native bridges
- Unified UX: User sees "total portfolio" across chains

---

## What to Keep (90% of current system)

### 1. Passkey Authentication System ✅

**Files to keep as-is**:
- `backend/database_passkeys.py` - Database schema
- `backend/api/routes/passkey_auth.py` - Auth endpoints
- `backend/api/utils/passkey_helpers.py` - WebAuthn helpers
- `backend/services/passkey_service.py` - Business logic
- `backend/services/email.py` - SendGrid emails
- `src/services/passkeyAuth.ts` - Frontend service
- `src/contexts/AuthContext.tsx` - React context

**Why keep**: Production-tested, handles all auth concerns, chain-agnostic

### 2. Vault Architecture Concept ✅

**Keep the model**:
- Non-custodial shares (users deposit → receive vault tokens)
- Dual-authority security (agent strategies, user withdrawals)
- Fee distribution (platform fee + user rewards)
- Real-time share value calculation

**Rewrite implementation**: Migrate from Soroban → Solidity (ERC-4626 standard)

### 3. AI Agent Framework ✅

**Keep the approach**:
- LangChain orchestration
- Multi-step reasoning (up to 10 iterations)
- Tool-based architecture
- Context management + conversation history
- User isolation (separate accounts per user)

**Enhance with**: Agent SDK (Claude or OpenHands) for better isolation

### 4. Frontend Core ✅

**Keep components**:
- `ChatInterface.tsx` - AI chat UI
- `VaultDashboard.tsx` - Vault interface (update for EVM)
- Dashboard layouts
- Notification system
- Design patterns

**Update**: Wallet integration only (Stellar → EVM)

### 5. Database & Account Management ✅

**Keep**:
- User accounts table
- Passkey tables (credentials, challenges, sessions, recovery codes)
- Thread/conversation history
- Agent isolation logic

**Add**: New tables for EVM addresses, vault positions

---

## What to Change/Migrate

### 1. Smart Contracts: Soroban → Solidity

**Current** (Soroban/Rust):
```rust
// contracts/vault/src/lib.rs
pub fn deposit(env: Env, user: Address, amount: i128) -> i128 {
    // Mint TUX0 shares proportionally
}
```

**Target** (Solidity/ERC-4626):
```solidity
// contracts/TUX0Vault.sol
contract TUX0Vault is ERC4626, Ownable {
    function deposit(uint256 assets, address receiver)
        public override returns (uint256 shares) {
        // ERC-4626 standard vault
    }
}
```

**Migration tasks**:
- [  ] Rewrite vault contract as ERC-4626
- [ ] Rewrite TUX token as ERC-20
- [ ] Add yield distribution logic (2% platform, 98% users)
- [ ] Add agent authorization system
- [ ] Add emergency pause/unpause
- [ ] Test on Base Sepolia (testnet)
- [ ] Audit smart contracts before mainnet deployment

**Estimated effort**: 2-3 weeks

### 2. Blockchain SDK: Stellar SDK → ethers.js/web3.py

**Current** (Stellar):
```python
from stellar_sdk import Server, Keypair, TransactionBuilder

server = Server("https://horizon.stellar.org")
account = server.load_account(public_key)
```

**Target** (Base/EVM):
```python
from web3 import Web3

web3 = Web3(Web3.HTTPProvider("https://mainnet.base.org"))
account = web3.eth.account.from_key(private_key)
```

**Migration tasks**:
- [ ] Replace Stellar SDK with web3.py in backend
- [ ] Create EVM account manager (similar to current AccountManager)
- [ ] Update encryption for EVM private keys (same encryption.py)
- [ ] Replace stellar_tools.py → evm_tools.py
- [ ] Update transaction signing + gas estimation

**Estimated effort**: 1-2 weeks

### 3. DeFi Integrations: Blend → Aave/Morpho/Compound

**Current** (Blend Capital on Stellar):
```python
# blend_pool_tools.py
async def blend_supply_to_pool(pool_id, asset, amount):
    # Supply to Blend pool
```

**Target** (Aave V3 on Base):
```python
# aave_tools.py
async def aave_supply(asset, amount):
    # Supply to Aave V3 pool on Base
    aave_pool = web3.eth.contract(address=AAVE_POOL, abi=AAVE_ABI)
    tx = aave_pool.functions.supply(asset, amount, user, 0)
```

**New integrations needed**:
- [ ] Aave V3 integration (lending/borrowing)
- [ ] Morpho integration (optimized yields)
- [ ] Uniswap V3 (swaps + LP)
- [ ] Base-native protocols (Moonwell, Seamless)

**Migration tasks**:
- [ ] Create aave_tools.py (replace blend_pool_tools.py)
- [ ] Add morpho_tools.py
- [ ] Add uniswap_tools.py
- [ ] Update AI agent with new tool names
- [ ] Remove Blend-specific code

**Estimated effort**: 2-3 weeks

### 4. Frontend Wallet Integration: Stellar → EVM

**Current** (Stellar):
```typescript
import { StellarWalletsKit } from "@creit.tech/stellar-wallets-kit";

const kit = new StellarWalletsKit({ network: "PUBLIC" });
await kit.openModal({ onWalletSelected: async (wallet) => {...} });
```

**Target** (Base/EVM):
```typescript
import { createConfig, http } from 'wagmi';
import { base } from 'wagmi/chains';
import { ConnectKitProvider } from 'connectkit';

const config = createConfig({
  chains: [base],
  transports: { [base.id]: http() }
});

// Supports MetaMask, Coinbase Wallet, WalletConnect
```

**Migration tasks**:
- [ ] Remove Stellar Wallets Kit
- [ ] Add wagmi + viem for EVM wallet connections
- [ ] Add ConnectKit or RainbowKit for UI
- [ ] Update ChatInterface to use EVM wallet addresses
- [ ] Update VaultDashboard for ERC-4626 vaults
- [ ] Add network switcher (Base mainnet/testnet)

**Estimated effort**: 1 week

### 5. Agent Tools: Update All 19 Tools

**Current tools**:
- 6 Stellar tools (account, market, trading, trustlines, utilities, soroban)
- 6 Blend tools (pool discovery, APY, supply, withdraw, positions)
- 7 Vault tools (deposit, withdraw, performance, agent strategies)

**Target tools**:
- **6 EVM tools**: Account management, balance queries, token operations, gas estimation, transaction history, contract interactions
- **6 Aave tools**: Pool discovery, APY queries, supply/withdraw, borrow/repay, positions, health factor
- **7 Vault tools**: Same concepts, but ERC-4626 compliant

**Migration approach**: Parallel implementation
- Keep Stellar tools functional (for existing users)
- Add EVM tools alongside
- Agent selects tools based on chain context
- Eventually deprecate Stellar tools

**Estimated effort**: 2 weeks

---

## Agent SDK Integration

Based on prior research (`docs/AGENT_SDK_RESEARCH_AND_RECOMMENDATIONS.md`), we have two options:

### Option A: Claude Agent SDK (Recommended)

**Why**:
- ✅ Filesystem-native (perfect for research/knowledge management)
- ✅ Subagent parallelization (research, strategy, execution)
- ✅ Built for writing/research workflows (matches our use case)
- ✅ Simpler setup for Anthropic-compatible endpoints

**How to integrate**:
```typescript
// Orchestrator agent
const orchestrator = new Agent({
  apiKey: process.env.ANTHROPIC_API_KEY
});

// Research subagent (Kimi K2 for critical feedback)
const research = await orchestrator.createSubagent({
  name: 'ResearchAgent',
  apiKey: process.env.KIMI_API_KEY,
  baseURL: 'https://api.moonshot.ai/anthropic'
});

// Strategy subagent (Claude for reasoning)
const strategy = await orchestrator.createSubagent({
  name: 'StrategyAgent'
});

// Execution subagent (with EVM tools)
const execution = await orchestrator.createSubagent({
  name: 'ExecutionAgent',
  tools: [aave_tools, vault_tools, uniswap_tools]
});
```

**Container isolation**: Use Docker containers for each subagent

### Option B: OpenHands SDK (Alternative)

**Why**:
- ✅ LiteLLM integration (100+ model providers)
- ✅ Built-in Docker/Kubernetes support
- ✅ Better for code-heavy tasks

**Trade-off**: More complex setup, less ideal for research workflows

### Recommendation: Start with Claude SDK

**Rationale**:
1. Our workflow is research → strategy → execution (not code generation)
2. Simpler integration with existing FastAPI backend
3. Filesystem-based context matches our knowledge base approach
4. Can migrate to OpenHands later if needed

**Estimated effort**: 2-3 weeks (setup + testing)

---

## Migration Phases (Non-Breaking Approach)

### Phase 1: Research & Setup (Weeks 1-2)

**Goals**: Set up Base development environment, no production changes

- [ ] Set up Base testnet (Sepolia) environment
- [ ] Create test wallet + fund with testnet ETH
- [ ] Deploy simple "Hello World" Solidity contract to Base Sepolia
- [ ] Test ethers.js/web3.py connection to Base RPC
- [ ] Research Aave V3 on Base (contracts, ABIs, docs)
- [ ] Set up local development with Hardhat/Foundry

**Deliverable**: Working Base testnet environment

### Phase 2: Smart Contracts (Weeks 3-5)

**Goals**: Rewrite vault system in Solidity (ERC-4626)

- [ ] Write TUX0Vault.sol (ERC-4626 compliant)
- [ ] Write TUX.sol (ERC-20 token)
- [ ] Write YieldDistributor.sol (2% platform, 98% users)
- [ ] Add agent authorization (only authorized address can execute strategies)
- [ ] Write comprehensive tests (Foundry or Hardhat)
- [ ] Deploy to Base Sepolia testnet
- [ ] Integration testing with real testnet transactions

**Deliverable**: Production-ready smart contracts on Base testnet

### Phase 3: Backend EVM Integration (Weeks 6-8)

**Goals**: Add EVM support alongside existing Stellar

- [ ] Create `backend/chains/evm.py` (parallel to `stellar.py`)
- [ ] Create `backend/evm_tools.py` (account, balances, transactions)
- [ ] Create `backend/aave_tools.py` (Aave V3 integration)
- [ ] Create `backend/evm_vault_tools.py` (TUX0 vault operations)
- [ ] Update `backend/account_manager.py` to support EVM accounts
- [ ] Add database tables: `evm_accounts`, `vault_positions_evm`
- [ ] Test agent with EVM tools (parallel to Stellar)

**Deliverable**: Backend supports both Stellar and Base

### Phase 4: Agent SDK Integration (Weeks 9-11)

**Goals**: Add Claude Agent SDK for better isolation

- [ ] Install Claude Agent SDK (TypeScript or Python)
- [ ] Create orchestrator agent pattern
- [ ] Create subagents: Research, Strategy, Execution
- [ ] Add filesystem-based context management (`.claude/` directories)
- [ ] Integrate with existing LangChain tools
- [ ] Add Docker containers for agent isolation
- [ ] Test multi-subagent workflows

**Deliverable**: Agent SDK running alongside current system

### Phase 5: Frontend EVM Support (Weeks 12-13)

**Goals**: Add EVM wallet connections + Base vault UI

- [ ] Install wagmi + viem
- [ ] Add ConnectKit for wallet UI
- [ ] Create `useEVMWallet` hook (parallel to `useWallet`)
- [ ] Update VaultDashboard to support ERC-4626 vaults
- [ ] Add network switcher (Stellar vs Base)
- [ ] Add "Migrate to Base" flow for existing users
- [ ] Test MetaMask, Coinbase Wallet, WalletConnect

**Deliverable**: Frontend supports both Stellar and Base

### Phase 6: Testnet Beta (Weeks 14-15)

**Goals**: Beta test with real users on Base testnet

- [ ] Deploy frontend to staging environment
- [ ] Invite 10-20 beta testers
- [ ] Provide testnet ETH for gas
- [ ] Collect feedback on UX, wallet integration, agent performance
- [ ] Monitor for bugs, errors, edge cases
- [ ] Iterate based on feedback

**Deliverable**: Production-ready Base integration (testnet-tested)

### Phase 7: Mainnet Launch (Weeks 16-18)

**Goals**: Deploy to Base mainnet, gradual migration

- [ ] Audit smart contracts (professional audit recommended)
- [ ] Deploy TUX0Vault + TUX token to Base mainnet
- [ ] Configure mainnet RPC endpoints
- [ ] Add "Migrate from Stellar" wizard in UI
- [ ] Offer migration incentives (TUX token bonuses for early movers)
- [ ] Monitor closely for issues
- [ ] Gradual deprecation of Stellar features (announce 3-6 month timeline)

**Deliverable**: Tuxedo running on Base mainnet

### Phase 8: Multichain Expansion (Future)

**Goals**: Add more EVM chains

- [ ] Arbitrum support (L2, low fees, strong DeFi)
- [ ] Optimism support (L2, Superchain)
- [ ] Polygon zkEVM (low fees, zkRollup)
- [ ] Cross-chain bridging (LayerZero or native bridges)

**Deliverable**: True multichain platform

---

## Technical Decisions

### Account Management: Smart Contract Wallets vs EOAs

**Option A: Externally Owned Accounts (EOAs)** - Traditional private key wallets
- ✅ Simple, compatible with all wallets
- ✅ Lower gas costs
- ❌ No account recovery if key lost
- ❌ No batching, no gas abstraction

**Option B: Smart Contract Wallets** - ERC-4337 Account Abstraction
- ✅ Account recovery (social recovery, passkey recovery)
- ✅ Gas abstraction (pay fees in USDC not ETH)
- ✅ Transaction batching (approve + deposit in one tx)
- ❌ Higher gas costs
- ❌ More complex implementation

**Recommendation**: Start with EOAs (Phase 1-7), migrate to AA wallets (Phase 8+)

**Rationale**: EOAs are simpler to implement and test. Once Base integration is stable, add AA wallets as an optional upgrade for users who want recovery/abstraction features.

### Passkey + EVM Integration

**Current**: Passkeys used only for authentication (session tokens)

**Future option**: Passkeys as EVM signers
- Use WebAuthn signatures to sign EVM transactions
- No separate private key storage needed
- **Challenge**: Browser support for secp256k1 signatures

**Recommendation**: Keep passkeys for auth only (current approach), use standard EVM private keys for blockchain operations.

**Why**: Simpler, more compatible, follows proven patterns. Passkey-as-signer is experimental and has limited browser support.

### Database Schema Changes

**New tables needed**:

```sql
-- EVM accounts (parallel to Stellar accounts)
CREATE TABLE evm_accounts (
    id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL,
    address TEXT NOT NULL,  -- 0x...
    private_key_encrypted TEXT NOT NULL,
    chain_id INTEGER NOT NULL,  -- 8453 for Base mainnet
    label TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
);

-- Vault positions on EVM chains
CREATE TABLE vault_positions_evm (
    id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL,
    vault_address TEXT NOT NULL,  -- TUX0Vault contract address
    chain_id INTEGER NOT NULL,
    shares_balance TEXT NOT NULL,  -- BigInt as string
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
);

-- DeFi positions (Aave, etc.)
CREATE TABLE defi_positions_evm (
    id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL,
    protocol TEXT NOT NULL,  -- 'aave', 'compound', 'morpho'
    asset_address TEXT NOT NULL,
    amount TEXT NOT NULL,  -- BigInt as string
    position_type TEXT NOT NULL,  -- 'supply', 'borrow'
    chain_id INTEGER NOT NULL,
    apy REAL,
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
);
```

**Migration**: Keep existing Stellar tables, add EVM tables in parallel.

---

## Risk Mitigation

### Technical Risks

**Risk 1**: Smart contract bugs → Loss of user funds
- **Mitigation**: Professional audit before mainnet deployment
- **Mitigation**: Start with small TVL limits ($10k max initially)
- **Mitigation**: Bug bounty program (CHIP token rewards)

**Risk 2**: Gas price spikes → Expensive operations
- **Mitigation**: Use Base (L2) for low fees (~$0.01 vs $1-50 on Ethereum mainnet)
- **Mitigation**: Batch transactions where possible
- **Mitigation**: Monitor gas prices, pause operations if too high

**Risk 3**: Agent SDK integration bugs → Lost transactions
- **Mitigation**: Extensive testing in isolated containers
- **Mitigation**: Read-only mode first, require manual approval for writes
- **Mitigation**: Transaction simulation before execution

**Risk 4**: User migration issues → Confusion, lost funds
- **Mitigation**: Clear migration wizard with step-by-step instructions
- **Mitigation**: Keep Stellar system running in parallel (6-12 months)
- **Mitigation**: Migration incentives (CHIP bonuses for early movers)

### Business Risks

**Risk 1**: Stellar users don't migrate → Fragmented user base
- **Mitigation**: Strong incentives (lower fees on Base, higher APYs, TUX bonuses)
- **Mitigation**: Clear communication about Base benefits
- **Mitigation**: Gradual deprecation (6-12 month transition period)

**Risk 2**: EVM competition → Hard to differentiate
- **Mitigation**: Focus on the unique "marketplace of ideas" economic model.
- **Mitigation**: Best-in-class UX with passkey auth and principal protection.
- **Mitigation**: The Harmonic Intelligence flywheel is a defensible moat.

**Risk 3**: Base chain issues → Network downtime or bugs
- **Mitigation**: Multi-chain from day 1 (plan for Arbitrum, Optimism fallbacks)
- **Mitigation**: Monitor Base network status, pause operations if issues
- **Mitigation**: Emergency withdrawal mechanisms in smart contracts

---

## Success Metrics

### Phase 1-3 (Months 1-3):
- [ ] Smart contracts deployed to Base testnet
- [ ] 100 test transactions executed successfully
- [ ] Agent can perform Aave supply/withdraw operations
- [ ] No critical bugs in testnet testing

### Phase 4-6 (Months 4-5):
- [ ] 50 beta users testing on Base testnet
- [ ] 500+ testnet transactions across all protocols
- [ ] Agent SDK running isolated workflows
- [ ] Frontend supports both Stellar + Base wallets

### Phase 7 (Month 6):
- [ ] Smart contracts audited with 0 critical findings
- [ ] $10k TVL in mainnet vault (initial cap)
- [ ] 10 users migrated from Stellar to Base
- [ ] 0 incidents or fund losses

### Phase 8+ (Months 7-12):
- [ ] $100k+ TVL across Base vaults
- [ ] 100+ active users on Base
- [ ] 80%+ of Stellar users migrated to Base
- [ ] Arbitrum/Optimism chains added
- [ ] Cross-chain vaults operational

---

## Next Immediate Steps

### Week 1 Tasks (Get started)

1. **Set up Base development environment**
   ```bash
   # Install Hardhat or Foundry
   npm install --save-dev hardhat
   # OR
   curl -L https://foundry.paradigm.xyz | bash
   foundryup

   # Get Base testnet RPC
   # https://base.org/docs - use Alchemy, Infura, or public RPC
   ```

2. **Create minimal ERC-4626 vault**
   ```bash
   cd contracts
   mkdir base
   # Create TUX0Vault.sol, TUX.sol
   # Use OpenZeppelin ERC4626 as starting point
   ```

3. **Research Aave V3 on Base**
   - [ ] Find Aave V3 Pool contract address on Base
   - [ ] Download ABIs from Aave docs
   - [ ] Review Aave V3 supply/withdraw flow
   - [ ] Test Aave interaction on Base testnet

4. **Update project documentation**
   - [ ] Add Base RPC URLs to CLAUDE.md
   - [ ] Document EVM environment variables
   - [ ] Create migration timeline doc for users

### Decision Points

**Before Phase 2** (Smart Contracts):
- [ ] Confirm ERC-4626 vs custom vault standard
- [ ] Confirm OpenZeppelin vs custom implementation
- [ ] Confirm audit provider (OpenZeppelin, Trail of Bits, etc.)

**Before Phase 4** (Agent SDK):
- [ ] Final decision: Claude Agent SDK vs OpenHands SDK
- [ ] Confirm container isolation approach (Docker vs K8s vs local)
- [ ] Confirm model endpoints (Bedrock, Kimi K2, etc.)

**Before Phase 7** (Mainnet):
- [ ] Complete smart contract audit
- [ ] Confirm TVL limits for initial launch
- [ ] Confirm insurance/security fund for potential bugs

---

## Open Questions

1. **Should we support Stellar long-term, or fully deprecate?**
   - Option A: Full migration, sunset Stellar in 12 months
   - Option B: Keep both chains indefinitely (multichain native)
   - **Recommendation**: Option A (focus on EVM ecosystem)

2. **Which agent SDK: Claude or OpenHands?**
   - Both viable, Claude better for research workflows
   - OpenHands better if we add code generation features later
   - **Recommendation**: Start with Claude, evaluate OpenHands later

3. **Account Abstraction: Now or later?**
   - AA wallets provide better UX (gas abstraction, recovery)
   - But add complexity and gas costs
   - **Recommendation**: Start with EOAs, add AA as optional upgrade (Phase 8+)

4. **Cross-chain bridges: Which one?**
   - LayerZero (most popular)
   - Wormhole (multi-chain)
   - Native bridges (Base ↔ Ethereum)
   - **Recommendation**: Defer until Phase 8, use native bridges first

5. **APY typo location?**
   - User mentioned 50% APY typo in whitepaper/docs
   - Couldn't find it in search
   - **Action**: Need user to clarify specific location

---

## Summary & Timeline

**Total Estimated Time**: 4-6 months (18 weeks)

**Phases**:
1. **Months 1-2**: Research, setup, smart contracts (Base testnet)
2. **Months 3-4**: Backend integration, Agent SDK, parallel Stellar/Base support
3. **Month 5**: Frontend EVM support, beta testing
4. **Month 6**: Mainnet launch, user migration
5. **Months 7-12**: Multichain expansion (Arbitrum, Optimism, etc.)

**Non-Breaking Approach**: Keep Stellar system running throughout migration, gradual user transition with incentives.

**Key Decisions**:
- Base as primary EVM chain ✅
- ERC-4626 vaults ✅
- Claude Agent SDK (tentative) ✅
- EOAs first, AA wallets later ✅

**Next Actions**:
1. Fix APY typo (need user clarification on location)
2. Set up Base testnet environment (Week 1)
3. Begin ERC-4626 vault contract (Week 3)
4. Research Aave V3 integration (Week 1-2)

---

**Document Status**: Draft for review
**Feedback needed**:
- Confirm Base as primary chain
- Confirm timeline (too aggressive? too conservative?)
- Confirm agent SDK choice (Claude vs OpenHands)
- **Clarify APY typo location**
