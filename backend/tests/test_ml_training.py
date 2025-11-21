"""
Tests for AI Model Training and Optimization System

This module contains comprehensive tests for the ML training pipeline,
model evaluation, continuous learning, versioning, and monitoring.
"""

import pytest
import json
import tempfile
import shutil
from pathlib import Path
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, MagicMock
import numpy as np
import pandas as pd

from sqlalchemy.orm import Session
from app.services.ml_training_service import MLTrainingService, ModelType, TrainingConfig, ModelMetrics
from app.services.model_evaluation_service import ModelEvaluationService, ValidationConfig, ValidationMethod
from app.services.continuous_learning_service import ContinuousLearningService, FeedbackData, FeedbackType, LearningConfig, LearningStrategy
from app.services.model_versioning_service import ModelVersioningService, DeploymentConfig, DeploymentStrategy, DeploymentStatus
from app.services.model_monitoring_service import ModelMonitoringService, MonitoringConfig, MetricType, AlertSeverity
from app.models.assessment import Assessment, AssessmentResponse, Question, AssessmentStatus
from app.models.user import User


class TestMLTrainingService:
    """Test ML Training Service"""
    
    @pytest.fixture
    def mock_db(self):
        return Mock(spec=Session)
    
    @pytest.fixture
    def training_service(self, mock_db):
        return MLTrainingService(mock_db)
    
    @pytest.fixture
    def sample_training_config(self):
        return TrainingConfig(
            model_type=ModelType.SKILL_CLASSIFIER,
            features=["response_text", "time_spent", "points_earned"],
            target="category",
            test_size=0.2,
            cv_folds=5
        )
    
    def test_create_training_pipeline_success(self, training_service, sample_training_config, mock_db):
        """Test successful training pipeline creation"""
        
        # Mock data extraction
        sample_data = [
            {
                'assessment_id': 'test-1',
                'question_id': 'q-1',
                'category': 'python',
                'points_earned': 8.5,
                'response_text': 'def function(): return True',
                'time_spent': 120,
                'is_correct': True
            }
        ] * 100  # Ensure minimum data requirement
        
        with patch.object(training_service, '_extract_training_data', return_value=sample_data):
            with patch.object(training_service, '_prepare_features_and_targets') as mock_prepare:
                mock_prepare.return_value = (np.random.rand(100, 10), np.random.randint(0, 3, 100))
                
                with patch.object(training_service, '_train_model') as mock_train:
                    mock_model = Mock()
                    mock_train.return_value = (mock_model, 30.5)
                    
                    with patch.object(training_service, '_evaluate_model') as mock_evaluate:
                        mock_metrics = ModelMetrics(accuracy=0.85, precision=0.82, recall=0.88, f1_score=0.85)
                        mock_evaluate.return_value = mock_metrics
                        
                        with patch.object(training_service, '_detect_bias') as mock_bias:
                            mock_bias.return_value = {'overall_bias_score': 0.05}
                            
                            with patch.object(training_service, '_save_model') as mock_save:
                                mock_save.return_value = Path('test_model.pkl')
                                
                                result = training_service.create_training_pipeline(sample_training_config)
        
        assert result["success"] is True
        assert result["model_type"] == ModelType.SKILL_CLASSIFIER
        assert "model_path" in result
        assert result["metrics"]["accuracy"] == 0.85
        assert result["training_samples"] == 100
    
    def test_create_training_pipeline_insufficient_data(self, training_service, sample_training_config):
        """Test training pipeline with insufficient data"""
        
        # Mock insufficient data
        with patch.object(training_service, '_extract_training_data', return_value=[]):
            result = training_service.create_training_pipeline(sample_training_config)
        
        assert result["success"] is False
        assert "Insufficient training data" in result["error"]
    
    def test_extract_training_data(self, training_service, mock_db):
        """Test training data extraction"""
        
        # Mock database queries
        mock_assessment = Mock()
        mock_assessment.id = 'test-assessment'
        mock_assessment.candidate_id = 'test-candidate'
        mock_assessment.percentage_score = 85.0
        mock_assessment.passed = True
        mock_assessment.assessment_type.value = 'technical'
        mock_assessment.created_at = datetime.utcnow()
        
        mock_response = Mock()
        mock_response.question_id = 'test-question'
        mock_response.points_earned = 8.5
        mock_response.is_correct = True
        mock_response.response_text = 'test response'
        mock_response.time_spent_seconds = 120
        mock_response.ai_score_breakdown = {'accuracy': 0.9}
        
        mock_question = Mock()
        mock_question.question_type.value = 'multiple_choice'
        mock_question.difficulty_level.value = 'intermediate'
        mock_question.category = 'python'
        mock_question.max_points = 10
        
        mock_db.query.return_value.filter.return_value.all.return_value = [mock_assessment]
        mock_db.query.return_value.filter.return_value.first.return_value = mock_question
        
        # Mock the chained query for responses
        mock_db.query.return_value.filter.return_value.all.side_effect = [
            [mock_assessment],  # First call for assessments
            [mock_response]     # Second call for responses
        ]
        
        config = TrainingConfig(model_type=ModelType.SKILL_CLASSIFIER, features=[], target="")
        data = training_service._extract_training_data(config)
        
        assert len(data) > 0
        assert data[0]['assessment_id'] == 'test-assessment'
        assert data[0]['category'] == 'python'
        assert data[0]['points_earned'] == 8.5
    
    def test_skill_feature_extraction(self, training_service):
        """Test skill feature extraction"""
        
        df = pd.DataFrame([
            {
                'response_text': 'def function(): return True',
                'max_points': 10,
                'points_earned': 8,
                'response_length': 25,
                'time_spent': 120,
                'overall_score': 85,
                'question_type': 'coding',
                'difficulty_level': 'intermediate'
            }
        ])
        
        # Mock text vectorizer
        with patch.object(training_service.text_vectorizer, 'fit_transform') as mock_vectorizer:
            mock_vectorizer.return_value.toarray.return_value = np.random.rand(1, 100)
            
            features = training_service._extract_skill_features(df)
        
        assert features.shape[0] == 1
        assert features.shape[1] > 100  # Text features + numerical + categorical


