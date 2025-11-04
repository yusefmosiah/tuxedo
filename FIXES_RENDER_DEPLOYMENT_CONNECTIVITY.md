# Fix: Docker/Render Deployment Connectivity Issues

## Problem Summary

The deployed frontend at `https://tuxedo-frontend.onrender.com` was unable to connect to the backend at `https://tuxedo-backend.onrender.com`, causing "Backend offline" errors in the UI.

## Root Cause Analysis

### Issues Identified

1. **Incorrect API URL Configuration**: Frontend was using Docker-internal service names (`http://backend:8000`) instead of the actual Render URLs
2. **Build-Time vs Runtime Environment Variables**: Vite build process requires environment variables at build time, not runtime
3. **Documentation Port Inconsistencies**: Mixed references to ports 8000, 8001, and 8002 across the codebase

## Solutions Implemented

### 1. Frontend API Configuration Update

**File**: `src/lib/api.ts`

**Before**:
```typescript
const API_BASE_URL = import.meta.env.VITE_API_URL || import.meta.env.PUBLIC_API_URL || 'http://localhost:8000';
```

**After**:
```typescript
const API_BASE_URL = import.meta.env.VITE_API_URL ||
                     import.meta.env.PUBLIC_API_URL ||
                     (import.meta.env.DEV ? 'http://localhost:8000' : 'https://tuxedo-backend.onrender.com');
```

**Changes**:
- Added environment-specific URL detection
- Dev mode: Uses `http://localhost:8000` for local development
- Production: Uses `https://tuxedo-backend.onrender.com` for Render deployment
- Maintains backward compatibility with existing environment variables

### 2. Environment Variables Configuration

**Removed**: `.env.frontend` and `.env.backend` files (should not be committed)

**Platform Environment Variables**:
- Frontend uses `VITE_API_URL=https://tuxedo-backend.onrender.com` from Render dashboard
- Backend uses environment variables configured in Render dashboard
- No local .env files are copied to Docker containers

### 3. Docker Configuration Fixes

**File**: `docker-compose.yaml`

**Before**:
```yaml
environment:
  - VITE_API_URL=http://backend:8000
```

**After**:
```yaml
environment:
  - VITE_API_URL=https://tuxedo-backend.onrender.com
```

**File**: `Dockerfile.frontend`

**Removed**:
```dockerfile
# Copy environment file for build-time variables
COPY .env.frontend .env.production
```

**Replaced with**:
```dockerfile
# Copy source code (excluding .env files via .dockerignore)
COPY . .

# Build the application (skip TypeScript checking)
# Environment variables are provided by the platform (Render/Docker)
RUN npx vite build --mode production
```

### 4. Documentation Port References Fixed

**Files Updated**:
- `README.md`: Updated port references from 8002 to 8000
- `backend/tests/test_agent.py`: Updated API URL from port 8002 to 8000
- `backend/tests/test_chat/test_multiturn.py`: Updated API URL from port 8002 to 8000
- `backend/tests/test_chat/test_multiturn_with_tools.py`: Updated API URL from port 8002 to 8000
- `backend/tests/test_agent_management/test_wallet_fix.py`: Updated API URL from port 8002 to 8000

## Current Architecture

### Development Environment
- **Frontend**: `http://localhost:5173` (Vite dev server)
- **Backend**: `http://localhost:8000` (FastAPI)
- **Connection**: Frontend connects to `http://localhost:8000`

### Production Environment (Render)
- **Frontend**: `https://tuxedo-frontend.onrender.com`
- **Backend**: `https://tuxedo-backend.onrender.com`
- **Connection**: Frontend connects to `https://tuxedo-backend.onrender.com`

### Docker Environment
- **Frontend**: Container on port 8080
- **Backend**: Container on port 8000
- **Connection**: Frontend configured to connect to Render URL for external deployment

## Deployment Instructions

### For Render Deployment

1. **Backend**: Deploy with existing configuration
2. **Frontend**: Ensure `VITE_API_URL=https://tuxedo-backend.onrender.com` is set in Render environment variables
3. **Build**: The build process will use the correct API URL

### For Local Development

```bash
# Backend
cd backend && source .venv/bin/activate && python main.py

# Frontend (in separate terminal)
npm run dev
```

### For Docker Deployment

```bash
# Build and run (requires docker-compose)
docker-compose up --build
```

## Migration Path for Future Platforms

When migrating from Render to Phala or other platforms:

1. **Update Environment Variables**:
   - Set `VITE_API_URL` to the new backend URL
   - Update `.env.frontend` file
   - Update `docker-compose.yaml` if using Docker

2. **Frontend Code**: No changes required - uses environment variables

3. **Backend Code**: No changes required - platform-agnostic

## Verification Steps

1. **Local Development**:
   - Start both services
   - Navigate to `http://localhost:5173`
   - Verify "Backend online" status

2. **Production Deployment**:
   - Deploy to Render with updated environment variables
   - Navigate to `https://tuxedo-frontend.onrender.com`
   - Verify "Backend online" status
   - Test chat functionality

3. **Docker Testing**:
   - Run `docker-compose up`
   - Test container communication
   - Verify health checks pass

## Files Modified

- `src/lib/api.ts` - Updated API URL resolution logic
- `.env.frontend` - Updated Render backend URL
- `.env.backend` - Created with backend configuration
- `docker-compose.yaml` - Updated frontend environment variables
- `Dockerfile.frontend` - Added environment file copying
- `README.md` - Fixed port documentation
- Multiple test files - Updated port references from 8002 to 8000

## Summary

This fix ensures the frontend correctly connects to the backend in all deployment environments by:
1. Using proper environment-specific URLs
2. Maintaining build-time environment variable injection
3. Providing clear documentation and consistent configuration
4. Enabling easy migration to future platforms like Phala

The deployment should now work correctly on Render with the frontend successfully connecting to the backend service.