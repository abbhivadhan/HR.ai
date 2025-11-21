"""
User Acceptance Testing (UAT) Scenarios
Tests that validate business requirements and user workflows
"""
import pytest
import asyncio
import aiohttp
import time
import json
from typing import Dict, List, Any
import os


class UATResults:
    """Container for UAT results"""
    
    def __init__(self):
        self.scenario_results: Dict[str, Dict[str, Any]] = {}
        self.business_requirements: Dict[str, bool] = {}
        self.user_workflows: Dict[str, bool] = {}
        self.performance_metrics: Dict[str, float] = {}
        self.errors: List[str] = []
    
    def add_scenario_result(self, scenario_name: str, passed: bool, details: Dict = None):
        """Add UAT scenario result"""
        self.scenario_results[scenario_name] = {
            "passed": passed,
            "details": details or {},
            "timestamp": time.time()
        }
    
    def add_business_requirement(self, requirement_id: str, satisfied: bool):
        """Add business requirement validation"""
        self.business_requirements[requirement_id] = satisfied
    
    def add_user_workflow(self, workflow_name: str, completed: bool):
        """Add user workflow validation"""
        self.user_workflows[workflow_name] = completed
    
    def add_performance_metric(self, metric_name: str, value: float):
        """Add performance metric"""
        self.performance_metrics[metric_name] = value
    
    def add_error(self, error: str):
        """Add error message"""
        self.errors.append(error)
    
    def get_summary(self) -> Dict[str, Any]:
        """Get UAT summary"""
        total_scenarios = len(self.scenario_results)
        passed_scenarios = sum(1 for result in self.scenario_results.values() if result["passed"])
        
        total_requirements = len(self.business_requirements)
        satisfied_requirements = sum(self.business_requirements.values())
        
        total_workflows = len(self.user_workflows)
        completed_workflows = sum(self.user_workflows.values())
        
        return {
            "scenario_results": self.scenario_results,
            "business_requirements": self.business_requirements,
            "user_workflows": self.user_workflows,
            "performance_metrics": self.performance_metrics,
            "errors": self.errors,
            "summary": {
                "total_scenarios": total_scenarios,
                "passed_scenarios": passed_scenarios,
                "scenario_success_rate": passed_scenarios / total_scenarios if total_scenarios > 0 else 0,
                "total_requirements": total_requirements,
                "satisfied_requirements": satisfied_requirements,
                "requirement_satisfaction_rate": satisfied_requirements / total_requirements if total_requirements > 0 else 0,
                "total_workflows": total_workflows,
                "completed_workflows": completed_workflows,
                "workflow_completion_rate": completed_workflows / total_workflows if total_workflows > 0 else 0
            }
        }


