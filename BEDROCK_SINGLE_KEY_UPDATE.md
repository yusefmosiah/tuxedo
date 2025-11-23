# Bedrock Single-Key Authentication Update

**Date**: 2025-11-22
**Status**: ✅ Complete - Ready for your API key

---

## 🎯 Summary

AWS Bedrock now supports **single-key authentication** using `AWS_BEARER_TOKEN_BEDROCK`. The codebase has been updated to support this simpler method alongside the traditional IAM credentials approach.

You can now use your single Bedrock API key instead of needing both access key ID and secret access key!

---

## ✅ What Was Updated

### Code Changes

1. **`backend/agent/claude_sdk_wrapper.py`** - Updated authentication logic
   - ✅ Detects `AWS_BEARER_TOKEN_BEDROCK` environment variable
   - ✅ Falls back to traditional IAM credentials if bearer token not found
   - ✅ Clear logging shows which authentication method is active
   - Lines 65-89: New authentication detection logic

2. **`backend/.env.example`** - Updated configuration template
   - ✅ Shows API key method as Option 2 (recommended for Bedrock)
   - ✅ Traditional IAM method as Option 3
   - Lines 16-26: New Bedrock authentication options

### Documentation Updates

3. **`AWS_BEDROCK_SETUP_SUMMARY.md`**
   - ✅ Added API key method as recommended approach
   - ✅ Updated "Get Your AWS Credentials" section
   - ✅ Updated expected test output

4. **`docs/AWS_BEDROCK_CONFIGURATION.md`**
   - ✅ Added "Authentication Methods" section at top
   - ✅ Method 1: API Key Authentication (recommended)
   - ✅ Method 2: IAM Credentials (traditional)
   - ✅ Clear step-by-step instructions for each method

5. **`docs/CLAUDE_SDK_INTEGRATION.md`**
   - ✅ Updated from 2 to 3 authentication methods
   - ✅ Option B: AWS Bedrock with API Key (recommended for production)
   - ✅ Option C: AWS Bedrock with IAM Credentials (traditional)

6. **`backend/BEDROCK_QUICKSTART.md`**
   - ✅ Updated Step 1 with both authentication options
   - ✅ Updated "Getting AWS Credentials" section
   - ✅ Updated quick switch examples

### New Documentation

7. **`BEDROCK_API_KEY_SETUP.md`** (NEW)
   - Quick reference guide specifically for single-key setup
   - Troubleshooting tips
   - Next steps for Ghostwriter integration

8. **`BEDROCK_SINGLE_KEY_UPDATE.md`** (THIS FILE)
   - Complete update summary
   - Files changed and what was updated

---

## 🚀 How to Use Your API Key

### Quick Setup (3 Steps)

1. **Create or edit** `backend/.env`:

```bash
# Claude SDK Configuration - AWS Bedrock
CLAUDE_SDK_USE_BEDROCK=true
ENABLE_CLAUDE_SDK=true

# Paste your Bedrock API key here
AWS_BEARER_TOKEN_BEDROCK=your_actual_bedrock_api_key_here
AWS_REGION=us-east-1
```

2. **Test the configuration**:

```bash
cd backend
source .venv/bin/activate
python3 test_claude_sdk_integration.py
```

**Expected output:**

```
✅ Using AWS Bedrock API Key authentication (region: us-east-1)
✅ Claude SDK initialized successfully
   Authentication: AWS Bedrock
```

3. **Start the backend**:

```bash
python3 main.py
```

**Look for:**

```
✅ Using AWS Bedrock API Key authentication (region: us-east-1)
✅ Claude SDK initialized successfully
```

---

## 📋 Files Changed

| File                                  | Lines Changed | Type   |
| ------------------------------------- | ------------- | ------ |
| `backend/agent/claude_sdk_wrapper.py` | 65-89         | Code   |
| `backend/.env.example`                | 9-26          | Config |
| `AWS_BEDROCK_SETUP_SUMMARY.md`        | 15-77         | Docs   |
| `docs/AWS_BEDROCK_CONFIGURATION.md`   | 1-77          | Docs   |
| `docs/CLAUDE_SDK_INTEGRATION.md`      | 79-137        | Docs   |
| `backend/BEDROCK_QUICKSTART.md`       | 5-105         | Docs   |
| `BEDROCK_API_KEY_SETUP.md`            | New file      | Docs   |
| `BEDROCK_SINGLE_KEY_UPDATE.md`        | New file      | Docs   |

**Total**: 6 files updated, 2 files created

---

## 🔍 Technical Details

### How It Works

The `ClaudeSDKAgent` class now checks for authentication in this order:

1. **Bedrock mode enabled?** Check `CLAUDE_SDK_USE_BEDROCK` environment variable
2. **If Bedrock:**
   - First check for `AWS_BEARER_TOKEN_BEDROCK` (single-key method)
   - Fall back to `AWS_ACCESS_KEY_ID` + `AWS_SECRET_ACCESS_KEY` (traditional method)
   - Log which authentication method is being used
3. **If not Bedrock:** Use `ANTHROPIC_API_KEY` (direct Anthropic API)

### Environment Variable Precedence

