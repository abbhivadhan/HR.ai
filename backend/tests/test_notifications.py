import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from uuid import uuid4
from datetime import datetime, timedelta

from ..app.main import app
from ..app.models.notification import (
    Notification, NotificationPreference, NotificationTemplate,
    NotificationType, NotificationCategory, NotificationPriority, NotificationStatus
)
from ..app.models.user import User, UserType
from ..app.services.notification_service import NotificationService

client = TestClient(app)


@pytest.fixture
def notification_service():
    return NotificationService()


@pytest.fixture
def test_user(db_session: Session):
    user = User(
        id=uuid4(),
        email="test@example.com",
        password_hash="hashed_password",
        first_name="Test",
        last_name="User",
        user_type=UserType.CANDIDATE,
        is_active=True,
        is_verified=True
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def test_notification(db_session: Session, test_user: User):
    notification = Notification(
        id=uuid4(),
        user_id=test_user.id,
        type=NotificationType.IN_APP,
        category=NotificationCategory.JOB_MATCH,
        priority=NotificationPriority.MEDIUM,
        title="Test Notification",
        message="This is a test notification",
        status=NotificationStatus.PENDING
    )
    db_session.add(notification)
    db_session.commit()
    db_session.refresh(notification)
    return notification


class TestNotificationService:
    """Test notification service functionality"""
    
    @pytest.mark.asyncio
    async def test_create_notification(self, db_session: Session, test_user: User, notification_service: NotificationService):
        """Test creating a new notification"""
        notification = await notification_service.create_notification(
            db=db_session,
            user_id=test_user.id,
            title="Test Notification",
            message="Test message",
            category=NotificationCategory.JOB_MATCH,
            notification_type=NotificationType.EMAIL,
            priority=NotificationPriority.HIGH
        )
        
        assert notification.id is not None
        assert notification.user_id == test_user.id
        assert notification.title == "Test Notification"
        assert notification.message == "Test message"
        assert notification.category == NotificationCategory.JOB_MATCH
        assert notification.type == NotificationType.EMAIL
        assert notification.priority == NotificationPriority.HIGH
        assert notification.status == NotificationStatus.PENDING

    @pytest.mark.asyncio
    async def test_send_in_app_notification(self, db_session: Session, test_notification: Notification, notification_service: NotificationService):
        """Test sending in-app notification"""
        result = await notification_service.send_notification(
            db=db_session,
            notification_id=test_notification.id
        )
        
        assert result['success'] is True
        
        # Refresh notification from database
        db_session.refresh(test_notification)
        assert test_notification.status == NotificationStatus.SENT
        assert test_notification.sent_at is not None

    def test_get_user_notifications(self, db_session: Session, test_user: User, notification_service: NotificationService):
        """Test getting user notifications"""
        result = notification_service.get_user_notifications(
            db=db_session,
            user_id=test_user.id,
            limit=10,
            offset=0
        )
        
        assert 'notifications' in result
        assert 'total' in result
        assert 'unread_count' in result
        assert isinstance(result['notifications'], list)

    def test_mark_notification_as_read(self, db_session: Session, test_notification: Notification, notification_service: NotificationService):
        """Test marking notification as read"""
        success = notification_service.mark_notification_as_read(
            db=db_session,
            notification_id=test_notification.id,
            user_id=test_notification.user_id
        )
        
        assert success is True
        
        # Refresh notification from database
        db_session.refresh(test_notification)
        assert test_notification.read_at is not None
        assert test_notification.status == NotificationStatus.READ

    @pytest.mark.asyncio
    async def test_send_bulk_notifications(self, db_session: Session, test_user: User, notification_service: NotificationService):
        """Test sending bulk notifications"""
        result = await notification_service.send_bulk_notifications(
            db=db_session,
            user_ids=[test_user.id],
            title="Bulk Test",
            message="Bulk test message",
            category=NotificationCategory.SYSTEM_ALERT,
            notification_type=NotificationType.IN_APP
        )
        
        assert result['success'] is True
        assert result['total_sent'] == 1
        assert result['successful'] >= 0
        assert result['failed'] >= 0


class TestNotificationAPI:
    """Test notification API endpoints"""
    
    def test_get_notifications_unauthorized(self):
        """Test getting notifications without authentication"""
        response = client.get("/api/notifications/")
        assert response.status_code == 401

    def test_get_notifications_with_auth(self, auth_headers):
        """Test getting notifications with authentication"""
        response = client.get("/api/notifications/", headers=auth_headers)
        assert response.status_code == 200
        
        data = response.json()
        assert 'notifications' in data
        assert 'total' in data
        assert 'unread_count' in data

    def test_mark_notification_read(self, auth_headers, test_notification: Notification):
        """Test marking notification as read via API"""
        response = client.post(
            f"/api/notifications/{test_notification.id}/mark-read",
            headers=auth_headers
        )
        assert response.status_code == 200

    def test_get_notification_preferences(self, auth_headers):
        """Test getting notification preferences"""
        response = client.get("/api/notifications/preferences/", headers=auth_headers)
        assert response.status_code == 200
        
        data = response.json()
        assert 'preferences' in data

    def test_update_notification_preference(self, auth_headers):
        """Test updating notification preferences"""
        preference_data = {
            "email_enabled": True,
            "sms_enabled": False,
            "push_enabled": True,
            "in_app_enabled": True
        }
        
        response = client.put(
            f"/api/notifications/preferences/{NotificationCategory.JOB_MATCH}",
            json=preference_data,
            headers=auth_headers
        )
        assert response.status_code == 200


class TestEmailService:
    """Test email service functionality"""
    
    @pytest.mark.asyncio
    async def test_email_service_initialization(self):
        """Test email service initialization"""
        from ..app.services.email_service import EmailService
        
        email_service = EmailService()
        assert email_service is not None

    @pytest.mark.asyncio
    async def test_render_template(self):
        """Test email template rendering"""
        from ..app.services.email_service import EmailService
        
        email_service = EmailService()
        template = "Hello {{name}}, welcome to {{platform}}!"
        variables = {"name": "John", "platform": "AI-HR Platform"}
        
        result = email_service._render_template(template, variables)
        assert result == "Hello John, welcome to AI-HR Platform!"


class TestSMSService:
    """Test SMS service functionality"""
    
    @pytest.mark.asyncio
    async def test_sms_service_initialization(self):
        """Test SMS service initialization"""
        from ..app.services.sms_service import SMSService
        
        sms_service = SMSService()
        assert sms_service is not None

    @pytest.mark.asyncio
    async def test_render_sms_template(self):
        """Test SMS template rendering"""
        from ..app.services.sms_service import SMSService
        
        sms_service = SMSService()
        template = "Job match: {{job_title}} at {{company}}. {{match_score}}% match."
        variables = {"job_title": "Developer", "company": "TechCorp", "match_score": "95"}
        
        result = sms_service._render_template(template, variables)
        assert result == "Job match: Developer at TechCorp. 95% match."


class TestPushNotificationService:
    """Test push notification service functionality"""
    
    @pytest.mark.asyncio
    async def test_push_service_initialization(self):
        """Test push notification service initialization"""
        from ..app.services.push_notification_service import PushNotificationService
        
        push_service = PushNotificationService()
        assert push_service is not None

    @pytest.mark.asyncio
    async def test_render_push_template(self):
        """Test push notification template rendering"""
        from ..app.services.push_notification_service import PushNotificationService
        
        push_service = PushNotificationService()
        template = "New job: {{job_title}} - {{match_score}}% match"
        variables = {"job_title": "Software Engineer", "match_score": "90"}
        
        result = push_service._render_template(template, variables)
        assert result == "New job: Software Engineer - 90% match"


class TestNotificationModels:
    """Test notification database models"""
    
    def test_notification_model_creation(self, db_session: Session, test_user: User):
        """Test creating notification model"""
        notification = Notification(
            user_id=test_user.id,
            type=NotificationType.EMAIL,
            category=NotificationCategory.JOB_MATCH,
            priority=NotificationPriority.HIGH,
            title="Test Notification",
            message="Test message"
        )
        
        db_session.add(notification)
        db_session.commit()
        db_session.refresh(notification)
        
        assert notification.id is not None
        assert notification.user_id == test_user.id
        assert notification.status == NotificationStatus.PENDING

    def test_notification_preference_model(self, db_session: Session, test_user: User):
        """Test creating notification preference model"""
        preference = NotificationPreference(
            user_id=test_user.id,
            category=NotificationCategory.JOB_MATCH,
            email_enabled=True,
            sms_enabled=False,
            push_enabled=True,
            in_app_enabled=True
        )
        
        db_session.add(preference)
        db_session.commit()
        db_session.refresh(preference)
        
        assert preference.id is not None
        assert preference.user_id == test_user.id
        assert preference.email_enabled is True
        assert preference.sms_enabled is False