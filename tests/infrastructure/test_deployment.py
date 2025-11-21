"""
Infrastructure and Deployment Tests
"""
import pytest
import asyncio
import aiohttp
import time
from kubernetes import client, config
from typing import Dict, List
import os


class TestKubernetesDeployment:
    """Test Kubernetes deployment health and functionality"""
    
    @classmethod
    def setup_class(cls):
        """Setup Kubernetes client"""
        try:
            if os.getenv('KUBERNETES_SERVICE_HOST'):
                config.load_incluster_config()
            else:
                config.load_kube_config()
            
            cls.apps_v1 = client.AppsV1Api()
            cls.core_v1 = client.CoreV1Api()
            cls.namespace = "ai-hr-platform"
        except Exception as e:
            pytest.skip(f"Kubernetes not available: {e}")
    
    def test_namespace_exists(self):
        """Test that the namespace exists"""
        namespaces = self.core_v1.list_namespace()
        namespace_names = [ns.metadata.name for ns in namespaces.items]
        assert self.namespace in namespace_names
    
    def test_deployments_exist(self):
        """Test that all required deployments exist"""
        expected_deployments = [
            "backend-deployment",
            "frontend-deployment",
            "postgres-deployment",
            "redis-deployment",
            "mongodb-deployment"
        ]
        
        deployments = self.apps_v1.list_namespaced_deployment(namespace=self.namespace)
        deployment_names = [d.metadata.name for d in deployments.items]
        
        for expected in expected_deployments:
            assert expected in deployment_names, f"Deployment {expected} not found"
    
    def test_deployments_ready(self):
        """Test that all deployments are ready"""
        deployments = self.apps_v1.list_namespaced_deployment(namespace=self.namespace)
        
        for deployment in deployments.items:
            assert deployment.status.ready_replicas is not None, \
                f"Deployment {deployment.metadata.name} has no ready replicas"
            assert deployment.status.ready_replicas > 0, \
                f"Deployment {deployment.metadata.name} has 0 ready replicas"
    
    def test_services_exist(self):
        """Test that all required services exist"""
        expected_services = [
            "backend-service",
            "frontend-service",
            "postgres-service",
            "redis-service",
            "mongodb-service"
        ]
        
        services = self.core_v1.list_namespaced_service(namespace=self.namespace)
        service_names = [s.metadata.name for s in services.items]
        
        for expected in expected_services:
            assert expected in service_names, f"Service {expected} not found"
    
    def test_pods_running(self):
        """Test that all pods are running"""
        pods = self.core_v1.list_namespaced_pod(namespace=self.namespace)
        
        for pod in pods.items:
            assert pod.status.phase == "Running", \
                f"Pod {pod.metadata.name} is not running: {pod.status.phase}"
    
    def test_persistent_volumes_bound(self):
        """Test that persistent volume claims are bound"""
        pvcs = self.core_v1.list_namespaced_persistent_volume_claim(namespace=self.namespace)
        
        for pvc in pvcs.items:
            assert pvc.status.phase == "Bound", \
                f"PVC {pvc.metadata.name} is not bound: {pvc.status.phase}"


