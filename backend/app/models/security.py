"""
Security-related database models
"""
from sqlalchemy import Column, String, Boolean, DateTime, JSON, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from enum import Enum
import uuid
from ..database import Base


class AuditSeverity(str, Enum):
    """Audit log severity levels"""
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class SecurityEventType(str, Enum):
    """Security event types"""
    FAILED_LOGIN = "FAILED_LOGIN"
    SUSPICIOUS_ACTIVITY = "SUSPICIOUS_ACTIVITY"
    RATE_LIMIT_EXCEEDED = "RATE_LIMIT_EXCEEDED"
    UNAUTHORIZED_ACCESS = "UNAUTHORIZED_ACCESS"
    DATA_BREACH_ATTEMPT = "DATA_BREACH_ATTEMPT"
    ACCOUNT_LOCKED = "ACCOUNT_LOCKED"
    MFA_BYPASS_ATTEMPT = "MFA_BYPASS_ATTEMPT"


class AuditLog(Base):
    """Audit log for security compliance and tracking"""
    __tablename__ = "audit_logs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    action = Column(String, nullable=False, index=True)
    resource = Column(String, nullable=True)
    resource_id = Column(String, nullable=True)
    ip_address = Column(String, nullable=True)
    user_agent = Column(String, nullable=True)
    details = Column(JSON, nullable=True)
    timestamp = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)
    severity = Column(String, nullable=False, default=AuditSeverity.INFO)

    # Relationships
    user = relationship("User", backref="audit_logs")


class SecurityEvent(Base):
    """Security events for threat detection and monitoring"""
    __tablename__ = "security_events"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    event_type = Column(String, nullable=False, index=True)
    ip_address = Column(String, nullable=True, index=True)
    user_agent = Column(String, nullable=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    details = Column(JSON, nullable=True)
    severity = Column(String, nullable=False, index=True)
    resolved = Column(Boolean, default=False)
    timestamp = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)

    # Relationships
    user = relationship("User", backref="security_events")