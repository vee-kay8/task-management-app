# AWS Phase 5: Backend Deployment (ECS Fargate)

## Overview
Deploy your backend API to Amazon ECS (Elastic Container Service) using Fargate. ECS Fargate is a serverless compute engine that runs your containers without managing servers. This phase also includes setting up an Application Load Balancer (ALB) to distribute traffic.

**Timeline**: 3-4 hours  
**Cost**: ~$20-25/month (ALB: ~$16/month + Fargate: ~$8/month for 2 small tasks)  
**Prerequisites**: Phase 4 complete (Docker images in ECR), Phase 3 complete (RDS database)

---

## What You'll Create

1. **ECS Cluster**: Logical grouping for your containers
2. **IAM Roles**: Task execution role and task role
3. **CloudWatch Log Group**: For application logs
4. **Task Definition**: Blueprint for running your backend container
5. **Application Load Balancer**: Distributes traffic across tasks
6. **Target Group**: Routes traffic to backend containers
7. **ECS Service**: Maintains desired number of running tasks

---

## Architecture Overview

```
Internet → ALB (Public Subnets) → ECS Tasks (Private Subnets) → RDS (Private Subnets)
          Port 80                  Port 5000 ↓                   Port 5432
                                             NAT Gateway (for ECR access)
                                                  ↓
                                             Internet (ECR)
```

---

## Important Note: Production-Ready Setup with NAT Gateway

For a production-ready deployment, we'll recreate the NAT Gateway to enable ECS tasks in private subnets to access the internet (for pulling ECR images and other external resources).

### Why NAT Gateway?
- ✅ **Security**: Tasks remain in private subnets without public IPs
- ✅ **Production-Ready**: Industry standard architecture
- ✅ **Scalability**: No public IP exhaustion concerns
- ✅ **Best Practice**: Follows AWS Well-Architected Framework
- ⚠️ **Cost**: ~$32/month (worth it for production setup)

### Architecture Benefits:
1. **Backend tasks** run in private subnets (no direct internet access)
2. **NAT Gateway** provides outbound internet for ECR image pulls
3. **Application Load Balancer** in public subnets handles incoming traffic
4. **Database** in private subnets (already configured)
5. **Multi-layer security** with defense in depth

**This guide uses private subnets with NAT Gateway** for a production-ready, secure deployment.

---

## Step 1: Recreate NAT Gateway

Recreate the NAT Gateway to enable private subnet internet access.

### AWS Console Method

1. **Allocate Elastic IP**
   - Navigate to EC2 → Elastic IPs
   - Click "Allocate Elastic IP address"
   - Click "Allocate"
   - Note the Elastic IP address

2. **Create NAT Gateway**
   - Go to VPC → NAT Gateways
   - Click "Create NAT gateway"
   ```
   Name: taskapp-nat-gateway
   Subnet: Public Subnet 1 (subnet-0aee84b90626ffe46, us-east-1a)
   Elastic IP allocation ID: Select the EIP you just allocated
   ```
   - Click "Create NAT gateway"
   - Wait for state: "Available" (2-3 minutes)

3. **Update Private Route Table**
   - Go to VPC → Route Tables
   - Select Private RT (rtb-09b52332e1238780c)
   - Click "Routes" tab → "Edit routes"
   - Remove the current 0.0.0.0/0 route (if exists)
   - Click "Add route"
   ```
   Destination: 0.0.0.0/0
   Target: NAT Gateway → Select taskapp-nat-gateway
   ```
   - Click "Save changes"

### AWS CLI Method

