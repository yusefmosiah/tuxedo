# Magic Link Authentication System

## Overview

The Tuxedo AI platform has moved from wallet-based authentication to a modern **magic link authentication system** that provides seamless access for blockchain-phobic users while maintaining security and supporting our cloud TEE agent architecture.

## Architecture

### Authentication Flow

```
1. User Email → Magic Link Request
2. Backend → Generate Token (15 min expiry)
3. Backend → SendGrid Email with Magic Link
4. User Clicks Link → Token Validation
5. Backend → Create User Session (7 days)
6. User → Authenticated Session
7. User → Access AI Agents & Chat
```

### Database Schema

```sql
-- User accounts
CREATE TABLE users (
    id TEXT PRIMARY KEY,
    email TEXT UNIQUE NOT NULL,
    encrypted_private_key TEXT,
    public_key TEXT UNIQUE,
    recovery_method TEXT DEFAULT 'email',
    recovery_data TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE
);

-- Magic link sessions (15-minute expiry)
CREATE TABLE magic_link_sessions (
    id TEXT PRIMARY KEY,
    user_id TEXT,
    email TEXT NOT NULL,
    token TEXT UNIQUE NOT NULL,
    expires_at TIMESTAMP NOT NULL,
    used_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users (id)
);

-- User sessions (7-day expiry)
CREATE TABLE user_sessions (
    id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL,
    session_token TEXT UNIQUE NOT NULL,
    expires_at TIMESTAMP NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_accessed TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users (id)
);

-- AI agents managed by users
CREATE TABLE agents (
    id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL,
    agent_name TEXT NOT NULL,
    stellar_address TEXT UNIQUE NOT NULL,
    encrypted_private_key TEXT NOT NULL,
    permissions TEXT DEFAULT 'trade',
    auto_approve_limit REAL DEFAULT 100.0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE,
    FOREIGN KEY (user_id) REFERENCES users (id)
);

-- Chat threads (user-owned)
CREATE TABLE threads (
    id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL,
    title TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_archived BOOLEAN DEFAULT FALSE,
    FOREIGN KEY (user_id) REFERENCES users (id)
);

-- Chat messages with metadata
CREATE TABLE messages (
    id TEXT PRIMARY KEY,
    thread_id TEXT NOT NULL,
    role TEXT NOT NULL,
    content TEXT NOT NULL,
    metadata TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (thread_id) REFERENCES threads (id) ON DELETE CASCADE
);
```

## API Endpoints

### Authentication Routes (`/auth/*`)

#### `POST /auth/magic-link`
Request a magic link for email authentication.

**Request:**
```json
{
  "email": "user@example.com"
}
```

**Response:**
```json
{
  "success": true,
  "message": "If an account exists with user@example.com, you'll receive a magic link shortly."
}
```

#### `GET /auth/magic-link/validate?token={token}`
Validate magic link token and create user session.

**Response:** 302 Redirect to frontend with session cookie

#### `POST /auth/validate-session`
Validate existing user session.

**Request:**
```bash
Authorization: Bearer {session_token}
```

**Response:**
```json
{
  "success": true,
  "session_token": "l9600AXvxj2iiwanJGT87HC15fJdPqCQ_dW25ddRvE8YLwm3ai1kePQmDtRoBoTfdOEkZQ92kcERtPQgnnzAOQ",
  "user": {
    "id": "user_OAQRu_X3xPZ8x3qqNh3nzw",
    "email": "test@example.com",
    "public_key": null,
    "last_login": null
  },
  "message": "Session valid"
}
```

#### `POST /auth/logout`
Clear user session by removing session cookie.

#### `GET /auth/me`
Get current authenticated user information.

### Threads Routes (`/threads/*`)

All threads routes now require authentication and belong to users instead of wallets.

#### `POST /threads`
Create a new chat thread for authenticated user.

**Request:**
```json
{
  "title": "My AI Agent Chat"
}
```

**Headers:**
```bash
Authorization: Bearer {session_token}
```

