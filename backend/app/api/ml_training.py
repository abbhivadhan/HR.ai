"""
ML Training and Optimization API Endpoints

This module provides REST API endpoints for AI model training,
evaluation, continuous learning, versioning, and monitoring.
"""

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from datetime import datetime
import uuid

from ..database import get_db
from ..auth.dependencies import get_current_user
from ..models.user import User
from ..services.ml_training_service import MLTrainingService, ModelType, TrainingConfig
from ..services.model_evaluation_service import ModelEvaluationService, ValidationConfig, ValidationMethod
from ..services.continuous_learning_service import ContinuousLearningService, FeedbackData, FeedbackType, LearningConfig, LearningStrategy
from ..services.model_versioning_service import ModelVersioningService, DeploymentConfig, DeploymentStrategy, DeploymentStatus
from ..services.model_monitoring_service import ModelMonitoringService, MonitoringConfig, MetricType, AlertSeverity
from pydantic import BaseModel


router = APIRouter(prefix="/api/ml", tags=["ML Training & Optimization"])


# Request/Response Models
class TrainingRequest(BaseModel):
    model_type: ModelType
    features: List[str] = []
    target: str = ""
    test_size: float = 0.2
    cv_folds: int = 5
    hyperparameters: Dict[str, Any] = {}


class EvaluationRequest(BaseModel):
    model_path: str
    validation_method: ValidationMethod = ValidationMethod.CROSS_VALIDATION
    n_splits: int = 5
    test_size: float = 0.2


class FeedbackRequest(BaseModel):
    assessment_id: str
    question_id: str = ""
    feedback_type: FeedbackType
    feedback_content: Dict[str, Any]
    confidence_score: float = 0.8


class LearningUpdateRequest(BaseModel):
    model_type: ModelType
    strategy: LearningStrategy = LearningStrategy.INCREMENTAL
    update_threshold: int = 100
    confidence_threshold: float = 0.8


class DeploymentRequest(BaseModel):
    version_id: str
    strategy: DeploymentStrategy = DeploymentStrategy.BLUE_GREEN
    target_environment: DeploymentStatus
    traffic_percentage: float = 100.0
    approval_required: bool = True


class MonitoringSetupRequest(BaseModel):
    model_type: ModelType
    metrics_to_monitor: List[MetricType]
    accuracy_threshold: float = 0.7
    latency_threshold_ms: float = 1000.0
    error_rate_threshold: float = 0.05


