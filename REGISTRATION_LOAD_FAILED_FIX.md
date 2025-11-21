# Fix: "Load Failed" Error (AuthRetryableFetchError)

## The Problem
Error: `AuthRetryableFetchError` with `status: 0` means the browser **cannot connect** to Supabase at all.

## Solution: Restart Everything

### Step 1: Stop the Dev Server
In your terminal where `npm run dev` is running, press `Ctrl+C` to stop it.

### Step 2: Clear Next.js Cache
```bash
cd frontend
rm -rf .next
```

### Step 3: Restart Dev Server
```bash
npm run dev
```

### Step 4: Hard Refresh Browser
- Press `Cmd+Shift+R` (Mac) or `Ctrl+Shift+R` (Windows/Linux)
- Or open DevTools (F12) → Right-click refresh button → "Empty Cache and Hard Reload"

### Step 5: Try Registration Again
Go to: http://localhost:3000/test-registration

## If Still Not Working

### Check 1: Browser Extensions
Disable these temporarily:
- Ad blockers (uBlock Origin, AdBlock, etc.)
- Privacy extensions (Privacy Badger, Ghostery, etc.)
- VPN extensions

### Check 2: Network Tab
1. Open DevTools (F12)
2. Go to "Network" tab
3. Try registration again
4. Look for a request to `ykjjzawistyotgxdmukq.supabase.co`
5. Check if it's:
   - **Red/Failed**: Network issue
   - **Blocked**: Browser extension blocking it
   - **CORS error**: Supabase configuration issue

### Check 3: Verify Supabase Project is Active
1. Go to: https://supabase.com/dashboard
2. Check if your project is **active** (not paused)
3. If paused, click "Resume Project"

### Check 4: Test Direct Connection
Open this URL in your browser:
```
https://ykjjzawistyotgxdmukq.supabase.co/auth/v1/health
```

You should see: `{"version":"...","name":"GoTrue"}`

If you see an error page, your Supabase project might be down.

## Alternative: Use Different Email Provider

If the issue persists, it might be Supabase's email confirmation blocking. Try:

1. Go to Supabase Dashboard → Authentication → Settings
2. Disable "Enable email confirmations"
3. Try registration again

## Quick Test Command

Run this to test if Supabase is reachable:
```bash
curl https://ykjjzawistyotgxdmukq.supabase.co/auth/v1/health
```

Should return: `{"version":"...","name":"GoTrue"}`

## Still Stuck?

Check the browser console for the EXACT error:
1. F12 → Console tab
2. Try registration
3. Copy the full error message
4. Look for clues like:
   - "CORS"
   - "blocked"
   - "net::ERR_"
   - "Failed to fetch"
