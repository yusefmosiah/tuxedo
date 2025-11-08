# Agent Portfolio Security Architecture
**Chain-Agnostic Multi-Account Management with Wallet Bridging**

---

## Executive Summary

**Vision:** Tuxedo agents operate across multiple blockchains, managing portfolios of account collections through filesystem-based storage, with seamless wallet import/export bridging existing DeFi users into the agentic world.

**Core Principles:**
1. **Chain Agnostic:** Wallets and blockchain tools are just data and code at the agent's fingertips
2. **Portfolio-Based:** Agents control collections of accounts, not single accounts
3. **Custodial Control:** Full wallet import/export for "not-your-keys-not-your-crypto" crowd
4. **Filesystem Native:** Account collections managed as encrypted filesystem artifacts

**Timeline:** 15-20 hours for Phase 1 (Stellar + Ethereum), expandable to other chains
**Priority:** CRITICAL - Killer feature for DeFi user onboarding

---

## Architecture Vision

### Current (Misaligned) Approach
```
User → Single Agent Account (Stellar only) → Stellar Blockchain
       ❌ Single chain
       ❌ Single account
       ❌ No import/export
       ❌ No portfolio management
```

### Target (Chain-Agnostic Portfolio) Approach
```
┌──────────────────────────────────────────────────────────┐
│  User (Passkey Auth)                                     │
│  user_id: "user_abc123"                                  │
└────────────────────┬─────────────────────────────────────┘
                     │
                     ↓
┌──────────────────────────────────────────────────────────┐
│  Portfolio Manager (Filesystem-Based)                    │
│  ~/.tuxedo/portfolios/user_abc123/                       │
│                                                           │
│  Collections:                                            │
│  ├── defi-strategy-1/                                    │
│  │   ├── stellar_accounts.json (encrypted)              │
│  │   ├── ethereum_accounts.json (encrypted)             │
│  │   └── metadata.json                                  │
│  │                                                       │
│  ├── long-term-holdings/                                 │
│  │   ├── bitcoin_accounts.json (encrypted)              │
│  │   └── metadata.json                                  │
│  │                                                       │
│  └── experimental/                                       │
│      ├── solana_accounts.json (encrypted)               │
│      └── metadata.json                                  │
└────────────────────┬─────────────────────────────────────┘
                     │
                     ↓
┌──────────────────────────────────────────────────────────┐
│  Chain Abstraction Layer                                 │
│  ├── Stellar (stellar-sdk)                               │
│  ├── Ethereum (ethers.js / viem)                         │
│  ├── Solana (web3.js)                                    │
│  ├── Bitcoin (bitcoinjs-lib)                             │
│  └── Cosmos (cosmjs)                                     │
└────────────────────┬─────────────────────────────────────┘
                     │
                     ↓
┌──────────────────────────────────────────────────────────┐
│  Wallet Import/Export Bridge                             │
│  Import: Stellar Wallets Kit, WalletConnect, etc.       │
│  Export: Standard wallet formats, hardware wallet paths │
│  → "Not-your-keys-not-your-crypto" compatibility        │
└──────────────────────────────────────────────────────────┘
                     │
                     ↓
            Multiple Blockchains
```

---

## Key Features

### 1. Chain-Agnostic Account Management

**Supported Chains (Phase 1):**
- ✅ Stellar (native, already integrated)
- ✅ Ethereum (EVM-compatible: Polygon, Arbitrum, Base, etc.)
- 🔄 Solana (Phase 2)
- 🔄 Bitcoin (Phase 2)
- 🔄 Cosmos ecosystem (Phase 3)

**Chain Abstraction Interface:**
```typescript
interface ChainAccount {
  chain: 'stellar' | 'ethereum' | 'solana' | 'bitcoin' | 'cosmos';
  address: string;
  privateKey: string; // encrypted
  derivationPath?: string; // for HD wallets
  metadata: {
    name: string;
    created_at: string;
    last_used_at?: string;
    tags: string[];
  };
}
```

### 2. Portfolio-Based Organization

**Collection Structure:**
```
~/.tuxedo/portfolios/
  {user_id}/
    collections/
      {collection_name}/
        {chain}_accounts.json    # Encrypted account data
        metadata.json            # Collection settings
        permissions.json         # Agent access rules
        audit_log.json          # Operation history
```

**Collection Types:**
- **Strategy Collections:** DeFi yield farming, trading bots, liquidity provision
- **Chain Collections:** All Stellar accounts, all Ethereum accounts
- **Purpose Collections:** Long-term holdings, experimental, business
- **Time Collections:** Q1-2025 trades, tax year 2024

**Benefits:**
- Organize accounts by any criteria
- Isolate risk across collections
- Fine-grained permission control
- Clear audit trails per collection

### 3. Wallet Import/Export (Killer Feature)

#### Import Capabilities

**From External Wallets:**
```typescript
interface WalletImport {
  // Stellar ecosystem
  importFromFreighter(): Promise<StellarAccount[]>;
  importFromLobstr(): Promise<StellarAccount[]>;
  importFromStellarWalletsKit(): Promise<StellarAccount[]>;

  // Ethereum ecosystem
  importFromMetaMask(): Promise<EthereumAccount[]>;
  importFromWalletConnect(): Promise<EthereumAccount[]>;

  // Universal
  importFromPrivateKey(key: string, chain: string): Promise<ChainAccount>;
  importFromMnemonic(mnemonic: string, chains: string[]): Promise<ChainAccount[]>;
  importFromHardwareWallet(path: string): Promise<ChainAccount>;
}
```

