# AWS Phase 4: Container Registry (ECR)

## Overview
Set up Amazon Elastic Container Registry (ECR) to store your Docker images. ECR is AWS's managed container registry service that integrates seamlessly with ECS, making it the ideal choice for hosting your application images.

**Timeline**: 1-1.5 hours  
**Cost**: $0.50/month (under 500MB free tier)  
**Prerequisites**: Phase 3 complete (Database ready), Docker images built locally or in GHCR

---

## What You'll Create

1. **ECR Repository for Backend**: Store backend API Docker images
2. **ECR Repository for Frontend**: Store Next.js frontend Docker images
3. **Docker Image Tags**: Push versioned and latest images
4. **Image Scanning**: Enable vulnerability scanning (optional)

---

## Architecture Overview

```
Your Local Machine / GHCR
        ↓
    AWS ECR (us-east-1)
        ├── taskapp-backend:latest
        ├── taskapp-backend:v1.0.0
        ├── taskapp-frontend:latest
        └── taskapp-frontend:v1.0.0
        ↓
    ECS Fargate (Phase 5)
```

---

## Step 1: Create ECR Repository for Backend

### AWS Console Method

1. **Navigate to ECR**
   - Open AWS Console
   - Search for "ECR" and click "Elastic Container Registry"

2. **Create Repository**
   - Click "Get started" (if first time) or "Create repository"
   - Repository name: `taskapp-backend`
   - Visibility: **Private**
   - Tag immutability: **Disabled** (allows overwriting tags)
   - Image scan on push: **Enabled** (optional, recommended)
   - KMS encryption: **Disabled** (not needed for dev)

3. **Create**
   - Click "Create repository"
   - Wait for status: "Active"

### AWS CLI Method

```bash
# Create backend repository
aws ecr create-repository \
  --repository-name taskapp-backend \
  --image-scanning-configuration scanOnPush=true \
  --region us-east-1 \
  --tags Key=Project,Value=TaskManagementApp Key=Component,Value=Backend

# Verify creation
aws ecr describe-repositories \
  --repository-names taskapp-backend \
  --region us-east-1
```

**Output**: Copy the `repositoryUri` - looks like: `858448674350.dkr.ecr.us-east-1.amazonaws.com/taskapp-backend`

---

## Step 2: Create ECR Repository for Frontend

### AWS Console Method

1. **Create Second Repository**
   - Click "Create repository" again
   - Repository name: `taskapp-frontend`
   - Visibility: **Private**
   - Tag immutability: **Disabled**
   - Image scan on push: **Enabled**
   - KMS encryption: **Disabled**

2. **Create**
   - Click "Create repository"

### AWS CLI Method

```bash
# Create frontend repository
aws ecr create-repository \
  --repository-name taskapp-frontend \
  --image-scanning-configuration scanOnPush=true \
  --region us-east-1 \
  --tags Key=Project,Value=TaskManagementApp Key=Component,Value=Frontend

# Verify creation
aws ecr describe-repositories \
  --repository-names taskapp-frontend \
  --region us-east-1
```

**Output**: Copy the `repositoryUri` - looks like: `858448674350.dkr.ecr.us-east-1.amazonaws.com/taskapp-frontend`

---

## Step 3: Get ECR Repository URIs

You'll need these URIs for tagging and pushing images.

### AWS Console Method

1. **View Repositories**
   - In ECR console, you'll see both repositories listed
   - Click on `taskapp-backend`
   - Copy the "URI" field

2. **Repeat for Frontend**
   - Go back and click `taskapp-frontend`
   - Copy the "URI" field

### AWS CLI Method

```bash
# Get both repository URIs
aws ecr describe-repositories \
  --repository-names taskapp-backend taskapp-frontend \
  --region us-east-1 \
  --query 'repositories[*].[repositoryName,repositoryUri]' \
  --output table
```

**Save these URIs** - you'll use them frequently:
```
Backend URI:  858448674350.dkr.ecr.us-east-1.amazonaws.com/taskapp-backend
Frontend URI: 858448674350.dkr.ecr.us-east-1.amazonaws.com/taskapp-frontend
```

---

## Step 4: Authenticate Docker to ECR

Before pushing images, Docker needs to authenticate with ECR.

### Get Login Credentials

```bash
# Get ECR login token and authenticate Docker
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin 858448674350.dkr.ecr.us-east-1.amazonaws.com
```

**Expected output**: `Login Succeeded`

**Note**: This authentication is temporary (12 hours). You'll need to re-authenticate if it expires.

---

## Step 5: Prepare Docker Images

You have two options: build locally or pull from GitHub Container Registry.

### Option A: Build Images Locally (Recommended)

#### Build Backend Image

