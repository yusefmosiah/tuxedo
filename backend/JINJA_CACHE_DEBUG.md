# Jinja2 Cache Permission Error - Debugging Guide

## Problem Summary

**Error**: `[Errno 13] Permission denied: '/usr/local/lib/python3.12/site-packages/openhands/sdk/agent/prompts/.jinja_cache'`

**Location**: Ghostwriter pipeline using OpenHands SDK

**Previous Fix Attempts** (commits 868e806, 0c39d0b):
1. Set `XDG_CACHE_HOME` and `LITELLM_CACHE_DIR` in main.py
2. Set `TMPDIR` environment variable in main.py
3. Created `/tmp/tuxedo_cache` in Dockerfile

**Why Previous Fixes Didn't Work**:
- Environment variables were set in Python code (`main.py`) at runtime
- Some module imports may happen before or during app initialization
- OpenHands SDK might be hardcoding the Jinja2 cache location
- Container-level environment needs to be set before Python starts

---

## Root Cause Analysis

### The Issue Chain:
1. Docker container installs Python packages as **root user** (`uv pip install --system`)
2. Packages go to `/usr/local/lib/python3.12/site-packages/` (system directory)
3. Container switches to **app user** (non-root)
4. OpenHands SDK imports Jinja2 and tries to create bytecode cache
5. Default cache location: `<package_dir>/openhands/sdk/agent/prompts/.jinja_cache`
6. **Permission denied** - app user can't write to system package directory

### Why Setting TMPDIR in Python Code Didn't Work:
- Environment variables set in `main.py` only affect the current process
- Some imports happen at module level, before env vars are set
- Jinja2's `FileSystemBytecodeCache` might be initialized during import
- Child processes or already-initialized modules don't see the env vars

---

## New Debugging Strategy (Multi-Layered Approach)

### Layer 1: Container-Level Environment Variables ✅
**File**: `Dockerfile.backend`

Set environment variables at Docker layer (before any Python code runs):
```dockerfile
ENV TMPDIR=/tmp/tuxedo_cache
ENV XDG_CACHE_HOME=/tmp/tuxedo_cache
ENV LITELLM_CACHE_DIR=/tmp/tuxedo_cache
ENV JINJA2_CACHE_DIR=/tmp/tuxedo_cache
```

**Why this helps**:
- Env vars available from container start
- All Python processes inherit these variables
- Jinja2's `tempfile.gettempdir()` will use `/tmp/tuxedo_cache`
- No timing issues with import order

### Layer 2: Pre-Create Cache Directory in Package ✅
**File**: `Dockerfile.backend`

Create writable `.jinja_cache` directory in OpenHands package location:
```dockerfile
RUN mkdir -p /usr/local/lib/python3.*/site-packages/openhands/sdk/agent/prompts/.jinja_cache && \
    chmod -R 777 /usr/local/lib/python3.*/site-packages/openhands/sdk/agent/prompts/.jinja_cache
```

**Why this helps**:
- Fallback if OpenHands hardcodes the cache path
- Allows writing to system package directory (controlled environment)
- Uses `|| true` to continue even if OpenHands isn't installed (dev environments)

### Layer 3: Enhanced Diagnostic Logging ✅
**File**: `main.py`

Added logging to verify environment configuration:
```python
logger.info(f"Cache directory configured: {CACHE_DIR}")
logger.info(f"TMPDIR: {os.environ.get('TMPDIR')}")
logger.info(f"XDG_CACHE_HOME: {os.environ.get('XDG_CACHE_HOME')}")
logger.info(f"LITELLM_CACHE_DIR: {os.environ.get('LITELLM_CACHE_DIR')}")
logger.info(f"JINJA2_CACHE_DIR: {os.environ.get('JINJA2_CACHE_DIR')}")
logger.info(f"tempfile.gettempdir(): {tempfile.gettempdir()}")
```

**What to look for in logs**:
- All env vars should show `/tmp/tuxedo_cache`
- `tempfile.gettempdir()` should return `/tmp/tuxedo_cache`
- If any show different values, those env vars aren't being respected

---

## Testing Procedure

### 1. Rebuild Docker Image
```bash
# From project root
docker build -f Dockerfile.backend -t choir-backend:debug .
```

### 2. Run Container and Check Logs
```bash
docker run -p 8000:8000 choir-backend:debug
```

**Look for in startup logs**:
```
INFO:     Cache directory configured: /tmp/tuxedo_cache
INFO:     TMPDIR: /tmp/tuxedo_cache
INFO:     XDG_CACHE_HOME: /tmp/tuxedo_cache
INFO:     LITELLM_CACHE_DIR: /tmp/tuxedo_cache
INFO:     JINJA2_CACHE_DIR: /tmp/tuxedo_cache
INFO:     tempfile.gettempdir(): /tmp/tuxedo_cache
```

### 3. Test Ghostwriter
```bash
# Make API call to trigger Ghostwriter
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Research yield farming on Base", "history": []}'
```

**Expected outcome**:
- ✅ No permission errors
- ✅ Ghostwriter pipeline runs successfully
- ✅ Report generated with citations

**If still fails**, check container logs for:
```
[Errno 13] Permission denied: '/usr/local/lib/python3.12/site-packages/...'
```

---

## Debugging Decision Tree

### If error still occurs:

#### Option A: OpenHands is ignoring environment variables
**Diagnosis**: Logs show correct env vars, but error persists
**Solution**: Investigate OpenHands SDK source to find hardcoded cache path
```bash
# Inside container
find /usr/local/lib/python3.*/site-packages/openhands -name "*.py" -exec grep -l "FileSystemBytecodeCache\|jinja.*cache" {} \;
```

#### Option B: Import timing issue
**Diagnosis**: Some imports happen before main.py sets env vars
**Solution**: Move env var setup earlier (before `load_dotenv()`)
```python
# At very top of main.py, before any imports
import os
os.environ.setdefault("TMPDIR", "/tmp/tuxedo_cache")
```

#### Option C: Multiple Python processes
**Diagnosis**: Worker processes inherit clean environment
**Solution**: Ensure uvicorn workers inherit environment
```dockerfile
# In Dockerfile, before CMD
ENV UVICORN_WORKER_CONNECTIONS=1
ENV UVICORN_WORKERS=1
```

#### Option D: File permissions on cache directory
**Diagnosis**: `/tmp/tuxedo_cache` exists but isn't writable
**Solution**: Check ownership and permissions
```bash
# Inside container (as app user)
ls -la /tmp/tuxedo_cache
# Should show: drwxr-xr-x app app

# Test write access
touch /tmp/tuxedo_cache/test.txt
```

---

## Expected Results After Fix

### Successful Startup Logs:
```
INFO:     Cache directory configured: /tmp/tuxedo_cache
INFO:     TMPDIR: /tmp/tuxedo_cache
INFO:     XDG_CACHE_HOME: /tmp/tuxedo_cache
INFO:     LITELLM_CACHE_DIR: /tmp/tuxedo_cache
INFO:     JINJA2_CACHE_DIR: /tmp/tuxedo_cache
INFO:     tempfile.gettempdir(): /tmp/tuxedo_cache
INFO:     Started server process [1]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

### Successful Ghostwriter Execution:
```
INFO:     Ghostwriter pipeline started for user: user_123
INFO:     Stage 1: Hypothesis Formation - Starting
INFO:     Stage 1: Hypothesis Formation - Complete
...
INFO:     Stage 8: Style & Polish - Complete
INFO:     Ghostwriter pipeline completed successfully
```

### Cache Files Created:
```bash
# Inside container
ls -la /tmp/tuxedo_cache/
# Should show Jinja2 and LiteLLM cache files owned by app user
```

---

## Verification Commands

### 1. Check Environment in Running Container
```bash
docker exec -it <container_id> /bin/bash
echo $TMPDIR
echo $XDG_CACHE_HOME
echo $LITELLM_CACHE_DIR
python -c "import tempfile; print(tempfile.gettempdir())"
```

### 2. Check Cache Directory Permissions
```bash
docker exec -it <container_id> /bin/bash
ls -la /tmp/tuxedo_cache
ls -la /usr/local/lib/python3.*/site-packages/openhands/sdk/agent/prompts/.jinja_cache 2>/dev/null || echo "Not created (expected if Layer 1 works)"
```

### 3. Check File Ownership
```bash
docker exec -it <container_id> /bin/bash
ps aux | grep uvicorn  # Should run as 'app' user, not root
whoami  # Should be 'app'
```

---

## Changes Made

### 1. Dockerfile.backend
- ✅ Added ENV variables for cache directories (Layer 1)
- ✅ Pre-created `.jinja_cache` in package directory (Layer 2)

### 2. main.py
- ✅ Added `JINJA2_CACHE_DIR` to environment setup
- ✅ Added diagnostic logging for all cache-related env vars
- ✅ Added `tempfile.gettempdir()` logging

### 3. Documentation
- ✅ Created this debugging guide

---

## Next Steps

1. **Rebuild and test**: Build new Docker image and verify logs
2. **Monitor for errors**: Check if permission error still occurs
3. **Review logs**: Analyze diagnostic output to confirm env vars are set
4. **Iterate if needed**: Use decision tree above to debug further

---

## Success Criteria

- ✅ No `[Errno 13] Permission denied` errors when running Ghostwriter
- ✅ Startup logs show all env vars correctly set to `/tmp/tuxedo_cache`
- ✅ `tempfile.gettempdir()` returns `/tmp/tuxedo_cache`
- ✅ Ghostwriter pipeline completes successfully
- ✅ Cache files created in `/tmp/tuxedo_cache`, not in system packages

---

## References

- **Previous fix attempts**:
  - Commit 868e806: "fix: configure writable cache directory for LiteLLM/OpenHands"
  - Commit 0c39d0b: "fix: configure Jinja2 cache directory via TMPDIR environment variable"

- **Related files**:
  - `Dockerfile.backend` - Container build configuration
  - `backend/main.py` - Application entry point
  - `backend/agent/ghostwriter/pipeline.py` - Ghostwriter implementation
  - `backend/.env.example` - Environment variable documentation

- **Jinja2 Documentation**:
  - https://jinja.palletsprojects.com/en/stable/api/#bytecode-cache
  - Jinja2 uses `tempfile.gettempdir()` for default cache location
  - Can be overridden with `FileSystemBytecodeCache(directory=...)`

- **Docker Best Practices**:
  - Set environment variables at container level for system-wide effect
  - Create required directories before switching to non-root user
  - Use `|| true` for operations that may fail in different environments
