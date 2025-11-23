# AWS Bedrock Configuration - Complete! ✅

**Date**: 2025-11-20
**Commit**: 52a786e
**Status**: Ready for your AWS credentials

---

## What Was Added

The Claude SDK integration now supports **AWS Bedrock** as an alternative to direct Anthropic API authentication. You can choose whichever method works best for you!

## 📝 Configuration Template for You

Add these to your `backend/.env` file:

```bash
# Claude SDK Configuration - AWS Bedrock
CLAUDE_SDK_USE_BEDROCK=true
ENABLE_CLAUDE_SDK=true

# AWS Bedrock API Key (recommended - simpler method, July 2025+)
AWS_BEARER_TOKEN_BEDROCK=<your-bedrock-api-key>
AWS_REGION=us-east-1
```

**That's it!** Just replace the placeholder with your actual Bedrock API key.

**Alternative (Traditional IAM Credentials):**

```bash
# Claude SDK Configuration - AWS Bedrock
CLAUDE_SDK_USE_BEDROCK=true
ENABLE_CLAUDE_SDK=true

# Traditional IAM credentials
AWS_ACCESS_KEY_ID=<your-access-key>
AWS_SECRET_ACCESS_KEY=<your-secret-key>
AWS_REGION=us-east-1
```

## 🚀 Quick Start

### 1. Get Your AWS Bedrock API Key

**Recommended Method (Simpler):**

1. Go to AWS Console → Amazon Bedrock
2. Navigate to "API Keys" section (available July 2025+)
3. Click "Create API Key"
4. Copy your Bedrock API key

**Alternative (Traditional IAM):**

1. Go to AWS Console → IAM
2. Create or select a user
3. Attach Bedrock permissions (see docs for IAM policy)
4. Create access key
5. Copy the access key ID and secret access key

### 2. Edit `.env`

```bash
cd backend
nano .env  # or use your favorite editor
```

Add the AWS Bedrock configuration (see template above).

### 3. Test It

```bash
cd backend
source .venv/bin/activate
python3 test_claude_sdk_integration.py
```

Expected output:

```
✅ Using AWS Bedrock API Key authentication (region: us-east-1)
✅ Claude SDK initialized successfully
   Authentication: AWS Bedrock
```

### 4. Start Backend

```bash
python3 main.py
```

Look for this in the logs:

```
Initializing Claude SDK with AWS Bedrock (region: us-east-1)
✅ Claude SDK initialized successfully
   Authentication: AWS Bedrock
```

## 📚 Documentation Created

### Quick Reference

- **backend/BEDROCK_QUICKSTART.md** - 3-minute setup guide

### Detailed Guide

- **docs/AWS_BEDROCK_CONFIGURATION.md** - Complete configuration guide with:
  - IAM permissions template
  - Available regions and models
  - Troubleshooting tips
  - Security best practices
  - Cost optimization
  - Production IAM role setup

### Integration Docs

- **docs/CLAUDE_SDK_INTEGRATION.md** - Updated with dual authentication options

## 🔄 Switching Between Authentication Methods

You can easily switch between Anthropic API and AWS Bedrock:

### Use Anthropic API:

```bash
CLAUDE_SDK_USE_BEDROCK=false
ANTHROPIC_API_KEY=sk-ant-your-key
ENABLE_CLAUDE_SDK=true
```

### Use AWS Bedrock:

```bash
CLAUDE_SDK_USE_BEDROCK=true
AWS_REGION=us-east-1
AWS_ACCESS_KEY_ID=your-key
AWS_SECRET_ACCESS_KEY=your-secret
ENABLE_CLAUDE_SDK=true
```

Just change the config and restart the backend.

## ✨ New Features

### Automatic Detection

- System automatically reads `CLAUDE_SDK_USE_BEDROCK` from environment
- Falls back to Anthropic API if Bedrock not configured
- Clear logging shows which authentication method is active

### Dual Mode Support

```python
# In claude_sdk_wrapper.py
agent = ClaudeSDKAgent(use_bedrock=True)  # AWS Bedrock
agent = ClaudeSDKAgent(use_bedrock=False) # Anthropic API
```

### Production Ready

- IAM role support for EC2/ECS
- Regional deployment options
- CloudTrail audit logging
- Cost tracking via AWS Cost Explorer

## 🔐 Security Best Practices

