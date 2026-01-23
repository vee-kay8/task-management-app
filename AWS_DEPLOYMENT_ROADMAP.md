# AWS Deployment Roadmap - Complete Guide

**Project**: Task Management Application Deployment to AWS
**Duration**: 3-4 weeks
**Status**: In Progress (11/12 phases complete - 92%)
**Live Application**: https://app.techveesolutions.com

---

## Overview

This document tracks the complete AWS deployment journey from account setup to production-ready infrastructure.

---

## Phase 1: AWS Account Setup & Prerequisites

**Timeline**: Day 1
**Status**: Completed

### Checklist
- [ ] Create AWS account (or verify existing)
- [ ] Set up billing alerts and budgets
- [ ] Create IAM user with admin access
- [ ] Configure MFA for root and IAM user
- [ ] Install AWS CLI
- [ ] Configure AWS credentials locally
- [ ] Choose deployment region
- [ ] Review AWS free tier limitations
- [ ] Create project structure for AWS files

### Deliverables
- AWS account ready
- AWS CLI configured and tested
- IAM user credentials stored securely
- Billing alerts active

### Documentation
- Account details
- Region selection rationale
- Security configuration notes

---

## Phase 2: Network Infrastructure (VPC Setup)

**Timeline**: Days 2-3
**Status**: Completed

### Checklist
- [ ] Create VPC (10.0.0.0/16 CIDR block)
- [ ] Enable DNS hostnames and resolution
- [ ] Create public subnet 1 (10.0.1.0/24, AZ: us-east-1a)
- [ ] Create public subnet 2 (10.0.2.0/24, AZ: us-east-1b)
- [ ] Create private subnet 1 (10.0.3.0/24, AZ: us-east-1a)
- [ ] Create private subnet 2 (10.0.4.0/24, AZ: us-east-1b)
- [ ] Create and attach Internet Gateway
- [ ] Create NAT Gateway (in public subnet 1)
- [ ] Create public route table
- [ ] Create private route table
- [ ] Associate subnets with route tables
- [ ] Create database security group
- [ ] Create backend security group
- [ ] Create frontend security group
- [ ] Create load balancer security group
- [ ] Document network architecture

### Deliverables
- Fully configured VPC
- 2 public subnets + 2 private subnets across 2 AZs
- Internet Gateway and NAT Gateway
- 4 security groups configured
- Network diagram

### Key Resources Created
- VPC ID: [To be filled]
- Internet Gateway ID: [To be filled]
- NAT Gateway ID: [To be filled]
- Public Subnet 1 ID: [To be filled]
- Public Subnet 2 ID: [To be filled]
- Private Subnet 1 ID: [To be filled]
- Private Subnet 2 ID: [To be filled]

---

## Phase 3: Database Layer (RDS PostgreSQL)

**Timeline**: Days 4-5
**Status**: ✅ Complete

### Checklist
- [ ] Create DB subnet group (private subnets)
- [ ] Generate strong master password
- [ ] Create RDS PostgreSQL instance
  - [ ] Engine: PostgreSQL 15
  - [ ] Instance class: db.t3.micro
  - [ ] Storage: 20GB SSD
  - [ ] VPC: Created VPC
  - [ ] Subnet group: DB subnet group
  - [ ] Security group: Database SG
  - [ ] Backup retention: 7 days
  - [ ] Encryption: Enabled
- [ ] Wait for RDS instance to be available
- [ ] Store credentials in AWS Secrets Manager
- [ ] Create bastion host or use Cloud9 for DB access
- [ ] Connect to RDS database
- [ ] Run schema initialization script
- [ ] Verify tables created (users, projects, tasks)
- [ ] Test database connectivity
- [ ] Document connection details

### Deliverables
- RDS PostgreSQL instance running
- Database schema initialized
- Connection string in Secrets Manager
- Database access documented

### Key Resources Created
- RDS Instance Identifier: [To be filled]
- Endpoint: [To be filled]
- Secret ARN: [To be filled]
- Database Name: taskapp

---

## Phase 4: Container Registry (ECR)

**Timeline**: Day 6
**Status**: ✅ Complete

### Checklist
- [ ] Create ECR repository for backend
- [ ] Create ECR repository for frontend
- [ ] Authenticate Docker to ECR
- [ ] Pull images from GHCR (or build locally)
- [ ] Tag images for ECR
- [ ] Push backend image to ECR
- [ ] Push frontend image to ECR
- [ ] Verify images in AWS console
- [ ] Enable image scanning (optional)
- [ ] Document image URIs

