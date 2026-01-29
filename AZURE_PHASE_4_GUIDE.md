# Azure Phase 4: Container Registry - Complete Guide

**Duration**: 1-2 hours  
**Difficulty**: Beginner-Intermediate  
**Prerequisites**: Phase 1-3 complete (Account setup, VNet configured, Database created)  
**Goal**: Create Azure Container Registry and push Docker images for backend and frontend

---

## 📋 Overview

This phase sets up your container registry using Azure Container Registry (ACR). By the end, you'll have:

✅ Azure Container Registry created  
✅ Docker images built for backend and frontend  
✅ Images tagged and pushed to ACR  
✅ Registry authentication configured  
✅ Images verified and ready for deployment  

**Why ACR?** Azure Container Registry is a private Docker registry that stores your container images securely within Azure. Container Apps (Phase 6-7) will pull images directly from ACR.

---

## Table of Contents

1. [Understanding Azure Container Registry](#understanding-azure-container-registry)
2. [Create Azure Container Registry](#step-1-create-azure-container-registry)
3. [Authenticate Docker to ACR](#step-2-authenticate-docker-to-acr)
4. [Build Docker Images](#step-3-build-docker-images)
5. [Tag and Push Images to ACR](#step-4-tag-and-push-images-to-acr)
6. [Verify Images in ACR](#step-5-verify-images-in-acr)
7. [Phase 4 Completion Checklist](#phase-4-completion-checklist)

---

## Understanding Azure Container Registry

### What is Azure Container Registry? 🐳

**Azure Container Registry (ACR)** is a managed Docker registry service for storing and managing private container images. It's Azure's equivalent to Docker Hub or Amazon ECR.

**AWS Equivalent:** ECR (Elastic Container Registry)

### Why Use ACR?

| Feature | Benefit |
|---------|---------|
| **Private Registry** | Your images are private, not public like Docker Hub |
| **Azure Integration** | Works seamlessly with Container Apps, AKS, etc. |
| **Security** | Built-in vulnerability scanning (with Defender) |
| **Geo-Replication** | Replicate images across regions (Premium tier) |
| **Performance** | Fast image pulls from same region |
| **Cost-Effective** | Basic tier is only ~$5/month |

### ACR Tiers Comparison

| Tier | Storage | Webhooks | Geo-Replication | Cost (Estimate) | Best For |
|------|---------|----------|-----------------|-----------------|----------|
| **Basic** | 10 GB | 2 | ❌ | ~$5/month | Dev/Test, Learning |
| **Standard** | 100 GB | 10 | ❌ | ~$20/month | Small production workloads |
| **Premium** | 500 GB | 500 | ✅ | ~$100/month | Enterprise, high availability |

> 💡 **For Learning**: We'll use **Basic tier** - perfect for development and keeps costs minimal.

### ACR Features

**What ACR Provides:**
- **Private Image Storage**: Store unlimited Docker images (within storage limits)
- **Authentication**: Multiple auth methods (admin user, service principal, managed identity)
- **Access Control**: RBAC for fine-grained permissions
- **Image Scanning**: Vulnerability detection (with Microsoft Defender for Cloud)
- **Webhooks**: Trigger actions when images are pushed
- **Retention Policies**: Auto-delete old images (Standard/Premium)
- **Azure Integration**: Works with Container Apps, AKS, App Service, etc.

### How ACR Works with Container Apps

```
┌─────────────────────────────────────────────────────────────┐
│  Your Development Machine                                   │
│                                                              │
│  ┌──────────────┐         ┌──────────────┐                 │
│  │   Backend    │         │   Frontend   │                 │
│  │   Dockerfile │         │   Dockerfile │                 │
│  └──────┬───────┘         └──────┬───────┘                 │
│         │                        │                          │
│         │ docker build           │ docker build             │
│         ▼                        ▼                          │
│  ┌──────────────┐         ┌──────────────┐                 │
│  │ backend:     │         │ frontend:    │                 │
│  │ latest       │         │ latest       │                 │
│  └──────┬───────┘         └──────┬───────┘                 │
│         │                        │                          │
│         │ docker tag             │ docker tag               │
│         ▼                        ▼                          │
│  ┌────────────────────────────────────────┐                │
│  │ taskappacr.azurecr.io/taskapp-backend  │                │
│  │ taskappacr.azurecr.io/taskapp-frontend │                │
│  └──────┬─────────────────────────────────┘                │
│         │                                                   │
│         │ docker push                                       │
│         ▼                                                   │
└─────────┼───────────────────────────────────────────────────┘
          │
          │ Push to ACR
          ▼
┌─────────────────────────────────────────────────────────────┐
│  Azure Container Registry                                   │
│  taskappacr.azurecr.io                                      │
│                                                              │
│  📦 Repositories:                                           │
│     • taskapp-backend:latest                                │
│     • taskapp-frontend:latest                               │
│                                                              │
└─────────────────────────────────────────────────────────────┘
          │
          │ Pull images
          ▼
┌─────────────────────────────────────────────────────────────┐
│  Azure Container Apps (Phase 6-7)                           │
│                                                              │
│  ┌──────────────────┐       ┌──────────────────┐           │
│  │ Backend App      │       │ Frontend App     │           │
│  │ (pulls backend)  │       │ (pulls frontend) │           │
│  └──────────────────┘       └──────────────────┘           │
└─────────────────────────────────────────────────────────────┘
```

### Registry Naming Rules

**ACR Name Requirements:**
- **Globally unique** across all of Azure
- **5-50 characters** (lowercase letters and numbers only)
- **No hyphens, underscores, or special characters**
- Must start with a letter

**Examples:**
- ✅ `taskappacr2026`
- ✅ `taskappacrvk`
- ✅ `taskappregistry01`
- ❌ `taskapp-acr` (no hyphens)
- ❌ `TaskAppACR` (no uppercase)
- ❌ `task_app_acr` (no underscores)

---

## Architecture Overview

Here's what we'll build in Phase 4:

```
┌─────────────────────────────────────────────────────────────────┐
│  Resource Group: rg-taskapp-prod (Central US)                   │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │  Azure Container Registry                                  │ │
│  │  Name: taskappacr[unique]                                  │ │
│  │  SKU: Basic                                                │ │
│  │  Login Server: taskappacr[unique].azurecr.io               │ │
│  │                                                            │ │
│  │  📦 Repositories:                                          │ │
│  │     ┌──────────────────────────────────────────┐          │ │
│  │     │ taskapp-backend                          │          │ │
│  │     │   Tags: latest, v1.0.0                   │          │ │
│  │     │   Size: ~500 MB                          │          │ │
│  │     └──────────────────────────────────────────┘          │ │
│  │     ┌──────────────────────────────────────────┐          │ │
│  │     │ taskapp-frontend                         │          │ │
│  │     │   Tags: latest, v1.0.0                   │          │ │
│  │     │   Size: ~200 MB                          │          │ │
│  │     └──────────────────────────────────────────┘          │ │
│  │                                                            │ │
│  │  🔐 Authentication:                                        │ │
│  │     • Admin user enabled (for development)                │ │
│  │     • Will use managed identity in Phase 6                │ │
│  └────────────────────────────────────────────────────────────┘ │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## Step 1: Create Azure Container Registry

### What You're Creating

An Azure Container Registry with:
- **Basic tier** (cost-effective for learning)
- **Admin user enabled** (simplifies authentication)
- **Same region as other resources** (Central US)
- **Private access** (not exposed to internet without authentication)

### Choose a Unique Registry Name

Your registry name must be **globally unique** across all of Azure.

**Suggestions:**
- Your initials + "acr" + numbers: `vkacr2026`
- Project name + random: `taskappacr88`
- Simple + unique: `taskappregistry01`

**Test if name is available:**
```bash
az acr check-name --name YOUR-REGISTRY-NAME --query nameAvailable --output tsv
```

**Expected output:**
- `true` = Available ✅
- `false` = Already taken, try another name ❌

### Option A: Console (Azure Portal) Method

**Step-by-step:**

1. **Navigate to Container Registries**
   - Go to Azure Portal: https://portal.azure.com
   - Click **"+ Create a resource"**
   - Search for **"Container Registry"**
   - Click **"Container Registry"** by Microsoft
   - Click **"Create"**

2. **Basics Tab - Project Details**
   - **Subscription**: Azure subscription 1 (your subscription)
   - **Resource group**: rg-taskapp-prod
   - **Registry name**: YOUR-UNIQUE-NAME (e.g., taskappacr2026)
   - **Location**: Central US ✅ (same as other resources)
   - **SKU**: Basic

3. **Networking Tab**
   - **Public access**: Enabled (default)
   - Note: We'll secure this with authentication; public access just means it has a public endpoint

4. **Encryption Tab**
   - Leave defaults (Microsoft-managed key)

5. **Tags Tab** (Optional but recommended)
   - Add tags:
     - `Environment` = `Production`
     - `Project` = `TaskApp`
     - `ManagedBy` = `Manual`
     - `CostCenter` = `Learning`

6. **Review + Create**
   - Review your settings:
     - Registry name: YOUR-UNIQUE-NAME
     - SKU: Basic
     - Location: Central US
   - Click **"Create"**

7. **Wait for Deployment**
   - Deployment takes 1-2 minutes ⏳
   - Click **"Go to resource"** when complete

8. **Enable Admin User**
   - In the left menu, click **"Access keys"** (under Settings)
   - Toggle **"Admin user"** to **Enabled** ✅
   - Note the **Login server**, **Username**, and **Password** (we'll use these)
   - You'll see 2 passwords - you can use either one

### Option B: CLI Method (Recommended)

**Create the registry:**

```bash
# Replace YOUR-REGISTRY-NAME with your chosen unique name
# Example: taskappacr2026, vkacr2026, etc.

az acr create \
  --resource-group rg-taskapp-prod \
  --name YOUR-REGISTRY-NAME \
  --sku Basic \
  --location centralus \
  --admin-enabled true \
  --tags Environment=Production Project=TaskApp ManagedBy=Manual CostCenter=Learning
```

**This command will take 1-2 minutes** ⏳

**Expected output:**
```json
{
  "adminUserEnabled": true,
  "creationDate": "2026-01-29T...",
  "id": "/subscriptions/.../resourceGroups/rg-taskapp-prod/providers/Microsoft.ContainerRegistry/registries/YOUR-REGISTRY-NAME",
  "location": "centralus",
  "loginServer": "YOUR-REGISTRY-NAME.azurecr.io",
  "name": "YOUR-REGISTRY-NAME",
  "provisioningState": "Succeeded",
  "sku": {
    "name": "Basic",
    "tier": "Basic"
  },
  "status": null,
  "storageAccount": null
}
```

**Key fields to note:**
- **`loginServer`**: This is your registry URL (e.g., `taskappacr2026.azurecr.io`)
- **`adminUserEnabled`**: true ✅
- **`provisioningState`**: "Succeeded" ✅

### Verify Registry Creation

```bash
# List all container registries
az acr list --resource-group rg-taskapp-prod --output table

# Expected output:
# Name               ResourceGroup    Location    SKU    LoginServer                    CreationDate
# -----------------  ---------------  ----------  -----  -----------------------------  ---------------
# YOUR-REGISTRY-NAME rg-taskapp-prod  centralus   Basic  YOUR-REGISTRY-NAME.azurecr.io  2026-01-29T...
```

### Get Registry Credentials

```bash
# Get admin credentials
az acr credential show \
  --resource-group rg-taskapp-prod \
  --name YOUR-REGISTRY-NAME \
  --output table

# Expected output:
# USERNAME           PASSWORD                          PASSWORD2
# -----------------  --------------------------------  --------------------------------
# YOUR-REGISTRY-NAME [long-random-password]           [another-long-password]
```

### Save Registry Details

```bash
# Save registry details to a file
cat > azure/config/acr-details.txt << EOF
Azure Container Registry Details
=================================
Registry Name: YOUR-REGISTRY-NAME
Login Server: YOUR-REGISTRY-NAME.azurecr.io
Location: Central US
SKU: Basic
Admin User Enabled: Yes

Created: $(date)

Note: Admin credentials available via:
az acr credential show --name YOUR-REGISTRY-NAME --resource-group rg-taskapp-prod
EOF

echo "✅ Registry details saved to azure/config/acr-details.txt"
```

### What Just Happened? 🤔

- **Container Registry Created**: Private Docker registry in Azure
- **Basic Tier**: Cost-effective for learning ($5/month)
- **Admin User Enabled**: Simplified authentication for development
- **Login Server**: YOUR-REGISTRY-NAME.azurecr.io (this is your registry URL)
- **Ready for Images**: Can now push Docker images

---

## Step 2: Authenticate Docker to ACR

### What You're Doing

Authenticating your local Docker client to Azure Container Registry so you can push images.

### Prerequisites

**Verify Docker is installed and running:**

```bash
# Check Docker version
docker --version

# Expected output: Docker version 24.x.x or higher
```

If Docker is not installed:
- **Windows/Mac**: Install Docker Desktop from https://www.docker.com/products/docker-desktop
- **Linux**: `sudo apt-get install docker.io` (Ubuntu/Debian)

### Method 1: Using Azure CLI (Recommended)

This method uses your Azure CLI credentials (no need to copy/paste passwords).

```bash
# Login to ACR using Azure CLI
az acr login --name YOUR-REGISTRY-NAME
```

**Expected output:**
```
Login Succeeded
```

**How it works:**
- Uses your current Azure CLI authentication
- Automatically generates a Docker access token
- Token is valid for 3 hours
- Simplest method for development

### Method 2: Using Admin Credentials

If you prefer to use the admin username/password:

```bash
# Get credentials
REGISTRY_NAME="YOUR-REGISTRY-NAME"
ACR_USERNAME=$(az acr credential show --name $REGISTRY_NAME --resource-group rg-taskapp-prod --query username --output tsv)
ACR_PASSWORD=$(az acr credential show --name $REGISTRY_NAME --resource-group rg-taskapp-prod --query passwords[0].value --output tsv)

# Login to Docker
echo $ACR_PASSWORD | docker login ${REGISTRY_NAME}.azurecr.io --username $ACR_USERNAME --password-stdin
```

**Expected output:**
```
Login Succeeded
```

### Verify Authentication

```bash
# Test connection by listing repositories (should be empty for now)
az acr repository list --name YOUR-REGISTRY-NAME --output table

# Expected output: (empty)
```

### What Just Happened? 🤔

- **Docker Authenticated**: Your Docker client can now push to ACR
- **Secure Connection**: All pushes are authenticated and encrypted
- **Ready to Push**: Can now tag and push images

---

## Step 3: Build Docker Images

### What You're Doing

Building Docker images for your backend and frontend applications locally.

### Verify Dockerfiles Exist

```bash
# Check backend Dockerfile exists
ls backend/Dockerfile

# Check frontend Dockerfile exists
ls frontend/Dockerfile

# Both should exist ✅
```

### Build Backend Image

**Navigate to project root and build:**

```bash
# Build backend image
docker build -t taskapp-backend:latest ./backend

# This will take 3-5 minutes ⏳
# Docker will:
# 1. Download Python base image
# 2. Install dependencies from requirements.txt
# 3. Copy application code
# 4. Set up entry point
```

**Expected output (final lines):**
```
Successfully built a1b2c3d4e5f6
Successfully tagged taskapp-backend:latest
```

**Verify backend image:**
```bash
docker images | grep taskapp-backend

# Expected output:
# REPOSITORY         TAG       IMAGE ID       CREATED          SIZE
# taskapp-backend    latest    a1b2c3d4e5f6   10 seconds ago   ~500MB
```

### Build Frontend Image

**Build frontend image:**

```bash
# Build frontend image
docker build -t taskapp-frontend:latest ./frontend

# This will take 3-5 minutes ⏳
# Docker will:
# 1. Download Node.js base image
# 2. Install npm dependencies
# 3. Build Next.js production bundle
# 4. Copy built files
# 5. Set up entry point
```

**Expected output (final lines):**
```
Successfully built b2c3d4e5f6a1
Successfully tagged taskapp-frontend:latest
```

**Verify frontend image:**
```bash
docker images | grep taskapp-frontend

# Expected output:
# REPOSITORY          TAG       IMAGE ID       CREATED          SIZE
# taskapp-frontend    latest    b2c3d4e5f6a1   10 seconds ago   ~200MB
```

### Verify Both Images

```bash
# List all taskapp images
docker images | grep taskapp

# Expected output:
# REPOSITORY          TAG       IMAGE ID       CREATED          SIZE
# taskapp-frontend    latest    b2c3d4e5f6a1   1 minute ago     ~200MB
# taskapp-backend     latest    a1b2c3d4e5f6   5 minutes ago    ~500MB
```

### Optional: Test Images Locally

**Test backend:**
```bash
# Run backend container locally (optional)
docker run -d -p 5000:5000 --name test-backend taskapp-backend:latest

# Check if running
curl http://localhost:5000/health || curl http://localhost:5000

# Stop and remove
docker stop test-backend && docker rm test-backend
```

**Test frontend:**
```bash
# Run frontend container locally (optional)
docker run -d -p 3000:3000 --name test-frontend taskapp-frontend:latest

# Check if running
curl http://localhost:3000

# Stop and remove
docker stop test-frontend && docker rm test-frontend
```

### What Just Happened? 🤔

- **Backend Image Built**: Python Flask application containerized
- **Frontend Image Built**: Next.js application containerized
- **Local Images Created**: Stored in local Docker cache
- **Ready to Tag**: Images ready to be tagged for ACR

---

## Step 4: Tag and Push Images to ACR

### What You're Doing

Tagging your local images with the ACR registry name, then pushing them to Azure Container Registry.

### Understanding Image Tagging

**Image tag format:**
```
<registry-login-server>/<repository-name>:<tag>

Example:
taskappacr2026.azurecr.io/taskapp-backend:latest
│                       │ │               │ │
│                       │ │               │ └─ Tag (version)
│                       │ │               └─── Repository name
│                       │ └───────────────── Separator
│                       └─────────────────── Registry server
└─────────────────────────────────────────── Your ACR name
```

### Tag Backend Image

```bash
# Replace YOUR-REGISTRY-NAME with your actual registry name
REGISTRY_NAME="YOUR-REGISTRY-NAME"

# Tag backend image
docker tag taskapp-backend:latest ${REGISTRY_NAME}.azurecr.io/taskapp-backend:latest

# Also tag with version number (optional but recommended)
docker tag taskapp-backend:latest ${REGISTRY_NAME}.azurecr.io/taskapp-backend:v1.0.0

# Verify tags
docker images | grep taskapp-backend
```

**Expected output:**
```
REPOSITORY                                        TAG       IMAGE ID       CREATED        SIZE
YOUR-REGISTRY-NAME.azurecr.io/taskapp-backend     latest    a1b2c3d4e5f6   10 mins ago    ~500MB
YOUR-REGISTRY-NAME.azurecr.io/taskapp-backend     v1.0.0    a1b2c3d4e5f6   10 mins ago    ~500MB
taskapp-backend                                   latest    a1b2c3d4e5f6   10 mins ago    ~500MB
```

### Tag Frontend Image

```bash
# Tag frontend image
docker tag taskapp-frontend:latest ${REGISTRY_NAME}.azurecr.io/taskapp-frontend:latest

# Also tag with version number
docker tag taskapp-frontend:latest ${REGISTRY_NAME}.azurecr.io/taskapp-frontend:v1.0.0

# Verify tags
docker images | grep taskapp-frontend
```

**Expected output:**
```
REPOSITORY                                         TAG       IMAGE ID       CREATED        SIZE
YOUR-REGISTRY-NAME.azurecr.io/taskapp-frontend     latest    b2c3d4e5f6a1   5 mins ago     ~200MB
YOUR-REGISTRY-NAME.azurecr.io/taskapp-frontend     v1.0.0    b2c3d4e5f6a1   5 mins ago     ~200MB
taskapp-frontend                                   latest    b2c3d4e5f6a1   5 mins ago     ~200MB
```

### Push Backend Image to ACR

```bash
# Push backend image (latest tag)
docker push ${REGISTRY_NAME}.azurecr.io/taskapp-backend:latest

# This will take 2-5 minutes depending on your internet speed ⏳
# You'll see progress for each layer
```

**Expected output:**
```
The push refers to repository [YOUR-REGISTRY-NAME.azurecr.io/taskapp-backend]
a1b2c3d4e5f6: Pushed
b2c3d4e5f6a1: Pushed
c3d4e5f6a1b2: Pushed
...
latest: digest: sha256:1a2b3c4d5e6f... size: 2345
```

**Push version tag:**
```bash
# Push backend image (v1.0.0 tag)
docker push ${REGISTRY_NAME}.azurecr.io/taskapp-backend:v1.0.0

# This will be fast since layers are already pushed
```

### Push Frontend Image to ACR

```bash
# Push frontend image (latest tag)
docker push ${REGISTRY_NAME}.azurecr.io/taskapp-frontend:latest

# This will take 2-5 minutes ⏳
```

**Expected output:**
```
The push refers to repository [YOUR-REGISTRY-NAME.azurecr.io/taskapp-frontend]
d4e5f6a1b2c3: Pushed
e5f6a1b2c3d4: Pushed
f6a1b2c3d4e5: Pushed
...
latest: digest: sha256:2b3c4d5e6f7a... size: 1234
```

**Push version tag:**
```bash
# Push frontend image (v1.0.0 tag)
docker push ${REGISTRY_NAME}.azurecr.io/taskapp-frontend:v1.0.0
```

### What Just Happened? 🤔

- **Images Tagged**: Local images tagged with ACR registry URL
- **Images Pushed**: Uploaded to Azure Container Registry
- **Multiple Tags**: Both `latest` and `v1.0.0` tags pushed
- **Available in Azure**: Images now stored in ACR and ready for deployment

---

## Step 5: Verify Images in ACR

### Verify via Azure CLI

**List all repositories:**
```bash
az acr repository list \
  --name YOUR-REGISTRY-NAME \
  --output table

# Expected output:
# Result
# -----------------
# taskapp-backend
# taskapp-frontend
```

**List tags for backend:**
```bash
az acr repository show-tags \
  --name YOUR-REGISTRY-NAME \
  --repository taskapp-backend \
  --output table

# Expected output:
# Result
# --------
# latest
# v1.0.0
```

**List tags for frontend:**
```bash
az acr repository show-tags \
  --name YOUR-REGISTRY-NAME \
  --repository taskapp-frontend \
  --output table

# Expected output:
# Result
# --------
# latest
# v1.0.0
```

### Get Detailed Image Information

**Backend image details:**
```bash
az acr repository show \
  --name YOUR-REGISTRY-NAME \
  --repository taskapp-backend \
  --output json

# Shows: image count, last update time, manifest count, etc.
```

**Frontend image details:**
```bash
az acr repository show \
  --name YOUR-REGISTRY-NAME \
  --repository taskapp-frontend \
  --output json
```

### Verify in Azure Portal

1. Go to Azure Portal: https://portal.azure.com
2. Navigate to **Resource groups** → **rg-taskapp-prod**
3. Click on your Container Registry (YOUR-REGISTRY-NAME)
4. In the left menu, click **"Repositories"** (under Services)
5. You should see:
   - **taskapp-backend** (2 tags: latest, v1.0.0)
   - **taskapp-frontend** (2 tags: latest, v1.0.0)
6. Click on each repository to see tags and details

### Get Image Pull Commands

**Backend pull command:**
```bash
echo "${REGISTRY_NAME}.azurecr.io/taskapp-backend:latest"

# This is the full image reference you'll use in Phase 6
```

**Frontend pull command:**
```bash
echo "${REGISTRY_NAME}.azurecr.io/taskapp-frontend:latest"

# This is the full image reference you'll use in Phase 7
```

### Optional: Pull Image to Verify

**Test pulling backend image:**
```bash
# Remove local image first
docker rmi ${REGISTRY_NAME}.azurecr.io/taskapp-backend:latest

# Pull from ACR
docker pull ${REGISTRY_NAME}.azurecr.io/taskapp-backend:latest

# Should download successfully ✅
```

### What Just Happened? 🤔

- **Images Verified**: Both images exist in ACR
- **Tags Confirmed**: Multiple tags (latest, v1.0.0) available
- **Pull Commands Ready**: Full image references for Container Apps deployment
- **Storage Used**: ~700 MB of your 10 GB Basic tier storage

---

## Phase 4 Completion Checklist

### What You've Accomplished

- [x] **Step 1: Azure Container Registry Created**
  - Registry name: YOUR-REGISTRY-NAME
  - Login server: YOUR-REGISTRY-NAME.azurecr.io
  - SKU: Basic ($5/month)
  - Location: Central US
  - Admin user enabled
  - Tags applied

- [x] **Step 2: Docker Authentication**
  - Docker client authenticated to ACR
  - Can push and pull images
  - Credentials secured

- [x] **Step 3: Docker Images Built**
  - Backend image: taskapp-backend:latest (~500 MB)
  - Frontend image: taskapp-frontend:latest (~200 MB)
  - Built from Dockerfiles
  - Tested locally (optional)

- [x] **Step 4: Images Tagged and Pushed**
  - Backend: YOUR-REGISTRY-NAME.azurecr.io/taskapp-backend:latest
  - Backend: YOUR-REGISTRY-NAME.azurecr.io/taskapp-backend:v1.0.0
  - Frontend: YOUR-REGISTRY-NAME.azurecr.io/taskapp-frontend:latest
  - Frontend: YOUR-REGISTRY-NAME.azurecr.io/taskapp-frontend:v1.0.0
  - All images pushed successfully

- [x] **Step 5: Images Verified**
  - 2 repositories created
  - 4 total tags (2 per image)
  - Images accessible from ACR
  - Pull commands ready

### Verification Commands Summary

```bash
# Verify registry exists
az acr list --resource-group rg-taskapp-prod --output table

# Verify repositories
az acr repository list --name YOUR-REGISTRY-NAME --output table

# Verify backend tags
az acr repository show-tags --name YOUR-REGISTRY-NAME --repository taskapp-backend --output table

# Verify frontend tags
az acr repository show-tags --name YOUR-REGISTRY-NAME --repository taskapp-frontend --output table

# Get image references (save these for Phase 6-7)
echo "Backend Image: ${REGISTRY_NAME}.azurecr.io/taskapp-backend:latest"
echo "Frontend Image: ${REGISTRY_NAME}.azurecr.io/taskapp-frontend:latest"
```

### Save Image References

**Create a reference file for Phase 6-7:**

```bash
cat > azure/config/container-images.txt << EOF
Container Image References
==========================

Backend Image:
${REGISTRY_NAME}.azurecr.io/taskapp-backend:latest
${REGISTRY_NAME}.azurecr.io/taskapp-backend:v1.0.0

Frontend Image:
${REGISTRY_NAME}.azurecr.io/taskapp-frontend:latest
${REGISTRY_NAME}.azurecr.io/taskapp-frontend:v1.0.0

Registry Login Server:
${REGISTRY_NAME}.azurecr.io

Note: Use these references when deploying Container Apps in Phase 6-7

Created: $(date)
EOF

echo "✅ Image references saved to azure/config/container-images.txt"
```

### Cost Summary for Phase 4

- **Azure Container Registry (Basic)**: ~$5/month
- **Storage Used**: ~0.7 GB of 10 GB limit
- **Data Transfer**: First 100 GB free, then $0.087/GB

**Total Phase 4 Cost**: ~$5/month ✅

### Resources Created

| Resource | Type | Location | Status |
|----------|------|----------|--------|
| YOUR-REGISTRY-NAME | Container Registry | Central US | ✅ Created |
| taskapp-backend | Repository | ACR | ✅ 2 tags |
| taskapp-frontend | Repository | ACR | ✅ 2 tags |

### Overall Progress

**Completed Phases:**
- ✅ Phase 1: Account Setup (Complete)
- ✅ Phase 2: Networking (Complete)
- ✅ Phase 3: Database (Complete)
- ✅ Phase 4: Container Registry (Complete)

**Progress**: 4/13 phases (30.8%) 🎉

---

## Next Steps: Phase 5 - Azure Key Vault

With your container images ready in ACR, you're prepared to:
1. Create Azure Key Vault
2. Store database credentials securely
3. Generate JWT secret key
4. Set up managed identity access
5. Prepare for Container Apps deployment

**Estimated Time**: 1-2 hours  
**Cost**: ~$0.03/secret (~$0.12/month total)

**Why Phase 5 Before Phase 6?**  
Container Apps will need to access database credentials and JWT secrets. By storing them in Key Vault first, we can configure Container Apps to pull secrets securely using managed identities (no hardcoded passwords!).

Ready to proceed? Let's move to Phase 5! 🔐

---

## Troubleshooting

### Issue: "az acr login" fails

**Error:** `An error occurred: DOCKER_COMMAND_ERROR`

**Solutions:**
```bash
# 1. Verify Docker is running
docker --version
docker ps

# 2. Restart Docker Desktop (Windows/Mac)

# 3. Use admin credentials instead
az acr credential show --name YOUR-REGISTRY-NAME --resource-group rg-taskapp-prod
# Then use docker login manually
```

### Issue: "docker push" is very slow

**Possible causes:**
- Large image size
- Slow internet connection
- Many layers to upload

**Solutions:**
```bash
# 1. Check image size
docker images | grep taskapp

# 2. Optimize Dockerfile (add .dockerignore)
# 3. Use a wired connection instead of WiFi
# 4. Push during off-peak hours
```

### Issue: "Repository not found"

**Error when pulling:** `repository does not exist or may require 'docker login'`

**Solutions:**
```bash
# 1. Verify repository exists
az acr repository list --name YOUR-REGISTRY-NAME

# 2. Check spelling of image name
# 3. Re-authenticate
az acr login --name YOUR-REGISTRY-NAME

# 4. Verify admin user is enabled
az acr show --name YOUR-REGISTRY-NAME --query adminUserEnabled
```

### Issue: Image tag already exists

**Want to push updated image with same tag:**

```bash
# Option 1: Delete old tag (not recommended for production)
az acr repository delete \
  --name YOUR-REGISTRY-NAME \
  --image taskapp-backend:latest \
  --yes

# Option 2: Use new version tag (recommended)
docker tag taskapp-backend:latest ${REGISTRY_NAME}.azurecr.io/taskapp-backend:v1.0.1
docker push ${REGISTRY_NAME}.azurecr.io/taskapp-backend:v1.0.1
```

### Issue: Running out of storage

**Basic tier: 10 GB limit**

**Check storage usage:**
```bash
# Get total storage used
az acr show-usage --name YOUR-REGISTRY-NAME --output table
```

**Clean up old images:**
```bash
# Delete old tags
az acr repository delete \
  --name YOUR-REGISTRY-NAME \
  --image taskapp-backend:old-tag \
  --yes

# Or upgrade to Standard tier (100 GB)
az acr update --name YOUR-REGISTRY-NAME --sku Standard
```

---

## Additional Resources

### Useful ACR Commands

```bash
# Show ACR details
az acr show --name YOUR-REGISTRY-NAME --output json

# Show storage usage
az acr show-usage --name YOUR-REGISTRY-NAME --output table

# List all tags for an image
az acr repository show-tags --name YOUR-REGISTRY-NAME --repository taskapp-backend

# Get image manifest
az acr repository show-manifests --name YOUR-REGISTRY-NAME --repository taskapp-backend

# Delete a specific tag
az acr repository delete --name YOUR-REGISTRY-NAME --image taskapp-backend:v1.0.0 --yes

# Delete entire repository
az acr repository delete --name YOUR-REGISTRY-NAME --repository taskapp-backend --yes

# Enable/disable admin user
az acr update --name YOUR-REGISTRY-NAME --admin-enabled true|false
```

### Docker Best Practices

**1. Use .dockerignore:**
```
node_modules
.git
.env
*.md
.vscode
__pycache__
*.pyc
.pytest_cache
htmlcov
```

**2. Multi-stage builds** (reduce image size):
```dockerfile
# Example for Node.js
FROM node:18 AS builder
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

FROM node:18-alpine
WORKDIR /app
COPY --from=builder /app/.next ./.next
COPY --from=builder /app/public ./public
CMD ["npm", "start"]
```

**3. Tag with versions:**
```bash
# Always tag with specific versions
docker tag app:latest registry.azurecr.io/app:v1.2.3
docker tag app:latest registry.azurecr.io/app:latest
```

### Security Best Practices

1. **Disable admin user in production:**
   ```bash
   az acr update --name YOUR-REGISTRY-NAME --admin-enabled false
   ```

2. **Use managed identities** (Phase 6-7)

3. **Enable vulnerability scanning:**
   ```bash
   # Requires Microsoft Defender for Cloud (additional cost)
   az security atp storage update --is-enabled true
   ```

4. **Use Azure RBAC** instead of admin credentials

5. **Enable audit logging** via Azure Monitor

---

## Summary

**Phase 4 Complete!** 🎉

You now have:
- ✅ Azure Container Registry with Basic tier
- ✅ Backend and frontend images stored in ACR
- ✅ Multiple tags (latest, v1.0.0) for version control
- ✅ Images ready to deploy to Container Apps
- ✅ Registry authenticated and tested

**Cost**: ~$5/month for ACR Basic tier  
**Storage Used**: ~0.7 GB of 10 GB  
**Next**: Phase 5 - Azure Key Vault for secure secrets management

**Key Takeaways:**
- ACR is your private Docker registry in Azure
- Images are secure and only accessible with authentication
- Container Apps will pull images directly from ACR
- Version tags help track deployments

Ready for Phase 5? 🚀