```bash
# Allocate Elastic IP
EIP_ALLOC_ID=$(aws ec2 allocate-address \
  --domain vpc \
  --region us-east-1 \
  --query 'AllocationId' \
  --output text)

echo "Elastic IP Allocation ID: $EIP_ALLOC_ID"

# Get Elastic IP address
EIP_ADDRESS=$(aws ec2 describe-addresses \
  --allocation-ids $EIP_ALLOC_ID \
  --query 'Addresses[0].PublicIp' \
  --output text)

echo "Elastic IP Address: $EIP_ADDRESS"

# Create NAT Gateway in Public Subnet 1
NAT_GW_ID=$(aws ec2 create-nat-gateway \
  --subnet-id subnet-0aee84b90626ffe46 \
  --allocation-id $EIP_ALLOC_ID \
  --tag-specifications 'ResourceType=nat-gateway,Tags=[{Key=Name,Value=taskapp-nat-gateway},{Key=Project,Value=TaskManagementApp}]' \
  --region us-east-1 \
  --query 'NatGateway.NatGatewayId' \
  --output text)

echo "NAT Gateway ID: $NAT_GW_ID"

# Wait for NAT Gateway to be available (takes 2-3 minutes)
echo "Waiting for NAT Gateway to become available..."
aws ec2 wait nat-gateway-available \
  --nat-gateway-ids $NAT_GW_ID \
  --region us-east-1

echo "NAT Gateway is now available!"

# Update Private Route Table
PRIVATE_RT_ID=rtb-09b52332e1238780c

# Remove old route if exists (might fail if no route, that's okay)
aws ec2 delete-route \
  --route-table-id $PRIVATE_RT_ID \
  --destination-cidr-block 0.0.0.0/0 \
  --region us-east-1 2>/dev/null || true

# Add new route to NAT Gateway
aws ec2 create-route \
  --route-table-id $PRIVATE_RT_ID \
  --destination-cidr-block 0.0.0.0/0 \
  --nat-gateway-id $NAT_GW_ID \
  --region us-east-1

echo "Route table updated successfully!"

# Verify route
aws ec2 describe-route-tables \
  --route-table-ids $PRIVATE_RT_ID \
  --query 'RouteTables[0].Routes' \
  --region us-east-1
```

### Verify NAT Gateway

```bash
# Check NAT Gateway status
aws ec2 describe-nat-gateways \
  --nat-gateway-ids $NAT_GW_ID \
  --query 'NatGateways[0].[NatGatewayId,State,SubnetId,NatGatewayAddresses[0].PublicIp]' \
  --output table

# Expected: State should be "available"
```

**Save these values** for your aws-resources.md:
- NAT Gateway ID: [from output]
- Elastic IP: [from output]

---

## Step 2: Create ECS Cluster

### AWS Console Method

1. **Navigate to ECS**
   - Open AWS Console
   - Search for "ECS" and click "Elastic Container Service"

2. **Create Cluster**
   - Click "Clusters" in left sidebar
   - Click "Create cluster"

3. **Configure Cluster**
   ```
   Cluster name: taskapp-cluster
   Infrastructure: AWS Fargate (serverless)
   ```

4. **Monitoring (Optional)**
   ```
   ☐ Use Container Insights (costs extra)
   ```

5. **Create**
   - Click "Create"
   - Wait for status: "Active"

### AWS CLI Method

```bash
# Create ECS cluster
aws ecs create-cluster \
  --cluster-name taskapp-cluster \
  --region us-east-1 \
  --tags key=Project,value=TaskManagementApp key=Component,value=Backend

# Verify creation
aws ecs describe-clusters \
  --clusters taskapp-cluster \
  --region us-east-1
```

---

## Step 3: Create CloudWatch Log Group

This stores your backend application logs.

### AWS Console Method

1. **Navigate to CloudWatch**
   - Search for "CloudWatch"
   - Click "Logs" → "Log groups"

2. **Create Log Group**
   - Click "Create log group"
   - Log group name: `/ecs/taskapp-backend`
   - Retention: 7 days
   - Click "Create"

### AWS CLI Method

```bash
# Create log group
aws logs create-log-group \
  --log-group-name /ecs/taskapp-backend \
  --region us-east-1

# Set retention (7 days)
aws logs put-retention-policy \
  --log-group-name /ecs/taskapp-backend \
  --retention-in-days 7 \
  --region us-east-1

# Verify
aws logs describe-log-groups \
  --log-group-name-prefix /ecs/taskapp-backend
```

**Windows Git Bash Users**: If you get path conversion errors, use double slashes:
```bash
aws logs create-log-group --log-group-name //ecs/taskapp-backend --region us-east-1
```

---

## Step 4: Create IAM Roles

ECS needs two roles: one to pull images and create logs (execution role), and one for your application to access AWS services (task role).

### Create Task Execution Role

**AWS Console Method:**

1. **Navigate to IAM**
   - Go to IAM console
   - Click "Roles" → "Create role"

2. **Select Trusted Entity**
   - Trusted entity type: AWS service
   - Use case: Elastic Container Service
   - Select: Elastic Container Service Task
   - Click "Next"

3. **Add Permissions**
   - Search and select: `AmazonECSTaskExecutionRolePolicy`
   - Click "Next"

