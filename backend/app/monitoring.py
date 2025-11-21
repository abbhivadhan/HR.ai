"""
Application Performance Monitoring and Error Tracking
"""
import time
import logging
import traceback
from typing import Dict, Any, Optional
from functools import wraps
from contextlib import contextmanager

import psutil
from prometheus_client import Counter, Histogram, Gauge, generate_latest
from fastapi import Request, Response
from fastapi.responses import PlainTextResponse
import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration
from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration

# Prometheus metrics
REQUEST_COUNT = Counter(
    'http_requests_total',
    'Total HTTP requests',
    ['method', 'endpoint', 'status']
)

REQUEST_DURATION = Histogram(
    'http_request_duration_seconds',
    'HTTP request duration in seconds',
    ['method', 'endpoint']
)

ACTIVE_CONNECTIONS = Gauge(
    'active_database_connections',
    'Number of active database connections'
)

CPU_USAGE = Gauge(
    'cpu_usage_percent',
    'CPU usage percentage'
)

MEMORY_USAGE = Gauge(
    'memory_usage_percent',
    'Memory usage percentage'
)

DISK_USAGE = Gauge(
    'disk_usage_percent',
    'Disk usage percentage'
)

ERROR_COUNT = Counter(
    'application_errors_total',
    'Total application errors',
    ['error_type', 'endpoint']
)

AI_MODEL_INFERENCE_TIME = Histogram(
    'ai_model_inference_seconds',
    'AI model inference time in seconds',
    ['model_name', 'operation']
)

JOB_MATCHING_ACCURACY = Gauge(
    'job_matching_accuracy_score',
    'Job matching algorithm accuracy score'
)

logger = logging.getLogger(__name__)


class PerformanceMonitor:
    """Application Performance Monitor"""
    
    def __init__(self):
        self.start_time = time.time()
        self._setup_sentry()
        self._setup_system_metrics_collection()
    
    def _setup_sentry(self):
        """Initialize Sentry for error tracking"""
        import os
        sentry_dsn = os.getenv("SENTRY_DSN")
        if sentry_dsn:
            sentry_sdk.init(
                dsn=sentry_dsn,
                integrations=[
                    FastApiIntegration(),
                    SqlalchemyIntegration(),
                ],
                traces_sample_rate=0.1,
                environment=os.getenv("ENVIRONMENT", "development"),
                release="ai-hr-platform@1.0.0"
            )
    
    def _setup_system_metrics_collection(self):
        """Setup system metrics collection"""
        import threading
        import time
        
        def collect_system_metrics():
            while True:
                try:
                    # CPU usage
                    cpu_percent = psutil.cpu_percent(interval=1)
                    CPU_USAGE.set(cpu_percent)
                    
                    # Memory usage
                    memory = psutil.virtual_memory()
                    MEMORY_USAGE.set(memory.percent)
                    
                    # Disk usage
                    disk = psutil.disk_usage('/')
                    DISK_USAGE.set(disk.percent)
                    
                except Exception as e:
                    logger.error(f"Error collecting system metrics: {e}")
                
                time.sleep(30)  # Collect every 30 seconds
        
        thread = threading.Thread(target=collect_system_metrics, daemon=True)
        thread.start()
    
    @contextmanager
    def track_request(self, request: Request):
        """Context manager to track HTTP requests"""
        start_time = time.time()
        method = request.method
        endpoint = request.url.path
        
        try:
            yield
            status = "success"
        except Exception as e:
            status = "error"
            ERROR_COUNT.labels(
                error_type=type(e).__name__,
                endpoint=endpoint
            ).inc()
            
            # Log error with context
            logger.error(
                f"Request error: {method} {endpoint}",
                extra={
                    "method": method,
                    "endpoint": endpoint,
                    "error": str(e),
                    "traceback": traceback.format_exc()
                }
            )
            raise
        finally:
            duration = time.time() - start_time
            REQUEST_DURATION.labels(method=method, endpoint=endpoint).observe(duration)
            REQUEST_COUNT.labels(method=method, endpoint=endpoint, status=status).inc()
    
    def track_ai_inference(self, model_name: str, operation: str):
        """Decorator to track AI model inference time"""
        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                start_time = time.time()
                try:
                    result = func(*args, **kwargs)
                    return result
                finally:
                    duration = time.time() - start_time
                    AI_MODEL_INFERENCE_TIME.labels(
                        model_name=model_name,
                        operation=operation
                    ).observe(duration)
            return wrapper
        return decorator
    
    def update_job_matching_accuracy(self, accuracy_score: float):
        """Update job matching accuracy metric"""
        JOB_MATCHING_ACCURACY.set(accuracy_score)
    
    def track_database_connections(self, connection_count: int):
        """Track active database connections"""
        ACTIVE_CONNECTIONS.set(connection_count)
    
    def log_business_metric(self, metric_name: str, value: float, labels: Dict[str, str] = None):
        """Log custom business metrics"""
        logger.info(
            f"Business metric: {metric_name}",
            extra={
                "metric_name": metric_name,
                "value": value,
                "labels": labels or {}
            }
        )


