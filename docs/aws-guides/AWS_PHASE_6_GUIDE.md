# AWS Phase 6: Frontend Deployment (ECS Fargate)

## Overview
Deploy your Next.js frontend to Amazon ECS Fargate alongside your backend. Since your application has dynamic content, authentication, and client-side routing, deploying to ECS provides a better experience than static hosting.

**Timeline**: 2-3 hours  
**Cost**: ~$18/month (2 frontend tasks on Fargate)  
**Prerequisites**: Phase 5 complete (Backend API running on ECS)

---

## ⚠️ CRITICAL: Next.js Build-Time Environment Variables

**READ THIS FIRST!** The #1 issue you'll encounter:

**Problem:** Next.js `NEXT_PUBLIC_*` variables are compiled into JavaScript at **BUILD TIME**, not runtime.

**Impact:** If you build your Docker image without setting `NEXT_PUBLIC_API_URL`, your frontend will try to call `localhost:5000` even when deployed to AWS.

**Solution:** Always build with `--build-arg`:
```bash
docker build \
  --build-arg NEXT_PUBLIC_API_URL=http://taskapp-alb-1878540875.us-east-1.elb.amazonaws.com \
  -t taskapp-frontend:latest .
```

**Verification:**
```bash
# After building, verify the ALB URL is baked in:
docker run --rm taskapp-frontend:latest sh -c "grep -r 'taskapp-alb' /app/.next/server/ | head -2"
# Should see your ALB URL in the output!
```

