# AI-HR Platform API Documentation

## Overview

The AI-HR Platform API is a comprehensive RESTful API that powers the next generation of recruitment technology. Built with FastAPI and leveraging cutting-edge AI/ML technologies, it provides endpoints for user management, AI-powered assessments, video interviews, job matching, and real-time analytics.

## Base URL

- **Production**: `https://api.aihr-platform.com`
- **Staging**: `https://staging-api.aihr-platform.com`
- **Development**: `http://localhost:8000`

## API Versioning

The API supports versioning through multiple methods:

### Version Header (Recommended)
```http
API-Version: 1.1
```

### Accept Header
```http
Accept: application/vnd.aihr.v1.1+json
```

### Query Parameter
```http
GET /api/users/profile?version=1.1
```

### URL Path
```http
GET /api/v1.1/users/profile
```

### Supported Versions

- **v1.1** (Current) - Latest features and improvements
- **v1.0** (Deprecated) - Legacy version, sunset date: 2024-12-31

## Authentication

The API uses JWT Bearer tokens for authentication:

```http
Authorization: Bearer <your_jwt_token>
```

### Getting Started

1. **Register a new account**:
```bash
curl -X POST https://api.aihr-platform.com/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "developer@example.com",
    "password": "SecurePassword123!",
    "first_name": "John",
    "last_name": "Developer",
    "user_type": "candidate"
  }'
```

2. **Login to get tokens**:
```bash
curl -X POST https://api.aihr-platform.com/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "developer@example.com",
    "password": "SecurePassword123!"
  }'
```

3. **Use the access token**:
```bash
curl -X GET https://api.aihr-platform.com/api/users/profile \
  -H "Authorization: Bearer <access_token>"
```

## Rate Limiting

API endpoints are rate limited to ensure fair usage:

- **Default**: 1000 requests per hour per IP
- **Authenticated users**: Higher limits based on subscription
- **Premium users**: Custom rate limits available

Rate limit headers are included in responses:
```http
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 999
X-RateLimit-Reset: 1640995200
```

## Core Endpoints

### Authentication
- `POST /api/auth/register` - Register new user
- `POST /api/auth/login` - User login
- `POST /api/auth/refresh` - Refresh access token
- `POST /api/auth/logout` - User logout

### Assessments
- `POST /api/assessments/start` - Start new assessment
- `GET /api/assessments/{id}` - Get assessment details
- `POST /api/assessments/{id}/submit` - Submit assessment response
- `POST /api/assessments/{id}/complete` - Complete assessment

### Job Matching
- `GET /api/matching/recommendations` - Get job recommendations
- `GET /api/matching/score/{job_id}` - Get match score for job
- `POST /api/matching/feedback` - Provide matching feedback

### Interviews
- `POST /api/interviews/schedule` - Schedule interview
- `GET /api/interviews/{id}/join` - Join interview session
- `GET /api/interviews/{id}/results` - Get interview results

### Webhooks
- `POST /api/webhooks` - Create webhook endpoint
- `GET /api/webhooks` - List webhooks
- `PUT /api/webhooks/{id}` - Update webhook
- `DELETE /api/webhooks/{id}` - Delete webhook

## Developer Tools

### Interactive Sandbox

Access the interactive API sandbox at:
```
https://api.aihr-platform.com/api/developer/sandbox
```

The sandbox provides:
- Interactive API testing interface
- Real-time request/response inspection
- Code generation for multiple languages
- Pre-built examples for common use cases

### API Usage Analytics

Monitor your API usage:
```bash
curl -X GET https://api.aihr-platform.com/api/developer/usage-stats \
  -H "Authorization: Bearer <access_token>"
```

Response:
```json
{
  "total_requests": 1250,
  "requests_by_endpoint": {
    "/api/auth/login": 45,
    "/api/assessments/start": 120
  },
  "average_response_time": 245.5,
  "error_rate": 0.02,
  "rate_limit_hits": 3
}
```

## SDKs and Client Libraries

### Python SDK
```bash
pip install aihr-platform-sdk
```

```python
from aihr_platform_sdk import AIHRClient

client = AIHRClient(api_key="your_api_key")
user = await client.auth.login("user@example.com", "password")
assessment = await client.assessments.start("technical")
```

