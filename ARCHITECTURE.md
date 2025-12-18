# ️ Architecture Diagrams

## Multi-Tier Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                         CLIENT BROWSER                          │
│                      (User's Web Browser)                       │
└───────────────────────────┬─────────────────────────────────────┘
                            │
                            │ HTTPS Requests
                            │
┌───────────────────────────▼─────────────────────────────────────┐
│                    TIER 1: PRESENTATION LAYER                   │
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │              React Application (Port 3000)              │   │
│  │                                                         │   │
│  │  • Kanban Board UI                                      │   │
│  │  • Task Management Forms                                │   │
│  │  • User Authentication UI                               │   │
│  │  • Real-time Updates                                    │   │
│  │  • Drag-and-Drop Interface                              │   │
│  │                                                         │   │
│  │  Technologies:                                          │   │
│  │  - React 18 + TypeScript                                │   │
│  │  - Tailwind CSS                                         │   │
│  │  - React Query (Data Fetching)                          │   │
│  │  - React DnD (Drag & Drop)                              │   │
│  │  - Axios (HTTP Client)                                  │   │
│  └─────────────────────────────────────────────────────────┘   │
└───────────────────────────┬─────────────────────────────────────┘
                            │
                            │ REST API Calls (JSON)
                            │ GET, POST, PUT, DELETE /api/*
                            │
┌───────────────────────────▼─────────────────────────────────────┐
│                  TIER 2: APPLICATION/LOGIC LAYER                │
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │            Flask/FastAPI Server (Port 5000)             │   │
│  │                                                         │   │
│  │  ┌───────────────────────────────────────────────┐     │   │
│  │  │         API Routes (Controllers)              │     │   │
│  │  │  /api/auth/*  - Authentication                │     │   │
│  │  │  /api/users/* - User Management                │     │   │
│  │  │  /api/projects/* - Projects                   │     │   │
│  │  │  /api/tasks/* - Tasks CRUD                    │     │   │
│  │  │  /api/comments/* - Comments                   │     │   │
│  │  └───────────────────────────────────────────────┘     │   │
│  │                          │                              │   │
│  │  ┌───────────────────────▼───────────────────────┐     │   │
│  │  │         Business Logic (Services)             │     │   │
│  │  │  • Task Management Logic                      │     │   │
│  │  │  • User Authorization Checks                  │     │   │
│  │  │  • Data Validation                            │     │   │
│  │  │  • File Processing                            │     │   │
│  │  └───────────────────────────────────────────────┘     │   │
│  │                          │                              │   │
│  │  ┌───────────────────────▼───────────────────────┐     │   │
│  │  │         Data Access Layer (Models)            │     │   │
│  │  │  • SQLAlchemy ORM                             │     │   │
│  │  │  • Database Models                            │     │   │
│  │  │  • Query Builders                             │     │   │
│  │  └───────────────────────────────────────────────┘     │   │
│  │                                                         │   │
│  │  Technologies:                                          │   │
│  │  - Python 3.10+                                         │   │
│  │  - Flask / FastAPI                                      │   │
│  │  - SQLAlchemy (ORM)                                     │   │
│  │  - PyJWT (Authentication)                               │   │
│  │  - Marshmallow (Serialization)                          │   │
│  │  - Boto3 (AWS S3)                                       │   │
│  └─────────────────────────────────────────────────────────┘   │
└───────────────────────────┬─────────────────────────────────────┘
                            │
                            │ SQL Queries
                            │ SELECT, INSERT, UPDATE, DELETE
                            │
┌───────────────────────────▼─────────────────────────────────────┐
│                     TIER 3: DATA LAYER                          │
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │         PostgreSQL Database (Port 5432)                 │   │
│  │                                                         │   │
│  │  Tables:                                                │   │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐             │   │
│  │  │  users   │  │ projects │  │  tasks   │             │   │
│  │  └──────────┘  └──────────┘  └──────────┘             │   │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐             │   │
│  │  │ comments │  │attachments│  │activity  │             │   │
│  │  └──────────┘  └──────────┘  └──────────┘             │   │
│  │  ┌──────────────┐                                      │   │
│  │  │project_members│                                      │   │
│  │  └──────────────┘                                      │   │
│  │                                                         │   │
│  │  Features:                                              │   │
│  │  • ACID Transactions                                    │   │
│  │  • Foreign Key Constraints                              │   │
│  │  • Indexes for Performance                              │   │
│  │  • JSONB Support                                        │   │
│  │  • UUID Primary Keys                                    │   │
│  └─────────────────────────────────────────────────────────┘   │
└───────────────────────────┬─────────────────────────────────────┘
                            │
┌───────────────────────────▼─────────────────────────────────────┐
│                    TIER 4: STORAGE LAYER                        │
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │              AWS S3 / Azure Blob Storage                │   │
│  │                                                         │   │
│  │  • Task Attachments (PDFs, Documents)                   │   │
│  │  • User Avatars                                         │   │
│  │  • Project Files                                        │   │
│  │  • Uploaded Images                                      │   │
│  │                                                         │   │
│  │  Features:                                              │   │
│  │  • Scalable Storage                                     │   │
│  │  • CDN Integration                                      │   │
│  │  • Secure Access (Presigned URLs)                       │   │
│  └─────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
```

## Data Flow Example: Creating a Task

```
User Action                     Frontend                Backend                  Database
    │                              │                       │                        │
    │  1. Click "Create Task"      │                       │                        │
    ├────────────────────────────> │                       │                        │
    │                              │                       │                        │
    │  2. Fill Form & Submit       │                       │                        │
    ├────────────────────────────> │                       │                        │
    │                              │                       │                        │
    │                              │ 3. POST /api/tasks    │                        │
    │                              │   {title, description}│                        │
    │                              ├──────────────────────>│                        │
    │                              │                       │                        │
    │                              │                       │ 4. Validate Data       │
    │                              │                       │    Check Auth          │
    │                              │                       │    Verify Permissions  │
    │                              │                       │                        │
    │                              │                       │ 5. INSERT INTO tasks   │
    │                              │                       ├───────────────────────>│
    │                              │                       │                        │
    │                              │                       │ 6. Return New Task ID  │
    │                              │                       │<───────────────────────┤
    │                              │                       │                        │
    │                              │ 7. 201 Created        │                        │
    │                              │    {id, title, ...}   │                        │
    │                              │<──────────────────────┤                        │
    │                              │                       │                        │
    │  8. Show Success & Update UI │                       │                        │
    │<──────────────────────────── │                       │                        │
    │                              │                       │                        │
```

## Database Schema Relationships

```
┌─────────────────────┐
│       users         │
│─────────────────────│
│ id (PK)            │
│ email              │◄──────────┐
│ password_hash      │           │
│ full_name          │           │
│ role               │           │
│ created_at         │           │
└──────────┬──────────┘           │
           │                      │
           │ owner_id             │ user_id
           │                      │
           │         ┌────────────┴───────────────┐
           │         │                            │
┌──────────▼─────────────────┐         ┌─────────┴──────────────┐
│       projects             │         │   project_members      │
│────────────────────────────│         │────────────────────────│
│ id (PK)                   │◄────────┤ project_id (FK)        │
│ name                      │         │ user_id (FK)           │
│ description               │         │ role                   │
│ status                    │         │ joined_at              │
│ owner_id (FK) ────────────┘         └────────────────────────┘
│ created_at                │
└──────────┬─────────────────┘
           │
           │ project_id
           │
┌──────────▼─────────────────┐
│        tasks               │
│────────────────────────────│
│ id (PK)                   │
│ title                     │
│ description               │
│ status                    │
│ priority                  │
│ project_id (FK) ──────────┘
│ assignee_id (FK) ─────────┐
│ reporter_id (FK) ─────────┤───────> users
│ position                  │
│ due_date                  │
│ created_at                │
└──────────┬─────────────────┘
           │
           ├─────────────────┬──────────────────┐
           │                 │                  │
           │ task_id         │ task_id          │ task_id
           │                 │                  │
┌──────────▼───────┐  ┌──────▼──────────┐  ┌───▼──────────────┐
│    comments      │  │  attachments    │  │  activity_log    │
│──────────────────│  │─────────────────│  │──────────────────│
│ id (PK)         │  │ id (PK)        │  │ id (PK)         │
│ task_id (FK)    │  │ task_id (FK)   │  │ task_id (FK)    │
│ user_id (FK)────┤  │ uploaded_by ───┤  │ user_id (FK)────┤──> users
│ content         │  │ filename       │  │ action          │
│ created_at      │  │ storage_url    │  │ changes (JSONB) │
└─────────────────┘  │ uploaded_at    │  │ created_at      │
                     └────────────────┘  └─────────────────┘
```

## Authentication Flow (Phase 5)

```
┌────────┐                 ┌─────────┐                ┌──────────┐
│ Client │                 │ Backend │                │ Database │
└────┬───┘                 └────┬────┘                └─────┬────┘
     │                          │                           │
     │ 1. POST /api/auth/login  │                           │
     │    {email, password}     │                           │
     ├─────────────────────────>│                           │
     │                          │                           │
     │                          │ 2. Query user by email    │
     │                          ├──────────────────────────>│
     │                          │                           │
     │                          │ 3. Return user + hash     │
     │                          │<──────────────────────────┤
     │                          │                           │
     │                          │ 4. Verify password hash   │
     │                          │    bcrypt.compare()       │
     │                          │                           │
     │                          │ 5. Generate JWT token     │
     │                          │    jwt.encode()           │
     │                          │                           │
     │ 6. Return token          │                           │
     │    {token, user_info}    │                           │
     │<─────────────────────────┤                           │
     │                          │                           │
     │ 7. Store token           │                           │
     │    (localStorage)        │                           │
     │                          │                           │
     │ 8. Subsequent requests   │                           │
     │    Header: Authorization:│                           │
     │    Bearer <token>        │                           │
     ├─────────────────────────>│                           │
     │                          │                           │
     │                          │ 9. Verify & decode token  │
     │                          │    jwt.decode()           │
     │                          │                           │
     │                          │ 10. Process request       │
     │                          │                           │
```

## File Upload Flow (Phase 4)

```
┌────────┐        ┌─────────┐        ┌──────────┐        ┌─────┐
│ Client │        │ Backend │        │ Database │        │ S3  │
└────┬───┘        └────┬────┘        └─────┬────┘        └──┬──┘
     │                 │                    │                │
     │ 1. Select file  │                    │                │
     │    & Upload     │                    │                │
     ├────────────────>│                    │                │
     │                 │                    │                │
     │                 │ 2. Validate file   │                │
     │                 │    (type, size)    │                │
     │                 │                    │                │
     │                 │ 3. Generate        │                │
     │                 │    unique filename │                │
     │                 │                    │                │
     │                 │ 4. Upload to S3    │                │
     │                 ├────────────────────┼───────────────>│
     │                 │                    │                │
     │                 │ 5. S3 URL returned │                │
     │                 │<────────────────────┼───────────────┤
     │                 │                    │                │
     │                 │ 6. Save metadata   │                │
     │                 │    to database     │                │
     │                 ├───────────────────>│                │
     │                 │                    │                │
     │ 7. Success      │                    │                │
     │    response     │                    │                │
     │<────────────────┤                    │                │
     │                 │                    │                │
```

## Deployment Architecture (Production)

```
                        ┌──────────────┐
                        │   Internet   │
                        └───────┬──────┘
                                │
                    ┌───────────▼──────────┐
                    │    Load Balancer     │
                    │  (AWS ALB / Nginx)   │
                    └───────────┬──────────┘
                                │
                ┌───────────────┴────────────────┐
                │                                │
    ┌───────────▼──────────┐        ┌───────────▼──────────┐
    │   Frontend (Static)  │        │   Backend API        │
    │   Vercel / Netlify   │        │   Docker Container   │
    │   - React Build      │        │   - Flask App        │
    │   - CDN Cached       │        │   - Auto-scaling     │
    └──────────────────────┘        └───────────┬──────────┘
                                                 │
                                    ┌────────────┴──────────┐
                                    │                       │
                        ┌───────────▼────────┐  ┌──────────▼────────┐
                        │  PostgreSQL RDS    │  │   AWS S3 Bucket   │
                        │  - Primary DB      │  │   - File Storage  │
                        │  - Read Replicas   │  │   - CloudFront CDN│
                        └────────────────────┘  └───────────────────┘
```
