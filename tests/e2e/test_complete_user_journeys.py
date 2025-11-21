"""
End-to-End Testing for Complete User Journeys
Tests complete user workflows from registration to job matching
"""
import pytest
import asyncio
import aiohttp
import time
from typing import Dict, Any
import json
import os


class TestCandidateJourney:
    """Test complete candidate user journey"""
    
    @pytest.fixture
    def base_url(self):
        """Get base URL for testing"""
        return os.getenv("TEST_BASE_URL", "http://localhost:8000")
    
    @pytest.fixture
    def candidate_data(self):
        """Test candidate data"""
        return {
            "email": f"candidate_{int(time.time())}@example.com",
            "password": "TestPassword123!",
            "first_name": "Test",
            "last_name": "Candidate",
            "user_type": "candidate"
        }
    
    @pytest.mark.asyncio
    async def test_complete_candidate_journey(self, base_url, candidate_data):
        """Test complete candidate journey from registration to job matching"""
        async with aiohttp.ClientSession() as session:
            # Step 1: Register candidate
            async with session.post(f"{base_url}/api/auth/register", json=candidate_data) as response:
                assert response.status == 201
                user_data = await response.json()
                user_id = user_data["id"]
            
            # Step 2: Login
            login_data = {
                "email": candidate_data["email"],
                "password": candidate_data["password"]
            }
            async with session.post(f"{base_url}/api/auth/login", json=login_data) as response:
                assert response.status == 200
                auth_data = await response.json()
                access_token = auth_data["access_token"]
            
            headers = {"Authorization": f"Bearer {access_token}"}
            
            # Step 3: Update profile
            profile_data = {
                "skills": ["Python", "FastAPI", "Machine Learning"],
                "experience_years": 3,
                "preferred_locations": ["Remote", "San Francisco"],
                "salary_expectation": {"min": 80000, "max": 120000}
            }
            async with session.put(f"{base_url}/api/users/profile", json=profile_data, headers=headers) as response:
                assert response.status == 200
            
            # Step 4: Start assessment
            assessment_data = {
                "assessment_type": "technical",
                "difficulty_level": "intermediate"
            }
            async with session.post(f"{base_url}/api/assessments/start", json=assessment_data, headers=headers) as response:
                assert response.status == 200
                assessment_info = await response.json()
                assessment_id = assessment_info["assessment_id"]
            
            # Step 5: Complete assessment
            # Simulate answering questions
            assessment_responses = {
                "responses": [
                    {"question_id": "q1", "answer": "Python is a high-level programming language"},
                    {"question_id": "q2", "answer": "FastAPI is a modern web framework for Python"},
                    {"question_id": "q3", "answer": "Machine learning is a subset of AI"}
                ]
            }
            async with session.post(f"{base_url}/api/assessments/{assessment_id}/submit", 
                                  json=assessment_responses, headers=headers) as response:
                assert response.status == 200
                results = await response.json()
                assert "score" in results
                assert results["score"] > 0
            
            # Step 6: Get job recommendations
            async with session.get(f"{base_url}/api/matching/recommendations", headers=headers) as response:
                assert response.status == 200
                recommendations = await response.json()
                assert "recommendations" in recommendations
                assert isinstance(recommendations["recommendations"], list)
            
            # Step 7: Apply to a job (if recommendations exist)
            if recommendations["recommendations"]:
                job_id = recommendations["recommendations"][0]["job_id"]
                application_data = {
                    "cover_letter": "I am interested in this position and believe my skills align well."
                }
                async with session.post(f"{base_url}/api/jobs/{job_id}/apply", 
                                      json=application_data, headers=headers) as response:
                    assert response.status == 200
            
            # Step 8: Check application status
            async with session.get(f"{base_url}/api/applications/status", headers=headers) as response:
                assert response.status == 200
                applications = await response.json()
                assert isinstance(applications, list)


