# Phase 2: Network Infrastructure (VPC Setup) - Detailed Guide

**Timeline**: Days 2-3 (3-4 hours)
**Difficulty**: Medium
**Cost**: ~$1-2/day (NAT Gateway)

---

## Overview

In this phase, you will create the foundational networking infrastructure for your application:
- Virtual Private Cloud (VPC)
- Public and Private Subnets across 2 Availability Zones
- Internet Gateway for public internet access
- NAT Gateway for private subnet internet access
- Route Tables for traffic routing
- Security Groups for firewall rules

---

## Architecture You're Building

```
Internet
    |
Internet Gateway
    |
    +-- Public Subnet 1 (us-east-1a)  -- NAT Gateway
    |       |
    |       +-- Load Balancer
    |
    +-- Public Subnet 2 (us-east-1b)
    |       |
    |       +-- Load Balancer (HA)
    |
    +-- Private Subnet 1 (us-east-1a)
    |       |
    |       +-- Backend (ECS Tasks)
    |       +-- Database (RDS)
    |
    +-- Private Subnet 2 (us-east-1b)
            |
            +-- Backend (ECS Tasks - HA)
            +-- Database (RDS - HA)
```

---

## Pre-requisites

Before starting, ensure:
- [ ] Phase 1 completed (AWS account, IAM user, AWS CLI configured)
- [ ] Signed in to AWS Console as IAM user (taskapp-admin)
- [ ] Region set to us-east-1
- [ ] Terminal/command prompt open

---

## Step 1: Create VPC

**What**: Virtual Private Cloud - Your isolated network in AWS
**Why**: All resources will live in this network

### Via AWS Console:

1. **Navigate to VPC**
   - In AWS Console search bar, type "VPC"
   - Click "VPC" service

2. **Create VPC**
   - Click "Create VPC" (orange button, top right)

3. **VPC Settings**
   - Resources to create: Select "VPC only"
   - Name tag: `taskapp-vpc`
   - IPv4 CIDR block: `10.0.0.0/16`
     - This gives you 65,536 IP addresses (10.0.0.0 to 10.0.255.255)
   - IPv6 CIDR block: No IPv6 CIDR block
   - Tenancy: Default
   - Tags:
     - Key: `Name`, Value: `taskapp-vpc`
     - Key: `Project`, Value: `TaskManagement`
     - Key: `Environment`, Value: `Production`

4. **Create VPC**
   - Click "Create VPC"
   - Wait for creation (should be instant)
   - Copy VPC ID (looks like: vpc-0123456789abcdef0)

5. **Enable DNS Settings**
   - Select your VPC (checkbox)
   - Click "Actions" dropdown
   - Select "Edit VPC settings"
   - Check "Enable DNS hostnames"
   - Check "Enable DNS resolution"
   - Click "Save"

### Via AWS CLI:

```bash
# Create VPC
aws ec2 create-vpc \
    --cidr-block 10.0.0.0/16 \
    --tag-specifications 'ResourceType=vpc,Tags=[{Key=Name,Value=taskapp-vpc},{Key=Project,Value=TaskManagement},{Key=Environment,Value=Production}]'

# Save VPC ID (replace with your actual VPC ID from output)
export VPC_ID=vpc-0123456789abcdef0

# Enable DNS hostnames
aws ec2 modify-vpc-attribute \
    --vpc-id $VPC_ID \
    --enable-dns-hostnames

# Enable DNS resolution
aws ec2 modify-vpc-attribute \
    --vpc-id $VPC_ID \
    --enable-dns-support
```

**Save This**: VPC ID: `vpc-xxxxxxxxxxxxxxxxx`

---

## Step 2: Create Internet Gateway

**What**: Gateway that allows communication between VPC and the internet
**Why**: Public subnets need internet access

### Via AWS Console:

1. **Navigate to Internet Gateways**
   - In VPC Dashboard, left menu
   - Click "Internet gateways"

2. **Create Internet Gateway**
   - Click "Create internet gateway"
   - Name tag: `taskapp-igw`
   - Click "Create internet gateway"

3. **Attach to VPC**
   - After creation, you'll see "Attach to a VPC" button
   - Click "Attach to a VPC"
   - Select your VPC: `taskapp-vpc`
   - Click "Attach internet gateway"
   - State should change to "Attached"

