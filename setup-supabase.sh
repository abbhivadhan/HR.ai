#!/bin/bash

# Supabase Setup Script for AI-HR Platform

echo "🚀 Setting up Supabase for AI-HR Platform"
echo "=========================================="
echo ""

# Check if we're in the right directory
if [ ! -d "frontend" ]; then
    echo "❌ Error: frontend directory not found"
    echo "Please run this script from the project root directory"
    exit 1
fi

echo "📦 Installing Supabase client..."
cd frontend
npm install @supabase/supabase-js

echo ""
echo "📝 Creating environment file..."
if [ ! -f ".env.local" ]; then
    cp .env.example .env.local
    echo "✅ Created .env.local from .env.example"
    echo ""
    echo "⚠️  IMPORTANT: Edit frontend/.env.local with your Supabase credentials:"
    echo "   - NEXT_PUBLIC_SUPABASE_URL"
    echo "   - NEXT_PUBLIC_SUPABASE_ANON_KEY"
    echo "   - NEXT_PUBLIC_API_URL"
else
    echo "ℹ️  .env.local already exists, skipping..."
fi

echo ""
echo "✅ Supabase setup complete!"
echo ""
echo "📋 Next steps:"
echo "1. Create a Supabase project at https://supabase.com"
echo "2. Run the SQL migration in supabase/migrations/001_initial_schema.sql"
echo "3. Update frontend/.env.local with your Supabase credentials"
echo "4. Run 'npm run dev' to test locally"
echo "5. Deploy with 'vercel --prod'"
echo ""
echo "📚 See START_HERE_DEPLOYMENT.md for detailed instructions"
