# AWS Resources

## Account Information
- Account ID: 858448674350 
- IAM User: taskapp-admin
- Region: us-east-1

## Access
- Console URL: https://858448674350.signin.aws.amazon.com/console
- MFA: Enabled
- Access Keys: Created and configured

## Billing
- Budget: $10/month
- Alert Threshold: 80% ($8)
- Billing alerts: Enabled

## Next Steps
- Ready for Phase 2: VPC and networking setup
## Phase 2: Network Infrastructure

### VPC
- VPC ID: vpc-016004b6f25f26302
- CIDR Block: 10.0.0.0/16
- DNS Hostnames: Enabled
- DNS Resolution: Enabled

### Internet Gateway
- IGW ID: igw-051694bb6c0f6612f
- State: Attached to VPC

### Subnets
- Public Subnet 1: subnet-0aee84b90626ffe46 (10.0.1.0/24, us-east-1a)
- Public Subnet 2: subnet-0be6223f381db982f (10.0.2.0/24, us-east-1b)
- Private Subnet 1: subnet-0681cafcc954cd8a6 (10.0.3.0/24, us-east-1a)
- Private Subnet 2: subnet-04f1cbee6ad2f9d17 (10.0.4.0/24, us-east-1b)

### NAT Gateway
- NAT Gateway ID: Created in Phase 5
- Elastic IP: Allocated in Phase 5
- Location: Public Subnet 1 (subnet-0aee84b90626ffe46, us-east-1a)
- State: Available
- Status: Recreated in Phase 5 for production-ready ECS deployment
- Cost: ~$32/month (0.045/hour + $0.045/GB data processed)

### Route Tables
- Public RT: rtb-07193bd0bc57c946b
  - Routes: 0.0.0.0/0 → Internet Gateway
  - Associations: Public Subnet 1, Public Subnet 2
  
- Private RT: rtb-09b52332e1238780c
  - Routes: 0.0.0.0/0 → NAT Gateway (recreated in Phase 5)
  - Associations: Private Subnet 1, Private Subnet 2
  - Note: Production-ready configuration - private subnets use NAT for outbound internet only

### Security Groups
- Database SG: sg-0c57afe621eb3932d (TaskApp-Database-SG)
  - Inbound: Port 5432 from VPC (10.0.0.0/16)
  - Inbound: Port 5432 from your IP (24.157.119.12/32) - for management
  - Inbound: All ports from 0.0.0.0/0 - ⚠️ TO BE REMOVED (overly permissive)
  
- Backend SG: sg-01e0fb4d04d2a2234
  - Inbound: Port 5000 from ALB SG
  
- Load Balancer SG: sg-0ca03625756c71a66
  - Inbound: Port 80 from 0.0.0.0/0
  - Inbound: Port 443 from 0.0.0.0/0

### Cost Estimate (Phase 2)
- VPC, Subnets, Route Tables, Security Groups: Free
- Internet Gateway: Free

---

## Phase 3: RDS Database

### Database Instance
- Instance ID: taskapp-db
- Instance Class: db.t3.micro
- Engine: PostgreSQL 14.13
- Storage: 20 GB (gp2)
- Multi-AZ: No
- Publicly Accessible: Yes
- Endpoint: taskapp-db.cqaewjp43tdm.us-east-1.rds.amazonaws.com:5432
- Status: Available

### Database Configuration
- Database Name: taskmanagement
- Master Username: postgres
- Master Password: Stored in `.env.aws` (gitignored)
- Port: 5432
- Parameter Group: default.postgres14
- Option Group: default:postgres-14

### DB Subnet Groups
- Primary: taskapp-db-subnet-group
  - Subnets: subnet-0681cafcc954cd8a6 (us-east-1a), subnet-04f1cbee6ad2f9d17 (us-east-1b)
  - Status: Active (currently in use)
  
- Alternative: taskapp-db-public-subnet-group
  - Subnets: subnet-0aee84b90626ffe46 (us-east-1a), subnet-0be6223f381db982f (us-east-1b)
  - Status: Created but not in use
  - Note: Cannot change subnet group of existing RDS instance

### Database Schema
- Tables: 7 (users, projects, tasks, project_members, comments, attachments, activity_log)
- Extensions: uuid-ossp
- Custom Types: user_role, task_status, task_priority, project_status
- Triggers: Auto-update timestamps on users, projects, tasks, comments

### Demo Data
- Admin User: admin@taskapp.com (password: admin123)
- Manager User: john@taskapp.com (password: admin123)
- Member User: jane@taskapp.com (password: admin123)

### Backups
- Automated Backups: Enabled
- Backup Retention: 7 days
- Backup Window: 03:00-04:00 UTC
- Maintenance Window: Mon 04:00-05:00 UTC

