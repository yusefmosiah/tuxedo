# Passkey Implementation: 4-Hour Sprint

**Mode:** Documentation-Driven Development + Agentic Coding
**Timeline:** 4 hours
**Philosophy:** Rapid iteration, exponential compounding

---

## Multi-Agent Architecture (CRITICAL)

### Key Principle: Multiple Agents Run Simultaneously

```
User (passkey auth)
  ├─ Agent 1 (Stellar account A) → Thread 1
  ├─ Agent 2 (Stellar account B) → Thread 2
  └─ Agent N (Stellar account N) → Thread N

Sidebar Structure:
┌─────────────────────┐
│ 🤖 New Agent Box    │ ← Meta chat: Initialize agents
├─────────────────────┤
│ 💬 Thread 1         │
│ 💬 Thread 2         │
│ 💬 Thread N         │
└─────────────────────┘
```

**Mobile-First:** Sidebar chat box IS the primary prompt input

---

## Hour 1: Database + PRF Fallback

### 1.1 Database Schema (15 min)

```sql
-- Drop old magic link tables
DROP TABLE IF EXISTS magic_link_sessions;
DROP TABLE IF EXISTS user_sessions;

-- Passkey tables
CREATE TABLE users (
    id TEXT PRIMARY KEY,
    email TEXT UNIQUE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP
);

CREATE TABLE passkey_credentials (
    id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL,
    credential_id TEXT UNIQUE NOT NULL,
    public_key TEXT NOT NULL,
    sign_count INTEGER DEFAULT 0,
    backup_eligible BOOLEAN DEFAULT FALSE,
    transports TEXT,
    friendly_name TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
);

CREATE TABLE passkey_challenges (
    id TEXT PRIMARY KEY,
    challenge TEXT UNIQUE NOT NULL,
    user_id TEXT,
    expires_at TIMESTAMP NOT NULL,
    used BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE passkey_sessions (
    id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL,
    session_token TEXT UNIQUE NOT NULL,
    expires_at TIMESTAMP NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
);

-- Multi-agent support
CREATE TABLE agents (
    id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL,
    agent_name TEXT NOT NULL,
    stellar_address TEXT UNIQUE NOT NULL,
    encrypted_private_key TEXT NOT NULL,
    permissions TEXT DEFAULT 'trade',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE,
    FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
);

-- Threads (one per agent)
CREATE TABLE threads (
    id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL,
    agent_id TEXT,  -- NULL = meta thread for spawning agents
    title TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users (id),
    FOREIGN KEY (agent_id) REFERENCES agents (id) ON DELETE CASCADE
);

CREATE TABLE messages (
    id TEXT PRIMARY KEY,
    thread_id TEXT NOT NULL,
    role TEXT NOT NULL,
    content TEXT NOT NULL,
    metadata TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (thread_id) REFERENCES threads (id) ON DELETE CASCADE
);

-- Recovery codes
CREATE TABLE recovery_codes (
    id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL,
    code_hash TEXT NOT NULL,
    used BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    used_at TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
);

-- Indexes
CREATE INDEX idx_passkey_credentials_user_id ON passkey_credentials(user_id);
CREATE INDEX idx_passkey_credentials_credential_id ON passkey_credentials(credential_id);
CREATE INDEX idx_passkey_sessions_user_id ON passkey_sessions(user_id);
CREATE INDEX idx_passkey_sessions_token ON passkey_sessions(session_token);
CREATE INDEX idx_agents_user_id ON agents(user_id);
CREATE INDEX idx_threads_user_id ON threads(user_id);
CREATE INDEX idx_threads_agent_id ON threads(agent_id);
```

### 1.2 PRF Fallback Strategy (30 min)

**Problem:** Windows Hello doesn't support PRF extension

**Solution:** Two-tier key derivation

