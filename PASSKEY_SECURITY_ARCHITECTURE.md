# Passkey Security Architecture for Tuxedo
## Research & Implementation Proposal

**Date**: November 5, 2025
**Branch**: `claude/passkey-security-research-011CUpDegmDhBfwEFqsQQkuB`
**Status**: Research Phase - Architecture Proposal
**Priority**: CRITICAL for Phala Deployment

---

## Executive Summary

This document presents a comprehensive passkey security architecture for Tuxedo, replacing magic link authentication with phishing-resistant, hardware-backed passkey authentication. The proposal integrates WebAuthn/FIDO2 standards with Stellar wallet functionality, creating a secure foundation for the next 4 billion decentralized financial market participants.

### Key Objectives

1. **Security First**: Replace vulnerable magic links with passkeys (phishing-resistant, hardware-backed)
2. **User Experience**: Seamless biometric authentication (Face ID, Touch ID, Windows Hello)
3. **Wallet Integration**: Bridge between passkey auth and Stellar wallet import/export
4. **Production Ready**: Prepare for Phala TEE deployment with enterprise-grade security

### Strategic Vision

**Passkeys as the centerpiece** - Primary authentication method
**Wallet adapter as advanced feature** - For crypto-native users to import/export
**Magic links as fallback** - Temporary bridge during migration

---

## Table of Contents

