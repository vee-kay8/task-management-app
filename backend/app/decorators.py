"""
============================================================
AUTHENTICATION DECORATORS
============================================================

Custom decorators for role-based access control and permissions.

Usage Examples:
    @app.route('/admin')
    @jwt_required()
    @admin_required()
    def admin_only_view():
        return {'message': 'Admin access granted'}
    
    @app.route('/manager')
    @jwt_required()
    @roles_required(['ADMIN', 'MANAGER'])
    def manager_view():
        return {'message': 'Manager access granted'}
"""

from functools import wraps
from flask import jsonify
from flask_jwt_extended import get_jwt, verify_jwt_in_request, get_jwt_identity
from app.models.user import User, UserRole
from app.models.project import ProjectMember


def admin_required():
    """
    Decorator to require admin role
    
    Must be used after @jwt_required()
    
    Usage:
        @app.route('/admin-only')
        @jwt_required()
        @admin_required()
        def admin_view():
            return {'data': 'sensitive'}
    """
    def wrapper(fn):
        @wraps(fn)
        def decorator(*args, **kwargs):
            # Verify JWT token is present
            verify_jwt_in_request()
            
            # Get JWT claims
            claims = get_jwt()
            user_role = claims.get('role')
            
            # Check if user is admin
            if user_role != UserRole.ADMIN.value:
                return jsonify({
                    'error': 'Admin access required',
                    'code': 'FORBIDDEN'
                }), 403
            
            return fn(*args, **kwargs)
        return decorator
    return wrapper


def roles_required(required_roles):
    """
    Decorator to require one of specified roles
    
    Must be used after @jwt_required()
    
    Args:
        required_roles (list): List of role names (e.g., ['ADMIN', 'MANAGER'])
    
    Usage:
        @app.route('/managers')
        @jwt_required()
        @roles_required(['ADMIN', 'MANAGER'])
        def manager_view():
            return {'data': 'manager content'}
    """
    def wrapper(fn):
        @wraps(fn)
        def decorator(*args, **kwargs):
            # Verify JWT token is present
            verify_jwt_in_request()
            
            # Get JWT claims
            claims = get_jwt()
            user_role = claims.get('role')
            
            # Check if user has required role
            if user_role not in required_roles:
                return jsonify({
                    'error': f'Access denied. Required roles: {", ".join(required_roles)}',
                    'code': 'FORBIDDEN'
                }), 403
            
            return fn(*args, **kwargs)
        return decorator
    return wrapper


def account_active_required():
    """
    Decorator to ensure user account is active
    
    Must be used after @jwt_required()
    Verifies that user account hasn't been deactivated
    
    Usage:
        @app.route('/profile')
        @jwt_required()
        @account_active_required()
        def profile():
            return {'data': 'user profile'}
    """
    def wrapper(fn):
        @wraps(fn)
        def decorator(*args, **kwargs):
            # Verify JWT token is present
            verify_jwt_in_request()
            
            # Get user ID from token
            user_id = get_jwt_identity()
            
            # Check if user exists and is active
            user = User.query.get(user_id)
            
            if not user:
                return jsonify({
                    'error': 'User not found',
                    'code': 'USER_NOT_FOUND'
                }), 404
            
            if not user.is_active:
                return jsonify({
                    'error': 'Account has been deactivated',
                    'code': 'ACCOUNT_INACTIVE'
                }), 403
            
            return fn(*args, **kwargs)
        return decorator
    return wrapper


