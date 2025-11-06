# Passkey Authentication Architecture v2
**Clean Separation of Concerns**

---

## Core Principle

**Passkeys are for AUTHENTICATION, not APPLICATION FEATURES.**

Authentication answers: "Who are you?"
Application features answer: "What can you do?"

**Do not conflate these concerns.**

---

## Phase 1: Passkey Authentication (Current Sprint)

### Scope

Replace magic link authentication with WebAuthn passkey authentication.

**In Scope**:
- User registration with passkey
- User login with passkey
- Session management (token-based)
- Recovery codes (8 single-use backup codes)
- Session validation endpoint

**Out of Scope** (for this sprint):
- Multi-agent system
- Stellar key derivation from passkeys
- Sidebar UI component
- Thread-to-agent relationships
- Any "advanced" WebAuthn features (PRF, etc.)

### Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     User Authentication                      │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  Registration:                                               │
│  1. User enters email                                        │
│  2. Browser creates passkey (WebAuthn)                       │
│  3. Server stores credential                                 │
│  4. Server generates 8 recovery codes                        │
│  5. Server creates session token                             │
│  → User is authenticated                                     │
│                                                              │
│  Login:                                                      │
│  1. User clicks "Login with Passkey"                         │
│  2. Browser prompts for passkey                              │
│  3. Server verifies credential                               │
│  4. Server creates session token                             │
│  → User is authenticated                                     │
│                                                              │
│  Recovery:                                                   │
│  1. User enters recovery code                                │
│  2. Server validates and marks code as used                  │
│  3. Server creates session token                             │
│  → User is authenticated                                     │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

### Database Schema

#### New Tables

```sql
-- Store WebAuthn credentials
CREATE TABLE passkey_credentials (
    id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL,
    credential_id TEXT UNIQUE NOT NULL,
    public_key TEXT NOT NULL,
    sign_count INTEGER DEFAULT 0,
    backup_eligible BOOLEAN DEFAULT FALSE,
    transports TEXT,  -- JSON array
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_used_at TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
);

-- Store authentication challenges (short-lived)
CREATE TABLE passkey_challenges (
    id TEXT PRIMARY KEY,
    challenge TEXT UNIQUE NOT NULL,
    user_id TEXT,  -- NULL for login start
    expires_at TIMESTAMP NOT NULL,
    used BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Store active sessions
CREATE TABLE passkey_sessions (
    id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL,
    session_token TEXT UNIQUE NOT NULL,
    expires_at TIMESTAMP NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_active_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
);

-- Store recovery codes
CREATE TABLE recovery_codes (
    id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL,
    code_hash TEXT NOT NULL,  -- SHA-256 hash
    used BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    used_at TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
);
```

#### Indexes

```sql
CREATE INDEX idx_passkey_credentials_user_id ON passkey_credentials(user_id);
CREATE INDEX idx_passkey_credentials_credential_id ON passkey_credentials(credential_id);
CREATE INDEX idx_passkey_sessions_user_id ON passkey_sessions(user_id);
CREATE INDEX idx_passkey_sessions_token ON passkey_sessions(session_token);
CREATE INDEX idx_recovery_codes_user_id ON recovery_codes(user_id);
```

#### Tables to Remove

```sql
DROP TABLE IF EXISTS magic_link_sessions;
DROP TABLE IF EXISTS user_sessions;
```

### API Endpoints

#### Registration

```
POST /auth/passkey/register/start
Request:  { email: string }
Response: { challenge_id: string, options: PublicKeyCredentialCreationOptions }

POST /auth/passkey/register/verify
Request:  { email: string, challenge_id: string, credential: object }
Response: {
    user: { id, email },
    session_token: string,
    recovery_codes: string[],  // Only shown once!
    recovery_codes_message: string
}
```

#### Authentication

```
POST /auth/passkey/login/start
Request:  { email?: string }  // Optional for usernameless flow
Response: { challenge_id: string, options: PublicKeyCredentialRequestOptions }

POST /auth/passkey/login/verify
Request:  { challenge_id: string, credential: object }
Response: {
    user: { id, email },
    session_token: string
}
```

#### Recovery

```
POST /auth/passkey/recovery/verify
Request:  { code: string }
Response: {
    user: { id, email },
    session_token: string
}
```

#### Session Management

```
POST /auth/validate-passkey-session
Headers:  Authorization: Bearer <session_token>
Response: { user: { id, email }, valid: true }

POST /auth/logout
Headers:  Authorization: Bearer <session_token>
Response: { success: true }
```

### Frontend Implementation

#### Core Service