class TestModelEvaluationService:
    """Test Model Evaluation Service"""
    
    @pytest.fixture
    def mock_db(self):
        return Mock(spec=Session)
    
    @pytest.fixture
    def evaluation_service(self, mock_db):
        return ModelEvaluationService(mock_db)
    
    @pytest.fixture
    def temp_model_file(self):
        """Create a temporary model file for testing"""
        with tempfile.NamedTemporaryFile(suffix='.pkl', delete=False) as f:
            import pickle
            model_data = {
                'model': Mock(),
                'config': Mock(),
                'metrics': Mock()
            }
            pickle.dump(model_data, f)
            yield f.name
        Path(f.name).unlink()
    
    def test_evaluate_model_success(self, evaluation_service, temp_model_file):
        """Test successful model evaluation"""
        
        config = ValidationConfig(method=ValidationMethod.CROSS_VALIDATION)
        
        with patch.object(evaluation_service, '_load_evaluation_data') as mock_load:
            mock_load.return_value = (np.random.rand(100, 10), np.random.randint(0, 3, 100))
            
            with patch.object(evaluation_service, '_perform_validation') as mock_validate:
                mock_validate.return_value = {
                    'metrics': {'accuracy': 0.85, 'f1_score': 0.82},
                    'confidence_intervals': {'accuracy': (0.80, 0.90)}
                }
                
                with patch.object(evaluation_service, '_calculate_feature_importance') as mock_importance:
                    mock_importance.return_value = {'feature_1': 0.3, 'feature_2': 0.2}
                    
                    with patch.object(evaluation_service, '_generate_learning_curves') as mock_curves:
                        mock_curves.return_value = {'train_scores_mean': [0.8, 0.85]}
                        
                        results = evaluation_service.evaluate_model(temp_model_file, config)
        
        assert results.validation_method == ValidationMethod.CROSS_VALIDATION
        assert results.metrics['accuracy'] == 0.85
        assert 'feature_1' in results.feature_importance
    
    def test_compare_models(self, evaluation_service):
        """Test model comparison"""
        
        model_paths = ['model1.pkl', 'model2.pkl']
        config = ValidationConfig(method=ValidationMethod.HOLDOUT)
        
        with patch.object(evaluation_service, 'evaluate_model') as mock_evaluate:
            # Mock evaluation results for two models
            mock_evaluate.side_effect = [
                Mock(metrics={'accuracy': 0.85, 'f1_score': 0.82}),
                Mock(metrics={'accuracy': 0.88, 'f1_score': 0.85})
            ]
            
            comparison = evaluation_service.compare_models(model_paths, config)
        
        assert 'models' in comparison
        assert 'best_model' in comparison
        assert len(comparison['models']) == 2
    
    def test_validate_model_fairness(self, evaluation_service, temp_model_file):
        """Test model fairness validation"""
        
        with patch.object(evaluation_service, '_load_evaluation_data') as mock_load:
            mock_load.return_value = (np.random.rand(100, 10), np.random.randint(0, 2, 100))
            
            with patch.object(evaluation_service, '_calculate_individual_fairness') as mock_fairness:
                mock_fairness.return_value = 0.85
                
                results = evaluation_service.validate_model_fairness(temp_model_file, ['gender', 'age'])
        
        assert 'fairness_score' in results
        assert 'individual_fairness' in results
        assert results['fairness_score'] == 0.85


