import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from typing import List, Optional, Dict, Any
import logging
from jinja2 import Template
import asyncio
from concurrent.futures import ThreadPoolExecutor

from ..config import settings

logger = logging.getLogger(__name__)


class EmailService:
    def __init__(self):
        self.smtp_server = settings.smtp_server
        self.smtp_port = settings.smtp_port
        self.smtp_username = settings.smtp_username
        self.smtp_password = settings.smtp_password
        self.from_email = settings.from_email
        self.from_name = settings.from_name
        self.use_tls = settings.smtp_use_tls
        self.executor = ThreadPoolExecutor(max_workers=5)

    def _create_smtp_connection(self):
        """Create and return SMTP connection"""
        try:
            if self.use_tls:
                context = ssl.create_default_context()
                server = smtplib.SMTP(self.smtp_server, self.smtp_port)
                server.starttls(context=context)
            else:
                server = smtplib.SMTP_SSL(self.smtp_server, self.smtp_port)
            
            if self.smtp_username and self.smtp_password:
                server.login(self.smtp_username, self.smtp_password)
            
            return server
        except Exception as e:
            logger.error(f"Failed to create SMTP connection: {str(e)}")
            raise

    def _render_template(self, template_str: str, variables: Dict[str, Any]) -> str:
        """Render email template with variables"""
        try:
            template = Template(template_str)
            return template.render(**variables)
        except Exception as e:
            logger.error(f"Failed to render email template: {str(e)}")
            raise

    def _send_email_sync(
        self,
        to_email: str,
        subject: str,
        body: str,
        html_body: Optional[str] = None,
        attachments: Optional[List[Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        """Send email synchronously"""
        try:
            # Create message
            msg = MIMEMultipart('alternative')
            msg['From'] = f"{self.from_name} <{self.from_email}>"
            msg['To'] = to_email
            msg['Subject'] = subject

            # Add text part
            text_part = MIMEText(body, 'plain', 'utf-8')
            msg.attach(text_part)

            # Add HTML part if provided
            if html_body:
                html_part = MIMEText(html_body, 'html', 'utf-8')
                msg.attach(html_part)

            # Add attachments if provided
            if attachments:
                for attachment in attachments:
                    part = MIMEBase('application', 'octet-stream')
                    part.set_payload(attachment['content'])
                    encoders.encode_base64(part)
                    part.add_header(
                        'Content-Disposition',
                        f'attachment; filename= {attachment["filename"]}'
                    )
                    msg.attach(part)

            # Send email
            with self._create_smtp_connection() as server:
                server.send_message(msg)

            logger.info(f"Email sent successfully to {to_email}")
            return {
                'success': True,
                'message': 'Email sent successfully',
                'recipient': to_email
            }

        except Exception as e:
            error_msg = f"Failed to send email to {to_email}: {str(e)}"
            logger.error(error_msg)
            return {
                'success': False,
                'error': error_msg,
                'recipient': to_email
            }

    async def send_email(
        self,
        to_email: str,
        subject: str,
        body: str,
        html_body: Optional[str] = None,
        attachments: Optional[List[Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        """Send email asynchronously"""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            self.executor,
            self._send_email_sync,
            to_email,
            subject,
            body,
            html_body,
            attachments
        )

    async def send_templated_email(
        self,
        to_email: str,
        subject_template: str,
        body_template: str,
        variables: Dict[str, Any],
        html_template: Optional[str] = None
    ) -> Dict[str, Any]:
        """Send email using templates"""
        try:
            # Render templates
            subject = self._render_template(subject_template, variables)
            body = self._render_template(body_template, variables)
            html_body = None
            
            if html_template:
                html_body = self._render_template(html_template, variables)

            return await self.send_email(to_email, subject, body, html_body)

        except Exception as e:
            error_msg = f"Failed to send templated email to {to_email}: {str(e)}"
            logger.error(error_msg)
            return {
                'success': False,
                'error': error_msg,
                'recipient': to_email
            }

    async def send_bulk_emails(
        self,
        recipients: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Send bulk emails asynchronously"""
        tasks = []
        
        for recipient in recipients:
            task = self.send_email(
                to_email=recipient['email'],
                subject=recipient['subject'],
                body=recipient['body'],
                html_body=recipient.get('html_body'),
                attachments=recipient.get('attachments')
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
                    'recipient': recipients[i]['email']
                })
            else:
                processed_results.append(result)

        return processed_results

    def validate_email_config(self) -> bool:
        """Validate email configuration"""
        try:
            with self._create_smtp_connection() as server:
                server.noop()
            return True
        except Exception as e:
            logger.error(f"Email configuration validation failed: {str(e)}")
            return False


# Default email templates
DEFAULT_EMAIL_TEMPLATES = {
    'job_match_notification': {
        'subject': 'New Job Match Found - {{job_title}} at {{company_name}}',
        'body': '''
Hello {{candidate_name}},

We found a great job opportunity that matches your skills and preferences!

Job Title: {{job_title}}
Company: {{company_name}}
Location: {{job_location}}
Match Score: {{match_score}}%

{{job_description}}

To view the full job details and apply, please visit your dashboard:
{{dashboard_url}}

Best regards,
The AI-HR Platform Team
        ''',
        'html': '''
<html>
<body>
    <h2>New Job Match Found!</h2>
    <p>Hello {{candidate_name}},</p>
    
    <p>We found a great job opportunity that matches your skills and preferences!</p>
    
    <div style="background-color: #f5f5f5; padding: 20px; margin: 20px 0; border-radius: 5px;">
        <h3>{{job_title}}</h3>
        <p><strong>Company:</strong> {{company_name}}</p>
        <p><strong>Location:</strong> {{job_location}}</p>
        <p><strong>Match Score:</strong> <span style="color: #28a745; font-weight: bold;">{{match_score}}%</span></p>
    </div>
    
    <p>{{job_description}}</p>
    
    <p><a href="{{dashboard_url}}" style="background-color: #007bff; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">View Job Details</a></p>
    
    <p>Best regards,<br>The AI-HR Platform Team</p>
</body>
</html>
        '''
    },
    'assessment_reminder': {
        'subject': 'Reminder: Complete Your Skills Assessment',
        'body': '''
Hello {{candidate_name}},

This is a friendly reminder to complete your skills assessment for the {{assessment_type}} position.

Assessment Details:
- Type: {{assessment_type}}
- Duration: {{duration}} minutes
- Deadline: {{deadline}}

Complete your assessment here: {{assessment_url}}

Best regards,
The AI-HR Platform Team
        ''',
        'html': '''
<html>
<body>
    <h2>Assessment Reminder</h2>
    <p>Hello {{candidate_name}},</p>
    
    <p>This is a friendly reminder to complete your skills assessment.</p>
    
    <div style="background-color: #fff3cd; padding: 20px; margin: 20px 0; border-radius: 5px; border-left: 4px solid #ffc107;">
        <h3>Assessment Details</h3>
        <p><strong>Type:</strong> {{assessment_type}}</p>
        <p><strong>Duration:</strong> {{duration}} minutes</p>
        <p><strong>Deadline:</strong> {{deadline}}</p>
    </div>
    
    <p><a href="{{assessment_url}}" style="background-color: #ffc107; color: #212529; padding: 10px 20px; text-decoration: none; border-radius: 5px;">Complete Assessment</a></p>
    
    <p>Best regards,<br>The AI-HR Platform Team</p>
</body>
</html>
        '''
    }
}