**User Experience:**
1. Connect existing Freighter wallet
2. Select accounts to import
3. Choose collection (or create new)
4. Accounts now accessible to agent
5. Original wallet still controls keys

**Bridge Use Case:**
> "I've been using Freighter for DeFi on Stellar for 2 years. Now I can import my accounts into Tuxedo, let the agent help with yield optimization, and I still maintain full control - I can export back to Freighter anytime."

#### Export Capabilities

**To External Wallets:**
```typescript
interface WalletExport {
  // Export to standard formats
  exportToPrivateKey(account: ChainAccount): string;
  exportToMnemonic(accounts: ChainAccount[]): string;
  exportToKeystore(account: ChainAccount, password: string): Keystore;

  // Direct wallet export
  exportToFreighter(accounts: StellarAccount[]): void;
  exportToMetaMask(accounts: EthereumAccount[]): void;

  // Hardware wallet paths
  exportToLedger(accounts: ChainAccount[]): DerivationPaths;
}
```

**User Experience:**
1. Select accounts from collection
2. Choose export format (private key, mnemonic, keystore)
3. Download encrypted file or copy to clipboard
4. Import into external wallet
5. Full custodial control maintained

**"Not-Your-Keys-Not-Your-Crypto" Guarantee:**
- Users can export at any time
- No lock-in to Tuxedo
- Full compatibility with standard wallets
- Hardware wallet support

### 4. Security Model

#### Encryption Layers

**Layer 1: User-Level Master Key**
- Derived from passkey authentication
- Encrypts all portfolio data
- User-specific encryption ensures multi-user isolation

**Layer 2: Collection-Level Keys**
- Each collection has unique encryption key
- Derived from master key + collection_id
- Allows selective decryption

**Layer 3: Account-Level Encryption**
- Private keys encrypted within collection files
- Double encryption (collection key + account salt)

**Encryption Implementation:**
```python
# backend/security/portfolio_encryption.py
class PortfolioEncryption:
    def __init__(self, user_id: str):
        # Derive master key from user passkey
        self.master_key = self._derive_master_key(user_id)

    def encrypt_collection(
        self,
        collection_id: str,
        accounts: List[ChainAccount]
    ) -> bytes:
        """Encrypt entire collection with collection-specific key"""
        collection_key = self._derive_collection_key(collection_id)
        encrypted_accounts = []

        for account in accounts:
            # Double encryption
            encrypted_private_key = self._encrypt_account_key(
                account.privateKey,
                collection_key
            )
            encrypted_accounts.append({
                **account,
                'privateKey': encrypted_private_key
            })

        return self._encrypt(json.dumps(encrypted_accounts), collection_key)

    def decrypt_account(
        self,
        collection_id: str,
        account_address: str
    ) -> ChainAccount:
        """Decrypt single account from collection"""
        collection_key = self._derive_collection_key(collection_id)
        collection_data = self._load_collection(collection_id)

        account = next(a for a in collection_data if a['address'] == account_address)
        decrypted_private_key = self._decrypt_account_key(
            account['privateKey'],
            collection_key
        )

        return ChainAccount(**{**account, 'privateKey': decrypted_private_key})
```

#### Permission System

**Agent Access Control:**
```json
// ~/.tuxedo/portfolios/{user_id}/collections/{collection_name}/permissions.json
{
  "collection_id": "defi-strategy-1",
  "agent_permissions": {
    "read_balances": true,
    "sign_transactions": true,
    "max_transaction_value": {
      "stellar": {"XLM": 1000},
      "ethereum": {"ETH": 0.5, "USDC": 5000}
    },
    "allowed_operations": [
      "swap",
      "provide_liquidity",
      "stake"
    ],
    "forbidden_operations": [
      "send_to_external",
      "delete_account"
    ],
    "require_user_approval": [
      "transactions_over_limit",
      "new_contract_interaction"
    ]
  },
  "audit_settings": {
    "log_all_operations": true,
    "alert_on_large_transactions": true,
    "daily_summary": true
  }
}
```

**Permission Enforcement:**
- Every agent operation checks permissions
- Transaction limits enforced pre-signing
- User approval required for sensitive operations
- Real-time audit logging

#### Audit Trail

**Operation Logging:**
```json
// ~/.tuxedo/portfolios/{user_id}/collections/{collection_name}/audit_log.json
{
  "operations": [
    {
      "timestamp": "2025-11-08T10:30:00Z",
      "operation": "sign_transaction",
      "agent_id": "agent_xyz",
      "account": "GXXX...STELLAR",
      "chain": "stellar",
      "details": {
        "type": "swap",
        "from_asset": "XLM",
        "to_asset": "USDC",
        "amount": 100,
        "tx_hash": "abc123..."
      },
      "approved": true,
      "user_approval_required": false
    },
    {
      "timestamp": "2025-11-08T11:45:00Z",
      "operation": "import_account",
      "agent_id": "system",
      "account": "0x123...ETHEREUM",
      "chain": "ethereum",
      "details": {
        "source": "metamask",
        "import_method": "wallet_connect"
      },
      "approved": true
    }
  ]
}
```

---

## Implementation Plan

### Phase 1: Stellar + Ethereum Foundation (15-20 hours)

#### 1.1 Filesystem Portfolio Manager (4-5 hours)

**New File:** `backend/portfolio/manager.py`