class TestContinuousLearningService:
    """Test Continuous Learning Service"""
    
    @pytest.fixture
    def mock_db(self):
        return Mock(spec=Session)
    
    @pytest.fixture
    def learning_service(self, mock_db):
        return ContinuousLearningService(mock_db)
    
    @pytest.fixture
    def sample_feedback(self):
        return FeedbackData(
            feedback_id='test-feedback-1',
            assessment_id='test-assessment',
            question_id='test-question',
            user_id='test-user',
            feedback_type=FeedbackType.EXPLICIT,
            feedback_content={'rating': 4, 'comment': 'Good question'},
            confidence_score=0.9,
            timestamp=datetime.utcnow()
        )
    
    @pytest.mark.asyncio
    async def test_collect_feedback_success(self, learning_service, sample_feedback):
        """Test successful feedback collection"""
        
        with patch.object(learning_service, '_validate_feedback', return_value=True):
            with patch.object(learning_service, '_store_feedback'):
                with patch.object(learning_service, '_should_trigger_update', return_value=False):
                    result = await learning_service.collect_feedback(sample_feedback)
        
        assert result["success"] is True
        assert result["feedback_id"] == 'test-feedback-1'
        assert "stored_at" in result
    
    @pytest.mark.asyncio
    async def test_collect_feedback_invalid(self, learning_service, sample_feedback):
        """Test feedback collection with invalid data"""
        
        with patch.object(learning_service, '_validate_feedback', return_value=False):
            result = await learning_service.collect_feedback(sample_feedback)
        
        assert result["success"] is False
        assert "Invalid feedback data" in result["error"]
    
    @pytest.mark.asyncio
    async def test_process_implicit_feedback(self, learning_service, mock_db):
        """Test implicit feedback processing"""
        
        # Mock assessment
        mock_assessment = Mock()
        mock_assessment.id = 'test-assessment'
        mock_assessment.candidate_id = 'test-candidate'
        mock_assessment.started_at = datetime.utcnow() - timedelta(minutes=30)
        mock_assessment.completed_at = datetime.utcnow()
        mock_assessment.duration_minutes = 60
        mock_assessment.percentage_score = 25.0  # Very low score
        
        mock_db.query.return_value.filter.return_value.first.return_value = mock_assessment
        
        with patch.object(learning_service, '_extract_implicit_signals') as mock_extract:
            mock_extract.return_value = [
                {
                    'type': 'performance',
                    'signal': 'very_low_score',
                    'value': 25.0,
                    'confidence': 0.9
                }
            ]
            
            with patch.object(learning_service, 'collect_feedback') as mock_collect:
                mock_collect.return_value = {"success": True}
                
                result = await learning_service.process_implicit_feedback('test-assessment')
        
        assert result["success"] is True
        assert result["signals_processed"] == 1
    
    def test_extract_implicit_signals(self, learning_service, mock_db):
        """Test implicit signal extraction"""
        
        # Mock assessment with suspicious patterns
        mock_assessment = Mock()
        mock_assessment.started_at = datetime.utcnow() - timedelta(minutes=5)  # Very fast completion
        mock_assessment.completed_at = datetime.utcnow()
        mock_assessment.duration_minutes = 60
        mock_assessment.percentage_score = 95.0  # Very high score
        
        # Mock responses with consistent timing
        mock_responses = []
        for i in range(5):
            mock_response = Mock()
            mock_response.time_spent_seconds = 60  # Exactly 1 minute each
            mock_responses.append(mock_response)
        
        mock_db.query.return_value.filter.return_value.all.return_value = mock_responses
        
        signals = learning_service._extract_implicit_signals(mock_assessment)
        
        assert len(signals) > 0
        signal_types = [s['type'] for s in signals]
        assert 'completion_time' in signal_types or 'performance' in signal_types


