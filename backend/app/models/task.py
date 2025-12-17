"""
============================================================
TASK MODEL
============================================================

This is the core model of our application!
Tasks are the main items users create and manage.

Think of a task like a sticky note on a Kanban board:
- Title: "What needs to be done?"
- Description: "Details and notes"
- Status: "Which column is it in?" (TODO, IN_PROGRESS, etc.)
- Priority: "How urgent is it?"
"""

from app import db
from datetime import datetime
import uuid
from enum import Enum as PyEnum
from sqlalchemy.dialects import postgresql
from sqlalchemy.dialects.postgresql import UUID


# ============================================================
# ENUM CLASSES
# ============================================================

class TaskStatus(PyEnum):
    """
    Task status - represents which stage task is in
    
    This maps to Kanban board columns:
    - TODO: Not started yet (backlog)
    - IN_PROGRESS: Currently being worked on
    - IN_REVIEW: Waiting for review/approval
    - DONE: Completed!
    - ARCHIVED: Old task, kept for reference
    """
    TODO = 'TODO'
    IN_PROGRESS = 'IN_PROGRESS'
    IN_REVIEW = 'IN_REVIEW'
    DONE = 'DONE'
    ARCHIVED = 'ARCHIVED'


class TaskPriority(PyEnum):
    """
    Task priority - how urgent/important is this?
    
    - URGENT: Drop everything, do this now! 🔥
    - HIGH: Important, do soon
    - MEDIUM: Normal priority
    - LOW: Nice to have, can wait
    """
    LOW = 'LOW'
    MEDIUM = 'MEDIUM'
    HIGH = 'HIGH'
    URGENT = 'URGENT'


# ============================================================
# TASK MODEL
# ============================================================

