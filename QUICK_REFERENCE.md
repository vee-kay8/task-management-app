# Docker Quick Reference
## Task Management Application - Command Cheat Sheet

**Version**: 1.0.0 | **Date**: January 2, 2026

---

## 🚀 Quick Start (30 Seconds)

```bash
# Clone and start
git clone https://github.com/yourusername/task-management-app.git
cd task-management-app
cp .env.example .env
docker-compose -f docker-compose.hub.yml up -d

# Access
# Frontend: http://localhost:3000
# Backend:  http://localhost:5000
```

---

## 📋 Essential Commands

### Start Services

```bash
# Development (local build)
docker-compose up -d

# Production (Docker Hub)
docker-compose -f docker-compose.hub.yml up -d

# Production (with resource limits)
docker-compose -f docker-compose.hub.yml -f docker-compose.prod.yml up -d

# Build and start
docker-compose up --build -d

# Start specific service
docker-compose up -d backend
```

### Stop Services

```bash
# Stop all (keeps containers)
docker-compose stop

# Stop and remove containers
docker-compose down

# Stop and remove everything (⚠️ deletes data)
docker-compose down -v

# Stop specific service
docker-compose stop backend
```

### Restart Services

```bash
# Restart all
docker-compose restart

# Restart specific service
docker-compose restart backend

# Full restart (rebuild)
docker-compose down && docker-compose up --build -d
```

---

## 🔍 Monitoring & Debugging

### Check Status

```bash
# Service status
docker-compose ps

# Detailed status
docker-compose ps -a

# Resource usage
docker stats

# System info
docker system df
```

### View Logs

```bash
# All services (follow)
docker-compose logs -f

# Specific service
docker-compose logs -f backend
docker-compose logs -f frontend
docker-compose logs -f db

# Last 50 lines
docker-compose logs --tail=50

# Since specific time
docker-compose logs --since 2026-01-02T10:00:00

# Save logs to file
docker-compose logs > logs.txt
```

### Interactive Shell

```bash
# Backend shell
docker-compose exec backend sh

# Frontend shell
docker-compose exec frontend sh

# Database shell
docker-compose exec db psql -U taskuser -d taskdb

# Root shell (debugging)
docker-compose exec --user root backend sh
```

---

## 🏥 Health Checks

### Test Endpoints

```bash
# Backend health
curl http://localhost:5000/api/health

# Frontend health
curl http://localhost:3000/api/health

# With response time
time curl http://localhost:5000/api/health

# Check all health status
docker-compose ps | grep -E "(healthy|unhealthy)"
```

### Database Health

```bash
# Check if database is ready
docker-compose exec db pg_isready -U taskuser

# List databases
docker-compose exec db psql -U taskuser -c "\l"

# List tables
docker-compose exec db psql -U taskuser -d taskdb -c "\dt"

# Check connections
docker-compose exec db psql -U taskuser -d taskdb -c "SELECT count(*) FROM pg_stat_activity;"
```

---

## 🗄️ Database Operations

### Backup

```bash
# Backup database to file
docker exec taskmanagement_postgres pg_dump -U taskuser taskdb > backup_$(date +%Y%m%d).sql

# Backup with compression
docker exec taskmanagement_postgres pg_dump -U taskuser taskdb | gzip > backup.sql.gz

# Backup volume
docker run --rm -v postgres_data:/data -v $(pwd):/backup alpine tar czf /backup/postgres_data.tar.gz /data
```

### Restore

```bash
# Restore from backup
cat backup.sql | docker exec -i taskmanagement_postgres psql -U taskuser taskdb

# Restore from compressed
gunzip -c backup.sql.gz | docker exec -i taskmanagement_postgres psql -U taskuser taskdb

# Restore volume
docker run --rm -v postgres_data:/data -v $(pwd):/backup alpine tar xzf /backup/postgres_data.tar.gz -C /
```

### Maintenance

