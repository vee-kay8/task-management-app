# Azure Deployment Roadmap - Complete Guide

**Project**: Task Management Application Deployment to Azure
**Duration**: 3-4 weeks
**Status**: In Progress (8/13 phases complete - 61.5%)
**Live Application**: https://app.techveesolutions.com

---

## Overview

This document tracks the complete Azure deployment journey from account setup to production-ready infrastructure. This is a learning project to understand Azure cloud services and compare with AWS deployment experience.

### Azure vs AWS Service Mapping

| AWS Service | Azure Equivalent | Purpose |
|-------------|------------------|---------|
| VPC | Virtual Network (VNet) | Network isolation |
| ECS Fargate | Container Apps | Serverless containers |
| ECR | Container Registry (ACR) | Docker image storage |
| RDS PostgreSQL | Database for PostgreSQL | Managed database |
| ALB | Application Gateway / Container Apps Ingress | Load balancing |
| Route 53 | Azure DNS | Domain management |
| CloudWatch | Azure Monitor + Log Analytics | Monitoring & logging |
| Secrets Manager | Key Vault | Secrets management |
| IAM | Azure AD + RBAC | Identity & access |
| Terraform | Bicep or Terraform | Infrastructure as Code |

---

## Phase 1: Azure Account Setup & Prerequisites

**Timeline**: Day 1
**Status**: ✅ Complete
**Progress**: 100%
**Completion Date**: January 26, 2026

### Learning Goals
- Understand Azure portal navigation
- Learn Azure CLI basics
- Understand Azure subscription and resource groups
- Set up billing and cost management

### Checklist
- [x] Create Azure free account ($200 free credit for 30 days)
- [x] Verify email and phone number
- [x] Set up billing alerts and budgets
- [x] Create Azure AD user (or use existing)
- [x] Enable multi-factor authentication (MFA)
- [x] Install Azure CLI (version 2.80.0)
- [x] Run `az login` and authenticate
- [x] Choose primary region: **East US** (eastus)
- [x] Review Azure free tier limitations
- [x] Create project directory structure for Azure files
- [x] Install additional tools (jq, git, Docker)

### Deliverables
- [x] Azure account active with free credits
- [x] Azure CLI installed and configured (v2.80.0)
- [x] MFA enabled for security
- [x] Billing alerts configured ($100/month budget)
- [x] Project directory structure created

### Azure-Specific Commands
```bash
# Install Azure CLI (Windows)
winget install Microsoft.AzureCLI

# Login to Azure
az login

# Set default subscription
az account set --subscription "Your Subscription Name"

# Verify authentication
az account show

# List available regions
az account list-locations --output table
```

### Documentation Notes
- Account details and subscription ID
- Region selection rationale
- Security configuration details
- Free tier resource limits

### Estimated Cost
**Phase 1**: $0 (free tier)

---

## Phase 2: Resource Group & Virtual Network Setup

**Timeline**: Days 2-3
**Status**: ✅ Complete
**Progress**: 100%
**Completion Date**: January 26, 2026

### Learning Goals
- Understand Azure Resource Groups
- Learn Virtual Network (VNet) architecture
- Understand subnets and network security groups
- Learn Azure networking best practices

### Checklist
- [x] Create main Resource Group (rg-taskapp-prod)
- [x] Add tags (Environment: Production, Project: TaskApp, ManagedBy: Manual)
- [x] Create Virtual Network (vnet-taskapp)
  - [x] Address space: 10.0.0.0/16
  - [x] Enable DDoS protection: Basic
  - [x] DNS servers: Azure-provided
- [x] Create subnet for Container Apps (subnet-container-apps)
  - [x] Address range: 10.0.1.0/24
- [x] Create subnet for Database (subnet-database)
  - [x] Address range: 10.0.2.0/24
- [x] Create Network Security Group for database (nsg-database)
  - [x] Allow PostgreSQL (5432) from Container Apps subnet
  - [x] Deny all other inbound traffic
- [x] Create Network Security Group for Container Apps (nsg-container-apps)
  - [x] Allow HTTP (80) and HTTPS (443) from internet
  - [x] Allow all outbound traffic
- [x] Associate NSGs with subnets
- [x] Document network architecture
- [ ] Create network diagram (optional)

### Deliverables
- [x] Resource Group created and tagged
- [x] Virtual Network with 2 subnets
- [x] Network Security Groups configured
- [x] Documentation of IP ranges and rules
- [ ] Network architecture diagram (optional)

### Key Resources to Create
- **Resource Group**: rg-taskapp-prod
- **Virtual Network**: vnet-taskapp (10.0.0.0/16)
- **Subnets**:
  - subnet-container-apps: 10.0.1.0/24
  - subnet-database: 10.0.2.0/24
- **Network Security Groups**:
  - nsg-database
  - nsg-container-apps

### Azure-Specific Commands
```bash
# Create Resource Group
az group create \
  --name rg-taskapp-prod \
  --location eastus \
  --tags Environment=Production Project=TaskApp

# Create Virtual Network
az network vnet create \
  --resource-group rg-taskapp-prod \
  --name vnet-taskapp \
  --address-prefix 10.0.0.0/16

# Create subnets
az network vnet subnet create \
  --resource-group rg-taskapp-prod \
  --vnet-name vnet-taskapp \
  --name subnet-container-apps \
  --address-prefix 10.0.1.0/24

az network vnet subnet create \
  --resource-group rg-taskapp-prod \
  --vnet-name vnet-taskapp \
  --name subnet-database \
  --address-prefix 10.0.2.0/24
```

### Documentation Notes
- Why this subnet structure?
- Network security considerations
- Differences from AWS VPC setup

### Estimated Cost
**Phase 2**: $0 (VNet and NSGs are free)

---

## Phase 3: Database Layer (Azure Database for PostgreSQL)

**Timeline**: Days 4-5
**Status**: ✅ Complete
**Progress**: 100%
**Completion Date**: January 26, 2026

