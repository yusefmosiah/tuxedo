# OpenHands SDK AWS Bedrock Configuration Guide

**Date**: 2025-11-23
**Status**: Researched and Documented
**Purpose**: Guide for configuring OpenHands SDK with AWS Bedrock Claude 4.5 models

---

## Research Summary

OpenHands SDK uses **LiteLLM** under the hood for LLM provider abstraction. This means AWS Bedrock configuration follows LiteLLM conventions, NOT a custom OpenHands API.

### Key Findings

1. ❌ **WRONG**: `LLM(provider="bedrock", model="...", aws_region="...")`
   ✅ **CORRECT**: `LLM(model="bedrock/...", aws_region_name="...", aws_access_key_id="...", aws_secret_access_key="...")`

2. Model names must use the **`bedrock/` prefix** followed by the full Bedrock model ID

3. AWS credentials are passed as **direct parameters**, not via a separate provider field

---

## Correct LLM Configuration

### Claude 4.5 Haiku (Fast, Cost-Efficient)

```python
from openhands.sdk import LLM

llm_haiku = LLM(
    model="bedrock/anthropic.claude-haiku-4-5-20251001-v1:0",
    aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
    aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
    aws_region_name="us-east-1"
)
```

### Claude 4.5 Sonnet (Complex Reasoning)

```python
llm_sonnet = LLM(
    model="bedrock/anthropic.claude-sonnet-4-5-20250929-v1:0",
    aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
    aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
    aws_region_name="us-east-1"
)
```

### Alternative: Using AWS Bearer Token (Simpler)

If using the new AWS Bedrock API key method (July 2025+):

```python
llm = LLM(
    model="bedrock/anthropic.claude-haiku-4-5-20251001-v1:0",
    api_key=os.getenv("AWS_BEARER_TOKEN_BEDROCK"),  # Single key auth
    aws_region_name="us-east-1"
)
```

---

## LLM Class Parameters

Based on code inspection of `openhands/sdk/llm/llm.py`:

### Core Parameters

| Parameter | Type | Description | Example |
|-----------|------|-------------|---------|
| `model` | `str` | Model ID with provider prefix | `"bedrock/anthropic.claude-haiku-4-5-20251001-v1:0"` |
| `api_key` | `str \| SecretStr \| None` | API key (for bearer token auth) | `os.getenv("AWS_BEARER_TOKEN_BEDROCK")` |
| `base_url` | `str \| None` | Custom base URL | Usually `None` for Bedrock |
| `api_version` | `str \| None` | API version | Usually `None` for Bedrock |

### AWS-Specific Parameters

| Parameter | Type | Description | Example |
|-----------|------|-------------|---------|
| `aws_access_key_id` | `str \| SecretStr \| None` | AWS access key ID | `os.getenv("AWS_ACCESS_KEY_ID")` |
| `aws_secret_access_key` | `str \| SecretStr \| None` | AWS secret access key | `os.getenv("AWS_SECRET_ACCESS_KEY")` |
| `aws_region_name` | `str \| None` | AWS region | `"us-east-1"` |

### Performance Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `num_retries` | `int` | `5` | Number of retry attempts |
| `retry_multiplier` | `float` | `8.0` | Retry backoff multiplier |
| `retry_min_wait` | `int` | `8` | Minimum wait between retries (seconds) |
| `retry_max_wait` | `int` | `64` | Maximum wait between retries (seconds) |
| `timeout` | `int \| None` | `None` | HTTP timeout (seconds) |

---

## Model ID Reference

### Available Claude 4.5 Models on Bedrock

| Model | Bedrock ID | Use Case | Cost |
|-------|-----------|----------|------|
| **Claude 4.5 Haiku** | `bedrock/anthropic.claude-haiku-4-5-20251001-v1:0` | Fast operations, extraction, verification | ~$0.25/1M input tokens |
| **Claude 4.5 Sonnet** | `bedrock/anthropic.claude-sonnet-4-5-20250929-v1:0` | Complex reasoning, drafting, critique | ~$3/1M input tokens |

### Model Naming Convention

LiteLLM Bedrock format:
```
bedrock/<model-id>
```

Where `<model-id>` is the full Bedrock model identifier including:
- Provider prefix (e.g., `anthropic`)
- Model name (e.g., `claude-haiku-4-5`)
- Version date (e.g., `20251001`)
- Version suffix (e.g., `v1:0`)

---

## Environment Variables

### Recommended Setup

```bash
# AWS Bedrock Credentials
AWS_REGION_NAME=us-east-1

# Option 1: Bearer Token (Simpler, July 2025+)
AWS_BEARER_TOKEN_BEDROCK=your_bedrock_api_key_here

# Option 2: Traditional IAM Credentials
AWS_ACCESS_KEY_ID=your_access_key_id
AWS_SECRET_ACCESS_KEY=your_secret_access_key
```

### Load in Python

```python
import os
from dotenv import load_dotenv

load_dotenv()  # Load from .env file

# Use in LLM configuration
aws_region = os.getenv("AWS_REGION_NAME", "us-east-1")
aws_bearer_token = os.getenv("AWS_BEARER_TOKEN_BEDROCK")
```

---

## Common Errors & Fixes

### Error 1: "Extra inputs are not permitted" for `provider` field

**Wrong:**
```python
LLM(provider="bedrock", model="...", aws_region="...")
```

**Fix:**
```python
LLM(model="bedrock/...", aws_region_name="...")
```

The `LLM` class doesn't have a `provider` field. Provider is determined by the model name prefix.

