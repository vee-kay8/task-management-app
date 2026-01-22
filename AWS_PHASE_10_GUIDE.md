# Phase 10: CI/CD Pipeline Integration - Complete Guide

**Objective**: Automate deployments to AWS ECS using GitHub Actions
**Timeline**: 2-3 hours
**Prerequisites**: Phases 1-9 complete, GitHub repository with code

---

## Overview

This phase sets up automated CI/CD pipelines that will:
- Build Docker images on every push to main branch
- Push images to ECR automatically
- Update ECS task definitions
- Deploy to ECS services with zero downtime
- Run tests before deployment

---

## Architecture

```
GitHub Push → GitHub Actions → Build Images → Push to ECR → Update ECS Task Definitions → Deploy to ECS
```

---

## Phase 10 Checklist

### Part 1: AWS IAM Setup (30 minutes)
- [ ] Create IAM user for GitHub Actions
- [ ] Create custom IAM policy for deployments
- [ ] Attach policy to user
- [ ] Generate access keys
- [ ] Store access keys securely
- [ ] Test IAM credentials locally

### Part 2: GitHub Secrets Configuration (15 minutes)
- [ ] Add AWS_ACCESS_KEY_ID to GitHub Secrets
- [ ] Add AWS_SECRET_ACCESS_KEY to GitHub Secrets
- [ ] Add AWS_REGION to GitHub Secrets
- [ ] Add ECR_BACKEND_REPOSITORY to GitHub Secrets
- [ ] Add ECR_FRONTEND_REPOSITORY to GitHub Secrets
- [ ] Add ECS_CLUSTER to GitHub Secrets
- [ ] Add ECS_BACKEND_SERVICE to GitHub Secrets
- [ ] Add ECS_FRONTEND_SERVICE to GitHub Secrets
- [ ] Add DATABASE_URL to GitHub Secrets
- [ ] Add SECRET_KEY to GitHub Secrets
- [ ] Add JWT_SECRET_KEY to GitHub Secrets

### Part 3: GitHub Actions Workflows (45 minutes)
- [ ] Create .github/workflows directory
- [ ] Create backend deployment workflow
- [ ] Create frontend deployment workflow
- [ ] Configure workflow triggers
- [ ] Add build and test jobs
- [ ] Add Docker build steps
- [ ] Add ECR push steps
- [ ] Add ECS deployment steps
- [ ] Test workflows with a commit

### Part 4: Testing & Validation (30 minutes)
- [ ] Make a test change to backend
- [ ] Push and verify backend deployment
- [ ] Make a test change to frontend
- [ ] Push and verify frontend deployment
- [ ] Check ECS task updates
- [ ] Verify application still works
- [ ] Test rollback if needed
- [ ] Document the CI/CD process

---

## Step-by-Step Guide

### Part 1: AWS IAM Setup

#### Step 1.1: Create IAM User

**Method 1: AWS Console (Recommended for Beginners)**

1. Sign in to AWS Console: https://console.aws.amazon.com
2. Navigate to **IAM** service (search "IAM" in top search bar)
3. In left sidebar, click **Users**
4. Click **Create user** button (top right)
5. User name: `github-actions-ecs-deployer`
6. **Important**: DO NOT check "Provide user access to AWS Management Console" (this is a programmatic user)
7. Click **Next** button
8. You'll see "Set permissions" page - click **Next** (we'll attach policy in next step)
9. Click **Create user**
10. You should see success message with user details

**Method 2: AWS CLI**

```bash
# Create IAM user for GitHub Actions
aws iam create-user --user-name github-actions-ecs-deployer

# Output will show user ARN
```

#### Step 1.2: Create IAM Policy

**Method 1: AWS Console (Recommended)**

1. In IAM Console, click **Policies** in left sidebar
2. Click **Create policy** button
3. Click **JSON** tab (top of editor)
4. Delete the default policy content
5. Copy and paste the policy below
6. Click **Next** button
7. Policy name: `GitHubActionsECSDeployPolicy`
8. Description (optional): `Allows GitHub Actions to deploy to ECS`
9. Click **Create policy**
10. You should see success message - note the policy name

**Method 2: AWS CLI**

