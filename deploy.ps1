# =============================================================================
# Task Management App - Automated Deployment Script (Windows PowerShell)
# =============================================================================
# This script automates the entire deployment process:
# - Generates secure random keys using Docker
# - Creates .env file automatically
# - Pulls Docker images from Docker Hub
# - Deploys the application
#
# Usage: .\deploy.ps1
# =============================================================================

$ErrorActionPreference = "Stop"

Write-Host "=========================================" -ForegroundColor Cyan
Write-Host "Task Management App - Deployment" -ForegroundColor Cyan
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host ""

# Check if Docker is installed
try {
    docker --version | Out-Null
    Write-Host "✅ Docker detected" -ForegroundColor Green
} catch {
    Write-Host "❌ Error: Docker is not installed!" -ForegroundColor Red
    Write-Host "Please install Docker from: https://docs.docker.com/desktop/windows/install/" -ForegroundColor Yellow
    exit 1
}

# Check if Docker Compose is installed
try {
    docker-compose --version | Out-Null
    Write-Host "✅ Docker Compose detected" -ForegroundColor Green
} catch {
    Write-Host "❌ Error: Docker Compose is not installed!" -ForegroundColor Red
    exit 1
}

Write-Host ""

# Check if .env already exists
$SkipEnv = $false
if (Test-Path .env) {
    Write-Host "⚠️  .env file already exists!" -ForegroundColor Yellow
    $response = Read-Host "Do you want to regenerate secrets? (y/N)"
    if ($response -notmatch "^[Yy]$") {
        Write-Host "Using existing .env file..." -ForegroundColor Yellow
        $SkipEnv = $true
    }
}

if (-not $SkipEnv) {
    Write-Host "🔐 Generating secure keys using Docker..." -ForegroundColor Cyan
    
    # Generate SECRET_KEY
    $SECRET_KEY = (docker run --rm python:3.12-alpine python -c 'import secrets; print(secrets.token_hex(32))').Trim()
    Write-Host "✅ SECRET_KEY generated" -ForegroundColor Green
    
    # Generate JWT_SECRET_KEY
    $JWT_SECRET_KEY = (docker run --rm python:3.12-alpine python -c 'import secrets; print(secrets.token_hex(32))').Trim()
    Write-Host "✅ JWT_SECRET_KEY generated" -ForegroundColor Green
    
    # Generate POSTGRES_PASSWORD
    $POSTGRES_PASSWORD = (docker run --rm python:3.12-alpine python -c 'import secrets; print(secrets.token_urlsafe(32))').Trim()
    Write-Host "✅ POSTGRES_PASSWORD generated" -ForegroundColor Green
    Write-Host ""
    
    Write-Host "📝 Creating .env file..." -ForegroundColor Cyan
    
    # Create .env file content
    $envContent = @"
# =============================================================================
# PRODUCTION ENVIRONMENT CONFIGURATION
# Auto-generated on $(Get-Date -Format "yyyy-MM-dd HH:mm:ss")
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
POSTGRES_PASSWORD=$POSTGRES_PASSWORD

DATABASE_URL=postgresql://taskapp_user:${POSTGRES_PASSWORD}@db:5432/taskmanagement_db

DB_POOL_SIZE=20
DB_MAX_OVERFLOW=40

# ===================================
# BACKEND (Flask) CONFIGURATION
# ===================================
FLASK_APP=run.py
FLASK_HOST=0.0.0.0
FLASK_PORT=5000

SECRET_KEY=$SECRET_KEY
JWT_SECRET_KEY=$JWT_SECRET_KEY

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
"@

    # Write .env file
    $envContent | Out-File -FilePath .env -Encoding ASCII -NoNewline
    Write-Host "✅ .env file created successfully" -ForegroundColor Green
    Write-Host ""
}

Write-Host "🐳 Pulling Docker images from Docker Hub..." -ForegroundColor Cyan
docker pull veekay8/task-management-backend:1.0.0
docker pull veekay8/task-management-frontend:1.0.0
Write-Host "✅ Images pulled successfully" -ForegroundColor Green
Write-Host ""

Write-Host "🚀 Deploying application..." -ForegroundColor Cyan
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d
Write-Host ""

Write-Host "⏳ Waiting for services to start..." -ForegroundColor Yellow
Start-Sleep -Seconds 10

Write-Host ""
Write-Host "=========================================" -ForegroundColor Green
Write-Host "✅ Deployment Complete!" -ForegroundColor Green
Write-Host "=========================================" -ForegroundColor Green
Write-Host ""
Write-Host "🌐 Access your application:" -ForegroundColor Cyan
Write-Host "   Frontend: http://localhost:3000" -ForegroundColor White
Write-Host "   Backend API: http://localhost:5000/api" -ForegroundColor White
Write-Host ""
Write-Host "📊 Check status:" -ForegroundColor Cyan
Write-Host "   docker-compose ps" -ForegroundColor White
Write-Host ""
Write-Host "📝 View logs:" -ForegroundColor Cyan
Write-Host "   docker-compose logs -f" -ForegroundColor White
Write-Host ""
Write-Host "🛑 Stop application:" -ForegroundColor Cyan
Write-Host "   docker-compose down" -ForegroundColor White
Write-Host ""
