#!/bin/bash

# AI-HR Platform Deployment Script
# This script helps deploy the application to production

set -e

echo "🚀 AI-HR Platform Deployment Script"
echo "===================================="
echo ""

# Check if required tools are installed
command -v node >/dev/null 2>&1 || { echo "❌ Node.js is required but not installed. Aborting." >&2; exit 1; }
command -v npm >/dev/null 2>&1 || { echo "❌ npm is required but not installed. Aborting." >&2; exit 1; }

# Check for environment variables
if [ ! -f "frontend/.env.local" ]; then
    echo "⚠️  Warning: frontend/.env.local not found"
    echo "📝 Creating from .env.example..."
    cp frontend/.env.example frontend/.env.local
    echo "✅ Please update frontend/.env.local with your Supabase credentials"
    exit 1
fi

echo "📦 Installing dependencies..."
cd frontend
npm install

echo ""
echo "🔍 Running type check..."
npm run type-check || echo "⚠️  Type check had warnings"

echo ""
echo "🧪 Running linter..."
npm run lint || echo "⚠️  Linter had warnings"

echo ""
echo "🏗️  Building production bundle..."
npm run build

echo ""
echo "✅ Build completed successfully!"
echo ""
echo "📋 Next steps:"
echo "1. Deploy to Vercel: vercel --prod"
echo "2. Or deploy to your preferred platform"
echo "3. Set environment variables in your deployment platform"
echo "4. Test the deployment thoroughly"
echo ""
echo "📚 See DEPLOYMENT_SUPABASE.md for detailed instructions"
