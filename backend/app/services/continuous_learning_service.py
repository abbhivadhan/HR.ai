"""
Continuous Learning Service

This service implements continuous learning from user feedback,
online learning capabilities, and adaptive model improvement.
"""

import json
import pickle
import numpy as np
import pandas as pd
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
from pathlib import Path
import logging
from dataclasses import dataclass
from enum import Enum
import asyncio

from sklearn.base import clone
from sklearn.metrics import accuracy_score
from sqlalchemy.orm import Session

from ..models.assessment import Assessment, AssessmentResponse, Question
from ..models.user import User
from .ml_training_service import MLTrainingService, ModelType, TrainingConfig
from .model_evaluation_service import ModelEvaluationService, ValidationConfig, ValidationMethod


class FeedbackType(str, Enum):
    EXPLICIT = "explicit"  # Direct user feedback
    IMPLICIT = "implicit"  # Inferred from behavior
    EXPERT = "expert"      # Expert review/correction


class LearningStrategy(str, Enum):
    INCREMENTAL = "incremental"  # Update existing model
    PERIODIC_RETRAIN = "periodic_retrain"  # Full retraining
    ENSEMBLE = "ensemble"  # Combine models
    ACTIVE_LEARNING = "active_learning"  # Query for labels


@dataclass
class FeedbackData:
    feedback_id: str
    assessment_id: str
    question_id: str
    user_id: str
    feedback_type: FeedbackType
    feedback_content: Dict[str, Any]
    confidence_score: float
    timestamp: datetime


@dataclass
class LearningConfig:
    strategy: LearningStrategy
    update_threshold: int = 100  # Minimum feedback samples
    retrain_interval_days: int = 7
    confidence_threshold: float = 0.8
    max_model_age_days: int = 30


