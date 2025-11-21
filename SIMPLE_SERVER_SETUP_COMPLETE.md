# ✅ Simple Server with Google OAuth - Setup Complete!

## 🎉 What's Been Done

Your AI-HR Platform is now configured to use the **simple_server.py** backend with Google OAuth support. No Supabase required!

## 📦 What Was Created/Modified

### New Files
- ✅ `frontend/src/contexts/AuthContextSimple.tsx` - Auth context for simple server
- ✅ `backend/simple_server.py` - Updated with Google OAuth endpoint
- ✅ `SIMPLE_SERVER_GOOGLE_AUTH_GUIDE.md` - Complete usage guide
- ✅ `start-simple-server.sh` - One-command startup script
- ✅ `SIMPLE_SERVER_SETUP_COMPLETE.md` - This file

### Modified Files
- ✅ `frontend/.env.local` - Points to simple server (localhost:8000)
- ✅ `frontend/src/app/layout.tsx` - Uses AuthContextSimple

## 🚀 How to Start

### Option 1: Use the Startup Script (Easiest)

```bash
./start-simple-server.sh
```

This starts both backend and frontend automatically!

### Option 2: Manual Start

**Terminal 1 - Backend:**
```bash
cd backend
python3 simple_server.py
```

**Terminal 2 - Frontend:**
```bash
cd frontend
npm run dev
```

## 🎯 Quick Test

1. **Open**: http://localhost:3000/auth/login
2. **Click**: "Sign in with Google"
3. **See**: Mock Google OAuth popup
4. **Use**: Pre-filled test data (or change it)
5. **Click**: "Sign In with Google"
6. **Done**: You're logged in!

## ✨ Features Available

### Email/Password Authentication
- ✅ User registration
- ✅ User login
- ✅ JWT tokens
- ✅ Session persistence

### Google OAuth Authentication
- ✅ Mock Google OAuth flow
- ✅ Popup-based authentication
- ✅ Automatic user creation
- ✅ Pre-verified accounts
- ✅ OAuth provider tracking

### User Management
- ✅ In-memory user database
- ✅ User profile storage
- ✅ Multiple user types (Candidate/Company)
- ✅ View all users endpoint

## 📊 API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | API status |
| `/docs` | GET | Interactive API docs |
| `/api/auth/register` | POST | Register with email/password |
| `/api/auth/login` | POST | Login with email/password |
| `/api/auth/google` | POST | Login/register with Google |
| `/api/users` | GET | List all users |
| `/api/users/profile` | GET | Get current user |

## 🔍 Testing the Setup

### Test 1: Backend is Running
```bash
curl http://localhost:8000
# Should return: {"message": "Simple AI-HR Platform API is running"}
```

### Test 2: API Documentation
Open: http://localhost:8000/docs
- Should see interactive Swagger UI
- Can test endpoints directly

### Test 3: Frontend is Running
Open: http://localhost:3000
- Should see homepage
- Navigation should work

### Test 4: Email/Password Registration
1. Go to: http://localhost:3000/auth/register
2. Fill in form
3. Submit
4. Should be logged in

### Test 5: Google OAuth
1. Go to: http://localhost:3000/auth/login
2. Click "Sign in with Google"
3. Popup opens with mock form
4. Submit
5. Should be logged in

### Test 6: Session Persistence
1. Log in
2. Refresh page
3. Should still be logged in
4. Navigate to different pages
5. Session persists

### Test 7: Logout
1. While logged in, click logout
2. Should redirect to home/login
3. Try accessing /dashboard
4. Should redirect to login

## 💾 Data Storage

### Current Setup
- **Type**: In-memory dictionary
- **Persistence**: None (data lost on restart)
- **Perfect for**: Development and testing
- **Not for**: Production

### View Stored Users
```bash
curl http://localhost:8000/api/users
```

Or visit: http://localhost:8000/api/users

## 🔧 Configuration

### Backend Configuration
**File**: `backend/simple_server.py`
- Port: 8000
- CORS: localhost:3000, localhost:3001
- Token expiry: 30 minutes (access), 7 days (refresh)
- Storage: In-memory

### Frontend Configuration
**File**: `frontend/.env.local`
```bash
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_APP_URL=http://localhost:3000
```

**File**: `frontend/src/app/layout.tsx`
```typescript
import { AuthProvider } from '@/contexts/AuthContextSimple'
```

