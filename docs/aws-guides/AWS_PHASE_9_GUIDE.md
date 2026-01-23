# AWS Phase 9: Terraform Infrastructure as Code

## Overview
Convert your manually created AWS infrastructure to Terraform code. This allows you to version control your infrastructure, replicate environments easily, and manage resources as code.

**Timeline**: 6-8 hours (spread over 2 days)
**Cost**: $0 (no additional resources, same infrastructure managed via Terraform)
**Prerequisites**: Phase 8 complete (Infrastructure running and monitored)

---

## 📋 Phase 9 Checklist

### Step 1: Install and Configure Terraform
- [ ] Install Terraform CLI
- [ ] Verify Terraform installation
- [ ] Create Terraform project structure
- [ ] Configure AWS provider

### Step 2: Import Existing Infrastructure State
- [ ] Import VPC
- [ ] Import Subnets (4 subnets)
- [ ] Import Internet Gateway
- [ ] Import NAT Gateway
- [ ] Import Route Tables
- [ ] Import Security Groups
- [ ] Import RDS instance
- [ ] Import ECR repositories (2)
- [ ] Import ECS cluster
- [ ] Import ECS task definitions (2)
- [ ] Import ECS services (2)
- [ ] Import Target Groups (2)
- [ ] Import ALB and listeners
- [ ] Import Route 53 records
- [ ] Import CloudWatch alarms (6)
- [ ] Import SNS topic

### Step 3: Organize Terraform Code
- [ ] Separate resources into logical modules
- [ ] Create variables file
- [ ] Create outputs file
- [ ] Configure remote state storage (S3 + DynamoDB)
- [ ] Set up environment-specific variables

### Step 4: Validate and Test
- [ ] Run terraform plan (should show no changes)
- [ ] Verify state matches actual infrastructure
- [ ] Test making a minor change
- [ ] Document Terraform workflow

---

## 🎯 What You'll Achieve

**Before Phase 9:**
- Infrastructure created manually via AWS Console/CLI
- No version control for infrastructure
- Difficult to replicate or modify
- No infrastructure documentation as code

**After Phase 9:**
- Infrastructure defined as code (version controlled)
- Can recreate entire environment with one command
- Team can review infrastructure changes via pull requests
- Infrastructure serves as its own documentation
- Can easily spin up dev/staging/prod environments

---

## ⚠️ Important Considerations

### What is Terraform?
Terraform is an Infrastructure as Code (IaC) tool that lets you define cloud resources in declarative configuration files. Instead of clicking through the AWS Console, you write code that describes what you want, and Terraform creates it.

### Why Use Terraform?
1. **Version Control**: Infrastructure changes tracked in Git
2. **Reproducibility**: Recreate identical environments
3. **Documentation**: Code is the documentation
4. **Collaboration**: Team reviews via pull requests
5. **Safety**: Preview changes before applying
6. **Multi-cloud**: Works with AWS, Azure, GCP, etc.

### Should You Do This Phase?

**Skip Phase 9 if:**
- This is a one-time deployment
- You don't need to recreate the infrastructure
- You're just learning AWS basics
- You prefer manual Console management

**Do Phase 9 if:**
- You want to version control infrastructure
- You need dev/staging/prod environments
- You're working in a team
- You want professional DevOps practices
- You plan to maintain this long-term

### Alternative Approach
Instead of importing existing infrastructure, you could:
1. Write Terraform code from scratch
2. Deploy to a new AWS account/region
3. Migrate traffic once validated
4. Destroy old manual infrastructure

This guide uses **import** to preserve your existing resources.

---

## 📦 Step 1: Install Terraform

### Windows Installation

**Option 1: Chocolatey (Recommended)**
```bash
choco install terraform
```

**Option 2: Manual Download**
1. Visit https://www.terraform.io/downloads
2. Download Windows AMD64 zip
3. Extract to `C:\terraform`
4. Add to PATH: System Properties → Environment Variables → Path → Add `C:\terraform`

**Verify Installation:**
```bash
terraform version
```

Expected output:
```
Terraform v1.7.0
on windows_amd64
```

---

