# Agent Filesystem Isolation Strategy
**Preventing Cross-User Data Access in Multi-Tenant Agent Environment**

---

## The Problem

**Question:** How do we prevent an agent running for user X from accessing filesystem data belonging to user Y?

**Challenge:** If all agents run in the same Python process/environment, they have access to the same filesystem. Database-level isolation isn't enough if agents can read each other's files.

---

## Threat Model

### What Needs Protection?

1. **Private Keys** - Most critical
2. **Agent State/Memory** - Tool outputs, reasoning chains, context
3. **Research Reports** - Generated strategy documents
4. **User Data** - Portfolio configurations, preferences
5. **Temporary Files** - Tool execution artifacts

### Attack Vectors

1. **Malicious User Code** - User-provided prompts that attempt directory traversal
2. **Agent Misbehavior** - LLM hallucinations trying to access wrong paths
3. **Tool Exploits** - Compromised tools accessing unauthorized files
4. **Process Compromise** - If one agent is compromised, can it access other users' data?

---

## Layered Security Strategy

### Layer 1: No Private Keys on Filesystem (Implemented)

**Current Design:** Private keys are stored encrypted in the database, **never** written to disk.

```python
# ✅ CORRECT: Keys live in database only
class PortfolioManager:
    def get_keypair_for_signing(self, user_id: str, account_id: str):
        # 1. Fetch encrypted key from database
        account = self._get_account_by_id(account_id)

        # 2. Verify ownership
        if not self._verify_ownership(user_id, account):
            raise PermissionError("Not your account")

        # 3. Decrypt in-memory
        private_key = self.encryption.decrypt(
            account['encrypted_private_key'],
            user_id
        )

        # 4. Create keypair object (in-memory)
        adapter = self.chains[account['chain']]
        keypair = adapter.import_keypair(private_key)

        # 5. Return for immediate use
        return keypair
        # 6. Keypair is garbage collected after use
```

**Key points:**
- Private keys **never** touch the filesystem
- Decrypted keys exist only in-memory during transaction signing
- Python garbage collection clears keys from memory after use
- Even if filesystem is compromised, keys are safe

### Layer 2: Agent Execution Context with User ID

**Design:** Every agent operation carries a `user_id` context that's enforced at multiple layers.

```python
# Agent initialization with user context
class UserAgentExecutor:
    """Agent executor that enforces user isolation"""

    def __init__(self, user_id: str, tools: List[Tool]):
        self.user_id = user_id
        self.tools = self._wrap_tools_with_user_context(tools)
        self.agent = create_agent(tools=self.tools)

    def _wrap_tools_with_user_context(self, tools):
        """Inject user_id into all tool calls"""
        wrapped_tools = []
        for tool in tools:
            wrapped_tool = self._wrap_tool(tool, self.user_id)
            wrapped_tools.append(wrapped_tool)
        return wrapped_tools

    def _wrap_tool(self, tool, user_id):
        """Wrap tool to inject user_id parameter"""
        original_func = tool.func

        def wrapped_func(*args, **kwargs):
            # Inject user_id as first parameter
            return original_func(user_id, *args, **kwargs)

        tool.func = wrapped_func
        return tool
```

**Enforcement Example:**

```python
# All Stellar tools accept user_id as FIRST parameter
def stellar_get_balance(user_id: str, account_address: str) -> Dict:
    """Get balance for account (with permission check)"""

    # 1. Verify user owns this account
    portfolio_mgr = PortfolioManager()
    if not portfolio_mgr.user_owns_account(user_id, account_address):
        return {
            "error": f"Permission denied: account {account_address} not owned by user",
            "success": False
        }

    # 2. Proceed with operation
    adapter = StellarAdapter()
    account = adapter.get_account(account_address)
    return {"balance": account.balance, "success": True}
```

### Layer 3: Database-Backed Agent State (Recommended)

**Design:** Store agent state, memory, and outputs in the database instead of filesystem.

