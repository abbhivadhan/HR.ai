"""
Webhook System API

Provides webhook management, event delivery, and real-time integrations.
"""

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, status
from sqlalchemy.orm import Session
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from enum import Enum
import json
import hmac
import hashlib
import uuid
from pydantic import BaseModel, Field, HttpUrl

from ..database import get_db
from ..auth.dependencies import get_current_user
from ..models.user import User
from ..services.webhook_service import WebhookService, WebhookDeliveryService

router = APIRouter(prefix="/api/webhooks", tags=["webhooks"])


class WebhookEventType(str, Enum):
    """Supported webhook event types"""
    USER_REGISTERED = "user.registered"
    USER_VERIFIED = "user.verified"
    ASSESSMENT_STARTED = "assessment.started"
    ASSESSMENT_COMPLETED = "assessment.completed"
    INTERVIEW_SCHEDULED = "interview.scheduled"
    INTERVIEW_COMPLETED = "interview.completed"
    JOB_POSTED = "job.posted"
    JOB_APPLICATION = "job.application"
    MATCH_FOUND = "match.found"
    NOTIFICATION_SENT = "notification.sent"


class WebhookStatus(str, Enum):
    """Webhook endpoint status"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    FAILED = "failed"
    DISABLED = "disabled"


class WebhookCreate(BaseModel):
    """Create webhook endpoint model"""
    url: HttpUrl = Field(..., description="Webhook endpoint URL")
    events: List[WebhookEventType] = Field(..., description="Events to subscribe to")
    secret: Optional[str] = Field(default=None, description="Secret for signature verification")
    description: Optional[str] = Field(default=None, description="Webhook description")
    is_active: bool = Field(default=True, description="Whether webhook is active")


class WebhookUpdate(BaseModel):
    """Update webhook endpoint model"""
    url: Optional[HttpUrl] = Field(default=None, description="Webhook endpoint URL")
    events: Optional[List[WebhookEventType]] = Field(default=None, description="Events to subscribe to")
    secret: Optional[str] = Field(default=None, description="Secret for signature verification")
    description: Optional[str] = Field(default=None, description="Webhook description")
    is_active: Optional[bool] = Field(default=None, description="Whether webhook is active")


class WebhookResponse(BaseModel):
    """Webhook endpoint response model"""
    id: str
    url: str
    events: List[WebhookEventType]
    description: Optional[str]
    is_active: bool
    status: WebhookStatus
    created_at: datetime
    updated_at: datetime
    last_delivery_at: Optional[datetime]
    success_rate: float
    total_deliveries: int
    failed_deliveries: int


class WebhookDelivery(BaseModel):
    """Webhook delivery model"""
    id: str
    webhook_id: str
    event_type: WebhookEventType
    payload: Dict[str, Any]
    status_code: Optional[int]
    response_body: Optional[str]
    delivery_time_ms: Optional[float]
    attempts: int
    max_attempts: int
    next_retry_at: Optional[datetime]
    delivered_at: Optional[datetime]
    created_at: datetime


class WebhookEvent(BaseModel):
    """Webhook event payload model"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    event_type: WebhookEventType
    timestamp: datetime = Field(default_factory=datetime.now)
    data: Dict[str, Any]
    user_id: Optional[str] = None
    company_id: Optional[str] = None


