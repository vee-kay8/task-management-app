# Azure Resources Inventory

## Resource Group
- **rg-taskapp-prod** (Central US)

## Networking
- **VNet**: vnet-taskapp (10.0.0.0/16)
- **Subnets**:
  - subnet-container-apps (10.0.1.0/24)
  - subnet-database (10.0.2.0/24)
- **NSGs**:
  - nsg-container-apps (Allow 80/443)
  - nsg-database (Allow 5432 from 10.0.1.0/24)

## Compute
- **Container Apps Environment**: env-taskapp-prod
- **Container Apps**:
  - ca-taskapp-backend
  - ca-taskapp-frontend

## Database
- **PostgreSQL Flexible Server**: taskapp-db-88.postgres.database.azure.com
- **Version**: 15
- **Tier**: Burstable B1ms
- **Private Access**: Enabled (VNet integrated)

## Container Registry
- **ACR**: taskappacr2026
- **Login Server**: taskappacr2026.azurecr.io
- **SKU**: Basic

## Secrets
- **Key Vault**: kv-taskapp-2026
- **Secrets**: db-host, db-name, db-user, db-password, jwt-secret-key

## Monitoring
- **Log Analytics Workspace**: (verify in portal)
- **Alerts**: HTTP errors, container restarts (Phase 9)

## URLs
- **Frontend**: https://ca-taskapp-frontend.redtree-99ec4a5a.centralus.azurecontainerapps.io
- **Backend**: https://ca-taskapp-backend.purpleground-a372e111.centralus.azurecontainerapps.io
- **Custom Domain**: https://app.techveesolutions.com

## Notes

- Validate all resource names in Azure Portal.
- ACR image references are documented in azure/config/acr-image-references.txt.
