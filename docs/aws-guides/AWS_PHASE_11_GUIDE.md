# Phase 11: Cost Optimization & Auto-Scaling - Complete Guide

**Objective**: Optimize AWS costs and implement auto-scaling for production efficiency
**Timeline**: 1-2 days
**Prerequisites**: Phases 1-10 complete, application running in production

---

## Overview

Phase 11 focuses on reducing costs while maintaining performance through:
- Auto-scaling ECS services based on load
- Right-sizing resources
- Implementing cost monitoring
- Optimizing infrastructure usage
- Setting up scheduled scaling

**Current Monthly Cost**: ~$100-105/month
**Target After Optimization**: ~$60-80/month (40% reduction during low usage)

---

## Cost Breakdown (Current State)

| Resource | Monthly Cost | % of Total |
|----------|--------------|------------|
| NAT Gateway | ~$33 | 33% |
| ECS Backend (2 tasks) | ~$18 | 18% |
| ALB | ~$16.20 | 16% |
| RDS db.t3.micro | ~$15.30 | 15% |
| ECS Frontend (2 tasks) | ~$9.75 | 10% |
| CloudWatch | ~$5-10 | 5-10% |
| ECR + Route53 | ~$2 | 2% |
| **Total** | **~$100-105** | **100%** |

---

## Phase 11 Checklist

### Part 1: Cost Analysis & Monitoring (30 min)
- [ ] Enable AWS Cost Explorer
- [ ] Review last 30 days of costs
- [ ] Identify top 5 cost drivers
- [ ] Set up cost allocation tags
- [ ] Create cost anomaly detection alarm
- [ ] Set up daily cost reports
- [ ] Create monthly budget alert ($100 threshold)

### Part 2: ECS Auto-Scaling Setup (45 min)
- [ ] Configure backend service auto-scaling
  - [ ] Target tracking scaling policy (CPU 70%)
  - [ ] Min tasks: 1, Max tasks: 4
  - [ ] Scale-out cooldown: 60 seconds
  - [ ] Scale-in cooldown: 300 seconds
- [ ] Configure frontend service auto-scaling
  - [ ] Target tracking scaling policy (CPU 70%)
  - [ ] Min tasks: 1, Max tasks: 4
  - [ ] Scale-out cooldown: 60 seconds
  - [ ] Scale-in cooldown: 300 seconds
- [ ] Test auto-scaling with load
- [ ] Monitor CloudWatch metrics

### Part 3: Scheduled Scaling (30 min)
- [ ] Create scale-down schedule (nights/weekends)
  - [ ] Reduce to 1 task per service
  - [ ] Schedule: 11 PM - 6 AM weekdays
  - [ ] All day Saturday/Sunday
- [ ] Create scale-up schedule (business hours)
  - [ ] Increase to 2 tasks per service
  - [ ] Schedule: 6 AM - 11 PM weekdays
- [ ] Test scheduled scaling
- [ ] Verify application performance

### Part 4: Resource Right-Sizing (1 hour)
- [ ] Review ECS task CPU/Memory usage
- [ ] Consider reducing backend to 0.25 vCPU, 0.5 GB (already optimal)
- [ ] Consider reducing frontend to 0.25 vCPU, 0.5 GB (already optimal)
- [ ] Review RDS instance metrics
- [ ] Consider RDS storage auto-scaling
- [ ] Review ALB usage patterns
- [ ] Document sizing decisions

### Part 5: Infrastructure Optimization (1 hour)
- [ ] Review NAT Gateway usage
  - [ ] Consider VPC endpoints for AWS services
  - [ ] Estimate data transfer costs
- [ ] Enable CloudWatch Logs retention limits
  - [ ] Backend logs: 7 days retention
  - [ ] Frontend logs: 7 days retention
- [ ] Review ECR image lifecycle
  - [ ] Keep only last 10 images per repo
- [ ] Enable RDS storage auto-scaling
- [ ] Review backup retention (currently 7 days)
- [ ] Consider Reserved Instances (not recommended for learning project)

