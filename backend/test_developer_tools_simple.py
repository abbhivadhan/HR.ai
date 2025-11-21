"""
Simple test for developer tools API
"""

from fastapi.testclient import TestClient
from app.api.developer_tools import router
from fastapi import FastAPI

# Create a simple test app
app = FastAPI()
app.include_router(router)

def test_sandbox_ui():
    """Test sandbox UI endpoint"""
    with TestClient(app=app) as client:
        response = client.get("/api/developer/sandbox")
        assert response.status_code == 200
        assert "text/html" in response.headers["content-type"]
        assert "AI-HR Platform Developer Sandbox" in response.text
        print("✓ Sandbox UI test passed")

def test_api_examples():
    """Test API examples endpoint"""
    with TestClient(app=app) as client:
        response = client.get("/api/developer/api-examples")
        assert response.status_code == 200
        data = response.json()
        assert "authentication" in data
        assert "assessments" in data
        print("✓ API examples test passed")

def test_health_check():
    """Test developer tools health check"""
    with TestClient(app=app) as client:
        response = client.get("/api/developer/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "services" in data
        print("✓ Health check test passed")

if __name__ == "__main__":
    test_sandbox_ui()
    test_api_examples()
    test_health_check()
    print("All developer tools tests passed!")