# Google OAuth Testing Guide

This guide provides comprehensive testing procedures for the Google OAuth integration.

## Pre-Testing Checklist

Before testing, ensure:
- [ ] Google OAuth credentials are configured in Google Cloud Console
- [ ] Google provider is enabled in Supabase
- [ ] Client ID and Secret are added to Supabase
- [ ] Redirect URIs are properly configured
- [ ] Database migration `002_add_oauth_support.sql` has been run
- [ ] Frontend is running (`npm run dev`)
- [ ] You have a Google account for testing

## Test Scenarios

### 1. New User Registration with Google

**Objective**: Verify that a new user can sign up using Google OAuth.

**Steps**:
1. Navigate to `http://localhost:3000/auth/register`
2. On Step 1, click "Continue with Google"
3. Select/enter your Google account credentials
4. Grant permissions when prompted
5. Wait for redirect to callback page
6. Verify redirect to dashboard

**Expected Results**:
- ✅ Redirected to Google login page
- ✅ Successfully authenticated with Google
- ✅ Redirected to `/auth/callback`
- ✅ User profile created in database
- ✅ Redirected to `/dashboard`
- ✅ User is logged in
- ✅ User data visible in dashboard

**Database Verification**:
```sql
-- Check user was created
SELECT id, email, first_name, last_name, user_type, is_verified, oauth_provider
FROM users
WHERE email = 'your-test-email@gmail.com';

-- Expected:
-- - id: UUID from Supabase Auth
-- - email: Your Google email
-- - first_name: Extracted from Google
-- - last_name: Extracted from Google
-- - user_type: 'CANDIDATE' (default)
-- - is_verified: true
-- - oauth_provider: 'google'
```

### 2. Existing User Login with Google

**Objective**: Verify that an existing Google OAuth user can log in.

**Steps**:
1. Log out if currently logged in
2. Navigate to `http://localhost:3000/auth/login`
3. Click "Sign in with Google"
4. Select your Google account (should be remembered)
5. Wait for redirect

**Expected Results**:
- ✅ Redirected to Google (may skip login if session exists)
- ✅ Redirected to `/auth/callback`
- ✅ Redirected to `/dashboard`
- ✅ User is logged in with correct data
- ✅ Session persists after page refresh

### 3. Session Persistence

**Objective**: Verify that the OAuth session persists across page reloads.

**Steps**:
1. Log in with Google
2. Navigate to dashboard
3. Refresh the page (F5 or Cmd+R)
4. Navigate to different pages
5. Close and reopen the browser tab

**Expected Results**:
- ✅ User remains logged in after refresh
- ✅ User data is still available
- ✅ Navigation works correctly
- ✅ Session persists in new tab

**Browser Storage Check**:
```javascript
// Open browser console and check:
localStorage.getItem('accessToken')      // Should have JWT token
localStorage.getItem('refreshToken')     // Should have refresh token
localStorage.getItem('userData')         // Should have user object
```

### 4. Logout Functionality

**Objective**: Verify that logout works correctly for OAuth users.

**Steps**:
1. Log in with Google
2. Navigate to dashboard
3. Click logout button
4. Verify redirect to home/login page
5. Try to access protected routes

**Expected Results**:
- ✅ User is logged out
- ✅ Redirected to appropriate page
- ✅ Cannot access protected routes
- ✅ localStorage is cleared
- ✅ Can log in again successfully

### 5. Multiple Account Switching

**Objective**: Verify that users can switch between different Google accounts.

**Steps**:
1. Log in with Google Account A
2. Log out
3. Log in with Google Account B
4. Verify correct account is logged in
5. Log out
6. Log in with Account A again

**Expected Results**:
- ✅ Each account creates separate user profile
- ✅ Correct user data displayed for each account
- ✅ No data mixing between accounts
- ✅ Can switch accounts seamlessly

### 6. Error Handling - Denied Permissions

**Objective**: Verify proper error handling when user denies OAuth permissions.

**Steps**:
1. Navigate to login page
2. Click "Sign in with Google"
3. On Google consent screen, click "Cancel" or "Deny"
4. Observe error handling

**Expected Results**:
- ✅ User returned to login page
- ✅ Appropriate error message displayed
- ✅ Can retry login
- ✅ No partial user creation in database

### 7. Error Handling - Invalid Configuration

**Objective**: Test error handling with misconfigured OAuth.

**Test Cases**:

**A. Invalid Redirect URI**:
- Temporarily change redirect URI in Google Console
- Attempt login
- Should see "redirect_uri_mismatch" error

**B. Invalid Client ID**:
- Temporarily change Client ID in Supabase
- Attempt login
- Should see authentication error

**Expected Results**:
- ✅ Clear error messages displayed
- ✅ User can return to login page
- ✅ No broken states

### 8. Profile Data Accuracy

**Objective**: Verify that user profile data is correctly extracted from Google.

**Steps**:
1. Log in with Google account that has:
   - Full name set
   - Profile picture
   - Verified email
2. Check user profile in dashboard
3. Verify data in database

**Expected Results**:
- ✅ First name correctly extracted
- ✅ Last name correctly extracted
- ✅ Email matches Google account
- ✅ Profile picture URL stored (if implemented)
- ✅ Email marked as verified

### 9. Concurrent Sessions

**Objective**: Test multiple simultaneous sessions.

