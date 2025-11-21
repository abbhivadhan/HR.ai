#!/usr/bin/env python3
"""
Intelligent Scaling Policy for AI-HR Platform
Implements custom scaling logic based on business metrics
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import json
import os

import aiohttp
from kubernetes import client, config
import prometheus_client.parser

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class IntelligentScaler:
    """Intelligent scaling based on business metrics and traffic patterns"""
    
    def __init__(self):
        # Load Kubernetes config
        if os.getenv('KUBERNETES_SERVICE_HOST'):
            config.load_incluster_config()
        else:
            config.load_kube_config()
        
        self.apps_v1 = client.AppsV1Api()
        self.autoscaling_v2 = client.AutoscalingV2Api()
        self.namespace = "ai-hr-platform"
        
        # Scaling thresholds
        self.scaling_config = {
            "backend": {
                "min_replicas": 3,
                "max_replicas": 20,
                "target_cpu": 70,
                "target_memory": 80,
                "scale_up_threshold": 0.8,
                "scale_down_threshold": 0.3,
                "assessment_queue_threshold": 50,
                "interview_active_threshold": 10
            },
            "frontend": {
                "min_replicas": 2,
                "max_replicas": 10,
                "target_cpu": 70,
                "target_memory": 80,
                "scale_up_threshold": 0.8,
                "scale_down_threshold": 0.3
            }
        }
    
    async def get_prometheus_metrics(self) -> Dict:
        """Fetch metrics from Prometheus"""
        prometheus_url = "http://prometheus:9090"
        metrics = {}
        
        queries = {
            "cpu_usage": 'avg(rate(container_cpu_usage_seconds_total[5m])) by (pod)',
            "memory_usage": 'avg(container_memory_usage_bytes) by (pod)',
            "request_rate": 'sum(rate(http_requests_total[5m]))',
            "error_rate": 'sum(rate(http_requests_total{status=~"5.."}[5m]))',
            "response_time": 'histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m]))',
            "active_assessments": 'sum(active_assessments_total)',
            "active_interviews": 'sum(active_interviews_total)',
            "job_matching_queue": 'sum(job_matching_queue_size)'
        }
        
        async with aiohttp.ClientSession() as session:
            for metric_name, query in queries.items():
                try:
                    url = f"{prometheus_url}/api/v1/query"
                    params = {"query": query}
                    
                    async with session.get(url, params=params) as response:
                        if response.status == 200:
                            data = await response.json()
                            metrics[metric_name] = data.get("data", {}).get("result", [])
                        else:
                            logger.warning(f"Failed to fetch {metric_name}: {response.status}")
                            metrics[metric_name] = []
                except Exception as e:
                    logger.error(f"Error fetching {metric_name}: {e}")
                    metrics[metric_name] = []
        
        return metrics
    
    def calculate_scaling_decision(self, service: str, metrics: Dict) -> Dict:
        """Calculate scaling decision based on metrics"""
        config = self.scaling_config[service]
        
        # Get current replica count
        try:
            deployment = self.apps_v1.read_namespaced_deployment(
                name=f"{service}-deployment",
                namespace=self.namespace
            )
            current_replicas = deployment.status.replicas or config["min_replicas"]
        except Exception as e:
            logger.error(f"Error getting current replicas for {service}: {e}")
            current_replicas = config["min_replicas"]
        
        # Analyze metrics
        cpu_usage = self._get_metric_value(metrics.get("cpu_usage", []), service)
        memory_usage = self._get_metric_value(metrics.get("memory_usage", []), service)
        request_rate = self._get_metric_value(metrics.get("request_rate", []))
        error_rate = self._get_metric_value(metrics.get("error_rate", []))
        response_time = self._get_metric_value(metrics.get("response_time", []))
        
        # Business-specific metrics for backend
        if service == "backend":
            active_assessments = self._get_metric_value(metrics.get("active_assessments", []))
            active_interviews = self._get_metric_value(metrics.get("active_interviews", []))
            job_matching_queue = self._get_metric_value(metrics.get("job_matching_queue", []))
        else:
            active_assessments = active_interviews = job_matching_queue = 0
        
        # Calculate scaling score
        scaling_score = 0
        reasons = []
        
        # CPU-based scaling
        if cpu_usage > config["target_cpu"]:
            scaling_score += (cpu_usage - config["target_cpu"]) / 100
            reasons.append(f"High CPU usage: {cpu_usage:.1f}%")
        elif cpu_usage < config["target_cpu"] * 0.5:
            scaling_score -= (config["target_cpu"] * 0.5 - cpu_usage) / 100
            reasons.append(f"Low CPU usage: {cpu_usage:.1f}%")
        
        # Memory-based scaling
        if memory_usage > config["target_memory"]:
            scaling_score += (memory_usage - config["target_memory"]) / 100
            reasons.append(f"High memory usage: {memory_usage:.1f}%")
        
        # Response time-based scaling
        if response_time > 2.0:  # 2 seconds threshold
            scaling_score += min(response_time - 2.0, 2.0)
            reasons.append(f"High response time: {response_time:.2f}s")
        
        # Error rate-based scaling
        if error_rate > 0.05:  # 5% error rate threshold
            scaling_score += error_rate * 10
            reasons.append(f"High error rate: {error_rate:.2%}")
        
        # Business metrics for backend
        if service == "backend":
            if active_assessments > config["assessment_queue_threshold"]:
                scaling_score += (active_assessments - config["assessment_queue_threshold"]) / 100
                reasons.append(f"High assessment queue: {active_assessments}")
            
            if active_interviews > config["interview_active_threshold"]:
                scaling_score += (active_interviews - config["interview_active_threshold"]) / 10
                reasons.append(f"High active interviews: {active_interviews}")
            
            if job_matching_queue > 100:
                scaling_score += (job_matching_queue - 100) / 200
                reasons.append(f"High job matching queue: {job_matching_queue}")
        
        # Determine target replicas
        if scaling_score > config["scale_up_threshold"]:
            # Scale up
            target_replicas = min(
                current_replicas + max(1, int(scaling_score * 2)),
                config["max_replicas"]
            )
            action = "scale_up"
        elif scaling_score < -config["scale_down_threshold"]:
            # Scale down
            target_replicas = max(
                current_replicas - 1,
                config["min_replicas"]
            )
            action = "scale_down"
        else:
            # No scaling needed
            target_replicas = current_replicas
            action = "no_change"
        
        return {
            "service": service,
            "current_replicas": current_replicas,
            "target_replicas": target_replicas,
            "action": action,
            "scaling_score": scaling_score,
            "reasons": reasons,
            "metrics": {
                "cpu_usage": cpu_usage,
                "memory_usage": memory_usage,
                "request_rate": request_rate,
                "error_rate": error_rate,
                "response_time": response_time,
                "active_assessments": active_assessments,
                "active_interviews": active_interviews,
                "job_matching_queue": job_matching_queue
            }
        }
    
    def _get_metric_value(self, metric_data: List, service: str = None) -> float:
        """Extract metric value from Prometheus response"""
        if not metric_data:
            return 0.0
        
        if service:
            # Filter by service/pod name
            for item in metric_data:
                if service in item.get("metric", {}).get("pod", ""):
                    return float(item.get("value", [0, "0"])[1])
        
        # Return first value if no service filter
        if metric_data:
            return float(metric_data[0].get("value", [0, "0"])[1])
        
        return 0.0
    
    async def apply_scaling_decision(self, decision: Dict):
        """Apply scaling decision to Kubernetes deployment"""
        if decision["action"] == "no_change":
            logger.info(f"No scaling needed for {decision['service']}")
            return
        
        try:
            # Update deployment replicas
            deployment_name = f"{decision['service']}-deployment"
            
            # Get current deployment
            deployment = self.apps_v1.read_namespaced_deployment(
                name=deployment_name,
                namespace=self.namespace
            )
            
            # Update replica count
            deployment.spec.replicas = decision["target_replicas"]
            
            # Apply the update
            self.apps_v1.patch_namespaced_deployment(
                name=deployment_name,
                namespace=self.namespace,
                body=deployment
            )
            
            logger.info(
                f"Scaled {decision['service']} from {decision['current_replicas']} "
                f"to {decision['target_replicas']} replicas. "
                f"Reasons: {', '.join(decision['reasons'])}"
            )
            
        except Exception as e:
            logger.error(f"Error applying scaling decision for {decision['service']}: {e}")
    
    async def run_scaling_loop(self):
        """Main scaling loop"""
        logger.info("Starting intelligent scaling loop...")
        
        while True:
            try:
                # Fetch metrics
                metrics = await self.get_prometheus_metrics()
                
                # Calculate scaling decisions for each service
                services = ["backend", "frontend"]
                decisions = []
                
                for service in services:
                    decision = self.calculate_scaling_decision(service, metrics)
                    decisions.append(decision)
                    
                    # Apply scaling decision
                    await self.apply_scaling_decision(decision)
                
                # Log scaling summary
                logger.info(f"Scaling cycle completed. Decisions: {json.dumps(decisions, indent=2)}")
                
                # Wait before next cycle (5 minutes)
                await asyncio.sleep(300)
                
            except Exception as e:
                logger.error(f"Error in scaling loop: {e}")
                await asyncio.sleep(60)  # Wait 1 minute on error


async def main():
    """Main function"""
    scaler = IntelligentScaler()
    await scaler.run_scaling_loop()


if __name__ == "__main__":
    asyncio.run(main())