First, create a file `github-actions-policy.json`:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "ECRAccess",
      "Effect": "Allow",
      "Action": [
        "ecr:GetAuthorizationToken",
        "ecr:BatchCheckLayerAvailability",
        "ecr:GetDownloadUrlForLayer",
        "ecr:BatchGetImage",
        "ecr:PutImage",
        "ecr:InitiateLayerUpload",
        "ecr:UploadLayerPart",
        "ecr:CompleteLayerUpload"
      ],
      "Resource": "*"
    },
    {
      "Sid": "ECSAccess",
      "Effect": "Allow",
      "Action": [
        "ecs:DescribeServices",
        "ecs:DescribeTaskDefinition",
        "ecs:DescribeTasks",
        "ecs:ListTasks",
        "ecs:RegisterTaskDefinition",
        "ecs:UpdateService"
      ],
      "Resource": "*"
    },
    {
      "Sid": "IAMPassRole",
      "Effect": "Allow",
      "Action": "iam:PassRole",
      "Resource": "arn:aws:iam::858448674350:role/ecsTaskExecutionRole"
    },
    {
      "Sid": "CloudWatchLogs",
      "Effect": "Allow",
      "Action": [
        "logs:CreateLogGroup",
        "logs:CreateLogStream",
        "logs:PutLogEvents"
      ],
      "Resource": "*"
    }
  ]
}
```

Create the policy:

```bash
aws iam create-policy \
  --policy-name GitHubActionsECSDeployPolicy \
  --policy-document file://github-actions-policy.json

# Output will show policy ARN - SAVE THIS!
# Example: arn:aws:iam::858448674350:policy/GitHubActionsECSDeployPolicy
```

#### Step 1.3: Attach Policy to User

**Method 1: AWS Console**

1. In IAM Console, click **Users** in left sidebar
2. Click on `github-actions-ecs-deployer` user
3. Click **Permissions** tab
4. Click **Add permissions** button → **Attach policies directly**
5. In search box, type: `GitHubActionsECSDeployPolicy`
6. Check the box next to your policy
7. Click **Add permissions** button
8. You should see the policy listed under "Permissions policies"

**Method 2: AWS CLI**

```bash
# Replace with your actual policy ARN from step 1.2
aws iam attach-user-policy \
  --user-name github-actions-ecs-deployer \
  --policy-arn arn:aws:iam::858448674350:policy/GitHubActionsECSDeployPolicy
```

#### Step 1.4: Create Access Keys

**Method 1: AWS Console (Easiest to Copy/Paste)**

1. Still on the `github-actions-ecs-deployer` user page
2. Click **Security credentials** tab
3. Scroll down to **Access keys** section
4. Click **Create access key** button
5. Select use case: **Third-party service** or **Other**
6. Check the confirmation box
7. Click **Next**
8. Description (optional): `GitHub Actions ECS Deployment`
9. Click **Create access key**
10. **⚠️ CRITICAL STEP**: You'll see a success page with:
    - **Access key ID**: `AKIA...` (visible)
    - **Secret access key**: `wJal...` (visible ONLY NOW)
11. **DO THIS NOW**:
    - Click **Download .csv file** button (saves both keys)
    - OR copy both values to a secure text file
    - OR leave this browser tab open while you add secrets to GitHub
12. Click **Done** when you've saved the keys
13. **Warning**: You CANNOT view the secret key again after closing this page!

**Method 2: AWS CLI**

```bash
aws iam create-access-key --user-name github-actions-ecs-deployer

# Output will show:
# - AccessKeyId: AKIAXXXXXXXXXXXXXXXX
# - SecretAccessKey: xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
# 
# SAVE THESE IMMEDIATELY! You cannot retrieve the secret key again.
```

**⚠️ CRITICAL**: Save both the Access Key ID and Secret Access Key. You'll need them for GitHub Secrets in the next section.

#### Step 1.5: Test IAM Credentials (Optional)

```bash
# Configure AWS CLI with new credentials temporarily
export AWS_ACCESS_KEY_ID=AKIAXXXXXXXXXXXXXXXX
export AWS_SECRET_ACCESS_KEY=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx

# Test ECR access
aws ecr describe-repositories --region us-east-1

# Test ECS access
aws ecs describe-services \
  --cluster taskapp-cluster \
  --services taskapp-backend-service \
  --region us-east-1