### Deliverables
- 2 ECR repositories created
- Docker images pushed successfully
- Image URIs saved

### Key Resources Created
- Backend ECR URI: [To be filled]
- Frontend ECR URI: [To be filled]

---

## Phase 5: Backend Deployment (ECS Fargate)

**Timeline**: Days 7-9
**Status**: ✅ Complete

### Checklist
- [x] Recreate NAT Gateway for production security
- [x] Create ECS cluster (Fargate)
- [x] Create CloudWatch log group for backend
- [x] Create task execution role
- [x] Create task role (skipped - not needed yet)
- [x] Create task definition (backend)
  - [x] Configure container (image, port, env vars)
  - [x] Set CPU and memory (0.25 vCPU, 0.5 GB)
  - [x] Add environment variables (7 total)
  - [x] Configure CloudWatch logs
- [x] Create Application Load Balancer
  - [x] Internet-facing, public subnets
  - [x] Security group configured
- [x] Create target group
  - [x] Type: IP
  - [x] Health check: / (root endpoint)
  - [x] Port: 5000
- [x] Configure ALB listener (HTTP:80)
- [x] Create ECS service
  - [x] Desired tasks: 2
  - [x] Launch type: Fargate
  - [x] Private subnets (production-ready)
  - [x] Public IP disabled (using NAT Gateway)
  - [x] Load balancer attached
- [x] Verify tasks running (2/2 RUNNING)
- [x] Verify target health (2/2 healthy)
- [x] Test backend API endpoint
- [x] Monitor CloudWatch logs

### Deliverables
- Backend running on ECS Fargate
- Load balancer distributing traffic
- 2 tasks for high availability
- Health checks passing

### Key Resources Created
- NAT Gateway: Recreated in public subnet 1
- ECS Cluster: taskapp-cluster
- CloudWatch Log Group: /ecs/taskapp-backend
- IAM Execution Role: taskapp-ecs-execution-role
- Task Definition: taskapp-backend:1
- Service Name: taskapp-backend-service
- ALB Name: taskapp-alb
- ALB DNS Name: taskapp-alb-1878540875.us-east-1.elb.amazonaws.com
- Target Group: taskapp-backend-tg
- Backend URL: http://taskapp-alb-1878540875.us-east-1.elb.amazonaws.com/

---

## Phase 6: Frontend Deployment (ECS Fargate)

**Timeline**: Days 10-11  
**Status**: ✅ Complete