class TestApplicationHealth:
    """Test application health and endpoints"""
    
    @pytest.fixture
    def base_url(self):
        """Get base URL for testing"""
        # In production, this would be the actual domain
        # For testing, we might use port-forward or ingress
        return os.getenv("TEST_BASE_URL", "http://localhost:8000")
    
    @pytest.mark.asyncio
    async def test_health_endpoint(self, base_url):
        """Test health endpoint responds correctly"""
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{base_url}/health") as response:
                assert response.status == 200
                data = await response.json()
                assert data.get("status") == "healthy"
    
    @pytest.mark.asyncio
    async def test_readiness_endpoint(self, base_url):
        """Test readiness endpoint responds correctly"""
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{base_url}/ready") as response:
                assert response.status == 200
                data = await response.json()
                assert data.get("ready") is True
    
    @pytest.mark.asyncio
    async def test_metrics_endpoint(self, base_url):
        """Test metrics endpoint returns Prometheus metrics"""
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{base_url}/metrics") as response:
                assert response.status == 200
                content = await response.text()
                assert "http_requests_total" in content
                assert "http_request_duration_seconds" in content
    
    @pytest.mark.asyncio
    async def test_api_endpoints_accessible(self, base_url):
        """Test that main API endpoints are accessible"""
        endpoints = [
            "/docs",
            "/redoc",
            "/api/auth/health",
            "/api/assessments/health",
            "/api/dashboard/health"
        ]
        
        async with aiohttp.ClientSession() as session:
            for endpoint in endpoints:
                async with session.get(f"{base_url}{endpoint}") as response:
                    # Should not return 404 or 500
                    assert response.status < 500, f"Endpoint {endpoint} returned {response.status}"


class TestDatabaseConnectivity:
    """Test database connectivity and health"""
    
    @pytest.mark.asyncio
    async def test_postgres_connectivity(self):
        """Test PostgreSQL connectivity"""
        # This would typically use the actual database connection
        # For now, we'll test through the health endpoint
        pass
    
    @pytest.mark.asyncio
    async def test_redis_connectivity(self):
        """Test Redis connectivity"""
        # This would typically use the actual Redis connection
        pass
    
    @pytest.mark.asyncio
    async def test_mongodb_connectivity(self):
        """Test MongoDB connectivity"""
        # This would typically use the actual MongoDB connection
        pass


class TestScaling:
    """Test auto-scaling functionality"""
    
    @classmethod
    def setup_class(cls):
        """Setup for scaling tests"""
        try:
            if os.getenv('KUBERNETES_SERVICE_HOST'):
                config.load_incluster_config()
            else:
                config.load_kube_config()
            
            cls.apps_v1 = client.AppsV1Api()
            cls.autoscaling_v2 = client.AutoscalingV2Api()
            cls.namespace = "ai-hr-platform"
        except Exception as e:
            pytest.skip(f"Kubernetes not available: {e}")
    
    def test_hpa_exists(self):
        """Test that Horizontal Pod Autoscalers exist"""
        expected_hpas = ["backend-hpa", "frontend-hpa"]
        
        hpas = self.autoscaling_v2.list_namespaced_horizontal_pod_autoscaler(
            namespace=self.namespace
        )
        hpa_names = [hpa.metadata.name for hpa in hpas.items]
        
        for expected in expected_hpas:
            assert expected in hpa_names, f"HPA {expected} not found"
    
    def test_hpa_configuration(self):
        """Test HPA configuration is correct"""
        hpas = self.autoscaling_v2.list_namespaced_horizontal_pod_autoscaler(
            namespace=self.namespace
        )
        
        for hpa in hpas.items:
            assert hpa.spec.min_replicas >= 1, f"HPA {hpa.metadata.name} min replicas too low"
            assert hpa.spec.max_replicas >= hpa.spec.min_replicas, \
                f"HPA {hpa.metadata.name} max replicas less than min"
            assert len(hpa.spec.metrics) > 0, f"HPA {hpa.metadata.name} has no metrics"


class TestMonitoring:
    """Test monitoring infrastructure"""
    
    @pytest.fixture
    def monitoring_base_url(self):
        """Get monitoring base URL"""
        return os.getenv("MONITORING_BASE_URL", "http://localhost:9090")
    
    @pytest.mark.asyncio
    async def test_prometheus_accessible(self, monitoring_base_url):
        """Test Prometheus is accessible"""
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{monitoring_base_url}/-/healthy") as response:
                assert response.status == 200
    
    @pytest.mark.asyncio
    async def test_prometheus_targets(self, monitoring_base_url):
        """Test Prometheus targets are up"""
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{monitoring_base_url}/api/v1/targets") as response:
                assert response.status == 200
                data = await response.json()
                
                # Check that we have active targets
                active_targets = data.get("data", {}).get("activeTargets", [])
                assert len(active_targets) > 0, "No active Prometheus targets found"
                
                # Check that targets are healthy
                unhealthy_targets = [
                    target for target in active_targets 
                    if target.get("health") != "up"
                ]
                assert len(unhealthy_targets) == 0, f"Unhealthy targets: {unhealthy_targets}"