```python
# backend/crypto/key_derivation.py

import secrets
import hashlib
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from stellar_sdk.keypair import Keypair

class KeyDerivation:
    """Handles both PRF-based and server-based key derivation"""

    @staticmethod
    def derive_from_prf(prf_output: bytes, user_id: str) -> Keypair:
        """Derive Stellar keypair from WebAuthn PRF extension"""
        hkdf = HKDF(
            algorithm=hashes.SHA256(),
            length=32,
            salt=b'tuxedo-prf-v1',
            info=user_id.encode()
        )
        seed = hkdf.derive(prf_output)
        return Keypair.from_raw_ed25519_seed(seed)

    @staticmethod
    def derive_from_server(user_id: str, credential_id: str, server_secret: bytes) -> Keypair:
        """Fallback: Server-side deterministic derivation (no PRF)"""
        # Deterministic but server-dependent
        material = f"{user_id}:{credential_id}".encode()

        hkdf = HKDF(
            algorithm=hashes.SHA256(),
            length=32,
            salt=server_secret,  # From environment
            info=b'tuxedo-fallback-v1'
        )
        seed = hkdf.derive(material)
        return Keypair.from_raw_ed25519_seed(seed)

    @staticmethod
    def generate_agent_keypair(user_keypair: Keypair, agent_index: int) -> Keypair:
        """Derive agent keypairs from user's master keypair"""
        # Agent accounts derived from user account
        material = user_keypair.secret.raw_seed() + agent_index.to_bytes(4, 'big')

        seed = hashlib.sha256(material).digest()
        return Keypair.from_raw_ed25519_seed(seed)
```

### 1.3 Recovery Codes (15 min)

```python
# backend/auth/recovery.py

import secrets
import hashlib
import base64

class RecoveryCodeService:
    """Generate and validate recovery codes"""

    CODE_LENGTH = 16
    NUM_CODES = 8

    @staticmethod
    def generate_codes() -> list[str]:
        """Generate 8 recovery codes"""
        codes = []
        for _ in range(RecoveryCodeService.NUM_CODES):
            # Format: XXXX-XXXX-XXXX-XXXX
            code = secrets.token_hex(8).upper()
            formatted = f"{code[0:4]}-{code[4:8]}-{code[8:12]}-{code[12:16]}"
            codes.append(formatted)
        return codes

    @staticmethod
    def hash_code(code: str) -> str:
        """Hash recovery code for storage"""
        clean_code = code.replace("-", "")
        return hashlib.sha256(clean_code.encode()).hexdigest()

    @staticmethod
    async def store_codes(db, user_id: str, codes: list[str]):
        """Store hashed recovery codes"""
        for code in codes:
            code_hash = RecoveryCodeService.hash_code(code)
            await db.execute(
                """INSERT INTO recovery_codes (id, user_id, code_hash)
                   VALUES (?, ?, ?)""",
                (f"rc_{secrets.token_urlsafe(16)}", user_id, code_hash)
            )

    @staticmethod
    async def validate_code(db, user_id: str, code: str) -> bool:
        """Validate and mark recovery code as used"""
        code_hash = RecoveryCodeService.hash_code(code)

        result = await db.execute(
            """SELECT id FROM recovery_codes
               WHERE user_id = ? AND code_hash = ? AND used = FALSE""",
            (user_id, code_hash)
        )

        row = await result.fetchone()
        if not row:
            return False

        # Mark as used
        await db.execute(
            """UPDATE recovery_codes SET used = TRUE, used_at = CURRENT_TIMESTAMP
               WHERE id = ?""",
            (row['id'],)
        )
        return True
```

---

## Hour 2: Backend Passkey Endpoints

### 2.1 Install Dependencies (5 min)

```toml
# backend/pyproject.toml
dependencies = [
    "fastapi>=0.115.5",
    "webauthn>=2.2.0",  # NEW
    "py-webauthn>=2.0.0",  # Alternative
    "cryptography>=41.0.0",
    "stellar-sdk>=13.1.0",
]
```

```bash
cd backend && uv sync
```

### 2.2 Passkey Routes (55 min)

