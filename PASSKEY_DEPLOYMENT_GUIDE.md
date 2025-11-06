# Passkey Authentication Deployment Guide

## 🚀 Quick Start

### 1. Setup Environment
```bash
# Backend environment (.env)
TUXEDO_SERVER_SECRET=your_32_byte_server_secret_here

# Frontend environment (.env.local)
VITE_API_URL=http://localhost:8000
```

### 2. Run Database Migration
```bash
cd backend
source .venv/bin/activate
python migrate_to_passkeys.py
```

### 3. Start Services
```bash
# Terminal 1: Backend
cd backend && source .venv/bin/activate && python main.py

# Terminal 2: Frontend
npm run dev
```

### 4. Access Application
- **URL**: http://localhost:5173
- **Registration**: Email + Passkey creation
- **Login**: Biometric authentication
- **Recovery**: Use backup codes if needed

## 📋 Configuration Checklist

### Production Setup
- [ ] Set `TUXEDO_SERVER_SECRET` to 32-byte cryptographically secure value
- [ ] Update `RP_ID` to your domain (backend/api/routes/passkey.py:50)
- [ ] Update `RP_ORIGIN` to HTTPS URL (backend/api/routes/passkey.py:52)
- [ ] Enable HTTPS on frontend
- [ ] Test biometric authentication on target devices

### Security Verification
- [ ] Test passkey registration and login
- [ ] Verify recovery code generation and validation
- [ ] Test cross-browser compatibility
- [ ] Verify session expiration works
- [ ] Test database constraints and cascades

## 🔍 Testing Commands

```bash
# Test passkey components
python -c "
import api.routes.passkey
from crypto.key_derivation import KeyDerivation
from auth.recovery import RecoveryCodeService
print('✅ Passkey modules ready')
"

# Test database schema
python -c "import database; db = database.DatabaseManager(); print('✅ Database ready')"

# Build frontend
npm run build
```

## 📱 Browser Compatibility

| Browser | Version | Status |
|---------|---------|--------|
| Chrome | 108+ | ✅ Full Support |
| Firefox | 114+ | ✅ Full Support |
| Safari | 14+ | ✅ Full Support |
| Edge | 108+ | ✅ Full Support |

## 🔧 Troubleshooting

### Common Issues
- **"Passkeys not supported"**: Use recovery code or update browser
- **"Invalid credential"**: Clear browser storage and retry
- **"Database error"**: Run migration script again
- **"Key derivation failed"**: Check TUXEDO_SERVER_SECRET is set

### Debug Mode
```bash
# Backend debugging
export DEBUG=1
python main.py

# Frontend debugging
localStorage.setItem('debug', 'true')
```

## 📞 Support

See `PASSKEY_IMPLEMENTATION_COMPLETE.md` for detailed documentation.