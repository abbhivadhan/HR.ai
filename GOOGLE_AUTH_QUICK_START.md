# Google OAuth Quick Start

## 🚀 Quick Setup (5 Minutes)

### 1. Google Cloud Console Setup

```
1. Go to: https://console.cloud.google.com/
2. Create/Select Project
3. APIs & Services > Credentials
4. Create OAuth 2.0 Client ID
5. Add redirect URI: https://YOUR_SUPABASE_REF.supabase.co/auth/v1/callback
6. Copy Client ID and Client Secret
```

### 2. Supabase Configuration

```
1. Go to: https://supabase.com/dashboard
2. Authentication > Providers > Google
3. Enable Google
4. Paste Client ID and Client Secret
5. Save
```

### 3. Test It

```bash
cd frontend
npm run dev
# Visit http://localhost:3000/auth/login
# Click "Sign in with Google"
```

## 📝 Key Files

| File | Purpose |
|------|---------|
| `frontend/src/contexts/AuthContext.tsx` | Added `loginWithGoogle()` |
| `frontend/src/lib/supabase.ts` | Added `signInWithGoogle()` |
| `frontend/src/components/auth/LoginForm.tsx` | Google button on login |
| `frontend/src/components/auth/RegisterForm.tsx` | Google button on signup |
| `frontend/src/app/auth/callback/page.tsx` | OAuth callback handler |

## 🔑 How to Use in Code

### Login with Google

```typescript
import { useAuth } from '@/contexts/AuthContext'

function MyComponent() {
  const { loginWithGoogle } = useAuth()
  
  const handleGoogleLogin = async () => {
    try {
      await loginWithGoogle()
      // User will be redirected to Google
    } catch (error) {
      console.error('Login failed:', error)
    }
  }
  
  return (
    <button onClick={handleGoogleLogin}>
      Sign in with Google
    </button>
  )
}
```

### Check Authentication Status

```typescript
import { useAuth } from '@/contexts/AuthContext'

function MyComponent() {
  const { user, isAuthenticated } = useAuth()
  
  if (isAuthenticated) {
    return <div>Welcome, {user?.firstName}!</div>
  }
  
  return <div>Please log in</div>
}
```

## 🎯 What Happens During OAuth

```
1. User clicks "Sign in with Google"
   ↓
2. Redirected to Google login
   ↓
3. User authenticates with Google
   ↓
4. Google redirects to Supabase
   ↓
5. Supabase redirects to /auth/callback
   ↓
6. Callback creates user profile (if new)
   ↓
7. User redirected to dashboard
```

## ⚙️ Configuration Checklist

- [ ] Google OAuth Client ID created
- [ ] Google OAuth Client Secret created
- [ ] Redirect URI added in Google Console
- [ ] Google provider enabled in Supabase
- [ ] Client ID added to Supabase
- [ ] Client Secret added to Supabase
- [ ] Callback URL configured in Supabase
- [ ] Frontend running on correct URL
- [ ] Test user added (for development)

## 🐛 Common Issues

### "Redirect URI mismatch"
```
Fix: Ensure Google Console redirect URI exactly matches:
https://YOUR_PROJECT_REF.supabase.co/auth/v1/callback
```

### "Access blocked"
```
Fix: Add your email as a test user in Google OAuth consent screen
```

### Profile not created
```
Fix: Check Supabase RLS policies allow inserts on users table
```

## 📊 User Profile Structure

When a user signs in with Google, their profile is created with:

```typescript
{
  id: string,              // From Google/Supabase
  email: string,           // From Google account
  firstName: string,       // From Google full_name
  lastName: string,        // From Google full_name
  userType: 'CANDIDATE',   // Default (can be changed)
  isVerified: true         // Google accounts are pre-verified
}
```

## 🔒 Security Notes

- ✅ Tokens stored in localStorage
- ✅ Session persists across page reloads
- ✅ Automatic token refresh via Supabase
- ✅ Secure OAuth flow via Supabase
- ⚠️ Never commit Google Client Secret
- ⚠️ Use HTTPS in production

## 📚 Full Documentation

See `GOOGLE_AUTH_SETUP_GUIDE.md` for complete setup instructions and troubleshooting.

## 🎨 UI Components

Both login and register forms now include:
- Google sign-in button with official branding
- "Or continue with" divider
- Consistent styling with existing forms
- Loading states during authentication
- Error handling and display

## 🚀 Production Checklist

Before deploying:
- [ ] Add production domain to Google authorized origins
- [ ] Add production callback to Google redirect URIs
- [ ] Update Supabase Site URL
- [ ] Update Supabase Redirect URLs
- [ ] Set NEXT_PUBLIC_APP_URL to production domain
- [ ] Test complete OAuth flow in production
- [ ] Verify profile creation works
- [ ] Check session persistence

## 💡 Tips

1. **Development**: Use `http://localhost:3000` for testing
2. **Staging**: Add staging URLs to both Google and Supabase
3. **Production**: Always use HTTPS
4. **Testing**: Add test users in Google Console during development
5. **Monitoring**: Check Supabase logs for authentication issues

## 🆘 Need Help?

1. Check browser console for errors
2. Review Supabase dashboard logs
3. Verify Google Cloud Console settings
4. See full guide: `GOOGLE_AUTH_SETUP_GUIDE.md`