```python
# backend/api/routes/passkey.py

from fastapi import APIRouter, HTTPException, Response, Request, Depends
from pydantic import BaseModel, EmailStr
import secrets
from datetime import datetime, timedelta
from webauthn import (
    generate_registration_options,
    verify_registration_response,
    generate_authentication_options,
    verify_authentication_response,
)
from webauthn.helpers.structs import (
    PublicKeyCredentialRpEntity,
    PublicKeyCredentialUserEntity,
)

router = APIRouter(prefix="/auth/passkey", tags=["passkey"])

# Request models
class RegistrationStartRequest(BaseModel):
    email: EmailStr

class RegistrationVerifyRequest(BaseModel):
    email: EmailStr
    credential: dict  # WebAuthn credential response

class AuthenticationStartRequest(BaseModel):
    email: EmailStr | None = None  # Username-less if None

class AuthenticationVerifyRequest(BaseModel):
    credential: dict  # WebAuthn credential response

# RP configuration
RP_ID = "localhost"  # Change for production
RP_NAME = "Tuxedo AI"
RP_ORIGIN = "http://localhost:5173"

@router.post("/register/start")
async def start_registration(req: RegistrationStartRequest, request: Request):
    """Start passkey registration"""
    db = request.app.state.db

    # Check if user exists
    user = await db.get_user_by_email(req.email)
    if user:
        raise HTTPException(400, "User already exists")

    # Generate challenge
    challenge = secrets.token_bytes(32)
    challenge_id = f"ch_{secrets.token_urlsafe(16)}"

    # Store challenge
    await db.execute(
        """INSERT INTO passkey_challenges (id, challenge, expires_at)
           VALUES (?, ?, ?)""",
        (challenge_id, challenge.hex(), datetime.utcnow() + timedelta(minutes=15))
    )

    # Generate registration options
    options = generate_registration_options(
        rp_id=RP_ID,
        rp_name=RP_NAME,
        user_id=req.email.encode(),
        user_name=req.email,
        user_display_name=req.email,
        challenge=challenge,
        authenticator_selection={
            "authenticatorAttachment": "platform",
            "userVerification": "required",
            "residentKey": "required",
        },
        extensions={
            "prf": {}  # Request PRF if available
        }
    )

    return {
        "challenge_id": challenge_id,
        "options": options
    }

@router.post("/register/verify")
async def verify_registration(req: RegistrationVerifyRequest, request: Request):
    """Verify passkey registration and create user"""
    db = request.app.state.db

    try:
        # Verify WebAuthn response
        verification = verify_registration_response(
            credential=req.credential,
            expected_challenge=...,  # Get from challenge_id
            expected_origin=RP_ORIGIN,
            expected_rp_id=RP_ID,
        )

        # Check PRF support
        has_prf = "prf" in verification.credential_device_type

        # Create user
        user_id = f"user_{secrets.token_urlsafe(16)}"
        await db.execute(
            """INSERT INTO users (id, email) VALUES (?, ?)""",
            (user_id, req.email)
        )

        # Store credential
        cred_id = f"cred_{secrets.token_urlsafe(16)}"
        await db.execute(
            """INSERT INTO passkey_credentials
               (id, user_id, credential_id, public_key, backup_eligible, transports)
               VALUES (?, ?, ?, ?, ?, ?)""",
            (
                cred_id,
                user_id,
                verification.credential_id,
                verification.credential_public_key,
                verification.credential_backed_up,
                ",".join(verification.credential_device_type.transports or [])
            )
        )

        # Derive Stellar account
        from backend.crypto.key_derivation import KeyDerivation

        if has_prf:
            prf_output = verification.extensions.get("prf", {}).get("enabled")
            keypair = KeyDerivation.derive_from_prf(prf_output, user_id)
        else:
            # Fallback: server-side derivation
            server_secret = request.app.state.server_secret
            keypair = KeyDerivation.derive_from_server(
                user_id, verification.credential_id, server_secret
            )

        # Store Stellar public key reference (don't store private key)
        await db.execute(
            """UPDATE users SET stellar_public_key = ? WHERE id = ?""",
            (keypair.public_key, user_id)
        )

        # Generate recovery codes
        from backend.auth.recovery import RecoveryCodeService
        recovery_codes = RecoveryCodeService.generate_codes()
        await RecoveryCodeService.store_codes(db, user_id, recovery_codes)

        # Create session
        session_token = secrets.token_urlsafe(32)
        await db.execute(
            """INSERT INTO passkey_sessions (id, user_id, session_token, expires_at)
               VALUES (?, ?, ?, ?)""",
            (
                f"sess_{secrets.token_urlsafe(16)}",
                user_id,
                session_token,
                datetime.utcnow() + timedelta(days=7)
            )
        )

        return {
            "success": True,
            "session_token": session_token,
            "user": {"id": user_id, "email": req.email},
            "recovery_codes": recovery_codes,  # Show once
            "has_prf": has_prf
        }

    except Exception as e:
        raise HTTPException(400, f"Registration failed: {str(e)}")

@router.post("/login/start")
async def start_authentication(req: AuthenticationStartRequest, request: Request):
    """Start passkey authentication"""
    db = request.app.state.db

    # Generate challenge
    challenge = secrets.token_bytes(32)
    challenge_id = f"ch_{secrets.token_urlsafe(16)}"

    # Store challenge
    await db.execute(
        """INSERT INTO passkey_challenges (id, challenge, expires_at)
           VALUES (?, ?, ?)""",
        (challenge_id, challenge.hex(), datetime.utcnow() + timedelta(minutes=15))
    )

    # Get user's credentials (if email provided)
    allow_credentials = []
    if req.email:
        user = await db.get_user_by_email(req.email)
        if user:
            credentials = await db.execute(
                """SELECT credential_id FROM passkey_credentials WHERE user_id = ?""",
                (user['id'],)
            )
            allow_credentials = [{"id": c['credential_id'], "type": "public-key"}
                                  for c in await credentials.fetchall()]

    # Generate authentication options
    options = generate_authentication_options(
        rp_id=RP_ID,
        challenge=challenge,
        allow_credentials=allow_credentials,
        user_verification="required",
        extensions={"prf": {}}
    )

    return {
        "challenge_id": challenge_id,
        "options": options
    }

@router.post("/login/verify")
async def verify_authentication(req: AuthenticationVerifyRequest, request: Request):
    """Verify passkey authentication"""
    db = request.app.state.db

    try:
        # Get credential from DB
        credential = await db.execute(
            """SELECT * FROM passkey_credentials WHERE credential_id = ?""",
            (req.credential['id'],)
        )
        cred_row = await credential.fetchone()
        if not cred_row:
            raise HTTPException(401, "Invalid credential")

        # Verify WebAuthn response
        verification = verify_authentication_response(
            credential=req.credential,
            expected_challenge=...,  # Get from challenge_id
            expected_origin=RP_ORIGIN,
            expected_rp_id=RP_ID,
            credential_public_key=cred_row['public_key'],
            credential_current_sign_count=cred_row['sign_count'],
        )

        # Update sign count
        await db.execute(
            """UPDATE passkey_credentials SET sign_count = ?, last_used = CURRENT_TIMESTAMP
               WHERE id = ?""",
            (verification.new_sign_count, cred_row['id'])
        )

        # Get user
        user = await db.execute(
            """SELECT * FROM users WHERE id = ?""",
            (cred_row['user_id'],)
        )
        user_row = await user.fetchone()

        # Create session
        session_token = secrets.token_urlsafe(32)
        await db.execute(
            """INSERT INTO passkey_sessions (id, user_id, session_token, expires_at)
               VALUES (?, ?, ?, ?)""",
            (
                f"sess_{secrets.token_urlsafe(16)}",
                user_row['id'],
                session_token,
                datetime.utcnow() + timedelta(days=7)
            )
        )

        return {
            "success": True,
            "session_token": session_token,
            "user": {"id": user_row['id'], "email": user_row['email']}
        }

    except Exception as e:
        raise HTTPException(401, f"Authentication failed: {str(e)}")
```

