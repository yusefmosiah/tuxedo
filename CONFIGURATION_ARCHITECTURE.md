# Configuration Architecture

## Overview

Tuxedo now uses a **three-tier configuration system** that separates secrets, application config, and network definitions. This architecture supports multiple networks (testnet/mainnet) and multiple chains (Stellar, and future expansion).

## The Problem We Solved

**Before**: Everything in `.env` files - secrets mixed with non-secret config like network URLs, port numbers, and contract addresses. This made it:
- Hard to manage multi-network deployments
- Confusing what needs to be secret vs. what's just config
- Difficult to add new networks or chains
- Risky (non-secrets in .env encourage putting .env in gitignore, losing config documentation)

**After**: Clear separation of concerns with appropriate storage for each type of data.

## Architecture Layers

```
┌─────────────────────────────────────────────────────┐
│ Layer 1: Code Defaults                              │
│ Location: backend/config/*.py                       │
│ Purpose: Application defaults, framework settings   │
│ Version Control: ✅ YES                             │
│ Examples: Default ports, model names, timeouts      │
├─────────────────────────────────────────────────────┤
│ Layer 2: Network Configs (JSON)                     │
│ Location: backend/config/networks/*.json            │
│ Purpose: Network-specific settings, contracts       │
│ Version Control: ✅ YES                             │
│ Examples: RPC URLs, contract addresses, passphrases │
├─────────────────────────────────────────────────────┤
│ Layer 3: Secrets (Environment Variables)            │
│ Location: .env (runtime only)                       │
│ Purpose: API keys, encryption keys, passwords       │
│ Version Control: ❌ NO (only .env.example)          │
│ Examples: OPENAI_API_KEY, ENCRYPTION_MASTER_KEY     │
└─────────────────────────────────────────────────────┘
```

## Directory Structure

```
backend/
  config/
    __init__.py
    settings.py              # LEGACY - kept for backward compatibility
    settings_v2.py          # NEW unified settings system
    secrets.py              # Secrets from .env only
    application.py          # App config (models, ports, features)
    networks.py             # Network registry and loader
    networks/
      stellar_mainnet.json  # Stellar mainnet configuration
      stellar_testnet.json  # Stellar testnet configuration
      # Future additions:
      # base_mainnet.json
      # arbitrum_mainnet.json
      # ...
  .env                      # SECRETS ONLY (not in git)
  .env.minimal.example      # NEW minimal secrets template
  .env.example             # LEGACY template (will be deprecated)
```

## What Goes Where?

### ✅ Layer 1: Code Defaults (`application.py`)

**Non-secret application settings with sensible defaults**

```python
# Examples:
- Server: port, host, debug mode, log level
- AI: model names, base URLs (without API keys)
- Features: feature flags, limits, timeouts
- CORS: allowed origins
- Paths: keystore location, log directories
```

**Why in code?**
- These are operational settings, not secrets
- Developers need to see them to understand the system
- Can be overridden by environment variables if needed
- Version controlled for team collaboration

### ✅ Layer 2: Network Configs (`networks/*.json`)

**Network-specific configurations that vary by chain/network**

```json
{
  "network_id": "stellar-mainnet",
  "horizon_url": "https://horizon.stellar.org",
  "contracts": {
    "blend": {
      "backstop": "CAQQR5S...",
      "poolFactory": "CDSYOAV..."
    }
  }
}
```

**What belongs here:**
- RPC URLs (public endpoints)
- Horizon URLs
- Network passphrases (these are public constants)
- Contract addresses
- Token metadata
- Explorer URLs
- Feature availability per network