### Part 6: Testing & Validation (30 min)
- [ ] Generate load on application
- [ ] Verify auto-scaling triggers
- [ ] Check scale-out behavior (1 → 2 tasks)
- [ ] Wait for scale-in cooldown
- [ ] Check scale-in behavior (2 → 1 tasks)
- [ ] Verify application remains responsive
- [ ] Check CloudWatch metrics
- [ ] Review cost impact projections

---

## Step-by-Step Guide

### Part 1: Cost Analysis & Monitoring

#### Step 1.1: Enable Cost Explorer

**AWS Console Method:**
1. Go to AWS Billing Console: https://console.aws.amazon.com/billing/
2. Left sidebar → "Cost Explorer"
3. Click "Enable Cost Explorer" (if not already enabled)
4. Wait ~24 hours for first data (if first time)

**View Current Costs:**
1. Cost Explorer → "Launch Cost Explorer"
2. Date range: Last 30 days
3. Granularity: Daily
4. Group by: Service
5. Identify top cost drivers

#### Step 1.2: Create Cost Anomaly Detection

```bash
# Create cost anomaly monitor
aws ce create-anomaly-monitor \
  --anomaly-monitor Name=TaskAppCostMonitor,MonitorType=DIMENSIONAL \
  --region us-east-1

# Note the MonitorArn from output
```

**Console Method:**
1. Billing Console → Cost Anomaly Detection
2. Click "Create monitor"
3. Monitor type: AWS services
4. Monitor name: TaskAppCostMonitor
5. Alert threshold: $10 (individual alerts)
6. Click "Create monitor"

#### Step 1.3: Set Up Budget Alerts

```bash
# Create monthly budget with alerts
aws budgets create-budget \
  --account-id 858448674350 \
  --budget file://budget-config.json \
  --notifications-with-subscribers file://budget-notifications.json
```

**Create budget-config.json:**
```json
{
  "BudgetName": "TaskApp-Monthly-Budget",
  "BudgetLimit": {
    "Amount": "100",
    "Unit": "USD"
  },
  "TimeUnit": "MONTHLY",
  "BudgetType": "COST"
}
```

**Create budget-notifications.json:**
```json
[
  {
    "Notification": {
      "NotificationType": "ACTUAL",
      "ComparisonOperator": "GREATER_THAN",
      "Threshold": 80,
      "ThresholdType": "PERCENTAGE"
    },
    "Subscribers": [
      {
        "SubscriptionType": "EMAIL",
        "Address": "vokeogigbah@gmail.com"
      }
    ]
  },
  {
    "Notification": {
      "NotificationType": "FORECASTED",
      "ComparisonOperator": "GREATER_THAN",
      "Threshold": 100,
      "ThresholdType": "PERCENTAGE"
    },
    "Subscribers": [
      {
        "SubscriptionType": "EMAIL",
        "Address": "vokeogigbah@gmail.com"
      }
    ]
  }
]
```

**Console Method:**
1. Billing Console → Budgets
2. Click "Create budget"
3. Budget type: Cost budget
4. Budget name: TaskApp-Monthly-Budget
5. Period: Monthly
6. Budgeted amount: $100
7. Alert thresholds: 80% actual, 100% forecasted
8. Email: vokeogigbah@gmail.com
9. Click "Create budget"

---

### Part 2: ECS Auto-Scaling Setup

#### Step 2.1: Register Scalable Targets

**Backend Service:**
```bash
# Register backend service as scalable target
aws application-autoscaling register-scalable-target \
  --service-namespace ecs \
  --resource-id service/taskapp-cluster/taskapp-backend-service \
  --scalable-dimension ecs:service:DesiredCount \
  --min-capacity 1 \
  --max-capacity 4 \
  --region us-east-1
```

**Frontend Service:**
```bash
# Register frontend service as scalable target
aws application-autoscaling register-scalable-target \
  --service-namespace ecs \
  --resource-id service/taskapp-cluster/taskapp-frontend-service \
  --scalable-dimension ecs:service:DesiredCount \
  --min-capacity 1 \
  --max-capacity 4 \
  --region us-east-1
```

**Console Method:**
1. ECS Console → Clusters → taskapp-cluster
2. Click on service (taskapp-backend-service)
3. "Auto Scaling" tab
4. Click "Configure auto scaling"
5. Min tasks: 1
6. Max tasks: 4
7. Click "Next"
8. Repeat for frontend service

