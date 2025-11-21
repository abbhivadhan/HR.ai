"""
Analytics schemas for API request/response models
"""

from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any, Union
from datetime import datetime
from enum import Enum


class TimeRange(str, Enum):
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    YEARLY = "yearly"


class MetricType(str, Enum):
    PLATFORM = "platform"
    HIRING = "hiring"
    CANDIDATE = "candidate"
    COMPANY = "company"
    ENGAGEMENT = "engagement"


class ABTestStatus(str, Enum):
    DRAFT = "draft"
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


# Base metric models
class UserMetrics(BaseModel):
    total: int
    candidates: int
    companies: int
    active_in_period: int
    growth_rate: float


class JobMetrics(BaseModel):
    total: int
    active: int
    posted_in_period: int
    growth_rate: float


class ApplicationMetrics(BaseModel):
    total: int
    in_period: int
    success_rate: float
    growth_rate: float


class AssessmentMetrics(BaseModel):
    total: int
    completed: int
    completion_rate: float


class InterviewMetrics(BaseModel):
    total: int
    completed: int


# Platform metrics response
class PlatformMetricsResponse(BaseModel):
    users: UserMetrics
    jobs: JobMetrics
    applications: ApplicationMetrics
    assessments: AssessmentMetrics
    interviews: InterviewMetrics


# Hiring effectiveness models
class SourceEffectiveness(BaseModel):
    applications: int
    hires: int
    rate: float


class FunnelStage(BaseModel):
    count: int
    percentage: float


class FunnelMetrics(BaseModel):
    applied: FunnelStage
    reviewing: FunnelStage
    shortlisted: FunnelStage
    interviewed: FunnelStage
    accepted: FunnelStage
    rejected: FunnelStage


class HiringEffectivenessResponse(BaseModel):
    total_applications: int
    hiring_rate: float
    average_time_to_hire: float
    cost_per_hire: float
    quality_of_hire: float
    source_effectiveness: Dict[str, SourceEffectiveness]
    funnel_metrics: FunnelMetrics


# Candidate insights models
class SuccessMetrics(BaseModel):
    application_success_rate: float
    average_applications_per_candidate: float
    interview_conversion_rate: float


class SkillTrend(BaseModel):
    average_score: float
    improvement_trend: str
    candidate_count: int


class PerformanceDistribution(BaseModel):
    score_range: str
    count: int
    percentage: float


class CandidateInsightsResponse(BaseModel):
    total_candidates: int
    success_metrics: SuccessMetrics
    skill_trends: Dict[str, SkillTrend]
    performance_distribution: Dict[str, PerformanceDistribution]
    improvement_areas: List[str]


# Performance dashboard models
class JobPerformance(BaseModel):
    job_id: str
    title: str
    applications: int
    views: int
    application_rate: float
    status: str


class JobPostingPerformance(BaseModel):
    total_jobs: int
    performance: List[JobPerformance]


class ApplicationTrend(BaseModel):
    period: str
    applications: int


class CandidateQualityMetrics(BaseModel):
    average_score: float
    score_distribution: Dict[str, int]
    total_assessed: int


class ROIMetrics(BaseModel):
    total_hires: int
    cost_per_hire: float
    total_cost: float
    annual_benefit: float
    roi_percentage: float
    payback_period_months: float


class PeriodInfo(BaseModel):
    start_date: str
    end_date: str


class PerformanceDashboardResponse(BaseModel):
    job_performance: JobPostingPerformance
    application_trends: List[ApplicationTrend]
    hiring_metrics: HiringEffectivenessResponse
    candidate_quality: CandidateQualityMetrics
    roi_metrics: ROIMetrics
    time_range: TimeRange
    period: PeriodInfo


# Automated reports models
class AutomatedReportResponse(BaseModel):
    report_id: str
    report_type: str
    generated_at: str
    period: PeriodInfo
    data: Dict[str, Any]
    insights: List[str]
    recommendations: List[str]


# A/B Testing models
class ABTestVariant(BaseModel):
    name: str
    description: Optional[str] = None
    config: Dict[str, Any]
    traffic_split: float = Field(..., ge=0, le=100)


class ABTestConfigRequest(BaseModel):
    test_name: str
    description: Optional[str] = None
    variants: List[ABTestVariant]
    target_metric: str
    sample_size: int
    duration_days: Optional[int] = 14
    significance_level: float = Field(0.95, ge=0.8, le=0.99)


class ABTestResponse(BaseModel):
    test_id: str
    test_name: str
    description: Optional[str] = None
    status: ABTestStatus
    created_at: str
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    variants: List[ABTestVariant]
    target_metric: str
    sample_size: int
    current_participants: Optional[int] = None


class ABTestVariantResult(BaseModel):
    name: str
    participants: int
    conversion_rate: float
    confidence_interval: List[float]
    statistical_power: Optional[float] = None


class StatisticalSignificance(BaseModel):
    p_value: float
    confidence_level: float
    is_significant: bool
    winner: Optional[str] = None
    improvement: Optional[float] = None


class ABTestResultsResponse(BaseModel):
    test_id: str
    status: ABTestStatus
    duration_days: int
    participants: int
    variants: List[ABTestVariantResult]
    statistical_significance: StatisticalSignificance
    recommendations: List[str]


