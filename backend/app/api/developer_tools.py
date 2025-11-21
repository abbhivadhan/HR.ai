"""
Developer Tools API

Provides sandbox environment, API testing tools, and developer utilities.
"""

from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from fastapi.responses import HTMLResponse, JSONResponse
from sqlalchemy.orm import Session
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import json
import uuid
import asyncio
from pydantic import BaseModel, Field

from ..database import get_db
from ..auth.dependencies import get_current_user
from ..models.user import User
from ..versioning import get_api_version, VersionedResponse
from ..services.rate_limit_service import RateLimitService

router = APIRouter(prefix="/api/developer", tags=["developer-tools"])


class SandboxRequest(BaseModel):
    """Sandbox API request model"""
    endpoint: str = Field(..., description="API endpoint to test")
    method: str = Field(..., description="HTTP method (GET, POST, PUT, DELETE)")
    headers: Optional[Dict[str, str]] = Field(default={}, description="Request headers")
    query_params: Optional[Dict[str, str]] = Field(default={}, description="Query parameters")
    body: Optional[Dict[str, Any]] = Field(default={}, description="Request body")
    api_version: Optional[str] = Field(default="1.1", description="API version to test")


class SandboxResponse(BaseModel):
    """Sandbox API response model"""
    status_code: int
    headers: Dict[str, str]
    body: Dict[str, Any]
    execution_time_ms: float
    api_version: str
    request_id: str


class APIUsageStats(BaseModel):
    """API usage statistics model"""
    total_requests: int
    requests_by_endpoint: Dict[str, int]
    requests_by_method: Dict[str, int]
    average_response_time: float
    error_rate: float
    rate_limit_hits: int
    last_24h_requests: int


class WebhookTest(BaseModel):
    """Webhook testing model"""
    webhook_url: str = Field(..., description="Webhook URL to test")
    event_type: str = Field(..., description="Event type to simulate")
    payload: Dict[str, Any] = Field(..., description="Event payload")
    secret: Optional[str] = Field(default=None, description="Webhook secret for signature")


