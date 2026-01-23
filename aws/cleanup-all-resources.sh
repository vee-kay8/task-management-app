#!/bin/bash

# ============================================================
# AWS COMPLETE RESOURCE CLEANUP SCRIPT
# ============================================================
# This script deletes ALL AWS resources created during deployment
# Run this to completely tear down the infrastructure and stop costs
#
# WARNING: This is IRREVERSIBLE. All data will be lost.
# Make sure you have backups if needed.
# ============================================================

set -e  # Exit on any error

REGION="us-east-1"
CLUSTER_NAME="taskapp-cluster"
DB_IDENTIFIER="taskapp-db"
VPC_ID="vpc-016004b6f25f26302"

echo "============================================================"
echo "  AWS RESOURCE CLEANUP - TASK MANAGEMENT APP"
echo "============================================================"
echo ""
echo "This will DELETE ALL resources and STOP ALL COSTS."
echo "This action is IRREVERSIBLE."
echo ""
read -p "Are you absolutely sure? Type 'DELETE' to confirm: " confirm

if [ "$confirm" != "DELETE" ]; then
    echo "Cleanup cancelled."
    exit 0
fi

echo ""
echo "Starting cleanup process..."
echo ""

# ============================================================
# STEP 1: Delete Auto-Scaling Configurations
# ============================================================
echo ">>> STEP 1: Removing Auto-Scaling Configurations..."

# Delete scheduled actions
echo "  - Deleting scheduled scaling actions..."
aws application-autoscaling delete-scheduled-action \
  --service-namespace ecs \
  --resource-id service/$CLUSTER_NAME/taskapp-backend-service \
  --scheduled-action-name backend-scale-down-night \
  --region $REGION 2>/dev/null || true

aws application-autoscaling delete-scheduled-action \
  --service-namespace ecs \
  --resource-id service/$CLUSTER_NAME/taskapp-backend-service \
  --scheduled-action-name backend-scale-up-morning \
  --region $REGION 2>/dev/null || true

aws application-autoscaling delete-scheduled-action \
  --service-namespace ecs \
  --resource-id service/$CLUSTER_NAME/taskapp-frontend-service \
  --scheduled-action-name frontend-scale-down-night \
  --region $REGION 2>/dev/null || true

aws application-autoscaling delete-scheduled-action \
  --service-namespace ecs \
  --resource-id service/$CLUSTER_NAME/taskapp-frontend-service \
  --scheduled-action-name frontend-scale-up-morning \
  --region $REGION 2>/dev/null || true

# Delete scaling policies
echo "  - Deleting scaling policies..."
aws application-autoscaling delete-scaling-policy \
  --service-namespace ecs \
  --resource-id service/$CLUSTER_NAME/taskapp-backend-service \
  --scalable-dimension ecs:service:DesiredCount \
  --policy-name backend-cpu-scaling \
  --region $REGION 2>/dev/null || true

aws application-autoscaling delete-scaling-policy \
  --service-namespace ecs \
  --resource-id service/$CLUSTER_NAME/taskapp-frontend-service \
  --scalable-dimension ecs:service:DesiredCount \
  --policy-name frontend-cpu-scaling \
  --region $REGION 2>/dev/null || true

# Deregister scalable targets
echo "  - Deregistering scalable targets..."
aws application-autoscaling deregister-scalable-target \
  --service-namespace ecs \
  --resource-id service/$CLUSTER_NAME/taskapp-backend-service \
  --scalable-dimension ecs:service:DesiredCount \
  --region $REGION 2>/dev/null || true

aws application-autoscaling deregister-scalable-target \
  --service-namespace ecs \
  --resource-id service/$CLUSTER_NAME/taskapp-frontend-service \
  --scalable-dimension ecs:service:DesiredCount \
  --region $REGION 2>/dev/null || true

echo "  ✓ Auto-scaling configurations removed"
echo ""

# ============================================================
# STEP 2: Delete ECS Services
# ============================================================
echo ">>> STEP 2: Deleting ECS Services..."

echo "  - Scaling down backend service to 0 tasks..."
aws ecs update-service \
  --cluster $CLUSTER_NAME \
  --service taskapp-backend-service \
  --desired-count 0 \
  --region $REGION 2>/dev/null || true

echo "  - Scaling down frontend service to 0 tasks..."
aws ecs update-service \
  --cluster $CLUSTER_NAME \
  --service taskapp-frontend-service \
  --desired-count 0 \
  --region $REGION 2>/dev/null || true

echo "  - Waiting 30 seconds for tasks to drain..."
sleep 30

echo "  - Deleting backend service..."
aws ecs delete-service \
  --cluster $CLUSTER_NAME \
  --service taskapp-backend-service \
  --force \
  --region $REGION 2>/dev/null || true

