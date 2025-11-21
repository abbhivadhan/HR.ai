"""
Model Versioning and Deployment Service

This service handles model versioning, deployment management,
rollback capabilities, and A/B testing for AI models.
"""

import json
import pickle
import shutil
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
from pathlib import Path
import logging
from dataclasses import dataclass, asdict
from enum import Enum
import hashlib
import uuid

from sqlalchemy.orm import Session
from .ml_training_service import ModelType, ModelMetrics
from .model_evaluation_service import ModelEvaluationService, ValidationConfig, ValidationMethod


class DeploymentStatus(str, Enum):
    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"
    DEPRECATED = "deprecated"
    ROLLBACK = "rollback"


class DeploymentStrategy(str, Enum):
    BLUE_GREEN = "blue_green"
    CANARY = "canary"
    ROLLING = "rolling"
    A_B_TEST = "a_b_test"


@dataclass
class ModelVersion:
    version_id: str
    model_type: ModelType
    version_number: str
    model_path: str
    metrics: Dict[str, float]
    metadata: Dict[str, Any]
    created_at: datetime
    created_by: str
    status: DeploymentStatus
    parent_version: Optional[str] = None
    tags: List[str] = None
    checksum: str = ""


@dataclass
class DeploymentConfig:
    strategy: DeploymentStrategy
    target_environment: DeploymentStatus
    traffic_percentage: float = 100.0
    rollback_threshold: float = 0.05  # Performance degradation threshold
    monitoring_duration_hours: int = 24
    auto_promote: bool = False
    approval_required: bool = True