@router.get("/sandbox", response_class=HTMLResponse)
async def get_sandbox_ui():
    """Get the developer sandbox UI"""
    
    html_content = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>AI-HR Platform Developer Sandbox</title>
        <script src="https://cdn.tailwindcss.com"></script>
        <script src="https://unpkg.com/axios/dist/axios.min.js"></script>
    </head>
    <body class="bg-gray-100 min-h-screen">
        <div class="container mx-auto px-4 py-8">
            <div class="bg-white rounded-lg shadow-lg p-6">
                <h1 class="text-3xl font-bold text-gray-800 mb-6">AI-HR Platform Developer Sandbox</h1>
                
                <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
                    <!-- API Testing Panel -->
                    <div class="bg-gray-50 rounded-lg p-4">
                        <h2 class="text-xl font-semibold mb-4">API Testing</h2>
                        
                        <div class="space-y-4">
                            <div>
                                <label class="block text-sm font-medium text-gray-700">Endpoint</label>
                                <input type="text" id="endpoint" class="mt-1 block w-full rounded-md border-gray-300 shadow-sm" 
                                       placeholder="/api/auth/login" value="/api/auth/login">
                            </div>
                            
                            <div>
                                <label class="block text-sm font-medium text-gray-700">Method</label>
                                <select id="method" class="mt-1 block w-full rounded-md border-gray-300 shadow-sm">
                                    <option value="GET">GET</option>
                                    <option value="POST" selected>POST</option>
                                    <option value="PUT">PUT</option>
                                    <option value="DELETE">DELETE</option>
                                </select>
                            </div>
                            
                            <div>
                                <label class="block text-sm font-medium text-gray-700">API Version</label>
                                <select id="apiVersion" class="mt-1 block w-full rounded-md border-gray-300 shadow-sm">
                                    <option value="1.0">v1.0</option>
                                    <option value="1.1" selected>v1.1</option>
                                </select>
                            </div>
                            
                            <div>
                                <label class="block text-sm font-medium text-gray-700">Headers (JSON)</label>
                                <textarea id="headers" class="mt-1 block w-full rounded-md border-gray-300 shadow-sm" rows="3"
                                          placeholder='{"Authorization": "Bearer your_token"}'></textarea>
                            </div>
                            
                            <div>
                                <label class="block text-sm font-medium text-gray-700">Request Body (JSON)</label>
                                <textarea id="requestBody" class="mt-1 block w-full rounded-md border-gray-300 shadow-sm" rows="5"
                                          placeholder='{"email": "test@example.com", "password": "password123"}'></textarea>
                            </div>
                            
                            <button onclick="testAPI()" class="w-full bg-blue-600 text-white py-2 px-4 rounded-md hover:bg-blue-700">
                                Test API
                            </button>
                        </div>
                    </div>
                    
                    <!-- Response Panel -->
                    <div class="bg-gray-50 rounded-lg p-4">
                        <h2 class="text-xl font-semibold mb-4">Response</h2>
                        <div id="responseContainer" class="bg-gray-800 text-green-400 p-4 rounded-md font-mono text-sm min-h-96 overflow-auto">
                            <div class="text-gray-400">Response will appear here...</div>
                        </div>
                    </div>
                </div>
                
                <!-- Quick Examples -->
                <div class="mt-8">
                    <h2 class="text-xl font-semibold mb-4">Quick Examples</h2>
                    <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
                        <button onclick="loadExample('login')" class="bg-green-600 text-white py-2 px-4 rounded-md hover:bg-green-700">
                            User Login
                        </button>
                        <button onclick="loadExample('assessment')" class="bg-purple-600 text-white py-2 px-4 rounded-md hover:bg-purple-700">
                            Start Assessment
                        </button>
                        <button onclick="loadExample('matching')" class="bg-orange-600 text-white py-2 px-4 rounded-md hover:bg-orange-700">
                            Job Matching
                        </button>
                    </div>
                </div>
            </div>
        </div>
        
        <script>
            const examples = {
                login: {
                    endpoint: '/api/auth/login',
                    method: 'POST',
                    headers: '{"Content-Type": "application/json"}',
                    body: '{"email": "demo@example.com", "password": "demo123"}'
                },
                assessment: {
                    endpoint: '/api/assessments/start',
                    method: 'POST',
                    headers: '{"Authorization": "Bearer your_token", "Content-Type": "application/json"}',
                    body: '{"assessment_type": "technical", "difficulty_level": "intermediate"}'
                },
                matching: {
                    endpoint: '/api/matching/recommendations',
                    method: 'GET',
                    headers: '{"Authorization": "Bearer your_token"}',
                    body: ''
                }
            };
            
            function loadExample(type) {
                const example = examples[type];
                document.getElementById('endpoint').value = example.endpoint;
                document.getElementById('method').value = example.method;
                document.getElementById('headers').value = example.headers;
                document.getElementById('requestBody').value = example.body;
            }
            
            async function testAPI() {
                const endpoint = document.getElementById('endpoint').value;
                const method = document.getElementById('method').value;
                const apiVersion = document.getElementById('apiVersion').value;
                const headers = document.getElementById('headers').value;
                const requestBody = document.getElementById('requestBody').value;
                
                const responseContainer = document.getElementById('responseContainer');
                responseContainer.innerHTML = '<div class="text-yellow-400">Testing API...</div>';
                
                try {
                    const response = await axios.post('/api/developer/sandbox/test', {
                        endpoint: endpoint,
                        method: method,
                        api_version: apiVersion,
                        headers: headers ? JSON.parse(headers) : {},
                        body: requestBody ? JSON.parse(requestBody) : {}
                    });
                    
                    const result = response.data;
                    responseContainer.innerHTML = `
                        <div class="text-blue-400">Status: ${result.status_code}</div>
                        <div class="text-gray-400">Execution Time: ${result.execution_time_ms}ms</div>
                        <div class="text-gray-400">API Version: ${result.api_version}</div>
                        <div class="text-gray-400">Request ID: ${result.request_id}</div>
                        <div class="mt-2 text-white">Response:</div>
                        <pre class="text-green-400 whitespace-pre-wrap">${JSON.stringify(result.body, null, 2)}</pre>
                    `;
                } catch (error) {
                    responseContainer.innerHTML = `
                        <div class="text-red-400">Error: ${error.message}</div>
                        <pre class="text-red-300 whitespace-pre-wrap">${JSON.stringify(error.response?.data || error, null, 2)}</pre>
                    `;
                }
            }
        </script>
    </body>
    </html>
    """
    
    return HTMLResponse(content=html_content)


@router.post("/sandbox/test", response_model=SandboxResponse)
async def test_api_endpoint(
    request: SandboxRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Test API endpoint in sandbox environment"""
    
    start_time = datetime.now()
    request_id = str(uuid.uuid4())
    
    try:
        # Simulate API call (in real implementation, this would make actual HTTP requests)
        # For demo purposes, we'll return mock responses
        
        mock_responses = {
            "/api/auth/login": {
                "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "token_type": "bearer",
                "expires_in": 3600
            },
            "/api/assessments/start": {
                "assessment_id": "assess_123456789",
                "session_token": "session_abc123",
                "time_limit_minutes": 60,
                "total_questions": 25,
                "instructions": "Complete all questions within the time limit..."
            },
            "/api/matching/recommendations": {
                "recommendations": [
                    {
                        "job_id": "job_123456789",
                        "job_title": "Senior Python Developer",
                        "company_name": "TechCorp Inc.",
                        "match_score": 0.92
                    }
                ],
                "total_matches": 15
            }
        }
        
        # Get mock response or default
        response_body = mock_responses.get(request.endpoint, {
            "message": f"Mock response for {request.endpoint}",
            "method": request.method,
            "timestamp": datetime.now().isoformat()
        })
        
        # Calculate execution time
        execution_time = (datetime.now() - start_time).total_seconds() * 1000
        
        return SandboxResponse(
            status_code=200,
            headers={"Content-Type": "application/json", "API-Version": request.api_version},
            body=response_body,
            execution_time_ms=execution_time,
            api_version=request.api_version,
            request_id=request_id
        )
        
    except Exception as e:
        execution_time = (datetime.now() - start_time).total_seconds() * 1000
        
        return SandboxResponse(
            status_code=500,
            headers={"Content-Type": "application/json"},
            body={"error": str(e), "request_id": request_id},
            execution_time_ms=execution_time,
            api_version=request.api_version,
            request_id=request_id
        )