class TestModelVersioningService:
    """Test Model Versioning Service"""
    
    @pytest.fixture
    def mock_db(self):
        return Mock(spec=Session)
    
    @pytest.fixture
    def versioning_service(self, mock_db):
        with tempfile.TemporaryDirectory() as temp_dir:
            service = ModelVersioningService(mock_db)
            service.versions_dir = Path(temp_dir) / "versions"
            service.versions_dir.mkdir()
            service.deployments_dir = Path(temp_dir) / "deployments"
            service.deployments_dir.mkdir()
            service.registry_file = service.versions_dir / "registry.json"
            service._initialize_registry()
            yield service
    
    @pytest.fixture
    def temp_model_file(self):
        """Create a temporary model file"""
        with tempfile.NamedTemporaryFile(suffix='.pkl', delete=False) as f:
            import pickle
            model_data = {
                'model': Mock(),
                'config': Mock(),
                'metrics': Mock(accuracy=0.85, f1_score=0.82)
            }
            pickle.dump(model_data, f)
            yield f.name
        Path(f.name).unlink()
    
    def test_create_version_success(self, versioning_service, temp_model_file):
        """Test successful version creation"""
        
        version = versioning_service.create_version(
            model_path=temp_model_file,
            model_type=ModelType.SKILL_CLASSIFIER,
            metadata={'description': 'Test model'},
            tags=['test', 'v1']
        )
        
        assert version.model_type == ModelType.SKILL_CLASSIFIER
        assert version.version_number == '1.0.0'
        assert version.status == DeploymentStatus.DEVELOPMENT
        assert 'test' in version.tags
        assert version.checksum != ""
    
    def test_list_versions(self, versioning_service, temp_model_file):
        """Test version listing"""
        
        # Create multiple versions
        for i in range(3):
            versioning_service.create_version(
                model_path=temp_model_file,
                model_type=ModelType.SKILL_CLASSIFIER,
                metadata={'version': i}
            )
        
        versions = versioning_service.list_versions(model_type=ModelType.SKILL_CLASSIFIER)
        
        assert len(versions) == 3
        assert all(v.model_type == ModelType.SKILL_CLASSIFIER for v in versions)
        # Should be sorted by creation date (newest first)
        assert versions[0].version_number == '1.0.2'
    
    def test_compare_versions(self, versioning_service, temp_model_file):
        """Test version comparison"""
        
        # Create two versions
        version1 = versioning_service.create_version(
            model_path=temp_model_file,
            model_type=ModelType.SKILL_CLASSIFIER
        )
        
        version2 = versioning_service.create_version(
            model_path=temp_model_file,
            model_type=ModelType.SKILL_CLASSIFIER
        )
        
        comparison = versioning_service.compare_versions(version1.version_id, version2.version_id)
        
        assert 'version_1' in comparison
        assert 'version_2' in comparison
        assert 'metrics_comparison' in comparison
        assert 'recommendations' in comparison
    
    def test_deploy_version(self, versioning_service, temp_model_file):
        """Test version deployment"""
        
        version = versioning_service.create_version(
            model_path=temp_model_file,
            model_type=ModelType.SKILL_CLASSIFIER
        )
        
        config = DeploymentConfig(
            strategy=DeploymentStrategy.BLUE_GREEN,
            target_environment=DeploymentStatus.STAGING,
            approval_required=False
        )
        
        result = versioning_service.deploy_version(version.version_id, config)
        
        assert result["success"] is True
        assert result["strategy"] == "blue_green"
    
    def test_rollback_deployment(self, versioning_service, temp_model_file):
        """Test deployment rollback"""
        
        # Create and deploy two versions
        version1 = versioning_service.create_version(
            model_path=temp_model_file,
            model_type=ModelType.SKILL_CLASSIFIER
        )
        
        version2 = versioning_service.create_version(
            model_path=temp_model_file,
            model_type=ModelType.SKILL_CLASSIFIER
        )
        
        # Deploy both to production (simulating version progression)
        config = DeploymentConfig(
            strategy=DeploymentStrategy.BLUE_GREEN,
            target_environment=DeploymentStatus.PRODUCTION,
            approval_required=False
        )
        
        versioning_service.deploy_version(version1.version_id, config)
        versioning_service.deploy_version(version2.version_id, config)
        
        # Rollback to version 1
        result = versioning_service.rollback_deployment(
            ModelType.SKILL_CLASSIFIER,
            version1.version_id
        )
        
        assert result["success"] is True
        assert result["rolled_back_to"] == version1.version_id