**Why in JSON files?**
- Easy to add new networks without code changes
- Can be version controlled (these aren't secrets)
- Self-documenting for developers
- Can be loaded dynamically
- Future: Could be stored in admin database

### ❌ Layer 3: Secrets (`.env` - runtime only)

**Only actual secrets that must never be in git**

```bash
# API Keys
OPENAI_API_KEY=sk_...
ANKR_STELLER_RPC=https://...your-key-here

# Encryption
ENCRYPTION_MASTER_KEY=...

# Database
DATABASE_PASSWORD=...
```

**What belongs here:**
- API keys (OpenAI, OpenRouter, Ankr, etc.)
- Encryption keys
- Database passwords
- Private keys
- OAuth secrets
- Webhook signing secrets

**Why in .env?**
- Must never be committed to git
- Different per deployment environment
- Injected at runtime
- Can be managed by deployment platform (Render, Phala, etc.)

## Usage Examples

### Basic Usage (New System)

```python
from config.settings_v2 import settings, get_network

# Access secrets
api_key = settings.secrets.openai_api_key
encryption_key = settings.secrets.encryption_master_key

# Access app config
port = settings.app.port
model = settings.app.primary_model
cors_origins = settings.app.cors_origins

# Get network configuration
mainnet = get_network("stellar-mainnet")
rpc_url = mainnet.get_rpc_url()  # Checks env var first, then public URL
horizon = mainnet.horizon_url

# Get contract addresses
backstop_address = mainnet.get_contract_address("blend", "backstop")
usdc_token = mainnet.get_contract_address("blend", "usdcToken")

# Check network features
can_use_friendbot = mainnet.supports_feature("friendbot")  # False on mainnet
can_create_accounts = mainnet.supports_feature("account_creation")
```

### Multi-Network Support

```python
from config.settings_v2 import settings, list_networks

# List all available networks
networks = list_networks()
# Returns: ["stellar-mainnet", "stellar-testnet"]

# Iterate over Stellar networks
stellar_networks = settings.networks.get_by_chain("stellar")
for network in stellar_networks:
    print(f"{network.name}: {network.horizon_url}")
```

### Environment-Specific RPC URLs

In your network JSON, use `rpc_url_env_key` to reference an env var:

```json
{
  "network_id": "stellar-mainnet",
  "rpc_url_env_key": "ANKR_STELLER_RPC",
  "rpc_url_public": null,
  ...
}
```

Then in `.env`:
```bash
ANKR_STELLER_RPC=https://rpc.ankr.com/stellar/YOUR_SECRET_KEY
```

The system will check the env var first, fall back to public URL if available.

### Backward Compatibility

The old `settings.py` still works:

```python
from config.settings import settings

# Old way still works
api_key = settings.openai_api_key
port = settings.port
network_config = settings.get_network_config("mainnet")
```

## Migration Guide

### For Development

1. **Create minimal `.env`** with only secrets:
   ```bash
   cd backend
   cp .env.minimal.example .env
   # Edit .env and add your API keys
   ```

2. **Update imports** (gradually):
   ```python
   # Old
   from config.settings import settings

   # New
   from config.settings_v2 import settings, get_network
   ```

3. **Use network registry** for network-specific config:
   ```python
   # Old
   horizon_url = settings.testnet_horizon_url

   # New
   testnet = get_network("stellar-testnet")
   horizon_url = testnet.horizon_url
   ```

### For Production (Phala/Docker)

1. **Minimal `.env` file**:
   ```bash
   # Only secrets
   OPENAI_API_KEY=your_key
   ENCRYPTION_MASTER_KEY=your_key
   ANKR_STELLER_RPC=your_ankr_url
   ```

2. **Runtime config via env vars** (optional):
   ```bash
   DEFAULT_NETWORK=stellar-mainnet
   PORT=8000
   DEBUG=false
   ```

3. **Network configs** are in code (version controlled):
   - No need to pass network configs as env vars
   - Just deploy the code with `backend/config/networks/*.json`

## Adding New Networks

### Example: Adding Base Mainnet

1. **Create config file**: `backend/config/networks/base_mainnet.json`
   ```json
   {
     "network_id": "base-mainnet",
     "chain": "base",
     "name": "Base Mainnet",
     "description": "Base L2 mainnet",
     "enabled": true,
     "rpc_url_public": "https://mainnet.base.org",
     "rpc_url_env_key": "BASE_RPC_URL",
     "contracts": {
       "uniswap": {
         "factory": "0x...",
         "router": "0x..."
       }
     },
     "features": {
       "dex_trading": true
     }
   }
   ```

2. **That's it!** The network registry auto-loads all JSON files.

3. **Use it in code**:
   ```python
   base = get_network("base-mainnet")
   factory = base.get_contract_address("uniswap", "factory")
   ```

## Future: Admin UI

### Phase 1: View Configs
- Web dashboard showing all networks
- Contract address viewer
- Feature flag display

### Phase 2: Edit Configs
- UI to enable/disable networks
- Update contract addresses (with validation)
- Manage feature flags

### Phase 3: Database Storage
- Move from JSON files to database
- API for config management
- Audit log for config changes
- Version control for configs

### Phase 4: Multi-Tenant
- Per-user network preferences
- Custom RPC endpoints per user
- User-specific feature flags

## Best Practices

### ✅ DO

- Put secrets in `.env` only
- Put network configs in JSON files
- Put app defaults in `application.py`
- Use `rpc_url_env_key` for authenticated RPC endpoints
- Version control network JSON files
- Document what each network supports in `features`

### ❌ DON'T

- Don't put API keys in JSON files
- Don't put network configs in `.env` (unless overriding for testing)
- Don't hardcode contract addresses in business logic
- Don't commit `.env` files to git
- Don't mix secrets and non-secrets

## Security Considerations

### Secrets in .env
- ✅ Never committed to git
- ✅ Different per environment
- ✅ Managed by deployment platform
- ✅ Can be rotated without code changes

### Network Configs in JSON
- ✅ Can be version controlled (no secrets)
- ✅ Reviewed in PRs
- ✅ Easy to audit
- ⚠️ If network config becomes user-specific, move to database

### RPC URL Strategy
- **Public RPCs**: Put directly in JSON (`rpc_url_public`)
- **Authenticated RPCs**: Reference env var (`rpc_url_env_key`)
- System tries env var first, falls back to public

## Deployment Checklist

### Development
- [ ] Create `.env` from `.env.minimal.example`
- [ ] Add `OPENAI_API_KEY`
- [ ] Add `ENCRYPTION_MASTER_KEY`
- [ ] Set `DEFAULT_NETWORK=stellar-testnet` (optional)

### Staging
- [ ] Set secrets in platform (Render, Phala, etc.)
- [ ] Set `DEFAULT_NETWORK=stellar-testnet`
- [ ] Set `DEBUG=false`
- [ ] Configure CORS origins

### Production
- [ ] Set all required secrets
- [ ] Set `DEFAULT_NETWORK=stellar-mainnet`
- [ ] Set `DEBUG=false`
- [ ] Add production CORS origins
- [ ] Add authenticated RPC endpoint (`ANKR_STELLER_RPC`)
- [ ] Test network config loading

## Troubleshooting

### "Network not found" error
```python
# Check available networks
from config.settings_v2 import list_networks
print(list_networks())
```

### "RPC URL not configured" error
- Check if `ANKR_STELLER_RPC` is set in `.env`
- Or add `rpc_url_public` to network JSON

### Secrets not loading
```python
from config.settings_v2 import settings
missing = settings.secrets.validate_required()
if missing:
    print(f"Missing secrets: {missing}")
```

### Old code breaks after migration
- Use `settings_v2.py` for new code
- Keep `settings.py` for backward compatibility
- Gradually migrate imports

## Summary

**The Rule of Thumb:**

1. **Is it a secret?** → `.env` file
2. **Does it vary by network?** → `networks/*.json`
3. **Is it an app default?** → `application.py`

This architecture scales from single-network testnet deployments to multi-chain production systems with user-specific configurations.
