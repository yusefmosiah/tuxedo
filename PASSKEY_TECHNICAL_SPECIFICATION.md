# Passkey Authentication Technical Specification

## Overview

This technical specification details the implementation of passkey-based authentication for Tuxedo AI, leveraging WebAuthn with PRF extensions for deterministic Stellar account derivation.

## System Architecture

### Core Components

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Frontend      │    │     Backend      │    │   Authenticator │
│                 │    │                  │    │   (Device)      │
│ WebAuthn API    │◄──►│  Passkey Service │◄──►│ Secure Enclave  │
│ PRF Extension   │    │  Crypto Service  │    │  / TPM          │
│ Stellar SDK     │    │  Account Manager │    │                 │
│ UI Components   │    │  Session Manager │    │                 │
└─────────────────┘    └──────────────────┘    └─────────────────┘
         │                       │                       │
         │                       │                       │
         └───────────────────────┼───────────────────────┘
                                 │
                                 ▼
                    ┌─────────────────┐
                    │  Stellar Network│
                    │                 │
                    │  Account Mgmt   │
                    │  Transactions   │
                    │  Smart Contracts│
                    └─────────────────┘
```

## Database Schema

### Detailed Schema Definition

```sql
-- Core user table
CREATE TABLE users (
    id TEXT PRIMARY KEY DEFAULT (lower(hex(randomblob(16)))),
    email TEXT UNIQUE,
    credential_id TEXT UNIQUE NOT NULL,
    stellar_public_key TEXT UNIQUE NOT NULL,
    stellar_account_id TEXT UNIQUE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP,
    recovery_methods TEXT DEFAULT '["passkey", "seed"]',
    is_active BOOLEAN DEFAULT TRUE,
    preferences TEXT DEFAULT '{}',
    security_settings TEXT DEFAULT '{"require_biometric": true, "auto_logout_minutes": 60}'
);

-- Passkey credentials with full WebAuthn data
CREATE TABLE passkey_credentials (
    id TEXT PRIMARY KEY DEFAULT (lower(hex(randomblob(16)))),
    user_id TEXT NOT NULL,
    credential_id TEXT UNIQUE NOT NULL,
    credential_public_key TEXT NOT NULL,
    aaguid TEXT,
    sign_count INTEGER DEFAULT 0,
    user_verification TEXT NOT NULL, -- 'required', 'preferred', 'discouraged'
    authenticator_attachment TEXT, -- 'platform', 'cross-platform'
    backup_eligible BOOLEAN DEFAULT FALSE,
    backup_state BOOLEAN DEFAULT FALSE,
    device_type TEXT, -- 'single_device', 'multi_device'
    transports TEXT DEFAULT '["internal", "usb", "nfc", "ble"]',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_used TIMESTAMP,
    is_backup BOOLEAN DEFAULT FALSE,
    friendly_name TEXT,
    FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
);

-- Account derivation data
CREATE TABLE stellar_accounts (
    id TEXT PRIMARY KEY DEFAULT (lower(hex(randomblob(16)))),
    user_id TEXT NOT NULL,
    account_id TEXT UNIQUE NOT NULL,
    public_key TEXT UNIQUE NOT NULL,
    derivation_salt TEXT NOT NULL,
    network TEXT DEFAULT 'testnet',
    account_type TEXT DEFAULT 'passkey-derived', -- 'passkey-derived', 'imported', 'agent-managed'
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_used TIMESTAMP,
    balance_checked TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE,
    metadata TEXT DEFAULT '{}',
    FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
);

-- Recovery methods
CREATE TABLE recovery_options (
    id TEXT PRIMARY KEY DEFAULT (lower(hex(randomblob(16)))),
    user_id TEXT NOT NULL,
    recovery_type TEXT NOT NULL, -- 'seed', 'social', 'cloud', 'hardware'
    recovery_data TEXT NOT NULL, -- Encrypted recovery information
    recovery_hint TEXT,
    is_enabled BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_verified TIMESTAMP,
    verification_count INTEGER DEFAULT 0,
    FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
);

