# AI-HR Platform Go-Live Procedures

This document outlines the step-by-step procedures for taking the AI-HR Platform live in production.

## Pre-Go-Live Final Checks

### 1. System Health Verification
```bash
# Run comprehensive deployment validation
./scripts/deployment-validation.sh

# Check all pods are running
kubectl get pods -n ai-hr-platform

# Verify all services are healthy
kubectl get services -n ai-hr-platform

# Check ingress status
kubectl get ingress -n ai-hr-platform
```

### 2. Database Final Validation
```bash
# Verify database migrations are complete
kubectl exec -n ai-hr-platform deployment/backend-deployment -- python -m alembic current

# Test database connectivity
kubectl exec -n ai-hr-platform deployment/backend-deployment -- python -c "
from app.database import engine
with engine.connect() as conn:
    result = conn.execute('SELECT 1')
    print('Database connection successful')
"

# Verify backup system
kubectl get cronjobs -n ai-hr-platform
```

### 3. Security Final Check
```bash
# Run security assessment
cd backend && python security_assessment.py

# Verify SSL certificates
curl -I https://api.ai-hr-platform.com/health
openssl s_client -connect api.ai-hr-platform.com:443 -servername api.ai-hr-platform.com

# Check security headers
curl -I https://api.ai-hr-platform.com/health | grep -E "(X-Content-Type-Options|X-Frame-Options|Strict-Transport-Security)"
```

### 4. Performance Baseline
```bash
# Run load tests to establish baseline
cd tests/load && python -m pytest test_performance_load.py -v

# Check resource utilization
kubectl top pods -n ai-hr-platform
kubectl top nodes
```

## Go-Live Sequence

### Phase 1: Infrastructure Activation (T-60 minutes)

#### 1.1 Monitoring Systems
```bash
# Ensure Prometheus is collecting metrics
kubectl port-forward -n ai-hr-platform service/prometheus 9090:9090 &
curl http://localhost:9090/-/healthy

# Verify Grafana dashboards
kubectl port-forward -n ai-hr-platform service/grafana 3000:3000 &
# Access http://localhost:3000 and verify dashboards load

# Check Alertmanager
kubectl port-forward -n ai-hr-platform service/alertmanager 9093:9093 &
curl http://localhost:9093/-/healthy
```

#### 1.2 Backup Systems
```bash
# Trigger manual backup to ensure system works
kubectl create job --from=cronjob/postgres-backup manual-backup-$(date +%Y%m%d-%H%M%S) -n ai-hr-platform

# Verify backup completion
kubectl logs job/manual-backup-$(date +%Y%m%d-%H%M%S) -n ai-hr-platform
```

#### 1.3 Auto-scaling Validation
```bash
# Check HPA status
kubectl get hpa -n ai-hr-platform

# Verify metrics server
kubectl top pods -n ai-hr-platform
```

### Phase 2: Application Readiness (T-30 minutes)

#### 2.1 Service Health Checks
```bash
# Backend health check
curl https://api.ai-hr-platform.com/health
curl https://api.ai-hr-platform.com/ready

# Frontend accessibility
curl -I https://app.ai-hr-platform.com

# Database connectivity through API
curl https://api.ai-hr-platform.com/api/health/database
```

#### 2.2 AI/ML Services Validation
```bash
# Test AI assessment service
curl -X POST https://api.ai-hr-platform.com/api/assessments/health \
  -H "Content-Type: application/json"

# Test job matching service
curl https://api.ai-hr-platform.com/api/matching/health

# Verify model versions
curl https://api.ai-hr-platform.com/api/models/versions
```

#### 2.3 Integration Services
```bash
# Test email service
curl -X POST https://api.ai-hr-platform.com/api/notifications/test-email \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"email": "test@ai-hr-platform.com"}'

# Test file upload service
curl -X POST https://api.ai-hr-platform.com/api/files/health

# Test webhook system
curl https://api.ai-hr-platform.com/api/webhooks/health
```

