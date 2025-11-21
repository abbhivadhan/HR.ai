from sqlalchemy import Column, String, Text, Boolean, DateTime, ForeignKey, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from enum import Enum
import uuid

from ..database import Base


class NotificationType(str, Enum):
    EMAIL = "email"
    SMS = "sms"
    PUSH = "push"
    IN_APP = "in_app"


class NotificationStatus(str, Enum):
    PENDING = "pending"
    SENT = "sent"
    DELIVERED = "delivered"
    FAILED = "failed"
    READ = "read"


class NotificationPriority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


class NotificationCategory(str, Enum):
    JOB_MATCH = "job_match"
    ASSESSMENT_REMINDER = "assessment_reminder"
    INTERVIEW_SCHEDULED = "interview_scheduled"
    APPLICATION_UPDATE = "application_update"
    SYSTEM_ALERT = "system_alert"
    SECURITY_ALERT = "security_alert"


class Notification(Base):
    __tablename__ = "notifications"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    type = Column(SQLEnum(NotificationType), nullable=False)
    category = Column(SQLEnum(NotificationCategory), nullable=False)
    priority = Column(SQLEnum(NotificationPriority), default=NotificationPriority.MEDIUM)
    status = Column(SQLEnum(NotificationStatus), default=NotificationStatus.PENDING)
    
    title = Column(String(255), nullable=False)
    message = Column(Text, nullable=False)
    data = Column(Text)  # JSON data for additional context
    
    # Delivery tracking
    sent_at = Column(DateTime(timezone=True))
    delivered_at = Column(DateTime(timezone=True))
    read_at = Column(DateTime(timezone=True))
    failed_at = Column(DateTime(timezone=True))
    failure_reason = Column(Text)
    
    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    expires_at = Column(DateTime(timezone=True))
    
    # Relationships
    user = relationship("User", back_populates="notifications")


class NotificationTemplate(Base):
    __tablename__ = "notification_templates"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(100), unique=True, nullable=False)
    category = Column(SQLEnum(NotificationCategory), nullable=False)
    type = Column(SQLEnum(NotificationType), nullable=False)
    
    subject_template = Column(String(255), nullable=False)
    body_template = Column(Text, nullable=False)
    
    # Template variables documentation
    variables = Column(Text)  # JSON array of expected variables
    
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class NotificationPreference(Base):
    __tablename__ = "notification_preferences"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    category = Column(SQLEnum(NotificationCategory), nullable=False)
    
    # Channel preferences
    email_enabled = Column(Boolean, default=True)
    sms_enabled = Column(Boolean, default=False)
    push_enabled = Column(Boolean, default=True)
    in_app_enabled = Column(Boolean, default=True)
    
    # Frequency settings
    immediate = Column(Boolean, default=True)
    daily_digest = Column(Boolean, default=False)
    weekly_digest = Column(Boolean, default=False)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="notification_preferences")


class NotificationHistory(Base):
    __tablename__ = "notification_history"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    notification_id = Column(UUID(as_uuid=True), ForeignKey("notifications.id"), nullable=False)
    
    # Delivery attempt details
    attempt_number = Column(String(10), nullable=False)
    status = Column(SQLEnum(NotificationStatus), nullable=False)
    response_data = Column(Text)  # Provider response
    error_message = Column(Text)
    
    attempted_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    notification = relationship("Notification")