## 📁 Step 2: Create Terraform Project Structure

### Create Directory Structure
```bash
cd /c/Users/vokeo/OneDrive/Desktop/task-management-app
mkdir -p terraform/{modules/{vpc,rds,ecs,alb,monitoring},environments/production}
```

### Directory Layout
```
terraform/
├── main.tf                    # Root module
├── variables.tf               # Input variables
├── outputs.tf                 # Output values
├── terraform.tfvars           # Variable values
├── backend.tf                 # Remote state config
├── provider.tf                # AWS provider config
├── modules/
│   ├── vpc/                   # VPC module
│   │   ├── main.tf
│   │   ├── variables.tf
│   │   └── outputs.tf
│   ├── rds/                   # Database module
│   │   ├── main.tf
│   │   ├── variables.tf
│   │   └── outputs.tf
│   ├── ecs/                   # ECS module
│   │   ├── main.tf
│   │   ├── variables.tf
│   │   └── outputs.tf
│   ├── alb/                   # Load balancer module
│   │   ├── main.tf
│   │   ├── variables.tf
│   │   └── outputs.tf
│   └── monitoring/            # CloudWatch module
│       ├── main.tf
│       ├── variables.tf
│       └── outputs.tf
└── environments/
    └── production/
        ├── main.tf            # Production environment
        └── terraform.tfvars   # Production variables
```

---

## 🔧 Step 3: Configure AWS Provider

### Create `terraform/provider.tf`
```hcl
terraform {
  required_version = ">= 1.7.0"
  
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = var.aws_region
  
  default_tags {
    tags = {
      Project     = "TaskManagementApp"
      Environment = var.environment
      ManagedBy   = "Terraform"
    }
  }
}
```

### Create `terraform/variables.tf`
```hcl
variable "aws_region" {
  description = "AWS region for resources"
  type        = string
  default     = "us-east-1"
}

variable "environment" {
  description = "Environment name"
  type        = string
  default     = "production"
}

variable "project_name" {
  description = "Project name for resource naming"
  type        = string
  default     = "taskapp"
}
```

### Create `terraform/terraform.tfvars`
```hcl
aws_region   = "us-east-1"
environment  = "production"
project_name = "taskapp"
```

### Initialize Terraform
```bash
cd terraform
terraform init
```

Expected output:
```
Terraform has been successfully initialized!
```

---

## 📥 Step 4: Import VPC Resources

### Create `terraform/modules/vpc/main.tf`
```hcl
# VPC
resource "aws_vpc" "main" {
  cidr_block           = "10.0.0.0/16"
  enable_dns_hostnames = true
  enable_dns_support   = true

  tags = {
    Name = "${var.project_name}-vpc"
  }
}

# Internet Gateway
resource "aws_internet_gateway" "main" {
  vpc_id = aws_vpc.main.id

  tags = {
    Name = "${var.project_name}-igw"
  }
}

# Public Subnets
resource "aws_subnet" "public" {
  count             = 2
  vpc_id            = aws_vpc.main.id
  cidr_block        = cidrsubnet(var.vpc_cidr, 8, count.index + 1)
  availability_zone = data.aws_availability_zones.available.names[count.index]

  map_public_ip_on_launch = true

  tags = {
    Name = "${var.project_name}-public-${count.index + 1}"
  }
}

# Private Subnets
resource "aws_subnet" "private" {
  count             = 2
  vpc_id            = aws_vpc.main.id
  cidr_block        = cidrsubnet(var.vpc_cidr, 8, count.index + 3)
  availability_zone = data.aws_availability_zones.available.names[count.index]

  tags = {
    Name = "${var.project_name}-private-${count.index + 1}"
  }
}

# Elastic IP for NAT Gateway
resource "aws_eip" "nat" {
  domain = "vpc"

  tags = {
    Name = "${var.project_name}-nat-eip"
  }
}

# NAT Gateway
resource "aws_nat_gateway" "main" {
  allocation_id = aws_eip.nat.id
  subnet_id     = aws_subnet.public[0].id

  tags = {
    Name = "${var.project_name}-nat"
  }
}

# Public Route Table
resource "aws_route_table" "public" {
  vpc_id = aws_vpc.main.id

  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.main.id
  }

  tags = {
    Name = "${var.project_name}-public-rt"
  }
}

# Private Route Table
resource "aws_route_table" "private" {
  vpc_id = aws_vpc.main.id

  route {
    cidr_block     = "0.0.0.0/0"
    nat_gateway_id = aws_nat_gateway.main.id
  }

  tags = {
    Name = "${var.project_name}-private-rt"
  }
}

# Route Table Associations - Public
resource "aws_route_table_association" "public" {
  count          = 2
  subnet_id      = aws_subnet.public[count.index].id
  route_table_id = aws_route_table.public.id
}

# Route Table Associations - Private
resource "aws_route_table_association" "private" {
  count          = 2
  subnet_id      = aws_subnet.private[count.index].id
  route_table_id = aws_route_table.private.id
}

# Data source for availability zones
data "aws_availability_zones" "available" {
  state = "available"
}
```

