# Phase 1: AWS Account Setup & Prerequisites - Detailed Guide

**Timeline**: Day 1 (2-4 hours)
**Difficulty**: Easy
**Cost**: $0 (Free tier)

---

## Pre-requisites

Before starting, ensure you have:
- Valid email address
- Credit/debit card (required for AWS account verification, won't be charged if staying in free tier)
- Phone number for verification
- Computer with internet access

---

## Step 1: Create AWS Account

### If You Don't Have an AWS Account:

1. **Navigate to AWS**
   - Go to https://aws.amazon.com
   - Click "Create an AWS Account" (top right)

2. **Enter Account Information**
   - Root user email address: [your email]
   - AWS account name: "TaskApp-Cloud-Deployment" (or your choice)
   - Click "Verify email address"

3. **Verify Email**
   - Check your email for verification code
   - Enter the 6-digit code
   - Click "Verify"

4. **Create Password**
   - Enter a strong password
   - Confirm password
   - Click "Continue"

5. **Enter Contact Information**
   - Account type: Select "Personal" (unless you have a business)
   - Full name: [your name]
   - Phone number: [your phone]
   - Country/Region: [your country]
   - Address: [your address]
   - Check the AWS Customer Agreement box
   - Click "Continue"

6. **Payment Information**
   - Enter credit/debit card details
   - Note: You will see a $1 authorization charge (refunded)
   - Click "Verify and Continue"

7. **Identity Verification**
   - Choose verification method: "Text message (SMS)" or "Voice call"
   - Enter the security code sent to your phone
   - Click "Continue"

8. **Select Support Plan**
   - Choose "Basic support - Free"
   - Click "Complete sign up"

9. **Wait for Confirmation**
   - You will receive email confirmation (may take a few minutes)
   - When ready, click "Go to the AWS Management Console"

### If You Already Have an AWS Account:

1. Go to https://console.aws.amazon.com
2. Sign in with your root email and password
3. Proceed to Step 2

---

## Step 2: Set Up Billing Alerts

**Why**: Avoid surprise charges by getting notified when spending exceeds threshold

1. **Navigate to Billing Dashboard**
   - Click your account name (top right)
   - Select "Billing and Cost Management"

2. **Enable Billing Alerts**
   - In left menu, click "Billing preferences"
   - Check "Receive Free Tier Usage Alerts"
   - Enter email: [your email]
   - Check "Receive Billing Alerts"
   - Click "Save preferences"

3. **Create Budget**
   - In left menu, click "Budgets"
   - Click "Create budget"
   - Budget type: "Cost budget"
   - Click "Next"
   
4. **Configure Budget**
   - Budget name: "Monthly-AWS-Budget"
   - Period: "Monthly"
   - Budget renewal type: "Recurring budget"
   - Start month: [Current month]
   - Budgeting method: "Fixed"
   - Enter budgeted amount: $10.00 (or your threshold)
   - Click "Next"

5. **Set Up Alert**
   - Alert threshold: 80% of budgeted amount
   - Email recipients: [your email]
   - Click "Next"
   - Review and click "Create budget"

**Expected Result**: You will receive email alerts when spending reaches 80% of $10

---

## Step 3: Create IAM User (Security Best Practice)

**Why**: Never use root account for daily tasks. Create IAM user with specific permissions.

1. **Navigate to IAM**
   - In AWS console search bar, type "IAM"
   - Click "IAM" service

2. **Create IAM User**
   - In left menu, click "Users"
   - Click "Create user"
   
3. **User Details**
   - User name: "taskapp-admin"
   - Check "Provide user access to the AWS Management Console"
   - Console password: "Custom password"
   - Enter strong password (save this!)
   - Uncheck "Users must create a new password at next sign-in"
   - Click "Next"

4. **Set Permissions**
   - Select "Attach policies directly"
   - Search for "AdministratorAccess"
   - Check the box next to "AdministratorAccess"
   - Click "Next"

5. **Review and Create**
   - Review details
   - Click "Create user"

6. **Save Credentials**
   - Click "Download .csv file" (contains console sign-in URL, username, password)
   - Store this file securely
   - Click "Return to users list"

7. **Get Console Sign-In URL**
   - In IAM Dashboard, look for "AWS Account" section
   - Copy "Account ID" or "Account Alias"
   - Your IAM user sign-in URL: https://[account-id].signin.aws.amazon.com/console

---

## Step 4: Enable MFA (Multi-Factor Authentication)

**Why**: Extra security layer to protect your account

### For Root User:

1. **Sign Out and Sign In as Root**
   - Sign out of IAM user
   - Go to https://console.aws.amazon.com
   - Click "Sign in to the Console"
   - Select "Root user"
   - Enter root email and password

2. **Navigate to Security Credentials**
   - Click your account name (top right)
   - Select "Security credentials"

3. **Assign MFA Device**
   - Under "Multi-factor authentication (MFA)", click "Assign MFA device"
   - MFA device name: "root-mfa"
   - MFA device: "Authenticator app" (recommended)
   - Click "Next"

4. **Set Up Authenticator App**
   - Install Google Authenticator or Microsoft Authenticator on your phone
   - In the app, scan the QR code shown
   - Enter two consecutive MFA codes
   - Click "Add MFA"

### For IAM User:

1. **Sign Out and Sign In as IAM User**
   - Use the IAM sign-in URL from Step 3
   - Username: taskapp-admin
   - Password: [your password]

2. **Navigate to Security Credentials**
   - Click your username (top right)
   - Select "Security credentials"

3. **Assign MFA** (same process as root)
   - Device name: "taskapp-admin-mfa"
   - Follow same steps as root MFA setup

**Expected Result**: Both root and IAM user protected with MFA

---

## Step 5: Install AWS CLI

### Windows Installation:

1. **Download AWS CLI**
   - Go to https://aws.amazon.com/cli/
   - Click "Download and install AWS CLI"
   - Download the Windows installer (MSI)

2. **Run Installer**
   - Double-click the downloaded .msi file
   - Follow installation wizard
   - Click "Next" → "Next" → "Install"
   - Click "Finish"

3. **Verify Installation**
   - Open Command Prompt or PowerShell
   - Run:
   ```powershell
   aws --version
   ```
   - Expected output: `aws-cli/2.x.x Python/3.x.x Windows/10`

### Mac Installation:

```bash
# Using Homebrew
brew install awscli

# Verify
aws --version
```

### Linux Installation:

```bash
# Download
curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"

# Unzip
unzip awscliv2.zip

# Install
sudo ./aws/install

# Verify
aws --version
```

---

## Step 6: Configure AWS CLI Credentials

1. **Create Access Keys for IAM User**
   - Sign in as IAM user (taskapp-admin)
   - Navigate to IAM → Users → taskapp-admin
   - Click "Security credentials" tab
   - Scroll to "Access keys"
   - Click "Create access key"
   - Use case: "Command Line Interface (CLI)"
   - Check "I understand the recommendation"
   - Click "Next"
   - Description: "Local development CLI access"
   - Click "Create access key"
   - **IMPORTANT**: Download .csv file or copy keys (you won't see them again)
   - Save:
     - Access Key ID: AKIAXXXXXXXXXXXXX
     - Secret Access Key: wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY

2. **Configure AWS CLI**
   - Open terminal/command prompt
   - Run:
   ```bash
   aws configure
   ```
   
   - You will be prompted for:
   ```
   AWS Access Key ID: [Paste your access key]
   AWS Secret Access Key: [Paste your secret key]
   Default region name: us-east-1 (recommended)
   Default output format: json
   ```

3. **Verify Configuration**
   ```bash
   aws sts get-caller-identity
   ```
   
   - Expected output:
   ```json
   {
       "UserId": "AIDAXXXXXXXXXXXXX",
       "Account": "123456789012",
       "Arn": "arn:aws:iam::123456789012:user/taskapp-admin"
   }
   ```

---

## Step 7: Choose Deployment Region

**Recommended Regions:**

1. **us-east-1** (US East - N. Virginia)
   - Pros: Most services available, cheapest, most documentation
   - Cons: Occasional outages
   - Recommended for: Learning, cost optimization

2. **us-west-2** (US West - Oregon)
   - Pros: Reliable, good service availability
   - Cons: Slightly more expensive than us-east-1

3. **eu-west-1** (Europe - Ireland)
   - Best for: European users

**Decision**: Use **us-east-1** for this project

**To verify your region**:
```bash
aws configure get region
```

**To change region**:
```bash
aws configure set region us-east-1
```

---

## Step 8: Review AWS Free Tier

**Services We'll Use in Free Tier:**

1. **EC2/ECS**
   - 750 hours per month of t2.micro or t3.micro instances
   - Note: ECS Fargate has limited free tier

2. **RDS**
   - 750 hours per month of db.t2.micro or db.t3.micro
   - 20 GB storage

3. **S3**
   - 5 GB storage
   - 20,000 GET requests
   - 2,000 PUT requests

4. **CloudFront**
   - 50 GB data transfer out
   - 2,000,000 HTTP/HTTPS requests

5. **Load Balancer**
   - NOT free (costs ~$16-20/month)
   - This will be main cost

**Check Your Free Tier Usage**:
- Go to Billing Dashboard
- Click "Free Tier" in left menu
- Monitor usage throughout project

---

## Step 9: Create Project Structure

1. **Create AWS Directory**
   ```bash
   cd /c/Users/vokeo/OneDrive/Desktop/task-management-app
   mkdir aws
   cd aws
   ```

2. **Create Subdirectories**
   ```bash
   mkdir infrastructure
   mkdir terraform
   mkdir docs
   mkdir scripts
   ```

3. **Verify Structure**
   ```bash
   ls
   ```
   
   Expected:
   ```
   infrastructure/
   terraform/
   docs/
   scripts/
   ```

---

## Step 10: Document Your Setup

Create a file to track your AWS resources:

```bash
cd docs
touch aws-resources.md
```

Add this content:

```markdown
# AWS Resources

## Account Information
- Account ID: [your account id]
- IAM User: taskapp-admin
- Region: us-east-1

## Access
- Console URL: https://[account-id].signin.aws.amazon.com/console
- MFA: Enabled
- Access Keys: Created and configured

## Billing
- Budget: $10/month
- Alert Threshold: 80% ($8)
- Billing alerts: Enabled

## Next Steps
- Ready for Phase 2: VPC and networking setup
```

---

## Verification Checklist

Before moving to Phase 2, verify:

- [ ] AWS account created and accessible
- [ ] Billing alerts configured ($10 budget, 80% threshold)
- [ ] IAM user created (taskapp-admin)
- [ ] MFA enabled for both root and IAM user
- [ ] AWS CLI installed (version 2.x)
- [ ] AWS CLI configured with credentials
- [ ] Can run `aws sts get-caller-identity` successfully
- [ ] Region set to us-east-1
- [ ] Free tier usage dashboard accessible
- [ ] Project structure created (aws/ directory with subdirectories)
- [ ] AWS resources documented

---

## Expected Time

- AWS account creation: 15-20 minutes
- Billing alerts: 5 minutes
- IAM user setup: 10 minutes
- MFA setup: 10 minutes
- AWS CLI installation: 5-10 minutes
- AWS CLI configuration: 5 minutes
- Documentation: 10 minutes

**Total**: 60-80 minutes

---

## Troubleshooting

### Issue: Can't create AWS account
- Ensure you're using a valid credit/debit card
- Use a different email if you've had an AWS account before
- Contact AWS support if verification fails

### Issue: AWS CLI not found after installation
- Windows: Restart terminal/PowerShell
- Check PATH environment variable
- Reinstall AWS CLI

### Issue: Access denied when running AWS CLI commands
- Verify credentials are correct: `cat ~/.aws/credentials`
- Ensure IAM user has AdministratorAccess policy
- Check access keys are active in IAM console

### Issue: Wrong region
- Run: `aws configure set region us-east-1`
- Verify: `aws configure get region`

---

## What's Next?

After completing Phase 1, you're ready for:

**Phase 2: VPC and Network Infrastructure**
- Create VPC
- Set up subnets
- Configure security groups
- Deploy Internet and NAT gateways

**Estimated time for Phase 2**: 2-3 hours

---

**Phase 1 Status**: ⬜ Not Started → Mark as ✅ Complete when done
