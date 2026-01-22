# AWS Deployment Roadmap - Complete Guide

**Project**: Task Management Application Deployment to AWS
**Duration**: 3-4 weeks
**Status**: In Progress

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
**Status**: 🔄 In Progress (0%)

### Checklist
- [ ] Register domain in Route53 (or use existing domain)
- [ ] Verify hosted zone created/exists
- [ ] Request SSL certificate in ACM (us-east-1)
  - [ ] Domain: taskapp.com
  - [ ] Alternative: www.taskapp.com
  - [ ] Validation method: DNS
- [ ] Add CNAME records for certificate validation
- [ ] Wait for certificate status: "Issued"
- [ ] Add HTTPS listener to ALB (port 443)
- [ ] Attach certificate to HTTPS listener
- [ ] Configure path routing on HTTPS listener
  - [ ] Priority 1: `/api/*` → backend target group
  - [ ] Default: `/*` → frontend target group
- [ ] Update HTTP listener to redirect to HTTPS (301)
- [ ] Create Route53 A records (alias to ALB)
  - [ ] A record: taskapp.com → ALB
  - [ ] A record: www.taskapp.com → ALB
- [ ] Update backend CORS_ORIGINS environment variable
- [ ] Redeploy backend with new CORS settings
- [ ] (Optional) Update frontend API_URL to HTTPS
- [ ] Test `https://taskapp.com` loads frontend
- [ ] Test `https://www.taskapp.com` loads frontend
- [ ] Test `http://taskapp.com` redirects to HTTPS
- [ ] Verify SSL certificate in browser (green padlock)
- [ ] Test API calls over HTTPS (no mixed content)
- [ ] Test full application functionality

### Deliverables
- Custom domain configured (taskapp.com)
- SSL/HTTPS working on ALB
- Professional URLs operational
- HTTP to HTTPS redirect functional

### Key Resources Created
- Domain Name: [To be filled]
- Hosted Zone ID: [To be filled]
- Certificate ARN: [To be filled]
- HTTPS Listener ARN: [To be filled]

---

## Phase 8: Monitoring & Logging

**Timeline**: Days 14-15
**Status**: Not Started

### Checklist
- [ ] Verify CloudWatch log groups created
- [ ] Configure log retention (7-30 days)
- [ ] Create CloudWatch dashboard
  - [ ] ECS metrics (CPU, memory, tasks)
  - [ ] ALB metrics (requests, latency, errors)
  - [ ] RDS metrics (connections, CPU, storage)
  - [ ] CloudFront metrics (requests, errors)
- [ ] Create CloudWatch alarms
  - [ ] ECS high CPU (>80%)
  - [ ] ECS high memory (>80%)
  - [ ] ALB high error rate (>5%)
  - [ ] ALB high latency (>1s)
  - [ ] RDS high CPU (>80%)
  - [ ] RDS low storage (<2GB)
  - [ ] RDS connection limit
- [ ] Create SNS topic for alerts
- [ ] Subscribe email to SNS topic
- [ ] Link alarms to SNS topic
- [ ] Test alarm notifications
- [ ] Enable RDS Enhanced Monitoring
- [ ] Enable VPC Flow Logs (optional)
- [ ] Document monitoring setup

### Deliverables
- Comprehensive monitoring dashboard
- Critical alarms configured
- Email notifications working
- Logging strategy documented

### Key Resources Created
- Dashboard Name: [To be filled]
- SNS Topic ARN: [To be filled]
- Number of Alarms: [To be filled]

---

## Phase 9: Infrastructure as Code (Terraform)

**Timeline**: Days 16-18
**Status**: Not Started

### Checklist
- [ ] Install Terraform
- [ ] Create terraform directory structure
- [ ] Create provider.tf (AWS provider config)
- [ ] Create variables.tf (input variables)
- [ ] Create terraform.tfvars (variable values)
- [ ] Create networking.tf
  - [ ] VPC, subnets, route tables
  - [ ] Internet Gateway, NAT Gateway
  - [ ] Security groups
- [ ] Create database.tf
  - [ ] RDS subnet group
  - [ ] RDS instance
  - [ ] Secrets Manager
- [ ] Create ecr.tf
  - [ ] ECR repositories
- [ ] Create ecs.tf
  - [ ] ECS cluster
  - [ ] Task definitions
  - [ ] Services
- [ ] Create alb.tf
  - [ ] Load balancer
  - [ ] Target groups
  - [ ] Listeners
- [ ] Create s3.tf
  - [ ] S3 bucket for frontend
- [ ] Create cloudfront.tf
  - [ ] CloudFront distribution
- [ ] Create route53.tf
  - [ ] Hosted zone
  - [ ] DNS records
- [ ] Create acm.tf
  - [ ] SSL certificates
- [ ] Create monitoring.tf
  - [ ] CloudWatch alarms
  - [ ] SNS topics
- [ ] Create outputs.tf (output values)
- [ ] Run terraform init
- [ ] Run terraform plan
- [ ] Run terraform apply (test environment)
- [ ] Verify infrastructure created
- [ ] Document Terraform usage
- [ ] Create README for Terraform