# Training Endpoints
@router.post("/train")
async def train_model(
    request: TrainingRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Train a new AI model"""
    
    if current_user.user_type not in ["admin", "company"]:
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    
    training_service = MLTrainingService(db)
    
    config = TrainingConfig(
        model_type=request.model_type,
        features=request.features,
        target=request.target,
        test_size=request.test_size,
        cv_folds=request.cv_folds,
        hyperparameters=request.hyperparameters
    )
    
    # Run training in background
    background_tasks.add_task(training_service.create_training_pipeline, config)
    
    return {
        "message": "Training started",
        "model_type": request.model_type,
        "status": "in_progress"
    }


@router.get("/training/status/{model_type}")
async def get_training_status(
    model_type: ModelType,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get training status for a model type"""
    
    # In practice, this would check a job queue or database
    return {
        "model_type": model_type,
        "status": "completed",  # Simplified
        "last_trained": datetime.utcnow().isoformat()
    }


# Evaluation Endpoints
@router.post("/evaluate")
async def evaluate_model(
    request: EvaluationRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Evaluate a trained model"""
    
    if current_user.user_type not in ["admin", "company"]:
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    
    evaluation_service = ModelEvaluationService(db)
    
    config = ValidationConfig(
        method=request.validation_method,
        n_splits=request.n_splits,
        test_size=request.test_size
    )
    
    try:
        results = evaluation_service.evaluate_model(request.model_path, config)
        
        return {
            "success": True,
            "model_path": request.model_path,
            "validation_method": results.validation_method,
            "metrics": results.metrics,
            "confidence_intervals": {k: list(v) for k, v in results.confidence_intervals.items()},
            "feature_importance": results.feature_importance,
            "recommendations": results.recommendations
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Evaluation failed: {str(e)}")


@router.post("/evaluate/compare")
async def compare_models(
    model_paths: List[str],
    validation_method: ValidationMethod = ValidationMethod.CROSS_VALIDATION,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Compare multiple models"""
    
    if current_user.user_type not in ["admin", "company"]:
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    
    evaluation_service = ModelEvaluationService(db)
    
    config = ValidationConfig(method=validation_method)
    
    try:
        comparison = evaluation_service.compare_models(model_paths, config)
        return comparison
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Comparison failed: {str(e)}")


@router.post("/evaluate/fairness/{model_path}")
async def validate_fairness(
    model_path: str,
    protected_attributes: List[str] = [],
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Validate model fairness"""
    
    if current_user.user_type not in ["admin"]:
        raise HTTPException(status_code=403, detail="Admin access required")
    
    evaluation_service = ModelEvaluationService(db)
    
    try:
        fairness_results = evaluation_service.validate_model_fairness(model_path, protected_attributes)
        return fairness_results
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Fairness validation failed: {str(e)}")


# Continuous Learning Endpoints
@router.post("/feedback")
async def submit_feedback(
    request: FeedbackRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Submit feedback for continuous learning"""
    
    learning_service = ContinuousLearningService(db)
    
    feedback_data = FeedbackData(
        feedback_id=str(uuid.uuid4()),
        assessment_id=request.assessment_id,
        question_id=request.question_id,
        user_id=str(current_user.id),
        feedback_type=request.feedback_type,
        feedback_content=request.feedback_content,
        confidence_score=request.confidence_score,
        timestamp=datetime.utcnow()
    )
    
    try:
        result = await learning_service.collect_feedback(feedback_data)
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Feedback submission failed: {str(e)}")


@router.post("/learning/update")
async def trigger_learning_update(
    request: LearningUpdateRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Trigger model update with feedback"""
    
    if current_user.user_type not in ["admin"]:
        raise HTTPException(status_code=403, detail="Admin access required")
    
    learning_service = ContinuousLearningService(db)
    
    config = LearningConfig(
        strategy=request.strategy,
        update_threshold=request.update_threshold,
        confidence_threshold=request.confidence_threshold
    )
    
    # Run update in background
    background_tasks.add_task(
        learning_service.update_model_with_feedback,
        request.model_type,
        config
    )
    
    return {
        "message": "Learning update started",
        "model_type": request.model_type,
        "strategy": request.strategy
    }


@router.get("/learning/monitor/{model_type}")
async def monitor_model_performance(
    model_type: ModelType,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Monitor model performance for continuous learning"""
    
    if current_user.user_type not in ["admin", "company"]:
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    
    learning_service = ContinuousLearningService(db)
    
    try:
        monitoring_results = await learning_service.monitor_model_performance(model_type)
        return monitoring_results
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Monitoring failed: {str(e)}")


# Versioning Endpoints
@router.post("/versions/create")
async def create_model_version(
    model_path: str,
    model_type: ModelType,
    metadata: Dict[str, Any] = {},
    tags: List[str] = [],
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new model version"""
    
    if current_user.user_type not in ["admin"]:
        raise HTTPException(status_code=403, detail="Admin access required")
    
    versioning_service = ModelVersioningService(db)
    
    try:
        version = versioning_service.create_version(model_path, model_type, metadata, tags)
        
        return {
            "success": True,
            "version_id": version.version_id,
            "version_number": version.version_number,
            "model_type": version.model_type,
            "created_at": version.created_at.isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Version creation failed: {str(e)}")


@router.get("/versions")
async def list_model_versions(
    model_type: Optional[ModelType] = None,
    status: Optional[DeploymentStatus] = None,
    limit: int = 50,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List model versions"""
    
    versioning_service = ModelVersioningService(db)
    
    versions = versioning_service.list_versions(model_type, status, limit)
    
    return {
        "versions": [
            {
                "version_id": v.version_id,
                "version_number": v.version_number,
                "model_type": v.model_type,
                "status": v.status,
                "metrics": v.metrics,
                "created_at": v.created_at.isoformat(),
                "tags": v.tags
            }
            for v in versions
        ]
    }


@router.get("/versions/{version_id}")
async def get_model_version(
    version_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get a specific model version"""
    
    versioning_service = ModelVersioningService(db)
    
    version = versioning_service.get_version(version_id)
    if not version:
        raise HTTPException(status_code=404, detail="Version not found")
    
    return {
        "version_id": version.version_id,
        "version_number": version.version_number,
        "model_type": version.model_type,
        "status": version.status,
        "metrics": version.metrics,
        "metadata": version.metadata,
        "created_at": version.created_at.isoformat(),
        "tags": version.tags,
        "checksum": version.checksum
    }


@router.post("/versions/compare")
async def compare_model_versions(
    version_id_1: str,
    version_id_2: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Compare two model versions"""
    
    versioning_service = ModelVersioningService(db)
    
    try:
        comparison = versioning_service.compare_versions(version_id_1, version_id_2)
        return comparison
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Comparison failed: {str(e)}")


# Deployment Endpoints
@router.post("/deploy")
async def deploy_model_version(
    request: DeploymentRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Deploy a model version"""
    
    if current_user.user_type not in ["admin"]:
        raise HTTPException(status_code=403, detail="Admin access required")
    
    versioning_service = ModelVersioningService(db)
    
    config = DeploymentConfig(
        strategy=request.strategy,
        target_environment=request.target_environment,
        traffic_percentage=request.traffic_percentage,
        approval_required=request.approval_required
    )
    
    try:
        result = versioning_service.deploy_version(request.version_id, config)
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Deployment failed: {str(e)}")


@router.post("/rollback/{model_type}")
async def rollback_model(
    model_type: ModelType,
    target_version_id: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Rollback to a previous model version"""
    
    if current_user.user_type not in ["admin"]:
        raise HTTPException(status_code=403, detail="Admin access required")
    
    versioning_service = ModelVersioningService(db)
    
    try:
        result = versioning_service.rollback_deployment(model_type, target_version_id)
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Rollback failed: {str(e)}")


# Monitoring Endpoints
@router.post("/monitoring/setup")
async def setup_monitoring(
    request: MonitoringSetupRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Set up model monitoring"""
    
    if current_user.user_type not in ["admin"]:
        raise HTTPException(status_code=403, detail="Admin access required")
    
    monitoring_service = ModelMonitoringService(db)
    
    config = MonitoringConfig(
        model_type=request.model_type,
        metrics_to_monitor=request.metrics_to_monitor,
        accuracy_threshold=request.accuracy_threshold,
        latency_threshold_ms=request.latency_threshold_ms,
        error_rate_threshold=request.error_rate_threshold
    )
    
    monitoring_service.start_monitoring(config)
    
    return {
        "message": "Monitoring started",
        "model_type": request.model_type,
        "metrics": request.metrics_to_monitor
    }


@router.get("/monitoring/performance/{model_type}")
async def get_performance_summary(
    model_type: ModelType,
    hours_back: int = 24,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get model performance summary"""
    
    monitoring_service = ModelMonitoringService(db)
    
    summary = monitoring_service.get_performance_summary(model_type, hours_back)
    return summary


@router.get("/monitoring/alerts")
async def get_active_alerts(
    model_type: Optional[ModelType] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get active monitoring alerts"""
    
    if current_user.user_type not in ["admin", "company"]:
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    
    monitoring_service = ModelMonitoringService(db)
    
    alerts = monitoring_service.get_active_alerts(model_type)
    
    return {
        "alerts": [
            {
                "alert_id": alert.alert_id,
                "severity": alert.severity,
                "metric_type": alert.metric_type,
                "model_type": alert.model_type,
                "message": alert.message,
                "value": alert.value,
                "threshold": alert.threshold,
                "timestamp": alert.timestamp.isoformat(),
                "resolved": alert.resolved
            }
            for alert in alerts
        ]
    }


@router.post("/monitoring/alerts/{alert_id}/resolve")
async def resolve_alert(
    alert_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Resolve a monitoring alert"""
    
    if current_user.user_type not in ["admin"]:
        raise HTTPException(status_code=403, detail="Admin access required")
    
    monitoring_service = ModelMonitoringService(db)
    
    success = monitoring_service.resolve_alert(alert_id)
    
    if not success:
        raise HTTPException(status_code=404, detail="Alert not found")
    
    return {"message": "Alert resolved", "alert_id": alert_id}


@router.get("/monitoring/drift/{model_type}")
async def detect_model_drift(
    model_type: ModelType,
    days_back: int = 7,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Detect model drift"""
    
    monitoring_service = ModelMonitoringService(db)
    
    drift_results = monitoring_service.detect_model_drift(model_type, days_back)
    return drift_results


@router.get("/monitoring/report/{model_type}")
async def generate_monitoring_report(
    model_type: ModelType,
    days_back: int = 7,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Generate comprehensive monitoring report"""
    
    if current_user.user_type not in ["admin", "company"]:
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    
    monitoring_service = ModelMonitoringService(db)
    
    report = monitoring_service.generate_monitoring_report(model_type, days_back)
    return report


# Utility Endpoints
@router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "services": {
            "training": "operational",
            "evaluation": "operational",
            "learning": "operational",
            "versioning": "operational",
            "monitoring": "operational"
        }
    }


@router.get("/metrics/summary")
async def get_system_metrics(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get overall system metrics"""
    
    if current_user.user_type not in ["admin"]:
        raise HTTPException(status_code=403, detail="Admin access required")
    
    versioning_service = ModelVersioningService(db)
    monitoring_service = ModelMonitoringService(db)
    
    # Get version counts by model type
    version_counts = {}
    for model_type in ModelType:
        versions = versioning_service.list_versions(model_type=model_type, limit=1000)
        version_counts[model_type] = len(versions)
    
    # Get active alerts count
    active_alerts = monitoring_service.get_active_alerts()
    
    return {
        "total_model_versions": sum(version_counts.values()),
        "versions_by_type": version_counts,
        "active_alerts": len(active_alerts),
        "critical_alerts": len([a for a in active_alerts if a.severity == AlertSeverity.CRITICAL]),
        "system_status": "operational",
        "last_updated": datetime.utcnow().isoformat()
    }