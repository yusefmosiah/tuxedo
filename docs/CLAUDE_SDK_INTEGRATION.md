# Claude Agent SDK Integration

**Status**: ✅ Complete (2025-11-20)
**Version**: 1.0
**Integration Type**: Hybrid (Claude SDK + LangChain)

## Overview

Tuxedo now features a **hybrid agent system** that combines:

1. **LangChain** - For blockchain tool execution (Stellar, Blend Capital, Vault operations)
2. **Claude Agent SDK** - For advanced research, analysis, and reasoning

This approach provides the best of both worlds:

- Proven blockchain integrations remain intact
- New research and analysis capabilities added
- Gradual migration path available if desired

## Architecture

### System Components

```
┌─────────────────────────────────────────────────────────────┐
│                    Tuxedo Backend                            │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌──────────────────────┐    ┌──────────────────────────┐  │
│  │   LangChain Agent    │    │  Claude SDK Agent        │  │
│  │   (agent/core.py)    │    │  (agent/claude_sdk_      │  │
│  │                      │    │   wrapper.py)            │  │
│  ├──────────────────────┤    ├──────────────────────────┤  │
│  │ 19 Blockchain Tools  │    │ Research & Analysis      │  │
│  │ • Stellar (6 tools)  │    │ • Strategy Analysis      │  │
│  │ • Blend (6 tools)    │    │ • Yield Research         │  │
│  │ • Vault (7 tools)    │    │ • Report Generation      │  │
│  │ • Real-time ops      │    │ • Web Search             │  │
│  └──────────────────────┘    └──────────────────────────┘  │
│           │                            │                     │
│           └────────────┬───────────────┘                     │
│                        │                                     │
│              ┌─────────▼──────────┐                         │
│              │   FastAPI Routes   │                         │
│              │  • /chat           │                         │
│              │  • /api/claude-sdk │                         │
│              └────────────────────┘                         │
└─────────────────────────────────────────────────────────────┘
```

### When to Use Which System

**Use LangChain (`/chat` endpoint):**

- Executing blockchain transactions
- Checking balances and positions
- Managing vault deposits/withdrawals
- Real-time DeFi operations
- Multi-step blockchain workflows

**Use Claude SDK (`/api/claude-sdk/*` endpoints):**

- Strategy research and brainstorming
- Market analysis and insights
- Performance report generation
- Risk assessment
- Complex reasoning without blockchain execution

## Installation & Setup

### 1. Install Dependencies

Already done! Claude SDK was added via UV:

```bash
cd backend
uv add claude-agent-sdk
```

### 2. Configure Authentication

Claude SDK supports **three authentication methods**:

#### Option A: Direct Anthropic API (Recommended for Getting Started)

Add to your `backend/.env` file:

```bash
# Claude SDK Configuration
ANTHROPIC_API_KEY=your_anthropic_api_key_here
ENABLE_CLAUDE_SDK=true
```

Get your API key from: https://console.anthropic.com/

#### Option B: AWS Bedrock with API Key (Recommended for Production)

Add to your `backend/.env` file:

```bash
# Claude SDK Configuration - AWS Bedrock
CLAUDE_SDK_USE_BEDROCK=true
ENABLE_CLAUDE_SDK=true

# AWS Bedrock API Key (simpler method, July 2025+)
AWS_BEARER_TOKEN_BEDROCK=your_bedrock_api_key
AWS_REGION=us-east-1
```

**Benefits of this method:**

- Single-key authentication (no IAM complexity)
- Simpler setup than traditional IAM
- Enterprise billing and governance
- Regional data residency

#### Option C: AWS Bedrock with IAM Credentials (Traditional)

Add to your `backend/.env` file:

```bash
# Claude SDK Configuration - AWS Bedrock
CLAUDE_SDK_USE_BEDROCK=true
ENABLE_CLAUDE_SDK=true

# AWS IAM Credentials
AWS_REGION=us-east-1
AWS_ACCESS_KEY_ID=your_aws_access_key_id
AWS_SECRET_ACCESS_KEY=your_aws_secret_access_key
```

