"""
Audit Logging Service for security compliance
"""
from typing import Optional, Dict, Any
from sqlalchemy.orm import Session
from fastapi import Request
from ..models.security import AuditLog, SecurityEvent, AuditSeverity, SecurityEventType
from ..models.user import User
import uuid


class AuditService:
    """Service for handling audit logging and security events"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def log_action(
        self,
        action: str,
        user: Optional[User] = None,
        resource: Optional[str] = None,
        resource_id: Optional[str] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
        severity: AuditSeverity = AuditSeverity.INFO,
        request: Optional[Request] = None
    ) -> AuditLog:
        """Log an audit action"""
        
        # Extract request information if provided
        if request:
            ip_address = ip_address or self._get_client_ip(request)
            user_agent = user_agent or request.headers.get("user-agent")
        
        audit_log = AuditLog(
            user_id=user.id if user else None,
            action=action,
            resource=resource,
            resource_id=resource_id,
            ip_address=ip_address,
            user_agent=user_agent,
            details=details or {},
            severity=severity
        )
        
        self.db.add(audit_log)
        self.db.commit()
        return audit_log
    
    def log_security_event(
        self,
        event_type: SecurityEventType,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        user: Optional[User] = None,
        details: Optional[Dict[str, Any]] = None,
        severity: AuditSeverity = AuditSeverity.WARNING,
        request: Optional[Request] = None
    ) -> SecurityEvent:
        """Log a security event"""
        
        # Extract request information if provided
        if request:
            ip_address = ip_address or self._get_client_ip(request)
            user_agent = user_agent or request.headers.get("user-agent")
        
        security_event = SecurityEvent(
            event_type=event_type,
            ip_address=ip_address,
            user_agent=user_agent,
            user_id=user.id if user else None,
            details=details or {},
            severity=severity
        )
        
        self.db.add(security_event)
        self.db.commit()
        return security_event
    
    def log_login_attempt(
        self,
        email: str,
        success: bool,
        ip_address: str,
        user_agent: str,
        user: Optional[User] = None,
        mfa_used: bool = False
    ):
        """Log login attempt"""
        action = "LOGIN_SUCCESS" if success else "LOGIN_FAILED"
        severity = AuditSeverity.INFO if success else AuditSeverity.WARNING
        
        details = {
            "email": email,
            "mfa_used": mfa_used,
            "success": success
        }
        
        self.log_action(
            action=action,
            user=user,
            resource="authentication",
            ip_address=ip_address,
            user_agent=user_agent,
            details=details,
            severity=severity
        )
        
        # Log security event for failed login
        if not success:
            self.log_security_event(
                event_type=SecurityEventType.FAILED_LOGIN,
                ip_address=ip_address,
                user_agent=user_agent,
                user=user,
                details=details,
                severity=AuditSeverity.WARNING
            )
    
    def log_data_access(
        self,
        user: User,
        resource: str,
        resource_id: str,
        action: str,
        request: Request,
        details: Optional[Dict[str, Any]] = None
    ):
        """Log data access for GDPR compliance"""
        self.log_action(
            action=f"DATA_{action.upper()}",
            user=user,
            resource=resource,
            resource_id=resource_id,
            request=request,
            details=details,
            severity=AuditSeverity.INFO
        )
    
    def log_gdpr_action(
        self,
        user: User,
        action: str,
        request: Request,
        details: Optional[Dict[str, Any]] = None
    ):
        """Log GDPR-related actions"""
        self.log_action(
            action=f"GDPR_{action.upper()}",
            user=user,
            resource="gdpr_compliance",
            request=request,
            details=details,
            severity=AuditSeverity.INFO
        )
    
    def get_user_audit_trail(self, user_id: uuid.UUID, limit: int = 100) -> list[AuditLog]:
        """Get audit trail for a specific user"""
        return (
            self.db.query(AuditLog)
            .filter(AuditLog.user_id == user_id)
            .order_by(AuditLog.timestamp.desc())
            .limit(limit)
            .all()
        )
    
    def get_security_events(
        self,
        event_type: Optional[SecurityEventType] = None,
        resolved: Optional[bool] = None,
        limit: int = 100
    ) -> list[SecurityEvent]:
        """Get security events with optional filtering"""
        query = self.db.query(SecurityEvent)
        
        if event_type:
            query = query.filter(SecurityEvent.event_type == event_type)
        
        if resolved is not None:
            query = query.filter(SecurityEvent.resolved == resolved)
        
        return query.order_by(SecurityEvent.timestamp.desc()).limit(limit).all()
    
    def resolve_security_event(self, event_id: uuid.UUID) -> bool:
        """Mark a security event as resolved"""
        event = self.db.query(SecurityEvent).filter(SecurityEvent.id == event_id).first()
        if event:
            event.resolved = True
            self.db.commit()
            return True
        return False
    
    def _get_client_ip(self, request: Request) -> str:
        """Extract client IP address from request"""
        # Check for forwarded headers first (for load balancers/proxies)
        forwarded_for = request.headers.get("x-forwarded-for")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()
        
        real_ip = request.headers.get("x-real-ip")
        if real_ip:
            return real_ip
        
        # Fallback to direct client IP
        return request.client.host if request.client else "unknown"