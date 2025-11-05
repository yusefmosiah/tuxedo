# Wallet Integration Plan: Import/Export Functionality

## Overview

This document outlines the strategy for implementing wallet import/export functionality in Tuxedo AI's passkey-first architecture, providing seamless integration with the existing Stellar ecosystem while maintaining our security-first approach.

## Design Philosophy

### Two-Tier Architecture

**Tier 1: Native Passkey Wallet (Primary)**

- Default experience for all users
- Hardware-backed security via WebAuthn
- Seamless biometric authentication
- Automatic account management

**Tier 2: External Wallet Adapter (Advanced)**

- Power user features
- Migration capabilities
- Legacy wallet support
- Emergency recovery options

## Integration Scenarios

### Scenario 1: Import from External Wallet

**User Story**: "I have an existing Stellar wallet (Freighter, XBull, etc.) and want to use it in Tuxedo"

**Flow**:

1. User selects "Import Existing Wallet"
2. System prompts for wallet connection or secret key
3. User authenticates with passkey (security verification)
4. External wallet is imported and linked to passkey
5. User can now access imported wallet via passkey authentication

### Scenario 2: Export to External Wallet

**User Story**: "I want to use my Tuxedo account in another Stellar wallet"

**Flow**:

1. User selects "Export Account"
2. User authenticates with passkey
3. User selects export format (secret key, seed phrase, QR code)
4. System encrypts export data with passkey
5. User receives export data for external wallet import

### Scenario 3: Dual Account Management

**User Story**: "I want to use both my Tuxedo native account and imported wallet"

**Flow**:

1. User can have multiple accounts linked to their passkey
2. Native passkey-derived account (primary)
3. Imported external wallets (secondary)
4. Easy switching between accounts in UI
5. Unified experience across all accounts

## Technical Implementation

### Wallet Import Service