class TestModelMonitoringService:
    """Test Model Monitoring Service"""
    
    @pytest.fixture
    def mock_db(self):
        return Mock(spec=Session)
    
    @pytest.fixture
    def monitoring_service(self, mock_db):
        with tempfile.TemporaryDirectory() as temp_dir:
            service = ModelMonitoringService(mock_db)
            service.monitoring_dir = Path(temp_dir)
            service.metrics_file = service.monitoring_dir / "metrics.jsonl"
            service.alerts_file = service.monitoring_dir / "alerts.jsonl"
            yield service
    
    def test_start_monitoring(self, monitoring_service):
        """Test monitoring setup"""
        
        config = MonitoringConfig(
            model_type=ModelType.SKILL_CLASSIFIER,
            metrics_to_monitor=[MetricType.ACCURACY, MetricType.LATENCY],
            accuracy_threshold=0.7
        )
        
        monitoring_service.start_monitoring(config)
        
        assert ModelType.SKILL_CLASSIFIER in monitoring_service.monitoring_configs
        assert monitoring_service.monitoring_configs[ModelType.SKILL_CLASSIFIER].accuracy_threshold == 0.7
    
    def test_record_prediction_metrics(self, monitoring_service):
        """Test prediction metrics recording"""
        
        # Start monitoring first
        config = MonitoringConfig(
            model_type=ModelType.SKILL_CLASSIFIER,
            metrics_to_monitor=[MetricType.ACCURACY, MetricType.LATENCY]
        )
        monitoring_service.start_monitoring(config)
        
        # Record metrics
        monitoring_service.record_prediction_metrics(
            model_type=ModelType.SKILL_CLASSIFIER,
            model_version='1.0.0',
            prediction_time_ms=150.0,
            prediction_accuracy=0.85,
            error_occurred=False
        )
        
        # Check metrics were stored
        assert len(monitoring_service.metrics_buffer[ModelType.SKILL_CLASSIFIER]) > 0
        
        # Check metrics file was created
        assert monitoring_service.metrics_file.exists()
    
    def test_get_performance_summary(self, monitoring_service):
        """Test performance summary generation"""
        
        # Add some test metrics
        from ..services.model_monitoring_service import PerformanceMetric
        
        for i in range(10):
            metric = PerformanceMetric(
                metric_type=MetricType.ACCURACY,
                value=0.8 + (i * 0.01),
                timestamp=datetime.utcnow() - timedelta(hours=i),
                model_type=ModelType.SKILL_CLASSIFIER,
                model_version='1.0.0'
            )
            monitoring_service.metrics_buffer[ModelType.SKILL_CLASSIFIER].append(metric)
        
        summary = monitoring_service.get_performance_summary(ModelType.SKILL_CLASSIFIER, hours_back=24)
        
        assert summary['model_type'] == ModelType.SKILL_CLASSIFIER
        assert summary['total_predictions'] == 10
        assert MetricType.ACCURACY in summary['metrics']
        assert summary['metrics'][MetricType.ACCURACY]['mean'] > 0.8
    
    def test_detect_model_drift(self, monitoring_service):
        """Test model drift detection"""
        
        # Add metrics showing declining performance
        from ..services.model_monitoring_service import PerformanceMetric
        
        base_time = datetime.utcnow()
        for day in range(7):
            for hour in range(24):
                # Simulate declining accuracy over time
                accuracy = 0.9 - (day * 0.02)  # Decline by 2% per day
                
                metric = PerformanceMetric(
                    metric_type=MetricType.ACCURACY,
                    value=accuracy,
                    timestamp=base_time - timedelta(days=day, hours=hour),
                    model_type=ModelType.SKILL_CLASSIFIER,
                    model_version='1.0.0'
                )
                monitoring_service.metrics_buffer[ModelType.SKILL_CLASSIFIER].append(metric)
        
        drift_results = monitoring_service.detect_model_drift(ModelType.SKILL_CLASSIFIER, days_back=7)
        
        assert 'drift_detected' in drift_results
        assert 'drift_metrics' in drift_results
        # Should detect declining accuracy
        if 'accuracy_trend' in drift_results['drift_metrics']:
            assert drift_results['drift_metrics']['accuracy_trend'] < 0
    
    def test_generate_monitoring_report(self, monitoring_service):
        """Test monitoring report generation"""
        
        # Mock versioning service
        with patch.object(monitoring_service, 'versioning_service') as mock_versioning:
            mock_version = Mock()
            mock_version.version_id = 'test-version'
            mock_version.version_number = '1.0.0'
            mock_version.created_at = datetime.utcnow()
            mock_versioning.get_latest_version.return_value = mock_version
            
            with patch.object(monitoring_service, 'get_performance_summary') as mock_summary:
                mock_summary.return_value = {
                    'total_predictions': 100,
                    'metrics': {MetricType.ACCURACY: {'mean': 0.85}}
                }
                
                with patch.object(monitoring_service, 'detect_model_drift') as mock_drift:
                    mock_drift.return_value = {'drift_detected': False}
                    
                    report = monitoring_service.generate_monitoring_report(
                        ModelType.SKILL_CLASSIFIER, days_back=7
                    )
        
        assert 'model_type' in report
        assert 'performance_summary' in report
        assert 'drift_analysis' in report
        assert 'recommendations' in report
        assert report['model_type'] == ModelType.SKILL_CLASSIFIER


