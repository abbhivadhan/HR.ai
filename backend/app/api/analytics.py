"""
Analytics API endpoints for AI-HR Platform

Provides comprehensive analytics and reporting endpoints including:
- Platform metrics and KPIs
- Hiring effectiveness tracking
- Candidate success insights
- Performance analytics
- A/B testing framework
- Automated report generation
"""

from fastapi import APIRouter, Depends, HTTPException, Query, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum

from ..database import get_db
from ..auth.dependencies import get_current_user
from ..models.user import User, UserType
from ..services.analytics_service import AnalyticsService, TimeRange, MetricType
from ..schemas.analytics import (
    PlatformMetricsResponse,
    HiringEffectivenessResponse,
    CandidateInsightsResponse,
    PerformanceDashboardResponse,
    AutomatedReportResponse,
    ABTestConfigRequest,
    ABTestResponse,
    ABTestResultsResponse,
    ExportRequest,
    AnalyticsFilterRequest
)

router = APIRouter(prefix="/analytics", tags=["analytics"])


# Platform Analytics Endpoints
@router.get("/platform/metrics", response_model=PlatformMetricsResponse)
async def get_platform_metrics(
    start_date: Optional[datetime] = Query(None, description="Start date for metrics"),
    end_date: Optional[datetime] = Query(None, description="End date for metrics"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get comprehensive platform metrics (Admin only)"""
    if current_user.user_type != UserType.ADMIN:
        raise HTTPException(status_code=403, detail="Admin access required")
    
    analytics_service = AnalyticsService(db)
    metrics = analytics_service.get_platform_metrics(start_date, end_date)
    
    return PlatformMetricsResponse(**metrics)


@router.get("/hiring/effectiveness", response_model=HiringEffectivenessResponse)
async def get_hiring_effectiveness(
    company_id: Optional[str] = Query(None, description="Company ID for filtering"),
    start_date: Optional[datetime] = Query(None, description="Start date for analysis"),
    end_date: Optional[datetime] = Query(None, description="End date for analysis"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get hiring effectiveness metrics"""
    # Check permissions
    if current_user.user_type == UserType.CANDIDATE:
        raise HTTPException(status_code=403, detail="Access denied")
    
    # If company user, restrict to their own data
    if current_user.user_type == UserType.COMPANY:
        company_id = str(current_user.id)
    
    analytics_service = AnalyticsService(db)
    effectiveness = analytics_service.get_hiring_effectiveness_metrics(
        company_id, start_date, end_date
    )
    
    return HiringEffectivenessResponse(**effectiveness)


@router.get("/candidates/insights", response_model=CandidateInsightsResponse)
async def get_candidate_insights(
    candidate_id: Optional[str] = Query(None, description="Specific candidate ID"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get candidate success insights"""
    # Check permissions
    if current_user.user_type == UserType.CANDIDATE:
        candidate_id = str(current_user.id)
    elif current_user.user_type == UserType.COMPANY and candidate_id:
        # Companies can only see insights for candidates who applied to their jobs
        # This would need additional validation in production
        pass
    elif current_user.user_type != UserType.ADMIN:
        raise HTTPException(status_code=403, detail="Access denied")
    
    analytics_service = AnalyticsService(db)
    insights = analytics_service.get_candidate_success_insights(candidate_id)
    
    return CandidateInsightsResponse(**insights)


@router.get("/company/performance", response_model=PerformanceDashboardResponse)
async def get_company_performance(
    company_id: Optional[str] = Query(None, description="Company ID"),
    time_range: TimeRange = Query(TimeRange.MONTHLY, description="Time range for analysis"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get company performance dashboard data"""
    # Check permissions and set company_id
    if current_user.user_type == UserType.CANDIDATE:
        raise HTTPException(status_code=403, detail="Access denied")
    elif current_user.user_type == UserType.COMPANY:
        company_id = str(current_user.id)
    elif current_user.user_type == UserType.ADMIN and not company_id:
        raise HTTPException(status_code=400, detail="Company ID required for admin users")
    
    analytics_service = AnalyticsService(db)
    performance = analytics_service.get_performance_dashboard_data(company_id, time_range)
    
    return PerformanceDashboardResponse(**performance)


# Automated Reports
@router.post("/reports/generate", response_model=AutomatedReportResponse)
async def generate_automated_report(
    report_type: str = Query(..., description="Type of report to generate"),
    entity_id: Optional[str] = Query(None, description="Entity ID (company/candidate)"),
    time_range: TimeRange = Query(TimeRange.MONTHLY, description="Time range for report"),
    background_tasks: BackgroundTasks = BackgroundTasks(),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Generate automated report"""
    # Validate permissions based on report type
    if report_type == "platform_overview" and current_user.user_type != UserType.ADMIN:
        raise HTTPException(status_code=403, detail="Admin access required")
    elif report_type == "company_performance":
        if current_user.user_type == UserType.COMPANY:
            entity_id = str(current_user.id)
        elif current_user.user_type != UserType.ADMIN:
            raise HTTPException(status_code=403, detail="Access denied")
    elif report_type == "candidate_insights":
        if current_user.user_type == UserType.CANDIDATE:
            entity_id = str(current_user.id)
    
    analytics_service = AnalyticsService(db)
    
    try:
        report = analytics_service.generate_automated_report(
            report_type, entity_id, time_range
        )
        
        # In production, you might want to generate reports in background
        # background_tasks.add_task(generate_report_async, report_config)
        
        return AutomatedReportResponse(**report)
    
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/reports/{report_id}")
async def get_report(
    report_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get generated report by ID"""
    # In production, retrieve report from database/storage
    # For now, return mock response
    return {
        "report_id": report_id,
        "status": "completed",
        "download_url": f"/analytics/reports/{report_id}/download"
    }


@router.post("/export")
async def export_analytics_data(
    export_request: ExportRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Export analytics data in various formats"""
    # Validate permissions based on data type
    if export_request.data_type == "platform" and current_user.user_type != UserType.ADMIN:
        raise HTTPException(status_code=403, detail="Admin access required")
    
    # In production, generate export file and return download link
    export_id = f"export_{int(datetime.utcnow().timestamp())}"
    
    return {
        "export_id": export_id,
        "status": "processing",
        "estimated_completion": "2-5 minutes",
        "download_url": f"/analytics/exports/{export_id}/download"
    }


# A/B Testing Framework
@router.post("/ab-tests", response_model=ABTestResponse)
async def create_ab_test(
    test_config: ABTestConfigRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create new A/B test"""
    if current_user.user_type not in [UserType.ADMIN, UserType.COMPANY]:
        raise HTTPException(status_code=403, detail="Access denied")
    
    analytics_service = AnalyticsService(db)
    test = analytics_service.create_ab_test(
        test_config.test_name,
        test_config.variants,
        test_config.target_metric,
        test_config.sample_size
    )
    
    return ABTestResponse(**test)


@router.get("/ab-tests", response_model=List[ABTestResponse])
async def list_ab_tests(
    status: Optional[str] = Query(None, description="Filter by test status"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List A/B tests"""
    if current_user.user_type not in [UserType.ADMIN, UserType.COMPANY]:
        raise HTTPException(status_code=403, detail="Access denied")
    
    # In production, retrieve from database
    # Mock response for now
    tests = [
        {
            "test_id": "ab_test_1",
            "test_name": "Job Posting Layout Test",
            "status": "active",
            "created_at": datetime.utcnow().isoformat(),
            "variants": [
                {"name": "control", "traffic_split": 50},
                {"name": "variant_a", "traffic_split": 50}
            ],
            "target_metric": "application_rate",
            "sample_size": 1000
        }
    ]
    
    return [ABTestResponse(**test) for test in tests]


@router.get("/ab-tests/{test_id}/results", response_model=ABTestResultsResponse)
async def get_ab_test_results(
    test_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get A/B test results"""
    if current_user.user_type not in [UserType.ADMIN, UserType.COMPANY]:
        raise HTTPException(status_code=403, detail="Access denied")
    
    analytics_service = AnalyticsService(db)
    results = analytics_service.get_ab_test_results(test_id)
    
    return ABTestResultsResponse(**results)


@router.patch("/ab-tests/{test_id}/stop")
async def stop_ab_test(
    test_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Stop running A/B test"""
    if current_user.user_type not in [UserType.ADMIN, UserType.COMPANY]:
        raise HTTPException(status_code=403, detail="Access denied")
    
    # In production, update test status in database
    return {"message": f"A/B test {test_id} stopped successfully"}


# Real-time Analytics
@router.get("/realtime/metrics")
async def get_realtime_metrics(
    metric_types: List[MetricType] = Query(..., description="Types of metrics to retrieve"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get real-time analytics metrics"""
    if current_user.user_type != UserType.ADMIN:
        raise HTTPException(status_code=403, detail="Admin access required")
    
    # Mock real-time data
    realtime_data = {
        "timestamp": datetime.utcnow().isoformat(),
        "metrics": {
            "active_users": 1247,
            "applications_today": 89,
            "assessments_in_progress": 23,
            "interviews_scheduled": 12,
            "system_load": 0.65,
            "response_time_ms": 145
        }
    }
    
    return realtime_data


# Analytics Configuration
@router.get("/config/dashboard")
async def get_analytics_config(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get analytics dashboard configuration"""
    # Return user-specific dashboard configuration
    config = {
        "user_id": str(current_user.id),
        "dashboard_layout": "default",
        "widgets": [
            {"type": "metrics_overview", "position": {"x": 0, "y": 0}},
            {"type": "trends_chart", "position": {"x": 1, "y": 0}},
            {"type": "recent_activity", "position": {"x": 0, "y": 1}}
        ],
        "refresh_interval": 300,  # 5 minutes
        "timezone": "UTC"
    }
    
    return config


@router.put("/config/dashboard")
async def update_analytics_config(
    config: Dict[str, Any],
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update analytics dashboard configuration"""
    # In production, save configuration to database
    return {"message": "Dashboard configuration updated successfully"}


# Health and Performance
@router.get("/health")
async def get_analytics_health():
    """Get analytics system health status"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "services": {
            "database": "healthy",
            "cache": "healthy",
            "background_jobs": "healthy"
        },
        "performance": {
            "avg_query_time_ms": 45,
            "cache_hit_rate": 0.89,
            "active_connections": 23
        }
    }


# Utility endpoints
@router.post("/refresh")
async def refresh_analytics_cache(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Refresh analytics cache"""
    if current_user.user_type != UserType.ADMIN:
        raise HTTPException(status_code=403, detail="Admin access required")
    
    # In production, trigger cache refresh
    return {"message": "Analytics cache refresh initiated"}


@router.get("/metrics/definitions")
async def get_metrics_definitions():
    """Get definitions of all available metrics"""
    definitions = {
        "hiring_rate": {
            "name": "Hiring Rate",
            "description": "Percentage of applications that result in hires",
            "formula": "(Hired Applications / Total Applications) * 100",
            "unit": "percentage"
        },
        "time_to_hire": {
            "name": "Average Time to Hire",
            "description": "Average number of days from application to hire",
            "formula": "Average(Hire Date - Application Date)",
            "unit": "days"
        },
        "application_success_rate": {
            "name": "Application Success Rate",
            "description": "Percentage of applications that progress beyond initial screening",
            "formula": "(Progressed Applications / Total Applications) * 100",
            "unit": "percentage"
        },
        "candidate_quality_score": {
            "name": "Candidate Quality Score",
            "description": "Average assessment score of candidates",
            "formula": "Average(Assessment Scores)",
            "unit": "score"
        }
    }
    
    return definitions