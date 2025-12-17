"""
============================================================
PROJECT MODEL
============================================================

This file defines Project and ProjectMember models.

Projects organize tasks into workspaces/categories.
Think of it like folders that contain related tasks.
"""

from app import db
from datetime import datetime
import uuid
from enum import Enum as PyEnum
from sqlalchemy.dialects.postgresql import UUID


# ============================================================
# ENUM CLASSES
# ============================================================

class ProjectStatus(PyEnum):
    """
    Project lifecycle statuses
    
    PLANNING: Not started yet, in planning phase
    ACTIVE: Currently working on it
    ON_HOLD: Paused temporarily
    COMPLETED: Finished!
    ARCHIVED: Old project, kept for reference
    """
    PLANNING = 'PLANNING'
    ACTIVE = 'ACTIVE'
    ON_HOLD = 'ON_HOLD'
    COMPLETED = 'COMPLETED'
    ARCHIVED = 'ARCHIVED'


# ============================================================
# PROJECT MODEL
# ============================================================

class Project(db.Model):
    """
    Project model - represents a project/workspace
    
    Projects group related tasks together.
    Example: "Website Redesign", "Mobile App V2", "Marketing Campaign"
    
    Attributes:
        id: Unique identifier
        name: Project name
        description: Project details
        status: Current project status
        color: UI color code (hex)
        owner_id: User who created the project
        start_date: When project started
        end_date: Target completion date
        created_at: Creation timestamp
        updated_at: Last modification timestamp
    """
    
    __tablename__ = 'projects'
    
    # ========================================
    # COLUMNS
    # ========================================
    
    id = db.Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        comment='Unique project identifier'
    )
    
    # Project name - must be unique per user for clarity
    name = db.Column(
        db.String(255),
        nullable=False,
        comment='Project name'
    )
    
    # Description - optional detailed explanation
    description = db.Column(
        db.Text,
        nullable=True,
        comment='Project description'
    )
    
    # Status - where is this project in its lifecycle?
    # Using name='project_status' to match existing database enum type
    status = db.Column(
        db.Enum(ProjectStatus, name='project_status'),
        default=ProjectStatus.PLANNING,
        nullable=False,
        index=True,
        comment='Project status'
    )
    
    # Color - for visual identification in UI (e.g., '#3B82F6' = blue)
    color = db.Column(
        db.String(7),  # 7 characters for hex color (#RRGGBB)
        default='#3B82F6',
        nullable=False,
        comment='Project color code (hex)'
    )
    
    # Owner - who created this project?
    # Foreign key to users table
    owner_id = db.Column(
        UUID(as_uuid=True),
        db.ForeignKey('users.id', ondelete='CASCADE'),  # Delete project if owner deleted
        nullable=False,
        index=True,
        comment='Project owner user ID'
    )
    
    # Date range - when does this project run?
    start_date = db.Column(
        db.Date,
        nullable=True,
        comment='Project start date'
    )
    
    end_date = db.Column(
        db.Date,
        nullable=True,
        comment='Project target end date'
    )
    
    # Timestamps
    created_at = db.Column(
        db.DateTime(timezone=True),
        default=datetime.utcnow,
        nullable=False,
        comment='Project creation timestamp'
    )
    
    updated_at = db.Column(
        db.DateTime(timezone=True),
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
        comment='Last modification timestamp'
    )
    
    # ========================================
    # RELATIONSHIPS
    # ========================================
    
    # Tasks in this project
    # One project has many tasks (one-to-many)
    tasks = db.relationship(
        'Task',
        backref='project',
        lazy='dynamic',
        cascade='all, delete-orphan'  # Delete all tasks if project deleted
    )
    
    # Project members (users who can access this project)
    # Many-to-many relationship through ProjectMember table
    members = db.relationship(
        'ProjectMember',
        backref='project',
        lazy='dynamic',
        cascade='all, delete-orphan'
    )
    
    # ========================================
    # UTILITY METHODS
    # ========================================
    
    def to_dict(self, include_tasks=False, include_members=False):
        """
        Convert project to dictionary for JSON response
        
        Args:
            include_tasks (bool): Include list of tasks?
            include_members (bool): Include list of members?
            
        Returns:
            dict: Project data
        """
        data = {
            'id': str(self.id),
            'name': self.name,
            'description': self.description,
            'status': self.status.value,
            'color': self.color,
            'owner_id': str(self.owner_id),
            'start_date': self.start_date.isoformat() if self.start_date else None,
            'end_date': self.end_date.isoformat() if self.end_date else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }
        
        # Optionally include related data
        if include_tasks:
            data['tasks'] = [task.to_dict() for task in self.tasks.all()]
            data['task_count'] = self.tasks.count()
        
        if include_members:
            data['members'] = [member.to_dict() for member in self.members.all()]
            data['member_count'] = self.members.count()
        
        return data
    
    def add_member(self, user_id, role='MEMBER'):
        """
        Add a user to this project
        
        Args:
            user_id (str): User ID to add
            role (str): Member's role in project
            
        Returns:
            ProjectMember: Created membership
        """
        from app.models.user import UserRole
        
        # Check if already a member
        existing = ProjectMember.query.filter_by(
            project_id=self.id,
            user_id=user_id
        ).first()
        
        if existing:
            return existing
        
        # Create new membership
        member = ProjectMember(
            project_id=self.id,
            user_id=user_id,
            role=UserRole[role]
        )
        db.session.add(member)
        db.session.commit()
        return member
    
    def remove_member(self, user_id):
        """
        Remove a user from this project
        
        Args:
            user_id (str): User ID to remove
        """
        member = ProjectMember.query.filter_by(
            project_id=self.id,
            user_id=user_id
        ).first()
        
        if member:
            db.session.delete(member)
            db.session.commit()
    
    def is_member(self, user_id):
        """
        Check if user is a member of this project
        
        Args:
            user_id (str): User ID to check
            
        Returns:
            bool: True if user is member
        """
        return ProjectMember.query.filter_by(
            project_id=self.id,
            user_id=user_id
        ).first() is not None
    
    def __repr__(self):
        return f'<Project: {self.name}>'


