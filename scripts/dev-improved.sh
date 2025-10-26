#!/bin/bash

# Tuxedo Development Environment Launcher - Parallel Architecture
# Starts FastAPI backend + py-stellar-mcp + React frontend
# Clean separation: parallel directories, no git nesting

set -e

echo "🚀 Starting Tuxedo AI development environment (Parallel Architecture)..."

# Check if we're in right directory
if [ ! -d "backend" ] || [ ! -d "src" ]; then
    echo "❌ Error: Please run this script from root of tuxedo project"
    exit 1
fi

# Function to cleanup background processes
cleanup() {
    echo "🧹 Cleaning up background processes..."
    jobs -p | xargs -r kill 2>/dev/null || true
    exit 0
}

# Trap Ctrl+C to cleanup
trap cleanup SIGINT SIGTERM

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}📋 Service Architecture:${NC}"
echo "┌─────────────────────────────────────────────────┐"
echo "│ ${GREEN}React Frontend${NC}    │ ${BLUE}FastAPI Backend${NC}    │ ${YELLOW}MCP Server${NC} │"
echo "│ ${GREEN}(Port 5173)${NC}    │ ${BLUE}(Port 8002)${NC}    │ ${YELLOW}(Port 8003)${NC} │"
echo "└─────────────────────────────────────────────────┘"
echo ""

# Start py-stellar-mcp server (Port 8003)
echo -e "${YELLOW}🔧 Starting py-stellar-mcp server...${NC}"
cd py-stellar-mcp

# Check if py-stellar-mcp needs setup
if [ ! -f "requirements.txt" ]; then
    echo -e "${RED}⚠️  py-stellar-mcp requirements.txt not found${NC}"
    echo "Installing dependencies..."
    pip install -r requirements.txt
fi

# Start py-stellar-mcp server
python -m stellar_mcp.server &
MCP_PID=$!
echo -e "${GREEN}✅ py-stellar-mcp server started (PID: $MCP_PID)${NC}"

# Start FastAPI Backend (Port 8002)
echo -e "${BLUE}📦 Starting FastAPI backend...${NC}"
cd backend
source .venv/bin/activate
python main.py &
BACKEND_PID=$!
echo -e "${GREEN}✅ FastAPI backend started (PID: $BACKEND_PID)${NC}"

# Start React Frontend (Port 5173)
echo -e "${GREEN}⚛️ Starting React frontend...${NC}"
cd ..
npm run dev &
FRONTEND_PID=$!
echo -e "${GREEN}✅ React frontend started (PID: $FRONTEND_PID)${NC}"

# Wait for both services
echo ""
echo -e "${GREEN}🎉 All services started!${NC}"
echo ""
echo -e "${BLUE}📱 Frontend:${NC} ${GREEN} http://localhost:5173${NC}"
echo -e "${BLUE}🔧 Backend API:${NC} ${GREEN} http://localhost:8002${NC}"
echo -e "${BLUE}📊 Backend Docs:${NC} ${GREEN} http://localhost:8002/docs${NC}"
echo -e "${YELLOW}🔧 MCP Server:${NC} ${GREEN} http://localhost:8003${NC}"
echo ""
echo -e "${BLUE}Press Ctrl+C to stop all services${NC}"

# Function to check if services are still running
check_services() {
    echo -e "\n${BLUE}🔍 Checking service status...${NC}"

    # Check MCP server
    if ps -p $MCP_PID > /dev/null; then
        echo -e "${GREEN}  ✅ py-stellar-mcp: Running${NC}"
    else
        echo -e "${RED}  ❌ py-stellar-mcp: Not running${NC}"
    fi

    # Check FastAPI backend
    if ps -p $BACKEND_PID > /dev/null; then
        echo -e "${GREEN}  ✅ FastAPI: Running${NC}"
        # Test API health
        if curl -s http://localhost:8002/health > /dev/null 2>&1; then
            echo -e "${GREEN}  ✅ API Health: OK${NC}"
        else
            echo -e "${YELLOW}  ⚠️  API Health: Check failed${NC}"
        fi
    else
        echo -e "${RED}  ❌ FastAPI: Not running${NC}"
    fi

    # Check React frontend
    if ps -p $FRONTEND_PID > /dev/null; then
        echo -e "${GREEN}  ✅ Frontend: Running${NC}"
    else
        echo -e "${RED}  ❌ Frontend: Not running${NC}"
    fi
}

# Monitor services
while true; do
    check_services
    sleep 10
done