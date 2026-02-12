# Phase 11: CI/CD Integration (GitHub Actions) - Complete Guide

**Estimated Time**: 3-4 hours  
**Prerequisites**: Phases 1-10 completed  
**Status**: Not Started

---

## Overview

In this phase, you’ll automate deployments to Azure Container Apps using GitHub Actions. Every push to the repository will build new Docker images, push them to Azure Container Registry (ACR), and update the corresponding Container Apps with zero downtime revisions.

**What You’ll Learn**:
- Azure Service Principal creation and RBAC scopes
- GitHub Actions for Azure deployment
- ACR build/push automation
- Container Apps revision updates
- Secure secrets management in GitHub

**What You’ll Build**:
- GitHub Actions workflows for backend and frontend
- Automated Docker build and push pipeline
- Push-to-deploy CI/CD pipeline

---

## Architecture Overview

```
GitHub Push  ──▶  GitHub Actions  ──▶  ACR  ──▶  Container Apps (Backend/Frontend)
      ▲                │                    │                │
      └────────────────┴────────────────────┴────────────────┘
                  Secrets & Azure RBAC
```

---

## Prerequisites Check

```bash
# Verify Container Apps exist
az containerapp list \
  --resource-group rg-taskapp-prod \
  --output table

# Verify ACR exists
az acr list \
  --resource-group rg-taskapp-prod \
  --output table
```

---

## Step 1: Create Azure Service Principal

```bash
# Create Service Principal scoped to the resource group
az ad sp create-for-rbac \
  --name sp-github-actions-taskapp \
  --role contributor \
  --scopes /subscriptions/<SUBSCRIPTION_ID>/resourceGroups/rg-taskapp-prod \
  --sdk-auth
```

**Save the JSON output** — add it to GitHub Secrets as `AZURE_CREDENTIALS`.

### Grant ACR Push permissions

```bash
az role assignment create \
  --assignee <SERVICE_PRINCIPAL_APP_ID> \
  --role AcrPush \
  --scope /subscriptions/<SUBSCRIPTION_ID>/resourceGroups/rg-taskapp-prod/providers/Microsoft.ContainerRegistry/registries/taskappacr2026
```

---

## Step 2: Add GitHub Secrets

In your GitHub repo → **Settings → Secrets and variables → Actions**, add:

- `AZURE_CREDENTIALS` (JSON from the Service Principal)
- `AZURE_SUBSCRIPTION_ID`
- `AZURE_RESOURCE_GROUP` (rg-taskapp-prod)
- `ACR_NAME` (taskappacr2026)
- `ACR_LOGIN_SERVER` (taskappacr2026.azurecr.io)
- `BACKEND_CONTAINER_APP` (ca-taskapp-backend)
- `FRONTEND_CONTAINER_APP` (ca-taskapp-frontend)
- `NEXT_PUBLIC_API_URL` (https://api.techveesolutions.com)
- `DATABASE_URL` (from Key Vault / existing config)
- `SECRET_KEY`
- `JWT_SECRET_KEY`

---

## Step 3: Create Backend Workflow

**Create `.github/workflows/azure-deploy-backend.yml`**:

```yaml
name: Deploy Backend to Azure

on:
  push:
    branches: [ main, Cloud-Deployment-Azure ]
    paths:
      - 'backend/**'

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Login to Azure
        uses: azure/login@v1
        with:
          creds: ${{ secrets.AZURE_CREDENTIALS }}

      - name: Login to ACR
        run: az acr login --name ${{ secrets.ACR_NAME }}

      - name: Build and push Docker image
        working-directory: ./backend
        run: |
          docker build -t ${{ secrets.ACR_LOGIN_SERVER }}/taskapp-backend:${{ github.sha }} .
          docker push ${{ secrets.ACR_LOGIN_SERVER }}/taskapp-backend:${{ github.sha }}

      - name: Update Backend Container App
        run: |
          az containerapp update \
            --name ${{ secrets.BACKEND_CONTAINER_APP }} \
            --resource-group ${{ secrets.AZURE_RESOURCE_GROUP }} \
            --image ${{ secrets.ACR_LOGIN_SERVER }}/taskapp-backend:${{ github.sha }} \
            --set-env-vars \
              DATABASE_URL=${{ secrets.DATABASE_URL }} \
              SECRET_KEY=${{ secrets.SECRET_KEY }} \
              JWT_SECRET_KEY=${{ secrets.JWT_SECRET_KEY }}
```

---

## Step 4: Create Frontend Workflow

**Create `.github/workflows/azure-deploy-frontend.yml`**:

```yaml
name: Deploy Frontend to Azure

on:
  push:
    branches: [ main, Cloud-Deployment-Azure ]
    paths:
      - 'frontend/**'

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Login to Azure
        uses: azure/login@v1
        with:
          creds: ${{ secrets.AZURE_CREDENTIALS }}

      - name: Login to ACR
        run: az acr login --name ${{ secrets.ACR_NAME }}

      - name: Build and push Docker image
        working-directory: ./frontend
        run: |
          docker build \
            --build-arg NEXT_PUBLIC_API_URL=${{ secrets.NEXT_PUBLIC_API_URL }} \
            -t ${{ secrets.ACR_LOGIN_SERVER }}/taskapp-frontend:${{ github.sha }} .
          docker push ${{ secrets.ACR_LOGIN_SERVER }}/taskapp-frontend:${{ github.sha }}

      - name: Update Frontend Container App
        run: |
          az containerapp update \
            --name ${{ secrets.FRONTEND_CONTAINER_APP }} \
            --resource-group ${{ secrets.AZURE_RESOURCE_GROUP }} \
            --image ${{ secrets.ACR_LOGIN_SERVER }}/taskapp-frontend:${{ github.sha }}
```

---

## Step 5: Validate the Pipeline

1. Push a change to `backend/` and confirm the backend workflow runs.
2. Push a change to `frontend/` and confirm the frontend workflow runs.
3. Verify a new revision is created in Container Apps.

```bash
az containerapp revision list \
  --name ca-taskapp-backend \
  --resource-group rg-taskapp-prod \
  --output table
```

---

## Verification Checklist

- [ ] Service Principal created and scoped correctly
- [ ] GitHub Secrets added
- [ ] Backend workflow created and running
- [ ] Frontend workflow created and running
- [ ] Images pushed to ACR from CI
- [ ] Container Apps updated automatically
- [ ] App healthy after deployment

---

## Troubleshooting

### Issue: `azure/login` fails
**Fix**: Ensure `AZURE_CREDENTIALS` is valid JSON and the Service Principal has Contributor access.

### Issue: ACR push denied
**Fix**: Ensure the Service Principal has `AcrPush` on the registry scope.

### Issue: Container App update fails
**Fix**: Confirm `AZURE_RESOURCE_GROUP`, `BACKEND_CONTAINER_APP`, and `FRONTEND_CONTAINER_APP` are correct.

---

## Best Practices

1. Use unique tags per deployment (`${{ github.sha }}`)
2. Keep secrets in GitHub, never in workflow files
3. Add environment approvals for production (optional)
4. Use separate workflows for backend and frontend

---

## Cost Estimate

**Phase 11 Costs**: $0 (GitHub Actions free tier + Azure SP)

---

## Next Steps

After completing Phase 11:

1. Record completion in `AZURE_PROGRESS.md`
2. Verify zero-downtime deployment behavior
3. Proceed to Phase 12: Cost Optimization & Auto-Scaling

---

## Resources

- [GitHub Actions for Azure](https://learn.microsoft.com/en-us/azure/developer/github/github-actions)
- [Azure Container Apps CLI](https://learn.microsoft.com/en-us/azure/container-apps/)
- [Azure Login Action](https://github.com/azure/login)

---

**Phase 11 Status**: Ready to begin ✅  
**Estimated Completion Time**: 3-4 hours  
**Next Phase**: Phase 12 - Cost Optimization & Auto-Scaling
