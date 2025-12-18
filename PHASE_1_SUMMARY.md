# Phase 1: Project Structure & Database Setup

##  What We Accomplished

### 1. Project Foundation
- Created comprehensive project documentation (`PROJECT_GUIDE.md`)
- Set up environment configuration template (`.env.example`)
- Configured `.gitignore` for security and cleanliness

### 2. Database Infrastructure
- **Docker Compose**: Automated PostgreSQL setup for local development
- **Database Schema**: Complete relational database design with 8 tables
- **Seed Data**: Demo users for testing

### 3. Architecture Overview

```
┌─────────────────────────────────────────────────────────┐
│                    FRONTEND (React)                     │
│  - User Interface                                       │
│  - Kanban Board                                         │
│  - Task Management UI                                   │
└──────────────────────┬──────────────────────────────────┘
                       │ HTTP/REST API
┌──────────────────────▼──────────────────────────────────┐
│                  BACKEND (Flask/FastAPI)                │
│  - Business Logic                                       │
│  - Authentication                                       │
│  - API Endpoints                                        │
└──────────────────────┬──────────────────────────────────┘
                       │ SQL Queries
┌──────────────────────▼──────────────────────────────────┐
│                DATABASE (PostgreSQL)                    │
│  - Users, Projects, Tasks                               │
│  - Comments, Attachments                                │
│  - Activity Logs                                        │
└─────────────────────────────────────────────────────────┘
```

## ️ Database Schema Explained

### Tables and Their Purpose

#### 1. **users** - User Account Management
- Stores authentication credentials (email, hashed password)
- User profiles (name, avatar, role)
- Roles: ADMIN, MANAGER, MEMBER, VIEWER
- Tracks login activity and account status

#### 2. **projects** - Project/Workspace Organization
- Groups tasks into projects
- Each project has an owner
- Status tracking (PLANNING, ACTIVE, COMPLETED, etc.)
- Optional date ranges for project timelines

#### 3. **project_members** - Team Collaboration
- Links users to projects (many-to-many relationship)
- Each user can be in multiple projects
- Role-based access per project

#### 4. **tasks** - The Core Entity
- Task details (title, description)
- Status: TODO, IN_PROGRESS, IN_REVIEW, DONE, ARCHIVED
- Priority: LOW, MEDIUM, HIGH, URGENT
- Assignment to users
- Position tracking for Kanban board ordering
- Time estimation and tracking
- Tags for categorization (stored as JSON)

#### 5. **comments** - Task Discussion
- Threaded comments on tasks
- Supports replies (parent_comment_id)
- Edit tracking

#### 6. **attachments** - File Management
- Links files to tasks
- Stores S3 URLs and metadata
- Tracks file size, type, and uploader

#### 7. **activity_log** - Audit Trail
- Records all changes (who did what, when)
- Stores before/after values as JSON
- Enables activity timeline features

### Relationships Diagram

```
users ──┬──< project_members >──┬── projects
        │                       │
        ├───────────────────────┤
        │                       │
        ├──< tasks (assignee)   │
        ├──< tasks (reporter)   │
        ├──< comments           │
        ├──< attachments        │
        └──< activity_log       │
                                 │
                          tasks ─┴──< comments
                                 └──< attachments
```

##  Getting Started

### Step 1: Start PostgreSQL
```bash
# Start PostgreSQL database in Docker
docker-compose up -d

# Verify it's running
docker ps
```

### Step 2: Verify Database
```bash
# Connect to PostgreSQL (password: devpassword123)
docker exec -it taskmanagement_postgres psql -U taskapp_user -d taskmanagement_db

# Inside psql, list tables:
\dt

# Exit psql:
\q
```

### Step 3: Create Environment File
```bash
# Copy example environment file
cp .env.example .env

# Edit .env with your actual values (or use defaults for development)
```

##  Database Features

### 1. **UUID Primary Keys**
- Globally unique identifiers
- Better for distributed systems
- No sequential ID guessing

### 2. **Timestamps with Timezone**
- All dates include timezone information
- Prevents timezone-related bugs
- Auto-updated via triggers

### 3. **ENUM Types**
- Type-safe status and priority values
- Database-level validation
- Better performance than string comparison

### 4. **Indexes**
- Optimized query performance
- Indexes on frequently queried columns
- GIN index for JSONB (tags) searching

### 5. **Cascading Deletes**
- Automatic cleanup of related records
- e.g., Deleting a task removes its comments and attachments
- Maintains referential integrity

### 6. **Soft Deletes Ready**
- `is_active` flag on users
- Can archive without deleting
- Preserves historical data

##  Testing the Database

### Demo Users Created
The database automatically creates 3 demo users:

1. **Admin User**
   - Email: `admin@taskapp.com`
   - Password: `admin123`
   - Role: ADMIN

2. **Manager User**
   - Email: `john@taskapp.com`
   - Password: `admin123`
   - Role: MANAGER

3. **Member User**
   - Email: `jane@taskapp.com`
   - Password: `admin123`
   - Role: MEMBER

### SQL Queries to Test

```sql
-- View all users
SELECT email, full_name, role FROM users;

-- Check database tables
SELECT table_name FROM information_schema.tables 
WHERE table_schema = 'public';

-- View enum types
SELECT * FROM pg_type WHERE typtype = 'e';
```

##  Key Concepts Explained

### 1. **Multi-Tier Architecture**
- **Separation of Concerns**: Each tier has specific responsibility
- **Frontend**: What user sees (React UI)
- **Backend**: Business logic and rules (Python Flask)
- **Database**: Data storage (PostgreSQL)
- **Storage**: File handling (S3 - Phase 4)

### 2. **Relational Database Design**
- **Normalization**: Eliminates data redundancy
- **Foreign Keys**: Maintains relationships between tables
- **Constraints**: Ensures data integrity

### 3. **Security Considerations**
- Passwords are hashed (never stored plain text)
- UUID prevents ID enumeration attacks
- Role-based access control
- Environment variables for secrets

##  Phase 1 Complete!

You now have:
-  Project structure and documentation
-  PostgreSQL database running in Docker
-  Complete database schema with 8 tables
-  Demo data for testing
-  Environment configuration template

##  Next: Phase 2 - Backend API Development

In the next phase, we'll build:
- Flask application structure
- RESTful API endpoints
- JWT authentication
- CRUD operations for tasks and projects
- Database ORM with SQLAlchemy
- Input validation and error handling

---

**Questions before moving to Phase 2?**