### Get Existing Resource IDs
```bash
# Get VPC ID
aws ec2 describe-vpcs --filters "Name=tag:Name,Values=taskapp-vpc" --query 'Vpcs[0].VpcId' --output text

# Get Subnet IDs
aws ec2 describe-subnets --filters "Name=tag:Name,Values=taskapp-public-1" --query 'Subnets[0].SubnetId' --output text
aws ec2 describe-subnets --filters "Name=tag:Name,Values=taskapp-public-2" --query 'Subnets[0].SubnetId' --output text
aws ec2 describe-subnets --filters "Name=tag:Name,Values=taskapp-private-1" --query 'Subnets[0].SubnetId' --output text
aws ec2 describe-subnets --filters "Name=tag:Name,Values=taskapp-private-2" --query 'Subnets[0].SubnetId' --output text

# Get Internet Gateway ID
aws ec2 describe-internet-gateways --filters "Name=tag:Name,Values=taskapp-igw" --query 'InternetGateways[0].InternetGatewayId' --output text

# Get NAT Gateway ID
aws ec2 describe-nat-gateways --filter "Name=tag:Name,Values=taskapp-nat" --query 'NatGateways[0].NatGatewayId' --output text

# Get Route Table IDs
aws ec2 describe-route-tables --filters "Name=tag:Name,Values=taskapp-public-rt" --query 'RouteTables[0].RouteTableId' --output text
aws ec2 describe-route-tables --filters "Name=tag:Name,Values=taskapp-private-rt" --query 'RouteTables[0].RouteTableId' --output text
```

### Import VPC Resources
```bash
# Replace <VPC_ID> with actual IDs from above commands
terraform import module.vpc.aws_vpc.main <VPC_ID>
terraform import module.vpc.aws_internet_gateway.main <IGW_ID>
terraform import module.vpc.aws_subnet.public[0] <PUBLIC_SUBNET_1_ID>
terraform import module.vpc.aws_subnet.public[1] <PUBLIC_SUBNET_2_ID>
terraform import module.vpc.aws_subnet.private[0] <PRIVATE_SUBNET_1_ID>
terraform import module.vpc.aws_subnet.private[1] <PRIVATE_SUBNET_2_ID>
terraform import module.vpc.aws_nat_gateway.main <NAT_GW_ID>
terraform import module.vpc.aws_route_table.public <PUBLIC_RT_ID>
terraform import module.vpc.aws_route_table.private <PRIVATE_RT_ID>
```

---

## 🗄️ Step 5: Set Up Remote State Storage

Terraform state should be stored remotely for team collaboration and safety.

### Create S3 Bucket for State
```bash
aws s3api create-bucket \
  --bucket taskapp-terraform-state-$(aws sts get-caller-identity --query Account --output text) \
  --region us-east-1

# Enable versioning (recover from accidents)
aws s3api put-bucket-versioning \
  --bucket taskapp-terraform-state-$(aws sts get-caller-identity --query Account --output text) \
  --versioning-configuration Status=Enabled

# Enable encryption
aws s3api put-bucket-encryption \
  --bucket taskapp-terraform-state-$(aws sts get-caller-identity --query Account --output text) \
  --server-side-encryption-configuration '{
    "Rules": [{
      "ApplyServerSideEncryptionByDefault": {
        "SSEAlgorithm": "AES256"
      }
    }]
  }'
```

