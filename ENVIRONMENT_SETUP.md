# Environment Variables Setup Guide

## Overview

This guide explains how to configure environment variables for Tuxedo AI deployments. The application no longer includes `.env` files in Docker images for security reasons.

## Required Environment Variables

### AI Configuration

- `OPENAI_API_KEY`: Your OpenRouter API key
- `OPENAI_BASE_URL`: API base URL (default: https://openrouter.ai/api/v1)
- `PRIMARY_MODEL`: AI model to use (default: openai/gpt-oss-120b:exacto)

### Stellar Network

- `STELLAR_NETWORK`: Network name (testnet/mainnet)
- `HORIZON_URL`: Stellar Horizon API URL
- `SOROBAN_RPC_URL`: Soroban RPC URL

### Optional

- `DEFINDEX_API_KEY`: DeFindex API key
- `RENDER_API_KEY`: Render API key (if using Render services)
- `PYTHONUNBUFFERED`: Set to 1 for better logging
- `STELLAR_SCAFFOLD_ENV`: Environment (testing/production)

## Deployment Platform Setup

### Render.com

1. **Backend Service Environment Variables:**
   - Go to Render Dashboard → tuxedo-backend → Environment
   - Add the following variables:
     ```
     OPENAI_API_KEY=your_actual_key_here
     OPENAI_BASE_URL=https://openrouter.ai/api/v1
     PRIMARY_MODEL=openai/gpt-oss-120b:exacto
     STELLAR_NETWORK=testnet
     HORIZON_URL=https://horizon-testnet.stellar.org
     SOROBAN_RPC_URL=https://soroban-testnet.stellar.org
     DEFINDEX_API_KEY=your_defindex_key_here
     PYTHONUNBUFFERED=1
     ```

2. **Frontend Service Environment Variables:**
   - Go to Render Dashboard → tuxedo-frontend → Environment
   - Add the following variables:
     ```
     VITE_STELLAR_NETWORK=testnet
     VITE_HORIZON_URL=https://horizon-testnet.stellar.org
     VITE_RPC_URL=https://soroban-testnet.stellar.org
     VITE_API_URL=https://tuxedo-backend.onrender.com
     PUBLIC_API_URL=https://tuxedo-backend.onrender.com
     ```

### Phala Cloud

1. **CLI Environment Variables:**

   ```bash
   phala cvms update -n tuxedo-ai \
     -e OPENAI_API_KEY=your_actual_key_here \
     -e OPENAI_BASE_URL=https://openrouter.ai/api/v1 \
     -e PRIMARY_MODEL=openai/gpt-oss-120b:exacto \
     -e STELLAR_NETWORK=testnet \
     -e HORIZON_URL=https://horizon-testnet.stellar.org \
     -e SOROBAN_RPC_URL=https://soroban-testnet.stellar.org \
     -e DEFINDEX_API_KEY=your_defindex_key_here \
     -e PYTHONUNBUFFERED=1
   ```

2. **Or via Phala Cloud Dashboard:**
   - Go to your CVM → Environment Variables
   - Add the same variables as above

### Local Development

1. **Backend:**

   ```bash
   cp backend/.env.production.template backend/.env
   # Fill in the values in backend/.env
   ```

2. **Frontend:**
   ```bash
   cp .env.example .env.local
   # Fill in the values in .env.local
   ```

## Security Best Practices

### ✅ Do:

- Use platform-specific secret management
- Set environment variables at runtime
- Use different keys for development and production
- Rotate API keys regularly
- Monitor API key usage

### ❌ Don't:

- Commit API keys to git
- Include `.env` files in Docker images
- Share API keys in plain text
- Use production keys in development

## Verification

### Check Environment Variables

```bash
# In running container
phala cvms exec tuxedo-ai -- env | grep OPENAI
```

### Test API Connection

```bash
# Health check should show openai_configured: true
curl https://your-app-url/health
```

## Troubleshooting

### WARNING: OpenAI API key not configured

This means the environment variable isn't set correctly:

1. Check platform environment variables
2. Restart the service
3. Verify health endpoint shows `openai_configured: true`

### Stellar Tools Not Available

Check that Stellar environment variables are set correctly.

### Frontend Can't Connect to Backend

Verify `VITE_API_URL` is set to the correct backend URL.

## Migration from Old Setup

If you're migrating from the old setup that included `.env` files:

1. ✅ Done: Dockerfile no longer includes `.env` files
2. ✅ Done: `.dockerignore` updated to exclude environment files
3. ⚠️ TODO: Add environment variables to your deployment platform
4. ⚠️ TODO: Redeploy services
5. ⚠️ TODO: Remove old `.env` file from repository

## Template Files

- `backend/.env.production.template`: Production environment template
- Use these as references for required variables
- Don't commit actual environment files