def project_member_required(project_id_param='project_id'):
    """
    Decorator to require project membership
    
    Must be used after @jwt_required()
    
    Args:
        project_id_param (str): Name of URL parameter containing project ID
                               Default: 'project_id'
    
    Usage:
        @app.route('/projects/<project_id>/tasks')
        @jwt_required()
        @project_member_required()
        def project_tasks(project_id):
            return {'tasks': [...]}
    """
    def wrapper(fn):
        @wraps(fn)
        def decorator(*args, **kwargs):
            # Verify JWT token is present
            verify_jwt_in_request()
            
            # Get user ID from token
            user_id = get_jwt_identity()
            
            # Get project ID from URL parameters
            project_id = kwargs.get(project_id_param)
            
            if not project_id:
                return jsonify({
                    'error': f'Missing {project_id_param} parameter',
                    'code': 'BAD_REQUEST'
                }), 400
            
            # Check if user is admin (admins bypass project membership)
            claims = get_jwt()
            if claims.get('role') == UserRole.ADMIN.value:
                return fn(*args, **kwargs)
            
            # Check project membership
            member = ProjectMember.query.filter_by(
                project_id=project_id,
                user_id=user_id
            ).first()
            
            if not member:
                return jsonify({
                    'error': 'You are not a member of this project',
                    'code': 'FORBIDDEN'
                }), 403
            
            # Add member info to kwargs for use in route
            kwargs['_project_member'] = member
            
            return fn(*args, **kwargs)
        return decorator
    return wrapper


def project_role_required(required_roles, project_id_param='project_id'):
    """
    Decorator to require specific role in project
    
    Must be used after @jwt_required()
    
    Args:
        required_roles (list): List of role names (e.g., ['ADMIN', 'MANAGER'])
        project_id_param (str): Name of URL parameter containing project ID
    
    Usage:
        @app.route('/projects/<project_id>/settings')
        @jwt_required()
        @project_role_required(['ADMIN', 'MANAGER'])
        def project_settings(project_id):
            return {'settings': {...}}
    """
    def wrapper(fn):
        @wraps(fn)
        def decorator(*args, **kwargs):
            # Verify JWT token is present
            verify_jwt_in_request()
            
            # Get user ID from token
            user_id = get_jwt_identity()
            
            # Get project ID from URL parameters
            project_id = kwargs.get(project_id_param)
            
            if not project_id:
                return jsonify({
                    'error': f'Missing {project_id_param} parameter',
                    'code': 'BAD_REQUEST'
                }), 400
            
            # Check if user is global admin (admins bypass project roles)
            claims = get_jwt()
            if claims.get('role') == UserRole.ADMIN.value:
                return fn(*args, **kwargs)
            
            # Check project membership and role
            member = ProjectMember.query.filter_by(
                project_id=project_id,
                user_id=user_id
            ).first()
            
            if not member:
                return jsonify({
                    'error': 'You are not a member of this project',
                    'code': 'FORBIDDEN'
                }), 403
            
            if member.role.value not in required_roles:
                return jsonify({
                    'error': f'Insufficient project permissions. Required: {", ".join(required_roles)}',
                    'code': 'FORBIDDEN'
                }), 403
            
            # Add member info to kwargs for use in route
            kwargs['_project_member'] = member
            
            return fn(*args, **kwargs)
        return decorator
    return wrapper


def owner_or_admin_required(resource_owner_id_param='user_id'):
    """
    Decorator to require resource ownership or admin role
    
    Useful for routes where users can only access their own resources
    unless they are an admin
    
    Must be used after @jwt_required()
    
    Args:
        resource_owner_id_param (str): Name of URL parameter containing owner ID
    
    Usage:
        @app.route('/users/<user_id>/profile')
        @jwt_required()
        @owner_or_admin_required()
        def user_profile(user_id):
            return {'profile': {...}}
    """
    def wrapper(fn):
        @wraps(fn)
        def decorator(*args, **kwargs):
            # Verify JWT token is present
            verify_jwt_in_request()
            
            # Get current user ID from token
            current_user_id = get_jwt_identity()
            
            # Get resource owner ID from URL parameters
            resource_owner_id = kwargs.get(resource_owner_id_param)
            
            if not resource_owner_id:
                return jsonify({
                    'error': f'Missing {resource_owner_id_param} parameter',
                    'code': 'BAD_REQUEST'
                }), 400
            
            # Check if user is admin
            claims = get_jwt()
            is_admin = claims.get('role') == UserRole.ADMIN.value
            
            # Check if user is the resource owner
            is_owner = str(current_user_id) == str(resource_owner_id)
            
            # Allow if admin or owner
            if not (is_admin or is_owner):
                return jsonify({
                    'error': 'You can only access your own resources',
                    'code': 'FORBIDDEN'
                }), 403
            
            return fn(*args, **kwargs)
        return decorator
    return wrapper
