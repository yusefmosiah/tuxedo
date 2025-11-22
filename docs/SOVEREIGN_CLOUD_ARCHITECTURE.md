# Sovereign Cloud Architecture

**The Filesystem: Your Personal Banking Agent**

---

## Executive Summary

Choir (formerly Tuxedo) is **not a DApp** or **not a wallet**. It is a **Sovereign Cloud** — a secure, private computer running in a Trusted Execution Environment (TEE) that manages your financial assets across multiple blockchains.

**The Core Metaphor**: You log into a computer (your TEE filesystem) that holds:
- `keys.json` - Keys for EVM, Stellar, Solana, Bitcoin, Zcash
- `context.db` - Your preferences, risk tolerance, chat history
- `agent_logic.py` - The AI brain that orchestrates your assets

**Status**: Production financial platform launching Q4 2025

---

## 1. Core Architectural Shift: The Filesystem

### Stop Saying "DApp" or "Wallet"

**Old framing** (incorrect):
- "Connect your wallet to our DApp"
- "Tuxedo is a Stellar yield optimizer"
- "Link your MetaMask"

**New framing** (correct):
- "Log into your Sovereign Cloud computer"
- "Choir is a Personal Banking Agent running in a TEE"
- "Authenticate with biometrics to access your private filesystem"

### The Trusted Execution Environment (TEE)

```
┌─────────────────────────────────────────────────┐
│          Your Sovereign Cloud Computer          │
│         Running on Phala Network (TEE)          │
├─────────────────────────────────────────────────┤
│                                                  │
│  Filesystem:                                     │
│  ├── keys.json                                   │
│  │   ├── EVM: 0x742d...                         │
│  │   ├── Stellar: GABC...                       │
│  │   ├── Solana: 9vHf...                        │
│  │   ├── Bitcoin: bc1q...                       │
│  │   └── Zcash: t1Xg...                         │
│  │                                               │
│  ├── context.db                                  │
│  │   ├── Risk tolerance: Conservative           │
│  │   ├── Target APY: 10-15%                     │
│  │   ├── Chat history                           │
│  │   └── Strategy preferences                   │
│  │                                               │
│  └── agent_logic.py                              │
│      ├── Yield optimization engine               │
│      ├── Cross-chain router                     │
│      ├── Risk manager                           │
│      └── Research report generator              │
│                                                  │
└─────────────────────────────────────────────────┘
```

**Key Point**: The user *authenticates into the computer*, and the computer *manages the wallets*. No "wallet connect" flows. No third-party dependencies.

---

## 2. Infrastructure: Radical Chain Agnosticism

### Blockchains are Commodity Infrastructure

**The Narrative**: "We abstract the nerd details." The user sees "Yield" and "Assets," not "Chains" and "Gas."

```
┌──────────────────────────────────────────────────────────┐
│            The Sovereign Cloud Stack                      │
├──────────────────────────────────────────────────────────┤
│                                                           │
│  Compute Layer (The Brain):                              │
│  └── Phala Network TEE                                   │
│      - Hardware-isolated execution                       │
│      - Encrypted filesystem                              │
│      - Provable security via attestation                 │
│                                                           │
│  Capital Destinations (The Pipes):                       │
│  ├── EVM Chains (Primary)                                │
│  │   ├── Base (Ethereum L2) - Low fees, fast            │
│  │   ├── Ethereum Mainnet - Deep liquidity               │
│  │   ├── Arbitrum - L2 with strong DeFi                 │
│  │   └── Optimism - L2 Superchain                       │
│  │                                                       │
│  ├── Stellar - Cheap USDC transport, RWA anchors        │
│  ├── Solana/SVM - High-frequency opportunities           │
│  ├── Bitcoin - Pristine collateral                      │
│  └── Zcash - Privacy layer                              │
│                                                           │
│  DeFi Protocols (Where Capital Works):                  │
│  ├── EVM: Aave, Morpho, Compound, Uniswap               │
│  ├── Stellar: Blend Capital                             │
│  ├── Solana: Kamino, Drift                              │
│  └── Cross-chain: Symbiotic, EigenLayer                 │
│                                                           │
└──────────────────────────────────────────────────────────┘
```

### The Agent as "Cross-Chain CFO"

