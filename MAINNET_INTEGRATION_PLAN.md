# Tuxedo Mainnet Integration Plan

**Status**: Planning Document
**Created**: 2025-11-09
**Priority**: High - Testnet pools have zero yield, blocking core functionality

## Executive Summary

This document outlines the strategy for migrating Tuxedo from testnet-only to a **mainnet-first architecture** where:

1. **Mainnet is the default** for querying pool data, APY, and market information (real yields!)
2. **AI Agent controls network selection** dynamically based on user actions
3. **Testnet accounts** are automatically provided for learning/testing
4. **Mainnet accounts** require user deposit of real funds
5. **Network configuration** is centralized and easily toggled via environment variables

## Problem Statement

### Current State
- **Tuxedo is testnet-only** with hardcoded testnet contract addresses and URLs
- **Blend testnet pools have 0% APY** making yield farming demonstrations impossible
- **Configuration is scattered** across 13+ locations (frontend + backend)
- **No mainnet support** despite production-ready architecture

### Why Mainnet Now?
1. **Real market data**: Mainnet pools have actual yield (e.g., 5-15% APY on USDC)
2. **Real user value**: Demonstrable DeFi operations with meaningful returns
3. **Low risk entry**: $10 deposit is sufficient for educational demonstration
4. **Better UX**: Users see real numbers, not placeholder zeros

## Architecture Vision

### Agent-Controlled Network Toggle

```
User Action              →  AI Decision          →  Network Used
─────────────────────────────────────────────────────────────────
"What's USDC APY?"      →  Read-only query     →  MAINNET (real data)
"Show me pools"         →  Read-only query     →  MAINNET (real yields)
"Create an account"     →  Generate keypair    →  TESTNET (friendbot funded)
"Supply 100 USDC"       →  Check account type  →  Depends on account network
User deposits real XLM  →  Import to mainnet   →  MAINNET (real operations)
```

### Network Configuration Strategy

**Centralized Configuration** (`backend/config/settings.py` + `.env`):

```python
# Backend Environment Variables
STELLAR_NETWORK=mainnet              # Default to mainnet
MAINNET_HORIZON_URL=https://horizon.stellar.org
MAINNET_SOROBAN_RPC_URL=<provider>   # QuickNode, Blockdaemon, etc.
TESTNET_HORIZON_URL=https://horizon-testnet.stellar.org
TESTNET_SOROBAN_RPC_URL=https://soroban-testnet.stellar.org
```

**Frontend Configuration** (`src/contracts/util.ts`):

```typescript
export const NETWORK_CONFIG = {
  mainnet: {
    passphrase: 'Public Global Stellar Network ; September 2015',
    horizonUrl: 'https://horizon.stellar.org',
    rpcUrl: process.env.VITE_MAINNET_RPC_URL,
    contracts: BLEND_MAINNET_CONTRACTS
  },
  testnet: {
    passphrase: 'Test SDF Network ; September 2015',
    horizonUrl: 'https://horizon-testnet.stellar.org',
    rpcUrl: 'https://soroban-testnet.stellar.org',
    contracts: BLEND_TESTNET_CONTRACTS
  }
}

// Default to mainnet for read operations
export const DEFAULT_NETWORK = 'mainnet'
```

## Implementation Checklist

### Phase 1: Contract Address Configuration (Backend)

**File: `backend/blend_pool_tools.py`**

Current:
```python
BLEND_TESTNET_CONTRACTS = {
    'backstop': 'CBHWKF4RHIKOKSURAKXSJRIIA7RJAMJH4VHRVPYGUF4AJ5L544LYZ35X',
    # ... testnet addresses
}

NETWORK_CONFIG = {
    'testnet': { ... }
}
```