```typescript
// src/services/passkeyAuth.ts
export class PasskeyAuthService {
  async register(email: string): Promise<RegistrationResult>
  async authenticate(email?: string): Promise<AuthResult>
  async useRecoveryCode(code: string): Promise<AuthResult>
  async validateSession(token: string): Promise<User | null>
  logout(): void
  isSupported(): boolean
}
```

#### UI Components

**Minimal changes**:
- Update `src/components/Login.tsx` to use passkey service
- Update `src/contexts/AuthContext.tsx` to manage passkey sessions
- **NO sidebar changes**
- **NO layout changes**

### Security Considerations

#### Session Tokens
- Random 32-byte tokens (URL-safe base64)
- 7-day expiration (configurable)
- Stored in localStorage
- Sent as Bearer token in Authorization header

#### Recovery Codes
- 8 codes, each 24 characters (128-bit entropy)
- SHA-256 hashed before storage
- Single-use only (marked as used after validation)
- Displayed once during registration

#### Challenges
- 32-byte random challenges
- 15-minute expiration
- Single-use only
- Cleaned up after use or expiration

#### WebAuthn Configuration
- Relying Party ID: Domain name (e.g., "localhost" for dev)
- User Verification: Required
- Resident Key: Required (for usernameless flow)
- Authenticator Attachment: Platform preferred
- Attestation: None (simplest, most compatible)

### Testing Strategy

#### Unit Tests
- [ ] Passkey credential creation and storage
- [ ] Challenge generation and validation
- [ ] Session token generation and validation
- [ ] Recovery code generation and hashing
- [ ] Recovery code single-use enforcement

#### Integration Tests
- [ ] Full registration flow
- [ ] Full login flow
- [ ] Recovery code flow
- [ ] Session validation
- [ ] Session expiration
- [ ] Invalid credential rejection

#### Manual Testing Checklist
- [ ] Register new user with passkey
- [ ] Login with passkey
- [ ] Login fails with wrong passkey
- [ ] Save recovery codes
- [ ] Login with recovery code
- [ ] Recovery code only works once
- [ ] Session persists across page refresh
- [ ] Logout clears session
- [ ] Session expires after 7 days

### Deployment Checklist

#### Pre-Deployment
- [ ] All tests pass
- [ ] `npm run build` succeeds
- [ ] Backend starts without errors
- [ ] All dependencies installed (frontend and backend)
- [ ] Environment variables configured
- [ ] Database backup created

#### Deployment Steps
1. **Backup production database**
   ```bash
   cp tuxedo.db tuxedo.db.backup.$(date +%Y%m%d_%H%M%S)
   ```

2. **Install backend dependencies**
   ```bash
   cd backend
   source .venv/bin/activate
   uv sync
   # or: pip install -r requirements.txt
   ```

3. **Install frontend dependencies**
   ```bash
   npm install
   ```

4. **Run database migration**
   ```bash
   cd backend
   python migrate_to_passkeys.py
   ```

5. **Build frontend**
   ```bash
   npm run build
   ```

6. **Test backend health**
   ```bash
   cd backend
   python -c "from api.routes import passkey; print('✓ Passkey routes OK')"
   python main.py &
   sleep 5
   curl http://localhost:8000/health
   ```

7. **Deploy**
   ```bash
   # Your deployment process here
   ```

8. **Smoke test**
   - Visit login page
   - Test registration flow
   - Test login flow
   - Test recovery code

#### Rollback Plan

If deployment fails:

1. **Stop services**
2. **Restore database backup**
   ```bash
   cp tuxedo.db.backup.YYYYMMDD_HHMMSS tuxedo.db
   ```
3. **Revert code to previous commit**
   ```bash
   git checkout <previous-stable-commit>
   ```
4. **Restart services**

---

## Phase 2: Multi-Agent System (Future)

**Not in current sprint. Document for future reference.**

### Scope

Add ability for authenticated users to create and manage multiple AI agents.

### Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                  Multi-Agent Management                      │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  User (authenticated via passkey)                            │
│  │                                                           │
│  ├── Agent 1                                                 │
│  │   ├── Name: "Trading Bot"                                │
│  │   ├── Stellar Accounts:                                  │
│  │   │   ├── Account 1 (trading)                            │
│  │   │   └── Account 2 (backup)                             │
│  │   └── Threads:                                           │
│  │       └── Thread 1 (conversation history)                │
│  │                                                           │
│  ├── Agent 2                                                 │
│  │   ├── Name: "Research Assistant"                         │
│  │   ├── Stellar Accounts:                                  │
│  │   │   └── Account 3 (research)                           │
│  │   └── Threads:                                           │
│  │       └── Thread 2 (research notes)                      │
│  │                                                           │
│  └── Agent N                                                 │
│      └── ...                                                 │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

