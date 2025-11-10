# 🎯 Security Action Plan - Reconciled with Requirements

## ✅ **Acknowledged Requirements**

1. **Master key already exists** in staging (Render) environment ✅
2. **Remove master key creation branch** - eliminate fallback entirely
3. **Per-user salt is a great improvement** - high priority
4. **Database security is good enough for now** - defer until scaling
5. **Focus on API security** - CORS, rate limiting, request validation
6. **Manage configuration of non-secrets** - network URLs, etc.
7. **Transaction safety and simulation** - important for agentic transactions
8. **Fix tools sync/async distinction** - critical for tool factory

## 🚨 **Immediate Actions (This Week)**

### **1. Remove Master Key Fallback**

```python
# backend/encryption.py - REMOVE this entire branch:
if not self.master_key:
    logger.warning("Generating temporary key for development")
    self.master_key = Fernet.generate_key().decode()

# REPLACE with:
if not self.master_key:
    raise CriticalSecurityError(
        "ENCRYPTION_MASTER_KEY environment variable is required. "
        "This fallback has been removed for security."
    )
```

### **2. Implement Per-User Salt**

```python
# backend/encryption.py - ADD per-user salt generation:
def _derive_salt(self, user_id: str) -> bytes:
    server_salt_secret = os.getenv('SERVER_SALT_SECRET')
    if not server_salt_secret:
        raise CriticalSecurityError("SERVER_SALT_SECRET environment variable required")

    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        salt=(server_salt_secret + user_id).encode(),
        iterations=1,
    )
    return kdf.derive(b'salt-generation')
```

### **3. Fix CORS Configuration**

```python
# backend/app.py - REPLACE hardcoded origins:
def get_cors_origins():
    env = os.getenv("ENVIRONMENT", "development")

    if env == "production":
        return ["https://tuxedo.phala.network", "https://app.tuxedo.ai"] # fake urls
    elif env == "staging":
        return ["https://tuxedo-staging.onrender.com"] #fake url
    else:
        return ["http://localhost:5173", "http://localhost:8000"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=get_cors_origins(),
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],  # NOT ["*"]
    allow_headers=["Content-Type", "Authorization"],  # NOT ["*"]
)
```

## 🛠️ **Priority Implementation Order**

### **Week 1: Critical Security (Ready to Implement)**

- [x] **Master key exists** - ✅ Already in staging
- [ ] **Remove master key fallback** - Delete the branch entirely
- [ ] **Add per-user salt** - Implement SERVER_SALT_SECRET env var
- [ ] **Add CriticalSecurityError** - New exception class

### **Week 2: API Security (Research Complete)**

- [ ] **CORS hardening** - Environment-specific origins
- [ ] **Rate limiting** - Use slowapi library for agentic endpoints
- [ ] **Request validation** - Stellar address/amount validation
- [ ] **Security headers** - XSS protection, etc.

### **Week 3: Configuration Management**

- [ ] **Centralized network config** - Move hardcoded URLs
- [ ] **Non-secret configuration** - Contract addresses, vault addresses
- [ ] **Environment-specific** - Dev/staging/prod configs

### **Week 4: Tool Standardization (CRITICAL)**

- [ ] **Fix sync/async issue** - All tools must be async
- [ ] **Standardized tool interface** - BaseTool abstract class
- [ ] **Enhanced tool factory** - Integration with new interface
- [ ] **Migrate critical tools** - Start with account management

## 🔧 **Specific Implementation Details**

### **Rate Limiting Research Findings**

Based on research, use **slowapi** library:

```bash
pip install slowapi
```

```python
# Rate limits by endpoint and user type:
@limiter.limit("20/hour")  # Agentic transactions - very strict
async def execute_agent_transaction():
    pass

@limiter.limit("100/hour")  # Chat endpoints
async def chat_completion():
    pass
```

### **Request Validation Implementation**

```python
# Use Pydantic for Stellar-specific validation:
class StellarAddress(str):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if not re.match(r'^G[0-9A-Z]{55}$', v):
            raise ValueError('Invalid Stellar address')
        return v

class AmountValidator(str):
    @classmethod
    def validate(cls, v):
        try:
            amount = float(v)
            if amount <= 0 or amount > 1000000:
                raise ValueError('Invalid amount range')
            return v
        except ValueError:
            raise ValueError('Invalid amount format')
```

### **Tool Standardization Plan**

Current issue in `backend/agent/core.py:300-328`:

```python
# CURRENT - Complex tool execution patterns:
if hasattr(tool_func, 'ainvoke'):
    result = await tool_func.ainvoke(tool_args)
elif hasattr(tool_func, 'invoke'):
    result = tool_func.invoke(tool_args)
# ... 6 different execution patterns

# NEW - Standardized interface:
class BaseTool(ABC):
    @abstractmethod
    async def execute(self, **kwargs) -> ToolResult:
        pass

    async def safe_execute(self, **kwargs) -> ToolResult:
        # Built-in error handling, validation, timing
        try:
            return await self.execute(**kwargs)
        except Exception as e:
            return ToolResult.error(str(e))
```

## 🎯 **Environment Variables to Add**

```bash
# Critical for Phala deployment:
ENCRYPTION_MASTER_KEY=already-exists-in-staging ✅
SERVER_SALT_SECRET=new-required-variable
ENVIRONMENT=development|staging|production

# For rate limiting:
REDIS_URL=redis://localhost:6379

# For CORS:
FRONTEND_URL=https://tuxedo.phala.network  # Production
```

## 📊 **Impact Assessment**

| Change                     | Risk   | Impact   | Effort   | Timeline |
| -------------------------- | ------ | -------- | -------- | -------- |
| Remove master key fallback | Low    | Critical | 1 hour   | Week 1   |
| Per-user salt              | Low    | High     | 4 hours  | Week 1   |
| CORS hardening             | Low    | Medium   | 2 hours  | Week 2   |
| Rate limiting              | Low    | High     | 6 hours  | Week 2   |
| Tool standardization       | Medium | Critical | 20 hours | Week 4   |

## 🚀 **Ready-to-Deploy Solutions**

I have created three implementation files:

1. **`security_improvements.md`** - Complete roadmap with your requirements
2. **`api_security_improvements.py`** - Production-ready security middleware
3. **`standardized_tools.py`** - Complete tool interface standardization

## 📋 **Immediate Next Steps**

1. **Review the security_improvements.md** - Confirm it matches your requirements
2. **Remove master key fallback** in `backend/encryption.py`
3. **Add SERVER_SALT_SECRET** to staging environment
4. **Test per-user salt implementation** in staging
5. **Implement CORS changes** in `backend/app.py`
6. **Start tool standardization** with critical tools first

## 🔍 **Validation Plan**

After each change:

1. **Test in staging** (Render) before production
2. **Verify encryption/decryption** still works with new salt
3. **Test CORS** with different environments
4. **Validate tool execution** with new interface
5. **Run existing test suite** to ensure no regressions

This plan addresses all your specific requirements while prioritizing Phala Network deployment readiness. The master key issue is resolved, per-user salt is prioritized, and tool standardization is given critical importance.