# If both work, credentials are correct!
# Unset the test credentials
unset AWS_ACCESS_KEY_ID
unset AWS_SECRET_ACCESS_KEY
```

---

### Part 2: GitHub Secrets Configuration

#### Step 2.1: Navigate to GitHub Repository Settings

**Detailed Browser Steps:**

1. Open browser and go to: https://github.com/vee-kay8/task-management-app
2. Sign in to GitHub if prompted
3. You should see your repository page
4. Click the **Settings** tab (rightmost tab in navigation bar)
   - If you don't see Settings, you may not have admin access to the repo
5. In left sidebar, scroll down to **Security** section
6. Click **Secrets and variables** to expand it
7. Click **Actions** under it
8. You should now see "Actions secrets and variables" page
9. You'll see tabs: "Secrets" and "Variables" - stay on **Secrets** tab

#### Step 2.2: Add Required Secrets (11 Total)

**How to Add Each Secret:**

For each of the 11 secrets below, repeat these steps:

1. Click green **New repository secret** button (top right)
2. **Name** field: Type the exact name (e.g., `AWS_ACCESS_KEY_ID`)
3. **Secret** field: Paste the value (be careful - no extra spaces!)
4. Click **Add secret** button
5. You'll return to the secrets list - the new secret will appear
6. Repeat for next secret

**Secret #1:**
```
Name: AWS_ACCESS_KEY_ID
Value: [Paste the Access Key ID from AWS Console - starts with AKIA]
```

**Secret #2:**
```
Name: AWS_SECRET_ACCESS_KEY
Value: [Paste the Secret Access Key from AWS Console - long random string]
```

**Secret #3:**
```
Name: AWS_REGION
Value: us-east-1
```

**Secret #4:**
```
Name: ECR_BACKEND_REPOSITORY
Value: taskapp-backend
```

**Secret #5:**
```
Name: ECR_FRONTEND_REPOSITORY
Value: taskapp-frontend
```

**Secret #6:**
```
Name: ECS_CLUSTER
Value: taskapp-cluster
```

**Secret #7:**
```
Name: ECS_BACKEND_SERVICE
Value: taskapp-backend-service
```

**Secret #8:**
```
Name: ECS_FRONTEND_SERVICE
Value: taskapp-frontend-service
```

**Secret #9:**
```
Name: DATABASE_URL
Value: postgresql://postgres:YourSecurePassword123!@taskapp-db.cqaewjp43tdm.us-east-1.rds.amazonaws.com:5432/taskmanagement
```

**Secret #10:**
```
Name: SECRET_KEY
Value: FaKgFvIjFU3tz6bAugmkRw6CQfoaJuqAbJe/PYlyyu0=
```

**Secret #11:**
```
Name: JWT_SECRET_KEY
Value: IB8fu3yhS/mPgIRmP6CsBab//X7Hnm+VggOHqXnB/F4=
```

**Complete List for Reference:**

Add these secrets one by one:

| Secret Name | Value | Example |
|-------------|-------|---------|
| `AWS_ACCESS_KEY_ID` | From Step 1.4 | `AKIAIOSFODNN7EXAMPLE` |
| `AWS_SECRET_ACCESS_KEY` | From Step 1.4 | `wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY` |
| `AWS_REGION` | Your region | `us-east-1` |
| `ECR_BACKEND_REPOSITORY` | Backend repo name | `taskapp-backend` |
| `ECR_FRONTEND_REPOSITORY` | Frontend repo name | `taskapp-frontend` |
| `ECS_CLUSTER` | Cluster name | `taskapp-cluster` |
| `ECS_BACKEND_SERVICE` | Backend service | `taskapp-backend-service` |
| `ECS_FRONTEND_SERVICE` | Frontend service | `taskapp-frontend-service` |
| `DATABASE_URL` | RDS connection | `postgresql://postgres:YourSecurePassword123!@taskapp-db.cqaewjp43tdm.us-east-1.rds.amazonaws.com:5432/taskmanagement` |
| `SECRET_KEY` | Flask secret | `FaKgFvIjFU3tz6bAugmkRw6CQfoaJuqAbJe/PYlyyu0=` |
| `JWT_SECRET_KEY` | JWT secret | `IB8fu3yhS/mPgIRmP6CsBab//X7Hnm+VggOHqXnB/F4=` |

**Note**: Use the actual values from your deployment. Check your ECS task definitions for the current environment variable values.

#### Step 2.3: Verify Secrets Added

**How to Verify:**

1. On the "Actions secrets" page, you should see 11 secrets listed
2. Each secret shows:
   - Name (visible)
   - Last updated timestamp
   - Update/Remove buttons