The AI agent moves capital to wherever the **risk-adjusted yield is highest**, handling:
- Bridge routing (LayerZero, Wormhole, native bridges)
- Gas optimization (batch transactions, timing)
- Tax-aware rebalancing (minimize taxable events)
- Invisible swaps (user sees USDC → USDC, not USDC → ETH → wstETH → aWstETH)

**User experience**: "My agent earned 12.3% APY this quarter"
**Reality**: Agent executed 47 transactions across 3 chains and 5 protocols

---

## 3. Authentication: Direct Ownership

### No Wallet Connect. No Social Logins.

**Explicitly rejected**:
- ❌ MetaMask / WalletConnect (third-party dependency)
- ❌ Google / Coinbase OAuth (we own the relationship)
- ❌ Seed phrases (bad UX, user error)

**Implemented**:
- ✅ **Passkey / WebAuthn** (biometric vault)
- ✅ **Recovery codes** (8 single-use codes, rate-limited)
- ✅ **Email recovery** (SendGrid integration)

```
User Journey:
1. Visit choir.chat
2. Enter email: user@example.com
3. "Use Face ID to create your vault"
4. [TouchID prompt]
5. → Account created, TEE provisioned, keys generated
6. → Recovery codes displayed (save these!)
7. → Logged in
```

**Branding**: "Biometric Vault." "Bank-Grade Security." "Accessible Luxury."

**Rationale**: Rich people don't "Connect MetaMask." They scan their face to enter the vault.

---

## 4. Economics: Realism & The CHIP Bridge

### Purge the "50% APY" Hallucination

**Old model** (unrealistic):
- "Earn up to 50% APY!"
- Over-promise on yields
- Token emissions to subsidize returns

**New model** (realistic):
- **Base Yield**: 10-15% APY (blue-chip DeFi: Aave/Morpho on Base)
- **The Upside**: CHIP token bridges gap between "Safe Yield" and "Life-Changing Wealth"

```
Value Proposition:
"Your capital earns market-leading yield (10-15%).
Your intelligence earns CHIP (Network Equity)."

Example:
- Deploy: $10,000 USDC
- Base yield: 12% APY = $1,200/year
- CHIP rewards: 500 CHIP tokens/year
- If CHIP appreciates: 500 tokens × $10 = $5,000 upside
- Total return: $1,200 yield + $5,000 appreciation = 62% effective APY

BUT: The 62% comes from token appreciation (speculative),
     not from platform promising unsustainable yields.
```

### CHIP Token Economics

**CHIP is backed by the Treasury's productive output** (fundamental price floor):
- Treasury owns protocol-controlled liquidity
- Treasury deploys capital at 10-15% yields
- Treasury revenue flows to CHIP buyback/burn
- CHIP holders govern treasury allocation

**Distribution**:
- 40% - Yield mining rewards (capital deployers)
- 20% - Novelty rewards (early chat participants)
- 20% - Team + early contributors
- 20% - Treasury (DAO controlled)

---

## 5. Brand & Culture: The Anti-Feed

### Twitter is the Enemy

**What we are NOT**:
- ❌ "SocialFi" (engagement farming)
- ❌ "Decentralized Twitter" (Farcaster)
- ❌ Feed-based content (scroll addiction)
- ❌ Follower counts (vanity metrics)
- ❌ Viral posts (ephemeral noise)

**What we ARE**:
- ✅ **Knowledge Banking** (stock, not flow)
- ✅ **Citations** (measurable intellectual influence)
- ✅ **Reputation** (earned through quality)
- ✅ **Permanence** (content indexed for eternity)
- ✅ **Financial returns** (ideas earn money)

**Terminology Shift**:

| DELETE | INSERT |
|--------|--------|
| Post | Deposit |
| Feed | Vault |
| SocialFi | Knowledge Banking |
| Engagement | Citations |
| Followers | Reputation |

**The Vibe**: Accessible Luxury. Braun/Leica aesthetics. Quiet, high-status, permanent.

**The Thought Bank**: Content does NOT "scroll away." It is indexed into the vector database for eternity to be cited by agents. This is **Stock**, not **Flow**.

---

## 6. Regulatory & Privacy: The "Black Box" Defense

### TEE as Primary Defense

**Privacy Argument**:
- Since the agent runs in a TEE, even *we* (Choir team) cannot see:
  - User's private keys
  - Specific trade intents
  - Strategy parameters
  - Asset holdings
- This is **"Can't Be Evil"** architecture (not just "won't be evil")

