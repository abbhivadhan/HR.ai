# How to Get Your Supabase Credentials

## Quick Steps

### 1. Create Supabase Account (2 minutes)
1. Go to https://supabase.com
2. Click "Start your project"
3. Sign up with GitHub, Google, or Email
4. Verify your email if needed

### 2. Create New Project (2 minutes)
1. Click "New Project"
2. Fill in:
   - **Name**: `ai-hr-platform` (or any name you like)
   - **Database Password**: Generate a strong password (save it!)
   - **Region**: Choose closest to you (e.g., US East, Europe West)
3. Click "Create new project"
4. Wait ~2 minutes for setup to complete

### 3. Get Your API Credentials (1 minute)

Once your project is ready:

1. **Go to Settings**:
   - Click the ⚙️ (Settings) icon in the left sidebar
   - Click "API" in the settings menu

2. **Copy Your Credentials**:
   
   You'll see two important values:

   **Project URL**:
   ```
   https://xxxxxxxxxxxxx.supabase.co
   ```
   
   **anon/public key** (under "Project API keys"):
   ```
   eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6...
   ```

   ⚠️ **Important**: 
   - Copy the `anon public` key (NOT the `service_role` key)
   - The `service_role` key is secret and should never be used in frontend

### 4. Update Your .env.local File

1. **Open the file**:
   ```bash
   # The file is at: frontend/.env.local
   # Open it in your editor
   ```

2. **Replace the placeholder values**:
   ```env
   # Replace this:
   NEXT_PUBLIC_SUPABASE_URL=https://your-project-id.supabase.co
   
   # With your actual URL:
   NEXT_PUBLIC_SUPABASE_URL=https://xxxxxxxxxxxxx.supabase.co
   
   # Replace this:
   NEXT_PUBLIC_SUPABASE_ANON_KEY=your-anon-key-here
   
   # With your actual key:
   NEXT_PUBLIC_SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
   
   # Update API URL (same as Supabase URL):
   NEXT_PUBLIC_API_URL=https://xxxxxxxxxxxxx.supabase.co
   ```

3. **Save the file**

### 5. Set Up Database (3 minutes)

1. **Go to SQL Editor**:
   - Click "SQL Editor" in the left sidebar
   - Click "New query"

2. **Run the migration**:
   - Open the file: `supabase/migrations/001_initial_schema.sql`
   - Copy ALL the contents
   - Paste into the SQL Editor
   - Click "Run" (or press Cmd/Ctrl + Enter)

3. **Verify tables were created**:
   - Click "Table Editor" in the left sidebar
   - You should see tables: users, jobs, applications, etc.

### 6. Configure Authentication (1 minute)

1. **Go to Authentication**:
   - Click "Authentication" in the left sidebar
   - Click "Providers"

2. **Enable Email Provider**:
   - Make sure "Email" is enabled (it should be by default)

3. **Disable Email Confirmation** (for testing):
   - Click "Settings" under Authentication
   - Scroll to "Email Auth"
   - Toggle OFF "Enable email confirmations"
   - Click "Save"

   ⚠️ **Note**: In production, you should enable email confirmations!

### 7. Test Your Setup

1. **Restart your dev server**:
   ```bash
   cd frontend
   npm run dev
   ```

2. **Try registering**:
   - Go to http://localhost:3000/auth/register
   - Fill in the form
   - Click "Create Account"
   - Should work now! ✅

## Visual Guide

### Where to Find Your Credentials:

```
Supabase Dashboard
├── Settings (⚙️)
│   └── API
│       ├── Project URL ← Copy this
│       └── Project API keys
│           └── anon public ← Copy this (NOT service_role!)
```

### Your .env.local Should Look Like:

```env
NEXT_PUBLIC_SUPABASE_URL=https://abcdefghijklmnop.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImFiY2RlZmdoaWprbG1ub3AiLCJyb2xlIjoiYW5vbiIsImlhdCI6MTYzOTU4NzIwMCwiZXhwIjoxOTU1MTYzMjAwfQ.xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
NEXT_PUBLIC_API_URL=https://abcdefghijklmnop.supabase.co
NEXT_PUBLIC_APP_URL=http://localhost:3000
NEXT_PUBLIC_APP_NAME=AI-HR Platform
```

## Troubleshooting

### Can't find the API settings?
- Make sure your project finished creating (check the dashboard)
- Look for the ⚙️ Settings icon in the left sidebar
- Click "API" in the settings menu

### Which key should I use?
- ✅ Use: `anon public` key (safe for frontend)
- ❌ Don't use: `service_role` key (secret, backend only)

### My .env.local isn't working?
- Make sure the file is named exactly `.env.local` (with the dot)
- Make sure it's in the `frontend` folder
- Restart your dev server after creating/editing the file
- Check for typos in the variable names

### Still not working?
1. Check browser console (F12) for errors
2. Verify Supabase project is active (not paused)
3. Make sure you ran the database migration
4. Check that email provider is enabled in Supabase

## Quick Copy-Paste Template

Here's a template you can copy and fill in:

```bash
# 1. Copy this template
cat > frontend/.env.local << 'EOF'
NEXT_PUBLIC_SUPABASE_URL=
NEXT_PUBLIC_SUPABASE_ANON_KEY=
NEXT_PUBLIC_API_URL=
NEXT_PUBLIC_APP_URL=http://localhost:3000
NEXT_PUBLIC_APP_NAME=AI-HR Platform
EOF

# 2. Edit the file and add your credentials
# 3. Restart dev server
cd frontend && npm run dev
```

## Next Steps

After setting up:
1. ✅ Test registration
2. ✅ Test login
3. ✅ Test creating a job (company account)
4. ✅ Test applying to a job (candidate account)
5. 🚀 Deploy to production!

## Need Help?

- Supabase Docs: https://supabase.com/docs
- Supabase Discord: https://discord.supabase.com
- Check: `REGISTRATION_FIX.md` for troubleshooting
