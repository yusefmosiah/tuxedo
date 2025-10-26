# Render Deployment Guide

## Quick Setup

### 1. Create Render Account
1. Go to [render.com](https://render.com)
2. Sign up with GitHub (easiest option)
3. Verify your email

### 2. Create API Key
1. Go to Dashboard → Settings → API Keys
2. Click "Create API Key"
3. Name it: "Tuxedo Deployment"
4. Copy the key (you'll need it for MCP)

### 3. Configure MCP Server
```bash
# Set your Render API key
export RENDER_API_KEY="your_api_key_here"

# Test MCP connection
claude mcp list
```

### 4. Deploy Using MCP

Once MCP is authenticated, you can deploy using these MCP tools:

- **Services**: Create and manage web services
- **Environment Variables**: Configure app settings
- **Deployments**: Trigger and monitor deployments
- **Logs**: View application logs

### 5. Alternative: Manual Deploy via GitHub

#### Option A: Connect GitHub Repo
1. Push your code to GitHub
2. In Render Dashboard → "New +"
3. Select "Web Service"
4. Connect your GitHub repository
5. Select branch: `main`
6. Runtime: Docker
7. Build Command: `docker-compose build`
8. Start Command: `docker-compose up`
9. Add environment variables:
   - `OPENAI_API_KEY` (your OpenAI API key)
   - `OPENAI_BASE_URL`: `https://openrouter.ai/api/v1`
   - `OPENAI_API_KEY`: `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`

#### Option B: Use render.yaml (Recommended)
1. Copy `render.yaml` to your repository root
2. Push to GitHub
3. In Render: "New+" → "Blueprint"
4. Connect your repository
5. Render will automatically create both services

## Environment Variables Required

### Backend Environment Variables
- `OPENAI_API_KEY`: Your OpenAI API key (required)
- `OPENAI_BASE_URL`: `https://openrouter.ai/api/v1`
- `STELLAR_NETWORK`: `testnet`
- `HORIZON_URL`: `https://horizon-testnet.stellar.org`
- `SOROBAN_RPC_URL`: `https://soroban-testnet.stellar.org`

### Frontend Environment Variables
- `VITE_STELLAR_NETWORK`: `testnet`
- `VITE_HORIZON_URL`: `https://horizon-testnet.stellar.org`
- `VITE_RPC_URL`: `https://soroban-testnet.stellar.org`
- `VITE_API_URL`: `https://your-backend-url.onrender.com`

## Deployment URLs

Once deployed, your app will be available at:
- Frontend: `https://tuxedo.onrender.com`
- Backend: `https://tuxedo-backend.onrender.com`
- API Docs: `https://tuxedo-backend.onrender.com/docs`

## Troubleshooting

### Common Issues
1. **Build Failures**: Check that Dockerfile paths are correct
2. **API Key Errors**: Ensure OPENAI_API_KEY is set correctly
3. **CORS Issues**: Frontend can't reach backend - check API URL
4. **Cold Starts**: First load may be slow on free tier

### Using MCP to Debug
Once MCP is configured, you can:
- Check deployment status
- View service logs
- Update environment variables
- Restart services

## Next Steps After Deployment

1. **Test the Application**
   - Visit your frontend URL
   - Connect wallet
   - Try AI chat functionality

2. **Monitor Health**
   - Check service logs in Render dashboard
   - Monitor free tier usage

3. **Scale if Needed**
   - Upgrade from free tier for better performance
   - Add custom domains