3. **Note**: You CANNOT view the actual secret values (security feature)
4. If you need to change a value, click **Update** and paste new value
5. Count the secrets - should be exactly 11

**Checklist - Verify These 11 Secrets Exist:**
- [ ] AWS_ACCESS_KEY_ID
- [ ] AWS_SECRET_ACCESS_KEY  
- [ ] AWS_REGION
- [ ] ECR_BACKEND_REPOSITORY
- [ ] ECR_FRONTEND_REPOSITORY
- [ ] ECS_CLUSTER
- [ ] ECS_BACKEND_SERVICE
- [ ] ECS_FRONTEND_SERVICE
- [ ] DATABASE_URL
- [ ] SECRET_KEY
- [ ] JWT_SECRET_KEY

✅ If you see all 11, you're ready for the next step!

---

### Part 3: GitHub Actions Workflows

#### Step 3.1: Create Workflow Directory

**Method 1: VS Code (Visual)**

1. Open VS Code
2. Open folder: `C:/Users/vokeo/OneDrive/Desktop/task-management-app`
3. In Explorer sidebar (left), right-click in empty space
4. Select **New Folder**
5. Name it: `.github` (include the dot)
6. Right-click on `.github` folder
7. Select **New Folder**
8. Name it: `workflows`
9. You should now have `.github/workflows/` in your project

**Method 2: PowerShell**

```powershell
cd C:/Users/vokeo/OneDrive/Desktop/task-management-app

# Create nested directories
New-Item -ItemType Directory -Force -Path .github/workflows
```

**Method 3: Git Bash/Terminal**

```bash
cd C:/Users/vokeo/OneDrive/Desktop/task-management-app

# Create .github/workflows directory
mkdir -p .github/workflows
```

#### Step 3.2: Create Backend Deployment Workflow

**Method 1: VS Code (Recommended)**

1. In VS Code Explorer, navigate to `.github/workflows/` folder
2. Right-click on `workflows` folder
3. Select **New File**
4. Name: `deploy-backend.yml`
5. Press Enter - file opens in editor
6. Copy the YAML content below
7. Paste into the file (Ctrl+V)
8. Save (Ctrl+S)

**Method 2: Command Line**

```bash
# Create the file
touch .github/workflows/deploy-backend.yml

# Open in your editor and paste content
code .github/workflows/deploy-backend.yml
```

**File Content - Copy This:**

Create `.github/workflows/deploy-backend.yml` with this content:

```yaml
name: Deploy Backend to ECS

on:
  push:
    branches:
      - main
      - Cloud-Deployment
    paths:
      - 'backend/**'
      - '.github/workflows/deploy-backend.yml'

env:
  AWS_REGION: ${{ secrets.AWS_REGION }}
  ECR_REPOSITORY: ${{ secrets.ECR_BACKEND_REPOSITORY }}
  ECS_SERVICE: ${{ secrets.ECS_BACKEND_SERVICE }}
  ECS_CLUSTER: ${{ secrets.ECS_CLUSTER }}
  ECS_TASK_DEFINITION: taskapp-backend
  CONTAINER_NAME: backend

jobs:
  deploy:
    name: Deploy Backend
    runs-on: ubuntu-latest
    
    steps:
    - name: Checkout code
      uses: actions/checkout@v4

    - name: Configure AWS credentials
      uses: aws-actions/configure-aws-credentials@v4
      with:
        aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
        aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
        aws-region: ${{ env.AWS_REGION }}

    - name: Login to Amazon ECR
      id: login-ecr
      uses: aws-actions/amazon-ecr-login@v2

    - name: Build, tag, and push image to Amazon ECR
      id: build-image
      env:
        ECR_REGISTRY: ${{ steps.login-ecr.outputs.registry }}
        IMAGE_TAG: ${{ github.sha }}
      run: |
        cd backend
        docker build -t $ECR_REGISTRY/$ECR_REPOSITORY:$IMAGE_TAG .
        docker tag $ECR_REGISTRY/$ECR_REPOSITORY:$IMAGE_TAG $ECR_REGISTRY/$ECR_REPOSITORY:latest
        docker push $ECR_REGISTRY/$ECR_REPOSITORY:$IMAGE_TAG
        docker push $ECR_REGISTRY/$ECR_REPOSITORY:latest
        echo "image=$ECR_REGISTRY/$ECR_REPOSITORY:$IMAGE_TAG" >> $GITHUB_OUTPUT

    - name: Download current task definition
      run: |
        aws ecs describe-task-definition \
          --task-definition ${{ env.ECS_TASK_DEFINITION }} \
          --query taskDefinition > task-definition.json

    - name: Fill in the new image ID in the Amazon ECS task definition
      id: task-def
      uses: aws-actions/amazon-ecs-render-task-definition@v1
      with:
        task-definition: task-definition.json
        container-name: ${{ env.CONTAINER_NAME }}
        image: ${{ steps.build-image.outputs.image }}
        environment-variables: |
          DATABASE_URL=${{ secrets.DATABASE_URL }}
          FLASK_ENV=production
          SECRET_KEY=${{ secrets.SECRET_KEY }}
          JWT_SECRET_KEY=${{ secrets.JWT_SECRET_KEY }}
          JWT_ACCESS_TOKEN_EXPIRES=24
          CORS_ORIGINS=*
          DEBUG=False

    - name: Deploy Amazon ECS task definition
      uses: aws-actions/amazon-ecs-deploy-task-definition@v1
      with:
        task-definition: ${{ steps.task-def.outputs.task-definition }}
        service: ${{ env.ECS_SERVICE }}
        cluster: ${{ env.ECS_CLUSTER }}
        wait-for-service-stability: true

    - name: Deployment summary
      run: |
        echo "✅ Backend deployed successfully!"
        echo "Image: ${{ steps.build-image.outputs.image }}"
        echo "Service: ${{ env.ECS_SERVICE }}"
        echo "Cluster: ${{ env.ECS_CLUSTER }}"
```