```python
# New table for agent execution state
cursor.execute('''
    CREATE TABLE IF NOT EXISTS agent_executions (
        id TEXT PRIMARY KEY,
        user_id TEXT NOT NULL,
        agent_type TEXT NOT NULL,
        input_message TEXT,
        output_response TEXT,
        tool_calls JSON,
        memory_state JSON,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
    )
''')

# Agent state manager
class AgentStateManager:
    """Store agent state in database instead of filesystem"""

    def save_agent_state(self, user_id: str, execution_id: str, state: Dict):
        """Save agent execution state"""
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO agent_executions
                (id, user_id, agent_type, memory_state)
                VALUES (?, ?, ?, ?)
            ''', (execution_id, user_id, 'chat', json.dumps(state)))

    def load_agent_state(self, user_id: str, execution_id: str) -> Dict:
        """Load agent state with permission check"""
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT memory_state FROM agent_executions
                WHERE id = ? AND user_id = ?
            ''', (execution_id, user_id))
            row = cursor.fetchone()

            if not row:
                raise PermissionError("Execution not found or not owned by user")

            return json.loads(row[0])
```

**Benefits:**
- User isolation enforced by SQL foreign keys
- Automatic cascade delete when user is deleted
- Easy to audit and backup
- No filesystem permission issues

### Layer 4: User-Specific Directories (If Filesystem Needed)

**When filesystem is necessary** (e.g., large files, tool outputs), use isolated directories:

```python
class FileSystemManager:
    """Manages user-isolated filesystem access"""

    def __init__(self, base_path: str = "/data/tuxedo"):
        self.base_path = Path(base_path)
        self.base_path.mkdir(exist_ok=True, mode=0o700)

    def get_user_directory(self, user_id: str) -> Path:
        """Get user's isolated directory"""
        user_dir = self.base_path / user_id
        user_dir.mkdir(exist_ok=True, mode=0o700)  # rwx------
        return user_dir

    def write_file(self, user_id: str, filename: str, content: str):
        """Write file to user's directory"""
        user_dir = self.get_user_directory(user_id)
        file_path = user_dir / filename

        # Prevent directory traversal
        if not file_path.resolve().is_relative_to(user_dir):
            raise ValueError("Invalid filename: directory traversal detected")

        file_path.write_text(content)
        file_path.chmod(0o600)  # rw-------

    def read_file(self, user_id: str, filename: str) -> str:
        """Read file from user's directory"""
        user_dir = self.get_user_directory(user_id)
        file_path = user_dir / filename

        # Prevent directory traversal
        if not file_path.resolve().is_relative_to(user_dir):
            raise ValueError("Invalid filename: directory traversal detected")

        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {filename}")

        return file_path.read_text()
```

**Directory Structure:**
```
/data/tuxedo/
├── user_abc123/          (mode: 0700 - rwx------)
│   ├── research_reports/ (agent-generated docs)
│   ├── tool_outputs/     (temporary tool results)
│   └── agent_memory/     (conversation context)
├── user_def456/
│   ├── research_reports/
│   └── ...
```

**Key protections:**
- Each user gets isolated directory
- Directory permissions `0700` (owner read/write/execute only)
- Path validation prevents directory traversal attacks
- Files created with `0600` (owner read/write only)

### Layer 5: TEE Deployment (Production/Mainnet)

**For production deployment with real capital,** use Trusted Execution Environments:

```
┌─────────────────────────────────────────┐
│  Host OS (Untrusted)                    │
│                                         │
│  ┌───────────────────────────────────┐ │
│  │ TEE Enclave - User ABC123         │ │
│  │ ─────────────────────────────────  │ │
│  │ - Agent process (isolated)        │ │
│  │ - Keys in encrypted memory        │ │
│  │ - Cannot access other TEEs        │ │
│  │ - Attestation-verified            │ │
│  └───────────────────────────────────┘ │
│                                         │
│  ┌───────────────────────────────────┐ │
│  │ TEE Enclave - User DEF456         │ │
│  │ ─────────────────────────────────  │ │
│  │ - Separate isolated process       │ │
│  │ - No shared memory                │ │
│  │ - Hardware-level isolation        │ │
│  └───────────────────────────────────┘ │
└─────────────────────────────────────────┘
```

**TEE Benefits:**
- Hardware-level isolation between users
- Keys never leave encrypted memory
- Attestation proves code integrity
- Industry standard for custody (mentioned in Choir whitepaper)

