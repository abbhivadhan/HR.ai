from pydantic import BaseModel
from typing import List, Optional, Dict, Any, Union
from datetime import datetime
from enum import Enum


class NotificationType(str, Enum):
    INFO = "info"
    SUCCESS = "success"
    WARNING = "warning"
    ERROR = "error"


# Base response models
class CandidateStatsResponse(BaseModel):
    total_applications: int
    matching_jobs: int
    profile_views: int
    assessments_completed: int
    average_score: float
    interviews_scheduled: int


class CandidateRecommendationResponse(BaseModel):
    id: str
    job_title: str
    company_name: str
    match_score: int
    location: str
    salary_range: str
    posted_date: datetime
    skills: List[str]


class JobPostingStatsResponse(BaseModel):
    id: str
    title: str
    status: str
    applications: int
    views: int
    posted_date: datetime
    location: str


class ApplicationStatsResponse(BaseModel):
    id: str
    candidate_name: str
    job_title: str
    status: str
    match_score: int
    applied_date: datetime


class CompanyAnalyticsResponse(BaseModel):
    job_postings: Dict[str, int]
    applications: Dict[str, int]
    candidates: Dict[str, Union[int, float, List[str]]]
    performance: Dict[str, float]


class AdminMetricsResponse(BaseModel):
    users: Dict[str, int]
    platform: Dict[str, int]
    engagement: Dict[str, float]
    revenue: Dict[str, float]


class NotificationResponse(BaseModel):
    id: str
    type: NotificationType
    title: str
    message: str
    timestamp: datetime
    read: bool
    action_url: Optional[str] = None


class ChartDataset(BaseModel):
    label: str
    data: List[Union[int, float]]
    backgroundColor: Optional[Union[str, List[str]]] = None
    borderColor: Optional[Union[str, List[str]]] = None
    borderWidth: Optional[int] = None


class ChartDataResponse(BaseModel):
    labels: List[str]
    datasets: List[ChartDataset]


class TimeSeriesDataPoint(BaseModel):
    date: str
    value: Union[int, float]


class SkillDistributionResponse(BaseModel):
    skill: str
    count: int
    percentage: float


class SystemAlertResponse(BaseModel):
    id: str
    type: str
    title: str
    description: str
    timestamp: datetime
    resolved: bool


class RecentActivityResponse(BaseModel):
    id: str
    type: str
    description: str
    timestamp: datetime
    user_id: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


# Request models
class DashboardConfigRequest(BaseModel):
    layout: Dict[str, Any]
    widgets: List[Dict[str, Any]]
    preferences: Dict[str, Any]


class NotificationPreferencesRequest(BaseModel):
    email_notifications: bool
    push_notifications: bool
    sms_notifications: bool
    notification_types: List[NotificationType]


# Analytics request models
class AnalyticsFilterRequest(BaseModel):
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    metrics: Optional[List[str]] = None
    group_by: Optional[str] = None


class ExportRequest(BaseModel):
    format: str  # 'csv' or 'pdf'
    data_type: str
    filters: Optional[AnalyticsFilterRequest] = None


# Real-time data models
class RealTimeUpdate(BaseModel):
    type: str
    data: Dict[str, Any]
    timestamp: datetime


class WebSocketMessage(BaseModel):
    event: str
    data: Dict[str, Any]
    user_id: str


# Dashboard widget models
class WidgetConfig(BaseModel):
    id: str
    type: str
    title: str
    position: Dict[str, int]
    size: Dict[str, int]
    config: Dict[str, Any]


class DashboardLayout(BaseModel):
    widgets: List[WidgetConfig]
    layout_type: str
    auto_refresh: bool
    refresh_interval: int


# Performance metrics models
class PerformanceMetrics(BaseModel):
    response_time: float
    throughput: int
    error_rate: float
    uptime: float


class SystemHealth(BaseModel):
    status: str
    cpu_usage: float
    memory_usage: float
    disk_usage: float
    active_connections: int
    performance: PerformanceMetrics


# Aggregated data models
class UserEngagementMetrics(BaseModel):
    daily_active_users: int
    weekly_active_users: int
    monthly_active_users: int
    average_session_duration: float
    bounce_rate: float
    retention_rate: float


class BusinessMetrics(BaseModel):
    total_revenue: float
    monthly_recurring_revenue: float
    customer_acquisition_cost: float
    lifetime_value: float
    churn_rate: float
    growth_rate: float


class PlatformMetrics(BaseModel):
    total_users: int
    total_jobs: int
    total_applications: int
    total_assessments: int
    total_interviews: int
    success_rate: float


# Trend analysis models
class TrendData(BaseModel):
    period: str
    value: float
    change: float
    change_percentage: float


class TrendAnalysis(BaseModel):
    metric: str
    current_value: float
    trend: str  # 'up', 'down', 'stable'
    data_points: List[TrendData]
    forecast: Optional[List[TrendData]] = None


# Comparison models
class ComparisonData(BaseModel):
    label: str
    current_period: float
    previous_period: float
    change: float
    change_percentage: float


class BenchmarkComparison(BaseModel):
    metric: str
    current_value: float
    benchmark_value: float
    performance: str  # 'above', 'below', 'at'
    percentile: float