class ContinuousLearningService:
    def __init__(self, db: Session):
        self.db = db
        self.logger = logging.getLogger(__name__)
        self.feedback_dir = Path("feedback")
        self.feedback_dir.mkdir(exist_ok=True)
        
        self.training_service = MLTrainingService(db)
        self.evaluation_service = ModelEvaluationService(db)
        
        # Feedback storage
        self.feedback_buffer = []
        self.feedback_log_file = self.feedback_dir / "feedback_log.jsonl"
    
    async def collect_feedback(self, feedback_data: FeedbackData) -> Dict[str, Any]:
        """Collect and process user feedback"""
        
        self.logger.info(f"Collecting feedback: {feedback_data.feedback_type} for assessment {feedback_data.assessment_id}")
        
        try:
            # Validate feedback
            if not self._validate_feedback(feedback_data):
                return {"success": False, "error": "Invalid feedback data"}
            
            # Store feedback
            self._store_feedback(feedback_data)
            
            # Add to buffer for processing
            self.feedback_buffer.append(feedback_data)
            
            # Check if we should trigger learning update
            should_update = await self._should_trigger_update(feedback_data)
            
            result = {
                "success": True,
                "feedback_id": feedback_data.feedback_id,
                "stored_at": datetime.utcnow().isoformat(),
                "buffer_size": len(self.feedback_buffer)
            }
            
            if should_update:
                # Trigger asynchronous learning update
                asyncio.create_task(self._trigger_learning_update(feedback_data))
                result["learning_triggered"] = True
            
            return result
            
        except Exception as e:
            self.logger.error(f"Failed to collect feedback: {str(e)}")
            return {"success": False, "error": str(e)}
    
    async def process_implicit_feedback(self, assessment_id: str) -> Dict[str, Any]:
        """Process implicit feedback from assessment completion"""
        
        self.logger.info(f"Processing implicit feedback for assessment {assessment_id}")
        
        try:
            # Get assessment data
            assessment = self.db.query(Assessment).filter(Assessment.id == assessment_id).first()
            if not assessment:
                return {"success": False, "error": "Assessment not found"}
            
            # Extract implicit feedback signals
            implicit_signals = self._extract_implicit_signals(assessment)
            
            # Create feedback data
            for signal in implicit_signals:
                feedback_data = FeedbackData(
                    feedback_id=f"implicit_{assessment_id}_{signal['type']}",
                    assessment_id=assessment_id,
                    question_id=signal.get('question_id', ''),
                    user_id=str(assessment.candidate_id),
                    feedback_type=FeedbackType.IMPLICIT,
                    feedback_content=signal,
                    confidence_score=signal.get('confidence', 0.7),
                    timestamp=datetime.utcnow()
                )
                
                await self.collect_feedback(feedback_data)
            
            return {
                "success": True,
                "signals_processed": len(implicit_signals),
                "assessment_id": assessment_id
            }
            
        except Exception as e:
            self.logger.error(f"Failed to process implicit feedback: {str(e)}")
            return {"success": False, "error": str(e)}
    
    async def update_model_with_feedback(self, model_type: ModelType, config: LearningConfig) -> Dict[str, Any]:
        """Update model using collected feedback"""
        
        self.logger.info(f"Updating {model_type} model with feedback")
        
        try:
            # Get relevant feedback
            feedback_data = self._get_feedback_for_model(model_type)
            
            if len(feedback_data) < config.update_threshold:
                return {
                    "success": False,
                    "error": f"Insufficient feedback data: {len(feedback_data)} < {config.update_threshold}"
                }
            
            # Load current model
            current_model_path = self._get_latest_model_path(model_type)
            if not current_model_path:
                return {"success": False, "error": "No existing model found"}
            
            # Apply learning strategy
            if config.strategy == LearningStrategy.INCREMENTAL:
                result = await self._incremental_update(current_model_path, feedback_data, config)
            elif config.strategy == LearningStrategy.PERIODIC_RETRAIN:
                result = await self._periodic_retrain(model_type, feedback_data, config)
            elif config.strategy == LearningStrategy.ENSEMBLE:
                result = await self._ensemble_update(current_model_path, feedback_data, config)
            else:
                result = await self._active_learning_update(current_model_path, feedback_data, config)
            
            # Clear processed feedback from buffer
            self._clear_processed_feedback(feedback_data)
            
            return result
            
        except Exception as e:
            self.logger.error(f"Failed to update model with feedback: {str(e)}")
            return {"success": False, "error": str(e)}
    
    async def monitor_model_performance(self, model_type: ModelType) -> Dict[str, Any]:
        """Monitor model performance and trigger updates if needed"""
        
        self.logger.info(f"Monitoring performance for {model_type} model")
        
        try:
            # Get latest model
            model_path = self._get_latest_model_path(model_type)
            if not model_path:
                return {"success": False, "error": "No model found"}
            
            # Check model age
            model_age = self._get_model_age(model_path)
            
            # Monitor performance drift
            drift_results = self.evaluation_service.monitor_model_drift(model_path, days_back=7)
            
            # Check feedback volume
            recent_feedback = self._get_recent_feedback(model_type, days_back=7)
            
            monitoring_results = {
                "model_type": model_type,
                "model_path": model_path,
                "model_age_days": model_age,
                "drift_detected": drift_results.get('drift_detected', False),
                "recent_feedback_count": len(recent_feedback),
                "performance_metrics": drift_results.get('current_metrics', {}),
                "recommendations": []
            }
            
            # Generate recommendations
            if model_age > 30:
                monitoring_results["recommendations"].append("Model is over 30 days old, consider retraining")
            
            if drift_results.get('drift_detected'):
                monitoring_results["recommendations"].append("Performance drift detected, update recommended")
            
            if len(recent_feedback) > 50:
                monitoring_results["recommendations"].append("Significant feedback available, consider incremental update")
            
            # Auto-trigger updates if conditions are met
            if (drift_results.get('drift_detected') or 
                model_age > 30 or 
                len(recent_feedback) > 100):
                
                config = LearningConfig(strategy=LearningStrategy.INCREMENTAL)
                update_result = await self.update_model_with_feedback(model_type, config)
                monitoring_results["auto_update_triggered"] = True
                monitoring_results["update_result"] = update_result
            
            return monitoring_results
            
        except Exception as e:
            self.logger.error(f"Failed to monitor model performance: {str(e)}")
            return {"success": False, "error": str(e)}
    
    def _validate_feedback(self, feedback_data: FeedbackData) -> bool:
        """Validate feedback data"""
        
        required_fields = ['feedback_id', 'assessment_id', 'user_id', 'feedback_type']
        
        for field in required_fields:
            if not getattr(feedback_data, field):
                return False
        
        if feedback_data.confidence_score < 0 or feedback_data.confidence_score > 1:
            return False
        
        return True
    
    def _store_feedback(self, feedback_data: FeedbackData):
        """Store feedback to persistent storage"""
        
        feedback_record = {
            "feedback_id": feedback_data.feedback_id,
            "assessment_id": feedback_data.assessment_id,
            "question_id": feedback_data.question_id,
            "user_id": feedback_data.user_id,
            "feedback_type": feedback_data.feedback_type,
            "feedback_content": feedback_data.feedback_content,
            "confidence_score": feedback_data.confidence_score,
            "timestamp": feedback_data.timestamp.isoformat()
        }
        
        # Append to log file
        with open(self.feedback_log_file, 'a') as f:
            f.write(json.dumps(feedback_record) + '\n')
    
    async def _should_trigger_update(self, feedback_data: FeedbackData) -> bool:
        """Determine if feedback should trigger a learning update"""
        
        # High confidence explicit feedback triggers immediate update
        if (feedback_data.feedback_type == FeedbackType.EXPLICIT and 
            feedback_data.confidence_score > 0.9):
            return True
        
        # Expert feedback always triggers update
        if feedback_data.feedback_type == FeedbackType.EXPERT:
            return True
        
        # Check buffer size
        if len(self.feedback_buffer) >= 100:
            return True
        
        return False
    
    async def _trigger_learning_update(self, feedback_data: FeedbackData):
        """Trigger asynchronous learning update"""
        
        try:
            # Determine model type from feedback
            model_type = self._infer_model_type(feedback_data)
            
            if model_type:
                config = LearningConfig(strategy=LearningStrategy.INCREMENTAL)
                await self.update_model_with_feedback(model_type, config)
                
        except Exception as e:
            self.logger.error(f"Failed to trigger learning update: {str(e)}")
    
    def _extract_implicit_signals(self, assessment: Assessment) -> List[Dict[str, Any]]:
        """Extract implicit feedback signals from assessment"""
        
        signals = []
        
        # Time-based signals
        if assessment.started_at and assessment.completed_at:
            duration = (assessment.completed_at - assessment.started_at).total_seconds()
            expected_duration = assessment.duration_minutes * 60
            
            if duration < expected_duration * 0.5:
                signals.append({
                    "type": "completion_time",
                    "signal": "too_fast",
                    "value": duration,
                    "confidence": 0.8,
                    "interpretation": "Assessment completed unusually quickly"
                })
            elif duration > expected_duration * 1.5:
                signals.append({
                    "type": "completion_time",
                    "signal": "too_slow",
                    "value": duration,
                    "confidence": 0.7,
                    "interpretation": "Assessment took longer than expected"
                })
        
        # Performance-based signals
        if assessment.percentage_score is not None:
            if assessment.percentage_score < 30:
                signals.append({
                    "type": "performance",
                    "signal": "very_low_score",
                    "value": assessment.percentage_score,
                    "confidence": 0.9,
                    "interpretation": "Unusually low performance may indicate issues"
                })
            elif assessment.percentage_score > 95:
                signals.append({
                    "type": "performance",
                    "signal": "very_high_score",
                    "value": assessment.percentage_score,
                    "confidence": 0.8,
                    "interpretation": "Unusually high performance may indicate issues"
                })
        
        # Response pattern signals
        responses = self.db.query(AssessmentResponse).filter(
            AssessmentResponse.assessment_id == assessment.id
        ).all()
        
        if responses:
            # Check for patterns in response times
            response_times = [r.time_spent_seconds for r in responses if r.time_spent_seconds]
            if response_times:
                avg_time = np.mean(response_times)
                std_time = np.std(response_times)
                
                if std_time < avg_time * 0.1:  # Very consistent timing
                    signals.append({
                        "type": "response_pattern",
                        "signal": "consistent_timing",
                        "value": std_time / avg_time,
                        "confidence": 0.6,
                        "interpretation": "Unusually consistent response timing"
                    })
        
        return signals
    
    def _get_feedback_for_model(self, model_type: ModelType) -> List[FeedbackData]:
        """Get feedback data relevant to a specific model type"""
        
        feedback_data = []
        
        try:
            with open(self.feedback_log_file, 'r') as f:
                for line in f:
                    record = json.loads(line.strip())
                    
                    # Convert back to FeedbackData
                    feedback = FeedbackData(
                        feedback_id=record['feedback_id'],
                        assessment_id=record['assessment_id'],
                        question_id=record['question_id'],
                        user_id=record['user_id'],
                        feedback_type=FeedbackType(record['feedback_type']),
                        feedback_content=record['feedback_content'],
                        confidence_score=record['confidence_score'],
                        timestamp=datetime.fromisoformat(record['timestamp'])
                    )
                    
                    # Filter by model type relevance
                    if self._is_feedback_relevant(feedback, model_type):
                        feedback_data.append(feedback)
                        
        except FileNotFoundError:
            pass
        
        return feedback_data
    
    def _is_feedback_relevant(self, feedback: FeedbackData, model_type: ModelType) -> bool:
        """Check if feedback is relevant to a model type"""
        
        # Simple mapping - in practice this would be more sophisticated
        feedback_content = feedback.feedback_content
        
        if model_type == ModelType.SKILL_CLASSIFIER:
            return 'skill' in str(feedback_content).lower()
        elif model_type == ModelType.PERFORMANCE_PREDICTOR:
            return 'performance' in str(feedback_content).lower()
        elif model_type == ModelType.DIFFICULTY_ESTIMATOR:
            return 'difficulty' in str(feedback_content).lower()
        
        return True  # Default to relevant
    
    def _get_latest_model_path(self, model_type: ModelType) -> Optional[str]:
        """Get path to the latest model of specified type"""
        
        models_dir = Path("models")
        if not models_dir.exists():
            return None
        
        # Find latest model file for this type
        pattern = f"{model_type}_*.pkl"
        model_files = list(models_dir.glob(pattern))
        
        if not model_files:
            return None
        
        # Sort by modification time and return latest
        latest_file = max(model_files, key=lambda f: f.stat().st_mtime)
        return str(latest_file)
    
    def _get_model_age(self, model_path: str) -> int:
        """Get model age in days"""
        
        model_file = Path(model_path)
        if not model_file.exists():
            return 999  # Very old if file doesn't exist
        
        modification_time = datetime.fromtimestamp(model_file.stat().st_mtime)
        age = (datetime.utcnow() - modification_time).days
        
        return age
    
    def _get_recent_feedback(self, model_type: ModelType, days_back: int = 7) -> List[FeedbackData]:
        """Get recent feedback for a model type"""
        
        cutoff_date = datetime.utcnow() - timedelta(days=days_back)
        all_feedback = self._get_feedback_for_model(model_type)
        
        recent_feedback = [
            f for f in all_feedback 
            if f.timestamp >= cutoff_date
        ]
        
        return recent_feedback
    
    async def _incremental_update(self, model_path: str, feedback_data: List[FeedbackData], config: LearningConfig) -> Dict[str, Any]:
        """Perform incremental model update"""
        
        self.logger.info(f"Performing incremental update with {len(feedback_data)} feedback samples")
        
        try:
            # Load existing model
            with open(model_path, 'rb') as f:
                model_data = pickle.load(f)
            
            model = model_data['model']
            training_config = model_data['config']
            
            # Prepare feedback data for training
            X_feedback, y_feedback = self._prepare_feedback_data(feedback_data, training_config)
            
            if len(X_feedback) == 0:
                return {"success": False, "error": "No usable feedback data"}
            
            # Perform incremental learning (if supported)
            if hasattr(model, 'partial_fit'):
                model.partial_fit(X_feedback, y_feedback)
            else:
                # Retrain with combined data
                original_data = self.training_service._extract_training_data(training_config)
                X_original, y_original = self.training_service._prepare_features_and_targets(original_data, training_config)
                
                # Combine original and feedback data
                X_combined = np.vstack([X_original, X_feedback])
                y_combined = np.hstack([y_original, y_feedback])
                
                # Retrain model
                model.fit(X_combined, y_combined)
            
            # Evaluate updated model
            validation_config = ValidationConfig(method=ValidationMethod.HOLDOUT)
            evaluation_results = self.evaluation_service.evaluate_model(model_path, validation_config)
            
            # Save updated model
            updated_model_path = self.training_service._save_model(model, training_config, evaluation_results.metrics)
            
            return {
                "success": True,
                "updated_model_path": str(updated_model_path),
                "feedback_samples_used": len(feedback_data),
                "new_metrics": evaluation_results.metrics.__dict__,
                "update_type": "incremental"
            }
            
        except Exception as e:
            self.logger.error(f"Incremental update failed: {str(e)}")
            return {"success": False, "error": str(e)}
    
    async def _periodic_retrain(self, model_type: ModelType, feedback_data: List[FeedbackData], config: LearningConfig) -> Dict[str, Any]:
        """Perform periodic full retraining"""
        
        self.logger.info(f"Performing periodic retrain for {model_type}")
        
        try:
            # Create new training configuration
            training_config = TrainingConfig(
                model_type=model_type,
                features=[],  # Will be determined automatically
                target="",    # Will be determined automatically
            )
            
            # Trigger full retraining
            training_result = self.training_service.create_training_pipeline(training_config)
            
            return {
                "success": training_result["success"],
                "retrain_result": training_result,
                "feedback_samples_available": len(feedback_data),
                "update_type": "periodic_retrain"
            }
            
        except Exception as e:
            self.logger.error(f"Periodic retrain failed: {str(e)}")
            return {"success": False, "error": str(e)}
    
    async def _ensemble_update(self, model_path: str, feedback_data: List[FeedbackData], config: LearningConfig) -> Dict[str, Any]:
        """Create ensemble model with feedback"""
        
        # Simplified ensemble approach - would be more sophisticated in practice
        return await self._incremental_update(model_path, feedback_data, config)
    
    async def _active_learning_update(self, model_path: str, feedback_data: List[FeedbackData], config: LearningConfig) -> Dict[str, Any]:
        """Perform active learning update"""
        
        # Simplified active learning - would implement uncertainty sampling in practice
        return await self._incremental_update(model_path, feedback_data, config)
    
    def _prepare_feedback_data(self, feedback_data: List[FeedbackData], training_config) -> Tuple[np.ndarray, np.ndarray]:
        """Prepare feedback data for model training"""
        
        # Convert feedback to training format
        training_samples = []
        
        for feedback in feedback_data:
            # Get assessment and response data
            assessment = self.db.query(Assessment).filter(Assessment.id == feedback.assessment_id).first()
            if not assessment:
                continue
            
            # Create training sample from feedback
            sample = {
                'assessment_id': feedback.assessment_id,
                'question_id': feedback.question_id,
                'feedback_content': feedback.feedback_content,
                'confidence_score': feedback.confidence_score,
                # Add other relevant fields based on feedback content
            }
            
            training_samples.append(sample)
        
        if not training_samples:
            return np.array([]), np.array([])
        
        # Use training service to prepare features
        X, y = self.training_service._prepare_features_and_targets(training_samples, training_config)
        
        return X, y
    
    def _clear_processed_feedback(self, processed_feedback: List[FeedbackData]):
        """Clear processed feedback from buffer"""
        
        processed_ids = {f.feedback_id for f in processed_feedback}
        self.feedback_buffer = [
            f for f in self.feedback_buffer 
            if f.feedback_id not in processed_ids
        ]
    
    def _infer_model_type(self, feedback_data: FeedbackData) -> Optional[ModelType]:
        """Infer which model type the feedback applies to"""
        
        content = str(feedback_data.feedback_content).lower()
        
        if 'skill' in content or 'category' in content:
            return ModelType.SKILL_CLASSIFIER
        elif 'performance' in content or 'score' in content:
            return ModelType.PERFORMANCE_PREDICTOR
        elif 'difficulty' in content or 'hard' in content or 'easy' in content:
            return ModelType.DIFFICULTY_ESTIMATOR
        elif 'bias' in content or 'fair' in content:
            return ModelType.BIAS_DETECTOR
        
        return None  # Cannot infer