class ModelVersioningService:
    def __init__(self, db: Session):
        self.db = db
        self.logger = logging.getLogger(__name__)
        
        # Directory structure
        self.versions_dir = Path("model_versions")
        self.versions_dir.mkdir(exist_ok=True)
        
        self.deployments_dir = Path("deployments")
        self.deployments_dir.mkdir(exist_ok=True)
        
        # Version registry
        self.registry_file = self.versions_dir / "registry.json"
        self.deployment_log = self.deployments_dir / "deployment_log.jsonl"
        
        self.evaluation_service = ModelEvaluationService(db)
        
        # Initialize registry if it doesn't exist
        if not self.registry_file.exists():
            self._initialize_registry()
    
    def create_version(self, 
                      model_path: str, 
                      model_type: ModelType, 
                      metadata: Dict[str, Any] = None,
                      tags: List[str] = None) -> ModelVersion:
        """Create a new model version"""
        
        self.logger.info(f"Creating new version for {model_type} model")
        
        try:
            # Generate version info
            version_id = str(uuid.uuid4())
            version_number = self._generate_version_number(model_type)
            checksum = self._calculate_checksum(model_path)
            
            # Copy model to versioned location
            versioned_path = self._copy_to_versioned_location(model_path, version_id)
            
            # Load model metrics
            metrics = self._extract_model_metrics(model_path)
            
            # Create version object
            version = ModelVersion(
                version_id=version_id,
                model_type=model_type,
                version_number=version_number,
                model_path=str(versioned_path),
                metrics=metrics,
                metadata=metadata or {},
                created_at=datetime.utcnow(),
                created_by="system",  # Would be actual user in production
                status=DeploymentStatus.DEVELOPMENT,
                tags=tags or [],
                checksum=checksum
            )
            
            # Register version
            self._register_version(version)
            
            self.logger.info(f"Created version {version_number} with ID {version_id}")
            return version
            
        except Exception as e:
            self.logger.error(f"Failed to create version: {str(e)}")
            raise
    
    def get_version(self, version_id: str) -> Optional[ModelVersion]:
        """Get a specific model version"""
        
        registry = self._load_registry()
        
        for model_type, versions in registry.items():
            for version_data in versions:
                if version_data['version_id'] == version_id:
                    return ModelVersion(**version_data)
        
        return None
    
    def list_versions(self, 
                     model_type: Optional[ModelType] = None,
                     status: Optional[DeploymentStatus] = None,
                     limit: int = 50) -> List[ModelVersion]:
        """List model versions with optional filtering"""
        
        registry = self._load_registry()
        versions = []
        
        for mt, version_list in registry.items():
            if model_type and mt != model_type:
                continue
                
            for version_data in version_list:
                if status and version_data['status'] != status:
                    continue
                    
                versions.append(ModelVersion(**version_data))
        
        # Sort by creation date (newest first)
        versions.sort(key=lambda v: v.created_at, reverse=True)
        
        return versions[:limit]
    
    def get_latest_version(self, 
                          model_type: ModelType, 
                          status: Optional[DeploymentStatus] = None) -> Optional[ModelVersion]:
        """Get the latest version of a model type"""
        
        versions = self.list_versions(model_type=model_type, status=status, limit=1)
        return versions[0] if versions else None
    
    def compare_versions(self, version_id_1: str, version_id_2: str) -> Dict[str, Any]:
        """Compare two model versions"""
        
        version_1 = self.get_version(version_id_1)
        version_2 = self.get_version(version_id_2)
        
        if not version_1 or not version_2:
            raise ValueError("One or both versions not found")
        
        comparison = {
            "version_1": {
                "id": version_1.version_id,
                "number": version_1.version_number,
                "created_at": version_1.created_at.isoformat(),
                "metrics": version_1.metrics,
                "status": version_1.status
            },
            "version_2": {
                "id": version_2.version_id,
                "number": version_2.version_number,
                "created_at": version_2.created_at.isoformat(),
                "metrics": version_2.metrics,
                "status": version_2.status
            },
            "metrics_comparison": {},
            "recommendations": []
        }
        
        # Compare metrics
        for metric in set(version_1.metrics.keys()) | set(version_2.metrics.keys()):
            v1_value = version_1.metrics.get(metric, 0)
            v2_value = version_2.metrics.get(metric, 0)
            
            comparison["metrics_comparison"][metric] = {
                "version_1": v1_value,
                "version_2": v2_value,
                "difference": v2_value - v1_value,
                "improvement": v2_value > v1_value
            }
        
        # Generate recommendations
        accuracy_diff = comparison["metrics_comparison"].get("accuracy", {}).get("difference", 0)
        if accuracy_diff > 0.05:
            comparison["recommendations"].append(f"Version 2 shows significant accuracy improvement (+{accuracy_diff:.3f})")
        elif accuracy_diff < -0.05:
            comparison["recommendations"].append(f"Version 2 shows accuracy degradation ({accuracy_diff:.3f})")
        
        return comparison
    
    def deploy_version(self, version_id: str, config: DeploymentConfig) -> Dict[str, Any]:
        """Deploy a model version"""
        
        self.logger.info(f"Deploying version {version_id} to {config.target_environment}")
        
        try:
            version = self.get_version(version_id)
            if not version:
                raise ValueError(f"Version {version_id} not found")
            
            # Validate deployment
            validation_result = self._validate_deployment(version, config)
            if not validation_result["valid"]:
                return {
                    "success": False,
                    "error": validation_result["error"],
                    "version_id": version_id
                }
            
            # Execute deployment strategy
            if config.strategy == DeploymentStrategy.BLUE_GREEN:
                deployment_result = self._blue_green_deployment(version, config)
            elif config.strategy == DeploymentStrategy.CANARY:
                deployment_result = self._canary_deployment(version, config)
            elif config.strategy == DeploymentStrategy.A_B_TEST:
                deployment_result = self._ab_test_deployment(version, config)
            else:
                deployment_result = self._rolling_deployment(version, config)
            
            # Update version status
            if deployment_result["success"]:
                self._update_version_status(version_id, config.target_environment)
            
            # Log deployment
            self._log_deployment(version_id, config, deployment_result)
            
            return deployment_result
            
        except Exception as e:
            self.logger.error(f"Deployment failed: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "version_id": version_id
            }
    
    def rollback_deployment(self, model_type: ModelType, target_version_id: Optional[str] = None) -> Dict[str, Any]:
        """Rollback to a previous version"""
        
        self.logger.info(f"Rolling back {model_type} deployment")
        
        try:
            # Get current production version
            current_version = self.get_latest_version(model_type, DeploymentStatus.PRODUCTION)
            if not current_version:
                return {"success": False, "error": "No production version found"}
            
            # Determine rollback target
            if target_version_id:
                target_version = self.get_version(target_version_id)
                if not target_version:
                    return {"success": False, "error": "Target version not found"}
            else:
                # Find previous production version
                versions = self.list_versions(model_type=model_type, limit=10)
                production_versions = [v for v in versions if v.status == DeploymentStatus.PRODUCTION]
                
                if len(production_versions) < 2:
                    return {"success": False, "error": "No previous version to rollback to"}
                
                target_version = production_versions[1]  # Second most recent
            
            # Perform rollback
            rollback_config = DeploymentConfig(
                strategy=DeploymentStrategy.BLUE_GREEN,
                target_environment=DeploymentStatus.PRODUCTION,
                traffic_percentage=100.0
            )
            
            deployment_result = self.deploy_version(target_version.version_id, rollback_config)
            
            if deployment_result["success"]:
                # Mark current version as rollback
                self._update_version_status(current_version.version_id, DeploymentStatus.ROLLBACK)
                
                return {
                    "success": True,
                    "rolled_back_from": current_version.version_id,
                    "rolled_back_to": target_version.version_id,
                    "deployment_result": deployment_result
                }
            else:
                return {
                    "success": False,
                    "error": "Rollback deployment failed",
                    "deployment_result": deployment_result
                }
                
        except Exception as e:
            self.logger.error(f"Rollback failed: {str(e)}")
            return {"success": False, "error": str(e)}
    
    def cleanup_old_versions(self, model_type: ModelType, keep_count: int = 10) -> Dict[str, Any]:
        """Clean up old model versions"""
        
        self.logger.info(f"Cleaning up old versions for {model_type}")
        
        try:
            versions = self.list_versions(model_type=model_type, limit=100)
            
            # Keep production, staging, and recent versions
            protected_versions = []
            for version in versions:
                if (version.status in [DeploymentStatus.PRODUCTION, DeploymentStatus.STAGING] or
                    len(protected_versions) < keep_count):
                    protected_versions.append(version)
            
            # Identify versions to delete
            versions_to_delete = [v for v in versions if v not in protected_versions]
            
            deleted_count = 0
            for version in versions_to_delete:
                try:
                    # Delete model file
                    model_path = Path(version.model_path)
                    if model_path.exists():
                        model_path.unlink()
                    
                    # Remove from registry
                    self._remove_from_registry(version.version_id)
                    deleted_count += 1
                    
                except Exception as e:
                    self.logger.warning(f"Failed to delete version {version.version_id}: {str(e)}")
            
            return {
                "success": True,
                "deleted_count": deleted_count,
                "kept_count": len(protected_versions),
                "model_type": model_type
            }
            
        except Exception as e:
            self.logger.error(f"Cleanup failed: {str(e)}")
            return {"success": False, "error": str(e)}
    
    def _initialize_registry(self):
        """Initialize the version registry"""
        
        registry = {}
        for model_type in ModelType:
            registry[model_type] = []
        
        with open(self.registry_file, 'w') as f:
            json.dump(registry, f, indent=2)
    
    def _load_registry(self) -> Dict[str, List[Dict]]:
        """Load the version registry"""
        
        try:
            with open(self.registry_file, 'r') as f:
                registry = json.load(f)
                
            # Convert datetime strings back to datetime objects
            for model_type, versions in registry.items():
                for version in versions:
                    version['created_at'] = datetime.fromisoformat(version['created_at'])
                    
            return registry
            
        except Exception as e:
            self.logger.error(f"Failed to load registry: {str(e)}")
            return {}
    
    def _save_registry(self, registry: Dict[str, List[Dict]]):
        """Save the version registry"""
        
        # Convert datetime objects to strings for JSON serialization
        serializable_registry = {}
        for model_type, versions in registry.items():
            serializable_registry[model_type] = []
            for version in versions:
                version_copy = version.copy()
                if isinstance(version_copy['created_at'], datetime):
                    version_copy['created_at'] = version_copy['created_at'].isoformat()
                serializable_registry[model_type].append(version_copy)
        
        with open(self.registry_file, 'w') as f:
            json.dump(serializable_registry, f, indent=2)
    
    def _register_version(self, version: ModelVersion):
        """Register a new version in the registry"""
        
        registry = self._load_registry()
        
        if version.model_type not in registry:
            registry[version.model_type] = []
        
        registry[version.model_type].append(asdict(version))
        self._save_registry(registry)
    
    def _generate_version_number(self, model_type: ModelType) -> str:
        """Generate a semantic version number"""
        
        versions = self.list_versions(model_type=model_type, limit=1)
        
        if not versions:
            return "1.0.0"
        
        latest_version = versions[0].version_number
        
        try:
            # Parse semantic version (major.minor.patch)
            parts = latest_version.split('.')
            major, minor, patch = int(parts[0]), int(parts[1]), int(parts[2])
            
            # Increment patch version
            return f"{major}.{minor}.{patch + 1}"
            
        except:
            # Fallback to timestamp-based version
            return datetime.utcnow().strftime("1.%Y%m%d.%H%M%S")
    
    def _calculate_checksum(self, model_path: str) -> str:
        """Calculate checksum for model file"""
        
        try:
            with open(model_path, 'rb') as f:
                content = f.read()
                return hashlib.sha256(content).hexdigest()
        except:
            return ""
    
    def _copy_to_versioned_location(self, model_path: str, version_id: str) -> Path:
        """Copy model to versioned storage location"""
        
        source_path = Path(model_path)
        versioned_path = self.versions_dir / f"{version_id}.pkl"
        
        shutil.copy2(source_path, versioned_path)
        
        return versioned_path
    
    def _extract_model_metrics(self, model_path: str) -> Dict[str, float]:
        """Extract metrics from model file"""
        
        try:
            with open(model_path, 'rb') as f:
                model_data = pickle.load(f)
                
            if 'metrics' in model_data:
                metrics = model_data['metrics']
                if hasattr(metrics, '__dict__'):
                    return metrics.__dict__
                elif isinstance(metrics, dict):
                    return metrics
                    
        except Exception as e:
            self.logger.warning(f"Could not extract metrics from {model_path}: {str(e)}")
        
        return {}
    
    def _validate_deployment(self, version: ModelVersion, config: DeploymentConfig) -> Dict[str, Any]:
        """Validate deployment prerequisites"""
        
        # Check if model file exists
        if not Path(version.model_path).exists():
            return {"valid": False, "error": "Model file not found"}
        
        # Check metrics thresholds
        if version.metrics.get('accuracy', 0) < 0.5:
            return {"valid": False, "error": "Model accuracy too low for deployment"}
        
        # Check if approval is required
        if config.approval_required and config.target_environment == DeploymentStatus.PRODUCTION:
            # In practice, this would check an approval system
            pass
        
        return {"valid": True}
    
    def _blue_green_deployment(self, version: ModelVersion, config: DeploymentConfig) -> Dict[str, Any]:
        """Execute blue-green deployment"""
        
        try:
            # Copy model to deployment location
            deployment_path = self.deployments_dir / f"{config.target_environment}_{version.model_type}.pkl"
            shutil.copy2(version.model_path, deployment_path)
            
            # In practice, this would update load balancer configuration
            # and perform health checks
            
            return {
                "success": True,
                "strategy": "blue_green",
                "deployment_path": str(deployment_path),
                "traffic_percentage": config.traffic_percentage
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _canary_deployment(self, version: ModelVersion, config: DeploymentConfig) -> Dict[str, Any]:
        """Execute canary deployment"""
        
        # Simplified canary deployment
        return self._blue_green_deployment(version, config)
    
    def _ab_test_deployment(self, version: ModelVersion, config: DeploymentConfig) -> Dict[str, Any]:
        """Execute A/B test deployment"""
        
        # Simplified A/B test deployment
        return self._blue_green_deployment(version, config)
    
    def _rolling_deployment(self, version: ModelVersion, config: DeploymentConfig) -> Dict[str, Any]:
        """Execute rolling deployment"""
        
        # Simplified rolling deployment
        return self._blue_green_deployment(version, config)
    
    def _update_version_status(self, version_id: str, status: DeploymentStatus):
        """Update version status in registry"""
        
        registry = self._load_registry()
        
        for model_type, versions in registry.items():
            for version in versions:
                if version['version_id'] == version_id:
                    version['status'] = status
                    break
        
        self._save_registry(registry)
    
    def _log_deployment(self, version_id: str, config: DeploymentConfig, result: Dict[str, Any]):
        """Log deployment activity"""
        
        log_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "version_id": version_id,
            "strategy": config.strategy,
            "target_environment": config.target_environment,
            "traffic_percentage": config.traffic_percentage,
            "success": result["success"],
            "result": result
        }
        
        with open(self.deployment_log, 'a') as f:
            f.write(json.dumps(log_entry) + '\n')
    
    def _remove_from_registry(self, version_id: str):
        """Remove version from registry"""
        
        registry = self._load_registry()
        
        for model_type, versions in registry.items():
            registry[model_type] = [v for v in versions if v['version_id'] != version_id]
        
        self._save_registry(registry)