---

## Hour 3: Frontend Passkey Integration

### 3.1 Install Dependencies (5 min)

```json
// package.json
{
  "dependencies": {
    "@simplewebauthn/browser": "^10.0.0"
  }
}
```

```bash
npm install @simplewebauthn/browser
```

### 3.2 Passkey Service (30 min)

```typescript
// src/services/passkeyAuth.ts

import {
  startRegistration,
  startAuthentication,
  type RegistrationResponseJSON,
  type AuthenticationResponseJSON,
} from "@simplewebauthn/browser";

const API_URL = "http://localhost:8000";

export class PasskeyAuthService {
  async register(email: string) {
    try {
      // 1. Start registration
      const optionsRes = await fetch(`${API_URL}/auth/passkey/register/start`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email }),
      });

      if (!optionsRes.ok) {
        const error = await optionsRes.json();
        throw new Error(error.detail || "Registration failed");
      }

      const { challenge_id, options } = await optionsRes.json();

      // 2. Create passkey
      const credential = await startRegistration(options);

      // 3. Verify registration
      const verifyRes = await fetch(`${API_URL}/auth/passkey/register/verify`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email, credential }),
      });

      if (!verifyRes.ok) {
        const error = await verifyRes.json();
        throw new Error(error.detail || "Verification failed");
      }

      const result = await verifyRes.json();

      // Store session
      localStorage.setItem("session_token", result.session_token);
      localStorage.setItem("user", JSON.stringify(result.user));

      return {
        success: true,
        user: result.user,
        recovery_codes: result.recovery_codes,
        has_prf: result.has_prf,
      };
    } catch (error) {
      console.error("Passkey registration failed:", error);
      throw error;
    }
  }

  async authenticate(email?: string) {
    try {
      // 1. Start authentication
      const optionsRes = await fetch(`${API_URL}/auth/passkey/login/start`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email }),
      });

      if (!optionsRes.ok) {
        throw new Error("Failed to get authentication options");
      }

      const { challenge_id, options } = await optionsRes.json();

      // 2. Authenticate with passkey
      const credential = await startAuthentication(options);

      // 3. Verify authentication
      const verifyRes = await fetch(`${API_URL}/auth/passkey/login/verify`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ credential }),
      });

      if (!verifyRes.ok) {
        throw new Error("Authentication failed");
      }

      const result = await verifyRes.json();

      // Store session
      localStorage.setItem("session_token", result.session_token);
      localStorage.setItem("user", JSON.stringify(result.user));

      return {
        success: true,
        user: result.user,
      };
    } catch (error) {
      console.error("Passkey authentication failed:", error);
      throw error;
    }
  }

  async validateSession(token: string) {
    try {
      const res = await fetch(`${API_URL}/auth/validate-session`, {
        method: "POST",
        headers: { Authorization: `Bearer ${token}` },
      });

      if (!res.ok) return null;

      const result = await res.json();
      return result.user;
    } catch {
      return null;
    }
  }

  logout() {
    localStorage.removeItem("session_token");
    localStorage.removeItem("user");
  }
}
```

