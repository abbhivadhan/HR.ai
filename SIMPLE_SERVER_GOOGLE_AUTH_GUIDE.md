# Simple Server with Google OAuth - Quick Setup Guide

## 🎯 Overview

This guide shows you how to use the **simple_server.py** backend with Google OAuth authentication. No Supabase required! Perfect for testing and development.

## ✨ Features

- ✅ In-memory user database (no external DB needed)
- ✅ Email/password authentication
- ✅ Google OAuth authentication (mock flow for testing)
- ✅ JWT token generation
- ✅ CORS enabled for frontend
- ✅ FastAPI with automatic API docs

## 🚀 Quick Start (2 Minutes)

### 1. Start the Backend Server

```bash
# Navigate to backend directory
cd backend

# Install dependencies (if not already installed)
pip install fastapi uvicorn python-jose

# Start the server
python simple_server.py
```

You should see:
```
============================================================
Simple AI-HR Platform API Server
============================================================
Server running at: http://localhost:8000
API Docs: http://localhost:8000/docs
============================================================
```

### 2. Start the Frontend

```bash
# In a new terminal, navigate to frontend
cd frontend

# Start the dev server
npm run dev
```

### 3. Test It!

1. Open http://localhost:3000/auth/login
2. Try email/password login OR
3. Click "Sign in with Google" for mock OAuth flow

## 📁 Configuration

### Backend (simple_server.py)

The server is already configured and ready to use:
- **Port**: 8000
- **CORS**: Allows localhost:3000 and localhost:3001
- **Storage**: In-memory (resets on restart)
- **Auth**: JWT tokens with 30-minute expiry

### Frontend (.env.local)

Already configured to use simple server:
```bash
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_APP_URL=http://localhost:3000
```

### Frontend (layout.tsx)

Already configured to use simple auth:
```typescript
import { AuthProvider } from '@/contexts/AuthContextSimple'
```

## 🔐 Authentication Flows

### Email/Password Authentication

**Register:**
```bash
POST http://localhost:8000/api/auth/register
{
  "email": "user@example.com",
  "password": "password123",
  "firstName": "John",
  "lastName": "Doe",
  "userType": "CANDIDATE"
}
```

**Login:**
```bash
POST http://localhost:8000/api/auth/login
{
  "email": "user@example.com",
  "password": "password123"
}
```

**Response:**
```json
{
  "access_token": "eyJhbGc...",
  "refresh_token": "eyJhbGc...",
  "token_type": "bearer",
  "user": {
    "id": "1",
    "email": "user@example.com",
    "firstName": "John",
    "lastName": "Doe",
    "userType": "CANDIDATE",
    "isVerified": true
  }
}
```

### Google OAuth Authentication

**How it works:**

1. User clicks "Sign in with Google"
2. A popup window opens with a mock Google login form
3. User enters email, first name, last name (pre-filled for testing)
4. Data is sent to backend via POST /api/auth/google
5. Backend creates/retrieves user and returns tokens
6. User is logged in

**Mock OAuth Endpoint:**
```bash
POST http://localhost:8000/api/auth/google
{
  "email": "test@gmail.com",
  "firstName": "Test",
  "lastName": "User",
  "googleId": "google_123456",
  "userType": "CANDIDATE"
}
```

**Response:**
```json
{
  "access_token": "eyJhbGc...",
  "refresh_token": "eyJhbGc...",
  "token_type": "bearer",
  "user": {
    "id": "2",
    "email": "test@gmail.com",
    "firstName": "Test",
    "lastName": "User",
    "userType": "CANDIDATE",
    "isVerified": true,
    "oauthProvider": "google",
    "oauthProviderId": "google_123456"
  }
}
```

## 🧪 Testing

### Test Email/Password Flow

1. Go to http://localhost:3000/auth/register
2. Fill in the form:
   - Email: test@example.com
   - Password: password123
   - First Name: Test
   - Last Name: User
   - User Type: Candidate
3. Click "Create Account"
4. You should be logged in and redirected to dashboard

### Test Google OAuth Flow

1. Go to http://localhost:3000/auth/login
2. Click "Sign in with Google"
3. A popup opens with mock Google login
4. Default values are pre-filled:
   - Email: test@gmail.com
   - First Name: Test
   - Last Name: User
5. Click "Sign In with Google"
6. Popup closes and you're logged in

### Test Session Persistence

1. Log in with either method
2. Refresh the page (F5)
3. You should still be logged in
4. Navigate to different pages
5. Session persists

### Test Logout

1. While logged in, click logout
2. You should be redirected to home/login
3. Try accessing /dashboard
4. You should be redirected to login

## 📊 API Endpoints

### Authentication

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/auth/register` | Register new user |
| POST | `/api/auth/login` | Login with email/password |
| POST | `/api/auth/google` | Login/register with Google |
| GET | `/api/auth/google/url` | Get Google OAuth URL (future) |

### Users

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/users` | List all users (testing only) |
| GET | `/api/users/profile` | Get current user profile |

### Documentation

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | API status |
| GET | `/docs` | Interactive API documentation |
| GET | `/redoc` | Alternative API documentation |

## 🔍 Viewing API Documentation

FastAPI provides automatic interactive documentation:

1. **Swagger UI**: http://localhost:8000/docs
   - Interactive API testing
   - Try out endpoints directly
   - See request/response schemas

2. **ReDoc**: http://localhost:8000/redoc
   - Clean, readable documentation
   - Better for reference

## 💾 Data Storage

### In-Memory Database

The simple server uses an in-memory dictionary for user storage:

```python
users_db = {
  "user@example.com": {
    "id": "1",
    "email": "user@example.com",
    "password_hash": "...",
    "firstName": "John",
    "lastName": "Doe",
    "userType": "CANDIDATE",
    "isVerified": true
  }
}
```

**Important Notes:**
- Data is lost when server restarts
- Perfect for testing
- Not suitable for production
- No database setup required

### Viewing Stored Users

```bash
# List all users
curl http://localhost:8000/api/users
```

Or visit http://localhost:8000/api/users in your browser.

## 🔧 Customization

### Change Server Port

Edit `simple_server.py`:
```python
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)  # Change port here
```

Then update frontend `.env.local`:
```bash
NEXT_PUBLIC_API_URL=http://localhost:8080
```

### Add More CORS Origins

Edit `simple_server.py`:
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:3001",
        "http://localhost:3002",  # Add more origins
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### Change Token Expiry

Edit `simple_server.py`:
```python
# Access token (default: 30 minutes)
access_token_expires = timedelta(minutes=60)  # Change to 1 hour

# Refresh token (default: 7 days)
refresh_token = create_access_token(
    data={"sub": user["email"], "type": "refresh"}, 
    expires_delta=timedelta(days=30)  # Change to 30 days
)
```

## 🐛 Troubleshooting

### Server won't start

**Error**: `ModuleNotFoundError: No module named 'fastapi'`

**Solution**:
```bash
pip install fastapi uvicorn python-jose
```

### Frontend can't connect to backend

**Error**: Network error or CORS error

**Solution**:
1. Check backend is running: http://localhost:8000
2. Check CORS origins in `simple_server.py`
3. Check `NEXT_PUBLIC_API_URL` in `.env.local`
4. Restart both servers

### Google OAuth popup blocked

**Error**: Popup blocked by browser

**Solution**:
1. Allow popups for localhost:3000
2. Try clicking the button again
3. Check browser popup settings

### Users not persisting

**Issue**: Users disappear after server restart

**Explanation**: This is expected! The simple server uses in-memory storage. Data is lost on restart.

**Solution**: For persistent storage, use Supabase or a real database.

## 🔄 Switching Between Simple Server and Supabase

### To Use Simple Server (Current Setup)

**frontend/.env.local:**
```bash
NEXT_PUBLIC_API_URL=http://localhost:8000
```

**frontend/src/app/layout.tsx:**
```typescript
import { AuthProvider } from '@/contexts/AuthContextSimple'
```

### To Use Supabase

**frontend/.env.local:**
```bash
NEXT_PUBLIC_SUPABASE_URL=https://your-project.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=your-anon-key
NEXT_PUBLIC_API_URL=https://your-project.supabase.co
```

**frontend/src/app/layout.tsx:**
```typescript
import { AuthProvider } from '@/contexts/AuthContext'
```

Then restart the frontend.

## 📈 Advantages of Simple Server

✅ **No Setup Required**: No database, no Supabase account
✅ **Fast Development**: Instant startup, no migrations
✅ **Easy Testing**: Clear, simple code
✅ **Portable**: Works anywhere Python runs
✅ **Learning**: Great for understanding auth flows
✅ **Debugging**: Easy to add console logs and inspect

## ⚠️ Limitations

❌ **No Persistence**: Data lost on restart
❌ **No Scalability**: Single server, in-memory only
❌ **No Real OAuth**: Mock Google OAuth for testing
❌ **No Security**: Simplified for development
❌ **No Features**: No password reset, email verification, etc.

## 🚀 Production Considerations

For production, you should:
1. Use a real database (PostgreSQL, MongoDB, etc.)
2. Implement real Google OAuth with Google Cloud
3. Add proper security measures
4. Use environment variables for secrets
5. Add rate limiting
6. Implement proper error handling
7. Add logging and monitoring
8. Use HTTPS
9. Add input validation
10. Implement proper session management

## 📚 Next Steps

### For Development
- Keep using simple server for quick testing
- Add more mock endpoints as needed
- Test authentication flows

### For Production
- Switch to Supabase (see GOOGLE_AUTH_SETUP_GUIDE.md)
- Or implement full backend with database
- Set up real Google OAuth
- Deploy to production environment

## 🎓 Learning Resources

- **FastAPI Docs**: https://fastapi.tiangolo.com/
- **JWT Tokens**: https://jwt.io/
- **OAuth 2.0**: https://oauth.net/2/
- **Python Jose**: https://python-jose.readthedocs.io/

## 💡 Tips

1. **Keep server running**: Don't restart unless needed (data will be lost)
2. **Use API docs**: http://localhost:8000/docs for testing
3. **Check console**: Both frontend and backend logs are helpful
4. **Test incrementally**: Test each feature as you build
5. **Mock data**: Pre-populate users for testing if needed

## 🆘 Getting Help

If you encounter issues:
1. Check both terminal outputs (frontend and backend)
2. Check browser console for errors
3. Visit http://localhost:8000/docs to test API directly
4. Check that both servers are running
5. Verify .env.local configuration

## ✅ Quick Checklist

- [ ] Backend server running on port 8000
- [ ] Frontend server running on port 3000
- [ ] .env.local points to http://localhost:8000
- [ ] layout.tsx imports AuthContextSimple
- [ ] Can access http://localhost:8000/docs
- [ ] Can access http://localhost:3000
- [ ] Email/password login works
- [ ] Google OAuth mock works
- [ ] Session persists on refresh
- [ ] Logout works

---

**You're all set!** The simple server is perfect for development and testing. When you're ready for production, follow the Supabase guides to set up a real backend.
