# AWS Phase 3: RDS Database Setup

## Overview
Set up a managed PostgreSQL database using Amazon RDS (Relational Database Service). This will be the production database for your task management application.

**Timeline**: 2-3 hours  
**Cost**: ~$15-20/month (t3.micro instance, 20GB storage)  
**Prerequisites**: Phase 2 complete (VPC, subnets, security groups)

---

## What You'll Create

1. **DB Subnet Group**: Defines which subnets RDS can use
2. **RDS PostgreSQL Instance**: Managed database server
3. **Database Initialization**: Create tables and schema
4. **Connection Testing**: Verify database accessibility

---

## Architecture Decision: Database Accessibility

Since you deleted the NAT Gateway to save costs, we have two options for database setup:

### Option A: Publicly Accessible (Recommended for Learning)
- ✅ Easy to connect from your local machine
- ✅ Simple to initialize and test
- ✅ Can manage with GUI tools (pgAdmin, DBeaver)
- ⚠️ Must secure with security group rules
- 🔄 Can convert to private later

### Option B: Private with Bastion Host
- ✅ More secure, production-like setup
- ✅ Teaches bastion host pattern
- ⚠️ Requires EC2 instance ($3-4/month)
- ⚠️ More complex connection setup

**We'll use Option A** for this guide (publicly accessible with strict security group rules). You can switch to private access later when you deploy the application.

---

## Step 1: Create DB Subnet Group

A DB subnet group tells RDS which subnets it can use. RDS needs at least 2 subnets in different availability zones.

### AWS Console Method

1. **Navigate to RDS**
   - Open AWS Console
   - Search for "RDS" and click "RDS"

2. **Create Subnet Group**
   - In left sidebar, click "Subnet groups"
   - Click "Create DB subnet group"

3. **Configure Subnet Group**
   ```
   Name: taskapp-db-subnet-group
   Description: Subnet group for Task Management App database
   VPC: Select your VPC (10.0.0.0/16)
   ```

4. **Add Subnets**
   - Availability Zones: Select `us-east-1a` and `us-east-1b`
   - Subnets:
     - Select `10.0.3.0/24` (Private Subnet 1)
     - Select `10.0.4.0/24` (Private Subnet 2)

5. **Create**
   - Click "Create"
   - Wait for status: "Active"

### AWS CLI Method

```bash
# Create DB subnet group
aws rds create-db-subnet-group \
  --db-subnet-group-name taskapp-db-subnet-group \
  --db-subnet-group-description "Subnet group for Task Management App database" \
  --subnet-ids subnet-0681cafcc954cd8a6 subnet-04f1cbee6ad2f9d17 \
  --tags Key=Project,Value=TaskManagementApp Key=Phase,Value=3

# Verify creation
aws rds describe-db-subnet-groups \
  --db-subnet-group-name taskapp-db-subnet-group
```

---

## Step 2: Modify Database Security Group

Update the database security group to allow access from your local IP (for initialization and management).

### Get Your Public IP

```bash
# Windows (PowerShell)
(Invoke-WebRequest -Uri "https://api.ipify.org").Content

# Alternative: Visit https://whatismyipaddress.com/
```

### AWS Console Method

1. **Navigate to Security Groups**
   - Go to VPC Console → Security Groups
   - Find "TaskApp-Database-SG" (sg-0c57afe621eb3932d)

2. **Add Inbound Rule**
   - Click "Edit inbound rules"
   - Click "Add rule"
   ```
   Type: PostgreSQL
   Protocol: TCP
   Port: 5432
   Source: My IP (or enter your IP/32)
   Description: Temporary access for database initialization
   ```

3. **Save Rules**
   - Click "Save rules"

### AWS CLI Method

```bash
# Replace YOUR_IP with your actual IP address
YOUR_IP="123.45.67.89"

# Add rule to allow your IP
aws ec2 authorize-security-group-ingress \
  --group-id sg-0c57afe621eb3932d \
  --protocol tcp \
  --port 5432 \
  --cidr ${YOUR_IP}/32 \
  --region us-east-1

# Verify
aws ec2 describe-security-groups \
  --group-ids sg-0c57afe621eb3932d \
  --query 'SecurityGroups[0].IpPermissions'
```

**Important**: You'll remove this rule later and restrict access to only the backend security group.

---

## Step 3: Create RDS PostgreSQL Instance

