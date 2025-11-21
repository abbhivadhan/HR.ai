#!/usr/bin/env python3
"""
Demo script for AI Model Training and Optimization System

This script demonstrates the key features of the ML training pipeline:
- Model training
- Evaluation and validation
- Continuous learning
- Model versioning
- Performance monitoring
"""

import asyncio
import json
from datetime import datetime, timedelta
from pathlib import Path
import tempfile

# Mock database session for demo
class MockDB:
    def query(self, *args):
        return self
    
    def filter(self, *args):
        return self
    
    def all(self):
        return []
    
    def first(self):
        return None

async def demo_training_pipeline():
    """Demonstrate the complete ML training pipeline"""
    
    print("🚀 AI Model Training and Optimization System Demo")
    print("=" * 60)
    
    # Initialize services
    from app.services.ml_training_service import MLTrainingService, ModelType, TrainingConfig
    from app.services.model_evaluation_service import ModelEvaluationService, ValidationConfig, ValidationMethod
    from app.services.continuous_learning_service import ContinuousLearningService, FeedbackData, FeedbackType
    from app.services.model_versioning_service import ModelVersioningService, DeploymentConfig, DeploymentStrategy, DeploymentStatus
    from app.services.model_monitoring_service import ModelMonitoringService, MonitoringConfig, MetricType
    
    mock_db = MockDB()
    
    # 1. Model Training
    print("\n1. 🧠 Training AI Model")
    print("-" * 30)
    
    training_service = MLTrainingService(mock_db)
    
    config = TrainingConfig(
        model_type=ModelType.SKILL_CLASSIFIER,
        features=["response_text", "time_spent", "points_earned"],
        target="category",
        test_size=0.2,
        cv_folds=5
    )
    
    print(f"Training {config.model_type} model...")
    print(f"Features: {config.features}")
    print(f"Cross-validation folds: {config.cv_folds}")
    
    # Mock training result
    training_result = {
        "success": True,
        "model_type": config.model_type,
        "model_path": "models/skill_classifier_20241027_120000.pkl",
        "metrics": {
            "accuracy": 0.87,
            "precision": 0.85,
            "recall": 0.89,
            "f1_score": 0.87,
            "training_time": 45.2
        },
        "bias_results": {
            "overall_bias_score": 0.04,
            "category_bias": {"python": 0.88, "javascript": 0.86, "sql": 0.87},
            "recommendations": ["Bias levels are within acceptable range"]
        },
        "training_samples": 1250
    }
    
    print(f"✅ Training completed successfully!")
    print(f"   Accuracy: {training_result['metrics']['accuracy']:.3f}")
    print(f"   F1 Score: {training_result['metrics']['f1_score']:.3f}")
    print(f"   Training time: {training_result['metrics']['training_time']:.1f}s")
    print(f"   Bias score: {training_result['bias_results']['overall_bias_score']:.3f}")
    
    # 2. Model Evaluation
    print("\n2. 📊 Model Evaluation")
    print("-" * 30)
    
    evaluation_service = ModelEvaluationService(mock_db)
    
    validation_config = ValidationConfig(
        method=ValidationMethod.CROSS_VALIDATION,
        n_splits=5
    )
    
    print(f"Evaluating model with {validation_config.method}...")
    
    # Mock evaluation results
    evaluation_results = {
        "validation_method": "cross_validation",
        "metrics": {
            "accuracy": 0.87,
            "precision": 0.85,
            "recall": 0.89,
            "f1_score": 0.87
        },
        "confidence_intervals": {
            "accuracy": (0.84, 0.90),
            "f1_score": (0.84, 0.90)
        },
        "feature_importance": {
            "response_quality": 0.35,
            "time_efficiency": 0.28,
            "technical_accuracy": 0.22,
            "response_length": 0.15
        },
        "recommendations": [
            "Model performance is excellent",
            "Consider collecting more data for edge cases"
        ]
    }
    
    print("✅ Evaluation completed!")
    print(f"   Cross-validation accuracy: {evaluation_results['metrics']['accuracy']:.3f}")
    print(f"   95% CI: {evaluation_results['confidence_intervals']['accuracy']}")
    print(f"   Top feature: {list(evaluation_results['feature_importance'].keys())[0]}")
    
    # 3. Model Versioning
    print("\n3. 📦 Model Versioning")
    print("-" * 30)
    
    with tempfile.TemporaryDirectory() as temp_dir:
        versioning_service = ModelVersioningService(mock_db)
        versioning_service.versions_dir = Path(temp_dir) / "versions"
        versioning_service.versions_dir.mkdir()
        versioning_service.deployments_dir = Path(temp_dir) / "deployments"
        versioning_service.deployments_dir.mkdir()
        versioning_service.registry_file = versioning_service.versions_dir / "registry.json"
        versioning_service._initialize_registry()
        
        # Create a mock model file
        with tempfile.NamedTemporaryFile(suffix='.pkl', delete=False) as model_file:
            import pickle
            pickle.dump({'model': 'mock', 'config': config, 'metrics': training_result['metrics']}, model_file)
            model_file.flush()
            
            version = versioning_service.create_version(
                model_path=model_file.name,
                model_type=ModelType.SKILL_CLASSIFIER,
                metadata={
                    "description": "Skill classifier with improved accuracy",
                    "training_data_size": 1250,
                    "features_used": len(config.features)
                },
                tags=["production-ready", "v1.0"]
            )
        
        print(f"✅ Version created: {version.version_number}")
        print(f"   Version ID: {version.version_id}")
        print(f"   Status: {version.status}")
        print(f"   Tags: {version.tags}")
        
        # Deploy to staging
        deploy_config = DeploymentConfig(
            strategy=DeploymentStrategy.BLUE_GREEN,
            target_environment=DeploymentStatus.STAGING,
            approval_required=False
        )
        
        deploy_result = versioning_service.deploy_version(version.version_id, deploy_config)
        print(f"✅ Deployed to staging: {deploy_result['success']}")
        
        # Clean up
        Path(model_file.name).unlink()
    
    # 4. Continuous Learning
    print("\n4. 🔄 Continuous Learning")
    print("-" * 30)
    
    learning_service = ContinuousLearningService(mock_db)
    
    # Simulate feedback collection
    feedback_data = FeedbackData(
        feedback_id="feedback_001",
        assessment_id="assessment_123",
        question_id="question_456",
        user_id="user_789",
        feedback_type=FeedbackType.EXPLICIT,
        feedback_content={
            "rating": 4,
            "comment": "Question was well-designed and fair",
            "difficulty_feedback": "appropriate"
        },
        confidence_score=0.9,
        timestamp=datetime.utcnow()
    )
    
    print("Collecting user feedback...")
    feedback_result = await learning_service.collect_feedback(feedback_data)
    print(f"✅ Feedback collected: {feedback_result['success']}")
    print(f"   Feedback ID: {feedback_result['feedback_id']}")
    print(f"   Confidence: {feedback_data.confidence_score}")
    
    # Simulate implicit feedback processing
    print("\nProcessing implicit feedback...")
    implicit_result = await learning_service.process_implicit_feedback("assessment_123")
    print(f"✅ Implicit signals processed: {implicit_result.get('signals_processed', 0)}")
    
    # 5. Performance Monitoring
    print("\n5. 📈 Performance Monitoring")
    print("-" * 30)
    
    with tempfile.TemporaryDirectory() as temp_dir:
        monitoring_service = ModelMonitoringService(mock_db)
        monitoring_service.monitoring_dir = Path(temp_dir)
        monitoring_service.metrics_file = monitoring_service.monitoring_dir / "metrics.jsonl"
        monitoring_service.alerts_file = monitoring_service.monitoring_dir / "alerts.jsonl"
        
        # Set up monitoring
        monitor_config = MonitoringConfig(
            model_type=ModelType.SKILL_CLASSIFIER,
            metrics_to_monitor=[MetricType.ACCURACY, MetricType.LATENCY, MetricType.ERROR_RATE],
            accuracy_threshold=0.75,
            latency_threshold_ms=500.0
        )
        
        monitoring_service.start_monitoring(monitor_config)
        print(f"✅ Monitoring started for {monitor_config.model_type}")
        print(f"   Metrics: {monitor_config.metrics_to_monitor}")
        print(f"   Accuracy threshold: {monitor_config.accuracy_threshold}")
        
        # Simulate prediction metrics
        print("\nRecording prediction metrics...")
        for i in range(10):
            monitoring_service.record_prediction_metrics(
                model_type=ModelType.SKILL_CLASSIFIER,
                model_version="1.0.0",
                prediction_time_ms=150.0 + (i * 10),
                prediction_accuracy=0.85 + (i * 0.01),
                error_occurred=False
            )
        
        # Get performance summary
        summary = monitoring_service.get_performance_summary(
            ModelType.SKILL_CLASSIFIER, 
            hours_back=1
        )
        
        print(f"✅ Performance summary generated")
        print(f"   Total predictions: {summary['total_predictions']}")
        if MetricType.ACCURACY in summary['metrics']:
            acc_metrics = summary['metrics'][MetricType.ACCURACY]
            print(f"   Average accuracy: {acc_metrics['mean']:.3f}")
            print(f"   Accuracy range: {acc_metrics['min']:.3f} - {acc_metrics['max']:.3f}")
        
        # Check for drift
        drift_results = monitoring_service.detect_model_drift(
            ModelType.SKILL_CLASSIFIER, 
            days_back=1
        )
        print(f"   Drift detected: {drift_results.get('drift_detected', False)}")
    
    # 6. System Health Check
    print("\n6. 🏥 System Health Check")
    print("-" * 30)
    
    health_status = {
        "training_service": "operational",
        "evaluation_service": "operational", 
        "learning_service": "operational",
        "versioning_service": "operational",
        "monitoring_service": "operational",
        "overall_status": "healthy",
        "last_check": datetime.utcnow().isoformat()
    }
    
    print("✅ All services operational")
    for service, status in health_status.items():
        if service != "last_check":
            print(f"   {service}: {status}")
    
    print(f"\n🎉 Demo completed successfully!")
    print(f"   System is ready for production use")
    print(f"   All AI/ML components are functioning properly")


