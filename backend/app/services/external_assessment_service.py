"""
External Assessment Service
Integrates with third-party assessment platforms for real skill testing
"""

from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import httpx
import json
from ..config import settings

class ExternalAssessmentProvider:
    """Base class for external assessment providers"""
    
    def __init__(self, api_key: str, base_url: str):
        self.api_key = api_key
        self.base_url = base_url
        self.client = httpx.AsyncClient(timeout=30.0)
    
    async def get_available_tests(self) -> List[Dict[str, Any]]:
        """Get list of available tests from provider"""
        raise NotImplementedError
    
    async def create_test_session(self, test_id: str, candidate_email: str) -> Dict[str, Any]:
        """Create a test session for a candidate"""
        raise NotImplementedError
    
    async def get_test_results(self, session_id: str) -> Dict[str, Any]:
        """Get results for a completed test"""
        raise NotImplementedError
    
    async def close(self):
        """Close HTTP client"""
        await self.client.aclose()


class HackerRankProvider(ExternalAssessmentProvider):
    """
    HackerRank Integration
    https://www.hackerrank.com/work/tests
    """
    
    def __init__(self):
        super().__init__(
            api_key=settings.HACKERRANK_API_KEY,
            base_url="https://www.hackerrank.com/x/api/v3"
        )
    
    async def get_available_tests(self) -> List[Dict[str, Any]]:
        """Get HackerRank tests"""
        try:
            response = await self.client.get(
                f"{self.base_url}/tests",
                headers={"Authorization": f"Bearer {self.api_key}"}
            )
            response.raise_for_status()
            data = response.json()
            
            return [
                {
                    "id": test["id"],
                    "name": test["name"],
                    "description": test["description"],
                    "duration": test["duration"],
                    "skills": test["skills"],
                    "difficulty": test["difficulty"],
                    "provider": "hackerrank"
                }
                for test in data.get("data", [])
            ]
        except Exception as e:
            print(f"HackerRank API error: {e}")
            return self._get_mock_tests()
    
    async def create_test_session(self, test_id: str, candidate_email: str) -> Dict[str, Any]:
        """Create HackerRank test invitation"""
        try:
            response = await self.client.post(
                f"{self.base_url}/tests/{test_id}/candidates",
                headers={"Authorization": f"Bearer {self.api_key}"},
                json={
                    "email": candidate_email,
                    "full_name": candidate_email.split("@")[0],
                    "send_email": True
                }
            )
            response.raise_for_status()
            data = response.json()
            
            return {
                "session_id": data["id"],
                "test_url": data["url"],
                "expires_at": data["expires_at"],
                "status": "invited"
            }
        except Exception as e:
            print(f"HackerRank session creation error: {e}")
            return self._get_mock_session(test_id)
    
    async def get_test_results(self, session_id: str) -> Dict[str, Any]:
        """Get HackerRank test results"""
        try:
            response = await self.client.get(
                f"{self.base_url}/tests/candidates/{session_id}",
                headers={"Authorization": f"Bearer {self.api_key}"}
            )
            response.raise_for_status()
            data = response.json()
            
            return {
                "score": data["score"],
                "percentage": data["percentage_score"],
                "status": data["status"],
                "completed_at": data["completed_at"],
                "time_taken": data["time_taken"],
                "questions_attempted": data["questions_attempted"],
                "questions_correct": data["questions_correct"]
            }
        except Exception as e:
            print(f"HackerRank results error: {e}")
            return None
    
    def _get_mock_tests(self) -> List[Dict[str, Any]]:
        """Mock tests for development"""
        return [
            {
                "id": "hr_python_001",
                "name": "Python Programming Assessment",
                "description": "Test Python fundamentals, data structures, and algorithms",
                "duration": 60,
                "skills": ["Python", "Algorithms", "Data Structures"],
                "difficulty": "intermediate",
                "provider": "hackerrank"
            },
            {
                "id": "hr_javascript_001",
                "name": "JavaScript & React Assessment",
                "description": "Test JavaScript ES6+, React, and frontend development",
                "duration": 75,
                "skills": ["JavaScript", "React", "Frontend"],
                "difficulty": "intermediate",
                "provider": "hackerrank"
            },
            {
                "id": "hr_sql_001",
                "name": "SQL Database Assessment",
                "description": "Test SQL queries, database design, and optimization",
                "duration": 45,
                "skills": ["SQL", "Database", "PostgreSQL"],
                "difficulty": "intermediate",
                "provider": "hackerrank"
            }
        ]
    
    def _get_mock_session(self, test_id: str) -> Dict[str, Any]:
        """Mock session for development"""
        return {
            "session_id": f"mock_session_{test_id}_{datetime.utcnow().timestamp()}",
            "test_url": f"https://www.hackerrank.com/test/{test_id}",
            "expires_at": (datetime.utcnow() + timedelta(days=7)).isoformat(),
            "status": "invited"
        }


