# 🎓 Phase 2: Backend API - Quick Reference

## 📁 Backend Structure (What We Built)

```
backend/
├── app/                          # Main application package
│   ├── __init__.py              # App factory (creates Flask app)
│   ├── config.py                # Configuration settings
│   │
│   ├── models/                   # Database models (ORM)
│   │   ├── __init__.py          # Exports all models
│   │   ├── user.py              # User model
│   │   ├── project.py           # Project + ProjectMember models
│   │   └── task.py              # Task, Comment, Attachment models
│   │
│   ├── routes/                   # API endpoints (coming next)
│   │   ├── __init__.py
│   │   ├── auth.py              # Login, register
│   │   ├── tasks.py             # Task CRUD
│   │   ├── projects.py          # Project CRUD
│   │   └── users.py             # User management
│   │
│   ├── services/                 # Business logic (coming next)
│   │   └── __init__.py
│   │
│   └── utils/                    # Helper functions (coming next)
│       └── __init__.py
│
├── migrations/                   # Database migrations (auto-generated)
├── .env                         # Environment variables (DON'T commit!)
├── .env.example                 # Environment template
├── requirements.txt             # Python dependencies
└── run.py                       # Server entry point
```

## 🚀 Quick Start Commands

```bash
# 1. Go to backend folder
cd backend

# 2. Create virtual environment (first time only)
python -m venv venv

# 3. Activate virtual environment
source venv/bin/activate  # macOS/Linux
# OR
venv\Scripts\activate  # Windows

# 4. Install dependencies (first time only)
pip install -r requirements.txt

# 5. Setup environment (first time only)
cp .env.example .env

# 6. Initialize database (first time only)
flask db init
flask db migrate -m "Initial migration"
flask db upgrade

# 7. Run the server
python run.py

# Server runs on: http://localhost:5000
```

## 📊 Database Models Cheat Sheet

### User Model
```python
from app.models import User, UserRole

# Create user
user = User(
    email='john@example.com',
    full_name='John Doe',
    role=UserRole.MEMBER
)
user.set_password('secret123')
db.session.add(user)
db.session.commit()

# Query users
user = User.query.filter_by(email='john@example.com').first()
all_users = User.query.all()
admins = User.query.filter_by(role=UserRole.ADMIN).all()

# Check password
if user.check_password('secret123'):
    print('Login success!')

# Convert to dict (for JSON)
user_data = user.to_dict(include_email=True)
```

### Project Model
```python
from app.models import Project, ProjectStatus

# Create project
project = Project(
    name='Website Redesign',
    description='Redesign company website',
    status=ProjectStatus.ACTIVE,
    owner_id=user.id,
    color='#3B82F6'
)
db.session.add(project)
db.session.commit()

# Add team member
project.add_member(user_id='uuid-123', role='MEMBER')

# Query projects
project = Project.query.get(project_id)
my_projects = Project.query.filter_by(owner_id=user.id).all()
active = Project.query.filter_by(status=ProjectStatus.ACTIVE).all()
```

### Task Model
```python
from app.models import Task, TaskStatus, TaskPriority

# Create task
task = Task(
    title='Design homepage',
    description='Create mockups for new homepage',
    status=TaskStatus.TODO,
    priority=TaskPriority.HIGH,
    project_id=project.id,
    reporter_id=user.id,
    assignee_id=user.id
)
db.session.add(task)
db.session.commit()

# Update task
task.status = TaskStatus.IN_PROGRESS
task.add_tag('design')
db.session.commit()

# Mark complete
task.mark_complete()
db.session.commit()

# Query tasks
task = Task.query.get(task_id)
project_tasks = Task.query.filter_by(project_id=project.id).all()
my_tasks = Task.query.filter_by(assignee_id=user.id).all()
urgent = Task.query.filter_by(priority=TaskPriority.URGENT).all()

# Complex query
from datetime import datetime
overdue = Task.query.filter(
    Task.due_date < datetime.utcnow(),
    Task.status != TaskStatus.DONE
).all()
```

### Comment Model
```python
from app.models import Comment

# Add comment
comment = Comment(
    task_id=task.id,
    user_id=user.id,
    content='This looks great!'
)
db.session.add(comment)
db.session.commit()

# Get task comments
comments = Comment.query.filter_by(task_id=task.id).all()
```

## 🔑 Common SQLAlchemy Queries

```python
# Get one record
user = User.query.get(user_id)                    # By ID
user = User.query.filter_by(email=email).first()  # By field

# Get all records
users = User.query.all()

# Filter
active_users = User.query.filter_by(is_active=True).all()

# Multiple conditions (AND)
tasks = Task.query.filter_by(
    status=TaskStatus.TODO,
    priority=TaskPriority.HIGH
).all()

# OR conditions
from sqlalchemy import or_
tasks = Task.query.filter(
    or_(
        Task.status == TaskStatus.TODO,
        Task.status == TaskStatus.IN_PROGRESS
    )
).all()

# Order by
tasks = Task.query.order_by(Task.created_at.desc()).all()

# Limit
recent_tasks = Task.query.order_by(Task.created_at.desc()).limit(10).all()

# Count
task_count = Task.query.filter_by(project_id=project.id).count()

# Pagination
page = Task.query.paginate(page=1, per_page=20)
tasks = page.items
total = page.total

# Relationships
user.assigned_tasks.all()     # All tasks assigned to user
project.tasks.all()            # All tasks in project
task.comments.all()            # All comments on task
```

## 🔧 Database Session Operations

```python
# Add new record
db.session.add(user)

# Add multiple records
db.session.add_all([user1, user2, user3])

# Save changes
db.session.commit()

# Undo changes (before commit)
db.session.rollback()

# Delete record
db.session.delete(task)
db.session.commit()

# Update record
user.full_name = 'New Name'
db.session.commit()
```

## 🐛 Common Errors & Solutions

### Error: "No module named 'app'"
**Solution**: Activate virtual environment
```bash
source venv/bin/activate
```

### Error: "Could not locate a Flask application"
**Solution**: Make sure you're in the backend folder
```bash
cd backend
python run.py
```

### Error: "sqlalchemy.exc.OperationalError"
**Solution**: Database not running or wrong URL
```bash
# Check database is running
docker ps

# Check DATABASE_URL in .env
DATABASE_URL=postgresql://taskapp_user:devpassword123@localhost:5432/taskmanagement_db
```

### Error: "Table doesn't exist"
**Solution**: Run migrations
```bash
flask db upgrade
```

## 📚 Helpful Commands

### Flask-Migrate Commands
```bash
# Initialize migrations (first time only)
flask db init

# Create new migration
flask db migrate -m "Description of changes"

# Apply migrations
flask db upgrade

# Undo last migration
flask db downgrade

# Show current migration
flask db current

# Show migration history
flask db history
```

### Python Shell (for testing)
```bash
# Open Flask shell (with app context)
flask shell

# Now you can test models:
>>> from app.models import User
>>> users = User.query.all()
>>> print(users)
```

## 🎯 Status Check

At this point, you have:
- ✅ Backend folder structure
- ✅ Flask application configured
- ✅ Database models created
- ✅ All dependencies installed
- ✅ Server running on port 5000

**Next**: Build authentication and CRUD endpoints!

## 📖 Further Reading

- Flask docs: https://flask.palletsprojects.com/
- SQLAlchemy docs: https://docs.sqlalchemy.org/
- Flask-JWT-Extended: https://flask-jwt-extended.readthedocs.io/

---

**Questions?** Check PHASE_2_PART1_COMPLETE.md for detailed explanations!
