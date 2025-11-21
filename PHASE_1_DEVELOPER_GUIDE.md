# Phase 1 Developer Guide

## Quick Start

### Prerequisites
```bash
# Install dependencies
cd backend
pip install openai boto3

# Set environment variables
export OPENAI_API_KEY="your_key_here"
export AWS_ACCESS_KEY_ID="your_key" # Optional
export AWS_SECRET_ACCESS_KEY="your_secret" # Optional
```

### Run Migration
```bash
cd backend
alembic upgrade head
```

### Start Server
```bash
uvicorn app.main:app --reload
```

---

## API Overview

### Base URL
```
http://localhost:8000
```

### Authentication
All endpoints require Bearer token:
```bash
Authorization: Bearer YOUR_JWT_TOKEN
```

---

## Feature 1: AI Career Coach

### Create Career Plan
```bash
POST /api/career-coach/plans
{
  "current_role": "Software Engineer",
  "target_role": "Senior Software Engineer",
  "target_salary": 150000,
  "timeline_months": 12
}
```

### Start Conversation
```bash
POST /api/career-coach/conversations
{
  "career_plan_id": 1,
  "topic": "Skill Development",
  "initial_message": "What skills should I focus on?"
}
```

### Chat with AI
```bash
POST /api/career-coach/chat
{
  "conversation_id": 1,
  "message": "How can I improve my leadership skills?"
}
```

### Get Career Recommendations
```bash
GET /api/career-coach/plans/1/recommendations
```

### Get Salary Insights
```bash
GET /api/career-coach/salary-insights?role=Senior%20Engineer&location=San%20Francisco
```

---

## Feature 2: Video Resume & Portfolio

### Get My Portfolio
```bash
GET /api/portfolio/me
```

### Update Portfolio
```bash
PUT /api/portfolio/me
{
  "headline": "Full Stack Developer",
  "bio": "Passionate about building great products",
  "is_public": true
}
```

### Get Video Upload URL
```bash
POST /api/portfolio/video-upload
{
  "file_name": "intro.mp4",
  "file_size": 5242880,
  "content_type": "video/mp4"
}
```

### Add Project
```bash
POST /api/portfolio/projects
{
  "title": "E-commerce Platform",
  "description": "Built a scalable e-commerce platform",
  "technologies": ["React", "Node.js", "PostgreSQL"],
  "live_url": "https://example.com",
  "github_url": "https://github.com/user/project"
}
```

### Add Achievement
```bash
POST /api/portfolio/achievements
{
  "badge_type": "certification",
  "title": "AWS Certified Solutions Architect",
  "issuer": "Amazon Web Services",
  "date_earned": "2024-01-15T00:00:00Z"
}
```

---

## Feature 3: Smart Scheduling

### Get Preferences
```bash
GET /api/scheduling/preferences
```

### Update Preferences
```bash
PUT /api/scheduling/preferences
{
  "timezone": "America/New_York",
  "buffer_minutes": 15,
  "working_hours": {
    "monday": {"start": "09:00", "end": "17:00"},
    "tuesday": {"start": "09:00", "end": "17:00"}
  }
}
```

### Find Optimal Times
```bash
POST /api/scheduling/find-times
{
  "participant_ids": [2, 3],
  "duration_minutes": 60,
  "preferred_dates": ["2024-11-01T00:00:00Z", "2024-11-02T00:00:00Z"],
  "timezone": "UTC"
}
```

### Create Event
```bash
POST /api/scheduling/events
{
  "participant_id": 2,
  "title": "Technical Interview",
  "start_time": "2024-11-01T14:00:00Z",
  "end_time": "2024-11-01T15:00:00Z",
  "meeting_url": "https://zoom.us/j/123456"
}
```

---

## Feature 4: AI Resume Builder

### Create Resume
```bash
POST /api/resume-builder/resumes
{
  "title": "Software Engineer Resume",
  "template_id": "professional",
  "content": {
    "summary": "Experienced software engineer...",
    "experience": [...],
    "education": [...],
    "skills": [...]
  }
}
```

