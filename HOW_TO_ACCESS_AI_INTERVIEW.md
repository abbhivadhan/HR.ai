# 🎯 How to Access AI Video Interview

## Quick Access Methods

### Method 1: Direct URL (Fastest) ⚡
Simply navigate to:
```
http://localhost:3000/interviews/ai-video/demo-123
```
Replace `demo-123` with any ID you want.

### Method 2: From Dashboard 📊
1. Start the servers (see below)
2. Login to your account
3. Go to **Dashboard** → **Interviews**
4. Click the **"Try AI Interview"** button (purple gradient button)

### Method 3: From Homepage 🏠
1. Navigate to `http://localhost:3000`
2. Login or Register
3. Access from your dashboard

---

## Starting the Servers

### Terminal 1 - Backend:
```bash
cd backend
python simple_server.py
```
✅ Backend runs on `http://localhost:8000`

### Terminal 2 - Frontend:
```bash
cd frontend
npm run dev
```
✅ Frontend runs on `http://localhost:3000`

---

## Browser Requirements

### ✅ Best Experience:
- **Chrome 90+** (Recommended)
- **Edge 90+** (Recommended)

### ⚠️ Limited Support:
- Safari 14+ (speech recognition may not work)
- Firefox 88+ (speech recognition may not work)

---

## Permissions Required

When you start the interview, you'll be asked to allow:
1. **Camera access** - To record your video
2. **Microphone access** - To capture your voice

Click "Allow" when prompted.

---

## Quick Test Flow

1. **Open**: `http://localhost:3000/interviews/ai-video/test-123`
2. **Click**: "Start Interview"
3. **Allow**: Camera and microphone permissions
4. **Listen**: AI speaks the first question
5. **Speak**: Your response (or click "Stop Recording")
6. **Repeat**: For all 5 questions
7. **View**: Your analysis and scores

---

## Troubleshooting

### "Page not found"
- Make sure frontend is running on port 3000
- Check the URL is correct

### "Camera/Mic not working"
- Check browser permissions
- Use Chrome or Edge
- Ensure no other app is using camera/mic

### "AI not speaking"
- Check browser volume
- Refresh the page
- Try Chrome or Edge

### "Speech recognition not working"
- Use Chrome or Edge (best support)
- Speak clearly and loudly
- Check microphone permissions

---

## Demo Credentials

If you need to login:
```
Email: demo@example.com
Password: demo123
```

Or register a new account at:
```
http://localhost:3000/auth/register
```

---

## What to Expect

### Interview Questions (5 total):
1. **Introduction** (2 minutes) - Tell me about yourself
2. **Behavioral** (3 minutes) - Challenging project experience
3. **Technical** (2 minutes) - Technical skills discussion
4. **Situational** (2.5 minutes) - Problem-solving scenario
5. **Career** (2 minutes) - Career goals

### Analysis You'll Get:
- Overall score (0-100%)
- Words spoken
- Speaking rate (WPM)
- Sentiment analysis
- Clarity score
- Confidence level
- Strengths identified
- Areas for improvement
- Personalized recommendations

---

## Quick Links

### Documentation:
- 📖 [Implementation Guide](./AI_VIDEO_INTERVIEW_IMPLEMENTATION.md)
- 🧪 [Testing Guide](./AI_VIDEO_INTERVIEW_TESTING_GUIDE.md)
- 🏗️ [Architecture](./AI_VIDEO_INTERVIEW_ARCHITECTURE.md)
- 🚀 [Quick Start](./AI_VIDEO_INTERVIEW_QUICKSTART.md)
- ✅ [Completion Summary](./AI_VIDEO_INTERVIEW_COMPLETION_SUMMARY.md)

### Direct Access URLs:
```
Main Interview:     http://localhost:3000/interviews/ai-video/demo-123
Dashboard:          http://localhost:3000/dashboard
Interviews Page:    http://localhost:3000/dashboard/interviews
Login:              http://localhost:3000/auth/login
Register:           http://localhost:3000/auth/register
```

---

## Tips for Best Experience

1. **Use headphones** - Prevents echo
2. **Good lighting** - For better video quality
3. **Quiet environment** - For better speech recognition
4. **Speak clearly** - For accurate transcription
5. **Take your time** - No need to rush

---

## Need Help?

Check the documentation files or:
1. Open browser console (F12) for errors
2. Check backend logs in terminal
3. Verify both servers are running
4. Try a different browser (Chrome recommended)

---

**Ready to start? Go to:** `http://localhost:3000/interviews/ai-video/demo-123` 🚀
