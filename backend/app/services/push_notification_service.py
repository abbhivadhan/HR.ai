import logging
from typing import Dict, Any, List, Optional
import asyncio
import httpx
import json
from jinja2 import Template

from ..config import settings

logger = logging.getLogger(__name__)


class PushNotificationService:
    def __init__(self):
        self.firebase_server_key = settings.firebase_server_key
        self.firebase_project_id = settings.firebase_project_id
        self.apns_key_id = settings.apns_key_id
        self.apns_team_id = settings.apns_team_id
        self.apns_bundle_id = settings.apns_bundle_id
        self.apns_private_key = settings.apns_private_key

    def _render_template(self, template_str: str, variables: Dict[str, Any]) -> str:
        """Render push notification template with variables"""
        try:
            template = Template(template_str)
            return template.render(**variables)
        except Exception as e:
            logger.error(f"Failed to render push notification template: {str(e)}")
            raise

    async def _send_fcm_notification(
        self,
        device_tokens: List[str],
        title: str,
        body: str,
        data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Send push notification using Firebase Cloud Messaging"""
        try:
            url = "https://fcm.googleapis.com/fcm/send"
            
            headers = {
                'Authorization': f'key={self.firebase_server_key}',
                'Content-Type': 'application/json'
            }
            
            # Prepare notification payload
            notification_data = {
                'title': title,
                'body': body,
                'icon': '/icon-192x192.png',  # Default app icon
                'badge': '/badge-72x72.png',
                'click_action': settings.frontend_url
            }
            
            # Prepare data payload
            data_payload = data or {}
            data_payload.update({
                'timestamp': str(asyncio.get_event_loop().time()),
                'app_version': settings.app_version or '1.0.0'
            })
            
            results = []
            
            # Send to each device token
            for token in device_tokens:
                payload = {
                    'to': token,
                    'notification': notification_data,
                    'data': data_payload,
                    'priority': 'high',
                    'time_to_live': 3600  # 1 hour
                }
                
                async with httpx.AsyncClient() as client:
                    response = await client.post(
                        url,
                        headers=headers,
                        json=payload,
                        timeout=30.0
                    )
                    
                    if response.status_code == 200:
                        result = response.json()
                        if result.get('success', 0) > 0:
                            logger.info(f"Push notification sent successfully to token: {token[:20]}...")
                            results.append({
                                'success': True,
                                'token': token,
                                'message_id': result.get('results', [{}])[0].get('message_id')
                            })
                        else:
                            error = result.get('results', [{}])[0].get('error', 'Unknown error')
                            logger.error(f"FCM error for token {token[:20]}...: {error}")
                            results.append({
                                'success': False,
                                'token': token,
                                'error': error
                            })
                    else:
                        error_msg = f"FCM API error: {response.status_code} - {response.text}"
                        logger.error(error_msg)
                        results.append({
                            'success': False,
                            'token': token,
                            'error': error_msg
                        })
            
            success_count = sum(1 for r in results if r['success'])
            return {
                'success': success_count > 0,
                'total_sent': len(device_tokens),
                'successful': success_count,
                'failed': len(device_tokens) - success_count,
                'results': results
            }
            
        except Exception as e:
            error_msg = f"Failed to send FCM notifications: {str(e)}"
            logger.error(error_msg)
            return {
                'success': False,
                'error': error_msg,
                'total_sent': len(device_tokens),
                'successful': 0,
                'failed': len(device_tokens)
            }

    async def _send_apns_notification(
        self,
        device_tokens: List[str],
        title: str,
        body: str,
        data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Send push notification using Apple Push Notification Service"""
        try:
            # This is a simplified APNS implementation
            # In production, you would use a proper APNS library like aioapns
            
            results = []
            
            for token in device_tokens:
                # Prepare APNS payload
                payload = {
                    'aps': {
                        'alert': {
                            'title': title,
                            'body': body
                        },
                        'badge': 1,
                        'sound': 'default'
                    }
                }
                
                if data:
                    payload.update(data)
                
                # For now, we'll simulate APNS sending
                # In production, implement proper APNS HTTP/2 API calls
                logger.info(f"Would send APNS notification to token: {token[:20]}...")
                results.append({
                    'success': True,
                    'token': token,
                    'message': 'APNS notification simulated'
                })
            
            return {
                'success': True,
                'total_sent': len(device_tokens),
                'successful': len(device_tokens),
                'failed': 0,
                'results': results
            }
            
        except Exception as e:
            error_msg = f"Failed to send APNS notifications: {str(e)}"
            logger.error(error_msg)
            return {
                'success': False,
                'error': error_msg,
                'total_sent': len(device_tokens),
                'successful': 0,
                'failed': len(device_tokens)
            }

    async def send_push_notification(
        self,
        device_tokens: List[str],
        title: str,
        body: str,
        data: Optional[Dict[str, Any]] = None,
        platform: str = 'android'  # 'android', 'ios', 'web'
    ) -> Dict[str, Any]:
        """Send push notification to specified devices"""
        if not device_tokens:
            return {
                'success': False,
                'error': 'No device tokens provided',
                'total_sent': 0,
                'successful': 0,
                'failed': 0
            }
        
        # Filter out invalid tokens
        valid_tokens = [token for token in device_tokens if token and len(token) > 10]
        
        if not valid_tokens:
            return {
                'success': False,
                'error': 'No valid device tokens provided',
                'total_sent': 0,
                'successful': 0,
                'failed': len(device_tokens)
            }
        
        if platform.lower() == 'ios':
            return await self._send_apns_notification(valid_tokens, title, body, data)
        else:
            # Default to FCM for Android and Web
            return await self._send_fcm_notification(valid_tokens, title, body, data)

    async def send_templated_push_notification(
        self,
        device_tokens: List[str],
        title_template: str,
        body_template: str,
        variables: Dict[str, Any],
        data: Optional[Dict[str, Any]] = None,
        platform: str = 'android'
    ) -> Dict[str, Any]:
        """Send push notification using templates"""
        try:
            title = self._render_template(title_template, variables)
            body = self._render_template(body_template, variables)
            
            return await self.send_push_notification(
                device_tokens, title, body, data, platform
            )
        except Exception as e:
            error_msg = f"Failed to send templated push notification: {str(e)}"
            logger.error(error_msg)
            return {
                'success': False,
                'error': error_msg,
                'total_sent': len(device_tokens),
                'successful': 0,
                'failed': len(device_tokens)
            }

    async def send_bulk_push_notifications(
        self,
        notifications: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Send bulk push notifications"""
        tasks = []
        
        for notification in notifications:
            task = self.send_push_notification(
                device_tokens=notification['device_tokens'],
                title=notification['title'],
                body=notification['body'],
                data=notification.get('data'),
                platform=notification.get('platform', 'android')
            )
            tasks.append(task)

        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Process results
        processed_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                processed_results.append({
                    'success': False,
                    'error': str(result),
                    'notification_index': i
                })
            else:
                processed_results.append(result)

        return processed_results

    def validate_push_config(self) -> bool:
        """Validate push notification configuration"""
        try:
            # Check if at least one push service is configured
            fcm_configured = bool(self.firebase_server_key)
            apns_configured = bool(
                self.apns_key_id and 
                self.apns_team_id and 
                self.apns_bundle_id and 
                self.apns_private_key
            )
            
            return fcm_configured or apns_configured
        except Exception as e:
            logger.error(f"Push notification configuration validation failed: {str(e)}")
            return False


# Default push notification templates
DEFAULT_PUSH_TEMPLATES = {
    'job_match_notification': {
        'title': 'New Job Match Found!',
        'body': '{{job_title}} at {{company_name}} - {{match_score}}% match',
        'data': {
            'type': 'job_match',
            'job_id': '{{job_id}}',
            'action': 'view_job'
        }
    },
    'assessment_reminder': {
        'title': 'Assessment Reminder',
        'body': 'Complete your {{assessment_type}} assessment by {{deadline}}',
        'data': {
            'type': 'assessment_reminder',
            'assessment_id': '{{assessment_id}}',
            'action': 'take_assessment'
        }
    },
    'interview_scheduled': {
        'title': 'Interview Scheduled',
        'body': 'Interview for {{job_title}} on {{interview_date}}',
        'data': {
            'type': 'interview_scheduled',
            'interview_id': '{{interview_id}}',
            'action': 'join_interview'
        }
    },
    'application_update': {
        'title': 'Application Update',
        'body': 'Your application for {{job_title}} has been {{status}}',
        'data': {
            'type': 'application_update',
            'application_id': '{{application_id}}',
            'action': 'view_application'
        }
    }
}