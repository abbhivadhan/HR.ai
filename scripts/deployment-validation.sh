#!/bin/bash

# AI-HR Platform Deployment Validation Script
# Validates deployment health and functionality

set -e

NAMESPACE="ai-hr-platform"
TIMEOUT=300  # 5 minutes timeout
PROMETHEUS_URL="http://prometheus:9090"
GRAFANA_URL="http://grafana:3000"

echo "🚀 Starting AI-HR Platform Deployment Validation..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    local status=$1
    local message=$2
    case $status in
        "SUCCESS")
            echo -e "${GREEN}✅ $message${NC}"
            ;;
        "ERROR")
            echo -e "${RED}❌ $message${NC}"
            ;;
        "WARNING")
            echo -e "${YELLOW}⚠️  $message${NC}"
            ;;
        "INFO")
            echo -e "ℹ️  $message"
            ;;
    esac
}

# Function to wait for deployment to be ready
wait_for_deployment() {
    local deployment=$1
    local timeout=${2:-$TIMEOUT}
    
    print_status "INFO" "Waiting for deployment $deployment to be ready..."
    
    if kubectl wait --for=condition=available deployment/$deployment -n $NAMESPACE --timeout=${timeout}s; then
        print_status "SUCCESS" "Deployment $deployment is ready"
        return 0
    else
        print_status "ERROR" "Deployment $deployment failed to become ready within ${timeout}s"
        return 1
    fi
}

# Function to check pod health
check_pod_health() {
    local app_label=$1
    
    print_status "INFO" "Checking health of pods with label app=$app_label..."
    
    # Get pods with the specified label
    pods=$(kubectl get pods -n $NAMESPACE -l app=$app_label -o jsonpath='{.items[*].metadata.name}')
    
    if [ -z "$pods" ]; then
        print_status "ERROR" "No pods found with label app=$app_label"
        return 1
    fi
    
    for pod in $pods; do
        # Check pod status
        status=$(kubectl get pod $pod -n $NAMESPACE -o jsonpath='{.status.phase}')
        if [ "$status" != "Running" ]; then
            print_status "ERROR" "Pod $pod is not running (status: $status)"
            kubectl describe pod $pod -n $NAMESPACE
            return 1
        fi
        
        # Check readiness
        ready=$(kubectl get pod $pod -n $NAMESPACE -o jsonpath='{.status.conditions[?(@.type=="Ready")].status}')
        if [ "$ready" != "True" ]; then
            print_status "ERROR" "Pod $pod is not ready"
            kubectl describe pod $pod -n $NAMESPACE
            return 1
        fi
        
        print_status "SUCCESS" "Pod $pod is healthy"
    done
    
    return 0
}

# Function to test HTTP endpoint
test_endpoint() {
    local url=$1
    local expected_status=${2:-200}
    local description=$3
    
    print_status "INFO" "Testing endpoint: $url ($description)"
    
    if command -v curl >/dev/null 2>&1; then
        response=$(curl -s -o /dev/null -w "%{http_code}" "$url" || echo "000")
        if [ "$response" = "$expected_status" ]; then
            print_status "SUCCESS" "$description endpoint is responding correctly"
            return 0
        else
            print_status "ERROR" "$description endpoint returned status $response (expected $expected_status)"
            return 1
        fi
    else
        print_status "WARNING" "curl not available, skipping endpoint test for $description"
        return 0
    fi
}

# Function to check service connectivity
check_service_connectivity() {
    local service=$1
    local port=$2
    
    print_status "INFO" "Checking connectivity to service $service:$port..."
    
    # Use kubectl port-forward to test connectivity
    kubectl port-forward service/$service $port:$port -n $NAMESPACE &
    local pf_pid=$!
    
    # Wait a moment for port-forward to establish
    sleep 2
    
    # Test connectivity
    if nc -z localhost $port; then
        print_status "SUCCESS" "Service $service is accessible on port $port"
        kill $pf_pid 2>/dev/null || true
        return 0
    else
        print_status "ERROR" "Service $service is not accessible on port $port"
        kill $pf_pid 2>/dev/null || true
        return 1
    fi
}

