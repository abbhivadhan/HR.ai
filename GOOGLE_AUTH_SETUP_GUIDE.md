# Google OAuth Integration Setup Guide

This guide will walk you through setting up Google OAuth authentication for your AI-HR Platform.

## Overview

Google OAuth has been integrated into both the login and registration flows. Users can now:
- Sign in with their Google account
- Sign up with their Google account
- Automatically create a profile on first Google login

## Prerequisites

1. A Google Cloud Platform account
2. Access to your Supabase project dashboard
3. The application running on a known URL (localhost for development)

## Step 1: Create Google OAuth Credentials

### 1.1 Go to Google Cloud Console

1. Visit [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select an existing one
3. Navigate to "APIs & Services" > "Credentials"

### 1.2 Configure OAuth Consent Screen

1. Click on "OAuth consent screen" in the left sidebar
2. Choose "External" user type (or "Internal" if using Google Workspace)
3. Fill in the required information:
   - **App name**: AI-HR Platform
   - **User support email**: Your email
   - **Developer contact email**: Your email
4. Add scopes:
   - `userinfo.email`
   - `userinfo.profile`
5. Add test users (for development)
6. Save and continue

### 1.3 Create OAuth 2.0 Client ID

1. Go back to "Credentials"
2. Click "Create Credentials" > "OAuth client ID"
3. Choose "Web application"
4. Configure:
   - **Name**: AI-HR Platform Web Client
   - **Authorized JavaScript origins**:
     - `http://localhost:3000` (development)
     - Your production URL (e.g., `https://yourdomain.com`)
   - **Authorized redirect URIs**:
     - `https://YOUR_SUPABASE_PROJECT_REF.supabase.co/auth/v1/callback`
     - Get your Supabase project ref from your Supabase dashboard URL

5. Click "Create"
6. **Save your Client ID and Client Secret** - you'll need these next

## Step 2: Configure Supabase

### 2.1 Enable Google Provider

1. Go to your [Supabase Dashboard](https://supabase.com/dashboard)
2. Select your project
3. Navigate to "Authentication" > "Providers"
4. Find "Google" in the list
5. Toggle it to "Enabled"

### 2.2 Add Google Credentials

1. In the Google provider settings:
   - **Client ID**: Paste your Google OAuth Client ID
   - **Client Secret**: Paste your Google OAuth Client Secret
2. Click "Save"

### 2.3 Configure Redirect URLs

1. In Supabase, go to "Authentication" > "URL Configuration"
2. Add your redirect URLs:
   - **Site URL**: `http://localhost:3000` (development)
   - **Redirect URLs**: 
     - `http://localhost:3000/auth/callback`
     - Add production URLs when deploying

## Step 3: Update Environment Variables

Your `.env.local` file should already have the Supabase credentials:

```bash
NEXT_PUBLIC_SUPABASE_URL=https://YOUR_PROJECT_REF.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=your-anon-key
NEXT_PUBLIC_APP_URL=http://localhost:3000
```

No additional environment variables are needed for Google OAuth - it's configured in Supabase.

## Step 4: Test the Integration

### 4.1 Start the Development Server

```bash
cd frontend
npm run dev
```

### 4.2 Test Login Flow

1. Navigate to `http://localhost:3000/auth/login`
2. Click "Sign in with Google"
3. You should be redirected to Google's login page
4. After authentication, you'll be redirected back to `/auth/callback`
5. The callback page will:
   - Create a user profile if it doesn't exist
   - Store the session
   - Redirect to the dashboard

### 4.3 Test Registration Flow

1. Navigate to `http://localhost:3000/auth/register`
2. On step 1, click "Continue with Google"
3. Follow the same flow as login
4. New users will have a profile automatically created

## How It Works

### Authentication Flow

1. **User clicks "Sign in with Google"**
   - Frontend calls `loginWithGoogle()` from AuthContext
   - Supabase redirects to Google OAuth

2. **User authenticates with Google**
   - Google validates credentials
   - User grants permissions
   - Google redirects back to Supabase

3. **Supabase processes the OAuth response**
   - Creates/updates auth user
   - Redirects to `/auth/callback` with session

4. **Callback page processes the session**
   - Retrieves session from Supabase
   - Checks if user profile exists in database
   - Creates profile if needed (for new users)
   - Stores tokens and user data in localStorage
   - Redirects to dashboard

### User Profile Creation

For Google OAuth users, the profile is created with:
- **Email**: From Google account
- **First Name**: Extracted from Google's full_name
- **Last Name**: Extracted from Google's full_name
- **User Type**: Defaults to 'CANDIDATE' (can be changed later)
- **Is Verified**: Set to `true` (Google accounts are pre-verified)

## Files Modified

### Frontend Files

1. **`frontend/src/contexts/AuthContext.tsx`**
   - Added `loginWithGoogle()` method
   - Handles Google OAuth flow

2. **`frontend/src/lib/supabase.ts`**
   - Added `signInWithGoogle()` helper
   - Configures OAuth redirect

3. **`frontend/src/components/auth/LoginForm.tsx`**
   - Added Google sign-in button
   - Styled with Google branding

4. **`frontend/src/components/auth/RegisterForm.tsx`**
   - Added Google sign-up button on step 1
   - Consistent styling with login

5. **`frontend/src/app/auth/callback/page.tsx`** (NEW)
   - Handles OAuth callback
   - Creates user profiles
   - Manages session storage

## Troubleshooting

### "Redirect URI mismatch" Error

**Problem**: Google shows an error about redirect URI mismatch.

**Solution**: 
1. Check that your redirect URI in Google Cloud Console exactly matches:
   `https://YOUR_PROJECT_REF.supabase.co/auth/v1/callback`
2. Make sure there are no trailing slashes
3. Wait a few minutes after adding the URI for changes to propagate

### "Access blocked: This app's request is invalid"

**Problem**: Google blocks the authentication request.

**Solution**:
1. Ensure OAuth consent screen is properly configured
2. Add your email as a test user
3. Verify all required scopes are added

### User Profile Not Created

**Problem**: User can authenticate but profile isn't created.

**Solution**:
1. Check browser console for errors
2. Verify the `users` table exists in Supabase
3. Check Row Level Security (RLS) policies allow inserts
4. Ensure the callback page has proper error handling

### Session Not Persisting

**Problem**: User is logged out after page refresh.

**Solution**:
1. Check that localStorage is working
2. Verify Supabase client is configured with `persistSession: true`
3. Check browser's localStorage for tokens

## Security Considerations

1. **Never commit credentials**: Keep your Google Client Secret secure
2. **Use HTTPS in production**: OAuth requires secure connections
3. **Validate redirect URIs**: Only whitelist your actual domains
4. **Review OAuth scopes**: Only request necessary permissions
5. **Monitor OAuth usage**: Check Google Cloud Console for unusual activity

## Production Deployment

Before deploying to production:

1. **Update Google OAuth settings**:
   - Add production domain to authorized origins
   - Add production callback URL to redirect URIs

2. **Update Supabase settings**:
   - Add production URL to Site URL
   - Add production callback to Redirect URLs

3. **Update environment variables**:
   - Set `NEXT_PUBLIC_APP_URL` to production domain

4. **Test thoroughly**:
   - Test login flow
   - Test registration flow
   - Test profile creation
   - Test session persistence

## Additional Features

### Future Enhancements

Consider adding:
- **Account linking**: Allow users to link Google to existing email/password accounts
- **Multiple OAuth providers**: Add GitHub, LinkedIn, Microsoft, etc.
- **Profile completion**: Prompt Google users to complete their profile
- **Role selection**: Let Google users choose their role (Candidate/Company) after signup

## Support

If you encounter issues:
1. Check the browser console for errors
2. Review Supabase logs in the dashboard
3. Check Google Cloud Console for OAuth errors
4. Verify all configuration steps were completed

## Resources

- [Supabase Auth Documentation](https://supabase.com/docs/guides/auth)
- [Google OAuth 2.0 Documentation](https://developers.google.com/identity/protocols/oauth2)
- [Supabase Google OAuth Guide](https://supabase.com/docs/guides/auth/social-login/auth-google)