### Via AWS CLI:

```bash
# Create Internet Gateway
aws ec2 create-internet-gateway \
    --tag-specifications 'ResourceType=internet-gateway,Tags=[{Key=Name,Value=taskapp-igw}]'

# Save IGW ID
export IGW_ID=igw-0123456789abcdef0

# Attach to VPC
aws ec2 attach-internet-gateway \
    --internet-gateway-id $IGW_ID \
    --vpc-id $VPC_ID
```

**Save This**: Internet Gateway ID: `igw-xxxxxxxxxxxxxxxxx`

---

## Step 3: Create Subnets

**What**: Subdivisions of your VPC
**Why**: Separate public (internet-facing) and private (internal) resources

### Public Subnet 1 (AZ: us-east-1a)

**Via Console:**

1. **Navigate to Subnets**
   - VPC Dashboard → Subnets
   - Click "Create subnet"

2. **Subnet Settings**
   - VPC ID: Select `taskapp-vpc`
   - Subnet name: `taskapp-public-subnet-1`
   - Availability Zone: `us-east-1a`
   - IPv4 CIDR block: `10.0.1.0/24`
     - This gives you 256 IP addresses (10.0.1.0 to 10.0.1.255)
   - Click "Create subnet"

3. **Enable Auto-assign Public IP**
   - Select the subnet (checkbox)
   - Click "Actions" → "Edit subnet settings"
   - Check "Enable auto-assign public IPv4 address"
   - Click "Save"

**Via CLI:**

```bash
# Create Public Subnet 1
aws ec2 create-subnet \
    --vpc-id $VPC_ID \
    --cidr-block 10.0.1.0/24 \
    --availability-zone us-east-1a \
    --tag-specifications 'ResourceType=subnet,Tags=[{Key=Name,Value=taskapp-public-subnet-1}]'

# Save Subnet ID
export PUBLIC_SUBNET_1=subnet-xxxxxxxxxxxxxxxxx

# Enable auto-assign public IP
aws ec2 modify-subnet-attribute \
    --subnet-id $PUBLIC_SUBNET_1 \
    --map-public-ip-on-launch
```

### Public Subnet 2 (AZ: us-east-1b)

Repeat the same process with:
- Subnet name: `taskapp-public-subnet-2`
- Availability Zone: `us-east-1b`
- IPv4 CIDR block: `10.0.2.0/24`
- Enable auto-assign public IP

```bash
# CLI version
aws ec2 create-subnet \
    --vpc-id $VPC_ID \
    --cidr-block 10.0.2.0/24 \
    --availability-zone us-east-1b \
    --tag-specifications 'ResourceType=subnet,Tags=[{Key=Name,Value=taskapp-public-subnet-2}]'

export PUBLIC_SUBNET_2=subnet-xxxxxxxxxxxxxxxxx

aws ec2 modify-subnet-attribute \
    --subnet-id $PUBLIC_SUBNET_2 \
    --map-public-ip-on-launch
```

### Private Subnet 1 (AZ: us-east-1a)

- Subnet name: `taskapp-private-subnet-1`
- Availability Zone: `us-east-1a`
- IPv4 CIDR block: `10.0.3.0/24`
- Do NOT enable auto-assign public IP

```bash
aws ec2 create-subnet \
    --vpc-id $VPC_ID \
    --cidr-block 10.0.3.0/24 \
    --availability-zone us-east-1a \
    --tag-specifications 'ResourceType=subnet,Tags=[{Key=Name,Value=taskapp-private-subnet-1}]'

export PRIVATE_SUBNET_1=subnet-xxxxxxxxxxxxxxxxx
```

### Private Subnet 2 (AZ: us-east-1b)

- Subnet name: `taskapp-private-subnet-2`
- Availability Zone: `us-east-1b`
- IPv4 CIDR block: `10.0.4.0/24`
- Do NOT enable auto-assign public IP

```bash
aws ec2 create-subnet \
    --vpc-id $VPC_ID \
    --cidr-block 10.0.4.0/24 \
    --availability-zone us-east-1b \
    --tag-specifications 'ResourceType=subnet,Tags=[{Key=Name,Value=taskapp-private-subnet-2}]'

export PRIVATE_SUBNET_2=subnet-xxxxxxxxxxxxxxxxx
```