#### Step 3.3: Create Frontend Deployment Workflow

**Method 1: VS Code**

1. In VS Code Explorer, right-click on `.github/workflows/` folder
2. Select **New File**
3. Name: `deploy-frontend.yml`
4. Copy the YAML content below
5. Paste and save (Ctrl+S)

**Method 2: Command Line**

```bash
touch .github/workflows/deploy-frontend.yml
code .github/workflows/deploy-frontend.yml
```

**File Content - Copy This:**

Create `.github/workflows/deploy-frontend.yml` with this content:

```yaml
name: Deploy Frontend to ECS

on:
  push:
    branches:
      - main
      - Cloud-Deployment
    paths:
      - 'frontend/**'
      - '.github/workflows/deploy-frontend.yml'

env:
  AWS_REGION: ${{ secrets.AWS_REGION }}
  ECR_REPOSITORY: ${{ secrets.ECR_FRONTEND_REPOSITORY }}
  ECS_SERVICE: ${{ secrets.ECS_FRONTEND_SERVICE }}
  ECS_CLUSTER: ${{ secrets.ECS_CLUSTER }}
  ECS_TASK_DEFINITION: taskapp-frontend
  CONTAINER_NAME: frontend

jobs:
  deploy:
    name: Deploy Frontend
    runs-on: ubuntu-latest
    
    steps:
    - name: Checkout code
      uses: actions/checkout@v4

    - name: Configure AWS credentials
      uses: aws-actions/configure-aws-credentials@v4
      with:
        aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
        aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
        aws-region: ${{ env.AWS_REGION }}

    - name: Login to Amazon ECR
      id: login-ecr
      uses: aws-actions/amazon-ecr-login@v2

    - name: Build, tag, and push image to Amazon ECR
      id: build-image
      env:
        ECR_REGISTRY: ${{ steps.login-ecr.outputs.registry }}
        IMAGE_TAG: ${{ github.sha }}
      run: |
        cd frontend
        docker build \
          --build-arg NEXT_PUBLIC_API_URL=https://app.techveesolutions.com \
          -t $ECR_REGISTRY/$ECR_REPOSITORY:$IMAGE_TAG .
        docker tag $ECR_REGISTRY/$ECR_REPOSITORY:$IMAGE_TAG $ECR_REGISTRY/$ECR_REPOSITORY:latest
        docker push $ECR_REGISTRY/$ECR_REPOSITORY:$IMAGE_TAG
        docker push $ECR_REGISTRY/$ECR_REPOSITORY:latest
        echo "image=$ECR_REGISTRY/$ECR_REPOSITORY:$IMAGE_TAG" >> $GITHUB_OUTPUT

    - name: Download current task definition
      run: |
        aws ecs describe-task-definition \
          --task-definition ${{ env.ECS_TASK_DEFINITION }} \
          --query taskDefinition > task-definition.json

    - name: Fill in the new image ID in the Amazon ECS task definition
      id: task-def
      uses: aws-actions/amazon-ecs-render-task-definition@v1
      with:
        task-definition: task-definition.json
        container-name: ${{ env.CONTAINER_NAME }}
        image: ${{ steps.build-image.outputs.image }}
        environment-variables: |
          NODE_ENV=production
          NEXT_PUBLIC_API_URL=https://app.techveesolutions.com

    - name: Deploy Amazon ECS task definition
      uses: aws-actions/amazon-ecs-deploy-task-definition@v1
      with:
        task-definition: ${{ steps.task-def.outputs.task-definition }}
        service: ${{ env.ECS_SERVICE }}
        cluster: ${{ env.ECS_CLUSTER }}
        wait-for-service-stability: true

    - name: Deployment summary
      run: |
        echo "✅ Frontend deployed successfully!"
        echo "Image: ${{ steps.build-image.outputs.image }}"
        echo "Service: ${{ env.ECS_SERVICE }}"
        echo "Cluster: ${{ env.ECS_CLUSTER }}"
```