### Get AI Suggestions
```bash
GET /api/resume-builder/resumes/1/suggestions?section=experience
```

### Optimize for ATS
```bash
POST /api/resume-builder/resumes/1/optimize
{
  "job_id": 5,
  "job_description": "We are looking for a senior engineer..."
}
```

### Export Resume
```bash
POST /api/resume-builder/resumes/1/export
{
  "format": "pdf"
}
```

### Get Templates
```bash
GET /api/resume-builder/templates
```

---

## Database Models

### Career Plan
```python
class CareerPlan:
    id: int
    user_id: int
    current_role: str
    target_role: str
    target_salary: float
    timeline_months: int
    status: str
```

### Portfolio
```python
class Portfolio:
    id: int
    user_id: int
    video_intro_url: str
    headline: str
    bio: str
    is_public: bool
    view_count: int
```

### Resume
```python
class Resume:
    id: int
    user_id: int
    title: str
    template_id: str
    content: dict
    ats_score: float
    keywords: list
```

### Scheduled Event
```python
class ScheduledEvent:
    id: int
    organizer_id: int
    participant_id: int
    title: str
    start_time: datetime
    end_time: datetime
    status: str
```

---

## Service Layer

### Career Coach Service
```python
from backend.app.services.career_coach_service import CareerCoachService

coach = CareerCoachService()

# Create plan
plan = await coach.create_career_plan(db, user_id, ...)

# Chat
response = await coach.chat(db, conversation_id, message)

# Get recommendations
paths = await coach.get_career_path_recommendations(db, plan_id)
```

### Portfolio Service
```python
from backend.app.services.portfolio_service import PortfolioService

portfolio_svc = PortfolioService()

# Get or create
portfolio = portfolio_svc.get_or_create_portfolio(db, user_id)

# Add project
project = portfolio_svc.add_project(db, portfolio_id, data)

# Generate upload URL
upload_data = portfolio_svc.generate_video_upload_url(user_id, filename)
```

### Resume Builder Service
```python
from backend.app.services.resume_builder_service import ResumeBuilderService

resume_svc = ResumeBuilderService()

# Create resume
resume = await resume_svc.create_resume(db, user_id, title, template, content)

# Get suggestions
suggestions = await resume_svc.get_ai_suggestions(db, resume_id, section)

# Optimize
optimization = await resume_svc.optimize_for_ats(db, resume_id, job_id)
```

### Scheduling Service
```python
from backend.app.services.smart_scheduling_service import SmartSchedulingService

scheduling_svc = SmartSchedulingService()

# Find times
slots = await scheduling_svc.find_optimal_times(
    db, organizer_id, participant_ids, duration, dates
)

# Create event
event = scheduling_svc.create_event(db, organizer_id, participant_id, ...)
```

---

## Testing

### Unit Tests
```bash
cd backend
pytest tests/test_career_coach.py
pytest tests/test_portfolio.py
pytest tests/test_scheduling.py
pytest tests/test_resume_builder.py
```

### Integration Tests
```bash
pytest tests/integration/test_phase1_apis.py
```

### Manual Testing
Use Swagger UI at http://localhost:8000/docs

---

## Common Issues

### OpenAI API Key Missing
```
Error: OpenAI API key not configured
Solution: Set OPENAI_API_KEY environment variable
```

### Database Migration Failed
```
Error: relation "career_plans" does not exist
Solution: Run alembic upgrade head
```

### AWS S3 Not Configured
```
Note: Video uploads will use mock URLs
Solution: Set AWS credentials or use mock for development
```

---

## Next Steps

1. ✅ Backend complete
2. 🔄 Build frontend components
3. ⏳ Integration testing
4. ⏳ Production deployment

---

## Support

- API Docs: http://localhost:8000/docs
- Week 1 Summary: PHASE_1_WEEK_1_COMPLETE.md
- Week 2 Summary: PHASE_1_WEEK_2_COMPLETE.md
- Main Plan: PHASE_1_IMPLEMENTATION.md