class Task(db.Model):
    """
    Task model - the main entity of our application
    
    Represents a single task/item to be completed.
    
    Attributes:
        id: Unique identifier
        title: Task name/summary
        description: Detailed explanation
        status: Current status (TODO, IN_PROGRESS, etc.)
        priority: Importance level (LOW, MEDIUM, HIGH, URGENT)
        project_id: Which project does this belong to?
        assignee_id: Who is responsible for this?
        reporter_id: Who created this task?
        position: Order within status column (for drag-drop)
        due_date: Deadline
        completed_at: When was it finished?
        estimated_hours: How long should it take?
        actual_hours: How long did it actually take?
        tags: Categories/labels (JSON array)
        created_at: When was it created?
        updated_at: When was it last modified?
    """
    
    __tablename__ = 'tasks'
    
    # ========================================
    # COLUMNS
    # ========================================
    
    id = db.Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        comment='Unique task identifier'
    )
    
    # Title - short summary of task
    # This is what shows on the Kanban card
    title = db.Column(
        db.String(500),
        nullable=False,
        comment='Task title/summary'
    )
    
    # Description - detailed information
    # Supports markdown formatting
    description = db.Column(
        db.Text,
        nullable=True,
        comment='Task detailed description (supports markdown)'
    )
    
    # Status - which column is this task in?
    # Using name='task_status' to match existing database enum type
    status = db.Column(
        db.Enum(TaskStatus, name='task_status'),
        default=TaskStatus.TODO,
        nullable=False,
        index=True,  # Index for filtering by status
        comment='Task current status'
    )
    
    # Priority - how important is this?
    # Using name='task_priority' to match existing database enum type
    priority = db.Column(
        db.Enum(TaskPriority, name='task_priority'),
        default=TaskPriority.MEDIUM,
        nullable=False,
        index=True,  # Index for filtering by priority
        comment='Task priority level'
    )
    
    # Project - which project does this task belong to?
    # Foreign key to projects table
    project_id = db.Column(
        UUID(as_uuid=True),
        db.ForeignKey('projects.id', ondelete='CASCADE'),
        nullable=False,
        index=True,
        comment='Project ID this task belongs to'
    )
    
    # Assignee - who is working on this?
    # Foreign key to users table
    # nullable=True because tasks can be unassigned
    assignee_id = db.Column(
        UUID(as_uuid=True),
        db.ForeignKey('users.id', ondelete='SET NULL'),  # Keep task if user deleted
        nullable=True,
        index=True,
        comment='User ID assigned to this task'
    )
    
    # Reporter - who created this task?
    # Foreign key to users table
    reporter_id = db.Column(
        UUID(as_uuid=True),
        db.ForeignKey('users.id', ondelete='CASCADE'),
        nullable=False,
        index=True,
        comment='User ID who created this task'
    )
    
    # Position - for drag-and-drop ordering
    # Tasks in same status are ordered by this number
    # Lower number = higher on list
    # Example: position=0 is at top, position=100 is below it
    position = db.Column(
        db.Integer,
        default=0,
        nullable=False,
        comment='Position within status column (for ordering)'
    )
    
    # Due date - deadline for completion
    due_date = db.Column(
        db.DateTime(timezone=True),
        nullable=True,
        index=True,  # Index for finding overdue tasks
        comment='Task deadline'
    )
    
    # Completed at - when was it marked as done?
    # Auto-set when status changes to DONE
    completed_at = db.Column(
        db.DateTime(timezone=True),
        nullable=True,
        comment='Completion timestamp'
    )
    
    # Time tracking
    estimated_hours = db.Column(
        db.Numeric(5, 2),  # 5 digits total, 2 after decimal (e.g., 123.45)
        nullable=True,
        comment='Estimated time in hours'
    )
    
    actual_hours = db.Column(
        db.Numeric(5, 2),
        nullable=True,
        comment='Actual time spent in hours'
    )
    
    # Tags - categories/labels stored as JSON array
    # Example: ["bug", "frontend", "urgent"]
    # JSONB allows efficient querying of tags with GIN index
    tags = db.Column(
        postgresql.JSONB,  # Use JSONB for better performance and GIN indexing
        default=list,  # Default to empty list []
        nullable=False,
        comment='Task tags/labels (JSON array)'
    )
    
    # Timestamps
    created_at = db.Column(
        db.DateTime(timezone=True),
        default=datetime.utcnow,
        nullable=False,
        comment='Task creation timestamp'
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
    
    # Comments on this task
    # One task can have many comments (one-to-many)
    comments = db.relationship(
        'Comment',
        backref='task',
        lazy='dynamic',
        cascade='all, delete-orphan',  # Delete comments if task deleted
        order_by='Comment.created_at'  # Order by oldest first
    )
    
    # File attachments
    attachments = db.relationship(
        'Attachment',
        backref='task',
        lazy='dynamic',
        cascade='all, delete-orphan'
    )
    
    # ========================================
    # INDEXES
    # ========================================
    # Composite index for efficient Kanban queries
    # Often we query: "Get tasks in project X with status Y ordered by position"
    __table_args__ = (
        db.Index('idx_task_project_status_position', 'project_id', 'status', 'position'),
    )
    
    # ========================================
    # UTILITY METHODS
    # ========================================
    
    def to_dict(self, include_relations=False):
        """
        Convert task to dictionary for JSON response
        
        Args:
            include_relations (bool): Include comments and attachments?
            
        Returns:
            dict: Task data
            
        Example:
            task = Task.query.first()
            data = task.to_dict()
            # Returns: {'id': '...', 'title': '...', ...}
        """
        data = {
            'id': str(self.id),
            'title': self.title,
            'description': self.description,
            'status': self.status.value,  # Convert enum to string
            'priority': self.priority.value,
            'project_id': str(self.project_id),
            'assignee_id': str(self.assignee_id) if self.assignee_id else None,
            'reporter_id': str(self.reporter_id),
            'position': self.position,
            'due_date': self.due_date.isoformat() if self.due_date else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'estimated_hours': float(self.estimated_hours) if self.estimated_hours else None,
            'actual_hours': float(self.actual_hours) if self.actual_hours else None,
            'tags': self.tags or [],
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }
        
        # Include assignee info if exists
        if self.assignee:
            data['assignee'] = self.assignee.to_dict()
        
        # Include reporter info
        if self.reporter:
            data['reporter'] = self.reporter.to_dict()
        
        # Optionally include related data
        if include_relations:
            data['comments'] = [comment.to_dict() for comment in self.comments.all()]
            data['comment_count'] = self.comments.count()
            data['attachments'] = [att.to_dict() for att in self.attachments.all()]
            data['attachment_count'] = self.attachments.count()
        
        return data
    
    def mark_complete(self):
        """
        Mark task as completed
        
        Sets status to DONE and records completion time.
        
        Example:
            task = Task.query.get(task_id)
            task.mark_complete()
            db.session.commit()
        """
        self.status = TaskStatus.DONE
        self.completed_at = datetime.utcnow()
    
    def is_overdue(self):
        """
        Check if task is overdue
        
        Returns:
            bool: True if past due date and not completed
        """
        if not self.due_date:
            return False
        
        if self.status == TaskStatus.DONE:
            return False
        
        return datetime.utcnow() > self.due_date
    
    def add_tag(self, tag):
        """
        Add a tag to this task
        
        Args:
            tag (str): Tag name to add
        """
        if not self.tags:
            self.tags = []
        
        if tag not in self.tags:
            self.tags.append(tag)
            # Need to explicitly mark as modified for JSON columns
            db.session.add(self)
    
    def remove_tag(self, tag):
        """
        Remove a tag from this task
        
        Args:
            tag (str): Tag name to remove
        """
        if self.tags and tag in self.tags:
            self.tags.remove(tag)
            db.session.add(self)
    
    def update_position(self, new_position, new_status=None):
        """
        Update task position (for drag-and-drop)
        
        Args:
            new_position (int): New position number
            new_status (TaskStatus): New status if moving to different column
        """
        self.position = new_position
        
        if new_status and new_status != self.status:
            self.status = new_status
            
            # If moving to DONE, set completed_at
            if new_status == TaskStatus.DONE:
                self.completed_at = datetime.utcnow()
    
    def __repr__(self):
        return f'<Task: {self.title[:50]}>'
    
    def __str__(self):
        return f'{self.title} ({self.status.value})'


# ============================================================
# COMMENT MODEL
# ============================================================

class Comment(db.Model):
    """
    Comment model - discussion on tasks
    
    Users can add comments to tasks for communication.
    Supports threaded replies.
    """
    
    __tablename__ = 'comments'
    
    id = db.Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )
    
    # Which task is this comment on?
    task_id = db.Column(
        UUID(as_uuid=True),
        db.ForeignKey('tasks.id', ondelete='CASCADE'),
        nullable=False,
        index=True
    )
    
    # Who wrote this comment?
    user_id = db.Column(
        UUID(as_uuid=True),
        db.ForeignKey('users.id', ondelete='CASCADE'),
        nullable=False,
        index=True
    )
    
    # Comment text (supports markdown)
    content = db.Column(
        db.Text,
        nullable=False
    )
    
    # For threaded comments (optional - Phase 6)
    parent_comment_id = db.Column(
        UUID(as_uuid=True),
        db.ForeignKey('comments.id', ondelete='CASCADE'),
        nullable=True
    )
    
    # Track if edited
    is_edited = db.Column(
        db.Boolean,
        default=False
    )
    
    created_at = db.Column(
        db.DateTime(timezone=True),
        default=datetime.utcnow,
        nullable=False
    )
    
    updated_at = db.Column(
        db.DateTime(timezone=True),
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )
    
    # Relationships
    user = db.relationship('User', foreign_keys=[user_id], backref='user_comments')
    
    def to_dict(self):
        """Convert comment to dictionary"""
        return {
            'id': str(self.id),
            'task_id': str(self.task_id),
            'user_id': str(self.user_id),
            'content': self.content,
            'is_edited': self.is_edited,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'author': self.user.to_dict() if self.user else None
        }
    
    def __repr__(self):
        return f'<Comment by {self.user_id} on {self.task_id}>'


