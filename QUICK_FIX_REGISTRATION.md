# Quick Fix: Registration "Load Failed" Error

## The Problem
When registering a candidate, you get a "load failed" error because the database tables haven't been created in Supabase yet.

## The Solution (2 minutes)

### Step 1: Go to Supabase Dashboard
1. Visit https://supabase.com/dashboard
2. Select your project (ykjjzawistyotgxdmukq)

### Step 2: Run the Migration
1. Click **"SQL Editor"** in the left sidebar
2. Click **"New Query"**
3. Open this file on your computer: `supabase/migrations/001_initial_schema_fixed.sql`
4. Copy ALL the contents (Cmd+A, Cmd+C)
5. Paste into the SQL Editor (Cmd+V)
6. Click **"Run"** button (or press Cmd+Enter)

### Step 3: Verify
1. Click **"Table Editor"** in the left sidebar
2. You should now see these tables:
   - ✓ users
   - ✓ jobs
   - ✓ applications
   - ✓ assessments
   - ✓ interviews

### Step 4: Test Registration
1. Go to http://localhost:3000/auth/register
2. Fill in the registration form
3. Click "Create Account"
4. Should work without errors! 🎉

## What Changed?
- Installed `@supabase/supabase-js` package ✓
- Created proper database schema that works with Supabase Auth ✓
- Added better error messages to help debug issues ✓

## Still Having Issues?
Check the browser console (F12) for detailed error messages. The error will tell you exactly what's wrong.

Common issues:
- **"relation does not exist"** → Migration not run yet, follow steps above
- **"permission denied"** → RLS policies issue, migration includes fixes
- **"duplicate key"** → Email already registered, try different email