@router.get("/usage-stats", response_model=APIUsageStats)
async def get_api_usage_stats(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get API usage statistics for the current user"""
    
    # In a real implementation, this would query actual usage data
    # For demo purposes, returning mock data
    
    return APIUsageStats(
        total_requests=1250,
        requests_by_endpoint={
            "/api/auth/login": 45,
            "/api/assessments/start": 120,
            "/api/matching/recommendations": 89,
            "/api/jobs/search": 156,
            "/api/analytics/dashboard": 78
        },
        requests_by_method={
            "GET": 680,
            "POST": 420,
            "PUT": 95,
            "DELETE": 55
        },
        average_response_time=245.5,
        error_rate=0.02,
        rate_limit_hits=3,
        last_24h_requests=89
    )


@router.post("/webhook/test")
async def test_webhook(
    webhook_test: WebhookTest,
    current_user: User = Depends(get_current_user)
):
    """Test webhook endpoint with simulated events"""
    
    import httpx
    import hmac
    import hashlib
    
    try:
        # Prepare webhook payload
        payload = {
            "event_type": webhook_test.event_type,
            "timestamp": datetime.now().isoformat(),
            "data": webhook_test.payload
        }
        
        headers = {
            "Content-Type": "application/json",
            "User-Agent": "AI-HR-Platform-Webhook/1.0"
        }
        
        # Add signature if secret provided
        if webhook_test.secret:
            payload_str = json.dumps(payload, separators=(',', ':'))
            signature = hmac.new(
                webhook_test.secret.encode(),
                payload_str.encode(),
                hashlib.sha256
            ).hexdigest()
            headers["X-Webhook-Signature"] = f"sha256={signature}"
        
        # Send webhook (with timeout)
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(
                webhook_test.webhook_url,
                json=payload,
                headers=headers
            )
        
        return {
            "success": True,
            "status_code": response.status_code,
            "response_headers": dict(response.headers),
            "response_body": response.text[:1000],  # Limit response size
            "delivery_time_ms": response.elapsed.total_seconds() * 1000
        }
        
    except httpx.TimeoutException:
        return {
            "success": False,
            "error": "Webhook request timed out",
            "error_type": "timeout"
        }
    except httpx.RequestError as e:
        return {
            "success": False,
            "error": str(e),
            "error_type": "request_error"
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "error_type": "unknown"
        }


@router.get("/api-examples")
async def get_api_examples():
    """Get comprehensive API usage examples"""
    
    from ..api_docs import generate_api_examples
    return generate_api_examples()


@router.get("/rate-limits")
async def get_rate_limit_info(
    current_user: User = Depends(get_current_user)
):
    """Get current rate limit information for the user"""
    
    rate_limit_service = RateLimitService()
    
    # Get rate limit info (mock data for demo)
    return {
        "current_limits": {
            "requests_per_hour": 1000,
            "requests_per_minute": 100,
            "concurrent_requests": 10
        },
        "current_usage": {
            "requests_this_hour": 45,
            "requests_this_minute": 2,
            "concurrent_requests": 1
        },
        "reset_times": {
            "hourly_reset": (datetime.now() + timedelta(minutes=23)).isoformat(),
            "minute_reset": (datetime.now() + timedelta(seconds=45)).isoformat()
        },
        "upgrade_options": {
            "premium": {
                "requests_per_hour": 10000,
                "requests_per_minute": 1000,
                "concurrent_requests": 50
            },
            "enterprise": {
                "requests_per_hour": "unlimited",
                "requests_per_minute": 10000,
                "concurrent_requests": 200
            }
        }
    }


@router.get("/health")
async def developer_tools_health():
    """Health check for developer tools"""
    
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "services": {
            "sandbox": "operational",
            "webhook_testing": "operational",
            "rate_limiting": "operational",
            "api_documentation": "operational"
        }
    }