1. [Research Foundations](#research-foundations)
2. [Current State Analysis](#current-state-analysis)
3. [Proposed Architecture](#proposed-architecture)
4. [Implementation Strategy](#implementation-strategy)
5. [Wallet Integration Pattern](#wallet-integration-pattern)
6. [Security Considerations](#security-considerations)
7. [Migration Plan](#migration-plan)
8. [Technical Specifications](#technical-specifications)

---

## Research Foundations

### WebAuthn/FIDO2 Standards (2024-2025)

**Protocol Status**:
- **WebAuthn Level 2**: Current W3C Recommendation (stable)
- **WebAuthn Level 3**: First Public Working Draft (emerging features)
- **FIDO2 CTAP 2.2**: February 2025 (latest authenticator protocol)

**Key Features**:
- ✅ **96.36% browser support** (Chrome, Safari, Firefox, Edge)
- ✅ **Native protocol support** on all major platforms
- ✅ **Hardware-backed security** (Secure Enclave, TPM, security keys)
- ✅ **Phishing-resistant** by design (cryptographic origin binding)
- ✅ **Biometric authentication** (Face ID, Touch ID, Windows Hello)

**References**:
- W3C WebAuthn Spec: https://www.w3.org/TR/webauthn-2/
- FIDO Alliance: https://fidoalliance.org/specifications/
- Browser Support: https://webauthn.me/browser-support

### Stellar Ecosystem Support

**Protocol 21 (Activated June 18, 2024)**:
- **Native secp256r1 verification** (the curve used by passkeys)
- **CAP-0051**: Smart Contract Host Functionality for P256 signatures
- **First blockchain** with protocol-level passkey support

**Stellar Passkey Kit**:
- TypeScript SDK: `passkey-kit` (⚠️ unaudited demonstration code)
- Factory contract pattern for smart wallets
- Launchtube service for transaction abstraction
- Repository: https://github.com/kalepail/passkey-kit

**Status**: Stellar is the **most passkey-ready blockchain** as of 2025

### Crypto Wallet Implementations (2024-2025)

**Production Examples**:

1. **Coinbase Smart Wallet** (June 2024)
   - First major exchange with passkey-primary auth
   - Built on Base L2 with account abstraction
   - No seed phrases by default
   - Recovery via passkey + cloud backups

2. **Daimo** (Ethereum L2)
   - Stablecoin wallet with no seed phrases
   - Keys in phone's Secure Enclave (never leave device)
   - ERC-4337 contract wallet
   - Developed p256-verifier for onchain verification

3. **Clave** (zkSync)
   - WebAuthn + Smart Contract Account
   - Production-ready audited contracts
   - Native account abstraction on zkSync

**Key Pattern**: Smart contract wallets + passkey signers = best UX

### Security Vulnerabilities (2024-2025)

**CVE-2024-9956** (Critical - October 2024):
- Mobile passkey phishing via Bluetooth
- Affects all major mobile browsers
- **Fixed**: Chrome/Edge Oct 2024, Firefox Feb 2025, Safari Jan 2025
- **Impact**: Broke assumption that passkeys are impossible to phish

**Mitigation**: Always use latest browser versions, HTTPS enforcement

**Session Hijacking**:
- Stolen cookies still grant access even with passkey auth
- **Mitigation**: Short session timeouts, device fingerprinting, continuous auth

**Best Practices**:
- ✅ Require cloud-synced passkeys (prevent device loss = fund loss)
- ✅ Set `userVerification: "required"` (enforce biometric/PIN)
- ✅ Multi-device registration (backup authentication)
- ✅ Social recovery mechanisms
- ✅ HTTPS enforcement in production

---

## Current State Analysis

### Authentication System (Magic Links)

**Implementation**: Email-based magic link authentication (15-min expiry, single-use tokens)

**Database Schema**:
```sql
-- Users
CREATE TABLE users (
    id TEXT PRIMARY KEY,                    -- user_xxxxx
    email TEXT UNIQUE NOT NULL,
    encrypted_private_key TEXT,             -- Optional Stellar key
    public_key TEXT UNIQUE,                 -- Optional Stellar public key
    created_at TIMESTAMP,
    last_login TIMESTAMP
);

-- Magic Link Sessions
CREATE TABLE magic_link_sessions (
    id TEXT PRIMARY KEY,
    user_id TEXT,
    email TEXT NOT NULL,
    token TEXT UNIQUE NOT NULL,             -- 43-char URL-safe token
    expires_at TIMESTAMP NOT NULL,          -- 15 minutes
    used_at TIMESTAMP,                      -- Single-use enforcement
    FOREIGN KEY (user_id) REFERENCES users (id)
);

-- User Sessions
CREATE TABLE user_sessions (
    id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL,
    session_token TEXT UNIQUE NOT NULL,     -- 86-char URL-safe token
    expires_at TIMESTAMP NOT NULL,          -- 7 days
    last_accessed TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users (id)
);
```

**Security Strengths**:
- ✅ Time-limited tokens (15 min for magic links, 7 days for sessions)
- ✅ Single-use enforcement (tokens marked `used_at`)
- ✅ Cryptographically secure generation (`secrets.token_urlsafe`)
- ✅ No password storage
- ✅ User enumeration prevention

**Security Weaknesses**:
- ⚠️ Email interception risk
- ⚠️ Phishing-vulnerable (attackers can proxy magic link flow)
- ⚠️ No hardware-backed security
- ⚠️ Dependent on email provider security
- ⚠️ No cryptographic proof of user presence

**API Endpoints**:
- `POST /auth/magic-link` - Request magic link
- `GET /auth/magic-link/validate?token=` - Validate token, create session
- `POST /auth/validate-session` - Validate session token
- `POST /auth/logout` - Clear session
- `GET /auth/me` - Get current user

### Wallet Integration (Removed)

**Previous State** (removed in commit `970ed6f`):
- Used `@creit.tech/stellar-wallets-kit` v1.9.5
- Freighter wallet integration
- Client-side transaction signing
- Wallet-dependent architecture

**Current State** (agent-first):
- No wallet connection UI
- Agents manage own Stellar accounts server-side
- `useWallet.ts` is now a legacy shim (read-only agent account status)
- No transaction signing in frontend

**Package Availability**: `@creit.tech/stellar-wallets-kit` still in `package.json` (v1.9.5)

### Known Issues

From `auth_debugging.md`:
1. **CORS blocking redirects** - Fixed by returning JSON instead
2. **Single-use token validation** - Double validation on browser refresh
3. **TypeScript build errors** - Missing props, unsafe type handling

---

## Proposed Architecture

### System Overview

```
┌─────────────────────────────────────────────────────────────┐
│                    TUXEDO SECURITY LAYER                     │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  ┌──────────────────┐        ┌─────────────────────────┐   │
│  │  Passkey Auth    │◄──────►│  Wallet Import/Export   │   │
│  │  (Primary)       │        │  (Advanced Users)       │   │
│  └────────┬─────────┘        └───────────┬─────────────┘   │
│           │                              │                  │
│           │  ┌──────────────────────┐   │                  │
│           └─►│  User Identity       │◄──┘                  │
│              │  & Session Mgmt      │                      │
│              └──────────┬───────────┘                      │
│                         │                                   │
│              ┌──────────▼───────────┐                      │
│              │  Stellar Smart       │                      │
│              │  Wallet (Optional)   │                      │
│              └──────────────────────┘                      │
│                                                               │
└─────────────────────────────────────────────────────────────┘
                         │
                         ▼
             ┌────────────────────────┐
             │  AI Agent Backend      │
             │  (Account Management)  │
             └────────────────────────┘
```

### Three-Tier Authentication Model

#### Tier 1: Passkey Authentication (Primary)

**User Flow**:
1. User visits Tuxedo
2. Clicks "Sign in with Passkey"
3. Browser prompts for biometric (Face ID, Touch ID, etc.)
4. Passkey verified → 7-day session created
5. User enters chat interface (authenticated)

**Technical Flow**:
```
User → Frontend → POST /auth/passkey/authenticate/options
                → Backend generates challenge (10-min expiry)
                → Stores challenge in DB

User → Browser WebAuthn API → navigator.credentials.get()
     → Device prompts biometric
     → User authorizes (Face ID/Touch ID/PIN)
     → Device signs challenge with private key
     → Returns signed assertion

Frontend → POST /auth/passkey/authenticate/verify
        → Backend verifies signature with stored public key
        → Backend checks challenge matches (single-use)
        → Backend checks sign_count (cloning detection)
        → Backend creates 7-day session token
        → Returns session token (HTTP-only cookie)

User → Authenticated → Access chat interface
```

#### Tier 2: Wallet Adapter (Advanced Users)

**Purpose**: Bridge between Tuxedo passkeys and external Stellar wallets

**Capabilities**:
1. **Import**: Connect Freighter/xBull wallet → Create Tuxedo account with passkey
2. **Export**: Export Tuxedo account keys to external wallet
3. **Interoperability**: Move funds between Tuxedo and other wallets

**User Flow** (Import):
```
Advanced User → Settings → "Import from Wallet"
             → Wallet selection modal (Freighter, xBull, Lobstr)
             → User connects wallet (browser extension)
             → Frontend reads public key from wallet
             → User creates passkey for Tuxedo account
             → Backend associates passkey with imported wallet address
             → User can now use both passkey auth AND wallet signing
```

**User Flow** (Export):
```
User → Settings → "Export to Wallet"
    → Warning: "This will export your private key. Keep it secure!"
    → User confirms with passkey verification
    → Backend encrypts private key with user's passkey
    → User downloads encrypted key file or QR code
    → User imports into Freighter/Lobstr/other wallet
```

**Security Model**:
- Passkey remains primary authentication
- Wallet connection is **optional enhancement**
- Private keys encrypted at rest
- Export requires passkey re-verification (every time)

#### Tier 3: Magic Link Fallback (Temporary)

**Purpose**: Migration bridge during passkey rollout

**User Flow**:
1. User clicks "Can't use passkey? Use email instead"
2. Follows existing magic link flow
3. After login, prompt: "Secure your account with a passkey"
4. One-click passkey setup

**Deprecation Timeline**:
- **Phase 1** (0-3 months): Both passkey + magic link available
- **Phase 2** (3-6 months): Magic link only for recovery
- **Phase 3** (6+ months): Passkey-only (magic link removed)

### Database Schema Updates

```sql
-- New table: WebAuthn credentials
CREATE TABLE webauthn_credentials (
    id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL,

    -- Core credential data
    credential_id BLOB NOT NULL UNIQUE,     -- Raw credential ID (binary)
    credential_id_b64 TEXT NOT NULL UNIQUE, -- Base64 for API
    public_key BLOB NOT NULL,               -- CBOR-encoded public key

    -- Authenticator properties
    aaguid TEXT,                            -- Authenticator GUID
    attestation_type TEXT,                  -- 'none', 'basic', 'self'
    transport TEXT,                         -- JSON: ["internal", "usb", "nfc"]
    attachment TEXT,                        -- 'platform' or 'cross-platform'

    -- Security
    sign_count INTEGER DEFAULT 0,          -- Increment on each auth
    clone_warning BOOLEAN DEFAULT FALSE,   -- Detected cloning

    -- Backup state (passkey sync)
    backup_eligible BOOLEAN DEFAULT FALSE, -- Can be synced
    backup_state BOOLEAN DEFAULT TRUE,     -- Currently synced
    discoverable BOOLEAN DEFAULT TRUE,     -- Resident key

    -- Metadata
    device_name TEXT,                      -- "iPhone 15 Pro", "YubiKey 5"
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_used TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE,

    FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
);

-- New table: WebAuthn challenges (temporary)
CREATE TABLE webauthn_challenges (
    id TEXT PRIMARY KEY,
    user_id TEXT,                          -- NULL for registration
    email TEXT,                            -- For pre-registration lookup
    challenge BLOB NOT NULL UNIQUE,        -- Random 32-byte challenge
    challenge_b64 TEXT NOT NULL UNIQUE,    -- Base64 for API
    operation TEXT NOT NULL,               -- 'registration' or 'authentication'
    expires_at TIMESTAMP NOT NULL,         -- 10 minutes from creation
    used_at TIMESTAMP,                     -- Single-use enforcement
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (user_id) REFERENCES users (id)
);

-- Modify users table
ALTER TABLE users ADD COLUMN has_passkey BOOLEAN DEFAULT FALSE;
ALTER TABLE users ADD COLUMN email_verified BOOLEAN DEFAULT FALSE;
ALTER TABLE users ADD COLUMN recovery_code TEXT;  -- Account recovery

-- Wallet integration (optional)
CREATE TABLE wallet_connections (
    id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL,
    wallet_type TEXT NOT NULL,             -- 'freighter', 'xbull', 'lobstr'
    wallet_address TEXT NOT NULL,          -- Stellar address
    connected_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_used TIMESTAMP,
    is_primary BOOLEAN DEFAULT FALSE,      -- Primary wallet for this user

    FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
);

-- Indexes
CREATE INDEX idx_webauthn_credentials_user_id ON webauthn_credentials(user_id);
CREATE INDEX idx_webauthn_credentials_credential_id ON webauthn_credentials(credential_id_b64);
CREATE INDEX idx_webauthn_challenges_email ON webauthn_challenges(email);
CREATE INDEX idx_webauthn_challenges_expires ON webauthn_challenges(expires_at);
CREATE INDEX idx_wallet_connections_user_id ON wallet_connections(user_id);
CREATE INDEX idx_wallet_connections_address ON wallet_connections(wallet_address);
```

### Backend API Endpoints

```python
# Passkey Registration
POST /auth/passkey/register/options
    Request: { email: string }
    Response: { challengeOptions: PublicKeyCredentialCreationOptions }

POST /auth/passkey/register/verify
    Request: { email: string, credential: RegistrationCredential }
    Response: { success: true, sessionToken: string, user: User }

# Passkey Authentication
POST /auth/passkey/authenticate/options
    Request: { email?: string }  # Optional for conditional UI
    Response: { challengeOptions: PublicKeyCredentialRequestOptions }

POST /auth/passkey/authenticate/verify
    Request: { credential: AuthenticationCredential }
    Response: { success: true, sessionToken: string, user: User }

# Passkey Management
GET /auth/passkey/list
    Headers: { Authorization: Bearer <token> }
    Response: { passkeys: Array<PasskeyInfo> }

DELETE /auth/passkey/{credential_id}
    Headers: { Authorization: Bearer <token> }
    Response: { success: true }

# Wallet Integration (Advanced)
POST /wallet/connect
    Request: { walletType: 'freighter'|'xbull', publicKey: string }
    Response: { success: true, walletConnection: WalletConnection }

POST /wallet/export
    Headers: { Authorization: Bearer <token> }
    Response: { encryptedKey: string, qrCode: string }

POST /wallet/import
    Request: { publicKey: string, walletType: string }
    Response: { success: true }

# Legacy (migration period)
POST /auth/magic-link  # Existing endpoint
GET /auth/magic-link/validate  # Existing endpoint
```

### Frontend Components

```typescript
// New Components
src/components/auth/
├── PasskeyRegistration.tsx      // Setup passkey during signup
├── PasskeyAuthentication.tsx    // Login with passkey
├── PasskeyManagement.tsx        // List/delete passkeys in settings
├── WalletConnector.tsx          // Connect Freighter/xBull (advanced)
├── WalletExporter.tsx           // Export keys to wallet
└── AuthChoice.tsx               // Passkey vs Magic Link choice

// Updated Components
src/components/
├── Login.tsx                    // Add passkey option
└── Settings.tsx                 // Passkey + wallet management

// New Hooks
src/hooks/
├── usePasskeyAuth.ts            // Passkey registration/auth logic
├── useWalletConnect.ts          // Wallet integration logic
└── useWallet.ts                 // Updated with wallet adapter

// Context Updates
src/contexts/
└── AuthContext.tsx              // Add passkey methods
```

---

## Implementation Strategy

### Phase 1: Core Passkey Infrastructure (Week 1)

**Backend**:
1. Install `webauthn` library: `pip install webauthn>=2.7.0`
2. Create database migrations for new tables
3. Implement passkey registration endpoints
4. Implement passkey authentication endpoints
5. Add challenge management (generation, cleanup)
6. Update session management to support passkeys

**Frontend**:
1. Install `@simplewebauthn/browser`: `npm install @simplewebauthn/browser@^13.0.0`
2. Create `usePasskeyAuth` hook
3. Build `PasskeyRegistration` component
4. Build `PasskeyAuthentication` component
5. Update `AuthContext` with passkey methods
6. Add passkey option to `Login.tsx`

**Testing**:
- Unit tests for WebAuthn verification
- Integration tests for registration/auth flow
- Cross-browser testing (Chrome, Safari, Firefox, Edge)
- Mobile testing (iOS Safari, Android Chrome)

**Deliverable**: Working passkey authentication alongside magic links

### Phase 2: Wallet Integration (Week 2)

**Backend**:
1. Implement wallet connection endpoints
2. Create wallet encryption/decryption utilities
3. Build wallet export functionality
4. Add wallet import logic
5. Update database schema for wallet connections

**Frontend**:
1. Reinstall/update `@creit.tech/stellar-wallets-kit`
2. Create `useWalletConnect` hook
3. Build `WalletConnector` component (Freighter, xBull, Lobstr)
4. Build `WalletExporter` component
5. Create wallet management UI in Settings
6. Update `useWallet` hook to support real wallet connections

**Testing**:
- Test Freighter wallet connection flow
- Test xBull wallet connection flow
- Test wallet export/import roundtrip
- Verify passkey + wallet dual-auth works
- Security testing for key export

**Deliverable**: Full wallet adapter for advanced users

### Phase 3: Migration & Cleanup (Week 3)

**Migration**:
1. Add "Upgrade to Passkey" prompts for magic link users
2. One-click passkey setup after magic link login
3. Email campaign to existing users about passkeys
4. Monitor adoption metrics
5. Deprecate magic links based on adoption rate

**Security Hardening**:
1. Implement rate limiting on auth endpoints
2. Add device fingerprinting
3. Implement suspicious activity monitoring
4. Add audit logging for all auth events
5. Security penetration testing

**Documentation**:
1. User guide for passkey setup
2. Developer documentation for passkey architecture
3. Wallet adapter guide for advanced users
4. Security best practices documentation
5. API documentation updates

**Deliverable**: Production-ready passkey system

### Phase 4: Advanced Features (Week 4)

**Features**:
1. Multi-device passkey management
2. Recovery codes generation
3. Social recovery mechanisms
4. Passkey backup monitoring (`IsBackedUp` flag)
5. Conditional UI support (passkey autofill)
6. Cross-device authentication support

**Optimizations**:
1. Database query optimization
2. Challenge cleanup automation
3. Session token rotation
4. Performance monitoring
5. Load testing

**Deliverable**: Enterprise-grade authentication system

---

## Wallet Integration Pattern

### Architecture: Passkey-Wallet Bridge

**Core Principle**: Passkeys are the **identity layer**, wallets are the **interoperability layer**

```
┌─────────────────────────────────────────────────┐
│           USER AUTHENTICATION                    │
│                                                  │
│  ┌────────────────┐         ┌────────────────┐ │
│  │  Passkey Auth  │         │  Email Fallback│ │
│  │  (Biometric)   │         │  (Migration)   │ │
│  └───────┬────────┘         └────────────────┘ │
│          │                                       │
│          ▼                                       │
│  ┌──────────────────┐                          │
│  │  Tuxedo Identity │                          │
│  │  (user_id)       │                          │
│  └───────┬──────────┘                          │
│          │                                       │
└──────────┼───────────────────────────────────────┘
           │
           ▼
┌──────────────────────────────────────────────────┐
│           ACCOUNT MANAGEMENT                      │
│                                                   │
│  ┌────────────────┐         ┌────────────────┐  │
│  │  Tuxedo Agent  │         │  External      │  │
│  │  Accounts      │◄───────►│  Wallets       │  │
│  │  (AI-managed)  │  Bridge │  (User-owned)  │  │
│  └────────────────┘         └────────────────┘  │
│         │                           │            │
│         ▼                           ▼            │
│  ┌──────────────────────────────────────────┐  │
│  │       Stellar Network (Testnet)          │  │
│  │  - Smart Contracts (Blend Protocol)      │  │
│  │  - Token Transfers                       │  │
│  │  - DeFi Operations                       │  │
│  └──────────────────────────────────────────┘  │
└───────────────────────────────────────────────────┘
```

### Wallet Adapter Design

**Two-Way Bridge**:

1. **Import Direction**: External Wallet → Tuxedo
   - User connects Freighter/xBull wallet
   - Tuxedo reads wallet's public key
   - User creates passkey for Tuxedo auth
   - Tuxedo associates passkey with wallet address
   - User can now:
     - Authenticate with passkey
     - Sign transactions with either Tuxedo agent OR external wallet
     - View balances from both sources

2. **Export Direction**: Tuxedo → External Wallet
   - User authenticates with passkey
   - Requests private key export
   - Tuxedo encrypts private key with passkey
   - User downloads encrypted key / QR code
   - User imports into Freighter/Lobstr/other wallet
   - Now can use Tuxedo account in external wallet

**Key Security Features**:
- Private keys encrypted with passkey before export
- Export requires fresh passkey verification (not cached)
- Warning messages about key security
- Optional time-delay before export completes (24-hour cooling period)
- Audit logging of all export operations

### Implementation: Stellar Wallets Kit Integration

```typescript
// src/hooks/useWalletConnect.ts
import { StellarWalletsKit, WalletNetwork, allowAllModules } from '@creit.tech/stellar-wallets-kit';
import { usePasskeyAuth } from './usePasskeyAuth';

export function useWalletConnect() {
  const { user, verifyPasskey } = usePasskeyAuth();
  const [kit, setKit] = useState<StellarWalletsKit | null>(null);

  // Initialize Stellar Wallets Kit
  useEffect(() => {
    const walletsKit = new StellarWalletsKit({
      network: WalletNetwork.TESTNET,
      selectedWalletId: 'freighter',
      modules: allowAllModules(),  // Freighter, xBull, Lobstr, etc.
    });
    setKit(walletsKit);
  }, []);

  // Import wallet to Tuxedo
  const importWallet = async () => {
    if (!kit || !user) throw new Error('Not authenticated');

    // 1. Open wallet selection modal
    await kit.openModal({
      onWalletSelected: async (option) => {
        console.log('Wallet selected:', option.name);
      },
    });

    // 2. Get public key from connected wallet
    const { address } = await kit.getAddress();
    console.log('Wallet address:', address);

    // 3. Verify user with passkey before associating
    const verified = await verifyPasskey();
    if (!verified) throw new Error('Passkey verification failed');

    // 4. Send to backend to associate with user account
    const response = await fetch('http://localhost:8000/wallet/connect', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${sessionToken}`,
      },
      body: JSON.stringify({
        walletType: 'freighter',
        publicKey: address,
      }),
    });

    if (!response.ok) throw new Error('Failed to connect wallet');

    return await response.json();
  };

  // Export Tuxedo account to external wallet
  const exportWallet = async () => {
    if (!user) throw new Error('Not authenticated');

    // 1. Verify with passkey before exporting keys
    const verified = await verifyPasskey();
    if (!verified) throw new Error('Passkey verification required');

    // 2. Request encrypted key from backend
    const response = await fetch('http://localhost:8000/wallet/export', {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${sessionToken}`,
      },
      credentials: 'include',
    });

    if (!response.ok) throw new Error('Failed to export wallet');

    const { encryptedKey, qrCode } = await response.json();

    // 3. Offer download options
    return { encryptedKey, qrCode };
  };

  // Sign transaction with external wallet
  const signWithExternalWallet = async (xdr: string) => {
    if (!kit) throw new Error('Wallet kit not initialized');

    const { signedXDR } = await kit.signTransaction(xdr, {
      address: user?.wallet_address,
      networkPassphrase: 'Test SDF Network ; September 2015',
    });

    return signedXDR;
  };

  return {
    importWallet,
    exportWallet,
    signWithExternalWallet,
    isConnected: !!kit,
  };
}
```

**Backend Export Endpoint**:

```python
# backend/api/routes/wallet.py
from fastapi import APIRouter, Depends, HTTPException
from backend.auth import get_authenticated_user
from backend.crypto import encrypt_with_passkey
import base64

router = APIRouter()

@router.post("/wallet/export")
async def export_wallet(current_user = Depends(get_authenticated_user)):
    """Export user's Stellar private key (encrypted with passkey)"""

    # 1. Verify user has encrypted private key
    if not current_user.encrypted_private_key:
        raise HTTPException(status_code=400, detail="No private key to export")

    # 2. Get user's passkey public key
    passkey = db.query(WebAuthnCredential)\
        .filter_by(user_id=current_user.id, is_active=True)\
        .first()

    if not passkey:
        raise HTTPException(status_code=400, detail="Passkey required for export")

    # 3. Encrypt private key with passkey
    encrypted_key = encrypt_with_passkey(
        current_user.encrypted_private_key,
        passkey.public_key
    )

    # 4. Generate QR code for mobile import
    qr_code = generate_qr_code(encrypted_key)

    # 5. Log export event for security audit
    log_security_event(
        user_id=current_user.id,
        event_type="wallet_export",
        metadata={"timestamp": datetime.utcnow()}
    )

    return {
        "encryptedKey": base64.b64encode(encrypted_key).decode(),
        "qrCode": qr_code,
        "warning": "Keep this key secure. Anyone with this key can access your funds."
    }
```

### User Experience Flow

**Beginner User** (Passkey Only):
```
1. Sign up → Create passkey (Face ID)
2. Chat with AI agent → Agent creates Stellar accounts automatically
3. No wallet complexity, pure conversational UX
```

**Intermediate User** (Passkey + AI Agent):
```
1. Sign in with passkey
2. Use AI agent for DeFi operations
3. Optionally view agent accounts in Dashboard
4. No manual wallet management needed
```

**Advanced User** (Passkey + Wallet Adapter):
```
1. Sign in with passkey
2. Settings → "Connect External Wallet"
3. Connect Freighter wallet
4. Can now:
   - Use AI agent for complex operations
   - Sign transactions with Freighter for advanced features
   - Import/export funds between Tuxedo and external wallets
   - Participate in governance, staking, etc. via external wallet
```

**Crypto Native User** (Wallet Import):
```
1. "Import from Wallet" on signup page
2. Connect Freighter/Lobstr wallet
3. Create passkey to secure imported account
4. Now has both passkey auth AND wallet signing capability
5. Can export back to wallet anytime
```

---

## Security Considerations

### Threat Model

**Threats Mitigated by Passkeys**:
- ✅ Phishing attacks (cryptographic origin binding)
- ✅ Email interception (no secrets in email)
- ✅ Password reuse (no passwords)
- ✅ Credential stuffing (unique keys per user per site)
- ✅ Man-in-the-middle (private key never leaves device)

**Threats NOT Fully Mitigated**:
- ⚠️ Session hijacking (stolen cookies still work)
  - **Mitigation**: Short session timeouts (7 days → 24 hours), device fingerprinting
- ⚠️ Device theft with biometric bypass
  - **Mitigation**: Require cloud-synced passkeys, multi-device setup
- ⚠️ Malware on user's device
  - **Mitigation**: Hardware security modules (Secure Enclave, TPM), browser sandboxing
- ⚠️ Social engineering (user tricked into exporting keys)
  - **Mitigation**: Warning messages, cooling-off periods, passkey re-verification

### Security Best Practices

**WebAuthn Configuration**:
```python
# backend/config/webauthn.py
WEBAUTHN_CONFIG = {
    "rp_id": "tuxedo.ai",  # Production domain
    "rp_name": "Tuxedo AI",
    "origin": "https://tuxedo.ai",  # HTTPS required
    "user_verification": "required",  # Enforce biometric/PIN
    "authenticator_attachment": "platform",  # Platform authenticators (built-in)
    "require_resident_key": True,  # Discoverable credentials
    "challenge_timeout": 600,  # 10 minutes
    "session_timeout": 86400,  # 24 hours (reduced from 7 days)
}
```

**Database Security**:
- ✅ Encrypt private keys at rest (AES-256)
- ✅ Use parameterized queries (prevent SQL injection)
- ✅ Foreign key constraints (referential integrity)
- ✅ Regular backups with encryption
- ✅ Access logging for all credential operations

**API Security**:
- ✅ Rate limiting (10 requests/minute per IP)
- ✅ HTTPS enforcement (HSTS headers)
- ✅ CORS restrictions (whitelist origins)
- ✅ Input validation (Pydantic models)
- ✅ Output sanitization (prevent XSS)
- ✅ JWT token rotation (refresh tokens)

**Session Management**:
- ✅ HTTP-only cookies (prevent XSS)
- ✅ Secure flag (HTTPS only)
- ✅ SameSite=Lax (CSRF protection)
- ✅ Short expiration (24 hours)
- ✅ Device fingerprinting (detect session hijacking)
- ✅ Concurrent session limits (max 5 devices)

**Key Export Security**:
- ✅ Passkey re-verification required (fresh auth)
- ✅ Encryption with user's passkey public key
- ✅ 24-hour cooling-off period (optional, configurable)
- ✅ Email notification on export
- ✅ Audit logging with IP address, timestamp, device info
- ✅ Warning messages about key security
- ✅ Limit export frequency (1 per 7 days)

### Compliance & Auditing

**Audit Logging**:
```python
# Log all security-sensitive events
log_security_event(
    user_id=user.id,
    event_type="passkey_authentication",
    metadata={
        "ip_address": request.client.host,
        "user_agent": request.headers.get("user-agent"),
        "credential_id": credential_id,
        "timestamp": datetime.utcnow(),
        "success": True/False,
    }
)
```

**Events to Log**:
- Passkey registration
- Passkey authentication (success/failure)
- Passkey deletion
- Wallet connection
- Wallet export
- Session creation
- Session invalidation
- Failed authentication attempts
- Suspicious activity (multiple failures, unusual locations)

**GDPR Compliance**:
- User data export endpoint
- Right to be forgotten (delete all user data)
- Transparent privacy policy
- Consent for biometric data storage
- Data breach notification procedures

**SOC 2 Considerations**:
- Access control policies
- Encryption at rest and in transit
- Regular security audits
- Incident response plan
- Vendor risk management

---

## Migration Plan

### Phase 1: Soft Launch (Month 1)

**Goals**:
- Introduce passkeys as optional feature
- Maintain magic link as primary auth
- Gather user feedback
- Monitor adoption metrics

**Steps**:
1. Deploy passkey infrastructure (backend + frontend)
2. Add "Try Passkeys" button on login page
3. Show passkey setup modal after magic link login
4. Track adoption rate (target: 10% of new users)
5. Monitor error rates, browser compatibility issues
6. Collect user feedback via in-app surveys

**Success Criteria**:
- ✅ 10% adoption among new users
- ✅ <1% authentication failure rate
- ✅ Positive user feedback (>80% satisfaction)
- ✅ No critical security incidents

### Phase 2: Passkey First (Month 2-3)

**Goals**:
- Make passkeys the default authentication
- Magic links as fallback only
- Increase adoption to 50%+ of active users

**Steps**:
1. Update login page: Passkey button primary, magic link secondary
2. Email campaign to existing users: "Upgrade to Passkey Security"
3. In-app notification: "Secure your account with a passkey"
4. One-click passkey setup from settings
5. Track adoption rate (target: 50% of active users)
6. Monitor support tickets, user complaints

**Incentives**:
- "Secured with Passkey" badge in profile
- Early access to new features for passkey users
- Priority support for passkey-enabled accounts

**Success Criteria**:
- ✅ 50% adoption among active users
- ✅ <5% support tickets related to passkeys
- ✅ Positive user sentiment (>70%)

### Phase 3: Passkey Only (Month 4-6)

**Goals**:
- Deprecate magic links
- 100% passkey adoption for active users
- Magic links only for account recovery

**Steps**:
1. Announce magic link deprecation (30-day notice)
2. Block new magic link logins (force passkey setup)
3. Existing magic link sessions honored until expiry
4. Recovery flow: Magic link → immediate passkey setup required
5. Monitor churn, user complaints
6. Provide support for users unable to use passkeys

**Recovery Mechanism**:
- Magic link sends email → user clicks → immediate passkey setup required
- Backup: Recovery codes generated during initial passkey setup
- Support: Manual verification for users unable to use passkeys

**Success Criteria**:
- ✅ 90%+ active users using passkeys
- ✅ <2% churn due to passkey requirement
- ✅ Recovery flow working smoothly

### Phase 4: Advanced Features (Month 6+)

**Goals**:
- Multi-device passkey management
- Cross-device authentication
- Social recovery
- Wallet adapter rollout

**Features**:
1. Multi-device management (add/remove devices)
2. Device naming ("iPhone 15 Pro", "MacBook Air")
3. Cross-device authentication (phone as authenticator for laptop)
4. Social recovery (guardians can help recover account)
5. Wallet adapter for advanced users
6. Conditional UI (passkey autofill)

**Success Criteria**:
- ✅ Average 2+ passkeys per user
- ✅ <1% account lockout rate
- ✅ Wallet adapter adopted by 20% of users

### Rollback Plan

**Trigger Conditions**:
- Authentication failure rate >5%
- Critical security vulnerability discovered
- Widespread user complaints
- Browser compatibility issues affecting >10% of users

**Rollback Steps**:
1. Feature flag to disable passkey auth
2. Revert to magic link as primary auth
3. Announce temporary rollback with timeline
4. Fix underlying issues
5. Gradual re-rollout with fixes

**Communication**:
- In-app notification
- Email to all users
- Status page update
- Social media announcement

---

## Technical Specifications

### Backend Stack

**Python Dependencies**:
```txt
# Core
fastapi>=0.100.0
uvicorn[standard]>=0.23.0
pydantic>=2.0.0
sqlalchemy>=2.0.0

# WebAuthn
webauthn>=2.7.0

# Database
psycopg2-binary>=2.9.0  # PostgreSQL (production)
aiosqlite>=0.19.0       # SQLite (development)

# Session Management
python-jose[cryptography]>=3.3.0  # JWT
redis>=5.0.0                      # Session storage (optional)

# Crypto
cryptography>=41.0.0

# Email (fallback)
sendgrid>=6.10.0
python-dotenv>=1.0.0
```

**Installation**:
```bash
cd backend
pip install webauthn>=2.7.0 cryptography>=41.0.0
```

### Frontend Stack

**NPM Dependencies**:
```json
{
  "dependencies": {
    "@simplewebauthn/browser": "^13.0.0",
    "@creit.tech/stellar-wallets-kit": "^1.9.5",
    "@stellar/stellar-sdk": "^14.2.0",
    "react": "^19.1.1",
    "react-dom": "^19.1.1",
    "react-router-dom": "^7.9.3",
    "axios": "^1.12.2"
  }
}
```

**Installation**:
```bash
npm install @simplewebauthn/browser@^13.0.0
```

### WebAuthn Configuration

**Registration Options**:
```python
from webauthn import generate_registration_options

options = generate_registration_options(
    rp_id="tuxedo.ai",
    rp_name="Tuxedo AI",
    user_id=user_id_bytes,
    user_name=user.email,
    user_display_name=user.email.split('@')[0],
    attestation="none",  # Privacy-preserving
    authenticator_selection={
        "authenticator_attachment": "platform",
        "resident_key": "required",
        "user_verification": "required",
    },
    supported_pub_key_algs=[
        -7,   # ES256 (secp256r1 - Stellar compatible!)
        -257, # RS256 (RSA)
    ],
    timeout=60000,  # 60 seconds
)
```

**Authentication Options**:
```python
from webauthn import generate_authentication_options

options = generate_authentication_options(
    rp_id="tuxedo.ai",
    timeout=60000,
    user_verification="required",
    allow_credentials=[
        {"type": "public-key", "id": credential.credential_id}
        for credential in user.webauthn_credentials
    ] if user else [],
)
```

**Verification**:
```python
from webauthn import verify_authentication_response

verification = verify_authentication_response(
    credential=credential_data,
    expected_challenge=stored_challenge,
    expected_rp_id="tuxedo.ai",
    expected_origin="https://tuxedo.ai",
    credential_public_key=stored_public_key,
    credential_current_sign_count=stored_sign_count,
    require_user_verification=True,
)

if verification.verified:
    # Update sign count (cloning detection)
    credential.sign_count = verification.new_sign_count
    db.commit()

    # Create session
    session_token = create_session(user_id)
    return {"sessionToken": session_token}
```

### Frontend Implementation

**React Hook**:
```typescript
// src/hooks/usePasskeyAuth.ts
import { startRegistration, startAuthentication } from '@simplewebauthn/browser';
import { useState } from 'react';

export function usePasskeyAuth() {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const register = async (email: string) => {
    try {
      setLoading(true);
      setError(null);

      // 1. Get registration options from backend
      const optionsRes = await fetch('/auth/passkey/register/options', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email }),
      });
      const options = await optionsRes.json();

      // 2. Start WebAuthn registration (triggers biometric prompt)
      const credential = await startRegistration(options);

      // 3. Send credential to backend for verification
      const verifyRes = await fetch('/auth/passkey/register/verify', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, credential }),
        credentials: 'include',
      });

      if (!verifyRes.ok) throw new Error('Registration failed');

      const result = await verifyRes.json();
      return result;
    } catch (err: any) {
      setError(err.message || 'Registration failed');
      throw err;
    } finally {
      setLoading(false);
    }
  };

  const authenticate = async (email?: string) => {
    try {
      setLoading(true);
      setError(null);

      // 1. Get authentication options
      const optionsRes = await fetch('/auth/passkey/authenticate/options', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email }),
      });
      const options = await optionsRes.json();

      // 2. Start WebAuthn authentication
      const credential = await startAuthentication(options);

      // 3. Verify with backend
      const verifyRes = await fetch('/auth/passkey/authenticate/verify', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ credential }),
        credentials: 'include',
      });

      if (!verifyRes.ok) throw new Error('Authentication failed');

      const result = await verifyRes.json();
      return result;
    } catch (err: any) {
      setError(err.message || 'Authentication failed');
      throw err;
    } finally {
      setLoading(false);
    }
  };

  return { register, authenticate, loading, error };
}
```

**React Component**:
```typescript
// src/components/auth/PasskeyLogin.tsx
import React, { useState } from 'react';
import { usePasskeyAuth } from '../../hooks/usePasskeyAuth';

export function PasskeyLogin() {
  const [email, setEmail] = useState('');
  const [mode, setMode] = useState<'signin' | 'signup'>('signin');
  const { register, authenticate, loading, error } = usePasskeyAuth();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (mode === 'signup') {
      await register(email);
    } else {
      await authenticate(email);
    }
  };

  return (
    <div className="passkey-login">
      <h2>{mode === 'signup' ? 'Create Account' : 'Sign In'}</h2>

      <form onSubmit={handleSubmit}>
        <input
          type="email"
          placeholder="Email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          required
        />

        <button type="submit" disabled={loading}>
          {loading ? 'Processing...' : mode === 'signup' ? 'Create Passkey' : 'Sign In'}
        </button>
      </form>

      {error && <p className="error">{error}</p>}

      <button onClick={() => setMode(mode === 'signup' ? 'signin' : 'signup')}>
        {mode === 'signup' ? 'Already have an account?' : 'Need an account?'}
      </button>

      <p className="fallback">
        <a href="/auth/magic-link">Can't use passkey? Use email instead</a>
      </p>
    </div>
  );
}
```

### Database Migrations

**SQLite Migration** (Development):
```python
# backend/database.py

async def migrate_to_passkeys():
    """Add passkey tables to existing database"""

    # Create webauthn_credentials table
    await db.execute("""
        CREATE TABLE IF NOT EXISTS webauthn_credentials (
            id TEXT PRIMARY KEY,
            user_id TEXT NOT NULL,
            credential_id BLOB NOT NULL UNIQUE,
            credential_id_b64 TEXT NOT NULL UNIQUE,
            public_key BLOB NOT NULL,
            aaguid TEXT,
            attestation_type TEXT,
            transport TEXT,
            attachment TEXT,
            sign_count INTEGER DEFAULT 0,
            clone_warning BOOLEAN DEFAULT FALSE,
            backup_eligible BOOLEAN DEFAULT FALSE,
            backup_state BOOLEAN DEFAULT TRUE,
            discoverable BOOLEAN DEFAULT TRUE,
            device_name TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_used TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            is_active BOOLEAN DEFAULT TRUE,
            FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
        )
    """)

    # Create webauthn_challenges table
    await db.execute("""
        CREATE TABLE IF NOT EXISTS webauthn_challenges (
            id TEXT PRIMARY KEY,
            user_id TEXT,
            email TEXT,
            challenge BLOB NOT NULL UNIQUE,
            challenge_b64 TEXT NOT NULL UNIQUE,
            operation TEXT NOT NULL,
            expires_at TIMESTAMP NOT NULL,
            used_at TIMESTAMP,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    """)

    # Modify users table
    await db.execute("""
        ALTER TABLE users ADD COLUMN has_passkey BOOLEAN DEFAULT FALSE
    """)
    await db.execute("""
        ALTER TABLE users ADD COLUMN email_verified BOOLEAN DEFAULT FALSE
    """)
    await db.execute("""
        ALTER TABLE users ADD COLUMN recovery_code TEXT
    """)

    # Create indexes
    await db.execute("""
        CREATE INDEX IF NOT EXISTS idx_webauthn_credentials_user_id
        ON webauthn_credentials(user_id)
    """)
    await db.execute("""
        CREATE INDEX IF NOT EXISTS idx_webauthn_credentials_credential_id
        ON webauthn_credentials(credential_id_b64)
    """)
    await db.execute("""
        CREATE INDEX IF NOT EXISTS idx_webauthn_challenges_email
        ON webauthn_challenges(email)
    """)
    await db.execute("""
        CREATE INDEX IF NOT EXISTS idx_webauthn_challenges_expires
        ON webauthn_challenges(expires_at)
    """)

    await db.commit()
    print("✅ Passkey migration complete")
```

**Run Migration**:
```bash
cd backend
python -c "from database import migrate_to_passkeys; import asyncio; asyncio.run(migrate_to_passkeys())"
```

### Environment Variables

```bash
# .env (backend)

# WebAuthn Configuration
WEBAUTHN_RP_ID=tuxedo.ai
WEBAUTHN_RP_NAME="Tuxedo AI"
WEBAUTHN_ORIGIN=https://tuxedo.ai  # Production: HTTPS required
WEBAUTHN_USER_VERIFICATION=required
WEBAUTHN_CHALLENGE_TIMEOUT=600  # 10 minutes
WEBAUTHN_SESSION_TIMEOUT=86400  # 24 hours

# Feature Flags
FEATURE_PASSKEYS_ENABLED=true
FEATURE_MAGIC_LINKS_ENABLED=true  # Disable after migration
FEATURE_WALLET_ADAPTER_ENABLED=true

# Security
SESSION_SECRET=<random-256-bit-key>
JWT_SECRET=<random-256-bit-key>
ENCRYPTION_KEY=<random-256-bit-key>

# Stellar
STELLAR_NETWORK=testnet
HORIZON_URL=https://horizon-testnet.stellar.org
SOROBAN_RPC_URL=https://soroban-testnet.stellar.org

# Email (fallback)
SENDGRID_API_KEY=<key>
FROM_EMAIL=noreply@tuxedo.ai
FRONTEND_URL=https://tuxedo.ai
```

---

## Conclusion

### Why Passkeys Now?

**Security**: Magic links are vulnerable to email interception and phishing. Passkeys provide cryptographic proof of user presence with hardware-backed security.

**User Experience**: Biometric authentication (Face ID, Touch ID) is faster and more intuitive than email magic links. Users don't need to switch apps to check email.

**Industry Standard**: Passkeys are the future of authentication. Google, Apple, Microsoft, and major financial institutions have adopted passkeys. Tuxedo should lead, not follow.

**Stellar Readiness**: Protocol 21 makes Stellar the **most passkey-ready blockchain**. Native secp256r1 verification means we can build smart wallets with passkey signers without workarounds.

**Wallet Bridge**: The wallet adapter pattern allows advanced users to import/export while keeping passkeys as the identity layer. This serves both crypto-natives AND the next 4 billion users.

### Success Metrics

**Phase 1** (Month 1):
- ✅ 10% adoption among new users
- ✅ <1% authentication failure rate
- ✅ Positive user feedback (>80%)

**Phase 2** (Month 2-3):
- ✅ 50% adoption among active users
- ✅ <5% support tickets related to passkeys
- ✅ Wallet adapter adopted by 5% of users

**Phase 3** (Month 4-6):
- ✅ 90%+ active users using passkeys
- ✅ <2% churn due to passkey requirement
- ✅ Wallet adapter adopted by 20% of users

**Long-term** (6+ months):
- ✅ 100% passkey adoption
- ✅ Magic links deprecated
- ✅ Multi-device passkey management
- ✅ Enterprise-grade security audit passed

### Next Steps

1. **Immediate** (This Week):
   - Review and approve this architecture proposal
   - Set up development branch
   - Install dependencies (`webauthn`, `@simplewebauthn/browser`)

2. **Week 1**: Core passkey infrastructure
   - Database migrations
   - Backend passkey endpoints
   - Frontend passkey components
   - Testing on localhost

3. **Week 2**: Wallet integration
   - Stellar Wallets Kit integration
   - Wallet import/export functionality
   - Advanced user features

4. **Week 3**: Migration & cleanup
   - User migration flows
   - Security hardening
   - Documentation
   - Production testing

5. **Week 4**: Launch
   - Soft launch to beta users
   - Monitor metrics
   - Gather feedback
   - Iterate based on data

---

## References

### Research Documents

All research findings compiled in this directory:
- **WebAuthn/FIDO2 Standards**: See agent research output (comprehensive 2024-2025 standards)
- **Crypto Wallet Integration**: See agent research output (Coinbase, Daimo, Stellar)
- **FastAPI Libraries**: See agent research output (Python WebAuthn libraries)
- **Current Auth System**: See `AUTHENTICATION_SYSTEM.md`
- **Wallet Removal**: See `REFACTORING_SUMMARY.md` (commit 970ed6f)

### External Resources

**Official Specifications**:
- W3C WebAuthn Level 2: https://www.w3.org/TR/webauthn-2/
- FIDO Alliance: https://fidoalliance.org/
- Stellar Protocol 21: https://stellar.org/blog/developers/announcing-protocol-21

**Implementation Guides**:
- WebAuthn Guide: https://webauthn.guide/
- SimpleWebAuthn Docs: https://simplewebauthn.dev/
- Stellar Passkey Kit: https://github.com/kalepail/passkey-kit

**Libraries**:
- Python WebAuthn: https://github.com/duo-labs/py_webauthn
- SimpleWebAuthn Browser: https://www.npmjs.com/package/@simplewebauthn/browser
- Stellar Wallets Kit: https://www.npmjs.com/package/@creit.tech/stellar-wallets-kit

**Security**:
- FIDO Security Analysis: https://eprint.iacr.org/2020/756.pdf
- CVE-2024-9956: https://www.offsec.com/blog/cve-2024-9956/
- Passkey Best Practices: https://developers.yubico.com/WebAuthn/WebAuthn_Developer_Guide/

---

## Approval & Sign-off

**Prepared by**: Claude Code (AI Agent)
**Date**: November 5, 2025
**Status**: Awaiting Review

**Reviewers**:
- [ ] Product Owner
- [ ] Security Team
- [ ] Engineering Lead
- [ ] UX/UI Designer

**Approval**:
- [ ] Architecture approved
- [ ] Security review passed
- [ ] Implementation timeline approved
- [ ] Budget approved

---

**End of Document**