```python
"""
Portfolio Manager - Filesystem-based multi-chain account management
"""
from pathlib import Path
import json
from typing import List, Dict, Optional
from dataclasses import dataclass
from enum import Enum

class Chain(Enum):
    STELLAR = "stellar"
    ETHEREUM = "ethereum"
    SOLANA = "solana"
    BITCOIN = "bitcoin"
    COSMOS = "cosmos"

@dataclass
class ChainAccount:
    chain: Chain
    address: str
    private_key: str  # encrypted
    derivation_path: Optional[str] = None
    metadata: Dict = None

class PortfolioManager:
    """Manages user portfolios with multiple account collections"""

    def __init__(self, user_id: str, base_path: str = "~/.tuxedo/portfolios"):
        self.user_id = user_id
        self.portfolio_path = Path(base_path).expanduser() / user_id
        self.portfolio_path.mkdir(parents=True, exist_ok=True)

        from security.portfolio_encryption import PortfolioEncryption
        self.encryption = PortfolioEncryption(user_id)

    def create_collection(
        self,
        collection_name: str,
        metadata: Optional[Dict] = None
    ) -> Dict:
        """Create new account collection"""
        collection_path = self.portfolio_path / "collections" / collection_name
        collection_path.mkdir(parents=True, exist_ok=True)

        # Initialize metadata
        metadata_file = collection_path / "metadata.json"
        metadata_file.write_text(json.dumps({
            "name": collection_name,
            "created_at": datetime.now().isoformat(),
            "description": metadata.get("description", ""),
            "tags": metadata.get("tags", []),
            "chain_support": []
        }, indent=2))

        # Initialize permissions
        permissions_file = collection_path / "permissions.json"
        permissions_file.write_text(json.dumps({
            "collection_id": collection_name,
            "agent_permissions": {
                "read_balances": True,
                "sign_transactions": True,
                "max_transaction_value": {},
                "allowed_operations": [],
                "forbidden_operations": [],
                "require_user_approval": []
            }
        }, indent=2))

        # Initialize audit log
        audit_file = collection_path / "audit_log.json"
        audit_file.write_text(json.dumps({"operations": []}, indent=2))

        return {
            "collection_name": collection_name,
            "path": str(collection_path),
            "success": True
        }

    def add_account_to_collection(
        self,
        collection_name: str,
        account: ChainAccount
    ) -> Dict:
        """Add account to collection (encrypted)"""
        collection_path = self.portfolio_path / "collections" / collection_name

        if not collection_path.exists():
            return {"error": "Collection not found", "success": False}

        # Load existing accounts for this chain
        chain_file = collection_path / f"{account.chain.value}_accounts.json"

        if chain_file.exists():
            encrypted_data = chain_file.read_bytes()
            accounts = json.loads(
                self.encryption.decrypt_collection(collection_name, encrypted_data)
            )
        else:
            accounts = []

        # Add new account
        accounts.append({
            "chain": account.chain.value,
            "address": account.address,
            "private_key": account.private_key,  # Will be encrypted
            "derivation_path": account.derivation_path,
            "metadata": account.metadata or {}
        })

        # Encrypt and save
        encrypted_data = self.encryption.encrypt_collection(collection_name, accounts)
        chain_file.write_bytes(encrypted_data)

        # Log operation
        self._log_operation(collection_name, {
            "operation": "add_account",
            "chain": account.chain.value,
            "address": account.address,
            "timestamp": datetime.now().isoformat()
        })

        return {
            "collection": collection_name,
            "chain": account.chain.value,
            "address": account.address,
            "success": True
        }

    def get_accounts_in_collection(
        self,
        collection_name: str,
        chain: Optional[Chain] = None
    ) -> List[Dict]:
        """Get all accounts in collection (decrypted)"""
        collection_path = self.portfolio_path / "collections" / collection_name

        if not collection_path.exists():
            return []

        all_accounts = []

        # Determine which chain files to read
        if chain:
            chain_files = [collection_path / f"{chain.value}_accounts.json"]
        else:
            chain_files = list(collection_path.glob("*_accounts.json"))

        for chain_file in chain_files:
            if not chain_file.exists():
                continue

            encrypted_data = chain_file.read_bytes()
            accounts = json.loads(
                self.encryption.decrypt_collection(collection_name, encrypted_data)
            )

            # Return without private keys for listing
            all_accounts.extend([
                {
                    "chain": acc["chain"],
                    "address": acc["address"],
                    "metadata": acc["metadata"]
                }
                for acc in accounts
            ])

        return all_accounts

    def get_account_for_signing(
        self,
        collection_name: str,
        address: str
    ) -> Optional[ChainAccount]:
        """Get account with decrypted private key for signing"""
        # Check permissions
        if not self._check_permission(collection_name, "sign_transactions"):
            raise PermissionError(f"Agent not authorized to sign transactions in {collection_name}")

        # Find account across all chains in collection
        collection_path = self.portfolio_path / "collections" / collection_name

        for chain_file in collection_path.glob("*_accounts.json"):
            encrypted_data = chain_file.read_bytes()
            accounts = json.loads(
                self.encryption.decrypt_collection(collection_name, encrypted_data)
            )

            account = next((a for a in accounts if a["address"] == address), None)
            if account:
                # Log access
                self._log_operation(collection_name, {
                    "operation": "access_private_key",
                    "address": address,
                    "timestamp": datetime.now().isoformat()
                })

                return ChainAccount(**account)

        return None

    def list_collections(self) -> List[Dict]:
        """List all collections for user"""
        collections_path = self.portfolio_path / "collections"

        if not collections_path.exists():
            return []

        collections = []
        for collection_dir in collections_path.iterdir():
            if not collection_dir.is_dir():
                continue

            metadata_file = collection_dir / "metadata.json"
            if metadata_file.exists():
                metadata = json.loads(metadata_file.read_text())

                # Count accounts
                account_count = 0
                for chain_file in collection_dir.glob("*_accounts.json"):
                    encrypted_data = chain_file.read_bytes()
                    accounts = json.loads(
                        self.encryption.decrypt_collection(collection_dir.name, encrypted_data)
                    )
                    account_count += len(accounts)

                collections.append({
                    "name": collection_dir.name,
                    "metadata": metadata,
                    "account_count": account_count
                })

        return collections

    def _check_permission(self, collection_name: str, permission: str) -> bool:
        """Check if operation is allowed"""
        permissions_file = self.portfolio_path / "collections" / collection_name / "permissions.json"

        if not permissions_file.exists():
            return False

        permissions = json.loads(permissions_file.read_text())
        return permissions.get("agent_permissions", {}).get(permission, False)

    def _log_operation(self, collection_name: str, operation: Dict):
        """Log operation to audit trail"""
        audit_file = self.portfolio_path / "collections" / collection_name / "audit_log.json"

        if audit_file.exists():
            audit_data = json.loads(audit_file.read_text())
        else:
            audit_data = {"operations": []}

        audit_data["operations"].append(operation)

        audit_file.write_text(json.dumps(audit_data, indent=2))
```

