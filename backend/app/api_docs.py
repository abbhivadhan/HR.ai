"""
API Documentation Configuration and Utilities

This module provides comprehensive API documentation setup with OpenAPI/Swagger,
including custom schemas, examples, and developer tools.
"""

from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi
from fastapi.openapi.docs import get_swagger_ui_html, get_redoc_html
from fastapi.staticfiles import StaticFiles
from typing import Dict, Any, Optional
import json
import os

def custom_openapi(app: FastAPI) -> Dict[str, Any]:
    """
    Generate custom OpenAPI schema with enhanced documentation
    """
    if app.openapi_schema:
        return app.openapi_schema
    
    openapi_schema = get_openapi(
        title="AI-HR Platform API",
        version="1.0.0",
        description="""
        ## AI-HR Platform API Documentation
        
        A comprehensive AI-powered HR platform that revolutionizes recruitment through:
        
        * **AI-Powered Assessments**: Dynamic skill evaluation with machine learning
        * **Video Interviews**: AI-driven interview analysis and scoring
        * **Smart Job Matching**: ML-based candidate-job compatibility
        * **Real-time Analytics**: Advanced hiring insights and metrics
        * **Security First**: Enterprise-grade security and compliance
        
        ### Authentication
        
        This API uses JWT Bearer tokens for authentication. Include the token in the Authorization header:
        ```
        Authorization: Bearer <your_jwt_token>
        ```
        
        ### Rate Limiting
        
        API endpoints are rate limited to ensure fair usage:
        - Default: 1000 requests per hour per IP
        - Authenticated users: Higher limits based on subscription
        - Premium users: Custom rate limits available
        
        ### Webhooks
        
        The platform supports webhooks for real-time integrations:
        - Job application events
        - Assessment completion notifications
        - Interview scheduling updates
        - Matching algorithm results
        
        ### SDKs Available
        
        - Python SDK: `pip install aihr-platform-sdk`
        - JavaScript/Node.js SDK: `npm install @aihr/platform-sdk`
        - Java SDK: Available via Maven Central
        - .NET SDK: Available via NuGet
        
        ### Support
        
        - Documentation: https://docs.aihr-platform.com
        - Developer Portal: https://developers.aihr-platform.com
        - Support: support@aihr-platform.com
        """,
        routes=app.routes,
        servers=[
            {"url": "https://api.aihr-platform.com", "description": "Production server"},
            {"url": "https://staging-api.aihr-platform.com", "description": "Staging server"},
            {"url": "http://localhost:8000", "description": "Development server"}
        ]
    )
    
    # Add security schemes
    openapi_schema["components"]["securitySchemes"] = {
        "BearerAuth": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT",
            "description": "JWT token obtained from /api/auth/login endpoint"
        },
        "ApiKeyAuth": {
            "type": "apiKey",
            "in": "header",
            "name": "X-API-Key",
            "description": "API key for server-to-server authentication"
        }
    }
    
    # Add global security requirement
    openapi_schema["security"] = [
        {"BearerAuth": []},
        {"ApiKeyAuth": []}
    ]
    
    # Add custom tags with descriptions
    openapi_schema["tags"] = [
        {
            "name": "Authentication",
            "description": "User authentication and authorization endpoints",
            "externalDocs": {
                "description": "Authentication Guide",
                "url": "https://docs.aihr-platform.com/auth"
            }
        },
        {
            "name": "assessments",
            "description": "AI-powered skill assessments and testing",
            "externalDocs": {
                "description": "Assessment API Guide",
                "url": "https://docs.aihr-platform.com/assessments"
            }
        },
        {
            "name": "job-matching",
            "description": "ML-based job matching and recommendations",
            "externalDocs": {
                "description": "Job Matching Guide",
                "url": "https://docs.aihr-platform.com/matching"
            }
        },
        {
            "name": "interviews",
            "description": "AI video interviews and analysis",
            "externalDocs": {
                "description": "Interview API Guide",
                "url": "https://docs.aihr-platform.com/interviews"
            }
        },
        {
            "name": "analytics",
            "description": "Platform analytics and reporting",
            "externalDocs": {
                "description": "Analytics Guide",
                "url": "https://docs.aihr-platform.com/analytics"
            }
        },
        {
            "name": "webhooks",
            "description": "Real-time event notifications",
            "externalDocs": {
                "description": "Webhook Guide",
                "url": "https://docs.aihr-platform.com/webhooks"
            }
        },
        {
            "name": "developer-tools",
            "description": "Developer utilities and sandbox",
            "externalDocs": {
                "description": "Developer Tools",
                "url": "https://developers.aihr-platform.com"
            }
        }
    ]
    
    # Add example responses
    add_example_responses(openapi_schema)
    
    app.openapi_schema = openapi_schema
    return app.openapi_schema


