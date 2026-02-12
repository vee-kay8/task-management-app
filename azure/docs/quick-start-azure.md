# Azure Deployment Quick-Start Guide

This quick-start assumes infrastructure is already provisioned.

## 1) Set Subscription
```bash
az account set --subscription "<SUBSCRIPTION_ID>"
```

## 2) Verify Container Apps
```bash
az containerapp list --resource-group rg-taskapp-prod --output table
```

## 3) Update Backend Image
```bash
az containerapp update \
  --name ca-taskapp-backend \
  --resource-group rg-taskapp-prod \
  --image taskappacr2026.azurecr.io/taskapp-backend:latest
```

## 4) Update Frontend Image
```bash
az containerapp update \
  --name ca-taskapp-frontend \
  --resource-group rg-taskapp-prod \
  --image taskappacr2026.azurecr.io/taskapp-frontend:latest
```

## 5) Verify App
- Frontend: https://app.techveesolutions.com
- Backend: https://ca-taskapp-backend.purpleground-a372e111.centralus.azurecontainerapps.io
