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
- Status: Deleted (will recreate when needed)
- Note: Deleted to save costs (~$32/month). Will recreate in later phases when private subnet internet access is required.

### Route Tables
- Public RT: rtb-07193bd0bc57c946b
  - Routes: 0.0.0.0/0 → Internet Gateway
  - Associations: Public Subnet 1, Public Subnet 2
  
- Private RT: rtb-09b52332e1238780c
  - Routes: 0.0.0.0/0 → Internet Gateway (converted to public for RDS accessibility)
  - Associations: Private Subnet 1, Private Subnet 2
  - Note: Previously had NAT Gateway route (blackhole). Now uses IGW for internet access.

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

## Total AWS Costs (Phases 1-3)
- Phase 1 (IAM, Billing): $0/month
- Phase 2 (VPC, Networking): $0/month
- Phase 3 (RDS Database): ~$15.30/month
**Grand Total**: ~$15.30/month
- NAT Gateway: Deleted to save costs
**Total**: $0/month (Phase 2 infrastructure only)

## Phase 4 ECR
 Information to add to aws-resources.md:
 - Backend ECR Repository: taskapp-backend
 - Backend URI: 858448674350.dkr.ecr.us-east-1.amazonaws.com/taskapp-backend
 - Frontend ECR Repository: taskapp-frontend  
 - Frontend URI: 858448674350.dkr.ecr.us-east-1.amazonaws.com/taskapp-frontend
 - Images: latest, v1.0.0