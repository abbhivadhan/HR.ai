# Registration Fix - Supabase Integration

## What Was Fixed

Updated the AuthContext to use Supabase authentication instead of the old backend API.

### Changes Made:
1. ✅ Updated `register()` function to use Supabase Auth
2. ✅ Updated `login()` function to use Supabase Auth  
3. ✅ Updated `logout()` function to use Supabase Auth
4. ✅ Added user profile creation in Supabase database

## To Make Registration Work

### Option 1: Use Supabase (Recommended)

1. **Create Supabase Project** (if not done):
   ```bash
   # Go to https://supabase.com
   # Create new project
   # Wait for setup to complete
   ```

2. **Run Database Migration**:
   - Open Supabase Dashboard > SQL Editor
   - Copy contents of `supabase/migrations/001_initial_schema.sql`
   - Paste and click "Run"

3. **Configure Environment Variables**:
   ```bash
   cd frontend
   cp .env.example .env.local
   ```

   Edit `.env.local`:
   ```env
   NEXT_PUBLIC_SUPABASE_URL=https://xxxxx.supabase.co
   NEXT_PUBLIC_SUPABASE_ANON_KEY=eyJhbGc...
   NEXT_PUBLIC_API_URL=https://xxxxx.supabase.co
   ```

4. **Install Supabase Client** (if not done):
   ```bash
   cd frontend
   npm install @supabase/supabase-js
   ```

5. **Restart Frontend**:
   ```bash
   npm run dev
   ```

6. **Test Registration**:
   - Go to http://localhost:3000/auth/register
   - Fill in the form
   - Click "Create Account"
   - Should work now!

### Option 2: Use Simple Backend (Temporary)

If you want to test without Supabase:

1. **Revert AuthContext** (temporarily):
   - The old version used axios to call `/api/auth/register`
   - You'd need to run the Python backend

2. **Start Backend**:
   ```bash
   cd backend
   python simple_server.py
   ```

3. **Update .env.local**:
   ```env
   NEXT_PUBLIC_API_URL=http://localhost:8000
   ```

4. **Restart Frontend**:
   ```bash
   cd frontend
   npm run dev
   ```

## Troubleshooting

### Error: "Missing Supabase environment variables"

**Solution**: Create `.env.local` with Supabase credentials

```bash
cd frontend
cp .env.example .env.local
# Edit .env.local with your Supabase URL and key
```

### Error: "Failed to fetch user profile"

**Solution**: Make sure database migration was run

1. Go to Supabase Dashboard > SQL Editor
2. Run the migration from `supabase/migrations/001_initial_schema.sql`
3. Verify `users` table exists

### Error: "Registration failed - no user returned"

**Solution**: Check Supabase Auth settings

1. Go to Supabase Dashboard > Authentication > Providers
2. Enable Email provider
3. Disable email confirmation (for testing):
   - Go to Authentication > Settings
   - Disable "Enable email confirmations"

### Error: "Invalid API key"

**Solution**: Check your Supabase keys

1. Go to Supabase Dashboard > Settings > API
2. Copy the correct keys:
   - Project URL
   - anon/public key (NOT service_role key)
3. Update `.env.local`

### Registration works but can't login

**Solution**: Check if user was created

1. Go to Supabase Dashboard > Authentication > Users
2. Verify user appears in list
3. Go to Table Editor > users table
4. Verify user profile was created

## Testing Registration

1. **Open Browser Console** (F12)
2. **Go to Registration Page**: http://localhost:3000/auth/register
3. **Fill in Form**:
   - Select account type (Candidate or Company)
   - Enter name and email
   - Create password
   - Accept terms
4. **Click "Create Account"**
5. **Check Console** for logs:
   - Should see "Register attempt with Supabase"
   - Should see "Supabase registration successful"
   - Should see "Registration complete"

## Quick Test Script

```bash
# 1. Make sure Supabase is configured
cd frontend
cat .env.local | grep SUPABASE

# 2. Install dependencies
npm install

# 3. Start dev server
npm run dev

# 4. Open browser to http://localhost:3000/auth/register
# 5. Try registering a new user
```

## Next Steps

After registration works:
1. Test login functionality
2. Test logout functionality
3. Test protected routes
4. Deploy to production

## Need Help?

Check these files:
- `frontend/src/contexts/AuthContext.tsx` - Authentication logic
- `frontend/src/lib/supabase.ts` - Supabase client
- `supabase/migrations/001_initial_schema.sql` - Database schema
- `START_HERE_DEPLOYMENT.md` - Full deployment guide
