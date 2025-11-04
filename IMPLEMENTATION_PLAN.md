# Real Testnet Blend Integration Plan

## Executive Summary

This plan outlines the transition from mock data and mainnet queries to real testnet Blend pools with live DeFindex API integration. The objective is to create functional yield farming on Stellar testnet with real pool data, deposits, and yield tracking.

## Current State Analysis

### Critical Issues Identified
1. **Mixed Network Configuration**: Tools query mainnet vaults but execute testnet transactions
2. **Mock Data Everywhere**: APY values, TVL calculations, and vault data are hardcoded
3. **Unused API Client**: Complete DeFindex API client exists but tools don't use it
4. **Testnet Address Gaps**: Limited real testnet vault addresses
5. **No Real Deposits**: Current transactions are simple XLM payments, not actual vault deposits

### Files Requiring Major Changes
- `backend/defindex_soroban.py` - Core mock data removal
- `backend/defindex_tools.py` - API integration
- `backend/defindex_client.py` - Endpoint verification
- `backend/.env` - API key configuration

## Phase 1: API Integration Foundation

[x] COMPLETED
### 1.1 Environment Configuration
**File**: `backend/.env`
```bash
# Add DeFindex API configuration
DEFINDEX_API_KEY=sk_your_real_api_key_here
DEFINDEX_BASE_URL=https://api.defindex.io
DEFINDEX_NETWORK=testnet
```

**Action**: Obtain real DeFindex API key from https://docs.defindex.io

### 1.2 API Client Verification
**File**: `backend/defindex_client.py`

**Current Issues**:
- Base URL not verified (line 23: `# ⚠️ TODO: Verify correct base URL`)
- Multiple endpoint attempts indicate uncertainty
- No error handling for network-specific responses

**Required Changes**:
1. Verify correct base URL with DeFindex team
2. Test connection on startup
3. Add proper error handling for testnet vs mainnet differences
4. Implement endpoint discovery mechanism

### 1.3 Update Tools to Use API Client
**File**: `backend/defindex_tools.py`

**Current State**: Uses `get_defindex_soroban()` with hardcoded mock data
**Target State**: Use `get_defindex_client()` for real data

**Implementation Strategy**:
1. Import and initialize DeFindexClient
2. Replace `discover_high_yield_vaults()` to call `client.get_vaults()`
3. Add network parameter to ensure testnet consistency
4. Graceful fallback to mock data during testing

## Phase 2: Real Testnet Vault Discovery

### 2.1 Testnet Vault Address Research
**Problem**: Limited real testnet vault addresses
**Solution**: Create testnet vault discovery mechanism

**Approaches**:
1. **Official Testnet Vaults**: Contact DeFindex for official testnet vault list
2. **Create Test Vaults**: Use DeFindex dApp on testnet to create vaults
3. **Community Vaults**: Find community-created testnet vaults
4. **Mock Testnet Vaults**: Use Blend protocol directly for testnet pools

**File**: `backend/defindex_soroban.py`
```python
# Replace TESTNET_VAULTS with real addresses
TESTNET_VAULTS = {
    # Real testnet vaults (to be discovered)
    'XLM_Blend_Test': 'REAL_TESTNET_ADDRESS_HERE',
    'USDC_Blend_Test': 'REAL_TESTNET_ADDRESS_HERE',
}
```

### 2.2 Dynamic Vault Discovery
**Enhancement**: Add automatic testnet vault discovery

**Implementation**:
```python
async def discover_testnet_vaults() -> Dict[str, str]:
    """Discover real testnet vaults from multiple sources"""
    vaults = {}

    # 1. Try DeFindex API for testnet vaults
    try:
        client = get_defindex_client(network='testnet')
        api_vaults = client.get_vaults()
        for vault in api_vaults:
            vaults[vault['name']] = vault['address']
    except Exception as e:
        logger.warning(f"API discovery failed: {e}")

    # 2. Fallback to known Blend testnet pools
    vaults.update(get_blend_testnet_pools())

    return vaults
```

