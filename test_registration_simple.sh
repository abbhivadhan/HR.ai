#!/bin/bash

echo "🔍 Testing Supabase Registration Setup"
echo "========================================"
echo ""

# Check if tables exist using Supabase REST API
SUPABASE_URL="https://ykjjzawistyotgxdmukq.supabase.co"
SUPABASE_KEY="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Inlramp6YXdpc3R5b3RneGRtdWtxIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjMyMTk0MzEsImV4cCI6MjA3ODc5NTQzMX0.5kLy4FjVj_Av7FJpodvJYHbqXr30js0n-xbEK-mxdfE"

echo "Testing users table..."
RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" \
  "${SUPABASE_URL}/rest/v1/users?select=count&limit=1" \
  -H "apikey: ${SUPABASE_KEY}" \
  -H "Authorization: Bearer ${SUPABASE_KEY}")

if [ "$RESPONSE" = "200" ]; then
    echo "✅ Users table exists and is accessible"
elif [ "$RESPONSE" = "404" ]; then
    echo "❌ Users table does NOT exist"
    echo ""
    echo "ACTION REQUIRED:"
    echo "1. Go to: https://supabase.com/dashboard/project/ykjjzawistyotgxdmukq/sql/new"
    echo "2. Copy contents of: supabase/migrations/001_initial_schema_fixed.sql"
    echo "3. Paste and click 'Run'"
    exit 1
else
    echo "⚠️  Unexpected response: $RESPONSE"
    echo "This might be a permissions issue"
fi

echo ""
echo "Testing jobs table..."
RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" \
  "${SUPABASE_URL}/rest/v1/jobs?select=count&limit=1" \
  -H "apikey: ${SUPABASE_KEY}" \
  -H "Authorization: Bearer ${SUPABASE_KEY}")

if [ "$RESPONSE" = "200" ]; then
    echo "✅ Jobs table exists"
elif [ "$RESPONSE" = "404" ]; then
    echo "❌ Jobs table does NOT exist"
else
    echo "⚠️  Unexpected response: $RESPONSE"
fi

echo ""
echo "========================================" 
echo "Next step: Open frontend/test_supabase_connection.html in your browser"
echo "This will show you the EXACT error message"