### Learning Goals
- Understand Azure Database for PostgreSQL Flexible Server
- Learn database security and networking
- Understand backup and high availability options
- Practice database initialization

### Checklist
- [x] Generate strong admin password (save securely)
- [x] Create Azure Database for PostgreSQL Flexible Server
  - [x] Server name: taskapp-db-88
  - [x] PostgreSQL version: 15
  - [x] Compute tier: Burstable (B1ms - free tier eligible)
  - [x] Storage: 32 GB
  - [x] Backup retention: 7 days
  - [x] Geo-redundant backup: Disabled (saves cost)
- [x] Configure networking
  - [x] Private access (VNet integration)
  - [x] Connect to subnet-database
  - [x] Disable public access
- [x] Server created successfully in Central US region
- [x] Store credentials in Azure Key Vault (Phase 5, using temp file for now)
- [x] Document connection details
- ✅ Database schema initialization deferred to Phase 6 (backend app will handle via migrations)

### Deliverables
- [x] PostgreSQL Flexible Server running
- [x] Database server with VNet integration (private access only)
- [x] Connection string documented
- [x] Backup configuration verified
- [x] Network security configured
- [x] Credentials stored temporarily (will move to Key Vault in Phase 5)

**Note**: Database schema initialization will be handled by backend app migrations in Phase 6. This is the recommended production approach.

### Key Resources to Create
- **Database Server**: taskapp-db-88.postgres.database.azure.com ✅
- **Database Name**: taskmanagement_db (to be created)
- **Admin User**: taskapp_admin
- **SKU**: Standard_B1ms (Burstable, 1 vCore, 2 GB RAM)
- **Location**: Central US (changed from East US due to regional restrictions)

### Azure-Specific Commands
```bash
# Create PostgreSQL Flexible Server
az postgres flexible-server create \
  --resource-group rg-taskapp-prod \
  --name taskapp-db-[suffix] \
  --location eastus \
  --admin-user taskapp_admin \
  --admin-password [STRONG_PASSWORD] \
  --version 15 \
  --sku-name Standard_B1ms \
  --tier Burstable \
  --storage-size 32 \
  --backup-retention 7 \
  --vnet vnet-taskapp \
  --subnet subnet-database

# Create database
az postgres flexible-server db create \
  --resource-group rg-taskapp-prod \
  --server-name taskapp-db-[suffix] \
  --database-name taskmanagement_db

# Connect to database
az postgres flexible-server connect \
  --name taskapp-db-[suffix] \
  --admin-user taskapp_admin \
  --database-name taskmanagement_db
```

### Lessons to Learn
- Difference between Single Server vs Flexible Server
- VNet integration vs public access
- Backup and restore procedures
- Connection pooling considerations

### Estimated Cost
**Phase 3**: $0 (B1ms free for 12 months, then ~$15-20/month)

---

## Phase 4: Azure Container Registry (ACR)

**Timeline**: Day 6
**Status**: ✅ Complete
**Progress**: 100%
**Completion Date**: January 29, 2026

### Learning Goals
- Understand Azure Container Registry tiers
- Learn ACR authentication methods
- Practice Docker image tagging and pushing
- Learn ACR tasks and image scanning

### Checklist
- [x] Create Azure Container Registry
  - [x] Registry name: taskappacr2026 (globally unique)
  - [x] SKU: Basic (sufficient for learning, cheapest)
  - [x] Admin user: Enabled (for simplified development)
  - [x] Public access: Enabled
- [x] Authenticate Docker to ACR
- [x] Review Dockerfiles for Azure deployment readiness
- [x] Build backend Docker image locally
- [x] Build frontend Docker image locally
- [x] Tag local backend image for ACR (latest and v1.0.0)
- [x] Tag local frontend image for ACR (latest and v1.0.0)
- [x] Push backend image to ACR
- [x] Push frontend image to ACR
- [x] Verify images in Azure Portal
- [x] Document image URIs
- [x] Test image listing from ACR

### Deliverables
- [x] ACR created and configured (taskappacr2026)
- [x] Backend and frontend images pushed (4 total: 2 repos × 2 tags)
- [x] Image URIs documented in azure/config/acr-image-references.txt
- [x] Authentication working via Azure CLI

### Key Resources Created
- **Container Registry**: taskappacr2026.azurecr.io ✅
- **Login Server**: taskappacr2026.azurecr.io
- **Location**: Central US
- **Images**:
  - taskappacr2026.azurecr.io/taskapp-backend:latest (350 MB)
  - taskappacr2026.azurecr.io/taskapp-backend:v1.0.0 (350 MB)
  - taskappacr2026.azurecr.io/taskapp-frontend:latest (212 MB)
  - taskappacr2026.azurecr.io/taskapp-frontend:v1.0.0 (212 MB)

### Azure-Specific Commands
```bash
# Create Container Registry
az acr create \
  --resource-group rg-taskapp-prod \
  --name taskappacr[unique] \
  --sku Basic \
  --admin-enabled false

# Login to ACR
az acr login --name taskappacr[unique]

# Tag and push backend image
docker tag taskapp-backend:latest taskappacr[unique].azurecr.io/taskapp-backend:latest
docker push taskappacr[unique].azurecr.io/taskapp-backend:latest

# Tag and push frontend image
docker tag taskapp-frontend:latest taskappacr[unique].azurecr.io/taskapp-frontend:latest
docker push taskappacr[unique].azurecr.io/taskapp-frontend:latest

# List images
az acr repository list --name taskappacr[unique] --output table
```

### Lessons to Learn
- ACR tiers: Basic vs Standard vs Premium
- Authentication: Admin user vs Service Principal vs Managed Identity
- Image retention policies
- Geo-replication (Premium tier only)

### Estimated Cost
**Phase 4**: ~$5/month (Basic SKU)

---

## Phase 5: Azure Key Vault (Secrets Management)

**Timeline**: Day 7
**Status**: ✅ Complete
**Progress**: 100%
**Completion Date**: January 29, 2026

### Learning Goals
- Understand Azure Key Vault concepts
- Learn secrets, keys, and certificates management
- Practice managed identity integration
- Learn access policies and RBAC

