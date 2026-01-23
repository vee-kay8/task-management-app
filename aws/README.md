# AWS Infrastructure

This directory contains AWS-specific infrastructure files and configurations.

## Directory Structure

### config/
AWS configuration files used during deployment and operations.

**Auto-Scaling Configurations:**
- `backend-scaling-policy.json` - Backend ECS auto-scaling policy (CPU-based, 70% target)
- `frontend-scaling-policy.json` - Frontend ECS auto-scaling policy (CPU-based, 70% target)

**Cost Management:**
- `budget-config.json` - Monthly budget configuration ($100 limit)
- `budget-notifications.json` - Budget alert thresholds (80% actual, 100% forecasted)

**Infrastructure Optimization:**
- `ecr-lifecycle-policy.json` - ECR image lifecycle policy (keep last 10 images)
- `cloudwatch-dashboard.json` - CloudWatch dashboard configuration

**Testing:**
- `test-api.json` - API testing configuration

## Usage

These configuration files are used with AWS CLI commands during deployment and management operations. 

Example:
```bash
# Apply auto-scaling policy
aws application-autoscaling put-scaling-policy \
  --policy-name backend-cpu-scaling \
  --target-tracking-scaling-policy-configuration file://config/backend-scaling-policy.json

# Create budget
aws budgets create-budget \
  --budget file://config/budget-config.json \
  --notifications-with-subscribers file://config/budget-notifications.json
```

## Documentation

For complete deployment instructions, see:
- [AWS Deployment Roadmap](../AWS_DEPLOYMENT_ROADMAP.md)
- [AWS Phase Guides](../docs/aws-guides/)
- [Completion Reports](../docs/completion-reports/)