-- Session management
CREATE TABLE user_sessions (
    id TEXT PRIMARY KEY DEFAULT (lower(hex(randomblob(16)))),
    user_id TEXT NOT NULL,
    session_token TEXT UNIQUE NOT NULL,
    csrf_token TEXT UNIQUE,
    expires_at TIMESTAMP NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_accessed TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    ip_address TEXT,
    user_agent TEXT,
    device_fingerprint TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
);

-- Authentication challenges (short-lived)
CREATE TABLE auth_challenges (
    id TEXT PRIMARY KEY DEFAULT (lower(hex(randomblob(16)))),
    user_id TEXT,
    challenge_data TEXT NOT NULL,
    challenge_type TEXT NOT NULL, -- 'registration', 'authentication'
    expires_at TIMESTAMP NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    used_at TIMESTAMP,
    is_used BOOLEAN DEFAULT FALSE,
    FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
);

-- Security events
CREATE TABLE security_events (
    id TEXT PRIMARY KEY DEFAULT (lower(hex(randomblob(16)))),
    user_id TEXT,
    event_type TEXT NOT NULL, -- 'login', 'logout', 'account_creation', 'recovery_used'
    event_data TEXT,
    ip_address TEXT,
    user_agent TEXT,
    success BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
);

-- Indexes for performance
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_stellar_public_key ON users(stellar_public_key);
CREATE INDEX idx_passkey_credentials_user_id ON passkey_credentials(user_id);
CREATE INDEX idx_passkey_credentials_credential_id ON passkey_credentials(credential_id);
CREATE INDEX idx_stellar_accounts_user_id ON stellar_accounts(user_id);
CREATE INDEX idx_stellar_accounts_account_id ON stellar_accounts(account_id);
CREATE INDEX idx_recovery_options_user_id ON recovery_options(user_id);
CREATE INDEX idx_user_sessions_user_id ON user_sessions(user_id);
CREATE INDEX idx_user_sessions_session_token ON user_sessions(session_token);
CREATE INDEX idx_auth_challenges_user_id ON auth_challenges(user_id);
CREATE INDEX idx_security_events_user_id ON security_events(user_id);
CREATE INDEX idx_security_events_created_at ON security_events(created_at);
```

## API Endpoints

### Authentication Routes

#### `POST /auth/passkey/register`

**Purpose**: Register a new passkey for a user

**Request**:

```json
{
  "email": "user@example.com",
  "client_data_json": "...",
  "attestation_object": "...",
  "transports": ["internal", "usb"],
  "friendly_name": "My iPhone"
}
```

**Response**:

```json
{
  "success": true,
  "user": {
    "id": "user_12345",
    "email": "user@example.com",
    "stellar_public_key": "GD...123",
    "stellar_account_id": "0123456789abcdef...",
    "created_at": "2025-01-15T10:30:00Z"
  },
  "credential": {
    "id": "cred_67890",
    "created_at": "2025-01-15T10:30:00Z",
    "backup_eligible": true,
    "backup_state": false
  },
  "account": {
    "account_id": "0123456789abcdef...",
    "public_key": "GD...123",
    "network": "testnet",
    "funded": true
  }
}
```

#### `POST /auth/passkey/authenticate`

**Purpose**: Authenticate with existing passkey

**Request**:

```json
{
  "credential_id": "cred_67890",
  "authenticator_data": "...",
  "client_data_json": "...",
  "signature": "...",
  "user_handle": "user_12345"
}
```

**Response**:

```json
{
  "success": true,
  "session_token": "sess_abcdef123456...",
  "csrf_token": "csrf_789def...",
  "user": {
    "id": "user_12345",
    "email": "user@example.com",
    "stellar_public_key": "GD...123",
    "last_login": "2025-01-15T11:00:00Z"
  },
  "account": {
    "account_id": "0123456789abcdef...",
    "public_key": "GD...123",
    "balance": "1000.0000000",
    "network": "testnet"
  }
}
```

#### `GET /auth/passkey/challenge`

**Purpose**: Get authentication challenge

**Query Parameters**:

- `type`: "registration" or "authentication"
- `email`: (optional) user email for registration

**Response**:

```json
{
  "challenge": "a1b2c3d4e5f6...",
  "timeout": 60000,
  "user_verification": "required",
  "allow_credentials": ["cred_67890"], // for authentication
  "rp": {
    "id": "tuxedo.ai",
    "name": "Tuxedo AI"
  },
  "user": {
    "id": "user_12345",
    "name": "user@example.com",
    "displayName": "User"
  }
}
```

### Account Management Routes

#### `POST /accounts/import`

**Purpose**: Import existing Stellar account

**Request**:

```json
{
  "secret_key": "S...", // Encrypted or plaintext
  "network": "testnet",
  "account_type": "imported",
  "metadata": {
    "source": "freighter",
    "import_date": "2025-01-15"
  }
}
```

**Response**:

```json
{
  "success": true,
  "account": {
    "id": "acc_imported_123",
    "account_id": "0123456789abcdef...",
    "public_key": "GD...123",
    "balance": "500.0000000",
    "account_type": "imported",
    "linked_at": "2025-01-15T12:00:00Z"
  }
}
```

#### `POST /accounts/export`

**Purpose**: Export account for external wallet

**Request**:

```json
{
  "account_id": "0123456789abcdef...",
  "export_format": "secret_key", // "secret_key", "seed_phrase", "qr_code"
  "encryption": {
    "method": "passkey",
    "require_biometric": true
  }
}
```

**Response**:

```json
{
  "success": true,
  "export_data": {
    "format": "secret_key",
    "encrypted_data": "base64_encrypted_secret",
    "qr_code_data": "data:image/png;base64,...",
    "expires_at": "2025-01-15T13:00:00Z",
    "requires_verification": true
  }
}
```

## Frontend Implementation

### WebAuthn Integration

```typescript
// src/services/passkeyAuth.ts
import {
  generateRegistrationOptions,
  verifyRegistrationResponse,
  generateAuthenticationOptions,
  verifyAuthenticationResponse,
  type RegistrationResponseJSON,
  type AuthenticationResponseJSON,
} from "@simplewebauthn/server";
import {
  startRegistration,
  startAuthentication,
} from "@simplewebauthn/browser";