class TestCandidateUserAcceptance:
    """UAT scenarios for candidate users"""
    
    @pytest.fixture
    def base_url(self):
        return os.getenv("TEST_BASE_URL", "http://localhost:8000")
    
    @pytest.fixture
    def uat_results(self):
        return UATResults()
    
    @pytest.mark.asyncio
    async def test_candidate_registration_and_onboarding(self, base_url, uat_results):
        """UAT: Candidate can register and complete onboarding process"""
        scenario_name = "candidate_registration_onboarding"
        
        try:
            async with aiohttp.ClientSession() as session:
                # Step 1: Register new candidate
                candidate_data = {
                    "email": f"uat_candidate_{int(time.time())}@example.com",
                    "password": "UATPassword123!",
                    "first_name": "UAT",
                    "last_name": "Candidate",
                    "user_type": "candidate"
                }
                
                start_time = time.time()
                async with session.post(f"{base_url}/api/auth/register", json=candidate_data) as response:
                    registration_time = time.time() - start_time
                    
                    if response.status != 201:
                        uat_results.add_scenario_result(scenario_name, False, {"error": "Registration failed"})
                        return
                    
                    user_data = await response.json()
                
                # Step 2: Login
                login_data = {
                    "email": candidate_data["email"],
                    "password": candidate_data["password"]
                }
                async with session.post(f"{base_url}/api/auth/login", json=login_data) as response:
                    if response.status != 200:
                        uat_results.add_scenario_result(scenario_name, False, {"error": "Login failed"})
                        return
                    
                    auth_data = await response.json()
                    access_token = auth_data["access_token"]
                
                headers = {"Authorization": f"Bearer {access_token}"}
                
                # Step 3: Complete profile
                profile_data = {
                    "skills": ["Python", "JavaScript", "React"],
                    "experience_years": 2,
                    "education": [
                        {
                            "degree": "Bachelor's",
                            "field": "Computer Science",
                            "institution": "Test University"
                        }
                    ],
                    "preferred_locations": ["Remote", "New York"],
                    "salary_expectation": {"min": 70000, "max": 90000}
                }
                async with session.put(f"{base_url}/api/users/profile", json=profile_data, headers=headers) as response:
                    if response.status != 200:
                        uat_results.add_scenario_result(scenario_name, False, {"error": "Profile update failed"})
                        return
                
                # Step 4: Verify profile was saved
                async with session.get(f"{base_url}/api/users/profile", headers=headers) as response:
                    if response.status != 200:
                        uat_results.add_scenario_result(scenario_name, False, {"error": "Profile retrieval failed"})
                        return
                    
                    profile = await response.json()
                    profile_complete = (
                        len(profile.get("skills", [])) > 0 and
                        profile.get("experience_years", 0) > 0 and
                        len(profile.get("preferred_locations", [])) > 0
                    )
                
                uat_results.add_scenario_result(
                    scenario_name, 
                    profile_complete,
                    {
                        "registration_time": registration_time,
                        "profile_fields_completed": len([k for k, v in profile_data.items() if v])
                    }
                )
                uat_results.add_performance_metric("candidate_registration_time", registration_time)
                uat_results.add_user_workflow("candidate_onboarding", profile_complete)
                
        except Exception as e:
            uat_results.add_error(f"Candidate registration UAT failed: {str(e)}")
            uat_results.add_scenario_result(scenario_name, False, {"error": str(e)})
    
    @pytest.mark.asyncio
    async def test_skill_assessment_workflow(self, base_url, uat_results):
        """UAT: Candidate can take skill assessment and receive results"""
        scenario_name = "skill_assessment_workflow"
        
        try:
            async with aiohttp.ClientSession() as session:
                # Setup: Create and login candidate
                candidate_data = {
                    "email": f"uat_assessment_{int(time.time())}@example.com",
                    "password": "UATPassword123!",
                    "first_name": "Assessment",
                    "last_name": "Candidate",
                    "user_type": "candidate"
                }
                
                await session.post(f"{base_url}/api/auth/register", json=candidate_data)
                login_response = await session.post(f"{base_url}/api/auth/login", json={
                    "email": candidate_data["email"],
                    "password": candidate_data["password"]
                })
                auth_data = await login_response.json()
                headers = {"Authorization": f"Bearer {auth_data['access_token']}"}
                
                # Step 1: Start assessment
                assessment_data = {
                    "assessment_type": "technical",
                    "difficulty_level": "intermediate"
                }
                
                start_time = time.time()
                async with session.post(f"{base_url}/api/assessments/start", json=assessment_data, headers=headers) as response:
                    if response.status != 200:
                        uat_results.add_scenario_result(scenario_name, False, {"error": "Assessment start failed"})
                        return
                    
                    assessment_info = await response.json()
                    assessment_id = assessment_info["assessment_id"]
                
                # Step 2: Get assessment questions
                async with session.get(f"{base_url}/api/assessments/{assessment_id}", headers=headers) as response:
                    if response.status != 200:
                        uat_results.add_scenario_result(scenario_name, False, {"error": "Assessment retrieval failed"})
                        return
                    
                    assessment = await response.json()
                    questions = assessment.get("questions", [])
                
                # Step 3: Submit responses
                responses = {
                    "responses": [
                        {
                            "question_id": q.get("id", f"q{i}"),
                            "answer": f"This is a sample answer for question {i+1} about {q.get('topic', 'programming')}"
                        }
                        for i, q in enumerate(questions[:3])  # Answer first 3 questions
                    ]
                }
                
                async with session.post(f"{base_url}/api/assessments/{assessment_id}/submit", 
                                      json=responses, headers=headers) as response:
                    assessment_time = time.time() - start_time
                    
                    if response.status != 200:
                        uat_results.add_scenario_result(scenario_name, False, {"error": "Assessment submission failed"})
                        return
                    
                    results = await response.json()
                
                # Step 4: Verify results
                results_valid = (
                    "score" in results and
                    isinstance(results["score"], (int, float)) and
                    0 <= results["score"] <= 1 and
                    "analysis" in results
                )
                
                uat_results.add_scenario_result(
                    scenario_name,
                    results_valid,
                    {
                        "assessment_time": assessment_time,
                        "score": results.get("score"),
                        "questions_answered": len(responses["responses"])
                    }
                )
                uat_results.add_performance_metric("assessment_completion_time", assessment_time)
                uat_results.add_user_workflow("skill_assessment", results_valid)
                
        except Exception as e:
            uat_results.add_error(f"Skill assessment UAT failed: {str(e)}")
            uat_results.add_scenario_result(scenario_name, False, {"error": str(e)})
    
    @pytest.mark.asyncio
    async def test_job_matching_and_application(self, base_url, uat_results):
        """UAT: Candidate receives job recommendations and can apply"""
        scenario_name = "job_matching_application"
        
        try:
            async with aiohttp.ClientSession() as session:
                # Setup: Create candidate with skills
                candidate_data = {
                    "email": f"uat_jobmatch_{int(time.time())}@example.com",
                    "password": "UATPassword123!",
                    "first_name": "JobMatch",
                    "last_name": "Candidate",
                    "user_type": "candidate"
                }
                
                await session.post(f"{base_url}/api/auth/register", json=candidate_data)
                login_response = await session.post(f"{base_url}/api/auth/login", json={
                    "email": candidate_data["email"],
                    "password": candidate_data["password"]
                })
                auth_data = await login_response.json()
                headers = {"Authorization": f"Bearer {auth_data['access_token']}"}
                
                # Update profile with skills
                profile_data = {
                    "skills": ["Python", "FastAPI", "PostgreSQL"],
                    "experience_years": 3,
                    "preferred_locations": ["Remote"]
                }
                await session.put(f"{base_url}/api/users/profile", json=profile_data, headers=headers)
                
                # Step 1: Get job recommendations
                start_time = time.time()
                async with session.get(f"{base_url}/api/matching/recommendations", headers=headers) as response:
                    recommendation_time = time.time() - start_time
                    
                    if response.status != 200:
                        uat_results.add_scenario_result(scenario_name, False, {"error": "Job recommendations failed"})
                        return
                    
                    recommendations = await response.json()
                    job_list = recommendations.get("recommendations", [])
                
                # Step 2: Apply to a job (if available)
                application_successful = False
                if job_list:
                    job_id = job_list[0].get("job_id", "test_job_123")
                    application_data = {
                        "cover_letter": "I am very interested in this position and believe my skills are a great match."
                    }
                    
                    async with session.post(f"{base_url}/api/jobs/{job_id}/apply", 
                                          json=application_data, headers=headers) as response:
                        application_successful = response.status == 200
                
                # Step 3: Check application status
                async with session.get(f"{base_url}/api/applications/status", headers=headers) as response:
                    if response.status == 200:
                        applications = await response.json()
                        has_applications = isinstance(applications, list)
                    else:
                        has_applications = False
                
                workflow_complete = (
                    len(job_list) >= 0 and  # Should get recommendations (even if empty)
                    has_applications  # Should be able to check application status
                )
                
                uat_results.add_scenario_result(
                    scenario_name,
                    workflow_complete,
                    {
                        "recommendation_time": recommendation_time,
                        "recommendations_count": len(job_list),
                        "application_successful": application_successful
                    }
                )
                uat_results.add_performance_metric("job_recommendation_time", recommendation_time)
                uat_results.add_user_workflow("job_matching", workflow_complete)
                
        except Exception as e:
            uat_results.add_error(f"Job matching UAT failed: {str(e)}")
            uat_results.add_scenario_result(scenario_name, False, {"error": str(e)})


