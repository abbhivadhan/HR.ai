"""
Simple monitoring and infrastructure tests
"""
import pytest
import os
import sys
from pathlib import Path

# Add backend to path for imports
backend_path = Path(__file__).parent.parent.parent / "backend"
sys.path.insert(0, str(backend_path))

try:
    from app.monitoring import PerformanceMonitor, monitor
    MONITORING_AVAILABLE = True
except ImportError:
    MONITORING_AVAILABLE = False


class TestMonitoringModule:
    """Test monitoring module functionality"""
    
    @pytest.mark.skipif(not MONITORING_AVAILABLE, reason="Monitoring module not available")
    def test_performance_monitor_initialization(self):
        """Test that PerformanceMonitor can be initialized"""
        monitor_instance = PerformanceMonitor()
        assert monitor_instance is not None
        assert hasattr(monitor_instance, 'start_time')
    
    @pytest.mark.skipif(not MONITORING_AVAILABLE, reason="Monitoring module not available")
    def test_global_monitor_instance(self):
        """Test that global monitor instance exists"""
        assert monitor is not None
        assert hasattr(monitor, 'track_request')
        assert hasattr(monitor, 'track_ai_inference')
    
    def test_kubernetes_manifests_exist(self):
        """Test that Kubernetes manifests exist"""
        k8s_path = Path(__file__).parent.parent.parent / "k8s"
        
        required_files = [
            "namespace.yaml",
            "configmap.yaml",
            "backend-deployment.yaml",
            "frontend-deployment.yaml",
            "database-deployment.yaml",
            "redis-deployment.yaml",
            "mongodb-deployment.yaml",
            "ingress.yaml",
            "hpa.yaml",
            "backup-cronjob.yaml"
        ]
        
        for file_name in required_files:
            file_path = k8s_path / file_name
            assert file_path.exists(), f"Required Kubernetes manifest {file_name} not found"
            assert file_path.stat().st_size > 0, f"Kubernetes manifest {file_name} is empty"
    
    def test_monitoring_manifests_exist(self):
        """Test that monitoring manifests exist"""
        monitoring_path = Path(__file__).parent.parent.parent / "monitoring"
        
        required_files = [
            "prometheus-config.yaml",
            "prometheus-deployment.yaml",
            "grafana-deployment.yaml",
            "alertmanager-config.yaml",
            "alertmanager-deployment.yaml"
        ]
        
        for file_name in required_files:
            file_path = monitoring_path / file_name
            assert file_path.exists(), f"Required monitoring manifest {file_name} not found"
            assert file_path.stat().st_size > 0, f"Monitoring manifest {file_name} is empty"
    
    def test_scripts_exist_and_executable(self):
        """Test that deployment scripts exist and are executable"""
        scripts_path = Path(__file__).parent.parent.parent / "scripts"
        
        required_scripts = [
            "deployment-validation.sh",
            "disaster-recovery.sh",
            "scaling-policy.py"
        ]
        
        for script_name in required_scripts:
            script_path = scripts_path / script_name
            assert script_path.exists(), f"Required script {script_name} not found"
            assert script_path.stat().st_size > 0, f"Script {script_name} is empty"
            
            # Check if shell scripts are executable
            if script_name.endswith('.sh'):
                assert os.access(script_path, os.X_OK), f"Script {script_name} is not executable"
    
    def test_deployment_guide_exists(self):
        """Test that deployment guide exists"""
        guide_path = Path(__file__).parent.parent.parent / "DEPLOYMENT_GUIDE.md"
        assert guide_path.exists(), "DEPLOYMENT_GUIDE.md not found"
        assert guide_path.stat().st_size > 1000, "DEPLOYMENT_GUIDE.md seems too small"
    
    def test_monitoring_dependencies_in_requirements(self):
        """Test that monitoring dependencies are in requirements.txt"""
        requirements_path = Path(__file__).parent.parent.parent / "backend" / "requirements.txt"
        assert requirements_path.exists(), "requirements.txt not found"
        
        with open(requirements_path, 'r') as f:
            requirements_content = f.read()
        
        required_packages = [
            "prometheus-client",
            "sentry-sdk",
            "psutil"
        ]
        
        for package in required_packages:
            assert package in requirements_content, f"Required monitoring package {package} not in requirements.txt"


class TestKubernetesManifestStructure:
    """Test Kubernetes manifest structure and content"""
    
    def test_namespace_manifest_structure(self):
        """Test namespace manifest has correct structure"""
        namespace_path = Path(__file__).parent.parent.parent / "k8s" / "namespace.yaml"
        
        with open(namespace_path, 'r') as f:
            content = f.read()
        
        assert "apiVersion: v1" in content
        assert "kind: Namespace" in content
        assert "name: ai-hr-platform" in content
    
    def test_backend_deployment_structure(self):
        """Test backend deployment has required fields"""
        deployment_path = Path(__file__).parent.parent.parent / "k8s" / "backend-deployment.yaml"
        
        with open(deployment_path, 'r') as f:
            content = f.read()
        
        required_fields = [
            "apiVersion: apps/v1",
            "kind: Deployment",
            "name: backend-deployment",
            "replicas: 3",
            "containerPort: 8000",
            "livenessProbe",
            "readinessProbe"
        ]
        
        for field in required_fields:
            assert field in content, f"Required field '{field}' not found in backend deployment"
    
    def test_hpa_configuration(self):
        """Test HPA configuration is valid"""
        hpa_path = Path(__file__).parent.parent.parent / "k8s" / "hpa.yaml"
        
        with open(hpa_path, 'r') as f:
            content = f.read()
        
        required_fields = [
            "apiVersion: autoscaling/v2",
            "kind: HorizontalPodAutoscaler",
            "minReplicas:",
            "maxReplicas:",
            "averageUtilization: 70"
        ]
        
        for field in required_fields:
            assert field in content, f"Required HPA field '{field}' not found"


class TestMonitoringConfiguration:
    """Test monitoring configuration"""
    
    def test_prometheus_config_structure(self):
        """Test Prometheus configuration structure"""
        config_path = Path(__file__).parent.parent.parent / "monitoring" / "prometheus-config.yaml"
        
        with open(config_path, 'r') as f:
            content = f.read()
        
        required_sections = [
            "global:",
            "scrape_configs:",
            "alerting:",
            "rule_files:",
            "scrape_interval: 15s"
        ]
        
        for section in required_sections:
            assert section in content, f"Required Prometheus config section '{section}' not found"
    
    def test_alertmanager_config_structure(self):
        """Test Alertmanager configuration structure"""
        config_path = Path(__file__).parent.parent.parent / "monitoring" / "alertmanager-config.yaml"
        
        with open(config_path, 'r') as f:
            content = f.read()
        
        required_sections = [
            "global:",
            "route:",
            "receivers:",
            "smtp_smarthost:",
            "group_by:"
        ]
        
        for section in required_sections:
            assert section in content, f"Required Alertmanager config section '{section}' not found"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])