# Azure Phase 5: Key Vault - Complete Guide

**Duration**: 1-2 hours  
**Difficulty**: Beginner-Intermediate  
**Prerequisites**: Phase 1-4 complete (Account setup, VNet, Database, Container Registry)  
**Goal**: Create Azure Key Vault and securely store application secrets

---

## 📋 Overview

This phase sets up Azure Key Vault to manage your application secrets securely. By the end, you'll have:

✅ Azure Key Vault created  
✅ Database password stored securely  
✅ JWT secret key generated and stored  
✅ Access policies configured  
✅ Secrets tested and verified  
✅ Ready for Container Apps integration (Phase 6-7)

**Why Key Vault?** Azure Key Vault is a cloud service for securely storing and accessing secrets, encryption keys, and certificates. It eliminates hardcoding sensitive data in your application code.

---

## Table of Contents

1. [Understanding Azure Key Vault](#understanding-azure-key-vault)
2. [Create Azure Key Vault](#step-1-create-azure-key-vault)
3. [Generate and Store Secrets](#step-2-generate-and-store-secrets)
4. [Configure Access Policies](#step-3-configure-access-policies)
5. [Test Secret Retrieval](#step-4-test-secret-retrieval)
6. [Document Secret References](#step-5-document-secret-references)
7. [Phase 5 Completion Checklist](#phase-5-completion-checklist)

---

## Understanding Azure Key Vault

### What is Azure Key Vault? 🔐

**Azure Key Vault** is a cloud-based service for securely storing and managing:
- **Secrets**: Passwords, connection strings, API keys, tokens
- **Keys**: Cryptographic keys for encryption/decryption
- **Certificates**: SSL/TLS certificates

**AWS Equivalent:** AWS Secrets Manager + AWS KMS (Key Management Service)

### Why Use Key Vault?

| Benefit | Description |
|---------|-------------|
| **Security** | Secrets never exposed in code, config files, or environment variables |
| **Centralized** | Single source of truth for all secrets |
| **Access Control** | Fine-grained permissions via RBAC and access policies |
| **Audit Logs** | Track who accessed which secrets and when |
| **Versioning** | Automatic secret versioning and rotation support |
| **Azure Integration** | Container Apps, VMs, Functions can access via managed identity |
| **Encryption** | All secrets encrypted at rest with Azure-managed keys |

### Key Vault Concepts

#### 1. **Secrets**
Sensitive values stored as key-value pairs (e.g., database passwords, API keys).

**Example:**
```
Secret Name: db-password
Secret Value: SuperSecret123!@#
Version: v1 (auto-generated)
```

#### 2. **Access Policies vs RBAC**

Azure Key Vault supports two permission models:

| Model | How It Works | Best For |
|-------|--------------|----------|
| **Access Policies** | Traditional model - grant specific permissions (get, list, set) to users/apps | Legacy applications, specific permission needs |
| **RBAC** | Modern model - assign Azure roles (Key Vault Secrets Officer, Reader) | New deployments, easier management, Azure AD integration |

> 💡 **For This Project**: We'll use **RBAC** (recommended for new projects).

#### 3. **Managed Identity Integration**

In Phase 6-7, Container Apps will use **managed identities** to access Key Vault:
- No passwords or connection strings in app configuration
- Azure handles authentication automatically
- Most secure method

```
┌─────────────────┐         ┌─────────────────┐         ┌─────────────────┐
│ Container App   │ ──────▶ │ Managed         │ ──────▶ │ Key Vault       │
│ (Backend)       │         │ Identity        │         │ (Secrets)       │
└─────────────────┘         └─────────────────┘         └─────────────────┘
     Requests                   Authenticates                Returns
     secret                     automatically                secret value
```

### Key Vault Pricing

**Standard Tier** (we'll use this):
- **Secret Operations**: $0.03 per 10,000 transactions
- **Storage**: Negligible cost (first 10GB free)
- **Estimated Monthly Cost**: < $1/month for our use case

**Premium Tier** (not needed for this project):
- Adds hardware security module (HSM) protection
- ~$100/month + transaction fees

### Key Vault Naming Rules

**Key Vault Name Requirements:**
- **Globally unique** across all of Azure
- **3-24 characters** (letters, numbers, hyphens only)
- Must start with a letter
- Must end with a letter or number
- **No consecutive hyphens**

**Examples:**
- ✅ `kv-taskapp-2026`
- ✅ `taskapp-vault-vk`
- ✅ `kvtaskappvk88`
- ❌ `kv--taskapp` (consecutive hyphens)
- ❌ `kv-taskapp-` (ends with hyphen)
- ❌ `KV-TaskApp` (uppercase - will be auto-converted to lowercase)

---

## Architecture Overview

Here's what we'll build in Phase 5:

```
┌─────────────────────────────────────────────────────────────────┐
│  Resource Group: rg-taskapp-prod (Central US)                   │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │  Azure Key Vault                                           │ │
│  │  Name: kv-taskapp-[unique]                                 │ │
│  │  SKU: Standard                                             │ │
│  │  RBAC: Enabled                                             │ │
│  │                                                            │ │
│  │  🔐 Secrets:                                               │ │
│  │     ┌──────────────────────────────────────────┐          │ │
│  │     │ db-host                                  │          │ │
│  │     │   Value: taskapp-db-88.postgres...       │          │ │
│  │     └──────────────────────────────────────────┘          │ │
│  │     ┌──────────────────────────────────────────┐          │ │
│  │     │ db-name                                  │          │ │
│  │     │   Value: postgres                        │          │ │
│  │     └──────────────────────────────────────────┘          │ │
│  │     ┌──────────────────────────────────────────┐          │ │
│  │     │ db-user                                  │          │ │
│  │     │   Value: taskapp_admin                   │          │ │
│  │     └──────────────────────────────────────────┘          │ │
│  │     ┌──────────────────────────────────────────┐          │ │
│  │     │ db-password                              │          │ │
│  │     │   Value: [from temp file]                │          │ │
│  │     └──────────────────────────────────────────┘          │ │
│  │     ┌──────────────────────────────────────────┐          │ │
│  │     │ jwt-secret-key                           │          │ │
│  │     │   Value: [64-char random hex]            │          │ │
│  │     └──────────────────────────────────────────┘          │ │
│  │                                                            │ │
│  │  👤 Access (RBAC):                                         │ │
│  │     • You: Key Vault Secrets Officer (manage secrets)    │ │
│  │     • Container Apps: Key Vault Secrets User (read only) │ │
│  │                      (configured in Phase 6)              │ │
│  └────────────────────────────────────────────────────────────┘ │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## Prerequisites

### 1. Database Password Available

You should have the database password from Phase 3 stored in:
```
azure/config/db-credentials-temp.txt
```

**Verify it exists:**
```bash
cat azure/config/db-credentials-temp.txt
```

**Expected output:**
```
PostgreSQL Admin Credentials (TEMPORARY - DO NOT COMMIT)
==========================================================
Server: taskapp-db-88.postgres.database.azure.com
Admin User: taskapp_admin
Admin Password: [YOUR-SECURE-PASSWORD]

Created: [Date]

IMPORTANT: These credentials will be moved to Azure Key Vault in Phase 5.
After moving to Key Vault, delete this file.
```

If you don't have this file, retrieve the password:
```bash
# You'll need to reset the password if you lost it
az postgres flexible-server update \
  --resource-group rg-taskapp-prod \
  --name taskapp-db-88 \
  --admin-password "NewSecurePassword123!@#"
```

### 2. OpenSSL (for generating JWT secret)

**Verify OpenSSL is installed:**
```bash
openssl version
```

**Expected output:** `OpenSSL 1.x.x` or `OpenSSL 3.x.x`

**If not installed:**
- **Windows**: Included with Git Bash or install from https://slproweb.com/products/Win32OpenSSL.html
- **Mac**: Pre-installed
- **Linux**: `sudo apt-get install openssl`

---

## Step 1: Create Azure Key Vault

### What You're Creating

An Azure Key Vault with:
- **Standard tier** (sufficient for secrets management)
- **RBAC enabled** (modern permission model)
- **Same region as other resources** (Central US)
- **Soft-delete enabled** (can recover deleted secrets)
- **Purge protection disabled** (allows immediate deletion for learning)

### Choose a Unique Key Vault Name

Your Key Vault name must be **globally unique** across all of Azure.

**Suggestions:**
- `kv-taskapp-vk` (kv prefix + project + initials)
- `kv-taskapp-2026` (kv prefix + project + year)
- `taskapp-vault-88` (project + vault + random)

**Naming Convention:**
- `kv-` prefix indicates "Key Vault"
- Helps identify resource type at a glance

**Test if name is available:**
```bash
# Replace YOUR-VAULT-NAME with your chosen name
az keyvault list --query "[?name=='YOUR-VAULT-NAME']" --output table
```

**Expected output:**
- Empty table = Available ✅
- Table with data = Already taken, try another name ❌

### Option A: Console (Azure Portal) Method

**Step-by-step:**

1. **Navigate to Key Vaults**
   - Go to Azure Portal: https://portal.azure.com
   - Search for **"Key vaults"** in the top search bar
   - Click **"Key vaults"** service
   - Click **"+ Create"**

2. **Basics Tab - Project Details**
   - **Subscription**: Azure subscription 1 (your subscription)
   - **Resource group**: rg-taskapp-prod
   - **Key vault name**: YOUR-VAULT-NAME (e.g., kv-taskapp-vk)
   - **Region**: Central US
   - **Pricing tier**: Standard

3. **Access Configuration Tab**
   - **Permission model**: Select **"Azure role-based access control (RBAC)"**
   - Leave other settings as default

4. **Networking Tab**
   - **Connectivity method**: Public endpoint (all networks)
   - Note: We can restrict this later if needed

5. **Tags Tab** (Optional but recommended)
   - Add tags:
     - `Environment`: Production
     - `Project`: TaskApp
     - `ManagedBy`: Manual
     - `CostCenter`: Learning

6. **Review + Create**
   - Review your settings
   - Click **"Create"**

7. **Wait for Deployment**
   - Deployment takes 30-60 seconds ⏳
   - Click **"Go to resource"** when complete

8. **Assign Yourself Permissions**
   - In the left menu, click **"Access control (IAM)"**
   - Click **"+ Add"** → **"Add role assignment"**
   - **Role tab**: Search for and select **"Key Vault Secrets Officer"**
   - Click **"Next"**
   - **Members tab**: Click **"+ Select members"**
   - Search for your email address
   - Click **"Select"**
   - Click **"Review + assign"** (twice)

### Option B: CLI Method (Recommended)

**Step 1: Create the Key Vault**

```bash
# Replace YOUR-VAULT-NAME with your chosen unique name
# Example: kv-taskapp-vk, kv-taskapp-2026, etc.

az keyvault create \
  --name YOUR-VAULT-NAME \
  --resource-group rg-taskapp-prod \
  --location centralus \
  --sku standard \
  --enable-rbac-authorization true \
  --tags Environment=Production Project=TaskApp ManagedBy=Manual CostCenter=Learning
```

**This command will take 30-60 seconds** ⏳

**Expected output:**
```json
{
  "id": "/subscriptions/.../resourceGroups/rg-taskapp-prod/providers/Microsoft.KeyVault/vaults/YOUR-VAULT-NAME",
  "location": "centralus",
  "name": "YOUR-VAULT-NAME",
  "properties": {
    "accessPolicies": [],
    "enableRbacAuthorization": true,
    "enableSoftDelete": true,
    "provisioningState": "Succeeded",
    "sku": {
      "family": "A",
      "name": "standard"
    },
    "vaultUri": "https://YOUR-VAULT-NAME.vault.azure.net/"
  },
  "type": "Microsoft.KeyVault/vaults"
}
```

**Key fields to note:**
- **`vaultUri`**: This is your Key Vault URL (e.g., `https://kv-taskapp-vk.vault.azure.net/`)
- **`enableRbacAuthorization`**: true ✅ (using RBAC, not access policies)
- **`provisioningState`**: "Succeeded" ✅

**Step 2: Assign Yourself Permissions**

You need the "Key Vault Secrets Officer" role to create/manage secrets.

```bash
# Get your Azure AD user ID
USER_ID=$(az ad signed-in-user show --query id --output tsv)

# Get the Key Vault resource ID
VAULT_ID=$(az keyvault show \
  --name YOUR-VAULT-NAME \
  --resource-group rg-taskapp-prod \
  --query id \
  --output tsv)

# Assign Key Vault Secrets Officer role to yourself
az role assignment create \
  --role "Key Vault Secrets Officer" \
  --assignee $USER_ID \
  --scope $VAULT_ID
```

**Expected output:**
```json
{
  "principalId": "...",
  "principalType": "User",
  "roleDefinitionName": "Key Vault Secrets Officer",
  "scope": "/subscriptions/.../resourceGroups/rg-taskapp-prod/providers/Microsoft.KeyVault/vaults/YOUR-VAULT-NAME",
  "type": "Microsoft.Authorization/roleAssignments"
}
```

**⏰ Wait 2-3 minutes** for RBAC permissions to propagate before proceeding.

### Verify Key Vault Creation

```bash
# List all Key Vaults
az keyvault list --resource-group rg-taskapp-prod --output table

# Expected output:
# Location    Name               ResourceGroup
# ----------  -----------------  ---------------
# centralus   YOUR-VAULT-NAME    rg-taskapp-prod
```

**Get Key Vault URI:**
```bash
az keyvault show \
  --name YOUR-VAULT-NAME \
  --resource-group rg-taskapp-prod \
  --query properties.vaultUri \
  --output tsv

# Expected output: https://YOUR-VAULT-NAME.vault.azure.net/
```

### What Just Happened? 🤔

- **Key Vault Created**: Secure storage for secrets in Azure
- **RBAC Enabled**: Modern permission model using Azure roles
- **You Have Access**: Key Vault Secrets Officer role lets you manage secrets
- **Ready for Secrets**: Can now store database password and JWT key

---

## Step 2: Generate and Store Secrets

### What You're Storing

We need to store 5 secrets for our application:

| Secret Name | Purpose | Source |
|-------------|---------|--------|
| `db-host` | PostgreSQL server hostname | From Phase 3 |
| `db-name` | Database name | Will be "postgres" initially |
| `db-user` | Database admin username | From Phase 3 |
| `db-password` | Database admin password | From temp file |
| `jwt-secret-key` | JWT token signing key | Generate new |

### Set Variables for Easy Reference

First, let's set some variables to make commands easier:

```bash
# Your Key Vault name (replace with your actual name)
VAULT_NAME="YOUR-VAULT-NAME"

# Database details from Phase 3
DB_HOST="taskapp-db-88.postgres.database.azure.com"
DB_NAME="postgres"
DB_USER="taskapp_admin"
```

### Secret 1: Database Host

```bash
az keyvault secret set \
  --vault-name $VAULT_NAME \
  --name db-host \
  --value "$DB_HOST"
```

**Expected output:**
```json
{
  "attributes": {
    "created": "...",
    "enabled": true,
    "updated": "..."
  },
  "id": "https://YOUR-VAULT-NAME.vault.azure.net/secrets/db-host/...",
  "name": "db-host",
  "value": "taskapp-db-88.postgres.database.azure.com"
}
```

### Secret 2: Database Name

```bash
az keyvault secret set \
  --vault-name $VAULT_NAME \
  --name db-name \
  --value "$DB_NAME"
```

### Secret 3: Database User

```bash
az keyvault secret set \
  --vault-name $VAULT_NAME \
  --name db-user \
  --value "$DB_USER"
```

### Secret 4: Database Password

**Read password from temp file:**

```bash
# Extract password from temp file (adjust if your file format is different)
DB_PASSWORD=$(grep "Admin Password:" azure/config/db-credentials-temp.txt | cut -d':' -f2- | xargs)

# Verify it's not empty
if [ -z "$DB_PASSWORD" ]; then
  echo "❌ Error: Could not read password from file"
  echo "Please manually set DB_PASSWORD variable:"
  echo "  DB_PASSWORD='your-actual-password-here'"
else
  echo "✅ Password read successfully (length: ${#DB_PASSWORD} characters)"
fi
```

**Store password in Key Vault:**

```bash
az keyvault secret set \
  --vault-name $VAULT_NAME \
  --name db-password \
  --value "$DB_PASSWORD"
```

**Expected output:**
```json
{
  "attributes": {
    "created": "...",
    "enabled": true,
    "updated": "..."
  },
  "id": "https://YOUR-VAULT-NAME.vault.azure.net/secrets/db-password/...",
  "name": "db-password",
  "value": "[REDACTED]"
}
```

> 🔒 **Security Note**: The password value is automatically redacted in most outputs.

### Secret 5: JWT Secret Key

**Generate a secure random 256-bit (64 hex characters) key:**

```bash
# Generate random hex string
JWT_SECRET=$(openssl rand -hex 32)

# Verify it was generated
echo "Generated JWT secret (length: ${#JWT_SECRET} characters)"

# Store in Key Vault
az keyvault secret set \
  --vault-name $VAULT_NAME \
  --name jwt-secret-key \
  --value "$JWT_SECRET"
```

**What this generates:**
- 32 bytes = 256 bits of randomness
- Hex encoded = 64 characters (e.g., `a3f7b9c2e1d4...`)
- Cryptographically secure random data

### Verify All Secrets Were Created

```bash
# List all secrets
az keyvault secret list \
  --vault-name $VAULT_NAME \
  --query "[].{Name:name, Enabled:attributes.enabled}" \
  --output table
```

**Expected output:**
```
Name             Enabled
---------------  ---------
db-host          True
db-name          True
db-password      True
db-user          True
jwt-secret-key   True
```

You should see all 5 secrets listed! ✅

### What Just Happened? 🤔

- **5 Secrets Stored**: All application secrets now in Key Vault
- **Encrypted at Rest**: Azure encrypts secrets automatically
- **Versioned**: Each secret has a version (for rotation later)
- **Centralized**: Single source of truth for sensitive data
- **Ready for Apps**: Container Apps will reference these in Phase 6-7

---

## Step 3: Configure Access Policies

### What You're Doing

Configuring who/what can access your secrets. We've already granted yourself access (Key Vault Secrets Officer). In Phase 6, we'll grant the Container Apps' managed identities access.

### Verify Your Access

```bash
# List role assignments on the Key Vault
az role assignment list \
  --scope $(az keyvault show --name $VAULT_NAME --resource-group rg-taskapp-prod --query id --output tsv) \
  --query "[].{Principal:principalName, Role:roleDefinitionName}" \
  --output table
```

**Expected output:**
```
Principal                    Role
---------------------------  ----------------------------
vokeogigbah@yahoo.com        Key Vault Secrets Officer
```

You should see your email with the "Key Vault Secrets Officer" role. ✅

### Understanding RBAC Roles

Common Key Vault roles:

| Role | Permissions | Use Case |
|------|-------------|----------|
| **Key Vault Administrator** | Full access to vault and all contents | Vault owners, admins |
| **Key Vault Secrets Officer** | Create, read, update, delete secrets | Developers managing secrets |
| **Key Vault Secrets User** | Read secrets only | Applications (Container Apps) |
| **Key Vault Reader** | Read metadata only (not values) | Auditors |

### Access Control Best Practices

1. **Principle of Least Privilege**
   - Grant only the minimum permissions needed
   - Apps should have "Secrets User" (read-only), not "Officer"

2. **Use Managed Identities**
   - Never use passwords for app-to-vault authentication
   - Container Apps will use system-assigned managed identities (Phase 6)

3. **Audit Regularly**
   - Review who has access periodically
   - Use Azure Monitor to track secret access

4. **Separate Environments**
   - Different Key Vaults for dev/staging/prod
   - Prevents accidental production secret access from dev

---

## Step 4: Test Secret Retrieval

### What You're Doing

Testing that you can retrieve secrets successfully. This verifies:
- RBAC permissions are working
- Secrets are stored correctly
- Values are correct

### Method 1: Retrieve Individual Secrets

**Get database host:**
```bash
az keyvault secret show \
  --vault-name $VAULT_NAME \
  --name db-host \
  --query value \
  --output tsv
```

**Expected output:** `taskapp-db-88.postgres.database.azure.com`

**Get database name:**
```bash
az keyvault secret show \
  --vault-name $VAULT_NAME \
  --name db-name \
  --query value \
  --output tsv
```

**Expected output:** `postgres`

**Get database user:**
```bash
az keyvault secret show \
  --vault-name $VAULT_NAME \
  --name db-user \
  --query value \
  --output tsv
```

**Expected output:** `taskapp_admin`

**Get database password (careful - this shows the actual password):**
```bash
az keyvault secret show \
  --vault-name $VAULT_NAME \
  --name db-password \
  --query value \
  --output tsv
```

**Expected output:** `[Your actual database password]`

**Get JWT secret:**
```bash
az keyvault secret show \
  --vault-name $VAULT_NAME \
  --name jwt-secret-key \
  --query value \
  --output tsv
```

**Expected output:** `[64-character hex string]`

### Method 2: Test Full Database Connection String

**Build connection string from secrets:**

```bash
# Retrieve all components
DB_HOST_VAL=$(az keyvault secret show --vault-name $VAULT_NAME --name db-host --query value -o tsv)
DB_NAME_VAL=$(az keyvault secret show --vault-name $VAULT_NAME --name db-name --query value -o tsv)
DB_USER_VAL=$(az keyvault secret show --vault-name $VAULT_NAME --name db-user --query value -o tsv)
DB_PASS_VAL=$(az keyvault secret show --vault-name $VAULT_NAME --name db-password --query value -o tsv)

# Build PostgreSQL connection string
CONNECTION_STRING="postgresql://${DB_USER_VAL}:${DB_PASS_VAL}@${DB_HOST_VAL}/${DB_NAME_VAL}?sslmode=require"

# Display (be careful - shows password!)
echo "Connection String:"
echo "$CONNECTION_STRING"
```

**Expected format:**
```
postgresql://taskapp_admin:[PASSWORD]@taskapp-db-88.postgres.database.azure.com/postgres?sslmode=require
```

**Test the connection (optional):**

If you have `psql` installed:
```bash
psql "$CONNECTION_STRING" -c "SELECT version();"
```

**Expected output:** PostgreSQL version information ✅

### Method 3: Portal Verification

1. Go to Azure Portal: https://portal.azure.com
2. Navigate to your Key Vault
3. Click **"Secrets"** in the left menu
4. You should see all 5 secrets listed
5. Click on any secret to view metadata (not the value by default)
6. Click **"Show Secret Value"** to reveal the actual value

### Troubleshooting

**Error: "Forbidden" or "Access Denied"**
- **Cause**: RBAC permissions haven't propagated yet
- **Solution**: Wait 2-3 more minutes and try again
- **Verify Role**: Check role assignment (Step 3)

**Error: "Secret not found"**
- **Cause**: Secret name typo or wasn't created successfully
- **Solution**: List all secrets to verify: `az keyvault secret list --vault-name $VAULT_NAME --output table`

**Error: "Operation returned an invalid status code 'Conflict'"**
- **Cause**: Secret with same name already exists
- **Solution**: Update instead: Use same `az keyvault secret set` command (it will create new version)

---

## Step 5: Document Secret References

### What You're Creating

A reference document for your team (and future you) that lists:
- What secrets exist
- How to reference them
- How Container Apps will use them in Phase 6-7

### Create Secret Reference Documentation

```bash
cat > azure/config/keyvault-secrets-reference.md << 'EOF'
# Azure Key Vault - Secrets Reference

**Key Vault Name**: YOUR-VAULT-NAME
**Key Vault URI**: https://YOUR-VAULT-NAME.vault.azure.net/
**Location**: Central US
**RBAC**: Enabled
**Created**: January 29, 2026

---

## Stored Secrets

### Database Secrets

| Secret Name | Purpose | Sample Value (not actual) |
|-------------|---------|---------------------------|
| `db-host` | PostgreSQL server hostname | taskapp-db-88.postgres.database.azure.com |
| `db-name` | Database name | postgres |
| `db-user` | Database admin username | taskapp_admin |
| `db-password` | Database admin password | [REDACTED] |

### Application Secrets

| Secret Name | Purpose | Format |
|-------------|---------|--------|
| `jwt-secret-key` | JWT token signing key | 64-character hex string |

---

## Secret Versions

All secrets are currently on **version 1** (initial creation).

To view version history:
```bash
az keyvault secret list-versions \
  --vault-name YOUR-VAULT-NAME \
  --name SECRET-NAME \
  --output table
```

---

## Access Control (RBAC)

### Current Permissions

| Principal | Role | Scope |
|-----------|------|-------|
| vokeogigbah@yahoo.com | Key Vault Secrets Officer | Full vault |

### Future Permissions (Phase 6-7)

| Principal | Role | Scope | Purpose |
|-----------|------|-------|---------|
| ca-taskapp-backend (managed identity) | Key Vault Secrets User | Full vault | Backend app read secrets |
| ca-taskapp-frontend (managed identity) | Key Vault Secrets User | Full vault | Frontend app read secrets |

---

## How to Retrieve Secrets

### Via Azure CLI

**Single secret:**
```bash
az keyvault secret show \
  --vault-name YOUR-VAULT-NAME \
  --name db-password \
  --query value \
  --output tsv
```

**All secrets (names only):**
```bash
az keyvault secret list \
  --vault-name YOUR-VAULT-NAME \
  --query "[].name" \
  --output table
```

### Via Container Apps (Phase 6-7)

Container Apps will reference secrets using **Key Vault references**:

```yaml
secrets:
  - name: db-password
    keyVaultUrl: https://YOUR-VAULT-NAME.vault.azure.net/secrets/db-password
    identity: system
```

This tells Container Apps to:
1. Use its managed identity to authenticate to Key Vault
2. Retrieve the secret value at runtime
3. Inject as environment variable

### Via Code (Python - Backend)

**Using Azure SDK** (for local development):

```python
from azure.identity import DefaultAzureCredential
from azure.keyvault.secrets import SecretClient

# Authenticate (uses Azure CLI credentials locally)
credential = DefaultAzureCredential()
vault_url = "https://YOUR-VAULT-NAME.vault.azure.net/"
client = SecretClient(vault_url=vault_url, credential=credential)

# Retrieve secret
db_password = client.get_secret("db-password").value
```

**In Production**: Container Apps will use managed identity (no code changes needed).

---

## Secret Rotation

### When to Rotate

- **Immediately**: If a secret is compromised
- **Regularly**: Every 90 days (best practice)
- **Before expiry**: If secret has expiration date

### How to Rotate

```bash
# Create new version of secret
az keyvault secret set \
  --vault-name YOUR-VAULT-NAME \
  --name db-password \
  --value "NEW-PASSWORD-HERE"

# This creates a new version; old versions remain accessible
```

**Steps for Database Password Rotation:**
1. Update PostgreSQL password: `az postgres flexible-server update --admin-password`
2. Update Key Vault secret: `az keyvault secret set`
3. Restart Container Apps: They'll fetch the new version

---

## Monitoring & Auditing

### View Secret Access Logs

**Enable diagnostics** (optional - costs extra):
```bash
# Create Log Analytics workspace (if not exists)
az monitor log-analytics workspace create \
  --resource-group rg-taskapp-prod \
  --workspace-name law-taskapp-prod \
  --location centralus

# Enable diagnostics on Key Vault
az monitor diagnostic-settings create \
  --name KeyVaultDiagnostics \
  --resource $(az keyvault show --name YOUR-VAULT-NAME --query id -o tsv) \
  --logs '[{"category": "AuditEvent", "enabled": true}]' \
  --workspace $(az monitor log-analytics workspace show --resource-group rg-taskapp-prod --workspace-name law-taskapp-prod --query id -o tsv)
```

**Query logs** (after 15-30 minutes):
- Go to Key Vault in Azure Portal
- Click "Logs" in left menu
- Run query: `AzureDiagnostics | where ResourceType == "VAULTS"`

---

## Commands Reference

### Common Operations

**List all secrets:**
```bash
az keyvault secret list --vault-name YOUR-VAULT-NAME --output table
```

**Get secret value:**
```bash
az keyvault secret show --vault-name YOUR-VAULT-NAME --name SECRET-NAME --query value -o tsv
```

**Update secret:**
```bash
az keyvault secret set --vault-name YOUR-VAULT-NAME --name SECRET-NAME --value "NEW-VALUE"
```

**Delete secret** (soft delete - recoverable for 90 days):
```bash
az keyvault secret delete --vault-name YOUR-VAULT-NAME --name SECRET-NAME
```

**Purge secret** (permanent - not recoverable):
```bash
az keyvault secret purge --vault-name YOUR-VAULT-NAME --name SECRET-NAME
```

**Recover deleted secret:**
```bash
az keyvault secret recover --vault-name YOUR-VAULT-NAME --name SECRET-NAME
```

### Backup & Restore

**Backup secret:**
```bash
az keyvault secret backup \
  --vault-name YOUR-VAULT-NAME \
  --name SECRET-NAME \
  --file secret-backup.bin
```

**Restore secret:**
```bash
az keyvault secret restore \
  --vault-name YOUR-VAULT-NAME \
  --file secret-backup.bin
```

---

## Security Best Practices

1. ✅ **Never commit secrets to git**
   - `.gitignore` includes `azure/config/*.txt`
   - Use Key Vault for all production secrets

2. ✅ **Use managed identities in production**
   - No passwords in environment variables
   - Azure handles authentication

3. ✅ **Enable soft delete** (enabled by default)
   - Prevents accidental permanent deletion
   - 90-day recovery window

4. ✅ **Restrict network access** (optional for production)
   - Use private endpoints for VNet-only access
   - Add firewall rules to allow only specific IPs

5. ✅ **Enable audit logging** (optional - costs extra)
   - Track who accessed what secrets and when
   - Helps with compliance and security investigations

6. ✅ **Rotate secrets regularly**
   - Every 90 days minimum
   - Immediately if compromised

7. ✅ **Use separate Key Vaults per environment**
   - Dev, Staging, Production should have different vaults
   - Prevents accidental production access from dev

---

## Troubleshooting

### Issue: "Caller is not authorized to perform action"

**Symptoms:**
```
(Forbidden) The user, group or application 'appid=...' does not have secrets get permission...
```

**Cause:** Insufficient RBAC permissions

**Solution:**
```bash
# Check current role assignments
az role assignment list --scope $(az keyvault show --name YOUR-VAULT-NAME --query id -o tsv) --output table

# Grant yourself Secrets Officer role
az role assignment create \
  --role "Key Vault Secrets Officer" \
  --assignee $(az ad signed-in-user show --query id -o tsv) \
  --scope $(az keyvault show --name YOUR-VAULT-NAME --query id -o tsv)

# Wait 2-3 minutes for propagation
```

### Issue: RBAC permissions not working

**Cause:** Key Vault still using access policies, not RBAC

**Solution:**
```bash
# Check if RBAC is enabled
az keyvault show --name YOUR-VAULT-NAME --query properties.enableRbacAuthorization

# If false, enable RBAC
az keyvault update --name YOUR-VAULT-NAME --enable-rbac-authorization true
```

### Issue: Secret value is empty when retrieved

**Cause:** Secret wasn't set properly or is actually empty

**Solution:**
```bash
# Verify secret exists and has value
az keyvault secret show --vault-name YOUR-VAULT-NAME --name SECRET-NAME

# If value is null, set it again
az keyvault secret set --vault-name YOUR-VAULT-NAME --name SECRET-NAME --value "ACTUAL-VALUE"
```

---

## Next Steps

After completing Phase 5, you're ready for **Phase 6: Backend Deployment**.

In Phase 6, you'll:
- Create Container Apps Environment
- Deploy backend container from ACR
- Configure managed identity for Key Vault access
- Reference these secrets as environment variables

**Key Vault Integration in Phase 6:**
```bash
# Backend will use Key Vault references like this:
az containerapp create \
  --name ca-taskapp-backend \
  --secrets \
    db-password="keyvaultref:https://YOUR-VAULT-NAME.vault.azure.net/secrets/db-password,identityref:system"
```

Container Apps will automatically:
1. Authenticate using managed identity
2. Fetch secret from Key Vault
3. Inject as environment variable
4. Never expose the value in logs or Portal UI

---

## Cost Summary

**Phase 5 Estimated Monthly Cost:**
- Key Vault Standard: $0
- Secret operations (10,000 = $0.03): ~$0.03/month
- **Total: < $0.10/month**

Very affordable for the security benefits! 🎉

EOF

# Replace YOUR-VAULT-NAME placeholder with actual vault name
sed -i "s/YOUR-VAULT-NAME/$VAULT_NAME/g" azure/config/keyvault-secrets-reference.md

echo "✅ Secrets reference documentation created: azure/config/keyvault-secrets-reference.md"
```

### Create Quick Reference Card

```bash
cat > azure/config/keyvault-quick-reference.txt << EOF
Azure Key Vault Quick Reference
================================
Vault Name: $VAULT_NAME
Vault URI: https://${VAULT_NAME}.vault.azure.net/
Location: Central US

SECRETS (5 total)
-----------------
✓ db-host            PostgreSQL server hostname
✓ db-name            Database name (postgres)
✓ db-user            Database username (taskapp_admin)
✓ db-password        Database password
✓ jwt-secret-key     JWT signing key (64-char hex)

QUICK COMMANDS
--------------
# List secrets
az keyvault secret list --vault-name $VAULT_NAME --output table

# Get secret value
az keyvault secret show --vault-name $VAULT_NAME --name SECRET-NAME --query value -o tsv

# Update secret
az keyvault secret set --vault-name $VAULT_NAME --name SECRET-NAME --value "VALUE"

NEXT PHASE
----------
Phase 6: Backend Deployment
- Create Container Apps Environment
- Deploy backend with managed identity
- Configure Key Vault references
- Backend will auto-fetch secrets using managed identity

Created: $(date)
EOF

echo "✅ Quick reference created: azure/config/keyvault-quick-reference.txt"
```

### Optional: Delete Temporary Credentials File

Now that secrets are safely in Key Vault, you can delete the temporary file:

```bash
# IMPORTANT: Only run this AFTER verifying all secrets are in Key Vault!

# Verify secrets first
echo "Verifying all secrets are in Key Vault..."
SECRET_COUNT=$(az keyvault secret list --vault-name $VAULT_NAME --query "length(@)" --output tsv)

if [ "$SECRET_COUNT" -eq 5 ]; then
  echo "✅ All 5 secrets confirmed in Key Vault"
  echo ""
  echo "Safe to delete temporary credentials file?"
  echo "File: azure/config/db-credentials-temp.txt"
  echo ""
  read -p "Type 'yes' to delete: " confirm
  
  if [ "$confirm" = "yes" ]; then
    rm azure/config/db-credentials-temp.txt
    echo "✅ Temporary credentials file deleted"
    echo "🔒 All secrets now exclusively in Key Vault"
  else
    echo "Skipped deletion. You can delete manually later."
  fi
else
  echo "⚠️  Only $SECRET_COUNT secrets found (expected 5)"
  echo "Do NOT delete temp file yet. Verify secrets were created correctly."
fi
```

---

## Phase 5 Completion Checklist

Use this checklist to verify everything is complete:

### ✅ Key Vault Setup

- [ ] Azure Key Vault created
  - [ ] Name: kv-taskapp-[unique]
  - [ ] Location: Central US
  - [ ] SKU: Standard
  - [ ] RBAC: Enabled
- [ ] RBAC permissions configured
  - [ ] You have "Key Vault Secrets Officer" role
  - [ ] Permissions verified (can read/write secrets)

### ✅ Secrets Stored

- [ ] Database secrets created:
  - [ ] `db-host` (PostgreSQL hostname)
  - [ ] `db-name` (database name: postgres)
  - [ ] `db-user` (admin username)
  - [ ] `db-password` (admin password from temp file)
- [ ] Application secrets created:
  - [ ] `jwt-secret-key` (64-char random hex)

### ✅ Testing & Verification

- [ ] Retrieved each secret via CLI (values correct)
- [ ] Built PostgreSQL connection string from secrets
- [ ] (Optional) Tested database connection with connection string
- [ ] Verified all 5 secrets listed in portal

### ✅ Documentation

- [ ] Created `keyvault-secrets-reference.md`
- [ ] Created `keyvault-quick-reference.txt`
- [ ] Documented vault name and URI
- [ ] Listed all secret names and purposes

### ✅ Security & Cleanup

- [ ] Verified RBAC role assignments
- [ ] (Optional) Deleted temporary credentials file
- [ ] Confirmed no secrets in git repository
- [ ] Documented how Container Apps will access secrets in Phase 6

---

## Verification Commands

Run these commands to verify Phase 5 completion:

```bash
# Verify Key Vault exists
az keyvault show --name $VAULT_NAME --query "{Name:name, Location:location, RBAC:properties.enableRbacAuthorization}" --output table

# Verify all 5 secrets exist
az keyvault secret list --vault-name $VAULT_NAME --query "[].{Name:name, Enabled:attributes.enabled}" --output table

# Verify RBAC permissions
az role assignment list \
  --scope $(az keyvault show --name $VAULT_NAME --query id -o tsv) \
  --query "[].{Principal:principalName, Role:roleDefinitionName}" \
  --output table

# Test secret retrieval (database host)
az keyvault secret show --vault-name $VAULT_NAME --name db-host --query value -o tsv

# Verify documentation files exist
ls -lh azure/config/keyvault-*.{md,txt}
```

**Expected results:**
- ✅ Key Vault shows RBAC: true
- ✅ 5 secrets listed, all enabled
- ✅ Your email has "Key Vault Secrets Officer" role
- ✅ Secret retrieval returns correct value
- ✅ Documentation files exist

---

## What You Learned

Congratulations! 🎉 You've completed Phase 5. Here's what you learned:

### Key Concepts
- ✅ **Azure Key Vault fundamentals** - Secure secrets management
- ✅ **RBAC vs Access Policies** - Modern vs traditional permissions
- ✅ **Secret management** - Creating, updating, retrieving secrets
- ✅ **Managed identities** - How Container Apps will access secrets (Phase 6)

### Azure Skills
- ✅ Creating and configuring Key Vault
- ✅ Assigning RBAC roles
- ✅ Managing secrets via CLI
- ✅ Generating cryptographic keys
- ✅ Testing secret retrieval

### Security Best Practices
- ✅ Never hardcode secrets
- ✅ Use managed identities for authentication
- ✅ Centralize secrets in Key Vault
- ✅ Enable audit logging (optional)
- ✅ Rotate secrets regularly

### Comparison with AWS
| Task | Azure | AWS |
|------|-------|-----|
| Secrets storage | Key Vault | Secrets Manager |
| Permission model | RBAC | IAM policies |
| App authentication | Managed Identity | IAM Roles |
| Cost | ~$0.03/10k ops | ~$0.40/secret/month |

---

## Next: Phase 6 - Backend Deployment

You're now ready to deploy the backend Container App!

**Phase 6 Preview:**
- Create Container Apps Environment
- Deploy backend container from ACR (taskappacr2026.azurecr.io/taskapp-backend)
- Configure system-assigned managed identity
- Grant managed identity access to Key Vault
- Reference secrets via Key Vault URLs
- Configure environment variables
- Enable logging and monitoring
- Test backend API endpoints

**First command in Phase 6:**
```bash
# Create Container Apps Environment
az containerapp env create \
  --name env-taskapp-prod \
  --resource-group rg-taskapp-prod \
  --location centralus
```

**Estimated time for Phase 6:** 2-3 hours

---

## Troubleshooting Guide

### Common Issues

#### 1. "The user does not have secrets get permission"

**Error:**
```
(Forbidden) The user, group or application does not have secrets get permission on key vault...
```

**Solution:**
```bash
# Wait 2-3 minutes after role assignment
# Or re-assign the role:
az role assignment create \
  --role "Key Vault Secrets Officer" \
  --assignee $(az ad signed-in-user show --query id -o tsv) \
  --scope $(az keyvault show --name $VAULT_NAME --query id -o tsv)
```

#### 2. Key Vault name already taken

**Error:**
```
(ConflictError) The name 'kv-taskapp-vk' is already in use.
```

**Solution:**
```bash
# Choose a different name
VAULT_NAME="kv-taskapp-vk88"  # Add numbers or initials

# Verify availability
az keyvault list --query "[?name=='$VAULT_NAME']" --output table
# Should return empty
```

#### 3. OpenSSL not found (Windows)

**Error:**
```
'openssl' is not recognized as an internal or external command
```

**Solution:**
```bash
# Use Git Bash (includes OpenSSL)
# Or download from: https://slproweb.com/products/Win32OpenSSL.html

# Alternative: Generate in Azure Cloud Shell
az cloud-shell start
openssl rand -hex 32
```

#### 4. Can't read password from temp file

**Error:**
```
Error: Could not read password from file
```

**Solution:**
```bash
# Manually set the password
echo "Enter your database password:"
read -s DB_PASSWORD

# Or retrieve from Azure (if you remember the password)
# Reset if needed:
az postgres flexible-server update \
  --resource-group rg-taskapp-prod \
  --name taskapp-db-88 \
  --admin-password "NewPassword123!@#"

DB_PASSWORD="NewPassword123!@#"
```

---

## Additional Resources

### Microsoft Learn Modules
- [Manage secrets in Azure Key Vault](https://learn.microsoft.com/en-us/training/modules/manage-secrets-with-azure-key-vault/)
- [Configure and manage secrets in Azure Key Vault](https://learn.microsoft.com/en-us/training/modules/configure-and-manage-azure-key-vault/)
- [Authenticate apps to Azure services using service principals and managed identities](https://learn.microsoft.com/en-us/training/modules/authenticate-apps-with-managed-identities/)

### Official Documentation
- [Azure Key Vault Documentation](https://learn.microsoft.com/en-us/azure/key-vault/)
- [Key Vault RBAC Guide](https://learn.microsoft.com/en-us/azure/key-vault/general/rbac-guide)
- [Key Vault Best Practices](https://learn.microsoft.com/en-us/azure/key-vault/general/best-practices)
- [Managed Identities Overview](https://learn.microsoft.com/en-us/azure/active-directory/managed-identities-azure-resources/overview)

### Azure CLI Reference
- [az keyvault](https://learn.microsoft.com/en-us/cli/azure/keyvault)
- [az keyvault secret](https://learn.microsoft.com/en-us/cli/azure/keyvault/secret)
- [az role assignment](https://learn.microsoft.com/en-us/cli/azure/role/assignment)

---

**Phase 5 Complete!** 🎉

You now have:
- ✅ Secure secrets storage in Azure Key Vault
- ✅ All database and application secrets stored
- ✅ RBAC permissions configured
- ✅ Documentation for future reference
- ✅ Ready to deploy Container Apps with managed identity access

**Next:** [AZURE_PHASE_6_GUIDE.md](AZURE_PHASE_6_GUIDE.md) - Backend Deployment

---

*Last Updated: January 29, 2026*
*Guide Version: 1.0*
*Author: vee-kay8*