**TEE Options:**
- Intel SGX
- AMD SEV
- AWS Nitro Enclaves
- Azure Confidential Computing

---

## Implementation Roadmap

### Phase 1: Quantum Leap Migration (Immediate)

**Priority:** Complete user isolation in one atomic change

**Status:**
✅ **Layer 1: Database storage for keys** - COMPLETE (AccountManager implemented)
🚀 **Layer 2: User context enforcement** - IN PROGRESS (quantum leap migration)
📋 **Layer 3: Database-backed agent state** - OPTIONAL for MVP
⏳ **Layer 4: Filesystem isolation** - DEFERRED (only if filesystem storage needed)

**Quantum Leap Implementation:**
1. Delete `KeyManager` and `.stellar_keystore.json` (no valuable data)
2. Update all tool signatures: `user_id` as mandatory second parameter
3. Agent tool registration: inject `user_id` via lambda wrapper
4. Permission checks built into `AccountManager` methods
5. Test cross-user isolation

**Timeline:** 4-6 hours (see `AGENT_MIGRATION_QUANTUM_LEAP.md`)

### Phase 2: Pre-Mainnet (Before Real Capital)

**Priority:** Add filesystem isolation for safety

✅ **User-specific directories** with permission enforcement
✅ **Path validation** to prevent directory traversal
✅ **Audit logging** for all file operations
✅ **Rate limiting** on file writes

### Phase 3: Mainnet/Production

**Priority:** Hardware-level isolation

✅ **TEE deployment** for agent execution
✅ **Per-user TEE instances** for complete isolation
✅ **Attestation** to verify code integrity
✅ **Key management** within TEE secure memory

---

## Security Checklist

### Development Phase
- [ ] All tools accept `user_id` as first parameter
- [ ] Permission checks in every tool function
- [ ] Private keys stored in database (encrypted)
- [ ] Keys decrypted in-memory only
- [ ] No keys written to filesystem
- [ ] Agent state stored in database
- [ ] SQL foreign keys enforce user isolation

### Pre-Production
- [ ] User-specific directories implemented
- [ ] Path validation prevents directory traversal
- [ ] File permissions set to owner-only
- [ ] Audit logging for all file operations
- [ ] Integration tests verify isolation
- [ ] Penetration testing completed

### Production
- [ ] TEE deployment configured
- [ ] Per-user TEE instances running
- [ ] Attestation mechanism active
- [ ] Zero keys on filesystem
- [ ] Regular security audits
- [ ] Incident response plan

---

## Testing Strategy

### Unit Tests

```python
def test_user_cannot_access_other_user_accounts():
    """Test that user A cannot access user B's accounts"""
    portfolio_mgr = PortfolioManager()

    # User A creates account
    user_a = "user_a_id"
    portfolio_a = portfolio_mgr.create_portfolio(user_a, "Portfolio A")
    account_a = portfolio_mgr.generate_account(
        user_a,
        portfolio_a['portfolio_id'],
        "stellar"
    )

    # User B tries to access User A's account
    user_b = "user_b_id"
    with pytest.raises(PermissionError):
        portfolio_mgr.export_account(user_b, account_a['account_id'])

def test_filesystem_directory_traversal_prevention():
    """Test that directory traversal is blocked"""
    fs_mgr = FileSystemManager()
    user_id = "user_test"

    # Try to escape user directory
    with pytest.raises(ValueError, match="directory traversal"):
        fs_mgr.write_file(user_id, "../../../etc/passwd", "malicious")

    with pytest.raises(ValueError, match="directory traversal"):
        fs_mgr.read_file(user_id, "../../other_user/secrets.txt")

def test_agent_context_isolation():
    """Test that agent cannot access tools without user_id"""
    # Agent for user A
    agent_a = UserAgentExecutor("user_a", tools=[stellar_get_balance])

    # User B's account
    user_b_account = "GBXXXXXXXXXXXXXXX"

    # Agent A trying to access User B's account should fail
    result = agent_a.run(f"What is the balance of {user_b_account}?")
    assert "Permission denied" in result
```

### Integration Tests

