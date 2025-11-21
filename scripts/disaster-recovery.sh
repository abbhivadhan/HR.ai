#!/bin/bash

# AI-HR Platform Disaster Recovery Script
# This script handles disaster recovery procedures

set -e

NAMESPACE="ai-hr-platform"
BACKUP_BUCKET="ai-hr-platform-backups"
RESTORE_DATE=${1:-$(date +%Y%m%d)}

echo "Starting disaster recovery for AI-HR Platform..."
echo "Restore date: $RESTORE_DATE"

# Function to restore PostgreSQL database
restore_postgres() {
    echo "Restoring PostgreSQL database..."
    
    # Download backup from cloud storage
    aws s3 cp s3://$BACKUP_BUCKET/postgres/postgres-backup-$RESTORE_DATE.sql /tmp/
    
    # Scale down backend to prevent connections
    kubectl scale deployment backend-deployment --replicas=0 -n $NAMESPACE
    
    # Wait for pods to terminate
    kubectl wait --for=delete pod -l app=backend -n $NAMESPACE --timeout=300s
    
    # Restore database
    kubectl exec -it deployment/postgres-deployment -n $NAMESPACE -- psql -U postgres -d ai_hr_platform -f /tmp/postgres-backup-$RESTORE_DATE.sql
    
    # Scale backend back up
    kubectl scale deployment backend-deployment --replicas=3 -n $NAMESPACE
    
    echo "PostgreSQL restore completed"
}

# Function to restore MongoDB
restore_mongodb() {
    echo "Restoring MongoDB database..."
    
    # Download backup from cloud storage
    aws s3 cp s3://$BACKUP_BUCKET/mongodb/mongodb-backup-$RESTORE_DATE.tar.gz /tmp/
    
    # Extract backup
    tar -xzf /tmp/mongodb-backup-$RESTORE_DATE.tar.gz -C /tmp/
    
    # Restore MongoDB
    kubectl exec -it deployment/mongodb-deployment -n $NAMESPACE -- mongorestore --uri=mongodb://localhost:27017/ai_hr_platform /tmp/mongodb-backup-$RESTORE_DATE/ai_hr_platform
    
    echo "MongoDB restore completed"
}

# Function to verify system health after restore
verify_system_health() {
    echo "Verifying system health..."
    
    # Wait for all pods to be ready
    kubectl wait --for=condition=ready pod -l app=backend -n $NAMESPACE --timeout=300s
    kubectl wait --for=condition=ready pod -l app=frontend -n $NAMESPACE --timeout=300s
    kubectl wait --for=condition=ready pod -l app=postgres -n $NAMESPACE --timeout=300s
    kubectl wait --for=condition=ready pod -l app=mongodb -n $NAMESPACE --timeout=300s
    kubectl wait --for=condition=ready pod -l app=redis -n $NAMESPACE --timeout=300s
    
    # Test API endpoints
    BACKEND_URL=$(kubectl get ingress ai-hr-platform-ingress -n $NAMESPACE -o jsonpath='{.spec.rules[1].host}')
    
    if curl -f https://$BACKEND_URL/health; then
        echo "✅ Backend health check passed"
    else
        echo "❌ Backend health check failed"
        exit 1
    fi
    
    if curl -f https://$BACKEND_URL/ready; then
        echo "✅ Backend readiness check passed"
    else
        echo "❌ Backend readiness check failed"
        exit 1
    fi
    
    echo "System health verification completed successfully"
}

# Main recovery process
case "${2:-full}" in
    "postgres")
        restore_postgres
        ;;
    "mongodb")
        restore_mongodb
        ;;
    "full")
        restore_postgres
        restore_mongodb
        ;;
    *)
        echo "Usage: $0 [RESTORE_DATE] [postgres|mongodb|full]"
        exit 1
        ;;
esac

verify_system_health

echo "Disaster recovery completed successfully!"
echo "System is now restored to state from: $RESTORE_DATE"