"""Smart Scheduling Service"""
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from backend.app.models.schedule import (
    SchedulingPreference, ScheduledEvent, AvailabilitySlot
)


class SmartSchedulingService:
    """AI-powered scheduling service"""
    
    def get_or_create_preferences(
        self,
        db: Session,
        user_id: int
    ) -> SchedulingPreference:
        """Get or create scheduling preferences"""
        prefs = db.query(SchedulingPreference).filter(
            SchedulingPreference.user_id == user_id
        ).first()
        
        if not prefs:
            prefs = SchedulingPreference(user_id=user_id)
            db.add(prefs)
            db.commit()
            db.refresh(prefs)
        
        return prefs
    
    def update_preferences(
        self,
        db: Session,
        user_id: int,
        updates: Dict[str, Any]
    ) -> SchedulingPreference:
        """Update scheduling preferences"""
        prefs = self.get_or_create_preferences(db, user_id)
        
        for key, value in updates.items():
            if hasattr(prefs, key):
                setattr(prefs, key, value)
        
        prefs.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(prefs)
        
        return prefs
    
    async def find_optimal_times(
        self,
        db: Session,
        organizer_id: int,
        participant_ids: List[int],
        duration_minutes: int,
        preferred_dates: List[datetime],
        timezone: str = "UTC"
    ) -> List[Dict[str, Any]]:
        """Find optimal meeting times using AI"""
        suggestions = []
        
        # Get all participants' preferences
        all_user_ids = [organizer_id] + participant_ids
        preferences = db.query(SchedulingPreference).filter(
            SchedulingPreference.user_id.in_(all_user_ids)
        ).all()
        
        # Get existing events for conflict detection
        start_date = min(preferred_dates)
        end_date = max(preferred_dates) + timedelta(days=1)
        
        existing_events = db.query(ScheduledEvent).filter(
            and_(
                or_(
                    ScheduledEvent.organizer_id.in_(all_user_ids),
                    ScheduledEvent.participant_id.in_(all_user_ids)
                ),
                ScheduledEvent.start_time >= start_date,
                ScheduledEvent.end_time <= end_date,
                ScheduledEvent.status.in_(['scheduled', 'confirmed'])
            )
        ).all()
        
        # Analyze each preferred date
        for date in preferred_dates:
            # Find available slots
            slots = self._find_available_slots(
                date,
                duration_minutes,
                preferences,
                existing_events
            )
            
            for slot in slots:
                score = self._calculate_slot_score(slot, preferences)
                suggestions.append({
                    "start_time": slot["start_time"],
                    "end_time": slot["end_time"],
                    "score": score,
                    "reason": slot["reason"]
                })
        
        # Sort by score and return top suggestions
        suggestions.sort(key=lambda x: x["score"], reverse=True)
        return suggestions[:5]
    
    def create_event(
        self,
        db: Session,
        organizer_id: int,
        participant_id: int,
        title: str,
        start_time: datetime,
        end_time: datetime,
        **kwargs
    ) -> ScheduledEvent:
        """Create a scheduled event"""
        event = ScheduledEvent(
            organizer_id=organizer_id,
            participant_id=participant_id,
            title=title,
            start_time=start_time,
            end_time=end_time,
            **kwargs
        )
        
        db.add(event)
        db.commit()
        db.refresh(event)
        
        return event
    
    def _find_available_slots(
        self,
        date: datetime,
        duration_minutes: int,
        preferences: List[SchedulingPreference],
        existing_events: List[ScheduledEvent]
    ) -> List[Dict[str, Any]]:
        """Find available time slots"""
        slots = []
        
        # Default working hours: 9 AM - 5 PM
        start_hour = 9
        end_hour = 17
        
        # Check each hour
        current_time = date.replace(hour=start_hour, minute=0, second=0)
        end_time = date.replace(hour=end_hour, minute=0, second=0)
        
        while current_time < end_time:
            slot_end = current_time + timedelta(minutes=duration_minutes)
            
            # Check if slot conflicts with existing events
            has_conflict = False
            for event in existing_events:
                if (current_time < event.end_time and slot_end > event.start_time):
                    has_conflict = True
                    break
            
            if not has_conflict:
                slots.append({
                    "start_time": current_time,
                    "end_time": slot_end,
                    "reason": "Available slot within working hours"
                })
            
            # Move to next 30-minute slot
            current_time += timedelta(minutes=30)
        
        return slots
    
    def _calculate_slot_score(
        self,
        slot: Dict[str, Any],
        preferences: List[SchedulingPreference]
    ) -> float:
        """Calculate score for a time slot"""
        score = 50.0  # Base score
        
        hour = slot["start_time"].hour
        
        # Prefer mid-morning and early afternoon
        if 10 <= hour <= 11 or 14 <= hour <= 15:
            score += 20
        elif 9 <= hour <= 16:
            score += 10
        
        # Avoid very early or late times
        if hour < 9 or hour > 17:
            score -= 20
        
        # Prefer times with buffer
        if slot["start_time"].minute == 0:
            score += 5
        
        return min(100.0, max(0.0, score))
