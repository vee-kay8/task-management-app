# Phase 3 Quickstart Guide - Docker & Container Registry

## 🎯 What We're Doing

Containerizing your application with Docker for consistent deployments anywhere.

## ⚡ Quick Commands

### Build Docker Images Locally

```bash
# Build backend image
cd backend
docker build -t taskapp-backend:local .

# Build frontend image
cd ../frontend
docker build -t taskapp-frontend:local .

# Check built images
docker images | grep taskapp
```

### Run with Docker Compose

```bash
# Start all services (database + backend + frontend)
docker-compose up -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f

# Stop all services
docker-compose down

# Stop and remove all data
docker-compose down -v
```

### Access the Application

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:5000
- **Database**: localhost:5432

### Useful Docker Commands

```bash
# View running containers
docker ps

# View all containers (including stopped)
docker ps -a

# Stop a container
docker stop <container_name>

# Remove a container
docker rm <container_name>

# View container logs
docker logs <container_name>

# Execute command in running container
docker exec -it <container_name> /bin/bash

# Remove unused images
docker image prune

# Remove all unused data
docker system prune -a
```

### GitHub Container Registry

Images are automatically built and pushed to GHCR when you push to main/develop/CICD branches.

**View your images**:
```
https://github.com/vee-kay8?tab=packages
```

**Pull images**:
```bash
# Backend
docker pull ghcr.io/vee-kay8/task-management-app/backend:latest

# Frontend
docker pull ghcr.io/vee-kay8/task-management-app/frontend:latest
```

## 📦 What Was Created

### Files Added/Modified

1. **backend/Dockerfile** - Multi-stage backend image
2. **backend/.dockerignore** - Files to exclude from image
3. **frontend/Dockerfile** - Multi-stage frontend image  
4. **frontend/.dockerignore** - Files to exclude from image
5. **docker-compose.yml** - Local development orchestration
6. **.github/workflows/ci.yml** - Added Docker build/push job

### Docker Images

- **Backend**: Python 3.11 slim (~180MB)
- **Frontend**: Node 20 Alpine (~150MB)
- **Database**: PostgreSQL 15 Alpine (~230MB)

### CI/CD Updates

New job in GitHub Actions:
- ✅ Builds Docker images
- ✅ Pushes to GitHub Container Registry
- ✅ Tags with branch name + commit SHA
- ✅ Uses build cache for speed
- ✅ Only runs on push to main/develop/CICD

## 🏗️ Architecture

```
┌──────────────────────────────────────────────┐
│  Docker Compose                               │
│  ┌────────────┐  ┌────────────┐  ┌────────┐ │
│  │  Frontend  │  │  Backend   │  │   DB   │ │
│  │  (Next.js) │←→│  (Flask)   │←→│ (PG15) │ │
│  │  Port 3000 │  │  Port 5000 │  │  5432  │ │
│  └────────────┘  └────────────┘  └────────┘ │
│                                               │
│  Network: taskapp_network                     │
│  Volume: postgres_data (persistent)           │
└──────────────────────────────────────────────┘
```

## 🔍 Troubleshooting

### Build Fails

```bash
# Clean build (no cache)
docker build --no-cache -t taskapp-backend:local .

# Check for syntax errors
docker build -t test . --progress=plain
```

### Port Already in Use

```bash
# Find what's using the port (Windows)
netstat -ano | findstr :3000

# Kill the process or change port in docker-compose.yml
ports:
  - "3001:3000"  # Use different host port
```

### Container Exits Immediately

```bash
# Check logs
docker logs <container_name>

# Run interactively
docker run -it taskapp-backend:local /bin/bash
```

### Database Connection Issues

```bash
# Verify database is running
docker-compose ps

# Check database logs
docker-compose logs db

# Connect to database
docker-compose exec db psql -U taskapp_user -d taskmanagement_db
```

## 📊 Verify Everything Works

### 1. Build Images
```bash
cd backend && docker build -t test-backend . && cd ..
cd frontend && docker build -t test-frontend . && cd ..
```

### 2. Run Stack
```bash
docker-compose up -d
docker-compose ps  # All should be "Up (healthy)"
```

### 3. Test Endpoints
```bash
# Frontend
curl http://localhost:3000

# Backend health
curl http://localhost:5000/api/health

# Backend from frontend container
docker-compose exec frontend wget -O- http://backend:5000/api/health
```

### 4. Push to GitHub
```bash
git add .
git commit -m "feat: Add Docker containerization for Phase 3

- Added multi-stage Dockerfiles for backend and frontend
- Created docker-compose.yml for local development  
- Updated CI/CD to build and push images to GHCR
- Optimized images with .dockerignore files"

git push origin CICD
```

### 5. Verify CI/CD
- Go to https://github.com/vee-kay8/task-management-app/actions
- Check that docker-build-push job runs and succeeds
- Verify images appear in GitHub Packages

## 🎉 Success Criteria

- ✅ Backend Docker image builds successfully
- ✅ Frontend Docker image builds successfully
- ✅ `docker-compose up` runs entire stack
- ✅ Can access app at http://localhost:3000
- ✅ All health checks pass
- ✅ Images pushed to GitHub Container Registry
- ✅ CI/CD pipeline includes Docker build job

## 🚀 Next: Phase 4

With Docker images ready, we'll deploy to a staging environment!

- Deploy to cloud platform (AWS/GCP/Azure/Render)
- Set up environment variables
- Configure production database
- Implement monitoring and logging