@router.post("/", response_model=WebhookResponse, status_code=status.HTTP_201_CREATED)
async def create_webhook(
    webhook_data: WebhookCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new webhook endpoint"""
    
    webhook_service = WebhookService(db)
    webhook = await webhook_service.create_webhook(current_user.id, webhook_data)
    
    return WebhookResponse(
        id=webhook.id,
        url=str(webhook.url),
        events=webhook.events,
        description=webhook.description,
        is_active=webhook.is_active,
        status=webhook.status,
        created_at=webhook.created_at,
        updated_at=webhook.updated_at,
        last_delivery_at=webhook.last_delivery_at,
        success_rate=webhook.success_rate,
        total_deliveries=webhook.total_deliveries,
        failed_deliveries=webhook.failed_deliveries
    )


@router.get("/", response_model=List[WebhookResponse])
async def list_webhooks(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List all webhook endpoints for the current user"""
    
    webhook_service = WebhookService(db)
    webhooks = await webhook_service.get_user_webhooks(current_user.id)
    
    return [
        WebhookResponse(
            id=webhook.id,
            url=str(webhook.url),
            events=webhook.events,
            description=webhook.description,
            is_active=webhook.is_active,
            status=webhook.status,
            created_at=webhook.created_at,
            updated_at=webhook.updated_at,
            last_delivery_at=webhook.last_delivery_at,
            success_rate=webhook.success_rate,
            total_deliveries=webhook.total_deliveries,
            failed_deliveries=webhook.failed_deliveries
        )
        for webhook in webhooks
    ]


@router.get("/{webhook_id}", response_model=WebhookResponse)
async def get_webhook(
    webhook_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get a specific webhook endpoint"""
    
    webhook_service = WebhookService(db)
    webhook = await webhook_service.get_webhook(webhook_id, current_user.id)
    
    if not webhook:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Webhook not found"
        )
    
    return WebhookResponse(
        id=webhook.id,
        url=str(webhook.url),
        events=webhook.events,
        description=webhook.description,
        is_active=webhook.is_active,
        status=webhook.status,
        created_at=webhook.created_at,
        updated_at=webhook.updated_at,
        last_delivery_at=webhook.last_delivery_at,
        success_rate=webhook.success_rate,
        total_deliveries=webhook.total_deliveries,
        failed_deliveries=webhook.failed_deliveries
    )


@router.put("/{webhook_id}", response_model=WebhookResponse)
async def update_webhook(
    webhook_id: str,
    webhook_data: WebhookUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update a webhook endpoint"""
    
    webhook_service = WebhookService(db)
    webhook = await webhook_service.update_webhook(webhook_id, current_user.id, webhook_data)
    
    if not webhook:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Webhook not found"
        )
    
    return WebhookResponse(
        id=webhook.id,
        url=str(webhook.url),
        events=webhook.events,
        description=webhook.description,
        is_active=webhook.is_active,
        status=webhook.status,
        created_at=webhook.created_at,
        updated_at=webhook.updated_at,
        last_delivery_at=webhook.last_delivery_at,
        success_rate=webhook.success_rate,
        total_deliveries=webhook.total_deliveries,
        failed_deliveries=webhook.failed_deliveries
    )


@router.delete("/{webhook_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_webhook(
    webhook_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete a webhook endpoint"""
    
    webhook_service = WebhookService(db)
    success = await webhook_service.delete_webhook(webhook_id, current_user.id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Webhook not found"
        )


@router.post("/{webhook_id}/test")
async def test_webhook(
    webhook_id: str,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Test a webhook endpoint with a sample event"""
    
    webhook_service = WebhookService(db)
    webhook = await webhook_service.get_webhook(webhook_id, current_user.id)
    
    if not webhook:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Webhook not found"
        )
    
    # Create test event
    test_event = WebhookEvent(
        event_type=WebhookEventType.USER_REGISTERED,
        data={
            "user_id": str(current_user.id),
            "email": current_user.email,
            "user_type": current_user.user_type.value,
            "test": True
        },
        user_id=str(current_user.id)
    )
    
    # Deliver webhook in background
    delivery_service = WebhookDeliveryService(db)
    background_tasks.add_task(
        delivery_service.deliver_webhook,
        webhook,
        test_event
    )
    
    return {
        "message": "Test webhook delivery initiated",
        "webhook_id": webhook_id,
        "event_type": test_event.event_type
    }


@router.get("/{webhook_id}/deliveries", response_model=List[WebhookDelivery])
async def get_webhook_deliveries(
    webhook_id: str,
    limit: int = 50,
    offset: int = 0,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get delivery history for a webhook"""
    
    webhook_service = WebhookService(db)
    webhook = await webhook_service.get_webhook(webhook_id, current_user.id)
    
    if not webhook:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Webhook not found"
        )
    
    deliveries = await webhook_service.get_webhook_deliveries(webhook_id, limit, offset)
    
    return [
        WebhookDelivery(
            id=delivery.id,
            webhook_id=delivery.webhook_id,
            event_type=delivery.event_type,
            payload=delivery.payload,
            status_code=delivery.status_code,
            response_body=delivery.response_body,
            delivery_time_ms=delivery.delivery_time_ms,
            attempts=delivery.attempts,
            max_attempts=delivery.max_attempts,
            next_retry_at=delivery.next_retry_at,
            delivered_at=delivery.delivered_at,
            created_at=delivery.created_at
        )
        for delivery in deliveries
    ]


@router.post("/{webhook_id}/deliveries/{delivery_id}/retry")
async def retry_webhook_delivery(
    webhook_id: str,
    delivery_id: str,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Retry a failed webhook delivery"""
    
    webhook_service = WebhookService(db)
    webhook = await webhook_service.get_webhook(webhook_id, current_user.id)
    
    if not webhook:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Webhook not found"
        )
    
    delivery_service = WebhookDeliveryService(db)
    success = await delivery_service.retry_delivery(delivery_id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Delivery not found or cannot be retried"
        )
    
    return {
        "message": "Webhook delivery retry initiated",
        "delivery_id": delivery_id
    }


@router.get("/events/types")
async def get_event_types():
    """Get all available webhook event types"""
    
    return {
        "event_types": [
            {
                "type": event_type.value,
                "description": get_event_description(event_type)
            }
            for event_type in WebhookEventType
        ]
    }


@router.get("/events/schema/{event_type}")
async def get_event_schema(event_type: WebhookEventType):
    """Get the schema for a specific event type"""
    
    schemas = {
        WebhookEventType.USER_REGISTERED: {
            "type": "object",
            "properties": {
                "user_id": {"type": "string", "format": "uuid"},
                "email": {"type": "string", "format": "email"},
                "user_type": {"type": "string", "enum": ["candidate", "company", "admin"]},
                "first_name": {"type": "string"},
                "last_name": {"type": "string"},
                "created_at": {"type": "string", "format": "date-time"}
            },
            "required": ["user_id", "email", "user_type"]
        },
        WebhookEventType.ASSESSMENT_COMPLETED: {
            "type": "object",
            "properties": {
                "assessment_id": {"type": "string", "format": "uuid"},
                "candidate_id": {"type": "string", "format": "uuid"},
                "assessment_type": {"type": "string"},
                "score": {"type": "number", "minimum": 0, "maximum": 1},
                "completed_at": {"type": "string", "format": "date-time"},
                "duration_minutes": {"type": "integer", "minimum": 0}
            },
            "required": ["assessment_id", "candidate_id", "score"]
        },
        WebhookEventType.JOB_APPLICATION: {
            "type": "object",
            "properties": {
                "application_id": {"type": "string", "format": "uuid"},
                "job_id": {"type": "string", "format": "uuid"},
                "candidate_id": {"type": "string", "format": "uuid"},
                "company_id": {"type": "string", "format": "uuid"},
                "status": {"type": "string", "enum": ["applied", "reviewed", "interviewed", "offered", "rejected"]},
                "applied_at": {"type": "string", "format": "date-time"}
            },
            "required": ["application_id", "job_id", "candidate_id", "company_id"]
        }
    }
    
    schema = schemas.get(event_type)
    if not schema:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Schema not found for event type: {event_type}"
        )
    
    return {
        "event_type": event_type,
        "schema": schema,
        "example": generate_event_example(event_type)
    }


