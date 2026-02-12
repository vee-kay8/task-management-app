# Azure Deployment Troubleshooting Guide

## Common Issues

### 1) Container App won’t start
**Symptoms**: CrashLoopBackOff, unhealthy revisions
**Fix**:
- Check logs: `az containerapp logs show --name <app> --resource-group rg-taskapp-prod --follow`
- Verify env vars (DB URL, SECRET_KEY, JWT_SECRET_KEY)
- Confirm image tag exists in ACR

### 2) ACR pull denied
**Symptoms**: Image pull failed
**Fix**:
- Ensure Container Apps identity has `AcrPull`
- If using Service Principal for CI, assign `AcrPush`

### 3) Database connection failed
**Symptoms**: timeouts, connection refused
**Fix**:
- Confirm VNet integration and NSG rule (5432 from CA subnet)
- Verify DB hostname and credentials
- Ensure private DNS resolution

### 4) Custom domain not resolving
**Symptoms**: DNS errors
**Fix**:
- Check Azure DNS records
- Verify TLS cert is issued

### 5) CI/CD failing
**Symptoms**: GitHub Actions login failed
**Fix**:
- Recreate Service Principal and update `AZURE_CREDENTIALS`
- Validate subscription and resource group secrets

---

## Useful Commands

```bash
az containerapp list --resource-group rg-taskapp-prod --output table
az containerapp revision list --name ca-taskapp-backend --resource-group rg-taskapp-prod --output table
az acr repository list --name taskappacr2026 --output table
az postgres flexible-server show --name taskapp-db-88 --resource-group rg-taskapp-prod
```