Required Changes:
```python
# Add mainnet contract addresses
BLEND_MAINNET_CONTRACTS = {
    # Core V2 Infrastructure
    'backstop': 'CAQQR5SWBXKIGZKPBZDH3KM5GQ5GUTPKB7JAFCINLZBC5WXPJKRG3IM7',
    'poolFactory': 'CDSYOAVXFY7SM5S64IZPPPYB4GVGGLMQVFREPSQQEZVIWXX5R23G4QSU',
    'emitter': 'CCOQM6S7ICIUWA225O5PSJWUBEMXGFSSW2PQFO6FP4DQEKMS5DASRGRR',

    # Tokens
    'blnd': 'CD25MNVTZDL4Y3XBCPCJXGXATV5WUHHOWMYFF4YBEGU5FCPGMYTVG5JY',
    'usdc': 'CCW67TSZV3SSS2HXMBQ5JFGCKJNXKZM7UQUWUZPUTHXSTZLEO7SJMI75',
    'xlm': 'CAS3J7GYLGXMF6TDJBBYYSE3HQ6BBSMLNUQ34T6TZMYMW2EVH34XOWMA',

    # Pools
    'comet': 'CAS3FL6TLZKDGGSISDBWGGPXT3NRR4DYTZD7YOD3HMYO6LTJUVGRVEAM',
    'fixed': 'CAJJZSGMMM3PD7N33TAPHGBUGTB43OC73HVIK2L2G6BNGGGYOSSYBXBD',
    'yieldBlox': 'CCCCIQSDILITHMM7PBSLVDT5MISSY7R26MNZXCX4H7J5JQ5FPIYOGYFS',
}

NETWORK_CONFIG = {
    'mainnet': {
        'rpc_url': 'YOUR_MAINNET_RPC_PROVIDER',  # See RPC Providers section
        'passphrase': 'Public Global Stellar Network ; September 2015',
        'contracts': BLEND_MAINNET_CONTRACTS,
        'backstop': 'CAQQR5SWBXKIGZKPBZDH3KM5GQ5GUTPKB7JAFCINLZBC5WXPJKRG3IM7',
    },
    'testnet': {
        'rpc_url': 'https://soroban-testnet.stellar.org',
        'passphrase': 'Test SDF Network ; September 2015',
        'contracts': BLEND_TESTNET_CONTRACTS,
        'backstop': 'CBHWKF4RHIKOKSURAKXSJRIIA7RJAMJH4VHRVPYGUF4AJ5L544LYZ35X',
    }
}

# Default to mainnet for pool discovery
DEFAULT_NETWORK = 'mainnet'
```

### Phase 2: Contract Address Configuration (Frontend)

**File: `src/contracts/blend.ts`**

Current:
```typescript
export const BLEND_CONTRACTS = {
  poolFactory: "CDSMKKCWEAYQW4DAUSH3XGRMIVIJB44TZ3UA5YCRHT6MP4LWEWR4GYV6",
  // ... testnet only
}
```

Required Changes:
```typescript
// Mainnet contract addresses
export const BLEND_MAINNET_CONTRACTS = {
  // Core V2 Infrastructure
  backstop: "CAQQR5SWBXKIGZKPBZDH3KM5GQ5GUTPKB7JAFCINLZBC5WXPJKRG3IM7",
  poolFactory: "CDSYOAVXFY7SM5S64IZPPPYB4GVGGLMQVFREPSQQEZVIWXX5R23G4QSU",
  emitter: "CCOQM6S7ICIUWA225O5PSJWUBEMXGFSSW2PQFO6FP4DQEKMS5DASRGRR",

  // Tokens
  blndToken: "CD25MNVTZDL4Y3XBCPCJXGXATV5WUHHOWMYFF4YBEGU5FCPGMYTVG5JY",
  usdcToken: "CCW67TSZV3SSS2HXMBQ5JFGCKJNXKZM7UQUWUZPUTHXSTZLEO7SJMI75",
  xlmToken: "CAS3J7GYLGXMF6TDJBBYYSE3HQ6BBSMLNUQ34T6TZMYMW2EVH34XOWMA",

  // Pools
  cometPool: "CAS3FL6TLZKDGGSISDBWGGPXT3NRR4DYTZD7YOD3HMYO6LTJUVGRVEAM",
  fixedPool: "CAJJZSGMMM3PD7N33TAPHGBUGTB43OC73HVIK2L2G6BNGGGYOSSYBXBD",
  yieldBloxPool: "CCCCIQSDILITHMM7PBSLVDT5MISSY7R26MNZXCX4H7J5JQ5FPIYOGYFS",
} as const;

// Testnet contract addresses (existing)
export const BLEND_TESTNET_CONTRACTS = {
  poolFactory: "CDSMKKCWEAYQW4DAUSH3XGRMIVIJB44TZ3UA5YCRHT6MP4LWEWR4GYV6",
  backstop: "CBHWKF4RHIKOKSURAKXSJRIIA7RJAMJH4VHRVPYGUF4AJ5L544LYZ35X",
  // ... existing testnet addresses
} as const;

// Export based on environment (default to mainnet)
export const BLEND_CONTRACTS =
  import.meta.env.VITE_STELLAR_NETWORK === 'testnet'
    ? BLEND_TESTNET_CONTRACTS
    : BLEND_MAINNET_CONTRACTS;
```

