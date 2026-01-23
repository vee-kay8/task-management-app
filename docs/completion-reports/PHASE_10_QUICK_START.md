# Phase 10 Quick Checklist ⚡

## Pre-Flight Check
- [x] Phase 9 complete (Terraform)
- [x] Application running at https://app.techveesolutions.com
- [ ] GitHub repository ready
- [ ] AWS CLI configured

---

## Part 1: IAM Setup (30 min)

### Console Method (Easiest) 👈 RECOMMENDED

**Step 1: Create IAM User**
1. Go to AWS Console → IAM → Users
2. Click "Create user"
3. Username: `github-actions-ecs-deployer`
4. Click "Next" (no console access needed)
5. Click "Next" (skip permissions for now)
6. Click "Create user"

**Step 2: Create & Attach Policy**
1. IAM → Policies → "Create policy"
2. Click "JSON" tab
3. Copy policy from [AWS_PHASE_10_GUIDE.md](AWS_PHASE_10_GUIDE.md) (search for "github-actions-policy.json")
4. Paste and click "Next"
5. Policy name: `GitHubActionsECSDeployPolicy`
6. Click "Create policy"
7. Go back to Users → `github-actions-ecs-deployer`
8. "Permissions" tab → "Add permissions" → "Attach policies directly"
9. Search for `GitHubActionsECSDeployPolicy`, select it
10. Click "Add permissions"

**Step 3: Create Access Keys**
1. User page → "Security credentials" tab
2. Scroll to "Access keys" section
3. Click "Create access key"
4. Select "Third-party service" or "Other"
5. Click "Next" → "Create access key"
6. **⚠️ COPY BOTH VALUES NOW - YOU CAN'T SEE THEM AGAIN!**
   - Access key ID: `AKIA...`
   - Secret access key: `wJal...`
7. Click "Done"

---

### Terminal Method (Alternative)

```bash
# Navigate to project root
cd C:/Users/vokeo/OneDrive/Desktop/task-management-app

# 1. Create IAM user
aws iam create-user --user-name github-actions-ecs-deployer

# 2. Create policy file
# First, copy the policy JSON from AWS_PHASE_10_GUIDE.md
# Save it as github-actions-policy.json in current directory

# 3. Create policy
aws iam create-policy --policy-name GitHubActionsECSDeployPolicy --policy-document file://github-actions-policy.json

# 4. Attach policy (use the ARN from previous command output)
aws iam attach-user-policy --user-name github-actions-ecs-deployer --policy-arn arn:aws:iam::858448674350:policy/GitHubActionsECSDeployPolicy

# 5. Create access keys
aws iam create-access-key --user-name github-actions-ecs-deployer
# ⚠️ SAVE the AccessKeyId and SecretAccessKey from the output!
```

**Checklist:**
- [ ] IAM user created
- [ ] Policy created
- [ ] Policy attached
- [ ] Access keys generated
- [ ] Keys saved securely (paste in notepad temporarily)

---

## Part 2: GitHub Secrets (15 min)

### Browser Console Method 👈 DO THIS

**Navigate to Secrets Page:**
1. Open: https://github.com/vee-kay8/task-management-app/settings/secrets/actions
2. If redirected to login, sign in to GitHub
3. You should see "Actions secrets and variables" page

**Add Each Secret (repeat 11 times):**

For each secret below:
1. Click green "New repository secret" button
2. Name: Copy the name exactly (e.g., `AWS_ACCESS_KEY_ID`)
3. Secret: Copy the value exactly
4. Click "Add secret"
5. Check it off the list ✅

**Secret Values:**

```
Name: AWS_ACCESS_KEY_ID
Value: [Paste from IAM step - starts with AKIA...]
```

```
Name: AWS_SECRET_ACCESS_KEY
Value: [Paste from IAM step - long random string]
```

```
Name: AWS_REGION
Value: us-east-1
```

```
Name: ECR_BACKEND_REPOSITORY
Value: taskapp-backend
```

```
Name: ECR_FRONTEND_REPOSITORY
Value: taskapp-frontend
```

```
Name: ECS_CLUSTER
Value: taskapp-cluster
```

```
Name: ECS_BACKEND_SERVICE
Value: taskapp-backend-service
```

```
Name: ECS_FRONTEND_SERVICE
Value: taskapp-frontend-service
```

```
Name: DATABASE_URL
Value: postgresql://postgres:YourSecurePassword123!@taskapp-db.cqaewjp43tdm.us-east-1.rds.amazonaws.com:5432/taskmanagement
```

```
Name: SECRET_KEY
Value: FaKgFvIjFU3tz6bAugmkRw6CQfoaJuqAbJe/PYlyyu0=
```

```
Name: JWT_SECRET_KEY
Value: IB8fu3yhS/mPgIRmP6CsBab//X7Hnm+VggOHqXnB/F4=
```