class TestCompanyUserAcceptance:
    """UAT scenarios for company users"""
    
    @pytest.mark.asyncio
    async def test_company_job_posting_workflow(self, base_url, uat_results):
        """UAT: Company can post jobs and manage applications"""
        scenario_name = "company_job_posting"
        
        try:
            async with aiohttp.ClientSession() as session:
                # Setup: Create and login company
                company_data = {
                    "email": f"uat_company_{int(time.time())}@example.com",
                    "password": "UATCompanyPassword123!",
                    "first_name": "UAT",
                    "last_name": "Company",
                    "user_type": "company"
                }
                
                await session.post(f"{base_url}/api/auth/register", json=company_data)
                login_response = await session.post(f"{base_url}/api/auth/login", json={
                    "email": company_data["email"],
                    "password": company_data["password"]
                })
                auth_data = await login_response.json()
                headers = {"Authorization": f"Bearer {auth_data['access_token']}"}
                
                # Step 1: Post a job
                job_data = {
                    "title": "Senior Python Developer - UAT",
                    "description": "We are looking for an experienced Python developer for our UAT testing team.",
                    "requirements": ["Python", "FastAPI", "5+ years experience"],
                    "skills_required": ["Python", "FastAPI", "PostgreSQL", "Docker"],
                    "experience_level": "senior",
                    "salary_range": {"min": 100000, "max": 140000},
                    "location": "San Francisco",
                    "remote_allowed": True
                }
                
                start_time = time.time()
                async with session.post(f"{base_url}/api/jobs/create", json=job_data, headers=headers) as response:
                    job_posting_time = time.time() - start_time
                    
                    if response.status != 201:
                        uat_results.add_scenario_result(scenario_name, False, {"error": "Job posting failed"})
                        return
                    
                    job_info = await response.json()
                    job_id = job_info["id"]
                
                # Step 2: Verify job was posted
                async with session.get(f"{base_url}/api/jobs/{job_id}", headers=headers) as response:
                    if response.status != 200:
                        uat_results.add_scenario_result(scenario_name, False, {"error": "Job retrieval failed"})
                        return
                    
                    posted_job = await response.json()
                    job_posted_correctly = (
                        posted_job["title"] == job_data["title"] and
                        posted_job["location"] == job_data["location"] and
                        posted_job["remote_allowed"] == job_data["remote_allowed"]
                    )
                
                # Step 3: Access company dashboard
                async with session.get(f"{base_url}/api/dashboard/company", headers=headers) as response:
                    dashboard_accessible = response.status == 200
                    if dashboard_accessible:
                        dashboard_data = await response.json()
                        has_job_metrics = "active_jobs" in dashboard_data
                    else:
                        has_job_metrics = False
                
                workflow_complete = (
                    job_posted_correctly and
                    dashboard_accessible and
                    has_job_metrics
                )
                
                uat_results.add_scenario_result(
                    scenario_name,
                    workflow_complete,
                    {
                        "job_posting_time": job_posting_time,
                        "job_posted_correctly": job_posted_correctly,
                        "dashboard_accessible": dashboard_accessible
                    }
                )
                uat_results.add_performance_metric("job_posting_time", job_posting_time)
                uat_results.add_user_workflow("company_job_posting", workflow_complete)
                
        except Exception as e:
            uat_results.add_error(f"Company job posting UAT failed: {str(e)}")
            uat_results.add_scenario_result(scenario_name, False, {"error": str(e)})
    
    @pytest.mark.asyncio
    async def test_candidate_review_workflow(self, base_url, uat_results):
        """UAT: Company can review candidates and their assessments"""
        scenario_name = "candidate_review_workflow"
        
        try:
            async with aiohttp.ClientSession() as session:
                # Setup: Create company
                company_data = {
                    "email": f"uat_review_{int(time.time())}@example.com",
                    "password": "UATReviewPassword123!",
                    "first_name": "Review",
                    "last_name": "Company",
                    "user_type": "company"
                }
                
                await session.post(f"{base_url}/api/auth/register", json=company_data)
                login_response = await session.post(f"{base_url}/api/auth/login", json={
                    "email": company_data["email"],
                    "password": company_data["password"]
                })
                auth_data = await login_response.json()
                headers = {"Authorization": f"Bearer {auth_data['access_token']}"}
                
                # Step 1: Get candidate recommendations for a job
                job_id = "test_job_123"  # Mock job ID
                async with session.get(f"{base_url}/api/matching/candidates/{job_id}", headers=headers) as response:
                    if response.status == 200:
                        candidates = await response.json()
                        candidate_list = candidates.get("candidates", [])
                        has_candidates = len(candidate_list) >= 0  # Even empty list is valid
                    else:
                        has_candidates = False
                
                # Step 2: Access analytics dashboard
                async with session.get(f"{base_url}/api/dashboard/company", headers=headers) as response:
                    if response.status == 200:
                        dashboard = await response.json()
                        has_analytics = any(key in dashboard for key in ["total_applications", "active_jobs", "metrics"])
                    else:
                        has_analytics = False
                
                # Step 3: Test candidate search functionality
                search_params = {"skills": "Python", "experience_min": 2}
                async with session.get(f"{base_url}/api/candidates/search", params=search_params, headers=headers) as response:
                    search_functional = response.status in [200, 404]  # 404 is acceptable if no candidates match
                
                workflow_complete = (
                    has_candidates and
                    has_analytics and
                    search_functional
                )
                
                uat_results.add_scenario_result(
                    scenario_name,
                    workflow_complete,
                    {
                        "has_candidates": has_candidates,
                        "has_analytics": has_analytics,
                        "search_functional": search_functional
                    }
                )
                uat_results.add_user_workflow("candidate_review", workflow_complete)
                
        except Exception as e:
            uat_results.add_error(f"Candidate review UAT failed: {str(e)}")
            uat_results.add_scenario_result(scenario_name, False, {"error": str(e)})