def add_example_responses(openapi_schema: Dict[str, Any]) -> None:
    """Add example responses to API endpoints"""
    
    # Common error responses
    error_responses = {
        "400": {
            "description": "Bad Request",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "Invalid request data",
                        "error_code": "VALIDATION_ERROR",
                        "timestamp": "2024-01-01T00:00:00Z"
                    }
                }
            }
        },
        "401": {
            "description": "Unauthorized",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "Invalid or expired token",
                        "error_code": "UNAUTHORIZED",
                        "timestamp": "2024-01-01T00:00:00Z"
                    }
                }
            }
        },
        "403": {
            "description": "Forbidden",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "Insufficient permissions",
                        "error_code": "FORBIDDEN",
                        "timestamp": "2024-01-01T00:00:00Z"
                    }
                }
            }
        },
        "429": {
            "description": "Rate Limit Exceeded",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "Rate limit exceeded. Try again later.",
                        "error_code": "RATE_LIMIT_EXCEEDED",
                        "retry_after": 3600,
                        "timestamp": "2024-01-01T00:00:00Z"
                    }
                }
            }
        },
        "500": {
            "description": "Internal Server Error",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "An unexpected error occurred",
                        "error_code": "INTERNAL_ERROR",
                        "request_id": "req_123456789",
                        "timestamp": "2024-01-01T00:00:00Z"
                    }
                }
            }
        }
    }
    
    # Add error responses to all paths
    if "paths" in openapi_schema:
        for path_data in openapi_schema["paths"].values():
            for method_data in path_data.values():
                if isinstance(method_data, dict) and "responses" in method_data:
                    method_data["responses"].update(error_responses)


def setup_api_docs(app: FastAPI) -> None:
    """Setup enhanced API documentation"""
    
    # Custom OpenAPI schema
    app.openapi = lambda: custom_openapi(app)
    
    # Create docs directory if it doesn't exist
    docs_dir = "backend/static/docs"
    os.makedirs(docs_dir, exist_ok=True)
    
    # Mount static files for custom documentation assets
    if os.path.exists("backend/static"):
        app.mount("/static", StaticFiles(directory="backend/static"), name="static")


def generate_api_examples() -> Dict[str, Any]:
    """Generate comprehensive API usage examples"""
    
    return {
        "authentication": {
            "register": {
                "request": {
                    "email": "developer@example.com",
                    "password": "SecurePassword123!",
                    "first_name": "John",
                    "last_name": "Developer",
                    "user_type": "candidate"
                },
                "response": {
                    "id": "123e4567-e89b-12d3-a456-426614174000",
                    "email": "developer@example.com",
                    "first_name": "John",
                    "last_name": "Developer",
                    "user_type": "candidate",
                    "is_verified": False,
                    "created_at": "2024-01-01T00:00:00Z"
                }
            },
            "login": {
                "request": {
                    "email": "developer@example.com",
                    "password": "SecurePassword123!"
                },
                "response": {
                    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                    "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                    "token_type": "bearer",
                    "expires_in": 3600
                }
            }
        },
        "assessments": {
            "start_assessment": {
                "request": {
                    "assessment_type": "technical",
                    "job_id": "job_123456789",
                    "difficulty_level": "intermediate"
                },
                "response": {
                    "assessment_id": "assess_123456789",
                    "session_token": "session_abc123",
                    "time_limit_minutes": 60,
                    "total_questions": 25,
                    "instructions": "Complete all questions within the time limit..."
                }
            }
        },
        "job_matching": {
            "get_recommendations": {
                "response": {
                    "recommendations": [
                        {
                            "job_id": "job_123456789",
                            "job_title": "Senior Python Developer",
                            "company_name": "TechCorp Inc.",
                            "match_score": 0.92,
                            "match_reasons": [
                                "Strong Python skills match",
                                "Experience level alignment",
                                "Location preference match"
                            ],
                            "salary_range": {
                                "min": 80000,
                                "max": 120000,
                                "currency": "USD"
                            }
                        }
                    ],
                    "total_matches": 15,
                    "page": 1,
                    "per_page": 10
                }
            }
        }
    }


def get_api_changelog() -> Dict[str, Any]:
    """Get API changelog for version tracking"""
    
    return {
        "v1.0.0": {
            "release_date": "2024-01-01",
            "changes": [
                "Initial API release",
                "Authentication endpoints",
                "Assessment system",
                "Job matching algorithms",
                "Basic analytics"
            ],
            "breaking_changes": [],
            "deprecated": []
        },
        "v1.1.0": {
            "release_date": "2024-02-01",
            "changes": [
                "Added video interview endpoints",
                "Enhanced job matching with ML",
                "Webhook system implementation",
                "Developer sandbox"
            ],
            "breaking_changes": [],
            "deprecated": []
        }
    }