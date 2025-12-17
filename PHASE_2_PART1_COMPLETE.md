# 🎓 Phase 2 - Part 1 Complete: Database Models

## What We Just Built

We've created the **Python representation** of our database! Think of it like this:

- **Phase 1**: We designed the database structure (SQL tables)
- **Phase 2 (Part 1)**: We created Python classes that mirror those tables (ORM models)

## 📚 What is ORM? (Simple Explanation)

**ORM** = **O**bject-**R**elational **M**apping

It's a translator between Python and SQL:

### Without ORM (Raw SQL):
```python
# Have to write SQL strings 😰
cursor.execute("SELECT * FROM users WHERE email = ?", (email,))
user = cursor.fetchone()
```

### With ORM (SQLAlchemy):
```python
# Write Python code! 😊
user = User.query.filter_by(email=email).first()
```

## 🗂️ Files We Created

### 1. **requirements.txt** - Package List
Lists all Python libraries we need:
- `Flask` - Web framework
- `SQLAlchemy` - Database ORM
- `Flask-JWT-Extended` - Authentication
- `Bcrypt` - Password encryption
- And more...

### 2. **run.py** - Server Starter
The "power button" for our backend:
```bash
python run.py  # Starts the server!
```

### 3. **app/__init__.py** - App Factory
Creates and configures the Flask app:
- Initializes database
- Sets up authentication
- Registers routes
- Handles errors

### 4. **app/config.py** - Settings
Three environments with different settings:
- **Development**: Debugging enabled, shows errors
- **Testing**: Uses test database
- **Production**: Secure, optimized

### 5. **Models** - Database Tables as Python Classes

#### **app/models/user.py** - User Model
```python
# Represents the users table
user = User(email='test@example.com', full_name='Test User')
user.set_password('secret123')  # Hashes password automatically!
db.session.add(user)
db.session.commit()  # Saves to database
```

**Key Features**:
- ✅ Password hashing (never stores plain text)
- ✅ User roles (ADMIN, MANAGER, MEMBER, VIEWER)
- ✅ Email validation
- ✅ Last login tracking

#### **app/models/project.py** - Project Models
```python
# Create a project
project = Project(
    name='Website Redesign',
    owner_id=user.id,
    color='#3B82F6'
)
db.session.add(project)
db.session.commit()

# Add team member
project.add_member(another_user.id, role='MEMBER')
```

**Two Models**:
- `Project`: The workspace/folder
- `ProjectMember`: Links users to projects (many-to-many)

#### **app/models/task.py** - Task Models
```python
# Create a task
task = Task(
    title='Complete Phase 2',
    description='Build the backend API',
    status=TaskStatus.TODO,
    priority=TaskPriority.HIGH,
    project_id=project.id,
    reporter_id=user.id
)
db.session.add(task)
db.session.commit()

# Add comment
comment = Comment(
    task_id=task.id,
    user_id=user.id,
    content='Great progress!'
)
```

**Three Models**:
- `Task`: The main item
- `Comment`: Discussion on tasks
- `Attachment`: Files attached to tasks

## 🧠 Key Concepts Explained

### 1. **Database Session**
Think of it like a shopping cart:
```python
db.session.add(task)      # Put item in cart
db.session.add(comment)   # Add another item
db.session.commit()       # Checkout (save to database)
db.session.rollback()     # Cancel (undo everything)
```

### 2. **Relationships**
Connect tables together:
```python
# One user has many tasks (one-to-many)
user.assigned_tasks  # Get all tasks for this user

# One project has many members (many-to-many)
project.members  # Get all users in project
```

### 3. **Enums**
Limited choices for fields:
```python
TaskStatus.TODO         # Valid ✅
TaskStatus.IN_PROGRESS  # Valid ✅
TaskStatus.FLYING       # Error! Not in enum ❌
```

### 4. **Methods on Models**
Models have helpful functions:
```python
# Password methods
user.set_password('secret')      # Hash and save
user.check_password('secret')    # Returns True/False

# Conversion methods
task.to_dict()                   # Convert to dictionary for JSON

# Status methods
task.mark_complete()             # Mark as done
task.is_overdue()                # Check if past deadline
```

## 🔄 How Models Connect

```
User ─┬─ owns ──→ Project ─┬─ contains ──→ Task
      │                     │
      ├─ member of ─→ ProjectMember
      │                     
      ├─ assigned to ──→ Task
      ├─ created ──→ Task
      └─ commented ──→ Comment ──→ Task
```

## 🚀 Next Steps

Now we'll:
1. **Set up the environment** (install packages)
2. **Create database migrations** (sync models with database)
3. **Build API routes** (authentication endpoints)
4. **Test the API** (create users, login, etc.)

## 📝 Setup Instructions

### Step 1: Create Virtual Environment
```bash
cd backend

# Create virtual environment
python -m venv venv

# Activate it
# On macOS/Linux:
source venv/bin/activate
# On Windows:
# venv\Scripts\activate

# You'll see (venv) in your terminal prompt
```

**What is a virtual environment?**
- Like a separate room for this project
- Keeps packages isolated from other projects
- Prevents conflicts

### Step 2: Install Dependencies
```bash
# Install all packages from requirements.txt
pip install -r requirements.txt

# This will take a minute...
# Installing Flask, SQLAlchemy, etc.
```

### Step 3: Create Environment File
```bash
# Copy example environment file
cp .env.example .env

# The .env file contains settings (database URL, secret keys, etc.)
# It's gitignored for security
```

### Step 4: Initialize Database Migrations
```bash
# Initialize Flask-Migrate
flask db init

# This creates a 'migrations' folder
# It tracks database changes over time
```

### Step 5: Create First Migration
```bash
# Create migration from our models
flask db migrate -m "Initial migration - create all tables"

# This generates SQL commands to create tables
# Based on our Python models
```

### Step 6: Apply Migration
```bash
# Apply migration to database
flask db upgrade

# This actually creates the tables in PostgreSQL
# Your models are now real tables!
```

### Step 7: Start the Server!
```bash
# Run the Flask server
python run.py

# You should see:
# 🚀 Task Management API Server Starting...
# 📍 Running on: http://localhost:5000
```

### Step 8: Test It!
Open your browser or use curl:
```bash
# Check if server is running
curl http://localhost:5000/

# Should return:
# {"name": "Task Management API", "status": "running", ...}

# Test routes
curl http://localhost:5000/api/auth/test
curl http://localhost:5000/api/tasks/test
```

## 🐛 Common Issues

### Issue: "Module not found"
**Solution**: Make sure virtual environment is activated
```bash
source venv/bin/activate  # (macOS/Linux)
```

### Issue: "Database connection failed"
**Solution**: Make sure PostgreSQL is running
```bash
docker-compose up -d
docker ps  # Check if running
```

### Issue: "Port 5000 already in use"
**Solution**: Change port in .env file
```bash
FLASK_PORT=5001
```

## 📊 What's in the Database Now?

After running migrations, your database has:
- ✅ `users` table
- ✅ `projects` table
- ✅ `project_members` table
- ✅ `tasks` table
- ✅ `comments` table
- ✅ `attachments` table

Plus all the demo users from Phase 1!

## 🎯 Progress Check

✅ Backend structure created
✅ Configuration system built
✅ Database models defined
✅ Package dependencies listed
✅ Ready for API routes!

---

**Next**: We'll build the authentication system (login/register) and task CRUD endpoints!

Let me know when you're ready to continue! 🚀