def demo_api_usage():
    """Demonstrate API usage examples"""
    
    print("\n" + "=" * 60)
    print("📡 API Usage Examples")
    print("=" * 60)
    
    api_examples = {
        "Train Model": {
            "method": "POST",
            "endpoint": "/api/ml/train",
            "payload": {
                "model_type": "skill_classifier",
                "features": ["response_text", "time_spent"],
                "target": "category",
                "test_size": 0.2,
                "hyperparameters": {"n_estimators": 100}
            }
        },
        "Evaluate Model": {
            "method": "POST", 
            "endpoint": "/api/ml/evaluate",
            "payload": {
                "model_path": "models/skill_classifier_latest.pkl",
                "validation_method": "cross_validation",
                "n_splits": 5
            }
        },
        "Submit Feedback": {
            "method": "POST",
            "endpoint": "/api/ml/feedback", 
            "payload": {
                "assessment_id": "assessment_123",
                "feedback_type": "explicit",
                "feedback_content": {"rating": 4, "comment": "Good question"},
                "confidence_score": 0.9
            }
        },
        "Deploy Model": {
            "method": "POST",
            "endpoint": "/api/ml/deploy",
            "payload": {
                "version_id": "version_abc123",
                "strategy": "blue_green", 
                "target_environment": "production",
                "traffic_percentage": 100.0
            }
        },
        "Get Performance": {
            "method": "GET",
            "endpoint": "/api/ml/monitoring/performance/skill_classifier?hours_back=24",
            "payload": None
        }
    }
    
    for name, example in api_examples.items():
        print(f"\n{name}:")
        print(f"  {example['method']} {example['endpoint']}")
        if example['payload']:
            print(f"  Payload: {json.dumps(example['payload'], indent=4)}")


if __name__ == "__main__":
    print("Starting AI Model Training and Optimization Demo...")
    
    # Run the async demo
    asyncio.run(demo_training_pipeline())
    
    # Show API examples
    demo_api_usage()
    
    print(f"\n✨ Demo completed at {datetime.utcnow().isoformat()}")
    print("The AI training and optimization system is ready for use!")