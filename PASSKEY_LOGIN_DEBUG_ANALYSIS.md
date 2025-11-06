# Passkey Login Flow Debug Analysis

**Date**: 2025-11-06
**Issue**: "Failed to start login" error when attempting to sign in with passkey on iOS Safari
**Status**: ROOT CAUSE IDENTIFIED ✅

---

## Executive Summary

The passkey **login flow fails on iOS Safari** due to breaking the user gesture chain. While registration works correctly by pre-loading challenge options, **login does NOT pre-load** and attempts to fetch challenge options **after** the user click, causing iOS Safari to reject the WebAuthn API call with an empty Error object.

**Root Cause**: Missing challenge pre-loading for login flow (only implemented for signup)

**Solution**: Enable challenge pre-loading for BOTH signup AND login flows

---

## User-Reported Symptoms

From console logs:
```
🚀 API Request: GET /api/agent/accounts
✅ API Response: 200 /api/agent/accounts
🔄 Pre-loading challenge options for: yusefnathanson@me.com
🔐 Starting passkey authentication with API: https://tuxedo-backend.onrender.com
🌐 Current origin: https://tuxedo-frontend.onrender.com
Login failed: Error {  }
Authentication error: Object { name: "Error", message: "Failed to start login", stack: "@https://tuxedo-frontend.onrender.com/assets/index-CDwJ5Z2q.js:1475:201766", fullError: Error }
```

**Key Observations**:
1. Pre-loading IS happening (for accounts API)
2. Login starts correctly with proper API URL and origin
3. **Empty Error object** indicates iOS Safari silently rejecting WebAuthn call
4. Generic "Failed to start login" message from frontend error handling

---

## Technical Deep Dive

### iOS Safari User Gesture Requirements

From WebAuthn community research:

> **Safari's "Freebie" Limitation**: Safari typically allows websites a single "freebie" indirect execution of WebAuthn, and if there was any kind of asynchronicity before the call, Safari would fail the API call right away with an inscrutable error message.

> **User Gesture Requirement**: WebAuthn API must be called within user activated events (click, touchend, doubleclick, keydown). Any async operation breaks this chain.

**Impact**:
- ✅ `navigator.credentials.create()` - Works if called synchronously after user click
- ❌ `navigator.credentials.get()` - Fails if preceded by async `fetch()`

---

## Current Implementation Analysis

### Registration Flow (✅ WORKS)

**Location**: `src/components/Login.tsx:33-41`

```typescript
const {
  options: preloadedOptions,
  loading: preloadingChallenge,
  error: preloadError,
} = useChallengePreload(
  email,
  authMode === "signup" && isPasskeySupported, // ✅ Pre-loading enabled for signup
  500, // 500ms debounce
);
```

**Flow**:
1. User types email → `useChallengePreload` hook automatically fetches challenge
2. User clicks "Sign Up with Passkey" button
3. Challenge options already in memory
4. `navigator.credentials.create()` called **immediately** (within gesture)
5. ✅ **Success on iOS Safari!**

**Code**: `src/services/passkeyAuth.ts:56-205`
```typescript
async registerWithPreloadedOptions(
  email: string,
  preloadedOptions: { challenge_id: string; options: any },
): Promise<RegistrationResult> {
  // Step 1: Create credential SYNCHRONOUSLY - maintains user gesture
  credential = await navigator.credentials.create({
    publicKey: publicKeyOptions,
  });
  // Step 2: Verify with backend AFTER gesture is used (async is OK here)
  verifyResponse = await fetch(`${API_BASE_URL}/auth/passkey/register/verify`, ...);
}
```

---

### Login Flow (❌ FAILS)

**Location**: `src/components/Login.tsx:39`

```typescript
authMode === "signup" && isPasskeySupported, // ❌ ONLY signup, NOT signin!
```

**Flow**:
1. User types email → **NO pre-loading happens**
2. User clicks "Sign In with Passkey" button
3. Code makes async `fetch()` to `/auth/passkey/login/start`
4. **User gesture chain BROKEN by async operation**
5. Tries to call `navigator.credentials.get()`
6. ❌ **iOS Safari rejects with empty Error**

**Code**: `src/services/passkeyAuth.ts:422-583`
```typescript
async authenticate(email?: string): Promise<AuthResult> {
  // Step 1: Start authentication (ASYNC - breaks user gesture!)
  startResponse = await fetch(`${API_BASE_URL}/auth/passkey/login/start`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ email }),
  });

  // Step 2: Get credential using WebAuthn
  // ❌ TOO LATE - user gesture chain already broken!
  credential = await navigator.credentials.get({
    publicKey: publicKeyOptions,
  });
}
```