### AWS Console Method

1. **Navigate to RDS Dashboard**
   - Click "Databases" in left sidebar
   - Click "Create database"

2. **Choose Database Creation Method**
   - Select: **Standard create**

3. **Engine Options**
   ```
   Engine type: PostgreSQL
   Engine Version: PostgreSQL 15.x (latest)
   ```

4. **Templates**
   - Select: **Free tier** (if eligible)
   - Otherwise: **Dev/Test**

5. **Settings**
   ```
   DB instance identifier: taskapp-db
   Master username: postgres
   Master password: <Create a strong password>
   Confirm password: <Same password>
   ```
   
   **⚠️ IMPORTANT**: Save your password securely! You'll need it to connect.

6. **Instance Configuration**
   ```
   DB instance class: Burstable classes (includes t classes)
   Select: db.t3.micro (or db.t4g.micro)
   ```

7. **Storage**
   ```
   Storage type: General Purpose SSD (gp3)
   Allocated storage: 20 GiB
   ☐ Enable storage autoscaling (uncheck for now)
   ```

8. **Connectivity**
   ```
   VPC: Select your VPC (10.0.0.0/16)
   DB subnet group: taskapp-db-subnet-group
   Public access: Yes (for now - will change later)
   VPC security group: Choose existing
   Existing security groups:
     ☑ TaskApp-Database-SG (remove default if present)
   Availability Zone: No preference
   ```

9. **Database Authentication**
   ```
   Select: Password authentication
   ```

10. **Additional Configuration** (click to expand)
    ```
    Initial database name: taskmanagement
    ☐ Enable automated backups (uncheck for dev environment)
    ☐ Enable encryption (optional - costs extra)
    ☐ Enable Enhanced monitoring (uncheck for now)
    ☐ Enable auto minor version upgrade (your choice)
    ```

11. **Create Database**
    - Review estimated monthly costs
    - Click "Create database"
    - Wait 5-10 minutes for status: "Available"

### AWS CLI Method

```bash
# Set your master password (replace with your secure password)
DB_PASSWORD="YourSecurePassword123!"

# Create RDS instance
aws rds create-db-instance \
  --db-instance-identifier taskapp-db \
  --db-instance-class db.t3.micro \
  --engine postgres \
  --engine-version 15.5 \
  --master-username postgres \
  --master-user-password "$DB_PASSWORD" \
  --allocated-storage 20 \
  --storage-type gp3 \
  --db-subnet-group-name taskapp-db-subnet-group \
  --vpc-security-group-ids sg-0c57afe621eb3932d \
  --publicly-accessible \
  --db-name taskmanagement \
  --backup-retention-period 0 \
  --no-multi-az \
  --no-auto-minor-version-upgrade \
  --tags Key=Project,Value=TaskManagementApp Key=Phase,Value=3

# Monitor creation status (repeat every 30 seconds)
aws rds describe-db-instances \
  --db-instance-identifier taskapp-db \
  --query 'DBInstances[0].[DBInstanceIdentifier,DBInstanceStatus,Endpoint.Address]' \
  --output table
```

**Wait for status**: `available` (5-10 minutes)

---

## Step 4: Get Database Endpoint

Once the database is available, get the endpoint address.

### AWS Console Method

1. Click on "taskapp-db" database
2. Find "Endpoint & port" section
3. Copy the endpoint (looks like: `taskapp-db.xxxxxx.us-east-1.rds.amazonaws.com`)
4. Note the port: `5432`

### AWS CLI Method

```bash
# Get endpoint
aws rds describe-db-instances \
  --db-instance-identifier taskapp-db \
  --query 'DBInstances[0].Endpoint.Address' \
  --output text
```

---

## Step 5: Test Database Connection

Test that you can connect to the database from your local machine.

### Option A: Using psql (PostgreSQL Command Line)

#### Install psql (if not already installed)

**Windows**:
```bash
# Download PostgreSQL installer from postgresql.org
# Or use Chocolatey:
choco install postgresql15
```

**Mac**:
```bash
brew install postgresql@15
```

#### Connect to Database

```bash
# Replace with your actual endpoint and password
DB_ENDPOINT="taskapp-db.xxxxxx.us-east-1.rds.amazonaws.com"
DB_PASSWORD="YourSecurePassword123!"

# Connect
psql -h $DB_ENDPOINT -U postgres -d taskmanagement

# When prompted, enter your password

# Once connected, test:
\l              # List databases
\dt             # List tables (should be empty)
\q              # Quit
```