#### Step 3.4: Create Combined Workflow (Optional)

If you want to deploy both on any change, create `.github/workflows/deploy-all.yml`:

```yaml
name: Deploy All Services

on:
  workflow_dispatch:  # Manual trigger only
  
jobs:
  deploy-backend:
    uses: ./.github/workflows/deploy-backend.yml
    secrets: inherit
    
  deploy-frontend:
    uses: ./.github/workflows/deploy-frontend.yml
    secrets: inherit
    needs: deploy-backend
```

---

### Part 4: Testing & Validation

#### Step 4.1: Commit and Push Workflows

```bash
cd C:/Users/vokeo/OneDrive/Desktop/task-management-app

# Add the workflow files
git add .github/workflows/

# Commit
git commit -m "Add GitHub Actions CI/CD workflows for ECS deployment"

# Push to trigger workflows
git push origin Cloud-Deployment
```

#### Step 4.2: Monitor Workflow Execution

**Browser Steps:**

1. Open: https://github.com/vee-kay8/task-management-app/actions
2. You should see the **Actions** tab page
3. Look for workflow runs - you may see:
   - Yellow dot (🟡) = Running
   - Green checkmark (✅) = Success
   - Red X (❌) = Failed
4. Click on a workflow run name (e.g., "Add GitHub Actions CI/CD workflows...")
5. You'll see the workflow details page with job(s)
6. Click on a job name (e.g., "Deploy Backend")
7. Watch the steps expand with logs:
   - Checkout code
   - Configure AWS credentials
   - Login to ECR
   - Build image
   - Push to ECR
   - Update task definition
   - Deploy to ECS
8. Each step shows real-time output
9. Wait for all steps to complete (green checkmarks)
10. Successful deployment shows summary at bottom

**What to Look For:**
- ✅ All steps should turn green
- Build time: ~3-5 minutes for backend, ~4-6 for frontend
- Final step should say "✅ Backend/Frontend deployed successfully!"
- Service should show as stable

#### Step 4.3: Test Backend Deployment

Make a simple change to test:

```bash
# Edit a backend file
echo "# CI/CD Test" >> backend/README.md

# Commit and push
git add backend/README.md
git commit -m "Test backend CI/CD pipeline"
git push origin Cloud-Deployment
```

Watch the deployment in GitHub Actions. Once complete, verify:

```bash
# Check ECS service
aws ecs describe-services \
  --cluster taskapp-cluster \
  --services taskapp-backend-service \
  --query 'services[0].deployments' \
  --region us-east-1

# You should see a new deployment with status "PRIMARY"
```

#### Step 4.4: Test Frontend Deployment

```bash
# Edit a frontend file
echo "/* CI/CD Test */" >> frontend/app/page.tsx

# Commit and push
git add frontend/app/page.tsx
git commit -m "Test frontend CI/CD pipeline"
git push origin Cloud-Deployment
```

Monitor in GitHub Actions and verify deployment.

#### Step 4.5: Verify Application

Visit https://app.techveesolutions.com and ensure:
- [ ] Application loads correctly
- [ ] Login works
- [ ] Backend API calls work
- [ ] No console errors

---

## Troubleshooting

### Issue 1: Workflow Not Triggering

**Symptom**: Push to main/Cloud-Deployment branch doesn't trigger workflow