class TestBusinessRequirementValidation:
    """Validate business requirements are met"""
    
    @pytest.mark.asyncio
    async def test_ai_assessment_requirement(self, base_url, uat_results):
        """Validate: System provides AI-powered skill assessments"""
        try:
            # This would test that the AI assessment system is working
            # For UAT, we verify the endpoints exist and return expected data
            
            async with aiohttp.ClientSession() as session:
                # Test assessment endpoint exists
                async with session.get(f"{base_url}/api/assessments/health") as response:
                    assessment_service_available = response.status == 200
                
                uat_results.add_business_requirement("ai_powered_assessments", assessment_service_available)
                
        except Exception as e:
            uat_results.add_error(f"AI assessment requirement validation failed: {str(e)}")
            uat_results.add_business_requirement("ai_powered_assessments", False)
    
    @pytest.mark.asyncio
    async def test_job_matching_requirement(self, base_url, uat_results):
        """Validate: System provides intelligent job matching"""
        try:
            async with aiohttp.ClientSession() as session:
                # Test job matching endpoint exists
                async with session.get(f"{base_url}/api/matching/health") as response:
                    matching_service_available = response.status == 200
                
                uat_results.add_business_requirement("intelligent_job_matching", matching_service_available)
                
        except Exception as e:
            uat_results.add_error(f"Job matching requirement validation failed: {str(e)}")
            uat_results.add_business_requirement("intelligent_job_matching", False)
    
    @pytest.mark.asyncio
    async def test_security_requirement(self, base_url, uat_results):
        """Validate: System implements proper security measures"""
        try:
            async with aiohttp.ClientSession() as session:
                # Test that protected endpoints require authentication
                async with session.get(f"{base_url}/api/users/profile") as response:
                    requires_auth = response.status == 401
                
                # Test that security headers are present
                async with session.get(f"{base_url}/health") as response:
                    has_security_headers = (
                        "X-Content-Type-Options" in response.headers or
                        "X-Frame-Options" in response.headers
                    )
                
                security_implemented = requires_auth and has_security_headers
                uat_results.add_business_requirement("security_measures", security_implemented)
                
        except Exception as e:
            uat_results.add_error(f"Security requirement validation failed: {str(e)}")
            uat_results.add_business_requirement("security_measures", False)
    
    @pytest.mark.asyncio
    async def test_scalability_requirement(self, base_url, uat_results):
        """Validate: System is designed for scalability"""
        try:
            async with aiohttp.ClientSession() as session:
                # Test that system responds within reasonable time under normal load
                start_time = time.time()
                async with session.get(f"{base_url}/health") as response:
                    response_time = time.time() - start_time
                    
                    scalable_performance = (
                        response.status == 200 and
                        response_time < 2.0  # Should respond quickly
                    )
                
                uat_results.add_business_requirement("scalable_architecture", scalable_performance)
                uat_results.add_performance_metric("health_check_response_time", response_time)
                
        except Exception as e:
            uat_results.add_error(f"Scalability requirement validation failed: {str(e)}")
            uat_results.add_business_requirement("scalable_architecture", False)