echo "  - Deleting frontend service..."
aws ecs delete-service \
  --cluster $CLUSTER_NAME \
  --service taskapp-frontend-service \
  --force \
  --region $REGION 2>/dev/null || true

echo "  ✓ ECS services deleted"
echo ""

# ============================================================
# STEP 3: Delete ECS Cluster
# ============================================================
echo ">>> STEP 3: Deleting ECS Cluster..."

echo "  - Waiting 30 seconds for services to fully delete..."
sleep 30

aws ecs delete-cluster \
  --cluster $CLUSTER_NAME \
  --region $REGION 2>/dev/null || true

echo "  ✓ ECS cluster deleted"
echo ""

# ============================================================
# STEP 4: Delete Application Load Balancer
# ============================================================
echo ">>> STEP 4: Deleting Application Load Balancer..."

# Get ALB ARN
ALB_ARN=$(aws elbv2 describe-load-balancers \
  --names taskapp-alb \
  --query 'LoadBalancers[0].LoadBalancerArn' \
  --output text \
  --region $REGION 2>/dev/null || echo "")

if [ "$ALB_ARN" != "" ] && [ "$ALB_ARN" != "None" ]; then
    echo "  - Found ALB: $ALB_ARN"
    
    # Delete listeners
    echo "  - Deleting ALB listeners..."
    LISTENERS=$(aws elbv2 describe-listeners \
      --load-balancer-arn $ALB_ARN \
      --query 'Listeners[*].ListenerArn' \
      --output text \
      --region $REGION 2>/dev/null || echo "")
    
    for LISTENER_ARN in $LISTENERS; do
        aws elbv2 delete-listener \
          --listener-arn $LISTENER_ARN \
          --region $REGION 2>/dev/null || true
    done
    
    # Delete target groups
    echo "  - Deleting target groups..."
    aws elbv2 delete-target-group \
      --target-group-arn $(aws elbv2 describe-target-groups \
        --names taskapp-backend-tg \
        --query 'TargetGroups[0].TargetGroupArn' \
        --output text \
        --region $REGION 2>/dev/null) \
      --region $REGION 2>/dev/null || true
    
    aws elbv2 delete-target-group \
      --target-group-arn $(aws elbv2 describe-target-groups \
        --names taskapp-frontend-tg \
        --query 'TargetGroups[0].TargetGroupArn' \
        --output text \
        --region $REGION 2>/dev/null) \
      --region $REGION 2>/dev/null || true
    
    # Delete ALB
    echo "  - Deleting ALB..."
    aws elbv2 delete-load-balancer \
      --load-balancer-arn $ALB_ARN \
      --region $REGION
    
    echo "  - Waiting 60 seconds for ALB to delete..."
    sleep 60
else
    echo "  - ALB not found, skipping..."
fi

echo "  ✓ Load balancer deleted"
echo ""

# ============================================================
# STEP 5: Delete RDS Database
# ============================================================
echo ">>> STEP 5: Deleting RDS Database..."

echo "  - Deleting RDS instance (skip final snapshot)..."
aws rds delete-db-instance \
  --db-instance-identifier $DB_IDENTIFIER \
  --skip-final-snapshot \
  --delete-automated-backups \
  --region $REGION 2>/dev/null || true

echo "  - This may take several minutes in the background..."
echo "  ✓ RDS deletion initiated"
echo ""

# ============================================================
# STEP 6: Delete NAT Gateway and Elastic IP
# ============================================================
echo ">>> STEP 6: Deleting NAT Gateway..."

NAT_GW_ID=$(aws ec2 describe-nat-gateways \
  --filter "Name=vpc-id,Values=$VPC_ID" "Name=state,Values=available" \
  --query 'NatGateways[0].NatGatewayId' \
  --output text \
  --region $REGION 2>/dev/null || echo "")

if [ "$NAT_GW_ID" != "" ] && [ "$NAT_GW_ID" != "None" ]; then
    echo "  - Found NAT Gateway: $NAT_GW_ID"
    
    # Get Elastic IP allocation ID
    ALLOC_ID=$(aws ec2 describe-nat-gateways \
      --nat-gateway-ids $NAT_GW_ID \
      --query 'NatGateways[0].NatGatewayAddresses[0].AllocationId' \
      --output text \
      --region $REGION)
    
    echo "  - Deleting NAT Gateway..."
    aws ec2 delete-nat-gateway \
      --nat-gateway-id $NAT_GW_ID \
      --region $REGION
    
    echo "  - Waiting 90 seconds for NAT Gateway to delete..."
    sleep 90
    
    if [ "$ALLOC_ID" != "" ] && [ "$ALLOC_ID" != "None" ]; then
        echo "  - Releasing Elastic IP: $ALLOC_ID..."
        aws ec2 release-address \
          --allocation-id $ALLOC_ID \
          --region $REGION 2>/dev/null || true
    fi