export class PasskeyAuthService {
  private baseUrl: string;
  private rpId: string;

  constructor() {
    this.baseUrl = process.env.VITE_API_URL || "http://localhost:8000";
    this.rpId = window.location.hostname;
  }

  async register(email: string): Promise<RegistrationResult> {
    try {
      // 1. Get registration challenge from server
      const challengeResponse = await fetch(
        `${this.baseUrl}/auth/passkey/challenge?type=registration&email=${email}`,
      );
      const options = await challengeResponse.json();

      // 2. Create passkey using WebAuthn API
      const registrationResult = await startRegistration({
        ...options,
        user: {
          ...options.user,
          name: email,
          displayName: email,
        },
        authenticatorSelection: {
          authenticatorAttachment: "platform",
          userVerification: "required",
          residentKey: "required",
        },
        extensions: {
          prf: {
            eval: {
              first: crypto.getRandomValues(new Uint8Array(32)),
            },
          },
        },
      });

      // 3. Send registration to server
      const verificationResponse = await fetch(
        `${this.baseUrl}/auth/passkey/register`,
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            email,
            ...registrationResult,
          }),
        },
      );

      const result = await verificationResponse.json();

      if (result.success) {
        // Store user session
        localStorage.setItem("session_token", result.session_token);
        localStorage.setItem("user_data", JSON.stringify(result.user));

        return {
          success: true,
          user: result.user,
          account: result.account,
        };
      } else {
        throw new Error(result.error || "Registration failed");
      }
    } catch (error) {
      console.error("Passkey registration error:", error);
      throw error;
    }
  }

  async authenticate(): Promise<AuthenticationResult> {
    try {
      // 1. Get authentication challenge from server
      const challengeResponse = await fetch(
        `${this.baseUrl}/auth/passkey/challenge?type=authentication`,
      );
      const options = await challengeResponse.json();

      // 2. Authenticate with existing passkey
      const authenticationResult = await startAuthentication({
        ...options,
        userVerification: "required",
        extensions: {
          prf: {
            eval: {
              first: crypto.getRandomValues(new Uint8Array(32)),
            },
          },
        },
      });

      // 3. Send authentication to server
      const verificationResponse = await fetch(
        `${this.baseUrl}/auth/passkey/authenticate`,
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify(authenticationResult),
        },
      );

      const result = await verificationResponse.json();

      if (result.success) {
        // Store user session
        localStorage.setItem("session_token", result.session_token);
        localStorage.setItem("csrf_token", result.csrf_token);
        localStorage.setItem("user_data", JSON.stringify(result.user));

        return {
          success: true,
          user: result.user,
          account: result.account,
        };
      } else {
        throw new Error(result.error || "Authentication failed");
      }
    } catch (error) {
      console.error("Passkey authentication error:", error);
      throw error;
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

    const response = await fetch(`${this.baseUrl}/accounts/export`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${sessionToken}`,
        "X-CSRF-Token": localStorage.getItem("csrf_token") || "",
      },
      body: JSON.stringify({
        account_id: accountId,
        export_format: format,
        encryption: {
          method: "passkey",
          require_biometric: true,
        },
      }),
    });

    const result = await response.json();

    if (result.success) {
      return result.export_data;
    } else {
      throw new Error(result.error || "Export failed");
    }
  }

  async importAccount(
    secretKey: string,
    network: string = "testnet",
  ): Promise<ImportResult> {
    const sessionToken = localStorage.getItem("session_token");
    if (!sessionToken) {
      throw new Error("No active session");
    }

    const response = await fetch(`${this.baseUrl}/accounts/import`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${sessionToken}`,
        "X-CSRF-Token": localStorage.getItem("csrf_token") || "",
      },
      body: JSON.stringify({
        secret_key,
        network,
        account_type: "imported",
      }),
    });

    const result = await response.json();

    if (result.success) {
      return result.account;
    } else {
      throw new Error(result.error || "Import failed");
    }
  }
}
```

### React Integration

```typescript
// src/contexts/PasskeyContext.tsx
import React, { createContext, useContext, useState, useEffect } from 'react';
import { PasskeyAuthService } from '../services/passkeyAuth';

