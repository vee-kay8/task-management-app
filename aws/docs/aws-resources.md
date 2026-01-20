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
- NAT Gateway ID: nat-0b8ad83bfb204e518
- Elastic IP: 13.223.103.168
- Subnet: Public Subnet 1
- State: Available

### Route Tables
- Public RT: rtb-07193bd0bc57c946b
  - Routes: 0.0.0.0/0 → Internet Gateway
  - Associations: Public Subnet 1, Public Subnet 2
  
- Private RT: rtb-09b52332e1238780c
  - Routes: 0.0.0.0/0 → NAT Gateway
  - Associations: Private Subnet 1, Private Subnet 2

### Security Groups
- Database SG: sg-0c57afe621eb3932d
  - Inbound: Port 5432 from VPC (10.0.0.0/16)
  
- Backend SG: sg-01e0fb4d04d2a2234
  - Inbound: Port 5000 from ALB SG
  
- Load Balancer SG: sg-0ca03625756c71a66
  - Inbound: Port 80 from 0.0.0.0/0
  - Inbound: Port 443 from 0.0.0.0/0

### Cost Estimate (Phase 2)
- NAT Gateway: ~$0.045/hour = ~$32.40/month
- Elastic IP (while NAT Gateway running): Free
- VPC, Subnets, Route Tables, Security Groups: Free
- Internet Gateway: Free
**Total**: ~$32.40/month