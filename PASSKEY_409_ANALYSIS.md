# Passkey Registration 409 Error Analysis

## Executive Summary
The 409 (Conflict) error in passkey registration is triggered when attempting to register with an email that already has an active user account. However, there are several critical issues in the implementation that could cause database IntegrityErrors and unhandled race conditions.

---

## 1. EXACT CODE THAT RETURNS 409

### Location: `/home/user/tuxedo/backend/api/routes/passkey_auth.py` (Lines 224-235)

```python
@router.post("/auth/passkey/register/start", response_model=RegisterStartResponse)
async def register_start(req: Request, request: RegisterStartRequest):
    """Start passkey registration flow"""
    try:
        # Check if user already exists
        existing_user = db.get_user_by_email(request.email)
        if existing_user:
            create_error_response(
                "USER_EXISTS",
                "An account with this email already exists",
                status_code=409  # <-- 409 CONFLICT RETURNED HERE
            )
```

The error is created by the `create_error_response()` function (lines 205-220):

```python
def create_error_response(code: str, message: str, details: Optional[Dict] = None, status_code: int = 400):
    """Create standardized error response"""
    error_data = {
        "code": code,
        "message": message
    }
    if details:
        error_data["details"] = details

    raise HTTPException(
        status_code=status_code,
        detail={
            "success": False,
            "error": error_data
        }
    )
```

---

## 2. CONDITIONS THAT TRIGGER 409 ERROR

The 409 error is triggered in the `/auth/passkey/register/start` endpoint when:

1. **An HTTP POST request** is made to `/auth/passkey/register/start`
2. **With an email** in the request body
3. **AND** a user already exists in the database with that email where `is_active = TRUE`

### Database Query (Line 229):
```python
existing_user = db.get_user_by_email(request.email)
```

### User Lookup Implementation (`database_passkeys.py` Lines 185-193):
```python
def get_user_by_email(self, email: str) -> Optional[Dict[str, Any]]:
    """Get user by email"""
    with sqlite3.connect(self.db_path) as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        cursor.execute('SELECT * FROM users WHERE email = ? AND is_active = TRUE', (email,))
        user = cursor.fetchone()
        return dict(user) if user else None
```

**Key Point:** The check ONLY looks for **ACTIVE** users (`is_active = TRUE`).

---

## 3. HOW USER UNIQUENESS IS DETERMINED

### Database Schema (`database_passkeys.py` Lines 26-33):
```python
CREATE TABLE IF NOT EXISTS users (
    id TEXT PRIMARY KEY,
    email TEXT UNIQUE NOT NULL,  # <-- UNIQUE CONSTRAINT on email
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE  # <-- Soft-delete flag
)
```

### Uniqueness Logic:

**Two levels of user uniqueness:**

1. **At Application Level** (`/register/start`):
   - Checks if `email` exists with `is_active = TRUE`
   - Returns 409 if found
   
2. **At Database Level**:
   - Email has `UNIQUE NOT NULL` constraint
   - Would raise `sqlite3.IntegrityError` if constraint is violated
   - This constraint applies to ALL emails, regardless of `is_active` status

### The Problem:

The check at line 229 in `passkey_auth.py` only checks for **active** users, but the database constraint applies to **all** users (active and inactive). This creates a scenario where:
- Inactive users can prevent new registrations (database constraint violation)
- No proper error handling for this case

---

## 4. CRITICAL ISSUES WITH CURRENT IMPLEMENTATION

### Issue #1: Race Condition in Registration Flow

**Flow:**
1. **User A** → `/register/start` with email@example.com
   - Check passes: no active user found
   - Generates challenge_id: `challenge_abc123`
   - Returns to frontend

2. **User B** → `/register/start` with email@example.com (SAME EMAIL)
   - Check passes: no active user found (still!)
   - Generates challenge_id: `challenge_xyz789`
   - Returns to frontend

3. **User A** → `/register/verify` with challenge_id: `challenge_abc123`
   - Line 361: `user = db.create_user(request.email)`
   - **SUCCESS** - User A is created

4. **User B** → `/register/verify` with challenge_id: `challenge_xyz789`
   - Line 361: `user = db.create_user(request.email)`
   - **UNHANDLED `sqlite3.IntegrityError`** - UNIQUE constraint violation!
   - Falls through to generic Exception handler (line 407)
   - Returns 500 error instead of 409!

**Code Location:** `/home/user/tuxedo/backend/api/routes/passkey_auth.py` (Lines 286-413)

```python
@router.post("/auth/passkey/register/verify", response_model=RegisterVerifyResponse)
async def register_verify(req: Request, request: RegisterVerifyRequest):
    """Verify passkey registration and create user"""
    try:
        # ... validation code ...
        
        # Create user - NO CHECK FOR EXISTING USER!
        user = db.create_user(request.email)  # Line 361 - CAN FAIL WITH IntegrityError!
        
        # ... rest of registration ...
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error verifying registration: {e}")
        create_error_response(
            "REGISTRATION_VERIFY_FAILED",
            "Failed to complete registration",
            status_code=500  # <-- WRONG STATUS CODE FOR DUPLICATE EMAIL
        )
```

**Where is the check?** There is NO check for existing users in `register_verify`!

### Issue #2: Deactivated User Scenario

**Flow:**
1. User has account with email@example.com and `is_active = TRUE`
2. User gets deactivated: `is_active = FALSE` (possibly from admin action)
3. User tries to re-register with same email@example.com
4. `/register/start` check:
   ```python
   cursor.execute('SELECT * FROM users WHERE email = ? AND is_active = TRUE', (email,))
   ```
   - Returns: `None` (because is_active is FALSE)
