# AWS Phase 7: Domain & SSL/TLS Configuration ✅ COMPLETE

## Overview
Add a custom domain name and enable HTTPS for your application. This phase makes your application production-ready with professional URLs and secure communication.

**Timeline**: 2-3 hours (Completed in 2 hours)  
**Cost**: $0 (Used existing domain + certificate)  
**Prerequisites**: Phase 6 complete (Frontend + Backend on ECS)
**Actual Implementation**: Used existing techveesolutions.com domain and certificate

---

## ✅ What Was Implemented

**Domain**: app.techveesolutions.com  
**Certificate**: Existing wildcard certificate (*.techveesolutions.com)  
**Result**: Application now live at https://app.techveesolutions.com

---

## What You'll Create

1. **Custom Domain** - Professional domain name (e.g., `taskapp.com`)
2. **Route 53 Hosted Zone** - DNS management in AWS
3. **ACM SSL Certificate** - Free SSL/TLS certificate from AWS
4. **HTTPS on ALB** - Secure HTTPS listener on Application Load Balancer
5. **HTTP to HTTPS Redirect** - Automatic redirect from HTTP to HTTPS
6. **DNS Records** - Point your domain to AWS resources

---

## Architecture After Phase 7

```
Internet → DNS (Route 53)
            ↓
         taskapp.com (A Record)
            ↓
    ALB HTTPS Listener (443) ← SSL Certificate (ACM)
    │
    ├─ /api/* → Backend ECS (HTTP:5000)
    └─ /*     → Frontend ECS (HTTP:3000)

HTTP → HTTPS Redirect (Listener on port 80)
```

**What Changes:**
- Before: `http://taskapp-alb-1878540875.us-east-1.elb.amazonaws.com`
- After: `https://taskapp.com` or `https://www.taskapp.com`

---

## Decision Point: Domain Registration

### Option 1: Use Route 53 to Register Domain (Recommended)
- **Pros**: Everything in one place, automatic hosted zone creation, easy management
- **Cons**: Costs $12-$15/year depending on TLD
- **Best for**: New domains, AWS-native workflow

### Option 2: Use Existing Domain from Another Registrar
- **Pros**: Keep existing domain, no new purchase needed
- **Cons**: Need to update nameservers at your registrar
- **Best for**: Existing domains, GoDaddy/Namecheap users

### Option 3: Skip This Phase (Not Recommended)
- **Pros**: Save $12/year
- **Cons**: Unprofessional ALB URL, no HTTPS, not production-ready
- **Best for**: Short-term testing only

**For this guide, we'll use Option 1 (Route 53 domain registration)**

---

## Step 1: Register Domain Name (Route 53)

### Search for Available Domain

