"""
============================================================
USER MANAGEMENT ROUTES
============================================================

User profile and management endpoints:
- GET /api/users - List all users (admin only)
- GET /api/users/:id - Get specific user profile
- PUT /api/users/:id - Update user profile
- DELETE /api/users/:id - Deactivate user account (admin only)

Access Control:
- Public: None (all routes require authentication)
- User: Can view and update own profile
- Admin: Can view all users, update any profile, deactivate accounts
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from app import db
from app.models.user import User, UserRole
from sqlalchemy.exc import IntegrityError
from datetime import datetime
import re

# ============================================================
# BLUEPRINT SETUP
# ============================================================
users_bp = Blueprint('users', __name__)


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def is_admin():
    """Check if current user has admin role"""
    jwt_data = get_jwt()
    return jwt_data.get('role') == UserRole.ADMIN.value


def validate_email(email):
    """Validate email format"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None


def validate_password(password):
    """Validate password strength"""
    if len(password) < 8:
        return False, "Password must be at least 8 characters long"
    
    if not re.search(r'[A-Z]', password):
        return False, "Password must contain at least one uppercase letter"
    
    if not re.search(r'[a-z]', password):
        return False, "Password must contain at least one lowercase letter"
    
    if not re.search(r'\d', password):
        return False, "Password must contain at least one number"
    
    return True, "Password is valid"


# ============================================================
# USER ROUTES
# ============================================================