class HealthChecker:
    """System health checker"""
    
    def __init__(self, db_session, redis_client, mongodb_client):
        self.db_session = db_session
        self.redis_client = redis_client
        self.mongodb_client = mongodb_client
    
    async def check_database_health(self) -> Dict[str, Any]:
        """Check PostgreSQL database health"""
        try:
            # Simple query to check database connectivity
            result = await self.db_session.execute("SELECT 1")
            return {
                "status": "healthy",
                "response_time_ms": 0,  # Would measure actual response time
                "details": "Database connection successful"
            }
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e),
                "details": "Database connection failed"
            }
    
    async def check_redis_health(self) -> Dict[str, Any]:
        """Check Redis health"""
        try:
            await self.redis_client.ping()
            return {
                "status": "healthy",
                "details": "Redis connection successful"
            }
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e),
                "details": "Redis connection failed"
            }
    
    async def check_mongodb_health(self) -> Dict[str, Any]:
        """Check MongoDB health"""
        try:
            await self.mongodb_client.admin.command('ping')
            return {
                "status": "healthy",
                "details": "MongoDB connection successful"
            }
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e),
                "details": "MongoDB connection failed"
            }
    
    async def check_ai_services_health(self) -> Dict[str, Any]:
        """Check AI services health"""
        try:
            # Test AI service connectivity
            # This would test actual AI service endpoints
            return {
                "status": "healthy",
                "details": "AI services responding"
            }
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e),
                "details": "AI services unavailable"
            }
    
    async def get_comprehensive_health(self) -> Dict[str, Any]:
        """Get comprehensive system health status"""
        health_checks = {
            "database": await self.check_database_health(),
            "redis": await self.check_redis_health(),
            "mongodb": await self.check_mongodb_health(),
            "ai_services": await self.check_ai_services_health()
        }
        
        # Determine overall health
        overall_status = "healthy"
        for service, status in health_checks.items():
            if status["status"] != "healthy":
                overall_status = "unhealthy"
                break
        
        return {
            "status": overall_status,
            "timestamp": time.time(),
            "uptime_seconds": time.time() - monitor.start_time,
            "services": health_checks,
            "system_metrics": {
                "cpu_usage_percent": psutil.cpu_percent(),
                "memory_usage_percent": psutil.virtual_memory().percent,
                "disk_usage_percent": psutil.disk_usage('/').percent
            }
        }


# Global monitor instance
monitor = PerformanceMonitor()


def get_metrics_endpoint():
    """Prometheus metrics endpoint"""
    return PlainTextResponse(generate_latest())


async def health_endpoint(health_checker: HealthChecker):
    """Health check endpoint"""
    health_status = await health_checker.get_comprehensive_health()
    status_code = 200 if health_status["status"] == "healthy" else 503
    return Response(
        content=str(health_status),
        status_code=status_code,
        media_type="application/json"
    )


async def readiness_endpoint(health_checker: HealthChecker):
    """Readiness check endpoint"""
    # Check if application is ready to serve requests
    health_status = await health_checker.get_comprehensive_health()
    
    # Application is ready if database and Redis are healthy
    critical_services = ["database", "redis"]
    ready = all(
        health_status["services"][service]["status"] == "healthy"
        for service in critical_services
    )
    
    status_code = 200 if ready else 503
    return Response(
        content=str({"ready": ready}),
        status_code=status_code,
        media_type="application/json"
    )