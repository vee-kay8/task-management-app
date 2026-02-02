# Azure Phase 6: Backend Deployment - Complete Guide

**Duration**: 2-3 hours  
**Difficulty**: Intermediate  
**Prerequisites**: Phase 1-5 complete (Account, VNet, Database, Container Registry, Key Vault)  
**Goal**: Deploy backend application using Azure Container Apps

---

## 📋 Overview

This phase deploys your Flask backend application to Azure Container Apps. By the end, you'll have:

✅ Container Apps Environment created  
✅ Backend Container App running  
✅ Managed identity configured  
✅ Key Vault integration working  
✅ Database connectivity verified  
✅ Backend API accessible  
✅ Logging and monitoring enabled  

**Why Container Apps?** Azure Container Apps is a serverless platform for running containerized applications. It handles scaling, load balancing, and infrastructure management automatically.

---

## Table of Contents

1. [Understanding Azure Container Apps](#understanding-azure-container-apps)
2. [Create Container Apps Environment](#step-1-create-container-apps-environment)
3. [Create Backend Container App](#step-2-create-backend-container-app)
4. [Configure Managed Identity](#step-3-configure-managed-identity)
5. [Configure Environment Variables](#step-4-configure-environment-variables)
6. [Test Backend Deployment](#step-5-test-backend-deployment)
7. [Verify Database Connectivity](#step-6-verify-database-connectivity)
8. [Phase 6 Completion Checklist](#phase-6-completion-checklist)

---

## Understanding Azure Container Apps

### What is Azure Container Apps? 🚀

**Azure Container Apps** is a fully managed serverless platform for running containerized applications. It's built on Kubernetes but abstracts away the complexity.

**AWS Equivalent:** ECS Fargate (serverless containers)

### Why Use Container Apps?

| Feature | Benefit |
|---------|---------|
| **Serverless** | No server management, auto-scaling |
| **Cost-Effective** | Pay only for what you use (consumption-based) |
| **Simple** | Easier than AKS (Azure Kubernetes Service) |
| **Built-in Features** | Load balancing, HTTPS, traffic splitting |
| **Microservices** | Perfect for microservices architecture |
| **Integration** | Works seamlessly with ACR, Key Vault, VNet |

### Container Apps Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│  Container Apps Environment (env-taskapp-prod)                  │
│  • Shared infrastructure for multiple container apps           │
│  • Log Analytics workspace for monitoring                      │
│  • VNet integration for private networking                     │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │  Backend Container App (ca-taskapp-backend)                │ │
│  │                                                            │ │
│  │  📦 Container:                                             │ │
│  │     Image: taskappacr2026.azurecr.io/taskapp-backend      │ │
│  │     Port: 5000                                            │ │
│  │                                                            │ │
│  │  🔐 Managed Identity:                                      │ │
│  │     • Authenticates to Key Vault                          │ │
│  │     • Pulls images from ACR                               │ │
│  │                                                            │ │
│  │  🔑 Secrets (from Key Vault):                             │ │
│  │     • db-host                                             │ │
│  │     • db-name                                             │ │
│  │     • db-user                                             │ │
│  │     • db-password                                         │ │
│  │     • jwt-secret-key                                      │ │
│  │                                                            │ │
│  │  🌐 Ingress:                                               │ │
│  │     • External (accessible from internet)                 │ │
│  │     • HTTPS enabled                                       │ │
│  │     • Target port: 5000                                   │ │
│  │                                                            │ │
│  │  📊 Scaling:                                               │ │
│  │     • Min replicas: 1                                     │ │
│  │     • Max replicas: 3                                     │ │
│  │     • Auto-scale based on HTTP requests                   │ │
│  └────────────────────────────────────────────────────────────┘ │
│                                                                  │
│  Future: Frontend Container App (Phase 7)                       │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### Container Apps vs Other Azure Services

| Service | Use Case | Complexity | Cost |
|---------|----------|------------|------|
| **Container Apps** | Microservices, APIs, background jobs | Low | $$ |
| **App Service** | Traditional web apps, single container | Low | $$$ |
| **AKS** | Complex Kubernetes workloads | High | $$$$ |
| **Container Instances** | Simple one-off containers | Very Low | $ |

> 💡 **For This Project**: Container Apps is perfect - serverless, simple, cost-effective.

### Key Concepts

#### 1. **Container Apps Environment**

A boundary that groups one or more container apps. Apps in the same environment:
- Share the same VNet
- Share the same Log Analytics workspace
- Can communicate internally

**You'll create one environment** for both backend and frontend (Phase 7).

#### 2. **Managed Identity**

A secure way for Container Apps to authenticate to other Azure services:
- **System-assigned**: Created automatically with the container app
- **User-assigned**: Created separately and assigned to multiple apps

**We'll use system-assigned** (simpler, automatically tied to the app lifecycle).

```
Container App → Managed Identity → Key Vault
                                 → ACR
                                 → Database
```

#### 3. **Ingress**

How external traffic reaches your container app:
- **External**: Accessible from internet (public endpoint)
- **Internal**: Only accessible within VNet (private)

**Backend**: External (so frontend can call it)  
**Frontend** (Phase 7): External (so users can access it)

#### 4. **Revisions**

Each deployment creates a new revision:
- **Multiple revisions** can run simultaneously
- **Traffic splitting** between revisions (blue/green deployments)
- **Rollback** to previous revision

#### 5. **Scaling**

Container Apps auto-scale based on:
- HTTP requests
- CPU usage
- Custom metrics

**Default for this project**: 1-3 replicas based on HTTP traffic.

---

## Prerequisites

### 1. Verify Phase 1-5 Resources

```bash
# Check Resource Group exists
az group show --name rg-taskapp-prod --query "{Name:name, Location:location}" --output table

# Check Container Registry exists
az acr show --name taskappacr2026 --query "{Name:name, LoginServer:loginServer}" --output table

# Check Key Vault exists
az keyvault show --name kv-taskapp-2026 --query "{Name:name, VaultUri:properties.vaultUri}" --output table

# Check Database exists
az postgres flexible-server show --name taskapp-db-88 --resource-group rg-taskapp-prod --query "{Name:name, State:state}" --output table

# Verify backend image exists in ACR
az acr repository show-tags --name taskappacr2026 --repository taskapp-backend --output table
```

**Expected**: All commands return valid data ✅

### 2. Install Container Apps Extension

```bash
# Install the Container Apps extension for Azure CLI
az extension add --name containerapp --upgrade

# Verify installation
az containerapp --version
```

**Expected output**: `containerapp 0.x.x` or higher

### 3. Register Microsoft.App Namespace

```bash
# Register the Container Apps namespace (if not already registered)
az provider register --namespace Microsoft.App

# Check registration status (may take 2-3 minutes)
az provider show --namespace Microsoft.App --query "registrationState" --output tsv
```

**Expected output**: `Registered` ✅

If it shows `Registering`, wait 2-3 minutes and check again.

---

## Step 1: Create Container Apps Environment

### What You're Creating

A Container Apps Environment that will host your backend and frontend apps. It includes:
- **Log Analytics workspace** (for monitoring and logs)
- **VNet integration** (optional - we'll skip for simplicity)
- **Shared infrastructure** for all apps

### Option A: Console (Azure Portal) Method

**Step-by-step:**

1. **Navigate to Container Apps**
   - Go to Azure Portal: https://portal.azure.com
   - Search for **"Container Apps"** in the top search bar
   - Click **"Container Apps"** service
   - Click **"+ Create"**

2. **Basics Tab - Create Environment**
   - **Subscription**: Azure subscription 1
   - **Resource group**: rg-taskapp-prod
   - Click **"Create new"** under Container Apps Environment
   
3. **Create Environment - Basics**
   - **Environment name**: env-taskapp-prod
   - **Region**: Central US
   - **Zone redundancy**: Disabled (saves cost)
   - Click **"Next: Monitoring"**

4. **Create Environment - Monitoring**
   - **Log Analytics workspace**: Create new
   - **Workspace name**: law-taskapp-prod (or auto-generated)
   - Click **"Create"**

5. **Wait for Environment Creation**
   - Takes 2-3 minutes ⏳
   - You'll return to the Container App creation (we'll do this via CLI)
   - Click **"Cancel"** for now

### Option B: CLI Method (Recommended)

**Create the environment:**

```bash
# Create Container Apps Environment with Log Analytics
az containerapp env create \
  --name env-taskapp-prod \
  --resource-group rg-taskapp-prod \
  --location centralus \
  --tags Environment=Production Project=TaskApp ManagedBy=Manual CostCenter=Learning
```

**This command will take 2-3 minutes** ⏳

It automatically creates:
- Container Apps Environment
- Log Analytics workspace (for logs and monitoring)

**Expected output:**
```json
{
  "id": "/subscriptions/.../resourceGroups/rg-taskapp-prod/providers/Microsoft.App/managedEnvironments/env-taskapp-prod",
  "location": "centralus",
  "name": "env-taskapp-prod",
  "properties": {
    "defaultDomain": "...",
    "provisioningState": "Succeeded",
    "staticIp": "..."
  },
  "type": "Microsoft.App/managedEnvironments"
}
```

**Key fields to note:**
- **`defaultDomain`**: The base domain for your apps (e.g., `nicegrass-12345678.centralus.azurecontainerapps.io`)
- **`provisioningState`**: "Succeeded" ✅

### Verify Environment Creation

```bash
# List Container Apps Environments
az containerapp env list --resource-group rg-taskapp-prod --output table

# Expected output:
# Location    Name                ResourceGroup
# ----------  ------------------  ---------------
# centralus   env-taskapp-prod    rg-taskapp-prod
```

**Get the default domain:**

```bash
az containerapp env show \
  --name env-taskapp-prod \
  --resource-group rg-taskapp-prod \
  --query properties.defaultDomain \
  --output tsv
```

**Expected output**: Something like `nicegrass-12345678.centralus.azurecontainerapps.io`

### What Just Happened? 🤔

- **Environment Created**: Isolated boundary for your container apps
- **Log Analytics Workspace**: Auto-created for logging and monitoring
- **Default Domain**: Your apps will get subdomains of this (e.g., `backend.nicegrass-12345678.centralus.azurecontainerapps.io`)
- **Ready for Apps**: Can now deploy backend and frontend containers

---

## Step 2: Create Backend Container App

### What You're Creating

A Container App that runs your Flask backend container from ACR. It will:
- Pull the image from `taskappacr2026.azurecr.io/taskapp-backend:latest`
- Enable system-assigned managed identity
- Configure ingress on port 5000
- Auto-scale based on traffic

### Set Variables for Easy Reference

```bash
# Set variables (copy/paste all together)
RESOURCE_GROUP="rg-taskapp-prod"
ENVIRONMENT="env-taskapp-prod"
APP_NAME="ca-taskapp-backend"
ACR_NAME="taskappacr2026"
IMAGE="taskappacr2026.azurecr.io/taskapp-backend:latest"
```

### Create the Backend Container App

```bash
# Create backend Container App
az containerapp create \
  --name $APP_NAME \
  --resource-group $RESOURCE_GROUP \
  --environment $ENVIRONMENT \
  --image $IMAGE \
  --registry-server "${ACR_NAME}.azurecr.io" \
  --target-port 5000 \
  --ingress external \
  --min-replicas 1 \
  --max-replicas 3 \
  --cpu 0.5 \
  --memory 1.0Gi \
  --system-assigned \
  --tags Environment=Production Project=TaskApp Component=Backend
```

**⏰ This command will take 3-5 minutes** - Container Apps needs to:
1. Create the app
2. Enable managed identity
3. Pull the image from ACR (first pull takes longer)
4. Start the container
5. Configure ingress

**Command Explanation:**

| Parameter | Value | Why |
|-----------|-------|-----|
| `--name` | ca-taskapp-backend | Name of the container app |
| `--environment` | env-taskapp-prod | The environment we created in Step 1 |
| `--image` | taskappacr2026.azurecr.io/taskapp-backend:latest | Image from ACR |
| `--registry-server` | taskappacr2026.azurecr.io | ACR login server |
| `--target-port` | 5000 | Port Flask listens on |
| `--ingress external` | External access | Accessible from internet |
| `--min-replicas` | 1 | Always have at least 1 instance |
| `--max-replicas` | 3 | Scale up to 3 instances max |
| `--cpu` | 0.5 | 0.5 CPU cores per replica |
| `--memory` | 1.0Gi | 1 GB RAM per replica |
| `--system-assigned` | Enable managed identity | For Key Vault access |

**Expected output:**
```json
{
  "id": "/subscriptions/.../resourceGroups/rg-taskapp-prod/providers/Microsoft.App/containerApps/ca-taskapp-backend",
  "location": "centralus",
  "name": "ca-taskapp-backend",
  "properties": {
    "configuration": {
      "ingress": {
        "external": true,
        "fqdn": "ca-taskapp-backend.nicegrass-12345678.centralus.azurecontainerapps.io",
        "targetPort": 5000
      }
    },
    "provisioningState": "Succeeded"
  },
  "systemData": {
    "createdAt": "2026-01-29T..."
  }
}
```

**Key fields to note:**
- **`fqdn`**: Your backend URL (e.g., `ca-taskapp-backend.nicegrass-12345678.centralus.azurecontainerapps.io`)
- **`provisioningState`**: "Succeeded" ✅

### Save the Backend URL

```bash
# Get the backend URL
BACKEND_URL=$(az containerapp show \
  --name $APP_NAME \
  --resource-group $RESOURCE_GROUP \
  --query properties.configuration.ingress.fqdn \
  --output tsv)

echo "Backend URL: https://${BACKEND_URL}"

# Save to file
cat > azure/config/backend-url.txt << EOF
Backend Container App URL
==========================
Container App Name: ca-taskapp-backend
URL: https://${BACKEND_URL}
Environment: env-taskapp-prod
Resource Group: rg-taskapp-prod

Created: $(date)

Note: This URL will be used by the frontend in Phase 7.
EOF

echo "✅ Backend URL saved to azure/config/backend-url.txt"
```

### Verify Container App Creation

```bash
# List all container apps
az containerapp list --resource-group $RESOURCE_GROUP --output table

# Check backend app status
az containerapp show \
  --name $APP_NAME \
  --resource-group $RESOURCE_GROUP \
  --query "{Name:name, Status:properties.provisioningState, URL:properties.configuration.ingress.fqdn}" \
  --output table
```

**Expected output:**
```
Name                 Status     URL
-------------------  ---------  ------------------------------------------------
ca-taskapp-backend   Succeeded  ca-taskapp-backend.nicegrass-12345678.centralus.azurecontainerapps.io
```

### What Just Happened? 🤔

- **Container App Created**: Flask backend is now running in Azure
- **Managed Identity**: System-assigned identity created automatically
- **Public Endpoint**: Backend is accessible at `https://BACKEND_URL`
- **Auto-Scaling**: Will scale 1-3 replicas based on traffic
- **Image Pulled**: Container image downloaded from ACR

---

## Step 3: Configure Managed Identity

### What You're Doing

Granting the backend's managed identity access to:
1. **Azure Container Registry (ACR)**: To pull images
2. **Azure Key Vault**: To read secrets

### Step 3A: Grant ACR Access

The managed identity needs permission to pull images from ACR.

```bash
# Get the managed identity principal ID
PRINCIPAL_ID=$(az containerapp show \
  --name $APP_NAME \
  --resource-group $RESOURCE_GROUP \
  --query identity.principalId \
  --output tsv)

echo "Managed Identity Principal ID: $PRINCIPAL_ID"

# Get ACR resource ID
ACR_ID=$(az acr show --name $ACR_NAME --query id --output tsv)

# Assign AcrPull role to the managed identity
az role assignment create \
  --assignee $PRINCIPAL_ID \
  --role AcrPull \
  --scope $ACR_ID

echo "✅ Granted AcrPull permission to managed identity"
```

**Expected output:**
```json
{
  "principalId": "...",
  "principalType": "ServicePrincipal",
  "roleDefinitionName": "AcrPull",
  "scope": "/subscriptions/.../resourceGroups/rg-taskapp-prod/providers/Microsoft.ContainerRegistry/registries/taskappacr2026"
}
```

### Step 3B: Grant Key Vault Access

The managed identity needs permission to read secrets from Key Vault.

```bash
# Set Key Vault name
VAULT_NAME="kv-taskapp-2026"

# Get Key Vault resource ID
VAULT_ID=$(az keyvault show --name $VAULT_NAME --query id --output tsv)

# Assign Key Vault Secrets User role to the managed identity
az role assignment create \
  --assignee $PRINCIPAL_ID \
  --role "Key Vault Secrets User" \
  --scope $VAULT_ID

echo "✅ Granted Key Vault Secrets User permission to managed identity"
```

**Expected output:**
```json
{
  "principalId": "...",
  "principalType": "ServicePrincipal",
  "roleDefinitionName": "Key Vault Secrets User",
  "scope": "/subscriptions/.../resourceGroups/rg-taskapp-prod/providers/Microsoft.KeyVault/vaults/kv-taskapp-2026"
}
```

### Verify Role Assignments

```bash
# List all role assignments for the managed identity
az role assignment list \
  --assignee $PRINCIPAL_ID \
  --query "[].{Role:roleDefinitionName, Scope:scope}" \
  --output table
```

**Expected output:**
```
Role                      Scope
------------------------  -------------------------------------------------------
AcrPull                   /subscriptions/.../registries/taskappacr2026
Key Vault Secrets User    /subscriptions/.../vaults/kv-taskapp-2026
```

You should see both roles assigned! ✅

### What Just Happened? 🤔

- **ACR Access**: Backend can now pull updated images from ACR (for future deployments)
- **Key Vault Access**: Backend can now read secrets from Key Vault
- **No Passwords**: All authentication happens via managed identity (no credentials stored)

---

## Step 4: Configure Environment Variables

### What You're Doing

Configuring the backend to:
1. Load secrets from Key Vault
2. Set Flask configuration
3. Connect to PostgreSQL database

### Understanding Key Vault References

Container Apps supports **Key Vault references** - instead of copying secret values, you reference them:

```yaml
secrets:
  - name: db-password
    keyVaultUrl: https://kv-taskapp-2026.vault.azure.net/secrets/db-password
    identity: system
```

This tells Container Apps:
- Use system-assigned managed identity
- Fetch the secret value from Key Vault
- Inject it as a secret named `db-password`

### Configure Secrets from Key Vault

```bash
# Update Container App with Key Vault secret references
az containerapp update \
  --name $APP_NAME \
  --resource-group $RESOURCE_GROUP \
  --set-env-vars \
    "FLASK_ENV=production" \
    "FLASK_APP=run.py" \
    "LOG_LEVEL=INFO" \
  --secrets \
    "db-host=keyvaultref:https://${VAULT_NAME}.vault.azure.net/secrets/db-host,identityref:system" \
    "db-name=keyvaultref:https://${VAULT_NAME}.vault.azure.net/secrets/db-name,identityref:system" \
    "db-user=keyvaultref:https://${VAULT_NAME}.vault.azure.net/secrets/db-user,identityref:system" \
    "db-password=keyvaultref:https://${VAULT_NAME}.vault.azure.net/secrets/db-password,identityref:system" \
    "jwt-secret=keyvaultref:https://${VAULT_NAME}.vault.azure.net/secrets/jwt-secret-key,identityref:system"
```

**⏰ This command will take 1-2 minutes** - Container Apps needs to:
1. Fetch secrets from Key Vault
2. Create a new revision
3. Deploy the new revision
4. Health check the new revision

**Expected output:**
```json
{
  "name": "ca-taskapp-backend",
  "properties": {
    "configuration": {
      "secrets": [
        {
          "identity": "system",
          "keyVaultUrl": "https://kv-taskapp-2026.vault.azure.net/secrets/db-host",
          "name": "db-host"
        },
        ...
      ]
    }
  }
}
```

### Set Environment Variables Referencing Secrets

Now we need to set environment variables that use these secrets:

```bash
# Build DATABASE_URL from individual secrets
az containerapp update \
  --name $APP_NAME \
  --resource-group $RESOURCE_GROUP \
  --replace-env-vars \
    "FLASK_ENV=production" \
    "FLASK_APP=run.py" \
    "LOG_LEVEL=INFO" \
    "DB_HOST=secretref:db-host" \
    "DB_NAME=secretref:db-name" \
    "DB_USER=secretref:db-user" \
    "DB_PASSWORD=secretref:db-password" \
    "JWT_SECRET_KEY=secretref:jwt-secret" \
    "DATABASE_URL=postgresql://\$(DB_USER):\$(DB_PASSWORD)@\$(DB_HOST)/\$(DB_NAME)?sslmode=require"
```

**Wait, that won't work!** Container Apps doesn't support variable interpolation in environment variables.

**Alternative approach:** We'll need to modify the backend code to build the DATABASE_URL from individual variables, OR create a pre-built DATABASE_URL secret in Key Vault.

### Option 1: Create DATABASE_URL Secret in Key Vault (Recommended)

```bash
# Build the connection string locally
DB_HOST_VAL=$(az keyvault secret show --vault-name $VAULT_NAME --name db-host --query value -o tsv)
DB_NAME_VAL=$(az keyvault secret show --vault-name $VAULT_NAME --name db-name --query value -o tsv)
DB_USER_VAL=$(az keyvault secret show --vault-name $VAULT_NAME --name db-user --query value -o tsv)
DB_PASS_VAL=$(az keyvault secret show --vault-name $VAULT_NAME --name db-password --query value -o tsv)

# Create DATABASE_URL secret
DATABASE_URL="postgresql://${DB_USER_VAL}:${DB_PASS_VAL}@${DB_HOST_VAL}/${DB_NAME_VAL}?sslmode=require"

# Store in Key Vault
az keyvault secret set \
  --vault-name $VAULT_NAME \
  --name database-url \
  --value "$DATABASE_URL"

echo "✅ Created DATABASE_URL secret in Key Vault"
```

### Update Container App with DATABASE_URL

```bash
# Add DATABASE_URL secret reference
az containerapp secret set \
  --name $APP_NAME \
  --resource-group $RESOURCE_GROUP \
  --secrets \
    "database-url=keyvaultref:https://${VAULT_NAME}.vault.azure.net/secrets/database-url,identityref:system" \
    "jwt-secret=keyvaultref:https://${VAULT_NAME}.vault.azure.net/secrets/jwt-secret-key,identityref:system"

# Set environment variables
az containerapp update \
  --name $APP_NAME \
  --resource-group $RESOURCE_GROUP \
  --replace-env-vars \
    "FLASK_ENV=production" \
    "FLASK_APP=run.py" \
    "LOG_LEVEL=INFO" \
    "DATABASE_URL=secretref:database-url" \
    "JWT_SECRET_KEY=secretref:jwt-secret"
```

**⏰ This will take 1-2 minutes** - new revision being deployed.

### Verify Environment Variables

```bash
# Check environment variables (secrets won't show values)
az containerapp show \
  --name $APP_NAME \
  --resource-group $RESOURCE_GROUP \
  --query "properties.template.containers[0].env" \
  --output table
```

**Expected output:**
```
Name           SecretRef      Value
-------------  -------------  ----------
FLASK_ENV                     production
FLASK_APP                     run.py
LOG_LEVEL                     INFO
DATABASE_URL   database-url
JWT_SECRET_KEY jwt-secret
```

### What Just Happened? 🤔

- **Secrets from Key Vault**: Container App now fetches secrets at runtime
- **No Hardcoded Values**: Secrets never stored in Container App configuration
- **Environment Variables**: Flask app receives DATABASE_URL and JWT_SECRET_KEY
- **New Revision**: Container restarted with new configuration

---

## Step 5: Test Backend Deployment

### What You're Testing

Verifying that:
1. Backend container is running
2. Health endpoint responds
3. API is accessible
4. No errors in logs

### Get the Backend URL

```bash
# Get backend URL
BACKEND_URL=$(az containerapp show \
  --name $APP_NAME \
  --resource-group $RESOURCE_GROUP \
  --query properties.configuration.ingress.fqdn \
  --output tsv)

echo "Backend URL: https://${BACKEND_URL}"
```

### Test Health Endpoint

```bash
# Test health endpoint
curl https://${BACKEND_URL}/api/health

# Or with verbose output
curl -v https://${BACKEND_URL}/api/health
```

**Expected successful output:**
```json
{
  "status": "healthy",
  "database": "connected",
  "timestamp": "2026-01-29T12:34:56.789Z"
}
```

**If you get an error:**
- `503 Service Unavailable`: Container is still starting (wait 30 seconds and retry)
- `502 Bad Gateway`: Container crashed (check logs - Step 5B)
- `Connection refused`: Ingress not configured properly

### Test API Root Endpoint

```bash
# Test API root
curl https://${BACKEND_URL}/api/

# Or pretty-printed
curl https://${BACKEND_URL}/api/ | jq
```

**Expected output:**
```json
{
  "message": "Task Management API",
  "version": "1.0.0",
  "endpoints": {
    "auth": "/api/auth",
    "users": "/api/users",
    "projects": "/api/projects",
    "tasks": "/api/tasks"
  }
}
```

### Check Container App Status

```bash
# Check app status
az containerapp show \
  --name $APP_NAME \
  --resource-group $RESOURCE_GROUP \
  --query "{Name:name, Status:properties.runningStatus, Replicas:properties.template.scale.minReplicas}" \
  --output table
```

**Expected output:**
```
Name                 Status   Replicas
-------------------  -------  ---------
ca-taskapp-backend   Running  1
```

### Check Revision Status

```bash
# List revisions
az containerapp revision list \
  --name $APP_NAME \
  --resource-group $RESOURCE_GROUP \
  --query "[].{Name:name, Active:properties.active, Replicas:properties.replicas, Created:properties.createdTime}" \
  --output table
```

**Expected output:**
```
Name                                  Active  Replicas  Created
------------------------------------  ------  --------  ------------------------
ca-taskapp-backend--abc123           True    1         2026-01-29T12:00:00+00:00
```

### View Logs

```bash
# View recent logs
az containerapp logs show \
  --name $APP_NAME \
  --resource-group $RESOURCE_GROUP \
  --tail 50

# Or follow logs in real-time
az containerapp logs show \
  --name $APP_NAME \
  --resource-group $RESOURCE_GROUP \
  --follow
```

**Expected log output (look for):**
```
 * Running on http://0.0.0.0:5000
 * Serving Flask app 'run.py'
 * Environment: production
Database connection successful
```

**Press Ctrl+C to exit follow mode.**

### What to Look For in Logs

**✅ Good signs:**
- `Running on http://0.0.0.0:5000`
- `Database connection successful`
- `Gunicorn` startup messages
- No error tracebacks

**❌ Bad signs:**
- `Error connecting to database`
- `KeyError` or `AttributeError`
- `Module not found`
- Repeated restarts

---

## Step 6: Verify Database Connectivity

### What You're Testing

Verifying that the backend can:
1. Connect to PostgreSQL database
2. Run database migrations
3. Create tables

### Check Backend Can Connect to Database

The health endpoint should have already tested this, but let's verify:

```bash
# Check health endpoint again
curl https://${BACKEND_URL}/api/health

# Look for "database": "connected"
```

### Run Database Migrations

Your Flask backend uses Flask-Migrate (Alembic) to manage database schema. The migrations should run automatically on first startup.

**Check if tables were created:**

We can't directly connect to the database (it's private), but we can check the backend logs:

```bash
# Search logs for migration messages
az containerapp logs show \
  --name $APP_NAME \
  --resource-group $RESOURCE_GROUP \
  --tail 100 | grep -i "migrat\|alembic\|table"
```

**Expected output (if migrations ran):**
```
INFO [alembic.runtime.migration] Running upgrade -> abc123, Initial migration
INFO [alembic.runtime.migration] Created table users
INFO [alembic.runtime.migration] Created table projects
INFO [alembic.runtime.migration] Created table tasks
```

### Test User Registration (Creates Database Entry)

Let's test that the backend can write to the database:

```bash
# Register a test user
curl -X POST https://${BACKEND_URL}/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "email": "test@example.com",
    "password": "Test123!@#"
  }'
```

**Expected successful output:**
```json
{
  "message": "User registered successfully",
  "user": {
    "id": 1,
    "username": "testuser",
    "email": "test@example.com",
    "created_at": "2026-01-29T12:34:56.789Z"
  },
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

**If successful**: ✅ Database connectivity is working!

### Test User Login

```bash
# Login with the test user
curl -X POST https://${BACKEND_URL}/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "password": "Test123!@#"
  }'
```

**Expected successful output:**
```json
{
  "message": "Login successful",
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "user": {
    "id": 1,
    "username": "testuser",
    "email": "test@example.com"
  }
}
```

### Troubleshooting Database Connection

**If you get database connection errors:**

**Error: "FATAL: no pg_hba.conf entry"**
- Database isn't allowing connections from Container Apps subnet
- Solution: Check that database has VNet integration enabled

**Error: "could not connect to server: Connection timed out"**
- Database is in private VNet, Container Apps can't reach it
- Solution: Container Apps needs VNet integration (advanced - we're skipping this for simplicity)

**Workaround for Learning:** Enable temporary public access on database:

```bash
# WARNING: This makes the database publicly accessible
# Only do this temporarily for learning/testing

# Add firewall rule to allow all IPs (temporary)
az postgres flexible-server firewall-rule create \
  --resource-group $RESOURCE_GROUP \
  --name taskapp-db-88 \
  --rule-name AllowAllIps \
  --start-ip-address 0.0.0.0 \
  --end-ip-address 255.255.255.255

echo "⚠️  Database is now publicly accessible (for testing only)"
echo "Remove this rule after Phase 7 testing!"
```

**After testing Phase 6-7, remove the rule:**
```bash
az postgres flexible-server firewall-rule delete \
  --resource-group $RESOURCE_GROUP \
  --name taskapp-db-88 \
  --rule-name AllowAllIps \
  --yes
```

---

## Phase 6 Completion Checklist

Use this checklist to verify everything is complete:

### ✅ Container Apps Environment

- [ ] Container Apps Environment created (env-taskapp-prod)
- [ ] Environment is in "Succeeded" state
- [ ] Log Analytics workspace created
- [ ] Default domain retrieved

### ✅ Backend Container App

- [ ] Backend Container App created (ca-taskapp-backend)
- [ ] App is in "Running" state
- [ ] Image pulled from ACR successfully
- [ ] Ingress configured (external, port 5000)
- [ ] Backend URL accessible

### ✅ Managed Identity & Permissions

- [ ] System-assigned managed identity enabled
- [ ] AcrPull role assigned (for ACR access)
- [ ] Key Vault Secrets User role assigned (for Key Vault access)
- [ ] Role assignments verified

### ✅ Environment Variables & Secrets

- [ ] DATABASE_URL secret created in Key Vault
- [ ] DATABASE_URL secret reference configured
- [ ] JWT_SECRET_KEY secret reference configured
- [ ] FLASK_ENV, FLASK_APP set correctly
- [ ] Environment variables verified

### ✅ Testing & Verification

- [ ] Health endpoint returns 200 OK
- [ ] API root endpoint returns JSON
- [ ] Logs show no errors
- [ ] Database connection successful
- [ ] User registration works (creates database entry)
- [ ] User login works (retrieves from database)

---

## Verification Commands

Run these commands to verify Phase 6 completion:

```bash
# Set variables
RESOURCE_GROUP="rg-taskapp-prod"
ENVIRONMENT="env-taskapp-prod"
APP_NAME="ca-taskapp-backend"
VAULT_NAME="kv-taskapp-2026"

# Verify Environment
az containerapp env show \
  --name $ENVIRONMENT \
  --resource-group $RESOURCE_GROUP \
  --query "{Name:name, Status:properties.provisioningState}" \
  --output table

# Verify Backend App
az containerapp show \
  --name $APP_NAME \
  --resource-group $RESOURCE_GROUP \
  --query "{Name:name, Status:properties.runningStatus, URL:properties.configuration.ingress.fqdn}" \
  --output table

# Verify Managed Identity Roles
PRINCIPAL_ID=$(az containerapp show --name $APP_NAME --resource-group $RESOURCE_GROUP --query identity.principalId -o tsv)
az role assignment list \
  --assignee $PRINCIPAL_ID \
  --query "[].{Role:roleDefinitionName}" \
  --output table

# Verify Secrets
az containerapp show \
  --name $APP_NAME \
  --resource-group $RESOURCE_GROUP \
  --query "properties.configuration.secrets[].name" \
  --output table

# Test Health Endpoint
BACKEND_URL=$(az containerapp show --name $APP_NAME --resource-group $RESOURCE_GROUP --query properties.configuration.ingress.fqdn -o tsv)
curl https://${BACKEND_URL}/api/health

# View Recent Logs
az containerapp logs show --name $APP_NAME --resource-group $RESOURCE_GROUP --tail 20
```

**Expected results:**
- ✅ Environment status: Succeeded
- ✅ App status: Running
- ✅ 2 roles: AcrPull, Key Vault Secrets User
- ✅ 2 secrets: database-url, jwt-secret
- ✅ Health endpoint: `{"status": "healthy"}`
- ✅ Logs: No errors

---

## Common Issues & Troubleshooting

### Issue 1: Container App Stuck in "Provisioning"

**Symptoms:**
```bash
az containerapp show --name ca-taskapp-backend --query properties.runningStatus
# Output: "Provisioning" (for more than 5 minutes)
```

**Causes:**
- Image pull failed (ACR authentication issue)
- Container crashes immediately on startup
- Resource limits too low

**Solutions:**

```bash
# Check revision provisioning state
az containerapp revision list \
  --name $APP_NAME \
  --resource-group $RESOURCE_GROUP \
  --query "[0].properties.provisioningState"

# Check replica status
az containerapp replica list \
  --name $APP_NAME \
  --resource-group $RESOURCE_GROUP \
  --revision $(az containerapp revision list --name $APP_NAME --resource-group $RESOURCE_GROUP --query "[0].name" -o tsv)

# View logs for errors
az containerapp logs show --name $APP_NAME --resource-group $RESOURCE_GROUP --tail 100
```

### Issue 2: Health Endpoint Returns 502 Bad Gateway

**Symptoms:**
```bash
curl https://ca-taskapp-backend.....azurecontainerapps.io/api/health
# Output: 502 Bad Gateway
```

**Causes:**
- Backend container not listening on port 5000
- Container crashed
- Flask not starting properly

**Solutions:**

```bash
# Check logs for startup errors
az containerapp logs show --name $APP_NAME --resource-group $RESOURCE_GROUP --tail 50

# Common errors to look for:
# - "ModuleNotFoundError" → Missing dependency in requirements.txt
# - "KeyError: DATABASE_URL" → Environment variable not set
# - "Connection refused" → Wrong port configuration
# - "Out of memory" → Increase memory limit
```

**Fix: Update resource limits**
```bash
az containerapp update \
  --name $APP_NAME \
  --resource-group $RESOURCE_GROUP \
  --cpu 1.0 \
  --memory 2.0Gi
```

### Issue 3: Database Connection Fails

**Symptoms:**
```json
{
  "status": "unhealthy",
  "database": "disconnected",
  "error": "could not connect to server"
}
```

**Causes:**
- Database is in private VNet, Container Apps can't reach it
- DATABASE_URL format is wrong
- Database password incorrect

**Solutions:**

**Option 1: Enable temporary public access (learning only)**
```bash
az postgres flexible-server firewall-rule create \
  --resource-group $RESOURCE_GROUP \
  --name taskapp-db-88 \
  --rule-name TempAllowAll \
  --start-ip-address 0.0.0.0 \
  --end-ip-address 255.255.255.255
```

**Option 2: Verify DATABASE_URL format**
```bash
# Check DATABASE_URL secret in Key Vault
az keyvault secret show \
  --vault-name $VAULT_NAME \
  --name database-url \
  --query value \
  --output tsv

# Expected format:
# postgresql://USER:PASSWORD@HOST/DATABASE?sslmode=require
```

**Option 3: Check database is running**
```bash
az postgres flexible-server show \
  --name taskapp-db-88 \
  --resource-group $RESOURCE_GROUP \
  --query "{Name:name, State:state}" \
  --output table
```

### Issue 4: Key Vault Access Denied

**Symptoms:**
```
Error: Forbidden - The user, group or application does not have secrets get permission
```

**Causes:**
- Managed identity doesn't have Key Vault Secrets User role
- RBAC permissions haven't propagated yet

**Solutions:**

```bash
# Re-assign Key Vault role
PRINCIPAL_ID=$(az containerapp show --name $APP_NAME --resource-group $RESOURCE_GROUP --query identity.principalId -o tsv)
VAULT_ID=$(az keyvault show --name $VAULT_NAME --query id -o tsv)

az role assignment create \
  --assignee $PRINCIPAL_ID \
  --role "Key Vault Secrets User" \
  --scope $VAULT_ID

# Wait 2-3 minutes for propagation
# Then restart the container app
az containerapp revision restart \
  --name $APP_NAME \
  --resource-group $RESOURCE_GROUP \
  --revision $(az containerapp revision list --name $APP_NAME --resource-group $RESOURCE_GROUP --query "[0].name" -o tsv)
```

---

## What You Learned

Congratulations! 🎉 You've completed Phase 6. Here's what you learned:

### Azure Concepts
- ✅ **Container Apps Environment** - Shared infrastructure for container apps
- ✅ **Container Apps** - Serverless container hosting
- ✅ **Managed Identity** - Password-less authentication
- ✅ **Ingress** - External vs internal access
- ✅ **Revisions** - Deployment versioning
- ✅ **Auto-scaling** - Automatic replica management

### Azure Skills
- ✅ Creating Container Apps environments
- ✅ Deploying containers from ACR
- ✅ Configuring managed identities
- ✅ Assigning RBAC roles
- ✅ Using Key Vault references
- ✅ Viewing container logs
- ✅ Testing API endpoints

### Backend Deployment
- ✅ Flask backend running in Azure
- ✅ Database connectivity working
- ✅ Secrets managed securely
- ✅ Auto-scaling configured
- ✅ HTTPS enabled automatically

### Comparison with AWS
| Task | Azure | AWS |
|------|-------|-----|
| Serverless containers | Container Apps | ECS Fargate |
| Managed identity | System-assigned identity | Task IAM Role |
| Secrets | Key Vault references | Secrets Manager |
| Logs | Log Analytics | CloudWatch Logs |
| Auto-scaling | Built-in | Target Tracking |

---

## Next: Phase 7 - Frontend Deployment

You're now ready to deploy the frontend Next.js application!

**Phase 7 Preview:**
- Create frontend Container App
- Configure environment variables (NEXT_PUBLIC_API_URL)
- Point frontend to backend URL
- Test complete application flow
- Configure custom domain (optional)
- Enable HTTPS

**First command in Phase 7:**
```bash
# Deploy frontend container app
az containerapp create \
  --name ca-taskapp-frontend \
  --resource-group rg-taskapp-prod \
  --environment env-taskapp-prod \
  --image taskappacr2026.azurecr.io/taskapp-frontend:latest \
  --target-port 3000 \
  --ingress external \
  --env-vars "NEXT_PUBLIC_API_URL=https://BACKEND_URL/api"
```

**Estimated time for Phase 7:** 1-2 hours

---

## Cost Summary

**Phase 6 Estimated Monthly Cost:**

| Resource | Cost |
|----------|------|
| Container Apps Environment | $0 (included) |
| Backend Container App (1 replica, 0.5 CPU, 1GB RAM) | ~$10-15/month |
| Log Analytics Workspace | ~$2-5/month (first 5GB free) |
| **Total Phase 6** | **~$12-20/month** |

**Total Project Cost So Far:**
- Phase 1-2: $0
- Phase 3: $0 (free for 12 months)
- Phase 4: $5/month (ACR)
- Phase 5: < $1/month (Key Vault)
- Phase 6: ~$15/month (Container Apps)
- **Total: ~$20/month** 💰

---

## Additional Resources

### Microsoft Learn
- [Azure Container Apps Documentation](https://learn.microsoft.com/en-us/azure/container-apps/)
- [Deploy your first container app](https://learn.microsoft.com/en-us/azure/container-apps/quickstart-portal)
- [Managed identities in Container Apps](https://learn.microsoft.com/en-us/azure/container-apps/managed-identity)

### Azure CLI Reference
- [az containerapp](https://learn.microsoft.com/en-us/cli/azure/containerapp)
- [az containerapp env](https://learn.microsoft.com/en-us/cli/azure/containerapp/env)
- [az containerapp logs](https://learn.microsoft.com/en-us/cli/azure/containerapp/logs)

---

**Phase 6 Complete!** 🎉

You now have:
- ✅ Backend API running in Azure Container Apps
- ✅ Database connectivity working
- ✅ Secrets managed via Key Vault
- ✅ Auto-scaling configured
- ✅ Managed identity authentication
- ✅ Ready to deploy frontend

**Next:** [AZURE_PHASE_7_GUIDE.md](AZURE_PHASE_7_GUIDE.md) - Frontend Deployment

---

*Last Updated: January 29, 2026*  
*Guide Version: 1.0*  
*Author: vee-kay8*