#### 1.2 Wallet Import/Export Bridge (5-6 hours)

**New File:** `backend/wallet/import_export.py`

```python
"""
Wallet Import/Export Bridge
Supports importing from external wallets and exporting to standard formats
"""
from typing import List, Dict, Optional
from dataclasses import dataclass
import json

@dataclass
class ImportResult:
    success: bool
    accounts: List[ChainAccount]
    errors: List[str] = None

class WalletBridge:
    """Bridge between Tuxedo and external wallet systems"""

    def __init__(self, portfolio_manager: PortfolioManager):
        self.portfolio = portfolio_manager

    # IMPORT METHODS

    async def import_from_stellar_wallets_kit(
        self,
        collection_name: str
    ) -> ImportResult:
        """Import accounts from connected Stellar wallet"""
        try:
            # This will integrate with Stellar Wallets Kit on frontend
            # Backend receives the public key and signs with user's consent
            # For full import, user provides private key

            # Placeholder for actual implementation
            return ImportResult(
                success=False,
                accounts=[],
                errors=["Stellar Wallets Kit integration pending"]
            )
        except Exception as e:
            return ImportResult(
                success=False,
                accounts=[],
                errors=[str(e)]
            )

    def import_from_private_key(
        self,
        collection_name: str,
        private_key: str,
        chain: Chain,
        account_name: Optional[str] = None
    ) -> ImportResult:
        """Import account from private key"""
        try:
            # Derive public address from private key
            if chain == Chain.STELLAR:
                from stellar_sdk import Keypair
                keypair = Keypair.from_secret(private_key)
                address = keypair.public_key

            elif chain == Chain.ETHEREUM:
                from eth_account import Account
                account = Account.from_key(private_key)
                address = account.address

            else:
                raise ValueError(f"Chain {chain} not yet supported")

            # Create account object
            account = ChainAccount(
                chain=chain,
                address=address,
                private_key=private_key,
                metadata={
                    "name": account_name or f"Imported {chain.value} account",
                    "imported_at": datetime.now().isoformat(),
                    "import_method": "private_key"
                }
            )

            # Add to collection
            result = self.portfolio.add_account_to_collection(collection_name, account)

            if result.get("success"):
                return ImportResult(
                    success=True,
                    accounts=[account]
                )
            else:
                return ImportResult(
                    success=False,
                    accounts=[],
                    errors=[result.get("error")]
                )

        except Exception as e:
            return ImportResult(
                success=False,
                accounts=[],
                errors=[str(e)]
            )

    def import_from_mnemonic(
        self,
        collection_name: str,
        mnemonic: str,
        chains: List[Chain],
        derivation_paths: Optional[Dict[Chain, str]] = None
    ) -> ImportResult:
        """Import HD wallet accounts from mnemonic"""
        try:
            imported_accounts = []
            errors = []

            for chain in chains:
                try:
                    if chain == Chain.STELLAR:
                        # Stellar uses SLIP-0010 / BIP-0032
                        from stellar_sdk import Keypair
                        # Derive key from mnemonic (implementation depends on library)
                        # For now, placeholder
                        errors.append(f"Stellar mnemonic import not yet implemented")

                    elif chain == Chain.ETHEREUM:
                        # Ethereum uses BIP-44: m/44'/60'/0'/0/0
                        from eth_account import Account
                        Account.enable_unaudited_hdwallet_features()

                        path = derivation_paths.get(chain, "m/44'/60'/0'/0/0") if derivation_paths else "m/44'/60'/0'/0/0"
                        account = Account.from_mnemonic(mnemonic, account_path=path)

                        chain_account = ChainAccount(
                            chain=chain,
                            address=account.address,
                            private_key=account.key.hex(),
                            derivation_path=path,
                            metadata={
                                "name": f"Imported {chain.value} HD wallet",
                                "imported_at": datetime.now().isoformat(),
                                "import_method": "mnemonic"
                            }
                        )

                        self.portfolio.add_account_to_collection(collection_name, chain_account)
                        imported_accounts.append(chain_account)

                    else:
                        errors.append(f"Chain {chain} not yet supported")

                except Exception as e:
                    errors.append(f"Error importing {chain.value}: {str(e)}")

            return ImportResult(
                success=len(imported_accounts) > 0,
                accounts=imported_accounts,
                errors=errors if errors else None
            )

        except Exception as e:
            return ImportResult(
                success=False,
                accounts=[],
                errors=[str(e)]
            )

    # EXPORT METHODS

    def export_to_private_key(
        self,
        collection_name: str,
        address: str
    ) -> Dict:
        """Export account as private key"""
        try:
            account = self.portfolio.get_account_for_signing(collection_name, address)

            if not account:
                return {
                    "success": False,
                    "error": "Account not found"
                }

            return {
                "success": True,
                "chain": account.chain.value,
                "address": account.address,
                "private_key": account.private_key,
                "export_format": "private_key",
                "warning": "Keep this private key secure. Anyone with access can control your funds."
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

    def export_to_keystore(
        self,
        collection_name: str,
        address: str,
        password: str
    ) -> Dict:
        """Export account as encrypted keystore file (Ethereum standard)"""
        try:
            account = self.portfolio.get_account_for_signing(collection_name, address)

            if not account:
                return {"success": False, "error": "Account not found"}

            if account.chain == Chain.ETHEREUM:
                from eth_account import Account
                eth_account = Account.from_key(account.private_key)
                keystore = eth_account.encrypt(password)

                return {
                    "success": True,
                    "keystore": keystore,
                    "export_format": "keystore",
                    "instructions": "Import this keystore file into MetaMask or other Ethereum wallets"
                }
            else:
                return {
                    "success": False,
                    "error": f"Keystore export not supported for {account.chain.value}"
                }

        except Exception as e:
            return {"success": False, "error": str(e)}

    def export_collection_summary(
        self,
        collection_name: str
    ) -> Dict:
        """Export non-sensitive collection summary"""
        try:
            accounts = self.portfolio.get_accounts_in_collection(collection_name)

            return {
                "success": True,
                "collection": collection_name,
                "accounts": [
                    {
                        "chain": acc["chain"],
                        "address": acc["address"],
                        "name": acc["metadata"].get("name", "")
                    }
                    for acc in accounts
                ],
                "export_format": "summary",
                "note": "This export does not include private keys"
            }

        except Exception as e:
            return {"success": False, "error": str(e)}
```

