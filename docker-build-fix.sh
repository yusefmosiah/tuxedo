#!/bin/bash

# Fix for Docker build issue with node-gyp and USB module
echo "=== Fixing Docker build issue ==="

# Stop any running containers
echo "Stopping any running containers..."
docker stop $(docker ps -q) 2>/dev/null || true

# Clean up Docker cache
echo "Cleaning Docker cache..."
docker system prune -f

# Build with the fixed Dockerfile
echo "Building with fixed Dockerfile..."
docker build -f Dockerfile.frontend-fixed -t blend-pools-frontend . 2>&1 | tee build.log

if [ $? -eq 0 ]; then
    echo "✅ Build successful!"
    echo "Run with: docker run -p 8080:8080 blend-pools-frontend"
else
    echo "❌ Build failed. Check build.log for details."
    echo ""
    echo "Try these additional fixes:"
    echo "1. Delete node_modules and package-lock.json, then npm install"
    echo "2. Use the minimal Dockerfile: docker build -f Dockerfile.frontend-minimal -t blend-pools-frontend ."
    echo "3. Add this to your Dockerfile before npm ci:"
    echo "   RUN apk add --no-cache python3 make g++ linux-headers udev"
    echo "   RUN npm config set python /usr/bin/python3"
fi