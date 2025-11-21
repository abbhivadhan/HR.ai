from fastapi import FastAPI, Request, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from .api.auth import router as auth_router
from .api.assessments import router as assessments_router
from .api.job_matching import router as job_matching_router
from .api.dashboard import router as dashboard_router
from .api.security import router as security_router
from .api.analytics import router as analytics_router
from .api.notifications import router as notifications_router
from .api.ml_training import router as ml_training_router
from .api.developer_tools import router as developer_tools_router
from .api.webhooks import router as webhooks_router
from .api.career_coach import router as career_coach_router
from .api.portfolio import router as portfolio_router
from .api.scheduling import router as scheduling_router
from .api.resume_builder import router as resume_builder_router
from .api.advanced_features import router as advanced_features_router
from .database import engine, Base, get_db
from .services.security_monitoring_service import SecurityMonitoringService
from .services.rate_limit_service import RateLimitService
from .config import settings
from .api_docs import setup_api_docs
from .versioning import version_manager, get_api_version, add_version_headers
from .monitoring import monitor, HealthChecker, get_metrics_endpoint, health_endpoint, readiness_endpoint
import time

# Create database tables (optional for testing)
try:
    Base.metadata.create_all(bind=engine)
except Exception as e:
    print(f"Warning: Could not create database tables: {e}")
    print("This is expected if database is not running during import testing")

# Initialize rate limiter
limiter = Limiter(
    key_func=get_remote_address,
    storage_uri=settings.redis_url,
    default_limits=["1000/hour"]
)

app = FastAPI(
    title="AI-HR Platform API",
    description="AI-powered HR platform for modern recruitment",
    version="1.1.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Setup enhanced API documentation
setup_api_docs(app)

# Add rate limiting middleware
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.add_middleware(SlowAPIMiddleware)

# Security middleware (simplified for development)
@app.middleware("http")
async def security_middleware(request: Request, call_next):
    """Simplified security middleware for development"""
    start_time = time.time()
    
    try:
        # Process the request
        response = await call_next(request)
        
        # Add basic security headers
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        
        # Log response time for monitoring
        process_time = time.time() - start_time
        response.headers["X-Process-Time"] = str(process_time)
        
        return response
        
    except Exception as e:
        # Log security middleware errors
        print(f"Security middleware error: {str(e)}")
        response = await call_next(request)
        return response

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth_router, prefix="/api")
app.include_router(assessments_router, prefix="/api")
app.include_router(job_matching_router)
app.include_router(dashboard_router, prefix="/api")
app.include_router(security_router)
app.include_router(analytics_router, prefix="/api")
app.include_router(notifications_router, prefix="/api")
app.include_router(ml_training_router)
app.include_router(developer_tools_router)
app.include_router(webhooks_router)
# Phase 1 routers
app.include_router(career_coach_router)
app.include_router(portfolio_router)
app.include_router(scheduling_router)
app.include_router(resume_builder_router)
# Advanced features router
app.include_router(advanced_features_router)

@app.get("/")
async def root():
    return {"message": "AI-HR Platform API is running"}

@app.get("/health")
async def health_check():
    """Simple health check endpoint"""
    return {"status": "healthy", "message": "AI-HR Platform API is running"}

@app.get("/ready")
async def readiness_check():
    """Simple readiness check endpoint"""
    return {"status": "ready", "message": "AI-HR Platform API is ready"}

@app.get("/metrics")
async def metrics():
    """Simple metrics endpoint"""
    return {"status": "ok", "message": "Metrics endpoint"}

@app.middleware("http")
async def monitoring_middleware(request: Request, call_next):
    """Simple monitoring middleware"""
    response = await call_next(request)
    return response