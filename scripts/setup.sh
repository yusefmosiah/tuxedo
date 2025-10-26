#!/bin/bash

# Tuxedo Project Setup Script
# One-time setup for the entire development environment

set -e

echo "🔧 Setting up Tuxedo AI development environment..."

# Check if uv is installed
if ! command -v uv &> /dev/null; then
    echo "📦 Installing uv..."
    curl -LsSf https://astral.sh/uv/install.sh | sh
    source $HOME/.local/bin/env
else
    echo "✅ uv already installed"
fi

# Setup Python backend
echo "🐍 Setting up Python backend..."
cd backend

# Create virtual environment if it doesn't exist
if [ ! -d ".venv" ]; then
    echo "📦 Creating Python virtual environment..."
    uv venv
fi

# Install dependencies
echo "📦 Installing Python dependencies..."
source .venv/bin/activate
uv sync

echo "✅ Backend setup complete"

# Setup frontend dependencies
echo "⚛️ Setting up frontend..."
cd ..
npm install

echo "✅ Frontend setup complete"

# Create development environment file if it doesn't exist
if [ ! -f ".env" ]; then
    echo "📝 Creating .env file from template..."
    cp .env.example .env
    echo "⚠️  Please edit .env file with your API keys"
fi

echo ""
echo "🎉 Setup complete!"
echo ""
echo "Next steps:"
echo "1. Edit .env file with your API keys"
echo "2. Run: ./scripts/dev.sh"
echo ""
echo "Services will be available at:"
echo "- Frontend: http://localhost:5173"
echo "- Backend: http://localhost:8001"
echo "- API Docs: http://localhost:8001/docs"