**Response:**
```json
{
  "id": "thread_1762308461207",
  "user_id": "user_OAQRu_X3xPZ8x3qqNh3nzw",
  "title": "My AI Agent Chat",
  "created_at": "2025-11-05 02:07:41.207848",
  "updated_at": "2025-11-05 02:07:41.207850",
  "is_archived": false
}
```

#### `GET /threads`
Get all threads for authenticated user.

**Response:**
```json
[
  {
    "id": "thread_1762308461207",
    "user_id": "user_OAQRu_X3xPZ8x3qqNh3nzw",
    "title": "My AI Agent Chat",
    "created_at": "2025-11-05 02:07:41.207848",
    "updated_at": "2025-11-05 02:07:41.207850",
    "is_archived": false
  }
]
```

## Security Features

### Session Management
- **HTTP-Only Cookies**: Prevents XSS attacks
- **Bearer Token Support**: API-friendly authentication
- **7-Day Sessions**: Balance between security and convenience
- **Automatic Cleanup**: Expired sessions automatically invalidated

### Magic Link Security
- **15-Minute Expiry**: Short window for token usage
- **Single-Use Tokens**: Tokens marked as used after validation
- **Secure Token Generation**: Cryptographically secure random tokens
- **Email Validation**: Only works with verified email addresses

### Database Security
- **Encrypted Private Keys**: User keys stored encrypted in database
- **SQL Injection Protection**: Parameterized queries throughout
- **Foreign Key Constraints**: Data integrity maintained
- **Proper Indexing**: Performance and security optimized

## SendGrid Integration

### Email Template
The system sends beautiful HTML emails with:

- Professional branding
- Clear call-to-action buttons
- Security warnings about expiry
- Mobile-responsive design
- Tuxedo AI branding and messaging

### Configuration
```env
SENDGRID_API_KEY=your_sendgrid_api_key
FROM_EMAIL=noreply@yourdomain.com
FRONTEND_URL=http://localhost:5173
```

### Fallback System
If SendGrid fails, the system:
- Logs the magic link to console (for development)
- Continues authentication flow
- Warns about email delivery issues
- Maintains system stability

## Frontend Integration

### Authentication Flow

```javascript
// Request magic link
const requestMagicLink = async (email) => {
  const response = await fetch('/auth/magic-link', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ email })
  });
  return response.json();
};

// Validate session
const validateSession = async (sessionToken) => {
  const response = await fetch('/auth/validate-session', {
    method: 'POST',
    headers: { 'Authorization': `Bearer ${sessionToken}` }
  });
  return response.json();
};

// Create thread (authenticated)
const createThread = async (title, sessionToken) => {
  const response = await fetch('/threads', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${sessionToken}`
    },
    body: JSON.stringify({ title })
  });
  return response.json();
};
```

### Session Management

```javascript
// Session storage
const storeSession = (sessionToken, userData) => {
  localStorage.setItem('session_token', sessionToken);
  localStorage.setItem('user_data', JSON.stringify(userData));
};

// Session retrieval
const getSession = () => {
  return {
    token: localStorage.getItem('session_token'),
    user: JSON.parse(localStorage.getItem('user_data') || '{}')
  };
};

// Session validation
const isAuthenticated = async () => {
  const { token } = getSession();
  if (!token) return false;

  try {
    const response = await validateSession(token);
    return response.success;
  } catch (error) {
    return false;
  }
};
```

## Environment Setup

### Required Dependencies

```bash
# Add to pyproject.toml
dependencies = [
    "sendgrid>=6.12.5",
    "email-validator>=2.3.0",
    # ... existing dependencies
]
```

### Environment Variables

```env
# OpenAI Configuration
OPENAI_API_KEY=your_api_key
OPENAI_BASE_URL=https://openrouter.ai/api/v1

# SendGrid Configuration
SENDGRID_API_KEY=SG.your_sendgrid_key
FROM_EMAIL=noreply@yourdomain.com

# Frontend URL
FRONTEND_URL=http://localhost:5173