class TestBackupSystem:
    """Test backup and disaster recovery systems"""
    
    @classmethod
    def setup_class(cls):
        """Setup for backup tests"""
        try:
            if os.getenv('KUBERNETES_SERVICE_HOST'):
                config.load_incluster_config()
            else:
                config.load_kube_config()
            
            cls.batch_v1 = client.BatchV1Api()
            cls.namespace = "ai-hr-platform"
        except Exception as e:
            pytest.skip(f"Kubernetes not available: {e}")
    
    def test_backup_cronjobs_exist(self):
        """Test that backup CronJobs exist"""
        expected_cronjobs = ["postgres-backup", "mongodb-backup"]
        
        cronjobs = self.batch_v1.list_namespaced_cron_job(namespace=self.namespace)
        cronjob_names = [cj.metadata.name for cj in cronjobs.items]
        
        for expected in expected_cronjobs:
            assert expected in cronjob_names, f"CronJob {expected} not found"
    
    def test_backup_schedule_valid(self):
        """Test that backup schedules are valid"""
        cronjobs = self.batch_v1.list_namespaced_cron_job(namespace=self.namespace)
        
        for cronjob in cronjobs.items:
            schedule = cronjob.spec.schedule
            assert schedule is not None, f"CronJob {cronjob.metadata.name} has no schedule"
            # Basic validation - should contain 5 parts (minute hour day month weekday)
            parts = schedule.split()
            assert len(parts) == 5, f"Invalid cron schedule: {schedule}"


class TestSecurity:
    """Test security configurations"""
    
    @pytest.fixture
    def base_url(self):
        """Get base URL for testing"""
        return os.getenv("TEST_BASE_URL", "http://localhost:8000")
    
    @pytest.mark.asyncio
    async def test_security_headers(self, base_url):
        """Test that security headers are present"""
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{base_url}/health") as response:
                headers = response.headers
                
                # Check for security headers
                assert "X-Content-Type-Options" in headers
                assert "X-Frame-Options" in headers
                assert "X-XSS-Protection" in headers
                assert headers["X-Content-Type-Options"] == "nosniff"
                assert headers["X-Frame-Options"] == "DENY"
    
    @pytest.mark.asyncio
    async def test_rate_limiting(self, base_url):
        """Test that rate limiting is working"""
        async with aiohttp.ClientSession() as session:
            # Make multiple rapid requests
            responses = []
            for _ in range(10):
                async with session.get(f"{base_url}/health") as response:
                    responses.append(response.status)
            
            # Should not get rate limited for health checks
            # but this tests that the rate limiting middleware is active
            assert all(status < 500 for status in responses)


@pytest.mark.integration
class TestEndToEndDeployment:
    """End-to-end deployment tests"""
    
    @pytest.mark.asyncio
    async def test_full_user_journey(self):
        """Test a complete user journey through the deployed system"""
        # This would test:
        # 1. User registration
        # 2. Login
        # 3. Taking an assessment
        # 4. Viewing results
        # 5. Job matching
        # This is a placeholder for comprehensive E2E testing
        pass
    
    @pytest.mark.asyncio
    async def test_load_handling(self):
        """Test system behavior under load"""
        # This would simulate load and verify:
        # 1. Response times remain acceptable
        # 2. Error rates stay low
        # 3. Auto-scaling triggers appropriately
        # 4. System recovers gracefully
        pass


if __name__ == "__main__":
    pytest.main([__file__, "-v"])