```bash
# Navigate to project root
cd /c/Users/vokeo/OneDrive/Desktop/task-management-app

# Build backend image
docker build -t taskapp-backend:latest ./backend

# Verify image created
docker images | grep taskapp-backend
```

#### Build Frontend Image

**Important**: Update the API URL environment variable for AWS deployment.

1. **Check current configuration**
   ```bash
   cat frontend/next.config.js
   ```

2. **Build frontend**
   ```bash
   # Build with production API URL (we'll update this in Phase 5)
   docker build -t taskapp-frontend:latest ./frontend

   # Verify image created
   docker images | grep taskapp-frontend
   ```

### Option B: Pull from GHCR

If you already pushed images to GitHub Container Registry during CI/CD phase:

```bash
# Pull backend from GHCR
docker pull ghcr.io/vee-kay8/task-management-app-backend:latest

# Tag for local use
docker tag ghcr.io/vee-kay8/task-management-app-backend:latest taskapp-backend:latest

# Pull frontend from GHCR
docker pull ghcr.io/vee-kay8/task-management-app-frontend:latest

# Tag for local use
docker tag ghcr.io/vee-kay8/task-management-app-frontend:latest taskapp-frontend:latest

# Verify images
docker images | grep taskapp
```

---

## Step 6: Tag Images for ECR

Tag your local images with the ECR repository URIs.

```bash
# Set variables (replace with your actual account ID)
ACCOUNT_ID=858448674350
REGION=us-east-1
BACKEND_REPO=${ACCOUNT_ID}.dkr.ecr.${REGION}.amazonaws.com/taskapp-backend
FRONTEND_REPO=${ACCOUNT_ID}.dkr.ecr.${REGION}.amazonaws.com/taskapp-frontend

# Tag backend image (latest and versioned)
docker tag taskapp-backend:latest ${BACKEND_REPO}:latest
docker tag taskapp-backend:latest ${BACKEND_REPO}:v1.0.0

# Tag frontend image (latest and versioned)
docker tag taskapp-frontend:latest ${FRONTEND_REPO}:latest
docker tag taskapp-frontend:latest ${FRONTEND_REPO}:v1.0.0

# Verify tags
docker images | grep ecr
```

**Expected output**: You should see 4 new images with ECR URIs

---

## Step 7: Push Images to ECR

### Push Backend Images

```bash
# Push backend:latest
docker push ${BACKEND_REPO}:latest

# Push backend:v1.0.0
docker push ${BACKEND_REPO}:v1.0.0
```

**Progress**: You'll see layers being pushed. First push takes 2-5 minutes depending on image size and connection speed.

### Push Frontend Images

```bash
# Push frontend:latest
docker push ${FRONTEND_REPO}:latest

# Push frontend:v1.0.0
docker push ${FRONTEND_REPO}:v1.0.0
```

**Progress**: Similar to backend, 2-5 minutes per push.

---

## Step 8: Verify Images in ECR

### AWS Console Method

1. **Navigate to ECR**
   - Go to ECR console
   - Click on `taskapp-backend`
   - You should see 2 images: `latest` and `v1.0.0`
   - Note the image size and pushed time

2. **Check Frontend**
   - Go back and click `taskapp-frontend`
   - You should see 2 images: `latest` and `v1.0.0`

3. **View Image Details**
   - Click on an image tag
   - View vulnerability scan results (if enabled)
   - Check image layers

### AWS CLI Method

```bash
# List backend images
aws ecr list-images \
  --repository-name taskapp-backend \
  --region us-east-1

# List frontend images
aws ecr list-images \
  --repository-name taskapp-frontend \
  --region us-east-1

# Get detailed image info (backend)
aws ecr describe-images \
  --repository-name taskapp-backend \
  --region us-east-1 \
  --output table

# Get detailed image info (frontend)
aws ecr describe-images \
  --repository-name taskapp-frontend \
  --region us-east-1 \
  --output table
```

---

## Step 9: Check Image Scan Results (Optional)

If you enabled image scanning on push, check for vulnerabilities.

### AWS Console Method

1. **View Scan Results**
   - In ECR repository, click on an image
   - Click "Scan results" tab
   - Review findings (Critical, High, Medium, Low, Informational)

2. **Interpret Results**
   - Critical/High: Should fix before production
   - Medium: Review and assess
   - Low/Informational: Awareness only

### AWS CLI Method

```bash
# Get scan findings for backend
aws ecr describe-image-scan-findings \
  --repository-name taskapp-backend \
  --image-id imageTag=latest \
  --region us-east-1

# Get scan findings for frontend
aws ecr describe-image-scan-findings \
  --repository-name taskapp-frontend \
  --image-id imageTag=latest \
  --region us-east-1
```

**Note**: First scan takes 5-10 minutes. If you see "SCAN_IN_PROGRESS", wait and retry.

---

## Step 10: Update AWS Resources Documentation