**Steps**:
1. Log in with Google in Browser A
2. Log in with same account in Browser B
3. Perform actions in both browsers
4. Log out in Browser A
5. Check Browser B

**Expected Results**:
- ✅ Both sessions work independently
- ✅ Logout in one doesn't affect the other
- ✅ Data stays consistent

### 10. Mobile Responsiveness

**Objective**: Verify OAuth works on mobile devices.

**Steps**:
1. Open site on mobile device or use browser dev tools
2. Navigate to login page
3. Click "Sign in with Google"
4. Complete OAuth flow

**Expected Results**:
- ✅ Google button displays correctly
- ✅ OAuth flow works on mobile
- ✅ Redirects work properly
- ✅ Session persists on mobile

## Performance Testing

### Load Time Metrics

Measure and verify:
- Time to redirect to Google: < 500ms
- Time for callback processing: < 2s
- Time to dashboard after auth: < 1s

### Network Requests

Monitor network tab for:
- Proper OAuth redirect flow
- Token exchange requests
- Profile creation requests
- No unnecessary API calls

## Security Testing

### 1. Token Security

**Verify**:
- [ ] Tokens stored in localStorage (not cookies for XSS protection)
- [ ] Tokens are JWT format
- [ ] Tokens have expiration
- [ ] Refresh tokens work correctly

### 2. CSRF Protection

**Verify**:
- [ ] State parameter used in OAuth flow
- [ ] PKCE flow enabled (check Supabase config)
- [ ] No token leakage in URLs

### 3. Session Security

**Verify**:
- [ ] Sessions expire appropriately
- [ ] Logout clears all tokens
- [ ] Cannot reuse old tokens after logout

## Browser Compatibility

Test on:
- [ ] Chrome (latest)
- [ ] Firefox (latest)
- [ ] Safari (latest)
- [ ] Edge (latest)
- [ ] Mobile Safari (iOS)
- [ ] Mobile Chrome (Android)

## Common Issues and Solutions

### Issue: "Redirect URI mismatch"

**Symptoms**: Google shows error about redirect URI.

**Solution**:
1. Check Google Console redirect URIs
2. Ensure exact match: `https://YOUR_REF.supabase.co/auth/v1/callback`
3. No trailing slashes
4. Wait 5 minutes for changes to propagate

### Issue: "Access blocked: This app's request is invalid"

**Symptoms**: Google blocks the authentication.

**Solution**:
1. Check OAuth consent screen is configured
2. Add test users in Google Console
3. Verify all required scopes are added
4. Check app is not in "Testing" mode with no test users

### Issue: Profile not created

**Symptoms**: User authenticated but no profile in database.

**Solution**:
1. Check browser console for errors
2. Verify RLS policies allow inserts
3. Check migration `002_add_oauth_support.sql` was run
4. Verify callback page logic

### Issue: Session not persisting

**Symptoms**: User logged out after refresh.

**Solution**:
1. Check localStorage is enabled
2. Verify Supabase client config has `persistSession: true`
3. Check browser's privacy settings
4. Verify tokens are being stored

## Automated Testing

### Unit Tests

Create tests for:
```typescript
// Test OAuth button rendering
describe('GoogleButton', () => {
  it('renders correctly', () => {})
  it('calls onClick when clicked', () => {})
  it('is disabled when disabled prop is true', () => {})
})

// Test auth context
describe('AuthContext', () => {
  it('loginWithGoogle redirects to Google', () => {})
  it('handles OAuth callback correctly', () => {})
  it('creates user profile for new users', () => {})
})
```

### Integration Tests

Test complete flows:
```typescript
describe('Google OAuth Flow', () => {
  it('completes full registration flow', () => {})
  it('completes full login flow', () => {})
  it('handles errors gracefully', () => {})
})
```

## Test Data Cleanup

After testing, clean up test data:

```sql
-- Remove test users
DELETE FROM users WHERE email LIKE '%test%@gmail.com';

-- Or remove specific test user
DELETE FROM users WHERE email = 'your-test-email@gmail.com';
```

## Production Testing Checklist

Before going live:
- [ ] Test with production URLs
- [ ] Verify SSL certificates
- [ ] Test with real user accounts
- [ ] Monitor error rates
- [ ] Check analytics/logging
- [ ] Verify email notifications (if any)
- [ ] Test account recovery flows
- [ ] Verify GDPR compliance
- [ ] Test data export/deletion

## Monitoring and Logging

Set up monitoring for:
- OAuth success rate
- OAuth failure reasons
- Time to complete auth flow
- Profile creation success rate
- Session duration
- Error types and frequency

## Success Criteria

OAuth integration is successful when:
- ✅ 95%+ success rate for OAuth flows
- ✅ < 3 seconds total auth time
- ✅ Zero security vulnerabilities
- ✅ Works across all supported browsers
- ✅ Proper error handling for all edge cases
- ✅ Session persistence works reliably
- ✅ User data accurately captured
- ✅ No data leakage or security issues

## Reporting Issues

When reporting OAuth issues, include:
1. Browser and version
2. Steps to reproduce
3. Expected vs actual behavior
4. Console errors (if any)
5. Network tab screenshots
6. User email (for database checks)
7. Timestamp of issue

## Resources

- [Supabase Auth Logs](https://supabase.com/dashboard/project/_/auth/logs)
- [Google OAuth Playground](https://developers.google.com/oauthplayground/)
- [JWT Debugger](https://jwt.io/)