```python
# backend/services/wallet_import_service.py
import json
import base64
from typing import Dict, Any, Optional
from stellar_sdk.keypair import Keypair
from stellar_sdk.exceptions import Ed25519SecretSeedInvalidError
import hashlib
import hmac

class WalletImportService:
    """Service for importing external Stellar wallets"""

    def __init__(self, db, passkey_service):
        self.db = db
        self.passkey_service = passkey_service

    async def import_from_secret_key(self,
                                   user_id: str,
                                   secret_key: str,
                                   network: str = 'testnet',
                                   friendly_name: Optional[str] = None) -> Dict[str, Any]:
        """Import wallet from Stellar secret key"""

        try:
            # Validate secret key
            keypair = Keypair.from_secret(secret_key)

            # Verify account exists on network
            account_info = await self._get_account_info(keypair.public_key, network)
            if not account_info:
                raise ValueError("Account not found on network")

            # Store imported wallet
            async with self.db.transaction():
                account_id = await self.db.create_stellar_account(
                    user_id=user_id,
                    account_id=keypair.account_id,
                    public_key=keypair.public_key,
                    derivation_salt=None,  # Not derived from passkey
                    network=network,
                    account_type='imported',
                    metadata={
                        'import_method': 'secret_key',
                        'imported_at': datetime.utcnow().isoformat(),
                        'friendly_name': friendly_name
                    }
                )

                # Store encrypted secret key for recovery
                encrypted_secret = await self._encrypt_secret_key(user_id, secret_key)
                await self.db.create_recovery_option(
                    user_id=user_id,
                    recovery_type='encrypted_secret',
                    recovery_data=encrypted_secret,
                    recovery_hint=f"Imported account {keypair.public_key[:8]}..."
                )

            return {
                'success': True,
                'account_id': account_id,
                'public_key': keypair.public_key,
                'account_info': account_info
            }

        except Ed25519SecretSeedInvalidError:
            raise ValueError("Invalid secret key format")
        except Exception as e:
            raise ValueError(f"Import failed: {str(e)}")

    async def import_from_seed_phrase(self,
                                    user_id: str,
                                    seed_phrase: str,
                                    derivation_path: str = "m/44'/148'/0'",
                                    network: str = 'testnet',
                                    friendly_name: Optional[str] = None) -> Dict[str, Any]:
        """Import wallet from BIP39 seed phrase"""

        try:
            # Validate seed phrase
            if not self._validate_seed_phrase(seed_phrase):
                raise ValueError("Invalid seed phrase")

            # Derive keypair from seed phrase
            keypair = await self._derive_from_seed_phrase(seed_phrase, derivation_path)

            # Verify account exists
            account_info = await self._get_account_info(keypair.public_key, network)

            # Store imported wallet
            async with self.db.transaction():
                account_id = await self.db.create_stellar_account(
                    user_id=user_id,
                    account_id=keypair.account_id,
                    public_key=keypair.public_key,
                    derivation_salt=None,
                    network=network,
                    account_type='imported',
                    metadata={
                        'import_method': 'seed_phrase',
                        'derivation_path': derivation_path,
                        'imported_at': datetime.utcnow().isoformat(),
                        'friendly_name': friendly_name
                    }
                )

                # Store encrypted seed phrase
                encrypted_seed = await self._encrypt_seed_phrase(user_id, seed_phrase)
                await self.db.create_recovery_option(
                    user_id=user_id,
                    recovery_type='encrypted_seed',
                    recovery_data=encrypted_seed,
                    recovery_hint=f"Seed phrase imported account"
                )

            return {
                'success': True,
                'account_id': account_id,
                'public_key': keypair.public_key,
                'account_info': account_info
            }

        except Exception as e:
            raise ValueError(f"Seed phrase import failed: {str(e)}")

    async def import_from_wallet_connect(self,
                                       user_id: str,
                                       wallet_type: str,  # 'freighter', 'xbull', 'albedo'
                                       network: str = 'testnet') -> Dict[str, Any]:
        """Import wallet via wallet connection"""

        try:
            # This would integrate with wallet-specific APIs
            if wallet_type == 'freighter':
                account_info = await self._connect_freighter(network)
            elif wallet_type == 'xbull':
                account_info = await self._connect_xbull(network)
            elif wallet_type == 'albedo':
                account_info = await self._connect_albedo(network)
            else:
                raise ValueError(f"Unsupported wallet type: {wallet_type}")

            # Store connected wallet
            async with self.db.transaction():
                account_id = await self.db.create_stellar_account(
                    user_id=user_id,
                    account_id=account_info['account_id'],
                    public_key=account_info['public_key'],
                    derivation_salt=None,
                    network=network,
                    account_type='connected',
                    metadata={
                        'import_method': 'wallet_connect',
                        'wallet_type': wallet_type,
                        'connected_at': datetime.utcnow().isoformat()
                    }
                )

            return {
                'success': True,
                'account_id': account_id,
                'public_key': account_info['public_key'],
                'account_info': account_info
            }

        except Exception as e:
            raise ValueError(f"Wallet connection failed: {str(e)}")

    def _validate_seed_phrase(self, seed_phrase: str) -> bool:
        """Validate BIP39 seed phrase"""
        words = seed_phrase.strip().split()
        return len(words) in [12, 15, 18, 21, 24] and all(word.isalpha() for word in words)

    async def _derive_from_seed_phrase(self, seed_phrase: str, derivation_path: str) -> Keypair:
        """Derive Stellar keypair from BIP39 seed phrase"""
        # Implementation would use BIP39/BIP32 libraries
        # This is a simplified example
        import mnemonic
        from bip32utils import BIP32Key

        # Convert seed phrase to seed
        m = mnemonic.Mnemonic("english")
        seed = m.to_seed(seed_phrase)

        # Derive key using BIP32
        root = BIP32Key.fromEntropy(seed)

        # Parse derivation path and derive child key
        # For Stellar: m/44'/148'/0'/accountIndex'
        child_key = root.ChildKey(44).ChildKey(148).ChildKey(0).ChildKey(0)

        return Keypair.from_secret(child_key.PrivateKey())

    async def _encrypt_secret_key(self, user_id: str, secret_key: str) -> str:
        """Encrypt secret key with user's passkey-derived encryption key"""
        # Get user's passkey-derived encryption key
        encryption_key = await self._get_user_encryption_key(user_id)

        # Encrypt secret key
        from cryptography.fernet import Fernet
        f = Fernet(encryption_key)
        encrypted = f.encrypt(secret_key.encode())

        return base64.b64encode(encrypted).decode()

    async def _encrypt_seed_phrase(self, user_id: str, seed_phrase: str) -> str:
        """Encrypt seed phrase with user's passkey-derived encryption key"""
        encryption_key = await self._get_user_encryption_key(user_id)

        from cryptography.fernet import Fernet
        f = Fernet(encryption_key)
        encrypted = f.encrypt(seed_phrase.encode())

        return base64.b64encode(encrypted).decode()

    async def _get_user_encryption_key(self, user_id: str) -> bytes:
        """Get user's passkey-derived encryption key"""
        # This would derive an encryption key from the user's passkey
        # For security, this requires user authentication
        pass
```