### Phase 3: Network Configuration (`backend/config/settings.py`)

```python
class Settings:
    def __init__(self):
        # ... existing settings ...

        # Network Selection
        self.default_network = os.getenv("STELLAR_NETWORK", "mainnet")

        # Mainnet Configuration
        self.mainnet_horizon_url = os.getenv(
            "MAINNET_HORIZON_URL",
            "https://horizon.stellar.org"
        )
        self.mainnet_rpc_url = os.getenv(
            "MAINNET_SOROBAN_RPC_URL",
            None  # Must be provided by user
        )
        self.mainnet_passphrase = "Public Global Stellar Network ; September 2015"

        # Testnet Configuration
        self.testnet_horizon_url = os.getenv(
            "TESTNET_HORIZON_URL",
            "https://horizon-testnet.stellar.org"
        )
        self.testnet_rpc_url = os.getenv(
            "TESTNET_SOROBAN_RPC_URL",
            "https://soroban-testnet.stellar.org"
        )
        self.testnet_passphrase = "Test SDF Network ; September 2015"
        self.friendbot_url = os.getenv(
            "FRIENDBOT_URL",
            "https://friendbot.stellar.org"
        )

    def get_network_config(self, network: str = None):
        """Get configuration for specified network (defaults to default_network)"""
        net = network or self.default_network

        if net == "mainnet":
            if not self.mainnet_rpc_url:
                raise ValueError(
                    "MAINNET_SOROBAN_RPC_URL not configured. "
                    "Please set up a mainnet RPC provider."
                )
            return {
                'horizon_url': self.mainnet_horizon_url,
                'rpc_url': self.mainnet_rpc_url,
                'passphrase': self.mainnet_passphrase,
            }
        else:  # testnet
            return {
                'horizon_url': self.testnet_horizon_url,
                'rpc_url': self.testnet_rpc_url,
                'passphrase': self.testnet_passphrase,
            }
```

### Phase 4: Account Manager Network Tracking

**File: `backend/account_manager.py`**

Add network field to account metadata:

```python
def generate_account(
    self,
    user_id: str,
    chain: str = "stellar",
    name: str = "Stellar Account",
    network: str = "testnet"  # NEW: default to testnet for safety
) -> Dict[str, Any]:
    """
    Generate new account with network tracking.

    Testnet accounts: Auto-funded via Friendbot
    Mainnet accounts: Require manual funding
    """
    # ... existing keypair generation ...

    account_data = {
        'id': account_id,
        'user_id': user_id,
        'public_key': public_key,
        'encrypted_private_key': encrypted_sk,
        'chain': chain,
        'network': network,  # NEW: track which network
        'alias': name,
        'created_at': datetime.now().isoformat(),
    }

    # Auto-fund testnet accounts
    if network == 'testnet':
        self._fund_testnet_account(public_key)

    # Mainnet accounts require manual funding
    # (user must deposit real XLM)
```

### Phase 5: AI Agent Tool Updates

**File: `backend/blend_account_tools.py`**

Update LangChain tool wrappers to accept network parameter:

```python
@tool
def blend_find_best_yield(
    asset_symbol: str,
    min_apy: float = 0.0,
    network: str = "mainnet"  # NEW: default to mainnet for queries
) -> str:
    """
    Find highest APY opportunities across all Blend pools.

    Args:
        asset_symbol: Asset to search (e.g., "USDC", "XLM")
        min_apy: Minimum APY threshold
        network: "mainnet" (real yields) or "testnet" (usually 0%)

    Returns:
        Formatted list of yield opportunities
    """
    # ... implementation with network parameter
```

### Phase 6: RPC Provider Selection

**Mainnet Soroban RPC Providers** (required for mainnet):