### Phase 3: DNS and Traffic Routing (T-15 minutes)

#### 3.1 DNS Configuration
```bash
# Update DNS records (example using AWS Route 53)
aws route53 change-resource-record-sets --hosted-zone-id Z123456789 --change-batch '{
  "Changes": [{
    "Action": "UPSERT",
    "ResourceRecordSet": {
      "Name": "api.ai-hr-platform.com",
      "Type": "A",
      "AliasTarget": {
        "DNSName": "production-alb-123456789.us-west-2.elb.amazonaws.com",
        "EvaluateTargetHealth": true,
        "HostedZoneId": "Z1D633PJN98FT9"
      }
    }
  }]
}'

# Verify DNS propagation
nslookup api.ai-hr-platform.com
nslookup app.ai-hr-platform.com
```

#### 3.2 CDN Configuration
```bash
# Update CDN origin (example using CloudFront)
aws cloudfront update-distribution --id E123456789 --distribution-config '{
  "Origins": {
    "Items": [{
      "Id": "ai-hr-platform-origin",
      "DomainName": "app.ai-hr-platform.com",
      "CustomOriginConfig": {
        "HTTPPort": 443,
        "HTTPSPort": 443,
        "OriginProtocolPolicy": "https-only"
      }
    }]
  }
}'

# Purge CDN cache
aws cloudfront create-invalidation --distribution-id E123456789 --paths "/*"
```

#### 3.3 SSL Certificate Validation
```bash
# Verify SSL certificates are working
echo | openssl s_client -servername api.ai-hr-platform.com -connect api.ai-hr-platform.com:443 2>/dev/null | openssl x509 -noout -dates

echo | openssl s_client -servername app.ai-hr-platform.com -connect app.ai-hr-platform.com:443 2>/dev/null | openssl x509 -noout -dates
```

### Phase 4: Go-Live Activation (T-0)

#### 4.1 Final System Check
```bash
# Run end-to-end tests
cd tests/e2e && python -m pytest test_complete_user_journeys.py -v

# Verify all critical endpoints
endpoints=(
  "https://api.ai-hr-platform.com/health"
  "https://api.ai-hr-platform.com/ready"
  "https://app.ai-hr-platform.com"
  "https://api.ai-hr-platform.com/docs"
)

for endpoint in "${endpoints[@]}"; do
  echo "Testing $endpoint"
  curl -f -s -o /dev/null "$endpoint" && echo "✅ OK" || echo "❌ FAILED"
done
```

#### 4.2 Enable Production Traffic
```bash
# If using traffic splitting, gradually increase traffic
# Example: Update ingress weights or load balancer configuration

# Enable production ingress
kubectl patch ingress ai-hr-platform-ingress -n ai-hr-platform -p '{
  "metadata": {
    "annotations": {
      "nginx.ingress.kubernetes.io/canary": "false"
    }
  }
}'

# Verify traffic is flowing
kubectl logs -f deployment/backend-deployment -n ai-hr-platform | grep "GET /health"
```

#### 4.3 Activate Monitoring Alerts
```bash
# Enable production alerting rules
kubectl apply -f monitoring/production-alerts.yaml

# Verify alerts are loaded
kubectl port-forward -n ai-hr-platform service/prometheus 9090:9090 &
curl http://localhost:9090/api/v1/rules | jq '.data.groups[].rules[].name'
```

## Post-Go-Live Monitoring (First 4 Hours)

### Hour 1: Critical Monitoring
```bash
# Monitor key metrics every 5 minutes
watch -n 300 '
echo "=== System Health ==="
kubectl get pods -n ai-hr-platform | grep -v Running
echo "=== Response Times ==="
curl -w "@curl-format.txt" -s -o /dev/null https://api.ai-hr-platform.com/health
echo "=== Error Rates ==="
kubectl logs --tail=100 deployment/backend-deployment -n ai-hr-platform | grep ERROR | wc -l
'
```

