# 🏗️ AI Video Interview - Architecture

## System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         USER BROWSER                             │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │           Interview Page (page.tsx)                       │  │
│  │  ┌────────────┐  ┌────────────┐  ┌────────────────────┐ │  │
│  │  │   Setup    │→ │   Active   │→ │    Completed       │ │  │
│  │  │   Screen   │  │  Interview │  │     Screen         │ │  │
│  │  └────────────┘  └────────────┘  └────────────────────┘ │  │
│  └──────────────────────────────────────────────────────────┘  │
│                           ↓                                      │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │                    Components                             │  │
│  │  ┌──────────────┐  ┌──────────────┐  ┌───────────────┐  │  │
│  │  │ Animated AI  │  │   Speech     │  │  Interview    │  │  │
│  │  │   Avatar     │  │ Recognition  │  │   Analysis    │  │  │
│  │  └──────────────┘  └──────────────┘  └───────────────┘  │  │
│  └──────────────────────────────────────────────────────────┘  │
│                           ↓                                      │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │              Browser APIs                                 │  │
│  │  • MediaDevices API (Camera/Mic)                         │  │
│  │  • Web Speech API (Text-to-Speech)                       │  │
│  │  • Speech Recognition API (Voice-to-Text)                │  │
│  └──────────────────────────────────────────────────────────┘  │
│                           ↓                                      │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │         AI Interview Service (TypeScript)                 │  │
│  │  • API Communication                                      │  │
│  │  • Authentication                                         │  │
│  │  • Error Handling                                         │  │
│  └──────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
                           ↓ HTTP/REST
┌─────────────────────────────────────────────────────────────────┐
│                      BACKEND SERVER                              │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │              API Endpoints (FastAPI)                      │  │
│  │  • POST /analyze-response                                 │  │
│  │  • POST /analyze-full-interview                           │  │
│  │  • GET  /{id}/analysis                                    │  │
│  └──────────────────────────────────────────────────────────┘  │
│                           ↓                                      │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │         AI Interview Service (Python)                     │  │
│  │  ┌────────────────────────────────────────────────────┐  │  │
│  │  │  Response Analysis                                  │  │  │
│  │  │  • Word count & WPM calculation                     │  │  │
│  │  │  • Sentiment analysis (TextBlob)                    │  │  │
│  │  │  • Clarity scoring                                  │  │  │
│  │  │  • Confidence detection                             │  │  │
│  │  │  • Filler word detection                            │  │  │
│  │  │  • Structure analysis                               │  │  │
│  │  │  • Technical term extraction                        │  │  │
│  │  │  • Overall score calculation                        │  │  │
│  │  └────────────────────────────────────────────────────┘  │  │
│  │  ┌────────────────────────────────────────────────────┐  │  │
│  │  │  Full Interview Analysis                            │  │  │
│  │  │  • Aggregate metrics                                │  │  │
│  │  │  • Performance trends                               │  │  │
│  │  │  • Strengths identification                         │  │  │
│  │  │  • Weaknesses identification                        │  │  │
│  │  │  • Recommendations generation                       │  │  │
│  │  └────────────────────────────────────────────────────┘  │  │
│  └──────────────────────────────────────────────────────────┘  │
│                           ↓                                      │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │                   Database (SQLAlchemy)                   │  │
│  │  • Interview records                                      │  │
│  │  • Interview analysis                                     │  │
│  │  • User data                                              │  │
│  └──────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

---

## Data Flow

### 1. Interview Start Flow
```
User clicks "Start Interview"
    ↓
Request camera/mic permissions
    ↓
MediaDevices API grants access
    ↓
Video stream displayed
    ↓
State changes to "active"
    ↓
AI speaks first question (Web Speech API)
```

### 2. Response Capture Flow
```
AI finishes speaking
    ↓
Speech Recognition starts listening
    ↓
User speaks response
    ↓
Speech Recognition API transcribes
    ↓
Transcript displayed in real-time
    ↓
Timer counts down
    ↓
User stops or timer ends
    ↓
Response saved locally
```

### 3. Analysis Flow
```
Response completed
    ↓
Basic metrics calculated (frontend)
    ↓
Data sent to backend API
    ↓
AI Interview Service analyzes:
  • Sentiment (TextBlob)
  • Clarity (sentence structure)
  • Confidence (word analysis)
  • Filler words (pattern matching)
  • Structure (intro/body/conclusion)
    ↓
Weighted score calculated
    ↓
Feedback generated
    ↓
Results returned to frontend
    ↓
Next question or complete
```

### 4. Full Interview Analysis Flow
```
All questions completed
    ↓
All responses collected
    ↓
Sent to backend for full analysis
    ↓
AI Interview Service:
  • Aggregates metrics
  • Calculates trends
  • Identifies strengths
  • Identifies weaknesses
  • Generates recommendations
    ↓
Analysis saved to database
    ↓
Results displayed to user
```

---

