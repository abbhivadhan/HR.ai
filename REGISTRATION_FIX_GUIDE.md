# Registration "Load Failed" Fix

## Problem
Registration fails with "load failed" error because the database tables don't exist yet.

## Solution

You need to run the database migration to create the required tables in Supabase.

### Option 1: Using Supabase Dashboard (Recommended)

1. **Go to your Supabase Dashboard**
   - Visit: https://supabase.com/dashboard
   - Select your project

2. **Open SQL Editor**
   - Click on "SQL Editor" in the left sidebar
   - Click "New Query"

3. **Run the Migration**
   - Open the file: `supabase/migrations/001_initial_schema_fixed.sql`
   - Copy ALL the contents
   - Paste into the SQL Editor
   - Click "Run" (or press Cmd/Ctrl + Enter)
   
   **Important:** Use the `001_initial_schema_fixed.sql` file, not the original one. The fixed version works properly with Supabase Auth.

4. **Verify Tables Created**
   - Go to "Table Editor" in the left sidebar
   - You should see tables like: `users`, `jobs`, `applications`, `assessments`, `interviews`

### Option 2: Using Supabase CLI

If you have the Supabase CLI installed:

```bash
# Link your project (first time only)
supabase link --project-ref your-project-ref

# Push the migration
supabase db push
```

### Option 3: Manual Table Creation

If the migration file is too large, you can create tables one by one:

1. Go to Supabase Dashboard > Table Editor
2. Click "New Table"
3. Create the `users` table first with these columns:
   - `id` (uuid, primary key)
   - `email` (text, unique)
   - `first_name` (text)
   - `last_name` (text)
   - `user_type` (text)
   - `is_active` (boolean, default: true)
   - `is_verified` (boolean, default: false)
   - `created_at` (timestamp with time zone)
   - `updated_at` (timestamp with time zone)

## After Running Migration

1. **Test Registration**
   - Go to: http://localhost:3000/auth/register
   - Fill in the form
   - Click "Create Account"
   - Should succeed without "load failed" error

2. **Check Browser Console**
   - Open Developer Tools (F12)
   - Look for any error messages
   - Should see: "Registration complete: {user data}"

## Common Issues

### "relation does not exist" error
- The migration hasn't been run yet
- Follow Option 1 above to create tables

### "permission denied" error
- Check Row Level Security (RLS) policies
- The migration includes policies, but verify they're enabled

### "duplicate key" error
- User already exists with that email
- Try a different email address

## Verify Setup

Run this command to check your setup:
```bash
./check_supabase_setup.sh
```

## Need Help?

Check the browser console (F12) for detailed error messages. The error will tell you exactly what's missing.