```bash
# Run vacuum
docker-compose exec db psql -U taskuser -d taskdb -c "VACUUM ANALYZE;"

# Check database size
docker-compose exec db psql -U taskuser -d taskdb -c "SELECT pg_size_pretty(pg_database_size('taskdb'));"

# Check table sizes
docker-compose exec db psql -U taskuser -d taskdb -c "
  SELECT tablename, pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) 
  FROM pg_tables WHERE schemaname = 'public' 
  ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;"
```

---

## 🏗️ Build & Deploy

### Local Build

```bash
# Build all services
docker-compose build

# Build specific service
docker-compose build backend

# Build without cache
docker-compose build --no-cache

# Build with BuildKit (faster)
DOCKER_BUILDKIT=1 docker-compose build

# Parallel build
docker-compose build --parallel
```

### Docker Hub

```bash
# Login
docker login

# Pull images
docker-compose -f docker-compose.hub.yml pull

# Tag images
VERSION=1.0.0
docker tag task-backend veekay8/task-management-backend:$VERSION
docker tag task-frontend veekay8/task-management-frontend:$VERSION

# Push images
docker push veekay8/task-management-backend:$VERSION
docker push veekay8/task-management-frontend:$VERSION

# Multi-tag push
docker push veekay8/task-management-backend:1.0.0
docker push veekay8/task-management-backend:1.0
docker push veekay8/task-management-backend:1
docker push veekay8/task-management-backend:latest
```

---

## 🧹 Cleanup

### Safe Cleanup

```bash
# Remove stopped containers
docker container prune

# Remove unused images
docker image prune

# Remove unused volumes
docker volume prune

# Remove unused networks
docker network prune
```

### Aggressive Cleanup

```bash
# Remove all stopped containers
docker container prune -a

# Remove all unused images
docker image prune -a

# Full system cleanup (⚠️ dangerous)
docker system prune -a --volumes

# Remove specific service
docker-compose stop backend
docker-compose rm -f backend
```

### Project Cleanup

```bash
# Stop and remove containers (keep volumes)
docker-compose down

# Remove all project containers and volumes
docker-compose down -v

# Remove all project images
docker rmi $(docker images -q 'veekay8/task-management-*')

# Remove specific volume
docker volume rm postgres_data
```

---

## 🔐 Security & Configuration

### Environment Variables

```bash
# View environment in container
docker-compose exec backend env

# Check specific variable
docker-compose exec backend printenv DATABASE_URL

# Validate configuration
docker-compose config

# Check effective configuration
docker-compose config | grep -A 5 backend
```

### User & Permissions

```bash
# Check running user
docker-compose exec backend whoami
docker-compose exec backend id

# Check file permissions
docker-compose exec backend ls -la /app

# Run as specific user
docker-compose exec --user appuser backend sh
```

### Secrets Management

```bash
# Generate secret key (32+ chars)
openssl rand -base64 32

# Generate JWT secret
python3 -c "import secrets; print(secrets.token_urlsafe(32))"

# Check .env file
cat .env | grep -E "(SECRET|PASSWORD)"
```

---

## 📊 Performance Monitoring

### Resource Usage

```bash
# Live stats (all containers)
docker stats

# Stats snapshot
docker stats --no-stream

# Specific container
docker stats taskmanagement_backend

# Format output
docker stats --format "table {{.Container}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.MemPerc}}"
```

### Performance Testing

```bash
# API response time (single)
time curl http://localhost:5000/api/health

# Average response time (10 requests)
for i in {1..10}; do 
  curl -s -w "%{time_total}\n" -o /dev/null http://localhost:5000/api/health
done | awk '{sum+=$1} END {print "Avg:", sum/NR, "sec"}'

# Concurrent requests (load test)
ab -n 100 -c 10 http://localhost:5000/api/health

# Database query performance
docker-compose exec db psql -U taskuser -d taskdb -c "
  SELECT query, calls, mean_time 
  FROM pg_stat_statements 
  ORDER BY mean_time DESC 
  LIMIT 10;"
```

### Network Diagnostics

```bash
# Test connectivity between services
docker-compose exec frontend ping -c 3 backend
docker-compose exec backend ping -c 3 db

# DNS resolution
docker-compose exec frontend nslookup backend

# Port listening
docker-compose exec backend netstat -tlnp

# Network details
docker network inspect taskapp_network
```