#### 1.3 Chain Abstraction Layer (3-4 hours)

**New File:** `backend/chains/abstraction.py`

```python
"""
Chain Abstraction Layer
Provides unified interface for blockchain operations across chains
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from enum import Enum

class TransactionStatus(Enum):
    PENDING = "pending"
    SUCCESS = "success"
    FAILED = "failed"

class ChainAdapter(ABC):
    """Abstract base class for chain-specific implementations"""

    @abstractmethod
    async def get_balance(self, address: str, asset: Optional[str] = None) -> Dict:
        """Get account balance"""
        pass

    @abstractmethod
    async def send_transaction(
        self,
        from_address: str,
        to_address: str,
        amount: float,
        asset: Optional[str] = None,
        private_key: str = None
    ) -> Dict:
        """Send transaction"""
        pass

    @abstractmethod
    async def get_transaction(self, tx_hash: str) -> Dict:
        """Get transaction details"""
        pass

    @abstractmethod
    async def get_transaction_history(
        self,
        address: str,
        limit: int = 10
    ) -> List[Dict]:
        """Get transaction history"""
        pass

class StellarAdapter(ChainAdapter):
    """Stellar blockchain adapter"""

    def __init__(self, network: str = "testnet"):
        from stellar_sdk import Server
        self.network = network
        self.horizon_url = (
            "https://horizon-testnet.stellar.org"
            if network == "testnet"
            else "https://horizon.stellar.org"
        )
        self.server = Server(self.horizon_url)

    async def get_balance(self, address: str, asset: Optional[str] = None) -> Dict:
        try:
            account = self.server.load_account(address)
            balances = []

            for balance in account.raw_data.get('balances', []):
                if asset and balance.get('asset_code') != asset and balance.get('asset_type') != 'native':
                    continue

                balances.append({
                    "asset": balance.get('asset_code', 'XLM'),
                    "balance": float(balance.get('balance', 0)),
                    "asset_type": balance.get('asset_type')
                })

            return {
                "success": True,
                "chain": "stellar",
                "address": address,
                "balances": balances
            }

        except Exception as e:
            return {"success": False, "error": str(e)}

    async def send_transaction(
        self,
        from_address: str,
        to_address: str,
        amount: float,
        asset: Optional[str] = None,
        private_key: str = None
    ) -> Dict:
        try:
            from stellar_sdk import TransactionBuilder, Network, Keypair, Asset
            from stellar_sdk.operation import Payment

            source_keypair = Keypair.from_secret(private_key)
            source_account = self.server.load_account(from_address)

            # Build transaction
            transaction = (
                TransactionBuilder(
                    source_account=source_account,
                    network_passphrase=Network.TESTNET_NETWORK_PASSPHRASE if self.network == "testnet" else Network.PUBLIC_NETWORK_PASSPHRASE,
                    base_fee=100
                )
                .append_payment_op(
                    destination=to_address,
                    asset=Asset.native() if not asset or asset == "XLM" else Asset(asset),
                    amount=str(amount)
                )
                .set_timeout(30)
                .build()
            )

            # Sign and submit
            transaction.sign(source_keypair)
            response = self.server.submit_transaction(transaction)

            return {
                "success": True,
                "chain": "stellar",
                "tx_hash": response["hash"],
                "status": TransactionStatus.SUCCESS.value
            }

        except Exception as e:
            return {"success": False, "error": str(e)}

    async def get_transaction(self, tx_hash: str) -> Dict:
        try:
            tx = self.server.transactions().transaction(tx_hash).call()

            return {
                "success": True,
                "chain": "stellar",
                "tx_hash": tx_hash,
                "status": TransactionStatus.SUCCESS.value,
                "created_at": tx.get('created_at'),
                "source_account": tx.get('source_account'),
                "fee": tx.get('fee_charged')
            }

        except Exception as e:
            return {"success": False, "error": str(e)}

    async def get_transaction_history(self, address: str, limit: int = 10) -> List[Dict]:
        try:
            txs = self.server.transactions().for_account(address).limit(limit).order(desc=True).call()

            return {
                "success": True,
                "chain": "stellar",
                "address": address,
                "transactions": [
                    {
                        "tx_hash": tx["hash"],
                        "created_at": tx["created_at"],
                        "source_account": tx["source_account"],
                        "fee": tx["fee_charged"]
                    }
                    for tx in txs.get("_embedded", {}).get("records", [])
                ]
            }

        except Exception as e:
            return {"success": False, "error": str(e)}

class EthereumAdapter(ChainAdapter):
    """Ethereum blockchain adapter"""

    def __init__(self, rpc_url: str = None, network: str = "mainnet"):
        from web3 import Web3

        self.network = network
        self.rpc_url = rpc_url or "https://eth.llamarpc.com"
        self.web3 = Web3(Web3.HTTPProvider(self.rpc_url))

    async def get_balance(self, address: str, asset: Optional[str] = None) -> Dict:
        try:
            if not asset or asset.upper() == "ETH":
                # Native ETH balance
                balance_wei = self.web3.eth.get_balance(address)
                balance_eth = self.web3.from_wei(balance_wei, 'ether')

                return {
                    "success": True,
                    "chain": "ethereum",
                    "address": address,
                    "balances": [{
                        "asset": "ETH",
                        "balance": float(balance_eth)
                    }]
                }
            else:
                # ERC-20 token balance (requires contract address)
                # Placeholder for ERC-20 implementation
                return {
                    "success": False,
                    "error": "ERC-20 token balance not yet implemented"
                }

        except Exception as e:
            return {"success": False, "error": str(e)}

    async def send_transaction(
        self,
        from_address: str,
        to_address: str,
        amount: float,
        asset: Optional[str] = None,
        private_key: str = None
    ) -> Dict:
        try:
            from eth_account import Account

            account = Account.from_key(private_key)

            # Build transaction
            nonce = self.web3.eth.get_transaction_count(from_address)

            transaction = {
                'nonce': nonce,
                'to': to_address,
                'value': self.web3.to_wei(amount, 'ether'),
                'gas': 21000,
                'gasPrice': self.web3.eth.gas_price,
                'chainId': self.web3.eth.chain_id
            }

            # Sign and send
            signed_tx = account.sign_transaction(transaction)
            tx_hash = self.web3.eth.send_raw_transaction(signed_tx.rawTransaction)

            return {
                "success": True,
                "chain": "ethereum",
                "tx_hash": tx_hash.hex(),
                "status": TransactionStatus.PENDING.value
            }

        except Exception as e:
            return {"success": False, "error": str(e)}

    async def get_transaction(self, tx_hash: str) -> Dict:
        try:
            tx = self.web3.eth.get_transaction(tx_hash)
            receipt = self.web3.eth.get_transaction_receipt(tx_hash)

            status = TransactionStatus.SUCCESS if receipt['status'] == 1 else TransactionStatus.FAILED

            return {
                "success": True,
                "chain": "ethereum",
                "tx_hash": tx_hash,
                "status": status.value,
                "from": tx['from'],
                "to": tx['to'],
                "value": float(self.web3.from_wei(tx['value'], 'ether')),
                "gas_used": receipt['gasUsed']
            }

        except Exception as e:
            return {"success": False, "error": str(e)}

    async def get_transaction_history(self, address: str, limit: int = 10) -> List[Dict]:
        # Ethereum doesn't have a built-in transaction history endpoint
        # Need to use external service like Etherscan API
        return {
            "success": False,
            "error": "Transaction history requires Etherscan API integration"
        }

class ChainRegistry:
    """Registry of supported chains and their adapters"""

    def __init__(self):
        self.adapters = {}

    def register_chain(self, chain: Chain, adapter: ChainAdapter):
        """Register chain adapter"""
        self.adapters[chain] = adapter

    def get_adapter(self, chain: Chain) -> ChainAdapter:
        """Get adapter for chain"""
        if chain not in self.adapters:
            raise ValueError(f"Chain {chain} not registered")
        return self.adapters[chain]

    def get_supported_chains(self) -> List[Chain]:
        """Get list of supported chains"""
        return list(self.adapters.keys())

# Global registry
chain_registry = ChainRegistry()
chain_registry.register_chain(Chain.STELLAR, StellarAdapter(network="testnet"))
chain_registry.register_chain(Chain.ETHEREUM, EthereumAdapter(network="mainnet"))
```

