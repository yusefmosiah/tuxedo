# Passkey Authentication Setup Guide

This guide covers the setup and configuration of the new passkey-based authentication system for Tuxedo AI.

## Overview

Tuxedo AI now uses **WebAuthn passkey authentication** instead of magic links. This provides:
- ✅ Passwordless authentication with biometrics (Face ID, Touch ID, Windows Hello)
- ✅ Hardware security key support
- ✅ 8 single-use recovery codes for backup access
- ✅ Email recovery for lost passkeys
- ✅ Session management with sliding expiration (24h idle, 7d absolute)
- ✅ Multi-device support (multiple passkeys per user)

## Backend Setup

### 1. Install Dependencies

From the `backend` directory:

```bash
cd backend
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
uv sync  # Or: pip install -r requirements.txt
```

Key new dependency:
- `webauthn>=2.0.0` - WebAuthn library for Python

### 2. Configure Environment Variables

Update `backend/.env`:

```bash
# Required
OPENAI_API_KEY=your_openai_api_key

# SendGrid (for recovery emails)
SENDGRID_API_KEY=your_sendgrid_api_key
SENDGRID_FROM_EMAIL=no-reply@choir.chat
SENDGRID_FROM_NAME=Choir

# WebAuthn Configuration
RP_ID=localhost                     # Change to your domain in production (e.g., "choir.chat")
RP_NAME=Choir                       # Your app name
EXPECTED_ORIGIN=http://localhost:5173  # Frontend URL

# Frontend URL (for email links)
FRONTEND_URL=http://localhost:5173

# Stellar Configuration (existing)
STELLAR_NETWORK=testnet
HORIZON_URL=https://horizon-testnet.stellar.org
SOROBAN_RPC_URL=https://soroban-testnet.stellar.org
```

### 3. Initialize New Database

The new passkey authentication uses a completely new database schema. **No migration needed** - just start fresh:

```bash
# Remove old database (if exists)
rm tuxedo.db

# Start backend (database will be created automatically)
python main.py
```

The new database includes these tables:
- `users` - User accounts with email
- `passkey_credentials` - WebAuthn credentials
- `passkey_challenges` - Short-lived authentication challenges
- `passkey_sessions` - Active user sessions
- `recovery_codes` - Backup recovery codes (SHA-256 hashed)
- `email_recovery_tokens` - Email recovery tokens
- `recovery_attempts` - Rate limiting for recovery codes
- `threads` and `messages` - Chat functionality (preserved)
- `agents` - Multi-agent support (future feature)

### 4. Start Backend Server

```bash
cd backend
source .venv/bin/activate
python main.py
```

Backend will run on `http://localhost:8000`

## Frontend Setup

### 1. Install Dependencies

From the project root:

```bash
npm install
```

### 2. Configure Environment Variables

Update `.env.local`:

```bash
VITE_API_URL=http://localhost:8000
```

### 3. Start Frontend

```bash
npm run dev
```

Frontend will run on `http://localhost:5173`

## Testing the Flow

### Registration Flow

1. Navigate to `http://localhost:5173`
2. Click "Sign Up" tab
3. Enter your email address
4. Click "Create Account"
5. Your browser will prompt you to create a passkey (use Face ID, Touch ID, Windows Hello, or security key)
6. **Save your 8 recovery codes** - copy them to a safe place
7. Click "I've Saved My Recovery Codes"
8. You're now authenticated and redirected to `/chat`

### Sign In Flow

1. Navigate to login page
2. Stay on "Sign In" tab
3. Enter your email address
4. Click "Sign In with Passkey"
5. Your browser will prompt you to authenticate with your passkey
6. You're authenticated and redirected to `/chat`

### Recovery Code Flow

1. Navigate to login page
2. Click "Lost access? Use recovery code"
3. Enter your email and one of your 8 recovery codes
4. Click "Sign In with Recovery Code"
5. You're authenticated
6. Check your email for a security alert

**Note**: Each recovery code can only be used once. Rate limit: 5 failed attempts per hour.

## Email Configuration (SendGrid)

Passkey authentication sends 5 types of emails:

1. **Welcome Email** - Sent after registration with recovery codes
2. **Recovery Code Used Alert** - Security notification when recovery code is used
3. **Email Recovery Link** - For lost passkeys + recovery codes
4. **Account Recovered Confirmation** - Sent after successful account recovery
5. **New Passkey Added** - Security alert when new passkey is registered

### SendGrid Setup

1. Create a SendGrid account at https://sendgrid.com
2. Create an API key with "Mail Send" permissions
3. Verify your sender email address
4. Add to `backend/.env`:

```bash
SENDGRID_API_KEY=SG.xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
SENDGRID_FROM_EMAIL=no-reply@yourdomain.com
SENDGRID_FROM_NAME=Your App Name
```

**Development Mode**: If SendGrid is not configured, emails will be logged to console instead.

## Production Deployment

### Environment-Specific Configuration

