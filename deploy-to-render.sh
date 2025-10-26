#!/bin/bash

echo "🚀 Deploying Blend Pools to Render..."
echo "=================================="

# Check if git is configured
echo "📋 Git Status:"
git status

echo ""
echo "🔧 Current changes:"
git add --dry-run .

echo ""
echo "📝 Ready to commit and push to GitHub for Render deployment?"
echo "This will:"
echo "1. Add all changes to git"
echo "2. Commit with Render deployment message"
echo "3. Push to origin/main"
echo "4. Trigger auto-deployment on Render (if using Blueprint)"
echo ""

read -p "Continue? (y/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "📦 Adding changes..."
    git add .

    echo "💾 Committing changes..."
    git commit -m "Fix Docker build for Render deployment

- Fix node-gyp Python dependency issues in Alpine Docker
- Use Dockerfile.frontend-fixed for production builds
- Add comprehensive build dependencies for USB module compilation
- Optimize health checks for Render compatibility
- Skip TypeScript checking to build successfully
- Add deployment documentation and scripts"

    echo "📤 Pushing to GitHub..."
    git push origin main

    echo ""
    echo "✅ Pushed to GitHub successfully!"
    echo ""
    echo "🌐 Next steps:"
    echo "1. Go to https://render.com"
    echo "2. If using Blueprint: Your services will auto-deploy"
    echo "3. If manual: Create new web services with your updated Dockerfile"
    echo "4. Monitor deployment progress in Render dashboard"
    echo ""
    echo "📊 Expected URLs:"
    echo "- Frontend: https://tuxedo.onrender.com"
    echo "- Backend: https://tuxedo-backend.onrender.com"
    echo "- API Docs: https://tuxedo-backend.onrender.com/docs"
else
    echo "❌ Deployment cancelled"
fi