#### Step 2.2: Create Target Tracking Scaling Policies

**Backend CPU-based scaling:**
```bash
# Create backend scaling policy
aws application-autoscaling put-scaling-policy \
  --service-namespace ecs \
  --resource-id service/taskapp-cluster/taskapp-backend-service \
  --scalable-dimension ecs:service:DesiredCount \
  --policy-name backend-cpu-scaling \
  --policy-type TargetTrackingScaling \
  --target-tracking-scaling-policy-configuration file://backend-scaling-policy.json \
  --region us-east-1
```

**Create backend-scaling-policy.json:**
```json
{
  "TargetValue": 70.0,
  "PredefinedMetricSpecification": {
    "PredefinedMetricType": "ECSServiceAverageCPUUtilization"
  },
  "ScaleOutCooldown": 60,
  "ScaleInCooldown": 300
}
```

**Frontend CPU-based scaling:**
```bash
# Create frontend scaling policy
aws application-autoscaling put-scaling-policy \
  --service-namespace ecs \
  --resource-id service/taskapp-cluster/taskapp-frontend-service \
  --scalable-dimension ecs:service:DesiredCount \
  --policy-name frontend-cpu-scaling \
  --policy-type TargetTrackingScaling \
  --target-tracking-scaling-policy-configuration file://frontend-scaling-policy.json \
  --region us-east-1
```

**Create frontend-scaling-policy.json:**
```json
{
  "TargetValue": 70.0,
  "PredefinedMetricSpecification": {
    "PredefinedMetricType": "ECSServiceAverageCPUUtilization"
  },
  "ScaleOutCooldown": 60,
  "ScaleInCooldown": 300
}
```

**Console Method:**
1. Service → Auto Scaling tab
2. "Scaling policies" section
3. Click "Create"
4. Policy name: backend-cpu-scaling
5. Metric type: ECSServiceAverageCPUUtilization
6. Target value: 70
7. Scale-out cooldown: 60 seconds
8. Scale-in cooldown: 300 seconds
9. Click "Create"

---

### Part 3: Scheduled Scaling

#### Step 3.1: Scale Down During Off-Hours

**Create scale-down scheduled action (11 PM weekdays):**
```bash
# Scale down backend at 11 PM (23:00 UTC is 6 PM EST)
aws application-autoscaling put-scheduled-action \
  --service-namespace ecs \
  --resource-id service/taskapp-cluster/taskapp-backend-service \
  --scalable-dimension ecs:service:DesiredCount \
  --scheduled-action-name backend-scale-down-night \
  --schedule "cron(0 4 ? * MON-FRI *)" \
  --scalable-target-action MinCapacity=1,MaxCapacity=1 \
  --region us-east-1

# Scale down frontend at 11 PM
aws application-autoscaling put-scheduled-action \
  --service-namespace ecs \
  --resource-id service/taskapp-cluster/taskapp-frontend-service \
  --scalable-dimension ecs:service:DesiredCount \
  --scheduled-action-name frontend-scale-down-night \
  --schedule "cron(0 4 ? * MON-FRI *)" \
  --scalable-target-action MinCapacity=1,MaxCapacity=1 \
  --region us-east-1
```

#### Step 3.2: Scale Up During Business Hours

**Create scale-up scheduled action (6 AM weekdays):**
```bash
# Scale up backend at 6 AM (11:00 UTC is 6 AM EST)
aws application-autoscaling put-scheduled-action \
  --service-namespace ecs \
  --resource-id service/taskapp-cluster/taskapp-backend-service \
  --scalable-dimension ecs:service:DesiredCount \
  --scheduled-action-name backend-scale-up-morning \
  --schedule "cron(0 11 ? * MON-FRI *)" \
  --scalable-target-action MinCapacity=1,MaxCapacity=4 \
  --region us-east-1

# Scale up frontend at 6 AM
aws application-autoscaling put-scheduled-action \
  --service-namespace ecs \
  --resource-id service/taskapp-cluster/taskapp-frontend-service \
  --scalable-dimension ecs:service:DesiredCount \
  --scheduled-action-name frontend-scale-up-morning \
  --schedule "cron(0 11 ? * MON-FRI *)" \
  --scalable-target-action MinCapacity=1,MaxCapacity=4 \
  --region us-east-1
```