**Checklist (11 total):**
- [ ] `AWS_ACCESS_KEY_ID`
- [ ] `AWS_SECRET_ACCESS_KEY`
- [ ] `AWS_REGION`
- [ ] `ECR_BACKEND_REPOSITORY`
- [ ] `ECR_FRONTEND_REPOSITORY`
- [ ] `ECS_CLUSTER`
- [ ] `ECS_BACKEND_SERVICE`
- [ ] `ECS_FRONTEND_SERVICE`
- [ ] `DATABASE_URL`
- [ ] `SECRET_KEY`
- [ ] `JWT_SECRET_KEY`

✅ **Verify**: You should see 11 secrets listed on the page

---

## Part 3: Create Workflows (45 min)

### PowerShell/Terminal Method

**Step 1: Create Directory Structure**

```powershell
# Open PowerShell or Git Bash
cd C:/Users/vokeo/OneDrive/Desktop/task-management-app

# Create workflows directory
mkdir -p .github/workflows

# Or in PowerShell:
New-Item -ItemType Directory -Force -Path .github/workflows
```

**Step 2: Create Backend Workflow**

```powershell
# Create empty file
New-Item -ItemType File -Path .github/workflows/deploy-backend.yml
```

Now open `.github/workflows/deploy-backend.yml` in VS Code and paste this:

<details>
<summary>Click to expand deploy-backend.yml content</summary>

```yaml
name: Deploy Backend to ECS

on:
  push:
    branches: [main, Cloud-Deployment]
    paths:
      - 'backend/**'
      - '.github/workflows/deploy-backend.yml'

env:
  AWS_REGION: ${{ secrets.AWS_REGION }}
  ECR_REPOSITORY: ${{ secrets.ECR_BACKEND_REPOSITORY }}
  ECS_CLUSTER: ${{ secrets.ECS_CLUSTER }}
  ECS_SERVICE: ${{ secrets.ECS_BACKEND_SERVICE }}
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
          docker push $ECR_REGISTRY/$ECR_REPOSITORY:$IMAGE_TAG
          docker tag $ECR_REGISTRY/$ECR_REPOSITORY:$IMAGE_TAG $ECR_REGISTRY/$ECR_REPOSITORY:latest
          docker push $ECR_REGISTRY/$ECR_REPOSITORY:latest
          echo "image=$ECR_REGISTRY/$ECR_REPOSITORY:$IMAGE_TAG" >> $GITHUB_OUTPUT

      - name: Download current task definition
        run: |
          aws ecs describe-task-definition \
            --task-definition taskapp-backend \
            --query taskDefinition > task-definition.json

      - name: Update task definition with new image
        id: task-def
        uses: aws-actions/amazon-ecs-render-task-definition@v1
        with:
          task-definition: task-definition.json
          container-name: ${{ env.CONTAINER_NAME }}
          image: ${{ steps.build-image.outputs.image }}
          environment-variables: |
            DATABASE_URL=${{ secrets.DATABASE_URL }}
            SECRET_KEY=${{ secrets.SECRET_KEY }}
            JWT_SECRET_KEY=${{ secrets.JWT_SECRET_KEY }}
            FLASK_ENV=production
            DEBUG=0
            CORS_ORIGINS=https://app.techveesolutions.com
            JWT_ACCESS_TOKEN_EXPIRES=3600

      - name: Deploy to Amazon ECS
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

</details>

**Step 3: Create Frontend Workflow**

```powershell
# Create empty file
New-Item -ItemType File -Path .github/workflows/deploy-frontend.yml
```

Open `.github/workflows/deploy-frontend.yml` and paste this:

<details>
<summary>Click to expand deploy-frontend.yml content</summary>

```yaml
name: Deploy Frontend to ECS

on:
  push:
    branches: [main, Cloud-Deployment]
    paths:
      - 'frontend/**'
      - '.github/workflows/deploy-frontend.yml'

env:
  AWS_REGION: ${{ secrets.AWS_REGION }}
  ECR_REPOSITORY: ${{ secrets.ECR_FRONTEND_REPOSITORY }}
  ECS_CLUSTER: ${{ secrets.ECS_CLUSTER }}
  ECS_SERVICE: ${{ secrets.ECS_FRONTEND_SERVICE }}
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
            --build-arg NEXT_PUBLIC_API_URL=https://app.techveesolutions.com/api \
            -t $ECR_REGISTRY/$ECR_REPOSITORY:$IMAGE_TAG .
          docker push $ECR_REGISTRY/$ECR_REPOSITORY:$IMAGE_TAG
          docker tag $ECR_REGISTRY/$ECR_REPOSITORY:$IMAGE_TAG $ECR_REGISTRY/$ECR_REPOSITORY:latest
          docker push $ECR_REGISTRY/$ECR_REPOSITORY:latest
          echo "image=$ECR_REGISTRY/$ECR_REPOSITORY:$IMAGE_TAG" >> $GITHUB_OUTPUT

      - name: Download current task definition
        run: |
          aws ecs describe-task-definition \
            --task-definition taskapp-frontend \
            --query taskDefinition > task-definition.json

      - name: Update task definition with new image
        id: task-def
        uses: aws-actions/amazon-ecs-render-task-definition@v1
        with:
          task-definition: task-definition.json
          container-name: ${{ env.CONTAINER_NAME }}
          image: ${{ steps.build-image.outputs.image }}
          environment-variables: |
            NODE_ENV=production
            NEXT_PUBLIC_API_URL=https://app.techveesolutions.com/api

      - name: Deploy to Amazon ECS
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

