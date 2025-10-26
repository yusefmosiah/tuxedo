# Tuxedo Backend

FastAPI + FastMCP backend for Tuxedo AI - conversational DeFi assistant for Stellar.

## Quick Start

```bash
# Install dependencies
uv sync

# Run development server
uv run python main.py

# Or run with uvicorn
uv run uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

## Environment Variables

Copy `.env.example` to `.env` and configure:

- `OPENAI_API_KEY`: Your OpenAI or RedPill API key
- `OPENAI_BASE_URL`: API base URL (defaults to OpenAI)
- `DEBUG`: Enable debug mode

## API Endpoints

- `GET /health`: Health check
- `POST /chat`: Chat with AI assistant

## FastMCP Tools

The backend exposes Stellar-related tools through FastMCP:

- `get_blend_pools`: Get all active Blend pools
- `get_account_info`: Get account information
- `calculate_risk_score`: Calculate risk metrics