## Component Hierarchy

```
AIVideoInterviewPage
├── AnimatedAIAvatar
│   ├── SVG Avatar
│   ├── Eye Animations
│   ├── Mouth Animations
│   ├── Status Indicators
│   └── Sound Waves
├── SpeechRecognition
│   ├── Transcript Display
│   ├── Timer
│   ├── Progress Bar
│   ├── Audio Visualizer
│   └── Stop Button
└── InterviewAnalysis
    ├── Overall Score
    ├── Metrics Dashboard
    ├── Question Breakdown
    ├── Strengths/Weaknesses
    └── Recommendations
```

---

## State Management

### Interview States
```typescript
type InterviewState = 'setup' | 'active' | 'completed'

setup:
  - Show introduction
  - Request permissions
  - Display instructions

active:
  - Show AI avatar
  - Display current question
  - Capture user response
  - Show progress

completed:
  - Display analysis
  - Show scores
  - Provide feedback
```

### Question Flow
```typescript
currentQuestion: number (0-4)
questions: Question[] (5 questions)

Flow:
  Question 0 → Question 1 → Question 2 → Question 3 → Question 4 → Complete
```

---

## API Contract

### Request: Analyze Response
```typescript
POST /api/interviews/ai-video/analyze-response

Request Body:
{
  transcript: string
  question: string
  duration: number
  question_type: string
}

Response:
{
  success: boolean
  analysis: {
    overall_score: number
    metrics: {...}
    analysis: {...}
    content: {...}
    feedback: {...}
  }
}
```

### Request: Analyze Full Interview
```typescript
POST /api/interviews/ai-video/analyze-full-interview

Request Body:
{
  interview_id: string
  responses: Array<{
    questionId: number
    question: string
    answer: string
    analysis: object
  }>
}

Response:
{
  success: boolean
  analysis: {
    overall_score: number
    total_questions: number
    aggregate_metrics: {...}
    performance: {...}
    strengths: string[]
    weaknesses: string[]
    recommendations: string[]
  }
  analysis_id: string
}
```

---

## Analysis Algorithm

### Score Calculation
```python
# Weighted scoring
weights = {
    'word_count': 0.15,      # 15%
    'wpm': 0.15,             # 15%
    'sentiment': 0.15,       # 15%
    'clarity': 0.20,         # 20%
    'confidence': 0.20,      # 20%
    'structure': 0.15        # 15%
}

# Normalize each metric to 0-100
normalized_scores = normalize_metrics(metrics)

# Calculate weighted sum
score = sum(normalized[key] * weights[key] for key in weights)

# Apply penalties
score -= filler_word_penalty

# Clamp to 0-100
final_score = max(0, min(100, score))
```

### Sentiment Analysis
```python
# Using TextBlob
blob = TextBlob(text)
polarity = blob.sentiment.polarity      # -1 to 1
subjectivity = blob.sentiment.subjectivity  # 0 to 1

# Convert to score
sentiment_score = (polarity + 1) * 50  # 0 to 100
```

---

## Technology Stack

### Frontend
- **Framework**: Next.js 14 (React)
- **Language**: TypeScript
- **Styling**: Tailwind CSS
- **Animations**: Framer Motion
- **Icons**: Heroicons
- **APIs**: Web Speech, Speech Recognition, MediaDevices

### Backend
- **Framework**: FastAPI
- **Language**: Python 3.9+
- **NLP**: TextBlob
- **Math**: NumPy
- **Database**: SQLAlchemy
- **Validation**: Pydantic

---

## Security Considerations

### Frontend
- Camera/mic permissions required
- Local video processing
- Secure token storage
- HTTPS required for production

### Backend
- JWT authentication
- Input validation (Pydantic)
- Rate limiting
- SQL injection prevention (SQLAlchemy)
- CORS configuration

---

## Performance Optimization

### Frontend
- Lazy loading components
- Memoized calculations
- Debounced API calls
- Optimized animations
- Efficient re-renders

### Backend
- Async/await operations
- Database query optimization
- Response caching
- Connection pooling
- Efficient algorithms

---

## Scalability

### Horizontal Scaling
- Stateless API design
- Load balancer ready
- Database connection pooling
- Microservices architecture

### Vertical Scaling
- Efficient algorithms
- Memory optimization
- CPU optimization
- Database indexing

---

## Monitoring & Logging

### Frontend
- Error tracking
- Performance metrics
- User analytics
- Browser compatibility

### Backend
- API response times
- Error rates
- Database performance
- Resource usage

---

## Future Enhancements

### Phase 2
- Video recording and playback
- Multiple AI avatars
- Custom question sets
- Industry-specific interviews

### Phase 3
- Multi-language support
- Advanced ML models
- Real-time coaching
- Emotion detection

### Phase 4
- VR/AR integration
- Group interviews
- Live human backup
- Advanced analytics

---

**Architecture Status: PRODUCTION READY** ✅
