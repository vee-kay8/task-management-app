# Azure Phase 7: Frontend Deployment - Complete Guide

**Duration**: 2-3 hours  
**Difficulty**: Intermediate  
**Prerequisites**: Phase 1-6 complete (Account, VNet, Database, ACR, Key Vault, Backend)  
**Goal**: Deploy Next.js frontend application using Azure Container Apps

---

## 📋 Overview

This phase deploys your Next.js frontend application to Azure Container Apps. By the end, you'll have:

✅ Frontend Container App running  
✅ Environment variables configured  
✅ Frontend connected to backend API  
✅ Public URL accessible  
✅ Complete application workflow tested  
✅ Logs and monitoring enabled  

**Why Same Container Apps Environment?** Deploying frontend in the same environment as backend allows internal communication, shared networking, and simplified management.

---

## Table of Contents

1. [Understanding Frontend Architecture](#understanding-frontend-architecture)
2. [Create Frontend Container App](#step-1-create-frontend-container-app)
3. [Configure Environment Variables](#step-2-configure-environment-variables)
4. [Test Frontend Deployment](#step-3-test-frontend-deployment)
5. [Verify Frontend-Backend Integration](#step-4-verify-frontend-backend-integration)
6. [Test Complete User Workflows](#step-5-test-complete-user-workflows)
7. [Phase 7 Completion Checklist](#phase-7-completion-checklist)

---

## Understanding Frontend Architecture

### What You're Deploying

```
┌──────────────────────────────────────────────────────────────────┐
│  Container Apps Environment (env-taskapp-prod)                   │
│  • Shared VNet integration                                       │
│  • Shared Log Analytics workspace                               │
│  • Default domain: redtree-99ec4a5a.centralus.azurecontainerapps.io │
├──────────────────────────────────────────────────────────────────┤
│                                                                   │
│  ┌─────────────────────────────────────────────────────────────┐ │
│  │  Backend Container App (ca-taskapp-backend) ✅ COMPLETE     │ │
│  │  URL: https://ca-taskapp-backend.redtree-99ec4a5a...        │ │
│  │  Port: 5000                                                 │ │
│  └─────────────────────────────────────────────────────────────┘ │
│                                                                   │
│  ┌─────────────────────────────────────────────────────────────┐ │
│  │  Frontend Container App (ca-taskapp-frontend) 🎯 THIS PHASE │ │
│  │                                                             │ │
│  │  📦 Container:                                              │ │
│  │     Image: taskappacr2026.azurecr.io/taskapp-frontend      │ │
│  │     Port: 3000                                             │ │
│  │                                                             │ │
│  │  🌐 Ingress:                                                │ │
│  │     • External (accessible from internet)                  │ │
│  │     • HTTPS enabled                                        │ │
│  │     • Target port: 3000                                    │ │
│  │                                                             │ │
│  │  🔧 Environment Variables:                                  │ │
│  │     • NEXT_PUBLIC_API_URL → Backend URL                    │ │
│  │     • NODE_ENV → production                                │ │
│  │                                                             │ │
│  │  📊 Scaling:                                                │ │
│  │     • Min replicas: 1                                      │ │
│  │     • Max replicas: 3                                      │ │
│  │     • Auto-scale based on HTTP requests                    │ │
│  └─────────────────────────────────────────────────────────────┘ │
│                                                                   │
└──────────────────────────────────────────────────────────────────┘
        ↓                                                    ↓
    BACKEND API                                         FRONTEND UI
    (Internal use)                                     (Public users)
```

### Traffic Flow

```
User Browser
    ↓ HTTPS
Frontend Container App (ca-taskapp-frontend)
    ↓ HTTPS API calls
Backend Container App (ca-taskapp-backend)
    ↓ Private VNet
PostgreSQL Database (taskapp-db-88)
```

### Key Concepts

#### 1. **Next.js in Production**

Next.js can run in two modes:
- **Development** (`npm run dev`): Hot reload, slower, debugging
- **Production** (`npm run start`): Optimized, faster, production-ready

**Our Docker image**: Already built for production with `npm run build && npm run start`

#### 2. **Environment Variables in Next.js**

Next.js has special rules for environment variables:

| Prefix | Where Available | Example |
|--------|----------------|---------|
| `NEXT_PUBLIC_*` | Client & Server | `NEXT_PUBLIC_API_URL` |
| No prefix | Server-only | `DATABASE_URL` |

**Frontend needs**: `NEXT_PUBLIC_API_URL` so the browser knows where to call the backend.

#### 3. **CORS Configuration**

Since frontend and backend are on different domains, CORS must be configured:
- **Backend CORS**: Allow requests from frontend domain
- **Frontend API calls**: Send credentials if needed

---

## Prerequisites

### 1. Verify Phase 6 Backend is Running

```bash
# Check backend Container App status
az containerapp show \
  --name ca-taskapp-backend \
  --resource-group rg-taskapp-prod \
  --query "{Name:name, Status:properties.runningStatus, URL:properties.configuration.ingress.fqdn}" \
  --output table
```

**Expected output**:
```
Name                 Status   URL
-------------------  -------  ------------------------------------------------
ca-taskapp-backend   Running  ca-taskapp-backend.redtree-99ec4a5a.centralus.azurecontainerapps.io
```

### 2. Get Backend URL

```bash
# Get backend URL
BACKEND_URL=$(az containerapp show \
  --name ca-taskapp-backend \
  --resource-group rg-taskapp-prod \
  --query properties.configuration.ingress.fqdn \
  --output tsv)

echo "Backend URL: https://${BACKEND_URL}"
```

**Expected**: `https://ca-taskapp-backend.redtree-99ec4a5a.centralus.azurecontainerapps.io`

### 3. Test Backend is Accessible

```bash
# Test backend health endpoint
curl https://${BACKEND_URL}/api/health
```

**Expected output**:
```json
{
  "status": "healthy",
  "service": "task-management-backend",
  "message": "Service is running"
}
```

### 4. Verify Frontend Image in ACR

```bash
# Check frontend image exists
az acr repository show-tags \
  --name taskappacr2026 \
  --repository taskapp-frontend \
  --output table
```

**Expected output**:
```
Result
--------
latest
v1.0.0
```

---

## Step 1: Create Frontend Container App

### What You're Creating

A Container App that runs your Next.js frontend container. It will:
- Pull the image from `taskappacr2026.azurecr.io/taskapp-frontend:latest`
- Run on port 3000
- Enable external ingress (public access)
- Auto-scale 1-3 replicas

### Set Variables

```bash
# Set variables for easy reference
RESOURCE_GROUP="rg-taskapp-prod"
ENVIRONMENT="env-taskapp-prod"
FRONTEND_APP="ca-taskapp-frontend"
ACR_NAME="taskappacr2026"
FRONTEND_IMAGE="taskappacr2026.azurecr.io/taskapp-frontend:latest"

# Get backend URL for environment variable
BACKEND_URL=$(az containerapp show \
  --name ca-taskapp-backend \
  --resource-group $RESOURCE_GROUP \
  --query properties.configuration.ingress.fqdn \
  --output tsv)

echo "Backend URL: https://${BACKEND_URL}"
```

### Create Frontend Container App

```bash
# Create frontend Container App
az containerapp create \
  --name $FRONTEND_APP \
  --resource-group $RESOURCE_GROUP \
  --environment $ENVIRONMENT \
  --image $FRONTEND_IMAGE \
  --registry-server ${ACR_NAME}.azurecr.io \
  --target-port 3000 \
  --ingress external \
  --min-replicas 1 \
  --max-replicas 3 \
  --cpu 0.5 \
  --memory 1.0Gi \
  --env-vars "NEXT_PUBLIC_API_URL=https://${BACKEND_URL}" "NODE_ENV=production" \
  --tags Environment=Production Project=TaskManagement Component=Frontend
```

**⏰ This command will take 3-5 minutes** - Container Apps needs to:
1. Create the app
2. Pull the image from ACR
3. Start the Next.js container
4. Configure ingress
5. Health check the container

**Command Explanation:**

| Parameter | Value | Why |
|-----------|-------|-----|
| `--name` | ca-taskapp-frontend | Name of the container app |
| `--environment` | env-taskapp-prod | Same environment as backend |
| `--image` | taskappacr2026.azurecr.io/taskapp-frontend:latest | Image from ACR |
| `--registry-server` | taskappacr2026.azurecr.io | ACR login server |
| `--target-port` | 3000 | Port Next.js listens on |
| `--ingress external` | External access | Accessible from internet |
| `--min-replicas` | 1 | Always have at least 1 instance |
| `--max-replicas` | 3 | Scale up to 3 instances max |
| `--cpu` | 0.5 | 0.5 CPU cores per replica |
| `--memory` | 1.0Gi | 1 GB RAM per replica |
| `--env-vars` | Environment variables | Backend URL and Node environment |

**Expected output:**
```json
{
  "id": "/subscriptions/.../containerApps/ca-taskapp-frontend",
  "name": "ca-taskapp-frontend",
  "properties": {
    "configuration": {
      "ingress": {
        "external": true,
        "fqdn": "ca-taskapp-frontend.redtree-99ec4a5a.centralus.azurecontainerapps.io",
        "targetPort": 3000
      }
    },
    "provisioningState": "Succeeded",
    "runningStatus": "Running"
  }
}
```

**Key fields to note:**
- **`fqdn`**: Your frontend URL (e.g., `ca-taskapp-frontend.redtree-99ec4a5a.centralus.azurecontainerapps.io`)
- **`provisioningState`**: "Succeeded" ✅
- **`runningStatus`**: "Running" ✅

### Save the Frontend URL

```bash
# Get the frontend URL
FRONTEND_URL=$(az containerapp show \
  --name $FRONTEND_APP \
  --resource-group $RESOURCE_GROUP \
  --query properties.configuration.ingress.fqdn \
  --output tsv)

echo "Frontend URL: https://${FRONTEND_URL}"

# Save to file for reference
cat > azure/config/frontend-url.txt << EOF
Frontend Container App URL
===========================
Container App Name: ca-taskapp-frontend
URL: https://${FRONTEND_URL}
Backend URL: https://${BACKEND_URL}
Environment: env-taskapp-prod
Resource Group: rg-taskapp-prod

Created: $(date)

This is your public application URL!
EOF

echo "✅ Frontend URL saved to azure/config/frontend-url.txt"
```

### Verify Container App Creation

```bash
# List all container apps
az containerapp list \
  --resource-group $RESOURCE_GROUP \
  --output table

# Expected output:
# Name                   Location    ResourceGroup     Status
# ---------------------  ----------  ----------------  --------
# ca-taskapp-backend     Central US  rg-taskapp-prod   Running
# ca-taskapp-frontend    Central US  rg-taskapp-prod   Running
```

---

## Step 2: Configure Environment Variables

### What You're Doing

Ensuring the frontend has the correct environment variables to connect to the backend API.

### Verify Environment Variables

```bash
# Check current environment variables
az containerapp show \
  --name $FRONTEND_APP \
  --resource-group $RESOURCE_GROUP \
  --query "properties.template.containers[0].env" \
  --output table
```

**Expected output**:
```
Name                    Value
----------------------  ---------------------------------------------------
NEXT_PUBLIC_API_URL     https://ca-taskapp-backend.redtree-99ec4a5a.centralus.azurecontainerapps.io
NODE_ENV                production
```

### Update Environment Variables (if needed)

If the backend URL changed or you need to update variables:

```bash
# Update environment variables
az containerapp update \
  --name $FRONTEND_APP \
  --resource-group $RESOURCE_GROUP \
  --replace-env-vars "NEXT_PUBLIC_API_URL=https://${BACKEND_URL}" "NODE_ENV=production"
```

**⏰ This will take 1-2 minutes** - new revision being deployed.

### Understanding NEXT_PUBLIC_API_URL

This variable tells the frontend (running in the user's browser) where to send API requests:

```javascript
// In frontend code (lib/api.ts or similar)
const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:5000'

// API calls go to:
fetch(`${API_URL}/api/auth/login`, { ... })
```

**Important**: The browser makes requests directly to the backend, not through the frontend server.

---

## Step 3: Test Frontend Deployment

### What You're Testing

Verifying that:
1. Frontend container is running
2. Next.js is serving the application
3. No errors in logs
4. Application loads in browser

### Get the Frontend URL

```bash
# Get frontend URL
FRONTEND_URL=$(az containerapp show \
  --name $FRONTEND_APP \
  --resource-group $RESOURCE_GROUP \
  --query properties.configuration.ingress.fqdn \
  --output tsv)

echo "Frontend URL: https://${FRONTEND_URL}"
echo "Open this URL in your browser!"
```

### Test Frontend Root Endpoint

```bash
# Test frontend root (should return HTML)
curl -I https://${FRONTEND_URL}

# Expected: HTTP/2 200
```

**Expected output**:
```
HTTP/2 200
content-type: text/html; charset=utf-8
...
```

### Check Container App Status

```bash
# Check frontend app status
az containerapp show \
  --name $FRONTEND_APP \
  --resource-group $RESOURCE_GROUP \
  --query "{Name:name, Status:properties.runningStatus, Replicas:properties.template.scale.minReplicas}" \
  --output table
```

**Expected output**:
```
Name                  Status   Replicas
--------------------  -------  ---------
ca-taskapp-frontend   Running  1
```

### View Logs

```bash
# View recent logs
az containerapp logs show \
  --name $FRONTEND_APP \
  --resource-group $RESOURCE_GROUP \
  --tail 50

# Or follow logs in real-time
az containerapp logs show \
  --name $FRONTEND_APP \
  --resource-group $RESOURCE_GROUP \
  --follow
```

**Expected log output (look for)**:
```
▲ Next.js 14.x.x
- Local:        http://0.0.0.0:3000
- Environment:  production

✓ Ready in XXXms
```

**Press Ctrl+C to exit follow mode.**

### Open Frontend in Browser

```bash
# Print the URL to open
echo "🌐 Open your frontend application:"
echo "https://${FRONTEND_URL}"
```

**Manually open this URL in your browser.**

**Expected**:
- ✅ Application loads successfully
- ✅ No console errors in browser DevTools (F12)
- ✅ Login/Register pages visible

---

## Step 4: Verify Frontend-Backend Integration

### What You're Testing

Verifying that the frontend can successfully communicate with the backend API.

### Test 1: Check API URL in Browser

1. **Open Frontend URL** in browser: `https://ca-taskapp-frontend.redtree-99ec4a5a.centralus.azurecontainerapps.io`

2. **Open Browser DevTools** (Press F12)

3. **Go to Console tab**

4. **Type this command**:
   ```javascript
   console.log(process.env.NEXT_PUBLIC_API_URL)
   ```

**Expected output**: The variable won't be accessible in console (it's only available during build). Instead, check network requests.

### Test 2: Register a New User

1. **Navigate to Register page** (usually `/register` or visible on homepage)

2. **Open DevTools → Network tab** (F12 → Network)

3. **Fill in registration form**:
   - Username: `azurefrontendtest`
   - Email: `azurefrontend@example.com`
   - Password: `AzureTest123!@#`
   - Full Name: `Azure Frontend Test`

4. **Click Register**

5. **Check Network tab**:
   - Look for request to: `https://ca-taskapp-backend.redtree-99ec4a5a.centralus.azurecontainerapps.io/api/auth/register`
   - Status should be: `200 OK` or `201 Created`
   - Response should contain user data and token

**Expected successful response**:
```json
{
  "message": "User registered successfully",
  "user": {
    "id": "...",
    "email": "azurefrontend@example.com",
    "full_name": "Azure Frontend Test"
  }
}
```

**If registration succeeds**: ✅ Frontend-backend integration is working!

### Test 3: Login with Created User

1. **Navigate to Login page**

2. **Enter credentials**:
   - Email: `azurefrontend@example.com`
   - Password: `AzureTest123!@#`

3. **Click Login**

4. **Check Network tab**:
   - Request to: `/api/auth/login`
   - Status: `200 OK`
   - Response contains `access_token`

5. **Verify redirect**: Should redirect to dashboard or home page (logged in state)

**If login succeeds**: ✅ Authentication flow is working!

### Test 4: Test Authenticated Requests

If you have a dashboard or protected routes:

1. **Navigate to Dashboard** (after logging in)

2. **Check Network tab**:
   - Requests should include `Authorization: Bearer <token>` header
   - Backend should return data (e.g., user's projects/tasks)

3. **Verify data loads**: Projects, tasks, or user data displays correctly

### Troubleshooting Frontend-Backend Issues

#### Issue: CORS Error in Browser Console

**Error message**:
```
Access to fetch at 'https://ca-taskapp-backend...' from origin 'https://ca-taskapp-frontend...'
has been blocked by CORS policy
```

**Solution**: Update backend CORS configuration to allow frontend domain.

**Run this on backend** (in Azure Cloud Shell):

```bash
# Get frontend URL
FRONTEND_URL=$(az containerapp show \
  --name ca-taskapp-frontend \
  --resource-group rg-taskapp-prod \
  --query properties.configuration.ingress.fqdn \
  --output tsv)

# Update backend with CORS environment variable
az containerapp update \
  --name ca-taskapp-backend \
  --resource-group rg-taskapp-prod \
  --set-env-vars "CORS_ORIGINS=https://${FRONTEND_URL}"
```

**Note**: Your backend code needs to read the `CORS_ORIGINS` environment variable. Check `backend/app/__init__.py`:

```python
# Should have something like:
cors = CORS()
cors.init_app(app, origins=os.getenv('CORS_ORIGINS', '*').split(','))
```

#### Issue: API Requests Go to Wrong URL

**Symptoms**: Network tab shows requests to `http://localhost:5000` or wrong URL

**Solution**: Environment variable not set correctly.

**Verify**:
```bash
az containerapp show \
  --name ca-taskapp-frontend \
  --resource-group rg-taskapp-prod \
  --query "properties.template.containers[0].env"
```

**Fix**:
```bash
BACKEND_URL=$(az containerapp show --name ca-taskapp-backend --resource-group rg-taskapp-prod --query properties.configuration.ingress.fqdn -o tsv)

az containerapp update \
  --name ca-taskapp-frontend \
  --resource-group rg-taskapp-prod \
  --replace-env-vars "NEXT_PUBLIC_API_URL=https://${BACKEND_URL}" "NODE_ENV=production"
```

#### Issue: 500 Internal Server Error

**Check backend logs**:
```bash
az containerapp logs show \
  --name ca-taskapp-backend \
  --resource-group rg-taskapp-prod \
  --tail 100
```

Look for Python errors/tracebacks.

---

## Step 5: Test Complete User Workflows

### What You're Testing

End-to-end user workflows to ensure the entire application is working.

### Workflow 1: User Registration → Login → Dashboard

1. **Register New User**
   - Go to Register page
   - Fill in form
   - Click Register
   - ✅ Should show success message or redirect

2. **Login**
   - Enter credentials
   - Click Login
   - ✅ Should redirect to dashboard

3. **View Dashboard**
   - ✅ Should display user's name
   - ✅ Should show projects/tasks (or empty state)

### Workflow 2: Create Project → Create Task → Update Task

1. **Create Project** (if your app has this feature)
   - Click "New Project"
   - Enter project name, description
   - Click Create
   - ✅ Project appears in list

2. **Create Task**
   - Click "New Task"
   - Enter task title, description
   - Assign to project
   - Click Create
   - ✅ Task appears in list

3. **Update Task**
   - Click on task
   - Change status (e.g., TODO → IN_PROGRESS)
   - Click Save
   - ✅ Task updates successfully

### Workflow 3: Logout → Login Again

1. **Logout**
   - Click Logout button
   - ✅ Should redirect to login/home page
   - ✅ Should clear authentication

2. **Try Accessing Protected Route**
   - Try to manually go to `/dashboard`
   - ✅ Should redirect to login page

3. **Login Again**
   - Enter credentials
   - ✅ Should redirect to dashboard
   - ✅ Previous data (projects/tasks) still there

### Test Results

**If all workflows pass**: ✅ Application is fully functional!

---

## Step 6: Update Backend CORS (If Needed)

### Why Update CORS?

By default, the backend might allow all origins (`*`). For security, you should restrict CORS to only allow requests from your frontend domain.

### Check Current CORS Configuration

```bash
# Check backend environment variables
az containerapp show \
  --name ca-taskapp-backend \
  --resource-group rg-taskapp-prod \
  --query "properties.template.containers[0].env" \
  --output table
```

Look for `CORS_ORIGINS` variable.

### Update Backend CORS

```bash
# Get frontend URL
FRONTEND_URL=$(az containerapp show \
  --name ca-taskapp-frontend \
  --resource-group rg-taskapp-prod \
  --query properties.configuration.ingress.fqdn \
  --output tsv)

# Update backend to allow only frontend domain
az containerapp update \
  --name ca-taskapp-backend \
  --resource-group rg-taskapp-prod \
  --set-env-vars "CORS_ORIGINS=https://${FRONTEND_URL}"
```

**⏰ This will take 1-2 minutes** - backend restarting with new config.

### Verify CORS Works

1. **Reload frontend** in browser
2. **Try login/register** again
3. **Check Network tab** - should still work (no CORS errors)

---

## Phase 7 Completion Checklist

Use this checklist to verify everything is complete:

### ✅ Frontend Container App

- [ ] Frontend Container App created (ca-taskapp-frontend)
- [ ] App is in "Running" state
- [ ] Image pulled from ACR successfully
- [ ] Ingress configured (external, port 3000)
- [ ] Frontend URL accessible

### ✅ Environment Variables

- [ ] NEXT_PUBLIC_API_URL set to backend URL
- [ ] NODE_ENV set to "production"
- [ ] Environment variables verified

### ✅ Testing & Verification

- [ ] Frontend loads in browser (no errors)
- [ ] Health check passes (200 OK)
- [ ] Logs show Next.js running successfully
- [ ] No errors in browser console

### ✅ Frontend-Backend Integration

- [ ] User registration works (creates user in database)
- [ ] User login works (returns JWT token)
- [ ] Authenticated requests work (dashboard loads)
- [ ] No CORS errors in browser console
- [ ] API requests go to correct backend URL

### ✅ Complete User Workflows

- [ ] Can register new user
- [ ] Can login with credentials
- [ ] Dashboard/home page loads after login
- [ ] Can create projects (if applicable)
- [ ] Can create tasks (if applicable)
- [ ] Can update tasks (if applicable)
- [ ] Can logout and login again
- [ ] Protected routes redirect to login when not authenticated

### ✅ Security & Configuration

- [ ] Backend CORS configured (allows frontend domain)
- [ ] No sensitive data in browser console
- [ ] HTTPS working for both frontend and backend

---

## Verification Commands

Run these commands to verify Phase 7 completion:

```bash
# Set variables
RESOURCE_GROUP="rg-taskapp-prod"
FRONTEND_APP="ca-taskapp-frontend"
BACKEND_APP="ca-taskapp-backend"

# Verify Frontend App
az containerapp show \
  --name $FRONTEND_APP \
  --resource-group $RESOURCE_GROUP \
  --query "{Name:name, Status:properties.runningStatus, URL:properties.configuration.ingress.fqdn}" \
  --output table

# Verify Environment Variables
az containerapp show \
  --name $FRONTEND_APP \
  --resource-group $RESOURCE_GROUP \
  --query "properties.template.containers[0].env" \
  --output table

# Get Frontend URL
FRONTEND_URL=$(az containerapp show --name $FRONTEND_APP --resource-group $RESOURCE_GROUP --query properties.configuration.ingress.fqdn -o tsv)
echo "Frontend URL: https://${FRONTEND_URL}"

# Test Frontend is Responding
curl -I https://${FRONTEND_URL}

# View Recent Logs
az containerapp logs show --name $FRONTEND_APP --resource-group $RESOURCE_GROUP --tail 20

# List All Container Apps
az containerapp list --resource-group $RESOURCE_GROUP --output table
```

**Expected results**:
- ✅ Frontend status: Running
- ✅ Environment variables: NEXT_PUBLIC_API_URL and NODE_ENV set
- ✅ Frontend responds with HTTP 200
- ✅ Logs show Next.js running
- ✅ Both backend and frontend apps listed

---

## Common Issues & Troubleshooting

### Issue 1: Frontend Shows "Cannot Connect to Server"

**Symptoms**:
- Frontend loads but shows connection errors
- API requests fail

**Causes**:
- NEXT_PUBLIC_API_URL not set correctly
- Backend is down
- CORS blocking requests

**Solutions**:

```bash
# 1. Verify backend is running
az containerapp show --name ca-taskapp-backend --resource-group rg-taskapp-prod --query properties.runningStatus

# 2. Test backend directly
curl https://ca-taskapp-backend.redtree-99ec4a5a.centralus.azurecontainerapps.io/api/health

# 3. Check frontend environment variables
az containerapp show --name ca-taskapp-frontend --resource-group rg-taskapp-prod --query "properties.template.containers[0].env"

# 4. Update frontend with correct backend URL
BACKEND_URL=$(az containerapp show --name ca-taskapp-backend --resource-group rg-taskapp-prod --query properties.configuration.ingress.fqdn -o tsv)
az containerapp update --name ca-taskapp-frontend --resource-group rg-taskapp-prod --replace-env-vars "NEXT_PUBLIC_API_URL=https://${BACKEND_URL}" "NODE_ENV=production"
```

---

### Issue 2: CORS Errors in Browser

**Symptoms**:
```
Access to fetch at 'https://ca-taskapp-backend...' has been blocked by CORS policy
```

**Solution**:

```bash
# Update backend CORS to allow frontend
FRONTEND_URL=$(az containerapp show --name ca-taskapp-frontend --resource-group rg-taskapp-prod --query properties.configuration.ingress.fqdn -o tsv)

az containerapp update \
  --name ca-taskapp-backend \
  --resource-group rg-taskapp-prod \
  --set-env-vars "CORS_ORIGINS=https://${FRONTEND_URL}"
```

**Verify backend CORS configuration in code** (`backend/app/__init__.py`):
```python
cors.init_app(app, origins=os.getenv('CORS_ORIGINS', '*').split(','))
```

---

### Issue 3: Frontend Container Stuck in "Provisioning"

**Symptoms**:
```bash
az containerapp show --name ca-taskapp-frontend --query properties.runningStatus
# Output: "Provisioning"
```

**Wait**: Initial deployment takes 3-5 minutes.

**Check logs**:
```bash
az containerapp logs show --name ca-taskapp-frontend --resource-group rg-taskapp-prod --tail 50
```

**Look for**:
- Image pull errors
- Port binding errors
- Next.js startup errors

**Common fixes**:
- Verify image exists: `az acr repository show-tags --name taskappacr2026 --repository taskapp-frontend`
- Check port: Should be 3000 (not 80 or 8080)

---

### Issue 4: 500 Internal Server Error on Frontend

**Check logs**:
```bash
az containerapp logs show --name ca-taskapp-frontend --resource-group rg-taskapp-prod --tail 100
```

**Look for**:
- Next.js build errors
- Missing environment variables
- Module not found errors

**Common fixes**:
- Ensure `NODE_ENV=production` is set
- Check if `NEXT_PUBLIC_API_URL` is set
- Verify Docker image was built correctly

---

## Next Steps

### Phase 8: Custom Domain & SSL (Optional)

If you have a custom domain:
- Map custom domain to Container App
- Configure SSL certificate
- Update DNS records

### Phase 9: Monitoring & Logging

- Set up Application Insights
- Configure alerts for errors/downtime
- Set up dashboards

### Phase 10: Cost Optimization

- Review Container Apps pricing
- Adjust replica counts
- Set up auto-pause for dev environments

---

## Cost Estimate

**Phase 7 Frontend**:
- Frontend Container App: ~$12-20/month (consumption-based)

**Total for Phase 6 + 7**:
- Backend Container App: ~$12-20/month
- Frontend Container App: ~$12-20/month
- **Total**: ~$24-40/month

**Free tier benefits**:
- First 180,000 vCPU-seconds free per month
- First 360,000 GiB-seconds free per month

With low traffic, you might stay within free tier limits!

---

## Summary

**What You Accomplished in Phase 7**:

✅ Deployed Next.js frontend to Azure Container Apps  
✅ Configured environment variables for backend connectivity  
✅ Tested frontend-backend integration  
✅ Verified complete user workflows  
✅ Configured CORS for security  
✅ Full application now running in Azure!  

**Your Application URLs**:
- **Frontend**: https://ca-taskapp-frontend.redtree-99ec4a5a.centralus.azurecontainerapps.io
- **Backend**: https://ca-taskapp-backend.redtree-99ec4a5a.centralus.azurecontainerapps.io

**Architecture**:
- 2 Container Apps in same environment
- Shared VNet and Log Analytics
- Private database access via VNet
- HTTPS enabled on all public endpoints

**Next Phase**: Domain configuration, monitoring, or infrastructure as code!

🎉 **Congratulations! Your task management application is now fully deployed on Azure!** 🎉