**Save These**:
- Public Subnet 1 ID: `subnet-xxxxxxxxxxxxxxxxx`
- Public Subnet 2 ID: `subnet-xxxxxxxxxxxxxxxxx`
- Private Subnet 1 ID: `subnet-xxxxxxxxxxxxxxxxx`
- Private Subnet 2 ID: `subnet-xxxxxxxxxxxxxxxxx`

---

## Step 4: Create NAT Gateway

**What**: Network Address Translation gateway
**Why**: Allows private subnets to access internet (for updates, API calls) without being directly accessible from internet

**Note**: NAT Gateway costs ~$0.045/hour (~$32/month). This is the main cost in networking.

### Via Console:

1. **Navigate to NAT Gateways**
   - VPC Dashboard → NAT gateways
   - Click "Create NAT gateway"

2. **NAT Gateway Settings**
   - Name: `taskapp-nat-gateway`
   - Subnet: Select `taskapp-public-subnet-1` (MUST be public subnet)
   - Connectivity type: Public
   - Elastic IP allocation ID: Click "Allocate Elastic IP"
     - This creates a static public IP for the NAT gateway
   - Click "Create NAT gateway"

3. **Wait for Available Status**
   - Status will be "Pending" for 1-2 minutes
   - Refresh until status is "Available"

### Via CLI:

```bash
# Allocate Elastic IP
aws ec2 allocate-address --domain vpc

# Save Allocation ID from output
export EIP_ALLOC_ID=eipalloc-xxxxxxxxxxxxxxxxx

# Create NAT Gateway
aws ec2 create-nat-gateway \
    --subnet-id $PUBLIC_SUBNET_1 \
    --allocation-id $EIP_ALLOC_ID \
    --tag-specifications 'ResourceType=natgateway,Tags=[{Key=Name,Value=taskapp-nat-gateway}]'

# Save NAT Gateway ID
export NAT_GW_ID=nat-xxxxxxxxxxxxxxxxx

# Wait for NAT Gateway to be available
aws ec2 wait nat-gateway-available --nat-gateway-ids $NAT_GW_ID
```

**Save This**: NAT Gateway ID: `nat-xxxxxxxxxxxxxxxxx`

---

## Step 5: Create Route Tables

**What**: Rules that determine where network traffic is directed
**Why**: Direct public subnet traffic to Internet Gateway, private subnet traffic to NAT Gateway

### Public Route Table

**Via Console:**

1. **Navigate to Route Tables**
   - VPC Dashboard → Route tables
   - Notice one route table already exists (main/default)
   - Click "Create route table"

2. **Route Table Settings**
   - Name: `taskapp-public-rt`
   - VPC: Select `taskapp-vpc`
   - Click "Create route table"

3. **Add Internet Gateway Route**
   - Select the route table (checkbox)
   - Click "Routes" tab (bottom panel)
   - Click "Edit routes"
   - Click "Add route"
     - Destination: `0.0.0.0/0` (all internet traffic)
     - Target: Select "Internet Gateway" → Select your `taskapp-igw`
   - Click "Save changes"

4. **Associate Public Subnets**
   - Click "Subnet associations" tab
   - Click "Edit subnet associations"
   - Check boxes for:
     - `taskapp-public-subnet-1`
     - `taskapp-public-subnet-2`
   - Click "Save associations"

**Via CLI:**

```bash
# Create public route table
aws ec2 create-route-table \
    --vpc-id $VPC_ID \
    --tag-specifications 'ResourceType=route-table,Tags=[{Key=Name,Value=taskapp-public-rt}]'

export PUBLIC_RT_ID=rtb-xxxxxxxxxxxxxxxxx

# Add route to Internet Gateway
aws ec2 create-route \
    --route-table-id $PUBLIC_RT_ID \
    --destination-cidr-block 0.0.0.0/0 \
    --gateway-id $IGW_ID

# Associate public subnets
aws ec2 associate-route-table \
    --route-table-id $PUBLIC_RT_ID \
    --subnet-id $PUBLIC_SUBNET_1

aws ec2 associate-route-table \
    --route-table-id $PUBLIC_RT_ID \
    --subnet-id $PUBLIC_SUBNET_2
```

