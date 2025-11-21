import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from datetime import datetime, timedelta

from app.database import Base, get_db
from app.models.user import User, UserType
from app.models.profile import CandidateProfile, CompanyProfile
from app.models.job import JobPosting, JobApplication, JobStatus, ApplicationStatus
from app.models.assessment import Assessment, AssessmentStatus

# Test database setup
SQLALCHEMY_DATABASE_URL = "sqlite:///./test_dashboard.db"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

# Import app after setting up database to avoid circular imports
from app.main import app
app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)


class TestDashboardEndpoints:
    """Test dashboard endpoints basic functionality"""
    
    def test_candidate_stats_unauthorized(self):
        """Test getting candidate stats without authentication"""
        response = client.get("/api/dashboard/candidate/stats")
        assert response.status_code == 401
    
    def test_company_analytics_unauthorized(self):
        """Test getting company analytics without authentication"""
        response = client.get("/api/dashboard/company/analytics")
        assert response.status_code == 401
    
    def test_admin_metrics_unauthorized(self):
        """Test getting admin metrics without authentication"""
        response = client.get("/api/dashboard/admin/metrics")
        assert response.status_code == 401
    
    def test_notifications_unauthorized(self):
        """Test getting notifications without authentication"""
        response = client.get("/api/dashboard/notifications")
        assert response.status_code == 401
    
    def test_mark_notification_as_read_unauthorized(self):
        """Test marking notification as read without authentication"""
        response = client.patch("/api/dashboard/notifications/test-id/read")
        assert response.status_code == 401
    
    def test_mark_all_notifications_as_read_unauthorized(self):
        """Test marking all notifications as read without authentication"""
        response = client.patch("/api/dashboard/notifications/read-all")
        assert response.status_code == 401
    
    def test_dismiss_notification_unauthorized(self):
        """Test dismissing notification without authentication"""
        response = client.delete("/api/dashboard/notifications/test-id")
        assert response.status_code == 401
    
    def test_candidate_recommendations_unauthorized(self):
        """Test getting candidate recommendations without authentication"""
        response = client.get("/api/dashboard/candidate/recommendations")
        assert response.status_code == 401
    
    def test_candidate_skill_scores_unauthorized(self):
        """Test getting candidate skill scores without authentication"""
        response = client.get("/api/dashboard/candidate/skill-scores")
        assert response.status_code == 401
    
    def test_candidate_application_trends_unauthorized(self):
        """Test getting candidate application trends without authentication"""
        response = client.get("/api/dashboard/candidate/application-trends")
        assert response.status_code == 401
    
    def test_company_job_postings_unauthorized(self):
        """Test getting company job postings without authentication"""
        response = client.get("/api/dashboard/company/job-postings")
        assert response.status_code == 401
    
    def test_company_applications_unauthorized(self):
        """Test getting company applications without authentication"""
        response = client.get("/api/dashboard/company/applications")
        assert response.status_code == 401