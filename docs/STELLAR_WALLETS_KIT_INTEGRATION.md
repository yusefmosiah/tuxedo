# Stellar Wallets Kit Integration Guide

## Executive Summary

This document provides a comprehensive plan to reintegrate `stellar-wallets-kit` into Tuxedo, enabling a hybrid architecture where:

1. **Agent operates autonomously** - No signing prompts, seamless DeFi operations
2. **Users can connect external wallets** - Freighter, xBull, Albedo, etc.
3. **Dual-mode operation** - Users choose between agent-managed accounts or self-custody
4. **Seamless bridging** - Import external wallets into agent management OR export agent accounts to external wallets

## Table of Contents

1. [Current Architecture Analysis](#current-architecture-analysis)
2. [The Private Key Storage "Bug"](#the-private-key-storage-bug)
3. [Stellar Wallets Kit Overview](#stellar-wallets-kit-overview)
4. [Proposed Hybrid Architecture](#proposed-hybrid-architecture)
5. [Implementation Plan](#implementation-plan)
6. [Code Examples](#code-examples)
7. [Migration Strategy](#migration-strategy)
8. [Security Considerations](#security-considerations)

---

## Current Architecture Analysis

### What We Have

**Backend (`backend/account_manager.py`):**
- ✅ Multi-user account management with encrypted private key storage
- ✅ Chain-agnostic design (currently Stellar mainnet only)
- ✅ `generate_account()` - Creates new accounts with encrypted private keys
- ✅ `import_account()` - Import external accounts with private keys
- ✅ `export_account()` - Export account private keys
- ✅ `get_keypair_for_signing()` - Retrieve decrypted keypairs for transaction signing

**Frontend (`src/hooks/useWallet.ts`):**
- ❌ Legacy stub that only fetches agent accounts from API
- ❌ No actual wallet connection functionality
- ❌ Placeholder `signTransaction()` that does nothing

**Dependencies:**
- ✅ `@creit.tech/stellar-wallets-kit` v1.9.5 already in `package.json`
- ✅ Package installed but not integrated

### Current Agent Flow

```
User Chat → AI Agent → AccountManager.get_keypair_for_signing() → Sign Transaction → Submit to Horizon
```

**Pros:**
- Fully autonomous - no user interaction needed
- Fast execution
- Works great for agent-managed accounts

**Cons:**
- Users can't use their existing wallets (Freighter, etc.)
- Users can't directly control transactions
- Limited interoperability with Stellar ecosystem

---

## The Private Key Storage "Bug"

### Investigation Findings

**GOOD NEWS:** Private keys ARE being stored!

When the agent calls `account_manager.generate_account()`:
1. Line 77: Generates keypair via `adapter.generate_keypair()`
2. Lines 79-83: Encrypts private key using `EncryptionManager`
3. Lines 88-106: Stores encrypted private key in database

**The ACTUAL issue might be:**

1. **UX Issue** - Users don't know their agent-created accounts have exportable keys
2. **No import workflow** - Users can't easily import external wallets into agent management
3. **No wallet connection UI** - Users expect a "Connect Wallet" button like other dApps

**Solution:** Implement stellar-wallets-kit to provide standard wallet UX while maintaining agent autonomy.

---

## Stellar Wallets Kit Overview

### Latest Version: v1.9.5 (September 2025)

**Key Features:**
- Supports 9 wallets: Freighter, xBull, Albedo, Rabet, WalletConnect, Lobstr, Hana, Hot Wallet, Klever
- Framework-agnostic (React, Vue, Angular, vanilla JS)
- Transaction signing with user approval
- Address retrieval
- Network switching (mainnet/testnet)
- Customizable UI/UX

### Installation

```bash
npx jsr add @creit.tech/stellar-wallets-kit
```

### Basic API

```typescript
import { StellarWalletsKit } from "@creit.tech/stellar-wallets-kit/sdk";
import { defaultModules } from '@creit.tech/stellar-wallets-kit/modules/utils';

// Initialize
StellarWalletsKit.init({modules: defaultModules()});

// Get connected address
const {address} = await StellarWalletsKit.getAddress();

// Sign transaction
const {signedTxXdr} = await StellarWalletsKit.signTransaction(
  tx.toXDR(),
  {networkPassphrase: Networks.PUBLIC, address}
);
```

### Production Examples

Used by: Stellar Lab, xBull Swap, **Blend Capital**, FXDAO, Sorobando Domains

---

## Proposed Hybrid Architecture

### Three Operating Modes

#### Mode 1: Agent-Managed Account (Default)
```
User → AI Agent → AccountManager → Autonomous Signing → Horizon
```
- Agent has full custody
- No signing prompts
- Fast, seamless operations
- Users can export keys anytime

#### Mode 2: External Wallet (Self-Custody)
```
User → AI Agent → Prepare Transaction → stellar-wallets-kit → User Approval → Horizon
```
- User keeps custody via Freighter/xBull/etc.
- User approves each transaction
- Standard dApp experience
- Full control and transparency

#### Mode 3: Imported Wallet (Hybrid)
```
User → Connect Wallet → Import to AccountManager → Agent Manages → Autonomous Signing
```
- User imports existing wallet into agent
- Agent gets custody for autonomous operations
- Best of both worlds: existing wallet + agent autonomy
- Reversible via export

### Account Types in Database

Extend `wallet_accounts` table metadata to track account type:

```json
{
  "account_type": "agent_generated" | "user_imported" | "external_connected",
  "wallet_source": "freighter" | "xbull" | "agent" | null,
  "custody_mode": "agent" | "user",
  "imported_at": "2025-11-10T12:00:00Z"
}
```

---

## Implementation Plan

### Phase 1: Core Wallet Integration (2-3 days)

**1.1 Install and Configure stellar-wallets-kit**

```bash
npx jsr add @creit.tech/stellar-wallets-kit
```

**1.2 Create React Context for Wallet State**

File: `src/contexts/WalletContext.tsx`

```typescript
import { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { StellarWalletsKit, WalletNetwork, ISupportedWallet } from '@creit.tech/stellar-wallets-kit';
import { FREIGHTER_ID, FreighterModule } from '@creit.tech/stellar-wallets-kit/modules/freighter';
import { xBullModule } from '@creit.tech/stellar-wallets-kit/modules/xbull';

export type AccountMode = 'agent' | 'external' | 'imported';

interface WalletContextType {
  // Wallet connection
  kit: StellarWalletsKit | null;
  address: string | null;
  isConnected: boolean;

  // Account mode
  mode: AccountMode;
  setMode: (mode: AccountMode) => void;

  // Actions
  connectWallet: () => Promise<void>;
  disconnectWallet: () => void;
  signTransaction: (xdr: string) => Promise<string>;

  // Agent accounts
  agentAccounts: Array<{id: string; address: string; balance: string}>;
  refreshAgentAccounts: () => Promise<void>;
}

const WalletContext = createContext<WalletContextType | undefined>(undefined);

export function WalletProvider({ children }: { children: ReactNode }) {
  const [kit, setKit] = useState<StellarWalletsKit | null>(null);
  const [address, setAddress] = useState<string | null>(null);
  const [isConnected, setIsConnected] = useState(false);
  const [mode, setMode] = useState<AccountMode>('agent');
  const [agentAccounts, setAgentAccounts] = useState<any[]>([]);

  // Initialize stellar-wallets-kit
  useEffect(() => {
    const initKit = async () => {
      const walletKit = new StellarWalletsKit({
        network: WalletNetwork.PUBLIC, // mainnet
        selectedWalletId: FREIGHTER_ID,
        modules: [
          new FreighterModule(),
          new xBullModule(),
        ],
      });
      setKit(walletKit);
    };
    initKit();
  }, []);

  // Fetch agent accounts
  const refreshAgentAccounts = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/agent/accounts`);
      if (response.ok) {
        const accounts = await response.json();
        setAgentAccounts(accounts);

        // If in agent mode and we have accounts, set first as active
        if (mode === 'agent' && accounts.length > 0 && !address) {
          setAddress(accounts[0].address);
          setIsConnected(true);
        }
      }
    } catch (error) {
      console.error('Failed to fetch agent accounts:', error);
    }
  };

  useEffect(() => {
    refreshAgentAccounts();
  }, [mode]);

  const connectWallet = async () => {
    if (!kit) throw new Error('Wallet kit not initialized');

    await kit.openModal({
      onWalletSelected: async (option: ISupportedWallet) => {
        kit.setWallet(option.id);
        const { address: walletAddress } = await kit.getAddress();
        setAddress(walletAddress);
        setIsConnected(true);
        setMode('external');
      },
    });
  };

  const disconnectWallet = () => {
    setAddress(null);
    setIsConnected(false);
    setMode('agent');
  };

  const signTransaction = async (xdr: string): Promise<string> => {
    if (mode === 'external' && kit) {
      // Use external wallet to sign
      const { signedTxXdr } = await kit.signTransaction(xdr, {
        networkPassphrase: 'Public Global Stellar Network ; September 2015',
        address: address!,
      });
      return signedTxXdr;
    } else if (mode === 'agent') {
      // Agent signs server-side (no user action needed)
      // Transaction will be signed by backend using AccountManager
      return xdr; // Backend will sign
    } else {
      throw new Error('Invalid account mode for signing');
    }
  };

  return (
    <WalletContext.Provider value={{
      kit,
      address,
      isConnected,
      mode,
      setMode,
      connectWallet,
      disconnectWallet,
      signTransaction,
      agentAccounts,
      refreshAgentAccounts,
    }}>
      {children}
    </WalletContext.Provider>
  );
}

export function useWallet() {
  const context = useContext(WalletContext);
  if (!context) {
    throw new Error('useWallet must be used within WalletProvider');
  }
  return context;
}
```

**1.3 Update App.tsx to Include WalletProvider**

```typescript
import { WalletProvider } from './contexts/WalletContext';

function App() {
  return (
    <WalletProvider>
      {/* Existing app components */}
    </WalletProvider>
  );
}
```

**1.4 Create WalletSelector Component**

File: `src/components/WalletSelector.tsx`

```typescript
import { useWallet } from '../contexts/WalletContext';
import { Button } from '@stellar/design-system';

export function WalletSelector() {
  const {
    address,
    isConnected,
    mode,
    setMode,
    connectWallet,
    disconnectWallet,
    agentAccounts,
  } = useWallet();

  const formatAddress = (addr: string) =>
    `${addr.slice(0, 4)}...${addr.slice(-4)}`;

  return (
    <div className="wallet-selector">
      {/* Mode Selector */}
      <div className="mode-tabs">
        <button
          className={mode === 'agent' ? 'active' : ''}
          onClick={() => setMode('agent')}
        >
          🤖 Agent Mode
        </button>
        <button
          className={mode === 'external' ? 'active' : ''}
          onClick={() => setMode('external')}
        >
          🔐 My Wallet
        </button>
      </div>

      {/* Agent Mode */}
      {mode === 'agent' && (
        <div className="agent-mode">
          {agentAccounts.length > 0 ? (
            <select
              value={address || ''}
              onChange={(e) => {/* Switch agent account */}}
            >
              {agentAccounts.map(acc => (
                <option key={acc.id} value={acc.address}>
                  {formatAddress(acc.address)} ({acc.balance} XLM)
                </option>
              ))}
            </select>
          ) : (
            <p>No agent accounts. Ask agent to create one!</p>
          )}
        </div>
      )}

      {/* External Wallet Mode */}
      {mode === 'external' && (
        <div className="external-mode">
          {isConnected ? (
            <div className="connected">
              <span>{formatAddress(address!)}</span>
              <Button onClick={disconnectWallet} size="sm" variant="secondary">
                Disconnect
              </Button>
            </div>
          ) : (
            <Button onClick={connectWallet} size="md">
              Connect Wallet
            </Button>
          )}
        </div>
      )}
    </div>
  );
}
```

### Phase 2: Backend Transaction Routing (1-2 days)

**2.1 Update Chat API to Handle Wallet Mode**

File: `backend/main.py`

```python
@app.post("/chat")
async def chat_endpoint(request: ChatRequest):
    wallet_mode = request.wallet_mode or "agent"  # "agent" | "external"
    wallet_address = request.wallet_address

    # Create agent context
    agent_context = AgentContext(
        user_id=request.user_id or "anonymous",
        wallet_mode=wallet_mode,
        wallet_address=wallet_address
    )

    # Run agent with context
    response = await run_agent(
        message=request.message,
        history=request.history,
        context=agent_context
    )

    return response
```

**2.2 Update Agent Context**

File: `backend/agent/context.py`

```python
@dataclass
class AgentContext:
    """Agent execution context with wallet mode awareness"""
    user_id: str
    delegated_user_ids: List[str] = None
    wallet_mode: str = "agent"  # "agent" | "external"
    wallet_address: Optional[str] = None

    def requires_user_signing(self) -> bool:
        """Check if transactions need user approval"""
        return self.wallet_mode == "external"

    def get_signing_address(self) -> str:
        """Get address for transaction signing"""
        if self.wallet_mode == "external":
            if not self.wallet_address:
                raise ValueError("External mode requires wallet_address")
            return self.wallet_address
        else:
            # Agent mode - return agent account
            # This will be used by AccountManager
            return self.wallet_address or "agent_default"
```

**2.3 Update Transaction Flow**

When `wallet_mode == "external"`:
1. Agent prepares transaction XDR
2. Returns unsigned XDR to frontend
3. Frontend uses stellar-wallets-kit to get user signature
4. Frontend submits signed XDR back to backend
5. Backend submits to Horizon

When `wallet_mode == "agent"`:
1. Agent prepares transaction
2. Agent signs via AccountManager
3. Agent submits to Horizon
4. Returns result to frontend

### Phase 3: Import/Export Workflows (2-3 days)

**3.1 Import External Wallet**

User connects Freighter → Agent offers to import → User confirms → Private key requested → Stored in AccountManager → Now available for autonomous operations

```typescript
// Frontend
async function importWalletToAgent() {
  const { address } = await kit.getAddress();

  // Request private key from user
  const privateKey = await promptUserForPrivateKey();

  // Send to backend
  const response = await fetch(`${API_BASE_URL}/api/agent/import-wallet`, {
    method: 'POST',
    body: JSON.stringify({
      address,
      private_key: privateKey,
      source: 'freighter',
    }),
  });

  if (response.ok) {
    // Wallet now managed by agent
    setMode('agent');
    refreshAgentAccounts();
  }
}
```

```python
# Backend
@app.post("/api/agent/import-wallet")
async def import_wallet(request: ImportWalletRequest):
    result = account_manager.import_account(
        user_id=request.user_id,
        chain="stellar",
        private_key=request.private_key,
        name=f"Imported from {request.source}",
        network="mainnet",
        metadata={
            "source": request.source,
            "imported_at": datetime.utcnow().isoformat(),
        }
    )
    return result
```

**3.2 Export Agent Account**

User wants to use agent account in Freighter → Request export → Agent provides private key → User imports to Freighter → Can now use in both places

```typescript
async function exportAgentAccount(accountId: string) {
  const response = await fetch(`${API_BASE_URL}/api/agent/export-account`, {
    method: 'POST',
    body: JSON.stringify({ account_id: accountId }),
  });

  const { private_key, address } = await response.json();

  // Show QR code or secret key to user
  displayExportModal({
    address,
    secretKey: private_key,
    warning: 'Keep this private key secure!',
  });
}
```

### Phase 4: AI Agent Transaction Preparation (1 day)

**4.1 Update Agent Tools to Return Unsigned XDR**

When in external mode, tools should return unsigned transaction XDR instead of signing and submitting.

```python
def trading(action: str, agent_context: AgentContext, ...):
    # ... build transaction ...

    if agent_context.requires_user_signing():
        # Return unsigned XDR for frontend signing
        return {
            "requires_signature": True,
            "xdr": tx.to_xdr(),
            "description": "Buy 100 XLM for USDC",
            "message": "Please approve this transaction in your wallet"
        }
    else:
        # Agent signs and submits
        keypair = account_manager.get_keypair_for_signing(agent_context, account_id)
        stellar_keypair = Keypair.from_secret(keypair.private_key)
        tx.sign(stellar_keypair)
        response = horizon.submit_transaction(tx)
        return {
            "success": True,
            "hash": response.get("hash"),
            "ledger": response.get("ledger")
        }
```

**4.2 Frontend Transaction Signing Flow**

```typescript
// In ChatInterface.tsx
async function handleAgentResponse(response: AgentResponse) {
  if (response.requires_signature && mode === 'external') {
    // Agent prepared transaction, now user must sign
    const signedXdr = await signTransaction(response.xdr);

    // Submit signed transaction
    const submitResponse = await fetch(`${API_BASE_URL}/api/submit-signed`, {
      method: 'POST',
      body: JSON.stringify({ signed_xdr: signedXdr }),
    });

    // Show result to user
    const result = await submitResponse.json();
    displayTransactionResult(result);
  } else {
    // Agent handled everything
    displayAgentResponse(response);
  }
}
```

### Phase 5: UI/UX Polish (1-2 days)

**5.1 Mode Indicator**

Always show current mode prominently:
- 🤖 Agent Mode: "Agent managing transactions"
- 🔐 Wallet Mode: "You approve each transaction"

**5.2 Transaction Previews**

Before wallet signing, show:
- Operation type (e.g., "Supply 100 USDC to Comet Pool")
- Network fees
- Expected outcome
- Risk warnings

**5.3 Account Management UI**

Dashboard showing:
- Agent-managed accounts (with export option)
- Connected external wallets (with import option)
- Account balances and activity
- Easy switching between accounts

---

## Code Examples

### Complete useWallet Hook (Modern)

```typescript
// src/hooks/useWallet.ts
import { useContext } from 'react';
import { WalletContext } from '../contexts/WalletContext';

export function useWallet() {
  const context = useContext(WalletContext);
  if (!context) {
    throw new Error('useWallet must be used within WalletProvider');
  }
  return context;
}

// Backward compatible interface
export interface WalletState {
  address: string | null;
  isConnected: boolean;
  network: string;
  mode: 'agent' | 'external' | 'imported';
  signTransaction: (xdr: string) => Promise<string>;
  isPending: boolean;
  networkPassphrase: string;
}

// For components that still use old interface
export function useWalletLegacy(): WalletState {
  const { address, isConnected, mode, signTransaction } = useWallet();

  return {
    address,
    isConnected,
    network: 'mainnet',
    mode,
    signTransaction,
    isPending: false,
    networkPassphrase: 'Public Global Stellar Network ; September 2015',
  };
}
```

### Updated WalletButton Component

```typescript
// src/components/WalletButton.tsx
import { useWallet } from '../hooks/useWallet';
import { Button } from '@stellar/design-system';

export function WalletButton() {
  const {
    address,
    isConnected,
    mode,
    connectWallet,
    disconnectWallet,
    agentAccounts,
  } = useWallet();

  const formatAddress = (addr: string) =>
    `${addr.slice(0, 4)}...${addr.slice(-4)}`;

  if (mode === 'agent') {
    return (
      <Button variant="tertiary" size="sm">
        🤖 Agent ({agentAccounts.length} accounts)
      </Button>
    );
  }

  if (isConnected && address) {
    return (
      <Button
        variant="tertiary"
        size="sm"
        onClick={disconnectWallet}
      >
        🔐 {formatAddress(address)}
      </Button>
    );
  }

  return (
    <Button
      onClick={connectWallet}
      size="sm"
      variant="primary"
    >
      Connect Wallet
    </Button>
  );
}
```

### Agent Transaction Handler

```python
# backend/agent/transaction_handler.py
from typing import Dict, Any, Optional
from stellar_sdk import TransactionBuilder, Network, Keypair
from account_manager import AccountManager
from agent.context import AgentContext

class TransactionHandler:
    """Handle transaction signing based on wallet mode"""

    def __init__(self, account_manager: AccountManager):
        self.account_manager = account_manager

    def sign_and_submit(
        self,
        tx_builder: TransactionBuilder,
        agent_context: AgentContext,
        account_id: str,
        horizon_server
    ) -> Dict[str, Any]:
        """
        Sign and submit transaction based on wallet mode.

        Returns:
            For agent mode: {success: bool, hash: str, ledger: int}
            For external mode: {requires_signature: bool, xdr: str, description: str}
        """

        # Build transaction
        tx = tx_builder.set_timeout(30).build()

        # Check wallet mode
        if agent_context.requires_user_signing():
            # External wallet mode - return unsigned XDR
            return {
                "requires_signature": True,
                "xdr": tx.to_xdr(),
                "network_passphrase": Network.PUBLIC_NETWORK_PASSPHRASE,
                "description": self._describe_transaction(tx),
                "message": "Please approve this transaction in your wallet"
            }

        else:
            # Agent mode - sign and submit automatically
            try:
                # Get signing keypair
                keypair = self.account_manager.get_keypair_for_signing(
                    agent_context,
                    account_id
                )

                # Sign transaction
                stellar_keypair = Keypair.from_secret(keypair.private_key)
                tx.sign(stellar_keypair)

                # Submit to network
                response = horizon_server.submit_transaction(tx)

                return {
                    "success": response.get("successful", False),
                    "hash": response.get("hash"),
                    "ledger": response.get("ledger"),
                    "message": "Transaction submitted successfully"
                }

            except Exception as e:
                return {
                    "success": False,
                    "error": str(e)
                }

    def _describe_transaction(self, tx) -> str:
        """Generate human-readable transaction description"""
        ops = tx.transaction.operations
        if len(ops) == 1:
            op = ops[0]
            # Format based on operation type
            # Example: "Payment: Send 100 XLM to GABC..."
            return f"{op.__class__.__name__}: {self._format_operation(op)}"
        else:
            return f"Multi-operation transaction ({len(ops)} operations)"

    def _format_operation(self, operation) -> str:
        """Format single operation for display"""
        # Implementation depends on operation type
        # This is a simplified example
        return str(operation)
```

---

## Migration Strategy

### For Existing Users

**Step 1: No Disruption**
- Existing agent-managed accounts continue working
- No changes to agent autonomy

**Step 2: Gradual Rollout**
- Add wallet connection option to UI
- Offer import/export in account management
- Users can try external mode without losing agent accounts

**Step 3: User Education**
- In-app tutorials explaining modes
- Clear benefits of each mode
- Security best practices

### Testing Plan

**Unit Tests:**
- ✅ WalletContext state management
- ✅ Transaction signing in each mode
- ✅ Import/export workflows
- ✅ AccountManager integration

**Integration Tests:**
- ✅ Agent mode: Create account → Fund → Trade
- ✅ External mode: Connect Freighter → Approve transaction
- ✅ Import flow: Connect wallet → Import to agent → Use autonomously
- ✅ Export flow: Agent account → Export → Import to Freighter

**E2E Tests:**
- ✅ Full user journey in each mode
- ✅ Mode switching
- ✅ Multiple account management
- ✅ Error handling and recovery

---

## Security Considerations

### Agent Mode Security

**Pros:**
- ✅ Fast, seamless operations
- ✅ No wallet extension required
- ✅ Encrypted private key storage

**Cons:**
- ⚠️ Agent has custody of funds
- ⚠️ Users must trust backend security

**Mitigations:**
- Encryption at rest (EncryptionManager)
- User-specific encryption keys
- Export functionality for recovery
- Regular security audits

### External Wallet Mode Security

**Pros:**
- ✅ User maintains custody
- ✅ Transaction-by-transaction approval
- ✅ Standard Stellar wallet security

**Cons:**
- ⚠️ Slower UX (approval required)
- ⚠️ Requires browser extension
- ⚠️ Approval fatigue

**Mitigations:**
- Clear transaction previews
- Batch operations where possible
- Option to import for autonomous operations

### Import/Export Security

**Critical Considerations:**

1. **Private Key Transmission:**
   - ⚠️ ALWAYS use HTTPS
   - ⚠️ Never log private keys
   - ⚠️ Clear from memory after use
   - ⚠️ Rate limit import/export endpoints

2. **User Authentication:**
   - ✅ Require re-authentication for export
   - ✅ 2FA for sensitive operations
   - ✅ Audit logging

3. **Key Storage:**
   - ✅ Encrypted at rest
   - ✅ User-specific encryption keys
   - ✅ Secure key rotation

4. **User Warnings:**
   - ⚠️ "Importing gives agent custody"
   - ⚠️ "Exporting exposes private key"
   - ⚠️ "Keep exported keys secure"

---

## Appendix: stellar-wallets-kit API Reference

### Initialization

```typescript
import { StellarWalletsKit, WalletNetwork } from '@creit.tech/stellar-wallets-kit';
import { FreighterModule } from '@creit.tech/stellar-wallets-kit/modules/freighter';
import { xBullModule } from '@creit.tech/stellar-wallets-kit/modules/xbull';

const kit = new StellarWalletsKit({
  network: WalletNetwork.PUBLIC, // or WalletNetwork.TESTNET
  selectedWalletId: FREIGHTER_ID,
  modules: [
    new FreighterModule(),
    new xBullModule(),
    // ... other wallet modules
  ],
});
```

### Open Wallet Selection Modal

```typescript
await kit.openModal({
  onWalletSelected: async (option: ISupportedWallet) => {
    kit.setWallet(option.id);
    console.log('Selected:', option.name);
  },
  onClosed: () => {
    console.log('Modal closed');
  },
});
```

### Get Connected Address

```typescript
const { address } = await kit.getAddress();
console.log('Connected address:', address);
```

### Sign Transaction

```typescript
import { Networks } from '@stellar/stellar-sdk';

const signedXdr = await kit.signTransaction(unsignedXdr, {
  networkPassphrase: Networks.PUBLIC,
  address: connectedAddress,
});
```

### Sign Auth Entry (Soroban)

```typescript
const { signedAuthEntry } = await kit.signAuthEntry(
  authEntry,
  { networkPassphrase: Networks.PUBLIC }
);
```

### Sign Message

```typescript
const { signedMessage } = await kit.signMessage(
  'Hello Stellar!',
  { networkPassphrase: Networks.PUBLIC }
);
```

### Supported Wallets

- **Freighter**: Most popular browser extension
- **xBull**: Feature-rich wallet
- **Albedo**: Web-based wallet
- **Rabet**: Mobile-friendly
- **WalletConnect**: Mobile app integration
- **Lobstr**: Mobile wallet
- **Hana**: Browser extension
- **Hot Wallet**: Development wallet
- **Klever**: Multi-chain wallet

---

## Conclusion

This integration plan provides a comprehensive roadmap for reintegrating stellar-wallets-kit while maintaining agent autonomy. The hybrid architecture gives users choice and flexibility:

- **Power users** can keep self-custody with external wallets
- **Convenience seekers** can use agent-managed accounts
- **Bridge users** can import existing wallets for autonomous operations

The private key "bug" is actually a UX issue - keys ARE stored securely, we just need better UI to show users their options.

**Estimated Timeline:**
- Phase 1: 2-3 days
- Phase 2: 1-2 days
- Phase 3: 2-3 days
- Phase 4: 1 day
- Phase 5: 1-2 days
- **Total: 7-11 days**

**Next Steps:**
1. Review and approve architecture
2. Begin Phase 1 implementation
3. Test with mainnet (small amounts)
4. Iterate based on user feedback
5. Full production rollout

---

**Document Version:** 1.0
**Last Updated:** 2025-11-10
**Author:** Claude Code
**Status:** Ready for Implementation