def get_event_description(event_type: WebhookEventType) -> str:
    """Get description for webhook event type"""
    
    descriptions = {
        WebhookEventType.USER_REGISTERED: "Triggered when a new user registers on the platform",
        WebhookEventType.USER_VERIFIED: "Triggered when a user verifies their email address",
        WebhookEventType.ASSESSMENT_STARTED: "Triggered when a candidate starts an assessment",
        WebhookEventType.ASSESSMENT_COMPLETED: "Triggered when a candidate completes an assessment",
        WebhookEventType.INTERVIEW_SCHEDULED: "Triggered when an interview is scheduled",
        WebhookEventType.INTERVIEW_COMPLETED: "Triggered when an interview is completed",
        WebhookEventType.JOB_POSTED: "Triggered when a company posts a new job",
        WebhookEventType.JOB_APPLICATION: "Triggered when a candidate applies for a job",
        WebhookEventType.MATCH_FOUND: "Triggered when the AI finds a good candidate-job match",
        WebhookEventType.NOTIFICATION_SENT: "Triggered when a notification is sent to a user"
    }
    
    return descriptions.get(event_type, "No description available")


def generate_event_example(event_type: WebhookEventType) -> Dict[str, Any]:
    """Generate example payload for event type"""
    
    examples = {
        WebhookEventType.USER_REGISTERED: {
            "user_id": "123e4567-e89b-12d3-a456-426614174000",
            "email": "john.doe@example.com",
            "user_type": "candidate",
            "first_name": "John",
            "last_name": "Doe",
            "created_at": "2024-01-01T12:00:00Z"
        },
        WebhookEventType.ASSESSMENT_COMPLETED: {
            "assessment_id": "assess_123456789",
            "candidate_id": "123e4567-e89b-12d3-a456-426614174000",
            "assessment_type": "technical",
            "score": 0.85,
            "completed_at": "2024-01-01T13:30:00Z",
            "duration_minutes": 45
        },
        WebhookEventType.JOB_APPLICATION: {
            "application_id": "app_123456789",
            "job_id": "job_987654321",
            "candidate_id": "123e4567-e89b-12d3-a456-426614174000",
            "company_id": "456e7890-e89b-12d3-a456-426614174000",
            "status": "applied",
            "applied_at": "2024-01-01T14:00:00Z"
        }
    }
    
    return examples.get(event_type, {})