4. **Name and Create**
   ```
   Role name: taskapp-ecs-execution-role
   Description: Allows ECS tasks to pull images and write logs
   ```
   - Click "Create role"

**AWS CLI Method:**

```bash
# Create trust policy file
cat > ecs-task-execution-trust-policy.json << 'EOF'
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "Service": "ecs-tasks.amazonaws.com"
      },
      "Action": "sts:AssumeRole"
    }
  ]
}
EOF

# Create execution role
aws iam create-role \
  --role-name taskapp-ecs-execution-role \
  --assume-role-policy-document file://ecs-task-execution-trust-policy.json \
  --description "Allows ECS tasks to pull images and write logs"

# Attach AWS managed policy
aws iam attach-role-policy \
  --role-name taskapp-ecs-execution-role \
  --policy-arn arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy

# Get role ARN (save this)
aws iam get-role \
  --role-name taskapp-ecs-execution-role \
  --query 'Role.Arn' \
  --output text
```

### Create Task Role (Optional for now)

The task role allows your application code to access AWS services. We'll skip this for now since the backend doesn't directly call AWS services.

---

## Step 5: Create Application Load Balancer

### AWS Console Method

1. **Navigate to EC2 → Load Balancers**
   - Go to EC2 console
   - Click "Load Balancers" in left sidebar
   - Click "Create load balancer"

2. **Select Type**
   - Choose: Application Load Balancer
   - Click "Create"

3. **Basic Configuration**
   ```
   Load balancer name: taskapp-alb
   Scheme: Internet-facing
   IP address type: IPv4
   ```

4. **Network Mapping**
   ```
   VPC: Select your VPC (10.0.0.0/16)
   Mappings: Select both availability zones
     - us-east-1a → Public Subnet 1 (10.0.1.0/24)
     - us-east-1b → Public Subnet 2 (10.0.2.0/24)
   ```

5. **Security Groups**
   - Remove default security group
   - Select: TaskApp-ALB-SG (sg-0ca03625756c71a66)

6. **Listeners and Routing**
   ```
   Protocol: HTTP
   Port: 80
   Default action: Create target group (see next step)
   ```

7. **Don't create yet** - We need to create the target group first

### AWS CLI Method (After creating target group)

We'll create the ALB after the target group in Step 5.

---

## Step 6: Create Target Group

The target group routes traffic to your backend containers.

### AWS Console Method

1. **Create Target Group** (while creating ALB or separately)
   - In ALB creation wizard, click "Create target group"
   - OR: Go to EC2 → Target Groups → Create target group

2. **Choose Target Type**
   - Target type: IP addresses (required for Fargate)
   - Click "Next"

3. **Basic Configuration**
   ```
   Target group name: taskapp-backend-tg
   Protocol: HTTP
   Port: 5000
   VPC: Select your VPC
   Protocol version: HTTP1
   ```

4. **Health Checks**
   ```
   Health check protocol: HTTP
   Health check path: /
   ```
   
   **Note**: Your backend doesn't have a dedicated health endpoint. We'll use `/` for now. If it doesn't work, we'll adjust.

5. **Advanced Health Check Settings**
   ```
   Healthy threshold: 2
   Unhealthy threshold: 2
   Timeout: 5 seconds
   Interval: 30 seconds
   Success codes: 200
   ```

6. **Don't register targets yet** - ECS will do this automatically

7. **Create**
   - Click "Create target group"

### AWS CLI Method

```bash
# Create target group
aws elbv2 create-target-group \
  --name taskapp-backend-tg \
  --protocol HTTP \
  --port 5000 \
  --vpc-id vpc-016004b6f25f26302 \
  --target-type ip \
  --health-check-protocol HTTP \
  --health-check-path / \
  --health-check-interval-seconds 30 \
  --health-check-timeout-seconds 5 \
  --healthy-threshold-count 2 \
  --unhealthy-threshold-count 2 \
  --matcher HttpCode=200 \
  --region us-east-1

# Save the target group ARN from output
```

---

## Step 7: Complete ALB Creation

### AWS Console Method (continued from Step 5)

1. **Back to ALB Creation**
   - In the listener section, select the target group you just created
   - Click "Create load balancer"
   - Wait for state: "Active" (2-3 minutes)

2. **Get ALB DNS Name**
   - Click on your load balancer
   - Copy the DNS name (e.g., `taskapp-alb-123456789.us-east-1.elb.amazonaws.com`)

### AWS CLI Method