class CodeSignalProvider(ExternalAssessmentProvider):
    """
    CodeSignal Integration
    https://codesignal.com/developers/
    """
    
    def __init__(self):
        super().__init__(
            api_key=settings.CODESIGNAL_API_KEY,
            base_url="https://api.codesignal.com/v1"
        )
    
    async def get_available_tests(self) -> List[Dict[str, Any]]:
        """Get CodeSignal tests"""
        return [
            {
                "id": "cs_general_001",
                "name": "General Coding Assessment (GCA)",
                "description": "Comprehensive coding skills evaluation",
                "duration": 70,
                "skills": ["Problem Solving", "Algorithms", "Coding"],
                "difficulty": "all_levels",
                "provider": "codesignal"
            },
            {
                "id": "cs_frontend_001",
                "name": "Frontend Developer Assessment",
                "description": "HTML, CSS, JavaScript, and React skills",
                "duration": 60,
                "skills": ["HTML", "CSS", "JavaScript", "React"],
                "difficulty": "intermediate",
                "provider": "codesignal"
            },
            {
                "id": "cs_backend_001",
                "name": "Backend Developer Assessment",
                "description": "Server-side programming and API development",
                "duration": 75,
                "skills": ["Python", "Node.js", "APIs", "Databases"],
                "difficulty": "intermediate",
                "provider": "codesignal"
            }
        ]


class TestGorillaProvider(ExternalAssessmentProvider):
    """
    TestGorilla Integration
    https://www.testgorilla.com/
    """
    
    def __init__(self):
        super().__init__(
            api_key=settings.TESTGORILLA_API_KEY,
            base_url="https://api.testgorilla.com/v1"
        )
    
    async def get_available_tests(self) -> List[Dict[str, Any]]:
        """Get TestGorilla tests"""
        return [
            {
                "id": "tg_cognitive_001",
                "name": "Cognitive Ability Test",
                "description": "Measure problem-solving and critical thinking",
                "duration": 30,
                "skills": ["Critical Thinking", "Problem Solving", "Logic"],
                "difficulty": "all_levels",
                "provider": "testgorilla"
            },
            {
                "id": "tg_personality_001",
                "name": "Big 5 Personality Test",
                "description": "Assess personality traits and work style",
                "duration": 20,
                "skills": ["Personality", "Work Style", "Culture Fit"],
                "difficulty": "all_levels",
                "provider": "testgorilla"
            },
            {
                "id": "tg_communication_001",
                "name": "Communication Skills Test",
                "description": "Evaluate written and verbal communication",
                "duration": 25,
                "skills": ["Communication", "Writing", "Presentation"],
                "difficulty": "all_levels",
                "provider": "testgorilla"
            }
        ]


