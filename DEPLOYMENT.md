# Deployment Guide - Task Management Application

## Overview
This guide covers deploying the containerized Task Management Application using Docker images from Docker Hub.

## Quick Start (5 Minutes)

### Prerequisites
- Docker installed (version 20.10+)
- Docker Compose installed (version 2.0+)
- 2GB+ available RAM
- Ports 3000, 5000, 5432 available

### Instant Deployment
```bash
# 1. Clone the repository
git clone https://github.com/vee-kay8/task-management-app.git
cd task-management-app

# 2. Create environment file
cp .env.production .env

# 3. Update secrets (IMPORTANT!)
# Edit .env and replace all CHANGE_THIS values
nano .env

# 4. Deploy with Docker Compose
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d

# 5. Access the application
# Frontend: http://localhost:3000
# Backend API: http://localhost:5000
```

## Deployment Options

### Option 1: Production Deployment (Recommended)
Uses pre-built images from Docker Hub with production configurations.

```bash
# Pull latest images
docker pull veekay8/task-management-backend:1.0.0
docker pull veekay8/task-management-frontend:1.0.0

# Deploy with production settings
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d

# Check status
docker-compose ps
```

**Features**:
- Pre-built optimized images (no build time)
- Resource limits configured
- Production logging enabled
- Automatic restarts enabled

### Option 2: Development Deployment
Builds images locally with development configurations.

```bash
# Create development environment
cp .env.development .env

# Build and deploy
docker-compose up -d --build

# View logs
docker-compose logs -f
```

**Features**:
- Debug mode enabled
- Verbose logging
- Hot-reload capable (with volume mounts)
- Simple development passwords

### Option 3: Hybrid Deployment
Uses Docker Hub images but with local environment customization.

```bash
# Use production images but custom environment
cp .env.example .env
# Edit .env with your settings

# Deploy base compose (pulls from Docker Hub)
docker-compose up -d
```

## Docker Hub Images

### Available Images
- **Backend**: `veekay8/task-management-backend`
- **Frontend**: `veekay8/task-management-frontend`

### Image Tags
| Tag | Description | Use Case |
|-----|-------------|----------|
| `1.0.0` | Specific version | Production (pinned) |
| `1.0` | Latest patch of 1.0.x | Stable with patches |
| `1` | Latest minor of 1.x.x | Feature updates |
| `latest` | Most recent release | Development/Testing |

### Pulling Images
```bash
# Pull specific version (recommended for production)
docker pull veekay8/task-management-backend:1.0.0
docker pull veekay8/task-management-frontend:1.0.0

# Pull latest (for development)
docker pull veekay8/task-management-backend:latest
docker pull veekay8/task-management-frontend:latest
```

## Environment Configuration

### Required Environment Variables
```bash
# Database
POSTGRES_DB=taskmanagement_db
POSTGRES_USER=taskapp_user
POSTGRES_PASSWORD=<strong-password>  # CHANGE THIS!

# Backend Security
SECRET_KEY=<64-char-random-hex>      # CHANGE THIS!
JWT_SECRET_KEY=<64-char-random-hex>  # CHANGE THIS!

# Frontend
NEXT_PUBLIC_API_URL=http://localhost:5000/api
```

### Generate Secure Keys
```bash
# Generate SECRET_KEY
python -c "import secrets; print(secrets.token_hex(32))"

# Generate JWT_SECRET_KEY (use different value)
python -c "import secrets; print(secrets.token_hex(32))"
```

### Environment Files
- `.env.example` - Template with all variables
- `.env.development` - Development preset
- `.env.production` - Production template
- `.env` - Active configuration (not in git)

## Deployment Workflows

