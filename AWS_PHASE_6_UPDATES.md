# Phase 6 Guide Updates - ECS Deployment Approach

**Date**: January 21, 2026  
**Change**: Switched from S3/CloudFront static hosting to ECS Fargate deployment

---

## What Changed and Why

### Original Approach (S3 + CloudFront)
- Frontend built with `output: 'export'` for static HTML export
- Hosted on S3 bucket
- Served via CloudFront CDN
- Cost: ~$1-2/month
- **Problem**: Next.js App Router with dynamic routes (`/projects/[id]`) and authentication incompatible with static export

### New Approach (ECS Fargate)
- Frontend built with `output: 'standalone'` for Docker deployment
- Hosted on ECS Fargate (same as backend)
- Served via same ALB with path-based routing
- Cost: ~$10/month
- **Solution**: Full Next.js features work (SSR, dynamic routes, authentication, middleware)

---

## Why ECS Instead of S3?

Your task management app requires:
1. **Dynamic Content**: Users create projects and tasks constantly
2. **Authentication**: Protected routes with JWT tokens
3. **Client-Side Routing**: Dynamic route parameters (`/projects/[id]`)
4. **Server Features**: Next.js middleware, headers, rewrites

**Static export limitations:**
- All pages must be pre-rendered at build time
- Cannot use dynamic routes with `'use client'`
- `generateStaticParams()` doesn't work with client components
- No server-side features

**ECS benefits:**
- Full Next.js functionality
- Server-side rendering on demand
- Dynamic routes work seamlessly
- Same deployment pattern as backend (consistency)
- Single ALB for both services (simpler architecture)

---

## Documents Updated

### 1. AWS_PHASE_6_GUIDE.md
**Status**: ✅ Completely rewritten

**Changes:**
- Title: "S3 + CloudFront" → "ECS Fargate"
- Overview: Static hosting → Container orchestration
- 12 steps completely rewritten:
  1. Verify frontend environment configuration
  2. Build Docker image for frontend
  3. Push frontend image to ECR
  4. Create CloudWatch log group
  5. Create frontend task definition
  6. Create frontend target group
  7. Update ALB with path-based routing
  8. Create frontend ECS service
  9. Monitor frontend deployment
  10. Test frontend application
  11. Update frontend to use relative API paths
  12. Update backend CORS (optional)
- Cost: ~$1-2/month → ~$10/month
- Total infrastructure: ~$94/month

**Key additions:**
- Docker build instructions
- ECR authentication and push
- Task definition with environment variables
- ALB listener rules for path routing (`/api/*` → backend, `/*` → frontend)
- Target group configuration
- ECS service creation with load balancer integration
- Troubleshooting for ECS-specific issues

### 2. AWS_DEPLOYMENT_ROADMAP.md
**Status**: ✅ Updated

**Changes:**
- Phase 6 title: "S3 + CloudFront" → "ECS Fargate"
- Phase 6 status: "Not Started" → "In Progress (20%)"
- Updated checklist:
  - ✅ Update frontend environment variable (API URL to ALB)
  - ✅ Update frontend API client to call real backend
  - ✅ Build frontend for production (standalone mode)
  - ⏳ Build Docker image for frontend
  - ⏳ Push frontend image to ECR
  - ⏳ Create CloudWatch log group for frontend
  - ⏳ Create frontend task definition
  - ⏳ Create frontend target group
  - ⏳ Configure ALB path-based routing
  - ⏳ Create frontend ECS service
  - ⏳ Test full application flow
- Updated deliverables:
  - "Frontend deployed to S3" → "Frontend deployed to ECS Fargate"
  - "CloudFront distribution" → "Path-based routing on ALB"
  - "HTTPS enabled automatically" → "2 frontend tasks for high availability"
- Updated resources:
  - Removed: S3 bucket, CloudFront distribution
  - Added: Frontend task definition, service, target group, CloudWatch log group
- Updated Phase 11 (Cost Optimization):
  - Removed: CloudFront caching, S3 lifecycle policies, S3 versioning
  - Added: Review ALB listener rules, ECS auto-scaling for both services
- Updated Phase 10 (CI/CD):
  - "Deploy frontend to S3" → "CI/CD updates for ECS deployments"
  - "CloudFront invalidation" → removed
- Updated cost breakdown:
  - Added detailed monthly costs table
  - Total: ~$94/month
  - Listed cost optimization options

### 3. frontend/next.config.js
**Status**: ✅ Reverted to original

**Changes:**
- `output: 'export'` → `output: 'standalone'` (Docker mode)
- Removed `images.unoptimized: true`
- Removed `trailingSlash: true`
- Back to original Docker-ready configuration

### 4. frontend/.env.production
**Status**: ✅ Already configured

**Current:**
```env
NEXT_PUBLIC_API_URL=http://taskapp-alb-1878540875.us-east-1.elb.amazonaws.com
```

**After Phase 6 completion (optional):**
```env
NEXT_PUBLIC_API_URL=/api
```
*(Can use relative paths since both services behind same ALB)*

