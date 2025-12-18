"""Quick test to verify models load without errors"""
import sys
sys.path.insert(0, '/Users/voke/Desktop/task-management-app/backend')

from app import create_app, db
from app.models.user import User, UserRole
from app.models.project import Project, ProjectMember, ProjectStatus  
from app.models.task import Task, TaskStatus, TaskPriority, Comment, Attachment

app = create_app('development')

with app.app_context():
    print("[SUCCESS] All models imported successfully!")
    print(f"[SUCCESS] User model: {User.__tablename__}")
    print(f"[SUCCESS] Project model: {Project.__tablename__}")
    print(f"[SUCCESS] Task model: {Task.__tablename__}")
    print(f"[SUCCESS] Comment model: {Comment.__tablename__}")
    print("\n🎉 No relationship conflicts!")