class TestCompanyJourney:
    """Test complete company user journey"""
    
    @pytest.fixture
    def company_data(self):
        """Test company data"""
        return {
            "email": f"company_{int(time.time())}@example.com",
            "password": "CompanyPassword123!",
            "first_name": "Company",
            "last_name": "Admin",
            "user_type": "company"
        }
    
    @pytest.mark.asyncio
    async def test_complete_company_journey(self, base_url, company_data):
        """Test complete company journey from registration to candidate review"""
        async with aiohttp.ClientSession() as session:
            # Step 1: Register company
            async with session.post(f"{base_url}/api/auth/register", json=company_data) as response:
                assert response.status == 201
                user_data = await response.json()
            
            # Step 2: Login
            login_data = {
                "email": company_data["email"],
                "password": company_data["password"]
            }
            async with session.post(f"{base_url}/api/auth/login", json=login_data) as response:
                assert response.status == 200
                auth_data = await response.json()
                access_token = auth_data["access_token"]
            
            headers = {"Authorization": f"Bearer {access_token}"}
            
            # Step 3: Update company profile
            company_profile = {
                "company_name": "Test Tech Company",
                "industry": "Technology",
                "company_size": "50-200",
                "description": "A leading technology company"
            }
            async with session.put(f"{base_url}/api/users/profile", json=company_profile, headers=headers) as response:
                assert response.status == 200
            
            # Step 4: Post a job
            job_data = {
                "title": "Senior Python Developer",
                "description": "We are looking for a senior Python developer",
                "requirements": ["Python", "FastAPI", "5+ years experience"],
                "skills_required": ["Python", "FastAPI", "PostgreSQL"],
                "experience_level": "senior",
                "salary_range": {"min": 100000, "max": 150000},
                "location": "San Francisco",
                "remote_allowed": True
            }
            async with session.post(f"{base_url}/api/jobs/create", json=job_data, headers=headers) as response:
                assert response.status == 201
                job_info = await response.json()
                job_id = job_info["id"]
            
            # Step 5: Get job applications
            async with session.get(f"{base_url}/api/jobs/{job_id}/applications", headers=headers) as response:
                assert response.status == 200
                applications = await response.json()
                assert isinstance(applications, list)
            
            # Step 6: Get candidate recommendations
            async with session.get(f"{base_url}/api/matching/candidates/{job_id}", headers=headers) as response:
                assert response.status == 200
                candidates = await response.json()
                assert "candidates" in candidates
            
            # Step 7: Access company dashboard
            async with session.get(f"{base_url}/api/dashboard/company", headers=headers) as response:
                assert response.status == 200
                dashboard_data = await response.json()
                assert "active_jobs" in dashboard_data
                assert "total_applications" in dashboard_data


class TestInterviewJourney:
    """Test AI interview journey"""
    
    @pytest.mark.asyncio
    async def test_ai_interview_flow(self, base_url, candidate_data):
        """Test complete AI interview flow"""
        async with aiohttp.ClientSession() as session:
            # Setup: Register and login candidate
            await session.post(f"{base_url}/api/auth/register", json=candidate_data)
            login_response = await session.post(f"{base_url}/api/auth/login", json={
                "email": candidate_data["email"],
                "password": candidate_data["password"]
            })
            auth_data = await login_response.json()
            headers = {"Authorization": f"Bearer {auth_data['access_token']}"}
            
            # Step 1: Schedule interview
            interview_data = {
                "interview_type": "technical",
                "scheduled_time": "2024-10-28T10:00:00Z",
                "duration_minutes": 45
            }
            async with session.post(f"{base_url}/api/interviews/schedule", 
                                  json=interview_data, headers=headers) as response:
                assert response.status == 201
                interview_info = await response.json()
                interview_id = interview_info["interview_id"]
            
            # Step 2: Join interview
            async with session.get(f"{base_url}/api/interviews/{interview_id}/join", headers=headers) as response:
                assert response.status == 200
                join_info = await response.json()
                assert "session_token" in join_info
                assert "webrtc_config" in join_info
            
            # Step 3: Simulate interview completion
            completion_data = {
                "status": "completed",
                "duration_minutes": 42,
                "responses": [
                    {"question": "Tell me about yourself", "response": "I am a Python developer..."},
                    {"question": "Explain REST APIs", "response": "REST is an architectural style..."}
                ]
            }
            async with session.post(f"{base_url}/api/interviews/{interview_id}/complete", 
                                  json=completion_data, headers=headers) as response:
                assert response.status == 200
            
            # Step 4: Get interview results
            async with session.get(f"{base_url}/api/interviews/{interview_id}/results", headers=headers) as response:
                assert response.status == 200
                results = await response.json()
                assert "overall_score" in results
                assert "analysis" in results


class TestSystemIntegration:
    """Test system integration and cross-service functionality"""
    
    @pytest.mark.asyncio
    async def test_notification_system_integration(self, base_url):
        """Test notification system integration"""
        # This would test that notifications are properly sent
        # when various events occur (job matches, interview invites, etc.)
        pass
    
    @pytest.mark.asyncio
    async def test_analytics_integration(self, base_url):
        """Test analytics system integration"""
        # This would test that analytics data is properly collected
        # and aggregated across user actions
        pass
    
    @pytest.mark.asyncio
    async def test_webhook_integration(self, base_url):
        """Test webhook system integration"""
        # This would test that webhooks are properly triggered
        # for various events
        pass


class TestErrorRecovery:
    """Test error recovery and resilience"""
    
    @pytest.mark.asyncio
    async def test_database_connection_recovery(self, base_url):
        """Test system recovery from database connection issues"""
        # This would test graceful handling of database disconnections
        pass
    
    @pytest.mark.asyncio
    async def test_ai_service_fallback(self, base_url):
        """Test fallback behavior when AI services are unavailable"""
        # This would test that the system gracefully handles AI service outages
        pass
    
    @pytest.mark.asyncio
    async def test_rate_limit_handling(self, base_url):
        """Test proper handling of rate limits"""
        async with aiohttp.ClientSession() as session:
            # Make rapid requests to trigger rate limiting
            responses = []
            for _ in range(20):
                async with session.get(f"{base_url}/api/auth/health") as response:
                    responses.append(response.status)
            
            # Should handle rate limiting gracefully
            assert any(status == 429 for status in responses[-5:])  # Last few should be rate limited


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--asyncio-mode=auto"])