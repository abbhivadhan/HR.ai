"""
Model Evaluation and Validation Framework

This service provides comprehensive model evaluation, validation,
and performance monitoring capabilities for AI models.
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

from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    mean_squared_error, mean_absolute_error, r2_score,
    confusion_matrix, classification_report, roc_auc_score
)
from sklearn.model_selection import cross_val_score, learning_curve
try:
    import matplotlib.pyplot as plt
    import seaborn as sns
    HAS_PLOTTING = True
except ImportError:
    HAS_PLOTTING = False

from sqlalchemy.orm import Session
from .ml_training_service import ModelType, ModelMetrics


class ValidationMethod(str, Enum):
    CROSS_VALIDATION = "cross_validation"
    HOLDOUT = "holdout"
    TIME_SERIES_SPLIT = "time_series_split"
    BOOTSTRAP = "bootstrap"


@dataclass
class ValidationConfig:
    method: ValidationMethod
    n_splits: int = 5
    test_size: float = 0.2
    n_bootstrap: int = 100
    random_state: int = 42


@dataclass
class EvaluationResults:
    model_type: ModelType
    validation_method: ValidationMethod
    metrics: Dict[str, float]
    confidence_intervals: Dict[str, Tuple[float, float]]
    feature_importance: Dict[str, float]
    learning_curves: Dict[str, List[float]]
    confusion_matrix: Optional[np.ndarray] = None
    classification_report: Optional[Dict] = None
    recommendations: List[str] = None


class ModelEvaluationService:
    def __init__(self, db: Session):
        self.db = db
        self.logger = logging.getLogger(__name__)
        self.models_dir = Path("models")
        self.evaluation_dir = Path("evaluations")
        self.evaluation_dir.mkdir(exist_ok=True)
        
    def evaluate_model(self, model_path: str, validation_config: ValidationConfig) -> EvaluationResults:
        """Comprehensive model evaluation"""
        
        self.logger.info(f"Starting model evaluation for {model_path}")
        
        try:
            # Load model
            model_data = self._load_model(model_path)
            model = model_data['model']
            config = model_data['config']
            
            # Load evaluation data
            X, y = self._load_evaluation_data(config)
            
            # Perform validation
            validation_results = self._perform_validation(model, X, y, validation_config)
            
            # Calculate feature importance
            feature_importance = self._calculate_feature_importance(model, X, config)
            
            # Generate learning curves
            learning_curves = self._generate_learning_curves(model, X, y, validation_config)
            
            # Generate recommendations
            recommendations = self._generate_recommendations(validation_results, config)
            
            # Create evaluation results
            results = EvaluationResults(
                model_type=config.model_type,
                validation_method=validation_config.method,
                metrics=validation_results['metrics'],
                confidence_intervals=validation_results['confidence_intervals'],
                feature_importance=feature_importance,
                learning_curves=learning_curves,
                confusion_matrix=validation_results.get('confusion_matrix'),
                classification_report=validation_results.get('classification_report'),
                recommendations=recommendations
            )
            
            # Save evaluation results
            self._save_evaluation_results(results, model_path)
            
            return results
            
        except Exception as e:
            self.logger.error(f"Model evaluation failed: {str(e)}")
            raise
    
    def compare_models(self, model_paths: List[str], validation_config: ValidationConfig) -> Dict[str, Any]:
        """Compare multiple models"""
        
        self.logger.info(f"Comparing {len(model_paths)} models")
        
        comparison_results = {
            'models': {},
            'best_model': None,
            'comparison_metrics': {},
            'recommendations': []
        }
        
        best_score = -1
        best_model_path = None
        
        for model_path in model_paths:
            try:
                results = self.evaluate_model(model_path, validation_config)
                
                comparison_results['models'][model_path] = {
                    'metrics': results.metrics,
                    'model_type': results.model_type,
                    'recommendations': results.recommendations
                }
                
                # Determine best model based on F1 score or accuracy
                primary_metric = results.metrics.get('f1_score', results.metrics.get('accuracy', 0))
                if primary_metric > best_score:
                    best_score = primary_metric
                    best_model_path = model_path
                    
            except Exception as e:
                self.logger.error(f"Failed to evaluate model {model_path}: {str(e)}")
                comparison_results['models'][model_path] = {'error': str(e)}
        
        comparison_results['best_model'] = best_model_path
        
        # Generate comparison insights
        if len(comparison_results['models']) > 1:
            comparison_results['recommendations'] = self._generate_comparison_recommendations(
                comparison_results['models']
            )
        
        return comparison_results
    
    def validate_model_fairness(self, model_path: str, protected_attributes: List[str]) -> Dict[str, Any]:
        """Validate model fairness across protected attributes"""
        
        self.logger.info(f"Validating fairness for model {model_path}")
        
        try:
            # Load model and data
            model_data = self._load_model(model_path)
            model = model_data['model']
            config = model_data['config']
            
            X, y = self._load_evaluation_data(config)
            predictions = model.predict(X)
            
            # Calculate fairness metrics
            fairness_results = {
                'overall_accuracy': float(accuracy_score(y, predictions)),
                'group_fairness': {},
                'individual_fairness': {},
                'fairness_score': 0.0,
                'recommendations': []
            }
            
            # Group fairness analysis (if demographic data available)
            # This would require additional demographic data collection
            fairness_results['group_fairness'] = {
                'note': 'Group fairness analysis requires demographic data collection',
                'demographic_parity': 'Not available',
                'equalized_odds': 'Not available'
            }
            
            # Individual fairness (consistency of similar inputs)
            individual_fairness_score = self._calculate_individual_fairness(model, X, y)
            fairness_results['individual_fairness'] = {
                'consistency_score': individual_fairness_score,
                'interpretation': 'Higher scores indicate more consistent predictions for similar inputs'
            }
            
            # Overall fairness score
            fairness_results['fairness_score'] = individual_fairness_score
            
            # Generate fairness recommendations
            if individual_fairness_score < 0.8:
                fairness_results['recommendations'].append(
                    "Model shows inconsistent predictions for similar inputs"
                )
                fairness_results['recommendations'].append(
                    "Consider additional training data or feature engineering"
                )
            
            return fairness_results
            
        except Exception as e:
            self.logger.error(f"Fairness validation failed: {str(e)}")
            return {'error': str(e)}
    
    def monitor_model_drift(self, model_path: str, days_back: int = 30) -> Dict[str, Any]:
        """Monitor model performance drift over time"""
        
        self.logger.info(f"Monitoring drift for model {model_path}")
        
        try:
            # Load model
            model_data = self._load_model(model_path)
            model = model_data['model']
            config = model_data['config']
            
            # Get recent data
            recent_data = self._get_recent_data(days_back)
            
            if len(recent_data) < 10:
                return {
                    'error': 'Insufficient recent data for drift analysis',
                    'samples': len(recent_data)
                }
            
            # Prepare data
            X, y = self._prepare_drift_data(recent_data, config)
            
            # Calculate current performance
            predictions = model.predict(X)
            current_metrics = self._calculate_metrics(y, predictions, config.model_type)
            
            # Compare with baseline (training metrics)
            baseline_metrics = model_data['metrics'].__dict__
            
            # Calculate drift scores
            drift_results = {
                'current_metrics': current_metrics,
                'baseline_metrics': baseline_metrics,
                'drift_scores': {},
                'drift_detected': False,
                'recommendations': []
            }
            
            # Calculate drift for each metric
            for metric_name in ['accuracy', 'precision', 'recall', 'f1_score']:
                if metric_name in current_metrics and metric_name in baseline_metrics:
                    current_value = current_metrics[metric_name]
                    baseline_value = baseline_metrics[metric_name]
                    
                    drift_score = abs(current_value - baseline_value) / baseline_value
                    drift_results['drift_scores'][metric_name] = drift_score
                    
                    # Flag significant drift (>10% change)
                    if drift_score > 0.1:
                        drift_results['drift_detected'] = True
            
            # Generate recommendations
            if drift_results['drift_detected']:
                drift_results['recommendations'].append("Significant performance drift detected")
                drift_results['recommendations'].append("Consider retraining the model with recent data")
                drift_results['recommendations'].append("Review data quality and feature distributions")
            
            return drift_results
            
        except Exception as e:
            self.logger.error(f"Drift monitoring failed: {str(e)}")
            return {'error': str(e)}
    
    def _load_model(self, model_path: str) -> Dict[str, Any]:
        """Load model from file"""
        with open(model_path, 'rb') as f:
            return pickle.load(f)
    
    def _load_evaluation_data(self, config) -> Tuple[np.ndarray, np.ndarray]:
        """Load data for evaluation"""
        # This would use the same data extraction logic as training
        # For now, return dummy data
        from .ml_training_service import MLTrainingService
        
        training_service = MLTrainingService(self.db)
        training_data = training_service._extract_training_data(config)
        
        if len(training_data) == 0:
            raise ValueError("No evaluation data available")
        
        X, y = training_service._prepare_features_and_targets(training_data, config)
        return X, y
    
    def _perform_validation(self, model, X: np.ndarray, y: np.ndarray, config: ValidationConfig) -> Dict[str, Any]:
        """Perform model validation"""
        
        if config.method == ValidationMethod.CROSS_VALIDATION:
            return self._cross_validation(model, X, y, config)
        elif config.method == ValidationMethod.HOLDOUT:
            return self._holdout_validation(model, X, y, config)
        else:
            # Default to cross-validation
            return self._cross_validation(model, X, y, config)
    
    def _cross_validation(self, model, X: np.ndarray, y: np.ndarray, config: ValidationConfig) -> Dict[str, Any]:
        """Perform cross-validation"""
        
        # Perform cross-validation for different metrics
        cv_scores = {}
        
        # Accuracy
        accuracy_scores = cross_val_score(model, X, y, cv=config.n_splits, scoring='accuracy')
        cv_scores['accuracy'] = {
            'mean': float(np.mean(accuracy_scores)),
            'std': float(np.std(accuracy_scores)),
            'scores': accuracy_scores.tolist()
        }
        
        # F1 score (for classification)
        try:
            f1_scores = cross_val_score(model, X, y, cv=config.n_splits, scoring='f1_weighted')
            cv_scores['f1_score'] = {
                'mean': float(np.mean(f1_scores)),
                'std': float(np.std(f1_scores)),
                'scores': f1_scores.tolist()
            }
        except:
            pass
        
        # Calculate confidence intervals
        confidence_intervals = {}
        for metric, scores in cv_scores.items():
            mean_score = scores['mean']
            std_score = scores['std']
            ci_lower = mean_score - 1.96 * std_score / np.sqrt(config.n_splits)
            ci_upper = mean_score + 1.96 * std_score / np.sqrt(config.n_splits)
            confidence_intervals[metric] = (ci_lower, ci_upper)
        
        return {
            'metrics': {metric: scores['mean'] for metric, scores in cv_scores.items()},
            'confidence_intervals': confidence_intervals,
            'cv_scores': cv_scores
        }
    
    def _holdout_validation(self, model, X: np.ndarray, y: np.ndarray, config: ValidationConfig) -> Dict[str, Any]:
        """Perform holdout validation"""
        
        from sklearn.model_selection import train_test_split
        
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=config.test_size, random_state=config.random_state
        )
        
        # Train on training set
        model.fit(X_train, y_train)
        
        # Predict on test set
        predictions = model.predict(X_test)
        
        # Calculate metrics
        metrics = self._calculate_metrics(y_test, predictions, None)
        
        # Generate confusion matrix for classification
        confusion_mat = None
        classification_rep = None
        
        try:
            confusion_mat = confusion_matrix(y_test, predictions)
            classification_rep = classification_report(y_test, predictions, output_dict=True)
        except:
            pass
        
        return {
            'metrics': metrics,
            'confidence_intervals': {},  # Not applicable for holdout
            'confusion_matrix': confusion_mat,
            'classification_report': classification_rep
        }
    
    def _calculate_metrics(self, y_true: np.ndarray, y_pred: np.ndarray, model_type: Optional[ModelType]) -> Dict[str, float]:
        """Calculate evaluation metrics"""
        
        metrics = {}
        
        try:
            # Classification metrics
            metrics['accuracy'] = float(accuracy_score(y_true, y_pred))
            metrics['precision'] = float(precision_score(y_true, y_pred, average='weighted', zero_division=0))
            metrics['recall'] = float(recall_score(y_true, y_pred, average='weighted', zero_division=0))
            metrics['f1_score'] = float(f1_score(y_true, y_pred, average='weighted', zero_division=0))
        except:
            pass
        
        try:
            # Regression metrics
            metrics['mse'] = float(mean_squared_error(y_true, y_pred))
            metrics['mae'] = float(mean_absolute_error(y_true, y_pred))
            metrics['r2'] = float(r2_score(y_true, y_pred))
        except:
            pass
        
        return metrics
    
    def _calculate_feature_importance(self, model, X: np.ndarray, config) -> Dict[str, float]:
        """Calculate feature importance"""
        
        try:
            if hasattr(model, 'feature_importances_'):
                importances = model.feature_importances_
                
                # Create feature names (simplified)
                feature_names = [f"feature_{i}" for i in range(len(importances))]
                
                # Sort by importance
                importance_dict = dict(zip(feature_names, importances))
                sorted_importance = dict(sorted(importance_dict.items(), key=lambda x: x[1], reverse=True))
                
                # Return top 10 features
                return dict(list(sorted_importance.items())[:10])
            
        except Exception as e:
            self.logger.warning(f"Could not calculate feature importance: {str(e)}")
        
        return {}
    
    def _generate_learning_curves(self, model, X: np.ndarray, y: np.ndarray, config: ValidationConfig) -> Dict[str, List[float]]:
        """Generate learning curves"""
        
        try:
            train_sizes, train_scores, val_scores = learning_curve(
                model, X, y, cv=3, n_jobs=-1, 
                train_sizes=np.linspace(0.1, 1.0, 10)
            )
            
            return {
                'train_sizes': train_sizes.tolist(),
                'train_scores_mean': np.mean(train_scores, axis=1).tolist(),
                'train_scores_std': np.std(train_scores, axis=1).tolist(),
                'val_scores_mean': np.mean(val_scores, axis=1).tolist(),
                'val_scores_std': np.std(val_scores, axis=1).tolist()
            }
            
        except Exception as e:
            self.logger.warning(f"Could not generate learning curves: {str(e)}")
            return {}
    
    def _generate_recommendations(self, validation_results: Dict, config) -> List[str]:
        """Generate recommendations based on evaluation results"""
        
        recommendations = []
        metrics = validation_results['metrics']
        
        # Performance recommendations
        if metrics.get('accuracy', 0) < 0.7:
            recommendations.append("Low accuracy detected. Consider collecting more training data or feature engineering.")
        
        if metrics.get('f1_score', 0) < 0.6:
            recommendations.append("Low F1 score indicates poor precision-recall balance. Review class distribution.")
        
        # Overfitting detection
        cv_scores = validation_results.get('cv_scores', {})
        for metric, scores in cv_scores.items():
            if scores.get('std', 0) > 0.1:
                recommendations.append(f"High variance in {metric} suggests overfitting. Consider regularization.")
        
        if not recommendations:
            recommendations.append("Model performance looks good. Continue monitoring in production.")
        
        return recommendations
    
    def _generate_comparison_recommendations(self, models_results: Dict) -> List[str]:
        """Generate recommendations from model comparison"""
        
        recommendations = []
        
        # Find best performing model
        best_accuracy = 0
        best_model = None
        
        for model_path, results in models_results.items():
            if 'metrics' in results:
                accuracy = results['metrics'].get('accuracy', 0)
                if accuracy > best_accuracy:
                    best_accuracy = accuracy
                    best_model = model_path
        
        if best_model:
            recommendations.append(f"Best performing model: {best_model} (accuracy: {best_accuracy:.3f})")
        
        # Check for significant differences
        accuracies = [r['metrics'].get('accuracy', 0) for r in models_results.values() if 'metrics' in r]
        if len(accuracies) > 1 and np.std(accuracies) < 0.05:
            recommendations.append("Models show similar performance. Consider ensemble methods.")
        
        return recommendations
    
    def _calculate_individual_fairness(self, model, X: np.ndarray, y: np.ndarray) -> float:
        """Calculate individual fairness score"""
        
        try:
            # Simple consistency check: similar inputs should have similar outputs
            predictions = model.predict(X)
            
            # Calculate pairwise distances and prediction differences
            from sklearn.metrics.pairwise import euclidean_distances
            
            # Sample subset for efficiency
            n_samples = min(100, len(X))
            indices = np.random.choice(len(X), n_samples, replace=False)
            X_sample = X[indices]
            pred_sample = predictions[indices]
            
            distances = euclidean_distances(X_sample)
            pred_diffs = np.abs(pred_sample[:, np.newaxis] - pred_sample)
            
            # Calculate correlation between input similarity and prediction similarity
            # Higher correlation means more consistent (fair) predictions
            distance_flat = distances.flatten()
            pred_diff_flat = pred_diffs.flatten()
            
            # Remove diagonal (self-comparisons)
            mask = distance_flat > 0
            distance_flat = distance_flat[mask]
            pred_diff_flat = pred_diff_flat[mask]
            
            if len(distance_flat) > 0:
                correlation = np.corrcoef(distance_flat, pred_diff_flat)[0, 1]
                # Convert correlation to fairness score (0-1, higher is better)
                fairness_score = max(0, 1 - abs(correlation))
                return float(fairness_score)
            
        except Exception as e:
            self.logger.warning(f"Individual fairness calculation failed: {str(e)}")
        
        return 0.5  # Default neutral score
    
    def _get_recent_data(self, days_back: int) -> List[Dict]:
        """Get recent assessment data for drift monitoring"""
        
        from ..models.assessment import Assessment
        
        cutoff_date = datetime.utcnow() - timedelta(days=days_back)
        
        recent_assessments = self.db.query(Assessment).filter(
            Assessment.completed_at >= cutoff_date,
            Assessment.status == "completed"
        ).all()
        
        # Convert to training data format
        # This would use similar logic as in MLTrainingService
        return []  # Simplified for now
    
    def _prepare_drift_data(self, data: List[Dict], config) -> Tuple[np.ndarray, np.ndarray]:
        """Prepare data for drift analysis"""
        
        # This would use the same preparation logic as training
        from .ml_training_service import MLTrainingService
        
        training_service = MLTrainingService(self.db)
        return training_service._prepare_features_and_targets(data, config)
    
    def _save_evaluation_results(self, results: EvaluationResults, model_path: str):
        """Save evaluation results"""
        
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        results_file = self.evaluation_dir / f"evaluation_{timestamp}.json"
        
        # Convert results to serializable format
        results_dict = {
            'model_path': model_path,
            'model_type': results.model_type,
            'validation_method': results.validation_method,
            'metrics': results.metrics,
            'confidence_intervals': {k: list(v) for k, v in results.confidence_intervals.items()},
            'feature_importance': results.feature_importance,
            'learning_curves': results.learning_curves,
            'recommendations': results.recommendations,
            'evaluated_at': datetime.utcnow().isoformat()
        }
        
        with open(results_file, 'w') as f:
            json.dump(results_dict, f, indent=2)
        
        self.logger.info(f"Evaluation results saved to {results_file}")