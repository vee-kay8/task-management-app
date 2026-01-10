#!/bin/bash
# =============================================================================
# Task Management App - Automated Deployment Script (Linux/Mac)
# =============================================================================
# This script automates the entire deployment process:
# - Generates secure random keys using Docker
# - Creates .env file automatically
# - Pulls Docker images from Docker Hub
# - Deploys the application
#
# Usage: ./deploy.sh
# =============================================================================

set -e  # Exit on error

echo "========================================="
echo "Task Management App - Deployment"
echo "========================================="
echo ""

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Error: Docker is not installed!"
    echo "Please install Docker from: https://docs.docker.com/get-docker/"
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Error: Docker Compose is not installed!"
    echo "Please install Docker Compose from: https://docs.docker.com/compose/install/"
    exit 1
fi

echo "✅ Docker and Docker Compose detected"
echo ""

# Check if .env already exists
if [ -f .env ]; then
    echo "⚠️  .env file already exists!"
    read -p "Do you want to regenerate secrets? (y/N): " -n 1 -r
    echo ""
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Using existing .env file..."
        SKIP_ENV=true
    fi
fi

if [ "$SKIP_ENV" != "true" ]; then
    echo "🔐 Generating secure keys using Docker..."
    
    # Generate SECRET_KEY
    SECRET_KEY=$(docker run --rm python:3.12-alpine python -c "import secrets; print(secrets.token_hex(32))")
    echo "✅ SECRET_KEY generated"
    
    # Generate JWT_SECRET_KEY
    JWT_SECRET_KEY=$(docker run --rm python:3.12-alpine python -c "import secrets; print(secrets.token_hex(32))")
    echo "✅ JWT_SECRET_KEY generated"
    
    # Generate POSTGRES_PASSWORD
    POSTGRES_PASSWORD=$(docker run --rm python:3.12-alpine python -c "import secrets; print(secrets.token_urlsafe(32))")
    echo "✅ POSTGRES_PASSWORD generated"
    echo ""
    
    echo "📝 Creating .env file..."
    
    # Create .env file from template
    cat > .env << EOF
# =============================================================================
# PRODUCTION ENVIRONMENT CONFIGURATION
# Auto-generated on $(date)
# =============================================================================

# ===================================
# ENVIRONMENT
# ===================================
NODE_ENV=production
FLASK_ENV=production
FLASK_DEBUG=False

# ===================================
# DATABASE CONFIGURATION
# ===================================
POSTGRES_DB=taskmanagement_db
POSTGRES_USER=taskapp_user
POSTGRES_PASSWORD=${POSTGRES_PASSWORD}

DATABASE_URL=postgresql://taskapp_user:${POSTGRES_PASSWORD}@db:5432/taskmanagement_db

DB_POOL_SIZE=20
DB_MAX_OVERFLOW=40

# ===================================
# BACKEND (Flask) CONFIGURATION
# ===================================
FLASK_APP=run.py
FLASK_HOST=0.0.0.0
FLASK_PORT=5000

SECRET_KEY=${SECRET_KEY}
JWT_SECRET_KEY=${JWT_SECRET_KEY}

# ===================================
# JWT AUTHENTICATION
# ===================================
JWT_ACCESS_TOKEN_EXPIRES=3600
JWT_REFRESH_TOKEN_EXPIRES=604800
JWT_ALGORITHM=HS256

# ===================================
# FRONTEND (Next.js) CONFIGURATION
# ===================================
NEXT_PUBLIC_API_URL=http://localhost:5000/api
PORT=3000
HOSTNAME=0.0.0.0
NEXT_TELEMETRY_DISABLED=1

# ===================================
# CORS SETTINGS
# ===================================
CORS_ORIGINS=http://localhost:3000
CORS_ALLOW_CREDENTIALS=true
CORS_MAX_AGE=3600

# ===================================
# DOCKER CONFIGURATION
# ===================================
COMPOSE_PROJECT_NAME=task-management-app
TZ=UTC

# ===================================
# APPLICATION SETTINGS
# ===================================
ITEMS_PER_PAGE=20
APP_NAME=Task Management App
API_VERSION=v1
LOG_LEVEL=WARNING

# ===================================
# FILE UPLOAD SETTINGS
# ===================================
MAX_FILE_SIZE_MB=10
ALLOWED_EXTENSIONS=pdf,doc,docx,xls,xlsx,jpg,jpeg,png,gif
UPLOAD_FOLDER=/app/uploads
EOF

    echo "✅ .env file created successfully"
    echo ""
fi

echo "🐳 Pulling Docker images from Docker Hub..."
docker pull veekay8/task-management-backend:1.0.0
docker pull veekay8/task-management-frontend:1.0.0
echo "✅ Images pulled successfully"
echo ""

echo "🚀 Deploying application..."
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d
echo ""

echo "⏳ Waiting for services to start..."
sleep 10

echo ""
echo "========================================="
echo "✅ Deployment Complete!"
echo "========================================="
echo ""
echo "🌐 Access your application:"
echo "   Frontend: http://localhost:3000"
echo "   Backend API: http://localhost:5000/api"
echo ""
echo "📊 Check status:"
echo "   docker-compose ps"
echo ""
echo "📝 View logs:"
echo "   docker-compose logs -f"
echo ""
echo "🛑 Stop application:"
echo "   docker-compose down"
echo ""
