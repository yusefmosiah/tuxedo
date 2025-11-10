# Blend Capital Yield Farming Implementation Plan

**Created:** 2025-11-09
**Status:** Research Complete - Ready for Implementation
**Target:** Autonomous AI agent yield farming via direct Blend pool interactions

---

## Executive Summary

Replace the failing DeFindex API integration with direct Blend Capital pool interactions via Soroban RPC calls. This enables autonomous yield farming operations for the AI agent without relying on external APIs.

**Key Changes:**

- ✅ Keep DeFindex API client code (mark as disabled, may come back)
- ❌ Remove all fake/fallback/mock data completely
- ✅ Create new Blend pool tools for autonomous operations
- ✅ Use existing Soroban infrastructure (`stellar_soroban.py`)
- ✅ Direct on-chain data queries for real APY/TVL

---

## 1. Current State Analysis

### 1.1 DeFindex Integration (Failing)

**What exists:**

- `backend/defindex_client.py` - API client calling `https://api.defindex.io` (DOWN)
- `backend/defindex_soroban.py` - Fallback with fake mock data (TO BE CLEANED)
- `backend/defindex_tools.py` - LangChain agent tools
- `backend/defindex_account_tools.py` - User-scoped tools with AccountManager

**Vault Addresses (REAL - Keep These):**

**Mainnet:**

```python
MAINNET_VAULTS = {
    'USDC_Blend_Fixed': 'CDB2WMKQQNVZMEBY7Q7GZ5C7E7IAFSNMZ7GGVD6WKTCEWK7XOIAVZSAP',
    'USDC_Blend_Yieldblox': 'CCSRX5E4337QMCMC3KO3RDFYI57T5NZV5XB3W3TWE4USCASKGL5URKJL',
    'EURC_Blend_Fixed': 'CC5CE6MWISDXT3MLNQ7R3FVILFVFEIH3COWGH45GJKL6BD2ZHF7F7JVI',
    'EURC_Blend_Yieldblox': 'CA33NXYN7H3EBDSA3U2FPSULGJTTL3FQRHD2ADAAPTKS3FUJOE73735A',
    'XLM_Blend_Fixed': 'CDPWNUW7UMCSVO36VAJSQHQECISPJLCVPDASKHRC5SEROAAZDUQ5DG2Z',
    'XLM_Blend_Yieldblox': 'CBDOIGFO2QOOZTWQZ7AFPH5JOUS2SBN5CTTXR665NHV6GOCM6OUGI5KP'
}
```

**Testnet (HODL Vaults):**

```python
TESTNET_VAULTS = {
    'XLM_HODL_1': 'CAHWRPKBPX4FNLXZOAD565IBSICQPL5QX37IDLGJYOPWX22WWKFWQUBA',
    'XLM_HODL_2': 'CCSPRGGUP32M23CTU7RUAGXDNOHSA6O2BS2IK4NVUP5X2JQXKTSIQJKE',
    'XLM_HODL_3': 'CBLXUUHUL7TA3LF3U5G6ZTU7EACBBOSJLR4AYOM5YJKJ4APZ7O547R5T',
    'XLM_HODL_4': 'CCGKL6U2DHSNFJ3NU4UPRUKYE2EUGYR4ZFZDYA7KDJLP3TKSPHD5C4UP'
}
```

### 1.2 Blend Capital Infrastructure (Working)