# Export and filtering models
class AnalyticsFilterRequest(BaseModel):
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    metrics: Optional[List[str]] = None
    group_by: Optional[str] = None
    filters: Optional[Dict[str, Any]] = None


class ExportRequest(BaseModel):
    data_type: str
    format: str = Field(..., pattern="^(csv|pdf|xlsx|json)$")
    filters: Optional[AnalyticsFilterRequest] = None
    include_charts: bool = False
    email_delivery: bool = False


class ExportResponse(BaseModel):
    export_id: str
    status: str
    estimated_completion: str
    download_url: Optional[str] = None


# Real-time analytics models
class RealTimeMetric(BaseModel):
    name: str
    value: Union[int, float, str]
    unit: Optional[str] = None
    trend: Optional[str] = None  # "up", "down", "stable"
    change_percentage: Optional[float] = None


class RealTimeMetricsResponse(BaseModel):
    timestamp: str
    metrics: Dict[str, Union[int, float, str]]
    alerts: Optional[List[str]] = None


# Dashboard configuration models
class WidgetConfig(BaseModel):
    type: str
    title: str
    position: Dict[str, int]
    size: Dict[str, int]
    config: Dict[str, Any]
    refresh_interval: Optional[int] = None


class DashboardConfig(BaseModel):
    user_id: str
    dashboard_layout: str
    widgets: List[WidgetConfig]
    refresh_interval: int
    timezone: str
    theme: Optional[str] = "light"


class DashboardConfigRequest(BaseModel):
    dashboard_layout: str
    widgets: List[WidgetConfig]
    refresh_interval: int = Field(300, ge=60, le=3600)  # 1 minute to 1 hour
    timezone: str = "UTC"
    theme: str = "light"


# Notification models
class AnalyticsAlert(BaseModel):
    id: str
    type: str  # "threshold", "anomaly", "trend"
    title: str
    message: str
    severity: str  # "low", "medium", "high", "critical"
    timestamp: datetime
    metric: str
    current_value: Union[int, float]
    threshold_value: Optional[Union[int, float]] = None
    resolved: bool = False


class AlertRule(BaseModel):
    id: str
    name: str
    metric: str
    condition: str  # "greater_than", "less_than", "equals", "change_percentage"
    threshold: Union[int, float]
    enabled: bool = True
    notification_channels: List[str] = ["email", "dashboard"]


class AlertRuleRequest(BaseModel):
    name: str
    metric: str
    condition: str
    threshold: Union[int, float]
    notification_channels: List[str] = ["email", "dashboard"]


# Benchmark and comparison models
class BenchmarkData(BaseModel):
    metric: str
    industry_average: float
    top_quartile: float
    your_value: float
    percentile: float
    performance_rating: str  # "excellent", "good", "average", "below_average"


class CompetitorComparison(BaseModel):
    metric: str
    your_value: float
    competitor_average: float
    market_leader: float
    your_rank: int
    total_competitors: int


class BenchmarkResponse(BaseModel):
    company_id: str
    industry: str
    benchmarks: List[BenchmarkData]
    competitor_comparisons: List[CompetitorComparison]
    overall_score: float
    recommendations: List[str]


# Trend analysis models
class TrendPoint(BaseModel):
    date: str
    value: float
    predicted: bool = False


class TrendAnalysis(BaseModel):
    metric: str
    trend_direction: str  # "increasing", "decreasing", "stable", "volatile"
    trend_strength: float  # 0-1 scale
    data_points: List[TrendPoint]
    forecast_points: List[TrendPoint]
    seasonality_detected: bool = False
    anomalies: List[TrendPoint] = []


class TrendAnalysisRequest(BaseModel):
    metrics: List[str]
    time_range: TimeRange
    include_forecast: bool = True
    forecast_periods: int = Field(12, ge=1, le=52)  # 1-52 periods ahead


# System health and performance models
class SystemHealth(BaseModel):
    status: str
    timestamp: str
    services: Dict[str, str]
    performance: Dict[str, Union[int, float]]
    alerts: List[str] = []


class PerformanceMetrics(BaseModel):
    avg_response_time_ms: float
    throughput_requests_per_second: float
    error_rate_percentage: float
    cache_hit_rate: float
    database_connections: int
    memory_usage_percentage: float
    cpu_usage_percentage: float


# Audit and compliance models
class AnalyticsAuditLog(BaseModel):
    id: str
    user_id: str
    action: str
    resource: str
    timestamp: datetime
    ip_address: str
    user_agent: str
    details: Dict[str, Any]


class ComplianceReport(BaseModel):
    report_id: str
    generated_at: datetime
    compliance_framework: str  # "GDPR", "CCPA", "SOX", etc.
    status: str
    findings: List[str]
    recommendations: List[str]
    next_review_date: datetime


# Custom metric models
class CustomMetricDefinition(BaseModel):
    id: str
    name: str
    description: str
    formula: str
    data_sources: List[str]
    aggregation_method: str
    unit: str
    created_by: str
    created_at: datetime


class CustomMetricRequest(BaseModel):
    name: str
    description: str
    formula: str
    data_sources: List[str]
    aggregation_method: str = "sum"
    unit: str = "count"


class CustomMetricValue(BaseModel):
    metric_id: str
    timestamp: datetime
    value: float
    dimensions: Dict[str, str] = {}