#### 1.4 API Endpoints (2-3 hours)

**New File:** `backend/api/routes/portfolio.py`

```python
"""
Portfolio API Routes
"""
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import logging

from api.dependencies import get_current_user
from portfolio.manager import PortfolioManager, Chain, ChainAccount
from wallet.import_export import WalletBridge

logger = logging.getLogger(__name__)
router = APIRouter()

# Request/Response Models
class CreateCollectionRequest(BaseModel):
    name: str
    description: Optional[str] = None
    tags: Optional[List[str]] = None

class ImportPrivateKeyRequest(BaseModel):
    collection_name: str
    private_key: str
    chain: str
    account_name: Optional[str] = None

class ImportMnemonicRequest(BaseModel):
    collection_name: str
    mnemonic: str
    chains: List[str]
    derivation_paths: Optional[Dict[str, str]] = None

class ExportRequest(BaseModel):
    collection_name: str
    address: str
    export_format: str  # "private_key", "keystore", "summary"
    password: Optional[str] = None  # Required for keystore

# Endpoints

@router.post("/collections")
async def create_collection(
    request: CreateCollectionRequest,
    current_user: dict = Depends(get_current_user)
):
    """Create new account collection"""
    try:
        manager = PortfolioManager(current_user['id'])
        result = manager.create_collection(
            collection_name=request.name,
            metadata={
                "description": request.description,
                "tags": request.tags
            }
        )

        return result

    except Exception as e:
        logger.error(f"Error creating collection: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/collections")
async def list_collections(
    current_user: dict = Depends(get_current_user)
):
    """List all collections for user"""
    try:
        manager = PortfolioManager(current_user['id'])
        collections = manager.list_collections()

        return {
            "success": True,
            "collections": collections
        }

    except Exception as e:
        logger.error(f"Error listing collections: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/collections/{collection_name}/accounts")
async def get_collection_accounts(
    collection_name: str,
    chain: Optional[str] = None,
    current_user: dict = Depends(get_current_user)
):
    """Get accounts in collection"""
    try:
        manager = PortfolioManager(current_user['id'])

        chain_enum = Chain(chain) if chain else None
        accounts = manager.get_accounts_in_collection(collection_name, chain_enum)

        # Enhance with on-chain balances
        from chains.abstraction import chain_registry

        enhanced_accounts = []
        for account in accounts:
            try:
                adapter = chain_registry.get_adapter(Chain(account["chain"]))
                balance_data = await adapter.get_balance(account["address"])

                account["balances"] = balance_data.get("balances", [])
            except Exception as e:
                logger.warning(f"Could not fetch balance for {account['address']}: {e}")
                account["balances"] = []

            enhanced_accounts.append(account)

        return {
            "success": True,
            "collection": collection_name,
            "accounts": enhanced_accounts
        }

    except Exception as e:
        logger.error(f"Error getting collection accounts: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/import/private-key")
async def import_from_private_key(
    request: ImportPrivateKeyRequest,
    current_user: dict = Depends(get_current_user)
):
    """Import account from private key"""
    try:
        manager = PortfolioManager(current_user['id'])
        bridge = WalletBridge(manager)

        result = bridge.import_from_private_key(
            collection_name=request.collection_name,
            private_key=request.private_key,
            chain=Chain(request.chain),
            account_name=request.account_name
        )

        if not result.success:
            raise HTTPException(status_code=400, detail=result.errors)

        return {
            "success": True,
            "accounts": [
                {
                    "chain": acc.chain.value,
                    "address": acc.address,
                    "name": acc.metadata.get("name")
                }
                for acc in result.accounts
            ]
        }

    except Exception as e:
        logger.error(f"Error importing private key: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/import/mnemonic")
async def import_from_mnemonic(
    request: ImportMnemonicRequest,
    current_user: dict = Depends(get_current_user)
):
    """Import accounts from mnemonic phrase"""
    try:
        manager = PortfolioManager(current_user['id'])
        bridge = WalletBridge(manager)

        chains = [Chain(c) for c in request.chains]
        derivation_paths = {Chain(k): v for k, v in request.derivation_paths.items()} if request.derivation_paths else None

        result = bridge.import_from_mnemonic(
            collection_name=request.collection_name,
            mnemonic=request.mnemonic,
            chains=chains,
            derivation_paths=derivation_paths
        )

        response = {
            "success": result.success,
            "accounts": [
                {
                    "chain": acc.chain.value,
                    "address": acc.address,
                    "name": acc.metadata.get("name"),
                    "derivation_path": acc.derivation_path
                }
                for acc in result.accounts
            ]
        }

        if result.errors:
            response["warnings"] = result.errors

        return response

    except Exception as e:
        logger.error(f"Error importing mnemonic: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/export")
async def export_account(
    request: ExportRequest,
    current_user: dict = Depends(get_current_user)
):
    """Export account in specified format"""
    try:
        manager = PortfolioManager(current_user['id'])
        bridge = WalletBridge(manager)

        if request.export_format == "private_key":
            result = bridge.export_to_private_key(request.collection_name, request.address)

        elif request.export_format == "keystore":
            if not request.password:
                raise HTTPException(status_code=400, detail="Password required for keystore export")
            result = bridge.export_to_keystore(request.collection_name, request.address, request.password)

        elif request.export_format == "summary":
            result = bridge.export_collection_summary(request.collection_name)

        else:
            raise HTTPException(status_code=400, detail=f"Unsupported export format: {request.export_format}")

        if not result.get("success"):
            raise HTTPException(status_code=400, detail=result.get("error"))

        return result

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error exporting account: {e}")
        raise HTTPException(status_code=500, detail=str(e))
```