---

## 🐛 Troubleshooting

### Quick Diagnostics

```bash
# Full diagnostic report
{
  echo "=== Service Status ==="
  docker-compose ps
  echo -e "\n=== Resource Usage ==="
  docker stats --no-stream
  echo -e "\n=== Recent Logs ==="
  docker-compose logs --tail=50
  echo -e "\n=== System Info ==="
  docker system df
} > diagnostic_$(date +%Y%m%d_%H%M%S).txt
```

### Common Fixes

```bash
# Restart services
docker-compose restart

# Full reset (keep data)
docker-compose down
docker-compose up -d

# Clear cache and rebuild
docker-compose build --no-cache
docker-compose up -d

# Emergency reset (⚠️ deletes data)
docker-compose down -v
docker system prune -a --volumes
docker-compose up -d
```

### Port Conflicts

```bash
# Check what's using port
lsof -i :3000  # Frontend
lsof -i :5000  # Backend
lsof -i :5432  # Database

# Kill process using port
kill -9 $(lsof -t -i:3000)

# Change port in docker-compose.yml
# ports:
#   - "3001:3000"  # Use host port 3001
```

---

## 🔧 Advanced Operations

### Image Management

```bash
# List all images
docker images

# Image details
docker inspect veekay8/task-management-backend:1.0.0

# Image history (layers)
docker history veekay8/task-management-backend:1.0.0

# Image size breakdown
docker history --no-trunc veekay8/task-management-backend:1.0.0 --format "table {{.Size}}\t{{.CreatedBy}}"

# Save image to file
docker save veekay8/task-management-backend:1.0.0 | gzip > backend-1.0.0.tar.gz

# Load image from file
docker load < backend-1.0.0.tar.gz
```

### Container Management

```bash
# List running containers
docker ps

# List all containers
docker ps -a

# Container details
docker inspect taskmanagement_backend

# Container logs
docker logs taskmanagement_backend

# Copy files from container
docker cp taskmanagement_backend:/app/logs.txt ./logs.txt

# Copy files to container
docker cp ./config.json taskmanagement_backend:/app/config.json

# Execute command in container
docker exec taskmanagement_backend python -V
```

### Volume Management

```bash
# List volumes
docker volume ls

# Volume details
docker volume inspect postgres_data

# Create volume
docker volume create my_volume

# Remove volume
docker volume rm postgres_data

# Volume location (Linux)
docker volume inspect postgres_data --format '{{.Mountpoint}}'

# Backup volume
docker run --rm -v postgres_data:/source -v $(pwd):/backup alpine tar czf /backup/volume.tar.gz -C /source .
```

### Network Management

```bash
# List networks
docker network ls

# Network details
docker network inspect taskapp_network

# Create network
docker network create my_network

# Connect container to network
docker network connect taskapp_network my_container

# Disconnect container
docker network disconnect taskapp_network my_container
```

---

## 📱 Docker Compose Shortcuts

### Multiple Compose Files

```bash
# Use multiple files
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d

# Set default files
export COMPOSE_FILE=docker-compose.yml:docker-compose.prod.yml
docker-compose up -d

# Override file (auto-loaded in dev)
# Create docker-compose.override.yml
docker-compose up -d  # Automatically uses override
```

### Service Scaling

```bash
# Scale service (multiple instances)
docker-compose up -d --scale backend=3

# Check scaled instances
docker-compose ps backend
```

### Selective Operations

```bash
# Start only database
docker-compose up -d db

# Restart only backend
docker-compose restart backend

# Logs from multiple services
docker-compose logs -f backend frontend

# Build only frontend
docker-compose build frontend
```

---

## 🎯 One-Liners

