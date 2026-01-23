# Task Management Application

![CI Pipeline](https://github.com/vee-kay8/task-management-app/workflows/CI%20Pipeline/badge.svg)
[![codecov](https://codecov.io/gh/vee-kay8/task-management-app/branch/main/graph/badge.svg)](https://codecov.io/gh/vee-kay8/task-management-app)

A full-stack task management application built with Flask (Python), Next.js (React/TypeScript), and PostgreSQL, fully containerized with Docker.

## 🚀 Quick Start (One Command!)

### Windows
```powershell
.\deploy.ps1
```

### Linux/Mac
```bash
./deploy.sh
```

**That's it!** The application will be running at:
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:5000/api

---

## 📋 Prerequisites

- Docker (20.10+)
- Docker Compose (2.0+)
- 2GB+ RAM
- Ports 3000, 5000, 5432 available

**No Python installation required!**

---

## 🎯 Features

### Application Features
- ✅ User authentication (register/login)
- ✅ Project management
- ✅ Task management with status tracking
- ✅ Priority levels
- ✅ Due dates
- ✅ User assignments
- ✅ RESTful API
- ✅ Modern responsive UI

### Deployment Features
- ✅ **Fully automated deployment**
- ✅ **One-command setup**
- ✅ **Cross-platform compatible**
- ✅ **No manual configuration**
- ✅ **Secure secret generation**
- ✅ **Production-ready**

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────┐
│           Docker Compose Stack                  │
├─────────────────────────────────────────────────┤
│                                                 │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐     │
│  │ Next.js  │→ │  Flask   │→ │PostgreSQL│     │
│  │ Frontend │  │  Backend │  │ Database │     │
│  │  :3000   │  │  :5000   │  │  :5432   │     │
│  └──────────┘  └──────────┘  └──────────┘     │
│      168MB         215MB          25MB          │
│                                                 │
│         taskapp_network (bridge)                │
└─────────────────────────────────────────────────┘
```

### Tech Stack

**Frontend:**
- Next.js 14
- React 18
- TypeScript
- Tailwind CSS
- Axios for API calls

**Backend:**
- Flask (Python)
- SQLAlchemy ORM
- JWT Authentication
- PostgreSQL
- Gunicorn (production server)

**Infrastructure:**
- Docker & Docker Compose
- Docker Hub for image distribution
- Alpine Linux base images (optimized size)
- Multi-stage builds

---

## 📦 What the Deployment Script Does

1. **Checks Prerequisites** - Verifies Docker and Docker Compose
2. **Generates Secrets** - Creates secure random keys using Docker
3. **Creates .env File** - Auto-configures all environment variables
4. **Pulls Images** - Downloads pre-built images from Docker Hub
5. **Deploys Services** - Starts all containers with production settings
6. **Verifies Health** - Ensures all services are running correctly

### No Python Needed!

Secrets are generated using Docker:
```bash
docker run --rm python:3.12-alpine python -c 'import secrets; print(secrets.token_hex(32))'
```

---

## 📚 Documentation

| Document | Description |
|----------|-------------|
| [QUICK_DEPLOY.md](QUICK_DEPLOY.md) | **Start here** - Quick deployment guide |
| [AUTOMATION_SUMMARY.md](AUTOMATION_SUMMARY.md) | How automation works |
| [DEPLOYMENT.md](DEPLOYMENT.md) | Comprehensive deployment guide |
| [DOCKER_HUB_CONFIG.md](DOCKER_HUB_CONFIG.md) | Docker Hub image details |
| [TROUBLESHOOTING.md](TROUBLESHOOTING.md) | Common issues and solutions |
| [OPERATIONS_RUNBOOK.md](OPERATIONS_RUNBOOK.md) | Operations and maintenance |
| [SECURITY.md](SECURITY.md) | Security best practices |

### Containerization Phases
- [CONTAINERIZATION_PHASE1.md](CONTAINERIZATION_PHASE1.md) - Backend
- [CONTAINERIZATION_PHASE2.md](CONTAINERIZATION_PHASE2.md) - Frontend
- [CONTAINERIZATION_PHASE3.md](CONTAINERIZATION_PHASE3.md) - Orchestration
- [CONTAINERIZATION_PHASE4.md](CONTAINERIZATION_PHASE4.md) - Environment
- [CONTAINERIZATION_PHASE5.md](CONTAINERIZATION_PHASE5.md) - Optimization
- [CONTAINERIZATION_PHASE6.md](CONTAINERIZATION_PHASE6.md) - Docker Hub
- [CONTAINERIZATION_PHASE7.md](CONTAINERIZATION_PHASE7.md) - Production

---

## 🔧 Common Commands

### Check Status
```bash
docker-compose ps
```

### View Logs
```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f frontend
docker-compose logs -f backend
docker-compose logs -f db
```

### Restart Services
```bash
# All services
docker-compose restart

# Specific service
docker-compose restart frontend
```

### Stop Application
```bash
docker-compose down
```

### Start Application
```bash
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d
```

---

## 🌐 Accessing the Application

After deployment:

1. **Open your browser** → http://localhost:3000
2. **Register** a new account
3. **Login** with your credentials
4. **Create projects** and **add tasks**

### API Endpoints

Base URL: `http://localhost:5000/api`

**Authentication:**
- `POST /auth/register` - Register new user
- `POST /auth/login` - Login user
- `POST /auth/refresh` - Refresh token

**Projects:**
- `GET /projects` - List all projects
- `POST /projects` - Create project
- `GET /projects/:id` - Get project details
- `PUT /projects/:id` - Update project
- `DELETE /projects/:id` - Delete project

**Tasks:**
- `GET /projects/:id/tasks` - List project tasks
- `POST /tasks` - Create task
- `GET /tasks/:id` - Get task details
- `PUT /tasks/:id` - Update task
- `DELETE /tasks/:id` - Delete task

---

## 🛠️ Development

### Local Development Setup

1. **Clone the repository:**
   ```bash
   git clone https://github.com/vee-kay8/task-management-app.git
   cd task-management-app
   ```

2. **Deploy with development settings:**
   ```bash
   docker-compose up -d --build
   ```

### Project Structure
```
task-management-app/
├── backend/              # Flask API
│   ├── app/
│   │   ├── models/      # Database models
│   │   ├── routes/      # API endpoints
│   │   └── utils/       # Utilities
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/            # Next.js UI
│   ├── app/            # App router pages
│   ├── components/     # React components
│   ├── Dockerfile
│   └── package.json
├── database/           # Database initialization
│   └── init/
├── docker-compose.yml  # Base configuration
├── docker-compose.prod.yml  # Production overrides
├── deploy.sh          # Linux/Mac deployment
├── deploy.ps1         # Windows deployment
└── deploy.bat         # Windows batch wrapper
```

---

## 🔐 Security

### Automated Security Features
- ✅ Cryptographically secure random secret generation
- ✅ Strong password requirements
- ✅ JWT token authentication
- ✅ Environment variables not committed to git
- ✅ Production-grade configurations
- ✅ Resource limits enforced
- ✅ Non-root container users

### Production Considerations

For production deployment:
1. Update `NEXT_PUBLIC_API_URL` to your domain
2. Update `CORS_ORIGINS` to your frontend domain
3. Set up HTTPS/TLS with reverse proxy
4. Configure database backups
5. Set up monitoring and logging
6. Use secrets management system

See [SECURITY.md](SECURITY.md) for details.

---

## 📊 Resource Usage

**Development:**
- Frontend: ~35 MB RAM
- Backend: ~206 MB RAM
- Database: ~18 MB RAM
- **Total: ~260 MB**

**Production Limits:**
- Frontend: 512 MB RAM (256 MB reserved)
- Backend: 1 GB RAM (512 MB reserved)
- Database: 2 GB RAM (1 GB reserved)

---

## 🐳 Docker Images

Images are hosted on Docker Hub:

- **Backend**: [veekay8/task-management-backend](https://hub.docker.com/r/veekay8/task-management-backend)
- **Frontend**: [veekay8/task-management-frontend](https://hub.docker.com/r/veekay8/task-management-frontend)

### Available Tags
- `1.0.0` - Specific version (recommended for production)
- `1.0` - Latest patch of 1.0.x
- `1` - Latest minor of 1.x.x
- `latest` - Most recent release

---

## 🆘 Troubleshooting

### Port Already in Use
```bash
docker-compose down
```

### Frontend Not Starting
Check logs:
```bash
docker-compose logs -f frontend
```

### Database Connection Issues
Verify database is healthy:
```bash
docker-compose exec db psql -U taskapp_user -d taskmanagement_db -c "SELECT 1;"
```

For more issues, see [TROUBLESHOOTING.md](TROUBLESHOOTING.md)

---

## � Documentation

### Main Documentation
- **[AWS Deployment Roadmap](AWS_DEPLOYMENT_ROADMAP.md)** - Complete 12-phase AWS deployment guide
- **[Deployment Guide](DEPLOYMENT.md)** - Production deployment instructions
- **[Security Documentation](SECURITY.md)** - Security best practices

### Detailed Guides
- **[AWS Phase Guides](docs/aws-guides/)** - Step-by-step guides for each deployment phase
- **[Completion Reports](docs/completion-reports/)** - Phase completion summaries
- **[Medium Article](docs/articles/MEDIUM_ARTICLE.md)** - Complete deployment journey story

### AWS Configuration
- **[AWS Config Files](aws/config/)** - Auto-scaling, budgets, and infrastructure configs

---

## ☁️ Cloud Deployment

**Live Production Application:** https://app.techveesolutions.com

The application is deployed on AWS with:
- Multi-AZ high availability
- Auto-scaling (1-4 tasks per service)
- Zero-downtime CI/CD deployments
- Cost-optimized infrastructure (~$92/month)
- CloudWatch monitoring and alarms

See [AWS_DEPLOYMENT_ROADMAP.md](AWS_DEPLOYMENT_ROADMAP.md) for complete deployment documentation.

---

## 📝 Version

**Current Version:** 1.0.0  
**Last Updated:** January 22, 2026  
**Deployment Status:** 11/12 phases complete (92%)

---

## 👨‍💻 Author

**vee-kay8**  
GitHub: https://github.com/vee-kay8

---

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

---

## 🙏 Acknowledgments

- Docker for containerization
- Docker Hub for image hosting
- Flask and Next.js communities
- PostgreSQL team

---

## 🚀 Getting Started Now

**Ready to deploy?**

```powershell
# Windows
.\deploy.ps1

# Linux/Mac
./deploy.sh
```

**Questions?** Check [QUICK_DEPLOY.md](QUICK_DEPLOY.md) or [DEPLOYMENT.md](DEPLOYMENT.md)

**Enjoy your Task Management Application!** 🎉