| Provider       | Free Tier | Pricing | URL Pattern |
|----------------|-----------|---------|-------------|
| **QuickNode** | 3M requests/month | $9-299/mo | `https://[your-endpoint].stellar-mainnet.quiknode.pro/...` |
| **Blockdaemon** | 25M requests | $19-299/mo | `https://svc.blockdaemon.com/stellar/mainnet/rpc` |
| **Validation Cloud** | 100M requests | Contact | Custom endpoint |
| **Ankr** | 500M requests | Free tier available | `https://rpc.ankr.com/stellar` |

**Recommendation**: Start with **Ankr** (free tier) or **QuickNode** (best DX)

### Phase 7: Environment Variables Update

**Backend `.env`**:
```bash
# Network Selection
STELLAR_NETWORK=mainnet  # or "testnet"

# Mainnet Configuration
MAINNET_HORIZON_URL=https://horizon.stellar.org
MAINNET_SOROBAN_RPC_URL=https://your-provider.com/stellar-rpc  # REQUIRED

# Testnet Configuration (kept for account creation)
TESTNET_HORIZON_URL=https://horizon-testnet.stellar.org
TESTNET_SOROBAN_RPC_URL=https://soroban-testnet.stellar.org
FRIENDBOT_URL=https://friendbot.stellar.org
```

**Frontend `.env.local`**:
```bash
# Network Selection
VITE_STELLAR_NETWORK=mainnet

# Mainnet
VITE_MAINNET_HORIZON_URL=https://horizon.stellar.org
VITE_MAINNET_RPC_URL=https://your-provider.com/stellar-rpc

# Testnet
VITE_TESTNET_HORIZON_URL=https://horizon-testnet.stellar.org
VITE_TESTNET_RPC_URL=https://soroban-testnet.stellar.org
```

## User Experience Flow

### Scenario 1: User Asks About Yields (Read-Only)

```
User: "What's the best APY for USDC?"

Agent:
  1. Uses blend_find_best_yield(asset="USDC", network="mainnet")
  2. Queries MAINNET Blend pools
  3. Returns: "Comet Pool offers 12.5% APY for USDC on mainnet"

Network: MAINNET (read-only, no account needed)
```

### Scenario 2: User Creates Account (Testnet Default)

```
User: "Create me an account"

Agent:
  1. Calls account_manager.generate_account(user_id, network="testnet")
  2. Generates keypair
  3. Funds via Friendbot (10,000 XLM testnet)
  4. Returns account details

Network: TESTNET (safe, free, funded)
Agent Message: "Created testnet account with 10,000 XLM. To use mainnet,
               deposit real funds to: [mainnet_address]"
```

### Scenario 3: User Deposits Real Funds (Mainnet)

```
User deposits real XLM to provided mainnet address

Agent:
  1. Detects account has mainnet balance
  2. Marks account as "mainnet-ready"
  3. All subsequent operations use mainnet

Network: MAINNET (user has real funds)
Agent Message: "Detected 15 XLM on mainnet. You can now interact with
               real Blend pools!"
```

### Scenario 4: Supply Operation

```
User: "Supply 100 USDC to highest yield pool"

Agent:
  1. Checks account network (testnet or mainnet)
  2. If testnet: "This is a testnet account. Would you like to practice
                  on testnet or use your mainnet account?"
  3. If mainnet: Proceeds with real transaction

Network: Depends on account
```

## Security Considerations

### Mainnet Safety Guardrails

1. **Explicit Confirmation for Mainnet Transactions**
   ```python
   if network == 'mainnet' and operation_type == 'write':
       # Require explicit user confirmation
       agent_response = "⚠️ This will use REAL funds on mainnet. Confirm?"
   ```

2. **Transaction Limits for First-Time Mainnet Users**
   ```python
   if account.mainnet_tx_count < 5:
       max_amount = 10  # USD equivalent
       if amount > max_amount:
           return f"First-time limit: ${max_amount}. Build trust first!"
   ```

3. **Clear Network Indicators in UI**
   ```typescript
   <NetworkBadge network={currentNetwork}>
     {network === 'mainnet' ? '🔴 MAINNET (Real $)' : '🟢 TESTNET (Practice)'}
   </NetworkBadge>
   ```

## Migration Strategy

### Gradual Rollout

**Week 1**: Backend Configuration
- Add mainnet contract addresses
- Update network config system
- Set up RPC provider
- Deploy to staging

