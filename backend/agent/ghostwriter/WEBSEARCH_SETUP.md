# WebSearch Setup for Ghostwriter Pipeline

This document explains how to configure web search capabilities for the Ghostwriter research pipeline.

## Overview

The Ghostwriter pipeline uses **Tavily API** for web research. Tavily is specifically optimized for AI research tasks and provides:

- ✅ Authoritative, structured search results
- ✅ Automatic source verification and relevance scoring
- ✅ Content extraction from search results
- ✅ Academic, news, and documentation source types

## Setup Instructions

### 1. Get Tavily API Key

1. Visit https://app.tavily.com/
2. Sign up for an account
3. Navigate to API Keys section
4. Copy your API key

**Note**: Tavily offers a generous free tier for testing and development.

### 2. Add API Key to Environment

Edit `/home/user/tuxedo/backend/.env`:

```bash
# Web Search API Configuration (for Ghostwriter research)
TAVILY_API_KEY=tvly-XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
```

**Important**: Never commit your API key to git. The `.env` file is gitignored.

### 3. Verify Setup

Run the test suite to verify WebSearch is working:

```bash
cd /home/user/tuxedo/backend
source .venv/bin/activate
python test_websearch.py
```

Expected output:
```
✅ Tavily API key found: tvly-XXX...XXXX
✅ WebSearch successful!
✅ CLI tool test passed!
🎉 All tests passed! WebSearch is ready for Ghostwriter.
```

## Architecture

### Components

1. **openhands_websearch.py** - Core WebSearch executor using Tavily API
2. **websearch_cli.py** - CLI tool that researchers call via TerminalTool
3. **Integration** - Researchers use TerminalTool to execute searches

### How Researchers Use WebSearch

Researchers execute searches using the CLI tool via TerminalTool:

```bash
python3 -m agent.ghostwriter.websearch_cli "DeFi yield farming strategies" --max-results 5
```

The CLI tool:
1. Takes the search query as input
2. Calls Tavily API with appropriate parameters
3. Formats results for agent consumption
4. Returns structured markdown with URLs, titles, content, and scores

### Example Search Results

```
Search Results for: DeFi yield farming strategies

Found 5 authoritative sources:

============================================================
Result #1
============================================================
Title: Understanding DeFi Yield Farming in 2025
URL: https://example.com/defi-yield-farming
Relevance Score: 0.95
Published: 2025-01-15

Content Summary:
Yield farming has become one of the most popular ways to earn passive income
in decentralized finance (DeFi). This comprehensive guide covers...
```

## Alternative: Brave Search API

If you prefer Brave Search instead of Tavily:

1. Uncomment `BRAVE_SEARCH_API_KEY` in `.env`
2. Get API key from https://brave.com/search/api/
3. Modify `openhands_websearch.py` to use Brave API endpoint

**Why Tavily is recommended**:
- Optimized for AI research tasks
- Returns pre-structured results
- Better source verification
- Designed for LLM consumption

## Testing

### Quick Test

```bash
cd backend
source .venv/bin/activate
python -m agent.ghostwriter.websearch_cli "Stellar blockchain" --max-results 3
```

### Full Integration Test

```bash
cd backend
source .venv/bin/activate
python test_websearch.py
```

### Run Ghostwriter Pipeline

```bash
cd backend
source .venv/bin/activate
python -m agent.ghostwriter.test_pipeline
```

## Troubleshooting

### Error: TAVILY_API_KEY not found

**Solution**: Make sure your `.env` file is in `/home/user/tuxedo/backend/.env` and contains:
```
TAVILY_API_KEY=your_actual_key_here
```

### Error: Module not found

**Solution**: Make sure you're running from the backend directory:
```bash
cd /home/user/tuxedo/backend
python -m agent.ghostwriter.websearch_cli "query"
```

### Error: Search timeout

**Solution**: Check your internet connection and try with a simpler query first.

### Error: API rate limit exceeded

**Solution**: Tavily free tier has rate limits. Upgrade your plan or wait for the limit to reset.

## Cost Estimates

### Tavily API Pricing (as of 2025)

- **Free Tier**: 1,000 searches/month
- **Pro Tier**: $X/month for X,000 searches

### Ghostwriter Pipeline Usage

For a typical research report:
- 5 researchers × 5 searches each = **25 searches per report**
- Free tier allows ~40 reports/month
- Pro tier allows hundreds of reports/month

## API Documentation

- **Tavily Docs**: https://docs.tavily.com/
- **Tavily Python SDK**: https://github.com/tavily-ai/tavily-python
- **OpenHands SDK**: https://docs.openhands.dev/

## Security

- ✅ API keys are stored in `.env` (gitignored)
- ✅ Never log full API keys (only first/last chars)
- ✅ Use environment variables, never hardcode keys
- ✅ Rotate keys periodically for production use

## Next Steps

After WebSearch is configured:

1. ✅ Run test suite to verify setup
2. ✅ Test individual CLI searches
3. ✅ Run full Ghostwriter pipeline test
4. ✅ Generate sample research report
5. ✅ Monitor API usage and costs

---

**Questions?** Check the main Ghostwriter documentation: `docs/GHOSTWRITER_ARCHITECTURE_OPENHANDS_SDK.md`
