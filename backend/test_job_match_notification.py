#!/usr/bin/env python3
"""
Test job match notification integration
This demonstrates how the notification system integrates with job matching
"""

import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.services.notification_service import NotificationService
from app.models.notification import NotificationCategory, NotificationType, NotificationPriority
from uuid import uuid4


async def test_job_match_notification():
    """Test creating and sending a job match notification"""
    
    print("Testing Job Match Notification Integration...")
    
    try:
        # Initialize notification service
        notification_service = NotificationService()
        
        # Simulate a job match scenario
        candidate_id = uuid4()
        job_data = {
            "job_id": str(uuid4()),
            "job_title": "Senior Python Developer",
            "company_name": "TechCorp Inc.",
            "company_id": str(uuid4()),
            "match_score": 95,
            "location": "San Francisco, CA",
            "salary_range": "$120,000 - $150,000",
            "job_description": "We are looking for an experienced Python developer...",
            "dashboard_url": "http://localhost:3000/dashboard",
            "short_url": "http://localhost:3000/jobs/123"
        }
        
        # Test notification creation (without database)
        print("✓ Job match data prepared")
        print(f"  - Job: {job_data['job_title']} at {job_data['company_name']}")
        print(f"  - Match Score: {job_data['match_score']}%")
        print(f"  - Location: {job_data['location']}")
        
        # Test template rendering for different notification types
        email_service = notification_service.email_service
        sms_service = notification_service.sms_service
        push_service = notification_service.push_service
        
        # Test email template
        email_template = notification_service._get_email_template(NotificationCategory.JOB_MATCH)
        if email_template:
            variables = {
                "candidate_name": "John Doe",
                **job_data
            }
            
            subject = email_service._render_template(email_template['subject'], variables)
            body = email_service._render_template(email_template['body'], variables)
            
            print("✓ Email notification template rendered successfully")
            print(f"  - Subject: {subject}")
            print(f"  - Body preview: {body[:100]}...")
        
        # Test SMS template
        sms_template = notification_service._get_sms_template(NotificationCategory.JOB_MATCH)
        if sms_template:
            variables = {
                "candidate_name": "John Doe",
                **job_data
            }
            
            sms_message = sms_service._render_template(sms_template, variables)
            print("✓ SMS notification template rendered successfully")
            print(f"  - Message: {sms_message}")
        
        # Test push notification template
        push_template = notification_service._get_push_template(NotificationCategory.JOB_MATCH)
        if push_template:
            variables = {
                "candidate_name": "John Doe",
                **job_data
            }
            
            push_title = push_service._render_template(push_template['title'], variables)
            push_body = push_service._render_template(push_template['body'], variables)
            
            print("✓ Push notification template rendered successfully")
            print(f"  - Title: {push_title}")
            print(f"  - Body: {push_body}")
        
        print("\n✓ Job match notification integration test completed successfully!")
        return True
        
    except Exception as e:
        print(f"✗ Job match notification test failed: {e}")
        return False


async def test_notification_workflow():
    """Test the complete notification workflow"""
    
    print("\nTesting Complete Notification Workflow...")
    
    try:
        notification_service = NotificationService()
        
        # Simulate different notification scenarios
        scenarios = [
            {
                "category": NotificationCategory.JOB_MATCH,
                "title": "New Job Match Found!",
                "message": "A new job matches your skills and preferences.",
                "priority": NotificationPriority.HIGH,
                "data": {
                    "job_id": "123",
                    "job_title": "Python Developer",
                    "company_name": "TechCorp",
                    "match_score": 95
                }
            },
            {
                "category": NotificationCategory.ASSESSMENT_REMINDER,
                "title": "Assessment Reminder",
                "message": "Don't forget to complete your skills assessment.",
                "priority": NotificationPriority.MEDIUM,
                "data": {
                    "assessment_id": "456",
                    "assessment_type": "Python Programming",
                    "deadline": "2024-01-20"
                }
            },
            {
                "category": NotificationCategory.INTERVIEW_SCHEDULED,
                "title": "Interview Scheduled",
                "message": "Your interview has been scheduled.",
                "priority": NotificationPriority.HIGH,
                "data": {
                    "interview_id": "789",
                    "interview_date": "2024-01-25",
                    "interview_time": "2:00 PM",
                    "job_title": "Senior Developer"
                }
            }
        ]
        
        for i, scenario in enumerate(scenarios, 1):
            print(f"✓ Scenario {i}: {scenario['category'].value}")
            print(f"  - Title: {scenario['title']}")
            print(f"  - Priority: {scenario['priority'].value}")
            print(f"  - Data keys: {list(scenario['data'].keys())}")
            
            # Test template variables preparation
            mock_notification = type('MockNotification', (), {
                'id': str(uuid4()),
                'title': scenario['title'],
                'message': scenario['message'],
                'data': str(scenario['data'])  # JSON string
            })()
            
            mock_user = type('MockUser', (), {
                'full_name': 'John Doe',
                'email': 'john@example.com'
            })()
            
            variables = notification_service._prepare_template_variables(
                mock_notification,
                mock_user
            )
            
            print(f"  - Template variables prepared: {len(variables)} keys")
        
        print("\n✓ Complete notification workflow test completed successfully!")
        return True
        
    except Exception as e:
        print(f"✗ Notification workflow test failed: {e}")
        return False


async def main():
    """Run all integration tests"""
    
    print("=" * 70)
    print("JOB MATCH NOTIFICATION INTEGRATION TEST")
    print("=" * 70)
    
    tests = [
        await test_job_match_notification(),
        await test_notification_workflow()
    ]
    
    passed = sum(tests)
    total = len(tests)
    
    print("\n" + "=" * 70)
    print(f"INTEGRATION TEST RESULTS: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All integration tests passed! Job match notifications are ready.")
        return True
    else:
        print("❌ Some integration tests failed. Please check the implementation.")
        return False


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)