1. **Navigate to Route 53 Console**
   - Open [Route 53 Console](https://console.aws.amazon.com/route53/)
   - Click "Registered domains" in left sidebar
   - Click "Register domain"

2. **Search for Domain**
   ```
   Search for: taskapp.com
   Alternative suggestions:
   - taskapp.io ($35/year)
   - taskapp.net ($12/year)
   - mytaskapp.com ($12/year)
   - taskmanager.app ($18/year)
   ```

3. **Choose Domain**
   - Select available domain
   - Click "Add to cart"
   - **Note**: `.com` domains are ~$12/year, `.io` are ~$35/year

### Complete Registration

1. **Contact Information**
   - Fill in registrant contact details
   - ✅ Enable "Privacy protection" (hides your personal info from WHOIS)
   - ✅ Enable "Auto-renew" (recommended)

2. **Review and Purchase**
   - Review total: ~$12/year for `.com`
   - Accept terms and conditions
   - Click "Complete order"
   - Wait for confirmation email (5-15 minutes)

3. **Verify Email**
   - Check inbox for "Verify your email address" from AWS
   - Click verification link
   - **Important**: Domain won't work until verified!

### AWS CLI Method (Skip if using Console)

```bash
# Check domain availability
aws route53domains check-domain-availability \
  --domain-name taskapp.com \
  --region us-east-1

# Register domain (requires contact info JSON file)
aws route53domains register-domain \
  --domain-name taskapp.com \
  --duration-in-years 1 \
  --admin-contact file://contact.json \
  --registrant-contact file://contact.json \
  --tech-contact file://contact.json \
  --privacy-protect-admin-contact \
  --privacy-protect-registrant-contact \
  --privacy-protect-tech-contact \
  --auto-renew \
  --region us-east-1
```

**Note**: Domain registration can take 10-15 minutes. You can proceed to the next steps while waiting.

---

## Step 2: Create Hosted Zone (Skip if Auto-Created)

If you registered the domain in Route 53, a hosted zone is automatically created. Verify it exists:

### Verify Hosted Zone

```bash
# List hosted zones
aws route53 list-hosted-zones \
  --query 'HostedZones[?Name==`taskapp.com.`]' \
  --region us-east-1

# Get hosted zone details
aws route53 list-hosted-zones \
  --query 'HostedZones[?Name==`taskapp.com.`].[Id,Name,ResourceRecordSetCount]' \
  --output table \
  --region us-east-1
```

**Expected Output:**
```
Hosted Zone ID: /hostedzone/Z1234567890ABC
Name: taskapp.com.
Record Count: 2 (NS and SOA records)
```

### If Using External Domain (GoDaddy, Namecheap, etc.)

If you have an existing domain from another registrar:

1. **Create Hosted Zone in Route 53**
   ```bash
   aws route53 create-hosted-zone \
     --name taskapp.com \
     --caller-reference $(date +%s) \
     --region us-east-1
   ```

2. **Get Nameservers**
   ```bash
   aws route53 list-resource-record-sets \
     --hosted-zone-id Z1234567890ABC \
     --query "ResourceRecordSets[?Type=='NS']" \
     --region us-east-1
   ```

3. **Update Nameservers at Your Registrar**
   - Go to your domain registrar (GoDaddy, Namecheap, etc.)
   - Find "DNS Settings" or "Nameservers"
   - Change to "Custom nameservers"
   - Add the 4 nameservers from AWS (format: `ns-123.awsdns-45.com`)
   - Save changes
   - **Wait 24-48 hours for DNS propagation**

---

## Step 3: Request SSL/TLS Certificate (ACM)

AWS Certificate Manager (ACM) provides free SSL certificates.

### Request Certificate via Console

1. **Navigate to ACM**
   - Open [ACM Console](https://console.aws.amazon.com/acm/)
   - **Important**: Select **us-east-1** region (same as ALB)
   - Click "Request certificate"

2. **Request Public Certificate**
   - Certificate type: **Public certificate**
   - Click "Next"

3. **Domain Names**
   ```
   Fully qualified domain name: taskapp.com
   Add another name: www.taskapp.com
   Add another name: *.taskapp.com (optional wildcard)
   ```
   - This allows `taskapp.com`, `www.taskapp.com`, and any subdomain

4. **Validation Method**
   - Select: **DNS validation**
   - Click "Request"

### Request Certificate via AWS CLI

```bash
# Request certificate for domain and www subdomain
aws acm request-certificate \
  --domain-name taskapp.com \
  --subject-alternative-names www.taskapp.com \
  --validation-method DNS \
  --region us-east-1 \
  --tags Key=Name,Value=taskapp-certificate

# Save the certificate ARN
# Output: arn:aws:acm:us-east-1:858448674350:certificate/12345678-1234-1234-1234-123456789012
```

---

## Step 4: Validate Certificate (DNS Validation)

### Add CNAME Records for Validation

1. **Get Validation Records**
   - In ACM console, click on your certificate
   - Expand "Domains" section
   - You'll see CNAME records needed for validation

2. **Create CNAME Records in Route 53**
   - Click "Create records in Route 53" button
   - ACM will automatically add validation records to Route 53
   - Click "Create records"

3. **Wait for Validation**
   - Status will change from "Pending validation" to "Issued"
   - Usually takes 5-30 minutes
   - Check status: `aws acm describe-certificate --certificate-arn <ARN> --region us-east-1`

### AWS CLI Method

```bash
# Get validation details
aws acm describe-certificate \
  --certificate-arn arn:aws:acm:us-east-1:858448674350:certificate/12345678-1234-1234-1234-123456789012 \
  --query 'Certificate.DomainValidationOptions[*].[DomainName,ResourceRecord.Name,ResourceRecord.Value]' \
  --output table \
  --region us-east-1

# Get hosted zone ID
HOSTED_ZONE_ID=$(aws route53 list-hosted-zones \
  --query 'HostedZones[?Name==`taskapp.com.`].Id' \
  --output text | cut -d'/' -f3)

# Create validation CNAME record (example - replace with actual values)
aws route53 change-resource-record-sets \
  --hosted-zone-id $HOSTED_ZONE_ID \
  --change-batch file://acm-validation.json

# Check certificate status
aws acm describe-certificate \
  --certificate-arn arn:aws:acm:us-east-1:858448674350:certificate/12345678-1234-1234-1234-123456789012 \
  --query 'Certificate.Status' \
  --output text \
  --region us-east-1
```

**Wait until status shows "ISSUED" before proceeding.**

---

## Step 5: Add HTTPS Listener to ALB

### Get Certificate ARN

```bash
# List certificates
aws acm list-certificates --region us-east-1

# Get full ARN
CERTIFICATE_ARN=$(aws acm list-certificates \
  --query 'CertificateSummaryList[?DomainName==`taskapp.com`].CertificateArn' \
  --output text \
  --region us-east-1)

echo $CERTIFICATE_ARN
```

### Get ALB ARN

```bash
# Get ALB ARN
ALB_ARN=$(aws elbv2 describe-load-balancers \
  --names taskapp-alb \
  --query 'LoadBalancers[0].LoadBalancerArn' \
  --output text \
  --region us-east-1)

echo $ALB_ARN
```

### Get Target Group ARNs

```bash
# Get frontend target group ARN
FRONTEND_TG_ARN=$(aws elbv2 describe-target-groups \
  --names taskapp-frontend-tg \
  --query 'TargetGroups[0].TargetGroupArn' \
  --output text \
  --region us-east-1)

# Get backend target group ARN
BACKEND_TG_ARN=$(aws elbv2 describe-target-groups \
  --names taskapp-backend-tg \
  --query 'TargetGroups[0].TargetGroupArn' \
  --output text \
  --region us-east-1)

echo "Frontend TG: $FRONTEND_TG_ARN"
echo "Backend TG: $BACKEND_TG_ARN"
```

### Create HTTPS Listener (Port 443)

```bash
# Create HTTPS listener with default action to frontend
aws elbv2 create-listener \
  --load-balancer-arn $ALB_ARN \
  --protocol HTTPS \
  --port 443 \
  --certificates CertificateArn=$CERTIFICATE_ARN \
  --default-actions Type=forward,TargetGroupArn=$FRONTEND_TG_ARN \
  --region us-east-1

# Save the listener ARN from output
# Example: arn:aws:elasticloadbalancing:us-east-1:858448674350:listener/app/taskapp-alb/50dc6c495f0c9188/f2f7dc8efc522ab9
```

### Add Path-Based Routing Rule for Backend API

```bash
# Get HTTPS listener ARN
HTTPS_LISTENER_ARN=$(aws elbv2 describe-listeners \
  --load-balancer-arn $ALB_ARN \
  --query 'Listeners[?Port==`443`].ListenerArn' \
  --output text \
  --region us-east-1)

# Create rule: /api/* → backend
aws elbv2 create-rule \
  --listener-arn $HTTPS_LISTENER_ARN \
  --priority 1 \
  --conditions Field=path-pattern,Values='/api/*' \
  --actions Type=forward,TargetGroupArn=$BACKEND_TG_ARN \
  --region us-east-1
```

### Via AWS Console

1. **Navigate to EC2 → Load Balancers**
2. **Select taskapp-alb**
3. **Go to "Listeners" tab**
4. **Click "Add listener"**
   ```
   Protocol: HTTPS
   Port: 443
   Default action: Forward to taskapp-frontend-tg
   Security policy: ELBSecurityPolicy-2016-08
   Certificate: Select your ACM certificate (taskapp.com)
   ```
5. **Click "Add"**
6. **Add Rule for Backend API**
   - Click "View/edit rules" on HTTPS:443 listener
   - Click "+" to add rule
   - Insert rule at Priority 1
   - Condition: Path is `/api/*`
   - Action: Forward to `taskapp-backend-tg`
   - Save

---

## Step 6: Configure HTTP to HTTPS Redirect

### Update Existing HTTP Listener (Port 80)

```bash
# Get HTTP listener ARN
HTTP_LISTENER_ARN=$(aws elbv2 describe-listeners \
  --load-balancer-arn $ALB_ARN \
  --query 'Listeners[?Port==`80`].ListenerArn' \
  --output text \
  --region us-east-1)

# Modify to redirect to HTTPS
aws elbv2 modify-listener \
  --listener-arn $HTTP_LISTENER_ARN \
  --default-actions Type=redirect,RedirectConfig='{Protocol=HTTPS,Port=443,StatusCode=HTTP_301}' \
  --region us-east-1
```

### Via AWS Console

1. **Go to Load Balancers → taskapp-alb → Listeners**
2. **Select HTTP:80 listener**
3. **Click "Edit"**
4. **Delete existing rules**
5. **Change default action:**
   ```
   Type: Redirect to...
   Protocol: HTTPS
   Port: 443
   Status code: 301 - Permanently moved
   ```
6. **Click "Update"**

**Test redirect:**
```bash
curl -I http://taskapp-alb-1878540875.us-east-1.elb.amazonaws.com
# Should see: HTTP/1.1 301 Moved Permanently
# Location: https://taskapp-alb-1878540875.us-east-1.elb.amazonaws.com/
```

---

## Step 7: Create DNS Records in Route 53

### Create A Record for Root Domain (taskapp.com)

```bash
# Get ALB DNS name
ALB_DNS_NAME=$(aws elbv2 describe-load-balancers \
  --names taskapp-alb \
  --query 'LoadBalancers[0].DNSName' \
  --output text \
  --region us-east-1)

# Get ALB hosted zone ID (for alias record)
ALB_HOSTED_ZONE_ID=$(aws elbv2 describe-load-balancers \
  --names taskapp-alb \
  --query 'LoadBalancers[0].CanonicalHostedZoneId' \
  --output text \
  --region us-east-1)

# Get your Route 53 hosted zone ID
HOSTED_ZONE_ID=$(aws route53 list-hosted-zones \
  --query 'HostedZones[?Name==`taskapp.com.`].Id' \
  --output text | cut -d'/' -f3)

echo "ALB DNS: $ALB_DNS_NAME"
echo "ALB Hosted Zone: $ALB_HOSTED_ZONE_ID"
echo "Route53 Zone: $HOSTED_ZONE_ID"
```

Create the A record pointing to ALB:

```bash
# Create change batch JSON
cat > create-a-record.json << EOF
{
  "Changes": [
    {
      "Action": "CREATE",
      "ResourceRecordSet": {
        "Name": "taskapp.com",
        "Type": "A",
        "AliasTarget": {
          "HostedZoneId": "$ALB_HOSTED_ZONE_ID",
          "DNSName": "$ALB_DNS_NAME",
          "EvaluateTargetHealth": true
        }
      }
    }
  ]
}
EOF

# Apply changes
aws route53 change-resource-record-sets \
  --hosted-zone-id $HOSTED_ZONE_ID \
  --change-batch file://create-a-record.json \
  --region us-east-1
```

### Create A Record for www Subdomain (www.taskapp.com)

```bash
# Create change batch for www
cat > create-www-record.json << EOF
{
  "Changes": [
    {
      "Action": "CREATE",
      "ResourceRecordSet": {
        "Name": "www.taskapp.com",
        "Type": "A",
        "AliasTarget": {
          "HostedZoneId": "$ALB_HOSTED_ZONE_ID",
          "DNSName": "$ALB_DNS_NAME",
          "EvaluateTargetHealth": true
        }
      }
    }
  ]
}
EOF

# Apply changes
aws route53 change-resource-record-sets \
  --hosted-zone-id $HOSTED_ZONE_ID \
  --change-batch file://create-www-record.json \
  --region us-east-1
```

### Via AWS Console

1. **Navigate to Route 53 → Hosted zones**
2. **Click on `taskapp.com`**
3. **Click "Create record"**

**For root domain (taskapp.com):**
```
Record name: [leave blank]
Record type: A
Alias: Yes
Route traffic to: Alias to Application Load Balancer
Region: us-east-1
Load balancer: taskapp-alb
Routing policy: Simple routing
```

**For www subdomain:**
```
Record name: www
Record type: A
Alias: Yes
Route traffic to: Alias to Application Load Balancer
Region: us-east-1
Load balancer: taskapp-alb
```

---

## Step 8: Update Backend CORS Configuration

Your backend needs to allow requests from your new domain.

### Update Backend Environment Variable

```bash
# Get current task definition
aws ecs describe-task-definition \
  --task-definition taskapp-backend \
  --query 'taskDefinition' > backend-task-def.json

# Edit backend-task-def.json and update CORS_ORIGINS
# Find the environment variables section and change:
# From: "CORS_ORIGINS": "*"
# To: "CORS_ORIGINS": "https://taskapp.com,https://www.taskapp.com"
```

Update the `CORS_ORIGINS` environment variable:

```json
{
  "name": "CORS_ORIGINS",
  "value": "https://taskapp.com,https://www.taskapp.com"
}
```

Register new task definition:

```bash
# Clean up the JSON (remove unnecessary fields)
cat backend-task-def.json | jq 'del(.taskDefinitionArn, .revision, .status, .requiresAttributes, .compatibilities, .registeredAt, .registeredBy)' > backend-task-def-new.json

# Register new revision
aws ecs register-task-definition \
  --cli-input-json file://backend-task-def-new.json \
  --region us-east-1

# Update service to use new task definition
aws ecs update-service \
  --cluster taskapp-cluster \
  --service taskapp-backend-service \
  --task-definition taskapp-backend \
  --force-new-deployment \
  --region us-east-1
```

---

## Step 9: Update Frontend API URL (Optional)

Since you're now using HTTPS and a custom domain, you can update the frontend to use the new URL.

### Option 1: Keep Relative Paths (Recommended)

Your frontend already uses relative paths (`/api`), which will work with your custom domain. No changes needed!

### Option 2: Use Absolute HTTPS URL

If you want to explicitly use HTTPS URL:

```bash
# Update .env.production
cd frontend
echo "NEXT_PUBLIC_API_URL=https://taskapp.com" > .env.production

# Rebuild Docker image
docker build --no-cache \
  --build-arg NEXT_PUBLIC_API_URL=https://taskapp.com \
  -t taskapp-frontend:latest .

# Tag and push to ECR
docker tag taskapp-frontend:latest 858448674350.dkr.ecr.us-east-1.amazonaws.com/taskapp-frontend:latest
docker push 858448674350.dkr.ecr.us-east-1.amazonaws.com/taskapp-frontend:latest

# Force deployment
aws ecs update-service \
  --cluster taskapp-cluster \
  --service taskapp-frontend-service \
  --force-new-deployment \
  --region us-east-1
```

---

## Step 10: Test Your Custom Domain

### Wait for DNS Propagation

DNS changes can take 5-60 minutes to propagate worldwide.

Check DNS propagation:

```bash
# Check if DNS is resolving
nslookup taskapp.com
nslookup www.taskapp.com

# Or use dig
dig taskapp.com +short
dig www.taskapp.com +short

# Should show ALB IP addresses
```

### Test HTTPS Access

```bash
# Test root domain
curl -I https://taskapp.com
# Should return: HTTP/2 200

# Test www subdomain
curl -I https://www.taskapp.com
# Should return: HTTP/2 200

# Test HTTP redirect
curl -I http://taskapp.com
# Should return: HTTP/1.1 301 Moved Permanently
# Location: https://taskapp.com/

# Test backend API
curl https://taskapp.com/api/
# Should return: {"message":"Task Management API","version":"1.0.0"}
```

### Browser Testing

1. **Open browser:**
   ```
   https://taskapp.com
   ```

2. **Verify SSL certificate:**
   - Click padlock icon in address bar
   - Should show "Connection is secure"
   - Certificate issued to `taskapp.com`
   - Issued by Amazon

3. **Test application:**
   - Registration works
   - Login works
   - Projects page loads
   - API calls succeed (check Network tab)
   - No mixed content warnings
   - All requests use HTTPS

4. **Test redirect:**
   ```
   http://taskapp.com
   ```
   - Should automatically redirect to `https://taskapp.com`

---

## Troubleshooting

### Certificate Stuck in "Pending Validation"

**Cause:** CNAME records not added to Route 53 or incorrect values

**Solution:**
1. Check ACM console for exact CNAME records needed
2. Verify records exist in Route 53 hosted zone
3. Wait up to 30 minutes for validation
4. Check DNS propagation: `dig _validation.taskapp.com CNAME`

### "This site can't be reached" Error

**Cause:** DNS not propagated yet or wrong A record

**Solution:**
1. Wait 5-60 minutes for DNS propagation
2. Verify A record points to ALB: `dig taskapp.com +short`
3. Check ALB is running: `aws elbv2 describe-load-balancers --names taskapp-alb`
4. Try from different network or use mobile data

### SSL Certificate Errors in Browser

**Cause:** Certificate not attached to HTTPS listener or wrong domain

**Solution:**
1. Verify certificate is "Issued" in ACM
2. Check HTTPS listener has correct certificate attached
3. Verify domain name matches certificate (no typos)
4. Clear browser cache and try incognito mode

### Mixed Content Warnings

**Cause:** Frontend making HTTP requests instead of HTTPS

**Solution:**
1. Update frontend to use relative paths: `/api` instead of `http://...`
2. Or use `https://taskapp.com` in environment variables
3. Rebuild and redeploy frontend
4. Check browser console for specific mixed content URLs

### API Calls Failing with CORS Errors

**Cause:** Backend CORS not updated for new domain

**Solution:**
1. Check backend logs for CORS errors
2. Verify `CORS_ORIGINS` includes `https://taskapp.com`
3. Redeploy backend with updated environment variable
4. Check browser Network tab for CORS headers

---

## Phase 7 Verification Checklist

### DNS & Domain
- [ ] Domain registered and verified email
- [ ] Hosted zone created in Route 53
- [ ] Nameservers configured (if external domain)
- [ ] A record for root domain (`taskapp.com`) → ALB
- [ ] A record for www subdomain (`www.taskapp.com`) → ALB
- [ ] DNS resolving correctly: `dig taskapp.com +short`

### SSL/TLS Certificate
- [ ] ACM certificate requested
- [ ] Certificate validated (status: "Issued")
- [ ] Certificate covers both `taskapp.com` and `www.taskapp.com`
- [ ] Certificate attached to ALB HTTPS listener

### Application Load Balancer
- [ ] HTTPS listener created on port 443
- [ ] Certificate attached to HTTPS listener
- [ ] Path routing configured: `/api/*` → backend
- [ ] Default action: forward to frontend
- [ ] HTTP listener redirects to HTTPS (301)

### Application Updates
- [ ] Backend CORS updated with new domain
- [ ] Backend redeployed with new CORS settings
- [ ] Frontend tested (optional: updated to use HTTPS URL)

### Testing
- [ ] `https://taskapp.com` loads frontend
- [ ] `https://www.taskapp.com` loads frontend
- [ ] `http://taskapp.com` redirects to HTTPS
- [ ] SSL certificate valid (green padlock)
- [ ] API calls work over HTTPS
- [ ] No mixed content warnings
- [ ] Registration/Login functional
- [ ] All application features working

---

## Cost Summary

### One-Time Costs
- Domain registration: $12-35/year (depending on TLD)
  - `.com`: ~$12/year
  - `.io`: ~$35/year
  - `.net`: ~$12/year
  - `.app`: ~$18/year

### Monthly Recurring Costs
- SSL Certificate (ACM): **$0.00** (FREE!)
- Route 53 Hosted Zone: **$0.50/month**
- Route 53 DNS Queries: ~$0.40/month (first 1M queries)
- **Total New Monthly Cost: ~$0.90/month**

### Updated Infrastructure Costs (After Phase 7)

| Resource | Monthly Cost |
|----------|--------------|
| RDS db.t3.micro | ~$15.30 |
| Application Load Balancer | ~$16.20 |
| NAT Gateway | ~$33.00 |
| Backend ECS (2 tasks) | ~$18.00 |
| Frontend ECS (2 tasks) | ~$9.75 |
| CloudWatch Logs | ~$1.00 |
| ECR Storage | <$1.00 |
| Route 53 Hosted Zone | ~$0.50 |
| Route 53 Queries | ~$0.40 |
| **Total** | **~$95/month** |

**Annual Domain Cost:** +$12-35/year

---

## Next Steps

After completing Phase 7, you have:
- ✅ Professional custom domain
- ✅ Secure HTTPS everywhere
- ✅ Production-ready application

**Recommended Next Phases:**
- **Phase 8**: Set up monitoring and alerting
- **Phase 9**: Convert to Infrastructure as Code (Terraform)
- **Phase 10**: Add CI/CD pipeline for automated deployments

---

## Additional Resources

- [ACM Documentation](https://docs.aws.amazon.com/acm/)
- [Route 53 Documentation](https://docs.aws.amazon.com/route53/)
- [ALB HTTPS Listener Guide](https://docs.aws.amazon.com/elasticloadbalancing/latest/application/create-https-listener.html)
- [DNS Propagation Checker](https://www.whatsmydns.net/)

---

**Phase 7 Complete!** 🎉 Your application now has a professional domain with secure HTTPS!
