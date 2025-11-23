# AWS Bedrock Quick Start

## 🚀 3-Minute Setup

### Step 1: Edit `.env` file

Open `backend/.env` and add:

**Option A: Single API Key (Recommended, simpler)**

```bash
# Enable AWS Bedrock
CLAUDE_SDK_USE_BEDROCK=true
ENABLE_CLAUDE_SDK=true

# Your Bedrock API Key (add your actual key here)
AWS_BEARER_TOKEN_BEDROCK=your-bedrock-api-key-here
AWS_REGION=us-east-1
```

**Option B: Traditional IAM Credentials**

```bash
# Enable AWS Bedrock
CLAUDE_SDK_USE_BEDROCK=true
ENABLE_CLAUDE_SDK=true

# Your AWS IAM Credentials (add your actual keys here)
AWS_REGION=us-east-1
AWS_ACCESS_KEY_ID=your-access-key-here
AWS_SECRET_ACCESS_KEY=your-secret-key-here
```

### Step 2: Test Configuration

```bash
cd backend
source .venv/bin/activate
python3 test_claude_sdk_integration.py
```

### Step 3: Start Backend

```bash
python3 main.py
```

Look for:

```
✅ Claude SDK initialized successfully
   Authentication: AWS Bedrock
```

## ✅ Done!

Your Claude SDK is now using AWS Bedrock for all research and analysis features.

## 📚 Need Help?

- **Detailed Setup**: See `docs/AWS_BEDROCK_CONFIGURATION.md`
- **IAM Permissions**: See template in docs
- **Troubleshooting**: Check logs for "Claude SDK" messages
- **Switch to Anthropic API**: Set `CLAUDE_SDK_USE_BEDROCK=false`

## 🔑 Getting AWS Credentials

**Method 1: API Key (Simpler)**

1. Go to AWS Console → Amazon Bedrock
2. Navigate to "API Keys" section
3. Click "Create API Key"
4. Copy key to `.env` as `AWS_BEARER_TOKEN_BEDROCK`

**Method 2: IAM Credentials (Traditional)**

1. Go to AWS Console → IAM
2. Create new user or use existing
3. Add Bedrock permissions (see docs)
4. Create access key
5. Copy keys to `.env`

## 💰 Cost Tracking

Monitor usage: AWS Console → Cost Explorer → Filter by "Bedrock"

Typical costs: ~$3-15 per million tokens

## ⚡ Quick Switch Between Methods

**Use Anthropic API:**

```bash
CLAUDE_SDK_USE_BEDROCK=false
ANTHROPIC_API_KEY=sk-ant-your-key
```

**Use AWS Bedrock (API Key):**

```bash
CLAUDE_SDK_USE_BEDROCK=true
AWS_BEARER_TOKEN_BEDROCK=your-api-key
AWS_REGION=us-east-1
```

**Use AWS Bedrock (IAM):**

```bash
CLAUDE_SDK_USE_BEDROCK=true
AWS_ACCESS_KEY_ID=your-key
AWS_SECRET_ACCESS_KEY=your-secret
AWS_REGION=us-east-1
```

Restart backend after changing.
