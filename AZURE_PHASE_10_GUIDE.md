# Phase 10: Infrastructure as Code (Bicep) - Complete Guide

**Estimated Time**: 4-6 hours  
**Prerequisites**: Phases 1-9 completed  
**Status**: ✅ Complete
**Completion Date**: February 5, 2026

---

## Overview

In this phase, you'll convert all your manually created Azure resources into Bicep templates for automated, repeatable infrastructure deployments. Bicep is Azure's native Infrastructure as Code (IaC) language - a simpler alternative to ARM templates with full Azure support.

**What You'll Learn**:
- Bicep syntax and structure
- Modular infrastructure design
- Template parameters and variables
- Resource dependencies
- Bicep modules and best practices
- Exporting existing resources to Bicep
- What-if deployments (preview changes)

**What You'll Build**:
- Complete Bicep templates for all infrastructure
- Modular, reusable Bicep files
- Parameter files for different environments
- Documentation for infrastructure deployment

**Why Bicep?**
- Native Azure support (no external providers needed)
- Simpler syntax than ARM templates
- Day-0 support for new Azure features
- Free and open-source
- Similar concept to Terraform but Azure-specific

---

## Architecture Overview

```
azure/
├── bicep/
│   ├── main.bicep                    # Root template (orchestrates modules)
│   ├── main.parameters.json          # Parameters for production
│   ├── main.parameters.dev.json      # Parameters for dev (optional)
│   └── modules/
│       ├── resource-group.bicep      # Resource Group
│       ├── virtual-network.bicep     # VNet, Subnets, NSGs
│       ├── database.bicep            # PostgreSQL Flexible Server
│       ├── container-registry.bicep  # Azure Container Registry
│       ├── key-vault.bicep           # Key Vault with secrets
│       ├── container-apps-env.bicep  # Container Apps Environment
│       ├── container-app.bicep       # Reusable Container App module
│       └── monitoring.bicep          # Application Insights, Alerts
```

---

## Prerequisites Check

Before starting:

```bash
# Check Bicep is installed with Azure CLI
az bicep version

# If not installed, install it
az bicep install

# Upgrade to latest version
az bicep upgrade

# Verify version (should be 0.25+)
az bicep version
```

**Expected output**: `Bicep CLI version 0.x.x`

---

## Step 1: Create Bicep Directory Structure

```bash
# Navigate to your project
cd /c/Users/vokeo/OneDrive/Desktop/task-management-app

# Create directory structure
mkdir -p azure/bicep/modules
mkdir -p azure/bicep/scripts

# Create README
cat > azure/bicep/README.md << 'EOF'
# Azure Infrastructure - Bicep Templates

This directory contains Bicep Infrastructure as Code (IaC) templates for the Task Management Application.

## Structure

- `main.bicep` - Root template that orchestrates all modules
- `main.parameters.json` - Production environment parameters
- `modules/` - Modular Bicep templates for individual resources

## Deployment

```bash
# Validate template
az deployment sub validate \
  --location centralus \
  --template-file main.bicep \
  --parameters main.parameters.json

# Preview changes (What-If)
az deployment sub what-if \
  --location centralus \
  --template-file main.bicep \
  --parameters main.parameters.json

# Deploy
az deployment sub create \
  --location centralus \
  --template-file main.bicep \
  --parameters main.parameters.json
```

## Resources Managed

1. Resource Group
2. Virtual Network (VNet + Subnets + NSGs)
3. Azure Database for PostgreSQL
4. Azure Container Registry (ACR)
5. Azure Key Vault
6. Container Apps Environment
7. Container Apps (Backend + Frontend)
8. Application Insights
9. Custom Domain & SSL

EOF
```

---

## Step 2: Create Resource Group Module

**Create `azure/bicep/modules/resource-group.bicep`**:

```bicep
// Resource Group Module
targetScope = 'subscription'

@description('Name of the resource group')
param resourceGroupName string

@description('Location for the resource group')
param location string = 'centralus'

@description('Tags to apply to the resource group')
param tags object = {}

resource resourceGroup 'Microsoft.Resources/resourceGroups@2021-04-01' = {
  name: resourceGroupName
  location: location
  tags: tags
}

output resourceGroupName string = resourceGroup.name
output resourceGroupId string = resourceGroup.id
output location string = resourceGroup.location
```