5. Check passes! 409 is NOT returned
6. User goes through `/register/verify` and calls:
   ```python
   user = db.create_user(request.email)
   ```
7. **Result:** `sqlite3.IntegrityError` - UNIQUE constraint violation
8. Returns 500 error instead of proper 409

### Issue #3: No Error Handling for IntegrityError

**Location:** `/home/user/tuxedo/backend/database_passkeys.py` (Lines 168-183)

```python
def create_user(self, email: str) -> Dict[str, Any]:
    """Create a new user"""
    user_id = f"user_{secrets.token_urlsafe(16)}"

    with sqlite3.connect(self.db_path) as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        cursor.execute('''
            INSERT INTO users (id, email, created_at)
            VALUES (?, ?, ?)
        ''', (user_id, email, datetime.now()))
        conn.commit()  # <-- No error handling for UNIQUE constraint!

        cursor.execute('SELECT * FROM users WHERE id = ?', (user_id,))
        return dict(cursor.fetchone())
```

**Missing Exception Handling:**
- No `try/except` for `sqlite3.IntegrityError`
- No check before insert to verify email is truly unique
- Database constraint violations propagate as unhandled exceptions

---

## 5. RP_ID AND ORIGIN HANDLING

### Location: `/home/user/tuxedo/backend/api/routes/passkey_auth.py` (Lines 52-91)

```python
def get_rp_id_and_origin(request: Request) -> tuple[str, str]:
    """
    Dynamically determine RP_ID and origin from request headers.
    """
    # Try to get origin from request headers
    origin = request.headers.get("origin")
    referer = request.headers.get("referer")

    # Fallback to referer if origin is not present
    if not origin and referer:
        from urllib.parse import urlparse
        parsed = urlparse(referer)
        origin = f"{parsed.scheme}://{parsed.netloc}"

    # Default to localhost for development
    if not origin:
        origin = "http://localhost:5173"

    # Validate origin is in allowed list
    if origin not in ALLOWED_ORIGINS:
        logger.warning(f"Origin {origin} not in allowed list, using default")
        origin = "http://localhost:5173"  # <-- FALLBACK to localhost

    # Extract RP_ID (hostname) from origin
    from urllib.parse import urlparse
    parsed = urlparse(origin)
    rp_id = parsed.hostname or "localhost"

    # For localhost, use "localhost" as RP_ID
    # For production domains, use the full hostname
    if rp_id in ["localhost", "127.0.0.1"]:
        rp_id = "localhost"

    logger.info(f"Using RP_ID: {rp_id}, Origin: {origin}")
    return rp_id, origin
```

### RP_ID Derivation Process:

1. **Extract origin from request headers**
   - Primary: `Origin` header
   - Fallback: Extract from `Referer` header
   - Default: `http://localhost:5173`

2. **Validate against whitelist**:
   ```python
   ALLOWED_ORIGINS = [
       "http://localhost:5173",
       "http://localhost:3000",
       "https://tuxedo.onrender.com",
       "https://tuxedo-frontend.onrender.com"
   ]
   ```

3. **Extract hostname from origin**:
   - `https://tuxedo.onrender.com` → RP_ID: `tuxedo.onrender.com`
   - `http://localhost:5173` → RP_ID: `localhost`
   - `http://127.0.0.1:5173` → RP_ID: `localhost`

### Potential Issue: Inconsistent RP_ID

If a client connects from different origins (e.g., `localhost:5173` vs `127.0.0.1:5173`), they will get **the same RP_ID (`localhost`)**, which is good. However:

- **During `/register/start`**: RP_ID determined and used for challenge generation
- **During `/register/verify`**: RP_ID is determined AGAIN from new request headers
- **If origin differs between requests**, RP_ID may differ
- **This causes credential verification to fail**

The verification at line 322-328 expects:
```python
verification = verify_registration_response(
    credential=parsed_credential,
    expected_challenge=challenge_data['challenge'].encode(),
    expected_origin=origin,  # <-- MUST MATCH register/start origin
    expected_rp_id=rp_id,     # <-- MUST MATCH register/start RP_ID
    require_user_verification=True,
)
```

---

## 6. SUMMARY TABLE

| Aspect | Details |
|--------|---------|
| **409 Endpoint** | `POST /auth/passkey/register/start` |
| **409 Trigger** | User with email already exists AND `is_active = TRUE` |
| **Error Code** | `USER_EXISTS` |
| **Error Message** | `"An account with this email already exists"` |
| **Database Constraint** | `email TEXT UNIQUE NOT NULL` on `users` table |
| **Active User Check** | `is_active = TRUE` in SQL query |
| **Critical Gap** | No matching check in `/register/verify` endpoint |

---

## 7. RECOMMENDATIONS

### Priority 1 - Fix Race Condition:
Add email existence check to `register_verify` endpoint:
```python
# Before db.create_user(request.email)
existing_user = db.get_user_by_email(request.email)
if existing_user:
    create_error_response(
        "USER_EXISTS",
        "An account with this email already exists",
        status_code=409
    )
```

### Priority 2 - Handle IntegrityError:
Wrap `create_user()` with try/except:
```python
try:
    user = db.create_user(request.email)
except sqlite3.IntegrityError:
    create_error_response(
        "USER_EXISTS",
        "An account with this email already exists",
        status_code=409
    )
```

### Priority 3 - Store RP_ID in Challenge:
Store RP_ID and origin in challenge to ensure consistency:
```python
challenge_data = db.create_challenge(
    user_id=None,
    expires_minutes=15,
    rp_id=rp_id,
    origin=origin
)
```

### Priority 4 - Document Deactivated User Behavior:
Clarify whether deactivated users should be able to re-register or not.