@users_bp.route('', methods=['GET'])
@jwt_required()
def list_users():
    """
    Get list of all users (Admin only)
    
    Query Parameters:
    - role: Filter by role (ADMIN, MANAGER, MEMBER)
    - is_active: Filter by active status (true/false)
    - search: Search in email and full_name
    - page: Page number (default: 1)
    - per_page: Items per page (default: 20, max: 100)
    
    Headers:
        Authorization: Bearer <access_token>
    
    Returns:
    - 200: List of users with pagination
    - 403: Forbidden (non-admin user)
    """
    # Check admin permission
    if not is_admin():
        return jsonify({'error': 'Admin access required'}), 403
    
    try:
        # Get query parameters
        role_filter = request.args.get('role', '').upper()
        is_active_filter = request.args.get('is_active', '').lower()
        search = request.args.get('search', '').strip()
        page = request.args.get('page', 1, type=int)
        per_page = min(request.args.get('per_page', 20, type=int), 100)
        
        # Build query
        query = User.query
        
        # Apply role filter
        if role_filter:
            try:
                role_enum = UserRole[role_filter]
                query = query.filter_by(role=role_enum)
            except KeyError:
                return jsonify({
                    'error': f'Invalid role. Must be one of: {", ".join([r.name for r in UserRole])}'
                }), 400
        
        # Apply active status filter
        if is_active_filter in ['true', 'false']:
            query = query.filter_by(is_active=(is_active_filter == 'true'))
        
        # Apply search filter
        if search:
            search_pattern = f'%{search}%'
            query = query.filter(
                db.or_(
                    User.email.ilike(search_pattern),
                    User.full_name.ilike(search_pattern)
                )
            )
        
        # Execute paginated query
        pagination = query.order_by(User.created_at.desc()).paginate(
            page=page,
            per_page=per_page,
            error_out=False
        )
        
        return jsonify({
            'users': [user.to_dict() for user in pagination.items],
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': pagination.total,
                'pages': pagination.pages,
                'has_next': pagination.has_next,
                'has_prev': pagination.has_prev
            }
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Failed to list users: {str(e)}'}), 500


@users_bp.route('/<user_id>', methods=['GET'])
@jwt_required()
def get_user(user_id):
    """
    Get specific user profile
    
    Users can view their own profile.
    Admins can view any profile.
    
    Headers:
        Authorization: Bearer <access_token>
    
    Returns:
    - 200: User data
    - 403: Forbidden (non-admin trying to view other user)
    - 404: User not found
    """
    try:
        current_user_id = get_jwt_identity()
        
        # Check permission: must be own profile or admin
        if current_user_id != user_id and not is_admin():
            return jsonify({'error': 'You can only view your own profile'}), 403
        
        # Get user
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        return jsonify({
            'user': user.to_dict()
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Failed to get user: {str(e)}'}), 500


@users_bp.route('/<user_id>', methods=['PUT'])
@jwt_required()
def update_user(user_id):
    """
    Update user profile
    
    Users can update their own profile (limited fields).
    Admins can update any profile (all fields).
    
    Request Body (user updating own profile):
    {
        "full_name": "New Name",
        "email": "new@example.com",
        "current_password": "OldPass123",  (required if changing email/password)
        "new_password": "NewPass123"       (optional)
    }
    
    Request Body (admin updating any profile):
    {
        "full_name": "New Name",
        "email": "new@example.com",
        "role": "MANAGER",
        "is_active": true
    }
    
    Headers:
        Authorization: Bearer <access_token>
    
    Returns:
    - 200: User updated successfully
    - 400: Validation error
    - 403: Forbidden
    - 404: User not found
    """
    try:
        current_user_id = get_jwt_identity()
        is_self = (current_user_id == user_id)
        
        # Check permission
        if not is_self and not is_admin():
            return jsonify({'error': 'You can only update your own profile'}), 403
        
        # Get user to update
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        data = request.get_json()
        if not data:
            return jsonify({'error': 'Request body is required'}), 400
        
        # ===== Self-update logic =====
        if is_self:
            # Users can update: full_name, email, password
            
            # Update full name
            if 'full_name' in data:
                full_name = data['full_name'].strip()
                if len(full_name) < 2:
                    return jsonify({'error': 'Full name must be at least 2 characters'}), 400
                user.full_name = full_name
            
            # Update email or password requires current password verification
            if 'email' in data or 'new_password' in data:
                current_password = data.get('current_password', '')
                
                if not current_password:
                    return jsonify({
                        'error': 'current_password is required to change email or password'
                    }), 400
                
                # Verify current password
                if not user.check_password(current_password):
                    return jsonify({'error': 'Current password is incorrect'}), 401
                
                # Update email
                if 'email' in data:
                    new_email = data['email'].strip().lower()
                    
                    if not validate_email(new_email):
                        return jsonify({'error': 'Invalid email format'}), 400
                    
                    # Check if email already exists (not including current user)
                    existing = User.query.filter(
                        User.email == new_email,
                        User.id != user_id
                    ).first()
                    
                    if existing:
                        return jsonify({'error': 'Email already in use'}), 409
                    
                    user.email = new_email
                
                # Update password
                if 'new_password' in data:
                    new_password = data['new_password']
                    
                    is_valid, message = validate_password(new_password)
                    if not is_valid:
                        return jsonify({'error': message}), 400
                    
                    user.set_password(new_password)
        
        # ===== Admin update logic =====
        else:
            # Admins can update: full_name, email, role, is_active
            
            if 'full_name' in data:
                full_name = data['full_name'].strip()
                if len(full_name) < 2:
                    return jsonify({'error': 'Full name must be at least 2 characters'}), 400
                user.full_name = full_name
            
            if 'email' in data:
                new_email = data['email'].strip().lower()
                
                if not validate_email(new_email):
                    return jsonify({'error': 'Invalid email format'}), 400
                
                # Check uniqueness
                existing = User.query.filter(
                    User.email == new_email,
                    User.id != user_id
                ).first()
                
                if existing:
                    return jsonify({'error': 'Email already in use'}), 409
                
                user.email = new_email
            
            if 'role' in data:
                role_str = data['role'].upper()
                try:
                    role_enum = UserRole[role_str]
                    user.role = role_enum
                except KeyError:
                    return jsonify({
                        'error': f'Invalid role. Must be one of: {", ".join([r.name for r in UserRole])}'
                    }), 400
            
            if 'is_active' in data:
                user.is_active = bool(data['is_active'])
        
        # Save changes
        db.session.commit()
        
        return jsonify({
            'message': 'User updated successfully',
            'user': user.to_dict()
        }), 200
        
    except IntegrityError:
        db.session.rollback()
        return jsonify({'error': 'Email already in use'}), 409
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Failed to update user: {str(e)}'}), 500


@users_bp.route('/<user_id>', methods=['DELETE'])
@jwt_required()
def deactivate_user(user_id):
    """
    Deactivate user account (Admin only)
    
    Note: This soft-deletes by setting is_active=False.
    User data is retained for audit purposes.
    
    Headers:
        Authorization: Bearer <access_token>
    
    Returns:
    - 200: User deactivated successfully
    - 403: Forbidden (non-admin)
    - 404: User not found
    - 400: Cannot deactivate own account
    """
    # Check admin permission
    if not is_admin():
        return jsonify({'error': 'Admin access required'}), 403
    
    try:
        current_user_id = get_jwt_identity()
        
        # Prevent self-deactivation
        if current_user_id == user_id:
            return jsonify({'error': 'You cannot deactivate your own account'}), 400
        
        # Get user
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Deactivate
        user.is_active = False
        db.session.commit()
        
        return jsonify({
            'message': 'User deactivated successfully',
            'user': user.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Failed to deactivate user: {str(e)}'}), 500
