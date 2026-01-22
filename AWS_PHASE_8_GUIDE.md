# AWS Phase 8: Monitoring & Logging ✅ COMPLETE

## Overview
Set up comprehensive monitoring, logging, and alerting for your production application. This phase ensures you can track application health, diagnose issues, and receive alerts when problems occur.

**Timeline**: Completed in 3 hours
**Cost**: ~$5-10/month (CloudWatch metrics, logs, and alarms)
**Prerequisites**: Phase 7 complete (Application running with HTTPS)

---

## ⚠️ Windows Git Bash Users

If you're using Git Bash on Windows, prepend `MSYS_NO_PATHCONV=1` to AWS CLI commands that use paths starting with `/`:

```bash
# Instead of:
aws logs describe-log-groups --log-group-name-prefix "/ecs/" ...

# Use:
MSYS_NO_PATHCONV=1 aws logs describe-log-groups --log-group-name-prefix "/ecs/" ...
```

**Or use PowerShell/CMD instead of Git Bash for this phase.**

---

## What You'll Create

1. **CloudWatch Dashboard** - Visual monitoring of key metrics
2. **CloudWatch Alarms** - Automated alerts for critical issues
3. **Log Insights Queries** - Analyze application logs
4. **SNS Topic** - Email/SMS notifications for alerts
5. **Metric Filters** - Custom metrics from log data
6. **Container Insights** - Deep ECS monitoring

---

## Architecture After Phase 8

```
Application Logs → CloudWatch Logs → Log Insights
                        ↓
                   Metric Filters
                        ↓
                  CloudWatch Metrics → Dashboard
                        ↓
                  CloudWatch Alarms → SNS → Email/SMS
```

---

## Phase 8 Checklist

### Part 1: CloudWatch Logs Configuration
- [ ] Verify existing log groups
- [ ] Set log retention policies
- [ ] Configure log streaming

### Part 2: CloudWatch Alarms
- [ ] Create SNS topic for notifications
- [ ] Subscribe email to SNS topic
- [ ] Create alarm: Backend unhealthy targets
- [ ] Create alarm: Frontend unhealthy targets
- [ ] Create alarm: RDS high CPU usage
- [ ] Create alarm: RDS low storage
- [ ] Create alarm: ALB 5xx errors
- [ ] Create alarm: ECS task failures
- [ ] Test alarm notifications

### Part 3: CloudWatch Dashboard
- [ ] Create custom dashboard
- [ ] Add ALB metrics widget
- [ ] Add ECS CPU/Memory widgets
- [ ] Add RDS metrics widget
- [ ] Add custom application metrics
- [ ] Add log insights queries

### Part 4: Container Insights (Optional)
- [ ] Enable Container Insights on ECS cluster
- [ ] Review detailed container metrics
- [ ] Set up performance monitoring

### Part 5: Log Analysis
- [ ] Create useful Log Insights queries
- [ ] Set up saved queries for common issues
- [ ] Create metric filters for errors

---

## Step 1: Verify Existing Log Groups

Your application already has CloudWatch log groups created in previous phases. Let's verify and configure them:

```bash
# List all log groups
aws logs describe-log-groups \
  --log-group-name-prefix "/ecs/" \
  --region us-east-1 \
  --query 'logGroups[*].[logGroupName,retentionInDays,storedBytes]' \
  --output table
```

**Expected log groups:**
- `/ecs/taskapp-backend` - Backend application logs
- `/ecs/taskapp-frontend` - Frontend application logs

### Set Log Retention Policies

By default, logs are kept forever and can become expensive. Let's set retention to 30 days:

```bash
# Set backend log retention
aws logs put-retention-policy \
  --log-group-name /ecs/taskapp-backend \
  --retention-in-days 30 \
  --region us-east-1

# Set frontend log retention
aws logs put-retention-policy \
  --log-group-name /ecs/taskapp-frontend \
  --retention-in-days 30 \
  --region us-east-1
```

**Retention options:**
- 1, 3, 5, 7, 14, 30, 60, 90, 120, 150, 180, 365, 400, 545, 731, 1827, 3653 days