### Security
- VPC Security Group: sg-0c57afe621eb3932d
- Encryption at Rest: Not enabled (can enable for production)
- Encryption in Transit: SSL/TLS enabled
- IAM Authentication: Not enabled

### Connection String
```
DATABASE_URL=postgresql://postgres:PASSWORD@taskapp-db.cqaewjp43tdm.us-east-1.rds.amazonaws.com:5432/taskmanagement
```
- Stored in: `.env.aws` (gitignored)
- Tested: ✅ Successfully connected from local and backend

### Cost Estimate (Phase 3)
- db.t3.micro instance: ~$12.00/month
- 20 GB gp2 storage: ~$2.30/month
- Backup storage (7 days): ~$1.00/month
**Total**: ~$15.30/month

### Important Notes
- ⚠️ RDS is in "private" subnets but route table now has IGW route (effectively public)
- ⚠️ Security group has overly permissive rule (all ports from anywhere) - needs cleanup
- ✅ Database initialized with full schema and demo users
- ✅ Connection tested and verified working
- 🔐 Credentials stored securely in `.env.aws` (gitignored)

### Next Steps
1. Remove overly permissive security group rule
2. Restrict database access to backend security group only
3. Consider enabling encryption for production
4. Set up automated database backups to S3
5. Deploy backend application to connect to RDS

---

---

## Total AWS Costs Summary

### By Phase
- Phase 1 (Account, IAM, Billing): $0/month
- Phase 2 (VPC, Networking): $0/month (infrastructure only)
- Phase 3 (RDS Database): ~$15.30/month
- Phase 4 (ECR): <$1/month
- Phase 5 (ECS + ALB + NAT): ~$68/month

### Grand Total: ~$84/month

### Cost Breakdown
- RDS (db.t3.micro): ~$15.30/month
- ALB: ~$16.20/month
- ECS Fargate (2 tasks): ~$18/month
- NAT Gateway: ~$33/month
- CloudWatch Logs: ~$0.50/month
- ECR Storage: <$1/month

### Cost Optimization Options
- Reduce ECS tasks from 2 to 1: Save ~$9/month
- Delete NAT Gateway when not deploying: Save ~$33/month
- Stop ECS service when testing: Save ~$18/month + ALB costs
- Use smaller RDS instance: Limited options on free tier

### Production vs Development Costs
- **Full Production** (24/7): ~$84/month
- **Development** (stop services when not testing): ~$16/month (RDS + ECR only)
- **Completely Stopped**: $0/month (delete all resources, redeploy via IaC)

---

## Deployment Status

### Completed Phases
- ✅ Phase 1: AWS Account Setup
- ✅ Phase 2: VPC & Networking
- ✅ Phase 3: RDS Database
- ✅ Phase 4: ECR Container Registry
- ✅ Phase 5: Backend Deployment (ECS Fargate)

### Current State
- Backend API: **LIVE** at http://taskapp-alb-1878540875.us-east-1.elb.amazonaws.com/
- Database: **ACTIVE** with schema and demo data
- Container Images: **PUSHED** to ECR
- Infrastructure: **PRODUCTION-READY** with NAT Gateway security

### Next Phase
- 🔄 Phase 6: Frontend Deployment (S3 + CloudFront)

## Phase 4: ECR Container Registry

### Backend Repository
- Repository Name: taskapp-backend
- Repository URI: 858448674350.dkr.ecr.us-east-1.amazonaws.com/taskapp-backend
- Images: latest, v1.0.0
- Status: Active

### Frontend Repository
- Repository Name: taskapp-frontend
- Repository URI: 858448674350.dkr.ecr.us-east-1.amazonaws.com/taskapp-frontend
- Images: latest, v1.0.0
- Status: Active

### Cost Estimate (Phase 4)
- Storage: First 500 MB/month free, then $0.10/GB/month
- Data Transfer: Standard AWS data transfer rates
**Estimated**: <$1/month

---

## Phase 5: Backend Deployment (ECS Fargate)

### ECS Cluster
- Cluster Name: taskapp-cluster
- Launch Type: AWS Fargate (serverless)
- Region: us-east-1
- Status: Active

### CloudWatch Logs
- Log Group: /ecs/taskapp-backend
- Retention: 7 days
- Region: us-east-1
- ARN: arn:aws:logs:us-east-1:858448674350:log-group:/ecs/taskapp-backend

### IAM Roles
- Execution Role: taskapp-ecs-execution-role
  - Policy: AmazonECSTaskExecutionRolePolicy
  - Purpose: Pull ECR images, write CloudWatch logs
  - ARN: arn:aws:iam::858448674350:role/taskapp-ecs-execution-role