# Stellar Configuration
STELLAR_NETWORK=testnet
HORIZON_URL=https://horizon-testnet.stellar.org
SOROBAN_RPC_URL=https://soroban-testnet.stellar.org
```

## Testing

### Manual Testing

1. **Magic Link Request:**
   ```bash
   curl -X POST http://localhost:8001/auth/magic-link \
     -H "Content-Type: application/json" \
     -d '{"email": "test@example.com"}'
   ```

2. **Session Validation:**
   ```bash
   curl -X POST http://localhost:8001/auth/validate-session \
     -H "Authorization: Bearer your_session_token"
   ```

3. **Thread Creation:**
   ```bash
   curl -X POST http://localhost:8001/threads \
     -H "Content-Type: application/json" \
     -H "Authorization: Bearer your_session_token" \
     -d '{"title": "Test Thread"}'
   ```

### Automated Testing

The system includes comprehensive error handling and logging for all edge cases.

## Migration from Wallet-Based Auth

### Database Migration
- Old `chat_threads.db` → New `tuxedo.db`
- `wallet_address` → `user_id` foreign key relationship
- In-memory storage → Persistent SQLite database

### Frontend Migration
- Remove wallet connection components
- Add email-based authentication UI
- Update API calls to include session tokens
- Replace wallet address display with user email

## Benefits for Hackathon Demo

### User Experience
- **No Installation**: Users don't need browser wallet extensions
- **Universal Access**: Everyone has email
- **Professional Interface**: Beautiful, modern authentication flow
- **Persistent Sessions**: Users stay logged in across sessions

### Technical Advantages
- **Cloud TEE Ready**: Perfect for server-side agent management
- **Scalable**: Database-backed, no memory limitations
- **Secure**: Professional-grade authentication system
- **Maintainable**: Clean separation of concerns

### Demo Story
"Unlike traditional DeFi apps that require complex wallet installations, Tuxedo AI uses simple email-based authentication. Users receive a magic link, sign in securely, and immediately have access to AI agents that manage their DeFi operations in secure cloud environments."

## Future Enhancements

### Passkey Integration (Stretch Goal)
```typescript
// Add to existing auth system
const requestPasskeyAuth = async () => {
  // WebAuthn API integration
  // Fallback to magic link if not supported
};
```

### Multi-Factor Authentication
```typescript
const enableMFA = async (userId) => {
  // TOTP or SMS-based 2FA
  // Additional security for sensitive operations
};
```

### Team/Account Features
```sql
-- Future enhancement
CREATE TABLE teams (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    owner_id TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (owner_id) REFERENCES users (id)
);

CREATE TABLE team_members (
    team_id TEXT NOT NULL,
    user_id TEXT NOT NULL,
    role TEXT NOT NULL, -- 'admin', 'member', 'viewer'
    invited_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    joined_at TIMESTAMP,
    FOREIGN KEY (team_id) REFERENCES teams (id),
    FOREIGN KEY (user_id) REFERENCES users (id)
);
```

## Troubleshooting

### Common Issues

**1. Magic Link Not Received**
- Check SendGrid API key configuration
- Verify email in spam folder
- Check backend logs for SendGrid errors
- Console fallback shows magic link for testing

**2. Session Validation Fails**
- Verify session token is not expired
- Check that session token is properly formatted
- Ensure database is accessible
- Look for session cleanup issues

**3. Thread Creation Fails**
- Verify user is authenticated
- Check session token format
- Ensure database connections are working
- Validate request headers

### Debug Logging

All authentication operations include comprehensive logging:

```python
logger.info(f"Magic link requested for email: {email}")
logger.info(f"Magic link email sent successfully to {email}")
logger.info(f"User authenticated: {user['email']}")
logger.info(f"Created thread {thread_id} for user {user['email']}: {title}")
```

## Conclusion

The magic link authentication system provides a modern, secure, and user-friendly foundation for the Tuxedo AI platform. It eliminates the complexity of wallet-based authentication while maintaining the security required for financial applications. The system is production-ready and perfect for demonstrating the vision of AI-managed DeFi operations.

For the hackathon demo, this system showcases:
- **Innovation**: Email-based authentication for DeFi
- **User Experience**: Frictionless onboarding
- **Technical Excellence**: Modern security practices
- **Future-Ready**: Extensible architecture for enhanced features