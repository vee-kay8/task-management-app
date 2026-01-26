# Azure Phase 2: Resource Group & Virtual Network Setup - Complete Guide

**Duration**: 2-3 hours  
**Difficulty**: Beginner-Intermediate  
**Prerequisites**: Phase 1 complete (Azure account, CLI installed, authenticated)  
**Goal**: Create isolated network infrastructure for your application

---

## 📋 Overview

This phase builds the network foundation for your Azure deployment. By the end, you'll have:

✅ Resource Group created (container for all Azure resources)  
✅ Virtual Network (VNet) with proper IP addressing  
✅ Two subnets (Container Apps and Database)  
✅ Network Security Groups configured (firewall rules)  
✅ Network architecture documented  

---

## Table of Contents

1. [Understanding Azure Networking](#understanding-azure-networking)
2. [Create Resource Group](#step-1-create-resource-group)
3. [Create Virtual Network](#step-2-create-virtual-network)
4. [Create Subnets](#step-3-create-subnets)
5. [Create Network Security Groups](#step-4-create-network-security-groups)
6. [Configure NSG Rules](#step-5-configure-nsg-rules)
7. [Associate NSGs with Subnets](#step-6-associate-nsgs-with-subnets)
8. [Verify Network Setup](#step-7-verify-network-setup)
9. [Phase 2 Completion Checklist](#phase-2-completion-checklist)

---

## Understanding Azure Networking

### What is a Resource Group? 📦

A **Resource Group** is a logical container for Azure resources. Think of it as a folder that holds all related resources.

**Benefits:**
- **Organization**: Group related resources together
- **Management**: Manage all resources as a single unit
- **Billing**: Track costs by resource group
- **Deletion**: Delete all resources at once

**Best Practice:** One resource group per environment (dev, staging, prod)

### What is a Virtual Network (VNet)? 🌐

A **Virtual Network** is your private network in Azure. It's like your own isolated section of the Azure datacenter.

**AWS Equivalent:** VPC (Virtual Private Cloud)

**Key Concepts:**
- **Address Space**: IP range for your VNet (e.g., 10.0.0.0/16)
- **Subnets**: Smaller IP ranges within the VNet
- **CIDR Notation**: /16 means 65,536 IPs, /24 means 256 IPs

### What is a Subnet? 🗂️

A **Subnet** divides your VNet into smaller, manageable sections.

**Why use subnets?**
- **Isolation**: Separate different tiers (web, app, database)
- **Security**: Apply different security rules per subnet
- **Organization**: Logical grouping of resources

### What is a Network Security Group (NSG)? 🔐

An **NSG** is a firewall that filters network traffic to and from Azure resources.

**AWS Equivalent:** Security Groups

**How it works:**
- **Rules**: Allow or deny traffic based on source, destination, port, protocol
- **Priority**: Lower numbers = higher priority (100 = first, 4096 = last)
- **Default Rules**: Azure adds default allow/deny rules

---

## Architecture Overview

Here's what we'll build in Phase 2:

```
┌─────────────────────────────────────────────────────────────────┐
│  Resource Group: rg-taskapp-prod                                │
│  Region: East US                                                │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌───────────────────────────────────────────────────────────┐ │
│  │  Virtual Network: vnet-taskapp                            │ │
│  │  Address Space: 10.0.0.0/16 (65,536 IPs)                 │ │
│  │                                                           │ │
│  │  ┌─────────────────────────┐  ┌─────────────────────────┐│ │
│  │  │ Subnet: Container Apps  │  │ Subnet: Database        ││ │
│  │  │ 10.0.1.0/24 (256 IPs)   │  │ 10.0.2.0/24 (256 IPs)   ││ │
│  │  │                         │  │                         ││ │
│  │  │ NSG: nsg-container-apps │  │ NSG: nsg-database       ││ │
│  │  │ - Allow HTTP (80)       │  │ - Allow PostgreSQL      ││ │
│  │  │ - Allow HTTPS (443)     │  │   (5432) from           ││ │
│  │  │ - Allow all outbound    │  │   Container Apps subnet ││ │
│  │  │                         │  │ - Deny all other        ││ │
│  │  └─────────────────────────┘  └─────────────────────────┘│ │
│  │                                                           │ │
│  └───────────────────────────────────────────────────────────┘ │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### IP Address Planning

| Resource | CIDR | Range | IPs Available | Purpose |
|----------|------|-------|---------------|---------|
| **VNet** | 10.0.0.0/16 | 10.0.0.0 - 10.0.255.255 | 65,536 | Entire network |
| **Subnet: Container Apps** | 10.0.1.0/24 | 10.0.1.0 - 10.0.1.255 | 256 | Frontend & Backend containers |
| **Subnet: Database** | 10.0.2.0/24 | 10.0.2.0 - 10.0.2.255 | 256 | PostgreSQL database |

> 💡 **Why 10.0.0.0?** This is a private IP range (RFC 1918). It won't conflict with public internet IPs.

---

## Step 1: Create Resource Group

### What You're Creating

A Resource Group named `rg-taskapp-prod` that will contain all your Azure resources.

**Naming Convention:**
- `rg-` = Resource Group
- `taskapp` = Project name
- `prod` = Environment (production)

### Option A: Console (Azure Portal) Method

**Step-by-step:**

1. **Navigate to Resource Groups**
   - Go to Azure Portal: https://portal.azure.com
   - Click **"Resource groups"** in the left menu
   - Or search for "Resource groups" in the top search bar

2. **Create New Resource Group**
   - Click **"+ Create"** button at the top
   
3. **Fill in Basic Details**
   - **Subscription**: Select your subscription (Azure subscription 1)
   - **Resource group**: `rg-taskapp-prod`
   - **Region**: East US (must match what you chose in Phase 1)
   
4. **Add Tags (Recommended)**
   - Click **"Next: Tags"** button
   - Add the following tags:
     - **Name**: `Environment`, **Value**: `Production`
     - **Name**: `Project`, **Value**: `TaskApp`
     - **Name**: `ManagedBy`, **Value**: `Manual`
     - **Name**: `CostCenter`, **Value**: `Learning`
   
   > 💡 **Why tags?** They help organize resources, track costs, and automate management.

5. **Review and Create**
   - Click **"Next: Review + create"**
   - Verify all details are correct
   - Click **"Create"**

6. **Confirmation**
   - Wait 3-5 seconds for creation
   - You'll see: "Your deployment is complete"
   - Click **"Go to resource group"**

### Option B: CLI Method (Recommended)

**Step-by-step:**

1. **Open Terminal**
   - Use Git Bash, PowerShell, or Command Prompt

2. **Verify Azure CLI is Working**
   ```bash
   az --version
   # Should show: azure-cli 2.80.0 or higher
   ```

3. **Check Current Subscription**
   ```bash
   az account show --query "{Name:name, SubscriptionId:id}" --output table
   ```
   
   **Expected output:**
   ```
   Name                  SubscriptionId
   --------------------  ------------------------------------
   Azure subscription 1  84cbece2-bed5-48a8-9386-d5e8c71a64e8
   ```

4. **Create Resource Group**
   ```bash
   az group create \
     --name rg-taskapp-prod \
     --location eastus \
     --tags Environment=Production Project=TaskApp ManagedBy=Manual CostCenter=Learning
   ```
   
   **Expected output:**
   ```json
   {
     "id": "/subscriptions/84cbece2-bed5-48a8-9386-d5e8c71a64e8/resourceGroups/rg-taskapp-prod",
     "location": "eastus",
     "managedBy": null,
     "name": "rg-taskapp-prod",
     "properties": {
       "provisioningState": "Succeeded"
     },
     "tags": {
       "CostCenter": "Learning",
       "Environment": "Production",
       "ManagedBy": "Manual",
       "Project": "TaskApp"
     },
     "type": "Microsoft.Resources/resourceGroups"
   }
   ```

5. **Verify Creation**
   ```bash
   # List all resource groups
   az group list --output table
   
   # Show specific resource group
   az group show --name rg-taskapp-prod --output table
   ```

### Troubleshooting

**Error: "The subscription is not registered to use namespace 'Microsoft.Resources'"**
```bash
# Register the provider
az provider register --namespace Microsoft.Resources

# Wait 1-2 minutes, then try again
```

**Error: "Location 'eastus' is invalid"**
```bash
# List valid locations
az account list-locations --query "[].name" --output table

# Use the exact name from the list
```

### What Just Happened? 🤔

- **Resource Group Created**: Container for all your Azure resources
- **Location Set**: All resources in this group will default to East US
- **Tags Applied**: Easy to track and manage resources
- **Billing Scope**: You can now see costs for this resource group

### Save These Details

```
Resource Group Information
==========================
Name: rg-taskapp-prod
Location: eastus
Subscription: 84cbece2-bed5-48a8-9386-d5e8c71a64e8
Resource ID: /subscriptions/84cbece2-bed5-48a8-9386-d5e8c71a64e8/resourceGroups/rg-taskapp-prod
Tags: Environment=Production, Project=TaskApp, ManagedBy=Manual, CostCenter=Learning
```

---

## Step 2: Create Virtual Network

### What You're Creating

A Virtual Network named `vnet-taskapp` with address space 10.0.0.0/16.

### Option A: Console (Azure Portal) Method

**Step-by-step:**

1. **Navigate to Virtual Networks**
   - In Azure Portal, search for "Virtual networks"
   - Click **"Virtual networks"**
   - Click **"+ Create"**

2. **Basics Tab**
   - **Subscription**: Your subscription
   - **Resource group**: Select `rg-taskapp-prod`
   - **Name**: `vnet-taskapp`
   - **Region**: East US (should be pre-filled)
   - Click **"Next: IP Addresses"**

3. **IP Addresses Tab**
   - **IPv4 address space**: `10.0.0.0/16`
   - **Delete any existing subnets** (we'll create custom ones)
   - Click **"Next: Security"**

4. **Security Tab**
   - **BastionHost**: Disabled
   - **DDoS Protection**: Basic (free)
   - **Firewall**: Disabled
   - Click **"Next: Tags"**

5. **Tags Tab**
   - Tags are inherited from resource group
   - Click **"Next: Review + create"**

6. **Review and Create**
   - Verify settings
   - Click **"Create"**
   - Wait 10-20 seconds for deployment

### Option B: CLI Method (Recommended)

```bash
# Create Virtual Network
az network vnet create \
  --resource-group rg-taskapp-prod \
  --name vnet-taskapp \
  --address-prefix 10.0.0.0/16 \
  --location eastus
```

**Expected output:**
```json
{
  "newVNet": {
    "addressSpace": {
      "addressPrefixes": [
        "10.0.0.0/16"
      ]
    },
    "enableDdosProtection": false,
    "id": "/subscriptions/.../resourceGroups/rg-taskapp-prod/providers/Microsoft.Network/virtualNetworks/vnet-taskapp",
    "location": "eastus",
    "name": "vnet-taskapp",
    "provisioningState": "Succeeded",
    "resourceGroup": "rg-taskapp-prod",
    "subnets": [],
    "type": "Microsoft.Network/virtualNetworks"
  }
}
```

### Verify Creation

```bash
# List all VNets in resource group
az network vnet list --resource-group rg-taskapp-prod --output table

# Show specific VNet details
az network vnet show --resource-group rg-taskapp-prod --name vnet-taskapp --output json
```

### What Just Happened? 🤔

- **VNet Created**: Your private network in Azure (10.0.0.0/16 = 65,536 IPs)
- **DDoS Protection**: Basic protection enabled (free)
- **No Subnets Yet**: We'll create custom subnets next
- **Isolated**: Your VNet is isolated from other Azure customers

---

## Step 3: Create Subnets

### What You're Creating

Two subnets within your VNet:
1. **subnet-container-apps** (10.0.1.0/24) - For Container Apps
2. **subnet-database** (10.0.2.0/24) - For PostgreSQL database

### Subnet 1: Container Apps

**CLI Method:**

```bash
az network vnet subnet create \
  --resource-group rg-taskapp-prod \
  --vnet-name vnet-taskapp \
  --name subnet-container-apps \
  --address-prefix 10.0.1.0/24
```

**Expected output:**
```json
{
  "addressPrefix": "10.0.1.0/24",
  "id": "/subscriptions/.../subnets/subnet-container-apps",
  "name": "subnet-container-apps",
  "privateEndpointNetworkPolicies": "Disabled",
  "privateLinkServiceNetworkPolicies": "Enabled",
  "provisioningState": "Succeeded",
  "resourceGroup": "rg-taskapp-prod"
}
```

### Subnet 2: Database

```bash
az network vnet subnet create \
  --resource-group rg-taskapp-prod \
  --vnet-name vnet-taskapp \
  --name subnet-database \
  --address-prefix 10.0.2.0/24 \
  --delegations Microsoft.DBforPostgreSQL/flexibleServers
```

> 💡 **Note**: `--delegations` allows Azure Database for PostgreSQL to use this subnet

**Expected output:**
```json
{
  "addressPrefix": "10.0.2.0/24",
  "delegations": [
    {
      "name": "Microsoft.DBforPostgreSQL.flexibleServers",
      "serviceName": "Microsoft.DBforPostgreSQL/flexibleServers"
    }
  ],
  "id": "/subscriptions/.../subnets/subnet-database",
  "name": "subnet-database",
  "provisioningState": "Succeeded",
  "resourceGroup": "rg-taskapp-prod"
}
```

### Verify Subnets

```bash
# List all subnets in VNet
az network vnet subnet list \
  --resource-group rg-taskapp-prod \
  --vnet-name vnet-taskapp \
  --output table
```

**Expected output:**
```
Name                    AddressPrefix    ProvisioningState
----------------------  ---------------  -------------------
subnet-container-apps   10.0.1.0/24      Succeeded
subnet-database         10.0.2.0/24      Succeeded
```

### What Just Happened? 🤔

- **Two Subnets Created**: Logical separation within your VNet
- **IP Ranges Assigned**: 256 IPs each (10.0.1.0/24 and 10.0.2.0/24)
- **Database Delegation**: subnet-database can only be used by PostgreSQL
- **Container Apps Subnet**: General purpose, will hold our containers

---

## Step 4: Create Network Security Groups

### What You're Creating

Two NSGs (firewalls):
1. **nsg-container-apps** - For Container Apps subnet
2. **nsg-database** - For Database subnet

### NSG 1: Container Apps

```bash
az network nsg create \
  --resource-group rg-taskapp-prod \
  --name nsg-container-apps \
  --location eastus
```

**Expected output:**
```json
{
  "NewNSG": {
    "defaultSecurityRules": [...],
    "id": "/subscriptions/.../networkSecurityGroups/nsg-container-apps",
    "location": "eastus",
    "name": "nsg-container-apps",
    "provisioningState": "Succeeded",
    "resourceGroup": "rg-taskapp-prod",
    "securityRules": []
  }
}
```

### NSG 2: Database

```bash
az network nsg create \
  --resource-group rg-taskapp-prod \
  --name nsg-database \
  --location eastus
```

### Verify NSGs

```bash
# List all NSGs
az network nsg list --resource-group rg-taskapp-prod --output table
```

**Expected output:**
```
Name                 Location    ResourceGroup
-------------------  ----------  ---------------
nsg-container-apps   eastus      rg-taskapp-prod
nsg-database         eastus      rg-taskapp-prod
```

### What Just Happened? 🤔

- **NSGs Created**: Two firewalls, currently with default rules only
- **Default Rules**: Azure adds allow/deny rules automatically
- **No Custom Rules Yet**: We'll add specific rules in next step

---

## Step 5: Configure NSG Rules

### Understanding NSG Rules

Each NSG rule has:
- **Name**: Descriptive name
- **Priority**: 100-4096 (lower = higher priority)
- **Direction**: Inbound or Outbound
- **Access**: Allow or Deny
- **Protocol**: TCP, UDP, ICMP, or * (any)
- **Source**: IP, CIDR, Service Tag, or ASG
- **Destination**: IP, CIDR, Service Tag, or ASG
- **Port**: Specific port or range

### NSG Rules for Container Apps

**Rule 1: Allow HTTP (port 80)**

```bash
az network nsg rule create \
  --resource-group rg-taskapp-prod \
  --nsg-name nsg-container-apps \
  --name AllowHTTP \
  --priority 100 \
  --direction Inbound \
  --access Allow \
  --protocol Tcp \
  --source-address-prefixes '*' \
  --source-port-ranges '*' \
  --destination-address-prefixes '*' \
  --destination-port-ranges 80 \
  --description "Allow HTTP traffic from internet"
```

**Rule 2: Allow HTTPS (port 443)**

```bash
az network nsg rule create \
  --resource-group rg-taskapp-prod \
  --nsg-name nsg-container-apps \
  --name AllowHTTPS \
  --priority 110 \
  --direction Inbound \
  --access Allow \
  --protocol Tcp \
  --source-address-prefixes '*' \
  --source-port-ranges '*' \
  --destination-address-prefixes '*' \
  --destination-port-ranges 443 \
  --description "Allow HTTPS traffic from internet"
```

**Verify Container Apps NSG Rules:**

```bash
az network nsg rule list \
  --resource-group rg-taskapp-prod \
  --nsg-name nsg-container-apps \
  --output table
```

### NSG Rules for Database

**Rule 1: Allow PostgreSQL from Container Apps subnet**

```bash
az network nsg rule create \
  --resource-group rg-taskapp-prod \
  --nsg-name nsg-database \
  --name AllowPostgreSQLFromContainerApps \
  --priority 100 \
  --direction Inbound \
  --access Allow \
  --protocol Tcp \
  --source-address-prefixes 10.0.1.0/24 \
  --source-port-ranges '*' \
  --destination-address-prefixes '*' \
  --destination-port-ranges 5432 \
  --description "Allow PostgreSQL from Container Apps subnet only"
```

**Rule 2: Deny all other inbound (explicit)**

```bash
az network nsg rule create \
  --resource-group rg-taskapp-prod \
  --nsg-name nsg-database \
  --name DenyAllInbound \
  --priority 4096 \
  --direction Inbound \
  --access Deny \
  --protocol '*' \
  --source-address-prefixes '*' \
  --source-port-ranges '*' \
  --destination-address-prefixes '*' \
  --destination-port-ranges '*' \
  --description "Deny all other inbound traffic"
```

> 💡 **Note**: Priority 4096 is the lowest (last evaluated). Azure has default deny at 65000.

**Verify Database NSG Rules:**

```bash
az network nsg rule list \
  --resource-group rg-taskapp-prod \
  --nsg-name nsg-database \
  --output table
```

**Expected output:**
```
Name                               Priority  Direction  Access
---------------------------------  --------  ---------  ------
AllowPostgreSQLFromContainerApps   100       Inbound    Allow
DenyAllInbound                     4096      Inbound    Deny
```

### What Just Happened? 🤔

- **HTTP/HTTPS Rules**: Container Apps can receive traffic from internet
- **PostgreSQL Rule**: Database only accepts connections from Container Apps subnet
- **Security by Design**: Database is isolated from internet
- **Default Outbound**: Both NSGs allow all outbound by default

---

## Step 6: Associate NSGs with Subnets

### What You're Doing

Attaching the NSGs to their respective subnets to enforce firewall rules.

### Associate NSG with Container Apps Subnet

```bash
az network vnet subnet update \
  --resource-group rg-taskapp-prod \
  --vnet-name vnet-taskapp \
  --name subnet-container-apps \
  --network-security-group nsg-container-apps
```

**Expected output:**
```json
{
  "addressPrefix": "10.0.1.0/24",
  "id": "/subscriptions/.../subnets/subnet-container-apps",
  "name": "subnet-container-apps",
  "networkSecurityGroup": {
    "id": "/subscriptions/.../networkSecurityGroups/nsg-container-apps"
  },
  "provisioningState": "Succeeded"
}
```

### Associate NSG with Database Subnet

```bash
az network vnet subnet update \
  --resource-group rg-taskapp-prod \
  --vnet-name vnet-taskapp \
  --name subnet-database \
  --network-security-group nsg-database
```

### Verify Associations

```bash
# Check both subnets
az network vnet subnet show \
  --resource-group rg-taskapp-prod \
  --vnet-name vnet-taskapp \
  --name subnet-container-apps \
  --query "{Name:name, AddressPrefix:addressPrefix, NSG:networkSecurityGroup.id}" \
  --output table

az network vnet subnet show \
  --resource-group rg-taskapp-prod \
  --vnet-name vnet-taskapp \
  --name subnet-database \
  --query "{Name:name, AddressPrefix:addressPrefix, NSG:networkSecurityGroup.id}" \
  --output table
```

### What Just Happened? 🤔

- **NSGs Attached**: Firewall rules now active on subnets
- **Traffic Filtering**: All traffic in/out of subnets is checked against NSG rules
- **Security Enforced**: Database can only be accessed from Container Apps subnet

---

## Step 7: Verify Network Setup

### Verification Checklist

Run these commands to verify everything is set up correctly:

```bash
# 1. Verify Resource Group
az group show --name rg-taskapp-prod --output table

# 2. Verify VNet
az network vnet show \
  --resource-group rg-taskapp-prod \
  --name vnet-taskapp \
  --query "{Name:name, Location:location, AddressSpace:addressSpace.addressPrefixes}" \
  --output table

# 3. List all subnets
az network vnet subnet list \
  --resource-group rg-taskapp-prod \
  --vnet-name vnet-taskapp \
  --output table

# 4. List all NSGs
az network nsg list \
  --resource-group rg-taskapp-prod \
  --output table

# 5. Check Container Apps NSG rules
az network nsg rule list \
  --resource-group rg-taskapp-prod \
  --nsg-name nsg-container-apps \
  --query "[].{Name:name, Priority:priority, Direction:direction, Access:access, Protocol:protocol, DestinationPort:destinationPortRange}" \
  --output table

# 6. Check Database NSG rules
az network nsg rule list \
  --resource-group rg-taskapp-prod \
  --nsg-name nsg-database \
  --query "[].{Name:name, Priority:priority, Direction:direction, Access:access, Protocol:protocol, DestinationPort:destinationPortRange}" \
  --output table

# 7. List all resources in resource group
az resource list \
  --resource-group rg-taskapp-prod \
  --output table
```

### Expected Results Summary

| Check | Expected Result | Status |
|-------|----------------|--------|
| Resource Group exists | rg-taskapp-prod in eastus | ⬜ |
| VNet created | vnet-taskapp with 10.0.0.0/16 | ⬜ |
| Subnets created | 2 subnets (container-apps, database) | ⬜ |
| NSGs created | 2 NSGs (nsg-container-apps, nsg-database) | ⬜ |
| Container Apps NSG rules | HTTP (80), HTTPS (443) allowed | ⬜ |
| Database NSG rules | PostgreSQL (5432) from 10.0.1.0/24 | ⬜ |
| NSGs associated | Both subnets have NSGs attached | ⬜ |
| Total resources | 5 resources in resource group | ⬜ |

**✅ Mark each box when verified!**

### View in Azure Portal

1. Go to https://portal.azure.com
2. Navigate to **Resource groups** → **rg-taskapp-prod**
3. You should see 5 resources:
   - vnet-taskapp (Virtual network)
   - nsg-container-apps (Network security group)
   - nsg-database (Network security group)
   - subnet-container-apps (will appear under vnet-taskapp)
   - subnet-database (will appear under vnet-taskapp)

4. Click on **vnet-taskapp** → **Topology** to see visual diagram

### Troubleshooting

**Issue: Can't find resource group**
```bash
# List all resource groups
az group list --output table

# Make sure you're in the right subscription
az account show --query name
```

**Issue: NSG rules not showing**
```bash
# Get full NSG details
az network nsg show --resource-group rg-taskapp-prod --name nsg-container-apps
```

**Issue: Subnet doesn't have NSG**
```bash
# Re-run the association command
az network vnet subnet update \
  --resource-group rg-taskapp-prod \
  --vnet-name vnet-taskapp \
  --name subnet-container-apps \
  --network-security-group nsg-container-apps
```

---

## Cost Analysis

### What You're Paying For

| Resource | Cost | Notes |
|----------|------|-------|
| **Resource Group** | $0 | Free (logical container) |
| **Virtual Network** | $0 | Free (no charges for VNet itself) |
| **Subnets** | $0 | Free (part of VNet) |
| **Network Security Groups** | $0 | Free (NSG rules are free) |
| **Data Transfer** | Varies | Pay for data going out of Azure |

**Phase 2 Total Cost: $0** ✅

> 💡 **Future Costs**: When you deploy resources (containers, database) into these subnets, those resources will have costs. The networking infrastructure itself is free!

---

## Document Your Network Architecture

Create a network documentation file to track your setup:

```bash
cat > azure/docs/NETWORK_ARCHITECTURE.md << 'EOF'
# Network Architecture - Task Management App

**Created**: January 26, 2026  
**Environment**: Production  
**Region**: East US

## Resource Group

- **Name**: rg-taskapp-prod
- **Location**: eastus
- **Subscription**: 84cbece2-bed5-48a8-9386-d5e8c71a64e8

## Virtual Network

- **Name**: vnet-taskapp
- **Address Space**: 10.0.0.0/16 (65,536 IPs)
- **DNS Servers**: Azure-provided
- **DDoS Protection**: Basic (free tier)

## Subnets

### Subnet 1: Container Apps
- **Name**: subnet-container-apps
- **Address Range**: 10.0.1.0/24 (256 IPs)
- **Available IPs**: 251 (Azure reserves 5)
- **Purpose**: Azure Container Apps (frontend + backend)
- **Network Security Group**: nsg-container-apps

### Subnet 2: Database
- **Name**: subnet-database
- **Address Range**: 10.0.2.0/24 (256 IPs)
- **Available IPs**: 251 (Azure reserves 5)
- **Purpose**: Azure Database for PostgreSQL Flexible Server
- **Delegation**: Microsoft.DBforPostgreSQL/flexibleServers
- **Network Security Group**: nsg-database

## Network Security Groups

### NSG: nsg-container-apps

**Inbound Rules**:
| Priority | Name | Port | Protocol | Source | Destination | Action |
|----------|------|------|----------|--------|-------------|--------|
| 100 | AllowHTTP | 80 | TCP | * | * | Allow |
| 110 | AllowHTTPS | 443 | TCP | * | * | Allow |

**Outbound Rules**:
- Default: Allow all outbound

### NSG: nsg-database

**Inbound Rules**:
| Priority | Name | Port | Protocol | Source | Destination | Action |
|----------|------|------|----------|--------|-------------|--------|
| 100 | AllowPostgreSQLFromContainerApps | 5432 | TCP | 10.0.1.0/24 | * | Allow |
| 4096 | DenyAllInbound | * | * | * | * | Deny |

**Outbound Rules**:
- Default: Allow all outbound

## Security Design

- **Database Isolation**: PostgreSQL only accessible from Container Apps subnet
- **Public Access**: Container Apps can receive HTTP/HTTPS from internet
- **Private Communication**: Container-to-database communication stays within VNet
- **No Internet Access to DB**: Database cannot be accessed from public internet

## Future Additions

- Phase 3: Azure Database for PostgreSQL in subnet-database
- Phase 6: Backend Container App in subnet-container-apps
- Phase 7: Frontend Container App in subnet-container-apps

EOF

echo "✅ Network architecture documented"
```

---

## Phase 2 Completion Checklist

Before proceeding to Phase 3, ensure all tasks are complete:

### Resource Group ✅
- [ ] Resource group `rg-taskapp-prod` created
- [ ] Location set to East US
- [ ] Tags applied (Environment, Project, ManagedBy, CostCenter)
- [ ] Resource group ID saved

### Virtual Network ✅
- [ ] VNet `vnet-taskapp` created
- [ ] Address space 10.0.0.0/16 configured
- [ ] DDoS protection (basic) enabled
- [ ] VNet visible in Azure Portal

### Subnets ✅
- [ ] Subnet `subnet-container-apps` created (10.0.1.0/24)
- [ ] Subnet `subnet-database` created (10.0.2.0/24)
- [ ] Database subnet delegated to PostgreSQL
- [ ] Both subnets visible under VNet

### Network Security Groups ✅
- [ ] NSG `nsg-container-apps` created
- [ ] NSG `nsg-database` created
- [ ] HTTP rule (port 80) added to nsg-container-apps
- [ ] HTTPS rule (port 443) added to nsg-container-apps
- [ ] PostgreSQL rule (port 5432) added to nsg-database
- [ ] Deny all rule added to nsg-database

### NSG Associations ✅
- [ ] nsg-container-apps associated with subnet-container-apps
- [ ] nsg-database associated with subnet-database
- [ ] Associations verified via CLI

### Documentation ✅
- [ ] Network architecture documented
- [ ] IP address plan documented
- [ ] NSG rules documented
- [ ] Resource IDs saved
- [ ] Network diagram created (optional)

### Verification ✅
- [ ] All verification commands run successfully
- [ ] 5 resources exist in resource group
- [ ] VNet topology viewed in Portal
- [ ] No errors in Azure Portal
- [ ] Ready to proceed to Phase 3!

---

## What You've Accomplished! 🎉

Congratulations! You've completed Phase 2. Here's what you built:

### Network Infrastructure ✅
- ✅ **Resource Group**: Logical container for all resources
- ✅ **Virtual Network**: Isolated private network (10.0.0.0/16)
- ✅ **Two Subnets**: Container Apps (10.0.1.0/24) and Database (10.0.2.0/24)
- ✅ **Two NSGs**: Firewall rules for security
- ✅ **Secure Design**: Database isolated from internet

### Security Implemented ✅
- ✅ **Public Access**: Container Apps accessible via HTTP/HTTPS
- ✅ **Private Access**: Database only accessible from Container Apps
- ✅ **Network Segmentation**: Logical separation of tiers
- ✅ **Defense in Depth**: Multiple layers of security

### Skills Gained 🧠
- ✅ **Azure Networking**: VNets, subnets, CIDR notation
- ✅ **Network Security**: NSGs, security rules, priorities
- ✅ **Resource Organization**: Resource groups, tags
- ✅ **Azure CLI**: Creating and managing resources via CLI

---

## Next Steps → Phase 3

You're now ready to create the database!

**Phase 3 Preview - Azure Database for PostgreSQL:**
- Create PostgreSQL Flexible Server
- Configure VNet integration (private access)
- Initialize database schema
- Set up firewall rules
- Store credentials securely
- Test database connectivity

**Estimated Time**: 2-3 hours  
**New Concepts**: Managed databases, VNet integration, connection strings

**First command you'll run in Phase 3:**
```bash
az postgres flexible-server create \
  --resource-group rg-taskapp-prod \
  --name taskapp-db-[unique-suffix] \
  --location eastus \
  --admin-user taskapp_admin \
  --vnet vnet-taskapp \
  --subnet subnet-database
```

---

## Useful Resources

### Official Documentation
- **Virtual Networks**: https://learn.microsoft.com/en-us/azure/virtual-network/
- **Network Security Groups**: https://learn.microsoft.com/en-us/azure/virtual-network/network-security-groups-overview
- **Subnets**: https://learn.microsoft.com/en-us/azure/virtual-network/virtual-network-manage-subnet
- **Azure Networking**: https://learn.microsoft.com/en-us/azure/networking/

### Tools
- **Azure Portal**: https://portal.azure.com
- **Network Topology Viewer**: Portal → VNet → Topology
- **Azure IP Calculator**: https://www.subnet-calculator.com/cidr.php

### Learning Resources
- **Microsoft Learn - Networking**: https://learn.microsoft.com/training/paths/azure-network-fundamentals/
- **Network Security Best Practices**: https://learn.microsoft.com/azure/security/fundamentals/network-best-practices

---

## Phase 2 Complete! ✅

**Date Completed**: _______________  
**Time Spent**: _______________  
**Challenges Faced**: _______________  
**Notes**: _______________

**Resources Created:**
- [x] Resource Group: rg-taskapp-prod
- [x] Virtual Network: vnet-taskapp
- [x] Subnet: subnet-container-apps
- [x] Subnet: subnet-database
- [x] NSG: nsg-container-apps
- [x] NSG: nsg-database

**Ready for Phase 3?** YES / NO

If YES, proceed to `AZURE_PHASE_3_GUIDE.md` (to be created)  
If NO, review any incomplete checklist items above.

---

**Happy Azure Networking! 🚀☁️**