### Checklist
- [x] Create Azure Key Vault
  - [x] Name: kv-taskapp-2026
  - [x] Enable soft delete (30 days retention)
  - [x] Enable purge protection: No (easier for learning)
  - [x] Enable RBAC: Yes
- [x] Assign yourself "Key Vault Secrets Officer" role
- [x] Create secrets in Key Vault
  - [x] db-host (PostgreSQL hostname)
  - [x] db-name (database name)
  - [x] db-user (admin username)
  - [x] db-password (admin password)
  - [x] jwt-secret-key (JWT signing key)
- [x] Generate secure random values for secrets
- [x] Document secret names and versions
- [x] Test retrieving secrets via CLI
- [x] Prepare for managed identity integration (next phase)

### Deliverables
- [x] Key Vault created and configured (kv-taskapp-2026)
- [x] All application secrets stored (5 total)
- [x] Access policies documented
- [x] Secret retrieval tested

### Key Resources Created
- **Key Vault**: kv-taskapp-2026 ✅
- **Vault URI**: https://kv-taskapp-2026.vault.azure.net/
- **Secrets**:
  - db-host (PostgreSQL server hostname)
  - db-name (database name: postgres)
  - db-user (admin username: taskapp_admin)
  - db-password (admin password)
  - jwt-secret-key (JWT signing key - 64-char hex)

### Azure-Specific Commands
```bash
# Create Key Vault
az keyvault create \
  --name kv-taskapp-[unique] \
  --resource-group rg-taskapp-prod \
  --location eastus \
  --enable-rbac-authorization true

# Set secrets
az keyvault secret set \
  --vault-name kv-taskapp-[unique] \
  --name db-password \
  --value "[STRONG_PASSWORD]"

az keyvault secret set \
  --vault-name kv-taskapp-[unique] \
  --name secret-key \
  --value "$(openssl rand -hex 32)"

# Retrieve secret
az keyvault secret show \
  --vault-name kv-taskapp-[unique] \
  --name secret-key \
  --query value \
  --output tsv
```

### Lessons to Learn
- Soft delete and purge protection
- Access policies vs RBAC
- Managed identities for secret access
- Secret versioning and rotation

### Estimated Cost
**Phase 5**: ~$0.03/month per secret (~$0.12 total)

---

## Phase 6: Backend Deployment (Azure Container Apps)

**Timeline**: Days 8-10
**Status**: ✅ Complete
**Progress**: 100%
**Completion Date**: February 1, 2026

### Learning Goals
- Understand Azure Container Apps architecture
- Learn Container Apps Environment
- Practice environment variable configuration
- Learn ingress and scaling configuration

### Checklist
- [ ] Create Container Apps Environment
  - [ ] Name: env-taskapp-prod
  - [ ] VNet integration with subnet-container-apps
  - [ ] Log Analytics workspace (auto-created or existing)
- [ ] Create managed identity for backend app
- [ ] Grant managed identity access to Key Vault
- [ ] Grant managed identity access to ACR
- [ ] Create backend Container App
  - [ ] Name: ca-taskapp-backend
  - [ ] Image: taskappacr[unique].azurecr.io/taskapp-backend:latest
  - [ ] CPU: 0.25 cores
  - [ ] Memory: 0.5 Gi
  - [ ] Min replicas: 1
  - [ ] Max replicas: 4
  - [ ] Ingress: Enabled (internal only for now)
  - [ ] Target port: 5000
- [ ] Configure environment variables
  - [ ] DATABASE_URL (from Key Vault reference)
  - [ ] SECRET_KEY (from Key Vault reference)
  - [ ] JWT_SECRET_KEY (from Key Vault reference)
  - [ ] FLASK_ENV: production
  - [ ] CORS_ORIGINS: TBD (will update in Phase 7)
- [ ] Enable system-assigned managed identity
- [ ] Configure Key Vault references for secrets
- [ ] Deploy and verify container starts
- [ ] Check logs in Log Analytics
- [ ] Test backend health endpoint
- [ ] Verify database connectivity

### Deliverables
- [x] Container Apps Environment created (env-taskapp-prod) ✅
- [x] VNet integration configured with dedicated subnet ✅
- [x] Backend container app running (ca-taskapp-backend) ✅
- [x] Backend URL: https://ca-taskapp-backend.redtree-99ec4a5a.centralus.azurecontainerapps.io/ ✅
- [x] Managed identity configured with RBAC permissions ✅
- [x] Secrets loaded from Key Vault via secret references ✅
- [x] Database connectivity working via private VNet ✅
- [x] Logs accessible in Log Analytics workspace ✅
- [x] All API endpoints tested and functional ✅

### Key Resources Created
- **VNet Subnet**: subnet-containerapp-infra (10.0.4.0/23, delegated to Microsoft.App/environments) ✅
- **Container Apps Environment**: env-taskapp-prod ✅
- **Default Domain**: redtree-99ec4a5a.centralus.azurecontainerapps.io ✅
- **Backend Container App**: ca-taskapp-backend ✅
- **Backend URL**: https://ca-taskapp-backend.redtree-99ec4a5a.centralus.azurecontainerapps.io/ ✅
- **Managed Identity**: 10579475-79d3-4784-b639-ea765dab6865 (system-assigned) ✅
- **Log Analytics Workspace**: workspace-rgtaskappprodkPu0 (auto-created) ✅
- **Key Vault Secrets**: database-url (6th secret) ✅