**Regulatory Argument**:
- We provide the **Tool** (the Filesystem/TEE)
- The **User** directs the agent
- We are a **software provider**, not a custodial bank
- Stronger legal position than centralized platforms

**Phala Network Advantages**:
- Hardware-level isolation (Intel SGX / ARM TrustZone)
- Cryptographic attestation (provable security)
- Open-source stack (auditable)
- Decentralized compute (no single point of control)

---

## 7. Current Implementation Status

### What's Built (Q4 2025)

**Authentication** ✅
- Passkey/WebAuthn registration + login
- Recovery codes (8 per user, rate-limited)
- Email recovery (SendGrid integration)
- Multi-passkey support
- Session management (sliding expiration)

**Backend Infrastructure** ✅
- FastAPI + Python
- LangChain agent orchestration
- Claude SDK integration (research/analysis)
- Multi-step reasoning (up to 25 iterations)
- User isolation (separate accounts/contexts)

**Frontend** ✅
- React 19 + TypeScript + Vite
- Chat interface (conversational AI)
- Vault dashboard (deposit/withdraw)
- Real-time statistics hooks
- Responsive design

**Smart Contracts** ⚠️ (Built, not deployed)
- Vault contract (ERC-4626 or Soroban)
- TUX token (ERC-20 or SEP-41)
- Farming/distribution contracts

**Current Chain Support**:
- Stellar: Full implementation (6 tools, Blend Capital integration)
- EVM: Migration in progress (Base as primary target)
- Solana/Bitcoin/Zcash: Planned

---

## 8. Migration Roadmap: Stellar → Multichain

### Phase 1: Base (EVM) Integration (Q1 2026)

**Goals**:
- Deploy ERC-4626 vaults on Base
- Integrate Aave V3, Morpho, Compound
- Add EVM tools (18 tools parallel to Stellar)
- Support MetaMask/Coinbase Wallet (optional, for those who want it)

**Why Base**:
- Low fees (~$0.01 vs $1-50 on Ethereum)
- Fast (2 second blocks)
- Coinbase backing (easy onramps)
- Strong DeFi ecosystem (Aave, Uniswap, Morpho)

### Phase 2: Cross-Chain Router (Q2 2026)

**Goals**:
- LayerZero integration (bridge aggregator)
- Automatic yield routing across chains
- Gas optimization engine
- Single-click cross-chain deposits

**User Experience**:
```
User: "Deposit $1,000 USDC and find the best yield"

Agent:
1. Analyzes yields across all chains
2. Finds Morpho on Base: 14.2% APY (best)
3. Routes USDC from user's Ethereum wallet → Base
4. Supplies to Morpho vault
5. Generates research report citing strategy

User sees: "Deposited $1,000, earning 14.2% APY"
Reality: 3 transactions across 2 chains, invisible
```

### Phase 3: Solana + Bitcoin (Q3 2026)

**Solana**:
- Kamino Finance (lending)
- Drift Protocol (perps)
- High-frequency yield opportunities

**Bitcoin**:
- Pristine collateral (non-inflationary)
- Wrapped BTC on EVM (wBTC, tBTC)
- Lightning Network (fast payments)

**Zcash**:
- Privacy layer (shielded transactions)
- Regulatory hedge (if privacy becomes premium)

### Phase 4: Phala TEE Deployment (Q4 2026)

**Goals**:
- Migrate agent compute to Phala Network
- Encrypted filesystem (keys.json, context.db)
- Attestation UI (prove your agent is secure)
- Decentralized execution (no single point of failure)

**Phala Integration**:
```python
# agent_logic.py running in Phala TEE
from phala import SecureStorage, Attestation

class SovereignAgent:
    def __init__(self, user_id):
        self.storage = SecureStorage(user_id)  # Encrypted FS
        self.keys = self.storage.load('keys.json')  # Multi-chain keys
        self.context = self.storage.load('context.db')  # User prefs

    def optimize_yield(self):
        # Agent has full access to keys within TEE
        # But keys never leave the secure enclave
        yields = self.fetch_cross_chain_yields()
        best = max(yields, key=lambda y: y.apy_adjusted_for_risk)
        self.rebalance(best)
        self.generate_research_report()
```

---

## 9. Technical Stack Overview

### Infrastructure Layers