```bash
# Get subnet IDs
PUBLIC_SUBNET_1=subnet-0aee84b90626ffe46
PUBLIC_SUBNET_2=subnet-0be6223f381db982f
ALB_SG=sg-0ca03625756c71a66

# Get target group ARN (from previous step or query it)
TG_ARN=$(aws elbv2 describe-target-groups \
  --names taskapp-backend-tg \
  --query 'TargetGroups[0].TargetGroupArn' \
  --output text)

# Create Application Load Balancer
aws elbv2 create-load-balancer \
  --name taskapp-alb \
  --subnets $PUBLIC_SUBNET_1 $PUBLIC_SUBNET_2 \
  --security-groups $ALB_SG \
  --scheme internet-facing \
  --type application \
  --ip-address-type ipv4 \
  --tags Key=Project,Value=TaskManagementApp \
  --region us-east-1

# Get ALB ARN (save this)
ALB_ARN=$(aws elbv2 describe-load-balancers \
  --names taskapp-alb \
  --query 'LoadBalancers[0].LoadBalancerArn' \
  --output text)

# Create listener (HTTP:80 → target group)
aws elbv2 create-listener \
  --load-balancer-arn $ALB_ARN \
  --protocol HTTP \
  --port 80 \
  --default-actions Type=forward,TargetGroupArn=$TG_ARN \
  --region us-east-1

# Get ALB DNS name
aws elbv2 describe-load-balancers \
  --names taskapp-alb \
  --query 'LoadBalancers[0].DNSName' \
  --output text
```

---

## Step 8: Prepare Environment Variables

Your backend needs database connection info and other environment variables.

### Review Current Backend Environment Variables

```bash
# Check what your backend needs
cat backend/.env

# Common variables needed:
# - DATABASE_URL
# - JWT_SECRET
# - FLASK_ENV
# - CORS_ORIGINS
```

### Get Database Endpoint

```bash
# From your aws-resources.md or query RDS
aws rds describe-db-instances \
  --db-instance-identifier taskapp-db \
  --query 'DBInstances[0].Endpoint.Address' \
  --output text
```

**Output**: `taskapp-db.cqaewjp43tdm.us-east-1.rds.amazonaws.com`

### Create Environment Variables List

You'll need these for the task definition:

```bash
# Database
DATABASE_URL=postgresql://postgres:YOUR_PASSWORD@taskapp-db.cqaewjp43tdm.us-east-1.rds.amazonaws.com:5432/taskmanagement

# JWT Secret (generate a secure random string)
JWT_SECRET=$(openssl rand -base64 32)

# Flask environment
FLASK_ENV=production

# CORS (ALB DNS name - we'll update after we get it)
CORS_ORIGINS=http://taskapp-alb-XXXXXX.us-east-1.elb.amazonaws.com

# Database components (if backend uses them separately)
DB_HOST=taskapp-db.cqaewjp43tdm.us-east-1.rds.amazonaws.com
DB_PORT=5432
DB_NAME=taskmanagement
DB_USER=postgres
DB_PASSWORD=YOUR_PASSWORD
```

---

## Step 9: Create ECS Task Definition

The task definition is a blueprint for running your container.

### AWS Console Method

1. **Navigate to ECS → Task Definitions**
   - Click "Task definitions"
   - Click "Create new task definition"

2. **Configure Task Definition**
   ```
   Task definition family: taskapp-backend
   Launch type: AWS Fargate
   Operating system/Architecture: Linux/X86_64
   CPU: 0.25 vCPU
   Memory: 0.5 GB
   Task role: None (not needed yet)
   Task execution role: taskapp-ecs-execution-role
   ```

3. **Container - 1**
   
   **Container Details:**
   ```
   Name: backend
   Image URI: 858448674350.dkr.ecr.us-east-1.amazonaws.com/taskapp-backend:latest
   Essential container: Yes
   ```

   **Port Mappings:**
   ```
   Container port: 5000
   Protocol: TCP
   Port name: backend-5000-tcp
   App protocol: HTTP
   ```

   **Environment Variables:**
   Click "Add environment variable" for each:
   ```
   DATABASE_URL = postgresql://postgres:YOUR_PASSWORD@taskapp-db.cqaewjp43tdm.us-east-1.rds.amazonaws.com:5432/taskmanagement
   FLASK_ENV = production
   JWT_SECRET = YOUR_GENERATED_SECRET
   CORS_ORIGINS = *
   ```

   **CloudWatch Logs:**
   ```
   ☑ Use log collection
   Log driver: awslogs
   awslogs-group: /ecs/taskapp-backend
   awslogs-region: us-east-1
   awslogs-stream-prefix: ecs
   ```