### Azure-Specific Commands
```bash
# Create Container Apps Environment
az containerapp env create \
  --name env-taskapp-prod \
  --resource-group rg-taskapp-prod \
  --location eastus \
  --infrastructure-subnet-resource-id [SUBNET_ID]

# Create backend Container App
az containerapp create \
  --name ca-taskapp-backend \
  --resource-group rg-taskapp-prod \
  --environment env-taskapp-prod \
  --image taskappacr[unique].azurecr.io/taskapp-backend:latest \
  --target-port 5000 \
  --ingress internal \
  --cpu 0.25 --memory 0.5Gi \
  --min-replicas 1 --max-replicas 4 \
  --registry-server taskappacr[unique].azurecr.io \
  --registry-identity system

# Enable managed identity
az containerapp identity assign \
  --name ca-taskapp-backend \
  --resource-group rg-taskapp-prod \
  --system-assigned

# Set environment variables with Key Vault references
az containerapp update \
  --name ca-taskapp-backend \
  --resource-group rg-taskapp-prod \
  --set-env-vars \
    "DATABASE_URL=secretref:db-connection-string" \
    "SECRET_KEY=secretref:secret-key" \
    "JWT_SECRET_KEY=secretref:jwt-secret-key" \
    "FLASK_ENV=production"
```

### Lessons to Learn
- Container Apps vs Container Instances vs App Service
- Environment variables vs secrets vs Key Vault references
- Internal vs external ingress
- Revision management and traffic splitting

### Estimated Cost
**Phase 6**: ~$10-15/month (Container Apps consumption)

---

## Phase 7: Frontend Deployment (Azure Container Apps)

**Timeline**: Days 11-12
**Status**: Not Started
**Progress**: 0%

### Learning Goals
- Deploy second container app
- Configure app-to-app communication
- Learn external ingress configuration
- Practice Next.js Azure deployment

### Checklist
- [ ] Rebuild frontend with backend URL
  - [ ] NEXT_PUBLIC_API_URL: https://ca-taskapp-backend.internal.[domain]
  - [ ] Build locally with --build-arg
- [ ] Tag and push new frontend image to ACR
- [ ] Create managed identity for frontend app
- [ ] Grant managed identity access to ACR
- [ ] Create frontend Container App
  - [ ] Name: ca-taskapp-frontend
  - [ ] Image: taskappacr[unique].azurecr.io/taskapp-frontend:latest
  - [ ] CPU: 0.25 cores
  - [ ] Memory: 0.5 Gi
  - [ ] Min replicas: 1
  - [ ] Max replicas: 4
  - [ ] Ingress: Enabled (external - allows HTTP)
  - [ ] Target port: 3000
- [ ] Enable system-assigned managed identity
- [ ] Deploy and verify container starts
- [ ] Check logs in Log Analytics
- [ ] Test frontend loads in browser
- [ ] Test API calls from frontend to backend
- [ ] Verify CORS configuration
- [ ] Test full application flow
  - [ ] User registration
  - [ ] User login
  - [ ] Create project
  - [ ] Create tasks
  - [ ] Drag and drop functionality

### Deliverables
- [ ] Frontend container app running
- [ ] External URL accessible
- [ ] Frontend-to-backend communication working
- [ ] Full application functionality verified

### Key Resources to Create
- **Frontend Container App**: ca-taskapp-frontend
- **Managed Identity**: ca-taskapp-frontend (system-assigned)
- **Frontend Public URL**: https://ca-taskapp-frontend.[env-domain].eastus.azurecontainerapps.io

### Azure-Specific Commands
```bash
# Rebuild frontend locally (on your machine)
cd frontend
docker build \
  --build-arg NEXT_PUBLIC_API_URL=https://ca-taskapp-backend.internal.[domain] \
  -t taskappacr[unique].azurecr.io/taskapp-frontend:latest \
  .

# Push to ACR
docker push taskappacr[unique].azurecr.io/taskapp-frontend:latest

# Create frontend Container App
az containerapp create \
  --name ca-taskapp-frontend \
  --resource-group rg-taskapp-prod \
  --environment env-taskapp-prod \
  --image taskappacr[unique].azurecr.io/taskapp-frontend:latest \
  --target-port 3000 \
  --ingress external \
  --cpu 0.25 --memory 0.5Gi \
  --min-replicas 1 --max-replicas 4 \
  --registry-server taskappacr[unique].azurecr.io \
  --registry-identity system

# Get frontend URL
az containerapp show \
  --name ca-taskapp-frontend \
  --resource-group rg-taskapp-prod \
  --query properties.configuration.ingress.fqdn \
  --output tsv
```

### Lessons to Learn
- Next.js build-time vs runtime environment variables (same as AWS!)
- Internal vs external ingress in Container Apps
- Container-to-container communication in same environment
- CORS configuration for Azure domains

### Estimated Cost
**Phase 7**: ~$10-15/month (Frontend Container Apps consumption)
**Total so far**: ~$35-45/month

---

## Phase 8: Custom Domain & SSL Configuration

**Timeline**: Days 13-14
**Status**: Not Started
**Progress**: 0%

### Learning Goals
- Configure custom domain with Azure DNS
- Learn Azure-managed certificates
- Practice SSL/TLS configuration
- Update application for HTTPS

### Checklist
- [ ] Option A: Use existing domain (techveesolutions.com)
  - [ ] Create subdomain: azure-app.techveesolutions.com
  - [ ] Or use different subdomain from AWS
- [ ] Option B: Register new Azure domain (optional)
- [ ] Add custom domain to frontend Container App
- [ ] Verify domain ownership (TXT record)
- [ ] Create managed certificate in Container App
- [ ] Wait for certificate validation
- [ ] Update DNS with CNAME or A record
- [ ] Enable HTTPS redirect
- [ ] Update backend CORS_ORIGINS environment variable
  - [ ] Add https://[your-domain]
- [ ] Redeploy backend with new CORS settings
- [ ] Rebuild frontend with HTTPS API URL
  - [ ] NEXT_PUBLIC_API_URL: https://[your-domain]/api
  - [ ] Or keep internal backend URL if using path-based routing
- [ ] Push new frontend image to ACR
- [ ] Update frontend Container App with new image
- [ ] Test HTTPS access
- [ ] Verify SSL certificate in browser
- [ ] Test API calls over HTTPS
- [ ] Verify no mixed content warnings

### Deliverables
- [ ] Custom domain configured
- [ ] SSL certificate active
- [ ] HTTPS enforced
- [ ] Application accessible via custom domain
- [ ] No security warnings