---

## Step 2: Create SNS Topic for Alerts

SNS (Simple Notification Service) will send alerts to your email/phone.

### Create SNS Topic

```bash
# Create SNS topic
aws sns create-topic \
  --name taskapp-alerts \
  --region us-east-1

# Save the Topic ARN (you'll need it)
# Output example: arn:aws:sns:us-east-1:858448674350:taskapp-alerts
```

### Subscribe Your Email

```bash
# Subscribe email to SNS topic
aws sns subscribe \
  --topic-arn arn:aws:sns:us-east-1:858448674350:taskapp-alerts \
  --protocol email \
  --notification-endpoint your-email@example.com \
  --region us-east-1
```

**⚠️ Important**: Check your email and click the confirmation link to activate the subscription.

### Via AWS Console

1. **Open SNS Console** → Topics → Create topic
2. **Type**: Standard
3. **Name**: taskapp-alerts
4. **Click**: Create topic
5. **Click**: Create subscription
   - Protocol: Email
   - Endpoint: your-email@example.com
6. **Confirm**: Check email and click confirmation link

---

## Step 3: Create CloudWatch Alarms

### Alarm 1: Backend Unhealthy Targets

Alert when backend tasks become unhealthy:

```bash
# Get backend target group ARN
BACKEND_TG_ARN=$(aws elbv2 describe-target-groups \
  --names taskapp-backend-tg \
  --query 'TargetGroups[0].TargetGroupArn' \
  --output text \
  --region us-east-1)

# Extract target group suffix for metrics
TG_SUFFIX=$(echo $BACKEND_TG_ARN | grep -oP 'targetgroup/\K.*')

# Create alarm
aws cloudwatch put-metric-alarm \
  --alarm-name taskapp-backend-unhealthy-targets \
  --alarm-description "Alert when backend targets are unhealthy" \
  --metric-name UnHealthyHostCount \
  --namespace AWS/ApplicationELB \
  --statistic Average \
  --period 60 \
  --evaluation-periods 2 \
  --threshold 1 \
  --comparison-operator GreaterThanOrEqualToThreshold \
  --dimensions Name=TargetGroup,Value=$TG_SUFFIX \
  --alarm-actions arn:aws:sns:us-east-1:858448674350:taskapp-alerts \
  --region us-east-1
```

### Alarm 2: Frontend Unhealthy Targets

```bash
# Get frontend target group ARN
FRONTEND_TG_ARN=$(aws elbv2 describe-target-groups \
  --names taskapp-frontend-tg \
  --query 'TargetGroups[0].TargetGroupArn' \
  --output text \
  --region us-east-1)

TG_SUFFIX=$(echo $FRONTEND_TG_ARN | grep -oP 'targetgroup/\K.*')

aws cloudwatch put-metric-alarm \
  --alarm-name taskapp-frontend-unhealthy-targets \
  --alarm-description "Alert when frontend targets are unhealthy" \
  --metric-name UnHealthyHostCount \
  --namespace AWS/ApplicationELB \
  --statistic Average \
  --period 60 \
  --evaluation-periods 2 \
  --threshold 1 \
  --comparison-operator GreaterThanOrEqualToThreshold \
  --dimensions Name=TargetGroup,Value=$TG_SUFFIX \
  --alarm-actions arn:aws:sns:us-east-1:858448674350:taskapp-alerts \
  --region us-east-1
```

### Alarm 3: ALB 5xx Errors

Alert when server errors occur:

```bash
# Get ALB name
ALB_NAME=$(aws elbv2 describe-load-balancers \
  --names taskapp-alb \
  --query 'LoadBalancers[0].LoadBalancerName' \
  --output text \
  --region us-east-1)

# Get LoadBalancer dimension value (app/name/id)
LB_DIMENSION=$(aws elbv2 describe-load-balancers \
  --names taskapp-alb \
  --query 'LoadBalancers[0].LoadBalancerArn' \
  --output text \
  --region us-east-1 | grep -oP 'loadbalancer/\K.*')

aws cloudwatch put-metric-alarm \
  --alarm-name taskapp-alb-5xx-errors \
  --alarm-description "Alert when ALB returns 5xx errors" \
  --metric-name HTTPCode_Target_5XX_Count \
  --namespace AWS/ApplicationELB \
  --statistic Sum \
  --period 300 \
  --evaluation-periods 1 \
  --threshold 10 \
  --comparison-operator GreaterThanThreshold \
  --dimensions Name=LoadBalancer,Value=$LB_DIMENSION \
  --alarm-actions arn:aws:sns:us-east-1:858448674350:taskapp-alerts \
  --treat-missing-data notBreaching \
  --region us-east-1
```