```
┌─────────────────────────────────────────────────┐
│              User Interface Layer                │
│  React 19 + TypeScript + Vite                   │
│  - Chat interface (Choir Thought Bank)          │
│  - Vault dashboard (deposits/yields)            │
│  - Portfolio view (multi-chain assets)          │
└─────────────────────────────────────────────────┘
                    ↕ HTTPS/WebSocket
┌─────────────────────────────────────────────────┐
│           Application Backend Layer              │
│  FastAPI + Python 3.11+                         │
│  - LangChain agent orchestration                │
│  - Claude SDK (research/strategy)               │
│  - Multi-step reasoning engine                  │
│  - User isolation + session management          │
└─────────────────────────────────────────────────┘
                    ↕ API Calls
┌─────────────────────────────────────────────────┐
│         Blockchain Integration Layer             │
│  - web3.py / ethers.js (EVM chains)             │
│  - stellar-sdk (Stellar)                        │
│  - solana-py (Solana)                           │
│  - bitcoinlib (Bitcoin)                         │
└─────────────────────────────────────────────────┘
                    ↕ RPC/HTTP
┌─────────────────────────────────────────────────┐
│              DeFi Protocol Layer                 │
│  EVM: Aave V3, Morpho, Compound, Uniswap        │
│  Stellar: Blend Capital                         │
│  Solana: Kamino, Drift                          │
└─────────────────────────────────────────────────┘
                    ↕ Smart Contract Calls
┌─────────────────────────────────────────────────┐
│         Blockchain Settlement Layer              │
│  Base, Ethereum, Arbitrum, Optimism              │
│  Stellar, Solana, Bitcoin, Zcash                │
└─────────────────────────────────────────────────┘
```

### Security Architecture

```
┌─────────────────────────────────────────────────┐
│     Frontend (Untrusted, User's Browser)        │
│  - Passkey authentication (WebAuthn)            │
│  - UI rendering                                 │
│  - API calls to backend                         │
└─────────────────────────────────────────────────┘
                    ↕ HTTPS (TLS)
┌─────────────────────────────────────────────────┐
│     Backend (Semi-Trusted, Our Servers)         │
│  - Session validation                           │
│  - Agent orchestration                          │
│  - NO ACCESS to private keys                    │
└─────────────────────────────────────────────────┘
                    ↕ Secure Channel
┌─────────────────────────────────────────────────┐
│      Phala TEE (Trusted, Hardware-Isolated)     │
│  - Private keys stored encrypted                │
│  - Agent execution in secure enclave            │
│  - Cryptographic attestation                    │
│  - Even Choir team can't access keys            │
└─────────────────────────────────────────────────┘
```

---

## 10. Product Positioning

### Who We're For

**Target Users**:
1. **Intellectual Contributors** (no capital required)
   - Writers, researchers, analysts
   - Earn CHIP through chat/novelty rewards
   - Publish articles, earn citation income ($$ in stablecoins)
   - Never need to deploy capital to earn

2. **Sophisticated Investors** ($500 - $1M+ capital)
   - Want yield optimization without active management
   - Value transparency (research reports)
   - Appreciate tax-aware rebalancing
   - Need multi-chain access

3. **Hybrid Users** (ideas + capital)
   - Publish research that informs their own strategies
   - Deploy capital based on their own insights
   - Earn from both sides (citations + yields)

### Competitive Differentiation