Document your ECR repository URIs for future reference.

```bash
# Information to add to aws-resources.md:
# - Backend ECR Repository: taskapp-backend
# - Backend URI: 858448674350.dkr.ecr.us-east-1.amazonaws.com/taskapp-backend
# - Frontend ECR Repository: taskapp-frontend  
# - Frontend URI: 858448674350.dkr.ecr.us-east-1.amazonaws.com/taskapp-frontend
# - Images: latest, v1.0.0
```

---

## Phase 4 Verification Checklist

Use this checklist to verify Phase 4 completion:

### ECR Repositories
- [ ] Backend repository created (taskapp-backend)
- [ ] Frontend repository created (taskapp-frontend)
- [ ] Both repositories are private
- [ ] Image scanning enabled on both repositories
- [ ] Repositories visible in ECR console

### Docker Authentication
- [ ] Docker authenticated to ECR successfully
- [ ] Login command executed without errors
- [ ] Can push images to ECR

### Docker Images
- [ ] Backend image built or pulled
- [ ] Frontend image built or pulled
- [ ] Images tagged with ECR repository URIs
- [ ] Both `latest` and `v1.0.0` tags created
- [ ] Images visible in local Docker (`docker images`)

### Image Push
- [ ] Backend:latest pushed to ECR
- [ ] Backend:v1.0.0 pushed to ECR
- [ ] Frontend:latest pushed to ECR
- [ ] Frontend:v1.0.0 pushed to ECR
- [ ] All 4 images visible in ECR console

### Image Verification
- [ ] Backend images listed in ECR
- [ ] Frontend images listed in ECR
- [ ] Image sizes reasonable (backend: ~180MB, frontend: ~150MB)
- [ ] Image scan completed (if enabled)
- [ ] No critical vulnerabilities (or documented if present)

### Documentation
- [ ] ECR repository URIs saved
- [ ] Image tags documented
- [ ] aws-resources.md updated with ECR info
- [ ] Repository names saved for ECS task definitions

---

## Troubleshooting

### Docker Login Fails

**Issue**: `Error response from daemon: Get "https://...": unauthorized`

**Solutions**:
```bash
# 1. Verify AWS credentials are configured
aws sts get-caller-identity

# 2. Re-authenticate to ECR
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin 858448674350.dkr.ecr.us-east-1.amazonaws.com

# 3. Check AWS CLI version (needs v2.x)
aws --version

# 4. Verify region matches repository region
echo $AWS_REGION
```

### Image Push Fails

**Issue**: `denied: User: ... is not authorized to perform: ecr:InitiateLayerUpload`

**Solutions**:
```bash
# 1. Verify IAM permissions
aws ecr describe-repositories --repository-names taskapp-backend

# 2. Check repository exists
aws ecr list-repositories

# 3. Verify authentication
docker login --username AWS --password-stdin 858448674350.dkr.ecr.us-east-1.amazonaws.com

# 4. Check IAM policy includes ecr:* permissions
aws iam list-attached-user-policies --user-name taskapp-admin
```

### Image Tag Mismatch

**Issue**: Tagged image doesn't appear in ECR after push

**Solutions**:
```bash
# 1. List local images with ECR tags
docker images | grep ecr

# 2. Verify tag format (must include full URI)
docker images --format "{{.Repository}}:{{.Tag}}" | grep taskapp

# 3. Re-tag if needed
docker tag taskapp-backend:latest ${BACKEND_REPO}:latest

# 4. Push again
docker push ${BACKEND_REPO}:latest
```

### Large Image Size

**Issue**: Images are larger than expected, increasing costs

**Solutions**:
```bash
# 1. Check actual sizes
docker images --format "table {{.Repository}}\t{{.Tag}}\t{{.Size}}" | grep taskapp

# 2. Review Dockerfile for optimization opportunities
cat backend/Dockerfile

# 3. Use multi-stage builds (already implemented)
# 4. Remove unnecessary files from final stage
# 5. Consider using smaller base images (alpine)

# 6. Clean up unused layers
docker system prune -a
```

### Repository Not Found

**Issue**: `RepositoryNotFoundException` when pushing

**Solutions**:
```bash
# 1. Verify repository exists
aws ecr describe-repositories --region us-east-1

# 2. Check repository name matches exactly
aws ecr list-repositories --region us-east-1

# 3. Recreate repository if deleted
aws ecr create-repository --repository-name taskapp-backend --region us-east-1

# 4. Verify region matches
aws configure get region
```

### Scan Takes Too Long

**Issue**: Image scan status stuck at "SCAN_IN_PROGRESS"

