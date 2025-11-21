#!/bin/bash

echo "Checking Supabase Setup..."
echo "================================"
echo ""

# Check if .env.local exists
if [ -f "frontend/.env.local" ]; then
    echo "✓ Environment file found"
    
    # Extract Supabase URL
    SUPABASE_URL=$(grep NEXT_PUBLIC_SUPABASE_URL frontend/.env.local | cut -d '=' -f2)
    SUPABASE_KEY=$(grep NEXT_PUBLIC_SUPABASE_ANON_KEY frontend/.env.local | cut -d '=' -f2)
    
    if [ -n "$SUPABASE_URL" ] && [ -n "$SUPABASE_KEY" ]; then
        echo "✓ Supabase credentials configured"
        echo "  URL: $SUPABASE_URL"
    else
        echo "✗ Supabase credentials missing"
        exit 1
    fi
else
    echo "✗ Environment file not found"
    exit 1
fi

echo ""
echo "To apply the database migration:"
echo "1. Go to your Supabase project: https://supabase.com/dashboard"
echo "2. Navigate to SQL Editor"
echo "3. Copy and paste the contents of: supabase/migrations/001_initial_schema.sql"
echo "4. Click 'Run' to execute the migration"
echo ""
echo "Or use the Supabase CLI:"
echo "  supabase db push"
