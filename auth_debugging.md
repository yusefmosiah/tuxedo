# Authentication Debugging Issues

## Magic Link Authentication Issues

### 1. CORS Policy Error

**Issue**: Magic link validation fails due to CORS policy when backend redirects to frontend

```
Access to fetch at 'http://localhost:5173/auth/success?token=...' from origin 'http://localhost:5173' has been blocked by CORS policy: No 'Access-Control-Allow-Origin' header is present on the requested resource.
```

**Flow**:

1. User clicks magic link → `/auth/magic-link?token=...`
2. Frontend validates with backend → `http://localhost:8000/auth/magic-link/validate?token=...`
3. Backend redirects to → `http://localhost:5173/auth/success?token=...`
4. CORS error blocks the redirect

**Root Cause**: Backend is redirecting to a frontend URL that doesn't exist, causing CORS issues

### 2. Missing Route Error

**Issue**: Backend redirects to `/auth/success` route that doesn't exist in React Router

```
react-router-dom.js?v=88f18348:553 No routes matched location "/auth/magic-link?token=..."
```

**Current Implementation Problems**:

- Frontend has `/auth/magic-link` route but backend redirects to `/auth/success`
- CORS blocking prevents proper validation flow
- User gets stuck on "Validating your magic link..." screen

### 3. Backend Validation Error

**Issue**: Backend returns 400 Bad Request when validating magic link

```
:8000/auth/magic-link/validate?token=...:1 Failed to load resource: the server responded with a status of 400 (Bad Request)
```

**Possible Causes**:

- Token expiration
- Invalid token format
- Backend validation logic issues

## Dashboard/Blend Pool Issues (Unrelated to Auth)

### 1. Soroban RPC Connection Error

**Issue**: Cannot connect to insecure Soroban RPC server

```
Error: Cannot connect to insecure Soroban RPC server if `allowHttp` isn't set
```

**Affected Components**:

- Backstop pool discovery
- Pool metadata loading
- Blend SDK connections

## TypeScript Build Errors (GitHub Workflow)

### 1. Missing Required Props

```typescript
// src/contexts/AuthContext.tsx#L136
'email' is declared but its value is never read.

// src/components/Login.tsx#L161
Type '{ children: string; type: "submit"; variant: "primary"; size: "md"; isLoading: boolean; disabled: boolean; fullWidth: true; }' is not assignable to type 'IntrinsicAttributes & Props'.

// src/components/Login.tsx#L144
Type '{ type: "email"; label: string; placeholder: string; value: string; onChange: (e: ChangeEvent<HTMLInputElement>) => void; disabled: boolean; required: true; }' is missing the following properties from type 'Props': id, fieldSize
```

### 2. Missing Attributes

```typescript
// src/App.tsx#L111
Property 'as' is missing in type '{ children: string; size: "sm"; style: { margin: number; }; }' but required in type 'TProps'.

// src/App.tsx#L69, #L50
Add missing 'type' attribute on 'button' component
```

### 3. Unsafe Type Handling

```typescript
// src/App.tsx#L165, #L164, #L162, #L161
Unsafe member access on `any` values
Unsafe assignment of `any` value
Unsafe argument of type `any` assigned to parameter of type 'string'
```

### 4. Promise Handling

```typescript
// src/App.tsx#L145, #L16
Promises must be awaited, end with a call to .catch, end with a call to .then with a rejection handler or be explicitly marked as ignored with the `void` operator
```

## Recommended Solutions

### Magic Link Flow Fix

1. **Backend Configuration**: Configure backend to redirect to correct frontend URL
2. **Add /auth/success Route**: Create frontend route to handle successful magic link validation
3. **CORS Configuration**: Ensure proper CORS headers are set
4. **Error Handling**: Add proper error handling for failed validation attempts

### TypeScript Build Fixes

1. **Add missing required props** to Stellar Design System components
2. **Add proper type attributes** to button elements
3. **Implement proper type safety** for API responses
4. **Add proper promise handling** with try/catch or await

### Environment Configuration

1. **Set allowHttp: true** for Soroban RPC connections in development
2. **Configure proper environment variables** for frontend/backend URLs
3. **Add development-specific CORS settings**

## Current Status (Updated 2025-11-05 - LATEST)

- ✅ Authentication UI components implemented
- ✅ Magic link request flow working
- ✅ Frontend routing structure in place
- ✅ TypeScript build errors resolved
- ✅ Soroban RPC connection configured for development
- 🔧 **Magic link validation flow being debugged - Single-use token issue identified**
- 🔧 **Frontend redirect handling improved - Manual redirect processing added**
- 🆕 **New magic link available for testing**

## Latest Issues (November 5, 2025)

### 1. CORS Policy Blocking Backend Redirect

**Issue**: Backend redirect from `/auth/magic-link/validate` to `/auth/success` blocked by CORS

```
Access to fetch at 'http://localhost:5173/auth/success?token=...' from origin 'http://localhost:5173' has been blocked by CORS policy: No 'Access-Control-Allow-Origin' header is present on the requested resource.
```

**Flow**:

1. Frontend calls: `GET /auth/magic-link/validate?token=magic_token`
2. Backend responds: 400 Bad Request OR redirect to `/auth/success?token=session_token`
3. CORS blocks the redirect, causing frontend validation to fail

### 2. Backend 400 Bad Request on Magic Link Validation

**Issue**: Magic link tokens become invalid or expire immediately

```
Failed to load resource: the server responded with a status of 400 (Bad Request)
```

**Possible Causes**:

- Magic link tokens expiring too quickly
- Backend validation logic rejecting valid tokens
- Database session cleanup happening too aggressively

### 3. Frontend Error Handling Loop

**Issue**: When magic link validation fails, frontend still redirects to chat but without authentication

- User ends up on "sign in with your email" page again
- Creates infinite authentication loop
- Session data not persisted properly

## Debug Logs Analysis

**Frontend Console Logs**:

```
🔗 Magic link validation: Object { hasToken: true, tokenPreview: "zVIGeluqsnLtjPuA...", url: "http://localhost:5173/auth/magic-link?token=zVIGeluqsnLtjPuA..." }
📡 Validating magic link token with backend...
📡 Magic link validation response: Object { status: 400, ok: false, redirected: false }
❌ Magic link validation failed: 400
➡️ Redirecting to chat...
❌ Error validating magic link: TypeError: Failed to fetch
```

**Backend Logs Analysis**:

```
INFO:api.routes.auth:Received magic link validation request with token: zVIGeluqsnLtjPuA...
INFO:api.routes.auth:User authenticated: yusefnathanson@me.com
INFO:api.routes.auth:Received magic link validation request with token: zVIGeluqsnLtjPuA...
WARNING:api.routes.auth:Invalid or expired magic link token: zVIGeluq...
```

**Root Cause Confirmed**: Magic link tokens are **single-use only**. After successful validation, they're marked as "used" in the database and cannot be reused.

**Frontend Fix Applied**:

- Added logic to distinguish between `/auth/magic-link` (magic token) and `/auth/success` (session token) routes
- Added `redirect: 'manual'` to prevent automatic redirect following
- Added redirect URL parsing to extract session tokens from backend redirects
- Enhanced error handling and debugging logs

**Latest Magic Link for Testing**:
`http://localhost:5173/auth/magic-link?token=_u6gzkEnZEkZOu04Oe49SRx6JPWm2BuZA5kr_u1mZYQ`