### Option B: Using DBeaver (GUI Tool)

1. **Download DBeaver** (free): https://dbeaver.io/download/
2. **Create New Connection**
   - Click "New Database Connection"
   - Select "PostgreSQL"
3. **Configure Connection**
   ```
   Host: taskapp-db.xxxxxx.us-east-1.rds.amazonaws.com
   Port: 5432
   Database: taskmanagement
   Username: postgres
   Password: YourSecurePassword123!
   ```
4. **Test Connection** → Should succeed
5. **Save** connection

---

## Step 6: Initialize Database Schema

Now we'll create the tables using your existing schema file.

### Review Schema File

Your schema is already defined in: `database/init/01-schema.sql`

Let's verify it's ready:

```bash
# Navigate to your project
cd /c/Users/vokeo/OneDrive/Desktop/task-management-app

# View the schema
cat database/init/01-schema.sql
```

### Execute Schema

#### Method 1: Using psql

```bash
# Set variables
DB_ENDPOINT="taskapp-db.xxxxxx.us-east-1.rds.amazonaws.com"
DB_PASSWORD="YourSecurePassword123!"

# Execute schema file
PGPASSWORD=$DB_PASSWORD psql \
  -h $DB_ENDPOINT \
  -U postgres \
  -d taskmanagement \
  -f database/init/01-schema.sql

# Verify tables were created
PGPASSWORD=$DB_PASSWORD psql \
  -h $DB_ENDPOINT \
  -U postgres \
  -d taskmanagement \
  -c "\dt"
```

#### Method 2: Using DBeaver

1. Open DBeaver connection to taskmanagement database
2. Click "SQL Editor" → "New SQL Script"
3. Copy contents of `database/init/01-schema.sql`
4. Paste into SQL Editor
5. Click "Execute SQL Statement" (or press Ctrl+Enter)
6. Verify tables created in Database Navigator

### Verify Schema

```bash
# Check that tables exist
PGPASSWORD=$DB_PASSWORD psql \
  -h $DB_ENDPOINT \
  -U postgres \
  -d taskmanagement \
  -c "SELECT table_name FROM information_schema.tables WHERE table_schema = 'public';"

# Expected output:
#   table_name
# -------------
#   users
#   projects
#   tasks
# (3 rows)
```

---

## Step 7: Create Database Connection String

Document the connection string for your application.

### Format

```
DATABASE_URL=postgresql://postgres:PASSWORD@ENDPOINT:5432/taskmanagement
```

### Example

```bash
# Create .env.aws file in your project
cat > .env.aws << 'EOF'
# AWS RDS Database Configuration
DATABASE_URL=postgresql://postgres:YourSecurePassword123!@taskapp-db.xxxxxx.us-east-1.rds.amazonaws.com:5432/taskmanagement

# Database Details
DB_HOST=taskapp-db.xxxxxx.us-east-1.rds.amazonaws.com
DB_PORT=5432
DB_NAME=taskmanagement
DB_USER=postgres
DB_PASSWORD=YourSecurePassword123!
EOF
```

**⚠️ IMPORTANT**: 
- Add `.env.aws` to your `.gitignore`
- Never commit database credentials to git
- This is for AWS deployment, separate from local `.env`

---

## Step 8: Update AWS Resources Documentation

Add the database information to your tracking document.

```bash
# This will be done automatically - information to add:
# - DB Instance Identifier: taskapp-db
# - Endpoint: taskapp-db.xxxxxx.us-east-1.rds.amazonaws.com
# - Port: 5432
# - Database Name: taskmanagement
# - Subnet Group: taskapp-db-subnet-group
# - Security Group: sg-0c57afe621eb3932d (TaskApp-Database-SG)
```

---

## Step 9: Secure the Database (Optional but Recommended)

Once you've initialized the database and tested connectivity, you can remove public access for better security.

### Remove Your IP from Security Group

```bash
# Get your IP again
YOUR_IP="123.45.67.89"

# Remove the rule
aws ec2 revoke-security-group-ingress \
  --group-id sg-0c57afe621eb3932d \
  --protocol tcp \
  --port 5432 \
  --cidr ${YOUR_IP}/32

# Verify (should only show VPC CIDR rule)
aws ec2 describe-security-groups \
  --group-ids sg-0c57afe621eb3932d \
  --query 'SecurityGroups[0].IpPermissions'
```