# ============================================================
# PROJECT MEMBER MODEL (Many-to-Many Relationship)
# ============================================================

class ProjectMember(db.Model):
    """
    ProjectMember model - links users to projects
    
    This is a "junction table" or "association table"
    It creates a many-to-many relationship:
    - One user can be in many projects
    - One project can have many users
    
    Attributes:
        id: Unique identifier
        project_id: Which project?
        user_id: Which user?
        role: User's role in this project
        joined_at: When user joined project
    """
    
    __tablename__ = 'project_members'
    
    # ========================================
    # COLUMNS
    # ========================================
    
    id = db.Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        comment='Unique membership identifier'
    )
    
    # Foreign keys to link project and user
    project_id = db.Column(
        UUID(as_uuid=True),
        db.ForeignKey('projects.id', ondelete='CASCADE'),
        nullable=False,
        index=True,
        comment='Project ID'
    )
    
    user_id = db.Column(
        UUID(as_uuid=True),
        db.ForeignKey('users.id', ondelete='CASCADE'),
        nullable=False,
        index=True,
        comment='User ID'
    )
    
    # Role - user's permissions in this specific project
    # Can be different from their global role
    # Using name='user_role' to match existing database enum type
    from app.models.user import UserRole
    role = db.Column(
        db.Enum(UserRole, name='user_role'),
        default=UserRole.MEMBER,
        nullable=False,
        comment='Member role in project'
    )
    
    # When did this user join the project?
    joined_at = db.Column(
        db.DateTime(timezone=True),
        default=datetime.utcnow,
        nullable=False,
        comment='Membership creation timestamp'
    )
    
    # Ensure one user can only be added once per project
    __table_args__ = (
        db.UniqueConstraint('project_id', 'user_id', name='uq_project_user'),
    )
    
    # ========================================
    # UTILITY METHODS
    # ========================================
    
    def to_dict(self):
        """Convert membership to dictionary"""
        return {
            'id': str(self.id),
            'project_id': str(self.project_id),
            'user_id': str(self.user_id),
            'role': self.role.value,
            'joined_at': self.joined_at.isoformat() if self.joined_at else None,
            'user': self.user.to_dict() if self.user else None
        }
    
    def __repr__(self):
        return f'<ProjectMember: {self.user_id} in {self.project_id}>'