### Private Route Table

**Via Console:**

1. **Create Route Table**
   - Route tables → Create route table
   - Name: `taskapp-private-rt`
   - VPC: `taskapp-vpc`
   - Click "Create route table"

2. **Add NAT Gateway Route**
   - Select route table
   - Routes tab → Edit routes → Add route
     - Destination: `0.0.0.0/0`
     - Target: NAT Gateway → `taskapp-nat-gateway`
   - Save changes

3. **Associate Private Subnets**
   - Subnet associations tab → Edit subnet associations
   - Check:
     - `taskapp-private-subnet-1`
     - `taskapp-private-subnet-2`
   - Save associations

**Via CLI:**

```bash
# Create private route table
aws ec2 create-route-table \
    --vpc-id $VPC_ID \
    --tag-specifications 'ResourceType=route-table,Tags=[{Key=Name,Value=taskapp-private-rt}]'

export PRIVATE_RT_ID=rtb-xxxxxxxxxxxxxxxxx

# Add route to NAT Gateway
aws ec2 create-route \
    --route-table-id $PRIVATE_RT_ID \
    --destination-cidr-block 0.0.0.0/0 \
    --nat-gateway-id $NAT_GW_ID

# Associate private subnets
aws ec2 associate-route-table \
    --route-table-id $PRIVATE_RT_ID \
    --subnet-id $PRIVATE_SUBNET_1

aws ec2 associate-route-table \
    --route-table-id $PRIVATE_RT_ID \
    --subnet-id $PRIVATE_SUBNET_2
```

**Save These**:
- Public Route Table ID: `rtb-xxxxxxxxxxxxxxxxx`
- Private Route Table ID: `rtb-xxxxxxxxxxxxxxxxx`

---

## Step 6: Create Security Groups

**What**: Virtual firewalls that control inbound and outbound traffic
**Why**: Restrict access to only what's needed

### Database Security Group

**Via Console:**

1. **Navigate to Security Groups**
   - VPC Dashboard → Security groups
   - Click "Create security group"

2. **Security Group Settings**
   - Security group name: `taskapp-db-sg`
   - Description: `Security group for RDS PostgreSQL database`
   - VPC: `taskapp-vpc`

3. **Inbound Rules**
   - Click "Add rule"
     - Type: PostgreSQL
     - Protocol: TCP
     - Port range: 5432
     - Source: Custom → `10.0.0.0/16` (entire VPC CIDR)
     - Description: `PostgreSQL access from VPC`

4. **Outbound Rules**
   - Leave default (All traffic to 0.0.0.0/0)

5. **Tags**
   - Key: `Name`, Value: `taskapp-db-sg`
   - Click "Create security group"

**Via CLI:**

```bash
# Create database security group
aws ec2 create-security-group \
    --group-name taskapp-db-sg \
    --description "Security group for RDS PostgreSQL database" \
    --vpc-id $VPC_ID \
    --tag-specifications 'ResourceType=security-group,Tags=[{Key=Name,Value=taskapp-db-sg}]'

export DB_SG_ID=sg-xxxxxxxxxxxxxxxxx

# Add inbound rule for PostgreSQL
aws ec2 authorize-security-group-ingress \
    --group-id $DB_SG_ID \
    --protocol tcp \
    --port 5432 \
    --cidr 10.0.0.0/16
```

### Backend Security Group

**Via Console:**

- Name: `taskapp-backend-sg`
- Description: `Security group for backend ECS tasks`
- VPC: `taskapp-vpc`
- Inbound rules:
  - Type: Custom TCP
  - Port: 5000
  - Source: Custom → `10.0.0.0/16`
  - Description: `Backend API from VPC`

**Via CLI:**

```bash
aws ec2 create-security-group \
    --group-name taskapp-backend-sg \
    --description "Security group for backend ECS tasks" \
    --vpc-id $VPC_ID \
    --tag-specifications 'ResourceType=security-group,Tags=[{Key=Name,Value=taskapp-backend-sg}]'

export BACKEND_SG_ID=sg-xxxxxxxxxxxxxxxxx

aws ec2 authorize-security-group-ingress \
    --group-id $BACKEND_SG_ID \
    --protocol tcp \
    --port 5000 \
    --cidr 10.0.0.0/16
```

