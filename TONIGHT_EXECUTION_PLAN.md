# Tonight's Execution Plan - 6PM to Complete

**Goal**: Clean, refactor, and prepare Tuxedo for Phala deployment in one session.
**Approach**: Incremental, working with existing Render CI/CD, each change deployable.

## 🚀 Execution Order

### Step 1: Clean Up Dead Code (30 minutes)
**Goal**: Remove TUX farming and other dead code, ensure everything still works

**Actions**:
```bash
# Remove TUX farming components
rm -rf src/components/tux_farming/
rm src/hooks/useTuxFarming.ts
rm src/components/dashboard/TuxMiningDashboard.tsx

# Remove TUX farming backend
rm backend/tux_farming.py
rm backend/tux_farming_transactions.py

# Remove TUX farming tests
rm test_mock_farming.py
rm test_tux_farming.py

# Test deployment still works
git add .
git commit -m "Remove TUX farming dead code"
# Wait for Render deployment, verify app works
```

### Step 2: Fix Testing Structure (15 minutes)
**Goal**: Professional appearance, move tests out of root

**Actions**:
```bash
# Create proper test structure
mkdir -p tests/{integration,e2e,fixtures}
mkdir -p backend/tests/{test_tools,test_api,integration}

# Move test files to proper locations
mv test_agent.py backend/tests/
mv test_agent_with_tools.py backend/tests/test_tools/
mv test_multiturn.py backend/tests/test_chat/
mv test_multiturn_with_tools.py backend/tests/test_chat/
mv test_wallet_fix.py backend/tests/test_agent_management/

# Verify deployment still works
git add .
git commit -m "Fix testing structure, move tests out of root"
# Wait for Render deployment, verify tests still accessible if needed
```

### Step 3: Remove Wallet Dependencies (45 minutes)
**Goal**: Remove all wallet code, replace with agent-first approach

**Actions**:
```bash
# Remove wallet provider system
rm src/providers/WalletProvider.tsx
rm src/components/WalletButton.tsx
rm src/util/wallet.ts

# Create new agent provider
# (We'll create this file)

# Update all components that use wallet
# (We'll update these files)

# Test deployment
git add .
git commit -m "Remove wallet dependencies, add agent provider"
# Wait for Render deployment, verify agent interface works
```

### Step 4: Create Agent-First Account Tool (45 minutes)
**Goal**: Replace wallet with filesystem-based agent account management

**Actions**:
```python
# backend/tools/agent/account_management.py
# (Create new tool for agent account management)

# backend/api/routes/agent.py
# (Create new API endpoints for agent operations)

# src/components/agent/AccountManager.tsx
# (Create agent account management UI)
```

### Step 5: Update AI Agent to Use Agent Accounts (30 minutes)
**Goal**: AI agent manages and uses its own accounts

**Actions**:
```python
# Update AI agent tools to include account management
# Remove wallet references from prompts
# Add account creation/management tools
```

### Step 6: Deploy to Phala (30 minutes)
**Goal**: Get working version on Phala TEE

**Actions**:
```bash
# Update docker-compose.phala.yaml
# Deploy to Phala using existing checklist
# Verify agent functionality in TEE
```

## 📋 Detailed Implementation

### Step 1: Remove TUX Farming (Now)

```bash
# Remove TUX farming files
rm -rf src/components/tux_farming/
rm src/hooks/useTuxFarming.ts
rm src/components/dashboard/TuxMiningDashboard.tsx
rm backend/tux_farming.py
rm backend/tux_farming_transactions.py
rm test_mock_farming.py
rm test_tux_farming.py

# Clean up any remaining references
# (Search for "tux_farming" and remove imports/references)
```

### Step 2: Fix Testing Structure (After Step 1)

```bash
# Create proper test directories
mkdir -p backend/tests/{test_tools,test_api,test_chat,integration}
mkdir -p tests/{integration,e2e,fixtures}

# Move test files
mv test_agent.py backend/tests/
mv test_agent_with_tools.py backend/tests/test_tools/
mv test_multiturn.py backend/tests/test_chat/
mv test_multiturn_with_tools.py backend/tests/test_chat/
mv test_wallet_fix.py backend/tests/test_agent_management/

# Update test imports if needed
```

### Step 3: Remove Wallet Dependencies (After Step 2)

#### 3.1 Remove Wallet Files
```bash
rm src/providers/WalletProvider.tsx
rm src/components/WalletButton.tsx
rm src/util/wallet.ts
```

