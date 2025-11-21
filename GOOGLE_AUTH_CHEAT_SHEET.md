# Google OAuth Cheat Sheet

## 🚀 Quick Setup (5 Minutes)

### 1. Google Cloud Console
```
https://console.cloud.google.com/
→ APIs & Services → Credentials
→ Create OAuth Client ID
→ Add redirect: https://YOUR_REF.supabase.co/auth/v1/callback
→ Copy Client ID & Secret
```

### 2. Supabase Dashboard
```
https://supabase.com/dashboard
→ Authentication → Providers → Google
→ Enable & paste Client ID + Secret
→ Save
```

### 3. Run Migration
```bash
# Apply OAuth support migration
psql -h YOUR_DB_HOST -U postgres -d postgres -f supabase/migrations/002_add_oauth_support.sql
```

### 4. Test
```bash
cd frontend && npm run dev
# Visit http://localhost:3000/auth/login
# Click "Sign in with Google"
```

## 📁 Key Files

| File | Purpose |
|------|---------|
| `AuthContext.tsx` | `loginWithGoogle()` method |
| `supabase.ts` | `signInWithGoogle()` helper |
| `LoginForm.tsx` | Google button on login |
| `RegisterForm.tsx` | Google button on signup |
| `GoogleButton.tsx` | Reusable Google button |
| `auth/callback/page.tsx` | OAuth callback handler |

## 💻 Code Snippets

### Use Google Login
```typescript
import { useAuth } from '@/contexts/AuthContext'

function MyComponent() {
  const { loginWithGoogle } = useAuth()
  
  return (
    <button onClick={loginWithGoogle}>
      Sign in with Google
    </button>
  )
}
```

### Check Auth Status
```typescript
const { user, isAuthenticated } = useAuth()

if (isAuthenticated) {
  console.log('Logged in as:', user?.email)
}
```

### Google Button Component
```typescript
import GoogleButton from '@/components/auth/GoogleButton'

<GoogleButton
  onClick={handleGoogleLogin}
  disabled={isLoading}
  text="Sign in with Google"
/>
```

## 🔧 Configuration

### Environment Variables
```bash
NEXT_PUBLIC_SUPABASE_URL=https://xxx.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=xxx
NEXT_PUBLIC_APP_URL=http://localhost:3000
```

### Google OAuth URLs
```
Development:
- Origin: http://localhost:3000
- Redirect: https://YOUR_REF.supabase.co/auth/v1/callback

Production:
- Origin: https://yourdomain.com
- Redirect: https://YOUR_REF.supabase.co/auth/v1/callback
```

## 🔍 Debugging

### Check Browser Console
```javascript
// Check tokens
localStorage.getItem('accessToken')
localStorage.getItem('refreshToken')
localStorage.getItem('userData')

// Check Supabase session
const { data } = await supabase.auth.getSession()
console.log(data)
```

### Check Database
```sql
-- View OAuth users
SELECT id, email, first_name, last_name, oauth_provider, is_verified
FROM users
WHERE oauth_provider = 'google';

-- Check specific user
SELECT * FROM users WHERE email = 'test@gmail.com';
```

### Common Errors

| Error | Fix |
|-------|-----|
| "Redirect URI mismatch" | Check Google Console URIs match exactly |
| "Access blocked" | Add test users in Google OAuth consent screen |
| "Profile not created" | Check RLS policies, run migration |
| "Session not found" | Check Supabase config, verify tokens |

## 🎯 Testing Checklist

- [ ] New user can sign up with Google
- [ ] Existing user can log in with Google
- [ ] Session persists after refresh
- [ ] Logout works correctly
- [ ] Profile data is accurate
- [ ] Error handling works
- [ ] Works on mobile
- [ ] Works in all browsers

## 🔒 Security Checklist

- [ ] Client Secret not in code
- [ ] HTTPS in production
- [ ] Redirect URIs whitelisted
- [ ] RLS policies enabled
- [ ] Tokens in localStorage
- [ ] PKCE flow enabled
- [ ] OAuth scopes minimal

## 📊 User Flow

```
Login Page
    ↓ (Click Google button)
Google Login
    ↓ (Authenticate)
Supabase
    ↓ (Process OAuth)
/auth/callback
    ↓ (Create/fetch profile)
Dashboard
```

## 🛠️ Useful Commands

```bash
# Start dev server
cd frontend && npm run dev

# Check Supabase status
npx supabase status

# View Supabase logs
npx supabase logs

# Run migration
psql -h HOST -U USER -d DB -f migrations/002_add_oauth_support.sql

# Clear localStorage (browser console)
localStorage.clear()
```

## 📱 URLs

| Environment | URL |
|-------------|-----|
| Dev Login | http://localhost:3000/auth/login |
| Dev Register | http://localhost:3000/auth/register |
| Callback | http://localhost:3000/auth/callback |
| Dashboard | http://localhost:3000/dashboard |
| Google Console | https://console.cloud.google.com |
| Supabase Dashboard | https://supabase.com/dashboard |

## 🎨 Google Button Styling

```typescript
// Official Google colors
#4285F4 - Blue
#34A853 - Green
#FBBC05 - Yellow
#EA4335 - Red

// Button specs
- Border: 1px solid #dadce0
- Background: white
- Hover: #f8f9fa
- Height: 40px
- Border radius: 4px
```

## 📚 Documentation

| Doc | Purpose |
|-----|---------|
| `GOOGLE_AUTH_SETUP_GUIDE.md` | Full setup |
| `GOOGLE_AUTH_QUICK_START.md` | Quick ref |
| `GOOGLE_AUTH_TESTING.md` | Test cases |
| `GOOGLE_AUTH_IMPLEMENTATION_SUMMARY.md` | Overview |
| `GOOGLE_AUTH_CHEAT_SHEET.md` | This file |

## 🔗 Resources

- [Supabase Auth Docs](https://supabase.com/docs/guides/auth)
- [Google OAuth Docs](https://developers.google.com/identity/protocols/oauth2)
- [OAuth Playground](https://developers.google.com/oauthplayground/)
- [JWT Debugger](https://jwt.io/)

## 💡 Pro Tips

1. **Test Users**: Add your email as test user in Google Console
2. **Debugging**: Check both browser console AND Supabase logs
3. **URIs**: Redirect URIs must match EXACTLY (no trailing slash)
4. **Propagation**: Google changes take 5 minutes to propagate
5. **Tokens**: Use jwt.io to decode and inspect tokens
6. **RLS**: If profile creation fails, check RLS policies first

## 🆘 Quick Fixes

### Can't log in?
```bash
1. Check Google Console → OAuth consent screen → Test users
2. Verify redirect URI matches exactly
3. Check Supabase → Auth → Providers → Google is enabled
4. Clear browser cache and try again
```

### Profile not created?
```sql
-- Check RLS policies
SELECT * FROM pg_policies WHERE tablename = 'users';

-- Manually create if needed
INSERT INTO users (id, email, first_name, last_name, user_type, is_verified)
VALUES ('uuid-here', 'email@gmail.com', 'First', 'Last', 'CANDIDATE', true);
```

### Session not persisting?
```javascript
// Check Supabase client config
const supabase = createClient(url, key, {
  auth: {
    persistSession: true,  // Must be true
    autoRefreshToken: true,
    detectSessionInUrl: true
  }
})
```

---

**Print this page for quick reference!**