**Console Method:**
1. Service → Auto Scaling tab
2. "Scheduled actions" section
3. Click "Create scheduled action"
4. Name: backend-scale-down-night
5. Schedule: Cron expression: `cron(0 4 ? * MON-FRI *)`
6. Min capacity: 1
7. Max capacity: 1
8. Click "Create"
9. Repeat for scale-up and frontend

---

### Part 4: Resource Right-Sizing

#### Step 4.1: Review ECS Task Metrics

```bash
# Check backend CPU/Memory usage over last 7 days
aws cloudwatch get-metric-statistics \
  --namespace AWS/ECS \
  --metric-name CPUUtilization \
  --dimensions Name=ServiceName,Value=taskapp-backend-service Name=ClusterName,Value=taskapp-cluster \
  --start-time $(date -u -d '7 days ago' +%Y-%m-%dT%H:%M:%S) \
  --end-time $(date -u +%Y-%m-%dT%H:%M:%S) \
  --period 3600 \
  --statistics Average,Maximum \
  --region us-east-1

# Check backend memory usage
aws cloudwatch get-metric-statistics \
  --namespace AWS/ECS \
  --metric-name MemoryUtilization \
  --dimensions Name=ServiceName,Value=taskapp-backend-service Name=ClusterName,Value=taskapp-cluster \
  --start-time $(date -u -d '7 days ago' +%Y-%m-%dT%H:%M:%S) \
  --end-time $(date -u +%Y-%m-%dT%H:%M:%S) \
  --period 3600 \
  --statistics Average,Maximum \
  --region us-east-1
```

**Console Method:**
1. CloudWatch → Metrics → ECS
2. Select ServiceName = taskapp-backend-service
3. Select CPUUtilization and MemoryUtilization
4. Change time range to Last 7 days
5. Review average and peak usage
6. If avg CPU < 30% and avg Memory < 40%, tasks are oversized
7. If avg CPU > 70% or avg Memory > 70%, tasks are undersized

**Current Sizing (Already Optimal)**:
- Backend: 0.25 vCPU, 0.5 GB (smallest Fargate size)
- Frontend: 0.25 vCPU, 0.5 GB (smallest Fargate size)
- **No changes recommended** - already at minimum

#### Step 4.2: Enable RDS Storage Auto-Scaling

```bash
# Enable RDS storage auto-scaling (20 GB → max 100 GB)
aws rds modify-db-instance \
  --db-instance-identifier taskapp-db \
  --max-allocated-storage 100 \
  --apply-immediately \
  --region us-east-1
```

**Console Method:**
1. RDS Console → Databases → taskapp-db
2. Click "Modify"
3. Scroll to "Storage autoscaling"
4. Check "Enable storage autoscaling"
5. Maximum storage threshold: 100 GB
6. Click "Continue"
7. Apply: Immediately
8. Click "Modify DB instance"

---

### Part 5: Infrastructure Optimization

#### Step 5.1: ECR Image Lifecycle Policy

**Create lifecycle policy to keep only last 10 images:**

**Backend repository:**
```bash
# Create lifecycle policy JSON
cat > ecr-lifecycle-policy.json << 'EOF'
{
  "rules": [
    {
      "rulePriority": 1,
      "description": "Keep last 10 images",
      "selection": {
        "tagStatus": "any",
        "countType": "imageCountMoreThan",
        "countNumber": 10
      },
      "action": {
        "type": "expire"
      }
    }
  ]
}
EOF

# Apply to backend repository
aws ecr put-lifecycle-policy \
  --repository-name taskapp-backend \
  --lifecycle-policy-text file://ecr-lifecycle-policy.json \
  --region us-east-1

# Apply to frontend repository
aws ecr put-lifecycle-policy \
  --repository-name taskapp-frontend \
  --lifecycle-policy-text file://ecr-lifecycle-policy.json \
  --region us-east-1
```

