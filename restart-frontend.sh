#!/bin/bash

echo "🔄 Restarting Frontend with Fresh Environment..."
echo ""

# Kill any existing Next.js processes
echo "1. Killing existing Next.js processes..."
pkill -f "next dev" || true
sleep 2

# Clear Next.js cache
echo "2. Clearing Next.js cache..."
rm -rf frontend/.next
rm -rf frontend/node_modules/.cache

# Verify environment variables
echo "3. Verifying environment variables..."
if grep -q "your-project-id" frontend/.env.local; then
    echo "❌ ERROR: .env.local still has placeholder values!"
    echo "Please check frontend/.env.local"
    exit 1
fi

echo "✅ Environment variables look good"
echo ""
echo "4. Starting dev server..."
echo "Run this command in the frontend directory:"
echo "   cd frontend && npm run dev"
echo ""
echo "Then go to: http://localhost:3000/test-registration"