interface PasskeyContextType {
  isAuthenticated: boolean;
  user: User | null;
  account: Account | null;
  isLoading: boolean;
  register: (email: string) => Promise<void>;
  authenticate: () => Promise<void>;
  logout: () => void;
  exportAccount: (accountId: string, format: 'secret_key' | 'seed_phrase' | 'qr_code') => Promise<ExportResult>;
  importAccount: (secretKey: string) => Promise<void>;
}

const PasskeyContext = createContext<PasskeyContextType | undefined>(undefined);

export function PasskeyProvider({ children }: { children: React.ReactNode }) {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [user, setUser] = useState<User | null>(null);
  const [account, setAccount] = useState<Account | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  const passkeyService = new PasskeyAuthService();

  useEffect(() => {
    // Check for existing session on mount
    const checkSession = async () => {
      const sessionToken = localStorage.getItem('session_token');
      const userData = localStorage.getItem('user_data');

      if (sessionToken && userData) {
        try {
          // Validate session with server
          const response = await fetch('/auth/validate-session', {
            method: 'POST',
            headers: {
              'Authorization': `Bearer ${sessionToken}`
            }
          });

          if (response.ok) {
            const result = await response.json();
            setIsAuthenticated(true);
            setUser(result.user);
            setAccount(result.account);
          } else {
            // Clear invalid session
            localStorage.removeItem('session_token');
            localStorage.removeItem('csrf_token');
            localStorage.removeItem('user_data');
          }
        } catch (error) {
          console.error('Session validation failed:', error);
        }
      }

      setIsLoading(false);
    };

    checkSession();
  }, []);

  const register = async (email: string) => {
    setIsLoading(true);
    try {
      const result = await passkeyService.register(email);
      setIsAuthenticated(true);
      setUser(result.user);
      setAccount(result.account);
    } catch (error) {
      console.error('Registration failed:', error);
      throw error;
    } finally {
      setIsLoading(false);
    }
  };

  const authenticate = async () => {
    setIsLoading(true);
    try {
      const result = await passkeyService.authenticate();
      setIsAuthenticated(true);
      setUser(result.user);
      setAccount(result.account);
    } catch (error) {
      console.error('Authentication failed:', error);
      throw error;
    } finally {
      setIsLoading(false);
    }
  };

  const logout = () => {
    localStorage.removeItem('session_token');
    localStorage.removeItem('csrf_token');
    localStorage.removeItem('user_data');
    setIsAuthenticated(false);
    setUser(null);
    setAccount(null);
  };

  const exportAccount = async (accountId: string, format: 'secret_key' | 'seed_phrase' | 'qr_code') => {
    return await passkeyService.exportAccount(accountId, format);
  };

  const importAccount = async (secretKey: string) => {
    setIsLoading(true);
    try {
      const result = await passkeyService.importAccount(secretKey);
      // Refresh account data
      setAccount(prev => prev ? { ...prev, ...result } : null);
    } catch (error) {
      console.error('Import failed:', error);
      throw error;
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <PasskeyContext.Provider value={{
      isAuthenticated,
      user,
      account,
      isLoading,
      register,
      authenticate,
      logout,
      exportAccount,
      importAccount
    }}>
      {children}
    </PasskeyContext.Provider>
  );
}

export function usePasskey() {
  const context = useContext(PasskeyContext);
  if (context === undefined) {
    throw new Error('usePasskey must be used within a PasskeyProvider');
  }
  return context;
}
```

## Backend Implementation

### Python Backend with FastAPI

```python
# backend/services/passkey_service.py
import json
import secrets
import time
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from webauthn import (
    generate_registration_options,
    verify_registration_response,
    generate_authentication_options,
    verify_authentication_response,
    options_to_json,
    base64url_to_bytes,
)
from webauthn.helpers import (
    bytes_to_base64url,
    base64url_to_bytes,
)
from webauthn.helpers.structs import (
    PublicKeyCredentialRpEntity,
    PublicKeyCredentialUserEntity,
    AuthenticatorSelectionCriteria,
    ResidentKeyRequirement,
    UserVerificationRequirement,
)
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from cryptography.hazmat.backends import default_backend
import stellar_sdk
from stellar_sdk.keypair import Keypair

class PasskeyService:
    def __init__(self, db, rp_id: str, rp_name: str):
        self.db = db
        self.rp_id = rp_id
        self.rp_name = rp_name
        self.rp = PublicKeyCredentialRpEntity(id=rp_id, name=rp_name)

    async def create_registration_challenge(self, email: str) -> Dict[str, Any]:
        """Create challenge for passkey registration"""
        challenge = secrets.token_bytes(32)
        challenge_id = self._store_challenge(challenge, "registration", email=email)

        user = PublicKeyCredentialUserEntity(
            id=challenge_id.encode(),
            name=email,
            display_name=email
        )

        options = generate_registration_options(
            rp=self.rp,
            user=user,
            challenge=challenge,
            authenticator_selection=AuthenticatorSelectionCriteria(
                authenticator_attachment='platform',
                resident_key=ResidentKeyRequirement.REQUIRED,
                user_verification=UserVerificationRequirement.REQUIRED
            ),
            extensions={
                'prf': {
                    'eval': {
                        'first': secrets.token_bytes(32)
                    }
                }
            }
        )

        return {
            "challenge": bytes_to_base64url(challenge),
            "challenge_id": challenge_id,
            "options": json.loads(options_to_json(options))
        }

    async def create_authentication_challenge(self, user_id: Optional[str] = None) -> Dict[str, Any]:
        """Create challenge for passkey authentication"""
        challenge = secrets.token_bytes(32)
        challenge_id = self._store_challenge(challenge, "authentication", user_id=user_id)

        # Get user's credentials if user_id provided
        allow_credentials = []
        if user_id:
            credentials = await self.db.get_passkey_credentials(user_id)
            allow_credentials = [
                {"id": cred['credential_id'], "type": "public-key"}
                for cred in credentials
            ]

        options = generate_authentication_options(
            rp_id=self.rp_id,
            challenge=challenge,
            allow_credentials=allow_credentials,
            user_verification=UserVerificationRequirement.REQUIRED,
            extensions={
                'prf': {
                    'eval': {
                        'first': secrets.token_bytes(32)
                    }
                }
            }
        )

        return {
            "challenge": bytes_to_base64url(challenge),
            "challenge_id": challenge_id,
            "options": json.loads(options_to_json(options))
        }

    async def register_passkey(self,
                             email: str,
                             credential_id: str,
                             client_data_json: str,
                             attestation_object: str,
                             transports: list,
                             friendly_name: Optional[str] = None) -> Dict[str, Any]:
        """Complete passkey registration and create Stellar account"""

        # Verify registration response
        verification = await self._verify_registration(
            credential_id, client_data_json, attestation_object
        )

        if not verification.success:
            raise ValueError(f"Registration verification failed: {verification.error}")

        # Derive Stellar keypair from passkey PRF
        prf_result = verification.credential_extension_output.get('prf', {}).get('eval', {}).get('first')
        if not prf_result:
            raise ValueError("PRF extension required for account derivation")

        stellar_keypair = self._derive_stellar_keypair(prf_result)

        # Create user and related records
        async with self.db.transaction():
            # Create user
            user_id = await self.db.create_user(
                email=email,
                credential_id=credential_id,
                stellar_public_key=stellar_keypair.public_key,
                stellar_account_id=stellar_keypair.account_id
            )

            # Store passkey credential
            await self.db.create_passkey_credential(
                user_id=user_id,
                credential_id=credential_id,
                credential_public_key=verification.credential_public_key,
                aaguid=verification.aaguid,
                transports=transports,
                backup_eligible=verification.backup_eligible,
                backup_state=verification.backup_state,
                device_type=verification.device_type,
                friendly_name=friendly_name
            )

            # Create Stellar account record
            await self.db.create_stellar_account(
                user_id=user_id,
                account_id=stellar_keypair.account_id,
                public_key=stellar_keypair.public_key,
                derivation_salt=bytes_to_base64url(prf_result),
                network='testnet'
            )

            # Fund account on testnet
            await self._fund_testnet_account(stellar_keypair.account_id)

        return {
            "success": True,
            "user_id": user_id,
            "stellar_public_key": stellar_keypair.public_key,
            "stellar_account_id": stellar_keypair.account_id
        }

    async def authenticate_passkey(self,
                                 credential_id: str,
                                 authenticator_data: str,
                                 client_data_json: str,
                                 signature: str,
                                 user_handle: Optional[str] = None) -> Dict[str, Any]:
        """Complete passkey authentication"""

        # Verify authentication response
        verification = await self._verify_authentication(
            credential_id, authenticator_data, client_data_json, signature
        )

        if not verification.success:
            raise ValueError(f"Authentication verification failed: {verification.error}")

        # Get user from credential
        user = await self.db.get_user_by_credential_id(credential_id)
        if not user:
            raise ValueError("User not found for credential")

        # Get user's Stellar account
        account = await self.db.get_stellar_account(user['id'])

        # Update last login and usage
        async with self.db.transaction():
            await self.db.update_user_last_login(user['id'])
            await self.db.update_credential_last_used(credential_id)
            await self.db.log_security_event(
                user_id=user['id'],
                event_type='login',
                event_data={'credential_id': credential_id},
                success=True
            )

        # Create session
        session_token = secrets.token_urlsafe(32)
        csrf_token = secrets.token_urlsafe(32)
        await self.db.create_session(
            user_id=user['id'],
            session_token=session_token,
            csrf_token=csrf_token,
            expires_at=datetime.utcnow() + timedelta(days=7)
        )

        return {
            "success": True,
            "session_token": session_token,
            "csrf_token": csrf_token,
            "user": user,
            "account": account
        }

    def _derive_stellar_keypair(self, prf_result: bytes) -> Keypair:
        """Derive Stellar keypair from PRF output"""
        # Use HKDF to derive 32-byte seed for Stellar keypair
        hkdf = HKDF(
            algorithm=hashes.SHA256(),
            length=32,
            salt=b'tuxedo-stellar-derivation-v1',
            info=b'account-derivation',
            backend=default_backend()
        )

        seed = hkdf.derive(prf_result)
        return Keypair.from_secret(seed)

    async def _verify_registration(self,
                                 credential_id: str,
                                 client_data_json: str,
                                 attestation_object: str) -> Any:
        """Verify passkey registration response"""
        # Implementation would use SimpleWebAuthn library
        # This is a simplified example
        pass

    async def _verify_authentication(self,
                                   credential_id: str,
                                   authenticator_data: str,
                                   client_data_json: str,
                                   signature: str) -> Any:
        """Verify passkey authentication response"""
        # Implementation would use SimpleWebAuthn library
        # This is a simplified example
        pass

    async def _fund_testnet_account(self, account_id: str) -> bool:
        """Fund account on Stellar testnet using Friendbot"""
        try:
            response = requests.get(f"https://friendbot.stellar.org/?addr={account_id}")
            if response.status_code == 200:
                return True
            else:
                print(f"Friendbot funding failed: {response.text}")
                return False
        except Exception as e:
            print(f"Error funding account: {e}")
            return False

    def _store_challenge(self, challenge: bytes, challenge_type: str, **kwargs) -> str:
        """Store authentication challenge in database"""
        challenge_id = secrets.token_urlsafe(32)
        # Store in database with expiration
        self.db.create_challenge(
            challenge_id=challenge_id,
            challenge_data=bytes_to_base64url(challenge),
            challenge_type=challenge_type,
            expires_at=datetime.utcnow() + timedelta(minutes=15),
            **kwargs
        )
        return challenge_id
```

## Security Implementation Details

### Key Derivation Function

```python
# backend/crypto/key_derivation.py
import hashlib
import hmac
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from cryptography.hazmat.backends import default_backend
from stellar_sdk.keypair import Keypair

class StellarKeyDerivation:
    """Derives Stellar keypairs from passkey PRF outputs"""

    DERIVATION_SALT = b'tuxedo-stellar-derivation-v1'
    DERIVATION_INFO = b'account-derivation'

    @classmethod
    def derive_keypair(cls, prf_output: bytes, account_index: int = 0) -> Keypair:
        """Derive Stellar keypair from PRF output"""

        # Use account index to derive multiple accounts from same passkey
        account_bytes = account_index.to_bytes(4, byteorder='big')

        # Combine PRF output with account index
        input_material = prf_output + account_bytes

        # Derive 32-byte seed using HKDF
        hkdf = HKDF(
            algorithm=hashes.SHA256(),
            length=32,
            salt=cls.DERIVATION_SALT,
            info=cls.DERIVATION_INFO,
            backend=default_backend()
        )

        seed = hkdf.derive(input_material)

        # Generate Stellar keypair from seed
        return Keypair.from_secret(seed)

    @classmethod
    def verify_derivation(cls, prf_output: bytes, expected_public_key: str, account_index: int = 0) -> bool:
        """Verify that a public key was derived from given PRF output"""
        try:
            keypair = cls.derive_keypair(prf_output, account_index)
            return keypair.public_key == expected_public_key
        except:
            return False
```

### Session Security

```python
# backend/middleware/security.py
import secrets
import time
from datetime import datetime, timedelta
from fastapi import HTTPException, Request, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

security = HTTPBearer()

class SecurityMiddleware:
    def __init__(self, db):
        self.db = db

    async def verify_session(self, request: Request, credentials: HTTPAuthorizationCredentials):
        """Verify session token and update last accessed"""
        session_token = credentials.credentials

        session = await self.db.get_session_by_token(session_token)
        if not session or not session['is_active']:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid session"
            )

        if datetime.utcnow() > session['expires_at']:
            await self.db.deactivate_session(session['id'])
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Session expired"
            )

        # Update last accessed
        await self.db.update_session_last_accessed(session['id'])

        # Add user info to request state
        request.state.user_id = session['user_id']
        request.state.session_id = session['id']

        return session

    async def verify_csrf_token(self, request: Request, csrf_token: str):
        """Verify CSRF token for state-changing operations"""
        session_id = request.state.session_id
        session = await self.db.get_session_by_id(session_id)

        if not session or session['csrf_token'] != csrf_token:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Invalid CSRF token"
            )

    def generate_secure_token(self, length: int = 32) -> str:
        """Generate cryptographically secure random token"""
        return secrets.token_urlsafe(length)
