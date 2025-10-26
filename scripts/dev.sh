#!/bin/bash

# Tuxedo Development Environment Launcher
# Starts all services: MCP server, FastAPI backend, and React frontend

set -e

echo "🚀 Starting Tuxedo AI development environment..."

# Check if we're in the right directory
if [ ! -d "backend" ] || [ ! -d "src" ]; then
    echo "❌ Error: Please run this script from the root of the tuxedo project"
    exit 1
fi

# Function to cleanup background processes
cleanup() {
    echo "🧹 Cleaning up background processes..."
    jobs -p | xargs -r kill
    exit 0
}

# Trap Ctrl+C to cleanup
trap cleanup SIGINT SIGTERM

# Start FastAPI Backend (port 8001)
echo "📦 Starting FastAPI backend..."
cd backend
source .venv/bin/activate
python main.py &
BACKEND_PID=$!
echo "✅ Backend started on http://localhost:8001 (PID: $BACKEND_PID)"

# Start React Frontend (port 5173)
echo "⚛️ Starting React frontend..."
cd ..
npm run dev &
FRONTEND_PID=$!
echo "✅ Frontend started on http://localhost:5173 (PID: $FRONTEND_PID)"

# Wait for both services
echo ""
echo "🎉 All services started!"
echo "📱 Frontend: http://localhost:5173"
echo "🔧 Backend API: http://localhost:8001"
echo "📊 Backend docs: http://localhost:8001/docs"
echo ""
echo "Press Ctrl+C to stop all services"

# Wait for background jobs
wait $BACKEND_PID $FRONTEND_PID