#### 3.2 Create Agent Provider
```typescript
// src/providers/AgentProvider.tsx
import React, { createContext, useContext, useState, useEffect } from 'react';

interface AgentAccount {
  address: string;
  name: string;
  balance: number;
  network: string;
}

interface AgentContextType {
  accounts: AgentAccount[];
  activeAccount: string;
  setActiveAccount: (address: string) => void;
  createAccount: (name?: string) => Promise<string>;
  isLoading: boolean;
  error: string | null;
}

const AgentContext = createContext<AgentContextType>({
  accounts: [],
  activeAccount: '',
  setActiveAccount: () => {},
  createAccount: async () => '',
  isLoading: false,
  error: null,
});

export const useAgent = () => useContext(AgentContext);

export const AgentProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [accounts, setAccounts] = useState<AgentAccount[]>([]);
  const [activeAccount, setActiveAccount] = useState<string>('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const createAccount = async (name?: string): Promise<string> => {
    setIsLoading(true);
    setError(null);

    try {
      const response = await fetch('/api/agent/create-account', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ name })
      });

      if (!response.ok) throw new Error('Failed to create account');

      const newAccount = await response.json();
      setAccounts(prev => [...prev, newAccount]);
      setActiveAccount(newAccount.address);

      return newAccount.address;
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error');
      throw err;
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    // Load existing accounts on mount
    loadAccounts();
  }, []);

  const loadAccounts = async () => {
    try {
      const response = await fetch('/api/agent/accounts');
      if (response.ok) {
        const accounts = await response.json();
        setAccounts(accounts);
        if (accounts.length > 0 && !activeAccount) {
          setActiveAccount(accounts[0].address);
        }
      }
    } catch (err) {
      console.error('Failed to load accounts:', err);
    }
  };

  return (
    <AgentContext.Provider value={{
      accounts,
      activeAccount,
      setActiveAccount,
      createAccount,
      isLoading,
      error
    }}>
      {children}
    </AgentContext.Provider>
  );
};
```

#### 3.3 Update App.tsx
```typescript
// Replace WalletProvider with AgentProvider
import { AgentProvider } from './providers/AgentProvider';

// Wrap app with AgentProvider instead of WalletProvider
<AgentProvider>
  <App />
</AgentProvider>
```

### Step 4: Create Agent Account Management Tool (After Step 3)

#### 4.1 Backend Account Management Tool
```python
# backend/tools/agent/account_management.py
from typing import Dict, Optional, List
from stellar_sdk import Keypair
from services.key_manager import KeyManager
from services.stellar_client import StellarClient
from tools.base import BaseTool

class AccountManagementTool(BaseTool):
    """Agent-controlled account management tool"""

    def __init__(self):
        self.key_manager = KeyManager()
        self.stellar_client = StellarClient()

    async def create_account(self, account_name: Optional[str] = None) -> Dict:
        """Create new agent-controlled account"""

        # Generate new keypair
        keypair = Keypair.random()

        # Store in key manager with metadata
        metadata = {
            "name": account_name or f"Account {len(self.key_manager.list_accounts()) + 1}",
            "created_at": "2025-01-03T00:00:00Z",  # Use actual timestamp
            "network": "testnet"
        }

        self.key_manager.store(keypair.public_key, keypair.secret)

        # Fund with testnet lumens
        try:
            await self.stellar_client.fund_account(keypair.public_key)
            funded = True
        except Exception as e:
            funded = False
            print(f"Failed to fund account: {e}")

        return {
            "address": keypair.public_key,
            "name": metadata["name"],
            "funded": funded,
            "network": "testnet"
        }

    async def list_accounts(self) -> List[Dict]:
        """List all agent-controlled accounts"""
        accounts = []

        for address in self.key_manager.list_accounts():
            try:
                # Get account info from Stellar
                account_data = await self.stellar_client.get_account(address)
                accounts.append({
                    "address": address,
                    "balance": account_data.get("balance", 0),
                    "network": "testnet"
                })
            except Exception as e:
                # Account exists but might not be funded
                accounts.append({
                    "address": address,
                    "balance": 0,
                    "network": "testnet"
                })

        return accounts
```

