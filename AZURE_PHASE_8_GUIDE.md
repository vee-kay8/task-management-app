# Azure Phase 8: Custom Domain & SSL - Complete Guide

**Duration**: 2-3 hours  
**Difficulty**: Intermediate  
**Prerequisites**: Phase 1-7 complete (Backend & Frontend deployed)  
**Goal**: Configure custom domain with SSL/TLS certificate

**Special Note**: This guide covers using a domain hosted in **AWS Route 53** with Azure Container Apps.

---

## 📋 Overview

This phase configures your custom domain to point to your Azure Container Apps. By the end, you'll have:

✅ Custom domain configured for frontend  
✅ Custom domain configured for backend (API subdomain)  
✅ SSL/TLS certificates installed (HTTPS)  
✅ DNS records updated in Route 53  
✅ Domain ownership verified  
✅ Application accessible via custom domain  

**Example Result**:
- Frontend: `https://yourdomain.com` or `https://app.yourdomain.com`
- Backend: `https://api.yourdomain.com`

---

## Table of Contents

1. [Understanding Custom Domains in Azure](#understanding-custom-domains-in-azure)
2. [Prerequisites & Domain Planning](#prerequisites--domain-planning)
3. [Add Custom Domain to Frontend](#step-1-add-custom-domain-to-frontend)
4. [Configure DNS in Route 53](#step-2-configure-dns-in-route-53)
5. [Add SSL Certificate](#step-3-add-ssl-certificate)
6. [Add Custom Domain to Backend (API)](#step-4-add-custom-domain-to-backend)
7. [Update Application Configuration](#step-5-update-application-configuration)
8. [Test Custom Domain](#step-6-test-custom-domain)
9. [Phase 8 Completion Checklist](#phase-8-completion-checklist)

---

## Understanding Custom Domains in Azure

### What is a Custom Domain?

Instead of:
- Frontend: `https://ca-taskapp-frontend.redtree-99ec4a5a.centralus.azurecontainerapps.io`
- Backend: `https://ca-taskapp-backend.redtree-99ec4a5a.centralus.azurecontainerapps.io`

You'll have:
- Frontend: `https://yourdomain.com` or `https://app.yourdomain.com`
- Backend: `https://api.yourdomain.com`

### DNS Record Types

| Record Type | Purpose | Example |
|-------------|---------|---------|
| **A Record** | Maps domain to IP address | `yourdomain.com → 20.84.222.186` |
| **CNAME** | Maps domain to another domain | `app.yourdomain.com → ca-taskapp-frontend...azurecontainerapps.io` |
| **TXT** | Verification & ownership | `asuid.yourdomain.com → verification-code` |

**For Container Apps**: We'll use **CNAME records** (recommended).

### SSL/TLS Certificates

Azure Container Apps offers two SSL options:

| Option | Cost | Renewal | Complexity |
|--------|------|---------|------------|
| **Managed Certificate** | Free | Automatic | Easy (recommended) |
| **Custom Certificate** | $$ | Manual | Complex |

**We'll use Managed Certificates** - Azure automatically provisions and renews Let's Encrypt certificates.

### Route 53 + Azure Integration

Since your domain is in AWS Route 53, you'll:
1. Configure custom domain in Azure Container Apps
2. Get verification TXT record from Azure
3. Add TXT record to Route 53 for verification
4. Add CNAME record to Route 53 to point to Azure
5. Azure verifies ownership and provisions SSL certificate

---

## Prerequisites & Domain Planning

### 1. Verify Your Domain in Route 53

**Login to AWS Console**: https://console.aws.amazon.com/route53/

**Check your domain**:
1. Go to Route 53 → Hosted Zones
2. Click on your domain
3. Verify you have access to add records

### 2. Decide on Domain Structure

**Option A: Root Domain + API Subdomain** (Recommended)
- Frontend: `yourdomain.com`
- Backend: `api.yourdomain.com`

**Option B: App Subdomain + API Subdomain**
- Frontend: `app.yourdomain.com`
- Backend: `api.yourdomain.com`

**Option C: Separate Subdomains**
- Frontend: `tasks.yourdomain.com`
- Backend: `tasks-api.yourdomain.com`

**For this guide, we'll use Option A**: 
- Frontend: `yourdomain.com`
- Backend: `api.yourdomain.com`

### 3. Set Variables

Replace `yourdomain.com` with your actual domain:

```bash
# Set your domain name
YOUR_DOMAIN="yourdomain.com"  # Replace with your actual domain
FRONTEND_DOMAIN="$YOUR_DOMAIN"  # Or: app.$YOUR_DOMAIN
API_DOMAIN="api.$YOUR_DOMAIN"

# Azure resource variables
RESOURCE_GROUP="rg-taskapp-prod"
FRONTEND_APP="ca-taskapp-frontend"
BACKEND_APP="ca-taskapp-backend"

echo "Frontend will be: https://${FRONTEND_DOMAIN}"
echo "Backend API will be: https://${API_DOMAIN}"
```

---

## Step 1: Add Custom Domain to Frontend

### What You're Doing

Configuring Azure Container Apps to accept traffic from your custom domain.

### Option A: Azure Portal Method

1. **Go to Azure Portal**: https://portal.azure.com

2. **Navigate to Container App**:
   - Search for "Container Apps"
   - Click on `ca-taskapp-frontend`

3. **Go to Custom Domains**:
   - Left sidebar → Settings → **Custom domains**
   - Click **"+ Add custom domain"**

4. **Enter Domain Details**:
   - **Domain**: Enter your domain (e.g., `yourdomain.com` or `app.yourdomain.com`)
   - **Certificate**: Select "Managed certificate"
   - Click **"Validate"**

5. **Get Verification Records**:
   Azure will show you two records to add to DNS:
   - **TXT Record**: For domain verification
     - Name: `asuid.yourdomain.com` (or `asuid.app.yourdomain.com`)
     - Value: Long verification code (e.g., `ABC123...XYZ`)
   - **CNAME Record**: To point domain to Container App
     - Name: `yourdomain.com` (or `app.yourdomain.com`)
     - Value: `ca-taskapp-frontend.redtree-99ec4a5a.centralus.azurecontainerapps.io`

6. **Copy These Values** - you'll add them to Route 53 in Step 2

### Option B: CLI Method (Recommended)

```bash
# Set your domain
YOUR_DOMAIN="yourdomain.com"  # Replace with actual domain
FRONTEND_DOMAIN="$YOUR_DOMAIN"  # Or: app.$YOUR_DOMAIN

# Get the default Container App domain
DEFAULT_DOMAIN=$(az containerapp show \
  --name $FRONTEND_APP \
  --resource-group $RESOURCE_GROUP \
  --query properties.configuration.ingress.fqdn \
  --output tsv)

echo "Default domain: $DEFAULT_DOMAIN"

# Get the custom domain verification ID (needed for TXT record)
VERIFICATION_ID=$(az containerapp show \
  --name $FRONTEND_APP \
  --resource-group $RESOURCE_GROUP \
  --query properties.customDomainVerificationId \
  --output tsv)

echo ""
echo "===================================================="
echo "DNS RECORDS TO ADD IN ROUTE 53 (Step 2)"
echo "===================================================="
echo ""
echo "1. TXT Record for Verification:"
echo "   Name:  asuid.${FRONTEND_DOMAIN}"
echo "   Value: ${VERIFICATION_ID}"
echo ""
echo "2. CNAME Record for Domain:"
echo "   Name:  ${FRONTEND_DOMAIN}"
echo "   Value: ${DEFAULT_DOMAIN}"
echo ""
echo "===================================================="
echo ""
echo "Copy these values - you'll need them in Step 2!"
```

**Expected output**:
```
Default domain: ca-taskapp-frontend.redtree-99ec4a5a.centralus.azurecontainerapps.io

====================================================
DNS RECORDS TO ADD IN ROUTE 53 (Step 2)
====================================================

1. TXT Record for Verification:
   Name:  asuid.yourdomain.com
   Value: D91CE6252F840730D2D2B6688DA4F50511554403303E9DA9E44235EB5F837CCE

2. CNAME Record for Domain:
   Name:  yourdomain.com
   Value: ca-taskapp-frontend.redtree-99ec4a5a.centralus.azurecontainerapps.io

====================================================
```

**Save these values!** You'll use them in the next step.

---

## Step 2: Configure DNS in Route 53

### What You're Doing

Adding DNS records in AWS Route 53 to:
1. Verify you own the domain (TXT record)
2. Point your domain to Azure Container Apps (CNAME record)

### Add TXT Record for Verification

1. **Go to AWS Console**: https://console.aws.amazon.com/route53/

2. **Navigate to Hosted Zones**:
   - Click on your domain (e.g., `yourdomain.com`)

3. **Create TXT Record**:
   - Click **"Create record"**
   - **Record name**: `asuid` (or `asuid.app` if using subdomain)
   - **Record type**: **TXT**
   - **Value**: Paste the verification ID from Step 1
     - Example: `D91CE6252F840730D2D2B6688DA4F50511554403303E9DA9E44235EB5F837CCE`
   - **TTL**: 300 (5 minutes)
   - Click **"Create records"**

### Add CNAME Record for Domain

**Option 1: Root Domain (yourdomain.com)**

⚠️ **Note**: Route 53 doesn't allow CNAME for root domain. Use **ALIAS** instead:

1. **Create ALIAS Record** (Route 53 specific):
   - Click **"Create record"**
   - **Record name**: Leave blank (for root domain)
   - **Record type**: **A** (not CNAME!)
   - Toggle **"Alias"** to **ON**
   - **Route traffic to**: Select "IP address or another value..."
   - ❌ **This won't work directly** - Container Apps doesn't provide static IP for ALIAS

**Workaround for Root Domain**:

Use a subdomain instead: `app.yourdomain.com` or `www.yourdomain.com`

**Option 2: Subdomain (app.yourdomain.com)** (Recommended)

1. **Create CNAME Record**:
   - Click **"Create record"**
   - **Record name**: `app` (or leave blank if not using root)
   - **Record type**: **CNAME**
   - **Value**: Paste the Container App domain from Step 1
     - Example: `ca-taskapp-frontend.redtree-99ec4a5a.centralus.azurecontainerapps.io`
   - **TTL**: 300 (5 minutes)
   - Click **"Create records"**

### Verify DNS Records

```bash
# Wait 2-3 minutes for DNS propagation, then verify:

# Check TXT record
dig asuid.yourdomain.com TXT +short
# Expected: Verification ID

# Check CNAME record (if using subdomain)
dig app.yourdomain.com CNAME +short
# Expected: ca-taskapp-frontend.redtree-99ec4a5a.centralus.azurecontainerapps.io.

# Or use nslookup on Windows:
nslookup -type=TXT asuid.yourdomain.com
nslookup app.yourdomain.com
```

**If DNS doesn't resolve yet**: Wait 5-10 minutes for propagation.

---

## Step 3: Add SSL Certificate

### What You're Doing

Once DNS records are verified, Azure will automatically provision a free SSL/TLS certificate.

### Add Custom Domain with Managed Certificate

**Via CLI**:

```bash
# Set your domain
FRONTEND_DOMAIN="app.yourdomain.com"  # Use the domain you configured in DNS

# Add custom domain with managed certificate
az containerapp hostname add \
  --hostname $FRONTEND_DOMAIN \
  --resource-group $RESOURCE_GROUP \
  --name $FRONTEND_APP

# This command will:
# 1. Verify DNS records are configured correctly
# 2. Validate domain ownership via TXT record
# 3. Request Let's Encrypt SSL certificate
# 4. Bind certificate to the domain
```

**⏰ This command will take 3-5 minutes** - Azure needs to:
1. Check TXT record exists
2. Check CNAME points to Container App
3. Request SSL certificate from Let's Encrypt
4. Provision and bind certificate

**Expected output**:
```json
{
  "bindingType": "SniEnabled",
  "certificateId": "/subscriptions/.../certificates/...",
  "name": "app.yourdomain.com"
}
```

**If you get an error**:

**Error**: "Unable to verify domain ownership"
- **Solution**: Wait 5-10 minutes for DNS propagation, then retry

**Error**: "TXT record not found"
- **Solution**: Verify TXT record in Route 53: `asuid.app.yourdomain.com`

**Error**: "CNAME record not found"
- **Solution**: Verify CNAME record in Route 53: `app.yourdomain.com`

### Bind Managed Certificate

```bash
# Bind the managed certificate to the domain
az containerapp hostname bind \
  --hostname $FRONTEND_DOMAIN \
  --resource-group $RESOURCE_GROUP \
  --name $FRONTEND_APP \
  --environment env-taskapp-prod \
  --validation-method CNAME
```

**Expected output**:
```json
{
  "certificateId": "/subscriptions/.../managedCertificates/mc-env-taskapp-prod-app-yourdomain-com",
  "bindingType": "SniEnabled",
  "thumbprint": "ABC123..."
}
```

### Verify SSL Certificate

```bash
# Check custom domains
az containerapp hostname list \
  --resource-group $RESOURCE_GROUP \
  --name $FRONTEND_APP \
  --output table
```

**Expected output**:
```
Name                        BindingType  CertificateId
--------------------------  -----------  -------------
app.yourdomain.com          SniEnabled   /subscriptions/.../certificates/...
```

### Test HTTPS

```bash
# Test custom domain with HTTPS
curl -I https://app.yourdomain.com

# Expected: HTTP/2 200
```

**In browser**: Open `https://app.yourdomain.com`
- ✅ Should show secure padlock icon
- ✅ Certificate should be valid (Let's Encrypt)
- ✅ Frontend application loads

---

## Step 4: Add Custom Domain to Backend (API)

### What You're Doing

Configuring the backend API to be accessible via `api.yourdomain.com` instead of the long Azure domain.

### Get Backend Verification ID

```bash
# Get backend verification ID
API_DOMAIN="api.yourdomain.com"

VERIFICATION_ID=$(az containerapp show \
  --name $BACKEND_APP \
  --resource-group $RESOURCE_GROUP \
  --query properties.customDomainVerificationId \
  --output tsv)

DEFAULT_API_DOMAIN=$(az containerapp show \
  --name $BACKEND_APP \
  --resource-group $RESOURCE_GROUP \
  --query properties.configuration.ingress.fqdn \
  --output tsv)

echo ""
echo "===================================================="
echo "DNS RECORDS TO ADD IN ROUTE 53 FOR API"
echo "===================================================="
echo ""
echo "1. TXT Record for Verification:"
echo "   Name:  asuid.${API_DOMAIN}"
echo "   Value: ${VERIFICATION_ID}"
echo ""
echo "2. CNAME Record for API Domain:"
echo "   Name:  ${API_DOMAIN}"
echo "   Value: ${DEFAULT_API_DOMAIN}"
echo ""
echo "===================================================="
```

### Add DNS Records in Route 53 for API

**In AWS Console → Route 53 → Your Domain**:

1. **Create TXT Record**:
   - **Record name**: `asuid.api`
   - **Record type**: **TXT**
   - **Value**: Verification ID from above
   - **TTL**: 300
   - Click **"Create records"**

2. **Create CNAME Record**:
   - **Record name**: `api`
   - **Record type**: **CNAME**
   - **Value**: `ca-taskapp-backend.redtree-99ec4a5a.centralus.azurecontainerapps.io`
   - **TTL**: 300
   - Click **"Create records"**

### Wait for DNS Propagation

```bash
# Wait 2-3 minutes, then verify:
dig asuid.api.yourdomain.com TXT +short
dig api.yourdomain.com CNAME +short

# Or on Windows:
nslookup -type=TXT asuid.api.yourdomain.com
nslookup api.yourdomain.com
```

### Add Custom Domain to Backend

```bash
# Add custom domain with managed certificate
az containerapp hostname add \
  --hostname $API_DOMAIN \
  --resource-group $RESOURCE_GROUP \
  --name $BACKEND_APP

# Bind the managed certificate
az containerapp hostname bind \
  --hostname $API_DOMAIN \
  --resource-group $RESOURCE_GROUP \
  --name $BACKEND_APP \
  --environment env-taskapp-prod \
  --validation-method CNAME
```

**⏰ Takes 3-5 minutes** for SSL certificate provisioning.

### Verify Backend API Domain

```bash
# Test API health endpoint
curl https://api.yourdomain.com/api/health

# Expected:
# {
#   "status": "healthy",
#   "service": "task-management-backend",
#   "message": "Service is running"
# }
```

**If successful**: ✅ Backend API is now accessible via custom domain!

---

## Step 5: Update Application Configuration

### What You're Doing

Updating the frontend to use the new API custom domain instead of the Azure default domain.

### Update Frontend Environment Variables

```bash
# Update frontend to use custom API domain
API_DOMAIN="api.yourdomain.com"

az containerapp update \
  --name $FRONTEND_APP \
  --resource-group $RESOURCE_GROUP \
  --replace-env-vars "NEXT_PUBLIC_API_URL=https://${API_DOMAIN}" "NODE_ENV=production"
```

**⏰ Takes 1-2 minutes** - new revision being deployed.

### Update Backend CORS

```bash
# Update backend CORS to allow new frontend domain
FRONTEND_DOMAIN="app.yourdomain.com"

az containerapp update \
  --name $BACKEND_APP \
  --resource-group $RESOURCE_GROUP \
  --set-env-vars "CORS_ORIGINS=https://${FRONTEND_DOMAIN}"
```

**⏰ Takes 1-2 minutes** - backend restarting.

### Verify Environment Variables

```bash
# Verify frontend env vars
az containerapp show \
  --name $FRONTEND_APP \
  --resource-group $RESOURCE_GROUP \
  --query "properties.template.containers[0].env" \
  --output table

# Expected:
# Name                    Value
# ----------------------  ----------------------------
# NEXT_PUBLIC_API_URL     https://api.yourdomain.com
# NODE_ENV                production

# Verify backend env vars
az containerapp show \
  --name $BACKEND_APP \
  --resource-group $RESOURCE_GROUP \
  --query "properties.template.containers[0].env" \
  --output table

# Expected CORS_ORIGINS: https://app.yourdomain.com
```

---

## Step 6: Test Custom Domain

### What You're Testing

Verifying the entire application works with custom domains.

### Test 1: Frontend Loads

1. **Open browser** and go to: `https://app.yourdomain.com`

2. **Check**:
   - ✅ Page loads successfully
   - ✅ HTTPS padlock icon visible
   - ✅ No certificate errors
   - ✅ No console errors in DevTools (F12)

### Test 2: API Calls Work

1. **Open DevTools** (F12) → Network tab

2. **Navigate to Register/Login page**

3. **Check Network tab**:
   - ✅ API requests go to `https://api.yourdomain.com`
   - ✅ No CORS errors
   - ✅ Requests succeed (200 OK)

### Test 3: Complete User Flow

1. **Register a new user**:
   - Username: `customdomaintest`
   - Email: `customdomain@example.com`
   - Password: `CustomTest123!@#`
   - Full Name: `Custom Domain Test`

2. **Check Network tab**:
   - Request URL: `https://api.yourdomain.com/api/auth/register`
   - Status: 200 OK or 201 Created

3. **Login with created user**

4. **Navigate to Dashboard**
   - Should load successfully
   - API requests should go to `api.yourdomain.com`

**If all tests pass**: ✅ Custom domain fully configured!

### Test 4: Certificate Validity

```bash
# Check SSL certificate details
openssl s_client -connect app.yourdomain.com:443 -servername app.yourdomain.com < /dev/null 2>/dev/null | openssl x509 -noout -dates

# Expected output:
# notBefore=Feb  2 12:00:00 2026 GMT
# notAfter=May   3 12:00:00 2026 GMT
```

**In browser**:
1. Click padlock icon in address bar
2. Click "Certificate"
3. Verify:
   - ✅ Issued by: Let's Encrypt
   - ✅ Valid for: `app.yourdomain.com`
   - ✅ Expires in ~90 days

---

## Step 7: Optional - Add WWW Redirect

### What You're Doing

Redirecting `www.yourdomain.com` to `app.yourdomain.com` (or vice versa).

### Option A: Add WWW as Additional Domain

```bash
# Add www subdomain
WWW_DOMAIN="www.yourdomain.com"

# Add DNS records in Route 53:
# TXT: asuid.www.yourdomain.com → Verification ID
# CNAME: www.yourdomain.com → ca-taskapp-frontend...azurecontainerapps.io

# Then add to Container App:
az containerapp hostname add \
  --hostname $WWW_DOMAIN \
  --resource-group $RESOURCE_GROUP \
  --name $FRONTEND_APP

az containerapp hostname bind \
  --hostname $WWW_DOMAIN \
  --resource-group $RESOURCE_GROUP \
  --name $FRONTEND_APP \
  --environment env-taskapp-prod \
  --validation-method CNAME
```

### Option B: Route 53 Redirect (Simpler)

**Not directly supported** - Route 53 doesn't have built-in redirects like Cloudflare. You'd need:
- S3 bucket for redirect (adds complexity)
- Or just accept both `www` and non-www` work

**Recommendation**: Skip WWW redirect for now.

---

## Phase 8 Completion Checklist

Use this checklist to verify everything is complete:

### ✅ DNS Configuration

- [ ] TXT record added in Route 53 for frontend domain verification
- [ ] CNAME record added in Route 53 for frontend domain
- [ ] TXT record added in Route 53 for API domain verification
- [ ] CNAME record added in Route 53 for API domain
- [ ] DNS records verified (dig/nslookup)

### ✅ Custom Domains in Azure

- [ ] Custom domain added to frontend Container App
- [ ] Custom domain verified and validated
- [ ] Custom domain added to backend Container App
- [ ] Custom domain verified and validated

### ✅ SSL Certificates

- [ ] Managed certificate provisioned for frontend domain
- [ ] Managed certificate bound to frontend domain
- [ ] Managed certificate provisioned for API domain
- [ ] Managed certificate bound to API domain
- [ ] HTTPS works on both domains (padlock icon visible)
- [ ] No certificate errors

### ✅ Application Configuration

- [ ] Frontend NEXT_PUBLIC_API_URL updated to custom API domain
- [ ] Backend CORS_ORIGINS updated to custom frontend domain
- [ ] Environment variables verified

### ✅ Testing & Verification

- [ ] Frontend loads at custom domain (https://app.yourdomain.com)
- [ ] API health endpoint works (https://api.yourdomain.com/api/health)
- [ ] User registration works via custom domain
- [ ] User login works via custom domain
- [ ] Dashboard loads via custom domain
- [ ] No CORS errors in browser console
- [ ] All API requests go to custom API domain

---

## Verification Commands

Run these commands to verify Phase 8 completion:

```bash
# Set your domains
FRONTEND_DOMAIN="app.yourdomain.com"
API_DOMAIN="api.yourdomain.com"

# Verify DNS records
echo "Checking DNS records..."
dig $FRONTEND_DOMAIN CNAME +short
dig $API_DOMAIN CNAME +short
dig asuid.$FRONTEND_DOMAIN TXT +short
dig asuid.$API_DOMAIN TXT +short

# Verify custom domains in Azure
echo ""
echo "Checking custom domains in Azure..."
az containerapp hostname list --name ca-taskapp-frontend --resource-group rg-taskapp-prod --output table
az containerapp hostname list --name ca-taskapp-backend --resource-group rg-taskapp-prod --output table

# Test frontend HTTPS
echo ""
echo "Testing frontend HTTPS..."
curl -I https://$FRONTEND_DOMAIN

# Test API HTTPS
echo ""
echo "Testing API HTTPS..."
curl https://$API_DOMAIN/api/health

# Check environment variables
echo ""
echo "Checking environment variables..."
az containerapp show --name ca-taskapp-frontend --resource-group rg-taskapp-prod --query "properties.template.containers[0].env" --output table
az containerapp show --name ca-taskapp-backend --resource-group rg-taskapp-prod --query "properties.template.containers[0].env" --output table
```

**Expected results**:
- ✅ DNS records resolve correctly
- ✅ Both custom domains listed in Azure
- ✅ Frontend returns HTTP/2 200
- ✅ API health returns {"status": "healthy"}
- ✅ Environment variables show custom domains

---

## Common Issues & Troubleshooting

### Issue 1: "Unable to verify domain ownership"

**Symptoms**:
```
az containerapp hostname add fails with "Unable to verify domain ownership"
```

**Causes**:
- TXT record not created in Route 53
- TXT record not propagated yet
- Wrong TXT record value

**Solutions**:

```bash
# 1. Verify TXT record exists in Route 53
# Go to AWS Console → Route 53 → Your domain
# Check for: asuid.app.yourdomain.com TXT record

# 2. Wait for DNS propagation (5-10 minutes)
dig asuid.app.yourdomain.com TXT +short

# 3. Verify verification ID matches
az containerapp show --name ca-taskapp-frontend --resource-group rg-taskapp-prod --query properties.customDomainVerificationId -o tsv
```

---

### Issue 2: CNAME Record Not Resolving

**Symptoms**:
```
dig app.yourdomain.com returns no results
```

**Causes**:
- CNAME record not created in Route 53
- Wrong CNAME value
- DNS propagation delay

**Solutions**:

```bash
# 1. Check CNAME in Route 53
# Should point to: ca-taskapp-frontend.redtree-99ec4a5a.centralus.azurecontainerapps.io

# 2. Wait 5-10 minutes for propagation

# 3. Test with different DNS server
dig @8.8.8.8 app.yourdomain.com CNAME +short
```

---

### Issue 3: SSL Certificate Provisioning Failed

**Symptoms**:
```
Certificate status: Failed
```

**Causes**:
- DNS records not configured correctly
- Domain ownership not verified
- Let's Encrypt rate limit hit

**Solutions**:

```bash
# 1. Verify both TXT and CNAME records exist
dig asuid.app.yourdomain.com TXT +short
dig app.yourdomain.com CNAME +short

# 2. Check certificate status
az containerapp hostname list --name ca-taskapp-frontend --resource-group rg-taskapp-prod --output table

# 3. If failed, remove and re-add domain
az containerapp hostname delete --hostname app.yourdomain.com --name ca-taskapp-frontend --resource-group rg-taskapp-prod --yes

# Wait 15 minutes, then re-add
az containerapp hostname add --hostname app.yourdomain.com --name ca-taskapp-frontend --resource-group rg-taskapp-prod
```

---

### Issue 4: CORS Errors After Domain Change

**Symptoms**:
```
Browser console: "Access to fetch at 'https://api.yourdomain.com' has been blocked by CORS policy"
```

**Cause**: Backend CORS not updated with new frontend domain.

**Solution**:

```bash
# Update backend CORS
az containerapp update \
  --name ca-taskapp-backend \
  --resource-group rg-taskapp-prod \
  --set-env-vars "CORS_ORIGINS=https://app.yourdomain.com"

# Wait 1-2 minutes for backend to restart
# Then test again in browser
```

---

### Issue 5: Frontend Still Uses Old API URL

**Symptoms**: Network tab shows requests to `ca-taskapp-backend.redtree-99ec4a5a...` instead of `api.yourdomain.com`

**Cause**: Frontend environment variable not updated.

**Solution**:

```bash
# Update frontend env var
az containerapp update \
  --name ca-taskapp-frontend \
  --resource-group rg-taskapp-prod \
  --replace-env-vars "NEXT_PUBLIC_API_URL=https://api.yourdomain.com" "NODE_ENV=production"

# Wait 1-2 minutes for frontend to redeploy
# Hard refresh browser (Ctrl+Shift+R)
```

---

## Certificate Auto-Renewal

### How It Works

Azure automatically renews Let's Encrypt certificates:
- **Issued**: Valid for 90 days
- **Auto-renewal**: Starts 30 days before expiration
- **No action required**: Fully automatic

### Monitoring Renewal

```bash
# Check certificate expiration
az containerapp hostname list \
  --name ca-taskapp-frontend \
  --resource-group rg-taskapp-prod \
  --query "[].{Domain:name, Thumbprint:thumbprint}" \
  --output table
```

**Set up alerts** (Phase 9: Monitoring):
- Alert if certificate expires in <15 days
- Alert if renewal fails

---

## Cost Estimate

**Phase 8 Custom Domain & SSL**:
- Custom domains: **Free**
- Managed SSL certificates: **Free** (Let's Encrypt)
- DNS queries in Route 53: **~$0.50/month** (first 1M queries/month)

**Total additional cost**: **~$0.50/month**

---

## Summary

**What You Accomplished in Phase 8**:

✅ Configured custom domains for frontend and backend  
✅ Updated DNS records in AWS Route 53  
✅ Provisioned free SSL/TLS certificates (Let's Encrypt)  
✅ Verified domain ownership via TXT records  
✅ Updated application configuration to use custom domains  
✅ Tested complete application with custom domains  
✅ HTTPS working with valid certificates  

**Your Application URLs** (updated):
- **Frontend**: https://app.yourdomain.com (or your chosen domain)
- **Backend API**: https://api.yourdomain.com
- **Old URLs**: Still work but redirect/coexist with new domains

**Domain Provider**: AWS Route 53 (DNS)  
**Hosting Provider**: Azure Container Apps  
**SSL Certificates**: Free managed certificates (auto-renewing)

**Next Phase**: Monitoring, logging, and observability!

🎉 **Congratulations! Your application now has a professional custom domain with HTTPS!** 🎉