---

## Why Registration Works But Login Fails

| Aspect | Registration | Login | Why Different? |
|--------|-------------|-------|----------------|
| **Pre-loading** | ✅ Enabled | ❌ Disabled | Line 39 in Login.tsx only enables for signup |
| **Challenge fetch** | Before user click | After user click | useChallengePreload hook condition |
| **User gesture** | Preserved | Broken | Async fetch() breaks the chain |
| **iOS Safari** | ✅ Works | ❌ Fails | Strict gesture requirement enforced |
| **Method** | `registerWithPreloadedOptions()` | `authenticate()` | Different code paths |

---

## Git History Analysis

### Recent Commits Show Registration Fix:
```
c7a20e7 Merge pull request #17 - claude/debug-passkey-registration
14e1dcf fix: Resolve iOS Safari passkey registration by pre-loading challenge options
```

**What was fixed**: Registration flow on iOS Safari
**What was missed**: Login flow still uses old non-preloaded method

### Why Login Was Overlooked:

1. **Focus on registration bugs**: Multiple PRs focused on 409 errors and registration failures
2. **Different code paths**: Registration has TWO methods (`register()` and `registerWithPreloadedOptions()`), but login only has ONE (`authenticate()`)
3. **Testing gap**: Manual testing likely focused on registration after fix, not full login cycle
4. **Architecture decision**: Challenge pre-loading was added as iOS Safari workaround, not core architecture

---

## Architecture Comparison

### Current Architecture (Asymmetric)

```
Registration:
  User clicks → Use pre-loaded options → navigate.credentials.create() → Verify
  ✅ User gesture preserved

Login:
  User clicks → Fetch options → navigator.credentials.get() → Verify
  ❌ User gesture broken by fetch
```

### Proposed Architecture (Symmetric)

```
Registration:
  User clicks → Use pre-loaded options → navigator.credentials.create() → Verify
  ✅ User gesture preserved

Login:
  User clicks → Use pre-loaded options → navigator.credentials.get() → Verify
  ✅ User gesture preserved
```

---

## Solution Design

### Phase 1: Enable Pre-loading for Login ✅

**File**: `src/components/Login.tsx:39`

**Change**:
```typescript
// BEFORE (only signup)
authMode === "signup" && isPasskeySupported

// AFTER (both signup and signin)
(authMode === "signup" || authMode === "signin") && isPasskeySupported
```

**Impact**: Challenge options will be pre-loaded for login flow

---

### Phase 2: Add loginWithPreloadedOptions() Method ✅

**File**: `src/services/passkeyAuth.ts`

**New Method**:
```typescript
async loginWithPreloadedOptions(
  email: string,
  preloadedOptions: { challenge_id: string; options: any },
): Promise<AuthResult> {
  // Call navigator.credentials.get() IMMEDIATELY (within user gesture)
  // Then verify with backend
}
```

**Pattern**: Mirror `registerWithPreloadedOptions()` implementation

---

### Phase 3: Update Login Component ✅

**File**: `src/components/Login.tsx:88-96`

**Change**:
```typescript
} else {
  // Authenticate existing user
  if (preloadedOptions) {
    await loginWithPreloadedOptions(email, preloadedOptions);
  } else {
    await login(email); // Fallback
  }
}
```

**Behavior**: Use pre-loaded options if available, fallback to old method

---

### Phase 4: Update AuthContext ✅

**File**: `src/contexts/AuthContext_passkey.tsx`

**Add**:
```typescript
const loginWithPreloadedOptions = async (
  email: string,
  preloadedOptions: { challenge_id: string; options: any },
): Promise<void> => {
  const result = await passkeyAuthService.loginWithPreloadedOptions(email, preloadedOptions);
  setUser(result.user);
  setSessionToken(result.session_token);
};
```

**Export**: Add to AuthContextType interface and value object

---

## Implementation Checklist

### Code Changes
- [ ] Update `src/components/Login.tsx` - Enable pre-loading for signin
- [ ] Add `loginWithPreloadedOptions()` to `src/services/passkeyAuth.ts`
- [ ] Update `src/contexts/AuthContext_passkey.tsx` - Add new method
- [ ] Update Login.tsx to use preloaded options for signin

