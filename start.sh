#!/bin/bash
# Quick Start Script for AI Chatbot

echo "🚀 Starting Enterprise Solutions AI Chatbot..."
echo ""

# Check if .env file exists
if [ ! -f "backend/.env" ]; then
    echo "❌ ERROR: backend/.env file not found!"
    echo "Please create backend/.env with your API keys"
    exit 1
fi

# Check for required environment variables
source backend/.env 2>/dev/null

if [ -z "$DATABASE_URL" ]; then
    echo "❌ ERROR: DATABASE_URL not set in .env"
    exit 1
fi

if [ -z "$OPENAI_API_KEY" ]; then
    echo "⚠️  WARNING: OPENAI_API_KEY not set - AI chatbot will not work"
    echo "Set OPENAI_API_KEY in backend/.env to enable AI features"
fi

echo "✅ Configuration looks good!"
echo ""

# Start backend
echo "📦 Starting Backend Server..."
cd backend
pip install -r requirements.txt -q 2>/dev/null || echo "⚠️  Install dependencies: pip install -r requirements.txt"
python main.py &
BACKEND_PID=$!
echo "✅ Backend started (PID: $BACKEND_PID)"
echo ""

# Wait for backend to start
sleep 3

# Start frontend
echo "🎨 Starting Frontend Server..."
cd ../frontend
npm install 2>/dev/null || echo "⚠️  Install dependencies: npm install"
npm run dev &
FRONTEND_PID=$!
echo "✅ Frontend started (PID: $FRONTEND_PID)"
echo ""

echo "======================================"
echo "🎉 All services started!"
echo "======================================"
echo ""
echo "📍 Frontend: http://localhost:3000/dashboard/company"
echo "📍 Backend API: http://localhost:8000/docs"
echo ""
echo "Press Ctrl+C to stop all services"
echo ""

# Wait for Ctrl+C
trap "kill $BACKEND_PID $FRONTEND_PID; exit" INT
wait
