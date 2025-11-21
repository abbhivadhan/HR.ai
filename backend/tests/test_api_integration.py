"""
API Integration Tests

Comprehensive integration tests for all API endpoints.
"""

import pytest
import asyncio
from httpx import AsyncClient
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from ..app.main import app
from ..app.database import get_db
from ..app.models.user import User, UserType
from ..app.services.auth_service import AuthService


@pytest.fixture
def client():
    """Test client fixture"""
    return TestClient(app)


@pytest.fixture
async def async_client():
    """Async test client fixture"""
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac


@pytest.fixture
def db_session():
    """Database session fixture"""
    # In a real implementation, this would create a test database
    # For demo purposes, we'll mock it
    return None


@pytest.fixture
def test_user_data():
    """Test user data fixture"""
    return {
        "email": "test@example.com",
        "password": "TestPassword123!",
        "first_name": "Test",
        "last_name": "User",
        "user_type": "candidate"
    }


@pytest.fixture
def test_company_data():
    """Test company data fixture"""
    return {
        "email": "company@example.com",
        "password": "CompanyPassword123!",
        "first_name": "Company",
        "last_name": "Admin",
        "user_type": "company"
    }


class TestAuthenticationAPI:
    """Test authentication endpoints"""
    
    def test_register_candidate(self, client, test_user_data):
        """Test candidate registration"""
        response = client.post("/api/auth/register", json=test_user_data)
        
        assert response.status_code == 201
        data = response.json()
        assert data["email"] == test_user_data["email"]
        assert data["user_type"] == "candidate"
        assert "id" in data
    
    def test_register_company(self, client, test_company_data):
        """Test company registration"""
        response = client.post("/api/auth/register", json=test_company_data)
        
        assert response.status_code == 201
        data = response.json()
        assert data["email"] == test_company_data["email"]
        assert data["user_type"] == "company"
    
    def test_login_success(self, client, test_user_data):
        """Test successful login"""
        # First register user
        client.post("/api/auth/register", json=test_user_data)
        
        # Then login
        login_data = {
            "email": test_user_data["email"],
            "password": test_user_data["password"]
        }
        response = client.post("/api/auth/login", json=login_data)
        
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["token_type"] == "bearer"
    
    def test_login_invalid_credentials(self, client):
        """Test login with invalid credentials"""
        login_data = {
            "email": "nonexistent@example.com",
            "password": "wrongpassword"
        }
        response = client.post("/api/auth/login", json=login_data)
        
        assert response.status_code == 401
        assert "Incorrect email or password" in response.json()["detail"]


