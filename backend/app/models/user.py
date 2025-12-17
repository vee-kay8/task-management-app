"""
============================================================
USER MODEL
============================================================

This file defines the User table in Python using SQLAlchemy ORM.

What is a Model?
- A model is a Python class that represents a database table
- Each class attribute = database column
- Each instance of the class = one row in the table

Example:
    # Create a new user (Python object)
    user = User(email='john@example.com', full_name='John Doe')
    
    # This becomes SQL:
    # INSERT INTO users (email, full_name) VALUES ('john@example.com', 'John Doe')
"""

from app import db, bcrypt
from datetime import datetime
import uuid
from enum import Enum as PyEnum
from sqlalchemy.dialects.postgresql import UUID


# ============================================================
# ENUM CLASSES
# ============================================================
# These define allowed values for certain fields

class UserRole(PyEnum):
    """
    User roles for permission management
    
    - ADMIN: Full access to everything
    - MANAGER: Can manage projects and teams
    - MEMBER: Can create and manage own tasks
    - VIEWER: Read-only access
    """
    ADMIN = 'ADMIN'
    MANAGER = 'MANAGER'
    MEMBER = 'MEMBER'
    VIEWER = 'VIEWER'


# ============================================================
# USER MODEL
# ============================================================
class User(db.Model):
    """
    User model - represents a user account
    
    This class maps to the 'users' table in PostgreSQL.
    Each attribute is a column in that table.
    
    Attributes:
        id: Unique identifier (UUID)
        email: User's email address (unique)
        password_hash: Encrypted password
        full_name: User's display name
        avatar_url: Profile picture URL
        role: User role (ADMIN, MANAGER, MEMBER, VIEWER)
        is_active: Account enabled/disabled
        email_verified: Email confirmation status
        created_at: Account creation timestamp
        updated_at: Last modification timestamp
        last_login: Last login timestamp
    """
    
    # Table name in database
    __tablename__ = 'users'
    
    # ========================================
    # COLUMNS
    # ========================================
    
    # Primary Key - unique identifier for each user
    # UUID is better than integer ID because:
    # - Can't guess other user IDs
    # - Globally unique across databases
    # - Works better in distributed systems
    id = db.Column(
        UUID(as_uuid=True),  # Native PostgreSQL UUID type
        primary_key=True,
        default=uuid.uuid4,  # Auto-generate UUID
        comment='Unique user identifier'
    )
    
    # Email - must be unique, required, indexed for fast lookup
    email = db.Column(
        db.String(255),
        unique=True,  # No two users can have same email
        nullable=False,  # Must provide email
        index=True,  # Create index for faster queries
        comment='User email address'
    )
    
    # Password Hash - NEVER store plain passwords!
    # We store bcrypt hash, not the actual password
    password_hash = db.Column(
        db.String(255),
        nullable=False,
        comment='Bcrypt hashed password'
    )
    
    # Full Name - user's display name
    full_name = db.Column(
        db.String(255),
        nullable=False,
        comment='User full name'
    )
    
    # Avatar URL - profile picture (S3 URL in Phase 4)
    avatar_url = db.Column(
        db.String(500),
        nullable=True,  # Optional field
        comment='Profile picture URL'
    )
    
    # Role - permission level (ADMIN, MANAGER, MEMBER, VIEWER)
    # Using name='user_role' to match existing database enum type
    role = db.Column(
        db.Enum(UserRole, name='user_role'),
        default=UserRole.MEMBER,
        nullable=False,
        index=True,
        comment='User role for permissions'
    )
    
    # Account Status Flags
    is_active = db.Column(
        db.Boolean,
        default=True,
        nullable=False,
        comment='Account enabled/disabled'
    )
    
    email_verified = db.Column(
        db.Boolean,
        default=False,
        nullable=False,
        comment='Email verification status'
    )
    
    # Timestamps - automatic tracking
    created_at = db.Column(
        db.DateTime(timezone=True),
        default=datetime.utcnow,  # Auto-set when created
        nullable=False,
        comment='Account creation timestamp'
    )
    
    updated_at = db.Column(
        db.DateTime(timezone=True),
        default=datetime.utcnow,
        onupdate=datetime.utcnow,  # Auto-update when modified
        nullable=False,
        comment='Last modification timestamp'
    )
    
    last_login = db.Column(
        db.DateTime(timezone=True),
        nullable=True,  # Null until first login
        comment='Last login timestamp'
    )
    
    # ========================================
    # RELATIONSHIPS
    # ========================================
    # These create connections to other tables
    
    # Projects created by this user
    # One user can create many projects (one-to-many)
    owned_projects = db.relationship(
        'Project',
        foreign_keys='Project.owner_id',
        backref='owner',
        lazy='dynamic',  # Don't load until accessed
        cascade='all, delete-orphan'  # Delete projects if user deleted
    )
    
    # Tasks assigned to this user
    assigned_tasks = db.relationship(
        'Task',
        foreign_keys='Task.assignee_id',
        backref='assignee',
        lazy='dynamic'
    )
    
    # Tasks created by this user
    reported_tasks = db.relationship(
        'Task',
        foreign_keys='Task.reporter_id',
        backref='reporter',
        lazy='dynamic'
    )
    
    # Project memberships (through project_members table)
    project_memberships = db.relationship(
        'ProjectMember',
        backref='user',
        lazy='dynamic',
        cascade='all, delete-orphan'
    )
    
    # Comments made by this user
    comments = db.relationship(
        'Comment',
        foreign_keys='Comment.user_id',
        lazy='dynamic',
        cascade='all, delete-orphan'
    )
    
    # ========================================
    # PASSWORD METHODS
    # ========================================
    
    def set_password(self, password):
        """
        Hash and store password
        
        This converts plain text password into encrypted hash.
        We NEVER store passwords in plain text!
        
        Args:
            password (str): Plain text password
            
        Example:
            user = User(email='test@example.com')
            user.set_password('mypassword123')
            # password_hash becomes: "$2b$12$randomhash..."
        """
        self.password_hash = bcrypt.generate_password_hash(password).decode('utf-8')
    
    def check_password(self, password):
        """
        Verify password against stored hash
        
        This checks if provided password matches the stored hash.
        Used during login.
        
        Args:
            password (str): Plain text password to check
            
        Returns:
            bool: True if password matches, False otherwise
            
        Example:
            user = User.query.filter_by(email='test@example.com').first()
            if user.check_password('wrongpassword'):
                print('Login success!')  # Won't print
        """
        return bcrypt.check_password_hash(self.password_hash, password)
    
    # ========================================
    # UTILITY METHODS
    # ========================================
    
    def to_dict(self, include_email=False):
        """
        Convert user object to dictionary (for JSON responses)
        
        This is used when sending user data to frontend.
        We DON'T include password_hash for security!
        
        Args:
            include_email (bool): Whether to include email (privacy)
            
        Returns:
            dict: User data as dictionary
            
        Example:
            user = User.query.first()
            data = user.to_dict()
            # Returns: {'id': '...', 'full_name': 'John', ...}
        """
        data = {
            'id': str(self.id),
            'full_name': self.full_name,
            'avatar_url': self.avatar_url,
            'role': self.role.value,  # Convert enum to string
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'last_login': self.last_login.isoformat() if self.last_login else None
        }
        
        # Only include email if explicitly requested
        if include_email:
            data['email'] = self.email
            data['email_verified'] = self.email_verified
        
        return data
    
    def has_permission(self, required_role):
        """
        Check if user has required permission level
        
        Role hierarchy: ADMIN > MANAGER > MEMBER > VIEWER
        
        Args:
            required_role (UserRole): Minimum required role
            
        Returns:
            bool: True if user has permission
            
        Example:
            user = User.query.first()
            if user.has_permission(UserRole.MANAGER):
                # Allow access to manager features
        """
        role_hierarchy = {
            UserRole.VIEWER: 1,
            UserRole.MEMBER: 2,
            UserRole.MANAGER: 3,
            UserRole.ADMIN: 4
        }
        
        return role_hierarchy.get(self.role, 0) >= role_hierarchy.get(required_role, 0)
    
    def update_last_login(self):
        """
        Update last login timestamp
        
        Call this when user successfully logs in.
        
        Example:
            user = User.query.filter_by(email='test@example.com').first()
            user.update_last_login()
            db.session.commit()
        """
        self.last_login = datetime.utcnow()
        db.session.commit()
    
    # ========================================
    # SPECIAL METHODS
    # ========================================
    
    def __repr__(self):
        """
        String representation of user (for debugging)
        
        This is what you see when you print a User object.
        
        Example:
            user = User.query.first()
            print(user)  # Output: <User: john@example.com>
        """
        return f'<User: {self.email}>'
    
    def __str__(self):
        """
        Human-readable string (for logs)
        """
        return f'{self.full_name} ({self.email})'