**Benefits of AWS Bedrock:**

- Enterprise billing and governance
- IAM role-based authentication (for production)
- Integrated with AWS services
- Regional data residency
- Reserved capacity options

**See detailed setup guide:** [AWS_BEDROCK_CONFIGURATION.md](./AWS_BEDROCK_CONFIGURATION.md)

**Note**: Claude SDK features work without authentication in limited mode, but full functionality requires either Anthropic API key or AWS Bedrock credentials.

### 3. Verify Installation

Run the integration test:

```bash
cd backend
.venv/bin/python3 test_claude_sdk_integration.py
```

Expected output:

```
✅ Integration test completed!
```

## API Endpoints

All Claude SDK endpoints are available at `/api/claude-sdk/*`:

### 1. Simple Query

**POST** `/api/claude-sdk/query`

General-purpose query endpoint for research and analysis.

**Request:**

```json
{
  "prompt": "What are the risks of yield farming on Stellar?"
}
```

**Response:**

```json
{
  "success": true,
  "data": {
    "response": "Yield farming on Stellar carries several risks..."
  }
}
```

### 2. Strategy Analysis

**POST** `/api/claude-sdk/analyze-strategy`

Comprehensive DeFi strategy analysis with risk assessment.

**Request:**

```json
{
  "strategy_description": "Supply USDC to Blend Capital and stake BLND tokens",
  "market_context": {
    "usdc_supply_apy": "8.5%",
    "blnd_staking_apy": "15%"
  }
}
```

**Response:**

```json
{
  "success": true,
  "data": {
    "strategy": "Supply USDC to Blend...",
    "analysis": "## Risk Assessment\n...",
    "market_context": {...}
  }
}
```

### 3. Yield Research

**POST** `/api/claude-sdk/research-yield`

Research current yield opportunities across Stellar DeFi.

**Request:**

```json
{
  "asset": "USDC",
  "min_apy": 5.0
}
```

**Response:**

```json
{
  "success": true,
  "data": {
    "asset": "USDC",
    "min_apy": 5.0,
    "research": "## Top Yield Opportunities\n..."
  }
}
```

### 4. Generate Report

**POST** `/api/claude-sdk/generate-report`

Create comprehensive performance reports.

**Request:**

```json
{
  "user_positions": [
    {
      "protocol": "Blend Capital",
      "asset": "USDC",
      "amount": 1000,
      "apy": 8.5
    }
  ],
  "performance_data": {
    "total_invested": 1000,
    "current_value": 1085,
    "roi": 8.5
  }
}
```

**Response:**

```json
{
  "success": true,
  "data": {
    "report": "# Performance Report\n...",
    "positions_analyzed": 1
  }
}
```

### 5. Status Check

**GET** `/api/claude-sdk/status`

Check Claude SDK integration status.

**Response:**

```json
{
  "success": true,
  "data": {
    "enabled": true,
    "api_key_configured": true,
    "features": [
      "simple_query",
      "strategy_analysis",
      "yield_research",
      "report_generation"
    ],
    "status": "ready"
  }
}
```

## Python Usage Examples

### Direct Agent Usage

```python
from agent.claude_sdk_wrapper import get_claude_sdk_agent

# Create agent
agent = await get_claude_sdk_agent()

# Simple query
result = await agent.query_simple(
    "What are the best yield strategies on Stellar?"
)
print(result)

# Strategy analysis
analysis = await agent.analyze_strategy(
    strategy_description="Supply USDC to Blend and stake BLND",
    market_context={
        "usdc_apy": "8.5%",
        "blnd_apy": "15%"
    }
)
print(analysis['analysis'])

# Yield research
research = await agent.research_yield_opportunities(
    asset="USDC",
    min_apy=5.0
)
print(research['research'])
```

### HTTP API Usage