#### 4.2 Agent API Routes
```python
# backend/api/routes/agent.py
from fastapi import APIRouter, HTTPException
from tools.agent.account_management import AccountManagementTool
from api.schemas import AccountCreateRequest, AccountResponse

router = APIRouter()
account_tool = AccountManagementTool()

@router.post("/create-account", response_model=AccountResponse)
async def create_account(request: AccountCreateRequest):
    """Create new agent-controlled account"""
    try:
        result = await account_tool.create_account(request.name)
        return AccountResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/accounts", response_model=List[AccountResponse])
async def list_accounts():
    """List all agent-controlled accounts"""
    try:
        accounts = await account_tool.list_accounts()
        return [AccountResponse(**account) for account in accounts]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

#### 4.3 Agent Management UI
```typescript
// src/components/agent/AccountManager.tsx
import React from 'react';
import { useAgent } from '../../hooks/useAgent';

export const AccountManager: React.FC = () => {
  const { accounts, activeAccount, createAccount, setActiveAccount, isLoading, error } = useAgent();

  const handleCreateAccount = async () => {
    try {
      await createAccount();
    } catch (err) {
      console.error('Failed to create account:', err);
    }
  };

  return (
    <div className="account-manager">
      <h3>Agent Accounts</h3>

      <div className="account-actions">
        <button
          onClick={handleCreateAccount}
          disabled={isLoading}
        >
          {isLoading ? 'Creating...' : 'Create New Account'}
        </button>
      </div>

      {error && (
        <div className="error">
          Error: {error}
        </div>
      )}

      <div className="account-list">
        <h4>Your Agent Accounts:</h4>
        {accounts.map(account => (
          <div
            key={account.address}
            className={`account-item ${account.address === activeAccount ? 'active' : ''}`}
            onClick={() => setActiveAccount(account.address)}
          >
            <div className="account-name">{account.name}</div>
            <div className="account-address">{account.address}</div>
            <div className="account-balance">Balance: {account.balance} XLM</div>
          </div>
        ))}
      </div>

      {activeAccount && (
        <div className="active-account">
          <strong>Active Account:</strong> {activeAccount}
        </div>
      )}
    </div>
  );
};
```

### Step 5: Update AI Agent (After Step 4)

```python
# Add account management tools to AI agent
ACCOUNT_MANAGEMENT_TOOLS = [
    {
        "name": "create_account",
        "description": "Create a new agent-controlled Stellar account",
        "parameters": {
            "account_name": "Optional name for the account"
        }
    },
    {
        "name": "list_accounts",
        "description": "List all agent-controlled accounts",
        "parameters": {}
    },
    {
        "name": "switch_account",
        "description": "Switch to a different agent account",
        "parameters": {
            "account_address": "The address of the account to switch to"
        }
    }
]

# Update system prompts to remove wallet references
SYSTEM_PROMPT = """
You are Tuxedo, an AI agent that manages its own Stellar accounts for DeFi operations.

You can:
- Create and manage your own accounts (no external wallet needed)
- Perform DeFi operations using your controlled accounts
- Access Blend protocol and DeFindex vaults
- Execute transactions autonomously

You DO NOT need users to connect external wallets. You manage your own keys securely.
"""
```

### Step 6: Phala Deployment (After Step 5)

```bash
# Update docker-compose.phala.yaml
# Follow existing PHALA_DEPLOYMENT_CHECKLIST.md

# Deploy to Phala
phala cvms create -n tuxedo-ai -c ./docker-compose.phala.yaml

# Test agent functionality in TEE
curl https://your-phala-url/health
curl -X POST https://your-phala-url/api/agent/create-account
```

## ⏰ Timeline (6PM Start)

- **6:00-6:30**: Remove TUX farming, commit, verify Render deployment
- **6:30-6:45**: Fix testing structure, commit, verify deployment
- **6:45-7:30**: Remove wallet dependencies, create agent provider, commit, verify
- **7:30-8:15**: Create agent account management tool and API, commit, verify
- **8:15-8:45**: Update AI agent with account tools, commit, verify
- **8:45-9:15**: Deploy to Phala, test TEE functionality
- **9:15-9:30**: Final testing and validation

## ✅ Success Criteria

Each step should:
- ✅ Commit changes to git
- ✅ Wait for Render deployment success
- ✅ Verify functionality still works
- ✅ Move to next step only after current step is stable

## 🚨 Rollback Plan

If any step breaks the deployment:
```bash
git log --oneline  # See recent commits
git revert HEAD    # Revert last commit
# Wait for Render to redeploy working version
```

This incremental approach ensures we always have a working deployment and can isolate issues quickly.

Let's start with Step 1: Remove TUX farming code! 🚀