4. **Create**
   - Review configuration
   - Click "Create"

### AWS CLI Method

```bash
# First, get your ECR image URI and execution role ARN
ECR_IMAGE_URI=858448674350.dkr.ecr.us-east-1.amazonaws.com/taskapp-backend:latest
EXECUTION_ROLE_ARN=$(aws iam get-role --role-name taskapp-ecs-execution-role --query 'Role.Arn' --output text)

# Replace these with your actual values
DB_PASSWORD="YourActualPassword"
JWT_SECRET=$(openssl rand -base64 32)

# Create task definition JSON
cat > taskapp-backend-task-def.json << EOF
{
  "family": "taskapp-backend",
  "networkMode": "awsvpc",
  "requiresCompatibilities": ["FARGATE"],
  "cpu": "256",
  "memory": "512",
  "executionRoleArn": "$EXECUTION_ROLE_ARN",
  "containerDefinitions": [
    {
      "name": "backend",
      "image": "$ECR_IMAGE_URI",
      "essential": true,
      "portMappings": [
        {
          "containerPort": 5000,
          "protocol": "tcp",
          "name": "backend-5000-tcp",
          "appProtocol": "http"
        }
      ],
      "environment": [
        {
          "name": "DATABASE_URL",
          "value": "postgresql://postgres:$DB_PASSWORD@taskapp-db.cqaewjp43tdm.us-east-1.rds.amazonaws.com:5432/taskmanagement"
        },
        {
          "name": "FLASK_ENV",
          "value": "production"
        },
        {
          "name": "JWT_SECRET",
          "value": "$JWT_SECRET"
        },
        {
          "name": "CORS_ORIGINS",
          "value": "*"
        }
      ],
      "logConfiguration": {
        "logDriver": "awslogs",
        "options": {
          "awslogs-group": "/ecs/taskapp-backend",
          "awslogs-region": "us-east-1",
          "awslogs-stream-prefix": "ecs"
        }
      }
    }
  ]
}
EOF

# Register task definition
aws ecs register-task-definition \
  --cli-input-json file://taskapp-backend-task-def.json \
  --region us-east-1

# Verify creation
aws ecs describe-task-definition \
  --task-definition taskapp-backend \
  --region us-east-1
```

---

## Step 10: Create ECS Service

The service maintains your desired number of running tasks behind the load balancer.

### AWS Console Method

1. **Navigate to Cluster**
   - Go to ECS → Clusters
   - Click "taskapp-cluster"
   - Click "Services" tab
   - Click "Create"

2. **Environment**
   ```
   Compute options: Launch type
   Launch type: FARGATE
   Platform version: LATEST
   ```

3. **Deployment Configuration**
   ```
   Application type: Service
   Task definition:
     Family: taskapp-backend
     Revision: 1 (latest)
   Service name: taskapp-backend-service
   Desired tasks: 2
   ```

4. **Networking**
   ```
   VPC: Select your VPC (10.0.0.0/16)
   Subnets: Select both PRIVATE subnets
     - subnet-0681cafcc954cd8a6 (us-east-1a, Private Subnet 1)
     - subnet-04f1cbee6ad2f9d17 (us-east-1b, Private Subnet 2)
   Security group: Use existing
     - Select: TaskApp-Backend-SG (sg-01e0fb4d04d2a2234)
   Public IP: DISABLED (NAT Gateway provides internet access)
   ```

5. **Load Balancing**
   
   ⚠️ **IMPORTANT**: Do NOT create a new listener! The listener was already created in Step 7.
   
   ```
   Load balancer type: Application Load Balancer
   Load balancer: taskapp-alb
   
   Container to load balance:
     Container: backend:5000
     
   Listener: Use an existing listener ← CRITICAL: Select this option!
     - Select: 80:HTTP (created in Step 7)
   
   Target group: Use an existing target group
     - Select: taskapp-backend-tg
   ```
   
   **Common Mistake**: If you select "Create new listener" with port 80, you'll get an error:
   _"Listener port already exists, please specify a unique listener port"_
   
   **Solution**: Change to "Use an existing listener" and select the 80:HTTP listener.

6. **Service Auto Scaling (Optional - skip for now)**
   - Leave disabled