**Week 2**: Frontend Updates
- Add network toggle UI
- Update contract imports
- Test pool discovery on mainnet
- Deploy to production (read-only mode)

**Week 3**: Account Network Tracking
- Update AccountManager with network field
- Implement testnet auto-funding
- Add mainnet detection logic

**Week 4**: Full Integration
- Enable mainnet write operations
- Add safety confirmations
- Monitor transactions
- User feedback iteration

## Testing Plan

### Mainnet Read Operations (Safe)
- [ ] Pool discovery returns mainnet pools
- [ ] APY queries show real yields
- [ ] Reserve data matches Blend UI
- [ ] Best yield finder works correctly

### Testnet Account Creation (Safe)
- [ ] New accounts funded via Friendbot
- [ ] Account metadata includes network field
- [ ] Testnet operations isolated

### Mainnet Transactions (Careful Testing)
- [ ] Start with $1-5 test deposits
- [ ] Verify transaction signing
- [ ] Confirm blockchain submission
- [ ] Validate pool position updates

## Success Metrics

**Pre-Launch**:
- ❌ Blend testnet APY: 0%
- ❌ User frustration with fake data
- ❌ Cannot demonstrate real value

**Post-Launch**:
- ✅ Blend mainnet APY: 5-15% (real!)
- ✅ Users see actual yield opportunities
- ✅ $10 deposits enable real DeFi learning
- ✅ Network toggle provides flexibility

## Cost Estimates

### Monthly Operating Costs

| Resource | Provider | Tier | Cost |
|----------|----------|------|------|
| Mainnet RPC | Ankr | Free | $0 |
| Mainnet RPC | QuickNode | Basic | $9/mo |
| Horizon API | Stellar SDF | Free | $0 |
| User Test Funds | N/A | $10 one-time | $10 |

**Total**: $0-9/month + one-time $10 test deposit

## Risks and Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| User loses mainnet funds | High | Multi-level confirmations, small limits |
| RPC provider downtime | Medium | Fallback to testnet for queries |
| Network confusion | Medium | Clear UI indicators, agent messaging |
| Gas fee spikes | Low | Pre-calculate fees, warn if >$1 |

## Open Questions

1. **Which RPC provider to use?**
   - Recommendation: Start with Ankr (free), upgrade to QuickNode if needed

2. **Should we keep dual-network accounts?**
   - Yes - One testnet (practice) + one mainnet (real) per user

3. **How to handle network switching mid-conversation?**
   - Agent explicitly states: "Switching to mainnet for this operation..."

4. **Transaction fee warnings?**
   - Yes - Show estimated cost before every mainnet write

5. **Mainnet contract verification?**
   - Cross-reference all addresses with official Blend documentation

## Next Steps

1. **RPC Provider Setup**
   - Sign up for Ankr or QuickNode
   - Test connectivity
   - Add to `.env`

2. **Backend Configuration**
   - Implement Phase 1-3 changes
   - Test pool discovery on mainnet
   - Verify APY calculations

3. **Frontend Updates**
   - Add network toggle component
   - Update contract addresses
   - Test dashboard with mainnet data

4. **Documentation**
   - Update README with mainnet info
   - Add network toggle instructions
   - Document RPC setup

5. **Security Review**
   - Test transaction confirmations
   - Verify permission checks
   - Add network indicators

## References

- [Stellar Networks Documentation](https://developers.stellar.org/docs/networks)
- [Blend Capital Mainnet Deployments](https://docs-v1.blend.capital/mainnet-deployments)
- [Blend Utils Repository](https://github.com/blend-capital/blend-utils)
- Mainnet Contract Addresses: `mainnet.contracts.json`
- Testnet Contract Addresses: `testnet.contracts.json`

## Conclusion

Moving to mainnet-first architecture is:

✅ **Technically feasible** - All infrastructure is ready
✅ **User-valuable** - Real yields vs 0% testnet
✅ **Low-risk** - $10 test deposits, strong guardrails
✅ **Scalable** - Agent-controlled network selection

**Recommended Action**: Proceed with phased implementation, starting with read-only mainnet queries (Week 1-2), then gradually enabling mainnet write operations with proper safety checks.

---

**Document Status**: Ready for Review
**Last Updated**: 2025-11-09
**Owner**: Tuxedo Development Team
