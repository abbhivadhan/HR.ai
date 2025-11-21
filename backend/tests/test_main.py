import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_root_endpoint():
    """Test the root endpoint returns correct message."""
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "AI-HR Platform API is running"}

def test_health_check():
    """Test the health check endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}