```bash
# Quick health check all services
docker-compose ps | grep -E "(healthy|unhealthy|starting)"

# Total resource usage
docker stats --no-stream --format "table {{.Container}}\t{{.CPUPerc}}\t{{.MemUsage}}"

# Find large images
docker images --format "table {{.Repository}}\t{{.Tag}}\t{{.Size}}" | sort -k3 -h

# Remove all stopped containers
docker rm $(docker ps -aq -f status=exited)

# Remove all dangling images
docker rmi $(docker images -f "dangling=true" -q)

# Follow logs from all services with timestamps
docker-compose logs -f --timestamps

# Get IP addresses of all containers
docker inspect -f '{{.Name}} - {{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}' $(docker ps -q)

# Check disk usage by containers
docker ps -s --format "table {{.Names}}\t{{.Size}}"

# Backup all databases
for db in $(docker ps --filter "ancestor=postgres:15-alpine" --format "{{.Names}}"); do
  docker exec $db pg_dumpall -U postgres > "${db}_$(date +%Y%m%d).sql"
done
```

---

## 📚 Configuration Files

### Essential Files

```
task-management-app/
├── .env                          # Active environment variables
├── .env.example                  # Environment template
├── .env.development              # Development config
├── .env.production               # Production config
├── docker-compose.yml            # Main orchestration
├── docker-compose.prod.yml       # Production overrides
├── docker-compose.hub.yml        # Docker Hub deployment
├── VERSION                       # Version number
├── backend/
│   ├── Dockerfile               # Backend container definition
│   └── .dockerignore            # Build context filter
└── frontend/
    ├── Dockerfile               # Frontend container definition
    └── .dockerignore            # Build context filter
```

### Quick Edit

```bash
# Edit environment
nano .env

# Edit docker-compose
nano docker-compose.yml

# Edit Dockerfile
nano backend/Dockerfile

# Validate YAML
docker-compose config

# Apply changes
docker-compose up -d
```

---

## 🆘 Emergency Commands

### Service Down

```bash
# Quick restart
docker-compose restart

# Force recreate
docker-compose up -d --force-recreate

# Nuclear option (⚠️ deletes data)
docker-compose down -v && docker-compose up -d
```

### Database Corruption

```bash
# Stop all services
docker-compose down

# Backup if possible
docker run --rm -v postgres_data:/data -v $(pwd):/backup alpine tar czf /backup/emergency-backup.tar.gz /data

# Remove volume and start fresh
docker volume rm postgres_data
docker-compose up -d db

# Restore from backup
cat backup.sql | docker exec -i taskmanagement_postgres psql -U taskuser taskdb
```

### Out of Disk Space

```bash
# Quick cleanup
docker system prune -a

# Aggressive cleanup
docker system prune -a --volumes

# Check space freed
docker system df
```

---

## 📞 Quick Help

| Problem | Command |
|---------|---------|
| Services won't start | `docker-compose logs` |
| Port already in use | `lsof -i :PORT` |
| Can't connect to DB | `docker-compose exec db pg_isready` |
| Out of memory | `docker stats` |
| Slow performance | `docker stats --no-stream` |
| Check configuration | `docker-compose config` |
| Service unhealthy | `docker inspect CONTAINER` |
| Need to restart | `docker-compose restart` |

---

## 🔗 Useful Links

- **Full Documentation**: `CONTAINERIZATION.md`
- **Troubleshooting**: `TROUBLESHOOTING.md`
- **Security Guide**: `SECURITY.md`
- **Deployment**: `DEPLOYMENT.md`
- **Metrics**: `OPTIMIZATION_METRICS.md`

---

## 💡 Pro Tips

```bash
# Auto-restart on file changes (development)
docker-compose watch  # Docker Compose v2.22+

# Color output
docker-compose logs -f --no-log-prefix

# JSON output for scripting
docker inspect --format='{{json .State}}' CONTAINER | jq

# Tail logs from multiple containers
docker-compose logs -f backend frontend | grep -i error

# Export environment for debugging
docker-compose config > composed.yml

# Quick service check
watch -n 5 'docker-compose ps'
```

---

**Version**: 1.0.0  
**Last Updated**: January 2, 2026  
**Quick Help**: See `TROUBLESHOOTING.md` for detailed solutions

---

*Print this page and keep it handy! 📄*