### Checklist
- [x] Update frontend environment variable (API URL to ALB)
- [x] Update frontend API client to call real backend
- [x] Build frontend for production (standalone mode)
- [x] Build Docker image for frontend (with --build-arg)
- [x] Push frontend image to ECR
- [x] Create CloudWatch log group for frontend
- [x] Create frontend task definition (0.25 vCPU, 0.5 GB)
- [x] Create frontend target group (port 3000)
- [x] Configure ALB path-based routing
  - [x] /api/* → backend target group (Priority 1)
  - [x] /* → frontend target group (Default)
- [x] Create frontend ECS service (2 tasks)
- [x] Verify frontend tasks running (2/2 RUNNING)
- [x] Verify frontend target health (2/2 healthy)
- [x] Test frontend via ALB URL
- [x] Test full application flow
  - [x] Registration
  - [x] Login
  - [x] Create project
  - [x] Create tasks
  - [x] Drag and drop tasks
- [x] Verify API calls to backend working

### Deliverables
- Frontend deployed to ECS Fargate ✅
- Path-based routing on ALB ✅
- Full application working end-to-end ✅
- 2 frontend tasks for high availability ✅

### Key Resources Created
- CloudWatch Log Group: /ecs/taskapp-frontend
- Task Definition: taskapp-frontend:1
- Target Group: taskapp-frontend-tg (ARN: arn:aws:elasticloadbalancing:us-east-1:858448674350:targetgroup/taskapp-frontend-tg/bd88abf63d284380)
- Service Name: taskapp-frontend-service
- Frontend URL: http://taskapp-alb-1878540875.us-east-1.elb.amazonaws.com/
- ECR Image Digest: sha256:79f9d2ab47f0c15fd592de1f156c3a9cd7d1b61584ffbd9b68cbbab921098f6a

### Lessons Learned
- **Critical**: Next.js `NEXT_PUBLIC_*` environment variables are baked at BUILD time, not runtime
- **Solution**: Must use `docker build --build-arg NEXT_PUBLIC_API_URL=...` to properly configure API URL
- **Verification**: Always grep the built image to verify environment variables are correctly baked in
- **Health Checks**: Changed from `/` to `/api/health` for better reliability
- **Path Routing**: Backend must be Priority 1 (`/api/*`) so frontend default rule (`/*`) catches everything else

---

## Phase 7: Domain & SSL Configuration

**Timeline**: 2-3 hours
**Status**: ✅ Complete (100%)

### Checklist
- [x] Used existing domain (techveesolutions.com)
- [x] Verified existing SSL certificate in ACM
  - [x] Certificate: techveesolutions.com + *.techveesolutions.com (wildcard)
  - [x] Status: ISSUED
  - [x] ARN: arn:aws:acm:us-east-1:858448674350:certificate/095aa45c-e956-4590-b384-22eea11e5185
- [x] Add HTTPS listener to ALB (port 443)
- [x] Attach certificate to HTTPS listener
- [x] Configure path routing on HTTPS listener
  - [x] Priority 1: `/api/*` → backend target group
  - [x] Default: `/*` → frontend target group
- [x] Update HTTP listener to redirect to HTTPS (301)
- [x] Create Route53 A record (alias to ALB)
  - [x] A record: app.techveesolutions.com → ALB
- [x] Update backend CORS_ORIGINS environment variable
- [x] Redeploy backend with new CORS settings
- [x] Rebuild frontend with HTTPS URL
  - [x] Built with: `https://app.techveesolutions.com`
  - [x] Pushed to ECR (digest: sha256:9543e886741243b1312d3f556116bbe538e5a6480b546e2badf1041a99e8b02a)
- [x] Redeploy frontend with HTTPS-enabled image
- [x] Test `https://app.techveesolutions.com` loads frontend ✅
- [x] Verify SSL certificate in browser (green padlock) ✅
- [x] Test API calls over HTTPS (no mixed content) ✅
- [x] Test full application functionality ✅

### Deliverables
- ✅ Custom domain configured (app.techveesolutions.com)
- ✅ SSL/HTTPS working on ALB with existing certificate
- ✅ Professional URL operational
- ✅ HTTP to HTTPS redirect functional
- ✅ Frontend rebuilt with HTTPS API URL
- ✅ No mixed content errors
- ✅ Full application tested and working

### Key Resources Created
- Domain Name: app.techveesolutions.com
- Certificate ARN: arn:aws:acm:us-east-1:858448674350:certificate/095aa45c-e956-4590-b384-22eea11e5185
- HTTPS Listener: Created on ALB port 443
- Frontend Image: sha256:9543e886741243b1312d3f556116bbe538e5a6480b546e2badf1041a99e8b02a

### Lessons Learned
- **Existing Certificate**: Leveraged existing wildcard certificate (*.techveesolutions.com) saved time - no domain registration or certificate validation needed
- **Subdomain Strategy**: Using `app.techveesolutions.com` kept existing CloudFront setup untouched
- **Frontend Rebuild**: Had to rebuild frontend with `--build-arg NEXT_PUBLIC_API_URL=https://app.techveesolutions.com` to avoid mixed content errors
- **Same Issue as Phase 6**: Next.js environment variables must be baked at build time, not runtime

---

## Phase 8: Monitoring & Logging ✅

**Timeline**: Day 12 (Completed in 3 hours)
**Status**: ✅ Complete (100%)

### Checklist
- [x] Verify CloudWatch log groups created
- [x] Configure log retention (30 days)
- [x] Create SNS topic for alerts (taskapp-alerts)
- [x] Subscribe email to SNS topic (vokeogigbah@gmail.com)
- [x] Create CloudWatch alarms (6 alarms)
  - [x] Backend unhealthy targets
  - [x] Frontend unhealthy targets
  - [x] ALB 5xx errors (>10 in 5 min)
  - [x] RDS high CPU (>80%)
  - [x] RDS low storage (<2GB)
  - [x] ECS task failures
- [x] Create CloudWatch dashboard (taskapp-production)
  - [x] ALB request count
  - [x] Target response time
  - [x] ECS CPU utilization
  - [x] ECS memory utilization
  - [x] RDS database connections
  - [x] RDS CPU gauge
- [x] Create Log Insights saved queries (4 queries)
  - [x] Recent errors
  - [x] API response times
  - [x] Failed login attempts
  - [x] Slowest requests

### Deliverables
- ✅ Comprehensive monitoring dashboard (6 widgets)
- ✅ Critical alarms configured (6 alarms)
- ✅ Email notifications configured
- ✅ Log Insights queries saved (4 queries)
- ✅ 30-day log retention to control costs

### Key Resources Created
- **Dashboard**: taskapp-production (https://console.aws.amazon.com/cloudwatch/home?region=us-east-1#dashboards/dashboard/taskapp-production)
- **SNS Topic ARN**: arn:aws:sns:us-east-1:858448674350:taskapp-alerts
- **Email Subscription**: vokeogigbah@gmail.com
- **Alarms Created**: 6 (unhealthy targets, 5xx errors, RDS CPU/storage, task failures)
- **Log Groups**: /ecs/taskapp-backend, /ecs/taskapp-frontend (30-day retention)
- **Saved Queries**: 4 (errors, response times, failed logins, slow requests)

### Lessons Learned
- **Windows Git Bash**: AWS CLI commands with paths require `MSYS_NO_PATHCONV=1` prefix to prevent path conversion
- **CloudWatch Metrics**: Auto-detection works well without explicit dimensions for most AWS services
- **Cost Control**: 30-day log retention prevents unlimited storage costs (~$5-10/month total)
- **Dashboard Efficiency**: CLI creation faster than manual Console widget configuration

### Cost Impact
- **Monthly**: +$5-10 (CloudWatch Logs, metrics, alarms)
- **Total Running Cost**: ~$100-105/month

---

## Phase 9: Infrastructure as Code (Terraform)

**Timeline**: Days 16-18
**Status**: ✅ Complete

### Checklist
- [x] Install Terraform
- [x] Create terraform directory structure
- [x] Create provider.tf (AWS provider config)
- [x] Create variables.tf (input variables)
- [x] Create terraform.tfvars (variable values)
- [x] Create modules/vpc (VPC, subnets, gateways, routing)
- [x] Create modules/security (Security groups)
- [x] Create modules/rds (RDS instance and subnet group)
- [x] Create modules/ecr (ECR repositories)
- [x] Create modules/ecs (Cluster, task definitions, services)
- [x] Create modules/alb (Load balancer, target groups, listeners)
- [x] Create modules/route53 (DNS A record)
- [x] Create backend.tf (S3 + DynamoDB state management)
- [x] Run terraform init
- [x] Import existing VPC infrastructure (15 resources)
- [x] Import security groups (3 resources)
- [x] Import RDS database (2 resources)
- [x] Import ECR repositories (2 resources)
- [x] Import ECS cluster (1 resource)
- [x] Import ECS task definitions (2 resources)
- [x] Import ECS services (2 resources)
- [x] Import ALB components (6 resources)
- [x] Import Route 53 record (1 resource)
- [x] Run terraform plan (verify state matches)
- [x] Create .gitignore for Terraform
- [x] Document Terraform usage

### Deliverables
- Complete Terraform configuration (35 resources)
- Remote state backend (S3 + DynamoDB)
- All existing infrastructure imported
- Infrastructure as code documentation

### Key Resources Imported
- **VPC Module**: 15 resources (VPC, 4 subnets, IGW, NAT, EIP, 2 route tables, 4 associations)
- **Security Module**: 3 security groups (ALB, Backend, RDS)
- **RDS Module**: taskapp-db (db.t4g.micro, PostgreSQL 16.3), subnet group
- **ECR Module**: taskapp-backend, taskapp-frontend repositories
- **ECS Module**: taskapp-cluster, 2 task definitions, 2 services (4 tasks total)
- **ALB Module**: taskapp-alb, 2 target groups, 2 listeners, 1 listener rule
- **Route53 Module**: app.techveesolutions.com A record
- **State Backend**: S3 bucket (taskapp-terraform-state-858448674350), DynamoDB table (taskapp-terraform-locks)

### Files Created
- terraform/provider.tf
- terraform/variables.tf
- terraform/terraform.tfvars
- terraform/backend.tf
- terraform/main.tf
- terraform/.gitignore
- terraform/modules/vpc/ (main.tf, variables.tf, outputs.tf)
- terraform/modules/security/ (main.tf, variables.tf, outputs.tf)
- terraform/modules/rds/ (main.tf, variables.tf, outputs.tf)
- terraform/modules/ecr/ (main.tf, variables.tf, outputs.tf)
- terraform/modules/ecs/ (main.tf, variables.tf, outputs.tf)
- terraform/modules/alb/ (main.tf, variables.tf, outputs.tf)
- terraform/modules/route53/ (main.tf, variables.tf, outputs.tf)

### Lessons Learned
- **Import Strategy**: Module-by-module import prevents dependency confusion
- **Sensitive Variables**: Use TF_VAR_* environment variables for secrets (db_password, secret_key, jwt_secret_key)
- **State Backend**: Configure early to enable team collaboration
- **ECS Services**: deployment_configuration must use inline arguments, not nested blocks
- **Task Definitions**: Complex JSON structures imported successfully using jsonencode()
- **State Locking**: DynamoDB provides state locking for concurrent operations
- And 10+ more Terraform files

---

## Phase 10: CI/CD Integration

**Timeline**: Days 19-20
**Status**: ✅ Complete

### Checklist
- [x] Create IAM user for GitHub Actions (github-actions-ecs-deployer)
- [x] Create custom IAM policy for deployments (GitHubActionsECSDeployPolicy)
- [x] Generate access keys and store securely
- [x] Add AWS credentials to GitHub Secrets (11 secrets total)
  - [x] AWS_ACCESS_KEY_ID
  - [x] AWS_SECRET_ACCESS_KEY
  - [x] AWS_REGION
  - [x] ECR_BACKEND_REPOSITORY
  - [x] ECR_FRONTEND_REPOSITORY
  - [x] ECS_CLUSTER
  - [x] ECS_BACKEND_SERVICE
  - [x] ECS_FRONTEND_SERVICE
  - [x] DATABASE_URL (with SSL)
  - [x] SECRET_KEY
  - [x] JWT_SECRET_KEY
- [x] Create backend deployment workflow (.github/workflows/deploy-backend.yml)
- [x] Create frontend deployment workflow (.github/workflows/deploy-frontend.yml)
- [x] Configure workflows with proper triggers (push to main/Cloud-Deployment)
- [x] Add path filters (backend/** for backend, frontend/** for frontend)
- [x] Test backend deployment workflow (7 revisions deployed)
- [x] Test frontend deployment workflow (4 revisions deployed)
- [x] Fix task definition compatibility issues (enableFaultInjection)
- [x] Fix environment variable injection using jq
- [x] Verify automated deployments working
- [x] Test application after automated deployment
- [x] Document CI/CD pipeline

### Deliverables
- ✅ Automated deployment pipeline operational
- ✅ Push-to-deploy functionality working
- ✅ Zero manual deployment steps required
- ✅ Both backend and frontend auto-deploying
- ✅ Zero-downtime rolling deployments

### Key Resources Created
- IAM User: github-actions-ecs-deployer
- IAM Policy: GitHubActionsECSDeployPolicy
- GitHub Secrets: 11 configured
- Workflow Files: deploy-backend.yml, deploy-frontend.yml
- Task Definitions: Backend revision 7, Frontend revision 4

### Lessons Learned
- **Task Definition Compatibility**: AWS returns extra fields (enableFaultInjection, registeredAt, etc.) that must be removed before re-registration
- **Environment Variables**: amazon-ecs-render-task-definition action doesn't properly update environment variables; using jq directly is more reliable
- **Database Authentication**: RDS requires correct password and SSL mode (?sslmode=require) in connection string
- **Workflow Testing**: Test workflows with small README changes before actual code deployments
- **GitHub Secrets**: Must match exact values from .env.aws file for proper database connectivity

---

## Phase 11: Cost Optimization & Best Practices

**Timeline**: Days 21-22
**Status**: ✅ Completed (January 22, 2026)

### Checklist
- [x] Enable AWS Cost Explorer
- [x] Review cost breakdown by service
- [x] Identify optimization opportunities
- [x] Review ECS task sizing (backend and frontend)
- [x] Enable ECS auto-scaling (both services)
  - [x] Target tracking scaling (CPU 70%)
  - [x] Min tasks: 1, Max tasks: 4
  - [x] Scale-out cooldown: 60 seconds
  - [x] Scale-in cooldown: 300 seconds
- [x] Configure scheduled scaling
  - [x] Scale-down at 11 PM EST (Mon-Fri)
  - [x] Scale-up at 6 AM EST (Mon-Fri)
- [x] Create budget alerts
  - [x] Monthly budget: $100
  - [x] Alert at 80% actual spending
  - [x] Alert at 100% forecasted spending
- [x] Enable RDS storage auto-scaling (20 GB → 100 GB)
- [x] Configure ECR lifecycle policies (keep last 10 images)
- [x] Verify CloudWatch logs retention (30 days)
- [x] Document cost optimization steps
- [x] Validate all auto-scaling configurations

### Deliverables
- ✅ Cost optimization report (PHASE_11_COMPLETE.md)
- ✅ Auto-scaling configured (2 scalable targets, 2 policies, 4 scheduled actions)
- ✅ Budget monitoring active (TaskApp-Monthly-Budget)
- ✅ Infrastructure optimized (RDS auto-scaling, ECR cleanup)

### Achievements
- **Immediate Savings**: Services scaled from 2 → 1 tasks automatically
- **Cost Reduction**: 12% immediate ($12/month), up to 40% during low usage
- **Auto-Scaling Active**: CloudWatch alarms monitoring CPU, ready to scale 1-4 tasks
- **Budget Alerts**: Email notifications at 80% and 100% thresholds

### Estimated Monthly Costs
- ECS Fargate: [To be filled]
- RDS: [To be filled]
### Estimated Monthly Costs

| Resource | Cost |
|----------|------|
| RDS db.t3.micro | ~$15.30 |
| Application Load Balancer | ~$16.20 |
| NAT Gateway | ~$33.00 |
| Backend ECS (2 tasks) | ~$18.00 |
| Frontend ECS (2 tasks) | ~$9.75 |
| CloudWatch Logs | ~$1.00 |
| ECR Storage | <$1.00 |
| **Total** | **~$94/month** |

**Cost Optimization Options:**
- Reduce tasks from 2 to 1 per service: Save ~$14/month
- Stop services when not testing: Save ~$28/month
- Remove NAT Gateway when not deploying: Save ~$33/month
- Use t4g.micro RDS (ARM): Save ~$2/month

---

## Phase 12: Final Documentation & Handoff

**Timeline**: Days 23-25
**Status**: In Progress

### Checklist
- [ ] Create AWS architecture diagram
- [ ] Create network diagram
- [ ] Create data flow diagram
- [ ] Document all AWS resources created
- [ ] Create troubleshooting guide
- [ ] Document common issues and solutions
- [ ] Create cost breakdown spreadsheet
- [ ] Document lessons learned
- [ ] Note AWS-specific features used
- [ ] List challenges faced
- [ ] Document solutions implemented
- [ ] Create AWS deployment guide
- [ ] Take screenshots of AWS console
- [ ] Create comparison template for Azure/GCP
- [ ] Prepare for Azure deployment

### Deliverables
- Complete AWS documentation
- Architecture diagrams
- Cost analysis
- Lessons learned document
- Troubleshooting guide

---

## Progress Tracking

### Overall Status
- **Phases Completed**: 11/12
- **Days Elapsed**: 22/25
- **Progress**: 92%
- **Percentage Complete**: 92%

### Phase Status Summary
| Phase | Name | Status | Days | Completion |
|-------|------|--------|------|------------|
| 1 | Account Setup | ✅ Complete | 1 | 100% |
| 2 | VPC & Networking | ✅ Complete | 2-3 | 100% |
| 3 | RDS Database | ✅ Complete | 4-5 | 100% |
| 4 | ECR Registry | ✅ Complete | 6 | 100% |
| 5 | ECS Backend | ✅ Complete | 7-9 | 100% |
| 6 | ECS Frontend | ✅ Complete | 10-11 | 100% |
| 7 | Domain & SSL | ✅ Complete | 11 | 100% |
| 8 | Monitoring | ✅ Complete | 12 | 100% |
| 9 | Terraform IaC | ✅ Complete | 16-18 | 100% |
| 10 | CI/CD Integration | ✅ Complete | 19-20 | 100% |
| 11 | Cost Optimization | ✅ Complete | 21-22 | 100% |
| 12 | Documentation | 🔄 In Progress | 23-25 | 0% |

---

## Key Resources Reference

### Network Resources
- VPC ID: 
- Internet Gateway ID: 
- NAT Gateway ID: 
- Public Subnet 1 ID: 
- Public Subnet 2 ID: 
- Private Subnet 1 ID: 
- Private Subnet 2 ID: 

### Database Resources
- RDS Endpoint: 
- Secret ARN: 
- DB Subnet Group: 

### Container Resources
- ECR Backend URI: 
- ECR Frontend URI: 
- ECS Cluster: 
- Backend Service: 

### Load Balancing Resources
- ALB DNS Name: 
- Backend Target Group: 

### Frontend Resources
- Frontend Task Definition: taskapp-frontend:1
- Frontend Service: taskapp-frontend-service
- Frontend Target Group: taskapp-frontend-tg
- Frontend CloudWatch Log Group: /ecs/taskapp-frontend

### Domain & SSL
- Domain Name: 
- Hosted Zone ID: 
- Certificate ARN: 

---

## Notes & Observations

### Challenges Encountered
**Phase 6 - Frontend Deployment:**
- Next.js environment variables (`NEXT_PUBLIC_*`) are compiled into JavaScript at build time, not runtime
- Initial deployment showed localhost:5000 in browser because `--build-arg` wasn't used during docker build
- Multiple rebuild/redeploy cycles needed to diagnose and fix the issue

### Solutions Implemented
**Phase 6 - Frontend Deployment:**
- Modified Dockerfile to accept `ARG NEXT_PUBLIC_API_URL` before the build step
- Used `docker build --build-arg NEXT_PUBLIC_API_URL=http://taskapp-alb-...` to bake URL at build time
- Added verification step: `docker run --rm image grep -r 'taskapp-alb' /app/.next/server/` to confirm URL in bundles
- Documented this critical requirement in AWS_PHASE_6_GUIDE.md troubleshooting section

### AWS-Specific Learnings
**ECS Fargate:**
- Tasks in private subnets require NAT Gateway for ECR image pulls and internet access
- Health check paths must return 200 OK - Next.js root `/` can redirect (307), use `/api/health` instead
- Target group health checks run every 30 seconds with 2 consecutive successes required

**Application Load Balancer:**
- Path-based routing requires careful rule priority - `/api/*` must be Priority 1
- Default rule (`/*`) catches all remaining traffic, perfect for frontend catch-all routing
- Both services can share same ALB, reducing costs

**Docker & Next.js:**
- Next.js standalone mode creates minimal production server (~30MB vs ~300MB)
- Environment variables prefixed with `NEXT_PUBLIC_` are exposed to browser
- These variables must be set at build time, not container runtime

### Cost Insights
**Monthly Cost Breakdown (After Phase 11 - Optimized):**
- NAT Gateway: ~$33.00/month (35% of total)
- Application Load Balancer: ~$16.20/month (18%)
- RDS db.t3.micro: ~$15.30/month (17%)
- Backend ECS Fargate (1.3 avg tasks): ~$12.00/month (13%)
- Frontend ECS Fargate (1.3 avg tasks): ~$6.50/month (7%)
- CloudWatch Logs + Metrics: ~$8.00/month (9%)
- ECR Storage (10 image limit): ~$1.00/month (1%)
- Route 53 Hosted Zone: $0.50/month (0.5%)
- SSL Certificate (ACM): **$0.00 (FREE)**
- **Total Infrastructure: ~$92/month**

**Cost Optimization Applied (Phase 11):**
- Auto-scaling: ECS services now scale 1-4 tasks based on CPU (70% target)
- Scheduled scaling: Force 1 task at 11 PM, allow 4 tasks at 6 AM (Mon-Fri)
- RDS storage auto-scaling: 20 GB → 100 GB max (grows as needed)
- ECR lifecycle: Keep only last 10 images (automatic cleanup)
- CloudWatch logs: 30-day retention (prevents unlimited growth)
- **Savings: ~$12/month immediate (12%), up to $40/month during low usage (40%)**

**Phase 7 Savings:**
- Used existing domain (saved $12/year registration)
- Leveraged existing wildcard certificate (saved setup time)
- ACM certificates are always free

**Phase 8 Additions:**
- CloudWatch monitoring now operational
- 6 alarms protecting critical infrastructure
- Dashboard for visual monitoring
- Log Insights for troubleshooting

---

**Last Updated**: January 21, 2026
**Current Phase**: Phase 9 - Terraform Infrastructure as Code
**Next Milestone**: Convert manual infrastructure to Terraform
**Application Status**: ✅ **LIVE** at https://app.techveesolutions.com
