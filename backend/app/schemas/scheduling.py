"""Smart Scheduling Schemas"""
from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field


class WorkingHours(BaseModel):
    """Working hours for a day"""
    start: str = Field(..., pattern="^([0-1]?[0-9]|2[0-3]):[0-5][0-9]$")
    end: str = Field(..., pattern="^([0-1]?[0-9]|2[0-3]):[0-5][0-9]$")


class CalendarIntegration(BaseModel):
    """Calendar integration"""
    provider: str  # google, outlook, apple
    token: str
    calendar_id: str
    refresh_token: Optional[str] = None


class SchedulingPreferenceCreate(BaseModel):
    """Create scheduling preference"""
    timezone: str = "UTC"
    buffer_minutes: int = Field(15, ge=0, le=120)
    working_hours: Dict[str, WorkingHours] = {}
    auto_accept: bool = False


class SchedulingPreferenceUpdate(BaseModel):
    """Update scheduling preference"""
    timezone: Optional[str] = None
    buffer_minutes: Optional[int] = Field(None, ge=0, le=120)
    working_hours: Optional[Dict[str, WorkingHours]] = None
    auto_accept: Optional[bool] = None


class SchedulingPreferenceResponse(BaseModel):
    """Scheduling preference response"""
    id: int
    user_id: int
    timezone: str
    buffer_minutes: int
    working_hours: Dict[str, Any]
    calendar_integrations: List[Dict[str, Any]]
    auto_accept: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ScheduledEventCreate(BaseModel):
    """Create scheduled event"""
    interview_id: Optional[int] = None
    participant_id: int
    title: str = Field(..., max_length=200)
    description: Optional[str] = None
    start_time: datetime
    end_time: datetime
    timezone: str = "UTC"
    meeting_url: Optional[str] = None


class ScheduledEventUpdate(BaseModel):
    """Update scheduled event"""
    title: Optional[str] = Field(None, max_length=200)
    description: Optional[str] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    status: Optional[str] = None
    meeting_url: Optional[str] = None


class ScheduledEventResponse(BaseModel):
    """Scheduled event response"""
    id: int
    interview_id: Optional[int]
    organizer_id: int
    participant_id: int
    title: str
    description: Optional[str]
    start_time: datetime
    end_time: datetime
    timezone: str
    meeting_url: Optional[str]
    status: str
    reminder_sent: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class TimeSlotSuggestion(BaseModel):
    """AI-suggested time slot"""
    start_time: datetime
    end_time: datetime
    score: float
    reason: str


class AvailabilityRequest(BaseModel):
    """Request availability"""
    participant_ids: List[int]
    duration_minutes: int
    preferred_dates: List[datetime]
    timezone: str = "UTC"


class AvailabilityResponse(BaseModel):
    """Availability response"""
    suggested_slots: List[TimeSlotSuggestion]
    conflicts: List[Dict[str, Any]]