### Key Resources to Create
- **Custom Domain**: azure-app.techveesolutions.com (or your choice)
- **Managed Certificate**: Auto-managed by Azure Container Apps
- **DNS Records**: CNAME or TXT for verification

### Azure-Specific Commands
```bash
# Add custom domain to Container App
az containerapp hostname add \
  --hostname azure-app.techveesolutions.com \
  --resource-group rg-taskapp-prod \
  --name ca-taskapp-frontend

# Bind certificate (managed certificate auto-created)
az containerapp hostname bind \
  --hostname azure-app.techveesolutions.com \
  --resource-group rg-taskapp-prod \
  --name ca-taskapp-frontend \
  --environment env-taskapp-prod \
  --validation-method CNAME

# List hostnames
az containerapp hostname list \
  --resource-group rg-taskapp-prod \
  --name ca-taskapp-frontend
```

### Lessons to Learn
- Azure managed certificates vs bring-your-own
- Container Apps custom domain binding
- DNS propagation time
- HTTPS redirect configuration

### Estimated Cost
**Phase 8**: $0 (Managed certificates are free!)

---

## Phase 9: Monitoring & Logging (Azure Monitor)

**Timeline**: Days 15-16
**Status**: Not Started
**Progress**: 0%

### Learning Goals
- Understand Azure Monitor and Log Analytics
- Learn Application Insights integration
- Practice creating alerts and dashboards
- Learn KQL (Kusto Query Language) basics

### Checklist
- [ ] Verify Log Analytics Workspace created (auto-created with Container Apps Environment)
- [ ] Enable Application Insights for Container Apps (optional)
- [ ] Create Azure Monitor Action Group for alerts
  - [ ] Name: ag-taskapp-alerts
  - [ ] Email notification: your-email@example.com
- [ ] Create metric alerts
  - [ ] Backend replica count = 0 (critical)
  - [ ] Frontend replica count = 0 (critical)
  - [ ] Backend CPU > 80% (warning)
  - [ ] Frontend CPU > 80% (warning)
  - [ ] Backend memory > 90% (critical)
  - [ ] Database CPU > 80% (warning)
  - [ ] Database storage > 80% (warning)
- [ ] Create Azure Dashboard
  - [ ] Container Apps CPU usage
  - [ ] Container Apps memory usage
  - [ ] Container Apps request count
  - [ ] Container Apps replica count
  - [ ] Database connections
  - [ ] Database CPU percentage
- [ ] Create Log Analytics queries (KQL)
  - [ ] Recent errors (last 24 hours)
  - [ ] API response times (P95, P99)
  - [ ] Failed login attempts
  - [ ] Slowest requests
- [ ] Save queries for reuse
- [ ] Configure log retention (30 days to control cost)
- [ ] Test alerts by simulating issues
- [ ] Document monitoring setup

### Deliverables
- [ ] Comprehensive monitoring dashboard
- [ ] Critical alerts configured
- [ ] Email notifications working
- [ ] Saved KQL queries
- [ ] Log retention configured

### Key Resources to Create
- **Log Analytics Workspace**: (created with Container Apps Environment)
- **Action Group**: ag-taskapp-alerts
- **Alerts**: 7 metric alerts
- **Dashboard**: taskapp-azure-dashboard

### Azure-Specific Commands
```bash
# Create Action Group
az monitor action-group create \
  --name ag-taskapp-alerts \
  --resource-group rg-taskapp-prod \
  --short-name taskapp \
  --email-receiver name=admin email=your-email@example.com

# Create metric alert (example: backend replicas = 0)
az monitor metrics alert create \
  --name "Backend Down - No Replicas" \
  --resource-group rg-taskapp-prod \
  --scopes [BACKEND_RESOURCE_ID] \
  --condition "avg Replicas == 0" \
  --window-size 5m \
  --evaluation-frequency 1m \
  --action ag-taskapp-alerts \
  --severity 0 \
  --description "Backend container app has no running replicas"

# Query logs with KQL
az monitor log-analytics query \
  --workspace [WORKSPACE_ID] \
  --analytics-query "ContainerAppConsoleLogs_CL | where ContainerAppName_s == 'ca-taskapp-backend' | where Log_s contains 'error' | take 50"
```

### Sample KQL Queries to Create
```kql
// Recent errors (last 24 hours)
ContainerAppConsoleLogs_CL
| where TimeGenerated > ago(24h)
| where Log_s contains "error" or Log_s contains "ERROR"
| project TimeGenerated, ContainerAppName_s, Log_s
| order by TimeGenerated desc
| take 100

// API response times (P95, P99)
ContainerAppConsoleLogs_CL
| where ContainerAppName_s == "ca-taskapp-backend"
| where Log_s contains "response_time"
| extend ResponseTime = todouble(extract(@"response_time=(\d+\.?\d*)", 1, Log_s))
| summarize P95=percentile(ResponseTime, 95), P99=percentile(ResponseTime, 99) by bin(TimeGenerated, 5m)
| render timechart

// Failed login attempts
ContainerAppConsoleLogs_CL
| where Log_s contains "login" and Log_s contains "failed"
| project TimeGenerated, Log_s
| order by TimeGenerated desc
```

### Lessons to Learn
- KQL (Kusto Query Language) syntax
- Log Analytics vs Application Insights
- Metric alerts vs log alerts
- Dashboard customization

### Estimated Cost
**Phase 9**: ~$5-10/month (Log Analytics ingestion and retention)
**Total so far**: ~$55-70/month

---

## Phase 10: Infrastructure as Code (Bicep or Terraform)

**Timeline**: Days 17-19
**Status**: Not Started
**Progress**: 0%

### Learning Goals
- Understand Azure Bicep (native IaC language)
- Alternative: Continue using Terraform for Azure
- Learn infrastructure export and import
- Practice modular infrastructure design

