# Phase 3: Docker & Container Registry - Complete Implementation Guide

## 📚 Table of Contents
1. [Overview](#overview)
2. [What is Docker?](#what-is-docker)
3. [Phase 3 Objectives](#phase-3-objectives)
4. [Prerequisites](#prerequisites)
5. [Step-by-Step Implementation](#step-by-step-implementation)
6. [Docker Concepts Explained](#docker-concepts-explained)
7. [Multi-Stage Builds](#multi-stage-builds)
8. [GitHub Container Registry](#github-container-registry)
9. [Testing & Validation](#testing--validation)
10. [Troubleshooting](#troubleshooting)

---

## Overview

### What We're Building in Phase 3

**Goal**: Containerize your application so it runs consistently anywhere - your laptop, staging server, or production.

**Deliverables**:
- ✅ Backend Docker image (Python/Flask)
- ✅ Frontend Docker image (Next.js)
- ✅ Docker Compose for local development
- ✅ GitHub Container Registry integration
- ✅ Automated image builds in CI/CD

### Why Docker?

**The Problem Without Docker:**
```
Developer's laptop:
- Windows 11
- Python 3.14.2
- Node.js 20.10.0
- SQLite database
- Works perfectly! ✓

Production server:
- Ubuntu 22.04
- Python 3.10.6 (different version!)
- Node.js 18.12.0 (older!)
- PostgreSQL database (different DB!)
- App crashes! ✗
```

**The Solution With Docker:**
```
Everywhere (laptop, staging, production):
- Docker container
  - Same OS (Ubuntu 22.04)
  - Same Python (3.11)
  - Same Node.js (20)
  - Same dependencies
  - Works everywhere! ✓✓✓
```

### Real-World Analogy

**Shipping Containers**: Just like physical shipping containers standardize cargo transport, Docker containers standardize software deployment.

- **Before containers**: Each ship needed custom loading/unloading for different cargo types
- **After containers**: Standard containers fit on any ship, train, or truck
- **Docker**: Standard software containers run on any computer with Docker

---

## What is Docker?

### Docker in Simple Terms

**Docker** = A way to package your app with everything it needs to run

**Think of it as:**
- A pre-loaded computer inside your computer
- Has its own operating system
- Has all dependencies installed
- Isolated from the host machine
- Can be copied and run anywhere

### Key Docker Concepts

#### 1. Image
**What**: A blueprint/template for your application
**Like**: A recipe for a cake
**Contains**: Code + Dependencies + Configuration
**Create**: Using a `Dockerfile`

#### 2. Container
**What**: A running instance of an image
**Like**: The actual cake made from the recipe
**Runs**: Your application in isolation
**Create**: Using `docker run <image>`

#### 3. Dockerfile
**What**: Instructions to build an image
**Like**: Step-by-step recipe instructions
**Contains**: FROM, COPY, RUN, CMD commands
**Create**: Text file named `Dockerfile`

#### 4. Docker Compose
**What**: Tool to run multiple containers together
**Like**: Running a restaurant (kitchen + dining room + bar)
**Defines**: Services, networks, volumes
**Create**: `docker-compose.yml` file

#### 5. Registry
**What**: Storage for Docker images
**Like**: GitHub for code, but for Docker images
**Examples**: Docker Hub, GitHub Container Registry
**Use**: Push/pull images to share

### Docker vs Virtual Machines

```
Virtual Machine:
┌─────────────────────────────────┐
│  App A  │  App B  │  App C      │
├─────────────────────────────────┤
│  Guest OS  │  Guest OS  │  Guest OS │  (Heavy!)
├─────────────────────────────────┤
│        Hypervisor               │
├─────────────────────────────────┤
│        Host Operating System     │
└─────────────────────────────────┘

Docker:
┌─────────────────────────────────┐
│  App A  │  App B  │  App C      │  (Lightweight!)
├─────────────────────────────────┤
│       Docker Engine             │
├─────────────────────────────────┤
│        Host Operating System     │
└─────────────────────────────────┘
```

**Advantages of Docker:**
- Faster startup (seconds vs minutes)
- Less resource usage (MB vs GB)
- More containers per host
- Easier to manage

---

## Phase 3 Objectives

### Primary Goals

1. **Containerize Backend**
   - Create optimized Dockerfile
   - Multi-stage build (build + runtime)
   - Minimal final image size
   - Production-ready configuration

2. **Containerize Frontend**
   - Create optimized Dockerfile
   - Multi-stage build (build + serve)
   - Static file serving
   - Environment variable support

3. **Local Development with Docker Compose**
   - Run entire stack with one command
   - Database + Backend + Frontend
   - Hot reload for development
   - Proper networking between services

4. **GitHub Container Registry**
   - Automated image builds in CI/CD
   - Push to ghcr.io (GitHub Container Registry)
   - Version tagging
   - Pull images for deployment

### Success Criteria

- ✅ `docker build` succeeds for backend
- ✅ `docker build` succeeds for frontend
- ✅ `docker-compose up` runs entire stack
- ✅ Can access app at http://localhost:3000
- ✅ Backend tests pass inside container
- ✅ Images pushed to GitHub Container Registry
- ✅ Images are optimally sized (<200MB each)

---

## Prerequisites

### Required Software

1. **Docker Desktop** (Windows/Mac) or **Docker Engine** (Linux)
   - Download: https://www.docker.com/products/docker-desktop
   - Version: 24.0 or higher
   - Includes Docker Compose

2. **Git** (already have from Phase 1)

3. **GitHub Account** (already have from Phase 2)

### Verify Docker Installation

```bash
# Check Docker version
docker --version
# Output: Docker version 24.0.x, build xxxxx

# Check Docker Compose version
docker-compose --version
# Output: Docker Compose version v2.x.x

# Verify Docker is running
docker ps
# Output: CONTAINER ID   IMAGE   ...  (empty list is fine)
```

### GitHub Personal Access Token

You'll need a token to push images to GitHub Container Registry.

**Create Token:**
1. Go to GitHub → Settings → Developer settings → Personal access tokens → Tokens (classic)
2. Click "Generate new token (classic)"
3. Give it a name: "Docker Registry Access"
4. Set expiration: 90 days (or custom)
5. Select scopes:
   - ✅ `write:packages` - Upload packages to GitHub Package Registry
   - ✅ `read:packages` - Download packages from GitHub Package Registry
   - ✅ `delete:packages` - Delete packages from GitHub Package Registry
6. Click "Generate token"
7. **Copy the token immediately** (you won't see it again!)

**Save Token as GitHub Secret:**
1. Go to your repository on GitHub
2. Settings → Secrets and variables → Actions
3. Click "New repository secret"
4. Name: `GHCR_TOKEN`
5. Value: Paste your token
6. Click "Add secret"

---

## Step-by-Step Implementation

### Step 1: Create Backend Dockerfile

**Location**: `backend/Dockerfile`

```dockerfile
# ================================
# Stage 1: Builder
# ================================
FROM python:3.11-slim as builder

# Set working directory
WORKDIR /app

# Install system dependencies for building Python packages
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first (for better caching)
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir --user -r requirements.txt

# ================================
# Stage 2: Runtime
# ================================
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install runtime dependencies only
RUN apt-get update && apt-get install -y \
    libpq5 \
    && rm -rf /var/lib/apt/lists/*

# Copy Python dependencies from builder
COPY --from=builder /root/.local /root/.local

# Copy application code
COPY . .

# Make sure scripts are executable
RUN chmod +x run.py

# Update PATH to include local Python packages
ENV PATH=/root/.local/bin:$PATH

# Set environment variables
ENV FLASK_APP=run.py
ENV FLASK_ENV=production
ENV PYTHONUNBUFFERED=1

# Expose port
EXPOSE 5000

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:5000/api/health')" || exit 1

# Run the application
CMD ["python", "run.py"]
```

**Explanation of Each Section:**

**Stage 1: Builder**
```dockerfile
FROM python:3.11-slim as builder
```
- Uses Python 3.11 slim image (smaller than full Python image)
- Named "builder" so we can reference it later
- This stage will be discarded in final image

```dockerfile
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    libpq-dev
```
- Installs build tools needed to compile Python packages
- `gcc`/`g++`: C/C++ compilers for native extensions
- `libpq-dev`: PostgreSQL development libraries
- These are only needed for building, not running

```dockerfile
COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt
```
- Copies only requirements.txt first (Docker layer caching)
- `--no-cache-dir`: Don't store pip cache (saves space)
- `--user`: Install to user directory (easier to copy)

**Stage 2: Runtime**
```dockerfile
FROM python:3.11-slim
```
- Fresh start with clean slim image
- Builder stage is discarded
- Much smaller final image

```dockerfile
RUN apt-get update && apt-get install -y \
    libpq5
```
- Only runtime dependencies
- `libpq5`: PostgreSQL client library (not dev files)
- No build tools needed

```dockerfile
COPY --from=builder /root/.local /root/.local
```
- Copy installed Python packages from builder stage
- This is the magic of multi-stage builds!
- Get compiled packages without build tools

```dockerfile
ENV FLASK_ENV=production
ENV PYTHONUNBUFFERED=1
```
- `FLASK_ENV=production`: Run in production mode
- `PYTHONUNBUFFERED=1`: See logs immediately (don't buffer)

```dockerfile
HEALTHCHECK --interval=30s --timeout=3s
```
- Docker checks if app is healthy every 30 seconds
- Calls health endpoint
- Marks container unhealthy if it fails

---

### Step 2: Create Backend .dockerignore

**Location**: `backend/.dockerignore`

```
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
env/
venv/
ENV/
.venv

# Testing
.pytest_cache/
.coverage
htmlcov/
.tox/

# IDE
.vscode/
.idea/
*.swp
*.swo
*~

# OS
.DS_Store
Thumbs.db

# Git
.git/
.gitignore

# Database
*.db
*.sqlite
*.sqlite3

# Logs
*.log

# Environment
.env
.env.local
```

**Why .dockerignore?**
- Like `.gitignore` but for Docker
- Prevents copying unnecessary files into image
- Reduces image size
- Speeds up build process
- Prevents sensitive files from being included

---

### Step 3: Create Frontend Dockerfile

**Location**: `frontend/Dockerfile`

```dockerfile
# ================================
# Stage 1: Dependencies
# ================================
FROM node:20-alpine AS deps

# Set working directory
WORKDIR /app

# Copy package files
COPY package.json package-lock.json ./

# Install dependencies
RUN npm ci --only=production

# ================================
# Stage 2: Builder
# ================================
FROM node:20-alpine AS builder

WORKDIR /app

# Copy dependencies from deps stage
COPY --from=deps /app/node_modules ./node_modules

# Copy application code
COPY . .

# Build the application
ENV NEXT_TELEMETRY_DISABLED 1
RUN npm run build

# ================================
# Stage 3: Runner
# ================================
FROM node:20-alpine AS runner

WORKDIR /app

# Set to production
ENV NODE_ENV production
ENV NEXT_TELEMETRY_DISABLED 1

# Create non-root user
RUN addgroup --system --gid 1001 nodejs
RUN adduser --system --uid 1001 nextjs

# Copy necessary files from builder
COPY --from=builder /app/public ./public
COPY --from=builder /app/.next/standalone ./
COPY --from=builder /app/.next/static ./.next/static

# Set correct permissions
RUN chown -R nextjs:nodejs /app

# Switch to non-root user
USER nextjs

# Expose port
EXPOSE 3000

# Set hostname
ENV HOSTNAME "0.0.0.0"

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=10s --retries=3 \
    CMD node -e "require('http').get('http://localhost:3000/api/health', (r) => {process.exit(r.statusCode === 200 ? 0 : 1)})"

# Start the application
CMD ["node", "server.js"]
```

**Explanation:**

**Stage 1: Dependencies**
```dockerfile
FROM node:20-alpine AS deps
```
- Uses Alpine Linux (minimal OS, ~5MB vs ~100MB)
- Node.js 20 LTS
- Named "deps" for dependency installation

```dockerfile
RUN npm ci --only=production
```
- `npm ci`: Clean install (faster, more reliable than npm install)
- `--only=production`: Skip devDependencies (smaller image)

**Stage 2: Builder**
```dockerfile
COPY --from=deps /app/node_modules ./node_modules
```
- Reuse dependencies from deps stage
- Avoids reinstalling

```dockerfile
ENV NEXT_TELEMETRY_DISABLED 1
RUN npm run build
```
- Disable Next.js telemetry
- Build optimized production bundle

**Stage 3: Runner**
```dockerfile
RUN addgroup --system --gid 1001 nodejs
RUN adduser --system --uid 1001 nextjs
```
- Create non-root user for security
- Running as root inside container is dangerous
- Best practice: use dedicated user

```dockerfile
COPY --from=builder /app/.next/standalone ./
```
- Next.js standalone output (includes minimal Node.js server)
- Much smaller than full node_modules
- Only copies what's needed to run

```dockerfile
USER nextjs
```
- Switch to non-root user
- All subsequent commands run as nextjs user

---

### Step 4: Create Frontend .dockerignore

**Location**: `frontend/.dockerignore`

```
# Dependencies
node_modules/
npm-debug.log*
yarn-debug.log*
yarn-error.log*

# Next.js
.next/
out/
build/
dist/

# Testing
coverage/
.nyc_output/

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db

# Git
.git/
.gitignore

# Environment
.env
.env.local
.env.development.local
.env.test.local
.env.production.local

# Misc
*.log
.cache/
```

---

### Step 5: Update next.config.js for Standalone

**Location**: `frontend/next.config.js`

Add standalone output configuration:

```javascript
/** @type {import('next').NextConfig} */
const nextConfig = {
  // Enable standalone output for Docker
  output: 'standalone',
  
  // Existing config...
  reactStrictMode: true,
  swcMinify: true,
}

module.exports = nextConfig
```

**Why?**
- `output: 'standalone'` creates minimal production server
- Includes only necessary files
- Reduces image size from ~500MB to ~150MB
- Faster deployments

---

### Step 6: Create docker-compose.yml

**Location**: `docker-compose.yml` (root directory)

```yaml
version: '3.8'

services:
  # PostgreSQL Database
  db:
    image: postgres:15-alpine
    container_name: taskapp-db
    environment:
      POSTGRES_DB: taskmanager
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: postgres
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./database/init:/docker-entrypoint-initdb.d
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres"]
      interval: 10s
      timeout: 5s
      retries: 5
    networks:
      - taskapp-network

  # Backend Service
  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile
    container_name: taskapp-backend
    environment:
      DATABASE_URL: postgresql://postgres:postgres@db:5432/taskmanager
      JWT_SECRET_KEY: dev-secret-key-change-in-production
      FLASK_ENV: development
      FLASK_DEBUG: 1
    ports:
      - "5000:5000"
    volumes:
      - ./backend:/app
      - /app/__pycache__
    depends_on:
      db:
        condition: service_healthy
    healthcheck:
      test: ["CMD", "python", "-c", "import requests; requests.get('http://localhost:5000/api/health')"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s
    networks:
      - taskapp-network

  # Frontend Service
  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
    container_name: taskapp-frontend
    environment:
      NEXT_PUBLIC_API_URL: http://localhost:5000
      NODE_ENV: production
    ports:
      - "3000:3000"
    depends_on:
      backend:
        condition: service_healthy
    healthcheck:
      test: ["CMD-SHELL", "wget --no-verbose --tries=1 --spider http://localhost:3000/api/health || exit 1"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s
    networks:
      - taskapp-network

# Named volumes
volumes:
  postgres_data:
    driver: local

# Networks
networks:
  taskapp-network:
    driver: bridge
```

**Explanation:**

**Services Section:**
```yaml
services:
  db:
    image: postgres:15-alpine
```
- Defines three services: db, backend, frontend
- `db` uses official PostgreSQL image (no build needed)

**Environment Variables:**
```yaml
environment:
  DATABASE_URL: postgresql://postgres:postgres@db:5432/taskmanager
```
- `@db` - refers to the db service (Docker DNS)
- Services can find each other by service name

**Volumes:**
```yaml
volumes:
  - postgres_data:/var/lib/postgresql/data
```
- Named volume: persists data even if container stops
- Without this, database resets every restart!

```yaml
volumes:
  - ./backend:/app
```
- Bind mount: sync local files with container
- Changes on laptop appear in container immediately
- Enables hot reload during development

**Depends On:**
```yaml
depends_on:
  db:
    condition: service_healthy
```
- Backend waits for database to be healthy
- Frontend waits for backend to be healthy
- Ensures proper startup order

**Networks:**
```yaml
networks:
  taskapp-network:
    driver: bridge
```
- All services on same network
- Can communicate using service names
- Isolated from other Docker containers

---

### Step 7: Update GitHub Actions for Docker

**Location**: `.github/workflows/ci.yml`

Add Docker build and push job:

```yaml
name: CI/CD Pipeline

on:
  push:
    branches: [main, develop, CICD]
  pull_request:
    branches: [main, develop]

jobs:
  # ... existing backend-tests and frontend-tests jobs ...

  # New job: Build and Push Docker Images
  docker-build-push:
    needs: [backend-tests, frontend-tests]
    runs-on: ubuntu-latest
    if: github.event_name == 'push' && (github.ref == 'refs/heads/main' || github.ref == 'refs/heads/develop')
    
    permissions:
      contents: read
      packages: write
    
    steps:
      - name: Checkout code
        uses: actions/checkout@v4
      
      - name: Set up Docker Buildx
        uses: docker/setup-buildx-action@v3
      
      - name: Log in to GitHub Container Registry
        uses: docker/login-action@v3
        with:
          registry: ghcr.io
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}
      
      - name: Extract metadata (tags, labels)
        id: meta-backend
        uses: docker/metadata-action@v5
        with:
          images: ghcr.io/${{ github.repository }}/backend
          tags: |
            type=ref,event=branch
            type=sha,prefix={{branch}}-
            type=raw,value=latest,enable={{is_default_branch}}
      
      - name: Build and push backend image
        uses: docker/build-push-action@v5
        with:
          context: ./backend
          push: true
          tags: ${{ steps.meta-backend.outputs.tags }}
          labels: ${{ steps.meta-backend.outputs.labels }}
          cache-from: type=gha
          cache-to: type=gha,mode=max
      
      - name: Extract metadata for frontend
        id: meta-frontend
        uses: docker/metadata-action@v5
        with:
          images: ghcr.io/${{ github.repository }}/frontend
          tags: |
            type=ref,event=branch
            type=sha,prefix={{branch}}-
            type=raw,value=latest,enable={{is_default_branch}}
      
      - name: Build and push frontend image
        uses: docker/build-push-action@v5
        with:
          context: ./frontend
          push: true
          tags: ${{ steps.meta-frontend.outputs.tags }}
          labels: ${{ steps.meta-frontend.outputs.labels }}
          cache-from: type=gha
          cache-to: type=gha,mode=max
```

**Explanation:**

**Job Conditions:**
```yaml
if: github.event_name == 'push' && (github.ref == 'refs/heads/main' || github.ref == 'refs/heads/develop')
```
- Only build images on push (not pull requests)
- Only for main or develop branches
- Saves CI minutes and registry storage

**Permissions:**
```yaml
permissions:
  contents: read
  packages: write
```
- Needed to push to GitHub Container Registry
- `packages: write` allows publishing

**Docker Buildx:**
```yaml
- name: Set up Docker Buildx
  uses: docker/setup-buildx-action@v3
```
- Enhanced build capabilities
- Supports multi-platform builds
- Better caching

**Metadata Extraction:**
```yaml
tags: |
  type=ref,event=branch
  type=sha,prefix={{branch}}-
  type=raw,value=latest,enable={{is_default_branch}}
```
- Creates multiple tags:
  - `main` (branch name)
  - `main-abc123` (branch + commit SHA)
  - `latest` (only on default branch)

**Build and Push:**
```yaml
cache-from: type=gha
cache-to: type=gha,mode=max
```
- Uses GitHub Actions cache
- Dramatically speeds up rebuilds
- Only rebuilds changed layers

---

## Docker Concepts Explained

### Layers and Caching

**How Docker Builds Images:**

```dockerfile
FROM python:3.11-slim        # Layer 1: Base image
COPY requirements.txt .      # Layer 2: Requirements file
RUN pip install -r ...       # Layer 3: Install dependencies
COPY . .                     # Layer 4: Application code
CMD ["python", "run.py"]     # Layer 5: Run command
```

**Each instruction creates a layer:**
- Layers are cached
- If nothing changed, reuse cached layer
- Only rebuild from first changed layer

**Example:**

First build:
```
Layer 1: ████████ (downloaded)
Layer 2: ████████ (created)
Layer 3: ████████ (created) <- Takes 2 minutes
Layer 4: ████████ (created)
Layer 5: ████████ (created)
Total: 2.5 minutes
```

Change app code, rebuild:
```
Layer 1: ✓ cached (reused)
Layer 2: ✓ cached (reused)
Layer 3: ✓ cached (reused) <- Still cached!
Layer 4: ████████ (rebuilt)
Layer 5: ████████ (rebuilt)
Total: 5 seconds!
```

**Best Practice: Order matters!**
- Put rarely-changing things first (base image, dependencies)
- Put frequently-changing things last (app code)

---

### Multi-Stage Builds

**Problem**: Single-stage builds are huge

```dockerfile
# Single-stage (BAD)
FROM python:3.11
RUN apt-get install gcc g++ ...  # Build tools
RUN pip install ...               # Dependencies
COPY . .
Final image: 1.2 GB!  # Includes build tools we don't need!
```

**Solution**: Multi-stage builds

```dockerfile
# Stage 1: Build
FROM python:3.11 as builder
RUN apt-get install gcc g++      # Build tools
RUN pip install ...               # Compile packages

# Stage 2: Runtime
FROM python:3.11-slim             # Fresh start!
COPY --from=builder ...           # Copy only compiled packages
COPY . .
Final image: 180 MB!  # No build tools!
```

**Benefits:**
- Smaller images (faster downloads)
- More secure (less attack surface)
- Cheaper storage
- Faster deployments

---

### Container Networking

**How Services Communicate:**

```yaml
# docker-compose.yml
services:
  frontend:
    # Can access backend at: http://backend:5000
  
  backend:
    # Can access database at: postgresql://db:5432
  
  db:
    # Accessible to backend and frontend
```

**Docker DNS:**
- Each service name becomes a hostname
- Automatic service discovery
- Works only within same network

**Port Mapping:**
```yaml
ports:
  - "3000:3000"
  #  ^^^^ ^^^^
  #  Host Container
```
- Left: Port on your laptop
- Right: Port in container
- Access from laptop: `http://localhost:3000`
- Access from other container: `http://frontend:3000`

---

## GitHub Container Registry

### What is GHCR?

**GitHub Container Registry** (ghcr.io):
- Docker registry provided by GitHub
- Free for public repositories
- Integrated with GitHub Actions
- Supports Docker images and OCI artifacts

### Image Naming Convention

```
ghcr.io/vee-kay8/task-management-app/backend:latest
│      │        │                       │       │
│      │        │                       │       └─ Tag
│      │        │                       └───────── Image name
│      │        └───────────────────────────────── Repository
│      └────────────────────────────────────────── Username
└───────────────────────────────────────────────── Registry
```

### Pulling Images

```bash
# Login
echo $GITHUB_TOKEN | docker login ghcr.io -u USERNAME --password-stdin

# Pull backend
docker pull ghcr.io/vee-kay8/task-management-app/backend:latest

# Pull frontend
docker pull ghcr.io/vee-kay8/task-management-app/frontend:latest

# Run
docker run -p 5000:5000 ghcr.io/vee-kay8/task-management-app/backend:latest
```

---

## Testing & Validation

### Test 1: Build Backend Image

```bash
cd backend
docker build -t taskapp-backend:test .
```

**Expected output:**
```
[+] Building 45.2s (16/16) FINISHED
=> [builder 1/5] FROM docker.io/library/python:3.11-slim
=> [builder 2/5] COPY requirements.txt .
=> [builder 3/5] RUN pip install --user -r requirements.txt
=> [runtime 1/4] FROM docker.io/library/python:3.11-slim
=> [runtime 2/4] COPY --from=builder /root/.local /root/.local
=> [runtime 3/4] COPY . .
=> exporting to image
=> => naming to docker.io/library/taskapp-backend:test
```

**Verify:**
```bash
docker images | grep taskapp-backend
# Should show image ~180MB
```

### Test 2: Build Frontend Image

```bash
cd frontend
docker build -t taskapp-frontend:test .
```

**Expected output:**
```
[+] Building 120.3s (20/20) FINISHED
=> [deps 1/3] FROM docker.io/library/node:20-alpine
=> [deps 2/3] COPY package*.json ./
=> [deps 3/3] RUN npm ci --only=production
=> [builder 1/4] COPY --from=deps /app/node_modules
=> [builder 2/4] COPY . .
=> [builder 3/4] RUN npm run build
=> [runner 1/5] COPY --from=builder /app/.next/standalone
=> exporting to image
=> => naming to docker.io/library/taskapp-frontend:test
```

**Verify:**
```bash
docker images | grep taskapp-frontend
# Should show image ~150MB
```

### Test 3: Run with Docker Compose

```bash
# Start all services
docker-compose up -d

# Check status
docker-compose ps

# Expected output:
NAME                 STATUS              PORTS
taskapp-db          Up (healthy)        5432->5432
taskapp-backend     Up (healthy)        5000->5000
taskapp-frontend    Up (healthy)        3000->3000

# View logs
docker-compose logs -f

# Test the application
# Open browser: http://localhost:3000
```

### Test 4: Verify Connectivity

```bash
# Test database
docker-compose exec db psql -U postgres -c "\l"

# Test backend health
curl http://localhost:5000/api/health

# Test frontend
curl http://localhost:3000

# Test backend from frontend container
docker-compose exec frontend wget -O- http://backend:5000/api/health
```

### Test 5: Cleanup

```bash
# Stop all services
docker-compose down

# Remove volumes (database data)
docker-compose down -v

# Remove images
docker rmi taskapp-backend:test taskapp-frontend:test
```

---

## Troubleshooting

### Build Fails: "Cannot find module"

**Problem**: Missing dependencies

**Solution**:
```bash
# Make sure package.json is correct
cd frontend
npm install

# Rebuild
docker build -t taskapp-frontend:test .
```

### Build Fails: "pip install failed"

**Problem**: Network issue or wrong Python version

**Solution**:
```bash
# Try with --no-cache
docker build --no-cache -t taskapp-backend:test .

# Check requirements.txt has correct versions
cat requirements.txt | grep SQLAlchemy
```

### Container Exits Immediately

**Problem**: Application crashes on startup

**Solution**:
```bash
# Check logs
docker logs taskapp-backend

# Run interactively to debug
docker run -it taskapp-backend:test /bin/bash

# Inside container:
python run.py
```

### Port Already in Use

**Problem**: Port 3000 or 5000 already used

**Solution**:
```bash
# Find process using port
# Windows:
netstat -ano | findstr :3000

# Kill process or change port in docker-compose.yml
ports:
  - "3001:3000"  # Use different host port
```

### Database Connection Failed

**Problem**: Backend can't connect to database

**Solution**:
```bash
# Check database is running
docker-compose ps

# Verify DATABASE_URL
docker-compose exec backend env | grep DATABASE_URL

# Should be: postgresql://postgres:postgres@db:5432/taskmanager
```

### Image Push Failed

**Problem**: Authentication error with GHCR

**Solution**:
```bash
# Create GitHub token with write:packages scope
# Login manually:
echo $GITHUB_TOKEN | docker login ghcr.io -u vee-kay8 --password-stdin

# Try push again
docker push ghcr.io/vee-kay8/task-management-app/backend:latest
```

---

## Best Practices

### 1. Security

- ✅ Use multi-stage builds (smaller attack surface)
- ✅ Run as non-root user
- ✅ Don't include secrets in images
- ✅ Use specific image tags (not `latest` in production)
- ✅ Scan images for vulnerabilities

### 2. Performance

- ✅ Order Dockerfile commands for better caching
- ✅ Use .dockerignore to exclude unnecessary files
- ✅ Minimize number of layers
- ✅ Use alpine or slim base images
- ✅ Clean up package manager caches

### 3. Development Workflow

- ✅ Use docker-compose for local development
- ✅ Use volumes for hot reload
- ✅ Use environment variables for configuration
- ✅ Keep development and production configs similar

### 4. CI/CD

- ✅ Build images in CI pipeline
- ✅ Tag images with git SHA
- ✅ Use cache to speed up builds
- ✅ Only push on successful tests

---

## Summary

By the end of Phase 3, you will have:

✅ **Dockerized Backend**
- Multi-stage Dockerfile
- Optimized image size (~180MB)
- Production-ready configuration

✅ **Dockerized Frontend**
- Multi-stage Dockerfile
- Standalone Next.js build
- Optimized image size (~150MB)

✅ **Local Development Environment**
- Docker Compose orchestration
- Database + Backend + Frontend
- One-command startup
- Hot reload support

✅ **Automated CI/CD**
- Docker builds in GitHub Actions
- Images pushed to GHCR
- Proper versioning and tagging

✅ **Professional Infrastructure**
- Consistent environments
- Easy deployment
- Scalable architecture
- Industry-standard practices

**Next**: Phase 4 will deploy these containers to a staging environment! 🚀
