# Azure vs AWS Comparison

## Services Mapping

| AWS | Azure | Purpose |
|-----|-------|---------|
| VPC | Virtual Network (VNet) | Network isolation |
| ECS Fargate | Container Apps | Serverless containers |
| ECR | Container Registry (ACR) | Image storage |
| RDS PostgreSQL | Database for PostgreSQL | Managed DB |
| ALB | Application Gateway / CA Ingress | Load balancing |
| Route 53 | Azure DNS | Domain management |
| CloudWatch | Azure Monitor + Log Analytics | Monitoring |
| Secrets Manager | Key Vault | Secrets |
| IAM | Azure AD + RBAC | Access control |

## Cost Comparison (Monthly)

| Platform | Estimated Cost | Notes |
|----------|----------------|------|
| AWS | ~$92 | ECS + RDS + ALB + CloudWatch |
| Azure | ~$30-40 (year 1) | Container Apps + PostgreSQL B1ms |

## Feature Comparison

| Area | Azure | AWS |
|------|-------|-----|
| Container Platform | Container Apps (KEDA) | ECS Fargate |
| Observability | Azure Monitor + Log Analytics | CloudWatch |
| Secrets | Key Vault | Secrets Manager |
| IaC | Bicep/Terraform | CloudFormation/Terraform |

## Pros / Cons

**Azure Pros**
- Container Apps is developer-friendly
- Strong cost management tools
- Simple CI/CD integration with GitHub Actions

**Azure Cons**
- Some services have regional constraints on free tiers
- Portal can be heavy for quick navigation

**AWS Pros**
- Huge service ecosystem
- Mature tooling and community

**AWS Cons**
- Higher baseline cost for similar workloads
