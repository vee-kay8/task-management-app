# Azure Phase 3: Database Layer - Complete Guide

**Duration**: 2-3 hours  
**Difficulty**: Intermediate  
**Prerequisites**: Phase 1 & 2 complete (Account setup, VNet configured)  
**Goal**: Create a secure, managed PostgreSQL database with private network access

---

## 📋 Overview

This phase sets up your production database using Azure Database for PostgreSQL Flexible Server. By the end, you'll have:

✅ PostgreSQL Flexible Server created (private access via VNet)  
✅ Secure credentials generated and stored  
✅ Network security configured (private access only)  
✅ Backup and recovery configured  
✅ Server ready for backend app to initialize schema (Phase 6)

> **Note**: Database schema initialization (tables, indexes, etc.) will be handled automatically by the backend application in Phase 6 using Flask-Migrate/Alembic migrations. This is the recommended production approach and eliminates the need for manual database setup.  

---

## Table of Contents

1. [Understanding Azure Database for PostgreSQL](#understanding-azure-database-for-postgresql)
2. [Generate Secure Credentials](#step-1-generate-secure-credentials)
3. [Create PostgreSQL Flexible Server](#step-2-create-postgresql-flexible-server)
4. [Why We Skip Manual Schema Initialization](#why-we-skip-manual-schema-initialization)
5. [Phase 3 Completion Checklist](#phase-3-completion-checklist)

**Note**: Steps 3-7 from the original guide (firewall configuration, manual database connection, and schema initialization) are not needed when using VNet-integrated private access with application-managed migrations.

---

## Understanding Azure Database for PostgreSQL

### What is Azure Database for PostgreSQL? 🗄️

**Azure Database for PostgreSQL** is a fully managed database service based on PostgreSQL. Azure handles backups, patching, and high availability.

**AWS Equivalent:** RDS for PostgreSQL

**Deployment Options:**
1. **Single Server** (Legacy) - Being retired
2. **Flexible Server** (Recommended) - More control, better features, lower cost
3. **Hyperscale (Citus)** - Distributed PostgreSQL for massive scale

> 💡 **We're using Flexible Server** - it's the modern, cost-effective option.

### Single Server vs Flexible Server

| Feature | Single Server | Flexible Server |
|---------|---------------|-----------------|
| **Status** | Legacy (retiring 2025) | ✅ Current |
| **SKU Options** | Basic, General Purpose, Memory Optimized | Burstable, General Purpose, Memory Optimized |
| **VNet Integration** | Limited | ✅ Full support |
| **Zone Redundancy** | No | ✅ Yes |
| **Cost** | Higher | Lower |
| **Start/Stop** | No | ✅ Yes (save money!) |
| **Custom Maintenance Window** | No | ✅ Yes |

### Flexible Server SKU Tiers

| Tier | Use Case | CPU | RAM | Storage | Cost (Est.) |
|------|----------|-----|-----|---------|-------------|
| **Burstable** | Dev/Test, low traffic | 1-2 vCores | 0.5-4 GB | 32 GB - 16 TB | $15-40/month |
| **General Purpose** | Production workloads | 2-64 vCores | 4-256 GB | 32 GB - 16 TB | $100-2000/month |
| **Memory Optimized** | Memory-intensive apps | 2-64 vCores | 8-512 GB | 32 GB - 16 TB | $200-4000/month |

> 💡 **For Learning**: We'll use **Burstable B1ms** (1 vCore, 2 GB RAM) - **FREE for 12 months!**

### Network Security Options

**Two access modes:**

1. **Public Access** (Not recommended for production)
   - Database accessible from internet
   - Requires firewall rules
   - Less secure
   - Easier for testing

2. **Private Access** (Recommended) ✅
   - Database only accessible within VNet
   - No public IP address
   - Uses VNet integration
   - More secure
   - **We're using this!**

### What is VNet Integration? 🔒

**VNet Integration** means your database server is placed inside your Virtual Network, specifically in the `subnet-database` we created in Phase 2.

**Benefits:**
- ✅ **No public internet access** - Database can't be reached from outside Azure
- ✅ **Private IP only** - Database gets an IP in your subnet (10.0.2.x)
- ✅ **Network isolation** - Only resources in VNet can connect
- ✅ **NSG protection** - Network Security Group rules enforce access

**How it works:**
```
Internet ❌ → Database (blocked)
Container Apps ✅ → Database (allowed via subnet rules)
Your PC ❌ → Database (blocked, except temporary firewall rule)
```

---

## Architecture Overview

Here's what we'll build in Phase 3:

```
┌─────────────────────────────────────────────────────────────────┐
│  Resource Group: rg-taskapp-prod                                │
│  Region: East US                                                │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌───────────────────────────────────────────────────────────┐ │
│  │  Virtual Network: vnet-taskapp (10.0.0.0/16)              │ │
│  │                                                           │ │
│  │  ┌─────────────────────────┐  ┌─────────────────────────┐│ │
│  │  │ Subnet: Container Apps  │  │ Subnet: Database        ││ │
│  │  │ 10.0.1.0/24             │  │ 10.0.2.0/24             ││ │
│  │  │                         │  │                         ││ │
│  │  │ (Phase 6-7:             │  │ ┌─────────────────────┐││ │
│  │  │  Backend + Frontend)    │◄─┤ │ PostgreSQL Server   │││ │
│  │  │                         │  │ │ taskapp-db-xxxxx    │││ │
│  │  │                         │  │ │ Port: 5432          │││ │
│  │  │                         │  │ │ Private IP: 10.0.2.x│││ │
│  │  │                         │  │ │                     │││ │
│  │  │                         │  │ │ Database:           │││ │
│  │  │                         │  │ │ taskmanagement_db   │││ │
│  │  │                         │  │ └─────────────────────┘││ │
│  │  │                         │  │                         ││ │
│  │  └─────────────────────────┘  └─────────────────────────┘│ │
│  │                                                           │ │
│  └───────────────────────────────────────────────────────────┘ │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### Database Schema

We'll create these tables:

**1. users**
- `id` - UUID primary key
- `email` - Unique email address
- `password_hash` - Hashed password
- `name` - User's full name
- `created_at`, `updated_at` - Timestamps

**2. projects**
- `id` - UUID primary key
- `name` - Project name
- `description` - Project details
- `owner_id` - Foreign key to users
- `created_at`, `updated_at` - Timestamps

**3. tasks**
- `id` - UUID primary key
- `title` - Task title
- `description` - Task details
- `status` - ENUM (todo, in_progress, done)
- `priority` - ENUM (low, medium, high)
- `project_id` - Foreign key to projects
- `assigned_to` - Foreign key to users
- `due_date` - Optional deadline
- `created_at`, `updated_at` - Timestamps

---

## Step 1: Generate Secure Credentials

### What You're Doing

Creating a strong, random password for the PostgreSQL admin user. This password will be used to create the server and for initial database setup.

> ⚠️ **IMPORTANT**: In Phase 5, we'll move this to Azure Key Vault. For now, we'll store it temporarily.

### Option A: Using OpenSSL (Git Bash/Linux/Mac)

```bash
# Generate a 32-character random password
openssl rand -base64 32
```

**Example output:**
```
Kj9mN2pL4xR8vQ3wT6yU1zA5sD7fG9hJ2kL4mN6pQ8==
```

### Option B: Using PowerShell (Windows)

```powershell
# Generate a strong random password
Add-Type -AssemblyName 'System.Web'
[System.Web.Security.Membership]::GeneratePassword(32, 8)
```

**Example output:**
```
K9m!N2pL@4xR#8vQ$3wT%6yU&1zA*5sD
```

### Option C: Manual Generation

Use a password manager (1Password, LastPass, Bitwarden) to generate:
- **Length**: 32 characters
- **Include**: Uppercase, lowercase, numbers, symbols
- **Avoid**: Quotes (`'` or `"`), backslash (`\`), spaces

### Save Your Password

**Create a temporary credentials file:**

```bash
# Create secure credentials file (local only, not in git)
cat > azure/config/db-credentials-temp.txt << EOF
PostgreSQL Admin Credentials
=============================
Server: taskapp-db-<YOUR-UNIQUE-SUFFIX>
Admin User: taskapp_admin
Admin Password: <YOUR-GENERATED-PASSWORD>
Database: taskmanagement_db

⚠️ DELETE THIS FILE after moving to Key Vault in Phase 5!
⚠️ This file is in .gitignore - never commit it!

Created: $(date)
EOF

echo "✅ Credentials saved to azure/config/db-credentials-temp.txt"
```

**Verify it's ignored by git:**

```bash
# Check .gitignore
grep -E "credentials|secrets|\.txt" .gitignore

# Make sure credentials file is ignored
git status --ignored | grep credentials
```

> 💡 **Security Note**: This file should show as "ignored" in git. Never commit credentials!

### What Just Happened? 🤔

- **Strong Password**: 32+ random characters
- **Temporary Storage**: Saved locally (not in git)
- **Next Step**: We'll use this password to create the server
- **Future**: Move to Azure Key Vault (Phase 5)

---

## Step 2: Create PostgreSQL Flexible Server

### What You're Creating

A PostgreSQL 15 Flexible Server with:
- **Private network access** (VNet integrated)
- **Burstable B1ms** tier (1 vCore, 2 GB RAM - FREE for 12 months!)
- **32 GB storage** (minimum)
- **7-day backup retention**

### Important: Choose a Unique Server Name

Your server name must be **globally unique** across all of Azure.

**Format**: `taskapp-db-<unique-suffix>`

**Suggestions for unique suffix:**
- Your initials + random numbers: `taskapp-db-jd2401`
- Random word: `taskapp-db-falcon`
- Date + initials: `taskapp-db-20260126jd`

> 💡 **Tip**: Keep it short (max 63 characters total), lowercase letters, numbers, and hyphens only.

**Test if name is available:**
```bash
az postgres flexible-server show --name taskapp-db-YOUR-SUFFIX --resource-group rg-taskapp-prod 2>&1 | grep "not be found"
```
If you see "could not be found", the name is available! ✅

### Option A: Console (Azure Portal) Method

**Step-by-step:**

1. **Navigate to Azure Database for PostgreSQL**
   - Go to Azure Portal: https://portal.azure.com
   - Search for "Azure Database for PostgreSQL servers" in the top search bar
   - Click **"+ Create"**

2. **Select Deployment Option**
   - Select **"Flexible server"** (Recommended)
   - Click **"Create"**

3. **Basics Tab - Project Details**
   - **Subscription**: Select your subscription (Azure subscription 1)
   - **Resource group**: Select `rg-taskapp-prod`
   - **Server name**: `taskapp-db-YOUR-SUFFIX` (must be globally unique)
   - **Region**: East US (should match your resource group)
   - **PostgreSQL version**: 15 (latest stable)
   - **Workload type**: Development (automatically selects Burstable tier)

4. **Basics Tab - Authentication**
   - **Authentication method**: PostgreSQL authentication only
   - **Admin username**: `taskapp_admin`
   - **Password**: Enter the strong password from Step 1
   - **Confirm password**: Re-enter the password

5. **Basics Tab - Compute + Storage**
   - Click **"Configure server"**
   - **Compute tier**: Burstable
   - **Compute size**: Standard_B1ms (1 vCore, 2 GB RAM)
   - **Storage size**: 32 GiB (minimum)
   - **Storage Auto-growth**: Enabled
   - Click **"Save"**

6. **Networking Tab**
   - **Connectivity method**: Private access (VNet Integration) ✅
   - **Virtual network**: Select `vnet-taskapp`
   - **Subnet**: Select `subnet-database`
   - **Private DNS integration**: Yes (should auto-create)
   - Note: Azure will create a private DNS zone automatically

7. **Security Tab**
   - **Public access**: Disabled (should be grayed out due to VNet integration) ✅
   - Leave other settings as default

8. **Tags Tab**
   - Tags are inherited from resource group
   - Click **"Next: Review + create"**

9. **Review + Create**
   - Verify all settings:
     - Server name is unique
     - Burstable B1ms tier
     - VNet integration enabled
     - Private access only
   - Click **"Create"**

10. **Wait for Deployment**
    - Deployment will take 5-10 minutes ⏳
    - You'll see: "Your deployment is in progress"
    - When complete: "Your deployment is complete"
    - Click **"Go to resource"**

11. **Save Server Details**
    - On the Overview page, note:
      - **Server name**: taskapp-db-YOUR-SUFFIX.postgres.database.azure.com
      - **Status**: Available
      - **Location**: East US
      - **Version**: 15
    - Save the server name to your credentials file

### Option B: CLI Method (Recommended) - Interactive

This method will prompt you for the password interactively (more secure).

```bash
# Create PostgreSQL Flexible Server (interactive password)
az postgres flexible-server create \
  --resource-group rg-taskapp-prod \
  --name taskapp-db-YOUR-SUFFIX \
  --location eastus \
  --admin-user taskapp_admin \
  --tier Burstable \
  --sku-name Standard_B1ms \
  --storage-size 32 \
  --version 15 \
  --vnet vnet-taskapp \
  --subnet subnet-database \
  --yes
```

**When prompted**: Enter the password you generated in Step 1.

**This command will take 5-10 minutes** ⏳ (Azure is creating the server, configuring networking, etc.)

### Option C: CLI Method - Password in Command (Less Secure)

If you prefer to include the password in the command:

```bash
# Replace <YOUR-PASSWORD> with your generated password
az postgres flexible-server create \
  --resource-group rg-taskapp-prod \
  --name taskapp-db-YOUR-SUFFIX \
  --location eastus \
  --admin-user taskapp_admin \
  --admin-password '<YOUR-PASSWORD>' \
  --tier Burstable \
  --sku-name Standard_B1ms \
  --storage-size 32 \
  --version 15 \
  --vnet vnet-taskapp \
  --subnet subnet-database \
  --yes
```

> ⚠️ **Warning**: Password will be visible in terminal history. Use interactive method if concerned.

### Expected Output

```json
{
  "administratorLogin": "taskapp_admin",
  "availabilityZone": "1",
  "backup": {
    "backupRetentionDays": 7,
    "earliestRestoreDate": "2026-01-26T19:30:00+00:00",
    "geoRedundantBackup": "Disabled"
  },
  "fullyQualifiedDomainName": "taskapp-db-YOUR-SUFFIX.postgres.database.azure.com",
  "highAvailability": {
    "mode": "Disabled"
  },
  "id": "/subscriptions/84cbece2-bed5-48a8-9386-d5e8c71a64e8/resourceGroups/rg-taskapp-prod/providers/Microsoft.DBforPostgreSQL/flexibleServers/taskapp-db-YOUR-SUFFIX",
  "location": "East US",
  "name": "taskapp-db-YOUR-SUFFIX",
  "network": {
    "delegatedSubnetResourceId": "/subscriptions/.../subnets/subnet-database",
    "privateDnsZoneArmResourceId": "/subscriptions/.../privateDnsZones/...",
    "publicNetworkAccess": "Disabled"
  },
  "resourceGroup": "rg-taskapp-prod",
  "sku": {
    "name": "Standard_B1ms",
    "tier": "Burstable"
  },
  "state": "Ready",
  "storage": {
    "storageSizeGB": 32
  },
  "version": "15"
}
```

### Understanding the Output

**Key fields to note:**
- **`fullyQualifiedDomainName`**: Your server's hostname (save this!)
- **`network.publicNetworkAccess`**: "Disabled" = good! (private access only)
- **`state`**: "Ready" = server is running
- **`backup.backupRetentionDays`**: 7 = automatic backups for 7 days
- **`sku.name`**: "Standard_B1ms" = your server tier

### Verify Server Creation

```bash
# List all PostgreSQL servers
az postgres flexible-server list --resource-group rg-taskapp-prod --output table

# Show specific server details
az postgres flexible-server show \
  --resource-group rg-taskapp-prod \
  --name taskapp-db-YOUR-SUFFIX \
  --output table
```

**Expected output:**
```
Name                      Location    ResourceGroup    State    Version
------------------------  ----------  ---------------  -------  ---------
taskapp-db-YOUR-SUFFIX    eastus      rg-taskapp-prod  Ready    15
```

### What Just Happened? 🤔

- **PostgreSQL 15 Server Created**: Latest stable version
- **Private Network**: Server placed in subnet-database (10.0.2.x)
- **No Public Access**: Server can't be reached from internet
- **Private DNS Zone**: Azure created a DNS zone for VNet name resolution
- **7-Day Backups**: Automatic daily backups enabled
- **Burstable Tier**: Cost-effective for learning (FREE for 12 months!)

### Save Server Details

```bash
# Save server FQDN to variable
export DB_HOST=$(az postgres flexible-server show \
  --resource-group rg-taskapp-prod \
  --name taskapp-db-YOUR-SUFFIX \
  --query fullyQualifiedDomainName \
  --output tsv)

echo "Database Host: $DB_HOST"

# Append to credentials file
cat >> azure/config/db-credentials-temp.txt << EOF

Connection Details
==================
Host: $DB_HOST
Port: 5432
Database: taskmanagement_db
Username: taskapp_admin
SSL Mode: require

Connection String:
postgresql://taskapp_admin:<password>@$DB_HOST:5432/taskmanagement_db?sslmode=require
EOF

echo "✅ Connection details saved"
```

---

## Why We Skip Manual Schema Initialization

### The VNet Private Access Challenge

Your PostgreSQL server was created with **private VNet access only** - a security best practice. This means:
- ❌ No public internet access to the database
- ❌ Can't connect from your local PC without complex networking setup
- ❌ Azure Cloud Shell can't reach VNet-integrated resources
- ✅ Only resources within the VNet can connect (like Container Apps)

### The Better Approach: Application-Managed Migrations

Your backend application already has database migration tools configured:
- **Flask-Migrate**: Database migration framework
- **Alembic**: Schema versioning and migration engine
- **Migrations folder**: Contains schema definitions in `backend/migrations/`

**How it works:**
1. Backend container starts in Phase 6 (within the VNet)
2. Backend connects to database using private DNS
3. Flask-Migrate detects no tables exist
4. Migrations run automatically, creating all tables
5. Database schema is initialized with proper indexes, constraints, triggers

### Why This Is Better

| Manual Setup (Option A/B) | App Migrations (Option C) |
|---------------------------|---------------------------|
| Requires public access or complex networking | Works with private VNet access ✅ |
| Manual SQL scripts to maintain | Version-controlled migrations ✅ |
| One-time setup | Repeatable and automated ✅ |
| Security risk (temporary firewall rules) | Secure (stays private) ✅ |
| Requires psql client installation | No extra tools needed ✅ |
| Schema drift between environments | Consistent across all environments ✅ |

### What About the Schema?

Your backend's migration files already define the complete schema:
- **users table**: id, email, password_hash, name, timestamps
- **projects table**: id, name, description, owner_id, timestamps
- **tasks table**: id, title, description, status, priority, project_id, assigned_to, due_date, timestamps
- **Indexes**: Email lookups, foreign key relationships, status queries
- **Constraints**: Foreign keys, unique constraints, check constraints
- **Triggers**: Automatic updated_at timestamp updates

When you deploy the backend in Phase 6, all of this will be created automatically.

### If You Need to Verify Later

Once the backend is deployed (Phase 6), you can verify the schema:
```bash
# From within the backend Container App (Phase 6)
az containerapp exec \
  --name ca-taskapp-backend \
  --resource-group rg-taskapp-prod \
  --command "flask db current"

# Or check migration status
az containerapp logs show \
  --name ca-taskapp-backend \
  --resource-group rg-taskapp-prod \
  --follow
```

**Phase 3 is complete!** Your database server is ready and waiting for the backend app to initialize it properly.

---

## Phase 3 Completion Checklist

### What You've Accomplished

- [x] **Step 1: Secure Credentials Generated**
  - Strong 32-character password created
  - Stored in `azure/config/db-credentials-temp.txt`
  - File ignored by git (.gitignore)
  - Will move to Azure Key Vault in Phase 5

- [x] **Step 2: PostgreSQL Server Created**
  - Server: taskapp-db-88.postgres.database.azure.com
  - Version: PostgreSQL 15
  - Tier: Burstable B1ms (FREE for 12 months)
  - Region: Central US
  - Storage: 32 GB with 7-day backup retention
  - Network: Private VNet access only (subnet-database)
  - Private DNS Zone: taskapp-db-88.private.postgres.database.azure.com
  - State: Ready and running

- [x] **Security Configured**
  - No public internet access ✅
  - VNet integration enabled ✅
  - SSL/TLS required for connections ✅
  - NSG rules protect database subnet ✅
  - Only Container Apps can connect ✅

- [x] **Documentation Updated**
  - Connection details saved
  - Credentials stored securely (temporarily)
  - Architecture documented
  - Cost: $0/month (free tier)

### What's Deferred to Phase 6

- [ ] Database schema creation (backend app will handle)
- [ ] Table creation (users, projects, tasks)
- [ ] Index creation
- [ ] Constraint setup
- [ ] Initial data seeding (if any)

**Why deferred?** Backend app has Flask-Migrate/Alembic migrations that will automatically create the schema when the app first connects in Phase 6. This is more secure (no public access needed) and follows production best practices.

### Verification Commands

```bash
# Verify PostgreSQL server exists and is running
az postgres flexible-server show \
  --resource-group rg-taskapp-prod \
  --name taskapp-db-88 \
  --query "{name:name, state:state, version:version, location:location}" \
  --output table

# Expected output:
# Name            State    Version    Location
# --------------  -------  ---------  ----------
# taskapp-db-88   Ready    15         Central US

# Verify private network configuration
az postgres flexible-server show \
  --resource-group rg-taskapp-prod \
  --name taskapp-db-88 \
  --query "network.{publicAccess:publicNetworkAccess, subnet:delegatedSubnetResourceId}" \
  --output json

# Expected output:
# {
#   "publicAccess": "Disabled",  ✅
#   "subnet": "/subscriptions/.../subnet-database"  ✅
# }

# Verify backup configuration
az postgres flexible-server show \
  --resource-group rg-taskapp-prod \
  --name taskapp-db-88 \
  --query "backup.{retentionDays:backupRetentionDays, geoRedundant:geoRedundantBackup}" \
  --output table

# Expected output:
# RetentionDays    GeoRedundant
# ---------------  --------------
# 7                Disabled
```

### Cost Summary for Phase 3

- **PostgreSQL Flexible Server (B1ms)**: $0/month (FREE for 12 months)
- **Storage (32 GB)**: Included in free tier
- **Backup Storage**: Included in free tier
- **Network Egress**: $0 (private VNet traffic is free)

**Total Phase 3 Cost**: $0/month ✅

### Connection String (for Phase 6)

When configuring the backend Container App in Phase 6, you'll use:

```bash
# Format:
postgresql://taskapp_admin:<password>@taskapp-db-88.postgres.database.azure.com:5432/postgres?sslmode=require

# The backend will:
# 1. Connect using this connection string
# 2. Create the database: taskmanagement_db
# 3. Run migrations to create all tables
# 4. Application will be ready to use
```

**Password**: Stored in `azure/config/db-credentials-temp.txt` (will move to Key Vault in Phase 5)

---

## Next Steps: Phase 4 - Azure Container Registry

With the database server ready, you're prepared to:
1. Create Azure Container Registry (ACR)
2. Build Docker images for backend + frontend
3. Push images to ACR
4. Set up authentication for Container Apps to pull images

**Estimated Time**: 1-2 hours  
**Cost**: Basic tier ($5/month) or free alternatives

Ready to proceed? Let's move to Phase 4!

---

## Original Steps 3-7 (For Reference Only)

The following steps are **not required** when using VNet-integrated private access with application-managed migrations. They're preserved here for reference in case you need to manually access the database in the future or choose a different deployment approach.

<details>
<summary>Click to expand: Manual initialization steps (not needed for this deployment)</summary>

---

## Step 3: Configure Firewall for Initial Setup

### Why Do We Need This?

Your database is now **private** (VNet-only access). To connect from your PC and initialize the schema, we need to temporarily allow your IP address.

> 💡 **Temporary Rule**: We'll remove this after setup is complete (Step 7).

### Get Your Public IP Address

```bash
# Get your public IP (automatic)
MY_IP=$(curl -s ifconfig.me)
echo "Your public IP: $MY_IP"
```

Or visit https://whatismyipaddress.com/ to see your IP.

### Option A: Console (Azure Portal) Method

**Step-by-step:**

1. **Navigate to Your PostgreSQL Server**
   - Go to Azure Portal: https://portal.azure.com
   - Navigate to **Resource groups** → **rg-taskapp-prod**
   - Click on **taskapp-db-YOUR-SUFFIX**

2. **Open Networking Settings**
   - In the left menu, click **"Networking"** (under Settings)
   - You'll see: "Public access is disabled" ✅

3. **Add Firewall Rule**
   - Scroll down to **"Firewall rules"** section
   - Click **"+ Add firewall rule"**
   - **Rule name**: `AllowMyIP-Temporary`
   - **Start IP**: Your public IP (e.g., 203.0.113.45)
   - **End IP**: Same as Start IP
   - Click **"Save"** at the top of the page

4. **Wait for Update**
   - You'll see: "Updating server..."
   - Wait 10-30 seconds for the rule to apply
   - When complete, you'll see your rule in the list

5. **Verify Firewall Rule**
   - You should see the rule listed:
     - Name: AllowMyIP-Temporary
     - Start IP: YOUR.IP.HERE
     - End IP: YOUR.IP.HERE

> 💡 **Note**: Even with this rule, you'll still need SSL to connect.

### Option B: CLI Method

```bash
# Allow your IP to connect temporarily
az postgres flexible-server firewall-rule create \
  --resource-group rg-taskapp-prod \
  --name taskapp-db-YOUR-SUFFIX \
  --rule-name AllowMyIP-Temporary \
  --start-ip-address $MY_IP \
  --end-ip-address $MY_IP
```

**Expected output:**
```json
{
  "endIpAddress": "YOUR.IP.ADDRESS.HERE",
  "id": "/subscriptions/.../firewallRules/AllowMyIP-Temporary",
  "name": "AllowMyIP-Temporary",
  "resourceGroup": "rg-taskapp-prod",
  "startIpAddress": "YOUR.IP.ADDRESS.HERE"
}
```

### Verify Firewall Rule

```bash
# List all firewall rules
az postgres flexible-server firewall-rule list \
  --resource-group rg-taskapp-prod \
  --name taskapp-db-YOUR-SUFFIX \
  --output table
```

**Expected output:**
```
Name                   StartIpAddress      EndIpAddress
---------------------  ------------------  ------------------
AllowMyIP-Temporary    YOUR.IP.HERE        YOUR.IP.HERE
```

### What Just Happened? 🤔

- **Firewall Rule Created**: Your IP can now connect to the database
- **Temporary Access**: We'll remove this rule after schema initialization
- **Security Layer**: Even with this rule, SSL is required for connection

---

## Step 4: Connect to Database

### What You're Doing

Connecting to the PostgreSQL server to create the database and initialize the schema.

### Prerequisites

**Install PostgreSQL client** (if not already installed):

**Windows (PowerShell):**
```powershell
winget install PostgreSQL.PostgreSQL
```

**Mac:**
```bash
brew install postgresql@15
```

**Linux (Ubuntu/Debian):**
```bash
sudo apt-get update
sudo apt-get install postgresql-client-15
```

### Method 1: Using psql (Recommended)

```bash
# Connect to server (will prompt for password)
psql "host=taskapp-db-YOUR-SUFFIX.postgres.database.azure.com \
     port=5432 \
     dbname=postgres \
     user=taskapp_admin \
     sslmode=require"
```

**When prompted**: Enter the password from Step 1.

**Expected output:**
```
Password for user taskapp_admin:
psql (15.x)
SSL connection (protocol: TLSv1.3, cipher: TLS_AES_256_GCM_SHA384, compression: off)
Type "help" for help.

postgres=>
```

> 💡 **Success!** You're now connected to your Azure PostgreSQL server!

### Method 2: Using Azure CLI (Alternative)

```bash
# Connect using Azure CLI (auto-authenticates)
az postgres flexible-server connect \
  --name taskapp-db-YOUR-SUFFIX \
  --resource-group rg-taskapp-prod \
  --admin-user taskapp_admin \
  --database-name postgres
```

**When prompted**: Enter your password.

### Troubleshooting Connection Issues

**Error: "connection refused" or "timeout"**
```bash
# Check firewall rule exists
az postgres flexible-server firewall-rule list \
  --resource-group rg-taskapp-prod \
  --name taskapp-db-YOUR-SUFFIX \
  --output table

# Verify your current IP hasn't changed
curl -s ifconfig.me

# Update firewall rule if IP changed
az postgres flexible-server firewall-rule update \
  --resource-group rg-taskapp-prod \
  --name taskapp-db-YOUR-SUFFIX \
  --rule-name AllowMyIP-Temporary \
  --start-ip-address $(curl -s ifconfig.me) \
  --end-ip-address $(curl -s ifconfig.me)
```

**Error: "SSL connection is required"**
- Solution: Add `sslmode=require` to connection string

**Error: "password authentication failed"**
- Solution: Verify password from Step 1, check for typos

### Test Connection

**Once connected, run:**

```sql
-- Check PostgreSQL version
SELECT version();

-- List current databases
\l

-- List current user
SELECT current_user;

-- Check SSL connection
SELECT ssl_version();
```

**Expected output:**
```
                                                version
-------------------------------------------------------------------------------------------------------
 PostgreSQL 15.x on x86_64-pc-linux-gnu, compiled by gcc (Ubuntu 9.4.0-1ubuntu1~20.04.1) 9.4.0, 64-bit

    ssl_version
-----------------
 TLSv1.3
```

---

## Step 5: Initialize Database Schema

### What You're Doing

Creating the `taskmanagement_db` database and initializing all tables.

### Step 5.1: Create the Database

**In your psql session:**

```sql
-- Create the database
CREATE DATABASE taskmanagement_db;

-- Verify database created
\l

-- Connect to the new database
\c taskmanagement_db

-- Confirm you're in the right database
SELECT current_database();
```

**Expected output:**
```
CREATE DATABASE
You are now connected to database "taskmanagement_db" as user "taskapp_admin".
 current_database
------------------
 taskmanagement_db
```

### Step 5.2: Create Extensions

```sql
-- Enable UUID generation
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Verify extension
\dx
```

### Step 5.3: Create Tables

**Copy and paste this entire schema:**

```sql
-- =====================================================
-- Users Table
-- =====================================================
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    name VARCHAR(255) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create index on email for faster lookups
CREATE INDEX idx_users_email ON users(email);

-- =====================================================
-- Projects Table
-- =====================================================
CREATE TABLE projects (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255) NOT NULL,
    description TEXT,
    owner_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create index on owner_id for faster joins
CREATE INDEX idx_projects_owner_id ON projects(owner_id);

-- =====================================================
-- Tasks Table
-- =====================================================
CREATE TYPE task_status AS ENUM ('todo', 'in_progress', 'done');
CREATE TYPE task_priority AS ENUM ('low', 'medium', 'high');

CREATE TABLE tasks (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    title VARCHAR(255) NOT NULL,
    description TEXT,
    status task_status DEFAULT 'todo',
    priority task_priority DEFAULT 'medium',
    project_id UUID NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    assigned_to UUID REFERENCES users(id) ON DELETE SET NULL,
    due_date TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for faster queries
CREATE INDEX idx_tasks_project_id ON tasks(project_id);
CREATE INDEX idx_tasks_assigned_to ON tasks(assigned_to);
CREATE INDEX idx_tasks_status ON tasks(status);
CREATE INDEX idx_tasks_due_date ON tasks(due_date);

-- =====================================================
-- Updated_at Trigger Function
-- =====================================================
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Apply trigger to all tables
CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_projects_updated_at BEFORE UPDATE ON projects
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_tasks_updated_at BEFORE UPDATE ON tasks
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
```

### Step 5.4: Verify Schema

```sql
-- List all tables
\dt

-- Describe users table
\d users

-- Describe projects table
\d projects

-- Describe tasks table
\d tasks

-- List all enum types
\dT

-- List all indexes
\di
```

**Expected output:**
```
List of relations
 Schema |   Name   | Type  |     Owner
--------+----------+-------+---------------
 public | projects | table | taskapp_admin
 public | tasks    | table | taskapp_admin
 public | users    | table | taskapp_admin
```

### Step 5.5: Insert Test Data (Optional)

```sql
-- Create a test user
INSERT INTO users (email, password_hash, name)
VALUES ('test@example.com', 'hashed_password_here', 'Test User')
RETURNING id, email, name, created_at;

-- Create a test project
INSERT INTO projects (name, description, owner_id)
VALUES (
    'Test Project',
    'This is a test project',
    (SELECT id FROM users WHERE email = 'test@example.com')
)
RETURNING id, name, created_at;

-- Create a test task
INSERT INTO tasks (title, description, status, priority, project_id, assigned_to)
VALUES (
    'Test Task',
    'This is a test task',
    'todo',
    'medium',
    (SELECT id FROM projects WHERE name = 'Test Project'),
    (SELECT id FROM users WHERE email = 'test@example.com')
)
RETURNING id, title, status, created_at;

-- Verify data
SELECT u.name, p.name AS project, t.title AS task, t.status
FROM users u
JOIN projects p ON p.owner_id = u.id
JOIN tasks t ON t.project_id = p.id;
```

**Expected output:**
```
    name    |    project    |   task    | status
------------+---------------+-----------+--------
 Test User  | Test Project  | Test Task | todo
```

### What Just Happened? 🤔

- **Database Created**: taskmanagement_db is ready
- **UUID Extension**: Enabled for generating unique IDs
- **Tables Created**: users, projects, tasks with relationships
- **Indexes Added**: Optimized for common queries
- **Triggers Created**: Auto-update `updated_at` timestamps
- **Test Data**: Verified schema works correctly

---

## Step 6: Verify Database Setup

### Verification Checklist

Run these commands in your psql session:

```sql
-- 1. Check database exists
SELECT datname FROM pg_database WHERE datname = 'taskmanagement_db';

-- 2. Count tables (should be 3)
SELECT COUNT(*) AS table_count
FROM information_schema.tables
WHERE table_schema = 'public' AND table_type = 'BASE TABLE';

-- 3. List all tables with row counts
SELECT
    table_name,
    (SELECT COUNT(*) FROM users) AS users_count,
    (SELECT COUNT(*) FROM projects) AS projects_count,
    (SELECT COUNT(*) FROM tasks) AS tasks_count;

-- 4. Check foreign key constraints
SELECT
    tc.constraint_name,
    tc.table_name,
    kcu.column_name,
    ccu.table_name AS foreign_table_name,
    ccu.column_name AS foreign_column_name
FROM information_schema.table_constraints AS tc
JOIN information_schema.key_column_usage AS kcu
    ON tc.constraint_name = kcu.constraint_name
JOIN information_schema.constraint_column_usage AS ccu
    ON ccu.constraint_name = tc.constraint_name
WHERE tc.constraint_type = 'FOREIGN KEY';

-- 5. Check indexes
SELECT tablename, indexname, indexdef
FROM pg_indexes
WHERE schemaname = 'public'
ORDER BY tablename, indexname;

-- 6. Verify triggers
SELECT trigger_name, event_manipulation, event_object_table
FROM information_schema.triggers
WHERE trigger_schema = 'public';

-- 7. Test UUID generation
SELECT uuid_generate_v4();

-- 8. Exit psql
\q
```

### Expected Results Summary

| Check | Expected Result | Status |
|-------|----------------|--------|
| Database exists | taskmanagement_db | ⬜ |
| Table count | 3 tables (users, projects, tasks) | ⬜ |
| Foreign keys | 3 FKs (projects→users, tasks→projects, tasks→users) | ⬜ |
| Indexes | 7+ indexes | ⬜ |
| Triggers | 3 triggers (updated_at) | ⬜ |
| UUID extension | Generates valid UUIDs | ⬜ |
| Test data | 1 user, 1 project, 1 task | ⬜ |

**✅ Mark each box when verified!**

### Verify from Azure Portal

1. Go to https://portal.azure.com
2. Navigate to **Resource groups** → **rg-taskapp-prod**
3. Click on **taskapp-db-YOUR-SUFFIX**
4. Click **Databases** in left menu
5. You should see: `taskmanagement_db`, `postgres` (default)

### Document Your Database

```bash
# Create database documentation
cat >> azure/docs/DATABASE_SETUP.md << 'EOF'
# Database Setup Documentation

**Created**: January 26, 2026  
**Server**: taskapp-db-YOUR-SUFFIX  
**Database**: taskmanagement_db  
**PostgreSQL Version**: 15

## Connection Details

- **Host**: taskapp-db-YOUR-SUFFIX.postgres.database.azure.com
- **Port**: 5432
- **Database**: taskmanagement_db
- **Admin User**: taskapp_admin
- **SSL Mode**: require

## Schema

### Tables Created

1. **users**
   - `id` (UUID, PK)
   - `email` (VARCHAR, UNIQUE)
   - `password_hash` (VARCHAR)
   - `name` (VARCHAR)
   - `created_at`, `updated_at` (TIMESTAMP)

2. **projects**
   - `id` (UUID, PK)
   - `name` (VARCHAR)
   - `description` (TEXT)
   - `owner_id` (UUID, FK → users)
   - `created_at`, `updated_at` (TIMESTAMP)

3. **tasks**
   - `id` (UUID, PK)
   - `title` (VARCHAR)
   - `description` (TEXT)
   - `status` (ENUM: todo, in_progress, done)
   - `priority` (ENUM: low, medium, high)
   - `project_id` (UUID, FK → projects)
   - `assigned_to` (UUID, FK → users)
   - `due_date` (TIMESTAMP)
   - `created_at`, `updated_at` (TIMESTAMP)

## Indexes

- `idx_users_email` - users(email)
- `idx_projects_owner_id` - projects(owner_id)
- `idx_tasks_project_id` - tasks(project_id)
- `idx_tasks_assigned_to` - tasks(assigned_to)
- `idx_tasks_status` - tasks(status)
- `idx_tasks_due_date` - tasks(due_date)

## Backup Configuration

- **Retention**: 7 days
- **Geo-Redundant**: Disabled
- **Automated**: Daily

## Network Configuration

- **Access**: Private (VNet integrated)
- **Subnet**: subnet-database (10.0.2.0/24)
- **Public Access**: Disabled
- **Firewall**: Temporary rule for initial setup (to be removed)

## Connection String

```
postgresql://taskapp_admin:<password>@taskapp-db-YOUR-SUFFIX.postgres.database.azure.com:5432/taskmanagement_db?sslmode=require
```

## Next Steps

- Phase 5: Move credentials to Azure Key Vault
- Phase 6: Connect backend Container App to database
- Configure connection pooling (optional)
EOF

echo "✅ Database documentation created"
```

---

## Step 7: Remove Temporary Firewall Rule

### Why Remove It?

The firewall rule allowing your PC to connect was only needed for initial setup. Now that the schema is initialized, we should remove it for security.

> ✅ **Best Practice**: Only Container Apps (in VNet) should access the database.

### Option A: Console (Azure Portal) Method

**Step-by-step:**

1. **Navigate to Your PostgreSQL Server**
   - Go to Azure Portal: https://portal.azure.com
   - Navigate to **Resource groups** → **rg-taskapp-prod**
   - Click on **taskapp-db-YOUR-SUFFIX**

2. **Open Networking Settings**
   - In the left menu, click **"Networking"** (under Settings)

3. **Delete Firewall Rule**
   - Scroll down to **"Firewall rules"** section
   - Find the rule: **AllowMyIP-Temporary**
   - Click the **"..."** (three dots) on the right side of the rule
   - Click **"Delete"**
   - Confirm deletion when prompted
   - Click **"Save"** at the top of the page

4. **Wait for Update**
   - You'll see: "Updating server..."
   - Wait 10-30 seconds
   - When complete, the firewall rules list should be empty

5. **Verify Removal**
   - The **"Firewall rules"** section should show:
     - "No firewall rules configured" or empty list ✅

> ✅ **Success!** Your database is now fully private (VNet-only access).

### Option B: CLI Method

```bash
# Delete temporary firewall rule
az postgres flexible-server firewall-rule delete \
  --resource-group rg-taskapp-prod \
  --name taskapp-db-YOUR-SUFFIX \
  --rule-name AllowMyIP-Temporary \
  --yes
```

**Expected output:**
```
Firewall rule 'AllowMyIP-Temporary' deleted successfully.
```

### Verify Removal

```bash
# List firewall rules (should be empty)
az postgres flexible-server firewall-rule list \
  --resource-group rg-taskapp-prod \
  --name taskapp-db-YOUR-SUFFIX \
  --output table
```

**Expected output:**
```
(empty - no firewall rules)
```

</details>

---

## Summary

**Phase 3 Complete!** ✅

Your PostgreSQL Flexible Server is ready and waiting for the backend application to initialize the database schema in Phase 6. This approach is:
- More secure (no public access required)
- More maintainable (version-controlled migrations)
- Production-ready (same process used in production environments)
- Fully automated (no manual SQL scripts)

**Next**: Proceed to Phase 4 - Azure Container Registry

### Test Database is Now Private

```bash
# Try connecting from your PC (should fail now)
psql "host=taskapp-db-YOUR-SUFFIX.postgres.database.azure.com \
     port=5432 \
     dbname=taskmanagement_db \
     user=taskapp_admin \
     sslmode=require"
```

**Expected**: Connection should **timeout or be refused** ✅ (this is good! Database is private)

### What Just Happened? 🤔

- **Firewall Rule Removed**: Your PC can no longer connect
- **Database is Private**: Only resources in VNet can connect
- **Security Enhanced**: Database isolated from internet
- **Ready for Container Apps**: Phase 6 will deploy apps that can connect via VNet

---

## Cost Analysis

### What You're Paying For

| Resource | Cost | Notes |
|----------|------|-------|
| **PostgreSQL Flexible Server** | $0 (12 months free) | Burstable B1ms tier |
| **Storage (32 GB)** | $0 (included) | Up to 32 GB included |
| **Backup Storage** | $0 (first 32 GB) | 7-day retention |
| **Compute** | $0.025/hour after free tier | ~$18/month after 12 months |
| **Data Transfer (outbound)** | First 100 GB free | Then $0.087/GB |

**Phase 3 Total Cost**: **$0** (FREE for 12 months!) ✅

### After Free Tier Expires (Year 2)

| Item | Estimated Cost |
|------|----------------|
| B1ms compute | $18/month |
| Storage (32 GB) | Included |
| Backups | Included (first 32 GB) |
| **Total** | **~$18-20/month** |

### Cost Optimization Tips

**Save money by:**
1. **Stop/Start Server** (Burstable tier allows this)
   ```bash
   # Stop server when not in use
   az postgres flexible-server stop --name taskapp-db-YOUR-SUFFIX --resource-group rg-taskapp-prod
   
   # Start server when needed
   az postgres flexible-server start --name taskapp-db-YOUR-SUFFIX --resource-group rg-taskapp-prod
   ```

2. **Monitor Storage** - Delete old data, optimize indexes

3. **Reduce Backup Retention** - Change from 7 days to 1 day (saves backup storage)

4. **Use Private Access** - No data transfer costs within VNet

---

## Phase 3 Completion Checklist

Before proceeding to Phase 4, ensure all tasks are complete:

### Server Setup ✅
- [ ] Strong admin password generated (32+ characters)
- [ ] PostgreSQL Flexible Server created (Burstable B1ms)
- [ ] Server state is "Ready"
- [ ] VNet integration configured (subnet-database)
- [ ] Public access disabled
- [ ] Server FQDN saved

### Database Initialization ✅
- [ ] Temporary firewall rule created
- [ ] Connected to server via psql
- [ ] Database `taskmanagement_db` created
- [ ] UUID extension enabled
- [ ] `users` table created with indexes
- [ ] `projects` table created with indexes
- [ ] `tasks` table created with indexes
- [ ] Foreign key constraints verified
- [ ] Triggers created (updated_at)
- [ ] Test data inserted and verified

### Security ✅
- [ ] Temporary firewall rule removed
- [ ] Connection from PC now fails (private access verified)
- [ ] Credentials saved in temporary file
- [ ] Temporary credentials file in .gitignore
- [ ] SSL connection verified (TLSv1.3)

### Documentation ✅
- [ ] Server details documented
- [ ] Connection string saved
- [ ] Schema documented
- [ ] Backup configuration noted
- [ ] Ready for Phase 4!

---

## What You've Accomplished! 🎉

Congratulations! You've completed Phase 3. Here's what you built:

### Database Infrastructure ✅
- ✅ **PostgreSQL 15 Server**: Fully managed, production-ready
- ✅ **Private Access**: VNet-integrated, no internet exposure
- ✅ **Schema Initialized**: 3 tables with relationships
- ✅ **Automatic Backups**: 7-day retention
- ✅ **Free Tier**: $0 cost for 12 months!

### Security Implemented ✅
- ✅ **No Public Access**: Database only accessible from VNet
- ✅ **SSL Required**: Encrypted connections (TLSv1.3)
- ✅ **Strong Password**: 32+ character random password
- ✅ **Network Isolation**: Protected by NSG rules

### Skills Gained 🧠
- ✅ **Managed Databases**: PostgreSQL Flexible Server
- ✅ **VNet Integration**: Private database access
- ✅ **SQL Schema**: Tables, indexes, constraints, triggers
- ✅ **Azure Firewall**: Temporary access rules
- ✅ **psql Client**: Database connection and management

---

## Next Steps → Phase 4

You're now ready to set up Azure Container Registry!

**Phase 4 Preview - Azure Container Registry:**
- Create Azure Container Registry (ACR)
- Authenticate Docker to ACR
- Tag and push backend Docker image
- Tag and push frontend Docker image
- Enable vulnerability scanning
- Configure image retention policies

**Estimated Time**: 1-2 hours  
**New Concepts**: Container registries, Docker authentication, image tagging

**First command you'll run in Phase 4:**
```bash
az acr create \
  --resource-group rg-taskapp-prod \
  --name taskappacr[unique] \
  --sku Basic \
  --location eastus
```

---

## Useful Resources

### Official Documentation
- **PostgreSQL Flexible Server**: https://learn.microsoft.com/azure/postgresql/flexible-server/
- **VNet Integration**: https://learn.microsoft.com/azure/postgresql/flexible-server/concepts-networking-vnet
- **Backup & Restore**: https://learn.microsoft.com/azure/postgresql/flexible-server/concepts-backup-restore
- **Security Best Practices**: https://learn.microsoft.com/azure/postgresql/flexible-server/concepts-security

### Tools
- **Azure Portal**: https://portal.azure.com
- **Azure Data Studio**: https://docs.microsoft.com/sql/azure-data-studio/
- **pgAdmin**: https://www.pgadmin.org/
- **DBeaver**: https://dbeaver.io/

### Learning Resources
- **PostgreSQL Tutorial**: https://www.postgresqltutorial.com/
- **Azure Database for PostgreSQL Learning Path**: https://learn.microsoft.com/training/paths/azure-postgresql/

### Commands Reference

```bash
# Server Management
az postgres flexible-server list --resource-group rg-taskapp-prod
az postgres flexible-server show --name taskapp-db-XXX --resource-group rg-taskapp-prod
az postgres flexible-server stop --name taskapp-db-XXX --resource-group rg-taskapp-prod
az postgres flexible-server start --name taskapp-db-XXX --resource-group rg-taskapp-prod
az postgres flexible-server restart --name taskapp-db-XXX --resource-group rg-taskapp-prod

# Database Management
az postgres flexible-server db list --server-name taskapp-db-XXX --resource-group rg-taskapp-prod
az postgres flexible-server db show --server-name taskapp-db-XXX --resource-group rg-taskapp-prod --database-name taskmanagement_db

# Backup Management
az postgres flexible-server backup list --name taskapp-db-XXX --resource-group rg-taskapp-prod

# Firewall Rules
az postgres flexible-server firewall-rule list --name taskapp-db-XXX --resource-group rg-taskapp-prod
az postgres flexible-server firewall-rule create --name taskapp-db-XXX --resource-group rg-taskapp-prod --rule-name RuleName --start-ip-address X.X.X.X --end-ip-address X.X.X.X

# Connection
az postgres flexible-server connect --name taskapp-db-XXX --resource-group rg-taskapp-prod --admin-user taskapp_admin --database-name taskmanagement_db
```

---

## Phase 3 Complete! ✅

**Date Completed**: _______________  
**Time Spent**: _______________  
**Challenges Faced**: _______________  
**Notes**: _______________

**Resources Created:**
- [x] PostgreSQL Flexible Server: taskapp-db-YOUR-SUFFIX
- [x] Database: taskmanagement_db
- [x] Tables: users, projects, tasks
- [x] Private DNS Zone (auto-created)
- [x] Documentation files

**Ready for Phase 4?** YES / NO

If YES, proceed to `AZURE_PHASE_4_GUIDE.md` (to be created)  
If NO, review any incomplete checklist items above.

---

**Happy Database Building! 🗄️☁️**