### Hour 2-4: Functional Validation
```bash
# Test user registration flow
curl -X POST https://api.ai-hr-platform.com/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "golive-test@example.com",
    "password": "TestPassword123!",
    "first_name": "GoLive",
    "last_name": "Test",
    "user_type": "candidate"
  }'

# Test assessment system
# (This would involve a more complex flow with authentication)

# Monitor database performance
kubectl exec -n ai-hr-platform deployment/postgres-deployment -- psql -U postgres -d aihr -c "
SELECT 
  schemaname,
  tablename,
  n_tup_ins as inserts,
  n_tup_upd as updates,
  n_tup_del as deletes
FROM pg_stat_user_tables 
ORDER BY n_tup_ins + n_tup_upd + n_tup_del DESC 
LIMIT 10;
"
```

## Success Metrics Validation

### Technical Metrics
```bash
# Response time validation
for i in {1..10}; do
  curl -w "Response time: %{time_total}s\n" -s -o /dev/null https://api.ai-hr-platform.com/health
done

# Error rate check
kubectl logs --since=1h deployment/backend-deployment -n ai-hr-platform | \
  grep -E "(ERROR|CRITICAL)" | wc -l

# Throughput measurement
kubectl logs --since=1h deployment/backend-deployment -n ai-hr-platform | \
  grep "GET\|POST\|PUT\|DELETE" | wc -l
```

### Business Metrics
```bash
# User registration success rate
curl -H "Authorization: Bearer $ADMIN_TOKEN" \
  https://api.ai-hr-platform.com/api/analytics/registration-success-rate

# Assessment completion rate
curl -H "Authorization: Bearer $ADMIN_TOKEN" \
  https://api.ai-hr-platform.com/api/analytics/assessment-completion-rate

# Job matching accuracy
curl -H "Authorization: Bearer $ADMIN_TOKEN" \
  https://api.ai-hr-platform.com/api/analytics/matching-accuracy
```

## Rollback Procedures

### Immediate Rollback (if critical issues detected)
```bash
# Rollback application deployments
kubectl rollout undo deployment/backend-deployment -n ai-hr-platform
kubectl rollout undo deployment/frontend-deployment -n ai-hr-platform

# Wait for rollback to complete
kubectl rollout status deployment/backend-deployment -n ai-hr-platform
kubectl rollout status deployment/frontend-deployment -n ai-hr-platform

# Verify rollback success
curl https://api.ai-hr-platform.com/health
```

### DNS Rollback (if needed)
```bash
# Revert DNS to previous values
aws route53 change-resource-record-sets --hosted-zone-id Z123456789 --change-batch '{
  "Changes": [{
    "Action": "UPSERT",
    "ResourceRecordSet": {
      "Name": "api.ai-hr-platform.com",
      "Type": "A",
      "AliasTarget": {
        "DNSName": "staging-alb-123456789.us-west-2.elb.amazonaws.com",
        "EvaluateTargetHealth": true,
        "HostedZoneId": "Z1D633PJN98FT9"
      }
    }
  }]
}'
```

### Database Rollback (if data corruption detected)
```bash
# Restore from latest backup
./scripts/disaster-recovery.sh $(date +%Y%m%d) postgres

# Verify data integrity
kubectl exec -n ai-hr-platform deployment/backend-deployment -- python -c "
from app.database import SessionLocal
from app.models.user import User
db = SessionLocal()
user_count = db.query(User).count()
print(f'User count after restore: {user_count}')
db.close()
"
```

## Communication Plan

### Internal Team Notifications
```bash
# Slack notification (example)
curl -X POST -H 'Content-type: application/json' \
  --data '{"text":"🚀 AI-HR Platform is now LIVE in production! All systems operational."}' \
  $SLACK_WEBHOOK_URL

# Email notification to stakeholders
curl -X POST https://api.ai-hr-platform.com/api/notifications/send-email \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "to": ["stakeholders@ai-hr-platform.com"],
    "subject": "AI-HR Platform Production Go-Live Successful",
    "body": "The AI-HR Platform has successfully gone live in production. All systems are operational and monitoring is active."
  }'
```

