# AWS Bedrock API Key Setup (Single-Key Method)

**Last Updated**: 2025-11-22
**Status**: Ready to configure

---

## ✅ What You Have

You received a **single Bedrock API key** from AWS. This is the newer, simpler authentication method that doesn't require separate access key ID and secret access key.

## 🚀 Quick Setup (3 Steps)

### 1. Edit Your `.env` File

Open `backend/.env` and add:

```bash
# Claude SDK Configuration - AWS Bedrock API Key
CLAUDE_SDK_USE_BEDROCK=true
ENABLE_CLAUDE_SDK=true

# Your Bedrock API Key (paste your key here)
AWS_BEARER_TOKEN_BEDROCK=your_bedrock_api_key_here
AWS_REGION=us-east-1
```

### 2. Test the Configuration

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

### 3. Start the Backend

```bash
python3 main.py
```

**Look for this in the logs:**

```
Initializing Claude SDK with AWS Bedrock
✅ Using AWS Bedrock API Key authentication (region: us-east-1)
✅ Claude SDK initialized successfully
```

---

## 📝 What Changed

We updated the code to support **two Bedrock authentication methods**:

1. **Single API Key** (your method) - `AWS_BEARER_TOKEN_BEDROCK`
2. **Traditional IAM** - `AWS_ACCESS_KEY_ID` + `AWS_SECRET_ACCESS_KEY`

The system automatically detects which method you're using based on which environment variables are set.

---

## 🔧 Troubleshooting

### Can't find the API key?

- Check your AWS Bedrock console → API Keys section
- The key should start with a specific prefix (varies by AWS)

### Wrong region error?

- Make sure Claude models are enabled in your region
- Try `us-east-1` (most reliable)
- Check available regions: https://docs.aws.amazon.com/bedrock/latest/userguide/models-regions.html

### Still see "credentials not found" warning?

- Double-check your `.env` file is in the `backend/` directory
- Ensure no typos in variable names
- Make sure the variables are not commented out with `#`
- Restart the backend after changing `.env`

---

## 📚 Updated Documentation

All documentation has been updated to reflect the single-key method:

- ✅ `backend/agent/claude_sdk_wrapper.py` - Detects and uses `AWS_BEARER_TOKEN_BEDROCK`
- ✅ `backend/.env.example` - Shows API key method as recommended
- ✅ `AWS_BEDROCK_SETUP_SUMMARY.md` - Updated with API key instructions
- ✅ `docs/AWS_BEDROCK_CONFIGURATION.md` - Added Method 1 for API keys
- ✅ `docs/CLAUDE_SDK_INTEGRATION.md` - Added Option B for API keys

---

## 🎯 Next Steps for Ghostwriter

Once the Bedrock connection is working, you'll be able to use the Claude SDK for:

1. **Research queries** - `/api/claude-sdk/query`
2. **Strategy analysis** - `/api/claude-sdk/analyze-strategy`
3. **Yield research** - `/api/claude-sdk/research-yield`
4. **Performance reports** - `/api/claude-sdk/generate-report`

These endpoints will power the **Ghostwriter** feature for research, writing, and knowledge base building.

---

## 🔐 Security Notes

- Never commit your `.env` file to git (already in `.gitignore`)
- Keep your API key secure
- Rotate keys regularly
- Use IAM roles for production deployments

---

**Ready?** Just paste your API key into `backend/.env` and run the test! 🚀