### Wallet Export Service

```python
# backend/services/wallet_export_service.py
import base64
import io
import qrcode
from typing import Dict, Any, Optional
from PIL import Image
from stellar_sdk.keypair import Keypair

class WalletExportService:
    """Service for exporting Stellar accounts"""

    def __init__(self, db, passkey_service):
        self.db = db
        self.passkey_service = passkey_service

    async def export_account(self,
                           user_id: str,
                           account_id: str,
                           export_format: str,
                           encryption_method: str = 'passkey') -> Dict[str, Any]:
        """Export account in specified format"""

        # Verify user owns the account
        account = await self.db.get_user_account(user_id, account_id)
        if not account:
            raise ValueError("Account not found or access denied")

        # Verify user authentication (biometric required for export)
        await self._verify_user_authentication(user_id)

        # Get account secrets
        if account['account_type'] == 'passkey-derived':
            # Re-derive from passkey
            secret_key = await self._derive_secret_from_passkey(user_id, account_id)
        elif account['account_type'] == 'imported':
            # Retrieve encrypted secret
            secret_key = await self._decrypt_secret_key(user_id, account_id)
        else:
            raise ValueError(f"Cannot export account type: {account['account_type']}")

        # Export in requested format
        if export_format == 'secret_key':
            return await self._export_secret_key(secret_key, encryption_method)
        elif export_format == 'seed_phrase':
            return await self._export_seed_phrase(secret_key, encryption_method)
        elif export_format == 'qr_code':
            return await self._export_qr_code(secret_key, encryption_method)
        else:
            raise ValueError(f"Unsupported export format: {export_format}")

    async def _export_secret_key(self, secret_key: str, encryption_method: str) -> Dict[str, Any]:
        """Export account as secret key"""

        if encryption_method == 'passkey':
            # Encrypt with passkey (requires re-authentication)
            encrypted_secret = await self._encrypt_with_passkey_verification(secret_key)
            return {
                'format': 'encrypted_secret_key',
                'data': encrypted_secret,
                'requires_passkey': True,
                'expires_at': (datetime.utcnow() + timedelta(hours=1)).isoformat()
            }
        else:
            # Plain text (not recommended for production)
            return {
                'format': 'secret_key',
                'data': secret_key,
                'warning': 'Plain text secret key - handle with extreme care',
                'expires_at': (datetime.utcnow() + timedelta(minutes=5)).isoformat()
            }

    async def _export_seed_phrase(self, secret_key: str, encryption_method: str) -> Dict[str, Any]:
        """Export account as seed phrase (if available)"""

        # Check if seed phrase is available
        # This would only work for accounts imported from seed phrases

        if encryption_method == 'passkey':
            encrypted_seed = await self._encrypt_with_passkey_verification(seed_phrase)
            return {
                'format': 'encrypted_seed_phrase',
                'data': encrypted_seed,
                'requires_passkey': True,
                'expires_at': (datetime.utcnow() + timedelta(hours=1)).isoformat()
            }
        else:
            return {
                'format': 'seed_phrase',
                'data': seed_phrase,
                'warning': 'Plain text seed phrase - handle with extreme care',
                'expires_at': (datetime.utcnow() + timedelta(minutes=5)).isoformat()
            }

    async def _export_qr_code(self, secret_key: str, encryption_method: str) -> Dict[str, Any]:
        """Export account as QR code"""

        if encryption_method == 'passkey':
            # Create encrypted data for QR code
            encrypted_data = await self._encrypt_with_passkey_verification(secret_key)
            qr_data = f"tuxedo://encrypted/{encrypted_data}"
        else:
            # Create plain QR code (not recommended)
            qr_data = f"stellar:{secret_key}"

        # Generate QR code
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(qr_data)
        qr.make(fit=True)

        # Convert to image
        img = qr.make_image(fill_color="black", back_color="white")
        buffered = io.BytesIO()
        img.save(buffered, format="PNG")
        img_base64 = base64.b64encode(buffered.getvalue()).decode()

        return {
            'format': 'qr_code',
            'data': f"data:image/png;base64,{img_base64}",
            'requires_passkey': encryption_method == 'passkey',
            'expires_at': (datetime.utcnow() + timedelta(hours=1)).isoformat(),
            'instructions': 'Scan with compatible wallet app'
        }

    async def _verify_user_authentication(self, user_id: str):
        """Verify user is authenticated with biometrics"""
        # This would require a fresh WebAuthn authentication
        # to ensure the account owner is performing the export
        pass

    async def _encrypt_with_passkey_verification(self, data: str) -> str:
        """Encrypt data requiring fresh passkey verification"""
        # Implementation would require user to re-authenticate
        # and use fresh PRF output for encryption
        pass
```