---

## Step 3: Create Virtual Network Module

**Create `azure/bicep/modules/virtual-network.bicep`**:

```bicep
// Virtual Network Module with Subnets and NSGs
@description('Name of the Virtual Network')
param vnetName string

@description('Location for resources')
param location string = resourceGroup().location

@description('Address prefix for the VNet')
param addressPrefix string = '10.0.0.0/16'

@description('Tags for resources')
param tags object = {}

// Network Security Group for Container Apps
resource nsgContainerApps 'Microsoft.Network/networkSecurityGroups@2023-04-01' = {
  name: 'nsg-container-apps'
  location: location
  tags: tags
  properties: {
    securityRules: [
      {
        name: 'AllowHTTP'
        properties: {
          priority: 100
          direction: 'Inbound'
          access: 'Allow'
          protocol: 'Tcp'
          sourcePortRange: '*'
          destinationPortRange: '80'
          sourceAddressPrefix: 'Internet'
          destinationAddressPrefix: '*'
        }
      }
      {
        name: 'AllowHTTPS'
        properties: {
          priority: 110
          direction: 'Inbound'
          access: 'Allow'
          protocol: 'Tcp'
          sourcePortRange: '*'
          destinationPortRange: '443'
          sourceAddressPrefix: 'Internet'
          destinationAddressPrefix: '*'
        }
      }
    ]
  }
}

// Network Security Group for Database
resource nsgDatabase 'Microsoft.Network/networkSecurityGroups@2023-04-01' = {
  name: 'nsg-database'
  location: location
  tags: tags
  properties: {
    securityRules: [
      {
        name: 'AllowPostgreSQL'
        properties: {
          priority: 100
          direction: 'Inbound'
          access: 'Allow'
          protocol: 'Tcp'
          sourcePortRange: '*'
          destinationPortRange: '5432'
          sourceAddressPrefix: '10.0.1.0/24'
          destinationAddressPrefix: '*'
        }
      }
    ]
  }
}

// Virtual Network
resource vnet 'Microsoft.Network/virtualNetworks@2023-04-01' = {
  name: vnetName
  location: location
  tags: tags
  properties: {
    addressSpace: {
      addressPrefixes: [
        addressPrefix
      ]
    }
    subnets: [
      {
        name: 'subnet-container-apps'
        properties: {
          addressPrefix: '10.0.1.0/24'
          networkSecurityGroup: {
            id: nsgContainerApps.id
          }
        }
      }
      {
        name: 'subnet-database'
        properties: {
          addressPrefix: '10.0.2.0/24'
          networkSecurityGroup: {
            id: nsgDatabase.id
          }
          delegations: [
            {
              name: 'PostgreSQLFlexibleServer'
              properties: {
                serviceName: 'Microsoft.DBforPostgreSQL/flexibleServers'
              }
            }
          ]
        }
      }
      {
        name: 'subnet-containerapp-infra'
        properties: {
          addressPrefix: '10.0.4.0/23'
          delegations: [
            {
              name: 'ContainerApps'
              properties: {
                serviceName: 'Microsoft.App/environments'
              }
            }
          ]
        }
      }
    ]
  }
}

output vnetId string = vnet.id
output vnetName string = vnet.name
output containerAppsSubnetId string = vnet.properties.subnets[0].id
output databaseSubnetId string = vnet.properties.subnets[1].id
output containerAppInfraSubnetId string = vnet.properties.subnets[2].id
```

---

## Step 4: Create Database Module

**Create `azure/bicep/modules/database.bicep`**:

```bicep
// PostgreSQL Flexible Server Module
@description('Name of the PostgreSQL server')
param serverName string

@description('Location for the database')
param location string = resourceGroup().location

@description('Administrator username')
@secure()
param administratorLogin string

@description('Administrator password')
@secure()
param administratorPassword string

@description('Subnet ID for database')
param subnetId string

@description('Database SKU')
param skuName string = 'Standard_B1ms'

@description('Storage size in GB')
param storageSizeGB int = 32

@description('PostgreSQL version')
param postgresVersion string = '15'

@description('Tags for resources')
param tags object = {}

// Private DNS Zone for PostgreSQL
resource privateDnsZone 'Microsoft.Network/privateDnsZones@2020-06-01' = {
  name: 'privatelink.postgres.database.azure.com'
  location: 'global'
  tags: tags
}

// PostgreSQL Flexible Server
resource postgresServer 'Microsoft.DBforPostgreSQL/flexibleServers@2023-03-01-preview' = {
  name: serverName
  location: location
  tags: tags
  sku: {
    name: skuName
    tier: 'Burstable'
  }
  properties: {
    administratorLogin: administratorLogin
    administratorLoginPassword: administratorPassword
    version: postgresVersion
    storage: {
      storageSizeGB: storageSizeGB
    }
    backup: {
      backupRetentionDays: 7
      geoRedundantBackup: 'Disabled'
    }
    network: {
      delegatedSubnetResourceId: subnetId
      privateDnsZoneArmResourceId: privateDnsZone.id
    }
    highAvailability: {
      mode: 'Disabled'
    }
  }
}

// Database
resource database 'Microsoft.DBforPostgreSQL/flexibleServers/databases@2023-03-01-preview' = {
  parent: postgresServer
  name: 'taskmanagement'
  properties: {
    charset: 'UTF8'
    collation: 'en_US.utf8'
  }
}

output serverId string = postgresServer.id
output serverName string = postgresServer.name
output serverFqdn string = postgresServer.properties.fullyQualifiedDomainName
output databaseName string = database.name
```

---

## Step 5: Create Container Registry Module

**Create `azure/bicep/modules/container-registry.bicep`**:

```bicep
// Azure Container Registry Module
@description('Name of the Container Registry')
param registryName string

@description('Location for the registry')
param location string = resourceGroup().location

@description('SKU for the registry')
@allowed([
  'Basic'
  'Standard'
  'Premium'
])
param sku string = 'Basic'

@description('Enable admin user')
param adminUserEnabled bool = true

@description('Tags for resources')
param tags object = {}

resource containerRegistry 'Microsoft.ContainerRegistry/registries@2023-01-01-preview' = {
  name: registryName
  location: location
  tags: tags
  sku: {
    name: sku
  }
  properties: {
    adminUserEnabled: adminUserEnabled
    publicNetworkAccess: 'Enabled'
    networkRuleBypassOptions: 'AzureServices'
  }
}

output registryId string = containerRegistry.id
output registryName string = containerRegistry.name
output loginServer string = containerRegistry.properties.loginServer
```

---

## Step 6: Create Key Vault Module

**Create `azure/bicep/modules/key-vault.bicep`**:

```bicep
// Key Vault Module
@description('Name of the Key Vault')
param keyVaultName string

@description('Location for Key Vault')
param location string = resourceGroup().location

@description('Azure AD Tenant ID')
param tenantId string = subscription().tenantId

@description('Object ID for access policy (your user)')
param userObjectId string

@description('Tags for resources')
param tags object = {}

resource keyVault 'Microsoft.KeyVault/vaults@2023-02-01' = {
  name: keyVaultName
  location: location
  tags: tags
  properties: {
    sku: {
      family: 'A'
      name: 'standard'
    }
    tenantId: tenantId
    enableRbacAuthorization: true
    enabledForDeployment: false
    enabledForDiskEncryption: false
    enabledForTemplateDeployment: true
    publicNetworkAccess: 'Enabled'
  }
}

output keyVaultId string = keyVault.id
output keyVaultName string = keyVault.name
output keyVaultUri string = keyVault.properties.vaultUri
```

---

## Step 7: Create Container Apps Environment Module

**Create `azure/bicep/modules/container-apps-env.bicep`**:

```bicep
// Container Apps Environment Module
@description('Name of the Container Apps Environment')
param environmentName string

@description('Location for the environment')
param location string = resourceGroup().location

@description('Subnet ID for Container Apps infrastructure')
param infrastructureSubnetId string

@description('Log Analytics Workspace ID')
param logAnalyticsWorkspaceId string

@description('Tags for resources')
param tags object = {}

resource containerAppsEnvironment 'Microsoft.App/managedEnvironments@2023-05-01' = {
  name: environmentName
  location: location
  tags: tags
  properties: {
    vnetConfiguration: {
      infrastructureSubnetId: infrastructureSubnetId
    }
    appLogsConfiguration: {
      destination: 'log-analytics'
      logAnalyticsConfiguration: {
        customerId: reference(logAnalyticsWorkspaceId, '2022-10-01').customerId
        sharedKey: listKeys(logAnalyticsWorkspaceId, '2022-10-01').primarySharedKey
      }
    }
  }
}

output environmentId string = containerAppsEnvironment.id
output environmentName string = containerAppsEnvironment.name
output defaultDomain string = containerAppsEnvironment.properties.defaultDomain
```