### 3.3 Auth Context (25 min)

```typescript
// src/contexts/AuthContext.tsx

import React, { createContext, useContext, useState, useEffect } from "react";
import { PasskeyAuthService } from "../services/passkeyAuth";

interface User {
  id: string;
  email: string;
}

interface AuthContextType {
  user: User | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  register: (email: string) => Promise<any>;
  authenticate: (email?: string) => Promise<void>;
  logout: () => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  const passkeyService = new PasskeyAuthService();

  useEffect(() => {
    // Check for existing session
    const checkSession = async () => {
      const token = localStorage.getItem("session_token");
      if (token) {
        const user = await passkeyService.validateSession(token);
        if (user) {
          setUser(user);
        } else {
          localStorage.removeItem("session_token");
          localStorage.removeItem("user");
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
      setUser(result.user);
      return result;
    } finally {
      setIsLoading(false);
    }
  };

  const authenticate = async (email?: string) => {
    setIsLoading(true);
    try {
      const result = await passkeyService.authenticate(email);
      setUser(result.user);
    } finally {
      setIsLoading(false);
    }
  };

  const logout = () => {
    passkeyService.logout();
    setUser(null);
  };

  return (
    <AuthContext.Provider
      value={{
        user,
        isAuthenticated: !!user,
        isLoading,
        register,
        authenticate,
        logout,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error("useAuth must be used within AuthProvider");
  }
  return context;
}
```

---

## Hour 4: Multi-Agent UI + Testing

### 4.1 Sidebar with Meta Chat Box (30 min)

```typescript
// src/components/Sidebar.tsx

import React, { useState } from "react";
import { useAuth } from "../contexts/AuthContext";

interface Thread {
  id: string;
  title: string;
  agent_id?: string;
}

export function Sidebar() {
  const { user } = useAuth();
  const [threads, setThreads] = useState<Thread[]>([]);
  const [metaInput, setMetaInput] = useState("");

  const handleMetaSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!metaInput.trim()) return;

    // Create new agent + thread
    const res = await fetch("/api/agents/create", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${localStorage.getItem("session_token")}`,
      },
      body: JSON.stringify({
        initial_prompt: metaInput,
      }),
    });

    const { agent, thread } = await res.json();

    setThreads([...threads, thread]);
    setMetaInput("");

    // Navigate to new thread
    window.location.href = `/chat/${thread.id}`;
  };

  return (
    <aside className="sidebar">
      {/* Meta Chat Box - Hierarchical Top */}
      <div className="meta-chat-box">
        <h3>🤖 Initialize Agent</h3>
        <form onSubmit={handleMetaSubmit}>
          <input
            type="text"
            value={metaInput}
            onChange={(e) => setMetaInput(e.target.value)}
            placeholder="Start a new AI agent..."
            className="meta-input"
          />
          <button type="submit">Spawn Agent</button>
        </form>
      </div>

      {/* Thread List */}
      <div className="thread-list">
        <h4>Active Agents</h4>
        {threads.map((thread) => (
          <div key={thread.id} className="thread-item">
            <a href={`/chat/${thread.id}`}>{thread.title}</a>
          </div>
        ))}
      </div>

      {/* User Info */}
      <div className="user-info">
        <p>{user?.email}</p>
        <button onClick={() => {}}>Settings</button>
      </div>
    </aside>
  );
}
```

### 4.2 Agent Creation Endpoint (15 min)

```python
# backend/api/routes/agents.py

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
import secrets