### Make Database Private (Optional)

You can keep it public for now (controlled by security group) or make it fully private:

```bash
# Make database private (can't undo easily)
aws rds modify-db-instance \
  --db-instance-identifier taskapp-db \
  --no-publicly-accessible \
  --apply-immediately

# Check status
aws rds describe-db-instances \
  --db-instance-identifier taskapp-db \
  --query 'DBInstances[0].[PubliclyAccessible,DBInstanceStatus]'
```

**Note**: If you make it private now, you'll need a bastion host or VPN to access it later. **Recommend keeping publicly accessible for now** but with strict security group rules.

---

## Phase 3 Verification Checklist

Use this checklist to verify Phase 3 completion:

### Database Infrastructure
- [ ] DB subnet group created (taskapp-db-subnet-group)
- [ ] DB subnet group includes both private subnets
- [ ] RDS instance created (taskapp-db)
- [ ] Instance status: Available
- [ ] Instance type: db.t3.micro (or db.t4g.micro)
- [ ] PostgreSQL version 15.x
- [ ] Allocated storage: 20 GiB

### Database Configuration
- [ ] Database name: taskmanagement
- [ ] Master username: postgres
- [ ] Master password saved securely
- [ ] VPC: Your VPC (10.0.0.0/16)
- [ ] Security group: TaskApp-Database-SG attached
- [ ] Publicly accessible: Yes (for now)

### Database Connectivity
- [ ] Endpoint address obtained
- [ ] Port 5432 accessible
- [ ] Successfully connected from local machine
- [ ] Security group allows your IP (or restricted access)

### Schema Initialization
- [ ] Schema file executed successfully
- [ ] Tables created: users, projects, tasks
- [ ] Can query tables (even if empty)
- [ ] Table structures match application models

### Documentation
- [ ] Database endpoint documented in aws-resources.md
- [ ] Connection string created in .env.aws
- [ ] .env.aws added to .gitignore
- [ ] Database password stored securely (password manager)

### Security
- [ ] Strong master password set (12+ characters, mixed case, numbers, symbols)
- [ ] Security group rules reviewed
- [ ] Unnecessary access removed (optional)
- [ ] Database private access considered (optional)

### Cost Management
- [ ] Monthly cost estimate reviewed (~$15-20)
- [ ] Automated backups disabled (dev environment)
- [ ] Multi-AZ disabled (dev environment)
- [ ] Enhanced monitoring disabled

---

## Troubleshooting

### Cannot Connect to Database

**Issue**: Connection timeout or refused

**Solutions**:
1. Check security group allows your IP on port 5432
2. Verify database is publicly accessible
3. Confirm endpoint address is correct
4. Check your IP hasn't changed (get current IP and update security group)
5. Ensure database status is "Available"

```bash
# Check database status
aws rds describe-db-instances \
  --db-instance-identifier taskapp-db \
  --query 'DBInstances[0].[DBInstanceStatus,PubliclyAccessible,Endpoint.Address]'

# Check security group rules
aws ec2 describe-security-groups \
  --group-ids sg-0c57afe621eb3932d \
  --query 'SecurityGroups[0].IpPermissions'
```

### Schema Execution Errors

**Issue**: Errors when running schema file

**Solutions**:
1. Check PostgreSQL version compatibility
2. Verify you're connected to correct database (taskmanagement)
3. Check for syntax errors in schema file
4. Try executing statements one at a time

```bash
# Connect and check database
PGPASSWORD=$DB_PASSWORD psql \
  -h $DB_ENDPOINT \
  -U postgres \
  -d taskmanagement \
  -c "SELECT version();"
```

### Database Creation Takes Too Long

**Issue**: RDS instance stuck in "creating" status

**Solutions**:
1. Wait at least 10 minutes (normal creation time: 5-10 min)
2. Check for any error events in RDS console
3. Verify subnet group has subnets in different AZs
4. Check account limits haven't been reached

```bash
# Check recent events
aws rds describe-events \
  --source-identifier taskapp-db \
  --source-type db-instance \
  --duration 60
```

### High Costs

**Issue**: RDS costs higher than expected