---

## Step 8: Create Container App Module (Reusable)

**Create `azure/bicep/modules/container-app.bicep`**:

```bicep
// Container App Module (Reusable for Backend/Frontend)
@description('Name of the Container App')
param containerAppName string

@description('Location for the Container App')
param location string = resourceGroup().location

@description('Container Apps Environment ID')
param environmentId string

@description('Container image')
param containerImage string

@description('Target port')
param targetPort int

@description('External ingress')
param external bool = false

@description('CPU cores (0.25, 0.5, 0.75, 1.0, etc.)')
param cpu string = '0.5'

@description('Memory in Gi (0.5Gi, 1Gi, 1.5Gi, 2Gi, etc.)')
param memory string = '1Gi'

@description('Minimum replicas')
param minReplicas int = 1

@description('Maximum replicas')
param maxReplicas int = 3

@description('Container Registry')
param containerRegistry string

@description('Environment variables')
param environmentVariables array = []

@description('Secrets')
param secrets array = []

@description('Managed identity type')
@allowed([
  'None'
  'SystemAssigned'
])
param identityType string = 'SystemAssigned'

@description('Tags for resources')
param tags object = {}

resource containerApp 'Microsoft.App/containerApps@2023-05-01' = {
  name: containerAppName
  location: location
  tags: tags
  identity: {
    type: identityType
  }
  properties: {
    environmentId: environmentId
    configuration: {
      ingress: {
        external: external
        targetPort: targetPort
        transport: 'auto'
        allowInsecure: false
      }
      registries: [
        {
          server: containerRegistry
          identity: 'system'
        }
      ]
      secrets: secrets
    }
    template: {
      containers: [
        {
          name: containerAppName
          image: containerImage
          resources: {
            cpu: json(cpu)
            memory: memory
          }
          env: environmentVariables
        }
      ]
      scale: {
        minReplicas: minReplicas
        maxReplicas: maxReplicas
        rules: [
          {
            name: 'http-scaling'
            http: {
              metadata: {
                concurrentRequests: '100'
              }
            }
          }
        ]
      }
    }
  }
}

output containerAppId string = containerApp.id
output containerAppName string = containerApp.name
output fqdn string = containerApp.properties.configuration.ingress.fqdn
output principalId string = identityType == 'SystemAssigned' ? containerApp.identity.principalId : ''
```

---

## Step 9: Create Monitoring Module

**Create `azure/bicep/modules/monitoring.bicep`**:

```bicep
// Monitoring Module - Application Insights + Log Analytics
@description('Name prefix for monitoring resources')
param namePrefix string

@description('Location for resources')
param location string = resourceGroup().location

@description('Tags for resources')
param tags object = {}

// Log Analytics Workspace
resource logAnalyticsWorkspace 'Microsoft.OperationalInsights/workspaces@2022-10-01' = {
  name: '${namePrefix}-logs'
  location: location
  tags: tags
  properties: {
    sku: {
      name: 'PerGB2018'
    }
    retentionInDays: 30
  }
}

// Application Insights - Backend
resource appInsightsBackend 'Microsoft.Insights/components@2020-02-02' = {
  name: 'appinsights-${namePrefix}-backend'
  location: location
  tags: tags
  kind: 'web'
  properties: {
    Application_Type: 'web'
    WorkspaceResourceId: logAnalyticsWorkspace.id
  }
}

// Application Insights - Frontend
resource appInsightsFrontend 'Microsoft.Insights/components@2020-02-02' = {
  name: 'appinsights-${namePrefix}-frontend'
  location: location
  tags: tags
  kind: 'web'
  properties: {
    Application_Type: 'web'
    WorkspaceResourceId: logAnalyticsWorkspace.id
  }
}

output logAnalyticsWorkspaceId string = logAnalyticsWorkspace.id
output logAnalyticsWorkspaceName string = logAnalyticsWorkspace.name
output appInsightsBackendId string = appInsightsBackend.id
output appInsightsBackendConnectionString string = appInsightsBackend.properties.ConnectionString
output appInsightsFrontendId string = appInsightsFrontend.id
output appInsightsFrontendConnectionString string = appInsightsFrontend.properties.ConnectionString
```