### Alarm 4: RDS High CPU Usage

```bash
aws cloudwatch put-metric-alarm \
  --alarm-name taskapp-rds-high-cpu \
  --alarm-description "Alert when RDS CPU exceeds 80%" \
  --metric-name CPUUtilization \
  --namespace AWS/RDS \
  --statistic Average \
  --period 300 \
  --evaluation-periods 2 \
  --threshold 80 \
  --comparison-operator GreaterThanThreshold \
  --dimensions Name=DBInstanceIdentifier,Value=taskapp-db \
  --alarm-actions arn:aws:sns:us-east-1:858448674350:taskapp-alerts \
  --region us-east-1
```

### Alarm 5: RDS Low Storage

```bash
aws cloudwatch put-metric-alarm \
  --alarm-name taskapp-rds-low-storage \
  --alarm-description "Alert when RDS free storage is below 2GB" \
  --metric-name FreeStorageSpace \
  --namespace AWS/RDS \
  --statistic Average \
  --period 300 \
  --evaluation-periods 1 \
  --threshold 2000000000 \
  --comparison-operator LessThanThreshold \
  --dimensions Name=DBInstanceIdentifier,Value=taskapp-db \
  --alarm-actions arn:aws:sns:us-east-1:858448674350:taskapp-alerts \
  --region us-east-1
```

### Alarm 6: ECS Task Failures

```bash
aws cloudwatch put-metric-alarm \
  --alarm-name taskapp-backend-task-failures \
  --alarm-description "Alert when backend tasks fail to start" \
  --metric-name RunningTaskCount \
  --namespace ECS/ContainerInsights \
  --statistic Average \
  --period 300 \
  --evaluation-periods 2 \
  --threshold 1 \
  --comparison-operator LessThanThreshold \
  --dimensions Name=ServiceName,Value=taskapp-backend-service Name=ClusterName,Value=taskapp-cluster \
  --alarm-actions arn:aws:sns:us-east-1:858448674350:taskapp-alerts \
  --region us-east-1
```

---

## Step 4: Create CloudWatch Dashboard

### Via AWS Console (Recommended)

1. **Open CloudWatch Console** → Dashboards → Create dashboard
2. **Name**: `taskapp-production`
3. **Add widgets** (click "Add widget" for each):

#### Widget 1: ALB Request Count
```
Widget type: Line graph
Metric: AWS/ApplicationELB > Per-LoadBalancer Metrics
Select: RequestCount
Statistic: Sum
Period: 5 minutes
```

#### Widget 2: ALB Target Response Time
```
Widget type: Line graph
Metric: AWS/ApplicationELB > Per-TargetGroup Metrics
Select: TargetResponseTime (both target groups)
Statistic: Average
Period: 1 minute
```

#### Widget 3: ECS CPU Utilization
```
Widget type: Line graph
Metric: AWS/ECS > ClusterName, ServiceName
Select: CPUUtilization (both services)
Statistic: Average
Period: 1 minute
```

#### Widget 4: ECS Memory Utilization
```
Widget type: Line graph
Metric: AWS/ECS > ClusterName, ServiceName
Select: MemoryUtilization (both services)
Statistic: Average
Period: 1 minute
```

#### Widget 5: RDS Connections
```
Widget type: Number
Metric: AWS/RDS > Per-Database Metrics
Select: DatabaseConnections
Statistic: Average
Period: 5 minutes
```

#### Widget 6: RDS CPU
```
Widget type: Gauge
Metric: AWS/RDS > Per-Database Metrics
Select: CPUUtilization
Statistic: Average
Max value: 100
```