**Development**:
```bash
CORS_ORIGINS=http://localhost:5173
RP_ID=localhost
EXPECTED_ORIGIN=http://localhost:5173
SESSION_SECURE_COOKIE=false
LOG_LEVEL=DEBUG
```

**Production**:
```bash
CORS_ORIGINS=https://yourdomain.com
RP_ID=yourdomain.com
EXPECTED_ORIGIN=https://yourdomain.com
SESSION_SECURE_COOKIE=true
LOG_LEVEL=WARN
RATE_LIMIT_ENABLED=true
IP_TRACKING_ENABLED=true
```

### SSL/HTTPS Requirements

WebAuthn requires HTTPS in production (except for `localhost`). Ensure:
- Your domain has a valid SSL certificate
- `EXPECTED_ORIGIN` uses `https://`
- `RP_ID` matches your domain exactly

### Database Backup

Before deploying:

```bash
# Backup database
cp tuxedo.db tuxedo.db.backup.$(date +%Y%m%d_%H%M%S)
```

### Deploy Checklist

- [ ] Update all environment variables for production
- [ ] Configure SendGrid with production email
- [ ] Set up SSL certificate
- [ ] Test passkey registration on production domain
- [ ] Test passkey authentication
- [ ] Test recovery code flow
- [ ] Verify all emails are being sent
- [ ] Set up monitoring and alerts

## API Documentation

### Registration

**POST** `/auth/passkey/register/start`
- Request: `{ email: string }`
- Response: `{ challenge_id, options }`

**POST** `/auth/passkey/register/verify`
- Request: `{ email, challenge_id, credential, friendly_name? }`
- Response: `{ user, session_token, recovery_codes, must_acknowledge }`

### Authentication

**POST** `/auth/passkey/login/start`
- Request: `{ email: string }`
- Response: `{ challenge_id, options }`

**POST** `/auth/passkey/login/verify`
- Request: `{ challenge_id, credential }`
- Response: `{ user, session_token }`

### Recovery Code

**POST** `/auth/passkey/recovery/verify`
- Request: `{ email, code }`
- Response: `{ user, session_token, remaining_codes }`

### Session Management

**POST** `/auth/validate-passkey-session`
- Headers: `Authorization: Bearer <token>`
- Response: `{ user, valid }`

**POST** `/auth/logout`
- Headers: `Authorization: Bearer <token>`
- Response: `{ success }`

## Security Features

### Session Management
- **Sliding expiration**: 24 hours of inactivity
- **Absolute timeout**: 7 days maximum
- **Automatic cleanup**: Expired sessions removed

### Recovery Codes
- **8 codes** per user
- **SHA-256 hashed** in database
- **Single-use only**
- **Rate limited**: 5 failed attempts per hour

### Rate Limiting
- **Recovery attempts**: 5 failures → 1 hour lockout
- **IP tracking**: Optional for forensics
- **Security alerts**: Email notifications

### Email Recovery
- **1-hour expiration** on recovery links
- **Invalidates all passkeys** when used (security measure)
- **New recovery codes** generated
- **Confirmation email** sent

## Browser Support

Passkeys are supported in:
- ✅ Chrome 67+ (desktop), Chrome 108+ (mobile)
- ✅ Edge 18+
- ✅ Safari 13+ (macOS 10.15+), Safari 14+ (iOS 14+)
- ✅ Firefox 60+ (with some limitations)

**Note**: Users on unsupported browsers will see an error message.

## Troubleshooting

### "Passkeys are not supported"
- Update to a modern browser
- Ensure you're using HTTPS in production (localhost is OK for dev)

### Passkey creation fails
- Check browser console for errors
- Verify `RP_ID` matches your domain
- Ensure `EXPECTED_ORIGIN` is correct

### Emails not sending
- Check SendGrid API key is valid
- Verify sender email is verified in SendGrid
- Check backend logs for SendGrid errors

### Session expires immediately
- Check system clock is synchronized
- Verify session token is being stored in localStorage
- Check `SESSION_SECURE_COOKIE` settings

### Database errors
- Delete `tuxedo.db` and restart (creates fresh database)
- Check file permissions on database file

## Migration from Magic Links

If you have existing users with magic link authentication:

1. **No automatic migration** - This is a fresh start
2. **Users must re-register** with their email
3. **Old sessions are invalid** - Users will be logged out
4. **Communication**: Notify users about the change

## Monitoring

### Metrics to Track
- Registration success/failure rates
- Login success/failure rates
- Recovery code usage patterns
- Session duration averages
- Email delivery rates

### Alerts to Configure
- Rate limit triggers > 10/5min (potential attack)
- SendGrid delivery failure > 5%
- Database connection failures
- Session validation errors > 10/min

## Support

For issues or questions:
1. Check browser console for errors
2. Check backend logs: `tail -f backend/logs/app.log`
3. Review this documentation
4. File an issue on GitHub

---

**Last Updated**: 2025-11-06
**Version**: 1.0.0
**Status**: Production Ready for Testnet