**Solutions**:
1. Verify instance class is db.t3.micro (not larger)
2. Check storage is 20 GiB (not auto-scaling)
3. Ensure automated backups are disabled
4. Confirm Multi-AZ is disabled
5. Review CloudWatch for usage patterns

```bash
# Check instance details
aws rds describe-db-instances \
  --db-instance-identifier taskapp-db \
  --query 'DBInstances[0].[DBInstanceClass,AllocatedStorage,MultiAZ,BackupRetentionPeriod]'
```

---

## Cost Breakdown

### Monthly Costs (Estimated)

| Resource | Specification | Monthly Cost |
|----------|--------------|--------------|
| RDS Instance | db.t3.micro | ~$12.50 |
| Storage | 20 GiB gp3 | ~$2.30 |
| Backups | Disabled | $0 |
| Multi-AZ | Disabled | $0 |
| **Total** | | **~$14.80/month** |

### Cost Optimization Tips

1. **Free Tier**: If you're within AWS free tier (first 12 months), you get:
   - 750 hours/month of db.t3.micro (enough for 1 instance running 24/7)
   - 20 GiB of storage
   - 20 GiB of backups
   - **Total: $0/month** (for 12 months)

2. **Stop Instance**: You can stop the RDS instance when not in use
   - Stopped instances: ~$2.30/month (storage only)
   - Maximum stopped duration: 7 days (auto-starts after)

3. **Delete When Not Needed**: For learning projects
   - Take a snapshot before deleting
   - Restore from snapshot when needed
   - Snapshot storage: ~$0.095/GB/month

```bash
# Stop instance (saves ~$12/month)
aws rds stop-db-instance \
  --db-instance-identifier taskapp-db

# Start instance again
aws rds start-db-instance \
  --db-instance-identifier taskapp-db

# Create snapshot before deleting
aws rds create-db-snapshot \
  --db-instance-identifier taskapp-db \
  --db-snapshot-identifier taskapp-db-snapshot-$(date +%Y%m%d)
```

---

## What's Next?

After completing Phase 3, you'll have:
- ✅ A production-ready PostgreSQL database
- ✅ Proper network isolation (private subnets)
- ✅ Database schema initialized
- ✅ Secure connection configuration

**Phase 4 Preview**: ECR & Docker Images
- Create Elastic Container Registry (ECR) repositories
- Build and push Docker images to ECR
- Tag images for deployment
- Set up image scanning and lifecycle policies

Estimated time: 1.5-2 hours  
Estimated cost: $0/month (ECR free tier: 500 MB storage)

---

## Quick Reference Commands

```bash
# Connect to database
PGPASSWORD=$DB_PASSWORD psql -h $DB_ENDPOINT -U postgres -d taskmanagement

# List all tables
PGPASSWORD=$DB_PASSWORD psql -h $DB_ENDPOINT -U postgres -d taskmanagement -c "\dt"

# Check table row counts
PGPASSWORD=$DB_PASSWORD psql -h $DB_ENDPOINT -U postgres -d taskmanagement -c "
SELECT 
  'users' as table_name, COUNT(*) as row_count FROM users
UNION ALL
SELECT 'projects', COUNT(*) FROM projects  
UNION ALL
SELECT 'tasks', COUNT(*) FROM tasks;
"

# Check database size
PGPASSWORD=$DB_PASSWORD psql -h $DB_ENDPOINT -U postgres -d taskmanagement -c "
SELECT 
  pg_size_pretty(pg_database_size('taskmanagement')) as database_size;
"

# Get RDS instance details
aws rds describe-db-instances \
  --db-instance-identifier taskapp-db \
  --output table

# Stop/Start database
aws rds stop-db-instance --db-instance-identifier taskapp-db
aws rds start-db-instance --db-instance-identifier taskapp-db

# Delete database (with final snapshot)
aws rds delete-db-instance \
  --db-instance-identifier taskapp-db \
  --final-db-snapshot-identifier taskapp-db-final-snapshot \
  --no-delete-automated-backups
```

---

## Summary

You've now set up a fully managed PostgreSQL database on AWS RDS. This provides:

- **Automated Management**: AWS handles backups, patching, and maintenance
- **High Availability**: Can enable Multi-AZ for production
- **Scalability**: Easy to upgrade instance size or storage
- **Security**: Isolated in private subnets with security group controls
- **Monitoring**: CloudWatch metrics for performance tracking

The database is ready to connect to your backend application in the next phases!