### Frontend Integration

```typescript
// src/services/walletService.ts
import { PasskeyAuthService } from "./passkeyAuth";

export class WalletService {
  private passkeyService: PasskeyAuthService;
  private baseUrl: string;

  constructor() {
    this.passkeyService = new PasskeyAuthService();
    this.baseUrl = process.env.VITE_API_URL || "http://localhost:8000";
  }

  async importFromSecretKey(
    secretKey: string,
    friendlyName?: string,
  ): Promise<ImportResult> {
    const sessionToken = localStorage.getItem("session_token");
    if (!sessionToken) {
      throw new Error("No active session");
    }

    const response = await fetch(`${this.baseUrl}/wallets/import/secret-key`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${sessionToken}`,
        "X-CSRF-Token": localStorage.getItem("csrf_token") || "",
      },
      body: JSON.stringify({
        secret_key: secretKey,
        network: "testnet",
        friendly_name: friendlyName,
      }),
    });

    const result = await response.json();

    if (result.success) {
      return {
        success: true,
        account: result,
        message: "Wallet imported successfully",
      };
    } else {
      throw new Error(result.error || "Import failed");
    }
  }

  async importFromSeedPhrase(
    seedPhrase: string,
    friendlyName?: string,
  ): Promise<ImportResult> {
    const sessionToken = localStorage.getItem("session_token");
    if (!sessionToken) {
      throw new Error("No active session");
    }

    const response = await fetch(`${this.baseUrl}/wallets/import/seed-phrase`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${sessionToken}`,
        "X-CSRF-Token": localStorage.getItem("csrf_token") || "",
      },
      body: JSON.stringify({
        seed_phrase: seedPhrase,
        derivation_path: "m/44'/148'/0'",
        network: "testnet",
        friendly_name: friendlyName,
      }),
    });

    const result = await response.json();

    if (result.success) {
      return {
        success: true,
        account: result,
        message: "Seed phrase imported successfully",
      };
    } else {
      throw new Error(result.error || "Import failed");
    }
  }

  async importFromWallet(
    walletType: "freighter" | "xbull" | "albedo",
  ): Promise<ImportResult> {
    const sessionToken = localStorage.getItem("session_token");
    if (!sessionToken) {
      throw new Error("No active session");
    }

    // Connect to wallet
    let accountInfo;
    try {
      if (walletType === "freighter") {
        accountInfo = await this.connectFreighter();
      } else if (walletType === "xbull") {
        accountInfo = await this.connectXbull();
      } else if (walletType === "albedo") {
        accountInfo = await this.connectAlbedo();
      }
    } catch (error) {
      throw new Error(`Failed to connect to ${walletType}: ${error.message}`);
    }

    const response = await fetch(
      `${this.baseUrl}/wallets/import/wallet-connect`,
      {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${sessionToken}`,
          "X-CSRF-Token": localStorage.getItem("csrf_token") || "",
        },
        body: JSON.stringify({
          wallet_type: walletType,
          account_info: accountInfo,
          network: "testnet",
        }),
      },
    );

    const result = await response.json();

    if (result.success) {
      return {
        success: true,
        account: result,
        message: `${walletType} wallet connected successfully`,
      };
    } else {
      throw new Error(result.error || "Wallet connection failed");
    }
  }

  async exportAccount(
    accountId: string,
    format: "secret_key" | "seed_phrase" | "qr_code",
  ): Promise<ExportResult> {
    const sessionToken = localStorage.getItem("session_token");
    if (!sessionToken) {
      throw new Error("No active session");
    }

    // Require fresh authentication for security
    try {
      await this.passkeyService.authenticate();
    } catch (error) {
      throw new Error("Biometric authentication required for export");
    }

    const response = await fetch(`${this.baseUrl}/wallets/export`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${sessionToken}`,
        "X-CSRF-Token": localStorage.getItem("csrf_token") || "",
      },
      body: JSON.stringify({
        account_id: accountId,
        export_format: format,
        encryption_method: "passkey",
      }),
    });

    const result = await response.json();

    if (result.success) {
      return {
        success: true,
        exportData: result.export_data,
        message: "Account exported successfully",
      };
    } else {
      throw new Error(result.error || "Export failed");
    }
  }

  private async connectFreighter(): Promise<AccountInfo> {
    return new Promise((resolve, reject) => {
      // @ts-ignore - Freighter global
      if (!window.freight) {
        reject(new Error("Freighter wallet not installed"));
        return;
      }

      // @ts-ignore
      window.freight
        .connect()
        .then((address: string) => {
          resolve({
            public_key: address,
            account_id: address,
            wallet_type: "freighter",
          });
        })
        .catch(reject);
    });
  }

  private async connectXbull(): Promise<AccountInfo> {
    // Similar implementation for XBull
    throw new Error("XBull integration not implemented yet");
  }

  private async connectAlbedo(): Promise<AccountInfo> {
    return new Promise((resolve, reject) => {
      // Use Albedo's popup-based authentication
      const popup = window.open(
        "https://albedo.link/connect?protocol=stellar",
        "_blank",
        "width=400,height=600",
      );

      if (!popup) {
        reject(new Error("Popup blocked - please allow popups"));
        return;
      }

      const messageHandler = (event: MessageEvent) => {
        if (event.origin !== "https://albedo.link") return;

        if (event.data.type === "onConnected") {
          window.removeEventListener("message", messageHandler);
          popup.close();

          resolve({
            public_key: event.data.pubkey,
            account_id: event.data.pubkey,
            wallet_type: "albedo",
          });
        }
      };

      window.addEventListener("message", messageHandler);
    });
  }
}
```

### React Components

```typescript
// src/components/wallet/WalletImportModal.tsx
import React, { useState } from 'react';
import { Modal, Button, Alert } from '@stellar/design-system';
import { WalletService } from '../../services/walletService';

interface WalletImportModalProps {
  isOpen: boolean;
  onClose: () => void;
  onImportSuccess: (account: any) => void;
}

export function WalletImportModal({ isOpen, onClose, onImportSuccess }: WalletImportModalProps) {
  const [importMethod, setImportMethod] = useState<'secret-key' | 'seed-phrase' | 'wallet-connect'>('secret-key');
  const [secretKey, setSecretKey] = useState('');
  const [seedPhrase, setSeedPhrase] = useState('');
  const [walletType, setWalletType] = useState<'freighter' | 'xbull' | 'albedo'>('freighter');
  const [friendlyName, setFriendlyName] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const walletService = new WalletService();

  const handleImport = async () => {
    setError(null);
    setIsLoading(true);

    try {
      let result;

      switch (importMethod) {
        case 'secret-key':
          if (!secretKey.trim()) {
            throw new Error('Secret key is required');
          }
          result = await walletService.importFromSecretKey(secretKey, friendlyName || undefined);
          break;

        case 'seed-phrase':
          if (!seedPhrase.trim()) {
            throw new Error('Seed phrase is required');
          }
          result = await walletService.importFromSeedPhrase(seedPhrase, friendlyName || undefined);
          break;

        case 'wallet-connect':
          result = await walletService.importFromWallet(walletType);
          break;

        default:
          throw new Error('Invalid import method');
      }

      if (result.success) {
        onImportSuccess(result.account);
        onClose();
        // Reset form
        setSecretKey('');
        setSeedPhrase('');
        setFriendlyName('');
      }
    } catch (error) {
      setError(error instanceof Error ? error.message : 'Import failed');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <Modal isOpen={isOpen} onClose={onClose} title="Import External Wallet">
      <div className="space-y-4">
        {error && (
          <Alert variant="error">{error}</Alert>
        )}

        <div>
          <label className="block text-sm font-medium mb-2">Import Method</label>
          <select
            value={importMethod}
            onChange={(e) => setImportMethod(e.target.value as any)}
            className="w-full p-2 border rounded"
          >
            <option value="secret-key">Secret Key</option>
            <option value="seed-phrase">Seed Phrase</option>
            <option value="wallet-connect">Connect Wallet</option>
          </select>
        </div>

        {importMethod === 'secret-key' && (
          <div>
            <label className="block text-sm font-medium mb-2">Secret Key</label>
            <input
              type="password"
              value={secretKey}
              onChange={(e) => setSecretKey(e.target.value)}
              placeholder="S..."
              className="w-full p-2 border rounded"
            />
          </div>
        )}

        {importMethod === 'seed-phrase' && (
          <div>
            <label className="block text-sm font-medium mb-2">Seed Phrase</label>
            <textarea
              value={seedPhrase}
              onChange={(e) => setSeedPhrase(e.target.value)}
              placeholder="Enter your 12 or 24-word seed phrase"
              className="w-full p-2 border rounded h-24"
            />
          </div>
        )}

        {importMethod === 'wallet-connect' && (
          <div>
            <label className="block text-sm font-medium mb-2">Wallet Type</label>
            <select
              value={walletType}
              onChange={(e) => setWalletType(e.target.value as any)}
              className="w-full p-2 border rounded"
            >
              <option value="freighter">Freighter</option>
              <option value="xbull">XBull</option>
              <option value="albedo">Albedo</option>
            </select>
          </div>
        )}

        <div>
          <label className="block text-sm font-medium mb-2">Friendly Name (Optional)</label>
          <input
            type="text"
            value={friendlyName}
            onChange={(e) => setFriendlyName(e.target.value)}
            placeholder="My Trading Wallet"
            className="w-full p-2 border rounded"
          />
        </div>

        <div className="flex justify-end space-x-2">
          <Button variant="secondary" onClick={onClose}>
            Cancel
          </Button>
          <Button onClick={handleImport} isLoading={isLoading}>
            Import Wallet
          </Button>
        </div>
      </div>
    </Modal>
  );
}
```

```typescript
// src/components/wallet/WalletExportModal.tsx
import React, { useState } from 'react';
import { Modal, Button, Alert } from '@stellar/design-system';
import { WalletService } from '../../services/walletService';

interface WalletExportModalProps {
  isOpen: boolean;
  onClose: () => void;
  accountId: string;
  accountName: string;
}

export function WalletExportModal({ isOpen, onClose, accountId, accountName }: WalletExportModalProps) {
  const [exportFormat, setExportFormat] = useState<'secret_key' | 'seed_phrase' | 'qr_code'>('qr_code');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [exportData, setExportData] = useState<any>(null);

  const walletService = new WalletService();

  const handleExport = async () => {
    setError(null);
    setIsLoading(true);

    try {
      const result = await walletService.exportAccount(accountId, exportFormat);

      if (result.success) {
        setExportData(result.exportData);
      }
    } catch (error) {
      setError(error instanceof Error ? error.message : 'Export failed');
    } finally {
      setIsLoading(false);
    }
  };

  const renderExportData = () => {
    if (!exportData) return null;

    switch (exportData.format) {
      case 'qr_code':
        return (
          <div className="text-center">
            <img src={exportData.data} alt="QR Code" className="mx-auto" />
            <p className="text-sm text-gray-600 mt-2">
              Scan with a compatible wallet app
            </p>
            {exportData.expires_at && (
              <p className="text-xs text-orange-600 mt-1">
                Expires: {new Date(exportData.expires_at).toLocaleString()}
              </p>
            )}
          </div>
        );

      case 'encrypted_secret_key':
      case 'encrypted_seed_phrase':
        return (
          <div className="bg-yellow-50 p-4 rounded border">
            <p className="font-medium text-yellow-800">Encrypted Export Data</p>
            <p className="text-sm text-yellow-600 mt-1">
              This data is encrypted with your passkey and can only be decrypted with biometric authentication.
            </p>
            <textarea
              value={exportData.data}
              readOnly
              className="w-full mt-2 p-2 border rounded font-mono text-xs"
              rows={4}
            />
            {exportData.expires_at && (
              <p className="text-xs text-orange-600 mt-2">
                Expires: {new Date(exportData.expires_at).toLocaleString()}
              </p>
            )}
          </div>
        );

      default:
        return (
          <div className="bg-red-50 p-4 rounded border">
            <p className="font-medium text-red-800">⚠️ Plain Text Export</p>
            <p className="text-sm text-red-600 mt-1">
              Handle this data with extreme care. Anyone with access can control your account.
            </p>
            <textarea
              value={exportData.data}
              readOnly
              className="w-full mt-2 p-2 border rounded font-mono text-xs bg-red-100"
              rows={4}
            />
            {exportData.expires_at && (
              <p className="text-xs text-orange-600 mt-2">
                Expires: {new Date(exportData.expires_at).toLocaleString()}
              </p>
            )}
          </div>
        );
    }
  };

  return (
    <Modal isOpen={isOpen} onClose={onClose} title={`Export ${accountName}`}>
      <div className="space-y-4">
        {error && (
          <Alert variant="error">{error}</Alert>
        )}

        <Alert variant="warning">
          Exporting account credentials can expose your funds to security risks. Only export to trusted wallets and keep your export data secure.
        </Alert>

        {!exportData ? (
          <>
            <div>
              <label className="block text-sm font-medium mb-2">Export Format</label>
              <select
                value={exportFormat}
                onChange={(e) => setExportFormat(e.target.value as any)}
                className="w-full p-2 border rounded"
              >
                <option value="qr_code">QR Code (Recommended)</option>
                <option value="secret_key">Encrypted Secret Key</option>
                <option value="seed_phrase">Encrypted Seed Phrase</option>
              </select>
            </div>

            <div className="flex justify-end space-x-2">
              <Button variant="secondary" onClick={onClose}>
                Cancel
              </Button>
              <Button onClick={handleExport} isLoading={isLoading}>
                Export Account
              </Button>
            </div>
          </>
        ) : (
          <>
            {renderExportData()}

            <div className="flex justify-end space-x-2">
              <Button variant="secondary" onClick={() => setExportData(null)}>
                Export Another
              </Button>
              <Button onClick={onClose}>
                Done
              </Button>
            </div>
          </>
        )}
      </div>
    </Modal>
  );
}
```

## Security Considerations

### Import Security

1. **Authentication Required**: All imports require valid passkey authentication
2. **Account Verification**: Verify imported accounts exist on network
3. **Rate Limiting**: Prevent brute force import attempts
4. **Validation**: Proper validation of secret keys and seed phrases
5. **Encryption**: Store imported secrets encrypted with passkey-derived keys

### Export Security

1. **Biometric Verification**: Fresh biometric authentication required for all exports
2. **Time Limits**: Export data expires after limited time
3. **Encryption**: Export data encrypted by default
4. **Audit Logging**: All export attempts logged for security monitoring
5. **User Warnings**: Clear security warnings and user education

### Data Protection

1. **No Plain Text Storage**: Never store unencrypted secrets
2. **Passkey-Derived Encryption**: Use passkey PRF for encryption keys
3. **Secure Transmission**: Always use HTTPS for sensitive data
4. **Memory Safety**: Clear sensitive data from memory when possible
5. **Limited Retention**: Minimize storage of sensitive export data

## User Experience Flow

### Import Flow

1. User selects "Import Wallet"
2. User chooses import method
3. User provides import data (secret key/seed phrase/wallet connection)
4. System validates import data
5. User authenticates with passkey
6. System imports and links wallet to user account
7. User receives confirmation and can start using imported wallet

### Export Flow

1. User selects "Export Account"
2. User chooses account to export
3. User selects export format
4. System shows security warning
5. User authenticates with biometrics
6. System generates export data
7. User receives export data with clear instructions
8. Export data expires after time limit

## Testing Strategy

### Import Testing

- Test valid secret key import
- Test valid seed phrase import
- Test wallet connection import
- Test invalid data rejection
- Test authentication requirement
- Test duplicate account handling

### Export Testing

- Test QR code generation
- Test encrypted export
- Test biometric authentication requirement
- Test expiration functionality
- Test format validation
- Test audit logging

### Security Testing

- Test authentication bypass attempts
- Test export data encryption
- Test rate limiting
- Test session validation
- Test CSRF protection
- Test data leakage prevention

This comprehensive wallet integration plan provides secure, user-friendly import/export functionality while maintaining Tuxedo's security-first approach and seamless user experience.
