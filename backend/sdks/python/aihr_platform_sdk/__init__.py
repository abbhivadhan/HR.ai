"""
AI-HR Platform Python SDK

Official Python client library for the AI-HR Platform API.
"""

from .client import AIHRClient
from .exceptions import (
    AIHRException,
    AuthenticationError,
    RateLimitError,
    ValidationError,
    NotFoundError,
    ServerError
)
from .models import (
    User,
    Assessment,
    Job,
    JobMatch,
    Interview,
    Webhook
)

__version__ = "1.0.0"
__author__ = "AI-HR Platform Team"
__email__ = "developers@aihr-platform.com"

__all__ = [
    "AIHRClient",
    "AIHRException",
    "AuthenticationError", 
    "RateLimitError",
    "ValidationError",
    "NotFoundError",
    "ServerError",
    "User",
    "Assessment",
    "Job",
    "JobMatch",
    "Interview",
    "Webhook"
]