See the [Troubleshooting](#troubleshooting) section for detailed diagnosis and fixes.

---

## What You'll Create

1. **Frontend Docker Image**: Containerized Next.js app
2. **ECR Push**: Upload frontend image to existing ECR repository
3. **ECS Task Definition**: Blueprint for running frontend container
4. **ECS Service**: Maintains 2 running frontend tasks
5. **ALB Path Routing**: Route `/api/*` to backend, `/*` to frontend

---

## Architecture Overview

```
Internet → ALB (Public Subnets)
            ├─ /api/* → Backend ECS Tasks (Private Subnets, Port 5000)
            └─ /*     → Frontend ECS Tasks (Private Subnets, Port 3000)
                         ↓
                    RDS Database (Private Subnets, Port 5432)
```

**Benefits:**
- ✅ **Dynamic Content** - Full Next.js features (SSR, API routes)
- ✅ **Authentication** - Protected routes work seamlessly
- ✅ **Same Infrastructure** - Consistent deployment pattern
- ✅ **Path-Based Routing** - Single domain for frontend + backend
- ✅ **High Availability** - 2 tasks for redundancy

**Why ECS Instead of S3?**
- Your app uses authentication (JWT tokens)
- Dynamic user-generated content (projects, tasks)
- Client-side routing with protected routes
- Next.js server features (middleware, headers)

---

## Step 1: Verify Frontend Environment Configuration

Your frontend needs the correct backend API URL.

### Check .env.production

```bash
cd frontend
cat .env.production
```

**Should contain:**
```
NEXT_PUBLIC_API_URL=http://taskapp-alb-1878540875.us-east-1.elb.amazonaws.com
```

**Important:** Since frontend and backend will be behind the same ALB, we'll update this to use relative paths later.

### Verify Frontend Build

```bash
# Make sure build works
npm run build

# Check output
ls -la .next/standalone/
```

Expected: `.next/standalone/` directory with minimal Node.js server.

---

## Step 2: Build Docker Image for Frontend

### ⚠️ CRITICAL: Next.js Environment Variables

**IMPORTANT:** Next.js `NEXT_PUBLIC_*` variables are **baked into JavaScript at BUILD time**, not runtime!

- ❌ **WRONG:** Setting `NEXT_PUBLIC_API_URL` as runtime ENV in container  
- ✅ **CORRECT:** Setting `NEXT_PUBLIC_API_URL` during `docker build` using `--build-arg`

**Why this matters:**
- Next.js compiles these variables into your JavaScript bundles during build
- Changing environment variables in a running container has **NO EFFECT**
- You must rebuild the Docker image with correct values

### Verify Dockerfile Exists

```bash
# Check if Dockerfile exists
ls -la Dockerfile
cat Dockerfile
```

Your frontend should already have a Dockerfile from the Docker phase. It should:
- Use multi-stage build with standalone output
- Accept `ARG NEXT_PUBLIC_API_URL` before the build step
- Set `ENV NEXT_PUBLIC_API_URL=${NEXT_PUBLIC_API_URL}` to pass it to Next.js

### Build Docker Image with Correct API URL

```bash
# Navigate to frontend directory
cd frontend

# Build Docker image with ALB URL baked in
# CRITICAL: Use --build-arg to set NEXT_PUBLIC_API_URL at build time!
docker build \
  --build-arg NEXT_PUBLIC_API_URL=http://taskapp-alb-1878540875.us-east-1.elb.amazonaws.com \
  -t taskapp-frontend:latest .

# Optional: Verify the ALB URL is in the built image
docker run --rm taskapp-frontend:latest sh -c "grep -r 'taskapp-alb' /app/.next/server/ | head -2"

# Test locally (optional)
docker run -d -p 3000:3000 \
  --name taskapp-frontend-test \
  taskapp-frontend:latest

# Test in browser
start http://localhost:3000

# Stop test container
docker stop taskapp-frontend-test
docker rm taskapp-frontend-test
```

---

## Step 3: Push Frontend Image to ECR

You already have a frontend ECR repository from Phase 4.

### Authenticate Docker to ECR

```bash
# Login to ECR
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin 858448674350.dkr.ecr.us-east-1.amazonaws.com
```

### Tag and Push Image

```bash
# Tag image for ECR
docker tag taskapp-frontend:latest 858448674350.dkr.ecr.us-east-1.amazonaws.com/taskapp-frontend:latest
docker tag taskapp-frontend:latest 858448674350.dkr.ecr.us-east-1.amazonaws.com/taskapp-frontend:v1.0.0

# Push to ECR
docker push 858448674350.dkr.ecr.us-east-1.amazonaws.com/taskapp-frontend:latest
docker push 858448674350.dkr.ecr.us-east-1.amazonaws.com/taskapp-frontend:v1.0.0

# Verify images in ECR
aws ecr describe-images --repository-name taskapp-frontend --region us-east-1
```

---

## Step 4: Create CloudWatch Log Group

```bash
# Create log group for frontend
aws logs create-log-group \
  --log-group-name /ecs/taskapp-frontend \
  --region us-east-1

# Set retention (7 days)
aws logs put-retention-policy \
  --log-group-name /ecs/taskapp-frontend \
  --retention-in-days 7 \
  --region us-east-1
```

**Windows Git Bash users:**
```bash
# Use double slashes
aws logs create-log-group --log-group-name //ecs/taskapp-frontend --region us-east-1
aws logs put-retention-policy --log-group-name //ecs/taskapp-frontend --retention-in-days 7 --region us-east-1
```

---

## Step 5: Create Frontend Task Definition

### AWS Console Method

1. **Navigate to ECS → Task Definitions**
   - Click "Create new task definition"

2. **Configure Task Definition**
   ```
   Task definition family: taskapp-frontend
   Launch type: AWS Fargate
   Operating system/Architecture: Linux/X86_64
   CPU: 0.25 vCPU
   Memory: 0.5 GB
   Task role: None
   Task execution role: taskapp-ecs-execution-role (same as backend)
   ```

3. **Container Configuration**
   
   **Container Details:**
   ```
   Name: frontend
   Image URI: 858448674350.dkr.ecr.us-east-1.amazonaws.com/taskapp-frontend:latest
   Essential container: Yes
   ```

   **Port Mappings:**
   ```
   Container port: 3000
   Protocol: TCP
   Port name: frontend-3000-tcp
   App protocol: HTTP
   ```

   **Environment Variables:**
   ```
   NEXT_PUBLIC_API_URL = http://taskapp-alb-1878540875.us-east-1.elb.amazonaws.com
   NODE_ENV = production
   ```
   
   **Note:** We'll update the API URL to use relative paths after ALB routing is configured.

   **CloudWatch Logs:**
   ```
   ☑ Use log collection
   Log driver: awslogs
   awslogs-group: /ecs/taskapp-frontend
   awslogs-region: us-east-1
   awslogs-stream-prefix: ecs
   ```

4. **Create**
   - Review configuration
   - Click "Create"

### AWS CLI Method

```bash
# Get execution role ARN
EXECUTION_ROLE_ARN=$(aws iam get-role --role-name taskapp-ecs-execution-role --query 'Role.Arn' --output text)

# Create task definition JSON
cat > taskapp-frontend-task-def.json << EOF
{
  "family": "taskapp-frontend",
  "networkMode": "awsvpc",
  "requiresCompatibilities": ["FARGATE"],
  "cpu": "256",
  "memory": "512",
  "executionRoleArn": "$EXECUTION_ROLE_ARN",
  "containerDefinitions": [
    {
      "name": "frontend",
      "image": "858448674350.dkr.ecr.us-east-1.amazonaws.com/taskapp-frontend:latest",
      "essential": true,
      "portMappings": [
        {
          "containerPort": 3000,
          "protocol": "tcp",
          "name": "frontend-3000-tcp",
          "appProtocol": "http"
        }
      ],
      "environment": [
        {
          "name": "NEXT_PUBLIC_API_URL",
          "value": "http://taskapp-alb-1878540875.us-east-1.elb.amazonaws.com"
        },
        {
          "name": "NODE_ENV",
          "value": "production"
        }
      ],
      "logConfiguration": {
        "logDriver": "awslogs",
        "options": {
          "awslogs-group": "/ecs/taskapp-frontend",
          "awslogs-region": "us-east-1",
          "awslogs-stream-prefix": "ecs",
          "awslogs-create-group": "true"
        }
      }
    }
  ]
}
EOF

# Register task definition
aws ecs register-task-definition \
  --cli-input-json file://taskapp-frontend-task-def.json \
  --region us-east-1

# Verify
aws ecs describe-task-definition \
  --task-definition taskapp-frontend \
  --region us-east-1
```

---

## Step 6: Create Frontend Target Group

### AWS Console Method

1. **Navigate to EC2 → Target Groups**
   - Click "Create target group"

2. **Basic Configuration**
   ```
   Target type: IP addresses (for Fargate)
   Target group name: taskapp-frontend-tg
   Protocol: HTTP
   Port: 3000
   VPC: Select your VPC (vpc-016004b6f25f26302)
   Protocol version: HTTP1
   ```

3. **Health Checks**
   ```
   Health check protocol: HTTP
   Health check path: /
   ```

4. **Advanced Health Check Settings**
   ```
   Healthy threshold: 2
   Unhealthy threshold: 2
   Timeout: 5 seconds
   Interval: 30 seconds
   Success codes: 200
   ```

5. **Create**
   - Don't register targets (ECS will do this)
   - Click "Create target group"

### AWS CLI Method

```bash
# Create frontend target group
aws elbv2 create-target-group \
  --name taskapp-frontend-tg \
  --protocol HTTP \
  --port 3000 \
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

# Get target group ARN
FRONTEND_TG_ARN=$(aws elbv2 describe-target-groups \
  --names taskapp-frontend-tg \
  --query 'TargetGroups[0].TargetGroupArn' \
  --output text)

echo "Frontend Target Group ARN: $FRONTEND_TG_ARN"
```

---

## Step 7: Update ALB with Path-Based Routing

We need to configure the ALB to route traffic based on path:
- `/api/*` → Backend target group (port 5000)
- `/*` → Frontend target group (port 3000)

### AWS Console Method

1. **Navigate to EC2 → Load Balancers**
   - Select `taskapp-alb`
   - Click "Listeners" tab

2. **Edit HTTP:80 Listener**
   - Select the HTTP:80 listener
   - Click "Actions" → "Edit rules"

3. **Add Rule for API Routing**
   - Click "+ Insert Rule"
   - **Add condition:**
     - Type: Path
     - Path pattern: `/api/*`
   - **Add action:**
     - Type: Forward to
     - Target group: `taskapp-backend-tg`
   - Set priority: 1
   - Click "Save"

4. **Update Default Rule**
   - Click on "Default" rule at bottom
   - Click "Edit"
   - **Action:**
     - Type: Forward to
     - Target group: `taskapp-frontend-tg`
   - Click "Save"

**Final Routing:**
```
Priority 1: Path = /api/* → taskapp-backend-tg (port 5000)
Default:    Path = /*     → taskapp-frontend-tg (port 3000)
```

### AWS CLI Method

```bash
# Get listener ARN
ALB_ARN=$(aws elbv2 describe-load-balancers \
  --names taskapp-alb \
  --query 'LoadBalancers[0].LoadBalancerArn' \
  --output text)

LISTENER_ARN=$(aws elbv2 describe-listeners \
  --load-balancer-arn $ALB_ARN \
  --query 'Listeners[0].ListenerArn' \
  --output text)

# Get backend target group ARN
BACKEND_TG_ARN=$(aws elbv2 describe-target-groups \
  --names taskapp-backend-tg \
  --query 'TargetGroups[0].TargetGroupArn' \
  --output text)

# Create rule for /api/* → backend
aws elbv2 create-rule \
  --listener-arn $LISTENER_ARN \
  --priority 1 \
  --conditions Field=path-pattern,Values='/api/*' \
  --actions Type=forward,TargetGroupArn=$BACKEND_TG_ARN

# Modify default action to forward to frontend
aws elbv2 modify-listener \
  --listener-arn $LISTENER_ARN \
  --default-actions Type=forward,TargetGroupArn=$FRONTEND_TG_ARN
```

---

## Step 8: Create Frontend ECS Service

### AWS Console Method

1. **Navigate to ECS → Clusters**
   - Click `taskapp-cluster`
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
     Family: taskapp-frontend
     Revision: 1 (latest)
   Service name: taskapp-frontend-service
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
       OR create new security group (TaskApp-Frontend-SG)
   Public IP: DISABLED (using NAT Gateway)
   ```

5. **Load Balancing**
   ```
   Load balancer type: Application Load Balancer
   Load balancer: taskapp-alb
   
   Container to load balance:
     Container: frontend:3000
     
   Listener: Use an existing listener
     - Select: 80:HTTP
   
   Target group: Use an existing target group
     - Select: taskapp-frontend-tg
   ```

6. **Service Auto Scaling**
   - Leave disabled for now

7. **Create Service**
   - Review configuration
   - Click "Create"
   - Wait for tasks to start (2-3 minutes)

### AWS CLI Method

```bash
# Create frontend service
aws ecs create-service \
  --cluster taskapp-cluster \
  --service-name taskapp-frontend-service \
  --task-definition taskapp-frontend \
  --desired-count 2 \
  --launch-type FARGATE \
  --platform-version LATEST \
  --network-configuration "awsvpcConfiguration={subnets=[subnet-0681cafcc954cd8a6,subnet-04f1cbee6ad2f9d17],securityGroups=[sg-01e0fb4d04d2a2234],assignPublicIp=DISABLED}" \
  --load-balancers targetGroupArn=$FRONTEND_TG_ARN,containerName=frontend,containerPort=3000 \
  --region us-east-1

# Check service status
aws ecs describe-services \
  --cluster taskapp-cluster \
  --services taskapp-frontend-service \
  --query 'services[0].[serviceName,status,runningCount,desiredCount]' \
  --region us-east-1
```

---

## Step 9: Monitor Frontend Deployment

### Check Task Status

```bash
# List frontend tasks
aws ecs list-tasks \
  --cluster taskapp-cluster \
  --service-name taskapp-frontend-service \
  --region us-east-1

# Get task details
FRONTEND_TASK_ARN=$(aws ecs list-tasks --cluster taskapp-cluster --service-name taskapp-frontend-service --query 'taskArns[0]' --output text --region us-east-1)

aws ecs describe-tasks \
  --cluster taskapp-cluster \
  --tasks $FRONTEND_TASK_ARN \
  --query 'tasks[0].[taskArn,lastStatus,healthStatus]' \
  --region us-east-1
```

### Check CloudWatch Logs

**PowerShell:**
```bash
powershell -Command "aws logs tail /ecs/taskapp-frontend --follow --region us-east-1"
```

**Git Bash:**
```bash
powershell -Command "aws logs filter-log-events --log-group-name /ecs/taskapp-frontend --region us-east-1 --limit 50"
```

### Check Target Health

```bash
# Check frontend target health
powershell -Command "aws elbv2 describe-target-health --target-group-arn (aws elbv2 describe-target-groups --names taskapp-frontend-tg --query 'TargetGroups[0].TargetGroupArn' --output text --region us-east-1) --region us-east-1"
```

**Expected:** Both frontend targets should show `State: healthy`

---

## Step 10: Test Frontend Application

### Get ALB DNS Name

```bash
# Get ALB DNS (same as before)
powershell -Command "aws elbv2 describe-load-balancers --names taskapp-alb --query 'LoadBalancers[0].DNSName' --output text --region us-east-1"
```

**Output:** `taskapp-alb-1878540875.us-east-1.elb.amazonaws.com`

### Test Frontend via ALB

```bash
# Open in browser
start http://taskapp-alb-1878540875.us-east-1.elb.amazonaws.com
```

### Test Path-Based Routing

```bash
# Test frontend (root)
curl http://taskapp-alb-1878540875.us-east-1.elb.amazonaws.com/

# Test backend API
curl http://taskapp-alb-1878540875.us-east-1.elb.amazonaws.com/api/

# Should see different responses
```

### Test Full User Flow

1. **Homepage** - Should load Next.js frontend
2. **Registration** - Create new user
3. **Login** - Authenticate and receive token
4. **Dashboard** - View authenticated content
5. **Projects** - Create/view projects
6. **Tasks** - Create/manage tasks
7. **Drag & Drop** - Move tasks between columns

---

## Step 11: Update Frontend to Use Relative API Paths

Now that frontend and backend are behind the same ALB, we can use relative paths instead of absolute URLs.

### Update Frontend Environment

Since both services are behind the same ALB:
- Frontend: `http://taskapp-alb-xxx.com/`
- Backend API: `http://taskapp-alb-xxx.com/api/`

We can use relative paths!

### Option 1: Use Relative Paths (Recommended)

Update [frontend/lib/api.ts](frontend/lib/api.ts):

```typescript
// Use relative path since frontend and backend are on same domain
const API_URL = process.env.NEXT_PUBLIC_API_URL || '/api'
```

Then update `.env.production`:
```bash
NEXT_PUBLIC_API_URL=/api
```

### Option 2: Keep Absolute URL

Keep using the ALB DNS (works but not ideal):
```bash
NEXT_PUBLIC_API_URL=http://taskapp-alb-1878540875.us-east-1.elb.amazonaws.com/api
```

### Rebuild and Redeploy

If you change the API URL:

```bash
# Navigate to frontend
cd frontend

# CRITICAL: Clean build directory first
cmd //c "rmdir /s /q .next" 2>/dev/null || rm -rf .next

# Rebuild Docker image with new API URL
# MUST use --build-arg to bake URL into JavaScript bundles!
docker build --no-cache \
  --build-arg NEXT_PUBLIC_API_URL=http://taskapp-alb-1878540875.us-east-1.elb.amazonaws.com \
  -t taskapp-frontend:latest .

# Verify ALB URL is in the image (should see taskapp-alb URLs)
docker run --rm taskapp-frontend:latest sh -c "grep -r 'taskapp-alb' /app/.next/server/ | head -2"

# Tag and push to ECR
docker tag taskapp-frontend:latest 858448674350.dkr.ecr.us-east-1.amazonaws.com/taskapp-frontend:latest
docker push 858448674350.dkr.ecr.us-east-1.amazonaws.com/taskapp-frontend:latest

# Force new deployment in ECS
aws ecs update-service \
  --cluster taskapp-cluster \
  --service taskapp-frontend-service \
  --force-new-deployment \
  --region us-east-1

# Wait for deployment (about 2 minutes)
sleep 90

# Check target health
aws elbv2 describe-target-health \
  --target-group-arn $(aws elbv2 describe-target-groups --names taskapp-frontend-tg --query 'TargetGroups[0].TargetGroupArn' --output text --region us-east-1) \
  --region us-east-1
```

---

## Step 12: Update Backend CORS (Optional)

Since frontend is now on the same domain as backend (via ALB), you can simplify CORS.

### Current CORS Setting

Backend currently has `CORS_ORIGINS=*` (allow all).

### Update for Same-Origin

Since requests come from the same ALB domain, you can:

**Option 1: Keep CORS_ORIGINS=***
- Works fine for now
- Will update in Phase 7 when we add custom domain

**Option 2: Set to ALB Domain**
```
CORS_ORIGINS=http://taskapp-alb-1878540875.us-east-1.elb.amazonaws.com
```

**Option 3: Remove CORS (Same Origin)**
- If using relative paths (`/api`), CORS isn't needed
- Requests are same-origin

---

## Troubleshooting

### 🔥 Frontend Shows localhost:5000 in Browser Network Tab

**Symptom:** Application loads but API calls fail with `ERR_CONNECTION_REFUSED` to `http://localhost:5000/api/...`

**Root Cause:** Next.js `NEXT_PUBLIC_API_URL` was NOT set during Docker build, so it used the fallback value from `lib/api.ts`

**Why This Happens:**
- Next.js bakes `NEXT_PUBLIC_*` variables into JavaScript at **BUILD TIME**
- Setting environment variables in task definition has **NO EFFECT** on these values
- The values are hardcoded into your JavaScript bundles during compilation

**Solution:**

1. **Verify the issue:**
   ```bash
   # Pull your ECR image
   docker pull 858448674350.dkr.ecr.us-east-1.amazonaws.com/taskapp-frontend:latest
   
   # Check what API URL is baked in (should see localhost if wrong)
   docker run --rm 858448674350.dkr.ecr.us-east-1.amazonaws.com/taskapp-frontend:latest \
     sh -c "grep -r 'localhost:5000' /app/.next/server/ | head -2"
   ```

2. **Fix: Rebuild with --build-arg:**
   ```bash
   cd frontend
   
   # Clean build
   cmd //c "rmdir /s /q .next" 2>/dev/null || rm -rf .next
   
   # Rebuild with CORRECT build argument
   docker build --no-cache \
     --build-arg NEXT_PUBLIC_API_URL=http://taskapp-alb-1878540875.us-east-1.elb.amazonaws.com \
     -t taskapp-frontend:latest .
   
   # Verify ALB URL is now in image
   docker run --rm taskapp-frontend:latest \
     sh -c "grep -r 'taskapp-alb' /app/.next/server/ | head -2"
   # Should see your ALB URL!
   ```

3. **Push and redeploy:**
   ```bash
   # Tag and push
   docker tag taskapp-frontend:latest 858448674350.dkr.ecr.us-east-1.amazonaws.com/taskapp-frontend:latest
   docker push 858448674350.dkr.ecr.us-east-1.amazonaws.com/taskapp-frontend:latest
   
   # Force ECS deployment
   aws ecs update-service \
     --cluster taskapp-cluster \
     --service taskapp-frontend-service \
     --force-new-deployment \
     --region us-east-1
   ```

4. **Test in browser:**
   - Open DevTools → Network tab
   - Clear cache or use incognito mode
   - Try registration
   - Verify requests go to ALB URL, not localhost

**Prevention:**
- Always use `--build-arg NEXT_PUBLIC_API_URL=...` when building
- Verify with grep before pushing to ECR
- Document the correct build command in your CI/CD pipeline

### Frontend Shows 502 Bad Gateway

**Cause:** Tasks not running or unhealthy

**Solution:**
1. Check task status: `aws ecs list-tasks --cluster taskapp-cluster --service-name taskapp-frontend-service`
2. Check CloudWatch logs for errors
3. Verify image built correctly with `--build-arg`
4. Check task definition environment variables

### Frontend Loads But API Calls Fail

**Cause:** Path routing not configured correctly OR localhost issue (see above)

**Solution:**
1. **First, check browser DevTools Network tab** - are requests going to localhost or ALB?
2. Verify ALB listener rules:
   - Priority 1: `/api/*` → backend
   - Default: `/*` → frontend
3. Check both target groups have healthy targets
4. Test API endpoint directly: `curl http://ALB/api/`

### Tasks Keep Stopping

**Cause:** Application crash or configuration error

**Check CloudWatch logs:**
```bash
powershell -Command "aws logs filter-log-events --log-group-name /ecs/taskapp-frontend --region us-east-1 --limit 50"
```

**Common issues:**
- Missing environment variables
- Port mismatch (should be 3000)
- Image build failed
- Insufficient memory/CPU

### 404 on Frontend Routes

**Cause:** Next.js routing not working

**Solution:**
- Next.js in `standalone` mode handles routing automatically
- Verify task definition uses correct image
- Check CloudWatch logs for Next.js errors

---

## Phase 6 Verification Checklist

### Infrastructure
- [ ] Frontend Docker image built successfully
- [ ] Frontend image pushed to ECR (latest, v1.0.0)
- [ ] CloudWatch log group created (/ecs/taskapp-frontend)
- [ ] Frontend task definition created (taskapp-frontend:1)
- [ ] Frontend target group created (taskapp-frontend-tg)
- [ ] ALB listener rules configured (path-based routing)
- [ ] Frontend ECS service created (taskapp-frontend-service)

### Deployment
- [ ] Frontend service status: ACTIVE
- [ ] Frontend tasks: 2/2 RUNNING
- [ ] Frontend targets: 2/2 healthy in target group
- [ ] CloudWatch logs showing frontend startup
- [ ] No errors in logs

### Application
- [ ] Frontend homepage loads via ALB
- [ ] Path routing works: / → frontend, /api/ → backend
- [ ] Registration works
- [ ] Login works
- [ ] Dashboard loads after login
- [ ] Projects page works
- [ ] Tasks page works
- [ ] API calls to backend succeed
- [ ] Drag and drop works
- [ ] All CRUD operations functional

### Performance
- [ ] Page load time < 3 seconds
- [ ] API response time < 500ms
- [ ] No console errors in browser
- [ ] Health checks passing consistently

---

## Cost Breakdown (Phase 6)

### Monthly Costs (Estimated)

| Resource | Specification | Monthly Cost |
|----------|--------------|--------------|
| ECS Fargate (Frontend) | 2 tasks × 0.25 vCPU | ~$7.50/month |
| ECS Fargate (Frontend) | 2 tasks × 0.5 GB memory | ~$1.75/month |
| CloudWatch Logs (Frontend) | 1 GB/month | ~$0.50/month |
| Target Group | No additional cost | $0.00 |
| **Total (Frontend Only)** | | **~$9.75/month** |

### Combined Infrastructure (Phases 1-6)

| Component | Monthly Cost |
|-----------|--------------|
| RDS (db.t3.micro) | ~$15.30 |
| ALB | ~$16.20 |
| NAT Gateway | ~$33.00 |
| Backend ECS (2 tasks) | ~$18.00 |
| Frontend ECS (2 tasks) | ~$9.75 |
| CloudWatch Logs | ~$1.00 |
| ECR Storage | <$1.00 |
| **Grand Total** | **~$94/month** |

### Cost Optimization Tips

1. **Reduce task count** from 2 to 1 per service: Save ~$14/month
2. **Stop services when not testing**: Save ~$28/month
3. **Use smaller RDS instance**: Limited options on free tier
4. **Delete NAT Gateway when not deploying**: Save ~$33/month

---

## What's Next?

After completing Phase 6, you'll have:
- ✅ Frontend running on ECS Fargate
- ✅ Backend running on ECS Fargate
- ✅ Single ALB with path-based routing
- ✅ Full application accessible via ALB DNS
- ✅ Production-ready infrastructure

**Phase 7 Preview**: Domain & SSL Configuration
- Register custom domain (Route 53)
- Request SSL certificate (ACM)
- Add HTTPS listener to ALB
- Configure custom domain DNS
- Professional URLs: www.yourdomain.com

Estimated time: 2-3 hours  
Estimated cost: ~$12/year (domain only)

---

## Quick Reference Commands

```bash
# Build and push frontend image
docker build -t taskapp-frontend:latest .
docker tag taskapp-frontend:latest 858448674350.dkr.ecr.us-east-1.amazonaws.com/taskapp-frontend:latest
docker push 858448674350.dkr.ecr.us-east-1.amazonaws.com/taskapp-frontend:latest

# Check frontend service status
aws ecs describe-services --cluster taskapp-cluster --services taskapp-frontend-service --query 'services[0].[serviceName,status,runningCount,desiredCount]' --region us-east-1

# View frontend logs (PowerShell)
powershell -Command "aws logs tail /ecs/taskapp-frontend --follow --region us-east-1"

# Check target health
aws elbv2 describe-target-health --target-group-arn $(aws elbv2 describe-target-groups --names taskapp-frontend-tg --query 'TargetGroups[0].TargetGroupArn' --output text)

# Force new deployment
aws ecs update-service --cluster taskapp-cluster --service taskapp-frontend-service --force-new-deployment --region us-east-1

# Get ALB DNS
aws elbv2 describe-load-balancers --names taskapp-alb --query 'LoadBalancers[0].DNSName' --output text
```

---

## Summary

Phase 6 deploys your frontend to ECS Fargate using the same pattern as the backend:

- **ECS Fargate**: Serverless container orchestration
- **Application Load Balancer**: Path-based routing (`/api/*` vs `/*`)
- **CloudWatch**: Centralized logging
- **High Availability**: 2 frontend tasks, 2 backend tasks

Your full-stack application is now running on AWS with a unified infrastructure!

**Total Phase 6 Time**: 2-3 hours  
**Total Phase 6 Cost**: ~$10/month (frontend tasks)  
**Total Infrastructure Cost**: ~$94/month (all phases)
