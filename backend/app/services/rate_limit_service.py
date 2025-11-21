"""
Rate Limiting and DDoS Protection Service
"""
import time
from typing import Optional, Dict, Any
from fastapi import HTTPException, status, Request
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
import redis
from ..config import settings
from .audit_service import AuditService
from ..models.security import SecurityEventType, AuditSeverity


# Redis client for rate limiting
redis_client = redis.from_url(settings.redis_url)

# Rate limiter instance
limiter = Limiter(
    key_func=get_remote_address,
    storage_uri=settings.redis_url,
    default_limits=["1000/hour"]
)


class RateLimitService:
    """Service for handling rate limiting and DDoS protection"""
    
    def __init__(self, audit_service: Optional[AuditService] = None):
        self.audit_service = audit_service
        self.redis_client = redis_client
    
    def check_rate_limit(
        self,
        key: str,
        limit: int,
        window: int,
        request: Optional[Request] = None
    ) -> bool:
        """
        Check if rate limit is exceeded
        
        Args:
            key: Unique identifier for rate limiting (IP, user ID, etc.)
            limit: Maximum number of requests allowed
            window: Time window in seconds
            request: FastAPI request object for logging
        
        Returns:
            True if within limit, False if exceeded
        """
        current_time = int(time.time())
        window_start = current_time - window
        
        # Use Redis sorted set to track requests in time window
        pipe = self.redis_client.pipeline()
        
        # Remove old entries
        pipe.zremrangebyscore(key, 0, window_start)
        
        # Count current requests
        pipe.zcard(key)
        
        # Add current request
        pipe.zadd(key, {str(current_time): current_time})
        
        # Set expiry for cleanup
        pipe.expire(key, window)
        
        results = pipe.execute()
        current_requests = results[1]
        
        if current_requests >= limit:
            # Log rate limit exceeded
            if self.audit_service and request:
                self.audit_service.log_security_event(
                    event_type=SecurityEventType.RATE_LIMIT_EXCEEDED,
                    request=request,
                    details={
                        "key": key,
                        "limit": limit,
                        "window": window,
                        "current_requests": current_requests
                    },
                    severity=AuditSeverity.WARNING
                )
            return False
        
        return True
    
    def check_login_rate_limit(self, ip_address: str, email: str) -> bool:
        """Check rate limit for login attempts"""
        # IP-based rate limiting (5 attempts per minute)
        ip_key = f"login_attempts:ip:{ip_address}"
        if not self.check_rate_limit(ip_key, 5, 60):
            return False
        
        # Email-based rate limiting (3 attempts per minute)
        email_key = f"login_attempts:email:{email}"
        if not self.check_rate_limit(email_key, 3, 60):
            return False
        
        return True
    
    def check_api_rate_limit(self, user_id: str, endpoint: str) -> bool:
        """Check rate limit for API endpoints"""
        # User-based rate limiting (100 requests per minute)
        user_key = f"api_requests:user:{user_id}"
        if not self.check_rate_limit(user_key, 100, 60):
            return False
        
        # Endpoint-specific rate limiting
        endpoint_limits = {
            "/api/assessments/start": (5, 300),  # 5 per 5 minutes
            "/api/interviews/schedule": (10, 3600),  # 10 per hour
            "/api/jobs/create": (20, 3600),  # 20 per hour
        }
        
        if endpoint in endpoint_limits:
            limit, window = endpoint_limits[endpoint]
            endpoint_key = f"api_requests:endpoint:{user_id}:{endpoint}"
            if not self.check_rate_limit(endpoint_key, limit, window):
                return False
        
        return True
    
    def increment_failed_login(self, ip_address: str, email: str) -> Dict[str, Any]:
        """Increment failed login attempts and check for account locking"""
        ip_key = f"failed_logins:ip:{ip_address}"
        email_key = f"failed_logins:email:{email}"
        
        # Increment counters
        ip_failures = self.redis_client.incr(ip_key)
        email_failures = self.redis_client.incr(email_key)
        
        # Set expiry (1 hour)
        self.redis_client.expire(ip_key, 3600)
        self.redis_client.expire(email_key, 3600)
        
        # Check for suspicious activity
        should_lock_ip = ip_failures >= 10  # Lock IP after 10 failures
        should_lock_email = email_failures >= 5  # Lock email after 5 failures
        
        return {
            "ip_failures": ip_failures,
            "email_failures": email_failures,
            "should_lock_ip": should_lock_ip,
            "should_lock_email": should_lock_email
        }
    
    def is_ip_blocked(self, ip_address: str) -> bool:
        """Check if IP address is blocked"""
        blocked_key = f"blocked_ip:{ip_address}"
        return self.redis_client.exists(blocked_key)
    
    def block_ip(self, ip_address: str, duration: int = 3600) -> bool:
        """Block IP address for specified duration (default 1 hour)"""
        blocked_key = f"blocked_ip:{ip_address}"
        return self.redis_client.setex(blocked_key, duration, "blocked")
    
    def unblock_ip(self, ip_address: str) -> bool:
        """Unblock IP address"""
        blocked_key = f"blocked_ip:{ip_address}"
        return self.redis_client.delete(blocked_key)
    
    def get_blocked_ips(self) -> list[str]:
        """Get list of currently blocked IP addresses"""
        pattern = "blocked_ip:*"
        keys = self.redis_client.keys(pattern)
        return [key.decode().replace("blocked_ip:", "") for key in keys]
    
    def detect_ddos_pattern(self, ip_address: str) -> bool:
        """Detect potential DDoS patterns"""
        # Check for rapid requests from same IP
        rapid_key = f"rapid_requests:{ip_address}"
        requests_count = self.redis_client.incr(rapid_key)
        self.redis_client.expire(rapid_key, 10)  # 10 second window
        
        # If more than 50 requests in 10 seconds, consider it DDoS
        if requests_count > 50:
            return True
        
        # Check for distributed attack (many IPs with similar patterns)
        # This would require more sophisticated analysis
        
        return False
    
    def clear_rate_limit(self, key: str) -> bool:
        """Clear rate limit for a specific key"""
        return self.redis_client.delete(key)


# Rate limit decorator for FastAPI endpoints
def rate_limit(requests: str):
    """Decorator for applying rate limits to FastAPI endpoints"""
    def decorator(func):
        return limiter.limit(requests)(func)
    return decorator


# Custom rate limit exceeded handler
def custom_rate_limit_handler(request: Request, exc: RateLimitExceeded):
    """Custom handler for rate limit exceeded"""
    response = _rate_limit_exceeded_handler(request, exc)
    
    # Log the rate limit exceeded event
    # This would be called by the audit service if available
    
    return response