```

## Testing Strategy

### Unit Tests

```python
# tests/test_passkey_service.py
import pytest
from unittest.mock import AsyncMock, MagicMock
from backend.services.passkey_service import PasskeyService

class TestPasskeyService:
    @pytest.fixture
    def passkey_service(self):
        mock_db = AsyncMock()
        return PasskeyService(mock_db, "localhost", "Tuxedo AI Test")

    @pytest.mark.asyncio
    async def test_create_registration_challenge(self, passkey_service):
        """Test registration challenge creation"""
        email = "test@example.com"
        challenge_data = await passkey_service.create_registration_challenge(email)

        assert 'challenge' in challenge_data
        assert 'challenge_id' in challenge_data
        assert 'options' in challenge_data
        assert challenge_data['options']['user']['name'] == email

    @pytest.mark.asyncio
    async def test_stellar_key_derivation(self):
        """Test Stellar keypair derivation from PRF output"""
        from backend.crypto.key_derivation import StellarKeyDerivation

        prf_output = bytes.fromhex("a1b2c3d4e5f6" * 4)  # 32 bytes

        keypair = StellarKeyDerivation.derive_keypair(prf_output)

        assert len(keypair.secret) == 32
        assert len(keypair.public_key) == 56  # Stellar public key length
        assert len(keypair.account_id) == 63  # Stellar account ID length

        # Test deterministic derivation
        keypair2 = StellarKeyDerivation.derive_keypair(prf_output)
        assert keypair.public_key == keypair2.public_key
