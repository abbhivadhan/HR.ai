#!/bin/bash

# Development Server Start Script

echo "🚀 Starting AI-HR Platform Development Servers"
echo "=============================================="
echo ""

# Check if we should start backend
read -p "Start Python backend? (y/n, default: n): " start_backend
start_backend=${start_backend:-n}

if [ "$start_backend" = "y" ] || [ "$start_backend" = "Y" ]; then
    echo ""
    echo "📦 Starting Backend Server..."
    echo "Backend will run on http://localhost:8000"
    echo ""
    
    # Check if virtual environment exists
    if [ -d "backend/.venv" ]; then
        echo "✅ Virtual environment found"
        cd backend
        source .venv/bin/activate
        
        # Check if dependencies are installed
        if ! python -c "import fastapi" 2>/dev/null; then
            echo "📦 Installing backend dependencies..."
            pip install -r requirements.txt
        fi
        
        echo "🚀 Starting FastAPI server..."
        python -m uvicorn app.main:app --reload --port 8000 &
        BACKEND_PID=$!
        cd ..
    else
        echo "⚠️  Virtual environment not found. Using simple server..."
        cd backend
        python simple_server.py &
        BACKEND_PID=$!
        cd ..
    fi
    
    echo "✅ Backend started (PID: $BACKEND_PID)"
    sleep 2
fi

echo ""
echo "📦 Starting Frontend Server..."
echo "Frontend will run on http://localhost:3000"
echo ""

cd frontend

# Check if node_modules exists
if [ ! -d "node_modules" ]; then
    echo "📦 Installing frontend dependencies..."
    npm install
fi

# Check if .env.local exists
if [ ! -f ".env.local" ]; then
    echo "⚠️  Warning: .env.local not found"
    if [ -f ".env.example" ]; then
        echo "📝 Creating .env.local from .env.example..."
        cp .env.example .env.local
        echo "⚠️  Please update .env.local with your Supabase credentials"
    fi
fi

echo "🚀 Starting Next.js development server..."
npm run dev &
FRONTEND_PID=$!

echo ""
echo "✅ Development servers started!"
echo ""
echo "📋 Server URLs:"
echo "   Frontend: http://localhost:3000"
if [ "$start_backend" = "y" ] || [ "$start_backend" = "Y" ]; then
    echo "   Backend:  http://localhost:8000"
    echo "   API Docs: http://localhost:8000/docs"
fi
echo ""
echo "Press Ctrl+C to stop all servers"
echo ""

# Wait for Ctrl+C
trap "echo ''; echo '🛑 Stopping servers...'; kill $FRONTEND_PID 2>/dev/null; [ ! -z '$BACKEND_PID' ] && kill $BACKEND_PID 2>/dev/null; echo '✅ Servers stopped'; exit 0" INT

# Keep script running
wait