#### 1.5 Frontend Integration (2-3 hours)

**Updates to:** `src/hooks/usePortfolio.ts`

```typescript
/**
 * Portfolio management hook
 */
import { useState, useEffect } from 'react';
import { api } from '@/lib/api';

export interface Collection {
  name: string;
  metadata: {
    description?: string;
    tags?: string[];
    created_at: string;
  };
  account_count: number;
}

export interface ChainAccount {
  chain: string;
  address: string;
  metadata: {
    name?: string;
  };
  balances?: Array<{
    asset: string;
    balance: number;
  }>;
}

export function usePortfolio() {
  const [collections, setCollections] = useState<Collection[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchCollections = async () => {
    try {
      setLoading(true);
      const response = await api.get('/api/portfolio/collections');
      setCollections(response.data.collections);
      setError(null);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const createCollection = async (name: string, description?: string, tags?: string[]) => {
    try {
      setLoading(true);
      await api.post('/api/portfolio/collections', { name, description, tags });
      await fetchCollections(); // Refresh
      setError(null);
    } catch (err) {
      setError(err.message);
      throw err;
    } finally {
      setLoading(false);
    }
  };

  const getCollectionAccounts = async (collectionName: string, chain?: string): Promise<ChainAccount[]> => {
    try {
      const params = chain ? { chain } : {};
      const response = await api.get(`/api/portfolio/collections/${collectionName}/accounts`, { params });
      return response.data.accounts;
    } catch (err) {
      setError(err.message);
      throw err;
    }
  };

  const importFromPrivateKey = async (
    collectionName: string,
    privateKey: string,
    chain: string,
    accountName?: string
  ) => {
    try {
      setLoading(true);
      const response = await api.post('/api/portfolio/import/private-key', {
        collection_name: collectionName,
        private_key: privateKey,
        chain,
        account_name: accountName
      });
      setError(null);
      return response.data;
    } catch (err) {
      setError(err.message);
      throw err;
    } finally {
      setLoading(false);
    }
  };

  const exportAccount = async (
    collectionName: string,
    address: string,
    exportFormat: 'private_key' | 'keystore' | 'summary',
    password?: string
  ) => {
    try {
      setLoading(true);
      const response = await api.post('/api/portfolio/export', {
        collection_name: collectionName,
        address,
        export_format: exportFormat,
        password
      });
      setError(null);
      return response.data;
    } catch (err) {
      setError(err.message);
      throw err;
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchCollections();
  }, []);

  return {
    collections,
    loading,
    error,
    fetchCollections,
    createCollection,
    getCollectionAccounts,
    importFromPrivateKey,
    exportAccount
  };
}
```

