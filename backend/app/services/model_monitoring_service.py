"""
Model Performance Monitoring Service

This service provides real-time monitoring of AI model performance,
alerting, and automated response to performance issues.
"""

import json
import numpy as np
import pandas as pd
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
from pathlib import Path
import logging
from dataclasses import dataclass, asdict
from enum import Enum
import asyncio
from collections import defaultdict, deque

from sqlalchemy.orm import Session
from ..models.assessment import Assessment, AssessmentResponse
from .ml_training_service import ModelType
from .model_versioning_service import ModelVersioningService, DeploymentStatus


class AlertSeverity(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class MetricType(str, Enum):
    ACCURACY = "accuracy"
    LATENCY = "latency"
    THROUGHPUT = "throughput"
    ERROR_RATE = "error_rate"
    DRIFT = "drift"
    BIAS = "bias"


@dataclass
class PerformanceMetric:
    metric_type: MetricType
    value: float
    timestamp: datetime
    model_type: ModelType
    model_version: str
    metadata: Dict[str, Any] = None


@dataclass
class Alert:
    alert_id: str
    severity: AlertSeverity
    metric_type: MetricType
    model_type: ModelType
    message: str
    value: float
    threshold: float
    timestamp: datetime
    resolved: bool = False
    resolved_at: Optional[datetime] = None


@dataclass
class MonitoringConfig:
    model_type: ModelType
    metrics_to_monitor: List[MetricType]
    accuracy_threshold: float = 0.7
    latency_threshold_ms: float = 1000.0
    error_rate_threshold: float = 0.05
    drift_threshold: float = 0.1
    bias_threshold: float = 0.1
    alert_window_minutes: int = 15
    min_samples_for_alert: int = 10


class ModelMonitoringService:
    def __init__(self, db: Session):
        self.db = db
        self.logger = logging.getLogger(__name__)
        
        # Storage
        self.monitoring_dir = Path("monitoring")
        self.monitoring_dir.mkdir(exist_ok=True)
        
        self.metrics_file = self.monitoring_dir / "metrics.jsonl"
        self.alerts_file = self.monitoring_dir / "alerts.jsonl"
        
        # In-memory storage for real-time monitoring
        self.metrics_buffer = defaultdict(lambda: deque(maxlen=1000))
        self.active_alerts = {}
        
        # Services
        self.versioning_service = ModelVersioningService(db)
        
        # Monitoring configurations
        self.monitoring_configs = {}
        
        # Background monitoring task
        self.monitoring_task = None
    
    def start_monitoring(self, config: MonitoringConfig):
        """Start monitoring for a model type"""
        
        self.logger.info(f"Starting monitoring for {config.model_type}")
        
        self.monitoring_configs[config.model_type] = config
        
        # Start background monitoring if not already running
        if not self.monitoring_task or self.monitoring_task.done():
            self.monitoring_task = asyncio.create_task(self._monitoring_loop())
    
    def stop_monitoring(self, model_type: ModelType):
        """Stop monitoring for a model type"""
        
        self.logger.info(f"Stopping monitoring for {model_type}")
        
        if model_type in self.monitoring_configs:
            del self.monitoring_configs[model_type]
        
        # Stop background task if no models are being monitored
        if not self.monitoring_configs and self.monitoring_task:
            self.monitoring_task.cancel()
    
    def record_prediction_metrics(self, 
                                 model_type: ModelType, 
                                 model_version: str,
                                 prediction_time_ms: float,
                                 prediction_accuracy: Optional[float] = None,
                                 error_occurred: bool = False,
                                 metadata: Dict[str, Any] = None):
        """Record metrics from a model prediction"""
        
        timestamp = datetime.utcnow()
        
        # Record latency
        latency_metric = PerformanceMetric(
            metric_type=MetricType.LATENCY,
            value=prediction_time_ms,
            timestamp=timestamp,
            model_type=model_type,
            model_version=model_version,
            metadata=metadata
        )
        self._store_metric(latency_metric)
        
        # Record accuracy if available
        if prediction_accuracy is not None:
            accuracy_metric = PerformanceMetric(
                metric_type=MetricType.ACCURACY,
                value=prediction_accuracy,
                timestamp=timestamp,
                model_type=model_type,
                model_version=model_version,
                metadata=metadata
            )
            self._store_metric(accuracy_metric)
        
        # Record error if occurred
        if error_occurred:
            error_metric = PerformanceMetric(
                metric_type=MetricType.ERROR_RATE,
                value=1.0,  # Error occurred
                timestamp=timestamp,
                model_type=model_type,
                model_version=model_version,
                metadata=metadata
            )
            self._store_metric(error_metric)
        
        # Check for alerts
        asyncio.create_task(self._check_alerts(model_type))
    
    def get_performance_summary(self, 
                               model_type: ModelType, 
                               hours_back: int = 24) -> Dict[str, Any]:
        """Get performance summary for a model"""
        
        cutoff_time = datetime.utcnow() - timedelta(hours=hours_back)
        
        # Get metrics from buffer and file
        metrics = self._get_metrics(model_type, cutoff_time)
        
        if not metrics:
            return {
                "model_type": model_type,
                "period_hours": hours_back,
                "total_predictions": 0,
                "metrics": {}
            }
        
        # Calculate summary statistics
        summary = {
            "model_type": model_type,
            "period_hours": hours_back,
            "total_predictions": len(metrics),
            "metrics": {}
        }
        
        # Group metrics by type
        metrics_by_type = defaultdict(list)
        for metric in metrics:
            metrics_by_type[metric.metric_type].append(metric.value)
        
        # Calculate statistics for each metric type
        for metric_type, values in metrics_by_type.items():
            if values:
                summary["metrics"][metric_type] = {
                    "count": len(values),
                    "mean": float(np.mean(values)),
                    "median": float(np.median(values)),
                    "std": float(np.std(values)),
                    "min": float(np.min(values)),
                    "max": float(np.max(values)),
                    "p95": float(np.percentile(values, 95)),
                    "p99": float(np.percentile(values, 99))
                }
        
        # Add trend analysis
        summary["trends"] = self._calculate_trends(metrics_by_type, hours_back)
        
        return summary
    
    def get_active_alerts(self, model_type: Optional[ModelType] = None) -> List[Alert]:
        """Get active alerts"""
        
        alerts = []
        
        for alert_key, alert in self.active_alerts.items():
            if not alert.resolved and (not model_type or alert.model_type == model_type):
                alerts.append(alert)
        
        return sorted(alerts, key=lambda a: a.timestamp, reverse=True)
    
    def resolve_alert(self, alert_id: str) -> bool:
        """Resolve an alert"""
        
        for alert_key, alert in self.active_alerts.items():
            if alert.alert_id == alert_id:
                alert.resolved = True
                alert.resolved_at = datetime.utcnow()
                
                # Log resolution
                self._log_alert(alert)
                
                self.logger.info(f"Resolved alert {alert_id}")
                return True
        
        return False
    
    def detect_model_drift(self, model_type: ModelType, days_back: int = 7) -> Dict[str, Any]:
        """Detect model drift over time"""
        
        self.logger.info(f"Detecting drift for {model_type} over {days_back} days")
        
        try:
            # Get recent metrics
            cutoff_time = datetime.utcnow() - timedelta(days=days_back)
            metrics = self._get_metrics(model_type, cutoff_time)
            
            if len(metrics) < 50:  # Minimum samples for drift detection
                return {
                    "model_type": model_type,
                    "drift_detected": False,
                    "error": "Insufficient data for drift detection",
                    "samples": len(metrics)
                }
            
            # Group metrics by day
            daily_metrics = defaultdict(lambda: defaultdict(list))
            
            for metric in metrics:
                day = metric.timestamp.date()
                daily_metrics[day][metric.metric_type].append(metric.value)
            
            # Calculate daily averages
            daily_averages = {}
            for day, metrics_by_type in daily_metrics.items():
                daily_averages[day] = {}
                for metric_type, values in metrics_by_type.items():
                    if values:
                        daily_averages[day][metric_type] = np.mean(values)
            
            # Detect drift using statistical tests
            drift_results = {
                "model_type": model_type,
                "period_days": days_back,
                "drift_detected": False,
                "drift_metrics": {},
                "recommendations": []
            }
            
            # Check accuracy drift
            accuracy_values = []
            for day_metrics in daily_averages.values():
                if MetricType.ACCURACY in day_metrics:
                    accuracy_values.append(day_metrics[MetricType.ACCURACY])
            
            if len(accuracy_values) >= 3:
                # Simple trend analysis
                accuracy_trend = np.polyfit(range(len(accuracy_values)), accuracy_values, 1)[0]
                
                drift_results["drift_metrics"]["accuracy_trend"] = float(accuracy_trend)
                
                if accuracy_trend < -0.01:  # Declining accuracy
                    drift_results["drift_detected"] = True
                    drift_results["recommendations"].append("Accuracy is declining over time")
            
            # Check latency drift
            latency_values = []
            for day_metrics in daily_averages.values():
                if MetricType.LATENCY in day_metrics:
                    latency_values.append(day_metrics[MetricType.LATENCY])
            
            if len(latency_values) >= 3:
                latency_trend = np.polyfit(range(len(latency_values)), latency_values, 1)[0]
                
                drift_results["drift_metrics"]["latency_trend"] = float(latency_trend)
                
                if latency_trend > 10:  # Increasing latency
                    drift_results["drift_detected"] = True
                    drift_results["recommendations"].append("Response latency is increasing")
            
            return drift_results
            
        except Exception as e:
            self.logger.error(f"Drift detection failed: {str(e)}")
            return {
                "model_type": model_type,
                "drift_detected": False,
                "error": str(e)
            }
    
    def generate_monitoring_report(self, model_type: ModelType, days_back: int = 7) -> Dict[str, Any]:
        """Generate comprehensive monitoring report"""
        
        self.logger.info(f"Generating monitoring report for {model_type}")
        
        # Get performance summary
        performance_summary = self.get_performance_summary(model_type, days_back * 24)
        
        # Get drift analysis
        drift_analysis = self.detect_model_drift(model_type, days_back)
        
        # Get recent alerts
        recent_alerts = self._get_recent_alerts(model_type, days_back)
        
        # Get model version info
        current_version = self.versioning_service.get_latest_version(
            model_type, DeploymentStatus.PRODUCTION
        )
        
        report = {
            "model_type": model_type,
            "report_period_days": days_back,
            "generated_at": datetime.utcnow().isoformat(),
            "current_version": {
                "version_id": current_version.version_id if current_version else None,
                "version_number": current_version.version_number if current_version else None,
                "deployed_at": current_version.created_at.isoformat() if current_version else None
            },
            "performance_summary": performance_summary,
            "drift_analysis": drift_analysis,
            "alerts_summary": {
                "total_alerts": len(recent_alerts),
                "critical_alerts": len([a for a in recent_alerts if a.severity == AlertSeverity.CRITICAL]),
                "unresolved_alerts": len([a for a in recent_alerts if not a.resolved])
            },
            "recommendations": []
        }
        
        # Generate recommendations
        if drift_analysis.get("drift_detected"):
            report["recommendations"].extend(drift_analysis.get("recommendations", []))
        
        if performance_summary["metrics"].get(MetricType.ACCURACY, {}).get("mean", 1.0) < 0.7:
            report["recommendations"].append("Model accuracy is below acceptable threshold")
        
        if performance_summary["metrics"].get(MetricType.LATENCY, {}).get("p95", 0) > 1000:
            report["recommendations"].append("95th percentile latency exceeds 1 second")
        
        if not report["recommendations"]:
            report["recommendations"].append("Model performance is within acceptable ranges")
        
        return report
    
    async def _monitoring_loop(self):
        """Background monitoring loop"""
        
        self.logger.info("Starting monitoring loop")
        
        try:
            while self.monitoring_configs:
                # Check alerts for all monitored models
                for model_type in list(self.monitoring_configs.keys()):
                    try:
                        await self._check_alerts(model_type)
                        await self._check_drift(model_type)
                    except Exception as e:
                        self.logger.error(f"Error monitoring {model_type}: {str(e)}")
                
                # Wait before next check
                await asyncio.sleep(60)  # Check every minute
                
        except asyncio.CancelledError:
            self.logger.info("Monitoring loop cancelled")
        except Exception as e:
            self.logger.error(f"Monitoring loop error: {str(e)}")
    
    def _store_metric(self, metric: PerformanceMetric):
        """Store a performance metric"""
        
        # Add to in-memory buffer
        self.metrics_buffer[metric.model_type].append(metric)
        
        # Persist to file
        metric_record = asdict(metric)
        metric_record['timestamp'] = metric.timestamp.isoformat()
        
        with open(self.metrics_file, 'a') as f:
            f.write(json.dumps(metric_record) + '\n')
    
    def _get_metrics(self, model_type: ModelType, since: datetime) -> List[PerformanceMetric]:
        """Get metrics for a model type since a given time"""
        
        metrics = []
        
        # Get from in-memory buffer
        for metric in self.metrics_buffer[model_type]:
            if metric.timestamp >= since:
                metrics.append(metric)
        
        # Get from file if buffer doesn't have enough history
        if not metrics or min(m.timestamp for m in metrics) > since:
            try:
                with open(self.metrics_file, 'r') as f:
                    for line in f:
                        record = json.loads(line.strip())
                        
                        if (record['model_type'] == model_type and 
                            datetime.fromisoformat(record['timestamp']) >= since):
                            
                            metric = PerformanceMetric(
                                metric_type=MetricType(record['metric_type']),
                                value=record['value'],
                                timestamp=datetime.fromisoformat(record['timestamp']),
                                model_type=ModelType(record['model_type']),
                                model_version=record['model_version'],
                                metadata=record.get('metadata')
                            )
                            metrics.append(metric)
            except FileNotFoundError:
                pass
        
        return sorted(metrics, key=lambda m: m.timestamp)
    
    async def _check_alerts(self, model_type: ModelType):
        """Check for alert conditions"""
        
        config = self.monitoring_configs.get(model_type)
        if not config:
            return
        
        # Get recent metrics
        window_start = datetime.utcnow() - timedelta(minutes=config.alert_window_minutes)
        recent_metrics = self._get_metrics(model_type, window_start)
        
        if len(recent_metrics) < config.min_samples_for_alert:
            return
        
        # Group metrics by type
        metrics_by_type = defaultdict(list)
        for metric in recent_metrics:
            metrics_by_type[metric.metric_type].append(metric.value)
        
        # Check accuracy threshold
        if (MetricType.ACCURACY in config.metrics_to_monitor and 
            MetricType.ACCURACY in metrics_by_type):
            
            accuracy_values = metrics_by_type[MetricType.ACCURACY]
            avg_accuracy = np.mean(accuracy_values)
            
            if avg_accuracy < config.accuracy_threshold:
                await self._create_alert(
                    model_type=model_type,
                    metric_type=MetricType.ACCURACY,
                    value=avg_accuracy,
                    threshold=config.accuracy_threshold,
                    severity=AlertSeverity.HIGH,
                    message=f"Model accuracy ({avg_accuracy:.3f}) below threshold ({config.accuracy_threshold})"
                )
        
        # Check latency threshold
        if (MetricType.LATENCY in config.metrics_to_monitor and 
            MetricType.LATENCY in metrics_by_type):
            
            latency_values = metrics_by_type[MetricType.LATENCY]
            p95_latency = np.percentile(latency_values, 95)
            
            if p95_latency > config.latency_threshold_ms:
                await self._create_alert(
                    model_type=model_type,
                    metric_type=MetricType.LATENCY,
                    value=p95_latency,
                    threshold=config.latency_threshold_ms,
                    severity=AlertSeverity.MEDIUM,
                    message=f"95th percentile latency ({p95_latency:.1f}ms) exceeds threshold ({config.latency_threshold_ms}ms)"
                )
        
        # Check error rate
        if (MetricType.ERROR_RATE in config.metrics_to_monitor and 
            MetricType.ERROR_RATE in metrics_by_type):
            
            error_values = metrics_by_type[MetricType.ERROR_RATE]
            error_rate = np.mean(error_values)
            
            if error_rate > config.error_rate_threshold:
                await self._create_alert(
                    model_type=model_type,
                    metric_type=MetricType.ERROR_RATE,
                    value=error_rate,
                    threshold=config.error_rate_threshold,
                    severity=AlertSeverity.CRITICAL,
                    message=f"Error rate ({error_rate:.3f}) exceeds threshold ({config.error_rate_threshold})"
                )
    
    async def _check_drift(self, model_type: ModelType):
        """Check for model drift"""
        
        config = self.monitoring_configs.get(model_type)
        if not config or MetricType.DRIFT not in config.metrics_to_monitor:
            return
        
        # Perform drift detection
        drift_results = self.detect_model_drift(model_type, days_back=1)
        
        if drift_results.get("drift_detected"):
            await self._create_alert(
                model_type=model_type,
                metric_type=MetricType.DRIFT,
                value=1.0,  # Drift detected
                threshold=0.0,
                severity=AlertSeverity.HIGH,
                message="Model drift detected - performance degrading over time"
            )
    
    async def _create_alert(self, 
                           model_type: ModelType,
                           metric_type: MetricType,
                           value: float,
                           threshold: float,
                           severity: AlertSeverity,
                           message: str):
        """Create a new alert"""
        
        # Check if similar alert already exists
        alert_key = f"{model_type}_{metric_type}_{severity}"
        
        if alert_key in self.active_alerts and not self.active_alerts[alert_key].resolved:
            return  # Don't create duplicate alerts
        
        alert = Alert(
            alert_id=f"alert_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}_{model_type}_{metric_type}",
            severity=severity,
            metric_type=metric_type,
            model_type=model_type,
            message=message,
            value=value,
            threshold=threshold,
            timestamp=datetime.utcnow()
        )
        
        self.active_alerts[alert_key] = alert
        
        # Log alert
        self._log_alert(alert)
        
        self.logger.warning(f"Alert created: {alert.message}")
        
        # In production, this would trigger notifications (email, Slack, etc.)
    
    def _log_alert(self, alert: Alert):
        """Log alert to file"""
        
        alert_record = asdict(alert)
        alert_record['timestamp'] = alert.timestamp.isoformat()
        if alert.resolved_at:
            alert_record['resolved_at'] = alert.resolved_at.isoformat()
        
        with open(self.alerts_file, 'a') as f:
            f.write(json.dumps(alert_record) + '\n')
    
    def _get_recent_alerts(self, model_type: ModelType, days_back: int) -> List[Alert]:
        """Get recent alerts for a model type"""
        
        cutoff_time = datetime.utcnow() - timedelta(days=days_back)
        alerts = []
        
        try:
            with open(self.alerts_file, 'r') as f:
                for line in f:
                    record = json.loads(line.strip())
                    
                    if (record['model_type'] == model_type and 
                        datetime.fromisoformat(record['timestamp']) >= cutoff_time):
                        
                        alert = Alert(
                            alert_id=record['alert_id'],
                            severity=AlertSeverity(record['severity']),
                            metric_type=MetricType(record['metric_type']),
                            model_type=ModelType(record['model_type']),
                            message=record['message'],
                            value=record['value'],
                            threshold=record['threshold'],
                            timestamp=datetime.fromisoformat(record['timestamp']),
                            resolved=record['resolved'],
                            resolved_at=datetime.fromisoformat(record['resolved_at']) if record.get('resolved_at') else None
                        )
                        alerts.append(alert)
        except FileNotFoundError:
            pass
        
        return alerts
    
    def _calculate_trends(self, metrics_by_type: Dict[MetricType, List[float]], hours_back: int) -> Dict[str, Any]:
        """Calculate performance trends"""
        
        trends = {}
        
        for metric_type, values in metrics_by_type.items():
            if len(values) >= 10:  # Minimum points for trend analysis
                # Simple linear trend
                x = np.arange(len(values))
                trend_slope = np.polyfit(x, values, 1)[0]
                
                trends[metric_type] = {
                    "slope": float(trend_slope),
                    "direction": "increasing" if trend_slope > 0 else "decreasing" if trend_slope < 0 else "stable",
                    "samples": len(values)
                }
        
        return trends