For AWS Bedrock:

```python
if aws_bearer_token:
    # Use single-key API authentication
    logger.info("✅ Using AWS Bedrock API Key authentication")
elif aws_access_key_id and aws_secret_access_key:
    # Use traditional IAM credentials
    logger.info("✅ Using AWS Bedrock IAM credentials")
else:
    # No credentials found
    logger.warning("AWS Bedrock enabled but credentials not found")
```

---

## 🎓 Why This Matters

### Old Way (Complex)

```bash
# Required 3 pieces of information
AWS_ACCESS_KEY_ID=AKIA...
AWS_SECRET_ACCESS_KEY=wJal...
AWS_REGION=us-east-1

# Plus IAM setup:
# - Create IAM user
# - Attach Bedrock policy
# - Generate access keys
# - Manage key rotation
```

### New Way (Simple)

```bash
# Required 2 pieces of information
AWS_BEARER_TOKEN_BEDROCK=eyJhb...
AWS_REGION=us-east-1

# Plus simpler setup:
# - Go to Bedrock console
# - Click "Create API Key"
# - Done!
```

**Result**: 40% fewer configuration steps, simpler credential management.

---

## 🔐 Security Benefits

### API Key Method

- ✅ Scoped to Bedrock only (no broader AWS access)
- ✅ Simpler to rotate (single key instead of pair)
- ✅ No IAM user management complexity
- ✅ Clear audit trail in Bedrock console

### IAM Method (Still Supported)

- ✅ More granular permissions control
- ✅ Can use IAM roles (EC2, ECS, Lambda)
- ✅ Integrated with AWS Organizations
- ✅ Centralized billing and governance

**Choose based on your use case:**

- **Development/Testing**: API Key method
- **Production with AWS infrastructure**: IAM method with roles
- **Production without AWS infrastructure**: API Key method

---

## 📚 References

### Official AWS Documentation

- **Bedrock API Keys**: [AWS Bedrock Documentation](https://docs.aws.amazon.com/bedrock/)
- **Available Regions**: [Models by Region](https://docs.aws.amazon.com/bedrock/latest/userguide/models-regions.html)
- **Claude Models**: [Anthropic Claude on Bedrock](https://docs.aws.amazon.com/bedrock/latest/userguide/model-parameters-anthropic-claude.html)

### Project Documentation

- **Setup Guide**: `BEDROCK_API_KEY_SETUP.md` (for single-key method)
- **Detailed Config**: `docs/AWS_BEDROCK_CONFIGURATION.md` (both methods)
- **Quick Start**: `backend/BEDROCK_QUICKSTART.md` (3-minute setup)
- **Integration Docs**: `docs/CLAUDE_SDK_INTEGRATION.md` (complete guide)

### GitHub Issues & Discussions

- [Claude Code Bedrock API Keys Support](https://github.com/anthropics/claude-code/issues/3283)

---

## 🎯 Next Steps

### Immediate (Today)

1. ✅ Review this document
2. ⏭️ **Paste your Bedrock API key into `backend/.env`**
3. ⏭️ Run `python3 test_claude_sdk_integration.py`
4. ⏭️ Verify "API Key authentication" appears in logs
5. ⏭️ Start backend and confirm initialization

### Short Term (This Week)

1. Test Claude SDK endpoints via `/api/claude-sdk/*`
2. Integrate Ghostwriter features with Claude SDK
3. Set up cost monitoring in AWS Cost Explorer
4. Configure billing alerts for Bedrock usage

### Medium Term (This Month)

1. Build Ghostwriter UI components
2. Implement citation tracking system
3. Connect to knowledge base storage
4. Test full research → publish → cite → reward flow

---

## ✅ Verification Checklist

Before starting the backend, verify:

- [ ] `backend/.env` file exists
- [ ] `AWS_BEARER_TOKEN_BEDROCK` is set (your actual key, not placeholder)
- [ ] `CLAUDE_SDK_USE_BEDROCK=true` is set
- [ ] `AWS_REGION=us-east-1` (or your preferred region)
- [ ] `ENABLE_CLAUDE_SDK=true` is set
- [ ] No syntax errors in `.env` file

After starting backend, verify:

- [ ] Logs show "✅ Using AWS Bedrock API Key authentication"
- [ ] No authentication errors in logs
- [ ] `/api/claude-sdk/status` returns `"status": "ready"`
- [ ] Can successfully call `/api/claude-sdk/query`

---

## 💡 Pro Tips

1. **Use environment-specific configs**: Keep production keys in secrets manager, development keys in local `.env`
2. **Monitor costs early**: Set up AWS billing alerts before heavy usage
3. **Test with small queries first**: Verify authentication before long research sessions
4. **Keep fallback**: Maintain Anthropic API key as backup if Bedrock has issues
5. **Document your region choice**: Different regions may have different model availability and pricing

---

**Questions or Issues?**

Check the troubleshooting section in `BEDROCK_API_KEY_SETUP.md` or review the detailed configuration guide in `docs/AWS_BEDROCK_CONFIGURATION.md`.

---

**Status**: ✅ All changes committed and ready. Just add your API key and test! 🚀