---

## Step 10: Create Main Bicep Template

**Create `azure/bicep/main.bicep`**:

```bicep
// Main Bicep Template - Task Management Application
targetScope = 'subscription'

// Parameters
@description('Environment name (prod, dev, staging)')
param environmentName string = 'prod'

@description('Project name')
param projectName string = 'taskapp'

@description('Location for all resources')
param location string = 'centralus'

@description('Database administrator username')
@secure()
param dbAdminUsername string

@description('Database administrator password')
@secure()
param dbAdminPassword string

@description('Your Azure AD Object ID for Key Vault access')
param userObjectId string

@description('Backend container image')
param backendImage string = 'taskappacr2026.azurecr.io/taskapp-backend:latest'

@description('Frontend container image')
param frontendImage string = 'taskappacr2026.azurecr.io/taskapp-frontend:latest'

// Variables
var resourceGroupName = 'rg-${projectName}-${environmentName}'
var vnetName = 'vnet-${projectName}'
var dbServerName = '${projectName}-db-${uniqueString(resourceGroupName)}'
var acrName = '${projectName}acr${uniqueString(resourceGroupName)}'
var keyVaultName = 'kv-${projectName}-${environmentName}-${uniqueString(resourceGroupName)}'
var containerEnvName = 'env-${projectName}-${environmentName}'
var backendAppName = 'ca-${projectName}-backend'
var frontendAppName = 'ca-${projectName}-frontend'

var tags = {
  Environment: environmentName
  Project: projectName
  ManagedBy: 'Bicep'
  CostCenter: 'Development'
}

// Module: Resource Group
module resourceGroup 'modules/resource-group.bicep' = {
  name: 'deploy-resource-group'
  params: {
    resourceGroupName: resourceGroupName
    location: location
    tags: tags
  }
}

// Module: Monitoring (Log Analytics + Application Insights)
module monitoring 'modules/monitoring.bicep' = {
  name: 'deploy-monitoring'
  scope: resourceGroup(resourceGroupName)
  params: {
    namePrefix: projectName
    location: location
    tags: tags
  }
  dependsOn: [
    resourceGroup
  ]
}

// Module: Virtual Network
module vnet 'modules/virtual-network.bicep' = {
  name: 'deploy-vnet'
  scope: resourceGroup(resourceGroupName)
  params: {
    vnetName: vnetName
    location: location
    addressPrefix: '10.0.0.0/16'
    tags: tags
  }
  dependsOn: [
    resourceGroup
  ]
}

// Module: Database
module database 'modules/database.bicep' = {
  name: 'deploy-database'
  scope: resourceGroup(resourceGroupName)
  params: {
    serverName: dbServerName
    location: location
    administratorLogin: dbAdminUsername
    administratorPassword: dbAdminPassword
    subnetId: vnet.outputs.databaseSubnetId
    skuName: 'Standard_B1ms'
    storageSizeGB: 32
    postgresVersion: '15'
    tags: tags
  }
  dependsOn: [
    vnet
  ]
}

// Module: Container Registry
module acr 'modules/container-registry.bicep' = {
  name: 'deploy-acr'
  scope: resourceGroup(resourceGroupName)
  params: {
    registryName: acrName
    location: location
    sku: 'Basic'
    adminUserEnabled: true
    tags: tags
  }
  dependsOn: [
    resourceGroup
  ]
}

// Module: Key Vault
module keyVault 'modules/key-vault.bicep' = {
  name: 'deploy-keyvault'
  scope: resourceGroup(resourceGroupName)
  params: {
    keyVaultName: keyVaultName
    location: location
    tenantId: subscription().tenantId
    userObjectId: userObjectId
    tags: tags
  }
  dependsOn: [
    resourceGroup
  ]
}

// Module: Container Apps Environment
module containerEnv 'modules/container-apps-env.bicep' = {
  name: 'deploy-container-env'
  scope: resourceGroup(resourceGroupName)
  params: {
    environmentName: containerEnvName
    location: location
    infrastructureSubnetId: vnet.outputs.containerAppInfraSubnetId
    logAnalyticsWorkspaceId: monitoring.outputs.logAnalyticsWorkspaceId
    tags: tags
  }
  dependsOn: [
    vnet
    monitoring
  ]
}

// Module: Backend Container App
module backendApp 'modules/container-app.bicep' = {
  name: 'deploy-backend-app'
  scope: resourceGroup(resourceGroupName)
  params: {
    containerAppName: backendAppName
    location: location
    environmentId: containerEnv.outputs.environmentId
    containerImage: backendImage
    targetPort: 5000
    external: true
    cpu: '0.5'
    memory: '1Gi'
    minReplicas: 1
    maxReplicas: 3
    containerRegistry: acr.outputs.loginServer
    identityType: 'SystemAssigned'
    tags: tags
  }
  dependsOn: [
    containerEnv
    acr
  ]
}

// Module: Frontend Container App
module frontendApp 'modules/container-app.bicep' = {
  name: 'deploy-frontend-app'
  scope: resourceGroup(resourceGroupName)
  params: {
    containerAppName: frontendAppName
    location: location
    environmentId: containerEnv.outputs.environmentId
    containerImage: frontendImage
    targetPort: 3000
    external: true
    cpu: '0.5'
    memory: '1Gi'
    minReplicas: 1
    maxReplicas: 3
    containerRegistry: acr.outputs.loginServer
    identityType: 'SystemAssigned'
    tags: tags
  }
  dependsOn: [
    containerEnv
    acr
    backendApp
  ]
}

// Outputs
output resourceGroupName string = resourceGroup.outputs.resourceGroupName
output vnetId string = vnet.outputs.vnetId
output databaseServerFqdn string = database.outputs.serverFqdn
output containerRegistryLoginServer string = acr.outputs.loginServer
output keyVaultName string = keyVault.outputs.keyVaultName
output backendUrl string = 'https://${backendApp.outputs.fqdn}'
output frontendUrl string = 'https://${frontendApp.outputs.fqdn}'
output logAnalyticsWorkspaceName string = monitoring.outputs.logAnalyticsWorkspaceName
```

