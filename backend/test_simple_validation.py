"""
Simple validation test for API documentation components
"""

def test_imports():
    """Test that all components can be imported"""
    try:
        from app.api_docs import setup_api_docs, custom_openapi
        print("✓ API docs module imported successfully")
        
        from app.versioning import version_manager, APIVersion
        print("✓ Versioning module imported successfully")
        
        from app.services.webhook_service import WebhookService
        print("✓ Webhook service imported successfully")
        
        from app.api.developer_tools import router
        print("✓ Developer tools router imported successfully")
        
        from app.api.webhooks import router as webhook_router
        print("✓ Webhook router imported successfully")
        
        return True
    except Exception as e:
        print(f"✗ Import failed: {e}")
        return False

def test_version_manager():
    """Test version manager functionality"""
    try:
        from app.versioning import version_manager, APIVersion
        
        # Test current version
        assert version_manager.current_version == APIVersion.V1_1
        print("✓ Version manager current version correct")
        
        # Test supported versions
        assert APIVersion.V1_0 in version_manager.supported_versions
        assert APIVersion.V1_1 in version_manager.supported_versions
        print("✓ Version manager supported versions correct")
        
        return True
    except Exception as e:
        print(f"✗ Version manager test failed: {e}")
        return False

def test_webhook_service():
    """Test webhook service initialization"""
    try:
        from app.services.webhook_service import WebhookService, WebhookDeliveryService
        
        # Test service can be initialized (with None db for testing)
        service = WebhookService(None)
        delivery_service = WebhookDeliveryService(None)
        
        print("✓ Webhook services initialized successfully")
        return True
    except Exception as e:
        print(f"✗ Webhook service test failed: {e}")
        return False

if __name__ == "__main__":
    print("Running API documentation validation tests...")
    
    all_passed = True
    all_passed &= test_imports()
    all_passed &= test_version_manager()
    all_passed &= test_webhook_service()
    
    if all_passed:
        print("\n🎉 All validation tests passed!")
    else:
        print("\n❌ Some tests failed")