### JavaScript/Node.js SDK
```bash
npm install @aihr/platform-sdk
```

```javascript
import { AIHRClient } from '@aihr/platform-sdk';

const client = new AIHRClient({
  apiKey: 'your_api_key'
});

const loginResponse = await client.auth.login('user@example.com', 'password');
const assessment = await client.assessments.start({ assessmentType: 'technical' });
```

### Java SDK
```xml
<dependency>
  <groupId>com.aihr</groupId>
  <artifactId>platform-sdk</artifactId>
  <version>1.0.0</version>
</dependency>
```

### .NET SDK
```bash
dotnet add package AIHR.Platform.SDK
```

## Webhooks

### Supported Events

- `user.registered` - New user registration
- `user.verified` - Email verification completed
- `assessment.started` - Assessment session started
- `assessment.completed` - Assessment completed
- `interview.scheduled` - Interview scheduled
- `interview.completed` - Interview completed
- `job.posted` - New job posting
- `job.application` - Job application submitted
- `match.found` - AI found a good match
- `notification.sent` - Notification delivered

### Webhook Security

Webhooks are secured with HMAC-SHA256 signatures:

```javascript
const crypto = require('crypto');

function verifyWebhook(payload, signature, secret) {
  const expectedSignature = crypto
    .createHmac('sha256', secret)
    .update(payload)
    .digest('hex');
  
  return `sha256=${expectedSignature}` === signature;
}
```

### Example Webhook Payload

```json
{
  "id": "evt_123456789",
  "event_type": "assessment.completed",
  "timestamp": "2024-01-01T12:00:00Z",
  "data": {
    "assessment_id": "assess_123456789",
    "candidate_id": "user_123456789",
    "score": 0.85,
    "completed_at": "2024-01-01T12:00:00Z"
  }
}
```

## Error Handling

### Standard Error Response

```json
{
  "detail": "Error description",
  "error_code": "ERROR_CODE",
  "timestamp": "2024-01-01T12:00:00Z",
  "request_id": "req_123456789"
}
```

### HTTP Status Codes

- `200` - Success
- `201` - Created
- `400` - Bad Request
- `401` - Unauthorized
- `403` - Forbidden
- `404` - Not Found
- `422` - Validation Error
- `429` - Rate Limit Exceeded
- `500` - Internal Server Error

### Error Codes

- `VALIDATION_ERROR` - Request validation failed
- `UNAUTHORIZED` - Authentication required
- `FORBIDDEN` - Insufficient permissions
- `NOT_FOUND` - Resource not found
- `RATE_LIMIT_EXCEEDED` - Too many requests
- `INTERNAL_ERROR` - Server error

## Best Practices

### 1. Use Appropriate HTTP Methods
- `GET` for retrieving data
- `POST` for creating resources
- `PUT` for updating resources
- `DELETE` for removing resources

### 2. Handle Rate Limits
```python
import time
from aihr_platform_sdk.exceptions import RateLimitError

try:
    response = await client.request(...)
except RateLimitError as e:
    time.sleep(e.retry_after)
    response = await client.request(...)  # Retry
```

### 3. Implement Webhook Verification
Always verify webhook signatures to ensure authenticity.

### 4. Use Pagination
For endpoints that return lists, use pagination parameters:
```http
GET /api/jobs/search?limit=20&offset=40
```

### 5. Cache Responses
Cache API responses when appropriate to reduce API calls.

## Support and Resources

- **Documentation**: https://docs.aihr-platform.com
- **Developer Portal**: https://developers.aihr-platform.com
- **API Status**: https://status.aihr-platform.com
- **Support**: support@aihr-platform.com
- **GitHub**: https://github.com/aihr-platform

## Changelog

### v1.1.0 (Current)
- Added video interview endpoints
- Enhanced job matching with ML
- Webhook system implementation
- Developer sandbox and tools
- Improved error handling

### v1.0.0 (Deprecated)
- Initial API release
- Basic authentication
- Assessment system
- Job matching algorithms
- Core analytics

---

For more detailed information, visit our [interactive API documentation](https://api.aihr-platform.com/docs) or explore the [developer sandbox](https://api.aihr-platform.com/api/developer/sandbox).