### Load Balancer Security Group

**Via Console:**

- Name: `taskapp-alb-sg`
- Description: `Security group for Application Load Balancer`
- VPC: `taskapp-vpc`
- Inbound rules:
  - Rule 1:
    - Type: HTTP
    - Port: 80
    - Source: Anywhere IPv4 (0.0.0.0/0)
    - Description: `HTTP from internet`
  - Rule 2:
    - Type: HTTPS
    - Port: 443
    - Source: Anywhere IPv4 (0.0.0.0/0)
    - Description: `HTTPS from internet`

**Via CLI:**

```bash
aws ec2 create-security-group \
    --group-name taskapp-alb-sg \
    --description "Security group for Application Load Balancer" \
    --vpc-id $VPC_ID \
    --tag-specifications 'ResourceType=security-group,Tags=[{Key=Name,Value=taskapp-alb-sg}]'

export ALB_SG_ID=sg-xxxxxxxxxxxxxxxxx

# Allow HTTP
aws ec2 authorize-security-group-ingress \
    --group-id $ALB_SG_ID \
    --protocol tcp \
    --port 80 \
    --cidr 0.0.0.0/0

# Allow HTTPS
aws ec2 authorize-security-group-ingress \
    --group-id $ALB_SG_ID \
    --protocol tcp \
    --port 443 \
    --cidr 0.0.0.0/0
```

**Save These**:
- Database SG ID: `sg-xxxxxxxxxxxxxxxxx`
- Backend SG ID: `sg-xxxxxxxxxxxxxxxxx`
- Load Balancer SG ID: `sg-xxxxxxxxxxxxxxxxx`

---

## Step 7: Update Backend Security Group

**Why**: Backend should only accept traffic from Load Balancer, not entire VPC

**Via Console:**

1. Go to Security Groups → `taskapp-backend-sg`
2. Inbound rules tab → Edit inbound rules
3. Delete the existing rule (10.0.0.0/16)
4. Add new rule:
   - Type: Custom TCP
   - Port: 5000
   - Source: Security group → `taskapp-alb-sg`
   - Description: `Backend API from ALB only`
5. Save rules

**Via CLI:**

```bash
# Remove old rule
aws ec2 revoke-security-group-ingress \
    --group-id $BACKEND_SG_ID \
    --protocol tcp \
    --port 5000 \
    --cidr 10.0.0.0/16

# Add new rule (from ALB security group)
aws ec2 authorize-security-group-ingress \
    --group-id $BACKEND_SG_ID \
    --protocol tcp \
    --port 5000 \
    --source-group $ALB_SG_ID
```

---

## Step 8: Document Resources

Update your `aws/docs/aws-resources.md` file:

```bash
cd /c/Users/vokeo/OneDrive/Desktop/task-management-app/aws/docs
```

Add this information:

```markdown
## Phase 2: Network Infrastructure

### VPC
- VPC ID: vpc-xxxxxxxxxxxxxxxxx
- CIDR Block: 10.0.0.0/16
- DNS Hostnames: Enabled
- DNS Resolution: Enabled

### Internet Gateway
- IGW ID: igw-xxxxxxxxxxxxxxxxx
- State: Attached to VPC

### Subnets
- Public Subnet 1: subnet-xxxxxxxxxxxxxxxxx (10.0.1.0/24, us-east-1a)
- Public Subnet 2: subnet-xxxxxxxxxxxxxxxxx (10.0.2.0/24, us-east-1b)
- Private Subnet 1: subnet-xxxxxxxxxxxxxxxxx (10.0.3.0/24, us-east-1a)
- Private Subnet 2: subnet-xxxxxxxxxxxxxxxxx (10.0.4.0/24, us-east-1b)

### NAT Gateway
- NAT Gateway ID: nat-xxxxxxxxxxxxxxxxx
- Elastic IP: xx.xx.xx.xx
- Subnet: Public Subnet 1
- State: Available

### Route Tables
- Public RT: rtb-xxxxxxxxxxxxxxxxx
  - Routes: 0.0.0.0/0 → Internet Gateway
  - Associations: Public Subnet 1, Public Subnet 2
  
- Private RT: rtb-xxxxxxxxxxxxxxxxx
  - Routes: 0.0.0.0/0 → NAT Gateway
  - Associations: Private Subnet 1, Private Subnet 2

### Security Groups
- Database SG: sg-xxxxxxxxxxxxxxxxx
  - Inbound: Port 5432 from VPC (10.0.0.0/16)
  
- Backend SG: sg-xxxxxxxxxxxxxxxxx
  - Inbound: Port 5000 from ALB SG
  
- Load Balancer SG: sg-xxxxxxxxxxxxxxxxx
  - Inbound: Port 80 from 0.0.0.0/0
  - Inbound: Port 443 from 0.0.0.0/0

### Cost Estimate (Phase 2)
- NAT Gateway: ~$0.045/hour = ~$32.40/month
- Elastic IP (while NAT Gateway running): Free
- VPC, Subnets, Route Tables, Security Groups: Free
- Internet Gateway: Free
**Total**: ~$32.40/month
```

