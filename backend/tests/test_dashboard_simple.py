import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock

# Mock the database dependency to avoid database issues
def mock_get_db():
    return MagicMock()

# Mock the auth dependency
def mock_get_current_user():
    return MagicMock()

# Import and setup app with mocked dependencies
from app.main import app
from app.database import get_db
from app.auth.dependencies import get_current_user

app.dependency_overrides[get_db] = mock_get_db
app.dependency_overrides[get_current_user] = mock_get_current_user

client = TestClient(app)


class TestDashboardEndpointsSimple:
    """Test dashboard endpoints without database dependencies"""
    
    def test_health_check(self):
        """Test that the app is running"""
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json() == {"status": "healthy"}
    
    def test_root_endpoint(self):
        """Test root endpoint"""
        response = client.get("/")
        assert response.status_code == 200
        assert "AI-HR Platform API is running" in response.json()["message"]
    
    @patch('app.api.dashboard.get_current_user')
    def test_dashboard_endpoints_exist(self, mock_auth):
        """Test that dashboard endpoints are registered"""
        # Mock authentication
        mock_user = MagicMock()
        mock_user.user_type = "candidate"
        mock_auth.return_value = mock_user
        
        # Test that endpoints exist (they should return some response, not 404)
        endpoints = [
            "/api/dashboard/candidate/stats",
            "/api/dashboard/candidate/recommendations", 
            "/api/dashboard/candidate/skill-scores",
            "/api/dashboard/candidate/application-trends",
            "/api/dashboard/company/analytics",
            "/api/dashboard/company/job-postings",
            "/api/dashboard/company/applications",
            "/api/dashboard/admin/metrics",
            "/api/dashboard/notifications"
        ]
        
        for endpoint in endpoints:
            response = client.get(endpoint)
            # Should not be 404 (not found), meaning endpoint exists
            assert response.status_code != 404, f"Endpoint {endpoint} not found"
    
    def test_notification_endpoints_exist(self):
        """Test that notification management endpoints exist"""
        # Test PATCH endpoints
        response = client.patch("/api/dashboard/notifications/test-id/read")
        assert response.status_code != 404
        
        response = client.patch("/api/dashboard/notifications/read-all")
        assert response.status_code != 404
        
        # Test DELETE endpoint
        response = client.delete("/api/dashboard/notifications/test-id")
        assert response.status_code != 404