# Function to validate database connectivity
validate_database() {
    local db_type=$1
    
    print_status "INFO" "Validating $db_type database connectivity..."
    
    case $db_type in
        "postgres")
            # Test PostgreSQL connectivity through backend health endpoint
            kubectl exec -n $NAMESPACE deployment/backend-deployment -- python -c "
import psycopg2
import os
try:
    conn = psycopg2.connect(os.environ['DATABASE_URL'])
    conn.close()
    print('PostgreSQL connection successful')
except Exception as e:
    print(f'PostgreSQL connection failed: {e}')
    exit(1)
" && print_status "SUCCESS" "PostgreSQL database is accessible" || print_status "ERROR" "PostgreSQL database is not accessible"
            ;;
        "redis")
            kubectl exec -n $NAMESPACE deployment/redis-deployment -- redis-cli ping && \
                print_status "SUCCESS" "Redis is accessible" || \
                print_status "ERROR" "Redis is not accessible"
            ;;
        "mongodb")
            kubectl exec -n $NAMESPACE deployment/mongodb-deployment -- mongosh --eval "db.adminCommand('ping')" && \
                print_status "SUCCESS" "MongoDB is accessible" || \
                print_status "ERROR" "MongoDB is not accessible"
            ;;
    esac
}

# Function to check resource usage
check_resource_usage() {
    print_status "INFO" "Checking resource usage..."
    
    # Get resource usage for all pods
    kubectl top pods -n $NAMESPACE --no-headers | while read line; do
        pod_name=$(echo $line | awk '{print $1}')
        cpu_usage=$(echo $line | awk '{print $2}')
        memory_usage=$(echo $line | awk '{print $3}')
        
        print_status "INFO" "Pod $pod_name: CPU=$cpu_usage, Memory=$memory_usage"
    done
}

# Function to validate monitoring stack
validate_monitoring() {
    print_status "INFO" "Validating monitoring stack..."
    
    # Check if Prometheus is accessible
    if kubectl get pod -n $NAMESPACE -l app=prometheus >/dev/null 2>&1; then
        print_status "SUCCESS" "Prometheus pod is running"
        
        # Test Prometheus API
        kubectl port-forward service/prometheus 9090:9090 -n $NAMESPACE &
        local prom_pid=$!
        sleep 3
        
        if curl -s http://localhost:9090/-/healthy >/dev/null; then
            print_status "SUCCESS" "Prometheus is healthy"
        else
            print_status "ERROR" "Prometheus health check failed"
        fi
        
        kill $prom_pid 2>/dev/null || true
    else
        print_status "WARNING" "Prometheus not found (monitoring may not be deployed)"
    fi
    
    # Check if Grafana is accessible
    if kubectl get pod -n $NAMESPACE -l app=grafana >/dev/null 2>&1; then
        print_status "SUCCESS" "Grafana pod is running"
    else
        print_status "WARNING" "Grafana not found (monitoring may not be deployed)"
    fi
}

# Function to validate auto-scaling
validate_autoscaling() {
    print_status "INFO" "Validating auto-scaling configuration..."
    
    # Check HPA
    hpas=$(kubectl get hpa -n $NAMESPACE -o jsonpath='{.items[*].metadata.name}')
    if [ -n "$hpas" ]; then
        for hpa in $hpas; do
            status=$(kubectl get hpa $hpa -n $NAMESPACE -o jsonpath='{.status.conditions[?(@.type=="AbleToScale")].status}')
            if [ "$status" = "True" ]; then
                print_status "SUCCESS" "HPA $hpa is able to scale"
            else
                print_status "ERROR" "HPA $hpa is not able to scale"
            fi
        done
    else
        print_status "WARNING" "No HPAs found"
    fi
}