7. **Create Service**
   - Review configuration
   - Click "Create"
   - Wait for tasks to start (2-3 minutes)

### AWS CLI Method

```bash
# Get required values
CLUSTER_NAME=taskapp-cluster
SERVICE_NAME=taskapp-backend-service
TASK_DEF=taskapp-backend
PRIVATE_SUBNET_1=subnet-0681cafcc954cd8a6
PRIVATE_SUBNET_2=subnet-04f1cbee6ad2f9d17
BACKEND_SG=sg-01e0fb4d04d2a2234
TG_ARN=$(aws elbv2 describe-target-groups --names taskapp-backend-tg --query 'TargetGroups[0].TargetGroupArn' --output text)

# Create ECS service
aws ecs create-service \
  --cluster $CLUSTER_NAME \
  --service-name $SERVICE_NAME \
  --task-definition $TASK_DEF \
  --desired-count 2 \
  --launch-type FARGATE \
  --platform-version LATEST \
  --network-configuration "awsvpcConfiguration={subnets=[$PRIVATE_SUBNET_1,$PRIVATE_SUBNET_2],securityGroups=[$BACKEND_SG],assignPublicIp=DISABLED}" \
  --load-balancers "targetGroupArn=$TG_ARN,containerName=backend,containerPort=5000" \
  --region us-east-1

# Check service status
aws ecs describe-services \
  --cluster $CLUSTER_NAME \
  --services $SERVICE_NAME \
  --region us-east-1 \
  --query 'services[0].[serviceName,status,runningCount,desiredCount]'
```

---

## Step 11: Monitor Task Deployment

### Check Task Status

**AWS Console:**
1. Go to ECS → Clusters → taskapp-cluster
2. Click "Services" tab → taskapp-backend-service
3. Click "Tasks" tab
4. Wait for tasks to show "RUNNING" status
5. Check "Last status" should be "RUNNING"

**AWS CLI:**
```bash
# List tasks in service
aws ecs list-tasks \
  --cluster taskapp-cluster \
  --service-name taskapp-backend-service \
  --region us-east-1

# Get task details
TASK_ARN=$(aws ecs list-tasks --cluster taskapp-cluster --service-name taskapp-backend-service --query 'taskArns[0]' --output text)

aws ecs describe-tasks \
  --cluster taskapp-cluster \
  --tasks $TASK_ARN \
  --region us-east-1 \
  --query 'tasks[0].[taskArn,lastStatus,healthStatus,containers[0].healthStatus]'
```

### Check CloudWatch Logs

```bash
# View recent logs
aws logs tail /ecs/taskapp-backend --follow

# Windows Git Bash users - use double slash:
aws logs tail //ecs/taskapp-backend --follow

# Or in console:
# CloudWatch → Log groups → /ecs/taskapp-backend → View logs
```

---

## Step 12: Verify Health Checks

### Check Target Health

**AWS Console:**
1. Go to EC2 → Target Groups
2. Click "taskapp-backend-tg"
3. Click "Targets" tab
4. Wait for "Health status" to be "healthy"
5. Should see 2 targets (your 2 tasks)

**AWS CLI:**
```bash
# Check target health
aws elbv2 describe-target-health \
  --target-group-arn $(aws elbv2 describe-target-groups --names taskapp-backend-tg --query 'TargetGroups[0].TargetGroupArn' --output text) \
  --region us-east-1
```

**Expected output**: Both targets should show `State: healthy`

---

## Step 13: Test Backend API

### Get ALB DNS Name

```bash
# Get ALB DNS
aws elbv2 describe-load-balancers \
  --names taskapp-alb \
  --query 'LoadBalancers[0].DNSName' \
  --output text
```

### Test Endpoints

```bash
# Set ALB DNS (replace with your actual DNS)
ALB_DNS="taskapp-alb-XXXXXX.us-east-1.elb.amazonaws.com"

# Test root endpoint
curl http://$ALB_DNS/

# Expected: API response (might be 404 if no root route, that's okay)

# Test health endpoint (if you have one)
curl http://$ALB_DNS/api/health

# Test registration endpoint
curl -X POST http://$ALB_DNS/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "Test123!@#",
    "username": "testuser"
  }'

# Expected: Success response with user data or token

# Test login endpoint
curl -X POST http://$ALB_DNS/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "Test123!@#"
  }'

# Expected: Success response with auth token
```

---

## Troubleshooting

### Listener Port Already Exists Error

**Error**: "Listener port already exists, please specify a unique listener port" (Port 80)

