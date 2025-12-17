# Phase 2: Backend API Development - Complete Guide

## 🎯 What We're Building

A **REST API** (Application Programming Interface) that:
- Accepts requests from the frontend
- Processes business logic
- Talks to the database
- Returns responses (usually in JSON format)

## 🧒 Simple Analogy

Think of the backend as a **smart robot waiter** in a restaurant:

1. **Customer (Frontend)**: "I want to see all my tasks!"
2. **Robot Waiter (API)**: "Let me check the kitchen..."
3. **Kitchen (Backend Logic)**: "Are you allowed? Let me verify..."
4. **Storage Room (Database)**: "Here are your tasks!"
5. **Robot Waiter**: "Here you go!" (Returns JSON data)

## 📚 What is REST API?

**REST** = **RE**presentational **S**tate **T**ransfer

It's a way for computers to talk using HTTP (same as websites):

| Action | HTTP Method | Example | What it does |
|--------|-------------|---------|--------------|
| Get data | GET | `GET /api/tasks` | "Show me all tasks" |
| Create new | POST | `POST /api/tasks` | "Create a new task" |
| Update | PUT | `PUT /api/tasks/123` | "Update task #123" |
| Delete | DELETE | `DELETE /api/tasks/123` | "Delete task #123" |

## 🏗️ Backend Structure (Like a Building)

```
backend/
├── app/                          # Main application folder
│   ├── __init__.py              # Creates the Flask app (the building itself)
│   ├── config.py                # Settings (like building blueprints)
│   │
│   ├── models/                   # Database tables (like file cabinets)
│   │   ├── __init__.py
│   │   ├── user.py              # User information storage
│   │   ├── project.py           # Project storage
│   │   └── task.py              # Task storage
│   │
│   ├── routes/                   # API endpoints (like building entrances)
│   │   ├── __init__.py
│   │   ├── auth.py              # /api/auth/* (login, register)
│   │   ├── tasks.py             # /api/tasks/* (task operations)
│   │   └── projects.py          # /api/projects/* (project operations)
│   │
│   ├── services/                 # Business logic (the workers inside)
│   │   ├── __init__.py
│   │   ├── auth_service.py      # Authentication logic
│   │   └── task_service.py      # Task logic
│   │
│   └── utils/                    # Helper tools (like building tools)
│       ├── __init__.py
│       ├── decorators.py        # Code shortcuts
│       └── validators.py        # Data checking
│
├── migrations/                   # Database version control
├── tests/                        # Automated testing
├── requirements.txt              # List of Python packages needed
└── run.py                        # Start the server (turn on the lights)
```

## 🔧 Technologies We're Using

### 1. Flask
**What it is**: A Python web framework (like a toolkit for building web apps)
**Why we use it**: Simple, flexible, and perfect for APIs

```python
# Simple Flask example
from flask import Flask
app = Flask(__name__)

@app.route('/hello')  # Create an endpoint
def hello():
    return "Hello World!"  # Return response
```

### 2. SQLAlchemy
**What it is**: An ORM (Object-Relational Mapper)
**Why we use it**: Write Python code instead of SQL

**Without ORM (SQL)**:
```sql
SELECT * FROM users WHERE email = 'john@example.com';
```

**With ORM (Python)**:
```python
User.query.filter_by(email='john@example.com').first()
```

### 3. Flask-JWT-Extended
**What it is**: Library for creating secure tokens
**Why we use it**: Authentication without storing passwords everywhere

**How JWT works**:
```
Login → Server checks password → Creates special token → 
User stores token → Uses token for future requests
```

### 4. Marshmallow
**What it is**: Converts Python objects to JSON and validates data
**Why we use it**: Makes sure data is correct before saving

```python
# User sends: {"email": "notanemail", "age": "abc"}
# Marshmallow says: "Email is invalid! Age must be a number!"
```

## 📋 API Endpoints We'll Build

### Authentication (`/api/auth/`)
```
POST /api/auth/register
  - Creates new user account
  - Input: email, password, name
  - Output: success message

POST /api/auth/login
  - Logs in user
  - Input: email, password
  - Output: JWT token + user info

POST /api/auth/logout
  - Logs out user
  - Input: token
  - Output: success message
```

### Tasks (`/api/tasks/`)
```
GET /api/tasks
  - Get all tasks (with filters)
  - Query params: ?status=TODO&priority=HIGH
  - Output: list of tasks

GET /api/tasks/:id
  - Get one specific task
  - Output: task details

POST /api/tasks
  - Create new task
  - Input: title, description, status, priority
  - Output: created task

PUT /api/tasks/:id
  - Update existing task
  - Input: any fields to update
  - Output: updated task

DELETE /api/tasks/:id
  - Delete a task
  - Output: success message
```

### Projects (`/api/projects/`)
```
GET /api/projects
  - Get all projects
  - Output: list of projects

POST /api/projects
  - Create new project
  - Input: name, description
  - Output: created project

GET /api/projects/:id
  - Get project details
  - Output: project + tasks + members

PUT /api/projects/:id
  - Update project
  - Output: updated project

DELETE /api/projects/:id
  - Delete project
  - Output: success message
```

