# Quick Deployment Guide

## One-Command Deployment 🚀

Deploy the entire Task Management Application with **one command** - no manual configuration needed!

### Prerequisites
- Docker installed (20.10+)
- Docker Compose installed (2.0+)
- 2GB+ available RAM
- Ports 3000, 5000, 5432 available

---

## Windows Deployment

### Option 1: PowerShell (Recommended)
```powershell
.\deploy.ps1
```

### Option 2: Command Prompt
```cmd
deploy.bat
```

---

## Linux/Mac Deployment

```bash
./deploy.sh
```

---

## What the Script Does Automatically

✅ **Checks prerequisites** - Verifies Docker and Docker Compose are installed  
✅ **Generates secure secrets** - Uses Docker to create random keys (no Python needed)  
✅ **Creates .env file** - Auto-configures all environment variables  
✅ **Fixes HOSTNAME issues** - Handles Windows hostname conflicts automatically  
✅ **Pulls Docker images** - Downloads pre-built images from Docker Hub  
✅ **Deploys application** - Starts all services with production settings  

---

## After Deployment

Once deployment completes, access your application:

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:5000/api

### Useful Commands

**Check Status:**
```bash
docker-compose ps
```

**View Logs:**
```bash
docker-compose logs -f
```

**Stop Application:**
```bash
docker-compose down
```

**Restart Services:**
```bash
docker-compose restart
```

---

## Manual Deployment (Alternative)

If you prefer manual deployment or need to customize settings:

1. **Copy environment template:**
   ```bash
   cp .env.production .env
   ```

2. **Generate secrets using Docker:**
   ```bash
   # SECRET_KEY
   docker run --rm python:3.12-alpine python -c "import secrets; print(secrets.token_hex(32))"
   
   # JWT_SECRET_KEY
   docker run --rm python:3.12-alpine python -c "import secrets; print(secrets.token_hex(32))"
   
   # POSTGRES_PASSWORD
   docker run --rm python:3.12-alpine python -c "import secrets; print(secrets.token_urlsafe(32))"
   ```

3. **Edit .env file** - Update the generated secrets

4. **Deploy:**
   ```bash
   docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d
   ```

---

## Troubleshooting

### Script Permission Denied (Linux/Mac)
```bash
chmod +x deploy.sh
```

### PowerShell Execution Policy Error (Windows)
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Port Already in Use
Stop existing containers:
```bash
docker-compose down
```

### Re-generate Secrets
Run the deployment script again and answer "Yes" when prompted about regenerating secrets.

---

## Production Deployment Considerations

For **production environments**, consider:

1. **Update API URL** in .env:
   ```bash
   NEXT_PUBLIC_API_URL=https://api.yourdomain.com/api
   ```

2. **Update CORS origins** in .env:
   ```bash
   CORS_ORIGINS=https://yourdomain.com,https://www.yourdomain.com
   ```

3. **Set up HTTPS/TLS** - Use a reverse proxy (nginx, Traefik) with SSL certificates

4. **Configure backups** - Set up automated database backups

5. **Monitor resources** - Set up logging and monitoring

---

## Clean Uninstall

To completely remove the application and all data:

```bash
docker-compose down -v
```

⚠️ **Warning**: This will delete all database data permanently!

---

For detailed information, see [DEPLOYMENT.md](DEPLOYMENT.md)