**Cause**: You selected "Create new listener" instead of "Use an existing listener" in Step 10.

**Solution**:
1. In the service creation form, scroll to the "Load balancing" section
2. Change from "Create new listener" to "Use an existing listener"
3. Select the existing listener: **80:HTTP** (created in Step 7)
4. Click "Create" again

**Why**: The HTTP:80 listener was already created and attached to the ALB in Step 7. You must reuse it, not create a duplicate.

---

### Tasks Keep Stopping

**Check CloudWatch Logs:**
```bash
# Linux/Mac/PowerShell:
aws logs tail /ecs/taskapp-backend --since 10m

# Windows Git Bash:
aws logs tail //ecs/taskapp-backend --since 10m
```

**Common issues:**
- Database connection failed → Check DATABASE_URL
- Image pull failed → Verify ECR URI and permissions
- Container crashed → Check application logs

### Targets Unhealthy

**Check health check path:**
1. Verify your backend responds to `/` or update health check path
2. Check security group allows traffic from ALB
3. Verify container is listening on port 5000

**Update health check if needed:**
```bash
# If your backend has a /health endpoint, update target group
aws elbv2 modify-target-group \
  --target-group-arn <TG_ARN> \
  --health-check-path /api/health
```

### Cannot Pull ECR Image

**Error**: `CannotPullContainerError`

**Solutions:**
1. Verify NAT Gateway is in "available" state
2. Check private route table has route to NAT Gateway (0.0.0.0/0 → NAT Gateway)
3. Verify execution role has ECR permissions
4. Confirm ECR image URI is correct
5. Check security group allows outbound traffic

```bash
# Verify NAT Gateway is available
aws ec2 describe-nat-gateways \
  --query 'NatGateways[?State==`available`].[NatGatewayId,State]' \
  --output table

# Verify route table
aws ec2 describe-route-tables \
  --route-table-ids rtb-09b52332e1238780c \
  --query 'RouteTables[0].Routes'

# Verify image exists in ECR
aws ecr describe-images \
  --repository-name taskapp-backend \
  --image-ids imageTag=latest
```

### Database Connection Fails

**Check:**
1. Database security group allows backend security group on port 5432
2. DATABASE_URL is correct
3. Database is publicly accessible or in same VPC

```bash
# Test database connection from ECS task
# Get task ID
TASK_ID=$(aws ecs list-tasks --cluster taskapp-cluster --service-name taskapp-backend-service --query 'taskArns[0]' --output text | awk -F/ '{print $NF}')

# Execute command in running task (requires ECS Exec enabled)
# Or check logs for database connection errors

# Linux/Mac/PowerShell:
aws logs tail /ecs/taskapp-backend --since 5m | grep -i "database\|error"

# Windows Git Bash:
aws logs tail //ecs/taskapp-backend --since 5m | grep -i "database\|error"
```

### High Costs

**Reduce costs:**
```bash
# Reduce to 1 task
aws ecs update-service \
  --cluster taskapp-cluster \
  --service taskapp-backend-service \
  --desired-count 1

# Or stop service completely
aws ecs update-service \
  --cluster taskapp-cluster \
  --service taskapp-backend-service \
  --desired-count 0
```

---

## Phase 5 Verification Checklist

### Infrastructure
- [ ] NAT Gateway recreated and available
- [ ] Elastic IP allocated for NAT Gateway
- [ ] Private route table updated (0.0.0.0/0 → NAT Gateway)
- [ ] ECS cluster created (taskapp-cluster)
- [ ] CloudWatch log group created (/ecs/taskapp-backend)
- [ ] IAM execution role created (taskapp-ecs-execution-role)
- [ ] Application Load Balancer created (taskapp-alb)
- [ ] Target group created (taskapp-backend-tg)
- [ ] ALB listener configured (HTTP:80 → target group)

### Task Definition
- [ ] Task definition created (taskapp-backend)
- [ ] ECR image URI specified correctly
- [ ] Environment variables configured
- [ ] Database connection string set
- [ ] JWT secret configured
- [ ] CloudWatch logs configured
- [ ] CPU: 0.25 vCPU, Memory: 0.5 GB

### Service
- [ ] ECS service created (taskapp-backend-service)
- [ ] Desired count: 2 tasks
- [ ] Tasks running in private subnets
- [ ] Public IP disabled on tasks (using NAT Gateway)
- [ ] Security group attached (TaskApp-Backend-SG)
- [ ] Load balancer configured

