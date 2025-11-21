# Debug Registration Issue

## Quick Diagnosis

### Step 1: Open Test Page
Open this file in your browser:
```
frontend/test_supabase_connection.html
```

Or navigate to: `file:///path/to/your/project/frontend/test_supabase_connection.html`

### Step 2: Run Tests in Order
1. Click "1. Test Connection" - Should show ✅
2. Click "2. Test Tables" - This will tell us if tables exist
3. Click "3. Test Registration" - This will show exactly where it fails

### Step 3: Check Browser Console
Open Developer Tools (F12) and look at:
- **Console tab**: Look for error messages
- **Network tab**: Look for failed requests (red items)

## Common Issues & Solutions

### Issue 1: "relation 'users' does not exist"
**Problem:** Migration not run
**Solution:** 
1. Go to https://supabase.com/dashboard
2. SQL Editor → New Query
3. Paste contents of `supabase/migrations/001_initial_schema_fixed.sql`
4. Click Run

### Issue 2: "permission denied for table users"
**Problem:** RLS policies not set up correctly
**Solution:** Run this in Supabase SQL Editor:
```sql
-- Temporarily disable RLS for testing
ALTER TABLE users DISABLE ROW LEVEL SECURITY;
```

### Issue 3: "Failed to fetch" or CORS error
**Problem:** Supabase URL or API key incorrect
**Solution:** 
1. Check `.env.local` has correct values
2. Restart Next.js dev server: `npm run dev`

### Issue 4: "User already registered"
**Problem:** Email already exists
**Solution:** Try a different email or delete the user:
```sql
-- In Supabase SQL Editor
DELETE FROM auth.users WHERE email = 'your-test-email@example.com';
DELETE FROM users WHERE email = 'your-test-email@example.com';
```

## What to Look For

When you run the test page, you should see:

**✅ Good:**
```
✅ Connection successful!
✅ Users table exists and is accessible!
✅ Jobs table exists!
✅ Auth user created!
✅ Profile created successfully!
🎉 Registration completed successfully!
```

**❌ Bad (tells us what's wrong):**
```
❌ Users table error: relation "public.users" does not exist
```
This means: Run the migration!

```
❌ Profile Error: permission denied for table users
```
This means: RLS policy issue

```
❌ Auth Error: User already registered
```
This means: Use different email

## Next Steps

After running the test page, tell me:
1. What errors you see (copy the exact error messages)
2. Which step fails (Connection, Tables, or Registration)
3. Any red items in the Network tab

Then I can give you the exact fix!