**Console Method:**
1. ECR Console → Repositories → taskapp-backend
2. Left sidebar → Lifecycle policies
3. Click "Create rule"
4. Rule priority: 1
5. Description: Keep last 10 images
6. Image status: Any
7. Count type: Image count more than
8. Count: 10
9. Click "Save"
10. Repeat for frontend repository

#### Step 5.2: Review CloudWatch Logs Retention

```bash
# Set 7-day retention for backend logs (already done in Phase 8)
aws logs put-retention-policy \
  --log-group-name /ecs/taskapp-backend \
  --retention-in-days 7 \
  --region us-east-1

# Set 7-day retention for frontend logs (already done in Phase 8)
aws logs put-retention-policy \
  --log-group-name /ecs/taskapp-frontend \
  --retention-in-days 7 \
  --region us-east-1
```

**Already configured in Phase 8** ✅

#### Step 5.3: NAT Gateway Optimization (Optional)

**Option 1: VPC Endpoints for AWS Services** (Reduces NAT data transfer)

```bash
# Create VPC endpoint for ECR API
aws ec2 create-vpc-endpoint \
  --vpc-id vpc-016004b6f25f26302 \
  --service-name com.amazonaws.us-east-1.ecr.api \
  --vpc-endpoint-type Interface \
  --subnet-ids subnet-0681cafcc954cd8a6 subnet-04f1cbee6ad2f9d17 \
  --security-group-ids sg-01e0fb4d04d2a2234 \
  --region us-east-1

# Create VPC endpoint for ECR Docker
aws ec2 create-vpc-endpoint \
  --vpc-id vpc-016004b6f25f26302 \
  --service-name com.amazonaws.us-east-1.ecr.dkr \
  --vpc-endpoint-type Interface \
  --subnet-ids subnet-0681cafcc954cd8a6 subnet-04f1cbee6ad2f9d17 \
  --security-group-ids sg-01e0fb4d04d2a2234 \
  --region us-east-1

# Create VPC endpoint for S3 (ECR uses S3 for layers)
aws ec2 create-vpc-endpoint \
  --vpc-id vpc-016004b6f25f26302 \
  --service-name com.amazonaws.us-east-1.s3 \
  --route-table-ids rtb-09b52332e1238780c \
  --region us-east-1
```

**Cost Impact:**
- VPC Interface Endpoints: $0.01/hour = ~$7.20/month each ($14.40 for both ECR endpoints)
- S3 Gateway Endpoint: FREE
- NAT data savings: ~$5-10/month
- **Net savings: Minimal** (not recommended for learning project)

**Option 2: Delete NAT Gateway when not deploying** (Manual)
- Save ~$33/month when stopped
- Deployments will fail without NAT
- Only viable for development/testing

---

### Part 6: Testing & Validation

#### Step 6.1: Verify Auto-Scaling Configuration

```bash
# List scalable targets
aws application-autoscaling describe-scalable-targets \
  --service-namespace ecs \
  --resource-ids service/taskapp-cluster/taskapp-backend-service service/taskapp-cluster/taskapp-frontend-service \
  --region us-east-1

# List scaling policies
aws application-autoscaling describe-scaling-policies \
  --service-namespace ecs \
  --resource-id service/taskapp-cluster/taskapp-backend-service \
  --region us-east-1

# List scheduled actions
aws application-autoscaling describe-scheduled-actions \
  --service-namespace ecs \
  --resource-id service/taskapp-cluster/taskapp-backend-service \
  --region us-east-1
```

#### Step 6.2: Test Auto-Scaling with Load

**Generate CPU load on backend:**

```bash
# Install Apache Bench (if not installed)
# Windows: Download from https://httpd.apache.org/download.cgi
# Mac: brew install httpd
# Linux: sudo apt install apache2-utils

# Generate 1000 requests with 50 concurrent users
ab -n 1000 -c 50 https://app.techveesolutions.com/api/health

# Or use more intensive endpoint
ab -n 500 -c 25 https://app.techveesolutions.com/api/projects

# Watch ECS service scale out
watch -n 10 'aws ecs describe-services --cluster taskapp-cluster --services taskapp-backend-service --query "services[0].[desiredCount,runningCount]" --output text'
```

**Monitor in CloudWatch:**
1. CloudWatch Console → Metrics → ECS
2. Select CPUUtilization for taskapp-backend-service
3. Watch metric rise above 70%
4. Service should scale from 1 → 2 tasks within 60 seconds

