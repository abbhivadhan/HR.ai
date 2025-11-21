#!/bin/bash

echo "Testing AI-HR Platform Build..."
echo "================================"

# Test Backend
echo "1. Testing Backend..."
cd backend
if source .venv/bin/activate && python -c "import app.main; print('✅ Backend imports successfully')"; then
    echo "✅ Backend build: PASSED"
else
    echo "❌ Backend build: FAILED"
    exit 1
fi
cd ..

# Test Frontend
echo ""
echo "2. Testing Frontend..."
cd frontend
if npm run build > /dev/null 2>&1; then
    echo "✅ Frontend build: PASSED"
else
    echo "❌ Frontend build: FAILED"
    exit 1
fi
cd ..

echo ""
echo "🎉 All builds completed successfully!"
echo ""
echo "Next steps:"
echo "- Install Docker to use the full docker-compose setup"
echo "- Set up PostgreSQL and Redis for full functionality"
echo "- Configure environment variables in backend/.env"