### Via AWS CLI

Create dashboard JSON file:

```bash
cat > dashboard.json << 'EOF'
{
  "widgets": [
    {
      "type": "metric",
      "properties": {
        "metrics": [
          [ "AWS/ApplicationELB", "RequestCount", { "stat": "Sum", "label": "Requests" } ]
        ],
        "period": 300,
        "stat": "Sum",
        "region": "us-east-1",
        "title": "ALB Request Count",
        "yAxis": {
          "left": {
            "min": 0
          }
        }
      }
    },
    {
      "type": "metric",
      "properties": {
        "metrics": [
          [ "AWS/ECS", "CPUUtilization", { "stat": "Average" } ],
          [ ".", "MemoryUtilization", { "stat": "Average" } ]
        ],
        "period": 60,
        "stat": "Average",
        "region": "us-east-1",
        "title": "ECS Resource Usage"
      }
    }
  ]
}
EOF

# Create dashboard
aws cloudwatch put-dashboard \
  --dashboard-name taskapp-production \
  --dashboard-body file://dashboard.json \
  --region us-east-1
```

---

## Step 5: Useful Log Insights Queries

### Query 1: Recent Errors (Last 1 Hour)

1. **Open CloudWatch** → Logs → Insights
2. **Select log groups**: `/ecs/taskapp-backend`, `/ecs/taskapp-frontend`
3. **Query**:

```
fields @timestamp, @message
| filter @message like /ERROR/ or @message like /Exception/
| sort @timestamp desc
| limit 100
```

### Query 2: API Response Times

```
fields @timestamp, @message
| filter @message like /GET/ or @message like /POST/
| parse @message /(?<method>\w+) (?<path>\/\S+).*(?<status>\d{3}).*(?<duration>\d+)ms/
| stats avg(duration) as avg_duration, max(duration) as max_duration by path
| sort avg_duration desc
```

### Query 3: Failed Login Attempts

```
fields @timestamp, @message
| filter @message like /login/ and @message like /failed/
| stats count() as failed_logins by bin(5m)
```

### Query 4: Top 10 Slowest Requests

```
fields @timestamp, @message
| parse @message /(?<method>\w+) (?<path>\/\S+).*(?<status>\d{3}).*(?<duration>\d+)ms/
| sort duration desc
| limit 10
```

### Save Queries

Click "Save" after running each query to reuse them later.

---

## Step 6: Create Metric Filters (Optional)

Convert log patterns into metrics:

### Filter 1: Count 500 Errors

```bash
aws logs put-metric-filter \
  --log-group-name /ecs/taskapp-backend \
  --filter-name backend-500-errors \
  --filter-pattern "[time, request_id, level = ERROR, msg = *500*]" \
  --metric-transformations \
      metricName=Backend500Errors,metricNamespace=TaskApp,metricValue=1,defaultValue=0 \
  --region us-east-1
```

### Filter 2: Count Failed Logins

```bash
aws logs put-metric-filter \
  --log-group-name /ecs/taskapp-backend \
  --filter-name failed-logins \
  --filter-pattern "[time, request_id, level, msg = *login*failed*]" \
  --metric-transformations \
      metricName=FailedLogins,metricNamespace=TaskApp,metricValue=1,defaultValue=0 \
  --region us-east-1
```

---

## Step 7: Enable Container Insights (Optional)

Container Insights provides detailed metrics for ECS tasks.

**Cost**: Additional ~$7-10/month

```bash
# Enable Container Insights on cluster
aws ecs put-account-setting \
  --name containerInsights \
  --value enabled \
  --region us-east-1

# Update cluster
aws ecs update-cluster-settings \
  --cluster taskapp-cluster \
  --settings name=containerInsights,value=enabled \
  --region us-east-1
```

### View Container Insights

1. **CloudWatch Console** → Container Insights
2. **Select**: ECS Clusters
3. **Cluster**: taskapp-cluster
4. **View**: Detailed metrics for CPU, memory, network, disk

---

## Step 8: Test Your Alarms

