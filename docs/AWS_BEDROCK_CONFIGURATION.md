# AWS Bedrock Configuration Template

This file provides a template for configuring Claude SDK to use AWS Bedrock.

## Authentication Methods

AWS Bedrock supports **two authentication methods**:

1. **API Key (Recommended)** - Single-key authentication (available July 2025+)
2. **IAM Credentials (Traditional)** - Access key + secret key pair

## Prerequisites

1. AWS Account with Bedrock access
2. API Key OR IAM user with Bedrock permissions
3. Claude models enabled in your AWS region

## Required IAM Permissions

Your IAM user needs these permissions:

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

## Configuration

### Method 1: API Key Authentication (Recommended)

Add these to your `backend/.env` file:

```bash
# Claude SDK Configuration - AWS Bedrock
CLAUDE_SDK_USE_BEDROCK=true
ENABLE_CLAUDE_SDK=true

# AWS Bedrock API Key (simpler method)
AWS_BEARER_TOKEN_BEDROCK=your_bedrock_api_key_here
AWS_REGION=us-east-1
```

**How to get an API Key:**

1. Go to AWS Console → Amazon Bedrock
2. Navigate to "API Keys" section (available July 2025+)
3. Click "Create API Key"
4. Copy your Bedrock API key
5. Paste it in your `.env` file

### Method 2: IAM Credentials (Traditional)

Add these to your `backend/.env` file:

```bash
# Claude SDK Configuration - AWS Bedrock
CLAUDE_SDK_USE_BEDROCK=true
ENABLE_CLAUDE_SDK=true

# AWS IAM Credentials
AWS_REGION=us-east-1
AWS_ACCESS_KEY_ID=your_aws_access_key_id_here
AWS_SECRET_ACCESS_KEY=your_aws_secret_access_key_here

# Optional: AWS Session Token (if using temporary credentials)
# AWS_SESSION_TOKEN=your_session_token_here
```

## Available Regions

Claude models are available in these AWS regions:

- `us-east-1` (US East - N. Virginia)
- `us-west-2` (US West - Oregon)
- `ap-southeast-1` (Asia Pacific - Singapore)
- `ap-northeast-1` (Asia Pacific - Tokyo)
- `eu-central-1` (Europe - Frankfurt)

Check the latest list at: https://docs.aws.amazon.com/bedrock/latest/userguide/models-regions.html

## Available Models

Bedrock Claude models (as of 2025):

- `anthropic.claude-3-opus-20240229-v1:0` - Most capable
- `anthropic.claude-3-sonnet-20240229-v1:0` - Balanced
- `anthropic.claude-3-haiku-20240307-v1:0` - Fast and efficient
- `anthropic.claude-3-5-sonnet-20240620-v1:0` - Latest Sonnet

The Claude SDK will automatically use the appropriate model.

## Testing Configuration

Test your Bedrock configuration:

```bash
cd backend
source .venv/bin/activate

# Test the integration
python3 test_claude_sdk_integration.py
```

Expected output:

```
✅ Using AWS Bedrock in region: us-east-1
✅ Claude SDK initialized successfully
   Authentication: AWS Bedrock
```

## Troubleshooting

### Error: "AWS credentials not found"

- Verify `AWS_ACCESS_KEY_ID` and `AWS_SECRET_ACCESS_KEY` are set
- Check for typos in your `.env` file
- Ensure `.env` is in the `backend/` directory

### Error: "Access Denied" or 403

- Verify IAM user has Bedrock permissions (see above)
- Check that you've requested Bedrock access in AWS Console
- Verify Claude models are enabled in your region

### Error: "Model not found"

- Check Claude models are available in your region
- Verify model access is enabled in Bedrock console
- Try a different region (e.g., `us-east-1`)

### Cost Tracking

Monitor Bedrock usage in AWS Cost Explorer:

1. Go to AWS Console → Cost Explorer
2. Filter by Service: "Bedrock"
3. Group by: "Usage Type"

Typical costs (as of 2025):

- Input: ~$3 per million tokens
- Output: ~$15 per million tokens

## Security Best Practices

1. **Never commit credentials** to version control
2. **Use IAM roles** when running on EC2/ECS
3. **Rotate credentials** regularly
4. **Use temporary credentials** via AWS STS when possible
5. **Restrict IAM permissions** to only Bedrock
6. **Enable CloudTrail** for audit logging

## Alternative: IAM Roles (Production)

For production deployments, use IAM roles instead of access keys:

### On EC2/ECS:

1. Create IAM role with Bedrock permissions
2. Attach role to EC2 instance or ECS task
3. Remove `AWS_ACCESS_KEY_ID` and `AWS_SECRET_ACCESS_KEY` from `.env`
4. AWS SDK will automatically use instance credentials

### Configuration for IAM Roles:

```bash
# backend/.env - No AWS credentials needed!
CLAUDE_SDK_USE_BEDROCK=true
ENABLE_CLAUDE_SDK=true
AWS_REGION=us-east-1
```

## Cost Optimization Tips

1. **Use haiku models** for simple queries (~10x cheaper)
2. **Implement caching** for repeated research queries
3. **Set up billing alerts** in AWS Console
4. **Use reserved capacity** for predictable workloads
5. **Monitor usage** via CloudWatch metrics

## Switching Between Anthropic API and Bedrock

To switch authentication methods, just change one variable:

### Use Direct Anthropic API:

```bash
CLAUDE_SDK_USE_BEDROCK=false
ANTHROPIC_API_KEY=sk-ant-your-key-here
```

### Use AWS Bedrock:

```bash
CLAUDE_SDK_USE_BEDROCK=true
AWS_ACCESS_KEY_ID=your-access-key
AWS_SECRET_ACCESS_KEY=your-secret-key
AWS_REGION=us-east-1
```

## Support

- AWS Bedrock Docs: https://docs.aws.amazon.com/bedrock/
- Anthropic on Bedrock: https://docs.anthropic.com/claude/docs/aws-bedrock
- IAM Permissions: https://docs.aws.amazon.com/bedrock/latest/userguide/security-iam.html

---

**Ready to configure?**

1. Copy this template to your notes
2. Fill in your AWS credentials
3. Add to `backend/.env`
4. Run `python3 test_claude_sdk_integration.py`
5. Start using Claude SDK with AWS Bedrock! 🚀
