"""
AI-HR Platform SDK Exceptions

Custom exceptions for the AI-HR Platform SDK.
"""

from typing import Optional, Dict, Any, List


class AIHRException(Exception):
    """Base exception for AI-HR Platform SDK"""
    
    def __init__(self, message: str, status_code: Optional[int] = None):
        super().__init__(message)
        self.message = message
        self.status_code = status_code


class AuthenticationError(AIHRException):
    """Authentication failed"""
    
    def __init__(self, message: str = "Authentication failed"):
        super().__init__(message, 401)


class AuthorizationError(AIHRException):
    """Authorization failed"""
    
    def __init__(self, message: str = "Insufficient permissions"):
        super().__init__(message, 403)


class NotFoundError(AIHRException):
    """Resource not found"""
    
    def __init__(self, message: str = "Resource not found"):
        super().__init__(message, 404)


class ValidationError(AIHRException):
    """Request validation failed"""
    
    def __init__(self, message: str = "Validation failed", errors: Optional[List[Dict[str, Any]]] = None):
        super().__init__(message, 422)
        self.errors = errors or []


class RateLimitError(AIHRException):
    """Rate limit exceeded"""
    
    def __init__(self, message: str = "Rate limit exceeded", retry_after: int = 60):
        super().__init__(message, 429)
        self.retry_after = retry_after


class ServerError(AIHRException):
    """Server error"""
    
    def __init__(self, message: str = "Internal server error"):
        super().__init__(message, 500)


class TimeoutError(AIHRException):
    """Request timeout"""
    
    def __init__(self, message: str = "Request timeout"):
        super().__init__(message)


class ConnectionError(AIHRException):
    """Connection error"""
    
    def __init__(self, message: str = "Connection error"):
        super().__init__(message)