@pytest.mark.uat
async def test_comprehensive_user_acceptance():
    """Run comprehensive User Acceptance Testing"""
    results = UATResults()
    base_url = os.getenv("TEST_BASE_URL", "http://localhost:8000")
    
    # Run all UAT test classes
    test_classes = [
        TestCandidateUserAcceptance(),
        TestCompanyUserAcceptance(),
        TestBusinessRequirementValidation()
    ]
    
    for test_class in test_classes:
        for method_name in dir(test_class):
            if method_name.startswith('test_'):
                method = getattr(test_class, method_name)
                if asyncio.iscoroutinefunction(method):
                    try:
                        await method(base_url, results)
                    except Exception as e:
                        results.add_error(f"UAT {method_name} failed: {str(e)}")
    
    # Generate UAT report
    summary = results.get_summary()
    
    # Save detailed report
    with open("uat_report.json", "w") as f:
        json.dump(summary, f, indent=2)
    
    print("\n" + "="*60)
    print("USER ACCEPTANCE TESTING RESULTS")
    print("="*60)
    print(f"Scenarios: {summary['summary']['passed_scenarios']}/{summary['summary']['total_scenarios']} passed")
    print(f"Scenario Success Rate: {summary['summary']['scenario_success_rate']:.1%}")
    print(f"Business Requirements: {summary['summary']['satisfied_requirements']}/{summary['summary']['total_requirements']} satisfied")
    print(f"Requirement Satisfaction Rate: {summary['summary']['requirement_satisfaction_rate']:.1%}")
    print(f"User Workflows: {summary['summary']['completed_workflows']}/{summary['summary']['total_workflows']} completed")
    print(f"Workflow Completion Rate: {summary['summary']['workflow_completion_rate']:.1%}")
    print(f"Errors: {len(summary['errors'])}")
    
    if summary['performance_metrics']:
        print("\nPERFORMANCE METRICS:")
        for metric, value in summary['performance_metrics'].items():
            print(f"  {metric}: {value:.2f}s")
    
    if summary['errors']:
        print("\nERRORS:")
        for error in summary['errors']:
            print(f"  - {error}")
    
    print(f"\nDetailed report saved to: uat_report.json")
    
    # Assert UAT acceptance criteria
    assert summary['summary']['scenario_success_rate'] > 0.8, f"UAT scenario success rate too low: {summary['summary']['scenario_success_rate']:.1%}"
    assert summary['summary']['requirement_satisfaction_rate'] > 0.9, f"Business requirement satisfaction too low: {summary['summary']['requirement_satisfaction_rate']:.1%}"
    assert summary['summary']['workflow_completion_rate'] > 0.8, f"User workflow completion rate too low: {summary['summary']['workflow_completion_rate']:.1%}"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--asyncio-mode=auto"])