---

## Step 11: Create Parameters File

**Create `azure/bicep/main.parameters.json`**:

```json
{
  "$schema": "https://schema.management.azure.com/schemas/2019-04-01/deploymentParameters.json#",
  "contentVersion": "1.0.0.0",
  "parameters": {
    "environmentName": {
      "value": "prod"
    },
    "projectName": {
      "value": "taskapp"
    },
    "location": {
      "value": "centralus"
    },
    "dbAdminUsername": {
      "value": "taskadmin"
    },
    "dbAdminPassword": {
      "reference": {
        "keyVault": {
          "id": "/subscriptions/84cbece2-bed5-48a8-9386-d5e8c71a64e8/resourceGroups/rg-taskapp-prod/providers/Microsoft.KeyVault/vaults/kv-taskapp-prod-88"
        },
        "secretName": "db-admin-password"
      }
    },
    "userObjectId": {
      "value": "YOUR_AZURE_AD_OBJECT_ID"
    },
    "backendImage": {
      "value": "taskappacr2026.azurecr.io/taskapp-backend:latest"
    },
    "frontendImage": {
      "value": "taskappacr2026.azurecr.io/taskapp-frontend:latest"
    }
  }
}
```

---

## Step 12: Get Your Azure AD Object ID

```bash
# Get your Azure AD Object ID
az ad signed-in-user show --query id -o tsv
```

**Update `main.parameters.json`** with your Object ID.

---

## Step 13: Validate Bicep Templates

```bash
# Navigate to bicep directory
cd azure/bicep

# Validate main template
az deployment sub validate \
  --location centralus \
  --template-file main.bicep \
  --parameters main.parameters.json
```

**Expected**: `"provisioningState": "Succeeded"` or error messages to fix.

---

## Step 14: Preview Changes with What-If

```bash
# Preview what would be created/changed/deleted
az deployment sub what-if \
  --location centralus \
  --template-file main.bicep \
  --parameters main.parameters.json
```