```python
import httpx

async with httpx.AsyncClient() as client:
    # Strategy analysis
    response = await client.post(
        "http://localhost:8000/api/claude-sdk/analyze-strategy",
        json={
            "strategy_description": "Supply USDC to Blend",
            "market_context": {"usdc_apy": "8.5%"}
        }
    )
    data = response.json()
    print(data['data']['analysis'])
```

## Frontend Integration

### Example React Hook

```typescript
// hooks/useClaudeSDK.ts
import { useState } from "react";
import axios from "axios";

export function useClaudeSDK() {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const analyzeStrategy = async (
    description: string,
    context?: Record<string, any>,
  ) => {
    setLoading(true);
    setError(null);

    try {
      const response = await axios.post("/api/claude-sdk/analyze-strategy", {
        strategy_description: description,
        market_context: context,
      });
      return response.data.data;
    } catch (err) {
      setError(err.message);
      throw err;
    } finally {
      setLoading(false);
    }
  };

  const researchYield = async (asset: string, minApy: number = 0) => {
    setLoading(true);
    setError(null);

    try {
      const response = await axios.post("/api/claude-sdk/research-yield", {
        asset,
        min_apy: minApy,
      });
      return response.data.data;
    } catch (err) {
      setError(err.message);
      throw err;
    } finally {
      setLoading(false);
    }
  };

  return {
    analyzeStrategy,
    researchYield,
    loading,
    error,
  };
}
```

### Example Component

```typescript
// components/StrategyAnalyzer.tsx
import { useClaudeSDK } from '@/hooks/useClaudeSDK';

export function StrategyAnalyzer() {
  const { analyzeStrategy, loading } = useClaudeSDK();
  const [analysis, setAnalysis] = useState('');

  const handleAnalyze = async () => {
    const result = await analyzeStrategy(
      'Supply USDC to Blend Capital',
      { usdc_apy: '8.5%' }
    );
    setAnalysis(result.analysis);
  };

  return (
    <div>
      <button onClick={handleAnalyze} disabled={loading}>
        Analyze Strategy
      </button>
      {analysis && <Markdown>{analysis}</Markdown>}
    </div>
  );
}
```

## File Structure

New files added for Claude SDK integration:

```
backend/
├── agent/
│   └── claude_sdk_wrapper.py          # Claude SDK wrapper
├── api/
│   └── routes/
│       └── claude_sdk.py               # API endpoints
├── config/
│   └── settings.py                     # Updated with Claude SDK config
├── test_claude_sdk_integration.py      # Integration test
└── .env.example                        # Updated with API key config

docs/
└── CLAUDE_SDK_INTEGRATION.md           # This file
```

## Configuration Options

All configuration in `backend/config/settings.py`:

```python
class Settings:
    # Claude SDK Configuration
    anthropic_api_key: str              # Anthropic API key
    enable_claude_sdk: bool             # Enable/disable Claude SDK
```

Environment variables:

```bash
ANTHROPIC_API_KEY=sk-ant-...           # Required for full functionality
ENABLE_CLAUDE_SDK=true                 # Default: true
```

## Testing

### Unit Tests

```bash
cd backend
.venv/bin/python3 test_claude_sdk_integration.py
```

### Integration Tests

Start the backend and test endpoints:

```bash
# Terminal 1: Start backend
.venv/bin/python3 main.py

# Terminal 2: Test endpoints
curl -X POST http://localhost:8000/api/claude-sdk/query \
  -H "Content-Type: application/json" \
  -d '{"prompt": "What is Stellar?"}'

# Check status
curl http://localhost:8000/api/claude-sdk/status
```

### API Documentation

Visit http://localhost:8000/docs when backend is running to see interactive API documentation with all Claude SDK endpoints.

## Advanced Features

### Custom Tools

The Claude SDK wrapper supports custom tools via the `allowed_tools` parameter:

```python
agent = ClaudeSDKAgent(
    allowed_tools=["Read", "Write", "WebSearch", "Bash", "CustomTool"]
)
```

### Working Directory

Control where file operations occur:

```python
agent = ClaudeSDKAgent(
    working_directory="/path/to/research"
)
```

### Direct SDK Usage

For advanced use cases, use the Claude SDK directly:

```python
from claude_agent_sdk import query, ClaudeAgentOptions

options = ClaudeAgentOptions(
    allowed_tools=["Read", "Write"],
    permission_mode='acceptEdits',
    cwd=os.getcwd()
)

async for message in query(
    prompt="Research Stellar DeFi",
    options=options
):
    print(message)
```

## Migration Path

If you want to gradually migrate from LangChain to Claude SDK:

1. **Phase 1** (Current): Hybrid system - both active
2. **Phase 2**: Migrate non-blockchain tools to Claude SDK
3. **Phase 3**: Create Claude SDK wrappers for blockchain tools
4. **Phase 4**: Full Claude SDK migration (if desired)

**Current Recommendation**: Keep the hybrid approach - it provides the best of both worlds.

## Troubleshooting

### API Key Issues

**Problem**: "ANTHROPIC_API_KEY not set"
**Solution**: Add API key to `.env` file:

```bash
ANTHROPIC_API_KEY=sk-ant-your-key-here
```

### Import Errors

**Problem**: "ModuleNotFoundError: No module named 'claude_agent_sdk'"
**Solution**: Reinstall dependencies:

```bash
cd backend
uv sync
```

### Permission Errors

**Problem**: File operations failing
**Solution**: Check working directory permissions:

```python
agent = ClaudeSDKAgent(working_directory="/writable/path")
```

### Rate Limiting

**Problem**: API rate limit errors
**Solution**: Implement retry logic or reduce request frequency

## Performance Considerations

- **Claude SDK** is optimized for reasoning tasks, not blockchain execution
- **LangChain** remains faster for simple tool calls
- **Hybrid approach** uses each system for its strengths
- **Caching**: Consider implementing response caching for frequently asked research questions

## Security Notes

1. **API Keys**: Never commit API keys to version control
2. **Environment Variables**: Use `.env` files (gitignored)
3. **Production**: Use secrets management (Render.com secrets, AWS Secrets Manager, etc.)
4. **File Access**: Claude SDK has file system access - use `allowed_tools` to restrict

## Cost Optimization

Claude SDK API calls incur costs:

- **Simple queries**: ~$0.001-0.005 per query
- **Complex analysis**: ~$0.01-0.05 per analysis
- **Reports**: ~$0.05-0.10 per report

**Optimization strategies**:

1. Cache responses for common queries
2. Use LangChain for simple operations
3. Reserve Claude SDK for complex reasoning
4. Implement request rate limiting
5. Monitor usage via Anthropic console

## Future Enhancements

Potential improvements:

1. **Streaming responses** for better UX
2. **Custom tools** for Stellar-specific research
3. **Multi-agent workflows** (research → execute → verify)
4. **Conversation history** across Claude SDK calls
5. **Frontend integration** with dedicated UI components

## Related Documentation

- [Agent SDK Research](./AGENT_SDK_RESEARCH_AND_RECOMMENDATIONS.md) - Original research comparing SDKs
- [CLAUDE.md](../CLAUDE.md) - Main project documentation
- [Claude SDK Official Docs](https://docs.anthropic.com/claude/docs/agent-sdk)

## Support

For issues or questions:

1. Check this documentation
2. Review test file: `backend/test_claude_sdk_integration.py`
3. Check logs: Look for "Claude SDK" in backend logs
4. API Docs: http://localhost:8000/docs (when backend running)

## Changelog

### v1.0 (2025-11-20)

- ✅ Initial Claude SDK integration
- ✅ Hybrid architecture with LangChain
- ✅ 5 API endpoints added
- ✅ Configuration support
- ✅ Integration testing
- ✅ Documentation complete

---

**Last Updated**: 2025-11-20
**Status**: Production Ready
**Next Steps**: Add ANTHROPIC_API_KEY and start using `/api/claude-sdk` endpoints!
