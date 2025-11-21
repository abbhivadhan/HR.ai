# 🚀 AI Video Interview - Quick Start Guide

Get the AI Video Interview feature running in 5 minutes!

---

## Prerequisites

- Node.js 18+
- Python 3.9+
- Modern browser (Chrome/Edge recommended)
- Camera and microphone

---

## Installation

### 1. Backend Setup (2 minutes)

```bash
# Navigate to backend
cd backend

# Install Python dependencies
pip install fastapi uvicorn sqlalchemy pydantic textblob numpy python-jose passlib bcrypt

# Download TextBlob corpora (required for sentiment analysis)
python -m textblob.download_corpora

# Start the server
python simple_server.py
```

✅ Backend running at `http://localhost:8000`

### 2. Frontend Setup (2 minutes)

```bash
# Navigate to frontend
cd frontend

# Install dependencies (if not already done)
npm install

# Start development server
npm run dev
```

✅ Frontend running at `http://localhost:3000`

---

## Quick Test (1 minute)

### Open the Interview Page

Navigate to:
```
http://localhost:3000/interviews/ai-video/test-123
```

### Complete the Flow

1. **Click "Start Interview"**
2. **Allow camera/microphone** when prompted
3. **Listen to AI question**
4. **Speak your response** (or click "Stop Recording")
5. **Repeat for 5 questions**
6. **View your analysis**

---

## Troubleshooting

### Issue: "Speech recognition not available"
**Fix:** Use Chrome or Edge browser

### Issue: Camera not working
**Fix:** Check browser permissions in settings

### Issue: Backend not responding
**Fix:** Ensure backend is running on port 8000

### Issue: TextBlob error
**Fix:** Run `python -m textblob.download_corpora`

---

## File Locations

### Frontend Components:
```
frontend/src/
├── app/interviews/ai-video/[id]/page.tsx
├── components/interviews/
│   ├── AnimatedAIAvatar.tsx
│   ├── SpeechRecognition.tsx
│   └── InterviewAnalysis.tsx
└── services/aiInterviewService.ts
```

### Backend Services:
```
backend/app/
├── services/ai_interview_service.py
└── api/interviews.py
```

---

## API Endpoints

### Test with cURL:

```bash
# Analyze a response
curl -X POST http://localhost:8000/api/interviews/ai-video/analyze-response \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "transcript": "I have 5 years of experience in software development",
    "question": "Tell me about yourself",
    "duration": 60,
    "question_type": "introduction"
  }'
```

---

## Environment Variables

### Frontend (.env.local):
```env
NEXT_PUBLIC_API_URL=http://localhost:8000/api
```

### Backend (.env):
```env
DATABASE_URL=sqlite:///./ai_hr_platform.db
SECRET_KEY=your-secret-key-here
```

---

## Browser Requirements

### ✅ Fully Supported:
- Chrome 90+
- Edge 90+

### ⚠️ Partially Supported:
- Safari 14+ (limited speech recognition)
- Firefox 88+ (limited speech recognition)

### ❌ Not Supported:
- Internet Explorer
- Older mobile browsers

---

## Development Tips

### Hot Reload:
Both frontend and backend support hot reload. Changes are reflected immediately.

### Debug Mode:
Open browser console (F12) to see detailed logs.

### Mock Data:
The frontend service includes mock data for offline development.

### Testing:
Use different response lengths and styles to test the analysis algorithm.

---

## Next Steps

1. ✅ Read `AI_VIDEO_INTERVIEW_IMPLEMENTATION.md` for details
2. ✅ Follow `AI_VIDEO_INTERVIEW_TESTING_GUIDE.md` for testing
3. ✅ Review `AI_VIDEO_INTERVIEW_ARCHITECTURE.md` for architecture
4. ✅ Check `AI_VIDEO_INTERVIEW_COMPLETION_SUMMARY.md` for overview

---

## Quick Commands

### Start Everything:
```bash
# Terminal 1 - Backend
cd backend && python simple_server.py

# Terminal 2 - Frontend
cd frontend && npm run dev
```

### Stop Everything:
```bash
# Press Ctrl+C in both terminals
```

### Reset Database:
```bash
cd backend
rm ai_hr_platform.db
python simple_server.py  # Will recreate
```

---

## Support

### Documentation:
- Implementation Guide
- Testing Guide
- Architecture Guide
- Completion Summary

### Common Issues:
- Check browser console for errors
- Verify backend is running
- Ensure dependencies are installed
- Test API endpoints directly

---

## Success Checklist

- [ ] Backend running on port 8000
- [ ] Frontend running on port 3000
- [ ] Camera permission granted
- [ ] Microphone permission granted
- [ ] AI voice speaking
- [ ] Speech recognition working
- [ ] Transcript appearing
- [ ] Analysis displaying

---

**Ready to go! Start interviewing! 🎉**

---

## Quick Reference

### Interview Questions (5 total):
1. Introduction (120s)
2. Challenging project (180s)
3. Technical skills (120s)
4. Situational problem (150s)
5. Career goals (120s)

### Analysis Metrics:
- Overall Score (0-100%)
- Word Count
- Words Per Minute
- Sentiment
- Clarity
- Confidence
- Structure

### Ideal Metrics:
- WPM: 120-160
- Word Count: 50-200
- Filler Ratio: <3%
- Sentiment: Positive

---

**Total Setup Time: ~5 minutes**
**First Interview: ~10 minutes**
**Full Testing: ~30 minutes**

---

*Happy interviewing! 🚀*