### Deliverables
- Complete Terraform configuration
- Reproducible infrastructure
- Terraform documentation

### Files Created
- provider.tf
- variables.tf
- networking.tf
- database.tf
- ecs.tf
- And 10+ more Terraform files

---

## Phase 10: CI/CD Integration

**Timeline**: Days 19-20
**Status**: Not Started

### Checklist
- [ ] Create IAM user for GitHub Actions
- [ ] Create policy for deployments
- [ ] Generate access keys
- [ ] Add AWS credentials to GitHub Secrets
  - [ ] AWS_ACCESS_KEY_ID
  - [ ] AWS_SECRET_ACCESS_KEY
  - [ ] AWS_REGION
- [ ] Update GitHub Actions workflow
- [ ] Add AWS deployment job
  - [ ] Configure AWS credentials
  - [ ] Build Docker images
  - [ ] Push to ECR
  - [ ] Update ECS task definition
  - [ ] Deploy to ECS
  - [ ] Build frontend
  - [ ] Upload to S3
  - [ ] Invalidate CloudFront cache
- [ ] Test deployment workflow
- [ ] Make code change and push
- [ ] Verify automated deployment
- [ ] Check application updates
- [ ] Document CI/CD pipeline

### Deliverables
- Automated deployment pipeline
- Push-to-deploy functionality
- Zero manual deployment steps

### GitHub Actions Jobs
- Build and test
- Build Docker images
- Deploy to AWS ECS (backend and frontend)
- CI/CD updates for ECS deployments

---

## Phase 11: Cost Optimization & Best Practices

**Timeline**: Days 21-22
**Status**: Not Started

### Checklist
- [ ] Enable AWS Cost Explorer
- [ ] Review cost breakdown by service
- [ ] Identify optimization opportunities
- [ ] Review ECS task sizing (backend and frontend)
- [ ] Consider RDS instance right-sizing
- [ ] Enable ECS auto-scaling (both services)
  - [ ] Target tracking scaling
  - [ ] Min tasks: 1, Max tasks: 4
  - [ ] CPU target: 70%
- [ ] Configure ALB target tracking
- [ ] Review ALB listener rules and routing
- [ ] Review RDS backup retention
- [ ] Enable RDS automated backups
- [ ] Take manual RDS snapshot
- [ ] Enable AWS WAF on ALB (optional)
- [ ] Enable VPC Flow Logs
- [ ] Review security group rules
- [ ] Enable AWS Security Hub (optional)
- [ ] Run AWS Trusted Advisor checks
- [ ] Document cost optimization steps
- [ ] Create monthly cost estimate

### Deliverables
- Cost optimization report
- Auto-scaling configured
- Backup strategy implemented
- Security hardening complete

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

## Phase 12: Documentation & Comparison Prep

**Timeline**: Days 23-24
**Status**: Not Started

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
- **Phases Completed**: 6/12
- **Days Elapsed**: 11/24
- **Percentage Complete**: 50%

### Phase Status Summary
| Phase | Name | Status | Days | Completion |
|-------|------|--------|------|------------|
| 1 | Account Setup | ✅ Complete | 1 | 100% |
| 2 | VPC & Networking | ✅ Complete | 2-3 | 100% |
| 3 | RDS Database | ✅ Complete | 4-5 | 100% |
| 4 | ECR Registry | ✅ Complete | 6 | 100% |
| 5 | ECS Backend | ✅ Complete | 7-9 | 100% |
| 6 | ECS Frontend | ✅ Complete | 10-11 | 100% |
| 7 | Domain & SSL | 🔄 In Progress | 12-13 | 0% |
| 8 | Monitoring | Not Started | 14-15 | 0% |
| 9 | Terraform IaC | Not Started | 16-18 | 0% |
| 10 | CI/CD Integration | Not Started | 19-20 | 0% |
| 11 | Optimization | Not Started | 21-22 | 0% |
| 12 | Documentation | Not Started | 23-24 | 0% |

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
**Monthly Cost Breakdown (After Phase 6):**
- RDS db.t3.micro: ~$15.30/month
- Application Load Balancer: ~$16.20/month
- NAT Gateway: ~$33.00/month (biggest cost driver)
- Backend ECS Fargate (2 tasks): ~$18.00/month
- Frontend ECS Fargate (2 tasks): ~$9.75/month
- CloudWatch Logs: ~$1.00/month
- ECR Storage: <$1.00/month
- **Total Infrastructure: ~$94/month**

**Cost Optimization Opportunities:**
- NAT Gateway is 35% of total cost - consider stopping when not actively deploying
- Running 1 task per service instead of 2 would save ~$14/month
- Phase 11 will implement auto-scaling to scale down during low usage

---

**Last Updated**: January 21, 2026
**Current Phase**: Phase 7 - Domain & SSL Configuration
**Next Milestone**: Add custom domain with HTTPS support
**Application Status**: ✅ Fully functional at http://taskapp-alb-1878540875.us-east-1.elb.amazonaws.com