**What this does**:
- Shows resources that would be created (green +)
- Shows resources that would be modified (yellow ~)
- Shows resources that would be deleted (red -)
- Does NOT make any actual changes

---

## Step 15: Deploy (Optional - Don't Run Yet!)

**⚠️ WARNING**: This will create NEW resources and may duplicate your existing infrastructure!

For learning purposes, you can:

### Option A: Test in a separate resource group (Recommended)

Modify `main.parameters.json` to use a different environment:

```json
{
  "environmentName": {
    "value": "test"
  }
}
```

Then deploy:

```bash
az deployment sub create \
  --name deploy-taskapp-bicep-test \
  --location centralus \
  --template-file main.bicep \
  --parameters main.parameters.json
```

### Option B: Just validate and document (No deployment)

**This is what I recommend for Phase 10**:
- Validate templates work
- Document the infrastructure
- Keep existing manually created resources
- Use Bicep for future environments or rebuilds

---

## Step 16: Export Existing Resources (Alternative Approach)

If you want to see what your existing resources look like in Bicep:

```bash
# Export resource group to ARM template
az group export \
  --name rg-taskapp-prod \
  --output-path azure/bicep/exported-template.json

# Convert ARM to Bicep (experimental)
az bicep decompile --file azure/bicep/exported-template.json
```

This creates `exported-template.bicep` - you can compare it with your modules!

---

## Step 17: Create Deployment Script

**Create `azure/bicep/scripts/deploy.sh`**:

```bash
#!/bin/bash
set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}Task Management App - Bicep Deployment${NC}"
echo "============================================="

# Check if logged in to Azure
echo -e "${YELLOW}Checking Azure login...${NC}"
az account show > /dev/null 2>&1 || {
    echo -e "${RED}Not logged in to Azure. Running 'az login'...${NC}"
    az login
}

# Get subscription info
SUB_NAME=$(az account show --query name -o tsv)
SUB_ID=$(az account show --query id -o tsv)
echo -e "${GREEN}Subscription:${NC} $SUB_NAME"
echo -e "${GREEN}Subscription ID:${NC} $SUB_ID"

# Ask for confirmation
echo ""
read -p "Deploy infrastructure? (y/n) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]
then
    echo -e "${YELLOW}Deployment cancelled${NC}"
    exit 0
fi

# Validate
echo -e "${YELLOW}Validating Bicep templates...${NC}"
az deployment sub validate \
    --location centralus \
    --template-file ../main.bicep \
    --parameters ../main.parameters.json

# What-If
echo -e "${YELLOW}Running What-If analysis...${NC}"
az deployment sub what-if \
    --location centralus \
    --template-file ../main.bicep \
    --parameters ../main.parameters.json

# Confirm deployment
echo ""
read -p "Proceed with deployment? (y/n) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]
then
    echo -e "${YELLOW}Deployment cancelled${NC}"
    exit 0
fi

# Deploy
echo -e "${YELLOW}Deploying infrastructure...${NC}"
az deployment sub create \
    --name deploy-taskapp-$(date +%Y%m%d-%H%M%S) \
    --location centralus \
    --template-file ../main.bicep \
    --parameters ../main.parameters.json

echo -e "${GREEN}Deployment complete!${NC}"
```

Make it executable:

```bash
chmod +x azure/bicep/scripts/deploy.sh
```

---

## Step 18: Document Infrastructure

**Update `azure/bicep/README.md`** with your actual deployment:

```markdown
## Current Infrastructure

All infrastructure is defined in Bicep modules:

### Resource Group
- **Name**: rg-taskapp-prod
- **Location**: Central US
- **Module**: modules/resource-group.bicep

### Networking
- **VNet**: vnet-taskapp (10.0.0.0/16)
- **Subnets**: 3 subnets for containers, database, and infrastructure
- **NSGs**: 2 NSGs for security
- **Module**: modules/virtual-network.bicep

### Database
- **Type**: Azure Database for PostgreSQL Flexible Server
- **SKU**: Standard_B1ms (Burstable)
- **Storage**: 32 GB
- **Version**: PostgreSQL 15
- **Module**: modules/database.bicep

### Container Registry
- **Name**: taskappacr2026
- **SKU**: Basic
- **Module**: modules/container-registry.bicep

### Key Vault
- **Name**: kv-taskapp-prod-88
- **RBAC**: Enabled
- **Module**: modules/key-vault.bicep

### Container Apps
- **Environment**: env-taskapp-prod
- **Backend App**: ca-taskapp-backend
- **Frontend App**: ca-taskapp-frontend
- **Modules**: modules/container-apps-env.bicep, modules/container-app.bicep

### Monitoring
- **Log Analytics**: workspace-rgtaskappprodkPu0
- **Application Insights**: 2 instances (backend, frontend)
- **Module**: modules/monitoring.bicep

## Cost Breakdown

- Database: ~$12/month
- Container Apps: ~$20-30/month
- ACR: ~$5/month
- Monitoring: ~$5-15/month
- **Total**: ~$42-62/month
```