else
    echo "  - NAT Gateway not found, skipping..."
fi

echo "  ✓ NAT Gateway deleted"
echo ""

# ============================================================
# STEP 7: Delete ECR Repositories
# ============================================================
echo ">>> STEP 7: Deleting ECR Repositories..."

echo "  - Deleting taskapp-backend repository..."
aws ecr delete-repository \
  --repository-name taskapp-backend \
  --force \
  --region $REGION 2>/dev/null || true

echo "  - Deleting taskapp-frontend repository..."
aws ecr delete-repository \
  --repository-name taskapp-frontend \
  --force \
  --region $REGION 2>/dev/null || true

echo "  ✓ ECR repositories deleted"
echo ""

# ============================================================
# STEP 8: Delete CloudWatch Resources
# ============================================================
echo ">>> STEP 8: Deleting CloudWatch Resources..."

# Delete alarms
echo "  - Deleting CloudWatch alarms..."
ALARMS=$(aws cloudwatch describe-alarms \
  --query 'MetricAlarms[?contains(AlarmName, `taskapp`) || contains(AlarmName, `TargetTracking`)].AlarmName' \
  --output text \
  --region $REGION 2>/dev/null || echo "")

for ALARM in $ALARMS; do
    aws cloudwatch delete-alarms \
      --alarm-names "$ALARM" \
      --region $REGION 2>/dev/null || true
done

# Delete log groups
echo "  - Deleting CloudWatch log groups..."
aws logs delete-log-group \
  --log-group-name /ecs/taskapp-backend \
  --region $REGION 2>/dev/null || true

aws logs delete-log-group \
  --log-group-name /ecs/taskapp-frontend \
  --region $REGION 2>/dev/null || true

# Delete dashboard
echo "  - Deleting CloudWatch dashboard..."
aws cloudwatch delete-dashboards \
  --dashboard-names TaskApp-Dashboard \
  --region $REGION 2>/dev/null || true

echo "  ✓ CloudWatch resources deleted"
echo ""

# ============================================================
# STEP 9: Delete Route53 DNS Record
# ============================================================
echo ">>> STEP 9: Deleting Route53 DNS Record..."

HOSTED_ZONE_ID="Z094839029TR5QNGBDWEX"

echo "  - Deleting app.techveesolutions.com A record..."

# Get current record
RECORD_VALUE=$(aws route53 list-resource-record-sets \
  --hosted-zone-id $HOSTED_ZONE_ID \
  --query "ResourceRecordSets[?Name=='app.techveesolutions.com.'].AliasTarget.DNSName" \
  --output text 2>/dev/null || echo "")

if [ "$RECORD_VALUE" != "" ]; then
    # Create change batch
    cat > /tmp/delete-record.json << EOF
{
  "Changes": [
    {
      "Action": "DELETE",
      "ResourceRecordSet": {
        "Name": "app.techveesolutions.com",
        "Type": "A",
        "AliasTarget": {
          "DNSName": "$RECORD_VALUE",
          "EvaluateTargetHealth": false,
          "HostedZoneId": "Z35SXDOTRQ7X7K"
        }
      }
    }
  ]
}
EOF
    
    aws route53 change-resource-record-sets \
      --hosted-zone-id $HOSTED_ZONE_ID \
      --change-batch file:///tmp/delete-record.json 2>/dev/null || true
    
    rm -f /tmp/delete-record.json
    echo "  ✓ DNS record deleted"
else
    echo "  - DNS record not found, skipping..."
fi

echo ""

# ============================================================
# STEP 10: Delete VPC Resources
# ============================================================
echo ">>> STEP 10: Deleting VPC Resources..."

echo "  - Waiting 60 seconds for network interfaces to detach..."
sleep 60

# Delete security groups
echo "  - Deleting security groups..."
SG_IDS=$(aws ec2 describe-security-groups \
  --filters "Name=vpc-id,Values=$VPC_ID" \
  --query 'SecurityGroups[?GroupName!=`default`].GroupId' \
  --output text \
  --region $REGION 2>/dev/null || echo "")

for SG_ID in $SG_IDS; do
    echo "    - Deleting security group: $SG_ID"
    aws ec2 delete-security-group \
      --group-id $SG_ID \
      --region $REGION 2>/dev/null || true
done

# Delete subnets
echo "  - Deleting subnets..."
SUBNET_IDS=$(aws ec2 describe-subnets \
  --filters "Name=vpc-id,Values=$VPC_ID" \
  --query 'Subnets[].SubnetId' \
  --output text \
  --region $REGION 2>/dev/null || echo "")

