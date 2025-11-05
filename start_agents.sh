#!/bin/bash

# Quick start script for LiveKit Voice Agents
# This script helps start all required services

set -e

echo "🚀 Starting LiveKit Voice Agent System"
echo "======================================"
echo ""

# Check if .env exists
if [ ! -f "backend/.env" ]; then
    echo "❌ backend/.env not found!"
    echo "Please create backend/.env with required credentials:"
    echo "  OPENAI_API_KEY=..."
    echo "  LIVEKIT_URL=..."
    echo "  LIVEKIT_API_KEY=..."
    echo "  LIVEKIT_API_SECRET=..."
    exit 1
fi

echo "✅ Environment configuration found"
echo ""

# Function to check if port is in use
check_port() {
    if lsof -Pi :$1 -sTCP:LISTEN -t >/dev/null 2>&1; then
        echo "⚠️  Port $1 is already in use"
        return 1
    fi
    return 0
}

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 not found"
    exit 1
fi

# Check Node
if ! command -v node &> /dev/null; then
    echo "❌ Node.js not found"
    exit 1
fi

echo "Select what to start:"
echo "1) All services (4 terminals)"
echo "2) Backend API only"
echo "3) Agent workers only (dispatcher + driver)"
echo "4) Frontend only"
echo ""
read -p "Enter choice [1-4]: " choice

case $choice in
    1)
        echo ""
        echo "📝 Instructions:"
        echo "You need to open 4 terminals and run:"
        echo ""
        echo "Terminal 1 (Backend API):"
        echo "  cd backend && source .venv/bin/activate && uvicorn src.api.main:app --reload --port 8000"
        echo ""
        echo "Terminal 2 (Dispatcher Agent):"
        echo "  cd backend && source .venv/bin/activate && python agents/dispatcher_agent.py"
        echo ""
        echo "Terminal 3 (Driver Agent):"
        echo "  cd backend && source .venv/bin/activate && python agents/driver_agent.py"
        echo ""
        echo "Terminal 4 (Frontend):"
        echo "  cd frontend && npm run dev"
        echo ""
        ;;
    2)
        cd backend
        source .venv/bin/activate 2>/dev/null || true
        uvicorn src.api.main:app --reload --port 8000
        ;;
    3)
        echo "Starting agent workers..."
        echo "Open a second terminal and run:"
        echo "  cd backend && source .venv/bin/activate && python agents/driver_agent.py"
        echo ""
        cd backend
        source .venv/bin/activate 2>/dev/null || true
        python agents/dispatcher_agent.py
        ;;
    4)
        cd frontend
        npm run dev
        ;;
    *)
        echo "Invalid choice"
        exit 1
        ;;
esac