**Official Testnet Contracts** (Source: https://github.com/blend-capital/blend-utils/blob/main/testnet.contracts.json):

```python
BLEND_TESTNET_CONTRACTS = {
    # Core V2 Infrastructure
    'poolFactory': 'CDSMKKCWEAYQW4DAUSH3XGRMIVIJB44TZ3UA5YCRHT6MP4LWEWR4GYV6',
    'backstop': 'CBHWKF4RHIKOKSURAKXSJRIIA7RJAMJH4VHRVPYGUF4AJ5L544LYZ35X',
    'emitter': 'CCS5ACKIDOIVW2QMWBF7H3ZM4ZIH2Q2NP7I3P3GH7YXXGN7I3WND3D6G',

    # Tokens
    'xlm': 'CDLZFC3SYJYDZT7K67VZ75HPJVIEUVNIXF47ZG2FB2RMQQVU2HHGCYSC',
    'blnd': 'CB22KRA3YZVCNCQI64JQ5WE7UY2VAV7WFLK6A2JN3HEX56T2EDAFO7QF',
    'usdc': 'CAQCFVLOBK5GIULPNZRGATJJMIZL5BSP7X5YJVMCPTUEPFM4AVSRCJU',  # ✅ Matches Discord
    'weth': 'CAZAQB3D7KSLSNOSQKYD2V4JP5V2Y3B4RDJZRLBFCCIXDCTE3WHSY3UE',
    'wbtc': 'CAP5AMC2OHNVREO66DFIN6DHJMPOBAJ2KCDDIMFBR7WWJH5RZBFM3UEI',

    # Pools
    'comet': 'CCQ74HNBMLYICEFUGNLM23QQJU7BKZS7CXC7OAOX4IHRT3LDINZ4V3AF',
    'cometFactory': 'CCVR5U7CVFQNXVT74PGFSIK23HJMGEWSAAR5NZXSVTNGMFSRUIEHIXHN',

    # Utilities
    'oracleMock': 'CBKKSSMTHJJTQWSIOBJQAIGR42NSY43ZBKKXWF445PE4OLOTOGPOWWF4',
}
```

**Current Frontend Integration:**

- `src/contracts/blend.ts` - ✅ CONFIRMED TESTNET (comment on line 10)
- `src/hooks/useBlendPools.ts` - Working pool discovery via Backstop
- Uses `@blend-capital/blend-sdk` v3.2.1
- Successfully loads pools and reserve data

### 1.3 Existing Soroban Infrastructure (Ready to Use)

**File:** `backend/stellar_soroban.py`

Already has everything needed:

- ✅ `invoke` action for contract execution
- ✅ `simulate` action for testing without fees
- ✅ `get_data` action for reading contract storage
- ✅ `get_events` action for querying contract events
- ✅ Parameter parsing for all SCVal types (primitives + complex)
- ✅ AccountManager integration with user isolation
- ✅ Complete transaction flow: Build → Simulate → Prepare → Sign → Submit → Poll
- ✅ Async-first with proper error handling

**Network Configuration:**

```python
TESTNET_RPC = "https://soroban-testnet.stellar.org"
TESTNET_PASSPHRASE = "Test SDF Network ; September 2015"
```

---

## 2. Blend Protocol Technical Architecture

### 2.1 Core Concept: Unified `submit()` Function

**Critical Discovery:** Blend doesn't have separate `deposit()` or `withdraw()` functions. All operations use a unified interface:

```rust
// Pool contract signature
submit(
    from: Address,           // User's address
    spender: Address,        // Same as user for direct ops
    to: Address,             // Same as user for direct ops
    requests: Vec<Request>   // Array of operations
) -> Positions
```

### 2.2 Request Types

**Enum values from Blend contracts:**

```rust
0 = SupplyCollateral      // Supply assets as collateral (can borrow against)
1 = WithdrawCollateral    // Withdraw collateral
2 = Supply                // Supply without collateral designation
3 = Withdraw              // Withdraw supplied assets
4 = Borrow                // Borrow assets
5 = Repay                 // Repay borrowed assets
6 = FillUserLiquidationAuction
7 = FillBadDebtAuction
8 = FillInterestAuction
```

**For Yield Farming, we primarily need:**

- `SupplyCollateral` (0) - To earn yield
- `WithdrawCollateral` (1) - To remove funds

### 2.3 Request Structure

Each request in the `requests` vector contains:

```typescript
{
    amount: Int128,           // Scaled to asset decimals (typically 7)
    request_type: u32,        // Enum value (0-8)
    address: Address          // Asset contract ID
}
```

**Example for TypeScript SDK:**

```typescript
const submitArgs = {
  from: userAddress,
  spender: userAddress,
  to: userAddress,
  requests: [
    {
      amount: scaleInputToBigInt(amount, decimals), // e.g., 100 XLM → 1000000000
      request_type: RequestType.SupplyCollateral, // = 0
      address: assetContractId, // e.g., XLM token address
    },
  ],
};
```

### 2.4 Reserve Data Structure

Each pool has reserves with this data (accessible via `get_reserve(asset: Address)`):

```rust
Reserve {
    config: ReserveConfig {
        decimals: u32,
        c_factor: u32,      // Collateral factor
        l_factor: u32,      // Liability factor
        util: u32,          // Target utilization
        max_util: u32,      // Max utilization
        r_base: u32,        // Base rate
        r_one: u32,         // Rate at target util
        r_two: u32,         // Rate at max util
        r_three: u32,       // Rate above max util
        reactivity: u32,
        index: u32,
    },
    data: ReserveData {
        b_rate: i128,       // Borrow rate (use for APY calculation)
        d_rate: i128,       // Supply rate (use for APY calculation)
        b_supply: i128,     // Total supplied (scaled)
        d_supply: i128,     // Total borrowed (scaled)
        ir_mod: u32,        // Interest rate modifier
        last_time: i128,    // Last update timestamp
        backstop_credit: i128,
    }
}
```

**APY Calculation from Reserve Data:**

```python
supply_rate = reserve_data['b_rate'] / 1e7  # Adjust for decimals
supply_apr = supply_rate  # Annual rate
supply_apy = (1 + supply_apr / 365) ** 365 - 1
apy_percentage = supply_apy * 100
```

---

## 3. Implementation Plan

### Phase 1: Clean Up DeFindex Code

**Goal:** Remove all fake/mock/fallback data while keeping API client structure

#### 1.1 Mark DeFindex as Disabled

**File:** `backend/defindex_client.py`

Add at the top:

```python
"""
DeFindex API Client

⚠️ CURRENTLY DISABLED: DeFindex API is down (as of 2025-11-09)
This code is preserved in case the API comes back online.
For yield farming, use blend_pool_tools.py instead.
"""

DEFINDEX_ENABLED = False  # Set to True if API comes back
```

#### 1.2 Remove Fake Data from defindex_soroban.py

**File:** `backend/defindex_soroban.py`

**Lines to remove/modify:**

- Remove any `REALISTIC_APY_DATA` dictionaries (already removed on line 36)
- Remove `enhanced_mock` data generation
- Remove fallback APY calculations
- Keep only MAINNET_VAULTS and TESTNET_VAULTS dictionaries

**Function changes:**

```python
async def get_available_vaults(self, min_apy: float = 15.0) -> List[Dict]:
    """Get available vaults - REQUIRES API"""
    if not self.api_client:
        raise ValueError(
            "DeFindex API is currently unavailable. "
            "Please use Blend pools for yield farming instead. "
            "See blend_pool_tools.py"
        )

    # Only API data, no fallback
    vaults_data = []
    # ... rest of API-only logic
```

#### 1.3 Update Agent Tools

**File:** `backend/defindex_tools.py`

Add warning at top:

```python
"""
⚠️ DEPRECATED: DeFindex API is down
Use blend_pool_tools.py for yield farming instead
"""
```

Comment out tool registration in agent until API is back.

---

### Phase 2: Create Blend Pool Tools

**New File:** `backend/blend_pool_tools.py`

This will contain all autonomous yield farming operations for the AI agent.

#### 2.1 Pool Discovery

```python
async def blend_discover_pools(
    network: str = "testnet",
    soroban_server: SorobanServerAsync = None,
    account_manager: AccountManager = None,
    user_id: str = "system"  # Discovery doesn't need user auth
) -> List[Dict[str, Any]]:
    """
    Discover all active Blend pools from Backstop contract.

    Returns list of pools with basic info:
    [
        {
            'pool_address': 'CCQ74...',
            'name': 'Comet Pool',
            'total_reserves': 5,
            'status': 'active'
        }
    ]
    """

    backstop_address = (
        "CBHWKF4RHIKOKSURAKXSJRIIA7RJAMJH4VHRVPYGUF4AJ5L544LYZ35X"  # Testnet
        if network == "testnet" else
        "CAQQR5SWBXKIGZKPBZDH3KM5GQ5GUTPKB7JAFCINLZBC5WXPJKRG3IM7"  # Mainnet
    )

    # Query Backstop config to get reward zone (active pools)
    result = await soroban_operations(
        action="get_data",
        user_id=user_id,
        soroban_server=soroban_server,
        account_manager=account_manager,
        contract_id=backstop_address,
        key="Config",
        durability="persistent"
    )

    if not result.get('success'):
        return []

    # Parse config.rewardZone array (list of pool addresses)
    config = result['value']
    pool_addresses = config.get('rewardZone', [])

    # Load basic info for each pool
    pools = []
    for pool_addr in pool_addresses:
        pool_info = await _load_pool_basic_info(pool_addr, soroban_server, account_manager, user_id)
        if pool_info:
            pools.append(pool_info)

    return pools
```

#### 2.2 Get Reserve APY (Real Data)

```python
async def blend_get_reserve_apy(
    pool_address: str,
    asset_address: str,
    user_id: str,
    soroban_server: SorobanServerAsync,
    account_manager: AccountManager,
    network: str = "testnet"
) -> Dict[str, Any]:
    """
    Get real APY data for a reserve in a pool by querying on-chain data.

    Returns:
    {
        'asset_address': 'CAQCF...',
        'asset_symbol': 'USDC',
        'supply_apy': 12.5,         # Percentage
        'borrow_apy': 15.2,
        'total_supplied': 1000000,   # Scaled units
        'total_borrowed': 750000,
        'utilization': 0.75,
        'available_liquidity': 250000
    }
    """

    # Build parameters for get_reserve(asset: Address)
    parameters = json.dumps([
        {"type": "address", "value": asset_address}
    ])

    # Use simulate (read-only, no fees)
    # We need a temporary account for simulation context
    temp_account_id = await _get_or_create_temp_account(user_id, account_manager)

    result = await soroban_operations(
        action="simulate",
        user_id=user_id,
        soroban_server=soroban_server,
        account_manager=account_manager,
        contract_id=pool_address,
        function_name="get_reserve",
        parameters=parameters,
        account_id=temp_account_id,
        network_passphrase="Test SDF Network ; September 2015" if network == "testnet" else "Public Global Stellar Network ; September 2015"
    )

    if not result.get('success'):
        raise ValueError(f"Failed to get reserve data: {result.get('error')}")

    reserve = result['result']

    # Extract reserve data
    reserve_data = reserve['data']
    reserve_config = reserve['config']

    # Calculate APY from rates
    # b_rate is supply rate (what suppliers earn)
    supply_rate = reserve_data['b_rate'] / 1e7  # Stellar uses 7 decimals
    supply_apr = supply_rate
    supply_apy = ((1 + supply_apr / 365) ** 365 - 1) * 100

    # d_rate is borrow rate
    borrow_rate = reserve_data['d_rate'] / 1e7
    borrow_apr = borrow_rate
    borrow_apy = ((1 + borrow_apr / 365) ** 365 - 1) * 100

    # Calculate metrics
    total_supplied = reserve_data['b_supply']
    total_borrowed = reserve_data['d_supply']
    available = total_supplied - total_borrowed
    utilization = total_borrowed / total_supplied if total_supplied > 0 else 0

    # Get asset symbol from metadata (if available)
    asset_symbol = await _get_asset_symbol(asset_address, soroban_server, account_manager, user_id)

    return {
        'asset_address': asset_address,
        'asset_symbol': asset_symbol,
        'supply_apy': round(supply_apy, 2),
        'borrow_apy': round(borrow_apy, 2),
        'total_supplied': total_supplied,
        'total_borrowed': total_borrowed,
        'utilization': round(utilization, 4),
        'available_liquidity': available,
        'data_source': 'on_chain'
    }
```

#### 2.3 Supply Collateral (Deposit for Yield)

```python
async def blend_supply_collateral(
    pool_address: str,
    asset_address: str,
    amount: float,
    user_id: str,
    account_id: str,
    account_manager: AccountManager,
    soroban_server: SorobanServerAsync,
    network: str = "testnet"
) -> Dict[str, Any]:
    """
    Supply assets to a Blend pool to earn yield (autonomous operation).

    Args:
        pool_address: Pool contract ID (e.g., Comet pool)
        asset_address: Asset to supply (e.g., USDC, XLM)
        amount: Amount in decimal units (e.g., 100.5)
        user_id: User identifier for permission checks
        account_id: Account ID from AccountManager
        account_manager: AccountManager instance
        soroban_server: SorobanServerAsync instance
        network: "testnet" or "mainnet"

    Returns:
    {
        'success': True,
        'hash': 'abc123...',
        'amount_supplied': 100.5,
        'asset_symbol': 'USDC',
        'pool': 'Comet Pool',
        'message': 'Successfully supplied 100.5 USDC to Comet Pool'
    }
    """

    # Get account details for user address
    account_data = account_manager._get_account_by_id(account_id)
    user_address = account_data['public_key']

    # Scale amount to asset decimals (Stellar uses 7)
    amount_scaled = int(amount * 10_000_000)

    # Build Request struct as a map
    # Request { amount: Int128, request_type: u32, address: Address }
    request_map = {
        "amount": {"type": "int128", "value": amount_scaled},
        "request_type": {"type": "uint32", "value": 0},  # SupplyCollateral = 0
        "address": {"type": "address", "value": asset_address}
    }

    # Build parameters for submit(from, spender, to, requests)
    parameters = json.dumps([
        {"type": "address", "value": user_address},  # from
        {"type": "address", "value": user_address},  # spender
        {"type": "address", "value": user_address},  # to
        {
            "type": "vec",
            "value": [
                {"type": "map", "value": request_map}
            ]
        }
    ])

    # Execute via invoke action
    result = await soroban_operations(
        action="invoke",
        user_id=user_id,
        soroban_server=soroban_server,
        account_manager=account_manager,
        contract_id=pool_address,
        function_name="submit",
        parameters=parameters,
        account_id=account_id,
        auto_sign=True,
        network_passphrase="Test SDF Network ; September 2015" if network == "testnet" else "Public Global Stellar Network ; September 2015"
    )

    if not result.get('success'):
        return {
            'success': False,
            'error': result.get('error', 'Unknown error'),
            'message': f"Failed to supply {amount} to pool"
        }

    # Get asset symbol for user-friendly message
    asset_symbol = await _get_asset_symbol(asset_address, soroban_server, account_manager, user_id)
    pool_name = await _get_pool_name(pool_address, soroban_server, account_manager, user_id)

    return {
        'success': True,
        'hash': result['hash'],
        'ledger': result['ledger'],
        'amount_supplied': amount,
        'asset_symbol': asset_symbol,
        'pool': pool_name,
        'message': f"✅ Successfully supplied {amount} {asset_symbol} to {pool_name}. Tx: {result['hash']}"
    }
```

#### 2.4 Withdraw Collateral

```python
async def blend_withdraw_collateral(
    pool_address: str,
    asset_address: str,
    amount: float,
    user_id: str,
    account_id: str,
    account_manager: AccountManager,
    soroban_server: SorobanServerAsync,
    network: str = "testnet"
) -> Dict[str, Any]:
    """
    Withdraw supplied assets from a Blend pool (autonomous operation).

    Same structure as supply but with:
    - request_type: 1 (WithdrawCollateral)
    """

    # Same implementation as blend_supply_collateral but with request_type = 1
    # ... (code similar to above)

    request_map = {
        "amount": {"type": "int128", "value": amount_scaled},
        "request_type": {"type": "uint32", "value": 1},  # WithdrawCollateral = 1
        "address": {"type": "address", "value": asset_address}
    }

    # ... rest of implementation
```

#### 2.5 Get User Positions

```python
async def blend_get_my_positions(
    pool_address: str,
    user_id: str,
    account_id: str,
    account_manager: AccountManager,
    soroban_server: SorobanServerAsync,
    network: str = "testnet"
) -> Dict[str, Any]:
    """
    Check user's current positions in a Blend pool.

    Returns:
    {
        'pool': 'Comet Pool',
        'positions': {
            'USDC': {
                'supplied': 100.5,
                'borrowed': 0,
                'collateral': True
            },
            'XLM': {
                'supplied': 1000,
                'borrowed': 50,
                'collateral': True
            }
        }
    }
    """

    # Get user address
    account_data = account_manager._get_account_by_id(account_id)
    user_address = account_data['public_key']

    # Call get_positions(address: Address)
    parameters = json.dumps([
        {"type": "address", "value": user_address}
    ])

    result = await soroban_operations(
        action="simulate",  # Read-only
        user_id=user_id,
        soroban_server=soroban_server,
        account_manager=account_manager,
        contract_id=pool_address,
        function_name="get_positions",
        parameters=parameters,
        account_id=account_id,
        network_passphrase="Test SDF Network ; September 2015" if network == "testnet" else "Public Global Stellar Network ; September 2015"
    )

    if not result.get('success'):
        return {'error': result.get('error')}

    positions_data = result['result']

    # Parse positions (structure depends on Blend contract return format)
    # Typically: { liabilities: Map<Address, i128>, collateral: Map<Address, i128>, supply: Map<Address, i128> }

    formatted_positions = {}
    # ... parse and format positions data

    return {
        'pool': await _get_pool_name(pool_address, soroban_server, account_manager, user_id),
        'positions': formatted_positions,
        'data_source': 'on_chain'
    }
```

#### 2.6 Find Best Yield Opportunities

```python
async def blend_find_best_yield(
    asset_symbol: str,  # e.g., "USDC", "XLM"
    min_apy: float = 0.0,
    user_id: str,
    soroban_server: SorobanServerAsync,
    account_manager: AccountManager,
    network: str = "testnet"
) -> List[Dict[str, Any]]:
    """
    Find best yield opportunities across all Blend pools for a given asset.

    Returns sorted list by APY (highest first):
    [
        {
            'pool': 'Comet Pool',
            'pool_address': 'CCQ74...',
            'asset': 'USDC',
            'apy': 12.5,
            'available_liquidity': 500000,
            'utilization': 0.75
        }
    ]
    """

    # 1. Discover all pools
    pools = await blend_discover_pools(network, soroban_server, account_manager, user_id)

    # 2. For each pool, get reserves and find the asset
    opportunities = []

    for pool in pools:
        pool_address = pool['pool_address']

        # Get reserve list from pool
        reserves = await _get_pool_reserves(pool_address, soroban_server, account_manager, user_id)

        # Find the asset in reserves
        for reserve in reserves:
            if reserve['symbol'] == asset_symbol:
                # Get APY data
                apy_data = await blend_get_reserve_apy(
                    pool_address,
                    reserve['address'],
                    user_id,
                    soroban_server,
                    account_manager,
                    network
                )

                if apy_data['supply_apy'] >= min_apy:
                    opportunities.append({
                        'pool': pool['name'],
                        'pool_address': pool_address,
                        'asset': asset_symbol,
                        'apy': apy_data['supply_apy'],
                        'available_liquidity': apy_data['available_liquidity'] / 1e7,
                        'utilization': apy_data['utilization']
                    })

    # Sort by APY descending
    opportunities.sort(key=lambda x: x['apy'], reverse=True)

    return opportunities
```

---

### Phase 3: Agent Integration

**File:** `backend/agent/tool_factory.py`

#### 3.1 Create Blend Tools for Agent

```python
def create_user_tools(user_id: str, account_manager: AccountManager) -> List[StructuredTool]:
    """Create user-scoped tools with AccountManager integration"""

    tools = []

    # Initialize Soroban server
    soroban_server = SorobanServerAsync("https://soroban-testnet.stellar.org")

    # Blend Pool Tools
    tools.append(StructuredTool(
        name="blend_find_best_yield",
        description=(
            "Find the best yield opportunities for an asset across all Blend pools. "
            "Input: asset symbol (e.g., 'USDC', 'XLM'). "
            "Returns sorted list of pools by APY with real on-chain data."
        ),
        func=lambda asset: asyncio.run(blend_find_best_yield(
            asset_symbol=asset,
            min_apy=0.0,
            user_id=user_id,
            soroban_server=soroban_server,
            account_manager=account_manager,
            network="testnet"
        ))
    ))

    tools.append(StructuredTool(
        name="blend_supply_to_pool",
        description=(
            "Supply assets to a Blend pool to earn yield (autonomous operation). "
            "Inputs: pool_address, asset_address, amount, account_id. "
            "Returns transaction hash and confirmation. "
            "Use blend_find_best_yield first to find the best pool."
        ),
        func=lambda pool, asset, amount, account_id: asyncio.run(blend_supply_collateral(
            pool_address=pool,
            asset_address=asset,
            amount=amount,
            user_id=user_id,
            account_id=account_id,
            account_manager=account_manager,
            soroban_server=soroban_server,
            network="testnet"
        ))
    ))

    tools.append(StructuredTool(
        name="blend_withdraw_from_pool",
        description=(
            "Withdraw supplied assets from a Blend pool. "
            "Inputs: pool_address, asset_address, amount, account_id. "
            "Returns transaction hash and confirmation."
        ),
        func=lambda pool, asset, amount, account_id: asyncio.run(blend_withdraw_collateral(
            pool_address=pool,
            asset_address=asset,
            amount=amount,
            user_id=user_id,
            account_id=account_id,
            account_manager=account_manager,
            soroban_server=soroban_server,
            network="testnet"
        ))
    ))

    tools.append(StructuredTool(
        name="blend_check_my_positions",
        description=(
            "Check your current positions in a Blend pool (supplied, borrowed, collateral status). "
            "Inputs: pool_address, account_id. "
            "Returns detailed position information."
        ),
        func=lambda pool, account_id: asyncio.run(blend_get_my_positions(
            pool_address=pool,
            user_id=user_id,
            account_id=account_id,
            account_manager=account_manager,
            soroban_server=soroban_server,
            network="testnet"
        ))
    ))

    return tools
```

---

### Phase 4: Testing & Validation

#### 4.1 Unit Tests

**File:** `backend/tests/test_blend_pool_tools.py`

```python
import pytest
from blend_pool_tools import blend_discover_pools, blend_get_reserve_apy, blend_supply_collateral

@pytest.mark.asyncio
async def test_discover_pools():
    """Test pool discovery from Backstop"""
    pools = await blend_discover_pools(network="testnet")
    assert len(pools) > 0
    assert 'pool_address' in pools[0]
    assert 'name' in pools[0]

@pytest.mark.asyncio
async def test_get_reserve_apy():
    """Test fetching real APY data from a pool"""
    # Use Comet pool and USDC
    apy_data = await blend_get_reserve_apy(
        pool_address="CCQ74HNBMLYICEFUGNLM23QQJU7BKZS7CXC7OAOX4IHRT3LDINZ4V3AF",
        asset_address="CAQCFVLOBK5GIULPNZRGATJJMIZL5BSP7X5YJVMCPTUEPFM4AVSRCJU",
        user_id="test_user",
        # ... other params
    )
    assert 'supply_apy' in apy_data
    assert apy_data['supply_apy'] >= 0
    assert apy_data['data_source'] == 'on_chain'

# Add tests for supply, withdraw, positions
```

#### 4.2 Integration Test

**File:** `backend/test_blend_agent.py`

```python
#!/usr/bin/env python3
"""
Test Blend yield farming with AI agent
"""

async def test_full_yield_farming_flow():
    """Test complete flow: discover → supply → check positions → withdraw"""

    # 1. Find best yield
    print("🔍 Finding best yield for USDC...")
    opportunities = await blend_find_best_yield("USDC", user_id="test", ...)
    print(f"Found {len(opportunities)} opportunities")
    print(f"Best APY: {opportunities[0]['apy']}%")

    # 2. Supply to best pool
    print("\n💰 Supplying 10 USDC to best pool...")
    best_pool = opportunities[0]
    result = await blend_supply_collateral(
        pool_address=best_pool['pool_address'],
        asset_address="CAQCFVLOBK5GIULPNZRGATJJMIZL5BSP7X5YJVMCPTUEPFM4AVSRCJU",
        amount=10.0,
        # ... params
    )
    print(f"✅ {result['message']}")

    # 3. Check positions
    print("\n📊 Checking positions...")
    positions = await blend_get_my_positions(best_pool['pool_address'], ...)
    print(f"Positions: {positions}")

    # 4. Withdraw
    print("\n🏧 Withdrawing 5 USDC...")
    withdraw_result = await blend_withdraw_collateral(
        pool_address=best_pool['pool_address'],
        amount=5.0,
        # ... params
    )
    print(f"✅ {withdraw_result['message']}")
```

---

## 4. Implementation Checklist

### 4.1 Phase 1: Cleanup (1-2 hours)

- [ ] Add `DEFINDEX_ENABLED = False` flag to `defindex_client.py`
- [ ] Remove all fake/mock data from `defindex_soroban.py`
- [ ] Update `get_available_vaults()` to raise error if API unavailable
- [ ] Add deprecation warnings to `defindex_tools.py`
- [ ] Comment out DeFindex tool registration in agent

### 4.2 Phase 2: Blend Tools (4-6 hours)

- [ ] Create `backend/blend_pool_tools.py`
- [ ] Implement `blend_discover_pools()`
- [ ] Implement `blend_get_reserve_apy()`
- [ ] Implement `blend_supply_collateral()`
- [ ] Implement `blend_withdraw_collateral()`
- [ ] Implement `blend_get_my_positions()`
- [ ] Implement `blend_find_best_yield()`
- [ ] Add helper functions (`_get_asset_symbol`, `_get_pool_name`, etc.)

### 4.3 Phase 3: Agent Integration (2-3 hours)

- [ ] Update `tool_factory.py` with Blend tools
- [ ] Add proper tool descriptions for LangChain
- [ ] Test tool invocation from agent
- [ ] Update agent prompts to understand Blend operations

### 4.4 Phase 4: Testing (2-3 hours)

- [ ] Write unit tests for each function
- [ ] Create integration test script
- [ ] Test on testnet with real pools
- [ ] Verify APY calculations match frontend
- [ ] Test full flow: discover → supply → check → withdraw

### 4.5 Phase 5: Documentation (1 hour)

- [ ] Update `CLAUDE.md` with Blend integration details
- [ ] Add examples to README
- [ ] Document testnet vs mainnet differences
- [ ] Create troubleshooting guide

---

## 5. Example Agent Interactions

### Example 1: Find Best Yield

```
User: "Help me earn yield on my 100 USDC"

Agent reasoning:
1. Calls blend_find_best_yield("USDC")
2. Discovers Comet Pool offers 12.5% APY
3. Verifies sufficient liquidity available
4. Presents options to user

Agent: "I found the best yield opportunity:
- Comet Pool: 12.5% APY on USDC
- Available liquidity: 500,000 USDC
- Current utilization: 75%

Would you like me to supply your 100 USDC to this pool?"

User: "Yes, do it"

Agent:
1. Calls blend_supply_collateral(pool="CCQ74...", asset="CAQCF...", amount=100)
2. Transaction succeeds

Agent: "✅ Successfully supplied 100 USDC to Comet Pool earning 12.5% APY.
Transaction hash: abc123...
You'll start earning interest immediately!"
```

### Example 2: Check Positions

```
User: "What's in my yield farming positions?"

Agent:
1. Discovers all pools via blend_discover_pools()
2. For each pool, calls blend_get_my_positions()
3. Aggregates results

Agent: "Your Blend positions:

Comet Pool:
- Supplied: 100 USDC (earning 12.5% APY)
- Supplied: 500 XLM (earning 8.2% APY)
- Borrowed: 0

Total estimated yearly earnings: $15.63"
```

### Example 3: Rebalance

```
User: "Move my funds to the highest yield pool"

Agent:
1. Gets current positions
2. Calls blend_find_best_yield() for each asset
3. Compares current APY vs best available
4. Executes withdrawals and deposits

Agent: "I found a better opportunity:
- Current: Comet Pool USDC at 12.5% APY
- Better: YieldBlox Pool USDC at 15.8% APY

Executing rebalance...
✅ Withdrawn 100 USDC from Comet Pool
✅ Supplied 100 USDC to YieldBlox Pool
Your new APY: 15.8% (+3.3%)"
```

---

## 6. Technical Considerations

### 6.1 Testnet vs Mainnet

**Current Focus: Testnet Only**

Differences:

- Different contract addresses
- Different network passphrase
- Different RPC URL

**Config structure:**

```python
NETWORK_CONFIG = {
    'testnet': {
        'rpc_url': 'https://soroban-testnet.stellar.org',
        'passphrase': 'Test SDF Network ; September 2015',
        'contracts': BLEND_TESTNET_CONTRACTS,
    },
    'mainnet': {
        'rpc_url': 'https://mainnet.stellar.expert/explorer/rpc',
        'passphrase': 'Public Global Stellar Network ; September 2015',
        'contracts': BLEND_MAINNET_CONTRACTS,
    }
}
```

### 6.2 Amount Scaling

Stellar assets use **7 decimals**:

```python
# User input: 100.5 USDC
amount_stroops = int(100.5 * 10_000_000)  # = 1005000000

# From contract: 1005000000 stroops
amount_usdc = 1005000000 / 10_000_000  # = 100.5
```

### 6.3 Error Handling

Common errors and solutions:

| Error                 | Cause                                 | Solution                            |
| --------------------- | ------------------------------------- | ----------------------------------- |
| `MissingValue`        | Wrong contract address for network    | Verify testnet vs mainnet           |
| `InsufficientBalance` | Not enough tokens                     | Check balance first                 |
| `PermissionDenied`    | Wrong user_id                         | Verify AccountManager ownership     |
| `PoolPaused`          | Pool is frozen                        | Check pool status before operations |
| `ExceedsAvailable`    | Trying to withdraw more than supplied | Query positions first               |

### 6.4 Rate Limiting

RPC calls have limits:

- Simulate: No limits (doesn't hit chain)
- Invoke: Transaction fees apply
- Query: Reasonable rate limits

**Best practices:**

- Use `simulate` for read-only operations
- Batch queries when possible
- Cache pool data (refresh every 5 minutes)

### 6.5 Security Considerations

- ✅ User isolation via `user_id` checks
- ✅ AccountManager ownership verification before signing
- ✅ Read-only operations don't need private keys
- ✅ Write operations require explicit account_id
- ⚠️ Always validate amounts (prevent dust attacks)
- ⚠️ Check pool status before operations
- ⚠️ Verify asset addresses match expected tokens

---

## 7. Comparison: DeFindex API vs Direct Blend

| Aspect                  | DeFindex API            | Direct Blend               |
| ----------------------- | ----------------------- | -------------------------- |
| **Availability**        | ❌ Down                 | ✅ Always available        |
| **Data Source**         | External API            | ✅ On-chain contracts      |
| **Latency**             | API roundtrip           | ✅ Direct RPC (faster)     |
| **Dependencies**        | API key, network        | ✅ Just Soroban RPC        |
| **APY Data**            | Pre-calculated          | ✅ Real-time from reserves |
| **Reliability**         | Single point of failure | ✅ Decentralized           |
| **Autonomy**            | API returns XDR to sign | ✅ Full autonomous control |
| **Testnet Support**     | Limited                 | ✅ Full support            |
| **Transaction Control** | External                | ✅ Complete control        |

---

## 8. Success Metrics

After implementation, validate:

1. **Functional:**
   - ✅ Agent can discover all active Blend pools
   - ✅ Agent can query real-time APY from on-chain data
   - ✅ Agent can autonomously supply to pools
   - ✅ Agent can withdraw from pools
   - ✅ Agent can check user positions

2. **Performance:**
   - Pool discovery: < 5 seconds
   - APY query: < 2 seconds per pool
   - Supply transaction: < 10 seconds (including confirmation)
   - Withdraw transaction: < 10 seconds

3. **Accuracy:**
   - APY calculations match frontend display (within 0.1%)
   - Position data matches blockchain state
   - No fake/mock data in responses

4. **User Experience:**
   - Agent provides clear, actionable information
   - Errors are user-friendly
   - Confirmations include transaction hashes
   - Agent can explain why it chose specific pools

---

## 9. Future Enhancements

**Post-MVP:**

1. **Mainnet Support**
   - Add mainnet contract addresses
   - Separate testnet/mainnet configs
   - Add network switcher in agent

2. **Advanced Strategies**
   - Auto-rebalancing based on APY changes
   - Risk-adjusted yield (consider utilization)
   - Multi-pool diversification

3. **Analytics**
   - Track user's yield farming history
   - Calculate total earnings over time
   - Compare performance across pools

4. **Notifications**
   - Alert when better yield opportunities appear
   - Warn about pool status changes
   - Notify on significant utilization changes

5. **Borrow Operations**
   - Implement `Borrow` and `Repay` request types
   - Calculate health factor
   - Liquidation risk warnings

---

## 10. References

**Official Documentation:**

- Blend v2 Docs: https://docs.blend.capital/
- Testnet Contracts: https://github.com/blend-capital/blend-utils/blob/main/testnet.contracts.json
- Blend SDK: https://www.npmjs.com/package/@blend-capital/blend-sdk
- Soroban RPC: https://developers.stellar.org/docs/data/rpc

**Testnet Resources:**

- Blend Testnet UI: https://testnet.blend.capital/
- Friendbot (testnet XLM): https://friendbot.stellar.org
- Testnet RPC: https://soroban-testnet.stellar.org
- Stellar Expert (testnet): https://stellar.expert/explorer/testnet

**Codebase References:**

- Frontend pool loading: `src/hooks/useBlendPools.ts`
- Soroban operations: `backend/stellar_soroban.py`
- Account management: `backend/account_manager.py`

---

## 11. Implementation Order

**Recommended sequence:**

1. **Day 1: Cleanup & Foundation**
   - Morning: Clean DeFindex code
   - Afternoon: Create blend_pool_tools.py skeleton

2. **Day 2: Core Functions**
   - Morning: Implement discovery & APY queries
   - Afternoon: Implement supply/withdraw

3. **Day 3: Integration & Testing**
   - Morning: Agent tool integration
   - Afternoon: Write tests, validate on testnet

4. **Day 4: Polish & Documentation**
   - Morning: Fix bugs, improve error messages
   - Afternoon: Documentation, examples

**Total estimated time: 3-4 days**

---

## Appendix A: SCVal Parameter Examples

### Example 1: Simple SupplyCollateral Request

```python
# User wants to supply 100 USDC
parameters = [
    {"type": "address", "value": "GUSER..."},  # from (user address)
    {"type": "address", "value": "GUSER..."},  # spender
    {"type": "address", "value": "GUSER..."},  # to
    {
        "type": "vec",
        "value": [
            {
                "type": "map",
                "value": {
                    "amount": {"type": "int128", "value": 1000000000},  # 100 USDC scaled
                    "request_type": {"type": "uint32", "value": 0},      # SupplyCollateral
                    "address": {"type": "address", "value": "CAQCF..."}  # USDC token
                }
            }
        ]
    }
]
```

### Example 2: Multiple Requests (Supply + Withdraw)

```python
parameters = [
    {"type": "address", "value": "GUSER..."},
    {"type": "address", "value": "GUSER..."},
    {"type": "address", "value": "GUSER..."},
    {
        "type": "vec",
        "value": [
            # Request 1: Supply USDC
            {
                "type": "map",
                "value": {
                    "amount": {"type": "int128", "value": 1000000000},
                    "request_type": {"type": "uint32", "value": 0},
                    "address": {"type": "address", "value": "CAQCF..."}
                }
            },
            # Request 2: Withdraw XLM
            {
                "type": "map",
                "value": {
                    "amount": {"type": "int128", "value": 500000000},
                    "request_type": {"type": "uint32", "value": 1},
                    "address": {"type": "address", "value": "CDLZF..."}
                }
            }
        ]
    }
]
```

---

**END OF IMPLEMENTATION PLAN**
