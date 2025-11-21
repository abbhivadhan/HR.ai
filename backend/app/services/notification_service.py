import logging
from typing import Dict, Any, List, Optional, Union
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc
import asyncio
import json
from uuid import UUID

from ..models.notification import (
    Notification, NotificationTemplate, NotificationPreference, NotificationHistory,
    NotificationType, NotificationStatus, NotificationPriority, NotificationCategory
)
from ..models.user import User
from ..database import get_db
from .email_service import EmailService, DEFAULT_EMAIL_TEMPLATES
from .sms_service import SMSService, DEFAULT_SMS_TEMPLATES
from .push_notification_service import PushNotificationService, DEFAULT_PUSH_TEMPLATES

logger = logging.getLogger(__name__)


class NotificationService:
    def __init__(self):
        self.email_service = EmailService()
        self.sms_service = SMSService()
        self.push_service = PushNotificationService()

    async def create_notification(
        self,
        db: Session,
        user_id: UUID,
        title: str,
        message: str,
        category: NotificationCategory,
        notification_type: NotificationType,
        priority: NotificationPriority = NotificationPriority.MEDIUM,
        data: Optional[Dict[str, Any]] = None,
        expires_at: Optional[datetime] = None
    ) -> Notification:
        """Create a new notification"""
        try:
            notification = Notification(
                user_id=user_id,
                type=notification_type,
                category=category,
                priority=priority,
                title=title,
                message=message,
                data=json.dumps(data) if data else None,
                expires_at=expires_at
            )
            
            db.add(notification)
            db.commit()
            db.refresh(notification)
            
            logger.info(f"Created notification {notification.id} for user {user_id}")
            return notification
            
        except Exception as e:
            db.rollback()
            logger.error(f"Failed to create notification: {str(e)}")
            raise

    async def send_notification(
        self,
        db: Session,
        notification_id: UUID,
        force_send: bool = False
    ) -> Dict[str, Any]:
        """Send a notification using the appropriate channel"""
        try:
            # Get notification
            notification = db.query(Notification).filter(
                Notification.id == notification_id
            ).first()
            
            if not notification:
                return {'success': False, 'error': 'Notification not found'}
            
            # Check if already sent
            if notification.status == NotificationStatus.SENT and not force_send:
                return {'success': True, 'message': 'Notification already sent'}
            
            # Get user and preferences
            user = db.query(User).filter(User.id == notification.user_id).first()
            if not user:
                return {'success': False, 'error': 'User not found'}
            
            preferences = self._get_user_preferences(db, notification.user_id, notification.category)
            
            # Check if notification type is enabled for user
            if not self._is_notification_enabled(preferences, notification.type):
                logger.info(f"Notification type {notification.type} disabled for user {notification.user_id}")
                notification.status = NotificationStatus.DELIVERED
                notification.delivered_at = datetime.utcnow()
                db.commit()
                return {'success': True, 'message': 'Notification type disabled by user'}
            
            # Send notification based on type
            result = await self._send_by_type(notification, user)
            
            # Update notification status
            if result['success']:
                notification.status = NotificationStatus.SENT
                notification.sent_at = datetime.utcnow()
            else:
                notification.status = NotificationStatus.FAILED
                notification.failed_at = datetime.utcnow()
                notification.failure_reason = result.get('error', 'Unknown error')
            
            db.commit()
            
            # Log to history
            await self._log_notification_history(db, notification, result)
            
            return result
            
        except Exception as e:
            logger.error(f"Failed to send notification {notification_id}: {str(e)}")
            return {'success': False, 'error': str(e)}

    async def _send_by_type(self, notification: Notification, user: User) -> Dict[str, Any]:
        """Send notification using the specified type"""
        try:
            if notification.type == NotificationType.EMAIL:
                return await self._send_email_notification(notification, user)
            elif notification.type == NotificationType.SMS:
                return await self._send_sms_notification(notification, user)
            elif notification.type == NotificationType.PUSH:
                return await self._send_push_notification(notification, user)
            elif notification.type == NotificationType.IN_APP:
                return await self._send_in_app_notification(notification, user)
            else:
                return {'success': False, 'error': f'Unsupported notification type: {notification.type}'}
                
        except Exception as e:
            logger.error(f"Failed to send {notification.type} notification: {str(e)}")
            return {'success': False, 'error': str(e)}

    async def _send_email_notification(self, notification: Notification, user: User) -> Dict[str, Any]:
        """Send email notification"""
        try:
            # Get email template or use notification content
            template = self._get_email_template(notification.category)
            
            if template:
                # Use template
                variables = self._prepare_template_variables(notification, user)
                return await self.email_service.send_templated_email(
                    to_email=user.email,
                    subject_template=template['subject'],
                    body_template=template['body'],
                    variables=variables,
                    html_template=template.get('html')
                )
            else:
                # Use notification content directly
                return await self.email_service.send_email(
                    to_email=user.email,
                    subject=notification.title,
                    body=notification.message
                )
                
        except Exception as e:
            logger.error(f"Failed to send email notification: {str(e)}")
            return {'success': False, 'error': str(e)}

    async def _send_sms_notification(self, notification: Notification, user: User) -> Dict[str, Any]:
        """Send SMS notification"""
        try:
            # Get user phone number (assuming it's in profile)
            phone_number = getattr(user, 'phone_number', None)
            if not phone_number:
                return {'success': False, 'error': 'User phone number not available'}
            
            # Get SMS template or use notification content
            template = self._get_sms_template(notification.category)
            
            if template:
                variables = self._prepare_template_variables(notification, user)
                return await self.sms_service.send_templated_sms(
                    to_number=phone_number,
                    template=template,
                    variables=variables
                )
            else:
                # Use notification content directly (truncated for SMS)
                message = f"{notification.title}: {notification.message}"
                return await self.sms_service.send_sms(phone_number, message)
                
        except Exception as e:
            logger.error(f"Failed to send SMS notification: {str(e)}")
            return {'success': False, 'error': str(e)}

    async def _send_push_notification(self, notification: Notification, user: User) -> Dict[str, Any]:
        """Send push notification"""
        try:
            # Get user device tokens (assuming they're stored somewhere)
            device_tokens = getattr(user, 'device_tokens', [])
            if not device_tokens:
                return {'success': False, 'error': 'User device tokens not available'}
            
            # Get push template or use notification content
            template = self._get_push_template(notification.category)
            
            if template:
                variables = self._prepare_template_variables(notification, user)
                return await self.push_service.send_templated_push_notification(
                    device_tokens=device_tokens,
                    title_template=template['title'],
                    body_template=template['body'],
                    variables=variables,
                    data=template.get('data', {})
                )
            else:
                return await self.push_service.send_push_notification(
                    device_tokens=device_tokens,
                    title=notification.title,
                    body=notification.message
                )
                
        except Exception as e:
            logger.error(f"Failed to send push notification: {str(e)}")
            return {'success': False, 'error': str(e)}

    async def _send_in_app_notification(self, notification: Notification, user: User) -> Dict[str, Any]:
        """Send in-app notification (just mark as delivered since it's stored in DB)"""
        try:
            # In-app notifications are stored in the database and displayed in the UI
            # No external service call needed
            return {
                'success': True,
                'message': 'In-app notification ready for display',
                'recipient': str(user.id)
            }
        except Exception as e:
            logger.error(f"Failed to process in-app notification: {str(e)}")
            return {'success': False, 'error': str(e)}

    def _get_user_preferences(
        self,
        db: Session,
        user_id: UUID,
        category: NotificationCategory
    ) -> Optional[NotificationPreference]:
        """Get user notification preferences for category"""
        return db.query(NotificationPreference).filter(
            and_(
                NotificationPreference.user_id == user_id,
                NotificationPreference.category == category
            )
        ).first()

    def _is_notification_enabled(
        self,
        preferences: Optional[NotificationPreference],
        notification_type: NotificationType
    ) -> bool:
        """Check if notification type is enabled for user"""
        if not preferences:
            # Default preferences if none set
            return notification_type in [NotificationType.EMAIL, NotificationType.IN_APP]
        
        if notification_type == NotificationType.EMAIL:
            return preferences.email_enabled
        elif notification_type == NotificationType.SMS:
            return preferences.sms_enabled
        elif notification_type == NotificationType.PUSH:
            return preferences.push_enabled
        elif notification_type == NotificationType.IN_APP:
            return preferences.in_app_enabled
        
        return False

    def _get_email_template(self, category: NotificationCategory) -> Optional[Dict[str, str]]:
        """Get email template for category"""
        template_map = {
            NotificationCategory.JOB_MATCH: 'job_match_notification',
            NotificationCategory.ASSESSMENT_REMINDER: 'assessment_reminder'
        }
        
        template_name = template_map.get(category)
        return DEFAULT_EMAIL_TEMPLATES.get(template_name) if template_name else None

    def _get_sms_template(self, category: NotificationCategory) -> Optional[str]:
        """Get SMS template for category"""
        template_map = {
            NotificationCategory.JOB_MATCH: 'job_match_notification',
            NotificationCategory.ASSESSMENT_REMINDER: 'assessment_reminder',
            NotificationCategory.INTERVIEW_SCHEDULED: 'interview_scheduled',
            NotificationCategory.APPLICATION_UPDATE: 'application_update',
            NotificationCategory.SECURITY_ALERT: 'security_alert'
        }
        
        template_name = template_map.get(category)
        return DEFAULT_SMS_TEMPLATES.get(template_name) if template_name else None

    def _get_push_template(self, category: NotificationCategory) -> Optional[Dict[str, Any]]:
        """Get push notification template for category"""
        template_map = {
            NotificationCategory.JOB_MATCH: 'job_match_notification',
            NotificationCategory.ASSESSMENT_REMINDER: 'assessment_reminder',
            NotificationCategory.INTERVIEW_SCHEDULED: 'interview_scheduled',
            NotificationCategory.APPLICATION_UPDATE: 'application_update'
        }
        
        template_name = template_map.get(category)
        return DEFAULT_PUSH_TEMPLATES.get(template_name) if template_name else None

    def _prepare_template_variables(self, notification: Notification, user: User) -> Dict[str, Any]:
        """Prepare variables for template rendering"""
        from ..config import settings
        
        variables = {
            'user_name': user.full_name,
            'user_email': user.email,
            'notification_title': notification.title,
            'notification_message': notification.message,
            'platform_name': 'AI-HR Platform',
            'support_email': 'support@ai-hr-platform.com',
            'dashboard_url': f"{getattr(settings, 'frontend_url', 'http://localhost:3000')}/dashboard"
        }
        
        # Add notification data if available
        if notification.data:
            try:
                data = json.loads(notification.data)
                variables.update(data)
            except json.JSONDecodeError:
                logger.warning(f"Failed to parse notification data for {notification.id}")
        
        return variables

    async def _log_notification_history(
        self,
        db: Session,
        notification: Notification,
        result: Dict[str, Any]
    ):
        """Log notification delivery attempt to history"""
        try:
            history = NotificationHistory(
                notification_id=notification.id,
                attempt_number="1",  # Could be enhanced to track multiple attempts
                status=notification.status,
                response_data=json.dumps(result) if result else None,
                error_message=result.get('error') if not result.get('success') else None
            )
            
            db.add(history)
            db.commit()
            
        except Exception as e:
            logger.error(f"Failed to log notification history: {str(e)}")

    async def send_bulk_notifications(
        self,
        db: Session,
        user_ids: List[UUID],
        title: str,
        message: str,
        category: NotificationCategory,
        notification_type: NotificationType,
        priority: NotificationPriority = NotificationPriority.MEDIUM,
        data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Send notifications to multiple users"""
        try:
            created_notifications = []
            
            # Create notifications for all users
            for user_id in user_ids:
                notification = await self.create_notification(
                    db, user_id, title, message, category, notification_type, priority, data
                )
                created_notifications.append(notification)
            
            # Send all notifications
            send_tasks = []
            for notification in created_notifications:
                task = self.send_notification(db, notification.id)
                send_tasks.append(task)
            
            results = await asyncio.gather(*send_tasks, return_exceptions=True)
            
            # Process results
            successful = sum(1 for r in results if isinstance(r, dict) and r.get('success'))
            failed = len(results) - successful
            
            return {
                'success': True,
                'total_sent': len(user_ids),
                'successful': successful,
                'failed': failed,
                'results': results
            }
            
        except Exception as e:
            logger.error(f"Failed to send bulk notifications: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'total_sent': len(user_ids),
                'successful': 0,
                'failed': len(user_ids)
            }

    def get_user_notifications(
        self,
        db: Session,
        user_id: UUID,
        limit: int = 50,
        offset: int = 0,
        unread_only: bool = False
    ) -> Dict[str, Any]:
        """Get notifications for a user"""
        try:
            query = db.query(Notification).filter(Notification.user_id == user_id)
            
            if unread_only:
                query = query.filter(Notification.read_at.is_(None))
            
            # Get total count
            total = query.count()
            
            # Get notifications with pagination
            notifications = query.order_by(desc(Notification.created_at)).offset(offset).limit(limit).all()
            
            # Get unread count
            unread_count = db.query(Notification).filter(
                and_(
                    Notification.user_id == user_id,
                    Notification.read_at.is_(None)
                )
            ).count()
            
            return {
                'notifications': notifications,
                'total': total,
                'unread_count': unread_count
            }
            
        except Exception as e:
            logger.error(f"Failed to get user notifications: {str(e)}")
            return {
                'notifications': [],
                'total': 0,
                'unread_count': 0
            }

    def mark_notification_as_read(
        self,
        db: Session,
        notification_id: UUID,
        user_id: UUID
    ) -> bool:
        """Mark a notification as read"""
        try:
            notification = db.query(Notification).filter(
                and_(
                    Notification.id == notification_id,
                    Notification.user_id == user_id
                )
            ).first()
            
            if notification and not notification.read_at:
                notification.read_at = datetime.utcnow()
                notification.status = NotificationStatus.READ
                db.commit()
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Failed to mark notification as read: {str(e)}")
            return False

    def get_notification_stats(
        self,
        db: Session,
        user_id: Optional[UUID] = None,
        category: Optional[NotificationCategory] = None,
        days: int = 30
    ) -> Dict[str, Any]:
        """Get notification statistics"""
        try:
            # Base query
            query = db.query(Notification)
            
            # Apply filters
            if user_id:
                query = query.filter(Notification.user_id == user_id)
            
            if category:
                query = query.filter(Notification.category == category)
            
            # Date filter
            since_date = datetime.utcnow() - timedelta(days=days)
            query = query.filter(Notification.created_at >= since_date)
            
            # Get counts by status
            total_sent = query.filter(Notification.status == NotificationStatus.SENT).count()
            total_delivered = query.filter(Notification.status == NotificationStatus.DELIVERED).count()
            total_failed = query.filter(Notification.status == NotificationStatus.FAILED).count()
            total_read = query.filter(Notification.status == NotificationStatus.READ).count()
            
            total_notifications = query.count()
            
            # Calculate rates
            delivery_rate = (total_delivered / total_notifications * 100) if total_notifications > 0 else 0
            read_rate = (total_read / total_notifications * 100) if total_notifications > 0 else 0
            
            return {
                'total_sent': total_sent,
                'total_delivered': total_delivered,
                'total_failed': total_failed,
                'total_read': total_read,
                'delivery_rate': round(delivery_rate, 2),
                'read_rate': round(read_rate, 2)
            }
            
        except Exception as e:
            logger.error(f"Failed to get notification stats: {str(e)}")
            return {
                'total_sent': 0,
                'total_delivered': 0,
                'total_failed': 0,
                'total_read': 0,
                'delivery_rate': 0.0,
                'read_rate': 0.0
            }