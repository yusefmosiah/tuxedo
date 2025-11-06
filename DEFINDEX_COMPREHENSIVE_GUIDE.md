# DeFindex Comprehensive Guide - Tuxedo AI Agent

**Last Updated**: 2025-11-05
**Version**: 1.0
**Network**: Stellar Testnet
**Status**: 🟢 Production Ready for Educational Use

## 📋 Table of Contents

1. [Overview](#overview)
2. [Deployed Infrastructure](#deployed-infrastructure)
3. [AI Agent Tools](#ai-agent-tools)
4. [Integration Patterns](#integration-patterns)
5. [API Reference](#api-reference)
6. [Usage Examples](#usage-examples)
7. [Troubleshooting](#troubleshooting)
8. [Development Notes](#development-notes)

---

## 🎯 Overview

The Tuxedo AI Agent now provides **fully autonomous** DeFindex vault operations on Stellar testnet. This guide covers all deployed contracts, tool implementations, and integration patterns for developers and users.

### Key Features

- ✅ **Autonomous Transactions**: No manual wallet intervention required
- ✅ **Smart Account Management**: Agent automatically uses existing funded accounts
- ✅ **Real Vault Integration**: Works with actual deployed testnet contracts
- ✅ **Complete Tool Suite**: Discovery, details, deposits, and withdrawals
- ✅ **Error Handling**: Graceful fallbacks and user feedback
- ✅ **Educational Focus**: Safe testnet environment for learning

---

## 🏗️ Deployed Infrastructure

### Testnet Vault Contracts

All vaults are **LIVE** on Stellar testnet and ready for autonomous operations.

| Vault          | Address                                                    | Type           | APY  | TVL | Status    | Strategy |
| -------------- | ---------------------------------------------------------- | -------------- | ---- | --- | --------- | -------- |
| **XLM_HODL_1** | `CAHWRPKBPX4FNLXZOAD565IBSICQPL5QX37IDLGJYOPWX22WWKFWQUBA` | Volatile (XLM) | 0.0% | $0  | ✅ Active | HODL     |
| **XLM_HODL_2** | `CCSPRGGUP32M23CTU7RUAGXDNOHSA6O2BS2IK4NVUP5X2JQXKTSIQJKE` | Volatile (XLM) | 0.0% | $0  | ✅ Active | HODL     |
| **XLM_HODL_3** | `CBLXUUHUL7TA3LF3U5G6ZTU7EACBBOSJLR4AYOM5YJKJ4APZ7O547R5T` | Volatile (XLM) | 0.0% | $0  | ✅ Active | HODL     |
| **XLM_HODL_4** | `CCGKL6U2DHSNFJ3NU4UPRUKYE2EUGYR4ZFZDYA7KDJLP3TKSPHD5C4UP` | Volatile (XLM) | 0.0% | $0  | ✅ Active | HODL     |

### Fee Structure (All Vaults)

```
Deposit Fee: 0.1%
Withdrawal Fee: 0.1%
Performance Fee: 10% of profits
Minimum Deposit: 1 XLM
```

### Network Configuration

```yaml
Network: Stellar Testnet
Horizon URL: https://horizon-testnet.stellar.org
RPC URL: https://soroban-testnet.stellar.org
Friendbot: https://friendbot.stellar.org
Explorer: https://stellar.expert/explorer/testnet
```

### DeFindex API Configuration

```yaml
Base URL: https://api.defindex.io
Authentication: Bearer Token (DEFINDEX_API_KEY)
Supported Operations:
  - /vault/{address}/deposit (Build transaction)
  - /vault/{address}/withdraw (Build transaction)
  - /vault/{address}/balance (Check balance)
  - /send (Submit transaction)
```

---

## 🤖 AI Agent Tools

### Tool Categories

1. **Discovery Tools**: Find and analyze vaults
2. **Transaction Tools**: Execute autonomous operations
3. **Fallback Tools**: Manual payment instructions
4. **Account Tools**: Agent account management

### Tool Implementation Details

#### 1. discover_high_yield_vaults

**Purpose**: Discover all available DeFindex vaults sorted by APY
**File**: `backend/defindex_tools.py:25`
**Tool Type**: LangChain async tool

**Signature**:

```python
@tool
async def discover_high_yield_vaults(min_apy: Optional[float] = 0.0) -> str
```

**Parameters**:

- `min_apy` (optional): Minimum APY threshold as percentage (default 0.0%)

**Returns**: Complete list of available vaults sorted by APY with full details

**Usage Examples**:

```python
# Get all vaults
await discover_high_yield_vaults.ainvoke({"min_apy": 0.0})

# Get only high-yield vaults
await discover_high_yield_vaults.ainvoke({"min_apy": 15.0})
```

**Sample Output**:

```
Found 4 available DeFindex vaults on testnet (sorted by APY):

1. XLM HODL 1 (XLM) 🟡
   APY: 0.0% | Strategy: HODL
   TVL: $0 | Type: volatile
   Address: CAHWRPKBPX4FNLXZOAD565IBSICQPL5QX37IDLGJYOPWX22WWKFWQUBA
```

#### 2. get_defindex_vault_details

**Purpose**: Get detailed information about a specific vault
**File**: `backend/defindex_tools.py:76`
**Tool Type**: LangChain async tool

**Signature**:

```python
@tool
async def get_defindex_vault_details(vault_address: str) -> str
```

**Parameters**:

- `vault_address` (required): The contract address of the vault

**Returns**: Comprehensive vault information including strategies and performance

**Usage Examples**:

```python
await get_defindex_vault_details.ainvoke({
    "vault_address": "CAHWRPKBPX4FNLXZOAD565IBSICQPL5QX37IDLGJYOPWX22WWKFWQUBA"
})
```

#### 3. execute_defindex_deposit ⭐ **NEW**

**Purpose**: Execute autonomous deposit transactions via DeFindex API
**File**: `backend/defindex_tools.py:152`
**Tool Type**: LangChain async tool

**Signature**:

```python
@tool
async def execute_defindex_deposit(
    vault_address: str,
    amount_xlm: float,
    user_address: str,
    network: str = "testnet"
) -> str
```

**Parameters**:

- `vault_address` (required): Verified testnet vault address
- `amount_xlm` (required): Amount to deposit in XLM (e.g., 10.5)
- `user_address` (required): User's Stellar public key (agent account)
- `network` (optional): Network to use ('testnet' or 'mainnet', default 'testnet')

**Returns**: Transaction execution details including hash and status

**Usage Examples**:

```python
await execute_defindex_deposit.ainvoke({
    "vault_address": "CAHWRPKBPX4FNLXZOAD565IBSICQPL5QX37IDLGJYOPWX22WWKFWQUBA",
    "amount_xlm": 10.0,
    "user_address": "Gxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
    "network": "testnet"
})
```

**Sample Success Output**:

```
🚀 AUTONOMOUS DEPOSIT EXECUTED SUCCESSFULLY

✅ Transaction Confirmed: abc123...
💰 Amount: 10.0 XLM deposited to XLM_HODL_1
🏦 Vault: CAHWRPKB...WKFWQUBA
📊 Network: testnet
⚡ Agent Account: GC3RMNTD...PMIH3H4D

🔗 Stellar Explorer: https://stellar.expert/explorer/testnet/tx/abc123
```

#### 4. execute_defindex_withdrawal ⭐ **NEW**

**Purpose**: Execute autonomous withdrawal transactions via DeFindex API
**File**: `backend/defindex_tools.py:409`
**Tool Type**: LangChain async tool

**Signature**:

```python
@tool
async def execute_defindex_withdrawal(
    vault_address: str,
    amount_xlm: float,
    user_address: str,
    network: str = "testnet"
) -> str
```

**Parameters**:

- `vault_address` (required): Verified testnet vault address
- `amount_xlm` (required): Amount to withdraw in XLM (e.g., 5.0)
- `user_address` (required): User's Stellar public key (agent account)
- `network` (optional): Network to use ('testnet' or 'mainnet', default 'testnet')

**Returns**: Transaction execution details including hash and status

**Usage Examples**:

```python
await execute_defindex_withdrawal.ainvoke({
    "vault_address": "CAHWRPKBPX4FNLXZOAD565IBSICQPL5QX37IDLGJYOPWX22WWKFWQUBA",
    "amount_xlm": 5.0,
    "user_address": "Gxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
    "network": "testnet"
})
```

#### 5. prepare_defindex_deposit

**Purpose**: Manual payment fallback when API unavailable
**File**: `backend/defindex_tools.py:290`
**Tool Type**: LangChain async tool

**Signature**:

```python
@tool
async def prepare_defindex_deposit(
    vault_address: str,
    amount_xlm: float,
    user_address: str,
    network: str = "testnet"
) -> str
```

**Returns**: Manual payment instructions for wallet execution

---

## 🔧 Integration Patterns

### Agent System Integration

All DeFindex tools are automatically loaded into the agent system:

```python
# File: backend/agent/core.py:104
from defindex_tools import (
    discover_high_yield_vaults,
    get_defindex_vault_details,
    prepare_defindex_deposit,
    execute_defindex_deposit,      # Autonomous execution
    execute_defindex_withdrawal    # Autonomous execution
)

agent_tools.extend([
    discover_high_yield_vaults,
    get_defindex_vault_details,
    prepare_defindex_deposit,
    execute_defindex_deposit,      # NEW: Autonomous transaction execution
    execute_defindex_withdrawal    # NEW: Autonomous withdrawal execution
])
```

### Autonomous Transaction Flow

```
User Request → AI Agent → Tool Selection → DeFindex API → Transaction Builder →
Transaction Signing → Stellar Network → Confirmation → User Feedback
```

### Error Handling Patterns

1. **API Key Missing**: Graceful fallback to manual payment instructions
2. **Invalid Vault Address**: List available vaults and suggest alternatives
3. **Insufficient Balance**: Clear error with current balance information
4. **Network Issues**: User-friendly error messages and alternatives

### Account Management Patterns

```python
# Smart account selection (automatic)
from agent.core import get_default_agent_account
default_account = get_default_agent_account()

# Returns first account with balance ≥ 1 XLM, or first available account
```

---

## 📚 API Reference

### Core Agent Functions

#### process_agent_message

**File**: `backend/agent/core.py:152`
**Purpose**: Main agent processing function with streaming

```python
async def process_agent_message_streaming(
    message: str,
    history: List[Dict[str, str]],
    agent_account: Optional[str] = None
):
    """Process user message through AI agent with multi-step reasoning"""
```

#### get_agent_status

**File**: `backend/agent/core.py:124`
**Purpose**: Get current agent system status

```python
async def get_agent_status() -> Dict[str, Any]:
    """Get current agent system status including available tools"""
```

### Utility Functions

#### Transaction Signing

**File**: `backend/transaction_utils.py`

```python
def sign_transaction_with_agent_key(
    unsigned_xdr: str,
    agent_keypair: Keypair,
    network: str = "testnet"
) -> str:
    """Sign transaction XDR with agent keypair"""
```

#### Amount Validation

```python
def validate_transaction_amount(
    amount_xlm: float,
    min_balance: float = 1.0
) -> bool:
    """Validate transaction amount meets minimum requirements"""
```

---

## 💡 Usage Examples

### Example 1: Complete Vault Discovery and Deposit

```python
# Initialize agent
from agent.core import initialize_agent, process_agent_message_streaming
await initialize_agent()

# User request: "Show me vaults and deposit to the best one"
async for response in process_agent_message_streaming(
    message="Show me available vaults and deposit 10 XLM to the best one",
    history=[],
    agent_account=None  # Agent will auto-select
):
    print(response["content"])
```

**Expected Agent Response**:

```
🔧 Executing discover_high_yield_vaults...
Found 4 available DeFindex vaults on testnet...

🔧 Executing execute_defindex_deposit...
🚀 AUTONOMOUS DEPOSIT EXECUTED SUCCESSFULLY
✅ Transaction Confirmed: abc123...
```

### Example 2: Direct Tool Usage

```python
from defindex_tools import discover_high_yield_vaults, execute_defindex_deposit

# Discover vaults
vaults = await discover_high_yield_vaults.ainvoke({"min_apy": 0.0})
print(vaults)

# Execute autonomous deposit
result = await execute_defindex_deposit.ainvoke({
    "vault_address": "CAHWRPKBPX4FNLXZOAD565IBSICQPL5QX37IDLGJYOPWX22WWKFWQUBA",
    "amount_xlm": 10.0,
    "user_address": "GC3RMNTDPMIH3H4D2A5D3F5D5F5F5F5F5F5F5F5F5F5F5F5F5F5F",
    "network": "testnet"
})
print(result)
```

### Example 3: Error Handling

```python
# Invalid vault address
result = await execute_defindex_deposit.ainvoke({
    "vault_address": "INVALID_ADDRESS",
    "amount_xlm": 10.0,
    "user_address": "GC3RMNTD...",
    "network": "testnet"
})

# Returns helpful error message with available vaults
```

---

## 🚨 Troubleshooting

### Common Issues and Solutions

#### 1. "DEFINDEX_API_KEY environment variable not set"

**Issue**: DeFindex API client cannot authenticate
**Solution**: Set environment variable or use manual payment fallback

```bash
export DEINDEX_API_KEY="your_api_key_here"
```

#### 2. "No agent account found"

**Issue**: Agent has no funded accounts available
**Solution**: Create and fund an agent account

```python
from tools.agent.account_management import create_agent_account
result = create_agent_account("My Trading Account")
```

#### 3. "Transaction signing failed"

**Issue**: Cannot access private key for signing
**Solution**: Check key_manager configuration and permissions

#### 4. "Vault not found"

**Issue**: Invalid vault address provided
**Solution**: Use discover_high_yield_vaults to get valid addresses

### Testing Commands

```bash
# Test autonomous tools
cd backend
source .venv/bin/activate
python test_autonomous_transactions.py

# Check agent status
curl http://localhost:8000/health

# Test via chat interface
npm run dev  # Frontend
# Navigate to chat interface and try commands
```

---

## 📝 Development Notes

### File Structure

```
backend/
├── defindex_tools.py          # All LangChain tools
├── defindex_client.py         # DeFindex API client
├── transaction_utils.py       # Transaction signing utilities
├── agent/core.py             # Agent system integration
├── agent/tools.py            # Agent account tools
├── key_manager.py            # Private key management
└── test_autonomous_transactions.py  # Test suite
```

### Architecture Patterns

1. **Tool Design**: All tools follow LangChain @tool decorator pattern
2. **Error Handling**: Consistent error messages with helpful alternatives
3. **Account Management**: Smart defaults with fallback options
4. **Transaction Flow**: Build → Sign → Submit → Confirm
5. **Network Safety**: Testnet-only deployment with clear warnings

### Security Considerations

- ✅ Private keys stored securely in backend environment
- ✅ No private keys exposed to frontend
- ✅ Transactions signed server-side only
- ✅ Testnet-only deployment for safety
- ✅ Amount validation and balance checking
- ✅ Vault address validation against known contracts

### Performance Notes

- Tools use async/await patterns for non-blocking operations
- DeFindex API includes retry logic with exponential backoff
- Transaction building cached where possible
- Graceful degradation when services unavailable

---

## 📈 Status and Next Steps

### ✅ **Current Status**

- **Phase 1**: Account Management - COMPLETED
- **Phase 2**: Autonomous Transactions - COMPLETED
- **Phase 3**: Documentation & Integration - COMPLETED
- **Phase 4**: Human Experience Features - DEFERRED

### 🔄 **In Development**

- Mainnet vault deployment for real yield
- Multi-asset vault support (stablecoins, tokens)
- Enhanced APY with real yield-generating strategies
- Fiat onramp integration for USDC purchases

### 🎯 **Ready for Use**

The autonomous DeFindex integration is **production-ready** for educational use on Stellar testnet. All tools are tested, documented, and integrated into the AI agent system.

**Start Using**: Simply chat with the agent using natural language commands like:

- "Show me available vaults"
- "Deposit 10 XLM to the best vault"
- "Check my vault balance"
- "Withdraw 5 XLM from XLM_HODL_1"

---

**Last Updated**: 2025-11-05
**Version**: 1.0
**Contact**: Development Team