| Feature | Choir | Aave | Yearn | ChatGPT |
|---------|-------|------|-------|---------|
| Multi-chain yield | ✅ | Single chain | EVM only | N/A |
| AI agent | ✅ | ❌ | ❌ | No execution |
| Research layer | ✅ | ❌ | ❌ | No financial tools |
| Non-custodial | ✅ | ✅ | ✅ | N/A |
| TEE security | ✅ | ❌ | ❌ | ❌ |
| Passkey auth | ✅ | ❌ | ❌ | Password |
| Citation rewards | ✅ | N/A | N/A | N/A |
| Tax-aware | ✅ (Q3 '26) | ❌ | ❌ | N/A |

**The Moat**: Big Tech can't give you a private sovereign computer running in a TEE with keys you control across all chains.

---

## 11. Business Model

### Revenue Streams

**Primary**:
1. **Performance fees** (20% of profits from yield mining)
   - Example: User earns $10k yield → Choir takes $2k
   - Distributed: 70% citation rewards, 20% ops, 10% buyback/burn

2. **Protocol-owned liquidity** (trading fees)
   - Deep CHOIR/USDC pools on DEXs
   - Earn 0.3% fees on all trades
   - Estimated: $100k+/year at scale

3. **Treasury yield** (deploying protocol-owned capital)
   - Borrow against CHOIR holdings (40% LTV)
   - Deploy borrowed capital at 10-15% yields
   - Net revenue after borrowing costs

**Secondary**:
4. **Covered calls** (options premiums on CHOIR)
5. **User lending** (borrow USDC against CHIP, earn spreads)
6. **Ecosystem investments** (incubator for projects on Choir)

### Not Extraction

**We do NOT**:
- ❌ Charge subscriptions (users deposit, fees only on performance)
- ❌ Sell tokens (we accumulate CHIP, use as collateral)
- ❌ Extract from free users (they create network effects)
- ❌ Advertise (no ads, ever)

---

## 12. Success Metrics

### Q4 2025 (Launch)
- [ ] 1,000 registered users (passkey auth)
- [ ] $50k TVL across vaults (Base + Stellar)
- [ ] 50 published articles (Thought Bank)
- [ ] 10-15% average APY (realistic yields)

### Q1 2026 (Growth)
- [ ] 10,000 users
- [ ] $500k TVL
- [ ] 500 articles
- [ ] 3 chains supported (Base, Stellar, Arbitrum)

### Q2 2026 (Scale)
- [ ] 50,000 users
- [ ] $5M TVL
- [ ] 2,000 articles
- [ ] Cross-chain routing operational

### Q4 2026 (Maturity)
- [ ] 200,000 users
- [ ] $50M TVL
- [ ] Full Phala TEE deployment
- [ ] 6 chains supported
- [ ] Tax-aware optimization live

---

## 13. Open Questions & Decisions

### Technical Decisions

1. **Primary EVM chain**: Base vs Arbitrum vs Optimism
   - **Decision**: Base (Coinbase backing, low fees, fast growth)

2. **Smart contract standard**: ERC-4626 vs custom vault
   - **Decision**: ERC-4626 (industry standard, composability)

3. **Agent SDK**: Claude SDK vs OpenHands
   - **Decision**: Claude SDK (better for research workflows)

4. **Account abstraction**: Now vs later
   - **Decision**: Later (EOAs first, AA as optional upgrade in Q3 '26)

5. **Cross-chain bridge**: LayerZero vs Wormhole vs native
   - **Decision**: Start with native bridges, add LayerZero Q2 '26

### Business Decisions

1. **Migrate from Stellar or support both?**
   - **Decision**: Support both, but EVM as primary (12-month transition)

2. **Token launch timing**: Q4 2025 vs Q1 2026
   - **Decision**: Q4 2025 (alongside vault launch)

3. **Initial CHIP price**: $0.10 vs $1.00 vs market-determined
   - **Decision**: Market-determined via DEX launch (no pre-sale)

---

## 14. Next Immediate Actions

### Week 1 (Documentation)
- [x] Create SOVEREIGN_CLOUD_ARCHITECTURE.md (this doc)
- [ ] Update CLAUDE.md (remove Stellar exclusivity)
- [ ] Update MULTICHAIN_EVM_MIGRATION_PLAN.md (align with vision)
- [ ] Update CHOIR_WHITEPAPER.md (Sovereign Cloud framing)

### Week 2 (Base Integration)
- [ ] Set up Base testnet environment
- [ ] Deploy ERC-4626 vault to Base Sepolia
- [ ] Test Aave V3 integration on Base
- [ ] Create EVM tools (parallel to Stellar tools)

### Week 3 (Frontend Updates)
- [ ] Add wagmi + viem (EVM wallet support)
- [ ] Update VaultDashboard for ERC-4626
- [ ] Add chain switcher (Stellar vs Base)
- [ ] Test with MetaMask/Coinbase Wallet

### Month 2 (Testnet Beta)
- [ ] Invite 50 beta testers
- [ ] Deploy to Base testnet
- [ ] Collect feedback
- [ ] Iterate on UX

---

**Document Version**: 1.0
**Created**: 2025-11-22
**Status**: Authoritative architecture spec
**Supersedes**: All previous Stellar-exclusive documentation

**Key Contacts**:
- Architecture questions: Refer to this doc
- Implementation questions: See MULTICHAIN_EVM_MIGRATION_PLAN.md
- Business strategy: See CHOIR_WHITEPAPER.md (updated)