1. **Never commit credentials** to git (already in .gitignore)
2. **Use IAM roles** for production (EC2/ECS)
3. **Restrict permissions** to Bedrock only
4. **Rotate credentials** regularly
5. **Enable CloudTrail** for audit logs

## 💰 Cost Information

AWS Bedrock pricing (approximate, as of 2025):

- **Input tokens**: ~$3 per million
- **Output tokens**: ~$15 per million

Monitor usage in AWS Cost Explorer:

- AWS Console → Cost Explorer
- Filter by Service: "Bedrock"
- Set up billing alerts

## 🎯 Next Steps

### Immediate:

1. ✅ Review this summary
2. ⏭️ **Add your AWS credentials to `backend/.env`**
3. ⏭️ Run `python3 test_claude_sdk_integration.py`
4. ⏭️ Start backend: `python3 main.py`
5. ⏭️ Test endpoints via http://localhost:8000/docs

### Optional:

- Set up IAM role for production
- Configure billing alerts in AWS
- Enable CloudTrail logging
- Review cost optimization tips in docs

## 📦 Files Changed

```
Modified:
  backend/.env.example                    # Added Bedrock config template
  backend/agent/claude_sdk_wrapper.py     # Added dual auth support
  backend/config/settings.py              # Added AWS config options
  docs/CLAUDE_SDK_INTEGRATION.md          # Updated with Bedrock info

Created:
  backend/BEDROCK_QUICKSTART.md           # 3-min setup guide
  docs/AWS_BEDROCK_CONFIGURATION.md       # Detailed Bedrock guide
```

## 🔍 IAM Permissions Needed

Your AWS user needs this policy:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "bedrock:InvokeModel",
        "bedrock:InvokeModelWithResponseStream"
      ],
      "Resource": "arn:aws:bedrock:*::foundation-model/anthropic.claude-*"
    }
  ]
}
```

## 🌍 Available Regions

Claude models available in:

- `us-east-1` (N. Virginia) ✅ Recommended
- `us-west-2` (Oregon)
- `ap-southeast-1` (Singapore)
- `ap-northeast-1` (Tokyo)
- `eu-central-1` (Frankfurt)

## 🆘 Troubleshooting

### Can't find AWS credentials

- Check `.env` file exists in `backend/` directory
- Verify no typos in variable names
- Ensure credentials are not commented out

### Access Denied (403)

- Verify IAM permissions (see policy above)
- Check Bedrock is enabled in your AWS region
- Request model access in Bedrock console

### Wrong region

- Claude might not be available in your region
- Try `us-east-1` (most reliable)
- Check available regions in docs

### Need help?

- See `docs/AWS_BEDROCK_CONFIGURATION.md` for detailed troubleshooting
- Check backend logs for specific error messages
- Verify credentials work with AWS CLI: `aws bedrock list-foundation-models`

## ✅ Verification Checklist

Before starting the backend:

- [ ] AWS credentials added to `backend/.env`
- [ ] `CLAUDE_SDK_USE_BEDROCK=true` is set
- [ ] Region is set (default: `us-east-1`)
- [ ] IAM permissions configured correctly
- [ ] Integration test passes

After starting:

- [ ] Backend logs show "AWS Bedrock" authentication
- [ ] No error messages in logs
- [ ] `/api/claude-sdk/status` returns `"status": "ready"`
- [ ] Can call `/api/claude-sdk/query` successfully

## 🎉 You're All Set!

The configuration is complete on the code side. Now you just need to:

1. **Add your AWS credentials** to `backend/.env`
2. **Test the integration**
3. **Start using Claude SDK with AWS Bedrock!**

All the code changes are committed and pushed:

- Branch: `claude/setup-agents-sdk-01YZNisosPQ3k6Lm17z2jd2A`
- Commit: 52a786e

---

## Quick Reference Card

```bash
# Configuration file
backend/.env

# Required variables for AWS Bedrock
CLAUDE_SDK_USE_BEDROCK=true
AWS_REGION=us-east-1
AWS_ACCESS_KEY_ID=<your-key>
AWS_SECRET_ACCESS_KEY=<your-secret>
ENABLE_CLAUDE_SDK=true

# Test integration
cd backend && source .venv/bin/activate
python3 test_claude_sdk_integration.py

# Start backend
python3 main.py

# Check status
curl http://localhost:8000/api/claude-sdk/status

# API docs
http://localhost:8000/docs
```

**Ready when you are!** Just add your AWS credentials and you're good to go. 🚀
