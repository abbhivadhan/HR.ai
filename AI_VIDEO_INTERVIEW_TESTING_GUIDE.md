# 🎥 AI Video Interview - Testing Guide

## Overview
Complete guide for testing the AI Video Interview feature.

---

## Prerequisites

### Frontend Requirements:
- Node.js 18+
- Modern browser with:
  - Camera access
  - Microphone access
  - Web Speech API support (Chrome, Edge recommended)
  - Speech Recognition API support

### Backend Requirements:
- Python 3.9+
- Required packages:
  ```bash
  pip install textblob numpy
  python -m textblob.download_corpora
  ```

---

## Setup Instructions

### 1. Backend Setup

```bash
cd backend

# Install dependencies
pip install -r requirements.txt

# Download TextBlob corpora
python -m textblob.download_corpora

# Start the server
python simple_server.py
```

Backend should be running on `http://localhost:8000`

### 2. Frontend Setup

```bash
cd frontend

# Install dependencies (if not already done)
npm install

# Start development server
npm run dev
```

Frontend should be running on `http://localhost:3000`

---

## Testing the Feature

### Step 1: Access the Interview Page

Navigate to:
```
http://localhost:3000/interviews/ai-video/test-123
```

(Replace `test-123` with any interview ID)

### Step 2: Setup Screen

1. Click "Start Interview"
2. Allow camera and microphone permissions when prompted
3. Verify your video feed appears

### Step 3: Interview Flow

**Question 1: Introduction**
- AI speaks: "Hello! I'm Alex, your AI interviewer..."
- Wait for AI to finish speaking
- Speak your response (you have 2 minutes)
- Your words appear in real-time transcript
- Click "Stop Recording" or wait for timer to end

**Questions 2-5:**
- Same flow repeats for each question
- Progress bar shows completion percentage
- Each question has different time limits

### Step 4: Analysis Screen

After completing all 5 questions:
- View overall score (0-100%)
- See detailed metrics:
  - Total words spoken
  - Speaking rate (words per minute)
  - Total duration
- Review question-by-question analysis
- Check strengths and areas for improvement
- Read personalized recommendations

---

## Features to Test

### ✅ Camera & Microphone
- [ ] Camera permission request works
- [ ] Video feed displays correctly
- [ ] Microphone permission request works
- [ ] Audio is captured

### ✅ AI Avatar
- [ ] Avatar displays correctly
- [ ] Eyes blink naturally
- [ ] Mouth moves when AI speaks
- [ ] Status indicators show (Speaking/Listening)
- [ ] Animations are smooth

### ✅ Speech Recognition
- [ ] Transcript appears in real-time
- [ ] Words are captured accurately
- [ ] Timer counts down correctly
- [ ] Manual stop button works
- [ ] Auto-stop at time limit works

### ✅ AI Analysis
- [ ] Response analysis completes
- [ ] Scores are calculated
- [ ] Metrics are accurate
- [ ] Feedback is relevant
- [ ] Full interview analysis works

### ✅ UI/UX
- [ ] Gradient background displays
- [ ] Animations are smooth
- [ ] Progress bar updates
- [ ] State transitions work
- [ ] Buttons are responsive
- [ ] Mobile responsive (if applicable)

---

## Browser Compatibility

### Recommended:
- ✅ Chrome 90+ (Best support)
- ✅ Edge 90+ (Best support)

### Supported:
- ⚠️ Safari 14+ (Limited speech recognition)
- ⚠️ Firefox 88+ (Limited speech recognition)

### Not Supported:
- ❌ Internet Explorer
- ❌ Older mobile browsers

---

## Common Issues & Solutions

### Issue: "Speech recognition not available"
**Solution:** Use Chrome or Edge browser

### Issue: Camera/microphone not working
**Solution:** 
1. Check browser permissions
2. Ensure no other app is using camera/mic
3. Try HTTPS instead of HTTP (required by some browsers)

### Issue: AI voice not speaking
**Solution:**
1. Check browser volume
2. Ensure Web Speech API is supported
3. Try refreshing the page

### Issue: Transcript not appearing
**Solution:**
1. Speak clearly and loudly
2. Check microphone permissions
3. Ensure Speech Recognition API is enabled

### Issue: Analysis not loading
**Solution:**
1. Check backend is running
2. Verify API endpoint is accessible
3. Check browser console for errors

---

## API Endpoints

### Analyze Single Response
```bash
POST /api/interviews/ai-video/analyze-response
Content-Type: application/json
Authorization: Bearer <token>

{
  "transcript": "Your response text here",
  "question": "The question asked",
  "duration": 120,
  "question_type": "behavioral"
}
```

### Analyze Full Interview
```bash
POST /api/interviews/ai-video/analyze-full-interview
Content-Type: application/json
Authorization: Bearer <token>

{
  "interview_id": "uuid-here",
  "responses": [
    {
      "questionId": 1,
      "question": "Question text",
      "answer": "Answer text",
      "analysis": {...}
    }
  ]
}
```

### Get Saved Analysis
```bash
GET /api/interviews/ai-video/{interview_id}/analysis
Authorization: Bearer <token>
```

---

## Testing Checklist

### Functional Testing
- [ ] Complete full interview flow
- [ ] Test all 5 questions
- [ ] Verify analysis accuracy
- [ ] Test with different response lengths
- [ ] Test with technical vs non-technical answers

### Performance Testing
- [ ] Check page load time
- [ ] Monitor memory usage during interview
- [ ] Verify smooth animations
- [ ] Test with slow network

### Edge Cases
- [ ] Test with no response (silence)
- [ ] Test with very short responses
- [ ] Test with very long responses
- [ ] Test stopping early
- [ ] Test browser refresh during interview

### Accessibility
- [ ] Test keyboard navigation
- [ ] Check screen reader compatibility
- [ ] Verify color contrast
- [ ] Test with browser zoom

---

## Sample Test Responses

### Good Response (High Score):
```
"I have over 5 years of experience in software development, 
specializing in full-stack web applications. I'm proficient 
in React, Node.js, and Python. In my previous role, I led 
a team of 4 developers and successfully delivered a major 
e-commerce platform that increased sales by 30%. I'm passionate 
about clean code and user experience."
```

### Average Response (Medium Score):
```
"Um, I've worked on, like, several projects. I know JavaScript 
and stuff. I think I'm pretty good at coding. I've done some 
web development and, you know, worked with teams before."
```

### Poor Response (Low Score):
```
"Uh... I don't know... maybe... I guess I've done some coding..."
```

---

## Metrics Explanation

### Overall Score (0-100%)
- 80-100: Excellent
- 60-79: Good
- 40-59: Average
- 0-39: Needs Improvement

### Words Per Minute (WPM)
- 120-160: Ideal speaking pace
- <120: Too slow
- >160: Too fast

### Clarity Score (0-100)
- Based on sentence structure
- Presence of transition words
- Average sentence length

### Confidence Score (0-100)
- Confident words: "definitely", "certainly"
- Uncertain words: "maybe", "perhaps"

### Structure Score (0-100)
- Introduction present
- Examples provided
- Conclusion present

---

## Next Steps

After testing:
1. Report any bugs or issues
2. Suggest improvements
3. Test on different devices
4. Gather user feedback
5. Optimize performance

---

## Support

For issues or questions:
- Check browser console for errors
- Review backend logs
- Test API endpoints directly
- Verify all dependencies are installed

---

**Happy Testing! 🚀**
