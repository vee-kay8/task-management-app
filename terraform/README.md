# Terraform Infrastructure - Task Management App

This directory contains Terraform configuration for managing the complete AWS infrastructure for the Task Management Application.

## Quick Start

### Prerequisites
- Terraform 1.7.0+
- AWS CLI configured
- Access to AWS account (858448674350)

### Environment Variables

Before running any Terraform commands, set these environment variables:

```bash
export TF_VAR_db_password="YourSecurePassword123!"
export TF_VAR_secret_key="FaKgFvIjFU3tz6bAugmkRw6CQfoaJuqAbJe/PYlyyu0="
export TF_VAR_jwt_secret_key="IB8fu3yhS/mPgIRmP6CsBab//X7Hnm+VggOHqXnB/F4="
```

### Common Commands

```bash
# Initialize Terraform
terraform init

# Check current state
terraform state list

# Preview changes
terraform plan

# Apply changes (use with caution!)
terraform plan -out=tfplan
terraform apply tfplan

# View outputs
terraform output

# Format code
terraform fmt -recursive

# Validate configuration
terraform validate
```

## Directory Structure

```
terraform/
├── provider.tf          # AWS provider configuration
├── variables.tf         # Input variable definitions
├── terraform.tfvars     # Variable values (git-ignored)
├── backend.tf          # Remote state (S3 + DynamoDB)
├── main.tf             # Root module
├── .gitignore          # Terraform ignore rules
└── modules/
    ├── vpc/            # VPC, subnets, gateways (15 resources)
    ├── security/       # Security groups (3 resources)
    ├── rds/            # PostgreSQL database (2 resources)
    ├── ecr/            # Container registries (2 resources)
    ├── ecs/            # ECS cluster & services (5 resources)
    ├── alb/            # Load balancer (6 resources)
    └── route53/        # DNS records (1 resource)
```

## Managed Resources

**Total**: 35 AWS resources

- **VPC Module**: VPC, 4 subnets, IGW, NAT, routing
- **Security Module**: ALB, Backend, RDS security groups
- **RDS Module**: PostgreSQL database + subnet group
- **ECR Module**: Backend and frontend repositories
- **ECS Module**: Cluster, 2 task definitions, 2 services
- **ALB Module**: Load balancer, target groups, listeners
- **Route53 Module**: app.techveesolutions.com A record

## State Management

- **Backend**: S3 bucket `taskapp-terraform-state-858448674350`
- **Locking**: DynamoDB table `taskapp-terraform-locks`
- **Region**: us-east-1
- **State Path**: production/terraform.tfstate

## Default Tags

All resources are tagged with:
- `Project`: TaskManagementApp
- `Environment`: production
- `ManagedBy`: Terraform

## Important Notes

⚠️ **WARNING**: This Terraform configuration manages production infrastructure. Always:
1. Run `terraform plan` first
2. Review changes carefully
3. Use `-out` flag to save plans
4. Never run `terraform destroy` in production
5. Coordinate with team before making changes

## Sensitive Variables

The following variables contain secrets and must be provided via environment variables:
- `db_password` - RDS database password
- `secret_key` - Flask application secret key
- `jwt_secret_key` - JWT token secret key

**Never commit these values to Git!**

## Module Dependencies

```
VPC ─┬─→ Security ──→ RDS
     ├─→ Security ──→ ECS ──→ Services
     ├─→ ECR ────────→ ECS
     └─→ ALB ────────→ Route53
```

## Making Changes

1. Create a new branch
2. Edit module files
3. Run `terraform fmt` to format code
4. Run `terraform validate` to check syntax
5. Run `terraform plan` and review output
6. If correct, `terraform apply`
7. Commit and push changes
8. Create pull request for review

## Troubleshooting

### State Lock Error
```bash
# If Terraform crashes and leaves a lock
terraform force-unlock <LOCK_ID>
```

### Import Existing Resources
```bash
# General format
terraform import module.<MODULE>.aws_<TYPE>.<NAME> <AWS_ID>

# Example
terraform import module.vpc.aws_vpc.main vpc-016004b6f25f26302
```

### View Resource Details
```bash
# Show specific resource
terraform state show module.ecs.aws_ecs_cluster.main

# Show all state
terraform show
```

## Documentation

- [AWS_PHASE_9_GUIDE.md](../AWS_PHASE_9_GUIDE.md) - Complete Phase 9 guide
- [AWS_PHASE_9_COMPLETE.md](../AWS_PHASE_9_COMPLETE.md) - Completion summary
- [AWS_DEPLOYMENT_ROADMAP.md](../AWS_DEPLOYMENT_ROADMAP.md) - Overall deployment roadmap

## Support

For questions or issues:
1. Check the documentation files above
2. Review Terraform logs
3. Check AWS Console to verify resource state
4. Review commit history for recent changes

---

**Last Updated**: January 22, 2026
**Infrastructure Version**: v1.0
**Status**: Production