### Deployment Status
- [ ] Tasks status: RUNNING
- [ ] Running count matches desired count (2/2)
- [ ] No tasks in STOPPED state with errors
- [ ] CloudWatch logs show application startup

### Health & Connectivity
- [ ] Target health: healthy (both targets)
- [ ] ALB state: active
- [ ] ALB DNS name accessible
- [ ] Can access backend via ALB DNS
- [ ] Registration endpoint works
- [ ] Login endpoint works
- [ ] Database connectivity verified

### Security
- [ ] Backend security group allows ALB traffic on port 5000
- [ ] ALB security group allows internet traffic on port 80
- [ ] Database security group allows backend traffic on port 5432
- [ ] Tasks in private subnets (no direct internet access)
- [ ] NAT Gateway provides outbound internet only
- [ ] Tasks cannot be accessed directly (only via ALB)

---

## Cost Breakdown

### Monthly Costs (Estimated)

| Resource | Specification | Monthly Cost |
|----------|--------------|--------------|
| ALB | Active hours + LCU usage | ~$16.20/month |
| ECS Fargate | 2 tasks × 0.25 vCPU | ~$6.00/month |
| ECS Fargate | 2 tasks × 0.5 GB memory | ~$2.00/month |
| CloudWatch Logs | 1 GB/month | ~$0.50/month |
| **Total** | | **~$24.70/month** |

### Cost Optimization

1. **Reduce to 1 task during development**: Save $4/month
2. **Delete NAT Gateway when not actively deploying**: Save $32/month (recreate when needed)
3. **Stop service when not testing**: ALB + NAT still cost ~$48/month
4. **Use free tier CloudWatch**: 5 GB logs/month free
5. **Consider deleting entire stack when not in use**: Save all costs, redeploy via IaC later

---

## What's Next?

After completing Phase 5, you'll have:
- ✅ Backend API running on ECS Fargate
- ✅ Application Load Balancer distributing traffic
- ✅ 2 tasks for high availability
- ✅ Auto-recovery if tasks fail
- ✅ Centralized logging in CloudWatch

**Phase 6 Preview**: Frontend Deployment (S3 + CloudFront)
- Update frontend to use ALB URL for API calls
- Build frontend for production
- Create S3 bucket for static hosting
- Set up CloudFront CDN
- Deploy frontend
- Test full application flow

Estimated time: 2-3 hours  
Estimated cost: ~$1-2/month (S3 + CloudFront free tier eligible)

---

## Quick Reference Commands

```bash
# View service status
aws ecs describe-services \
  --cluster taskapp-cluster \
  --services taskapp-backend-service \
  --query 'services[0].[serviceName,status,runningCount,desiredCount,deployments]'

# List running tasks
aws ecs list-tasks \
  --cluster taskapp-cluster \
  --service-name taskapp-backend-service

# View logs (live tail)
aws logs tail /ecs/taskapp-backend --follow
# Windows Git Bash: aws logs tail //ecs/taskapp-backend --follow

# Check target health
aws elbv2 describe-target-health \
  --target-group-arn $(aws elbv2 describe-target-groups --names taskapp-backend-tg --query 'TargetGroups[0].TargetGroupArn' --output text)

# Update service (change task count)
aws ecs update-service \
  --cluster taskapp-cluster \
  --service taskapp-backend-service \
  --desired-count 1

# Force new deployment (after updating task definition)
aws ecs update-service \
  --cluster taskapp-cluster \
  --service taskapp-backend-service \
  --force-new-deployment

# Get ALB DNS
aws elbv2 describe-load-balancers \
  --names taskapp-alb \
  --query 'LoadBalancers[0].DNSName' \
  --output text

# Delete service (to save costs)
aws ecs delete-service \
  --cluster taskapp-cluster \
  --service taskapp-backend-service \
  --force
```

---

## Summary

Phase 5 deploys your containerized backend to AWS using modern, production-ready services:

- **ECS Fargate**: Serverless container orchestration (no servers to manage)
- **Application Load Balancer**: Distributes traffic, health checks, high availability
- **CloudWatch**: Centralized logging and monitoring
- **IAM**: Secure role-based permissions

Your backend is now running in the cloud with production-ready security, accessible via HTTP, ready for frontend integration!

**Total Phase 5 Time**: 3-4 hours  
**Total Phase 5 Cost**: ~$57/month (includes NAT Gateway for production security)
