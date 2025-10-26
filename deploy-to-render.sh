#!/bin/bash

echo "🚀 Deploying Tuxedo to Render from docker-compose.yaml..."

# Check if Render API key is set
if [ -z "$RENDER_API_KEY" ]; then
    echo "❌ RENDER_API_KEY environment variable not set"
    echo "Get your API key from: https://render.com/user/settings"
    exit 1
fi

echo "✅ Render API key found"

# Push to GitHub first (required for Render deployment)
echo "📤 Pushing to GitHub..."
git add .
git commit -m "Add Render deployment configuration"
git push origin main

echo "🌐 Now deploy via Render.com:"
echo "1. Go to https://render.com/dashboard"
echo "2. Click 'New +' → 'Blueprint'"
echo "3. Connect your GitHub repository"
echo "4. Select the repository and branch 'main'"
echo "5. Render will automatically read render.yaml and deploy both services"
echo ""
echo "📋 Required Environment Variables in Render Dashboard:"
echo "- Backend OPENAI_API_KEY (your OpenAI/OpenRouter API key)"
echo "- Backend OPENAI_BASE_URL: https://openrouter.ai/api/v1"
echo ""
echo "🔗 Your app will be available at:"
echo "- Frontend: https://tuxedo.onrender.com"
echo "- Backend: https://tuxedo-backend.onrender.com"
echo "- API Docs: https://tuxedo-backend.onrender.com/docs"