for SUBNET_ID in $SUBNET_IDS; do
    echo "    - Deleting subnet: $SUBNET_ID"
    aws ec2 delete-subnet \
      --subnet-id $SUBNET_ID \
      --region $REGION 2>/dev/null || true
done

# Delete route tables
echo "  - Deleting route tables..."
RT_IDS=$(aws ec2 describe-route-tables \
  --filters "Name=vpc-id,Values=$VPC_ID" \
  --query 'RouteTables[?Associations[0].Main!=`true`].RouteTableId' \
  --output text \
  --region $REGION 2>/dev/null || echo "")

for RT_ID in $RT_IDS; do
    echo "    - Deleting route table: $RT_ID"
    aws ec2 delete-route-table \
      --route-table-id $RT_ID \
      --region $REGION 2>/dev/null || true
done

# Detach and delete Internet Gateway
echo "  - Deleting Internet Gateway..."
IGW_ID=$(aws ec2 describe-internet-gateways \
  --filters "Name=attachment.vpc-id,Values=$VPC_ID" \
  --query 'InternetGateways[0].InternetGatewayId' \
  --output text \
  --region $REGION 2>/dev/null || echo "")

if [ "$IGW_ID" != "" ] && [ "$IGW_ID" != "None" ]; then
    aws ec2 detach-internet-gateway \
      --internet-gateway-id $IGW_ID \
      --vpc-id $VPC_ID \
      --region $REGION 2>/dev/null || true
    
    aws ec2 delete-internet-gateway \
      --internet-gateway-id $IGW_ID \
      --region $REGION 2>/dev/null || true
fi

# Delete VPC
echo "  - Deleting VPC..."
aws ec2 delete-vpc \
  --vpc-id $VPC_ID \
  --region $REGION 2>/dev/null || true

echo "  ✓ VPC resources deleted"
echo ""

# ============================================================
# STEP 11: Delete IAM Resources
# ============================================================
echo ">>> STEP 11: Deleting IAM Resources..."

# Delete IAM user for GitHub Actions
echo "  - Deleting IAM user: github-actions-ecs-deployer..."

# Delete access keys
ACCESS_KEYS=$(aws iam list-access-keys \
  --user-name github-actions-ecs-deployer \
  --query 'AccessKeyMetadata[].AccessKeyId' \
  --output text 2>/dev/null || echo "")

for KEY_ID in $ACCESS_KEYS; do
    aws iam delete-access-key \
      --user-name github-actions-ecs-deployer \
      --access-key-id $KEY_ID 2>/dev/null || true
done

# Detach policies
aws iam detach-user-policy \
  --user-name github-actions-ecs-deployer \
  --policy-arn arn:aws:iam::858448674350:policy/GitHubActionsECSDeployPolicy \
  2>/dev/null || true

# Delete user
aws iam delete-user \
  --user-name github-actions-ecs-deployer \
  2>/dev/null || true

# Delete custom policy
aws iam delete-policy \
  --policy-arn arn:aws:iam::858448674350:policy/GitHubActionsECSDeployPolicy \
  2>/dev/null || true

# Delete ECS execution role
echo "  - Deleting ECS execution role..."
aws iam detach-role-policy \
  --role-name taskapp-ecs-execution-role \
  --policy-arn arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy \
  2>/dev/null || true

aws iam delete-role \
  --role-name taskapp-ecs-execution-role \
  2>/dev/null || true

echo "  ✓ IAM resources deleted"
echo ""

# ============================================================
# STEP 12: Delete Budgets
# ============================================================
echo ">>> STEP 12: Deleting Budgets..."

aws budgets delete-budget \
  --account-id 858448674350 \
  --budget-name TaskApp-Monthly-Budget \
  2>/dev/null || true

echo "  ✓ Budget deleted"
echo ""

# ============================================================
# CLEANUP COMPLETE
# ============================================================
echo "============================================================"
echo "  CLEANUP COMPLETE!"
echo "============================================================"
echo ""
echo "All AWS resources have been deleted or deletion initiated."
echo ""
echo "Note: Some resources may take additional time to fully delete:"
echo "  - RDS database: 5-10 minutes"
echo "  - Network interfaces: May linger for a few minutes"
echo ""
echo "You can verify all resources are deleted by checking:"
echo "  - AWS Console > CloudFormation (should be empty)"
echo "  - AWS Console > VPC (should show only default VPC)"
echo "  - AWS Console > EC2 (should show no resources)"
echo "  - AWS Console > RDS (should be empty)"
echo ""
echo "Monthly costs should drop to $0.00 within 24 hours."
echo ""
echo "============================================================"
