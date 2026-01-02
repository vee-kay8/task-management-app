# Operational Runbook
## Task Management Application - Production Operations Guide

**Version**: 1.0.0  
**Last Updated**: January 2, 2026  
**Target Audience**: DevOps, SRE, Operations Teams

---

## Table of Contents

1. [Daily Operations](#daily-operations)
2. [Deployment Procedures](#deployment-procedures)
3. [Monitoring & Alerts](#monitoring--alerts)
4. [Backup & Recovery](#backup--recovery)
5. [Incident Response](#incident-response)
6. [Maintenance Windows](#maintenance-windows)
7. [Scaling Procedures](#scaling-procedures)
8. [Security Operations](#security-operations)
9. [Troubleshooting Playbooks](#troubleshooting-playbooks)
10. [Emergency Contacts](#emergency-contacts)

---

## Daily Operations

### Morning Health Check (5 minutes)

**Time**: 9:00 AM daily  
**Owner**: On-call engineer

```bash
#!/bin/bash
# daily-health-check.sh

echo "=== Daily Health Check - $(date) ==="

# 1. Check all services are running
echo -e "\n1. Service Status:"
docker-compose -f docker-compose.hub.yml ps

# 2. Verify health endpoints
echo -e "\n2. Health Endpoints:"
curl -s http://localhost:5000/api/health | jq
curl -s http://localhost:3000/api/health | jq

# 3. Check resource usage
echo -e "\n3. Resource Usage:"
docker stats --no-stream --format "table {{.Container}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.MemPerc}}"

# 4. Check disk space
echo -e "\n4. Disk Space:"
docker system df

# 5. Check recent errors
echo -e "\n5. Recent Errors (last 24h):"
docker-compose logs --since 24h | grep -i -E "(error|fatal|exception)" | tail -20

# 6. Database health
echo -e "\n6. Database Health:"
docker-compose exec -T db pg_isready -U taskuser
docker-compose exec -T db psql -U taskuser -d taskdb -c "SELECT count(*) as active_connections FROM pg_stat_activity;"

echo -e "\n=== Health Check Complete ==="
```

**Expected Results**:
- ✅ All services: `Up X minutes (healthy)`
- ✅ Health endpoints: `{"status":"healthy"}`
- ✅ CPU usage: <50%
- ✅ Memory usage: <70%
- ✅ Disk usage: <80%
- ✅ No critical errors in logs
- ✅ Database: `accepting connections`

**Action if Failed**:
- Services unhealthy → Restart: `docker-compose restart`
- High resource usage → Check [Performance Issues](#performance-issues)
- Errors in logs → Check [Troubleshooting Playbooks](#troubleshooting-playbooks)

---

### Log Review (10 minutes)

**Time**: 10:00 AM daily  
**Owner**: On-call engineer

```bash
# Check logs for anomalies
docker-compose logs --since 24h --tail=500 > daily-logs-$(date +%Y%m%d).txt

# Search for issues
grep -i -E "(error|exception|timeout|failed)" daily-logs-*.txt

# Check API response times
docker-compose logs backend --since 24h | grep "GET" | tail -100

# Check database slow queries
docker-compose exec db psql -U taskuser -d taskdb -c "
  SELECT query, calls, mean_time 
  FROM pg_stat_statements 
  WHERE mean_time > 100 
  ORDER BY mean_time DESC 
  LIMIT 10;"
```

**Action Items**:
- Document any recurring errors
- Create tickets for persistent issues
- Update monitoring thresholds if needed

---

### Backup Verification (5 minutes)

**Time**: 11:00 AM daily  
**Owner**: On-call engineer

```bash
# Verify last backup exists
ls -lh /backups/database/backup_$(date +%Y%m%d)*.sql

# Check backup size (should be >1MB)
du -h /backups/database/backup_$(date +%Y%m%d)*.sql

# Verify backup integrity (sample check)
head -20 /backups/database/backup_$(date +%Y%m%d)*.sql
```

**Action if Failed**:
- Missing backup → Run manual backup immediately
- Small file size (<100KB) → Investigate backup script
- Corrupted file → Check disk space and retry

---

## Deployment Procedures

### Standard Deployment (Zero Downtime)

**Duration**: 5-10 minutes  
**Risk**: Low  
**Prerequisites**: Testing in staging complete, backup verified

#### Pre-Deployment Checklist

```
- [ ] Staging tests passed
- [ ] Database backup completed (last 24h)
- [ ] Team notified (#deployments channel)
- [ ] Rollback plan ready
- [ ] Off-peak hours (if possible)
- [ ] On-call engineer available
```

#### Deployment Steps

```bash
#!/bin/bash
# deploy-production.sh

set -e  # Exit on error

VERSION="${1:-latest}"
BACKUP_DIR="/backups/database"

echo "=== Production Deployment - Version: $VERSION ==="

# Step 1: Backup database
echo "1. Creating database backup..."
timestamp=$(date +%Y%m%d_%H%M%S)
docker exec taskmanagement_postgres pg_dump -U taskuser taskdb > "$BACKUP_DIR/pre-deploy-$timestamp.sql"
echo "   Backup saved: $BACKUP_DIR/pre-deploy-$timestamp.sql"

# Step 2: Pull latest images
echo "2. Pulling Docker images..."
docker-compose -f docker-compose.hub.yml pull

# Step 3: Rolling update (one service at a time)
echo "3. Updating backend..."
docker-compose -f docker-compose.hub.yml up -d --no-deps backend
sleep 10  # Wait for health check

# Verify backend
if ! curl -sf http://localhost:5000/api/health > /dev/null; then
  echo "ERROR: Backend health check failed!"
  echo "Rolling back..."
  docker-compose -f docker-compose.hub.yml restart backend
  exit 1
fi
echo "   Backend healthy ✓"

echo "4. Updating frontend..."
docker-compose -f docker-compose.hub.yml up -d --no-deps frontend
sleep 10

# Verify frontend
if ! curl -sf http://localhost:3000/api/health > /dev/null; then
  echo "ERROR: Frontend health check failed!"
  echo "Rolling back..."
  docker-compose -f docker-compose.hub.yml restart frontend
  exit 1
fi
echo "   Frontend healthy ✓"

# Step 4: Verify deployment
echo "5. Final verification..."
docker-compose -f docker-compose.hub.yml ps

echo "=== Deployment Complete ✓ ==="
echo "Deployed version: $VERSION"
echo "Backup location: $BACKUP_DIR/pre-deploy-$timestamp.sql"
```

#### Post-Deployment Verification

```bash
# 1. Health checks
curl http://localhost:5000/api/health
curl http://localhost:3000/api/health

# 2. Check logs for errors
docker-compose logs --tail=50 backend frontend

# 3. Monitor for 15 minutes
watch -n 5 'docker-compose ps && docker stats --no-stream'

# 4. Check response times
for i in {1..10}; do 
  curl -s -w "Time: %{time_total}s\n" -o /dev/null http://localhost:5000/api/health
done
```

#### Rollback Procedure

```bash
#!/bin/bash
# rollback-deployment.sh

echo "=== ROLLBACK INITIATED ==="

# Option 1: Restart to previous image (if still cached)
docker-compose -f docker-compose.hub.yml restart

# Option 2: Restore from backup (if database changes)
BACKUP_FILE="/backups/database/pre-deploy-TIMESTAMP.sql"
cat $BACKUP_FILE | docker exec -i taskmanagement_postgres psql -U taskuser taskdb

# Option 3: Pull specific previous version
# docker-compose -f docker-compose.hub.yml down
# Edit docker-compose.hub.yml to use previous version tag
# docker-compose -f docker-compose.hub.yml up -d

echo "=== ROLLBACK COMPLETE ==="
echo "Verify services: docker-compose ps"
```

---

### Emergency Hotfix Deployment

**Duration**: 3-5 minutes  
**Risk**: Medium  
**Use Case**: Critical bug fix, security patch

```bash
#!/bin/bash
# emergency-hotfix.sh

set -e

echo "=== EMERGENCY HOTFIX DEPLOYMENT ==="

# Quick backup
docker exec taskmanagement_postgres pg_dump -U taskuser taskdb > /backups/emergency-$(date +%Y%m%d_%H%M%S).sql

# Pull and deploy immediately
docker-compose -f docker-compose.hub.yml pull
docker-compose -f docker-compose.hub.yml up -d --force-recreate

# Monitor for 5 minutes
echo "Monitoring for 5 minutes..."
for i in {1..30}; do
  echo "Check $i/30:"
  docker-compose ps
  curl -sf http://localhost:5000/api/health && echo "Backend: OK" || echo "Backend: FAIL"
  sleep 10
done

echo "=== HOTFIX COMPLETE ==="
```

---

## Monitoring & Alerts

### Key Metrics to Monitor

#### Application Metrics

```bash
# CPU Usage Alert (>80% for 5 min)
docker stats --no-stream --format "{{.CPUPerc}}" taskmanagement_backend

# Memory Usage Alert (>85%)
docker stats --no-stream --format "{{.MemPerc}}" taskmanagement_backend

# API Response Time (>500ms average)
curl -w "%{time_total}" -o /dev/null -s http://localhost:5000/api/health

# Error Rate (>5% of requests)
docker-compose logs backend --since 5m | grep -c "ERROR"
```

#### Database Metrics

```bash
# Database connections (>80% of max)
docker-compose exec db psql -U taskuser -d taskdb -c "
  SELECT count(*) FROM pg_stat_activity;"

# Database size (>5GB)
docker-compose exec db psql -U taskuser -d taskdb -c "
  SELECT pg_size_pretty(pg_database_size('taskdb'));"

# Slow queries (>1000ms)
docker-compose exec db psql -U taskuser -d taskdb -c "
  SELECT count(*) FROM pg_stat_statements WHERE mean_time > 1000;"
```

#### System Metrics

```bash
# Disk usage (>80%)
df -h | grep -E "(/$|/var/lib/docker)"

# Docker disk usage (>10GB)
docker system df

# Container restarts (any)
docker ps --filter "status=restarting"
```

### Alert Thresholds

| Metric | Warning | Critical | Action |
|--------|---------|----------|--------|
| CPU Usage | >70% | >90% | Scale up |
| Memory Usage | >70% | >85% | Restart/Scale |
| Disk Usage | >75% | >90% | Clean up |
| API Latency | >300ms | >1000ms | Investigate |
| Error Rate | >2% | >5% | Page on-call |
| DB Connections | >70 | >90 | Check leaks |
| Container Restarts | 1+ | 3+ | Investigate |

### Monitoring Dashboard Setup

```bash
# Install Prometheus & Grafana (optional)
docker run -d --name=prometheus -p 9090:9090 prom/prometheus
docker run -d --name=grafana -p 3001:3000 grafana/grafana

# Configure metrics endpoint
# Add to backend: prometheus-flask-exporter
# Add to docker-compose.yml:
#   prometheus:
#     image: prom/prometheus
#     volumes:
#       - ./prometheus.yml:/etc/prometheus/prometheus.yml
```

---

## Backup & Recovery

### Automated Daily Backup

**Time**: 2:00 AM daily  
**Retention**: 30 days  
**Location**: `/backups/database/`

```bash
#!/bin/bash
# /etc/cron.d/daily-backup
# 0 2 * * * /opt/scripts/backup-database.sh

BACKUP_DIR="/backups/database"
DATE=$(date +%Y%m%d)
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
RETENTION_DAYS=30

# Create backup
docker exec taskmanagement_postgres pg_dump -U taskuser taskdb | gzip > "$BACKUP_DIR/backup_${TIMESTAMP}.sql.gz"

# Verify backup
if [ ! -f "$BACKUP_DIR/backup_${TIMESTAMP}.sql.gz" ]; then
  echo "ERROR: Backup failed!" | mail -s "Backup Failure" ops@example.com
  exit 1
fi

# Check size (should be >100KB)
SIZE=$(stat -f%z "$BACKUP_DIR/backup_${TIMESTAMP}.sql.gz" 2>/dev/null || stat -c%s "$BACKUP_DIR/backup_${TIMESTAMP}.sql.gz")
if [ $SIZE -lt 100000 ]; then
  echo "WARNING: Backup file too small ($SIZE bytes)" | mail -s "Backup Warning" ops@example.com
fi

# Clean old backups
find $BACKUP_DIR -name "backup_*.sql.gz" -mtime +$RETENTION_DAYS -delete

# Upload to S3 (optional)
# aws s3 cp "$BACKUP_DIR/backup_${TIMESTAMP}.sql.gz" s3://backups-bucket/taskapp/

echo "Backup complete: backup_${TIMESTAMP}.sql.gz"
```

### Manual Backup

```bash
# Full backup
docker exec taskmanagement_postgres pg_dump -U taskuser taskdb > backup_manual_$(date +%Y%m%d_%H%M%S).sql

# Compressed backup
docker exec taskmanagement_postgres pg_dump -U taskuser taskdb | gzip > backup_manual_$(date +%Y%m%d_%H%M%S).sql.gz

# Schema only
docker exec taskmanagement_postgres pg_dump -U taskuser --schema-only taskdb > schema_$(date +%Y%m%d).sql

# Data only
docker exec taskmanagement_postgres pg_dump -U taskuser --data-only taskdb > data_$(date +%Y%m%d).sql
```

### Recovery Procedures

#### Full Database Restore

```bash
#!/bin/bash
# restore-database.sh

BACKUP_FILE="${1:?Usage: $0 <backup-file.sql>}"

echo "=== DATABASE RESTORE INITIATED ==="
echo "WARNING: This will DROP and RECREATE the database!"
read -p "Continue? (type 'yes'): " confirm

if [ "$confirm" != "yes" ]; then
  echo "Restore cancelled"
  exit 1
fi

# 1. Stop backend (prevent writes)
docker-compose stop backend frontend

# 2. Drop and recreate database
docker-compose exec db psql -U taskuser -c "DROP DATABASE IF EXISTS taskdb;"
docker-compose exec db psql -U taskuser -c "CREATE DATABASE taskdb;"

# 3. Restore from backup
if [[ $BACKUP_FILE == *.gz ]]; then
  gunzip -c $BACKUP_FILE | docker exec -i taskmanagement_postgres psql -U taskuser taskdb
else
  cat $BACKUP_FILE | docker exec -i taskmanagement_postgres psql -U taskuser taskdb
fi

# 4. Verify restore
echo "Verifying restore..."
docker-compose exec db psql -U taskuser -d taskdb -c "\dt"

# 5. Restart services
docker-compose start backend frontend

# 6. Health check
sleep 10
curl http://localhost:5000/api/health

echo "=== RESTORE COMPLETE ==="
```

#### Point-in-Time Recovery (PITR)

```bash
# If using WAL archiving (PostgreSQL)
# 1. Restore base backup
# 2. Apply WAL files up to target time
# 3. Verify and bring online

# See PostgreSQL PITR documentation for detailed steps
```

---

## Incident Response

### Severity Levels

| Level | Description | Response Time | Example |
|-------|-------------|---------------|---------|
| P0 (Critical) | Complete outage | <15 min | All services down |
| P1 (High) | Major degradation | <30 min | Database unavailable |
| P2 (Medium) | Partial degradation | <2 hours | Slow API responses |
| P3 (Low) | Minor issue | <24 hours | Single feature broken |

### P0 Incident Response

**Complete Service Outage**

```bash
# IMMEDIATE ACTIONS (5 minutes)

# 1. Acknowledge incident
echo "P0 Incident: $(date)" >> /var/log/incidents.log

# 2. Check if services are running
docker-compose ps

# 3. If services are down, restart
docker-compose restart

# 4. If restart fails, check logs
docker-compose logs --tail=100

# 5. Emergency recovery
docker-compose down
docker-compose up -d

# 6. Notify stakeholders
# Send to #incidents Slack channel

# 7. Monitor continuously
watch -n 5 'docker-compose ps && curl -s http://localhost:5000/api/health'
```

### P1 Incident Response

**Database Connection Issues**

```bash
# 1. Check database status
docker-compose ps db
docker-compose exec db pg_isready

# 2. Check connections
docker-compose exec db psql -U taskuser -d taskdb -c "SELECT count(*) FROM pg_stat_activity;"

# 3. Restart database if needed
docker-compose restart db

# 4. Check backend connectivity
docker-compose exec backend ping -c 3 db

# 5. Restart backend if needed
docker-compose restart backend

# 6. Verify recovery
curl http://localhost:5000/api/health
```

### Incident Communication Template

```markdown
## Incident Report

**Incident ID**: INC-$(date +%Y%m%d-%H%M)  
**Severity**: P0/P1/P2/P3  
**Status**: Investigating/Identified/Monitoring/Resolved  

### Impact
- Services affected: [backend/frontend/database]
- Users impacted: [estimated number/percentage]
- Duration: [start time - current/end time]

### Timeline
- HH:MM - Incident detected
- HH:MM - Investigation started
- HH:MM - Root cause identified
- HH:MM - Fix applied
- HH:MM - Monitoring
- HH:MM - Resolved

### Root Cause
[Brief description]

### Resolution
[Steps taken to resolve]

### Prevention
[Changes to prevent recurrence]

### Action Items
- [ ] Update monitoring
- [ ] Update runbook
- [ ] Team training
```

---

## Maintenance Windows

### Weekly Maintenance

**Time**: Sunday 2:00 AM - 4:00 AM  
**Duration**: 2 hours  
**Frequency**: Weekly

```bash
#!/bin/bash
# weekly-maintenance.sh

echo "=== Weekly Maintenance - $(date) ==="

# 1. Update system packages
echo "1. Updating system packages..."
sudo apt update && sudo apt upgrade -y

# 2. Docker cleanup
echo "2. Docker cleanup..."
docker image prune -f
docker container prune -f
docker volume prune -f

# 3. Database maintenance
echo "3. Database maintenance..."
docker-compose exec db psql -U taskuser -d taskdb -c "VACUUM ANALYZE;"
docker-compose exec db psql -U taskuser -d taskdb -c "REINDEX DATABASE taskdb;"

# 4. Check logs for issues
echo "4. Reviewing logs..."
docker-compose logs --since 7d | grep -i -E "(error|exception)" > weekly-errors.log

# 5. Update Docker images
echo "5. Pulling latest images..."
docker-compose -f docker-compose.hub.yml pull

# 6. Restart services (if updates available)
echo "6. Restarting services..."
docker-compose -f docker-compose.hub.yml up -d

# 7. Verify health
sleep 30
docker-compose ps
curl http://localhost:5000/api/health
curl http://localhost:3000/api/health

echo "=== Maintenance Complete ==="
```

### Monthly Maintenance

**Time**: First Sunday of month, 2:00 AM - 6:00 AM  
**Duration**: 4 hours

```bash
# Additional monthly tasks
- Security updates review
- Certificate renewal check
- Capacity planning review
- Backup restoration test
- Disaster recovery drill
- Documentation updates
```

---

## Scaling Procedures

### Vertical Scaling (Increase Resources)

```yaml
# docker-compose.prod.yml
services:
  backend:
    deploy:
      resources:
        limits:
          cpus: '2.0'      # Increase from 1.0
          memory: 1024M    # Increase from 512M
        reservations:
          cpus: '0.5'
          memory: 512M
```

```bash
# Apply changes
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d
```

### Horizontal Scaling (Add Instances)

```bash
# Scale backend to 3 instances
docker-compose up -d --scale backend=3

# Add load balancer (Nginx)
# See DEPLOYMENT.md for Nginx configuration
```

### Auto-Scaling (Cloud Platforms)

```bash
# AWS ECS
# Set auto-scaling based on CPU/memory metrics

# Kubernetes
# Use HorizontalPodAutoscaler (HPA)
```

---

## Security Operations

### Weekly Security Check

```bash
#!/bin/bash
# weekly-security-check.sh

# 1. Scan images for vulnerabilities
docker run --rm -v /var/run/docker.sock:/var/run/docker.sock \
  aquasec/trivy image veekay8/task-management-backend:latest

# 2. Check for updates
docker-compose pull --dry-run

# 3. Review access logs
docker-compose logs nginx --since 7d | grep -E "(401|403|404)"

# 4. Check failed login attempts
docker-compose logs backend --since 7d | grep -i "failed.*login"

# 5. Verify secrets rotation
echo "Last .env update:" $(stat -c %y .env 2>/dev/null || stat -f %Sm .env)
```

### Security Incident Response

```bash
# 1. Isolate affected service
docker-compose stop backend

# 2. Capture evidence
docker-compose logs backend > incident-logs-$(date +%Y%m%d).txt
docker exec taskmanagement_backend tar czf /tmp/app-state.tar.gz /app

# 3. Investigate
docker exec taskmanagement_backend sh -c "find /app -type f -mtime -1"

# 4. Rotate credentials
# Update .env with new secrets
# Restart services

# 5. Document incident
# Create incident report
```

---

## Troubleshooting Playbooks

### Playbook 1: High CPU Usage

**Trigger**: CPU > 80% for 5 minutes

```bash
# 1. Identify culprit
docker stats --no-stream | sort -k3 -h

# 2. Check processes
docker-compose exec backend top

# 3. Check for loops/deadlocks
docker-compose logs backend --tail=200 | grep -i "loop\|deadlock"

# 4. Temporary fix: Restart
docker-compose restart backend

# 5. Permanent fix: Scale or optimize code
docker-compose up -d --scale backend=2
```

### Playbook 2: High Memory Usage

**Trigger**: Memory > 85%

```bash
# 1. Check memory usage
docker stats --no-stream --format "table {{.Container}}\t{{.MemUsage}}\t{{.MemPerc}}"

# 2. Check for memory leaks
docker-compose exec backend ps aux --sort=-rss

# 3. Restart leaking service
docker-compose restart backend

# 4. Apply memory limits
# Edit docker-compose.prod.yml
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d
```

### Playbook 3: Slow Database Queries

**Trigger**: API latency > 500ms

```bash
# 1. Identify slow queries
docker-compose exec db psql -U taskuser -d taskdb -c "
  SELECT query, calls, mean_time, total_time 
  FROM pg_stat_statements 
  ORDER BY mean_time DESC 
  LIMIT 10;"

# 2. Check database connections
docker-compose exec db psql -U taskuser -d taskdb -c "
  SELECT count(*) FROM pg_stat_activity;"

# 3. Kill long-running queries (if needed)
docker-compose exec db psql -U taskuser -d taskdb -c "
  SELECT pg_terminate_backend(pid) 
  FROM pg_stat_activity 
  WHERE state = 'active' AND query_start < NOW() - INTERVAL '5 minutes';"

# 4. Vacuum and analyze
docker-compose exec db psql -U taskuser -d taskdb -c "VACUUM ANALYZE;"

# 5. Add indexes (if needed)
# Analyze query plan first
```

---

## Emergency Contacts

### On-Call Rotation

| Role | Primary | Backup | Phone | Slack |
|------|---------|--------|-------|-------|
| DevOps Lead | John Doe | Jane Smith | +1-555-0101 | @johndoe |
| Backend Lead | Alice Johnson | Bob Brown | +1-555-0102 | @alice |
| Database Admin | Charlie Davis | Diana Evans | +1-555-0103 | @charlie |
| Security | Eve Foster | Frank Green | +1-555-0104 | @eve |

### Escalation Path

1. **L1**: On-call engineer (15 min response)
2. **L2**: Team lead (30 min response)
3. **L3**: Engineering manager (1 hour response)
4. **L4**: CTO (as needed)

### Communication Channels

- **Incidents**: #incidents (Slack)
- **Deployments**: #deployments (Slack)
- **Monitoring**: #alerts (Slack)
- **Email**: ops@example.com
- **PagerDuty**: https://yourcompany.pagerduty.com

---

## Appendix

### Useful Scripts Location

```
/opt/scripts/
├── backup-database.sh
├── daily-health-check.sh
├── deploy-production.sh
├── emergency-hotfix.sh
├── restore-database.sh
├── rollback-deployment.sh
├── weekly-maintenance.sh
└── weekly-security-check.sh
```

### Configuration Files

```
/opt/config/
├── .env.production
├── docker-compose.hub.yml
├── docker-compose.prod.yml
├── nginx.conf
└── prometheus.yml
```

### Log Locations

```
/var/log/
├── incidents.log
├── deployments.log
├── maintenance.log
└── security.log
```

---

**Document Version**: 1.0.0  
**Last Reviewed**: January 2, 2026  
**Next Review**: April 2, 2026 (quarterly)  
**Owner**: DevOps Team

---

*This runbook is a living document. Update after each incident or deployment.*