### Initial Production Deployment
```bash
# 1. Prepare environment
git clone <repository>
cd task-management-app
cp .env.production .env

# 2. Generate secrets
export SECRET_KEY=$(python -c "import secrets; print(secrets.token_hex(32))")
export JWT_SECRET_KEY=$(python -c "import secrets; print(secrets.token_hex(32))")

# 3. Update .env file
sed -i "s/GENERATE_RANDOM_64_CHAR_HEX_STRING_HERE/$SECRET_KEY/" .env
sed -i "s/GENERATE_DIFFERENT_RANDOM_64_CHAR_HEX_STRING_HERE/$JWT_SECRET_KEY/" .env

# 4. Deploy
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d

# 5. Verify health
docker-compose ps
curl http://localhost:5000/api/health
curl http://localhost:3000/api/health
```

### Updating to New Version
```bash
# 1. Pull new images
docker pull veekay8/task-management-backend:1.1.0
docker pull veekay8/task-management-frontend:1.1.0

# 2. Update docker-compose.prod.yml with new version tags
sed -i 's/:1.0.0/:1.1.0/g' docker-compose.prod.yml

# 3. Recreate containers
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d

# 4. Verify deployment
docker-compose ps
```

### Rollback to Previous Version
```bash
# 1. Update to previous version tags
sed -i 's/:1.1.0/:1.0.0/g' docker-compose.prod.yml

# 2. Recreate containers
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d

# 3. Verify rollback
docker-compose ps
```

## Production Checklist

### Pre-Deployment
- [ ] Docker and Docker Compose installed
- [ ] Ports 3000, 5000, 5432 available
- [ ] Environment variables configured in `.env`
- [ ] Strong passwords generated for all secrets
- [ ] Database backup strategy in place
- [ ] SSL/TLS certificates ready (if using HTTPS)

### Security
- [ ] `SECRET_KEY` is random 64-character hex string
- [ ] `JWT_SECRET_KEY` is different random 64-character hex
- [ ] `POSTGRES_PASSWORD` is strong and unique
- [ ] `.env` file is NOT committed to git
- [ ] `FLASK_DEBUG=False` in production
- [ ] CORS origins updated to production domains
- [ ] All URLs using HTTPS in production

### Infrastructure
- [ ] Adequate server resources (2GB+ RAM recommended)
- [ ] Database backups automated
- [ ] Log rotation configured
- [ ] Monitoring/alerting set up
- [ ] Firewall rules configured

### Testing
- [ ] Health endpoints responding
- [ ] Database connection successful
- [ ] Frontend can reach backend API
- [ ] User registration works
- [ ] User login works
- [ ] All API endpoints functional

## Common Commands

### Container Management
```bash
# Start all services
docker-compose up -d

# Stop all services
docker-compose down

# Restart specific service
docker-compose restart backend

# View logs (all services)
docker-compose logs -f

# View logs (specific service)
docker-compose logs -f backend

# Check service status
docker-compose ps

# Execute command in container
docker-compose exec backend sh
```

### Database Operations
```bash
# Connect to PostgreSQL
docker-compose exec db psql -U taskapp_user -d taskmanagement_db

# Backup database
docker-compose exec db pg_dump -U taskapp_user taskmanagement_db > backup.sql

# Restore database
docker-compose exec -T db psql -U taskapp_user -d taskmanagement_db < backup.sql

# View database logs
docker-compose logs -f db
```

### Maintenance
```bash
# Pull latest images
docker-compose pull

# Remove unused images
docker image prune -a

# View resource usage
docker stats

# Clean up everything (CAUTION: destroys data)
docker-compose down -v
```

## Monitoring

### Health Checks
```bash
# Backend health
curl http://localhost:5000/api/health

# Frontend health
curl http://localhost:3000/api/health

# Expected response:
# {"status": "healthy", "service": "task-management-backend"}
```

### Container Logs
```bash
# Last 50 lines
docker-compose logs --tail=50

# Since timestamp
docker-compose logs --since 10m

# Follow logs in real-time
docker-compose logs -f
```

### Resource Usage
```bash
# All containers
docker stats

# Specific container
docker stats taskmanagement_backend
```