### Status Page Update
```bash
# Update status page (example using StatusPage.io API)
curl -X PATCH https://api.statuspage.io/v1/pages/$PAGE_ID/components/$COMPONENT_ID \
  -H "Authorization: OAuth $STATUSPAGE_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "component": {
      "status": "operational"
    }
  }'
```

## Troubleshooting Common Go-Live Issues

### Issue 1: High Response Times
```bash
# Check pod resource usage
kubectl top pods -n ai-hr-platform

# Scale up if needed
kubectl scale deployment backend-deployment --replicas=5 -n ai-hr-platform

# Check database connections
kubectl exec -n ai-hr-platform deployment/backend-deployment -- python -c "
from app.database import engine
print(f'Database pool size: {engine.pool.size()}')
print(f'Checked out connections: {engine.pool.checkedout()}')
"
```

### Issue 2: Database Connection Issues
```bash
# Check database pod status
kubectl describe pod -l app=postgres -n ai-hr-platform

# Test database connectivity
kubectl exec -n ai-hr-platform deployment/postgres-deployment -- pg_isready

# Check connection pool
kubectl logs deployment/backend-deployment -n ai-hr-platform | grep "database"
```

### Issue 3: SSL Certificate Issues
```bash
# Check certificate expiration
echo | openssl s_client -servername api.ai-hr-platform.com -connect api.ai-hr-platform.com:443 2>/dev/null | openssl x509 -noout -dates

# Renew certificate if needed (cert-manager)
kubectl delete certificate ai-hr-platform-tls -n ai-hr-platform
kubectl apply -f k8s/ingress.yaml
```

### Issue 4: Memory/CPU Issues
```bash
# Check resource usage
kubectl top pods -n ai-hr-platform

# Check for OOMKilled pods
kubectl get pods -n ai-hr-platform -o jsonpath='{range .items[*]}{.metadata.name}{"\t"}{.status.containerStatuses[0].restartCount}{"\t"}{.status.containerStatuses[0].lastState.terminated.reason}{"\n"}{end}'

# Increase resource limits if needed
kubectl patch deployment backend-deployment -n ai-hr-platform -p '{
  "spec": {
    "template": {
      "spec": {
        "containers": [{
          "name": "backend",
          "resources": {
            "limits": {
              "memory": "2Gi",
              "cpu": "1000m"
            }
          }
        }]
      }
    }
  }
}'
```

## Go-Live Checklist Summary

### Pre-Go-Live (T-60 to T-15)
- [ ] All deployment validation tests pass
- [ ] Monitoring systems operational
- [ ] Backup systems tested
- [ ] Security checks completed
- [ ] Performance baseline established
- [ ] DNS records prepared
- [ ] SSL certificates validated

### Go-Live (T-0)
- [ ] Final system health check passed
- [ ] DNS records updated
- [ ] CDN configured and cache purged
- [ ] Production traffic enabled
- [ ] Monitoring alerts activated
- [ ] Team notifications sent

### Post-Go-Live (T+0 to T+4h)
- [ ] Critical metrics monitored
- [ ] User workflows tested
- [ ] Error rates within acceptable limits
- [ ] Performance metrics acceptable
- [ ] No critical issues detected
- [ ] Success metrics validated

### Sign-off
- [ ] **Technical Lead**: _________________ Time: _______
- [ ] **DevOps Engineer**: _________________ Time: _______
- [ ] **Product Manager**: _________________ Time: _______

**Go-Live Status**: [ ] Successful [ ] Issues Detected [ ] Rollback Required

**Go-Live Completed At**: _______________
**Next Review**: _______________