### Error 2: "Extra inputs are not permitted" for `aws_region`

**Wrong:**
```python
LLM(model="bedrock/...", aws_region="us-east-1")
```

**Fix:**
```python
LLM(model="bedrock/...", aws_region_name="us-east-1")
```

The parameter name is `aws_region_name`, not `aws_region`.

### Error 3: Model not found

**Wrong:**
```python
LLM(model="anthropic.claude-haiku-4-5-20251001-v1:0", ...)
```

**Fix:**
```python
LLM(model="bedrock/anthropic.claude-haiku-4-5-20251001-v1:0", ...)
```

Always include the `bedrock/` prefix for Bedrock models.

---

## Integration with Ghostwriter Pipeline

### Updated `create_llm()` Method

```python
def create_llm(self, model: str) -> LLM:
    """
    Create LLM instance with Bedrock configuration.

    Args:
        model: Model ID (HAIKU or SONNET constant)

    Returns:
        Configured LLM instance
    """
    # Check if using bearer token or IAM credentials
    bearer_token = os.getenv("AWS_BEARER_TOKEN_BEDROCK")
    access_key = os.getenv("AWS_ACCESS_KEY_ID")
    secret_key = os.getenv("AWS_SECRET_ACCESS_KEY")
    region = os.getenv("AWS_REGION_NAME", "us-east-1")

    if bearer_token:
        # Bearer token auth (simpler)
        return LLM(
            model=f"bedrock/{model}",
            api_key=bearer_token,
            aws_region_name=region
        )
    elif access_key and secret_key:
        # IAM credentials auth
        return LLM(
            model=f"bedrock/{model}",
            aws_access_key_id=access_key,
            aws_secret_access_key=secret_key,
            aws_region_name=region
        )
    else:
        raise ValueError(
            "AWS Bedrock credentials not configured. Set either:\n"
            "  1. AWS_BEARER_TOKEN_BEDROCK (recommended)\n"
            "  2. AWS_ACCESS_KEY_ID + AWS_SECRET_ACCESS_KEY"
        )
```

### Updated Model Constants

```python
class GhostwriterPipeline:
    # AWS Bedrock model IDs for Claude 4.5
    HAIKU = "anthropic.claude-haiku-4-5-20251001-v1:0"  # No prefix here
    SONNET = "anthropic.claude-sonnet-4-5-20250929-v1:0"  # Prefix added in create_llm()
```

---

## Sources & References

### Official Documentation

- [LiteLLM AWS Bedrock Provider Docs](https://docs.litellm.ai/docs/providers/bedrock) - LiteLLM Bedrock configuration
- [OpenHands Software Agent SDK](https://github.com/OpenHands/software-agent-sdk) - Main SDK repository
- [Custom LLM Configurations - OpenHands](https://docs.openhands.dev/openhands/usage/llms/custom-llm-configs) - LLM config reference

### Community Issues & Discussions

- [Stack Overflow: OpenHands with AWS Bedrock](https://stackoverflow.com/questions/79167711/how-to-make-openhands-running-on-docker-on-macos-to-work-with-aws-bedrock) - Docker setup
- [GitHub Issue #755: BedrockException - AWS region not set](https://github.com/All-Hands-AI/OpenHands/issues/755) - Region configuration
- [GitHub Issue #10237: AWS credentials in config.toml](https://github.com/All-Hands-AI/OpenHands/issues/10237) - Credential issues
- [GitHub Issue #15818: Claude Haiku 4.5 on Bedrock](https://github.com/BerriAI/litellm/issues/15818) - Model support
- [LiteLLM Model Aliases](https://aws-samples.github.io/bedrock-litellm/25-config/10-model-alias/) - Model naming conventions

### AWS Documentation

- [AWS Bedrock Supported Models](https://docs.aws.amazon.com/bedrock/latest/userguide/models-supported.html) - Available models
- [Invoke Claude on Bedrock](https://docs.aws.amazon.com/bedrock/latest/userguide/bedrock-runtime_example_bedrock-runtime_InvokeModel_AnthropicClaude_section.html) - API reference

---

## Testing Recommendations

### 1. Test LLM Initialization

```python
from openhands.sdk import LLM
import os

# Test Haiku
try:
    llm_haiku = LLM(
        model="bedrock/anthropic.claude-haiku-4-5-20251001-v1:0",
        aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
        aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
        aws_region_name="us-east-1"
    )
    print("✅ Haiku LLM initialized successfully")
except Exception as e:
    print(f"❌ Haiku LLM initialization failed: {e}")
```

### 2. Test Simple Completion

```python
from openhands.sdk import Agent, Conversation, Tool

agent = Agent(llm=llm_haiku, tools=[Tool(name="FileEditorTool")])
conv = Conversation(agent=agent, workspace="/tmp/test")

conv.send_message("Write 'Hello from Bedrock' to test.txt")
conv.run()

# Check if test.txt was created
```

### 3. Test Cost Optimization

Use Haiku for simple tasks, Sonnet for complex:
- ✅ Haiku: extraction, verification, simple transformations
- ✅ Sonnet: drafting, critique, complex reasoning

---

## Conclusion

The key insight is that **OpenHands SDK delegates to LiteLLM**, so configuration follows LiteLLM conventions:

1. Use `model="bedrock/<model-id>"` format
2. Pass AWS credentials as direct LLM parameters
3. Use `aws_region_name` (not `aws_region`)
4. No separate `provider` field exists

This configuration is now correctly implemented in the Ghostwriter pipeline.