## Phase 3: Real Yield Data Integration

### 3.1 Replace Mock APY Data
**File**: `backend/defindex_soroban.py`

**Current Mock Data** (Lines 37-49):
```python
MOCK_APY_DATA = {
    'USDC_Blend_Fixed': 45.2,
    'USDC_Blend_Yieldblox': 52.8,
    # ... hardcoded values
}
```

**Replacement Strategy**:
1. **Primary**: Real-time APY from DeFindex API
2. **Secondary**: On-chain calculation using Blend protocol data
3. **Fallback**: Cached APY with timestamp for offline operation

### 3.2 Real TVL Calculation
**Current Mock Implementation** (Line 80):
```python
'tvl': 1000000 + hash(name) % 5000000,  # Mock TVL data
```

**Real TVL Implementation**:
```python
async def get_real_tvl(vault_address: str) -> float:
    """Get real TVL from on-chain data"""
    try:
        # Query vault contract for total assets
        contract_data = await soroban.get_contract_data(vault_address)
        return calculate_tvl_from_assets(contract_data)
    except Exception:
        # Fallback to API data
        return await client.get_vault_tvl(vault_address)
```

## Phase 4: Real Deposit Implementation

### 4.1 Current Deposit Analysis
**File**: `backend/defindex_tools.py` - `prepare_defindex_deposit()`

**Current Behavior**:
- Creates simple XLM payment to demo address
- Uses mainnet vault address only for metadata
- No actual vault interaction

**Target Behavior**:
- Build real vault deposit transaction
- Use DeFindex API transaction building
- Support testnet vault deposits

### 4.2 Real Deposit Transaction Building
**Implementation**:
```python
@tool
async def prepare_defindex_deposit(
    vault_address: str,
    amount_xlm: float,
    user_address: str,
    network: str = "testnet"
) -> str:
    """Prepare real deposit transaction using DeFindex API"""
    try:
        # Use API client for real transaction building
        client = get_defindex_client(network=network)

        # Convert to stroops
        amount_stroops = int(amount_xlm * 10_000_000)

        # Build real deposit transaction
        tx_data = client.build_deposit_transaction(
            vault_address=vault_address,
            amount_stroops=amount_stroops,
            caller=user_address,
            invest=True
        )

        return format_transaction_response(tx_data)

    except Exception as e:
        return f"Error building deposit: {str(e)}"
```

## Phase 5: Network Configuration Management

### 5.1 Centralized Network Configuration
**New File**: `backend/config/networks.py`

```python
class NetworkConfig:
    TESTNET = {
        'horizon_url': 'https://horizon-testnet.stellar.org',
        'soroban_url': 'https://soroban-testnet.stellar.org',
        'friendbot_url': 'https://friendbot.stellar.org',
        'network_passphrase': 'Test SDF Network ; September 2015'
    }

    MAINNET = {
        'horizon_url': 'https://horizon.stellar.org',
        'soroban_url': 'https://mainnet.stellar.expert/explorer/rpc',
        'network_passphrase': 'Public Global Stellar Network ; September 2015'
    }
```

### 5.2 Environment-Based Network Selection
**File**: `backend/main.py`

```python
# Load network from environment
NETWORK = os.getenv('STELLAR_NETWORK', 'testnet')  # Default to testnet

# Initialize clients with correct network
defindex_client = get_defindex_client(network=NETWORK)
stellar_tools = get_stellar_tools(network=NETWORK)
```

## Phase 6: Testing and Validation

### 6.1 Unit Tests
**New File**: `tests/test_defindex_integration.py`

```python
async def test_real_vault_discovery():
    """Test discovering real testnet vaults"""
    client = get_defindex_client('testnet')
    vaults = client.get_vaults()
    assert len(vaults) > 0, "No testnet vaults found"

async def test_real_deposit_transaction():
    """Test building real deposit transaction"""
    client = get_defindex_client('testnet')
    tx_data = client.build_deposit_transaction(
        vault_address=TEST_VAULT,
        amount_stroops=10000000,  # 1 XLM
        caller=TEST_USER
    )
    assert 'xdr' in tx_data, "No transaction XDR returned"
```