### Create DynamoDB Table for State Locking
```bash
aws dynamodb create-table \
  --table-name taskapp-terraform-locks \
  --attribute-definitions AttributeName=LockID,AttributeType=S \
  --key-schema AttributeName=LockID,KeyType=HASH \
  --billing-mode PAY_PER_REQUEST \
  --region us-east-1
```

### Create `terraform/backend.tf`
```hcl
terraform {
  backend "s3" {
    bucket         = "taskapp-terraform-state-858448674350"  # Replace with your account ID
    key            = "production/terraform.tfstate"
    region         = "us-east-1"
    encrypt        = true
    dynamodb_table = "taskapp-terraform-locks"
  }
}
```

### Migrate State to S3
```bash
terraform init -migrate-state
```

---

## 📊 Step 6: Import Security Groups

### Get Security Group IDs
```bash
# ALB Security Group
aws ec2 describe-security-groups --filters "Name=group-name,Values=taskapp-alb-sg" --query 'SecurityGroups[0].GroupId' --output text

# ECS Tasks Security Group
aws ec2 describe-security-groups --filters "Name=group-name,Values=taskapp-ecs-tasks-sg" --query 'SecurityGroups[0].GroupId' --output text

# RDS Security Group
aws ec2 describe-security-groups --filters "Name=group-name,Values=taskapp-rds-sg" --query 'SecurityGroups[0].GroupId' --output text
```

### Create `terraform/modules/security/main.tf`
```hcl
# ALB Security Group
resource "aws_security_group" "alb" {
  name        = "${var.project_name}-alb-sg"
  description = "Security group for ALB"
  vpc_id      = var.vpc_id

  ingress {
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
    description = "HTTP from anywhere"
  }

  ingress {
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
    description = "HTTPS from anywhere"
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
    description = "Allow all outbound"
  }

  tags = {
    Name = "${var.project_name}-alb-sg"
  }
}

# ECS Tasks Security Group
resource "aws_security_group" "ecs_tasks" {
  name        = "${var.project_name}-ecs-tasks-sg"
  description = "Security group for ECS tasks"
  vpc_id      = var.vpc_id

  ingress {
    from_port       = 0
    to_port         = 65535
    protocol        = "tcp"
    security_groups = [aws_security_group.alb.id]
    description     = "Allow traffic from ALB"
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
    description = "Allow all outbound"
  }

  tags = {
    Name = "${var.project_name}-ecs-tasks-sg"
  }
}

# RDS Security Group
resource "aws_security_group" "rds" {
  name        = "${var.project_name}-rds-sg"
  description = "Security group for RDS"
  vpc_id      = var.vpc_id

  ingress {
    from_port       = 5432
    to_port         = 5432
    protocol        = "tcp"
    security_groups = [aws_security_group.ecs_tasks.id]
    description     = "PostgreSQL from ECS tasks"
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
    description = "Allow all outbound"
  }

  tags = {
    Name = "${var.project_name}-rds-sg"
  }
}
```

### Import Security Groups
```bash
terraform import module.security.aws_security_group.alb <ALB_SG_ID>
terraform import module.security.aws_security_group.ecs_tasks <ECS_SG_ID>
terraform import module.security.aws_security_group.rds <RDS_SG_ID>
```

---

## 🎯 Step 7: Terraform Workflow

### Daily Workflow
```bash
# 1. Make changes to .tf files
vim terraform/main.tf

# 2. Format code
terraform fmt -recursive

# 3. Validate syntax
terraform validate

# 4. Preview changes
terraform plan

# 5. Apply changes (after review)
terraform apply

# 6. Commit to Git
git add terraform/
git commit -m "feat: add monitoring module"
git push
```

