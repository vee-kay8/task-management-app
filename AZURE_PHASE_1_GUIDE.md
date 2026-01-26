# Azure Phase 1: Account Setup & Prerequisites - Complete Guide

**Duration**: 1-2 hours  
**Difficulty**: Beginner  
**Prerequisites**: None (fresh start)  
**Goal**: Get your Azure account ready and configured for cloud deployment

---

## 📋 Overview

This phase sets up the foundation for your entire Azure deployment journey. By the end, you'll have:

✅ Active Azure account with free credits  
✅ Billing alerts configured to prevent surprises  
✅ Azure CLI installed and authenticated  
✅ Multi-factor authentication enabled  
✅ Project directory structure created  
✅ Region selected for deployment  

---

## Table of Contents

1. [Create Azure Free Account](#step-1-create-azure-free-account)
2. [Set Up Billing Alerts](#step-2-set-up-billing-alerts)
3. [Install Azure CLI](#step-3-install-azure-cli)
4. [Authenticate with Azure](#step-4-authenticate-with-azure)
5. [Enable Multi-Factor Authentication](#step-5-enable-multi-factor-authentication)
6. [Choose Deployment Region](#step-6-choose-deployment-region)
7. [Create Project Directory Structure](#step-7-create-project-directory-structure)
8. [Verify Setup](#step-8-verify-setup)
9. [Phase 1 Completion Checklist](#phase-1-completion-checklist)

---

## Step 1: Create Azure Free Account

### What You Get with Azure Free Account

| Benefit | Details |
|---------|---------|
| **Free Credits** | $200 USD to use in first 30 days |
| **Free Services** | 25+ services free for 12 months |
| **Always Free** | 55+ services always free (limited usage) |
| **No Auto-Charge** | Won't charge after credits expire unless you upgrade |

**Popular Free Tier Services (12 Months):**
- 750 hours of Azure Database for PostgreSQL (B1ms)
- 180,000 vCPU-seconds of Azure Container Apps
- 2 million requests to Azure Functions
- 5 GB of Azure Container Registry storage
- And many more!

### Option A: Console (Azure Portal) Method

**Step-by-step:**

1. **Navigate to Azure Free Account Page**
   - Open browser: https://azure.microsoft.com/free
   - Click **"Start free"** button (big green button)

2. **Sign In or Create Microsoft Account**
   - **If you have Microsoft account** (Outlook, Hotmail, Xbox):
     - Click "Sign in"
     - Enter email and password
   - **If you don't have Microsoft account**:
     - Click "Create one"
     - Enter email address (can use Gmail, Yahoo, etc.)
     - Create password (min 8 characters, needs uppercase, lowercase, number)
     - Complete email verification

3. **Fill Out "About You" Section**
   - **Country/Region**: Select your country
   - **First name**: Your first name
   - **Last name**: Your last name
   - **Email address**: Auto-filled from Microsoft account
   - **Phone number**: Enter valid phone number (for verification)
   
   Click **"Next"**

4. **Identity Verification by Phone**
   - Azure will send you a code via:
     - **Text message** (recommended), OR
     - **Phone call**
   - Select verification method
   - Click **"Send verification code"**
   - Enter the 6-digit code you receive
   - Click **"Verify code"**

5. **Identity Verification by Card**
   > ⚠️ **Important**: Your card will NOT be charged. This is only for identity verification.
   
   - Enter credit/debit card information:
     - Card number
     - Expiration date
     - CVV/Security code
     - Cardholder name
     - Billing address
   
   > 💡 **What happens**: Azure may place a temporary $1 hold that will be released within 3-5 business days

   Click **"Next"**

6. **Agreement**
   - Read the terms:
     - Subscription Agreement
     - Offer Details
     - Privacy Statement
   - Check the box: "I agree to the subscription agreement, offer details, and privacy statement"
   - Click **"Sign up"**

7. **Wait for Account Setup**
   - Azure will set up your account (30-60 seconds)
   - You'll see a progress indicator
   - When complete, you'll be redirected to Azure Portal

8. **Welcome to Azure Portal!**
   - You'll see the Azure Portal home page
   - A tutorial may pop up (you can skip or follow it)
   - Your $200 credit is now active!

### Option B: CLI Method

> ⚠️ **Note**: Account creation must be done via browser. CLI is used after account exists.

Once you have an account, you can verify it via CLI:

```bash
# This will open a browser for authentication
az login

# You should see output similar to:
# [
#   {
#     "cloudName": "AzureCloud",
#     "id": "12345678-1234-1234-1234-123456789012",
#     "isDefault": true,
#     "name": "Azure subscription 1",
#     "state": "Enabled",
#     "tenantId": "87654321-4321-4321-4321-210987654321",
#     "user": {
#       "name": "your-email@example.com",
#       "type": "user"
#     }
#   }
# ]
```

### What Just Happened? 🤔

- **Microsoft Account**: Acts as your identity across all Microsoft services
- **Azure Subscription**: Created automatically - this is your "billing account"
- **Tenant/Directory**: Created automatically - this is your organizational boundary
- **$200 Credits**: Activated for 30 days from today
- **Free Services**: Activated for 12 months

### Save These Important Details

Open a notepad and save:

```
Azure Account Information
========================
Microsoft Account Email: _______________________
Subscription Name: Azure subscription 1 (default)
Subscription ID: _______________________________ (find this in Portal)
Tenant ID: ____________________________________ (find this in Portal)
Free Credits: $200 USD
Credits Expire: [30 days from today]
Account Created: [Today's date]
```

**Where to find Subscription ID:**
1. In Azure Portal, search for "Subscriptions"
2. Click on your subscription
3. Copy the "Subscription ID" (format: xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx)

---

## Step 2: Set Up Billing Alerts

### Why Set Up Billing Alerts? 💰

- **Prevent surprise charges** after free credits expire
- **Monitor spending** in real-time
- **Get notified** before you exceed your budget
- **Learn cost patterns** of Azure services

### Option A: Console (Azure Portal) Method

**Step-by-step:**

1. **Navigate to Cost Management**
   - In Azure Portal home page
   - Click **"Cost Management + Billing"** (or search for it in top search bar)
   - If you don't see it, click ☰ (hamburger menu) → **"Cost Management + Billing"**

2. **Select Your Subscription**
   - In the left sidebar, under **Billing scopes**, click **"Subscriptions"**
   - Click on your subscription name (usually "Azure subscription 1")

3. **Navigate to Budgets**
   - In the left sidebar, under **Cost Management**, click **"Budgets"**
   - Click **"+ Add"** button at the top

4. **Create Budget - Basics**
   - **Name**: `TaskApp-Monthly-Budget` (or any descriptive name)
   - **Reset period**: Monthly
   - **Creation date**: Today's date (auto-filled)
   - **Expiration date**: 1 year from today
   - **Amount**: `100` (USD - adjust based on your needs)
   
   > 💡 **Tip**: Start with $100/month. Based on our roadmap, Azure deployment costs $30-60/month.
   
   Click **"Next"**

5. **Set Alert Conditions**
   
   You'll create 2 alerts:
   
   **Alert 1: 80% Actual Spending**
   - Click **"+ Add alert condition"**
   - **Alert type**: Actual
   - **% of budget**: `80`
   - **Alert recipients (email)**: Enter your email address
   - Click **"Add"** (or **"Create"** if button says that)
   
   **Alert 2: 100% Forecasted Spending**
   - Click **"+ Add alert condition"** again
   - **Alert type**: Forecasted
   - **% of budget**: `100`
   - **Alert recipients (email)**: Enter your email address (same as above)
   - Click **"Add"**

6. **Review and Create**
   - Review your budget settings:
     - Budget name: TaskApp-Monthly-Budget
     - Amount: $100
     - 2 alert conditions configured
   - Click **"Create"**

7. **Confirmation**
   - You'll see a notification: "Budget created successfully"
   - Your budget appears in the Budgets list
   - You'll receive a confirmation email for the alert subscriptions

### Option B: CLI Method

```bash
# 1. First, get your subscription ID
az account show --query id --output tsv

# Save the output (you'll need it)
# Example: 12345678-1234-1234-1234-123456789012

# 2. Create the budget (replace values in [brackets])
az consumption budget create \
  --budget-name "TaskApp-Monthly-Budget" \
  --amount 100 \
  --time-grain Monthly \
  --start-date $(date -u +%Y-%m-01) \
  --end-date $(date -u -d "+1 year" +%Y-%m-%d) \
  --category Cost \
  --resource-group-filter [] \
  --notifications \
    actual_GreaterThan_80_Percent="{'enabled': true, 'operator': 'GreaterThan', 'threshold': 80, 'contactEmails': ['your-email@example.com']}" \
    forecasted_GreaterThan_100_Percent="{'enabled': true, 'operator': 'GreaterThan', 'threshold': 100, 'contactEmails': ['your-email@example.com'], 'thresholdType': 'Forecasted'}"

# Note: Replace 'your-email@example.com' with your actual email
```

**Simpler Windows PowerShell version:**

```powershell
# Get subscription ID
$subscriptionId = az account show --query id --output tsv

# Create budget
az consumption budget create `
  --budget-name "TaskApp-Monthly-Budget" `
  --amount 100 `
  --time-grain Monthly `
  --category Cost `
  --notifications actual_GreaterThan_80_Percent="{enabled: true, operator: GreaterThan, threshold: 80, contactEmails: ['your-email@example.com']}"
```

### Verify Billing Alert Setup

**Via Portal:**
1. Go to **Cost Management + Billing** → **Budgets**
2. You should see "TaskApp-Monthly-Budget" listed
3. Click on it to see details and alert conditions

**Via CLI:**
```bash
# List all budgets
az consumption budget list --output table

# Show specific budget details
az consumption budget show --budget-name "TaskApp-Monthly-Budget"
```

### What Just Happened? 🤔

- **Budget Created**: Azure now tracks your spending against $100/month
- **80% Alert**: You'll get email when you've spent $80 (actual charges)
- **100% Forecast Alert**: You'll get email when Azure predicts you'll hit $100 this month
- **Email Notifications**: Check your inbox for confirmation emails

> 💡 **Pro Tip**: Check Cost Management daily during deployment to learn Azure pricing patterns!

---

## Step 3: Install Azure CLI

### What is Azure CLI? 🛠️

Azure CLI (`az`) is a command-line tool to manage Azure resources. Think of it like Git for Azure.

**Why use CLI instead of Portal?**
- ✅ **Faster**: Run commands vs clicking through menus
- ✅ **Repeatable**: Save commands in scripts
- ✅ **Automatable**: Use in CI/CD pipelines
- ✅ **Powerful**: Access features not in Portal
- ✅ **Learning**: Understand what's actually happening

### Option A: Windows Installation

**Method 1: Using Windows Package Manager (winget) - Recommended**

1. **Open PowerShell or Command Prompt**
   - Press `Win + X`
   - Select **"Windows PowerShell"** or **"Terminal"**

2. **Install Azure CLI**
   ```powershell
   winget install Microsoft.AzureCLI
   ```

3. **Wait for Installation**
   - Takes 1-2 minutes
   - You'll see progress bars and status messages

4. **Restart your terminal**
   - Close and reopen PowerShell/Terminal
   - This ensures the `az` command is available

5. **Verify Installation**
   ```bash
   az --version
   ```
   
   You should see output like:
   ```
   azure-cli                         2.56.0
   
   core                              2.56.0
   telemetry                          1.1.0
   
   Dependencies:
   msal                              1.26.0
   azure-mgmt-resource               23.1.0
   
   Python location 'C:\Program Files\Microsoft SDKs\Azure\CLI2\python.exe'
   Extensions directory 'C:\Users\YourName\.azure\cliextensions'
   
   Python (Windows) 3.11.7 (tags/v3.11.7:fa7a6f2, Dec  4 2023, 19:24:49) [MSC v.1937 64 bit (AMD64)]
   ```

**Method 2: Using MSI Installer**

1. **Download the MSI Installer**
   - Visit: https://aka.ms/installazurecliwindows
   - Click **"Download"** (file will be ~60 MB)

2. **Run the Installer**
   - Double-click the downloaded `.msi` file
   - Click **"Next"** through the wizard
   - Accept license agreement
   - Choose installation location (default is fine)
   - Click **"Install"**

3. **Complete Installation**
   - Click **"Finish"**
   - Restart your terminal

4. **Verify Installation**
   ```bash
   az --version
   ```

### Option B: Linux/WSL Installation

**Ubuntu/Debian:**

```bash
# Get packages needed for the install process
sudo apt-get update
sudo apt-get install ca-certificates curl apt-transport-https lsb-release gnupg

# Download and install the Microsoft signing key
sudo mkdir -p /etc/apt/keyrings
curl -sLS https://packages.microsoft.com/keys/microsoft.asc |
  gpg --dearmor |
  sudo tee /etc/apt/keyrings/microsoft.gpg > /dev/null
sudo chmod go+r /etc/apt/keyrings/microsoft.gpg

# Add the Azure CLI software repository
AZ_REPO=$(lsb_release -cs)
echo "deb [arch=`dpkg --print-architecture` signed-by=/etc/apt/keyrings/microsoft.gpg] https://packages.microsoft.com/repos/azure-cli/ $AZ_REPO main" |
  sudo tee /etc/apt/sources.list.d/azure-cli.list

# Update repository information and install the azure-cli package
sudo apt-get update
sudo apt-get install azure-cli

# Verify installation
az --version
```

### Option C: macOS Installation

**Using Homebrew:**

```bash
# Install Azure CLI
brew update && brew install azure-cli

# Verify installation
az --version
```

### Useful Azure CLI Commands to Know

```bash
# Get help
az --help

# Get help for specific command
az login --help

# List all available services
az --help | grep "az "

# Check for updates
az upgrade

# Enable auto-completion (optional)
# For Bash
echo "source /etc/bash_completion.d/azure-cli" >> ~/.bashrc

# For PowerShell
Register-ArgumentCompleter -Native -CommandName az -ScriptBlock {
    param($commandName, $wordToComplete, $cursorPosition)
    $completion_file = New-TemporaryFile
    $env:ARGCOMPLETE_USE_TEMPFILES = 1
    $env:_ARGCOMPLETE_STDOUT_FILENAME = $completion_file
    $env:COMP_LINE = $wordToComplete
    $env:COMP_POINT = $cursorPosition
    $env:_ARGCOMPLETE = 1
    $env:_ARGCOMPLETE_SUPPRESS_SPACE = 0
    $env:_ARGCOMPLETE_IFS = "`n"
    az 2>&1 | Out-Null
    Get-Content $completion_file | Sort-Object | ForEach-Object {
        [System.Management.Automation.CompletionResult]::new($_, $_, "ParameterValue", $_)
    }
    Remove-Item $completion_file, Env:\_ARGCOMPLETE, Env:\ARGCOMPLETE_USE_TEMPFILES, Env:\_ARGCOMPLETE_STDOUT_FILENAME, Env:\COMP_LINE, Env:\COMP_POINT, Env:\_ARGCOMPLETE_SUPPRESS_SPACE, Env:\_ARGCOMPLETE_IFS
}
```

### What Just Happened? 🤔

- **Azure CLI Installed**: Command-line tool to interact with Azure
- **Python Included**: Azure CLI uses Python (bundled with installer)
- **Global Commands Available**: `az` command works from any directory
- **Auto-Updates**: Azure CLI can update itself with `az upgrade`

---

## Step 4: Authenticate with Azure

### What is Authentication? 🔐

Authentication proves to Azure that you are who you say you are. Once authenticated, you can create and manage resources.

**Authentication Methods:**
1. **Interactive Login** (browser-based) - Best for personal use
2. **Service Principal** (app credentials) - Best for automation/CI/CD
3. **Managed Identity** (for Azure resources) - Best for production apps

We'll use **Interactive Login** for now.

### Option A: Interactive Login (Recommended for Phase 1)

**Step-by-step:**

1. **Open Terminal**
   - PowerShell, Command Prompt, or Bash

2. **Run Login Command**
   ```bash
   az login
   ```

3. **Browser Opens Automatically**
   - A browser window/tab will open
   - URL: https://microsoft.com/devicelogin or similar
   - If browser doesn't open, you'll see a code to enter manually

4. **Sign In to Microsoft Account**
   - Enter the email address you used for Azure account
   - Enter your password
   - Complete MFA if enabled (recommended - we'll set this up next)

5. **Grant Permissions**
   - You may see: "Azure CLI wants to access your account"
   - Click **"Accept"** or **"Yes"**

6. **Success Message in Browser**
   - "You have signed in to the Azure Cross-platform Command Line Interface application on your device"
   - You can close this browser tab

7. **Check Terminal Output**
   ```json
   [
     {
       "cloudName": "AzureCloud",
       "homeTenantId": "87654321-4321-4321-4321-210987654321",
       "id": "12345678-1234-1234-1234-123456789012",
       "isDefault": true,
       "managedByTenants": [],
       "name": "Azure subscription 1",
       "state": "Enabled",
       "tenantId": "87654321-4321-4321-4321-210987654321",
       "user": {
         "name": "your-email@example.com",
         "type": "user"
       }
     }
   ]
   ```

### Verify Authentication

```bash
# Show current account info
az account show

# Show in table format (easier to read)
az account show --output table

# Show just your email
az account show --query user.name --output tsv

# List all subscriptions (if you have multiple)
az account list --output table
```

### Set Default Subscription (if you have multiple)

```bash
# List all subscriptions
az account list --output table

# Set default subscription by name
az account set --subscription "Azure subscription 1"

# Or set by subscription ID
az account set --subscription "12345678-1234-1234-1234-123456789012"

# Verify it's set as default
az account show --query name --output tsv
```

### Understanding the Output 📊

Let's break down what each field means:

```json
{
  "cloudName": "AzureCloud",          // Which Azure cloud (public, government, China)
  "homeTenantId": "abc123...",        // Your organization's directory ID
  "id": "def456...",                  // Your subscription ID (IMPORTANT!)
  "isDefault": true,                  // Is this the active subscription?
  "name": "Azure subscription 1",     // Subscription display name
  "state": "Enabled",                 // Account status (Enabled/Disabled)
  "tenantId": "abc123...",            // Directory/Tenant ID (usually same as homeTenantId)
  "user": {
    "name": "you@example.com",        // Your login email
    "type": "user"                    // Account type (user vs servicePrincipal)
  }
}
```

**Save your Subscription ID!** You'll need it throughout the project.

### Troubleshooting Authentication

**Problem: Browser doesn't open**
```bash
# Use device code flow instead
az login --use-device-code

# Follow the instructions to enter code at https://microsoft.com/devicelogin
```

**Problem: Multiple subscriptions, wrong one selected**
```bash
# Set the correct one
az account set --subscription "YOUR_SUBSCRIPTION_NAME"
```

**Problem: Token expired**
```bash
# Re-authenticate
az login

# Or clear cache and re-login
az account clear
az login
```

### What Just Happened? 🤔

- **Token Created**: Azure CLI received an access token (valid for hours/days)
- **Credentials Cached**: Token stored in `~/.azure/` directory
- **Default Subscription Set**: All commands will use this subscription unless specified
- **Ready to Deploy**: You can now create Azure resources!

---

## Step 5: Enable Multi-Factor Authentication (MFA)

### Why Enable MFA? 🔒

**Security Statistics:**
- 99.9% of account compromises could be prevented with MFA
- Passwords alone are not enough (stolen, phished, guessed)
- MFA adds a second proof of identity

**What is MFA?**
- **Something you know**: Password
- **Something you have**: Phone, authenticator app, security key
- **Something you are**: Fingerprint, face recognition

### Option A: Console (Azure Portal) Method

**Step-by-step:**

1. **Navigate to Security Settings**
   - In Azure Portal, click your profile picture (top right)
   - Click **"View account"**
   - Or go directly to: https://account.microsoft.com/security

2. **Open Security Info**
   - Click **"Security"** tab
   - Under "Two-step verification", click **"Set up two-step verification"**
   - Or click **"Advanced security options"**

3. **Choose MFA Method**
   
   **Recommended: Authenticator App**
   - Click **"Set up authenticator app"**
   - Download Microsoft Authenticator app:
     - iOS: App Store
     - Android: Google Play Store
   - Open the app on your phone
   - In browser, click **"Next"**
   - App shows QR code scanner
   - Scan the QR code shown in browser
   - App adds your Microsoft account
   - Enter the 6-digit code from app into browser
   - Click **"Next"**
   - Confirmation: "Authenticator app has been set up"

   **Alternative: SMS Text Message**
   - Click **"Set up phone for two-step verification"**
   - Select country code
   - Enter phone number
   - Choose **"Text me a code"**
   - Click **"Next"**
   - Enter the code received via SMS
   - Click **"Next"**
   - Confirmation: "Phone has been set up"

   **Alternative: Phone Call**
   - Click **"Set up phone for two-step verification"**
   - Select country code
   - Enter phone number
   - Choose **"Call me"**
   - Click **"Next"**
   - Answer the phone call
   - Press # to confirm
   - Confirmation: "Phone has been set up"

4. **Add Backup Method (Recommended)**
   - Click **"Add sign-in method"**
   - Choose a different method (e.g., if you use app, add phone as backup)
   - Follow steps to set up
   - This protects you if you lose your phone

5. **Test MFA**
   - Click **"Sign out"** from Azure Portal
   - Go to portal.azure.com
   - Sign in with your email and password
   - You'll be prompted for second factor
   - Enter code from authenticator app (or receive SMS/call)
   - Successfully logged in with MFA! ✅

### Option B: Set Up MFA During First Login

Azure may prompt you to set up MFA automatically:

1. **During Login**
   - After entering password, you see: "More information required"
   - Click **"Next"**

2. **Follow Setup Wizard**
   - Choose your verification method
   - Complete setup as described above

3. **Required or Optional?**
   - Some Azure accounts require MFA (enterprise/work accounts)
   - Personal accounts: optional but strongly recommended

### Manage MFA Methods

**Add Additional Methods:**
```
Portal → Profile → View account → Security → Advanced security options → 
Add a new way to sign in or verify
```

**Remove a Method:**
```
Portal → Profile → View account → Security → Advanced security options →
Click method → Remove
```

**Change Default Method:**
```
Portal → Profile → View account → Security → Advanced security options →
Click method → Set as default
```

### MFA for Azure CLI

**First time after enabling MFA:**
```bash
# Logout and login again
az logout
az login

# You'll be prompted for MFA during browser login
```

**Every subsequent CLI use:**
- Token is cached (valid for hours)
- No MFA prompt unless token expires
- When token expires, `az login` again and complete MFA

### What Just Happened? 🤔

- **Second Factor Added**: Your account now requires password + code
- **Authenticator App Linked**: Generates time-based codes every 30 seconds
- **Backup Method Added**: Can still login if phone is lost
- **Account More Secure**: 99.9% protection against account compromise

---

## Step 6: Choose Deployment Region

### What is an Azure Region? 🌍

An **Azure Region** is a set of datacenters deployed within a latency-defined perimeter and connected through a dedicated low-latency network.

**Key Concepts:**
- **Region**: Geographic location (e.g., East US, West Europe)
- **Availability Zone**: Isolated datacenters within a region
- **Region Pair**: Two regions for disaster recovery

### Available Azure Regions (Popular Ones)

| Region | Location | Code | Best For |
|--------|----------|------|----------|
| **East US** | Virginia, USA | eastus | US-based, general purpose |
| **East US 2** | Virginia, USA | eastus2 | US-based, more availability zones |
| **West US** | California, USA | westus | US West Coast |
| **Central US** | Iowa, USA | centralus | US Central |
| **West Europe** | Netherlands | westeurope | European users |
| **North Europe** | Ireland | northeurope | European users |
| **Southeast Asia** | Singapore | southeastasia | Asian users |
| **East Asia** | Hong Kong | eastasia | Asian users |
| **UK South** | London, UK | uksouth | UK users |
| **Australia East** | Sydney | australiaeast | Australian users |

### How to Choose a Region? 🤔

**Factors to Consider:**

1. **User Location** (Most Important)
   - Choose region closest to your users
   - Lower latency = faster app
   - Example: US users → East US, European users → West Europe

2. **Service Availability**
   - Not all services available in all regions
   - Azure Container Apps available in most regions
   - Check: https://azure.microsoft.com/en-us/explore/global-infrastructure/products-by-region/

3. **Cost**
   - Prices vary slightly by region
   - Generally: US regions cheapest, some regions 10-20% more expensive
   - Check: https://azure.microsoft.com/en-us/pricing/calculator/

4. **Compliance**
   - Data residency requirements
   - GDPR (Europe), HIPAA (healthcare), etc.
   - Example: EU data must stay in EU → choose West Europe

5. **Availability Zones**
   - Some regions have 3+ availability zones (better HA)
   - Example: East US 2, West Europe have 3 AZs

### Check Available Regions (CLI)

```bash
# List all regions
az account list-locations --output table

# List regions with availability zones
az account list-locations --query "[?metadata.regionType=='Physical' && metadata.physicalLocation!=null].{Name:name, DisplayName:displayName, HasAvailabilityZones:metadata.regionCategory}" --output table

# Check if specific service available in region
az provider show --namespace Microsoft.App --query "resourceTypes[?resourceType=='managedEnvironments'].locations" --output table
```

### Recommended Regions for This Project

**For Learning/Testing (This Project):**
- **East US** (`eastus`) - Most common, cheapest, all services available
- **West Europe** (`westeurope`) - If you're in Europe

**For Production (Future):**
- Region closest to your users
- With availability zones if possible
- Check service availability first

### Set Your Chosen Region

**Make a decision and save it:**

```bash
# I'm choosing East US for this project
# You can choose differently based on your location

# Save as environment variable (temporary)
export AZURE_REGION="eastus"

# Verify
echo $AZURE_REGION
```

**Windows PowerShell:**
```powershell
$env:AZURE_REGION = "eastus"
echo $env:AZURE_REGION
```

**Document your choice:**
```
Selected Azure Region
====================
Region Name: East US
Region Code: eastus
Reason: Learning project, most services available, lowest cost
Latency: ~50ms (from my location)
Availability Zones: Yes (3 zones)
```

### What Just Happened? 🤔

- **Region Selected**: All resources will be created in this region
- **Latency Considered**: Closer region = faster app
- **Cost Optimized**: Chose cost-effective region
- **Service Availability Verified**: Confirmed Container Apps available

---

## Step 7: Create Project Directory Structure

### Why Organize Files? 📁

As you deploy to Azure, you'll create:
- Infrastructure as Code files (Bicep/Terraform)
- Deployment scripts
- Configuration files
- Documentation

**Good organization now = Easy maintenance later!**

### Recommended Directory Structure

```
task-management-app/
├── azure/                          # All Azure-specific files
│   ├── bicep/                      # Infrastructure as Code (Bicep)
│   │   ├── main.bicep
│   │   ├── main.parameters.json
│   │   └── modules/
│   │       ├── resourceGroup.bicep
│   │       ├── virtualNetwork.bicep
│   │       ├── database.bicep
│   │       ├── containerRegistry.bicep
│   │       ├── keyVault.bicep
│   │       └── containerApps.bicep
│   ├── scripts/                    # Deployment automation scripts
│   │   ├── deploy.sh              # Main deployment script
│   │   ├── setup-acr.sh           # Container Registry setup
│   │   ├── setup-database.sh      # Database setup
│   │   ├── setup-keyvault.sh      # Key Vault setup
│   │   └── setup-containers.sh    # Container Apps deployment
│   ├── config/                     # Configuration files
│   │   ├── backend-container.yaml
│   │   └── frontend-container.yaml
│   └── docs/                       # Azure-specific documentation
│       ├── PHASE_1_SETUP.md
│       ├── PHASE_2_NETWORKING.md
│       └── ...
├── .github/
│   └── workflows/
│       ├── azure-deploy-backend.yml    # CI/CD for Azure
│       └── azure-deploy-frontend.yml
├── backend/                        # Existing Flask app (unchanged)
├── frontend/                       # Existing Next.js app (unchanged)
├── .gitignore                      # Updated with Azure-specific ignores
├── AZURE_DEPLOYMENT_ROADMAP.md     # Your main roadmap (already created)
└── README.md                       # Updated with Azure info
```

### Create Directory Structure (CLI)

**Option 1: PowerShell (Windows)**

```powershell
# Navigate to your project root
cd C:\Users\vokeo\OneDrive\Desktop\task-management-app

# Create Azure directories
New-Item -ItemType Directory -Force -Path "azure"
New-Item -ItemType Directory -Force -Path "azure\bicep"
New-Item -ItemType Directory -Force -Path "azure\bicep\modules"
New-Item -ItemType Directory -Force -Path "azure\scripts"
New-Item -ItemType Directory -Force -Path "azure\config"
New-Item -ItemType Directory -Force -Path "azure\docs"

# Verify structure
tree azure /F

# Or use dir if tree not available
dir azure -Recurse
```

**Option 2: Bash (Linux/WSL/Git Bash)**

```bash
# Navigate to your project root
cd /c/Users/vokeo/OneDrive/Desktop/task-management-app

# Create Azure directories
mkdir -p azure/{bicep/modules,scripts,config,docs}

# Verify structure
tree azure

# Or use ls if tree not available
ls -R azure
```

**Option 3: Manual (File Explorer)**

1. Open File Explorer
2. Navigate to: `C:\Users\vokeo\OneDrive\Desktop\task-management-app`
3. Create folders:
   - Right-click → New → Folder → "azure"
   - Inside azure: "bicep", "scripts", "config", "docs"
   - Inside bicep: "modules"

### Create Placeholder Files

**Create README files to mark directories:**

```bash
# In Git Bash or PowerShell (from project root)

# Azure directory README
echo "# Azure Deployment Files" > azure/README.md
echo "This directory contains Azure-specific infrastructure and deployment files." >> azure/README.md

# Bicep directory README
echo "# Azure Bicep Templates" > azure/bicep/README.md
echo "Infrastructure as Code using Azure Bicep language." >> azure/bicep/README.md

# Scripts directory README
echo "# Azure Deployment Scripts" > azure/scripts/README.md
echo "Bash scripts to automate Azure resource deployment." >> azure/scripts/README.md

# Verify files created
ls azure/*/README.md
```

### Update .gitignore for Azure

Add Azure-specific entries to your `.gitignore`:

```bash
# Open .gitignore in your editor, or append using command:

# Windows PowerShell
@"

# Azure specific
azure/bicep/*.parameters.json
!azure/bicep/main.parameters.json
*.bicepparam
.azure/
azure-pipelines.yml

# Terraform (if using Terraform instead of Bicep)
azure/terraform/.terraform/
azure/terraform/terraform.tfstate
azure/terraform/terraform.tfstate.backup
azure/terraform/.terraform.lock.hcl
azure/terraform/*.tfvars
!azure/terraform/*.tfvars.example

# Environment files
.env.azure
.env.azure.local

# Azure Functions (if used later)
local.settings.json
__blobstorage__/
__queuestorage__/
__azurite_db*__.json
.python_packages/

"@ | Add-Content .gitignore
```

### Create Phase Tracking File

Create a file to track your progress:

```bash
# Create AZURE_PROGRESS.md
cat > AZURE_PROGRESS.md << 'EOF'
# Azure Deployment Progress Tracker

**Last Updated**: [Date]
**Current Phase**: Phase 1 - Account Setup

## Completed Tasks

### Phase 1: Account Setup ✅
- [x] Created Azure free account
- [x] Set up billing alerts ($100/month budget)
- [x] Installed Azure CLI
- [x] Authenticated with Azure
- [x] Enabled MFA
- [x] Chose deployment region (eastus)
- [x] Created project directory structure

**Next**: Phase 2 - Virtual Network Setup

---

## Quick Reference

**Subscription ID**: [YOUR_SUBSCRIPTION_ID]
**Tenant ID**: [YOUR_TENANT_ID]
**Primary Region**: eastus
**Resource Group**: rg-taskapp-prod (to be created in Phase 2)

**Useful Commands**:
```bash
# Show current account
az account show

# List all resources
az resource list --output table

# Check costs
az consumption usage list --output table
```
EOF
```

### What Just Happened? 🤔

- **Organized Structure**: All Azure files will go in `/azure` directory
- **Separation of Concerns**: Backend/frontend code untouched
- **Version Control Ready**: .gitignore updated for Azure files
- **Documentation Location**: Dedicated `/azure/docs` folder
- **Scripts Ready**: `/azure/scripts` for automation

---

## Step 8: Verify Setup

### Verification Checklist ✅

Let's verify everything is set up correctly before moving to Phase 2.

**Run these commands:**

```bash
# 1. Verify Azure CLI version
az --version
# Expected: azure-cli 2.56.0 or higher

# 2. Verify authentication
az account show
# Expected: JSON output with your subscription details

# 3. Verify subscription is active
az account show --query "state" --output tsv
# Expected: "Enabled"

# 4. List all regions (verify access)
az account list-locations --query "[].name" --output tsv | head -5
# Expected: List of region names

# 5. Verify you can query resources (should be empty for now)
az resource list --output table
# Expected: Empty table (no resources created yet)

# 6. Test creating a resource group (dry run)
az group create --name test-verify --location eastus --dry-run
# Expected: Shows what would be created (no actual creation)

# 7. Check your free credits balance (if within 30 days)
# Go to Portal > Cost Management + Billing > Credits

# 8. Verify directory structure
ls -la azure/
# Expected: bicep/, scripts/, config/, docs/ directories

# 9. Test budget was created
az consumption budget list --query "[].name" --output tsv
# Expected: "TaskApp-Monthly-Budget"

# 10. Verify git is tracking properly
git status
# Expected: Shows azure/ directory as untracked (if not committed yet)
```

### Expected Results Summary

| Check | Command | Expected Result | Status |
|-------|---------|-----------------|--------|
| Azure CLI Installed | `az --version` | Version 2.56+ | ⬜ |
| Authenticated | `az account show` | Shows subscription | ⬜ |
| Subscription Active | `az account show --query state -o tsv` | "Enabled" | ⬜ |
| Can Access APIs | `az account list-locations` | Lists regions | ⬜ |
| Budget Created | `az consumption budget list` | Shows budget | ⬜ |
| Directory Structure | `ls azure/` | Shows subdirectories | ⬜ |
| MFA Enabled | Login to portal | Prompts for 2FA | ⬜ |
| Git Configured | `git status` | Shows azure/ folder | ⬜ |

**✅ Mark each box when verified!**

### Troubleshooting Common Issues

**Issue: `az: command not found`**
```bash
# Solution: Restart terminal after installation
# Or add to PATH manually (Windows):
# System Properties > Environment Variables > Path > Add Azure CLI path
```

**Issue: `az account show` returns error**
```bash
# Solution: Re-authenticate
az login
```

**Issue: Budget not showing in CLI**
```bash
# Solution: Budget might take a few minutes to appear
# Check in Portal instead: Cost Management + Billing > Budgets
```

**Issue: Can't create directories**
```bash
# Solution: Check you're in correct project directory
pwd  # Should show: .../task-management-app

# Navigate to correct directory
cd /c/Users/vokeo/OneDrive/Desktop/task-management-app
```

---

## Phase 1 Completion Checklist

Before proceeding to Phase 2, ensure all tasks are complete:

### Account Setup ✅
- [ ] Azure free account created
- [ ] $200 free credits activated
- [ ] Subscription ID saved in secure location
- [ ] Tenant ID saved in secure location

### Billing & Cost Management ✅
- [ ] Monthly budget created ($100)
- [ ] 80% actual spending alert configured
- [ ] 100% forecasted spending alert configured
- [ ] Email notifications confirmed
- [ ] Cost Management dashboard viewed

### Azure CLI ✅
- [ ] Azure CLI installed
- [ ] Version verified (2.56+)
- [ ] `az` command works from terminal
- [ ] Auto-completion enabled (optional)

### Authentication ✅
- [ ] Logged in via `az login`
- [ ] Subscription verified with `az account show`
- [ ] Default subscription set (if multiple)
- [ ] Token cached successfully

### Security ✅
- [ ] Multi-factor authentication enabled
- [ ] Authenticator app configured
- [ ] Backup MFA method added
- [ ] MFA tested by logging out and back in

### Region Selection ✅
- [ ] Deployment region chosen (recommended: eastus)
- [ ] Service availability verified in chosen region
- [ ] Region code saved: ______________
- [ ] Cost for region reviewed

### Project Structure ✅
- [ ] `/azure` directory created
- [ ] `/azure/bicep` directory created
- [ ] `/azure/bicep/modules` directory created
- [ ] `/azure/scripts` directory created
- [ ] `/azure/config` directory created
- [ ] `/azure/docs` directory created
- [ ] `.gitignore` updated for Azure files
- [ ] README files added to directories

### Documentation ✅
- [ ] Account details saved securely
- [ ] Subscription ID documented
- [ ] Region choice documented
- [ ] Progress tracker created (AZURE_PROGRESS.md)
- [ ] Phase 1 guide reviewed

### Verification ✅
- [ ] All verification commands run successfully
- [ ] No errors in `az account show`
- [ ] Budget visible in Cost Management
- [ ] Directory structure verified
- [ ] Ready to proceed to Phase 2!

---

## What You've Accomplished! 🎉

Congratulations! You've completed Phase 1. Here's what you achieved:

### Account & Access ✅
- ✅ Azure account with $200 free credits (30 days)
- ✅ 12 months of free services activated
- ✅ Secure access with MFA enabled
- ✅ Azure CLI ready for command-line deployment

### Cost Protection ✅
- ✅ $100/month budget preventing surprise charges
- ✅ Email alerts at 80% and 100% spending
- ✅ Real-time cost tracking enabled

### Project Foundation ✅
- ✅ Organized directory structure
- ✅ Version control configured
- ✅ Documentation started
- ✅ Region selected for optimal performance

### Knowledge Gained 🧠
- ✅ Azure Portal navigation
- ✅ Azure CLI basics
- ✅ Subscription and tenant concepts
- ✅ Azure regions and availability zones
- ✅ Cost management tools

---

## Next Steps → Phase 2

You're now ready to start building Azure infrastructure!

**Phase 2 Preview - Virtual Network Setup:**
- Create Resource Group (logical container for all resources)
- Create Virtual Network (isolated network)
- Create subnets for Container Apps and Database
- Configure Network Security Groups (firewall rules)
- Document network architecture

**Estimated Time**: 2-3 hours  
**New Concepts**: VNets, Subnets, NSGs, CIDR blocks

**Command to start Phase 2:**
```bash
# We'll begin by creating a resource group
az group create --name rg-taskapp-prod --location eastus
```

---

## Useful Resources

### Official Documentation
- **Azure Portal**: https://portal.azure.com
- **Azure CLI Reference**: https://learn.microsoft.com/en-us/cli/azure/
- **Azure Free Account**: https://azure.microsoft.com/free
- **Azure Regions**: https://azure.microsoft.com/explore/global-infrastructure/geographies/
- **Azure Pricing Calculator**: https://azure.microsoft.com/pricing/calculator/

### Learning Resources
- **Microsoft Learn** (Free courses): https://learn.microsoft.com/training/azure/
- **Azure Architecture Center**: https://learn.microsoft.com/azure/architecture/
- **Azure Updates**: https://azure.microsoft.com/updates/

### Community
- **Stack Overflow**: https://stackoverflow.com/questions/tagged/azure
- **Azure Reddit**: https://reddit.com/r/AZURE
- **Azure Discord**: https://discord.gg/microsoft

### Tools
- **VS Code Azure Extension**: Install "Azure Tools" extension
- **Azure Storage Explorer**: https://azure.microsoft.com/features/storage-explorer/
- **Azure Mobile App**: Monitor resources on the go (iOS/Android)

---

## Phase 1 Complete! ✅

**Date Completed**: _______________  
**Time Spent**: _______________  
**Challenges Faced**: _______________  
**Notes**: _______________

**Ready for Phase 2?** YES / NO

If YES, proceed to `AZURE_PHASE_2_GUIDE.md`  
If NO, review any incomplete checklist items above.

---

**Happy Azure Learning! 🚀☁️**
