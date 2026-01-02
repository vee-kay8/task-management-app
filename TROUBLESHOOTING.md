# Troubleshooting Guide
## Task Management Application - Docker Issues & Solutions

**Version**: 1.0.0  
**Last Updated**: January 2, 2026

---

## Table of Contents

1. [Quick Diagnostics](#quick-diagnostics)
2. [Service Startup Issues](#service-startup-issues)
3. [Database Connection Problems](#database-connection-problems)
4. [Network & Connectivity Issues](#network--connectivity-issues)
5. [Performance Problems](#performance-problems)
6. [Build Failures](#build-failures)
7. [Resource Issues](#resource-issues)
8. [Health Check Failures](#health-check-failures)
9. [Environment Variable Issues](#environment-variable-issues)
10. [Volume & Persistence Issues](#volume--persistence-issues)
11. [Docker Hub Issues](#docker-hub-issues)
12. [Production-Specific Issues](#production-specific-issues)

---

## Quick Diagnostics

### First Steps for Any Issue

```bash
# 1. Check service status
docker-compose ps

# 2. View recent logs
docker-compose logs --tail=50

# 3. Check resource usage
docker stats --no-stream

# 4. Verify Docker installation
docker version
docker-compose version

# 5. Check system resources
docker system df
```

### Common Quick Fixes

```bash
# Restart all services
docker-compose restart

# Stop and start fresh
docker-compose down
docker-compose up -d

# Full cleanup and restart
docker-compose down -v
docker-compose up -d

# Rebuild everything
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

---

## Service Startup Issues

### Issue 1: Services Exit Immediately

**Symptoms**:
- `docker-compose ps` shows services as "Exited" or "Restarting"
- Services start but immediately stop
- Exit code 1, 127, or 139

**Diagnosis**:
```bash
# Check exit codes
docker-compose ps

# View error logs
docker-compose logs backend
docker-compose logs frontend

# Inspect last run
docker inspect taskmanagement_backend --format='{{.State.ExitCode}}'
```

**Solutions**:

1. **Missing .env file**:
```bash
# Verify .env exists
ls -la .env

# Create from template
cp .env.example .env
nano .env  # Configure required variables
```

2. **Port conflicts**:
```bash
# Check if ports are in use
lsof -i :3000  # Frontend
lsof -i :5000  # Backend
lsof -i :5432  # Database

# Kill conflicting processes or change ports in docker-compose.yml
```

3. **Insufficient permissions**:
```bash
# Check Docker daemon
sudo systemctl status docker  # Linux
docker info  # macOS/Windows

# Fix permissions (Linux)
sudo usermod -aG docker $USER
newgrp docker
```

4. **Syntax errors in configuration**:
```bash
# Validate docker-compose.yml
docker-compose config

# Check for YAML indentation errors
yamllint docker-compose.yml
```

---

### Issue 2: "Cannot Start Service" Errors

**Symptoms**:
```
ERROR: Cannot start service backend: driver failed programming external connectivity
```

**Diagnosis**:
```bash
# Check Docker network
docker network ls
docker network inspect taskapp_network

# Check iptables (Linux)
sudo iptables -L -n
```

**Solutions**:

1. **Network conflicts**:
```bash
# Remove and recreate network
docker network rm taskapp_network
docker-compose up -d
```

2. **Firewall blocking**:
```bash
# Linux - Allow Docker
sudo ufw allow 2375/tcp
sudo ufw allow 2376/tcp

# macOS - Check Security & Privacy settings
```

3. **Docker daemon restart**:
```bash
# Linux
sudo systemctl restart docker

# macOS
# Restart Docker Desktop from menu bar

# Windows
# Restart Docker Desktop
```

---

### Issue 3: Services Start but "Unhealthy"

**Symptoms**:
- `docker-compose ps` shows "(unhealthy)" status
- Services accessible but marked unhealthy

**Diagnosis**:
```bash
# Check health check details
docker inspect taskmanagement_backend --format='{{json .State.Health}}' | jq

# View health check logs
docker inspect taskmanagement_backend --format='{{range .State.Health.Log}}{{.Output}}{{end}}'

# Test health endpoint manually
curl http://localhost:5000/api/health
curl http://localhost:3000/api/health
```

**Solutions**:

1. **Health check timing**:
```yaml
# Increase timeout in docker-compose.yml
healthcheck:
  test: ["CMD", "curl", "-f", "http://localhost:5000/api/health"]
  interval: 15s        # Was 10s
  timeout: 5s          # Was 3s
  retries: 5           # Was 3
  start_period: 30s    # Was 15s
```

2. **Missing curl in container**:
```bash
# Use wget instead (already in alpine)
healthcheck:
  test: ["CMD", "wget", "--quiet", "--tries=1", "--spider", "http://localhost:3000/api/health"]
```

3. **Application not binding correctly**:
```bash
# Check if app is listening on 0.0.0.0 (not 127.0.0.1)
docker-compose exec backend netstat -tlnp

# Backend should show: 0.0.0.0:5000
# Frontend should show: 0.0.0.0:3000
```

---

## Database Connection Problems

### Issue 1: "Connection Refused" Errors

**Symptoms**:
```
psycopg2.OperationalError: could not connect to server: Connection refused
Is the server running on host "db" and accepting TCP/IP connections?
```

**Diagnosis**:
```bash
# Check database status
docker-compose ps db

# Test database connectivity
docker-compose exec db pg_isready -U taskuser

# Check if database is listening
docker-compose exec db netstat -tlnp | grep 5432

# Verify network connectivity
docker-compose exec backend ping -c 3 db
```

**Solutions**:

1. **Database not ready**:
```bash
# Wait for database to be fully ready
docker-compose up -d db
sleep 10  # Wait 10 seconds
docker-compose up -d backend frontend
```

2. **Wrong DATABASE_URL**:
```bash
# Verify .env configuration
cat .env | grep DATABASE_URL

# Should be: postgresql://taskuser:taskpass@db:5432/taskdb
# NOT: localhost or 127.0.0.1 (use service name "db")
```

3. **Dependency ordering**:
```yaml
# Ensure depends_on in docker-compose.yml
services:
  backend:
    depends_on:
      db:
        condition: service_healthy
```

---

### Issue 2: "Database Does Not Exist"

**Symptoms**:
```
psycopg2.OperationalError: FATAL: database "taskdb" does not exist
```

**Diagnosis**:
```bash
# List databases
docker-compose exec db psql -U taskuser -c "\l"

# Check initialization script
docker-compose logs db | grep -i "database system is ready"
```

**Solutions**:

1. **Database not initialized**:
```bash
# Check if init script ran
docker-compose logs db | grep "01-schema.sql"

# Recreate database from scratch
docker-compose down -v  # CAUTION: Deletes all data
docker-compose up -d
```

2. **Wrong database name in .env**:
```bash
# Verify environment variables match
echo "POSTGRES_DB from .env: $(grep POSTGRES_DB .env)"
echo "DATABASE_URL from .env: $(grep DATABASE_URL .env)"

# Both should reference "taskdb"
```

3. **Manual database creation**:
```bash
# Create database manually
docker-compose exec db psql -U taskuser -c "CREATE DATABASE taskdb;"

# Run schema
docker-compose exec db psql -U taskuser -d taskdb -f /docker-entrypoint-initdb.d/01-schema.sql
```

---

### Issue 3: "Authentication Failed"

**Symptoms**:
```
psycopg2.OperationalError: FATAL: password authentication failed for user "taskuser"
```

**Diagnosis**:
```bash
# Check environment variables
docker-compose exec backend env | grep DATABASE
docker-compose exec db env | grep POSTGRES

# Verify .env file
cat .env | grep -E "(POSTGRES_USER|POSTGRES_PASSWORD|DATABASE_URL)"
```

**Solutions**:

1. **Password mismatch**:
```bash
# Ensure consistent credentials
# .env should have:
POSTGRES_USER=taskuser
POSTGRES_PASSWORD=taskpass
DATABASE_URL=postgresql://taskuser:taskpass@db:5432/taskdb

# If changed, recreate database:
docker-compose down -v
docker-compose up -d
```

2. **Special characters in password**:
```bash
# URL-encode special characters in DATABASE_URL
# Example: password "p@ss!" becomes "p%40ss%21"

# Or use simple passwords (alphanumeric only)
POSTGRES_PASSWORD=taskpass123
```

---

## Network & Connectivity Issues

### Issue 1: Cannot Access Frontend/Backend from Host

**Symptoms**:
- `curl http://localhost:3000` fails
- Browser cannot connect to application
- "Connection refused" or timeout errors

**Diagnosis**:
```bash
# Check if containers are running
docker-compose ps

# Check port bindings
docker-compose port frontend 3000
docker-compose port backend 5000

# Test from inside container
docker-compose exec frontend wget -O- http://localhost:3000/api/health
```

**Solutions**:

1. **Port binding issues**:
```yaml
# Verify ports in docker-compose.yml
services:
  frontend:
    ports:
      - "3000:3000"  # host:container
  backend:
    ports:
      - "5000:5000"
```

2. **Firewall blocking**:
```bash
# macOS - Allow in Firewall settings
# Linux - Open ports
sudo ufw allow 3000/tcp
sudo ufw allow 5000/tcp

# Check if ports are listening
netstat -tuln | grep -E "(3000|5000)"
```

3. **Docker Desktop network settings** (macOS/Windows):
```
Docker Desktop → Preferences → Resources → Network
- Ensure "Use kernel networking for UDP" is enabled
- Try restarting Docker Desktop
```

---

### Issue 2: Services Cannot Communicate

**Symptoms**:
- Frontend cannot reach backend API
- Backend cannot reach database
- "getaddrinfo ENOTFOUND" or "Name or service not known"

**Diagnosis**:
```bash
# Test inter-service connectivity
docker-compose exec frontend ping -c 3 backend
docker-compose exec backend ping -c 3 db

# Check DNS resolution
docker-compose exec frontend nslookup backend
docker-compose exec backend nslookup db

# Inspect network
docker network inspect taskapp_network
```

**Solutions**:

1. **Wrong service names**:
```javascript
// frontend/lib/api.ts - Use service name, not localhost
const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://backend:5000';

// NOT: http://localhost:5000 (doesn't work inside containers)
```

2. **Network not created**:
```bash
# Recreate network
docker-compose down
docker network rm taskapp_network
docker-compose up -d
```

3. **Custom network configuration**:
```yaml
# docker-compose.yml - Ensure all services on same network
networks:
  taskapp_network:
    driver: bridge

services:
  backend:
    networks:
      - taskapp_network
  frontend:
    networks:
      - taskapp_network
  db:
    networks:
      - taskapp_network
```

---

## Performance Problems

### Issue 1: Slow API Response Times

**Symptoms**:
- API requests taking >500ms
- Slow page loads
- Timeouts under load

**Diagnosis**:
```bash
# Measure response time
time curl http://localhost:5000/api/health

# Check for slow queries
docker-compose exec db psql -U taskuser -d taskdb -c "
  SELECT query, calls, total_time, mean_time 
  FROM pg_stat_statements 
  ORDER BY mean_time DESC 
  LIMIT 10;"

# Monitor resource usage
docker stats
```

**Solutions**:

1. **Increase Gunicorn workers**:
```bash
# .env - Set workers to (2 * CPU cores) + 1
GUNICORN_WORKERS=9  # For 4 CPU cores

# Restart backend
docker-compose restart backend
```

2. **Database connection pooling**:
```python
# backend/app/config.py
SQLALCHEMY_ENGINE_OPTIONS = {
    'pool_size': 10,
    'pool_recycle': 3600,
    'pool_pre_ping': True,
    'max_overflow': 20
}
```

3. **Add database indexes**:
```sql
-- For frequently queried columns
CREATE INDEX idx_tasks_project_id ON tasks(project_id);
CREATE INDEX idx_tasks_status ON tasks(status);
CREATE INDEX idx_projects_user_id ON projects(user_id);
```

---

### Issue 2: High Memory Usage

**Symptoms**:
- Docker using >2GB RAM
- System slowing down
- OOM (Out of Memory) errors

**Diagnosis**:
```bash
# Check memory usage
docker stats

# Check container limits
docker inspect taskmanagement_backend --format='{{.HostConfig.Memory}}'

# System memory
free -h  # Linux
vm_stat  # macOS
```

**Solutions**:

1. **Apply resource limits**:
```bash
# Use production compose with limits
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d

# Verify limits applied
docker stats
```

2. **Reduce worker processes**:
```bash
# .env - Reduce Gunicorn workers
GUNICORN_WORKERS=2  # Instead of 4

docker-compose restart backend
```

3. **Increase Docker Desktop memory** (macOS/Windows):
```
Docker Desktop → Preferences → Resources
- Memory: Increase to 4GB or 6GB
- Apply & Restart
```

4. **Clean up Docker resources**:
```bash
# Remove unused images
docker image prune -a

# Remove unused volumes
docker volume prune

# Full cleanup
docker system prune -a --volumes  # CAUTION: Deletes everything
```

---

### Issue 3: Slow Build Times

**Symptoms**:
- `docker-compose build` takes >10 minutes
- Builds not using cache
- Repeated downloads of dependencies

**Diagnosis**:
```bash
# Build with timing
time docker-compose build

# Check layer caching
docker-compose build --progress=plain backend

# Check build context size
du -sh backend/
du -sh frontend/
```

**Solutions**:

1. **Enable BuildKit**:
```bash
# Use BuildKit for faster parallel builds
export DOCKER_BUILDKIT=1
docker-compose build

# Or set in .env
echo "DOCKER_BUILDKIT=1" >> .env
echo "COMPOSE_DOCKER_CLI_BUILD=1" >> .env
```

2. **Optimize .dockerignore**:
```bash
# backend/.dockerignore
**/__pycache__
**/*.pyc
**/.git
**/tests
**/test_*.py
**/.pytest_cache
**/.venv
**/venv
```

3. **Use Docker Hub images** (fastest):
```bash
# Skip build entirely
docker-compose -f docker-compose.hub.yml up -d

# Pull time: ~2 minutes vs 7+ minutes build
```

4. **Layer caching best practices**:
```dockerfile
# Copy dependencies first (changes less frequently)
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copy code last (changes more frequently)
COPY . .
```

---

## Build Failures

### Issue 1: npm/pip Install Failures

**Symptoms**:
```
ERROR: Could not find a version that satisfies the requirement
npm ERR! code ENOTFOUND
```

**Diagnosis**:
```bash
# Check network connectivity
docker run --rm alpine ping -c 3 pypi.org
docker run --rm alpine ping -c 3 registry.npmjs.org

# Check DNS
docker run --rm alpine nslookup pypi.org
```

**Solutions**:

1. **Network/proxy issues**:
```dockerfile
# Add to Dockerfile if behind proxy
ENV HTTP_PROXY=http://proxy:port
ENV HTTPS_PROXY=http://proxy:port
```

2. **Use package mirrors**:
```dockerfile
# Backend - Use PyPI mirror
RUN pip install --index-url https://pypi.tuna.tsinghua.edu.cn/simple -r requirements.txt

# Frontend - Use npm mirror
RUN npm config set registry https://registry.npm.taobao.org
RUN npm ci --only=production
```

3. **Cache pip/npm packages**:
```bash
# Create cache volume
docker volume create pip-cache
docker volume create npm-cache

# Use in builds
docker run -v pip-cache:/root/.cache/pip ...
```

---

### Issue 2: "COPY Failed" Errors

**Symptoms**:
```
COPY failed: file not found in build context
```

**Diagnosis**:
```bash
# Check file exists
ls -la backend/requirements.txt
ls -la frontend/package.json

# Check build context
docker-compose config
```

**Solutions**:

1. **Wrong file path**:
```dockerfile
# Ensure COPY paths are relative to Dockerfile location
# backend/Dockerfile
COPY requirements.txt .  # File is in same directory as Dockerfile
COPY ./app /app         # Copy app directory
```

2. **.dockerignore excluding needed files**:
```bash
# Check .dockerignore
cat backend/.dockerignore

# Remove any exclusions of required files
# Do NOT exclude: requirements.txt, package.json, etc.
```

---

### Issue 3: "No Space Left on Device"

**Symptoms**:
```
ERROR: failed to export image: failed to create image: no space left on device
```

**Diagnosis**:
```bash
# Check Docker disk usage
docker system df

# Check host disk space
df -h
```

**Solutions**:

1. **Clean Docker resources**:
```bash
# Remove dangling images
docker image prune

# Remove all unused images
docker image prune -a

# Full cleanup
docker system prune -a --volumes

# Check space freed
docker system df
```

2. **Increase Docker Desktop storage** (macOS/Windows):
```
Docker Desktop → Preferences → Resources → Disk
- Disk image size: Increase to 100GB
- Apply & Restart
```

3. **Clean host system**:
```bash
# Linux - Clean package cache
sudo apt clean
sudo apt autoremove

# macOS - Clear system cache
# Use Disk Utility or third-party tools
```

---

## Resource Issues

### Issue 1: CPU Throttling

**Symptoms**:
- Containers using 100% CPU
- System becomes unresponsive
- Services very slow

**Diagnosis**:
```bash
# Check CPU usage
docker stats

# Check container limits
docker inspect taskmanagement_backend --format='{{.HostConfig.CpuQuota}}'
```

**Solutions**:

1. **Apply CPU limits**:
```yaml
# docker-compose.prod.yml
services:
  backend:
    deploy:
      resources:
        limits:
          cpus: '1.0'  # Max 1 CPU core
        reservations:
          cpus: '0.25'
```

2. **Reduce worker processes**:
```bash
# .env
GUNICORN_WORKERS=2  # Reduce from 4 to 2

docker-compose restart backend
```

3. **Identify CPU-intensive processes**:
```bash
# Top processes inside container
docker-compose exec backend top

# Check for infinite loops or busy-waiting
docker-compose logs backend | grep -i error
```

---

### Issue 2: Disk I/O Bottleneck

**Symptoms**:
- Slow database queries
- High disk wait times
- Container freezes

**Diagnosis**:
```bash
# Check I/O stats
docker stats --format "table {{.Container}}\t{{.BlockIO}}"

# Linux - iostat
iostat -x 1

# macOS - Activity Monitor → Disk tab
```

**Solutions**:

1. **Use volume mounts for data**:
```yaml
# docker-compose.yml - Named volumes are faster than bind mounts
volumes:
  postgres_data:
    driver: local
```

2. **Optimize PostgreSQL**:
```bash
# docker-compose.yml - Add PostgreSQL tuning
environment:
  - POSTGRES_SHARED_BUFFERS=256MB
  - POSTGRES_EFFECTIVE_CACHE_SIZE=1GB
  - POSTGRES_MAX_CONNECTIONS=100
```

3. **Add database indexes**:
```sql
-- Speed up frequently accessed queries
CREATE INDEX CONCURRENTLY idx_tasks_created_at ON tasks(created_at DESC);
```

---

## Health Check Failures

### Issue 1: Health Check Command Not Found

**Symptoms**:
```
Health check failed: /bin/sh: curl: not found
```

**Diagnosis**:
```bash
# Check if curl exists in container
docker-compose exec backend which curl

# Check healthcheck configuration
docker inspect taskmanagement_backend --format='{{json .Config.Healthcheck}}' | jq
```

**Solutions**:

1. **Install curl in Dockerfile**:
```dockerfile
# Backend (Debian-based)
RUN apt-get update && apt-get install -y --no-install-recommends curl

# Frontend (Alpine-based)
RUN apk add --no-cache curl
```

2. **Use alternative health check**:
```yaml
# Use wget (available in Alpine)
healthcheck:
  test: ["CMD", "wget", "--quiet", "--tries=1", "--spider", "http://localhost:3000/api/health"]

# Or use Python
healthcheck:
  test: ["CMD", "python", "-c", "import urllib.request; urllib.request.urlopen('http://localhost:5000/api/health')"]
```

---

### Issue 2: Health Endpoint Returns 404

**Symptoms**:
- Health check fails even though service is running
- Manual curl returns 404

**Diagnosis**:
```bash
# Test endpoint manually
curl -v http://localhost:5000/api/health
curl -v http://localhost:3000/api/health

# Check if route exists
docker-compose exec backend grep -r "health" app/
docker-compose exec frontend grep -r "health" app/
```

**Solutions**:

1. **Verify health endpoint exists**:
```python
# backend/app/__init__.py
@app.route('/api/health', methods=['GET'])
def health():
    return jsonify({"status": "healthy"}), 200
```

```typescript
// frontend/app/api/health/route.ts
export async function GET() {
  return Response.json({ status: 'ok' });
}
```

2. **Check route path in healthcheck**:
```yaml
# Ensure path matches actual endpoint
healthcheck:
  test: ["CMD", "curl", "-f", "http://localhost:5000/api/health"]
  # NOT /health (missing /api prefix)
```

---

## Environment Variable Issues

### Issue 1: Environment Variables Not Loading

**Symptoms**:
- Application uses default values instead of .env
- "Environment variable not set" errors

**Diagnosis**:
```bash
# Check if .env file exists
ls -la .env

# Verify variables are set in container
docker-compose exec backend env
docker-compose exec frontend env

# Check docker-compose.yml syntax
docker-compose config
```

**Solutions**:

1. **Verify .env file location**:
```bash
# .env must be in same directory as docker-compose.yml
pwd
ls -la .env

# If missing, create it
cp .env.example .env
```

2. **Restart services after .env changes**:
```bash
# Environment variables are loaded at container creation
docker-compose down
docker-compose up -d
```

3. **Use env_file in docker-compose.yml**:
```yaml
services:
  backend:
    env_file:
      - .env
    environment:
      - FLASK_APP=run.py
```

---

### Issue 2: Wrong Environment Values

**Symptoms**:
- Variables have unexpected values
- Development settings in production

**Diagnosis**:
```bash
# Check what's being loaded
docker-compose config | grep -A 10 environment

# Verify .env contents
cat .env

# Check for multiple .env files
ls -la .env*
```

**Solutions**:

1. **Use correct .env file**:
```bash
# Development
cp .env.development .env
docker-compose up -d

# Production
cp .env.production .env
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d
```

2. **Avoid conflicting definitions**:
```yaml
# docker-compose.yml - env_file has lower priority
services:
  backend:
    env_file: .env           # Loaded first
    environment:             # Overrides .env
      FLASK_ENV: production
```

3. **Quote special characters**:
```bash
# .env - Quote values with special characters
SECRET_KEY="my-secret!@#$%"
DATABASE_URL="postgresql://user:p@ss!@localhost/db"
```

---

## Volume & Persistence Issues

### Issue 1: Data Not Persisting

**Symptoms**:
- Database data lost after `docker-compose down`
- User data disappears after restart

**Diagnosis**:
```bash
# Check volumes
docker volume ls
docker volume inspect postgres_data

# Check if volume is mounted
docker inspect taskmanagement_postgres --format='{{json .Mounts}}' | jq
```

**Solutions**:

1. **Use named volumes** (not anonymous):
```yaml
# docker-compose.yml
services:
  db:
    volumes:
      - postgres_data:/var/lib/postgresql/data  # Named volume

volumes:
  postgres_data:  # Volume definition
```

2. **Don't use `-v` flag**:
```bash
# DON'T: Deletes volumes
docker-compose down -v

# DO: Preserves volumes
docker-compose down
```

3. **Backup data before cleanup**:
```bash
# Backup database
docker exec taskmanagement_postgres pg_dump -U taskuser taskdb > backup.sql

# Then safe to delete
docker-compose down -v
```

---

### Issue 2: Permission Denied on Volumes

**Symptoms**:
```
Permission denied: '/var/lib/postgresql/data'
```

**Diagnosis**:
```bash
# Check volume permissions
docker volume inspect postgres_data

# Check container user
docker-compose exec db id
```

**Solutions**:

1. **Use proper user in Dockerfile**:
```dockerfile
# Already configured correctly
USER appuser  # UID 1001
```

2. **Fix volume permissions** (Linux):
```bash
# Find volume location
docker volume inspect postgres_data --format '{{.Mountpoint}}'

# Fix permissions (Linux only)
sudo chown -R 999:999 /var/lib/docker/volumes/postgres_data/_data
```

3. **Recreate volume**:
```bash
docker-compose down -v
docker volume rm postgres_data
docker-compose up -d
```

---

## Docker Hub Issues

### Issue 1: Cannot Pull Images

**Symptoms**:
```
Error response from daemon: pull access denied
```

**Diagnosis**:
```bash
# Check if logged in
docker info | grep Username

# Test pull manually
docker pull veekay8/task-management-backend:1.0.0
```

**Solutions**:

1. **Login to Docker Hub**:
```bash
docker login
# Enter username: veekay8
# Enter password: <your-token>
```

2. **Check image name/tag**:
```yaml
# docker-compose.hub.yml - Verify exact names
services:
  backend:
    image: veekay8/task-management-backend:1.0.0
    # NOT: veekay8/backend or wrong tag
```

3. **Rate limiting** (anonymous pulls):
```bash
# Login to increase rate limit from 100 to 200 pulls/6 hours
docker login

# Or wait and retry later
```

---

### Issue 2: Cannot Push Images

**Symptoms**:
```
denied: requested access to the resource is denied
```

**Solutions**:

1. **Login with correct credentials**:
```bash
docker logout
docker login
# Use Docker Hub username (not email)
```

2. **Correct image naming**:
```bash
# Image must start with your username
docker tag backend veekay8/task-management-backend:1.0.0
# NOT: task-management-backend:1.0.0 (missing username)

docker push veekay8/task-management-backend:1.0.0
```

3. **Check repository exists**:
```
- Login to hub.docker.com
- Create repository if needed
- Set to public or ensure you have access
```

---

## Production-Specific Issues

### Issue 1: SSL/TLS Certificate Errors

**Symptoms**:
- HTTPS not working
- Certificate warnings in browser

**Solutions**:

1. **Use reverse proxy (Nginx)**:
```yaml
# docker-compose.prod.yml - Add Nginx
services:
  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./certs:/etc/nginx/certs
```

2. **Use Let's Encrypt** (free SSL):
```bash
# Install certbot
sudo apt install certbot python3-certbot-nginx

# Get certificate
sudo certbot --nginx -d yourdomain.com
```

---

### Issue 2: High Load / Traffic Spikes

**Symptoms**:
- Services slow under load
- Timeout errors
- 503 Service Unavailable

**Solutions**:

1. **Horizontal scaling**:
```yaml
# docker-compose.prod.yml
services:
  backend:
    deploy:
      replicas: 3  # Run 3 backend instances
```

2. **Add load balancer**:
```yaml
services:
  nginx:
    image: nginx:alpine
    volumes:
      - ./nginx-lb.conf:/etc/nginx/nginx.conf
```

3. **Implement caching**:
```yaml
# Add Redis
services:
  redis:
    image: redis:alpine
    ports:
      - "6379:6379"
```

---

## Emergency Procedures

### Complete Reset (Nuclear Option)

```bash
# ⚠️ WARNING: This will delete ALL data ⚠️

# 1. Stop all containers
docker-compose down -v

# 2. Remove all project containers
docker rm -f $(docker ps -aq)

# 3. Remove all project images
docker rmi -f $(docker images -q)

# 4. Remove all volumes
docker volume prune -a

# 5. Remove all networks
docker network prune

# 6. Start fresh
docker-compose up -d
```

### Service-Specific Reset

```bash
# Reset backend only
docker-compose stop backend
docker-compose rm -f backend
docker-compose up -d backend

# Reset database (⚠️ deletes data)
docker-compose stop db
docker-compose rm -f db
docker volume rm postgres_data
docker-compose up -d db

# Reset everything but keep data
docker-compose down
docker-compose up -d
```

---

## Getting More Help

### Gather Information for Support

```bash
# Create diagnostic report
echo "=== Docker Version ===" > diagnostic.txt
docker version >> diagnostic.txt

echo -e "\n=== Compose Version ===" >> diagnostic.txt
docker-compose version >> diagnostic.txt

echo -e "\n=== Service Status ===" >> diagnostic.txt
docker-compose ps >> diagnostic.txt

echo -e "\n=== Recent Logs ===" >> diagnostic.txt
docker-compose logs --tail=100 >> diagnostic.txt

echo -e "\n=== System Info ===" >> diagnostic.txt
docker system df >> diagnostic.txt
docker stats --no-stream >> diagnostic.txt

# Share diagnostic.txt when asking for help
```

### Useful Resources

- **Docker Documentation**: https://docs.docker.com/
- **Docker Compose**: https://docs.docker.com/compose/
- **Community Forum**: https://forums.docker.com/
- **Stack Overflow**: Tag `docker` + `docker-compose`
- **GitHub Issues**: https://github.com/yourusername/task-management-app/issues

---

## Common Error Messages Reference

| Error | Likely Cause | Quick Fix |
|-------|-------------|-----------|
| `Connection refused` | Service not ready | Wait 30s, check health |
| `Address already in use` | Port conflict | Change port or kill process |
| `Permission denied` | User/permissions issue | Check volume ownership |
| `No space left` | Disk full | `docker system prune -a` |
| `Cannot connect to daemon` | Docker not running | Restart Docker |
| `Network not found` | Network deleted | `docker-compose up -d` |
| `Image not found` | Wrong image name/tag | Check docker-compose.yml |
| `YAML parse error` | Syntax error | Check indentation |
| `Container exits with 137` | Out of memory | Increase memory limit |
| `Container exits with 1` | Application error | Check logs |

---

**Need more help?** Open an issue at: https://github.com/yourusername/task-management-app/issues

**Last Updated**: January 2, 2026  
**Version**: 1.0.0
