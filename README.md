#  Task Management Application

A complete multi-tier task management system with Kanban board interface, built with modern technologies and industry best practices.

##  Project Structure

This project is built in **6 phases**, each with comprehensive documentation and explanations:

###  Phase 1: Project Structure & Database Setup (COMPLETED)
- PostgreSQL database with Docker
- Complete schema with 8 tables
- Environment configuration
- Development setup

** Read**: `PHASE_1_SUMMARY.md` for detailed explanation

###  Phase 2: Backend API with Flask (IN PROGRESS - Part 1 Complete!)
-  Flask application structure
-  SQLAlchemy ORM models
-  Configuration system
-  Authentication endpoints (next)
-  Task CRUD endpoints (next)
-  Project management endpoints (next)

** Read**: 
- `PHASE_2_GUIDE.md` - Complete explanation for beginners
- `PHASE_2_PART1_COMPLETE.md` - What we just built
- `PHASE_2_VISUAL_SUMMARY.md` - Visual summary with diagrams
- `PHASE_2_QUICK_REFERENCE.md` - Commands and code examples

###  Phase 3: Frontend React Application
- TypeScript + React setup
- API integration
- Form handling
- Routing

###  Phase 4: File Storage Integration
- AWS S3 / Azure Blob
- File upload/download
- Attachment management

###  Phase 5: Authentication & Authorization
- JWT tokens
- Password hashing
- Role-based access control
- Protected routes

###  Phase 6: Kanban Board UI
- Drag-and-drop interface
- Real-time updates
- Filtering and search

## ️ Tech Stack

### Backend (Tier 2)
- **Python Flask** - Web framework
- **SQLAlchemy** - ORM
- **PostgreSQL** - Database
- **JWT** - Authentication

### Frontend (Tier 1)
- **React + TypeScript** - UI framework
- **Tailwind CSS** - Styling
- **React Query** - Data fetching
- **React DnD** - Drag and drop

### Infrastructure
- **Docker** - Containerization
- **PostgreSQL 15** - Database
- **AWS S3** - File storage

##  Quick Start

### Prerequisites
- Docker Desktop
- Python 3.10+
- Node.js 18+

### 1. Start Database
```bash
# Start PostgreSQL in Docker
docker-compose up -d

# Verify it's running
docker ps
```

### 2. Setup Environment
```bash
# Copy environment template
cp .env.example .env
```

### 3. Connect to Database
```bash
# Default credentials (development only):
# Host: localhost
# Port: 5432
# Database: taskmanagement_db
# Username: taskapp_user
# Password: devpassword123
```

##  Documentation

- **`PROJECT_GUIDE.md`** - Complete project overview and architecture
- **`PHASE_1_SUMMARY.md`** - Database setup and schema explanation
- **`database/init/01-schema.sql`** - Database schema with detailed comments

##  Learning Objectives

Each phase teaches:
- **Multi-tier architecture** principles
- **Database design** and relationships
- **RESTful API** development
- **Authentication** and security
- **Modern frontend** development
- **Cloud storage** integration
- **Production-ready** code practices

##  Database Schema

```
users ──┬──< project_members >──┬── projects
        │                       │
        ├──< tasks              │
        ├──< comments           │
        ├──< attachments        │
        └──< activity_log       │
```

**8 Tables**: users, projects, project_members, tasks, comments, attachments, activity_log

##  Demo Users

The database includes 3 demo accounts:

| Email | Password | Role |
|-------|----------|------|
| admin@taskapp.com | admin123 | ADMIN |
| john@taskapp.com | admin123 | MANAGER |
| jane@taskapp.com | admin123 | MEMBER |

##  Features

-  User authentication & authorization
-  Project management
-  Task CRUD operations
-  Kanban board with drag-and-drop
-  Task comments
-  File attachments
-  Activity logging
-  Role-based permissions

##  License

This project is for educational purposes.

---

**Current Phase**: Phase 1 Complete - Ready for Phase 2 (Backend API Development)

**Questions?** Check the detailed documentation in each phase summary file.
