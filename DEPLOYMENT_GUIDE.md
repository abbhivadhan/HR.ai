# AI-HR Platform Deployment Guide

This guide provides comprehensive instructions for deploying the AI-HR Platform to production using Kubernetes with monitoring, backup, and auto-scaling capabilities.

## Prerequisites

- Kubernetes cluster (v1.21+)
- kubectl configured to access your cluster
- Docker registry access
- Helm (optional, for easier monitoring stack deployment)
- Cloud storage for backups (AWS S3, GCS, or Azure Blob)

## Quick Start

1. **Create namespace and apply configurations:**
```bash
kubectl apply -f k8s/namespace.yaml
kubectl apply -f k8s/configmap.yaml
```

2. **Deploy databases:**
```bash
kubectl apply -f k8s/database-deployment.yaml
kubectl apply -f k8s/redis-deployment.yaml
kubectl apply -f k8s/mongodb-deployment.yaml
```

3. **Deploy applications:**
```bash
kubectl apply -f k8s/backend-deployment.yaml
kubectl apply -f k8s/frontend-deployment.yaml
```

4. **Setup networking:**
```bash
kubectl apply -f k8s/ingress.yaml
```

5. **Enable auto-scaling:**
```bash
kubectl apply -f k8s/hpa.yaml
kubectl apply -f k8s/vpa.yaml
```

6. **Deploy monitoring:**
```bash
kubectl apply -f monitoring/prometheus-deployment.yaml
kubectl apply -f monitoring/grafana-deployment.yaml
kubectl apply -f monitoring/alertmanager-deployment.yaml
```

7. **Setup backups:**
```bash
kubectl apply -f k8s/backup-cronjob.yaml
```

8. **Validate deployment:**
```bash
./scripts/deployment-validation.sh
```

## Detailed Deployment Steps

### 1. Environment Setup

#### 1.1 Configure Secrets
Update the secrets in `k8s/configmap.yaml` with your actual values:
- JWT_SECRET_KEY
- DATABASE_PASSWORD
- OPENAI_API_KEY
- Email credentials
- Encryption keys

#### 1.2 Configure Domain and SSL
Update `k8s/ingress.yaml` with your actual domain names and SSL certificate configuration.

### 2. Database Deployment

#### 2.1 PostgreSQL
```bash
kubectl apply -f k8s/database-deployment.yaml
```

Wait for PostgreSQL to be ready:
```bash
kubectl wait --for=condition=ready pod -l app=postgres -n ai-hr-platform --timeout=300s
```

#### 2.2 Redis
```bash
kubectl apply -f k8s/redis-deployment.yaml
```

#### 2.3 MongoDB
```bash
kubectl apply -f k8s/mongodb-deployment.yaml
```

### 3. Application Deployment

#### 3.1 Backend API
```bash
# Build and push Docker image
docker build -t your-registry/ai-hr-platform/backend:latest ./backend
docker push your-registry/ai-hr-platform/backend:latest

# Deploy to Kubernetes
kubectl apply -f k8s/backend-deployment.yaml
```

#### 3.2 Frontend
```bash
# Build and push Docker image
docker build -t your-registry/ai-hr-platform/frontend:latest ./frontend
docker push your-registry/ai-hr-platform/frontend:latest

# Deploy to Kubernetes
kubectl apply -f k8s/frontend-deployment.yaml
```

### 4. Monitoring Setup

#### 4.1 Prometheus
```bash
kubectl apply -f monitoring/prometheus-config.yaml
kubectl apply -f monitoring/prometheus-deployment.yaml
```

#### 4.2 Grafana
```bash
kubectl apply -f monitoring/grafana-deployment.yaml
```

Access Grafana:
```bash
kubectl port-forward service/grafana 3000:3000 -n ai-hr-platform
```
Default credentials: admin/admin (change immediately)

#### 4.3 Alertmanager
```bash
kubectl apply -f monitoring/alertmanager-config.yaml
kubectl apply -f monitoring/alertmanager-deployment.yaml
```

### 5. Auto-scaling Configuration

#### 5.1 Horizontal Pod Autoscaler
```bash
kubectl apply -f k8s/hpa.yaml
```

#### 5.2 Vertical Pod Autoscaler (optional)
```bash
kubectl apply -f k8s/vpa.yaml
```

#### 5.3 Cluster Autoscaler
```bash
kubectl apply -f k8s/cluster-autoscaler.yaml
```

#### 5.4 Intelligent Scaling (optional)
Deploy the custom scaling service:
```bash
kubectl create configmap scaling-policy --from-file=scripts/scaling-policy.py -n ai-hr-platform
kubectl apply -f k8s/intelligent-scaler-deployment.yaml  # You would need to create this
```

### 6. Backup and Disaster Recovery

#### 6.1 Automated Backups
```bash
kubectl apply -f k8s/backup-cronjob.yaml
```

#### 6.2 Test Disaster Recovery
```bash
# Test backup restoration
./scripts/disaster-recovery.sh 20241027 postgres
```

### 7. Security Configuration

#### 7.1 Network Policies
Create network policies to restrict pod-to-pod communication:
```yaml
# Example network policy (create as needed)
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: ai-hr-platform-netpol
  namespace: ai-hr-platform
spec:
  podSelector: {}
  policyTypes:
  - Ingress
  - Egress
  ingress:
  - from:
    - namespaceSelector:
        matchLabels:
          name: ai-hr-platform
```

#### 7.2 Pod Security Policies
Implement pod security policies for enhanced security.

