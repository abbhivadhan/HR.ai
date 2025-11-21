"""
AI Model Training and Optimization Service

This service handles training pipelines for skill assessment models,
model evaluation, continuous learning, and performance monitoring.
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
import joblib

from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.ensemble import RandomForestClassifier, GradientBoostingRegressor
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, mean_squared_error
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.feature_extraction.text import TfidfVectorizer

from sqlalchemy.orm import Session
from ..models.assessment import Assessment, AssessmentResponse, Question
from ..models.user import User
from ..database import get_db


class ModelType(str, Enum):
    SKILL_CLASSIFIER = "skill_classifier"
    PERFORMANCE_PREDICTOR = "performance_predictor"
    DIFFICULTY_ESTIMATOR = "difficulty_estimator"
    BIAS_DETECTOR = "bias_detector"


@dataclass
class ModelMetrics:
    accuracy: float
    precision: float
    recall: float
    f1_score: float
    mse: Optional[float] = None
    training_time: float = 0.0
    validation_score: float = 0.0
    bias_score: float = 0.0


@dataclass
class TrainingConfig:
    model_type: ModelType
    features: List[str]
    target: str
    test_size: float = 0.2
    cv_folds: int = 5
    random_state: int = 42
    hyperparameters: Dict[str, Any] = None


class MLTrainingService:
    def __init__(self, db: Session):
        self.db = db
        self.logger = logging.getLogger(__name__)
        self.models_dir = Path("models")
        self.models_dir.mkdir(exist_ok=True)
        
        # Initialize feature extractors
        self.text_vectorizer = TfidfVectorizer(max_features=1000, stop_words='english')
        self.scaler = StandardScaler()
        self.label_encoders = {}
        
    def create_training_pipeline(self, config: TrainingConfig) -> Dict[str, Any]:
        """Create and execute a complete training pipeline"""
        
        self.logger.info(f"Starting training pipeline for {config.model_type}")
        
        try:
            # Extract training data
            training_data = self._extract_training_data(config)
            
            if len(training_data) < 50:  # Minimum data requirement
                raise ValueError(f"Insufficient training data: {len(training_data)} samples")
            
            # Prepare features and targets
            X, y = self._prepare_features_and_targets(training_data, config)
            
            # Split data
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=config.test_size, random_state=config.random_state
            )
            
            # Train model
            model, training_time = self._train_model(X_train, y_train, config)
            
            # Evaluate model
            metrics = self._evaluate_model(model, X_test, y_test, config)
            metrics.training_time = training_time
            
            # Perform bias detection
            bias_results = self._detect_bias(model, X_test, y_test, training_data)
            metrics.bias_score = bias_results['overall_bias_score']
            
            # Save model
            model_path = self._save_model(model, config, metrics)
            
            # Log training results
            self._log_training_results(config, metrics, model_path)
            
            return {
                "success": True,
                "model_type": config.model_type,
                "model_path": str(model_path),
                "metrics": metrics.__dict__,
                "bias_results": bias_results,
                "training_samples": len(training_data),
                "trained_at": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Training pipeline failed: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "model_type": config.model_type
            }
    
    def _extract_training_data(self, config: TrainingConfig) -> List[Dict[str, Any]]:
        """Extract training data from database"""
        
        # Get completed assessments with responses
        assessments = self.db.query(Assessment).filter(
            Assessment.status == "completed",
            Assessment.completed_at.isnot(None)
        ).all()
        
        training_data = []
        
        for assessment in assessments:
            # Get candidate info
            candidate = self.db.query(User).filter(User.id == assessment.candidate_id).first()
            if not candidate:
                continue
            
            # Get responses
            responses = self.db.query(AssessmentResponse).filter(
                AssessmentResponse.assessment_id == assessment.id
            ).all()
            
            for response in responses:
                question = self.db.query(Question).filter(
                    Question.id == response.question_id
                ).first()
                
                if not question:
                    continue
                
                # Create training sample
                sample = {
                    'assessment_id': str(assessment.id),
                    'candidate_id': str(assessment.candidate_id),
                    'question_id': str(response.question_id),
                    'question_type': question.question_type.value,
                    'difficulty_level': question.difficulty_level.value,
                    'category': question.category,
                    'max_points': question.max_points,
                    'points_earned': response.points_earned or 0,
                    'is_correct': response.is_correct or False,
                    'response_length': len(response.response_text or ''),
                    'time_spent': response.time_spent_seconds or 0,
                    'overall_score': assessment.percentage_score or 0,
                    'passed': assessment.passed or False,
                    'response_text': response.response_text or '',
                    'ai_score_breakdown': response.ai_score_breakdown or {},
                    'assessment_type': assessment.assessment_type.value,
                    'created_at': assessment.created_at
                }
                
                training_data.append(sample)
        
        self.logger.info(f"Extracted {len(training_data)} training samples")
        return training_data
    
    def _prepare_features_and_targets(self, training_data: List[Dict], config: TrainingConfig) -> Tuple[np.ndarray, np.ndarray]:
        """Prepare features and target variables"""
        
        df = pd.DataFrame(training_data)
        
        # Feature engineering based on model type
        if config.model_type == ModelType.SKILL_CLASSIFIER:
            features = self._extract_skill_features(df)
            targets = df['category'].values
            
            # Encode categorical targets
            if 'category' not in self.label_encoders:
                self.label_encoders['category'] = LabelEncoder()
                targets = self.label_encoders['category'].fit_transform(targets)
            else:
                targets = self.label_encoders['category'].transform(targets)
                
        elif config.model_type == ModelType.PERFORMANCE_PREDICTOR:
            features = self._extract_performance_features(df)
            targets = df['points_earned'].values
            
        elif config.model_type == ModelType.DIFFICULTY_ESTIMATOR:
            features = self._extract_difficulty_features(df)
            targets = df['difficulty_level'].values
            
            # Encode difficulty levels
            difficulty_mapping = {'beginner': 1, 'intermediate': 2, 'advanced': 3, 'expert': 4}
            targets = np.array([difficulty_mapping.get(d, 2) for d in targets])
            
        else:  # BIAS_DETECTOR
            features = self._extract_bias_features(df)
            targets = df['is_correct'].astype(int).values
        
        # Scale numerical features
        features = self.scaler.fit_transform(features)
        
        return features, targets
    
    def _extract_skill_features(self, df: pd.DataFrame) -> np.ndarray:
        """Extract features for skill classification"""
        
        # Text features from responses
        text_features = self.text_vectorizer.fit_transform(df['response_text'].fillna(''))
        
        # Numerical features
        numerical_features = df[[
            'max_points', 'points_earned', 'response_length', 
            'time_spent', 'overall_score'
        ]].fillna(0).values
        
        # Categorical features (one-hot encoded)
        question_type_dummies = pd.get_dummies(df['question_type']).values
        difficulty_dummies = pd.get_dummies(df['difficulty_level']).values
        
        # Combine all features
        features = np.hstack([
            text_features.toarray(),
            numerical_features,
            question_type_dummies,
            difficulty_dummies
        ])
        
        return features
    
    def _extract_performance_features(self, df: pd.DataFrame) -> np.ndarray:
        """Extract features for performance prediction"""
        
        # Response quality features
        df['response_quality'] = df['response_length'] / (df['max_points'] + 1)
        df['time_efficiency'] = df['points_earned'] / (df['time_spent'] + 1)
        
        # AI score features
        ai_scores = pd.json_normalize(df['ai_score_breakdown'].fillna({}))
        ai_scores = ai_scores.fillna(0)
        
        # Combine features
        features = pd.concat([
            df[['max_points', 'response_length', 'time_spent', 'response_quality', 'time_efficiency']],
            pd.get_dummies(df['question_type']),
            pd.get_dummies(df['difficulty_level']),
            ai_scores
        ], axis=1).fillna(0).values
        
        return features
    
    def _extract_difficulty_features(self, df: pd.DataFrame) -> np.ndarray:
        """Extract features for difficulty estimation"""
        
        # Question characteristics
        df['avg_score'] = df.groupby('question_id')['points_earned'].transform('mean')
        df['success_rate'] = df.groupby('question_id')['is_correct'].transform('mean')
        df['avg_time'] = df.groupby('question_id')['time_spent'].transform('mean')
        
        features = df[[
            'max_points', 'avg_score', 'success_rate', 'avg_time', 'response_length'
        ]].fillna(0).values
        
        return features
    
    def _extract_bias_features(self, df: pd.DataFrame) -> np.ndarray:
        """Extract features for bias detection"""
        
        # Performance features by demographic groups (if available)
        features = df[[
            'points_earned', 'time_spent', 'response_length', 'overall_score'
        ]].fillna(0).values
        
        # Add question type and difficulty as potential bias sources
        categorical_features = np.hstack([
            pd.get_dummies(df['question_type']).values,
            pd.get_dummies(df['difficulty_level']).values,
            pd.get_dummies(df['category']).values
        ])
        
        return np.hstack([features, categorical_features])
    
    def _train_model(self, X_train: np.ndarray, y_train: np.ndarray, config: TrainingConfig) -> Tuple[Any, float]:
        """Train the model based on configuration"""
        
        start_time = datetime.utcnow()
        
        # Select model based on type
        if config.model_type == ModelType.SKILL_CLASSIFIER:
            model = RandomForestClassifier(
                n_estimators=100,
                random_state=config.random_state,
                **(config.hyperparameters or {})
            )
        elif config.model_type == ModelType.PERFORMANCE_PREDICTOR:
            model = GradientBoostingRegressor(
                n_estimators=100,
                random_state=config.random_state,
                **(config.hyperparameters or {})
            )
        elif config.model_type == ModelType.DIFFICULTY_ESTIMATOR:
            model = RandomForestClassifier(
                n_estimators=100,
                random_state=config.random_state,
                **(config.hyperparameters or {})
            )
        else:  # BIAS_DETECTOR
            model = LogisticRegression(
                random_state=config.random_state,
                **(config.hyperparameters or {})
            )
        
        # Train model
        model.fit(X_train, y_train)
        
        training_time = (datetime.utcnow() - start_time).total_seconds()
        
        return model, training_time
    
    def _evaluate_model(self, model: Any, X_test: np.ndarray, y_test: np.ndarray, config: TrainingConfig) -> ModelMetrics:
        """Evaluate model performance"""
        
        predictions = model.predict(X_test)
        
        if config.model_type in [ModelType.SKILL_CLASSIFIER, ModelType.DIFFICULTY_ESTIMATOR, ModelType.BIAS_DETECTOR]:
            # Classification metrics
            accuracy = accuracy_score(y_test, predictions)
            precision = precision_score(y_test, predictions, average='weighted', zero_division=0)
            recall = recall_score(y_test, predictions, average='weighted', zero_division=0)
            f1 = f1_score(y_test, predictions, average='weighted', zero_division=0)
            
            return ModelMetrics(
                accuracy=accuracy,
                precision=precision,
                recall=recall,
                f1_score=f1
            )
        else:
            # Regression metrics
            mse = mean_squared_error(y_test, predictions)
            
            # Convert to classification-like metrics for consistency
            # Use correlation as accuracy proxy
            correlation = np.corrcoef(y_test, predictions)[0, 1]
            accuracy = max(0, correlation)
            
            return ModelMetrics(
                accuracy=accuracy,
                precision=accuracy,  # Use correlation as proxy
                recall=accuracy,
                f1_score=accuracy,
                mse=mse
            )
    
    def _detect_bias(self, model: Any, X_test: np.ndarray, y_test: np.ndarray, training_data: List[Dict]) -> Dict[str, Any]:
        """Detect potential bias in model predictions"""
        
        predictions = model.predict(X_test)
        
        # Calculate overall bias metrics
        bias_results = {
            'overall_bias_score': 0.0,
            'category_bias': {},
            'difficulty_bias': {},
            'question_type_bias': {},
            'recommendations': []
        }
        
        try:
            df = pd.DataFrame(training_data[-len(X_test):])  # Match test data
            
            # Check bias by category
            for category in df['category'].unique():
                mask = df['category'] == category
                if mask.sum() > 5:  # Minimum samples
                    category_accuracy = accuracy_score(y_test[mask], predictions[mask])
                    bias_results['category_bias'][category] = float(category_accuracy)
            
            # Check bias by difficulty
            for difficulty in df['difficulty_level'].unique():
                mask = df['difficulty_level'] == difficulty
                if mask.sum() > 5:
                    difficulty_accuracy = accuracy_score(y_test[mask], predictions[mask])
                    bias_results['difficulty_bias'][difficulty] = float(difficulty_accuracy)
            
            # Calculate overall bias score (standard deviation of group accuracies)
            all_accuracies = list(bias_results['category_bias'].values()) + list(bias_results['difficulty_bias'].values())
            if all_accuracies:
                bias_results['overall_bias_score'] = float(np.std(all_accuracies))
                
                # Generate recommendations
                if bias_results['overall_bias_score'] > 0.1:
                    bias_results['recommendations'].append("High bias detected across categories/difficulties")
                    bias_results['recommendations'].append("Consider collecting more balanced training data")
                    bias_results['recommendations'].append("Review question design for fairness")
        
        except Exception as e:
            self.logger.warning(f"Bias detection failed: {str(e)}")
            bias_results['error'] = str(e)
        
        return bias_results
    
    def _save_model(self, model: Any, config: TrainingConfig, metrics: ModelMetrics) -> Path:
        """Save trained model with metadata"""
        
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        model_filename = f"{config.model_type}_{timestamp}.pkl"
        model_path = self.models_dir / model_filename
        
        # Save model and metadata
        model_data = {
            'model': model,
            'config': config,
            'metrics': metrics,
            'scaler': self.scaler,
            'text_vectorizer': self.text_vectorizer,
            'label_encoders': self.label_encoders,
            'created_at': datetime.utcnow(),
            'version': '1.0'
        }
        
        with open(model_path, 'wb') as f:
            pickle.dump(model_data, f)
        
        self.logger.info(f"Model saved to {model_path}")
        return model_path
    
    def _log_training_results(self, config: TrainingConfig, metrics: ModelMetrics, model_path: Path):
        """Log training results for monitoring"""
        
        log_entry = {
            'timestamp': datetime.utcnow().isoformat(),
            'model_type': config.model_type,
            'model_path': str(model_path),
            'metrics': metrics.__dict__,
            'config': config.__dict__
        }
        
        # Save to training log file
        log_file = self.models_dir / 'training_log.jsonl'
        with open(log_file, 'a') as f:
            f.write(json.dumps(log_entry) + '\n')
        
        self.logger.info(f"Training completed - Accuracy: {metrics.accuracy:.3f}, F1: {metrics.f1_score:.3f}")