### 6.2 Integration Tests
**File**: `tests/test_integration.py`

```python
async def test_end_to_end_deposit():
    """Test complete deposit flow on testnet"""
    # 1. Discover vaults
    vaults = await discover_high_yield_vaults(min_apy=1.0)

    # 2. Build deposit transaction
    tx = await prepare_defindex_deposit(
        vault_address=vaults[0]['address'],
        amount_xlm=1.0,
        user_address=TEST_ACCOUNT
    )

    # 3. Validate transaction format
    assert 'xdr' in tx

    # 4. (Optional) Submit transaction for full test
```

## Phase 7: Frontend Updates

### 7.1 Network Indicator
**File**: `src/components/NetworkIndicator.tsx`

```typescript
const NetworkIndicator = () => {
  const { network } = useNetwork();

  return (
    <div className="network-indicator">
      <span className={`status ${network}`}>
        {network === 'testnet' ? '🧪 Testnet' : '🌐 Mainnet'}
      </span>
      <small>Real {network} data</small>
    </div>
  );
};
```

### 7.2 Real Yield Display
**File**: `src/components/dashboard/YieldDisplay.tsx`

**Current**: Shows mock APY data
**Target**: Display real-time APY with source attribution

```typescript
const YieldDisplay = ({ vault }) => {
  return (
    <div className="yield-display">
      <div className="apy">{vault.apy.toFixed(1)}% APY</div>
      <div className="source">
        📊 Live from DeFindex API
      </div>
      <div className="tvl">
        TVL: ${formatTvl(vault.tvl)}
      </div>
    </div>
  );
};
```

## Implementation Priority

### High Priority (Week 1)
1. ✅ Get DeFindex API key
2. ✅ Verify API endpoints work with testnet
3. ✅ Replace mock data in `discover_high_yield_vaults()`
4. ✅ Update environment configuration

### Medium Priority (Week 2)
1. ✅ Implement real deposit transaction building
2. ✅ Add testnet vault discovery
3. ✅ Update frontend for real data display
4. ✅ Add error handling for API failures

### Low Priority (Week 3)
1. ✅ Create comprehensive test suite
2. ✅ Add performance monitoring
3. ✅ Implement caching for API responses
4. ✅ Add mainnet preparation (future-proofing)

## Risk Mitigation

### Technical Risks
1. **API Unavailability**: Implement graceful fallback to cached data
2. **Rate Limiting**: Add request throttling and caching
3. **Testnet Limitations**: Document what works on testnet vs mainnet
4. **Transaction Failures**: Add detailed error messages and retry logic

### Business Risks
1. **API Costs**: Monitor usage and implement caching
2. **Data Accuracy**: Validate API data against on-chain sources
3. **User Experience**: Add loading states and error boundaries

## Success Metrics

### Technical Metrics
- [ ] 100% of vault data comes from live API
- [ ] Deposit transactions use real vault contracts
- [ ] Testnet deposits succeed in >90% of cases
- [ ] API response time <2 seconds for vault queries

### User Experience Metrics
- [ ] Users see real testnet APY data
- [ ] Deposit transactions show vault-specific details
- [ ] Clear network indicators (testnet/mainnet)
- [ ] Error messages guide users to solutions

## Next Steps

1. **Immediate**: Obtain DeFindex API key and test connection
2. **Week 1**: Replace mock data with API calls
3. **Week 2**: Implement real deposit functionality
4. **Week 3**: Testing, documentation, and deployment

## Required Resources

- **DeFindex API Key**: Contact DeFindex team
- **Testnet XLM**: Use friendbot for funding
- **Testnet Tokens**: Source from testnet faucets
- **Documentation**: https://docs.defindex.io
- **Support**: DeFindex Discord/community channels

---

**Prepared by**: Claude Code AI Assistant
**Date**: 2025-11-04
**Version**: 1.0
**Target Implementation**: Next coding session
