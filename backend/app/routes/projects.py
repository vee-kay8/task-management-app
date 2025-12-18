"""
============================================================
PROJECT MANAGEMENT ROUTES
============================================================

Project and team management endpoints:
- GET /api/projects - List user's projects
- POST /api/projects - Create new project
- GET /api/projects/:id - Get project details with members
- PUT /api/projects/:id - Update project
- DELETE /api/projects/:id - Delete project
- POST /api/projects/:id/members - Add team member
- DELETE /api/projects/:id/members/:userId - Remove team member

Access Control:
- Project Owner: Full access to project and members
- Project Manager/Member: Read access, limited updates
- Non-members: No access
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from app import db
from app.models.project import Project, ProjectMember, ProjectStatus
from app.models.user import User, UserRole as GlobalUserRole
from sqlalchemy.exc import IntegrityError
from datetime import datetime
import uuid

# ============================================================
# BLUEPRINT SETUP
# ============================================================
projects_bp = Blueprint('projects', __name__)


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def is_global_admin():
    """Check if current user is global admin"""
    jwt_data = get_jwt()
    return jwt_data.get('role') == GlobalUserRole.ADMIN.value


def get_user_project_role(project_id, user_id):
    """
    Get user's role in a project
    Returns ProjectMember object or None
    """
    return ProjectMember.query.filter_by(
        project_id=project_id,
        user_id=user_id
    ).first()


def has_project_access(project_id, user_id, required_roles=None):
    """
    Check if user has access to project
    
    Args:
        project_id: UUID of project
        user_id: UUID of user
        required_roles: List of roles that have access (e.g., ['OWNER', 'MANAGER'])
                       If None, any member has access
    
    Returns:
        (has_access: bool, member: ProjectMember or None)
    """
    # Global admins have access to everything
    if is_global_admin():
        # Create a mock member object for admins
        class AdminMember:
            role = GlobalUserRole.ADMIN
        return True, AdminMember()
    
    member = get_user_project_role(project_id, user_id)
    
    if not member:
        return False, None
    
    if required_roles is None:
        return True, member
    
    # Check if user's role is in required roles
    has_access = member.role.value in required_roles
    return has_access, member


# ============================================================
# PROJECT ROUTES
# ============================================================

@projects_bp.route('', methods=['GET'])
@jwt_required()
def list_projects():
    """
    List all projects the user is a member of
    
    Query Parameters:
    - status: Filter by status (ACTIVE, ON_HOLD, COMPLETED, ARCHIVED)
    - role: Filter by user's role in project (OWNER, MANAGER, MEMBER)
    - search: Search in project name and description
    - page: Page number (default: 1)
    - per_page: Items per page (default: 20, max: 100)
    
    Headers:
        Authorization: Bearer <access_token>
    
    Returns:
    - 200: List of projects with pagination
    """
    try:
        user_id = get_jwt_identity()
        
        # Get query parameters
        status_filter = request.args.get('status', '').upper()
        role_filter = request.args.get('role', '').upper()
        search = request.args.get('search', '').strip()
        page = request.args.get('page', 1, type=int)
        per_page = min(request.args.get('per_page', 20, type=int), 100)
        
        # Build query - start with projects user is member of
        query = db.session.query(Project).join(ProjectMember).filter(
            ProjectMember.user_id == user_id
        )
        
        # Apply status filter
        if status_filter:
            try:
                status_enum = ProjectStatus[status_filter]
                query = query.filter(Project.status == status_enum)
            except KeyError:
                return jsonify({
                    'error': f'Invalid status. Must be one of: {", ".join([s.name for s in ProjectStatus])}'
                }), 400
        
        # Apply role filter
        if role_filter:
            try:
                role_enum = GlobalUserRole[role_filter]
                query = query.filter(ProjectMember.role == role_enum)
            except KeyError:
                return jsonify({
                    'error': f'Invalid role. Must be one of: {", ".join([r.name for r in GlobalUserRole])}'
                }), 400
        
        # Apply search filter
        if search:
            search_pattern = f'%{search}%'
            query = query.filter(
                db.or_(
                    Project.name.ilike(search_pattern),
                    Project.description.ilike(search_pattern)
                )
            )
        
        # Execute paginated query
        pagination = query.order_by(Project.created_at.desc()).paginate(
            page=page,
            per_page=per_page,
            error_out=False
        )
        
        # Include member count and user's role for each project
        projects_data = []
        for project in pagination.items:
            project_dict = project.to_dict()
            
            # Add user's role in this project
            member = get_user_project_role(project.id, user_id)
            project_dict['user_role'] = member.role.value if member else None
            
            # Add member count
            project_dict['member_count'] = project.members.count()
            
            projects_data.append(project_dict)
        
        return jsonify({
            'projects': projects_data,
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
        return jsonify({'error': f'Failed to list projects: {str(e)}'}), 500


@projects_bp.route('', methods=['POST'])
@jwt_required()
def create_project():
    """
    Create a new project
    
    Creator automatically becomes project OWNER
    
    Request Body:
    {
        "name": "New Project",
        "description": "Project description",
        "start_date": "2024-01-01",      (optional)
        "end_date": "2024-12-31",        (optional)
        "status": "ACTIVE"               (optional, default: ACTIVE)
    }
    
    Headers:
        Authorization: Bearer <access_token>
    
    Returns:
    - 201: Project created successfully
    - 400: Validation error
    """
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'Request body is required'}), 400
        
        # Validate required fields
        name = data.get('name', '').strip()
        if not name:
            return jsonify({'error': 'Project name is required'}), 400
        
        if len(name) < 3:
            return jsonify({'error': 'Project name must be at least 3 characters'}), 400
        
        description = data.get('description', '').strip()
        start_date_str = data.get('start_date')
        end_date_str = data.get('end_date')
        status_str = data.get('status', 'ACTIVE').upper()
        color = data.get('color', '#3B82F6')  # Default blue color
        
        # Parse dates
        start_date = None
        end_date = None
        
        if start_date_str:
            try:
                start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
            except ValueError:
                return jsonify({'error': 'Invalid start_date format. Use YYYY-MM-DD'}), 400
        
        if end_date_str:
            try:
                end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
            except ValueError:
                return jsonify({'error': 'Invalid end_date format. Use YYYY-MM-DD'}), 400
        
        # Validate date range
        if start_date and end_date and start_date > end_date:
            return jsonify({'error': 'start_date cannot be after end_date'}), 400
        
        # Validate status
        try:
            status = ProjectStatus[status_str]
        except KeyError:
            return jsonify({
                'error': f'Invalid status. Must be one of: {", ".join([s.name for s in ProjectStatus])}'
            }), 400
        
        # Create project
        new_project = Project(
            name=name,
            description=description if description else None,
            status=status,
            color=color,
            start_date=start_date,
            end_date=end_date,
            owner_id=user_id
        )
        
        db.session.add(new_project)
        db.session.flush()  # Get the project ID
        
        # Add creator as OWNER
        creator_member = ProjectMember(
            project_id=new_project.id,
            user_id=user_id,
            role=GlobalUserRole.ADMIN  # Project owner gets ADMIN role
        )
        
        db.session.add(creator_member)
        db.session.commit()
        
        # Return project with user's role
        project_dict = new_project.to_dict()
        project_dict['user_role'] = GlobalUserRole.ADMIN.value
        project_dict['member_count'] = 1
        
        return jsonify({
            'message': 'Project created successfully',
            'project': project_dict
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Failed to create project: {str(e)}'}), 500


@projects_bp.route('/<project_id>', methods=['GET'])
@jwt_required()
def get_project(project_id):
    """
    Get project details with members and tasks
    
    Headers:
        Authorization: Bearer <access_token>
    
    Returns:
    - 200: Project data with members list
    - 403: User not a member
    - 404: Project not found
    """
    try:
        user_id = get_jwt_identity()
        
        # Check access
        has_access, member = has_project_access(project_id, user_id)
        if not has_access:
            return jsonify({'error': 'You do not have access to this project'}), 403
        
        # Get project
        project = Project.query.get(project_id)
        
        if not project:
            return jsonify({'error': 'Project not found'}), 404
        
        # Build response with additional details
        project_dict = project.to_dict()
        
        # Add user's role
        if member:
            project_dict['user_role'] = member.role.value if hasattr(member.role, 'value') else member.role
        
        # Add members list with user details
        members_data = []
        for pm in project.members.all():
            member_data = {
                'user_id': str(pm.user.id),
                'email': pm.user.email,
                'full_name': pm.user.full_name,
                'role': pm.role.value,
                'joined_at': pm.joined_at.isoformat()
            }
            members_data.append(member_data)
        
        project_dict['members'] = members_data
        project_dict['member_count'] = len(members_data)
        
        # Add task summary
        all_tasks = project.tasks.all()
        task_counts = {
            'total': len(all_tasks),
            'todo': len([t for t in all_tasks if t.status.value == 'TODO']),
            'in_progress': len([t for t in all_tasks if t.status.value == 'IN_PROGRESS']),
            'done': len([t for t in all_tasks if t.status.value == 'DONE'])
        }
        project_dict['task_summary'] = task_counts
        
        return jsonify({
            'project': project_dict
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Failed to get project: {str(e)}'}), 500


@projects_bp.route('/<project_id>', methods=['PUT'])
@jwt_required()
def update_project(project_id):
    """
    Update project details
    
    Only OWNER and MANAGER can update projects
    
    Request Body:
    {
        "name": "Updated Name",
        "description": "Updated description",
        "status": "COMPLETED",
        "start_date": "2024-01-01",
        "end_date": "2024-12-31"
    }
    
    Headers:
        Authorization: Bearer <access_token>
    
    Returns:
    - 200: Project updated successfully
    - 403: Insufficient permissions
    - 404: Project not found
    """
    try:
        user_id = get_jwt_identity()
        
        # Check access - require OWNER or MANAGER role
        has_access, member = has_project_access(
            project_id, 
            user_id, 
            required_roles=['ADMIN', 'MANAGER']
        )
        
        if not has_access:
            return jsonify({'error': 'You do not have permission to update this project'}), 403
        
        # Get project
        project = Project.query.get(project_id)
        
        if not project:
            return jsonify({'error': 'Project not found'}), 404
        
        data = request.get_json()
        if not data:
            return jsonify({'error': 'Request body is required'}), 400
        
        # Update name
        if 'name' in data:
            name = data['name'].strip()
            if len(name) < 3:
                return jsonify({'error': 'Project name must be at least 3 characters'}), 400
            project.name = name
        
        # Update description
        if 'description' in data:
            project.description = data['description'].strip() or None
        
        # Update status
        if 'status' in data:
            status_str = data['status'].upper()
            try:
                project.status = ProjectStatus[status_str]
            except KeyError:
                return jsonify({
                    'error': f'Invalid status. Must be one of: {", ".join([s.name for s in ProjectStatus])}'
                }), 400
        
        # Update dates
        if 'start_date' in data:
            if data['start_date']:
                try:
                    project.start_date = datetime.strptime(data['start_date'], '%Y-%m-%d').date()
                except ValueError:
                    return jsonify({'error': 'Invalid start_date format. Use YYYY-MM-DD'}), 400
            else:
                project.start_date = None
        
        if 'end_date' in data:
            if data['end_date']:
                try:
                    project.end_date = datetime.strptime(data['end_date'], '%Y-%m-%d').date()
                except ValueError:
                    return jsonify({'error': 'Invalid end_date format. Use YYYY-MM-DD'}), 400
            else:
                project.end_date = None
        
        # Validate date range
        if project.start_date and project.end_date and project.start_date > project.end_date:
            return jsonify({'error': 'start_date cannot be after end_date'}), 400
        
        db.session.commit()
        
        return jsonify({
            'message': 'Project updated successfully',
            'project': project.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Failed to update project: {str(e)}'}), 500


@projects_bp.route('/<project_id>', methods=['DELETE'])
@jwt_required()
def delete_project(project_id):
    """
    Delete project (OWNER only)
    
    This is a hard delete - will cascade to tasks, comments, etc.
    Use with caution. Consider archiving (status=ARCHIVED) instead.
    
    Headers:
        Authorization: Bearer <access_token>
    
    Returns:
    - 200: Project deleted successfully
    - 403: Insufficient permissions (only OWNER can delete)
    - 404: Project not found
    """
    try:
        user_id = get_jwt_identity()
        
        # Check access - require OWNER role only
        has_access, member = has_project_access(
            project_id, 
            user_id, 
            required_roles=['ADMIN']
        )
        
        if not has_access:
            return jsonify({'error': 'Only project owner can delete the project'}), 403
        
        # Get project
        project = Project.query.get(project_id)
        
        if not project:
            return jsonify({'error': 'Project not found'}), 404
        
        # Delete project (will cascade to members, tasks, etc.)
        db.session.delete(project)
        db.session.commit()
        
        return jsonify({
            'message': 'Project deleted successfully'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Failed to delete project: {str(e)}'}), 500


# ============================================================
# PROJECT MEMBER MANAGEMENT
# ============================================================

@projects_bp.route('/<project_id>/members', methods=['POST'])
@jwt_required()
def add_member(project_id):
    """
    Add a team member to project
    
    Only OWNER and MANAGER can add members
    
    Request Body:
    {
        "user_id": "uuid-of-user",
        "role": "MEMBER"  (ADMIN, MANAGER, or MEMBER)
    }
    
    Headers:
        Authorization: Bearer <access_token>
    
    Returns:
    - 201: Member added successfully
    - 400: Validation error or user already a member
    - 403: Insufficient permissions
    - 404: Project or user not found
    """
    try:
        current_user_id = get_jwt_identity()
        
        # Check access - require OWNER or MANAGER
        has_access, member = has_project_access(
            project_id,
            current_user_id,
            required_roles=['ADMIN', 'MANAGER']
        )
        
        if not has_access:
            return jsonify({'error': 'You do not have permission to add members'}), 403
        
        # Verify project exists
        project = Project.query.get(project_id)
        if not project:
            return jsonify({'error': 'Project not found'}), 404
        
        data = request.get_json()
        if not data:
            return jsonify({'error': 'Request body is required'}), 400
        
        # Validate user_id
        new_user_id = data.get('user_id', '').strip()
        if not new_user_id:
            return jsonify({'error': 'user_id is required'}), 400
        
        # Verify user exists
        new_user = User.query.get(new_user_id)
        if not new_user:
            return jsonify({'error': 'User not found'}), 404
        
        if not new_user.is_active:
            return jsonify({'error': 'Cannot add inactive user'}), 400
        
        # Check if already a member
        existing_member = get_user_project_role(project_id, new_user_id)
        if existing_member:
            return jsonify({'error': 'User is already a member of this project'}), 400
        
        # Validate role
        role_str = data.get('role', 'MEMBER').upper()
        try:
            role = GlobalUserRole[role_str]
        except KeyError:
            return jsonify({
                'error': f'Invalid role. Must be one of: {", ".join([r.name for r in GlobalUserRole])}'
            }), 400
        
        # Add member
        new_member = ProjectMember(
            project_id=project_id,
            user_id=new_user_id,
            role=role
        )
        
        db.session.add(new_member)
        db.session.commit()
        
        return jsonify({
            'message': 'Member added successfully',
            'member': {
                'user_id': str(new_user.id),
                'email': new_user.email,
                'full_name': new_user.full_name,
                'role': role.value,
                'joined_at': new_member.joined_at.isoformat()
            }
        }), 201
        
    except IntegrityError:
        db.session.rollback()
        return jsonify({'error': 'User is already a member'}), 400
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Failed to add member: {str(e)}'}), 500


@projects_bp.route('/<project_id>/members/<member_user_id>', methods=['DELETE'])
@jwt_required()
def remove_member(project_id, member_user_id):
    """
    Remove a team member from project
    
    Only OWNER can remove members
    Cannot remove project OWNER
    
    Headers:
        Authorization: Bearer <access_token>
    
    Returns:
    - 200: Member removed successfully
    - 400: Cannot remove project owner
    - 403: Insufficient permissions
    - 404: Project or member not found
    """
    try:
        current_user_id = get_jwt_identity()
        
        # Check access - require OWNER role
        has_access, member = has_project_access(
            project_id,
            current_user_id,
            required_roles=['ADMIN']
        )
        
        if not has_access:
            return jsonify({'error': 'Only project owner can remove members'}), 403
        
        # Verify project exists
        project = Project.query.get(project_id)
        if not project:
            return jsonify({'error': 'Project not found'}), 404
        
        # Get member to remove
        member_to_remove = get_user_project_role(project_id, member_user_id)
        
        if not member_to_remove:
            return jsonify({'error': 'User is not a member of this project'}), 404
        
        # Prevent removing the project creator/owner
        if member_to_remove.role == GlobalUserRole.ADMIN and str(project.owner_id) == member_user_id:
            return jsonify({'error': 'Cannot remove project owner'}), 400
        
        # Remove member
        db.session.delete(member_to_remove)
        db.session.commit()
        
        return jsonify({
            'message': 'Member removed successfully'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Failed to remove member: {str(e)}'}), 500
