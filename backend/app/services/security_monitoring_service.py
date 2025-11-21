"""
Security Monitoring and Threat Detection Service
"""
import re
import time
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from fastapi import Request
from ..models.security import SecurityEvent, SecurityEventType, AuditSeverity
from ..models.user import User
from .audit_service import AuditService
from .rate_limit_service import RateLimitService
import redis
from ..config import settings


class SecurityMonitoringService:
    """Service for monitoring security threats and suspicious activities"""
    
    def __init__(self, db: Session):
        self.db = db
        self.audit_service = AuditService(db)
        self.rate_limit_service = RateLimitService(self.audit_service)
        self.redis_client = redis.from_url(settings.redis_url)
    
    def analyze_request(self, request: Request, user: Optional[User] = None) -> Dict[str, Any]:
        """
        Analyze incoming request for security threats
        
        Returns:
            Dictionary with threat analysis results
        """
        threats = []
        risk_score = 0
        
        # Get request details
        ip_address = self._get_client_ip(request)
        user_agent = request.headers.get("user-agent", "")
        path = str(request.url.path)
        method = request.method
        
        # Check for SQL injection attempts
        if self._detect_sql_injection(request):
            threats.append("SQL_INJECTION_ATTEMPT")
            risk_score += 8
        
        # Check for XSS attempts
        if self._detect_xss_attempt(request):
            threats.append("XSS_ATTEMPT")
            risk_score += 6
        
        # Check for suspicious user agents
        if self._detect_suspicious_user_agent(user_agent):
            threats.append("SUSPICIOUS_USER_AGENT")
            risk_score += 3
        
        # Check for path traversal attempts
        if self._detect_path_traversal(path):
            threats.append("PATH_TRAVERSAL_ATTEMPT")
            risk_score += 7
        
        # Check for brute force patterns
        if self._detect_brute_force(ip_address, path):
            threats.append("BRUTE_FORCE_ATTEMPT")
            risk_score += 5
        
        # Check for unusual request patterns
        if self._detect_unusual_patterns(ip_address, user_agent, path):
            threats.append("UNUSUAL_REQUEST_PATTERN")
            risk_score += 4
        
        # Log high-risk threats
        if risk_score >= 7:
            self.audit_service.log_security_event(
                event_type=SecurityEventType.SUSPICIOUS_ACTIVITY,
                ip_address=ip_address,
                user_agent=user_agent,
                user=user,
                details={
                    "threats": threats,
                    "risk_score": risk_score,
                    "path": path,
                    "method": method
                },
                severity=AuditSeverity.ERROR if risk_score >= 10 else AuditSeverity.WARNING
            )
        
        return {
            "threats": threats,
            "risk_score": risk_score,
            "should_block": risk_score >= 10
        }
    
    def detect_account_takeover(self, user: User, request: Request) -> bool:
        """Detect potential account takeover attempts"""
        ip_address = self._get_client_ip(request)
        user_agent = request.headers.get("user-agent", "")
        
        # Check for login from new location/device
        recent_logins_key = f"recent_logins:{user.id}"
        recent_logins = self.redis_client.lrange(recent_logins_key, 0, -1)
        
        current_fingerprint = f"{ip_address}:{user_agent[:50]}"
        
        # If this is a completely new fingerprint, flag as suspicious
        if recent_logins and current_fingerprint.encode() not in recent_logins:
            # Check if it's from a completely different geographic location
            # (This would require IP geolocation service integration)
            
            self.audit_service.log_security_event(
                event_type=SecurityEventType.SUSPICIOUS_ACTIVITY,
                ip_address=ip_address,
                user_agent=user_agent,
                user=user,
                details={
                    "reason": "login_from_new_device_location",
                    "fingerprint": current_fingerprint
                },
                severity=AuditSeverity.WARNING
            )
            
            return True
        
        # Store current login fingerprint
        self.redis_client.lpush(recent_logins_key, current_fingerprint)
        self.redis_client.ltrim(recent_logins_key, 0, 9)  # Keep last 10 logins
        self.redis_client.expire(recent_logins_key, 86400 * 30)  # 30 days
        
        return False
    
    def check_data_breach_indicators(self, email: str) -> bool:
        """Check if email appears in known data breaches"""
        # This would integrate with services like HaveIBeenPwned API
        # For now, we'll implement a basic check
        
        # Check against a local blacklist of compromised emails
        breach_key = f"breached_email:{email.lower()}"
        is_breached = self.redis_client.exists(breach_key)
        
        if is_breached:
            self.audit_service.log_security_event(
                event_type=SecurityEventType.DATA_BREACH_ATTEMPT,
                details={"email": email, "reason": "email_in_breach_database"},
                severity=AuditSeverity.ERROR
            )
        
        return bool(is_breached)
    
    def monitor_privilege_escalation(self, user: User, requested_action: str, resource: str):
        """Monitor for privilege escalation attempts"""
        # Check if user is trying to access resources above their privilege level
        user_role = user.user_type
        
        # Define role hierarchy and permissions
        role_permissions = {
            "candidate": ["view_own_profile", "take_assessment", "apply_job"],
            "company": ["view_own_profile", "post_job", "view_candidates", "schedule_interview"],
            "admin": ["*"]  # Admin has all permissions
        }
        
        allowed_actions = role_permissions.get(user_role, [])
        
        if "*" not in allowed_actions and requested_action not in allowed_actions:
            self.audit_service.log_security_event(
                event_type=SecurityEventType.UNAUTHORIZED_ACCESS,
                user=user,
                details={
                    "requested_action": requested_action,
                    "resource": resource,
                    "user_role": user_role,
                    "reason": "privilege_escalation_attempt"
                },
                severity=AuditSeverity.ERROR
            )
            return False
        
        return True
    
    def get_security_dashboard_data(self) -> Dict[str, Any]:
        """Get security dashboard data for monitoring"""
        now = datetime.utcnow()
        last_24h = now - timedelta(hours=24)
        last_7d = now - timedelta(days=7)
        
        # Get recent security events
        recent_events = (
            self.db.query(SecurityEvent)
            .filter(SecurityEvent.timestamp >= last_24h)
            .order_by(SecurityEvent.timestamp.desc())
            .limit(50)
            .all()
        )
        
        # Count events by type
        event_counts = {}
        for event in recent_events:
            event_type = event.event_type
            event_counts[event_type] = event_counts.get(event_type, 0) + 1
        
        # Get blocked IPs
        blocked_ips = self.rate_limit_service.get_blocked_ips()
        
        # Get high-risk events (unresolved)
        high_risk_events = (
            self.db.query(SecurityEvent)
            .filter(
                SecurityEvent.severity.in_([AuditSeverity.ERROR, AuditSeverity.CRITICAL]),
                SecurityEvent.resolved == False,
                SecurityEvent.timestamp >= last_7d
            )
            .count()
        )
        
        return {
            "recent_events": [
                {
                    "id": str(event.id),
                    "type": event.event_type,
                    "severity": event.severity,
                    "timestamp": event.timestamp.isoformat(),
                    "ip_address": event.ip_address,
                    "resolved": event.resolved
                }
                for event in recent_events
            ],
            "event_counts": event_counts,
            "blocked_ips": blocked_ips,
            "high_risk_events": high_risk_events,
            "total_events_24h": len(recent_events)
        }
    
    def _detect_sql_injection(self, request: Request) -> bool:
        """Detect SQL injection attempts"""
        sql_patterns = [
            r"(\bunion\b.*\bselect\b)",
            r"(\bselect\b.*\bfrom\b)",
            r"(\binsert\b.*\binto\b)",
            r"(\bdelete\b.*\bfrom\b)",
            r"(\bdrop\b.*\btable\b)",
            r"(\bor\b.*=.*)",
            r"(\band\b.*=.*)",
            r"(--|\#|\/\*)",
            r"(\bexec\b|\bexecute\b)",
            r"(\bsp_\w+)"
        ]
        
        # Check query parameters and body
        query_string = str(request.url.query)
        
        for pattern in sql_patterns:
            if re.search(pattern, query_string, re.IGNORECASE):
                return True
        
        return False
    
    def _detect_xss_attempt(self, request: Request) -> bool:
        """Detect XSS attempts"""
        xss_patterns = [
            r"<script[^>]*>.*?</script>",
            r"javascript:",
            r"on\w+\s*=",
            r"<iframe[^>]*>",
            r"<object[^>]*>",
            r"<embed[^>]*>",
            r"eval\s*\(",
            r"document\.cookie",
            r"document\.write"
        ]
        
        query_string = str(request.url.query)
        
        for pattern in xss_patterns:
            if re.search(pattern, query_string, re.IGNORECASE):
                return True
        
        return False
    
    def _detect_suspicious_user_agent(self, user_agent: str) -> bool:
        """Detect suspicious user agents"""
        suspicious_patterns = [
            r"sqlmap",
            r"nikto",
            r"nmap",
            r"masscan",
            r"burp",
            r"owasp",
            r"python-requests",
            r"curl",
            r"wget",
            r"bot",
            r"crawler",
            r"spider"
        ]
        
        for pattern in suspicious_patterns:
            if re.search(pattern, user_agent, re.IGNORECASE):
                return True
        
        return False
    
    def _detect_path_traversal(self, path: str) -> bool:
        """Detect path traversal attempts"""
        traversal_patterns = [
            r"\.\./",
            r"\.\.\\",
            r"%2e%2e%2f",
            r"%2e%2e\\",
            r"..%2f",
            r"..%5c"
        ]
        
        for pattern in traversal_patterns:
            if re.search(pattern, path, re.IGNORECASE):
                return True
        
        return False
    
    def _detect_brute_force(self, ip_address: str, path: str) -> bool:
        """Detect brute force attempts"""
        # Check for rapid requests to authentication endpoints
        auth_endpoints = ["/api/auth/login", "/api/auth/register"]
        
        if any(endpoint in path for endpoint in auth_endpoints):
            key = f"auth_attempts:{ip_address}"
            attempts = self.redis_client.incr(key)
            self.redis_client.expire(key, 300)  # 5 minutes
            
            return attempts > 20  # More than 20 attempts in 5 minutes
        
        return False
    
    def _detect_unusual_patterns(self, ip_address: str, user_agent: str, path: str) -> bool:
        """Detect unusual request patterns"""
        # Check for requests without common headers
        if not user_agent or len(user_agent) < 10:
            return True
        
        # Check for requests to non-existent endpoints
        if "admin" in path.lower() or "config" in path.lower():
            return True
        
        return False
    
    def _get_client_ip(self, request: Request) -> str:
        """Extract client IP address from request"""
        forwarded_for = request.headers.get("x-forwarded-for")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()
        
        real_ip = request.headers.get("x-real-ip")
        if real_ip:
            return real_ip
        
        return request.client.host if request.client else "unknown"