# ============================================================
# ATTACHMENT MODEL
# ============================================================

class Attachment(db.Model):
    """
    Attachment model - files attached to tasks
    
    Users can upload files (docs, images, etc.) to tasks.
    Files are stored in S3 (Phase 4).
    """
    
    __tablename__ = 'attachments'
    
    id = db.Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )
    
    task_id = db.Column(
        UUID(as_uuid=True),
        db.ForeignKey('tasks.id', ondelete='CASCADE'),
        nullable=False,
        index=True
    )
    
    uploaded_by = db.Column(
        UUID(as_uuid=True),
        db.ForeignKey('users.id', ondelete='CASCADE'),
        nullable=False
    )
    
    # File information
    filename = db.Column(db.String(255), nullable=False)  # Sanitized filename
    original_filename = db.Column(db.String(255), nullable=False)  # Original name
    file_size = db.Column(db.BigInteger, nullable=False)  # Size in bytes
    mime_type = db.Column(db.String(100), nullable=False)  # e.g., 'image/png'
    
    # Storage URLs (S3)
    storage_url = db.Column(db.String(1000), nullable=False)  # Public URL
    storage_key = db.Column(db.String(500), nullable=False)  # S3 key for deletion
    
    uploaded_at = db.Column(
        db.DateTime(timezone=True),
        default=datetime.utcnow
    )
    
    # Relationships
    uploader = db.relationship('User', foreign_keys=[uploaded_by])
    
    def to_dict(self):
        """Convert attachment to dictionary"""
        return {
            'id': str(self.id),
            'task_id': str(self.task_id),
            'filename': self.filename,
            'original_filename': self.original_filename,
            'file_size': self.file_size,
            'mime_type': self.mime_type,
            'storage_url': self.storage_url,
            'uploaded_at': self.uploaded_at.isoformat(),
            'uploaded_by': self.uploader.to_dict() if self.uploader else None
        }
    
    def __repr__(self):
        return f'<Attachment: {self.filename}>'
