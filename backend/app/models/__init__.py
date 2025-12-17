"""
============================================================
MODELS PACKAGE
============================================================

This file imports all models and makes them available.

When you write:
    from app.models import User, Task, Project

This file makes that possible by importing everything here.
"""

# Import all models
from app.models.user import User, UserRole
from app.models.project import Project, ProjectMember, ProjectStatus
from app.models.task import Task, Comment, Attachment, TaskStatus, TaskPriority

# Make all models available when importing from app.models
__all__ = [
    # User models
    'User',
    'UserRole',
    
    # Project models
    'Project',
    'ProjectMember',
    'ProjectStatus',
    
    # Task models
    'Task',
    'TaskStatus',
    'TaskPriority',
    'Comment',
    'Attachment',
]
