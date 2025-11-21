"""Smart Scheduling API Endpoints"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from backend.app.database import get_db
from backend.app.auth.dependencies import get_current_user
from backend.app.models.user import User
from backend.app.models.schedule import SchedulingPreference, ScheduledEvent
from backend.app.schemas.scheduling import (
    SchedulingPreferenceCreate, SchedulingPreferenceUpdate, SchedulingPreferenceResponse,
    ScheduledEventCreate, ScheduledEventUpdate, ScheduledEventResponse,
    AvailabilityRequest, AvailabilityResponse
)
from backend.app.services.smart_scheduling_service import SmartSchedulingService

router = APIRouter(prefix="/api/scheduling", tags=["Scheduling"])
scheduling_service = SmartSchedulingService()


@router.get("/preferences", response_model=SchedulingPreferenceResponse)
def get_preferences(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get scheduling preferences"""
    prefs = scheduling_service.get_or_create_preferences(
        db=db,
        user_id=int(current_user.id)
    )
    return prefs


@router.put("/preferences", response_model=SchedulingPreferenceResponse)
def update_preferences(
    updates: SchedulingPreferenceUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update scheduling preferences"""
    prefs = scheduling_service.update_preferences(
        db=db,
        user_id=int(current_user.id),
        updates=updates.dict(exclude_unset=True)
    )
    return prefs


@router.post("/find-times", response_model=AvailabilityResponse)
async def find_optimal_times(
    request: AvailabilityRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Find optimal meeting times"""
    suggestions = await scheduling_service.find_optimal_times(
        db=db,
        organizer_id=int(current_user.id),
        participant_ids=request.participant_ids,
        duration_minutes=request.duration_minutes,
        preferred_dates=request.preferred_dates,
        timezone=request.timezone
    )
    
    return {
        "suggested_slots": suggestions,
        "conflicts": []
    }


@router.post("/events", response_model=ScheduledEventResponse)
def create_event(
    event_data: ScheduledEventCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a scheduled event"""
    event = scheduling_service.create_event(
        db=db,
        organizer_id=int(current_user.id),
        participant_id=event_data.participant_id,
        title=event_data.title,
        start_time=event_data.start_time,
        end_time=event_data.end_time,
        description=event_data.description,
        timezone=event_data.timezone,
        meeting_url=event_data.meeting_url,
        interview_id=event_data.interview_id
    )
    
    return event


@router.get("/events", response_model=List[ScheduledEventResponse])
def get_events(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get user's scheduled events"""
    from sqlalchemy import or_
    
    events = db.query(ScheduledEvent).filter(
        or_(
            ScheduledEvent.organizer_id == int(current_user.id),
            ScheduledEvent.participant_id == int(current_user.id)
        )
    ).order_by(ScheduledEvent.start_time).all()
    
    return events


@router.get("/events/{event_id}", response_model=ScheduledEventResponse)
def get_event(
    event_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get specific event"""
    from sqlalchemy import or_
    
    event = db.query(ScheduledEvent).filter(
        ScheduledEvent.id == event_id,
        or_(
            ScheduledEvent.organizer_id == int(current_user.id),
            ScheduledEvent.participant_id == int(current_user.id)
        )
    ).first()
    
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    
    return event


@router.put("/events/{event_id}", response_model=ScheduledEventResponse)
def update_event(
    event_id: int,
    updates: ScheduledEventUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update scheduled event"""
    event = db.query(ScheduledEvent).filter(
        ScheduledEvent.id == event_id,
        ScheduledEvent.organizer_id == int(current_user.id)
    ).first()
    
    if not event:
        raise HTTPException(status_code=404, detail="Event not found or not authorized")
    
    for key, value in updates.dict(exclude_unset=True).items():
        setattr(event, key, value)
    
    from datetime import datetime
    event.updated_at = datetime.utcnow()
    
    db.commit()
    db.refresh(event)
    
    return event


@router.delete("/events/{event_id}")
def cancel_event(
    event_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Cancel scheduled event"""
    event = db.query(ScheduledEvent).filter(
        ScheduledEvent.id == event_id,
        ScheduledEvent.organizer_id == int(current_user.id)
    ).first()
    
    if not event:
        raise HTTPException(status_code=404, detail="Event not found or not authorized")
    
    event.status = "cancelled"
    db.commit()
    
    return {"message": "Event cancelled"}