```python
def test_full_isolation_scenario():
    """End-to-end test of user isolation"""

    # User A session
    user_a = create_test_user("user_a@test.com")
    portfolio_a = create_portfolio(user_a['id'])
    account_a = generate_account(user_a['id'], portfolio_a['id'], "stellar")

    # User B session
    user_b = create_test_user("user_b@test.com")
    portfolio_b = create_portfolio(user_b['id'])

    # User B cannot see User A's accounts
    accounts = get_portfolio_accounts(user_b['id'], portfolio_a['id'])
    assert len(accounts) == 0 or accounts[0].get('error')

    # User B cannot export User A's account
    export_result = export_account(user_b['id'], account_a['account_id'])
    assert not export_result.get('success')
    assert 'Permission denied' in export_result.get('error', '')

    # User A can access their own account
    export_result = export_account(user_a['id'], account_a['account_id'])
    assert export_result.get('success')
```

---

## Best Practices

### 1. Principle of Least Privilege
- Agents get minimum permissions needed
- Read-only access by default
- Write access only when necessary
- Scope permissions to specific resources

### 2. Defense in Depth
- Multiple layers of security
- Database isolation + API checks + context enforcement
- Fail securely (deny by default)

### 3. Audit Everything
- Log all account accesses
- Log permission denials
- Monitor for suspicious patterns
- Alert on unauthorized access attempts

### 4. Zero Trust
- Never trust user_id from client
- Always verify via session token
- Re-verify permissions on every operation
- No caching of permission decisions

---

## Comparison: Database vs Filesystem Storage

| Aspect | Database Storage | Filesystem Storage |
|--------|-----------------|-------------------|
| **Isolation** | SQL foreign keys (strong) | OS permissions (medium) |
| **Encryption** | Column-level encryption | File encryption required |
| **Audit** | Built-in query logs | Requires custom logging |
| **Backup** | Standard DB backup | Need file backup strategy |
| **Recovery** | Transaction rollback | Manual file recovery |
| **Performance** | Good for small data | Better for large files |
| **Complexity** | Lower (one system) | Higher (DB + FS) |

**Recommendation:** Use **database storage** for all sensitive data unless file size requires filesystem.

---

## Future: Multi-Region Deployment

When scaling to multiple regions:

```
Region US-East
├── Database: user_data_us_east
├── Users: user_abc123 (US-based)
└── TEE Enclaves: US data residency

Region EU-West
├── Database: user_data_eu_west
├── Users: user_def456 (EU-based)
└── TEE Enclaves: GDPR compliance
```

- Regional data residency
- Separate databases per region
- TEE attestation per region
- Cross-region access forbidden

---

## Conclusion

**Short Answer:** We keep user X's agent isolated from user Y's data through:

1. **No keys on filesystem** - All in encrypted database ✅ COMPLETE
2. **User context enforcement** - Every tool call verified 🚀 QUANTUM LEAP IN PROGRESS
3. **Database-backed state** - Isolation via SQL foreign keys (optional for MVP)
4. **Filesystem isolation** (if needed) - User-specific directories with permission validation (deferred)
5. **TEE deployment** (production) - Hardware-level isolation (future)

**Current Phase:** Quantum leap migration (Layers 1-2 implemented atomically)

**Approach:** Complete replacement of `KeyManager` with `AccountManager`, no gradual migration

**Rationale:** No valuable data exists (testnet only), clean break enables simpler architecture

**Next Phase:** Add agent execution tracking (Layer 3) and filesystem isolation (Layer 4) only if needed

**Production Phase:** Deploy TEE for complete isolation (Layer 5)

**See Also:** `AGENT_MIGRATION_QUANTUM_LEAP.md` for detailed implementation guide

This layered approach provides security appropriate for each deployment phase while maintaining a clear upgrade path to production-grade isolation.

---

**Related Documents:**
- `AGENT_ACCOUNT_SECURITY_PLAN.md` - Overall security architecture
- `CHOIR_WHITEPAPER.md` - TEE deployment vision
- `PASSKEY_ARCHITECTURE_V2.md` - User authentication

**Status:** Design Document
**Created:** 2025-11-08
**Next Action:** Implement Layers 1-3 for testnet deployment
