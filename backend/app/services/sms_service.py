import logging
from typing import Dict, Any, List, Optional
import asyncio
from concurrent.futures import ThreadPoolExecutor
import httpx
from jinja2 import Template

from ..config import settings

logger = logging.getLogger(__name__)


class SMSService:
    def __init__(self):
        self.provider = settings.sms_provider  # 'twilio', 'aws_sns', 'custom'
        self.api_key = settings.sms_api_key
        self.api_secret = settings.sms_api_secret
        self.from_number = settings.sms_from_number
        self.executor = ThreadPoolExecutor(max_workers=3)

    def _render_template(self, template_str: str, variables: Dict[str, Any]) -> str:
        """Render SMS template with variables"""
        try:
            template = Template(template_str)
            return template.render(**variables)
        except Exception as e:
            logger.error(f"Failed to render SMS template: {str(e)}")
            raise

    async def _send_twilio_sms(self, to_number: str, message: str) -> Dict[str, Any]:
        """Send SMS using Twilio API"""
        try:
            import base64
            
            # Twilio API endpoint
            url = f"https://api.twilio.com/2010-04-01/Accounts/{self.api_key}/Messages.json"
            
            # Prepare authentication
            auth_string = f"{self.api_key}:{self.api_secret}"
            auth_bytes = auth_string.encode('ascii')
            auth_b64 = base64.b64encode(auth_bytes).decode('ascii')
            
            headers = {
                'Authorization': f'Basic {auth_b64}',
                'Content-Type': 'application/x-www-form-urlencoded'
            }
            
            data = {
                'From': self.from_number,
                'To': to_number,
                'Body': message
            }
            
            async with httpx.AsyncClient() as client:
                response = await client.post(url, headers=headers, data=data)
                
                if response.status_code == 201:
                    result = response.json()
                    logger.info(f"SMS sent successfully to {to_number} via Twilio")
                    return {
                        'success': True,
                        'message': 'SMS sent successfully',
                        'recipient': to_number,
                        'provider_response': result
                    }
                else:
                    error_msg = f"Twilio API error: {response.status_code} - {response.text}"
                    logger.error(error_msg)
                    return {
                        'success': False,
                        'error': error_msg,
                        'recipient': to_number
                    }
                    
        except Exception as e:
            error_msg = f"Failed to send SMS via Twilio to {to_number}: {str(e)}"
            logger.error(error_msg)
            return {
                'success': False,
                'error': error_msg,
                'recipient': to_number
            }

    async def _send_aws_sns_sms(self, to_number: str, message: str) -> Dict[str, Any]:
        """Send SMS using AWS SNS"""
        try:
            import boto3
            
            sns_client = boto3.client(
                'sns',
                aws_access_key_id=self.api_key,
                aws_secret_access_key=self.api_secret,
                region_name=settings.aws_region or 'us-east-1'
            )
            
            response = sns_client.publish(
                PhoneNumber=to_number,
                Message=message,
                MessageAttributes={
                    'AWS.SNS.SMS.SenderID': {
                        'DataType': 'String',
                        'StringValue': settings.sms_sender_id or 'AI-HR'
                    }
                }
            )
            
            logger.info(f"SMS sent successfully to {to_number} via AWS SNS")
            return {
                'success': True,
                'message': 'SMS sent successfully',
                'recipient': to_number,
                'provider_response': response
            }
            
        except Exception as e:
            error_msg = f"Failed to send SMS via AWS SNS to {to_number}: {str(e)}"
            logger.error(error_msg)
            return {
                'success': False,
                'error': error_msg,
                'recipient': to_number
            }

    async def _send_custom_sms(self, to_number: str, message: str) -> Dict[str, Any]:
        """Send SMS using custom API"""
        try:
            # This is a placeholder for custom SMS provider integration
            # Replace with your actual SMS provider API calls
            
            headers = {
                'Authorization': f'Bearer {self.api_key}',
                'Content-Type': 'application/json'
            }
            
            data = {
                'to': to_number,
                'from': self.from_number,
                'message': message
            }
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    settings.sms_api_url,
                    headers=headers,
                    json=data
                )
                
                if response.status_code == 200:
                    result = response.json()
                    logger.info(f"SMS sent successfully to {to_number} via custom provider")
                    return {
                        'success': True,
                        'message': 'SMS sent successfully',
                        'recipient': to_number,
                        'provider_response': result
                    }
                else:
                    error_msg = f"Custom SMS API error: {response.status_code} - {response.text}"
                    logger.error(error_msg)
                    return {
                        'success': False,
                        'error': error_msg,
                        'recipient': to_number
                    }
                    
        except Exception as e:
            error_msg = f"Failed to send SMS via custom provider to {to_number}: {str(e)}"
            logger.error(error_msg)
            return {
                'success': False,
                'error': error_msg,
                'recipient': to_number
            }

    async def send_sms(self, to_number: str, message: str) -> Dict[str, Any]:
        """Send SMS using configured provider"""
        # Validate phone number format
        if not to_number.startswith('+'):
            to_number = f'+{to_number}'
        
        # Truncate message if too long (SMS limit is typically 160 characters)
        if len(message) > 160:
            message = message[:157] + '...'
        
        if self.provider == 'twilio':
            return await self._send_twilio_sms(to_number, message)
        elif self.provider == 'aws_sns':
            return await self._send_aws_sns_sms(to_number, message)
        elif self.provider == 'custom':
            return await self._send_custom_sms(to_number, message)
        else:
            error_msg = f"Unsupported SMS provider: {self.provider}"
            logger.error(error_msg)
            return {
                'success': False,
                'error': error_msg,
                'recipient': to_number
            }

    async def send_templated_sms(
        self,
        to_number: str,
        template: str,
        variables: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Send SMS using template"""
        try:
            message = self._render_template(template, variables)
            return await self.send_sms(to_number, message)
        except Exception as e:
            error_msg = f"Failed to send templated SMS to {to_number}: {str(e)}"
            logger.error(error_msg)
            return {
                'success': False,
                'error': error_msg,
                'recipient': to_number
            }

    async def send_bulk_sms(
        self,
        recipients: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Send bulk SMS messages"""
        tasks = []
        
        for recipient in recipients:
            task = self.send_sms(
                to_number=recipient['phone'],
                message=recipient['message']
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
                    'recipient': recipients[i]['phone']
                })
            else:
                processed_results.append(result)

        return processed_results

    def validate_sms_config(self) -> bool:
        """Validate SMS configuration"""
        try:
            if not self.provider or not self.api_key:
                return False
            
            if self.provider in ['twilio', 'custom'] and not self.api_secret:
                return False
                
            if not self.from_number:
                return False
                
            return True
        except Exception as e:
            logger.error(f"SMS configuration validation failed: {str(e)}")
            return False


# Default SMS templates
DEFAULT_SMS_TEMPLATES = {
    'job_match_notification': 'New job match: {{job_title}} at {{company_name}}. {{match_score}}% match. View details: {{short_url}}',
    'assessment_reminder': 'Reminder: Complete your {{assessment_type}} assessment by {{deadline}}. Link: {{short_url}}',
    'interview_scheduled': 'Interview scheduled for {{interview_date}} at {{interview_time}}. Join: {{meeting_url}}',
    'application_update': 'Your application for {{job_title}} at {{company_name}} has been {{status}}. Check dashboard for details.',
    'security_alert': 'Security alert: {{alert_message}}. If this wasn\'t you, secure your account immediately.'
}