class TestIntegration:
    """Integration tests for the complete ML system"""
    
    @pytest.fixture
    def mock_db(self):
        return Mock(spec=Session)
    
    @pytest.mark.asyncio
    async def test_complete_ml_workflow(self, mock_db):
        """Test complete ML workflow from training to monitoring"""
        
        # 1. Train a model
        training_service = MLTrainingService(mock_db)
        config = TrainingConfig(
            model_type=ModelType.SKILL_CLASSIFIER,
            features=[],
            target=""
        )
        
        # Mock training data and process
        with patch.object(training_service, '_extract_training_data') as mock_extract:
            mock_extract.return_value = [{'test': 'data'}] * 100
            
            with patch.object(training_service, '_prepare_features_and_targets') as mock_prepare:
                mock_prepare.return_value = (np.random.rand(100, 10), np.random.randint(0, 3, 100))
                
                with patch.object(training_service, '_train_model') as mock_train:
                    mock_train.return_value = (Mock(), 30.0)
                    
                    with patch.object(training_service, '_evaluate_model') as mock_eval:
                        mock_eval.return_value = ModelMetrics(0.85, 0.82, 0.88, 0.85)
                        
                        with patch.object(training_service, '_detect_bias') as mock_bias:
                            mock_bias.return_value = {'overall_bias_score': 0.05}
                            
                            with tempfile.NamedTemporaryFile(suffix='.pkl') as temp_file:
                                with patch.object(training_service, '_save_model') as mock_save:
                                    mock_save.return_value = Path(temp_file.name)
                                    
                                    training_result = training_service.create_training_pipeline(config)
        
        assert training_result["success"] is True
        
        # 2. Create version
        with tempfile.TemporaryDirectory() as temp_dir:
            versioning_service = ModelVersioningService(mock_db)
            versioning_service.versions_dir = Path(temp_dir) / "versions"
            versioning_service.versions_dir.mkdir()
            versioning_service.deployments_dir = Path(temp_dir) / "deployments"
            versioning_service.deployments_dir.mkdir()
            versioning_service.registry_file = versioning_service.versions_dir / "registry.json"
            versioning_service._initialize_registry()
            
            with tempfile.NamedTemporaryFile(suffix='.pkl', delete=False) as model_file:
                import pickle
                pickle.dump({'model': Mock(), 'config': Mock(), 'metrics': Mock()}, model_file)
                model_file.flush()
                
                version = versioning_service.create_version(
                    model_path=model_file.name,
                    model_type=ModelType.SKILL_CLASSIFIER
                )
            
            assert version.version_number == '1.0.0'
            
            # 3. Deploy version
            deploy_config = DeploymentConfig(
                strategy=DeploymentStrategy.BLUE_GREEN,
                target_environment=DeploymentStatus.PRODUCTION,
                approval_required=False
            )
            
            deploy_result = versioning_service.deploy_version(version.version_id, deploy_config)
            assert deploy_result["success"] is True
            
            # 4. Set up monitoring
            monitoring_service = ModelMonitoringService(mock_db)
            monitoring_service.monitoring_dir = Path(temp_dir) / "monitoring"
            monitoring_service.monitoring_dir.mkdir()
            monitoring_service.metrics_file = monitoring_service.monitoring_dir / "metrics.jsonl"
            monitoring_service.alerts_file = monitoring_service.monitoring_dir / "alerts.jsonl"
            
            monitor_config = MonitoringConfig(
                model_type=ModelType.SKILL_CLASSIFIER,
                metrics_to_monitor=[MetricType.ACCURACY, MetricType.LATENCY]
            )
            
            monitoring_service.start_monitoring(monitor_config)
            
            # 5. Record some metrics
            monitoring_service.record_prediction_metrics(
                model_type=ModelType.SKILL_CLASSIFIER,
                model_version=version.version_number,
                prediction_time_ms=150.0,
                prediction_accuracy=0.85
            )
            
            # 6. Collect feedback
            learning_service = ContinuousLearningService(mock_db)
            learning_service.feedback_dir = Path(temp_dir) / "feedback"
            learning_service.feedback_dir.mkdir()
            learning_service.feedback_log_file = learning_service.feedback_dir / "feedback_log.jsonl"
            
            feedback = FeedbackData(
                feedback_id='test-feedback',
                assessment_id='test-assessment',
                question_id='test-question',
                user_id='test-user',
                feedback_type=FeedbackType.EXPLICIT,
                feedback_content={'rating': 4},
                confidence_score=0.9,
                timestamp=datetime.utcnow()
            )
            
            feedback_result = await learning_service.collect_feedback(feedback)
            assert feedback_result["success"] is True
            
            # Clean up
            Path(model_file.name).unlink()
    
    def test_error_handling_and_recovery(self, mock_db):
        """Test error handling and recovery mechanisms"""
        
        training_service = MLTrainingService(mock_db)
        
        # Test training with invalid configuration
        invalid_config = TrainingConfig(
            model_type=ModelType.SKILL_CLASSIFIER,
            features=[],
            target="",
            test_size=1.5  # Invalid test size
        )
        
        with patch.object(training_service, '_extract_training_data') as mock_extract:
            mock_extract.side_effect = Exception("Database connection failed")
            
            result = training_service.create_training_pipeline(invalid_config)
        
        assert result["success"] is False
        assert "error" in result
    
    def test_performance_under_load(self, mock_db):
        """Test system performance under load"""
        
        monitoring_service = ModelMonitoringService(mock_db)
        
        # Simulate high-frequency metric recording
        start_time = datetime.utcnow()
        
        for i in range(1000):
            monitoring_service.record_prediction_metrics(
                model_type=ModelType.SKILL_CLASSIFIER,
                model_version='1.0.0',
                prediction_time_ms=100.0 + (i % 50),
                prediction_accuracy=0.8 + (i % 20) * 0.01
            )
        
        end_time = datetime.utcnow()
        processing_time = (end_time - start_time).total_seconds()
        
        # Should process 1000 metrics in reasonable time
        assert processing_time < 5.0  # Less than 5 seconds
        
        # Check metrics were stored
        assert len(monitoring_service.metrics_buffer[ModelType.SKILL_CLASSIFIER]) == 1000


if __name__ == "__main__":
    pytest.main([__file__])