### Checklist - Option A: Bicep (Recommended for Azure)
- [ ] Install Bicep CLI
- [ ] Create azure/bicep directory structure
- [ ] Export existing resources to Bicep templates
- [ ] Create main.bicep (root template)
- [ ] Create modules
  - [ ] resourceGroup.bicep
  - [ ] virtualNetwork.bicep
  - [ ] database.bicep
  - [ ] containerRegistry.bicep
  - [ ] keyVault.bicep
  - [ ] containerApps.bicep
- [ ] Create parameters file (main.parameters.json)
- [ ] Define outputs in each module
- [ ] Validate Bicep templates
- [ ] Test deployment in separate resource group
- [ ] Document Bicep usage

### Checklist - Option B: Terraform (Familiar from AWS)
- [ ] Create azure/terraform directory structure
- [ ] Create provider.tf (Azure provider)
- [ ] Create variables.tf
- [ ] Create terraform.tfvars
- [ ] Create modules
  - [ ] resource-group
  - [ ] virtual-network
  - [ ] database
  - [ ] container-registry
  - [ ] key-vault
  - [ ] container-apps
- [ ] Configure remote state (Azure Storage Account)
- [ ] Run terraform init
- [ ] Import existing resources
- [ ] Run terraform plan
- [ ] Document Terraform usage

### Deliverables
- [ ] Complete IaC configuration (Bicep or Terraform)
- [ ] All existing infrastructure represented in code
- [ ] Modular and reusable templates
- [ ] Documentation for deployment

### Key Resources to Create
- **Bicep/Terraform Files**: Complete infrastructure definition
- **State Backend** (if Terraform): Azure Storage Account + Container

### Azure-Specific Commands (Bicep)
```bash
# Install Bicep
az bicep install

# Create main Bicep file
az bicep decompile --file template.json

# Validate Bicep template
az bicep build --file main.bicep

# Deploy Bicep template
az deployment group create \
  --resource-group rg-taskapp-prod \
  --template-file main.bicep \
  --parameters main.parameters.json

# What-if analysis (preview changes)
az deployment group what-if \
  --resource-group rg-taskapp-prod \
  --template-file main.bicep \
  --parameters main.parameters.json
```

### Lessons to Learn
- Bicep syntax and structure
- Modules and parameters
- Template validation
- What-if deployments (similar to terraform plan)
- Comparison: Bicep vs Terraform for Azure

### Estimated Cost
**Phase 10**: $0 (IaC tooling is free)

---

## Phase 11: CI/CD Integration (GitHub Actions for Azure)

**Timeline**: Days 20-21
**Status**: Not Started
**Progress**: 0%

### Learning Goals
- Understand Azure Service Principals
- Learn GitHub Actions for Azure deployment
- Practice automated container deployment
- Learn Azure Container Apps revisions

### Checklist
- [ ] Create Azure Service Principal for GitHub Actions
- [ ] Assign Contributor role to Service Principal
- [ ] Generate Service Principal credentials (JSON)
- [ ] Add Azure credentials to GitHub Secrets
  - [ ] AZURE_CREDENTIALS (Service Principal JSON)
  - [ ] AZURE_SUBSCRIPTION_ID
  - [ ] AZURE_RESOURCE_GROUP
  - [ ] ACR_NAME
  - [ ] ACR_LOGIN_SERVER
  - [ ] BACKEND_CONTAINER_APP
  - [ ] FRONTEND_CONTAINER_APP
  - [ ] DATABASE_URL
  - [ ] SECRET_KEY
  - [ ] JWT_SECRET_KEY