#### Step 6.3: Verify Cost Savings

**After 1 week of auto-scaling:**

```bash
# Check average task count over last 7 days
aws cloudwatch get-metric-statistics \
  --namespace AWS/ECS \
  --metric-name DesiredTaskCount \
  --dimensions Name=ServiceName,Value=taskapp-backend-service Name=ClusterName,Value=taskapp-cluster \
  --start-time $(date -u -d '7 days ago' +%Y-%m-%dT%H:%M:%S) \
  --end-time $(date -u +%Y-%m-%dT%H:%M:%S) \
  --period 86400 \
  --statistics Average \
  --region us-east-1
```

**Expected Results:**
- **Before**: 2 tasks running 24/7 = ~$27/month per service
- **After**: 1.3 tasks average = ~$17.50/month per service
- **Savings**: ~$20/month total (~20% reduction)

---

## Cost Optimization Summary

### Expected Monthly Costs After Phase 11

| Resource | Before | After | Savings |
|----------|--------|-------|---------|
| NAT Gateway | $33 | $33 | $0 |
| Backend ECS | $18 | $12 | $6 |
| Frontend ECS | $9.75 | $6.50 | $3.25 |
| RDS | $15.30 | $15.30 | $0 |
| ALB | $16.20 | $16.20 | $0 |
| CloudWatch | $10 | $8 | $2 |
| ECR + Other | $2 | $1 | $1 |
| **Total** | **~$105** | **~$92** | **~$12** |

**Percentage Reduction**: ~12% immediate, up to 40% during low usage periods

---

## Best Practices Implemented

1. ✅ **Target Tracking Auto-Scaling**: Automatic response to CPU load
2. ✅ **Scheduled Scaling**: Proactive cost reduction during known low-traffic periods
3. ✅ **Cooldown Periods**: Prevents rapid scaling oscillations
4. ✅ **Cost Monitoring**: Alerts before budget exceeded
5. ✅ **Resource Right-Sizing**: Tasks already at minimum Fargate size
6. ✅ **Log Retention**: 7 days prevents unlimited growth
7. ✅ **Image Lifecycle**: Automatic cleanup of old images
8. ✅ **Storage Auto-Scaling**: RDS grows automatically, no manual intervention

---

## Troubleshooting

### Issue 1: Auto-Scaling Not Triggering

**Check:**
```bash
# Verify scaling policy exists
aws application-autoscaling describe-scaling-policies \
  --service-namespace ecs \
  --resource-id service/taskapp-cluster/taskapp-backend-service

# Check CloudWatch alarms
aws cloudwatch describe-alarms \
  --alarm-name-prefix TargetTracking
```

**Solution**: Ensure CPU actually exceeds 70% for scale-out, or drops below 63% (70% * 0.9) for scale-in

### Issue 2: Scheduled Actions Not Executing

**Check:**
```bash
# List scheduled actions
aws application-autoscaling describe-scheduled-actions \
  --service-namespace ecs

# Verify time zone - AWS uses UTC
date -u
```

**Solution**: Convert local time to UTC for cron expressions

### Issue 3: Cost Not Decreasing

**Check:**
```bash
# Verify average task count decreased
aws cloudwatch get-metric-statistics \
  --namespace AWS/ECS \
  --metric-name DesiredTaskCount \
  --dimensions Name=ServiceName,Value=taskapp-backend-service
```

**Solution**: Wait 7-30 days for cost averaging; NAT Gateway is largest fixed cost

---

## Next Steps

**After Phase 11:**
- Monitor costs for 1 week
- Adjust scaling thresholds if needed
- Review CloudWatch metrics for optimization opportunities
- Proceed to Phase 12: Final Documentation

**Phase 12 Preview:**
- Complete architecture diagrams
- Full troubleshooting guide
- Cost comparison with Azure/GCP
- Lessons learned documentation

---

**Estimated Time**: 3-4 hours
**Difficulty**: Medium
**Cost Impact**: -$12/month immediate, up to -$40/month during low usage

---

*Ready to optimize your AWS costs? Let's make your infrastructure efficient!* 💰