```

### Integration Tests

```python
# tests/test_passkey_integration.py
import pytest
from fastapi.testclient import TestClient
from backend.app import app

class TestPasskeyIntegration:
    @pytest.fixture
    def client(self):
        return TestClient(app)

    def test_complete_registration_flow(self, client):
        """Test complete passkey registration flow"""
        # 1. Request registration challenge
        response = client.get("/auth/passkey/challenge?type=registration&email=test@example.com")
        assert response.status_code == 200
        challenge_data = response.json()

        # 2. Mock WebAuthn registration response
        mock_registration = {
            "credential_id": "mock_credential_id",
            "client_data_json": "mock_client_data",
            "attestation_object": "mock_attestation",
            "transports": ["internal"]
        }

        # 3. Complete registration
        response = client.post("/auth/passkey/register", json=mock_registration)
        assert response.status_code == 200
        result = response.json()

        assert result['success'] is True
        assert 'user_id' in result
        assert 'stellar_public_key' in result
        assert 'stellar_account_id' in result

    def test_complete_authentication_flow(self, client):
        """Test complete passkey authentication flow"""
        # 1. Request authentication challenge
        response = client.get("/auth/passkey/challenge?type=authentication")
        assert response.status_code == 200
        challenge_data = response.json()

        # 2. Mock WebAuthn authentication response
        mock_authentication = {
            "credential_id": "mock_credential_id",
            "authenticator_data": "mock_auth_data",
            "client_data_json": "mock_client_data",
            "signature": "mock_signature"
        }

        # 3. Complete authentication
        response = client.post("/auth/passkey/authenticate", json=mock_authentication)
        assert response.status_code == 200
        result = response.json()

        assert result['success'] is True
        assert 'session_token' in result
        assert 'csrf_token' in result
        assert 'user' in result
        assert 'account' in result
```

## Performance Considerations

### Optimization Strategies

1. **Database Indexing**: Proper indexes on frequently queried fields
2. **Connection Pooling**: Efficient database connection management
3. **Caching**: Redis caching for session data and frequently accessed records
4. **Async Operations**: Non-blocking I/O for all database operations
5. **Challenge Expiration**: Efficient cleanup of expired challenges

### Security Performance

1. **Rate Limiting**: Prevent brute force attacks
2. **Session Management**: Efficient session validation and cleanup
3. **Memory Safety**: Proper handling of cryptographic materials
4. **Timing Attack Prevention**: Constant-time comparisons for sensitive data

This technical specification provides the foundation for implementing enterprise-grade passkey authentication for Tuxedo AI, combining Web2 usability with Web3 security requirements.
