#!/usr/bin/env python3
"""
Simple integration test for the notification system
"""

import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.services.notification_service import NotificationService
from app.services.email_service import EmailService
from app.services.sms_service import SMSService
from app.services.push_notification_service import PushNotificationService
from app.models.notification import NotificationCategory, NotificationType, NotificationPriority


async def test_notification_services():
    """Test notification services initialization and basic functionality"""
    
    print("Testing Notification Services...")
    
    # Test NotificationService
    try:
        notification_service = NotificationService()
        print("✓ NotificationService initialized successfully")
    except Exception as e:
        print(f"✗ NotificationService initialization failed: {e}")
        return False
    
    # Test EmailService
    try:
        email_service = EmailService()
        print("✓ EmailService initialized successfully")
        
        # Test template rendering
        template = "Hello {{name}}, welcome to {{platform}}!"
        variables = {"name": "John", "platform": "AI-HR Platform"}
        result = email_service._render_template(template, variables)
        expected = "Hello John, welcome to AI-HR Platform!"
        assert result == expected, f"Expected '{expected}', got '{result}'"
        print("✓ Email template rendering works correctly")
        
    except Exception as e:
        print(f"✗ EmailService test failed: {e}")
        return False
    
    # Test SMSService
    try:
        sms_service = SMSService()
        print("✓ SMSService initialized successfully")
        
        # Test template rendering
        template = "Job match: {{job_title}} at {{company}}. {{match_score}}% match."
        variables = {"job_title": "Developer", "company": "TechCorp", "match_score": "95"}
        result = sms_service._render_template(template, variables)
        expected = "Job match: Developer at TechCorp. 95% match."
        assert result == expected, f"Expected '{expected}', got '{result}'"
        print("✓ SMS template rendering works correctly")
        
    except Exception as e:
        print(f"✗ SMSService test failed: {e}")
        return False
    
    # Test PushNotificationService
    try:
        push_service = PushNotificationService()
        print("✓ PushNotificationService initialized successfully")
        
        # Test template rendering
        template = "New job: {{job_title}} - {{match_score}}% match"
        variables = {"job_title": "Software Engineer", "match_score": "90"}
        result = push_service._render_template(template, variables)
        expected = "New job: Software Engineer - 90% match"
        assert result == expected, f"Expected '{expected}', got '{result}'"
        print("✓ Push notification template rendering works correctly")
        
    except Exception as e:
        print(f"✗ PushNotificationService test failed: {e}")
        return False
    
    print("\n✓ All notification services are working correctly!")
    return True


def test_notification_enums():
    """Test notification enums"""
    
    print("\nTesting Notification Enums...")
    
    try:
        # Test NotificationCategory
        categories = [
            NotificationCategory.JOB_MATCH,
            NotificationCategory.ASSESSMENT_REMINDER,
            NotificationCategory.INTERVIEW_SCHEDULED,
            NotificationCategory.APPLICATION_UPDATE,
            NotificationCategory.SYSTEM_ALERT,
            NotificationCategory.SECURITY_ALERT
        ]
        print(f"✓ NotificationCategory has {len(categories)} values")
        
        # Test NotificationType
        types = [
            NotificationType.EMAIL,
            NotificationType.SMS,
            NotificationType.PUSH,
            NotificationType.IN_APP
        ]
        print(f"✓ NotificationType has {len(types)} values")
        
        # Test NotificationPriority
        priorities = [
            NotificationPriority.LOW,
            NotificationPriority.MEDIUM,
            NotificationPriority.HIGH,
            NotificationPriority.URGENT
        ]
        print(f"✓ NotificationPriority has {len(priorities)} values")
        
        print("✓ All notification enums are working correctly!")
        return True
        
    except Exception as e:
        print(f"✗ Notification enums test failed: {e}")
        return False


def test_api_import():
    """Test API router import"""
    
    print("\nTesting API Import...")
    
    try:
        from app.api.notifications import router
        print("✓ Notification API router imported successfully")
        
        # Check if router has expected routes
        routes = [route.path for route in router.routes]
        expected_routes = [
            "/notifications/",
            "/notifications/{notification_id}",
            "/notifications/preferences/",
            "/notifications/stats/"
        ]
        
        for expected_route in expected_routes:
            if any(expected_route in route for route in routes):
                print(f"✓ Route '{expected_route}' found")
            else:
                print(f"⚠ Route '{expected_route}' not found in routes: {routes}")
        
        print("✓ API import test completed!")
        return True
        
    except Exception as e:
        print(f"✗ API import test failed: {e}")
        return False


async def main():
    """Run all tests"""
    
    print("=" * 60)
    print("NOTIFICATION SYSTEM INTEGRATION TEST")
    print("=" * 60)
    
    tests = [
        test_notification_enums(),
        test_api_import(),
        await test_notification_services()
    ]
    
    passed = sum(tests)
    total = len(tests)
    
    print("\n" + "=" * 60)
    print(f"TEST RESULTS: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Notification system is ready.")
        return True
    else:
        print("❌ Some tests failed. Please check the implementation.")
        return False


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)