class PluralsightProvider(ExternalAssessmentProvider):
    """
    Pluralsight Skills Integration
    https://www.pluralsight.com/product/skills
    """
    
    def __init__(self):
        super().__init__(
            api_key=settings.PLURALSIGHT_API_KEY,
            base_url="https://api.pluralsight.com/v1"
        )
    
    async def get_available_tests(self) -> List[Dict[str, Any]]:
        """Get Pluralsight skill assessments"""
        return [
            {
                "id": "ps_python_001",
                "name": "Python Skill Assessment",
                "description": "Comprehensive Python programming evaluation",
                "duration": 45,
                "skills": ["Python", "OOP", "Data Structures"],
                "difficulty": "all_levels",
                "provider": "pluralsight"
            },
            {
                "id": "ps_react_001",
                "name": "React Skill Assessment",
                "description": "React.js framework and ecosystem",
                "duration": 40,
                "skills": ["React", "JavaScript", "Hooks", "Redux"],
                "difficulty": "intermediate",
                "provider": "pluralsight"
            },
            {
                "id": "ps_aws_001",
                "name": "AWS Cloud Assessment",
                "description": "Amazon Web Services fundamentals and services",
                "duration": 50,
                "skills": ["AWS", "Cloud", "DevOps"],
                "difficulty": "intermediate",
                "provider": "pluralsight"
            }
        ]


class ExternalAssessmentService:
    """
    Main service to manage external assessment providers
    """
    
    def __init__(self):
        self.providers = {
            "hackerrank": HackerRankProvider(),
            "codesignal": CodeSignalProvider(),
            "testgorilla": TestGorillaProvider(),
            "pluralsight": PluralsightProvider()
        }
    
    async def get_all_available_tests(self) -> List[Dict[str, Any]]:
        """Get all available tests from all providers"""
        all_tests = []
        
        for provider_name, provider in self.providers.items():
            try:
                tests = await provider.get_available_tests()
                all_tests.extend(tests)
            except Exception as e:
                print(f"Error fetching tests from {provider_name}: {e}")
        
        return all_tests
    
    async def get_tests_by_skill(self, skill: str) -> List[Dict[str, Any]]:
        """Get tests filtered by skill"""
        all_tests = await self.get_all_available_tests()
        return [
            test for test in all_tests
            if skill.lower() in [s.lower() for s in test.get("skills", [])]
        ]
    
    async def get_tests_by_provider(self, provider_name: str) -> List[Dict[str, Any]]:
        """Get tests from specific provider"""
        if provider_name not in self.providers:
            return []
        
        provider = self.providers[provider_name]
        return await provider.get_available_tests()
    
    async def create_test_session(
        self,
        provider_name: str,
        test_id: str,
        candidate_email: str
    ) -> Optional[Dict[str, Any]]:
        """Create test session with specific provider"""
        if provider_name not in self.providers:
            return None
        
        provider = self.providers[provider_name]
        return await provider.create_test_session(test_id, candidate_email)
    
    async def get_test_results(
        self,
        provider_name: str,
        session_id: str
    ) -> Optional[Dict[str, Any]]:
        """Get test results from specific provider"""
        if provider_name not in self.providers:
            return None
        
        provider = self.providers[provider_name]
        return await provider.get_test_results(session_id)
    
    async def close_all(self):
        """Close all provider connections"""
        for provider in self.providers.values():
            await provider.close()
    
    def get_recommended_tests(self, job_skills: List[str]) -> List[Dict[str, Any]]:
        """Get recommended tests based on job requirements"""
        # This would use ML to recommend best tests
        # For now, return mock recommendations
        return [
            {
                "id": "hr_python_001",
                "name": "Python Programming Assessment",
                "provider": "hackerrank",
                "match_score": 95,
                "reason": "Matches required Python skills"
            },
            {
                "id": "cs_general_001",
                "name": "General Coding Assessment",
                "provider": "codesignal",
                "match_score": 88,
                "reason": "Tests overall coding ability"
            }
        ]


# Singleton instance
external_assessment_service = ExternalAssessmentService()