## Troubleshooting

### Services Not Starting
```bash
# Check logs
docker-compose logs -f

# Verify environment variables
docker-compose config

# Check port conflicts
lsof -i :3000
lsof -i :5000
lsof -i :5432
```

### Database Connection Errors
```bash
# Verify database is healthy
docker-compose ps db

# Check database logs
docker-compose logs -f db

# Test connection
docker-compose exec db psql -U taskapp_user -d taskmanagement_db -c "SELECT 1;"
```

### Image Pull Failures
```bash
# Login to Docker Hub
docker login

# Manually pull images
docker pull veekay8/task-management-backend:1.0.0
docker pull veekay8/task-management-frontend:1.0.0

# Check Docker Hub status
# Visit: https://status.docker.com
```

### Frontend Can't Reach Backend
```bash
# Verify backend is running
curl http://localhost:5000/api/health

# Check CORS settings in .env
grep CORS_ORIGINS .env

# Verify NEXT_PUBLIC_API_URL
grep NEXT_PUBLIC_API_URL .env
```

## Architecture

### Service Communication
```
┌─────────────────────────────────────────────┐
│          Docker Compose Stack               │
├─────────────────────────────────────────────┤
│                                             │
│  Frontend (3000) → Backend (5000) → DB      │
│       ↓                ↓            ↓       │
│   Next.js          Flask      PostgreSQL    │
│   168MB            215MB        ~25MB       │
│                                             │
│         taskapp_network (bridge)            │
└─────────────────────────────────────────────┘
```

### Port Mapping
- **3000**: Frontend (Next.js)
- **5000**: Backend API (Flask)
- **5432**: Database (PostgreSQL)

### Data Persistence
- Database data: `postgres_data` named volume
- Survives container restarts and recreates
- Backup with `docker-compose exec db pg_dump`

## Performance Tuning

### Resource Limits (Production)
Already configured in `docker-compose.prod.yml`:

**Database**:
- CPU: 2 cores max, 1 core reserved
- RAM: 2GB max, 1GB reserved

**Backend**:
- CPU: 2 cores max, 0.5 cores reserved
- RAM: 1GB max, 512MB reserved

**Frontend**:
- CPU: 1 core max, 0.25 cores reserved
- RAM: 512MB max, 256MB reserved

### Database Connection Pool
Edit `.env`:
```bash
DB_POOL_SIZE=20          # For high traffic
DB_MAX_OVERFLOW=40
```

## Security Best Practices

### Container Security
- ✅ Running as non-root users (appuser, nextjs)
- ✅ Multi-stage builds (minimal attack surface)
- ✅ Health checks enabled
- ✅ Resource limits configured
- ✅ Log rotation enabled

### Secrets Management
- ✅ No secrets in docker-compose.yml
- ✅ Environment variables in .env (not committed)
- ✅ Strong key generation documented
- ✅ Production checklist included

### Network Security
- ✅ Isolated bridge network (taskapp_network)
- ✅ Services communicate via service names
- ✅ CORS configured and restrictive
- ⚠️ Consider adding HTTPS/TLS in production
- ⚠️ Consider adding rate limiting

## Support

### Documentation
- `CONTAINERIZATION_PHASE1.md` - Backend containerization
- `CONTAINERIZATION_PHASE2.md` - Frontend containerization
- `CONTAINERIZATION_PHASE3.md` - Docker Compose orchestration
- `CONTAINERIZATION_PHASE4.md` - Environment management
- `DOCKER_HUB_CONFIG.md` - Image tagging and versioning

### Docker Hub Repositories
- Backend: https://hub.docker.com/r/veekay8/task-management-backend
- Frontend: https://hub.docker.com/r/veekay8/task-management-frontend

### Version Information
Current Version: **1.0.0**
Last Updated: January 2, 2026

## License
See LICENSE file in repository.