### Useful Commands
```bash
# Show current state
terraform show

# List resources in state
terraform state list

# Show specific resource
terraform state show aws_vpc.main

# View outputs
terraform output

# Destroy specific resource
terraform destroy -target=aws_instance.example

# Refresh state from AWS
terraform refresh

# Graph dependencies (requires graphviz)
terraform graph | dot -Tpng > graph.png
```

---

## ⚠️ Important Warnings

### State File Security
- **NEVER commit terraform.tfstate to Git** (contains secrets)
- Add to .gitignore: `*.tfstate`, `*.tfstate.*`
- Use remote state (S3) for team collaboration
- Enable versioning on S3 bucket for recovery

### Import Limitations
- Import doesn't import resource dependencies
- You must write the Terraform code to match existing resources
- State drift can occur if resources modified outside Terraform
- Always run `terraform plan` before `apply`

### Cost Considerations
- S3 state storage: ~$0.023/GB/month (pennies)
- DynamoDB state locking: Pay-per-request (pennies)
- No additional cost for Terraform itself (free tool)

---

## 📚 Next Steps After Phase 9

Once Terraform is managing your infrastructure:

1. **Create Development Environment**
   - Copy production module
   - Use smaller instance sizes
   - Single task counts
   - Save 50-70% on costs

2. **Implement GitOps Workflow**
   - Pull request reviews for infrastructure changes
   - CI/CD pipeline runs `terraform plan`
   - Manual approval before `terraform apply`

3. **Add Terraform Modules**
   - Reusable components
   - Shared across environments
   - Version controlled modules

4. **Enhance with Terragrunt** (Optional)
   - DRY (Don't Repeat Yourself) configurations
   - Easier multi-environment management
   - Remote state management

---

## 🆘 Troubleshooting

### "Resource already exists" Error
This means you're trying to create a resource that already exists. You need to import it:
```bash
terraform import aws_vpc.main vpc-xxxxx
```

### State Drift Detected
AWS resources modified outside Terraform:
```bash
# Refresh state to match reality
terraform refresh

# Or accept changes
terraform apply -refresh-only
```

### Can't Delete Resources
Terraform tracks dependencies. Use:
```bash
terraform state rm <resource>  # Remove from state without deleting
terraform destroy -target=<resource>  # Delete specific resource
```

### Import Errors
- Verify resource exists: `aws <service> describe-<resource>`
- Check resource ID format in Terraform docs
- Some resources can't be imported (recreate instead)

---

## 📖 Learning Resources

### Official Documentation
- Terraform Docs: https://www.terraform.io/docs
- AWS Provider: https://registry.terraform.io/providers/hashicorp/aws/latest/docs
- Terraform Import: https://www.terraform.io/docs/cli/import

### Tutorials
- HashiCorp Learn: https://learn.hashicorp.com/terraform
- AWS Terraform Workshop: https://aws-terraform-workshop.com
- Terraform Best Practices: https://www.terraform-best-practices.com

### Community
- Terraform Discuss: https://discuss.hashicorp.com/c/terraform-core
- Reddit: r/terraform
- Stack Overflow: [terraform] tag

---

## ✅ Phase 9 Completion Checklist

Before moving to Phase 10, verify:

- [ ] Terraform installed and working
- [ ] All existing resources imported into Terraform state
- [ ] `terraform plan` shows no changes (state matches reality)
- [ ] Remote state configured (S3 + DynamoDB)
- [ ] State file NOT in Git repository
- [ ] Documentation updated with Terraform commands
- [ ] Team knows Terraform workflow
- [ ] Successfully made and reverted a test change

---

## 🎓 Key Takeaways

**What You Learned:**
- Infrastructure as Code fundamentals
- Terraform syntax and workflow
- Importing existing infrastructure
- Remote state management
- Security best practices for state files

**Skills Gained:**
- Write declarative infrastructure code
- Version control infrastructure
- Preview changes before applying
- Collaborate on infrastructure via Git
- Manage multi-environment deployments

**Production Readiness:**
After Phase 9, your infrastructure is:
- ✅ Version controlled
- ✅ Reproducible
- ✅ Documented as code
- ✅ Team-collaborative
- ✅ Change-trackable

---

**Ready for Phase 10: CI/CD Pipeline Integration** 🚀
