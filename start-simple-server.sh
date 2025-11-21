#!/bin/bash

# Start Simple Server with Google OAuth Support
# This script starts both backend and frontend servers

echo "============================================"
echo "🚀 Starting AI-HR Platform (Simple Server)"
echo "============================================"
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed"
    echo "Please install Python 3 and try again"
    exit 1
fi

# Check if Node is installed
if ! command -v node &> /dev/null; then
    echo "❌ Node.js is not installed"
    echo "Please install Node.js and try again"
    exit 1
fi

echo "✅ Python 3 found: $(python3 --version)"
echo "✅ Node.js found: $(node --version)"
echo ""

# Install Python dependencies
echo "📦 Installing Python dependencies..."
pip install -q fastapi uvicorn python-jose 2>/dev/null || {
    echo "⚠️  Some Python packages may already be installed"
}

# Check if frontend dependencies are installed
if [ ! -d "frontend/node_modules" ]; then
    echo "📦 Installing frontend dependencies..."
    cd frontend && npm install && cd ..
fi

echo ""
echo "============================================"
echo "🎯 Starting Servers"
echo "============================================"
echo ""

# Start backend server in background
echo "🔧 Starting backend server on port 8000..."
cd backend
python3 simple_server.py &
BACKEND_PID=$!
cd ..

# Wait for backend to start
sleep 2

# Check if backend started successfully
if ps -p $BACKEND_PID > /dev/null; then
    echo "✅ Backend server started (PID: $BACKEND_PID)"
else
    echo "❌ Failed to start backend server"
    exit 1
fi

# Start frontend server in background
echo "🎨 Starting frontend server on port 3000..."
cd frontend
npm run dev &
FRONTEND_PID=$!
cd ..

# Wait for frontend to start
sleep 3

echo ""
echo "============================================"
echo "✅ Servers Running!"
echo "============================================"
echo ""
echo "📍 Backend API:  http://localhost:8000"
echo "📍 API Docs:     http://localhost:8000/docs"
echo "📍 Frontend:     http://localhost:3000"
echo ""
echo "============================================"
echo "🔐 Authentication Features"
echo "============================================"
echo ""
echo "✅ Email/Password Login"
echo "✅ Email/Password Registration"
echo "✅ Google OAuth (Mock for Testing)"
echo "✅ Session Persistence"
echo "✅ JWT Tokens"
echo ""
echo "============================================"
echo "📝 Quick Test"
echo "============================================"
echo ""
echo "1. Open: http://localhost:3000/auth/login"
echo "2. Click 'Sign in with Google'"
echo "3. Use pre-filled test data"
echo "4. You're logged in!"
echo ""
echo "============================================"
echo "⚠️  Press Ctrl+C to stop both servers"
echo "============================================"
echo ""

# Function to cleanup on exit
cleanup() {
    echo ""
    echo "🛑 Stopping servers..."
    kill $BACKEND_PID 2>/dev/null
    kill $FRONTEND_PID 2>/dev/null
    # Kill any remaining processes
    pkill -f "simple_server.py" 2>/dev/null
    pkill -f "next dev" 2>/dev/null
    echo "✅ Servers stopped"
    exit 0
}

# Trap Ctrl+C and call cleanup
trap cleanup INT TERM

# Wait for user to press Ctrl+C
wait