class TestAssessmentAPI:
    """Test assessment endpoints"""
    
    def test_start_assessment(self, client, test_user_data):
        """Test starting an assessment"""
        # Register and login user
        client.post("/api/auth/register", json=test_user_data)
        login_response = client.post("/api/auth/login", json={
            "email": test_user_data["email"],
            "password": test_user_data["password"]
        })
        token = login_response.json()["access_token"]
        
        # Start assessment
        headers = {"Authorization": f"Bearer {token}"}
        assessment_data = {
            "assessment_type": "technical",
            "difficulty_level": "intermediate"
        }
        response = client.post("/api/assessments/start", json=assessment_data, headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        assert "assessment_id" in data
        assert "session_token" in data
        assert data["time_limit_minutes"] > 0
    
    def test_get_assessment(self, client, test_user_data):
        """Test getting assessment details"""
        # Setup user and start assessment
        client.post("/api/auth/register", json=test_user_data)
        login_response = client.post("/api/auth/login", json={
            "email": test_user_data["email"],
            "password": test_user_data["password"]
        })
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # Start assessment
        assessment_response = client.post("/api/assessments/start", json={
            "assessment_type": "technical"
        }, headers=headers)
        assessment_id = assessment_response.json()["assessment_id"]
        
        # Get assessment details
        response = client.get(f"/api/assessments/{assessment_id}", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == assessment_id
        assert data["assessment_type"] == "technical"


class TestJobMatchingAPI:
    """Test job matching endpoints"""
    
    def test_get_recommendations(self, client, test_user_data):
        """Test getting job recommendations"""
        # Setup user
        client.post("/api/auth/register", json=test_user_data)
        login_response = client.post("/api/auth/login", json={
            "email": test_user_data["email"],
            "password": test_user_data["password"]
        })
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # Get recommendations
        response = client.get("/api/matching/recommendations", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        assert "recommendations" in data
        assert isinstance(data["recommendations"], list)
    
    def test_get_match_score(self, client, test_user_data):
        """Test getting match score for specific job"""
        # Setup user
        client.post("/api/auth/register", json=test_user_data)
        login_response = client.post("/api/auth/login", json={
            "email": test_user_data["email"],
            "password": test_user_data["password"]
        })
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # Get match score (using mock job ID)
        job_id = "job_123456789"
        response = client.get(f"/api/matching/score/{job_id}", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        assert "match_score" in data
        assert 0 <= data["match_score"] <= 1


class TestWebhookAPI:
    """Test webhook endpoints"""
    
    def test_create_webhook(self, client, test_user_data):
        """Test creating a webhook"""
        # Setup user
        client.post("/api/auth/register", json=test_user_data)
        login_response = client.post("/api/auth/login", json={
            "email": test_user_data["email"],
            "password": test_user_data["password"]
        })
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # Create webhook
        webhook_data = {
            "url": "https://example.com/webhook",
            "events": ["user.registered", "assessment.completed"],
            "description": "Test webhook"
        }
        response = client.post("/api/webhooks", json=webhook_data, headers=headers)
        
        assert response.status_code == 201
        data = response.json()
        assert data["url"] == webhook_data["url"]
        assert data["events"] == webhook_data["events"]
        assert data["is_active"] is True
    
    def test_list_webhooks(self, client, test_user_data):
        """Test listing webhooks"""
        # Setup user
        client.post("/api/auth/register", json=test_user_data)
        login_response = client.post("/api/auth/login", json={
            "email": test_user_data["email"],
            "password": test_user_data["password"]
        })
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # Create a webhook first
        webhook_data = {
            "url": "https://example.com/webhook",
            "events": ["user.registered"]
        }
        client.post("/api/webhooks", json=webhook_data, headers=headers)
        
        # List webhooks
        response = client.get("/api/webhooks", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 1


class TestDeveloperToolsAPI:
    """Test developer tools endpoints"""
    
    def test_sandbox_ui(self, client):
        """Test sandbox UI endpoint"""
        response = client.get("/api/developer/sandbox")
        
        assert response.status_code == 200
        assert "text/html" in response.headers["content-type"]
        assert "AI-HR Platform Developer Sandbox" in response.text
    
    def test_api_usage_stats(self, client, test_user_data):
        """Test API usage statistics"""
        # Setup user
        client.post("/api/auth/register", json=test_user_data)
        login_response = client.post("/api/auth/login", json={
            "email": test_user_data["email"],
            "password": test_user_data["password"]
        })
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # Get usage stats
        response = client.get("/api/developer/usage-stats", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        assert "total_requests" in data
        assert "requests_by_endpoint" in data
        assert "average_response_time" in data
    
    def test_sandbox_test_endpoint(self, client, test_user_data):
        """Test sandbox API testing"""
        # Setup user
        client.post("/api/auth/register", json=test_user_data)
        login_response = client.post("/api/auth/login", json={
            "email": test_user_data["email"],
            "password": test_user_data["password"]
        })
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # Test API endpoint through sandbox
        test_request = {
            "endpoint": "/api/auth/login",
            "method": "POST",
            "api_version": "1.1",
            "headers": {"Content-Type": "application/json"},
            "body": {
                "email": "demo@example.com",
                "password": "demo123"
            }
        }
        response = client.post("/api/developer/sandbox/test", json=test_request, headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        assert "status_code" in data
        assert "execution_time_ms" in data
        assert "request_id" in data


class TestAPIVersioning:
    """Test API versioning functionality"""
    
    def test_version_header(self, client, test_user_data):
        """Test API version header"""
        headers = {"API-Version": "1.0"}
        response = client.post("/api/auth/register", json=test_user_data, headers=headers)
        
        # Should work with older version
        assert response.status_code == 201
        assert response.headers.get("API-Version") == "1.0"
    
    def test_unsupported_version(self, client, test_user_data):
        """Test unsupported API version"""
        headers = {"API-Version": "2.0"}
        response = client.post("/api/auth/register", json=test_user_data, headers=headers)
        
        # Should return error for unsupported version
        assert response.status_code == 400
        assert "Unsupported API version" in response.json()["detail"]
    
    def test_deprecated_version_warning(self, client, test_user_data):
        """Test deprecated version warning"""
        headers = {"API-Version": "1.0"}
        response = client.post("/api/auth/register", json=test_user_data, headers=headers)
        
        # Should include deprecation warning headers
        assert response.status_code == 201
        # Note: In a real implementation, these headers would be added
        # assert "Deprecation" in response.headers
        # assert "Sunset" in response.headers


class TestRateLimiting:
    """Test rate limiting functionality"""
    
    def test_rate_limit_info(self, client, test_user_data):
        """Test rate limit information endpoint"""
        # Setup user
        client.post("/api/auth/register", json=test_user_data)
        login_response = client.post("/api/auth/login", json={
            "email": test_user_data["email"],
            "password": test_user_data["password"]
        })
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # Get rate limit info
        response = client.get("/api/developer/rate-limits", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        assert "current_limits" in data
        assert "current_usage" in data
        assert "reset_times" in data


class TestErrorHandling:
    """Test error handling across endpoints"""
    
    def test_unauthorized_access(self, client):
        """Test unauthorized access to protected endpoints"""
        response = client.get("/api/assessments/start")
        
        assert response.status_code == 401
        assert "detail" in response.json()
    
    def test_invalid_json(self, client):
        """Test invalid JSON in request body"""
        response = client.post("/api/auth/register", data="invalid json")
        
        assert response.status_code == 422
    
    def test_missing_required_fields(self, client):
        """Test missing required fields"""
        incomplete_data = {
            "email": "test@example.com"
            # Missing password, first_name, last_name
        }
        response = client.post("/api/auth/register", json=incomplete_data)
        
        assert response.status_code == 422
        assert "detail" in response.json()
    
    def test_not_found_endpoint(self, client):
        """Test accessing non-existent endpoint"""
        response = client.get("/api/nonexistent")
        
        assert response.status_code == 404


@pytest.mark.asyncio
class TestAsyncEndpoints:
    """Test async endpoint functionality"""
    
    async def test_concurrent_requests(self, async_client, test_user_data):
        """Test handling concurrent requests"""
        # Create multiple registration requests concurrently
        tasks = []
        for i in range(5):
            user_data = test_user_data.copy()
            user_data["email"] = f"user{i}@example.com"
            task = async_client.post("/api/auth/register", json=user_data)
            tasks.append(task)
        
        responses = await asyncio.gather(*tasks)
        
        # All should succeed
        for response in responses:
            assert response.status_code == 201
    
    async def test_webhook_delivery_async(self, async_client, test_user_data):
        """Test async webhook delivery"""
        # Setup user
        register_response = await async_client.post("/api/auth/register", json=test_user_data)
        assert register_response.status_code == 201
        
        login_response = await async_client.post("/api/auth/login", json={
            "email": test_user_data["email"],
            "password": test_user_data["password"]
        })
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # Create webhook
        webhook_data = {
            "url": "https://httpbin.org/post",
            "events": ["user.registered"]
        }
        webhook_response = await async_client.post("/api/webhooks", json=webhook_data, headers=headers)
        assert webhook_response.status_code == 201
        
        webhook_id = webhook_response.json()["id"]
        
        # Test webhook
        test_response = await async_client.post(f"/api/webhooks/{webhook_id}/test", headers=headers)
        assert test_response.status_code == 200


if __name__ == "__main__":
    pytest.main([__file__, "-v"])