## 🔐 How Authentication Works (Step-by-Step)

### Registration Flow:
```
1. User fills form: email, password, name
2. Frontend sends: POST /api/auth/register
3. Backend receives data
4. Backend checks: 
   - Is email format valid?
   - Does email already exist?
   - Is password strong enough?
5. Backend hashes password (makes it unreadable)
   - "password123" becomes "$2b$12$abc123xyz..."
6. Backend saves to database
7. Backend responds: "Account created!"
```

### Login Flow:
```
1. User enters: email + password
2. Frontend sends: POST /api/auth/login
3. Backend finds user by email
4. Backend compares password hash
   - User typed: "password123"
   - Database has: "$2b$12$abc123xyz..."
   - Backend checks if they match
5. If match: Create JWT token
   - Token = special encrypted string
   - Contains: user_id, email, expiration
6. Backend responds: {token: "eyJ0eX...", user: {...}}
7. Frontend stores token
8. Frontend includes token in future requests
```

### Protected Route Flow:
```
1. User wants to create task
2. Frontend sends: POST /api/tasks
   Headers: Authorization: Bearer eyJ0eX...
3. Backend checks token:
   - Is it valid?
   - Is it expired?
   - Which user does it belong to?
4. If valid: Process request
5. If invalid: Return error "Unauthorized"
```

## 🎨 Request/Response Examples

### Creating a Task (JSON Format)

**Request**:
```json
POST /api/tasks
Headers: {
  "Authorization": "Bearer eyJ0eXAiOiJKV1QiLCJ...",
  "Content-Type": "application/json"
}
Body: {
  "title": "Complete Phase 2",
  "description": "Build the backend API",
  "status": "IN_PROGRESS",
  "priority": "HIGH",
  "project_id": "uuid-123-456",
  "due_date": "2025-12-20T12:00:00Z"
}
```

**Response** (Success - 201 Created):
```json
{
  "success": true,
  "data": {
    "id": "uuid-789-012",
    "title": "Complete Phase 2",
    "description": "Build the backend API",
    "status": "IN_PROGRESS",
    "priority": "HIGH",
    "project_id": "uuid-123-456",
    "assignee_id": null,
    "reporter_id": "uuid-current-user",
    "due_date": "2025-12-20T12:00:00Z",
    "created_at": "2025-12-16T10:30:00Z",
    "updated_at": "2025-12-16T10:30:00Z"
  },
  "message": "Task created successfully"
}
```

**Response** (Error - 400 Bad Request):
```json
{
  "success": false,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Title is required",
    "fields": {
      "title": ["This field is required"]
    }
  }
}
```

## 🛡️ Security Features

### 1. Password Hashing
```python
# Never store plain passwords!
plain_password = "mypassword123"

# Hash it (one-way encryption)
hashed = bcrypt.hash(plain_password)
# Result: "$2b$12$AbC123XyZ..."

# Later, when user logs in:
user_typed = "mypassword123"
is_correct = bcrypt.verify(user_typed, hashed)  # True/False
```

### 2. JWT Tokens
```python
# Create token
token = jwt.encode({
    'user_id': '123',
    'email': 'user@example.com',
    'exp': datetime.utcnow() + timedelta(hours=24)
}, SECRET_KEY)

# Verify token
try:
    data = jwt.decode(token, SECRET_KEY)
    user_id = data['user_id']  # "123"
except:
    return "Invalid token!"
```

### 3. Input Validation
```python
# Check data before saving
if not email_is_valid(email):
    return "Invalid email format!"

if len(password) < 8:
    return "Password too short!"

if priority not in ['LOW', 'MEDIUM', 'HIGH', 'URGENT']:
    return "Invalid priority!"
```

## 📊 Error Handling

Good APIs always handle errors gracefully:

```python
try:
    task = Task.query.get(task_id)
    if not task:
        return {"error": "Task not found"}, 404
    
    return {"data": task.to_dict()}, 200
    
except ValidationError as e:
    return {"error": str(e)}, 400
    
except Exception as e:
    logger.error(f"Unexpected error: {e}")
    return {"error": "Internal server error"}, 500
```

**HTTP Status Codes**:
- `200 OK` - Success!
- `201 Created` - New item created
- `400 Bad Request` - Your data is wrong
- `401 Unauthorized` - You need to login
- `403 Forbidden` - You don't have permission
- `404 Not Found` - Item doesn't exist
- `500 Internal Server Error` - Server messed up

## 🧪 Testing the API

We'll use **curl** or **Postman** to test:

```bash
# Register new user
curl -X POST http://localhost:5000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"test123","full_name":"Test User"}'

# Login
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"test123"}'

# Get tasks (with token)
curl -X GET http://localhost:5000/api/tasks \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

## 🎯 What You'll Learn

By the end of Phase 2, you'll understand:
- ✅ How to build REST APIs
- ✅ How authentication works (JWT)
- ✅ How to connect Python to databases (ORM)
- ✅ How to validate and secure data
- ✅ How HTTP requests/responses work
- ✅ How to structure a professional backend

---

**Ready to code?** Let's start building! 🚀
