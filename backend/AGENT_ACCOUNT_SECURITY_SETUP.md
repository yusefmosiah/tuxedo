# Agent Account Security Setup Guide

This guide walks through setting up the secure agent account system with user isolation and encryption.

## Prerequisites

1. Python 3.11+ installed
2. Virtual environment activated
3. All dependencies installed via `uv sync`

## Step 1: Install Dependencies

The `cryptography` package has been added to `pyproject.toml`. Install it:

```bash
cd backend
uv sync
```

## Step 2: Generate Encryption Keys

Generate a secure encryption master key:

```bash
source .venv/bin/activate
python -c 'from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())'
```

Copy the output (it should look like: `1lPCmBCobCmqTotKhxx_4qNT79GFFy75EIzx8Ozfy4o=`)

## Step 3: Configure Environment Variables

Create a `.env` file in the `backend` directory (copy from `.env.example`):

```bash
cp .env.example .env
```

Edit `.env` and add the generated key:

```bash
# Agent Account Encryption
ENCRYPTION_MASTER_KEY=YOUR_GENERATED_KEY_HERE
ENCRYPTION_SALT=tuxedo-agent-accounts-v1
```

**IMPORTANT**: 
- Never commit the `.env` file to version control
- Store the master key securely (use a secrets manager in production)
- Changing the master key will make existing encrypted accounts inaccessible

## Step 4: Migrate Existing Accounts (Optional)

If you have existing accounts in `.stellar_keystore.json`, migrate them:

```bash
python migrate_keymanager_to_database.py
```

This will:
1. Back up your existing keystore to `.stellar_keystore.json.backup`
2. Create a migration user (`migration@tuxedo.local`)
3. Encrypt and migrate all accounts to the database

## Step 5: Test the Implementation

1. Start the backend server:
```bash
python main.py
```

2. Test account creation (requires authentication):
```bash
# You'll need a valid session token
curl -X POST http://localhost:8000/api/agent/create-account \
  -H "Authorization: Bearer YOUR_SESSION_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"name": "Test Account"}'
```

3. List accounts (requires authentication):
```bash
curl -X GET http://localhost:8000/api/agent/accounts \
  -H "Authorization: Bearer YOUR_SESSION_TOKEN"
```

## Security Features Implemented

✅ **User Isolation**: Database-enforced foreign key constraint linking accounts to users
✅ **Encryption at Rest**: Private keys encrypted with user-specific derived keys
✅ **Access Control**: Permission checks on every account operation
✅ **Audit Trail**: Created_at, last_used_at timestamps tracked
✅ **CASCADE DELETE**: Deleting a user automatically deletes their agent accounts

## Database Schema

The new `agent_accounts` table:

```sql
CREATE TABLE agent_accounts (
    id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL,
    stellar_public_key TEXT UNIQUE NOT NULL,
    stellar_secret_key_encrypted TEXT NOT NULL,
    name TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_used_at TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
)
```

## API Changes

All agent account endpoints now require authentication:

- `POST /api/agent/create-account` - Create account for authenticated user
- `GET /api/agent/accounts` - List accounts for authenticated user
- `GET /api/agent/accounts/{address}` - Get account info (permission check)
- `DELETE /api/agent/accounts/{address}` - Delete account (permission check)

## Troubleshooting

### Error: "ENCRYPTION_MASTER_KEY not set in environment"

Make sure you've created a `.env` file with the encryption key.

### Error: "Invalid or expired session"

The authentication token is missing or invalid. Make sure you're logged in via passkey auth.

### Migration fails

Check that:
1. The virtual environment is activated
2. The `.stellar_keystore.json` file exists
3. The `ENCRYPTION_MASTER_KEY` is set in `.env`

## Production Considerations

Before deploying to production:

1. Use a secure secrets manager (AWS Secrets Manager, HashiCorp Vault, etc.)
2. Rotate encryption keys regularly
3. Set up monitoring for failed permission checks
4. Enable audit logging for all account operations
5. Back up the database regularly
6. Consider using hardware security modules (HSM) for key storage

## Files Modified/Created

**Created:**
- `backend/encryption.py` - Encryption utilities
- `backend/agent_account_manager.py` - Secure account manager
- `backend/api/dependencies.py` - Auth dependencies
- `backend/migrate_keymanager_to_database.py` - Migration script
- `backend/.env.example` - Environment template

**Modified:**
- `backend/database_passkeys.py` - Added agent_accounts table and methods
- `backend/api/routes/agent.py` - Added authentication requirements
- `backend/tools/agent/account_management.py` - Updated to use new manager
- `backend/pyproject.toml` - Added cryptography dependency