**Key Points**:
- Agents are **application features**, not auth features
- Each agent can have **multiple** Stellar accounts
- User manages agents via API (CRUD operations)
- Agents are created **after** authentication
- No cryptographic coupling between passkey and agent keys

### Database Schema (Future)

```sql
CREATE TABLE agents (
    id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL,
    name TEXT NOT NULL,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    active BOOLEAN DEFAULT TRUE,
    FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
);

CREATE TABLE agent_stellar_accounts (
    id TEXT PRIMARY KEY,
    agent_id TEXT NOT NULL,
    public_key TEXT NOT NULL,
    private_key_encrypted TEXT NOT NULL,  -- Encrypted, NOT derived
    label TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (agent_id) REFERENCES agents (id) ON DELETE CASCADE
);

-- Update threads table
ALTER TABLE threads ADD COLUMN agent_id TEXT REFERENCES agents(id);
```

### API Endpoints (Future)

```
POST   /api/agents/          - Create new agent
GET    /api/agents/          - List user's agents
GET    /api/agents/:id       - Get agent details
PATCH  /api/agents/:id       - Update agent
DELETE /api/agents/:id       - Deactivate agent

POST   /api/agents/:id/accounts/  - Add Stellar account to agent
GET    /api/agents/:id/accounts/  - List agent's accounts
DELETE /api/agents/:id/accounts/:account_id  - Remove account
```

---

## Phase 3: UI Enhancements (Future)

**Not in current sprint. Document for future reference.**

### Scope

Add sidebar component for agent management and thread switching.

### Components

- `Sidebar.tsx` - Agent list and thread switcher
- `AgentSettings.tsx` - Agent configuration
- `ThreadHistory.tsx` - Conversation history

**Implementation**: After Phase 1 and Phase 2 are complete and tested.

---

## Success Metrics

### Phase 1 (Current Sprint)
- [ ] Users can register with passkey
- [ ] Users can login with passkey
- [ ] Recovery codes work
- [ ] Sessions persist correctly
- [ ] All tests pass
- [ ] Build succeeds
- [ ] Deployment works
- [ ] No security vulnerabilities

### Phase 2 (Future)
- [ ] Users can create agents
- [ ] Users can manage multiple agents
- [ ] Agents can have multiple Stellar accounts
- [ ] Thread-to-agent relationships work

### Phase 3 (Future)
- [ ] Sidebar shows agent list
- [ ] Users can switch between agents
- [ ] UI is responsive and intuitive

---

## Why This Architecture?

### Separation of Concerns

**Authentication Layer** (Phase 1):
- Handles: Who is the user?
- Concerns: Security, sessions, credentials
- Changes rarely

**Application Layer** (Phase 2):
- Handles: What can the user do?
- Concerns: Business logic, features, data
- Changes frequently

**Presentation Layer** (Phase 3):
- Handles: How does the user interact?
- Concerns: UI, UX, responsiveness
- Changes very frequently

### Testability

Each phase can be:
- Developed independently
- Tested independently
- Deployed independently
- Rolled back independently

### Simplicity

**Phase 1 complexity**: Low
- Standard WebAuthn implementation
- No crypto derivation
- No complex relationships
- ~500 lines of code

**Phase 2 complexity**: Medium
- Agent CRUD operations
- Account management
- Standard database relations
- ~300 lines of code

**Phase 3 complexity**: Low
- UI components
- State management
- ~200 lines of code

**Total**: ~1000 lines of focused, testable code
vs. Experimental branch: ~2000 lines of tightly coupled code

### Maintainability

- Each phase has clear boundaries
- Changes in one phase don't affect others
- Easy to onboard new developers
- Easy to debug issues
- Easy to add features

---

## What We Learned from Experimental Branch

### What Worked ✅
- WebAuthn endpoint structure
- Database schema design (for passkeys)
- Recovery code system
- Frontend service patterns

### What Didn't Work ❌
- Coupling passkeys to agent key derivation
- PRF extension complexity
- Sidebar in auth sprint
- Skipping deployment checklist

### Applying the Lessons ✅
- Focus on ONE thing: passkey auth
- Save agent system for Phase 2
- Save UI changes for Phase 3
- Follow deployment checklist religiously
- Test at each step

---

## Next Steps for Current Sprint

1. **Create fresh database** (we're in R&D mode, no migration needed)
2. **Implement Phase 1 passkey authentication** (only)
3. **Test thoroughly** (unit + integration + manual)
4. **Deploy carefully** (follow checklist)
5. **Verify in production** (smoke tests)
6. **Document lessons learned**

Then, and only then, move to Phase 2.

---

**Document Version**: 2.0
**Last Updated**: 2025-11-06
**Status**: Current architectural plan