- [ ] Create GitHub Actions workflow: .github/workflows/azure-deploy-backend.yml
  - [ ] Trigger: push to main, paths: backend/**
  - [ ] Login to Azure
  - [ ] Login to ACR
  - [ ] Build backend Docker image
  - [ ] Push to ACR
  - [ ] Update backend Container App revision
- [ ] Create GitHub Actions workflow: .github/workflows/azure-deploy-frontend.yml
  - [ ] Trigger: push to main, paths: frontend/**
  - [ ] Login to Azure
  - [ ] Login to ACR
  - [ ] Build frontend Docker image (with build args)
  - [ ] Push to ACR
  - [ ] Update frontend Container App revision
- [ ] Test backend deployment workflow
- [ ] Test frontend deployment workflow
- [ ] Verify zero-downtime deployment (revision management)
- [ ] Test application after automated deployment
- [ ] Document CI/CD pipeline

### Deliverables
- [ ] Automated deployment pipeline operational
- [ ] Push-to-deploy functionality working
- [ ] Zero-downtime deployments
- [ ] Both backend and frontend auto-deploying

### Key Resources to Create
- **Service Principal**: sp-github-actions-taskapp
- **GitHub Secrets**: 10 secrets configured
- **Workflow Files**: azure-deploy-backend.yml, azure-deploy-frontend.yml

### Azure-Specific Commands
```bash
# Create Service Principal
az ad sp create-for-rbac \
  --name sp-github-actions-taskapp \
  --role contributor \
  --scopes /subscriptions/[SUBSCRIPTION_ID]/resourceGroups/rg-taskapp-prod \
  --sdk-auth

# Output will be JSON - add to GitHub Secrets as AZURE_CREDENTIALS

# Grant ACR pull/push permissions
az role assignment create \
  --assignee [SERVICE_PRINCIPAL_APP_ID] \
  --role AcrPush \
  --scope /subscriptions/[SUB_ID]/resourceGroups/rg-taskapp-prod/providers/Microsoft.ContainerRegistry/registries/taskappacr[unique]
```

### Sample GitHub Actions Workflow (Backend)
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
      
      - name: Deploy to Container App
        run: |
          az containerapp update \
            --name ${{ secrets.BACKEND_CONTAINER_APP }} \
            --resource-group ${{ secrets.AZURE_RESOURCE_GROUP }} \
            --image ${{ secrets.ACR_LOGIN_SERVER }}/taskapp-backend:${{ github.sha }}
```

### Lessons to Learn
- Service Principal vs Managed Identity for CI/CD
- Azure Container Apps revision management
- GitHub Actions for Azure
- Comparison: GitHub Actions for Azure vs AWS

### Estimated Cost
**Phase 11**: $0 (GitHub Actions free tier sufficient, Azure Service Principal free)

---

## Phase 12: Cost Optimization & Auto-Scaling

**Timeline**: Days 22-23
**Status**: Not Started
**Progress**: 0%

### Learning Goals
- Understand Azure cost management tools
- Learn Container Apps scaling rules
- Practice KEDA scaling configuration
- Optimize resource allocation

### Checklist
- [ ] Review Azure Cost Management dashboard
- [ ] Analyze cost breakdown by service
- [ ] Identify optimization opportunities
- [ ] Configure Container Apps scaling rules
  - [ ] Backend: HTTP concurrent requests rule
  - [ ] Frontend: HTTP concurrent requests rule
  - [ ] Min replicas: 1, Max replicas: 5
- [ ] Configure KEDA scaling (optional advanced)
  - [ ] CPU-based scaling
  - [ ] Memory-based scaling
  - [ ] Custom metrics scaling
- [ ] Set up scheduled scaling (optional)
  - [ ] Scale down during off-hours
  - [ ] Scale up during business hours
- [ ] Create Azure Budget
  - [ ] Monthly budget: $100
  - [ ] Alert at 80% actual spending
  - [ ] Alert at 100% forecasted spending
- [ ] Review database tier
  - [ ] Consider Burstable tier for development
  - [ ] Plan for General Purpose in production
- [ ] Configure ACR image retention policy
  - [ ] Keep last 20 images per repository
  - [ ] Delete untagged images after 30 days
- [ ] Review Log Analytics retention (30 days recommended)
- [ ] Document cost optimization strategies
- [ ] Compare costs with AWS deployment

### Deliverables
- [ ] Cost optimization report
- [ ] Auto-scaling configured
- [ ] Budget monitoring active
- [ ] Infrastructure cost-optimized

### Scaling Rules to Configure
```bash
# Add HTTP concurrent requests scaling rule (backend)
az containerapp update \
  --name ca-taskapp-backend \
  --resource-group rg-taskapp-prod \
  --min-replicas 1 \
  --max-replicas 5 \
  --scale-rule-name http-rule \
  --scale-rule-type http \
  --scale-rule-http-concurrency 100

# Add CPU scaling rule (backend)
az containerapp update \
  --name ca-taskapp-backend \
  --resource-group rg-taskapp-prod \
  --scale-rule-name cpu-rule \
  --scale-rule-type cpu \
  --scale-rule-metadata "type=Utilization" "value=70"
```

### Estimated Monthly Costs (Optimized)

| Resource | Cost |
|----------|------|
| Azure Database for PostgreSQL (Burstable B1ms) | $0 (free 12 months), then ~$15-20 |
| Container Apps (Backend + Frontend, avg 1.5 replicas each) | ~$20-25 |
| Container Registry (Basic) | ~$5 |
| Key Vault (4 secrets) | ~$0.12 |
| Log Analytics (30-day retention) | ~$5-10 |
| Virtual Network | $0 (free) |
| Azure DNS (if used) | ~$0.50 |
| **Total (first 12 months)** | **~$30-40/month** |
| **Total (after free tier)** | **~$45-60/month** |

**Cost Comparison with AWS:**
- AWS: ~$92/month
- Azure: ~$30-40/month (first year), ~$45-60/month (after)
- **Savings: ~50-60% cheaper than AWS!**

### Deliverables
- [ ] Detailed cost analysis
- [ ] Scaling rules configured
- [ ] Budget alerts active
- [ ] Cost optimization documented

### Lessons to Learn
- Azure free tier benefits (12 months vs AWS 12 months)
- Container Apps consumption pricing model
- KEDA scaling capabilities
- Cost Management + Billing tools

### Estimated Cost
**Phase 12**: $0 (tooling free, implementing optimizations)

---

## Phase 13: Final Documentation & Comparison

**Timeline**: Days 24-25
**Status**: Not Started
**Progress**: 0%

### Learning Goals
- Document complete Azure architecture
- Compare Azure vs AWS deployment
- Create knowledge base for future projects
- Prepare for potential GCP deployment

### Checklist
- [ ] Create Azure architecture diagram
- [ ] Create network architecture diagram
- [ ] Create data flow diagram
- [ ] Document all Azure resources created
- [ ] Create troubleshooting guide
- [ ] Document common issues and solutions
- [ ] Create cost breakdown spreadsheet
- [ ] Document lessons learned
  - [ ] What worked well
  - [ ] What was challenging
  - [ ] Azure-specific features used
  - [ ] Differences from AWS
- [ ] Create Azure deployment quick-start guide
- [ ] Take screenshots of Azure Portal
- [ ] Create Azure vs AWS comparison table
  - [ ] Services mapping
  - [ ] Cost comparison
  - [ ] Features comparison
  - [ ] Pros and cons of each platform
- [ ] Update README.md with Azure deployment info
- [ ] Create AZURE_DEPLOYMENT_COMPLETE.md summary
- [ ] Archive any temporary files
- [ ] Prepare for next cloud platform (GCP?)

### Deliverables
- [ ] Complete Azure documentation
- [ ] Architecture diagrams (3+)
- [ ] Cost comparison analysis
- [ ] Lessons learned document
- [ ] Troubleshooting guide
- [ ] Azure vs AWS comparison report

### Comparison Checklist

Create detailed comparison covering:
- [ ] Deployment complexity (which was easier?)
- [ ] Time to production (which was faster?)
- [ ] Cost efficiency (monthly spend comparison)
- [ ] Learning curve (which was easier to learn?)
- [ ] Documentation quality (AWS vs Azure docs)
- [ ] CLI experience (aws-cli vs az-cli)
- [ ] Web console experience (AWS Console vs Azure Portal)
- [ ] Service availability (which has better uptime?)
- [ ] Feature parity (which has more features?)
- [ ] Community support (Stack Overflow, forums)
- [ ] Security features
- [ ] Monitoring capabilities
- [ ] CI/CD integration
- [ ] Developer experience overall

---

## Progress Tracking

### Overall Status
- **Phases Completed**: 1/13
- **Days Elapsed**: 1/25
- **Progress**: 7.7%
- **Current Phase**: Phase 2 - Virtual Network Setup

### Phase Status Summary
| Phase | Name | Status | Days | Completion |
|-------|------|--------|------|------------|
| 1 | Account Setup | ✅ Complete | 1 | 100% |
| 2 | VNet & Networking | 🔄 In Progress | 2-3 | 0% |
| 3 | PostgreSQL Database | Not Started | 4-5 | 0% |
| 4 | Container Registry | Not Started | 6 | 0% |
| 5 | Key Vault | Not Started | 7 | 0% |
| 6 | Backend Container App | Not Started | 8-10 | 0% |
| 7 | Frontend Container App | Not Started | 11-12 | 0% |
| 8 | Domain & SSL | Not Started | 13-14 | 0% |
| 9 | Monitoring | Not Started | 15-16 | 0% |
| 10 | Infrastructure as Code | Not Started | 17-19 | 0% |
| 11 | CI/CD Integration | Not Started | 20-21 | 0% |
| 12 | Cost Optimization | Not Started | 22-23 | 0% |
| 13 | Documentation | Not Started | 24-25 | 0% |

---

## Key Resources Reference

### Azure Resource Naming Convention
Following Azure best practices:
- **Resource Group**: rg-taskapp-prod
- **Virtual Network**: vnet-taskapp
- **Subnets**: subnet-container-apps, subnet-database
- **Database**: taskapp-db-[suffix]
- **Container Registry**: taskappacr[unique]
- **Key Vault**: kv-taskapp-[unique]
- **Container Apps**: ca-taskapp-backend, ca-taskapp-frontend
- **Environment**: env-taskapp-prod

### Resource IDs (To be filled during deployment)
- **Subscription ID**: 84cbece2-bed5-48a8-9386-d5e8c71a64e8
- **Tenant ID**: 9caabd71-e9db-45fa-a229-b97dd83b562a
- **User Email**: vokeogigbah@yahoo.com
- **Primary Region**: eastus
- **Resource Group ID**: (to be created in Phase 2)
- **VNet ID**: (to be created in Phase 2)
- **Database Server**: (to be created in Phase 3)
- **ACR Login Server**: (to be created in Phase 4)
- **Backend Container App URL**: (to be created in Phase 6)
- **Frontend Container App URL**: (to be created in Phase 7)
- **Custom Domain**: (to be configured in Phase 8) 

---

## Notes & Observations

### Challenges Encountered
(To be filled during deployment)

### Solutions Implemented
(To be filled during deployment)

### Azure-Specific Learnings
(To be filled during deployment)

### Cost Insights
(To be filled during deployment)

### Comparison with AWS
(To be filled during deployment)

---

## Quick Reference

### Essential Azure CLI Commands
```bash
# Login
az login

# Set subscription
az account set --subscription [NAME_OR_ID]

# List resource groups
az group list --output table

# List all resources in resource group
az resource list --resource-group rg-taskapp-prod --output table

# View Container App logs (live streaming)
az containerapp logs show \
  --name ca-taskapp-backend \
  --resource-group rg-taskapp-prod \
  --follow

# Get Container App URL
az containerapp show \
  --name ca-taskapp-frontend \
  --resource-group rg-taskapp-prod \
  --query properties.configuration.ingress.fqdn \
  --output tsv

# Scale Container App manually
az containerapp update \
  --name ca-taskapp-backend \
  --resource-group rg-taskapp-prod \
  --min-replicas 2 \
  --max-replicas 10

# View costs
az consumption usage list --output table
```

### Useful Azure Portal Links
- Azure Portal: https://portal.azure.com
- Cost Management: https://portal.azure.com/#view/Microsoft_Azure_CostManagement
- Resource Groups: https://portal.azure.com/#view/HubsExtension/BrowseResourceGroups
- Container Apps: https://portal.azure.com/#view/HubsExtension/BrowseResource/resourceType/Microsoft.App%2FcontainerApps

--Last Updated**: January 26, 2026
**Current Status**: Phase 1 Complete - Starting Phase 2
**Next Step**: Create Resource Group and Virtual Network
**Target Completion**: February 20, 2026 (25 days from start)
**Live Application**: TBD

---

## Phase 1 Completion Summary ✅

**Completed**: January 26, 2026  
**Duration**: 1 day

### Achievements:
- ✅ Azure account created with $200 free credits
- ✅ Billing alerts configured ($100/month budget, 80% & 100% alerts)
- ✅ Azure CLI installed (version 2.80.0) and configured for Git Bash
- ✅ Authentication working (Subscription: 84cbece2-bed5-48a8-9386-d5e8c71a64e8)
- ✅ MFA enabled for account security
- ✅ Region selected: East US (eastus)
- ✅ Project directory structure created (azure/bicep, scripts, config, docs)
- ✅ .gitignore updated with Azure-specific patterns

### Account Details:
- **Email**: vokeogigbah@yahoo.com
- **Subscription**: Azure subscription 1
- **Subscription ID**: 84cbece2-bed5-48a8-9386-d5e8c71a64e8
- **Tenant ID**: 9caabd71-e9db-45fa-a229-b97dd83b562a
- **Region**: East US (eastus)

### Files Created:
- `AZURE_DEPLOYMENT_ROADMAP.md` - Complete deployment roadmap
- `AZURE_PHASE_1_GUIDE.md` - Phase 1 detailed guide
- `AZURE_PROGRESS.md` - Progress tracking document
- `azure/` directory structure with READMEs
- Updated `.gitignore` for Azure files
- Updated `~/.bashrc` with Azure CLI alias for Git Bash

**Ready for Phase 2!** 🚀ing Phase
**Next Step**: Create Azure free account and install Azure CLI
**Target Completion**: February 20, 2026 (25 days from start)
**Live Application**: TBD