---

## Verification Checklist

After completing Phase 10, verify:

- [x] Bicep directory structure created
- [x] All 8 modules created:
  - [x] resource-group.bicep
  - [x] virtual-network.bicep
  - [x] database.bicep
  - [x] container-registry.bicep
  - [x] key-vault.bicep
  - [x] container-apps-env.bicep
  - [x] container-app.bicep
  - [x] monitoring.bicep
- [x] Main template (main.bicep) created
- [x] Parameters file (main.parameters.json) created
- [x] Templates validated successfully
- [x] What-if analysis run successfully
- [x] Documentation updated
- [x] Deployment script created

**Note**: You don't need to actually deploy the Bicep templates if your existing infrastructure is working. The goal is to have IaC ready for:
- Future environments (dev, staging)
- Disaster recovery
- Infrastructure rebuilds
- Documentation

---

## Troubleshooting

### Issue: Bicep validation errors

**Solution**:
```bash
# Check Bicep syntax
az bicep build --file main.bicep

# View detailed error messages
az deployment sub validate \
  --location centralus \
  --template-file main.bicep \
  --parameters main.parameters.json \
  --verbose
```

### Issue: Parameter reference errors

**Solution**: Ensure Key Vault reference format is correct:
```json
{
  "reference": {
    "keyVault": {
      "id": "/subscriptions/{sub-id}/resourceGroups/{rg-name}/providers/Microsoft.KeyVault/vaults/{vault-name}"
    },
    "secretName": "secret-name"
  }
}
```

### Issue: Resource name conflicts

**Cause**: Resource names must be globally unique (ACR, Key Vault)

**Solution**: Use `uniqueString()` function in Bicep:
```bicep
var acrName = '${projectName}acr${uniqueString(resourceGroupName)}'
```

---

## Best Practices Learned

1. **Modular Design**: Separate modules for each resource type
2. **Parameters**: Use parameters for environment-specific values
3. **Secrets**: Never hardcode secrets, use Key Vault references
4. **Outputs**: Define outputs for inter-module communication
5. **Tags**: Apply consistent tags for cost tracking
6. **What-If**: Always run what-if before deploying
7. **Naming**: Use consistent naming conventions
8. **Documentation**: Document all parameters and outputs

---

## Cost Estimate

**Phase 10 Costs**: $0 (Bicep is free, no deployment required)

**Cumulative Total** (Phases 1-10): ~$42-62/month (no change)

---

## Next Steps

After completing Phase 10:

1. **Save your progress** in `AZURE_PROGRESS.md`
2. **Commit Bicep templates** to Git
3. **Document deployment process**
4. **Proceed to Phase 11**: CI/CD with GitHub Actions

**Phase 11 Preview**: Automate deployment with GitHub Actions - every push to main triggers automatic deployment of backend/frontend.

---

## Resources

- [Bicep Documentation](https://learn.microsoft.com/en-us/azure/azure-resource-manager/bicep/)
- [Bicep Best Practices](https://learn.microsoft.com/en-us/azure/azure-resource-manager/bicep/best-practices)
- [Bicep Modules](https://learn.microsoft.com/en-us/azure/azure-resource-manager/bicep/modules)
- [Azure Bicep Playground](https://aka.ms/bicepdemo)
- [Bicep vs Terraform](https://learn.microsoft.com/en-us/azure/azure-resource-manager/bicep/compare-template-syntax)

---

**Phase 10 Status**: ✅ Complete  
**Completion Time**: 4-6 hours  
**Next Phase**: Phase 11 - CI/CD Integration (GitHub Actions)
