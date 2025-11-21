"""
AI-HR Platform Python SDK Client

Main client class for interacting with the AI-HR Platform API.
"""

import httpx
import json
from typing import Dict, Any, Optional, List, Union
from datetime import datetime
import asyncio
from urllib.parse import urljoin

from .exceptions import (
    AIHRException,
    AuthenticationError,
    RateLimitError,
    ValidationError,
    NotFoundError,
    ServerError
)
from .models import User, Assessment, Job, JobMatch, Interview, Webhook


class AIHRClient:
    """
    AI-HR Platform API Client
    
    Provides a convenient interface for interacting with the AI-HR Platform API.
    
    Example:
        ```python
        from aihr_platform_sdk import AIHRClient
        
        # Initialize client
        client = AIHRClient(
            api_key="your_api_key",
            base_url="https://api.aihr-platform.com"
        )
        
        # Authenticate user
        user = await client.auth.login("user@example.com", "password")
        
        # Start assessment
        assessment = await client.assessments.start("technical")
        
        # Get job recommendations
        matches = await client.matching.get_recommendations()
        ```
    """
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        access_token: Optional[str] = None,
        base_url: str = "https://api.aihr-platform.com",
        api_version: str = "1.1",
        timeout: float = 30.0,
        max_retries: int = 3
    ):
        """
        Initialize the AI-HR Platform client
        
        Args:
            api_key: API key for server-to-server authentication
            access_token: JWT access token for user authentication
            base_url: Base URL of the API
            api_version: API version to use
            timeout: Request timeout in seconds
            max_retries: Maximum number of retries for failed requests
        """
        self.base_url = base_url.rstrip('/')
        self.api_version = api_version
        self.timeout = timeout
        self.max_retries = max_retries
        
        # Authentication
        self._api_key = api_key
        self._access_token = access_token
        
        # HTTP client
        self._client = httpx.AsyncClient(
            timeout=timeout,
            headers=self._get_default_headers()
        )
        
        # API endpoints
        self.auth = AuthAPI(self)
        self.users = UsersAPI(self)
        self.assessments = AssessmentsAPI(self)
        self.jobs = JobsAPI(self)
        self.matching = MatchingAPI(self)
        self.interviews = InterviewsAPI(self)
        self.webhooks = WebhooksAPI(self)
        self.analytics = AnalyticsAPI(self)
    
    def _get_default_headers(self) -> Dict[str, str]:
        """Get default headers for requests"""
        headers = {
            "User-Agent": f"aihr-platform-sdk-python/1.0.0",
            "Content-Type": "application/json",
            "API-Version": self.api_version
        }
        
        if self._api_key:
            headers["X-API-Key"] = self._api_key
        elif self._access_token:
            headers["Authorization"] = f"Bearer {self._access_token}"
        
        return headers
    
    def set_access_token(self, access_token: str):
        """Set access token for authentication"""
        self._access_token = access_token
        self._client.headers["Authorization"] = f"Bearer {access_token}"
    
    def clear_access_token(self):
        """Clear access token"""
        self._access_token = None
        if "Authorization" in self._client.headers:
            del self._client.headers["Authorization"]
    
    async def request(
        self,
        method: str,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """
        Make HTTP request to API
        
        Args:
            method: HTTP method (GET, POST, PUT, DELETE)
            endpoint: API endpoint (without base URL)
            data: Request body data
            params: Query parameters
            headers: Additional headers
            
        Returns:
            Response data as dictionary
            
        Raises:
            AIHRException: For API errors
        """
        url = urljoin(self.base_url, endpoint.lstrip('/'))
        
        # Merge headers
        request_headers = self._client.headers.copy()
        if headers:
            request_headers.update(headers)
        
        # Retry logic
        for attempt in range(self.max_retries + 1):
            try:
                response = await self._client.request(
                    method=method,
                    url=url,
                    json=data,
                    params=params,
                    headers=request_headers
                )
                
                # Handle response
                return self._handle_response(response)
                
            except httpx.TimeoutException:
                if attempt == self.max_retries:
                    raise AIHRException("Request timeout")
                await asyncio.sleep(2 ** attempt)  # Exponential backoff
                
            except httpx.RequestError as e:
                if attempt == self.max_retries:
                    raise AIHRException(f"Request error: {str(e)}")
                await asyncio.sleep(2 ** attempt)
    
    def _handle_response(self, response: httpx.Response) -> Dict[str, Any]:
        """Handle HTTP response and raise appropriate exceptions"""
        
        # Parse JSON response
        try:
            data = response.json()
        except json.JSONDecodeError:
            data = {"detail": response.text}
        
        # Handle success
        if 200 <= response.status_code < 300:
            return data
        
        # Handle errors
        error_message = data.get("detail", f"HTTP {response.status_code}")
        
        if response.status_code == 401:
            raise AuthenticationError(error_message)
        elif response.status_code == 403:
            raise AuthenticationError(error_message)
        elif response.status_code == 404:
            raise NotFoundError(error_message)
        elif response.status_code == 422:
            raise ValidationError(error_message, data.get("errors"))
        elif response.status_code == 429:
            raise RateLimitError(
                error_message,
                retry_after=int(response.headers.get("Retry-After", 60))
            )
        elif response.status_code >= 500:
            raise ServerError(error_message)
        else:
            raise AIHRException(error_message)
    
    async def close(self):
        """Close the HTTP client"""
        await self._client.aclose()
    
    async def __aenter__(self):
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()


class AuthAPI:
    """Authentication API endpoints"""
    
    def __init__(self, client: AIHRClient):
        self.client = client
    
    async def register(
        self,
        email: str,
        password: str,
        first_name: str,
        last_name: str,
        user_type: str = "candidate"
    ) -> User:
        """Register a new user"""
        data = {
            "email": email,
            "password": password,
            "first_name": first_name,
            "last_name": last_name,
            "user_type": user_type
        }
        
        response = await self.client.request("POST", "/api/auth/register", data=data)
        return User.from_dict(response)
    
    async def login(self, email: str, password: str) -> Dict[str, Any]:
        """Login user and get tokens"""
        data = {"email": email, "password": password}
        
        response = await self.client.request("POST", "/api/auth/login", data=data)
        
        # Set access token in client
        if "access_token" in response:
            self.client.set_access_token(response["access_token"])
        
        return response
    
    async def refresh_token(self, refresh_token: str) -> Dict[str, Any]:
        """Refresh access token"""
        data = {"refresh_token": refresh_token}
        
        response = await self.client.request("POST", "/api/auth/refresh", data=data)
        
        # Update access token in client
        if "access_token" in response:
            self.client.set_access_token(response["access_token"])
        
        return response
    
    async def logout(self):
        """Logout user"""
        await self.client.request("POST", "/api/auth/logout")
        self.client.clear_access_token()


class AssessmentsAPI:
    """Assessment API endpoints"""
    
    def __init__(self, client: AIHRClient):
        self.client = client
    
    async def start(
        self,
        assessment_type: str,
        job_id: Optional[str] = None,
        difficulty_level: str = "intermediate"
    ) -> Assessment:
        """Start a new assessment"""
        data = {
            "assessment_type": assessment_type,
            "difficulty_level": difficulty_level
        }
        
        if job_id:
            data["job_id"] = job_id
        
        response = await self.client.request("POST", "/api/assessments/start", data=data)
        return Assessment.from_dict(response)
    
    async def get(self, assessment_id: str) -> Assessment:
        """Get assessment details"""
        response = await self.client.request("GET", f"/api/assessments/{assessment_id}")
        return Assessment.from_dict(response)
    
    async def submit_response(
        self,
        assessment_id: str,
        question_id: str,
        answer: Union[str, List[str], Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Submit answer to assessment question"""
        data = {
            "question_id": question_id,
            "answer": answer
        }
        
        return await self.client.request(
            "POST",
            f"/api/assessments/{assessment_id}/submit",
            data=data
        )
    
    async def complete(self, assessment_id: str) -> Dict[str, Any]:
        """Complete assessment and get results"""
        return await self.client.request("POST", f"/api/assessments/{assessment_id}/complete")


class JobsAPI:
    """Job API endpoints"""
    
    def __init__(self, client: AIHRClient):
        self.client = client
    
    async def search(
        self,
        query: Optional[str] = None,
        location: Optional[str] = None,
        remote: Optional[bool] = None,
        salary_min: Optional[int] = None,
        salary_max: Optional[int] = None,
        limit: int = 20,
        offset: int = 0
    ) -> List[Job]:
        """Search for jobs"""
        params = {"limit": limit, "offset": offset}
        
        if query:
            params["query"] = query
        if location:
            params["location"] = location
        if remote is not None:
            params["remote"] = remote
        if salary_min:
            params["salary_min"] = salary_min
        if salary_max:
            params["salary_max"] = salary_max
        
        response = await self.client.request("GET", "/api/jobs/search", params=params)
        return [Job.from_dict(job) for job in response.get("jobs", [])]
    
    async def get(self, job_id: str) -> Job:
        """Get job details"""
        response = await self.client.request("GET", f"/api/jobs/{job_id}")
        return Job.from_dict(response)
    
    async def apply(self, job_id: str, cover_letter: Optional[str] = None) -> Dict[str, Any]:
        """Apply for a job"""
        data = {}
        if cover_letter:
            data["cover_letter"] = cover_letter
        
        return await self.client.request("POST", f"/api/jobs/{job_id}/apply", data=data)


class MatchingAPI:
    """Job matching API endpoints"""
    
    def __init__(self, client: AIHRClient):
        self.client = client
    
    async def get_recommendations(
        self,
        limit: int = 10,
        min_score: float = 0.5
    ) -> List[JobMatch]:
        """Get job recommendations for current user"""
        params = {"limit": limit, "min_score": min_score}
        
        response = await self.client.request(
            "GET",
            "/api/matching/recommendations",
            params=params
        )
        
        return [JobMatch.from_dict(match) for match in response.get("recommendations", [])]
    
    async def get_match_score(self, job_id: str) -> Dict[str, Any]:
        """Get match score for specific job"""
        return await self.client.request("GET", f"/api/matching/score/{job_id}")


class InterviewsAPI:
    """Interview API endpoints"""
    
    def __init__(self, client: AIHRClient):
        self.client = client
    
    async def schedule(
        self,
        job_id: str,
        interview_type: str = "ai_video",
        preferred_time: Optional[datetime] = None
    ) -> Interview:
        """Schedule an interview"""
        data = {
            "job_id": job_id,
            "interview_type": interview_type
        }
        
        if preferred_time:
            data["preferred_time"] = preferred_time.isoformat()
        
        response = await self.client.request("POST", "/api/interviews/schedule", data=data)
        return Interview.from_dict(response)
    
    async def join(self, interview_id: str) -> Dict[str, Any]:
        """Join an interview session"""
        return await self.client.request("GET", f"/api/interviews/{interview_id}/join")
    
    async def get_results(self, interview_id: str) -> Dict[str, Any]:
        """Get interview results"""
        return await self.client.request("GET", f"/api/interviews/{interview_id}/results")


class WebhooksAPI:
    """Webhook API endpoints"""
    
    def __init__(self, client: AIHRClient):
        self.client = client
    
    async def create(
        self,
        url: str,
        events: List[str],
        secret: Optional[str] = None,
        description: Optional[str] = None
    ) -> Webhook:
        """Create a webhook endpoint"""
        data = {
            "url": url,
            "events": events
        }
        
        if secret:
            data["secret"] = secret
        if description:
            data["description"] = description
        
        response = await self.client.request("POST", "/api/webhooks", data=data)
        return Webhook.from_dict(response)
    
    async def list(self) -> List[Webhook]:
        """List all webhooks"""
        response = await self.client.request("GET", "/api/webhooks")
        return [Webhook.from_dict(webhook) for webhook in response]
    
    async def get(self, webhook_id: str) -> Webhook:
        """Get webhook details"""
        response = await self.client.request("GET", f"/api/webhooks/{webhook_id}")
        return Webhook.from_dict(response)
    
    async def update(
        self,
        webhook_id: str,
        url: Optional[str] = None,
        events: Optional[List[str]] = None,
        secret: Optional[str] = None,
        description: Optional[str] = None,
        is_active: Optional[bool] = None
    ) -> Webhook:
        """Update webhook endpoint"""
        data = {}
        
        if url:
            data["url"] = url
        if events:
            data["events"] = events
        if secret is not None:
            data["secret"] = secret
        if description is not None:
            data["description"] = description
        if is_active is not None:
            data["is_active"] = is_active
        
        response = await self.client.request("PUT", f"/api/webhooks/{webhook_id}", data=data)
        return Webhook.from_dict(response)
    
    async def delete(self, webhook_id: str):
        """Delete webhook endpoint"""
        await self.client.request("DELETE", f"/api/webhooks/{webhook_id}")
    
    async def test(self, webhook_id: str) -> Dict[str, Any]:
        """Test webhook endpoint"""
        return await self.client.request("POST", f"/api/webhooks/{webhook_id}/test")


class UsersAPI:
    """User API endpoints"""
    
    def __init__(self, client: AIHRClient):
        self.client = client
    
    async def get_profile(self) -> User:
        """Get current user profile"""
        response = await self.client.request("GET", "/api/users/profile")
        return User.from_dict(response)
    
    async def update_profile(self, **kwargs) -> User:
        """Update user profile"""
        response = await self.client.request("PUT", "/api/users/profile", data=kwargs)
        return User.from_dict(response)


class AnalyticsAPI:
    """Analytics API endpoints"""
    
    def __init__(self, client: AIHRClient):
        self.client = client
    
    async def get_dashboard_data(self) -> Dict[str, Any]:
        """Get dashboard analytics data"""
        return await self.client.request("GET", "/api/analytics/dashboard")
    
    async def get_usage_stats(self) -> Dict[str, Any]:
        """Get API usage statistics"""
        return await self.client.request("GET", "/api/developer/usage-stats")