# Function to validate backup system
validate_backup_system() {
    print_status "INFO" "Validating backup system..."
    
    # Check CronJobs
    cronjobs=$(kubectl get cronjob -n $NAMESPACE -o jsonpath='{.items[*].metadata.name}')
    if [ -n "$cronjobs" ]; then
        for cronjob in $cronjobs; do
            print_status "SUCCESS" "Backup CronJob $cronjob is configured"
        done
    else
        print_status "WARNING" "No backup CronJobs found"
    fi
}

# Function to run comprehensive validation
run_validation() {
    local exit_code=0
    
    print_status "INFO" "Starting comprehensive deployment validation..."
    
    # 1. Check namespace exists
    if kubectl get namespace $NAMESPACE >/dev/null 2>&1; then
        print_status "SUCCESS" "Namespace $NAMESPACE exists"
    else
        print_status "ERROR" "Namespace $NAMESPACE does not exist"
        exit 1
    fi
    
    # 2. Wait for all deployments to be ready
    deployments=("backend-deployment" "frontend-deployment" "postgres-deployment" "redis-deployment" "mongodb-deployment")
    for deployment in "${deployments[@]}"; do
        if ! wait_for_deployment $deployment; then
            exit_code=1
        fi
    done
    
    # 3. Check pod health
    apps=("backend" "frontend" "postgres" "redis" "mongodb")
    for app in "${apps[@]}"; do
        if ! check_pod_health $app; then
            exit_code=1
        fi
    done
    
    # 4. Validate database connectivity
    databases=("postgres" "redis" "mongodb")
    for db in "${databases[@]}"; do
        validate_database $db || exit_code=1
    done
    
    # 5. Test application endpoints
    # Note: In a real deployment, these would be the actual ingress URLs
    print_status "INFO" "Testing application endpoints..."
    
    # Port-forward to test endpoints
    kubectl port-forward service/backend-service 8000:80 -n $NAMESPACE &
    backend_pid=$!
    sleep 3
    
    test_endpoint "http://localhost:8000/health" 200 "Backend health" || exit_code=1
    test_endpoint "http://localhost:8000/ready" 200 "Backend readiness" || exit_code=1
    test_endpoint "http://localhost:8000/metrics" 200 "Metrics" || exit_code=1
    
    kill $backend_pid 2>/dev/null || true
    
    # 6. Check resource usage
    check_resource_usage
    
    # 7. Validate monitoring
    validate_monitoring
    
    # 8. Validate auto-scaling
    validate_autoscaling
    
    # 9. Validate backup system
    validate_backup_system
    
    # 10. Final summary
    if [ $exit_code -eq 0 ]; then
        print_status "SUCCESS" "All deployment validations passed! 🎉"
        print_status "INFO" "AI-HR Platform is successfully deployed and healthy"
    else
        print_status "ERROR" "Some deployment validations failed"
        print_status "INFO" "Please check the errors above and fix them before proceeding"
    fi
    
    return $exit_code
}

# Main execution
case "${1:-validate}" in
    "validate")
        run_validation
        ;;
    "quick")
        print_status "INFO" "Running quick validation..."
        for deployment in backend-deployment frontend-deployment; do
            wait_for_deployment $deployment 60
        done
        test_endpoint "http://localhost:8000/health" 200 "Backend health"
        ;;
    "monitoring")
        validate_monitoring
        ;;
    "scaling")
        validate_autoscaling
        ;;
    "backup")
        validate_backup_system
        ;;
    *)
        echo "Usage: $0 [validate|quick|monitoring|scaling|backup]"
        echo "  validate  - Run full deployment validation (default)"
        echo "  quick     - Run quick health checks"
        echo "  monitoring - Validate monitoring stack"
        echo "  scaling   - Validate auto-scaling configuration"
        echo "  backup    - Validate backup system"
        exit 1
        ;;
esac