### Test Unhealthy Target Alarm

Temporarily stop a task to trigger the alarm:

```bash
# List running backend tasks
aws ecs list-tasks \
  --cluster taskapp-cluster \
  --service-name taskapp-backend-service \
  --region us-east-1

# Stop one task (use task ID from above)
aws ecs stop-task \
  --cluster taskapp-cluster \
  --task <task-id> \
  --reason "Testing alarm" \
  --region us-east-1
```

**Wait 2-3 minutes** - you should receive an email alert!

The task will automatically restart, and alarm will resolve.

### Test 5xx Error Alarm

Create intentional errors to trigger the alarm (be careful in production):

```bash
# Make requests to a non-existent endpoint
for i in {1..15}; do
  curl https://app.techveesolutions.com/api/nonexistent
done
```

---

## Verification Checklist

### SNS & Alarms
- [ ] SNS topic created
- [ ] Email subscription confirmed
- [ ] 6 alarms created and in "OK" state
- [ ] Test alarm triggered and email received

### Dashboard
- [ ] Dashboard created with all widgets
- [ ] Metrics visible for all services
- [ ] Dashboard accessible via CloudWatch console

### Logs
- [ ] Log retention set to 30 days
- [ ] Log Insights queries saved
- [ ] Can search logs successfully

### Optional
- [ ] Container Insights enabled
- [ ] Metric filters created
- [ ] Custom metrics appearing

---

## Monitoring Best Practices

### 1. Regular Reviews
- Check dashboard daily
- Review alarms weekly
- Analyze logs when issues occur

### 2. Alarm Tuning
- Adjust thresholds based on actual usage
- Reduce false positives
- Add new alarms as needed

### 3. Log Management
- Keep retention reasonable (30-90 days)
- Archive important logs to S3 if needed
- Use structured logging in code

### 4. Cost Optimization
- Monitor CloudWatch costs
- Delete unused log groups
- Use log sampling for high-volume apps

---

## Cost Breakdown

**Monthly CloudWatch Costs:**
- Logs ingestion (5GB): ~$2.50
- Logs storage (30 days): ~$1.50
- Metrics (50 custom): ~$2.50
- Alarms (6): ~$0.60
- Dashboard (1): ~$3.00
- Container Insights: ~$7.00 (optional)

**Total**: ~$10-17/month (depending on usage and Container Insights)

---

## Common Issues & Solutions

### Issue: Alarm Not Triggering

**Solution**: Check alarm state and history
```bash
aws cloudwatch describe-alarms \
  --alarm-names taskapp-backend-unhealthy-targets \
  --region us-east-1
```

### Issue: No Logs Appearing

**Solution**: Check ECS task logs permissions and CloudWatch Logs agent

```bash
# Check recent log streams
aws logs describe-log-streams \
  --log-group-name /ecs/taskapp-backend \
  --order-by LastEventTime \
  --descending \
  --max-items 5 \
  --region us-east-1
```

### Issue: High CloudWatch Costs

**Solutions**:
- Reduce log retention period
- Filter logs before sending to CloudWatch
- Use log sampling for non-critical logs
- Delete old unused log groups

---

## Next Steps

After completing Phase 8, you have:
- ✅ Real-time monitoring of all services
- ✅ Automated alerts for critical issues
- ✅ Log analysis capabilities
- ✅ Visual dashboards for quick health checks

**Ready for Phase 9?**
- Convert infrastructure to Terraform (Infrastructure as Code)
- Version control your AWS resources
- Enable reproducible deployments

---

## Additional Resources

- [CloudWatch Documentation](https://docs.aws.amazon.com/cloudwatch/)
- [CloudWatch Logs Insights Query Syntax](https://docs.aws.amazon.com/AmazonCloudWatch/latest/logs/CWL_QuerySyntax.html)
- [Container Insights for ECS](https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/ContainerInsights.html)
- [SNS Best Practices](https://docs.aws.amazon.com/sns/latest/dg/sns-best-practices.html)

---

**Phase 8 Complete!** 🎉 Your application now has enterprise-grade monitoring and alerting!