router = APIRouter(prefix="/api/agents", tags=["agents"])

class CreateAgentRequest(BaseModel):
    initial_prompt: str

@router.post("/create")
async def create_agent(req: CreateAgentRequest, user=Depends(get_current_user)):
    """Create new AI agent with Stellar account"""
    db = ...

    # Derive agent keypair from user's master keypair
    from backend.crypto.key_derivation import KeyDerivation

    # Get user's keypair (re-derive or retrieve)
    user_keypair = ...  # Derive from passkey or retrieve

    # Get next agent index
    agent_count = await db.execute(
        """SELECT COUNT(*) as count FROM agents WHERE user_id = ?""",
        (user['id'],)
    )
    agent_index = (await agent_count.fetchone())['count']

    # Derive agent keypair
    agent_keypair = KeyDerivation.generate_agent_keypair(user_keypair, agent_index)

    # Create agent
    agent_id = f"agent_{secrets.token_urlsafe(16)}"
    await db.execute(
        """INSERT INTO agents (id, user_id, agent_name, stellar_address, encrypted_private_key)
           VALUES (?, ?, ?, ?, ?)""",
        (
            agent_id,
            user['id'],
            f"Agent {agent_index + 1}",
            agent_keypair.public_key,
            ""  # Don't store private key if derivable
        )
    )

    # Create thread for agent
    thread_id = f"thread_{secrets.token_urlsafe(16)}"
    await db.execute(
        """INSERT INTO threads (id, user_id, agent_id, title)
           VALUES (?, ?, ?, ?)""",
        (thread_id, user['id'], agent_id, f"Agent {agent_index + 1}")
    )

    # Add initial message
    await db.execute(
        """INSERT INTO messages (id, thread_id, role, content)
           VALUES (?, ?, ?, ?)""",
        (
            f"msg_{secrets.token_urlsafe(16)}",
            thread_id,
            "user",
            req.initial_prompt
        )
    )

    return {
        "success": True,
        "agent": {
            "id": agent_id,
            "stellar_address": agent_keypair.public_key
        },
        "thread": {
            "id": thread_id,
            "title": f"Agent {agent_index + 1}"
        }
    }
```

### 4.3 Testing (15 min)

```bash
# Terminal 1: Backend
cd backend
source .venv/bin/activate
python main.py

# Terminal 2: Frontend
npm run dev

# Manual Test Flow:
# 1. Open http://localhost:5173
# 2. Click "Register with Passkey"
# 3. Enter email, create passkey
# 4. Save recovery codes
# 5. Type prompt in meta chat box
# 6. Verify new agent + thread created
# 7. Test multiple agents running
```

---

## Critical Path Checklist

**Hour 1:**
- [ ] Run database migration script
- [ ] Implement PRF fallback
- [ ] Implement recovery codes
- [ ] Test key derivation

**Hour 2:**
- [ ] Install webauthn dependencies
- [ ] Implement registration endpoints
- [ ] Implement authentication endpoints
- [ ] Test with Postman/curl

**Hour 3:**
- [ ] Install @simplewebauthn/browser
- [ ] Implement PasskeyAuthService
- [ ] Update AuthContext
- [ ] Test registration flow

**Hour 4:**
- [ ] Build sidebar with meta chat
- [ ] Implement agent creation
- [ ] Test multi-agent spawning
- [ ] Deploy and verify

---

## Key Architecture Decisions

1. **PRF Fallback:** Two-tier (PRF preferred, server-derivation fallback)
2. **Multi-Agent:** Derived from user's master keypair
3. **Meta Chat Box:** Hierarchical top of sidebar = agent spawner
4. **Mobile-First:** Sidebar chat is primary UI
5. **Recovery:** 8 codes, single-use, shown once during registration

---

## Post-Sprint: Documentation Sweep

After passkey implementation, run comprehensive doc sweep to:
- Update CLAUDE.md with passkey architecture
- Consolidate passkey docs
- Archive outdated content
- Add mobile-specific docs

**Next 4 hours: SHIP IT.**