**Solutions**:
1. Check branch name in workflow file matches your branch
2. Verify paths filter - change in matching path required
3. Check GitHub Actions is enabled in repository settings

### Issue 2: ECR Login Fails

**Symptom**: `Error: Cannot perform an interactive login from a non TTY device`

**Solutions**:
1. Verify AWS credentials in GitHub Secrets
2. Check IAM user has ECR permissions
3. Ensure `aws-actions/amazon-ecr-login@v2` action is used

### Issue 3: ECS Deployment Fails

**Symptom**: Task definition update succeeds but service doesn't update

**Solutions**:
1. Check IAM user has `ecs:UpdateService` permission
2. Verify service name and cluster name are correct
3. Check task definition is valid (CPU/memory limits)
4. Look at ECS service events in AWS Console

### Issue 4: Environment Variables Not Set

**Symptom**: Application crashes with missing environment variable errors

**Solutions**:
1. Verify all secrets are added to GitHub
2. Check `environment-variables` section in workflow
3. Ensure secret names match exactly (case-sensitive)

### Issue 5: Image Build Fails

**Symptom**: Docker build step fails in GitHub Actions

**Solutions**:
1. Test build locally: `docker build -t test ./backend`
2. Check Dockerfile syntax
3. Ensure all required files are committed to Git
4. Check for large files (>100MB) that might timeout

---

## Best Practices

### 1. Branch Protection

After Phase 10, consider:
- Require PR reviews before merging to main
- Run tests before allowing merge
- Require status checks to pass

### 2. Environment Variables

- Never commit secrets to Git
- Use GitHub Secrets for all sensitive data
- Rotate IAM access keys every 90 days

### 3. Deployment Strategy

- Always test in a branch first
- Monitor CloudWatch logs during deployment
- Keep old task definitions for quick rollback

### 4. Workflow Optimization

- Cache Docker layers to speed up builds
- Use specific action versions (not @latest)
- Set appropriate timeout values

---

## Rollback Procedure

If a deployment breaks production:

### Option 1: Revert Git Commit

```bash
# Revert the bad commit
git revert HEAD

# Push to trigger automatic redeploy
git push origin Cloud-Deployment
```

### Option 2: Manual Rollback in AWS Console

1. Go to ECS Console → Clusters → taskapp-cluster
2. Click on the service (backend or frontend)
3. Click **Update**
4. Under **Revision**, select previous task definition
5. Click **Update service**

### Option 3: AWS CLI Rollback

```bash
# List task definitions
aws ecs list-task-definitions \
  --family-prefix taskapp-backend \
  --sort DESC \
  --region us-east-1

# Update service to previous revision
aws ecs update-service \
  --cluster taskapp-cluster \
  --service taskapp-backend-service \
  --task-definition taskapp-backend:X \
  --region us-east-1

# Replace X with the previous revision number
```

---

## Cost Impact

**GitHub Actions**: Free for public repositories, 2000 minutes/month for private repos

**Additional AWS Costs**: None - just using existing resources

---

## Next Steps After Phase 10

Once CI/CD is working:

1. **Add Tests to Workflow**
   - Backend: pytest
   - Frontend: Jest tests
   - Fail deployment if tests fail

2. **Add Notifications**
   - Slack/Discord notifications on deployment
   - Email on deployment failure

3. **Multi-Environment Setup**
   - Staging environment
   - Separate workflows for staging vs production

4. **Security Scanning**
   - Docker image vulnerability scanning
   - Dependency scanning with Dependabot

---

## Phase 10 Completion Checklist

- [ ] IAM user created with correct permissions
- [ ] All 11 GitHub Secrets configured
- [ ] Backend workflow created and tested
- [ ] Frontend workflow created and tested
- [ ] Successful backend deployment via CI/CD
- [ ] Successful frontend deployment via CI/CD
- [ ] Application verified working after automated deployment
- [ ] Rollback procedure tested
- [ ] Documentation updated

---

## Success Criteria

✅ **Phase 10 Complete When:**
- Pushing code to Cloud-Deployment branch automatically deploys to ECS
- Both backend and frontend workflows working
- Zero manual steps required for deployment
- Application remains stable after automated deployments

---

**Timeline**: 2-3 hours
**Difficulty**: Medium
**Impact**: High - Eliminates manual deployments forever!

---

*Ready to automate your deployments? Let's go!* 🚀