### 8. SSL/TLS Configuration

#### 8.1 Cert-Manager (recommended)
```bash
# Install cert-manager
kubectl apply -f https://github.com/jetstack/cert-manager/releases/download/v1.8.0/cert-manager.yaml

# Create ClusterIssuer
kubectl apply -f - <<EOF
apiVersion: cert-manager.io/v1
kind: ClusterIssuer
metadata:
  name: letsencrypt-prod
spec:
  acme:
    server: https://acme-v02.api.letsencrypt.org/directory
    email: admin@ai-hr-platform.com
    privateKeySecretRef:
      name: letsencrypt-prod
    solvers:
    - http01:
        ingress:
          class: nginx
EOF
```

## Monitoring and Observability

### Metrics Available
- HTTP request metrics (rate, duration, errors)
- System metrics (CPU, memory, disk)
- Business metrics (assessments, interviews, job matches)
- Database connection metrics
- AI model inference times

### Dashboards
Import the following Grafana dashboards:
- Application Performance Dashboard
- Infrastructure Metrics Dashboard
- Business Metrics Dashboard
- Alert Status Dashboard

### Alerts
Key alerts configured:
- High CPU/Memory usage
- Database connectivity issues
- High error rates
- Slow response times
- Failed backups

## Scaling Policies

### Automatic Scaling Triggers
- CPU usage > 70%
- Memory usage > 80%
- Response time > 2 seconds
- Error rate > 5%
- Assessment queue > 50 items
- Active interviews > 10

### Manual Scaling
```bash
# Scale backend manually
kubectl scale deployment backend-deployment --replicas=5 -n ai-hr-platform

# Scale frontend manually
kubectl scale deployment frontend-deployment --replicas=3 -n ai-hr-platform
```

## Backup and Recovery

### Backup Schedule
- PostgreSQL: Daily at 2 AM UTC
- MongoDB: Daily at 3 AM UTC
- Retention: 30 days

### Recovery Procedures
1. **Database Recovery:**
```bash
./scripts/disaster-recovery.sh YYYYMMDD postgres
```

2. **Full System Recovery:**
```bash
./scripts/disaster-recovery.sh YYYYMMDD full
```

## Troubleshooting

### Common Issues

#### 1. Pods Not Starting
```bash
# Check pod status
kubectl get pods -n ai-hr-platform

# Check pod logs
kubectl logs <pod-name> -n ai-hr-platform

# Describe pod for events
kubectl describe pod <pod-name> -n ai-hr-platform
```

#### 2. Database Connection Issues
```bash
# Check database pod logs
kubectl logs deployment/postgres-deployment -n ai-hr-platform

# Test database connectivity
kubectl exec -it deployment/backend-deployment -n ai-hr-platform -- python -c "
import psycopg2
import os
conn = psycopg2.connect(os.environ['DATABASE_URL'])
print('Database connection successful')
"
```

#### 3. High Resource Usage
```bash
# Check resource usage
kubectl top pods -n ai-hr-platform
kubectl top nodes

# Check HPA status
kubectl get hpa -n ai-hr-platform
```

#### 4. SSL Certificate Issues
```bash
# Check certificate status
kubectl get certificates -n ai-hr-platform
kubectl describe certificate ai-hr-platform-tls -n ai-hr-platform
```

### Health Checks

#### Application Health
```bash
# Check all endpoints
curl https://api.ai-hr-platform.com/health
curl https://api.ai-hr-platform.com/ready
curl https://api.ai-hr-platform.com/metrics
```

#### Infrastructure Health
```bash
# Run comprehensive validation
./scripts/deployment-validation.sh

# Quick health check
./scripts/deployment-validation.sh quick
```

## Performance Optimization

### Database Optimization
- Enable connection pooling
- Configure appropriate indexes
- Monitor slow queries
- Regular VACUUM and ANALYZE

### Application Optimization
- Enable Redis caching
- Optimize AI model inference
- Use CDN for static assets
- Implement request compression

### Kubernetes Optimization
- Set appropriate resource requests/limits
- Use node affinity for database pods
- Configure pod disruption budgets
- Implement graceful shutdown

## Security Best Practices

1. **Network Security:**
   - Use network policies
   - Enable TLS everywhere
   - Restrict ingress traffic

2. **Pod Security:**
   - Run as non-root user
   - Use read-only root filesystem
   - Drop unnecessary capabilities

3. **Secret Management:**
   - Use Kubernetes secrets
   - Rotate secrets regularly
   - Consider external secret management

4. **Image Security:**
   - Scan images for vulnerabilities
   - Use minimal base images
   - Keep images updated

## Maintenance

### Regular Tasks
- Monitor resource usage
- Review and rotate secrets
- Update container images
- Test backup/recovery procedures
- Review and update scaling policies

### Updates and Upgrades
1. Test in staging environment
2. Create backup before upgrade
3. Use rolling updates
4. Monitor during deployment
5. Have rollback plan ready

## Support and Monitoring

### Key Metrics to Monitor
- Application response times
- Error rates
- Resource utilization
- Database performance
- Backup success rates

### Alerting Channels
- Email notifications for critical alerts
- Slack integration for team notifications
- PagerDuty for on-call escalation

### Log Aggregation
Consider implementing centralized logging with:
- ELK Stack (Elasticsearch, Logstash, Kibana)
- Fluentd for log collection
- Structured logging in applications

This deployment guide provides a comprehensive foundation for running the AI-HR Platform in production with enterprise-grade monitoring, scaling, and reliability features.