## 🎨 Google OAuth Flow

### How It Works

```
1. User clicks "Sign in with Google"
   ↓
2. Popup opens with mock Google form
   ↓
3. User enters/confirms email, name
   ↓
4. Data sent to backend via postMessage
   ↓
5. Backend creates/retrieves user
   ↓
6. Backend returns JWT tokens
   ↓
7. Frontend stores tokens
   ↓
8. User logged in and redirected
```

### Mock OAuth Popup

The popup shows:
- Email field (pre-filled: test@gmail.com)
- First Name field (pre-filled: Test)
- Last Name field (pre-filled: User)
- "Sign In with Google" button

You can change these values for testing different users!

## 📚 Documentation

### Main Guide
**SIMPLE_SERVER_GOOGLE_AUTH_GUIDE.md** - Complete usage guide
- Setup instructions
- API documentation
- Testing procedures
- Troubleshooting
- Customization options

### Google OAuth Guides (For Supabase)
If you want to switch to real Google OAuth with Supabase:
- GOOGLE_AUTH_SETUP_GUIDE.md
- GOOGLE_AUTH_QUICK_START.md
- GOOGLE_AUTH_TESTING.md

## 🔄 Switching to Supabase

When you're ready for production:

### 1. Update .env.local
```bash
NEXT_PUBLIC_SUPABASE_URL=https://your-project.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=your-anon-key
NEXT_PUBLIC_API_URL=https://your-project.supabase.co
```

### 2. Update layout.tsx
```typescript
import { AuthProvider } from '@/contexts/AuthContext'
```

### 3. Follow Setup Guide
See: GOOGLE_AUTH_SETUP_GUIDE.md

## 🐛 Troubleshooting

### Backend won't start
```bash
# Install dependencies
pip install fastapi uvicorn python-jose

# Try starting manually
cd backend
python3 simple_server.py
```

### Frontend won't start
```bash
# Install dependencies
cd frontend
npm install

# Try starting manually
npm run dev
```

### Can't connect to backend
1. Check backend is running: http://localhost:8000
2. Check .env.local has correct API_URL
3. Restart both servers

### Google OAuth popup blocked
1. Allow popups for localhost:3000
2. Check browser popup settings
3. Try again

## 💡 Tips

1. **Keep backend running**: Data is lost on restart
2. **Use API docs**: http://localhost:8000/docs for testing
3. **Check console**: Both frontend and backend logs
4. **Test incrementally**: One feature at a time
5. **Mock data**: Perfect for testing different scenarios

## ⚡ Quick Commands

```bash
# Start everything
./start-simple-server.sh

# Start backend only
cd backend && python3 simple_server.py

# Start frontend only
cd frontend && npm run dev

# View API docs
open http://localhost:8000/docs

# View frontend
open http://localhost:3000

# Test API
curl http://localhost:8000

# View users
curl http://localhost:8000/api/users
```

## 📈 What's Next?

### For Development
- ✅ Keep using simple server
- ✅ Test authentication flows
- ✅ Build features
- ✅ Iterate quickly

### For Production
- 🔄 Switch to Supabase
- 🔄 Set up real Google OAuth
- 🔄 Add database
- 🔄 Deploy to production

## ✅ Success Checklist

- [ ] Backend running on port 8000
- [ ] Frontend running on port 3000
- [ ] Can access http://localhost:8000/docs
- [ ] Can access http://localhost:3000
- [ ] Email/password registration works
- [ ] Email/password login works
- [ ] Google OAuth mock works
- [ ] Session persists on refresh
- [ ] Logout works
- [ ] Can view users at /api/users

## 🎓 Learning Resources

- **FastAPI**: https://fastapi.tiangolo.com/
- **JWT**: https://jwt.io/
- **OAuth 2.0**: https://oauth.net/2/
- **React Context**: https://react.dev/reference/react/useContext

## 🆘 Need Help?

1. Check SIMPLE_SERVER_GOOGLE_AUTH_GUIDE.md
2. Check browser console for errors
3. Check backend terminal for errors
4. Visit http://localhost:8000/docs to test API
5. Verify both servers are running

---

## 🎉 You're All Set!

Your simple server is running with Google OAuth support. Perfect for development and testing!

**Start developing**: http://localhost:3000  
**Test API**: http://localhost:8000/docs  
**View users**: http://localhost:8000/api/users

Happy coding! 🚀