### 5. frontend/lib/api.ts
**Status**: ✅ Already updated

**Changes:**
- Completely rewritten from mock data to real API calls
- Added `fetchWithAuth()` helper
- All endpoints call real backend via ALB

---

## What You've Completed So Far (Phase 6)

✅ **Step 1**: Frontend environment configured (.env.production)  
✅ **Step 2**: API client updated to call real backend  
✅ **Step 3**: Frontend built successfully with `standalone` mode  
✅ **Documentation**: Phase 6 guide completely rewritten for ECS  

---

## Next Steps (Complete Phase 6)

Follow the updated [AWS_PHASE_6_GUIDE.md](AWS_PHASE_6_GUIDE.md):

### Step 2: Build Docker Image
```bash
cd frontend
docker build -t taskapp-frontend:latest .
```

### Step 3: Push to ECR
```bash
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin 858448674350.dkr.ecr.us-east-1.amazonaws.com

docker tag taskapp-frontend:latest 858448674350.dkr.ecr.us-east-1.amazonaws.com/taskapp-frontend:latest
docker push 858448674350.dkr.ecr.us-east-1.amazonaws.com/taskapp-frontend:latest
```

### Step 4-8: Create Infrastructure
- CloudWatch log group
- Frontend task definition (similar to backend)
- Frontend target group (port 3000)
- Update ALB listener rules (path-based routing)
- Create frontend ECS service (2 tasks)

### Step 9-12: Test and Optimize
- Monitor deployment
- Test via ALB URL
- Update to relative API paths
- Verify CORS settings

---

## Architecture Comparison

### Before (S3 + CloudFront)
```
User → CloudFront → S3 (Frontend Static Files)
         ↓
       ALB → ECS (Backend API)
```

**Problems:**
- Two separate domains
- CORS complexity
- Static export limitations
- Cannot use dynamic Next.js features

### After (ECS + Path Routing)
```
User → ALB
       ├─ /api/* → Backend ECS (Port 5000)
       └─ /*     → Frontend ECS (Port 3000)
```

**Benefits:**
- Single domain
- Simplified CORS (same origin)
- Full Next.js features
- Consistent deployment pattern
- Path-based routing

---

## Cost Comparison

| Component | S3 Approach | ECS Approach |
|-----------|-------------|--------------|
| Frontend Hosting | S3: Free tier | ECS: ~$10/month |
| CDN | CloudFront: Free tier | N/A (ALB handles) |
| Backend | ECS: ~$18/month | ECS: ~$18/month |
| Database | RDS: ~$15/month | RDS: ~$15/month |
| Load Balancer | ALB: ~$16/month | ALB: ~$16/month |
| NAT Gateway | NAT: ~$33/month | NAT: ~$33/month |
| **Total** | **~$84/month** | **~$94/month** |

**Difference**: +$10/month for full Next.js functionality and simpler architecture

---

## Lessons Learned

1. **Static Export ≠ Universal Solution**
   - Not all Next.js apps can be statically exported
   - Dynamic routes with client components need server rendering

2. **Build Modes Matter**
   - `output: 'export'` - Static HTML files (limited)
   - `output: 'standalone'` - Minimal Node server (full features)

3. **Architecture Alignment**
   - Mixing S3 and ECS adds complexity
   - Unified ECS approach simpler for full-stack apps

4. **Cost vs Features**
   - $10/month extra worth it for full functionality
   - Production apps need server-side features

5. **Path-Based Routing**
   - Single ALB can serve multiple services
   - `/api/*` and `/*` routing eliminates CORS issues

---

## Quick Reference

### Frontend Build
```bash
cd frontend
npm run build  # Creates .next/standalone/
```

### Docker Build
```bash
docker build -t taskapp-frontend:latest .
```

### ECR Push
```bash
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin 858448674350.dkr.ecr.us-east-1.amazonaws.com

docker tag taskapp-frontend:latest 858448674350.dkr.ecr.us-east-1.amazonaws.com/taskapp-frontend:latest
docker push 858448674350.dkr.ecr.us-east-1.amazonaws.com/taskapp-frontend:latest
```

### ALB DNS
```
http://taskapp-alb-1878540875.us-east-1.elb.amazonaws.com
```

### Target Routing
- Backend API: `http://alb-dns/api/`
- Frontend App: `http://alb-dns/`

---

## Summary

Phase 6 approach changed from **S3/CloudFront static hosting** to **ECS Fargate deployment** because:
- Your app uses dynamic user-generated content
- Authentication with JWT tokens requires server
- Next.js App Router dynamic routes need server-side rendering
- ECS provides full Next.js functionality
- Unified deployment pattern simpler than mixed architecture

**Trade-off**: +$10/month for production-ready features and architectural consistency.

**Status**: 
- ✅ Documentation updated
- ✅ Frontend code ready
- ⏳ Infrastructure deployment pending

Continue with [AWS_PHASE_6_GUIDE.md](AWS_PHASE_6_GUIDE.md) to complete deployment!