### Application Load Balancer
- Name: taskapp-alb
- DNS: taskapp-alb-1878540875.us-east-1.elb.amazonaws.com
- Scheme: Internet-facing
- Type: Application Load Balancer
- Subnets: Public Subnet 1 (us-east-1a), Public Subnet 2 (us-east-1b)
- Security Group: sg-0ca03625756c71a66 (TaskApp-ALB-SG)
- State: Active

### Target Group
- Name: taskapp-backend-tg
- Protocol: HTTP
- Port: 5000
- Target Type: IP addresses (Fargate)
- VPC: vpc-016004b6f25f26302
- Health Check:
  - Path: /
  - Protocol: HTTP
  - Interval: 30 seconds
  - Timeout: 5 seconds
  - Healthy Threshold: 2
  - Unhealthy Threshold: 2
  - Success Codes: 200
- Registered Targets: 2 (both healthy)
  - 10.0.3.41:5000 (us-east-1a) - healthy
  - 10.0.4.252:5000 (us-east-1b) - healthy

### ALB Listener
- Protocol: HTTP
- Port: 80
- Default Action: Forward to taskapp-backend-tg

### Task Definition
- Family: taskapp-backend
- Revision: 1
- Launch Type: Fargate
- Network Mode: awsvpc
- CPU: 0.25 vCPU (256)
- Memory: 0.5 GB (512)
- Execution Role: taskapp-ecs-execution-role

**Container Configuration:**
- Name: backend
- Image: 858448674350.dkr.ecr.us-east-1.amazonaws.com/taskapp-backend:latest
- Port Mapping: 5000:5000 (HTTP)
- Essential: Yes

**Environment Variables:**
- FLASK_ENV: production
- DEBUG: False
- SECRET_KEY: [Configured]
- JWT_SECRET_KEY: [Configured]
- DATABASE_URL: postgresql://postgres:***@taskapp-db.cqaewjp43tdm.us-east-1.rds.amazonaws.com:5432/taskmanagement
- CORS_ORIGINS: *
- JWT_ACCESS_TOKEN_EXPIRES: 24

**Logging:**
- Driver: awslogs
- Log Group: /ecs/taskapp-backend
- Region: us-east-1
- Stream Prefix: ecs

### ECS Service
- Service Name: taskapp-backend-service
- Cluster: taskapp-cluster
- Task Definition: taskapp-backend:1
- Desired Count: 2
- Running Count: 2
- Launch Type: Fargate
- Platform Version: LATEST
- Status: ACTIVE
- Deployment Status: COMPLETED

**Network Configuration:**
- VPC: vpc-016004b6f25f26302
- Subnets: Private Subnet 1 (subnet-0681cafcc954cd8a6), Private Subnet 2 (subnet-04f1cbee6ad2f9d17)
- Security Group: sg-01e0fb4d04d2a2234 (TaskApp-Backend-SG)
- Public IP: DISABLED (uses NAT Gateway for outbound)

**Load Balancer Integration:**
- Load Balancer: taskapp-alb
- Target Group: taskapp-backend-tg
- Container: backend:5000
- Health Check Grace Period: 0 seconds

### Deployment Verification
- ✅ Service Status: ACTIVE
- ✅ Tasks: 2/2 RUNNING
- ✅ Target Health: 2/2 healthy
- ✅ API Endpoint: http://taskapp-alb-1878540875.us-east-1.elb.amazonaws.com/
- ✅ Health Checks: Passing (200 status)
- ✅ CloudWatch Logs: Active
- ✅ Database Connectivity: Verified

### API Endpoints (Live)
- Base URL: http://taskapp-alb-1878540875.us-east-1.elb.amazonaws.com
- Auth: /api/auth
- Projects: /api/projects
- Tasks: /api/tasks
- Users: /api/users

### Cost Estimate (Phase 5)
- ALB: ~$16.20/month (720 hours)
- ECS Fargate (2 tasks):
  - vCPU: 2 × 0.25 × $0.04048/hour × 730 hours = ~$14.75/month
  - Memory: 2 × 0.5 GB × $0.004445/GB/hour × 730 hours = ~$3.25/month
- CloudWatch Logs: ~$0.50/month (1 GB)
- NAT Gateway: ~$32.85/month (0.045/hour × 730 hours)
- NAT Data Processing: ~$0.50/month (estimated)
**Total Phase 5**: ~$68/month

### Architecture Flow
```
Internet → ALB (Public Subnets, Port 80)
              ↓
          ECS Tasks (Private Subnets, Port 5000)
              ↓
          RDS Database (Private Subnets, Port 5432)
              ↓
          NAT Gateway (Outbound Internet for ECR pulls)
```

### Next Steps
- Phase 6: Frontend deployment (S3 + CloudFront)
- Update CORS_ORIGINS with actual frontend URL
- Consider SSL/TLS certificate (AWS Certificate Manager)
- Set up custom domain name (Route 53)