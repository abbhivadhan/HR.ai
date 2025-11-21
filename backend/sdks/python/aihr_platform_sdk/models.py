"""
AI-HR Platform SDK Models

Data models for API responses and requests.
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
from dataclasses import dataclass
from enum import Enum


class UserType(str, Enum):
    """User types"""
    CANDIDATE = "candidate"
    COMPANY = "company"
    ADMIN = "admin"


class AssessmentType(str, Enum):
    """Assessment types"""
    TECHNICAL = "technical"
    BEHAVIORAL = "behavioral"
    COGNITIVE = "cognitive"
    PERSONALITY = "personality"


class JobStatus(str, Enum):
    """Job posting status"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    FILLED = "filled"
    EXPIRED = "expired"


@dataclass
class User:
    """User model"""
    id: str
    email: str
    first_name: str
    last_name: str
    user_type: UserType
    is_verified: bool
    created_at: datetime
    updated_at: Optional[datetime] = None
    avatar_url: Optional[str] = None
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'User':
        """Create User from dictionary"""
        return cls(
            id=data["id"],
            email=data["email"],
            first_name=data["first_name"],
            last_name=data["last_name"],
            user_type=UserType(data["user_type"]),
            is_verified=data["is_verified"],
            created_at=datetime.fromisoformat(data["created_at"].replace('Z', '+00:00')),
            updated_at=datetime.fromisoformat(data["updated_at"].replace('Z', '+00:00')) if data.get("updated_at") else None,
            avatar_url=data.get("avatar_url")
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert User to dictionary"""
        return {
            "id": self.id,
            "email": self.email,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "user_type": self.user_type.value,
            "is_verified": self.is_verified,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "avatar_url": self.avatar_url
        }


@dataclass
class Assessment:
    """Assessment model"""
    id: str
    assessment_type: AssessmentType
    status: str
    score: Optional[float] = None
    time_limit_minutes: Optional[int] = None
    total_questions: Optional[int] = None
    completed_questions: Optional[int] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    session_token: Optional[str] = None
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Assessment':
        """Create Assessment from dictionary"""
        return cls(
            id=data["id"],
            assessment_type=AssessmentType(data["assessment_type"]),
            status=data["status"],
            score=data.get("score"),
            time_limit_minutes=data.get("time_limit_minutes"),
            total_questions=data.get("total_questions"),
            completed_questions=data.get("completed_questions"),
            started_at=datetime.fromisoformat(data["started_at"].replace('Z', '+00:00')) if data.get("started_at") else None,
            completed_at=datetime.fromisoformat(data["completed_at"].replace('Z', '+00:00')) if data.get("completed_at") else None,
            session_token=data.get("session_token")
        )


@dataclass
class Job:
    """Job model"""
    id: str
    title: str
    company_name: str
    description: str
    location: Optional[str] = None
    remote_allowed: bool = False
    salary_min: Optional[int] = None
    salary_max: Optional[int] = None
    currency: str = "USD"
    status: JobStatus = JobStatus.ACTIVE
    posted_at: Optional[datetime] = None
    expires_at: Optional[datetime] = None
    required_skills: Optional[List[str]] = None
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Job':
        """Create Job from dictionary"""
        return cls(
            id=data["id"],
            title=data["title"],
            company_name=data["company_name"],
            description=data["description"],
            location=data.get("location"),
            remote_allowed=data.get("remote_allowed", False),
            salary_min=data.get("salary_min"),
            salary_max=data.get("salary_max"),
            currency=data.get("currency", "USD"),
            status=JobStatus(data.get("status", "active")),
            posted_at=datetime.fromisoformat(data["posted_at"].replace('Z', '+00:00')) if data.get("posted_at") else None,
            expires_at=datetime.fromisoformat(data["expires_at"].replace('Z', '+00:00')) if data.get("expires_at") else None,
            required_skills=data.get("required_skills", [])
        )


@dataclass
class JobMatch:
    """Job match model"""
    job_id: str
    job_title: str
    company_name: str
    match_score: float
    match_reasons: List[str]
    location: Optional[str] = None
    salary_range: Optional[Dict[str, Any]] = None
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'JobMatch':
        """Create JobMatch from dictionary"""
        return cls(
            job_id=data["job_id"],
            job_title=data["job_title"],
            company_name=data["company_name"],
            match_score=data["match_score"],
            match_reasons=data.get("match_reasons", []),
            location=data.get("location"),
            salary_range=data.get("salary_range")
        )


@dataclass
class Interview:
    """Interview model"""
    id: str
    job_id: str
    interview_type: str
    status: str
    scheduled_at: Optional[datetime] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    join_url: Optional[str] = None
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Interview':
        """Create Interview from dictionary"""
        return cls(
            id=data["id"],
            job_id=data["job_id"],
            interview_type=data["interview_type"],
            status=data["status"],
            scheduled_at=datetime.fromisoformat(data["scheduled_at"].replace('Z', '+00:00')) if data.get("scheduled_at") else None,
            started_at=datetime.fromisoformat(data["started_at"].replace('Z', '+00:00')) if data.get("started_at") else None,
            completed_at=datetime.fromisoformat(data["completed_at"].replace('Z', '+00:00')) if data.get("completed_at") else None,
            join_url=data.get("join_url")
        )


@dataclass
class Webhook:
    """Webhook model"""
    id: str
    url: str
    events: List[str]
    is_active: bool
    status: str
    created_at: datetime
    description: Optional[str] = None
    last_delivery_at: Optional[datetime] = None
    success_rate: float = 1.0
    total_deliveries: int = 0
    failed_deliveries: int = 0
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Webhook':
        """Create Webhook from dictionary"""
        return cls(
            id=data["id"],
            url=data["url"],
            events=data["events"],
            is_active=data["is_active"],
            status=data["status"],
            created_at=datetime.fromisoformat(data["created_at"].replace('Z', '+00:00')),
            description=data.get("description"),
            last_delivery_at=datetime.fromisoformat(data["last_delivery_at"].replace('Z', '+00:00')) if data.get("last_delivery_at") else None,
            success_rate=data.get("success_rate", 1.0),
            total_deliveries=data.get("total_deliveries", 0),
            failed_deliveries=data.get("failed_deliveries", 0)
        )


@dataclass
class Question:
    """Assessment question model"""
    id: str
    question_text: str
    question_type: str
    options: Optional[List[str]] = None
    correct_answer: Optional[str] = None
    points: int = 1
    time_limit_seconds: Optional[int] = None
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Question':
        """Create Question from dictionary"""
        return cls(
            id=data["id"],
            question_text=data["question_text"],
            question_type=data["question_type"],
            options=data.get("options"),
            correct_answer=data.get("correct_answer"),
            points=data.get("points", 1),
            time_limit_seconds=data.get("time_limit_seconds")
        )


@dataclass
class WebhookEvent:
    """Webhook event model"""
    id: str
    event_type: str
    timestamp: datetime
    data: Dict[str, Any]
    user_id: Optional[str] = None
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'WebhookEvent':
        """Create WebhookEvent from dictionary"""
        return cls(
            id=data["id"],
            event_type=data["event_type"],
            timestamp=datetime.fromisoformat(data["timestamp"].replace('Z', '+00:00')),
            data=data["data"],
            user_id=data.get("user_id")
        )


@dataclass
class APIUsageStats:
    """API usage statistics model"""
    total_requests: int
    requests_by_endpoint: Dict[str, int]
    requests_by_method: Dict[str, int]
    average_response_time: float
    error_rate: float
    rate_limit_hits: int
    last_24h_requests: int
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'APIUsageStats':
        """Create APIUsageStats from dictionary"""
        return cls(
            total_requests=data["total_requests"],
            requests_by_endpoint=data["requests_by_endpoint"],
            requests_by_method=data["requests_by_method"],
            average_response_time=data["average_response_time"],
            error_rate=data["error_rate"],
            rate_limit_hits=data["rate_limit_hits"],
            last_24h_requests=data["last_24h_requests"]
        )