---

## Step 9: Create Network Diagram

Create a visual representation of your network. You can use:
- draw.io (https://app.diagrams.net/)
- Lucidchart
- Or simply document in text

Save as: `aws/docs/network-diagram.png` or `.md`

---

## Verification Checklist

Verify everything is configured correctly:

### VPC Verification

```bash
# Verify VPC
aws ec2 describe-vpcs --vpc-ids $VPC_ID

# Expected: State should be "available"
# DNS hostnames and resolution should be enabled
```

### Subnets Verification

```bash
# List all subnets in VPC
aws ec2 describe-subnets --filters "Name=vpc-id,Values=$VPC_ID"

# Expected: 4 subnets (2 public, 2 private) across 2 AZs
```

### Route Tables Verification

```bash
# Describe public route table
aws ec2 describe-route-tables --route-table-ids $PUBLIC_RT_ID

# Expected: Route to Internet Gateway (0.0.0.0/0 → igw-xxx)

# Describe private route table
aws ec2 describe-route-tables --route-table-ids $PRIVATE_RT_ID

# Expected: Route to NAT Gateway (0.0.0.0/0 → nat-xxx)
```

### Security Groups Verification

```bash
# List security groups
aws ec2 describe-security-groups --filters "Name=vpc-id,Values=$VPC_ID"

# Expected: 3 security groups + 1 default
```

### Connectivity Test

You can't fully test connectivity until Phase 5 (deploying resources), but verify:

- [ ] VPC exists and is available
- [ ] 4 subnets created in correct AZs
- [ ] Internet Gateway attached to VPC
- [ ] NAT Gateway is available
- [ ] Public route table routes to Internet Gateway
- [ ] Private route table routes to NAT Gateway
- [ ] Subnets associated with correct route tables
- [ ] 3 security groups created with correct rules
- [ ] Public subnets have auto-assign public IP enabled

---

## Complete Checklist

Mark as complete:

- [ ] VPC created (10.0.0.0/16)
- [ ] DNS hostnames and resolution enabled
- [ ] Internet Gateway created and attached
- [ ] 2 public subnets created (AZ 1a and 1b)
- [ ] 2 private subnets created (AZ 1a and 1b)
- [ ] Auto-assign public IP enabled on public subnets
- [ ] Elastic IP allocated
- [ ] NAT Gateway created in public subnet
- [ ] NAT Gateway status is "Available"
- [ ] Public route table created
- [ ] Route to Internet Gateway added (0.0.0.0/0)
- [ ] Public subnets associated with public route table
- [ ] Private route table created
- [ ] Route to NAT Gateway added (0.0.0.0/0)
- [ ] Private subnets associated with private route table
- [ ] Database security group created
- [ ] Backend security group created
- [ ] Load Balancer security group created
- [ ] Backend SG updated to only allow traffic from ALB SG
- [ ] All resource IDs documented
- [ ] Network diagram created (optional)

---

## Expected Time

- VPC creation: 5 minutes
- Internet Gateway: 5 minutes
- Subnets (4): 15 minutes
- NAT Gateway: 10 minutes (including wait time)
- Route Tables (2): 15 minutes
- Security Groups (3): 20 minutes
- Documentation: 10 minutes
- Verification: 10 minutes

**Total**: 90-120 minutes (1.5-2 hours)

---

## Troubleshooting

### Issue: Can't create subnet in specific AZ

**Error**: "The subnet cannot be created because there are no more IP addresses available in this Availability Zone"

**Solution**: Choose a different AZ or use a smaller CIDR block

### Issue: NAT Gateway stuck in "Pending"

**Solution**: 
- Wait 2-3 minutes
- Refresh the page
- If stuck for >5 minutes, delete and recreate

### Issue: Route table association fails

**Error**: "Resource already associated with another route table"

**Solution**: 
- Subnets can only be associated with one route table
- Disassociate from current route table first

### Issue: Security group rule not working

**Common mistakes**:
- Wrong port number
- Wrong protocol (TCP vs UDP)
- Wrong source (should be security group ID, not CIDR)
- Forgetting to save changes

### Issue: NAT Gateway costs more than expected

**NAT Gateway costs**:
- $0.045/hour for the gateway itself (~$32/month)
- $0.045/GB data processed (additional)

**To reduce costs during development**:
- Consider deleting NAT Gateway when not actively using
- Recreate when needed
- Note: This will break private subnet internet connectivity

---

## Cost Optimization Tips

### During Development:

1. **Delete NAT Gateway when not in use**
   ```bash
   # Delete NAT Gateway
   aws ec2 delete-nat-gateway --nat-gateway-id $NAT_GW_ID
   
   # Release Elastic IP
   aws ec2 release-address --allocation-id $EIP_ALLOC_ID
   ```

2. **Recreate when needed** (takes 2-3 minutes)

3. **Alternative**: Use EC2 instance as NAT (cheaper but more complex)

### For Production:

- Keep NAT Gateway (reliability is worth the cost)
- Consider NAT Gateway per AZ for high availability (doubles cost)

---

## What's Next?

After completing Phase 2, you're ready for:

**Phase 3: RDS PostgreSQL Database**
- Create DB subnet group
- Launch RDS instance
- Initialize database schema
- Store credentials in Secrets Manager

**Estimated time for Phase 3**: 2-3 hours

---

## Quick Reference Commands

```bash
# View all VPC resources
aws ec2 describe-vpcs --vpc-ids $VPC_ID
aws ec2 describe-subnets --filters "Name=vpc-id,Values=$VPC_ID"
aws ec2 describe-route-tables --filters "Name=vpc-id,Values=$VPC_ID"
aws ec2 describe-security-groups --filters "Name=vpc-id,Values=$VPC_ID"
aws ec2 describe-internet-gateways --filters "Name=attachment.vpc-id,Values=$VPC_ID"
aws ec2 describe-nat-gateways --filter "Name=vpc-id,Values=$VPC_ID"

# Delete all resources (in reverse order, for cleanup if needed)
# WARNING: Only run if you want to start over!
# aws ec2 delete-security-group --group-id $DB_SG_ID
# aws ec2 delete-security-group --group-id $BACKEND_SG_ID
# aws ec2 delete-security-group --group-id $ALB_SG_ID
# aws ec2 delete-nat-gateway --nat-gateway-id $NAT_GW_ID
# aws ec2 delete-route-table --route-table-id $PUBLIC_RT_ID
# aws ec2 delete-route-table --route-table-id $PRIVATE_RT_ID
# aws ec2 delete-subnet --subnet-id $PUBLIC_SUBNET_1
# aws ec2 delete-subnet --subnet-id $PUBLIC_SUBNET_2
# aws ec2 delete-subnet --subnet-id $PRIVATE_SUBNET_1
# aws ec2 delete-subnet --subnet-id $PRIVATE_SUBNET_2
# aws ec2 detach-internet-gateway --internet-gateway-id $IGW_ID --vpc-id $VPC_ID
# aws ec2 delete-internet-gateway --internet-gateway-id $IGW_ID
# aws ec2 delete-vpc --vpc-id $VPC_ID
```

---

**Phase 2 Status**: ⬜ Not Started → Mark as ✅ Complete when done

**Ready to begin?** Start with Step 1: Create VPC