---

### Phase 2: Solana + Bitcoin Support (8-10 hours)

- Solana adapter implementation
- Bitcoin adapter implementation
- Additional wallet bridges (Phantom, Ledger)
- Extended testing

### Phase 3: Advanced Features (10-12 hours)

- Hardware wallet integration (Ledger, Trezor)
- Multi-sig support
- Advanced permission system (spending limits, whitelists)
- Portfolio analytics and reporting
- Cross-chain swaps and bridges

---

## Security Considerations

### Private Key Management

1. **Never log private keys** - Strict logging rules
2. **Encrypted at rest** - Multiple encryption layers
3. **Encrypted in transit** - HTTPS/TLS only
4. **Memory security** - Clear sensitive data after use
5. **Audit trails** - Log all access to private keys

### Permission Boundaries

1. **User-level isolation** - Users can only access their portfolios
2. **Collection-level permissions** - Agent permissions per collection
3. **Transaction limits** - Max values enforced
4. **Operation whitelists** - Only allowed operations
5. **User approval** - High-value transactions require confirmation

### Filesystem Security

1. **Restricted permissions** - Files readable only by process owner
2. **Path validation** - Prevent directory traversal
3. **Backup strategy** - Regular encrypted backups
4. **Recovery procedures** - User can restore from passkey

---

## Migration from Current System

### Step 1: Deploy New Portfolio System (Parallel)

- Install new portfolio manager
- Keep existing KeyManager for backwards compatibility
- New accounts use portfolio system
- Old accounts continue using KeyManager

### Step 2: User Migration Flow

- Prompt users to create first collection
- Migrate existing accounts to collection
- Verify migration success
- Archive old keystore

### Step 3: Deprecate KeyManager

- After 100% migration, remove KeyManager
- Update all tools to use portfolio manager
- Clean up old files

---

## Success Metrics

### Technical Success
✅ Multi-chain support (Stellar + Ethereum minimum)
✅ Wallet import/export working
✅ Collection management functional
✅ Encryption verified secure
✅ Permission system enforced
✅ Audit trails complete

### User Success
✅ Existing DeFi users can import wallets
✅ Users can export for custodial control
✅ "Not-your-keys-not-your-crypto" trust established
✅ Multi-chain portfolios manageable
✅ Agent operations across chains seamless

### Business Success
✅ Killer feature for DeFi onboarding
✅ Bridges existing users to agentic world
✅ Legitimacy with blockchain enthusiasts
✅ Competitive advantage in market

---

## Related Documents

- `PASSKEY_ARCHITECTURE_V2.md` - User authentication foundation
- `AGENT_FIRST_ARCHITECTURE_PLAN.md` - Overall architecture
- `CLAUDE.md` - Project overview and conventions

---

**Document Version:** 2.0 (Revised)
**Created:** 2025-11-08
**Status:** Planning - Awaiting approval
**Key Change:** Shifted from single-chain single-account to multi-chain portfolio with wallet bridging
**Next Action:** Review and approve revised plan, then begin Phase 1 implementation
