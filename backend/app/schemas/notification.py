from pydantic import BaseModel, Field, validator
from typing import Optional, Dict, Any, List
from datetime import datetime
from uuid import UUID

from ..models.notification import (
    NotificationType, NotificationStatus, NotificationPriority, NotificationCategory
)


class NotificationBase(BaseModel):
    title: str = Field(..., max_length=255)
    message: str
    category: NotificationCategory
    priority: NotificationPriority = NotificationPriority.MEDIUM
    data: Optional[Dict[str, Any]] = None
    expires_at: Optional[datetime] = None


class NotificationCreate(NotificationBase):
    user_id: UUID
    type: NotificationType


class NotificationUpdate(BaseModel):
    status: Optional[NotificationStatus] = None
    read_at: Optional[datetime] = None


class NotificationResponse(NotificationBase):
    id: UUID
    user_id: UUID
    type: NotificationType
    status: NotificationStatus
    sent_at: Optional[datetime] = None
    delivered_at: Optional[datetime] = None
    read_at: Optional[datetime] = None
    failed_at: Optional[datetime] = None
    failure_reason: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class NotificationListResponse(BaseModel):
    notifications: List[NotificationResponse]
    total: int
    unread_count: int


class NotificationTemplateBase(BaseModel):
    name: str = Field(..., max_length=100)
    category: NotificationCategory
    type: NotificationType
    subject_template: str = Field(..., max_length=255)
    body_template: str
    variables: Optional[List[str]] = None
    is_active: bool = True


class NotificationTemplateCreate(NotificationTemplateBase):
    pass


class NotificationTemplateUpdate(BaseModel):
    subject_template: Optional[str] = Field(None, max_length=255)
    body_template: Optional[str] = None
    variables: Optional[List[str]] = None
    is_active: Optional[bool] = None


class NotificationTemplateResponse(NotificationTemplateBase):
    id: UUID
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class NotificationPreferenceBase(BaseModel):
    category: NotificationCategory
    email_enabled: bool = True
    sms_enabled: bool = False
    push_enabled: bool = True
    in_app_enabled: bool = True
    immediate: bool = True
    daily_digest: bool = False
    weekly_digest: bool = False


class NotificationPreferenceCreate(NotificationPreferenceBase):
    user_id: UUID


class NotificationPreferenceUpdate(BaseModel):
    email_enabled: Optional[bool] = None
    sms_enabled: Optional[bool] = None
    push_enabled: Optional[bool] = None
    in_app_enabled: Optional[bool] = None
    immediate: Optional[bool] = None
    daily_digest: Optional[bool] = None
    weekly_digest: Optional[bool] = None


class NotificationPreferenceResponse(NotificationPreferenceBase):
    id: UUID
    user_id: UUID
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class NotificationPreferencesResponse(BaseModel):
    preferences: List[NotificationPreferenceResponse]


class BulkNotificationCreate(BaseModel):
    user_ids: List[UUID]
    title: str = Field(..., max_length=255)
    message: str
    category: NotificationCategory
    type: NotificationType
    priority: NotificationPriority = NotificationPriority.MEDIUM
    data: Optional[Dict[str, Any]] = None
    expires_at: Optional[datetime] = None


class NotificationStatsResponse(BaseModel):
    total_sent: int
    total_delivered: int
    total_failed: int
    total_read: int
    delivery_rate: float
    read_rate: float


class SendNotificationRequest(BaseModel):
    template_name: Optional[str] = None
    title: Optional[str] = None
    message: Optional[str] = None
    category: NotificationCategory
    type: NotificationType
    priority: NotificationPriority = NotificationPriority.MEDIUM
    user_ids: List[UUID]
    template_variables: Optional[Dict[str, Any]] = None
    expires_at: Optional[datetime] = None

    @validator('title', 'message')
    def validate_title_or_template(cls, v, values):
        if not values.get('template_name') and not v:
            raise ValueError('Either template_name or title/message must be provided')
        return v