### Testing
- [ ] Test registration on iOS Safari (verify still works)
- [ ] Test login on iOS Safari (verify now works)
- [ ] Test on desktop Chrome (verify backward compatibility)
- [ ] Test with network delay (verify fallback works)
- [ ] Test with invalid email (verify error handling)
- [ ] Test when challenge expires (verify auto-refresh)

### Documentation
- [ ] Update PASSKEY_ARCHITECTURE_V2.md if needed
- [ ] Add comments explaining user gesture requirements
- [ ] Document fallback behavior

---

## Expected Outcomes

### Before Fix
```
User clicks "Sign In" →
  fetch /auth/passkey/login/start (async) →
  navigator.credentials.get() →
  ❌ Error: User gesture not detected (iOS Safari)
```

### After Fix
```
Challenge pre-loaded on email input →
User clicks "Sign In" →
  navigator.credentials.get() (sync, uses pre-loaded options) →
  fetch /auth/passkey/login/verify (async) →
  ✅ Success!
```

---

## Risk Assessment

### Low Risk Changes
- ✅ Enabling pre-loading for signin (one-line change)
- ✅ Adding loginWithPreloadedOptions() (mirrors existing pattern)
- ✅ Fallback to old method if pre-loading fails

### Potential Issues
- ⚠️ Extra API calls from pre-loading (mitigated by 500ms debounce)
- ⚠️ Challenge expiration (mitigated by auto-refresh in useChallengePreload)
- ⚠️ User switches between signin/signup modes (mitigated by mode check in hook)

### Mitigations
1. **Debouncing**: 500ms delay prevents excessive API calls while typing
2. **Auto-refresh**: Hook automatically refreshes expired challenges (15min lifetime)
3. **Fallback**: Old `authenticate()` method remains as backup
4. **Error handling**: Hook provides error state for UI feedback

---

## Backward Compatibility

### Desktop Browsers (Chrome, Firefox, Edge)
- ✅ Pre-loading works (no user gesture requirement)
- ✅ Fallback works if pre-loading fails
- ✅ No breaking changes

### iOS Safari
- ✅ Registration: Already working with pre-loading
- ✅ Login: Will now work with pre-loading
- ✅ Graceful degradation if pre-loading fails

### Android Chrome
- ✅ Pre-loading works
- ✅ No special user gesture requirements
- ✅ No breaking changes

---

## Lessons Learned

### What Went Well ✅
1. **Pattern already exists**: `registerWithPreloadedOptions()` provides proven solution
2. **Good architecture**: `useChallengePreload` hook is reusable
3. **Comprehensive error logging**: Made debugging much easier
4. **Documentation**: PASSKEY_ARCHITECTURE_V2.md provided excellent context

### What To Improve 🔧
1. **Symmetric design**: Both flows should work the same way from the start
2. **Test coverage**: Need iOS Safari in test matrix
3. **User gesture awareness**: Document this requirement prominently
4. **Code review**: Check ALL WebAuthn flows, not just the failing one

### Best Practices for Future 📚
1. **Always pre-load WebAuthn challenges** on user input (email, username)
2. **Never fetch challenge options after user click** (breaks gesture chain)
3. **Test on iOS Safari early** (strictest browser for WebAuthn)
4. **Document user gesture requirements** in code comments
5. **Provide fallback methods** for graceful degradation

---

## Related Documentation

- **Architecture**: `/home/user/tuxedo/PASSKEY_ARCHITECTURE_V2.md`
- **409 Error Analysis**: `/home/user/tuxedo/PASSKEY_409_ANALYSIS.md`
- **Challenge Pre-loading Hook**: `/home/user/tuxedo/src/hooks/useChallengePreload.ts`
- **WebAuthn Service**: `/home/user/tuxedo/src/services/passkeyAuth.ts`

---

## References

### WebAuthn User Gesture Requirements
- Apple WebKit: Requires direct user activation for navigator.credentials API
- Safari allows one "freebie" indirect call, then strictly enforces
- Empty Error object is Safari's way of rejecting without revealing info

### Similar Issues
- GitHub Issue #211 - MasterKale/SimpleWebAuthn: "No available authenticator"
- Stack Overflow: "Getting Type Error when using WebAuthn on iOS"
- Apple Forums: "WebAuthn re-authentication failure in iOS 15.5"

---

**Analysis Completed**: 2025-11-06
**Next Steps**: Implement Phase 1-4 of solution design
**Estimated Time**: 30-45 minutes implementation + testing