</details>

**Checklist:**
- [ ] `.github/workflows/deploy-backend.yml` created
- [ ] `.github/workflows/deploy-frontend.yml` created
- [ ] Both files have correct YAML content (no syntax errors)

---

## Part 4: Test & Deploy (30 min)

### Terminal Execution

**Step 1: Commit and Push Workflows**

```bash
# Make sure you're in project root
cd C:/Users/vokeo/OneDrive/Desktop/task-management-app

# Check git status
git status

# Add workflow files
git add .github/workflows/

# Commit
git commit -m "Add CI/CD workflows for backend and frontend"

# Push to Cloud-Deployment branch
git push origin Cloud-Deployment
```

**Step 2: Watch First Deployment**

1. Open browser: https://github.com/vee-kay8/task-management-app/actions
2. You should see workflows starting automatically
3. Click on a workflow to see live logs
4. Wait for green checkmarks ✅

**Step 3: Test Backend Deployment**

```bash
# Make a small change to backend
echo "" >> backend/README.md
echo "# CI/CD Pipeline Enabled" >> backend/README.md

# Commit and push
git add backend/README.md
git commit -m "Test backend CI/CD pipeline"
git push origin Cloud-Deployment
```

**Watch in browser:**
- Go to: https://github.com/vee-kay8/task-management-app/actions
- Click on "Deploy Backend to ECS" workflow
- Watch the build → push → deploy process (takes ~5-8 minutes)

**Step 4: Test Frontend Deployment**

```bash
# Make a small change to frontend
echo "" >> frontend/README.md
echo "# CI/CD Pipeline Enabled" >> frontend/README.md

# Commit and push
git add frontend/README.md
git commit -m "Test frontend CI/CD pipeline"
git push origin Cloud-Deployment
```

**Watch in browser:**
- Actions page should show "Deploy Frontend to ECS" running
- Wait for completion (~5-8 minutes)

**Step 5: Verify Deployments**

```bash
# Check ECS service status
aws ecs describe-services \
  --cluster taskapp-cluster \
  --services taskapp-backend-service taskapp-frontend-service \
  --query 'services[*].[serviceName,desiredCount,runningCount,deployments[0].status]' \
  --output table
```

**Browser Verification:**
1. Open: https://app.techveesolutions.com
2. Test login functionality
3. Create a task
4. Verify everything works

**Checklist:**
- [ ] Workflows committed and pushed
- [ ] Both workflows visible in GitHub Actions
- [ ] Backend test deployment successful (green checkmark)
- [ ] Frontend test deployment successful (green checkmark)
- [ ] New ECS tasks running (check AWS Console or CLI)
- [ ] Application works at https://app.techveesolutions.com
- [ ] Login/API calls functioning correctly

---

## Completion Criteria

✅ **Phase 10 Complete when:**
- All workflows created and committed
- IAM permissions working
- Automated deployments successful
- Application verified after auto-deploy

---

## Quick Commands Reference

```bash
# Check ECS service deployment status
aws ecs describe-services \
  --cluster taskapp-cluster \
  --services taskapp-backend-service taskapp-frontend-service \
  --query 'services[*].[serviceName,desiredCount,runningCount,deployments[0].status]' \
  --output table

# View recent workflow runs
gh run list --limit 5

# Rollback to previous task definition
aws ecs update-service \
  --cluster taskapp-cluster \
  --service taskapp-backend-service \
  --task-definition taskapp-backend:1 \
  --region us-east-1
```

---

## Troubleshooting

**Workflow not triggering?**
- Check branch name matches workflow trigger
- Verify file paths match what you changed

**ECR login fails?**
- Verify AWS credentials in GitHub Secrets
- Check IAM policy includes ECR permissions

**Deployment fails?**
- Check CloudWatch logs
- Verify environment variables in workflow
- Check ECS service events in AWS Console

---

## Documentation

- **Full Guide**: [AWS_PHASE_10_GUIDE.md](AWS_PHASE_10_GUIDE.md)
- **Current Status**: [AWS_DEPLOYMENT_ROADMAP.md](AWS_DEPLOYMENT_ROADMAP.md)

---

**Estimated Time**: 2-3 hours
**Impact**: Eliminates manual deployments forever! 🚀

**Ready?** Open [AWS_PHASE_10_GUIDE.md](AWS_PHASE_10_GUIDE.md) and let's go!