**Solutions**:
```bash
# 1. Wait 10-15 minutes (large images take longer)
# 2. Check scan status
aws ecr describe-image-scan-findings \
  --repository-name taskapp-backend \
  --image-id imageTag=latest

# 3. Manually trigger scan if needed
aws ecr start-image-scan \
  --repository-name taskapp-backend \
  --image-id imageTag=latest

# 4. Disable scanning if not needed
aws ecr put-image-scanning-configuration \
  --repository-name taskapp-backend \
  --image-scanning-configuration scanOnPush=false
```

---

## Cost Breakdown

### Monthly Costs (Estimated)

| Resource | Usage | Monthly Cost |
|----------|-------|--------------|
| ECR Storage | First 500 MB | Free |
| ECR Storage | Additional per GB | $0.10/GB |
| Data Transfer | To ECS (same region) | Free |
| Data Transfer | Out to internet | $0.09/GB |
| Image Scanning | First 100 scans | Free |
| Image Scanning | Additional scans | $0.09/scan |

### Current Estimate

Assuming:
- Backend image: ~180MB
- Frontend image: ~150MB
- Total: ~330MB
- 2 versions each (latest + v1.0.0)
- Total storage: ~660MB

**Cost**: ~$0.02/month (660MB - 500MB free = 160MB × $0.10/GB)

### Cost Optimization Tips

1. **Clean Up Old Images**
   ```bash
   # Delete old image versions
   aws ecr batch-delete-image \
     --repository-name taskapp-backend \
     --image-ids imageTag=old-tag
   ```

2. **Set Lifecycle Policies**
   ```bash
   # Keep only last 5 images
   cat > lifecycle-policy.json << 'EOF'
   {
     "rules": [
       {
         "rulePriority": 1,
         "description": "Keep last 5 images",
         "selection": {
           "tagStatus": "any",
           "countType": "imageCountMoreThan",
           "countNumber": 5
         },
         "action": {
           "type": "expire"
         }
       }
     ]
   }
   EOF

   aws ecr put-lifecycle-policy \
     --repository-name taskapp-backend \
     --lifecycle-policy-text file://lifecycle-policy.json
   ```

3. **Disable Scanning for Dev Images**
   - Only scan production images
   - Reduces scan costs
   - Faster push times

---

## What's Next?

After completing Phase 4, you'll have:
- ✅ ECR repositories for backend and frontend
- ✅ Docker images stored in AWS
- ✅ Versioned image tags (latest + v1.0.0)
- ✅ Images ready for ECS deployment

**Phase 5 Preview**: ECS Fargate - Backend Deployment
- Create ECS cluster (serverless Fargate)
- Define backend task definition (CPU, memory, env vars)
- Create Application Load Balancer (ALB)
- Configure target groups and health checks
- Deploy backend service with 2 tasks
- Connect to RDS database
- Test API endpoints via ALB

Estimated time: 3-4 hours  
Estimated cost: ~$20-25/month (ALB + Fargate)

---

## Quick Reference Commands

```bash
# Authenticate to ECR
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin 858448674350.dkr.ecr.us-east-1.amazonaws.com

# Build images
docker build -t taskapp-backend:latest ./backend
docker build -t taskapp-frontend:latest ./frontend

# Tag images for ECR
ACCOUNT_ID=858448674350
REGION=us-east-1
docker tag taskapp-backend:latest ${ACCOUNT_ID}.dkr.ecr.${REGION}.amazonaws.com/taskapp-backend:latest
docker tag taskapp-frontend:latest ${ACCOUNT_ID}.dkr.ecr.${REGION}.amazonaws.com/taskapp-frontend:latest

# Push images
docker push ${ACCOUNT_ID}.dkr.ecr.${REGION}.amazonaws.com/taskapp-backend:latest
docker push ${ACCOUNT_ID}.dkr.ecr.${REGION}.amazonaws.com/taskapp-frontend:latest

# List images in ECR
aws ecr list-images --repository-name taskapp-backend
aws ecr list-images --repository-name taskapp-frontend

# Get repository URIs
aws ecr describe-repositories \
  --repository-names taskapp-backend taskapp-frontend \
  --query 'repositories[*].[repositoryName,repositoryUri]' \
  --output table

# Clean up (delete repositories - WARNING: destructive)
aws ecr delete-repository --repository-name taskapp-backend --force
aws ecr delete-repository --repository-name taskapp-frontend --force
```

---

## Summary

Phase 4 sets up your container registry infrastructure on AWS. ECR provides:

- **Secure Storage**: Private repositories with IAM-based access control
- **Integration**: Seamless integration with ECS Fargate
- **Scanning**: Automated vulnerability detection
- **Reliability**: Highly available, managed service
- **Cost-Effective**: Free tier covers small projects

The images you push in this phase will be deployed to ECS in Phase 5, forming the runtime environment for your application.

**Total Phase 4 Time**: ~1-1.5 hours  
**Total Phase 4 Cost**: ~$0.02-0.50/month
