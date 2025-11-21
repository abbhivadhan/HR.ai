"""Smart Scheduling Models"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, JSON, Boolean
from sqlalchemy.orm import relationship
from backend.app.models import Base


class SchedulingPreference(Base):
    """User scheduling preferences"""
    __tablename__ = "scheduling_preferences"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, unique=True)
    timezone = Column(String(100), default="UTC")
    buffer_minutes = Column(Integer, default=15)
    working_hours = Column(JSON, default=dict)  # {day: {start, end}}
    calendar_integrations = Column(JSON, default=list)  # [{provider, token, calendar_id}]
    auto_accept = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="scheduling_preference")


class ScheduledEvent(Base):
    """Scheduled interviews and meetings"""
    __tablename__ = "scheduled_events"

    id = Column(Integer, primary_key=True, index=True)
    interview_id = Column(Integer, ForeignKey("interviews.id"))
    organizer_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    participant_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    title = Column(String(200), nullable=False)
    description = Column(Text)
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime, nullable=False)
    timezone = Column(String(100), default="UTC")
    meeting_url = Column(String(500))
    status = Column(String(50), default="scheduled")  # scheduled, confirmed, cancelled, completed
    reminder_sent = Column(Boolean, default=False)
    calendar_event_ids = Column(JSON, default=dict)  # {provider: event_id}
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    interview = relationship("Interview")
    organizer = relationship("User", foreign_keys=[organizer_id])
    participant = relationship("User", foreign_keys=[participant_id])
    availability_slots = relationship("AvailabilitySlot", back_populates="event", cascade="all, delete-orphan")


class AvailabilitySlot(Base):
    """Available time slots"""
    __tablename__ = "availability_slots"

    id = Column(Integer, primary_key=True, index=True)
    event_id = Column(Integer, ForeignKey("scheduled_events.id"))
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime, nullable=False)
    is_available = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    event = relationship("ScheduledEvent", back_populates="availability_slots")
    user = relationship("User")
