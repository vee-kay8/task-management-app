"""
============================================================
TASK MANAGEMENT ROUTES
============================================================

Task, comment, and attachment management:
- GET /api/tasks - List tasks with filters
- POST /api/tasks - Create new task
- GET /api/tasks/:id - Get task details with comments
- PUT /api/tasks/:id - Update task
- DELETE /api/tasks/:id - Delete task
- POST /api/tasks/:id/comments - Add comment to task
- POST /api/tasks/:id/attachments - Upload file attachment

Access Control:
- Project members can view and create tasks
- Task creator and project managers can update/delete
- Anyone can add comments if they have project access
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from app import db
from app.models.task import Task, TaskStatus, TaskPriority, Comment, Attachment
from app.models.project import Project, ProjectMember
from app.models.user import User, UserRole as GlobalUserRole
from sqlalchemy.exc import IntegrityError
from datetime import datetime
import uuid

# ============================================================
# BLUEPRINT SETUP
# ============================================================
tasks_bp = Blueprint('tasks', __name__)


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def is_global_admin():
    """Check if current user is global admin"""
    jwt_data = get_jwt()
    return jwt_data.get('role') == GlobalUserRole.ADMIN.value


def get_user_project_role(project_id, user_id):
    """Get user's role in a project"""
    return ProjectMember.query.filter_by(
        project_id=project_id,
        user_id=user_id
    ).first()


def has_project_access(project_id, user_id):
    """Check if user has access to project"""
    if is_global_admin():
        return True
    
    member = get_user_project_role(project_id, user_id)
    return member is not None


def can_modify_task(task, user_id):
    """
    Check if user can modify a task
    
    Can modify if:
    - Global admin
    - Task creator
    - Project owner/manager
    """
    if is_global_admin():
        return True
    
    # Task creator
    if str(task.reporter_id) == user_id:
        return True
    
    # Project owner/manager
    member = get_user_project_role(task.project_id, user_id)
    if member and member.role.value in ['ADMIN', 'MANAGER']:
        return True
    
    return False


# ============================================================
# TASK ROUTES
# ============================================================

@tasks_bp.route('', methods=['GET'])
@jwt_required()
def list_tasks():
    """
    List tasks with filters
    
    Query Parameters:
    - project_id: Filter by project (required if not admin)
    - status: Filter by status (TODO, IN_PROGRESS, DONE, CANCELLED)
    - priority: Filter by priority (LOW, MEDIUM, HIGH, URGENT)
    - assigned_to: Filter by assignee user_id
    - created_by: Filter by creator user_id
    - search: Search in title and description
    - due_before: Tasks due before date (YYYY-MM-DD)
    - due_after: Tasks due after date (YYYY-MM-DD)
    - page: Page number (default: 1)
    - per_page: Items per page (default: 20, max: 100)
    
    Headers:
        Authorization: Bearer <access_token>
    
    Returns:
    - 200: List of tasks with pagination
    - 400: Missing required parameters
    - 403: No access to project
    """
    try:
        user_id = get_jwt_identity()
        
        # Get query parameters
        project_id = request.args.get('project_id')
        status_filter = request.args.get('status', '').upper()
        priority_filter = request.args.get('priority', '').upper()
        assigned_to = request.args.get('assigned_to')
        created_by = request.args.get('created_by')
        search = request.args.get('search', '').strip()
        due_before = request.args.get('due_before')
        due_after = request.args.get('due_after')
        page = request.args.get('page', 1, type=int)
        per_page = min(request.args.get('per_page', 20, type=int), 100)
        
        # Validate project_id (required for non-admins)
        if not project_id and not is_global_admin():
            return jsonify({'error': 'project_id is required'}), 400
        
        # Check project access
        if project_id:
            if not has_project_access(project_id, user_id):
                return jsonify({'error': 'You do not have access to this project'}), 403
        
        # Build query
        query = Task.query
        
        # Filter by project
        if project_id:
            query = query.filter(Task.project_id == project_id)
        else:
            # Admin viewing all tasks - filter to projects user has access to
            accessible_projects = db.session.query(ProjectMember.project_id).filter(
                ProjectMember.user_id == user_id
            ).subquery()
            query = query.filter(Task.project_id.in_(accessible_projects))
        
        # Apply status filter
        if status_filter:
            try:
                status_enum = TaskStatus[status_filter]
                query = query.filter(Task.status == status_enum)
            except KeyError:
                return jsonify({
                    'error': f'Invalid status. Must be one of: {", ".join([s.name for s in TaskStatus])}'
                }), 400
        
        # Apply priority filter
        if priority_filter:
            try:
                priority_enum = TaskPriority[priority_filter]
                query = query.filter(Task.priority == priority_enum)
            except KeyError:
                return jsonify({
                    'error': f'Invalid priority. Must be one of: {", ".join([p.name for p in TaskPriority])}'
                }), 400
        
        # Apply assignee filter
        if assigned_to:
            query = query.filter(Task.assignee_id == assigned_to)
        
        # Apply creator filter
        if created_by:
            query = query.filter(Task.reporter_id == created_by)
        
        # Apply search filter
        if search:
            search_pattern = f'%{search}%'
            query = query.filter(
                db.or_(
                    Task.title.ilike(search_pattern),
                    Task.description.ilike(search_pattern)
                )
            )
        
        # Apply due date filters
        if due_before:
            try:
                due_before_date = datetime.strptime(due_before, '%Y-%m-%d').date()
                query = query.filter(Task.due_date <= due_before_date)
            except ValueError:
                return jsonify({'error': 'Invalid due_before format. Use YYYY-MM-DD'}), 400
        
        if due_after:
            try:
                due_after_date = datetime.strptime(due_after, '%Y-%m-%d').date()
                query = query.filter(Task.due_date >= due_after_date)
            except ValueError:
                return jsonify({'error': 'Invalid due_after format. Use YYYY-MM-DD'}), 400
        
        # Execute paginated query
        pagination = query.order_by(Task.created_at.desc()).paginate(
            page=page,
            per_page=per_page,
            error_out=False
        )
        
        # Build response with additional details
        tasks_data = []
        for task in pagination.items:
            task_dict = task.to_dict()
            
            # Add comment count
            task_dict['comment_count'] = task.comments.count()
            
            # Add attachment count
            task_dict['attachment_count'] = task.attachments.count()
            
            tasks_data.append(task_dict)
        
        return jsonify({
            'tasks': tasks_data,
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
        return jsonify({'error': f'Failed to list tasks: {str(e)}'}), 500


@tasks_bp.route('', methods=['POST'])
@jwt_required()
def create_task():
    """
    Create a new task
    
    Request Body:
    {
        "project_id": "uuid",
        "title": "Task title",
        "description": "Task description",
        "status": "TODO",              (optional, default: TODO)
        "priority": "MEDIUM",           (optional, default: MEDIUM)
        "assigned_to_id": "user-uuid",  (optional)
        "due_date": "2024-12-31",       (optional, YYYY-MM-DD)
        "tags": ["frontend", "urgent"]  (optional)
    }
    
    Headers:
        Authorization: Bearer <access_token>
    
    Returns:
    - 201: Task created successfully
    - 400: Validation error
    - 403: No access to project
    - 404: Project or user not found
    """
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'Request body is required'}), 400
        
        # Validate required fields
        project_id = data.get('project_id', '').strip()
        if not project_id:
            return jsonify({'error': 'project_id is required'}), 400
        
        # Verify project exists and user has access
        project = Project.query.get(project_id)
        if not project:
            return jsonify({'error': 'Project not found'}), 404
        
        if not has_project_access(project_id, user_id):
            return jsonify({'error': 'You do not have access to this project'}), 403
        
        # Validate title
        title = data.get('title', '').strip()
        if not title:
            return jsonify({'error': 'Task title is required'}), 400
        
        if len(title) < 3:
            return jsonify({'error': 'Task title must be at least 3 characters'}), 400
        
        description = data.get('description', '').strip() or None
        
        # Validate status
        status_str = data.get('status', 'TODO').upper()
        try:
            status = TaskStatus[status_str]
        except KeyError:
            return jsonify({
                'error': f'Invalid status. Must be one of: {", ".join([s.name for s in TaskStatus])}'
            }), 400
        
        # Validate priority
        priority_str = data.get('priority', 'MEDIUM').upper()
        try:
            priority = TaskPriority[priority_str]
        except KeyError:
            return jsonify({
                'error': f'Invalid priority. Must be one of: {", ".join([p.name for p in TaskPriority])}'
            }), 400
        
        # Validate assignee (if provided)
        assigned_to_id = data.get('assigned_to_id')
        if assigned_to_id:
            assignee = User.query.get(assigned_to_id)
            if not assignee:
                return jsonify({'error': 'Assigned user not found'}), 404
            
            # Check if assignee is project member
            if not has_project_access(project_id, assigned_to_id):
                return jsonify({'error': 'Assigned user is not a project member'}), 400
        
        # Parse due date
        due_date = None
        if data.get('due_date'):
            try:
                due_date = datetime.strptime(data['due_date'], '%Y-%m-%d').date()
            except ValueError:
                return jsonify({'error': 'Invalid due_date format. Use YYYY-MM-DD'}), 400
        
        # Validate tags
        tags = data.get('tags', [])
        if not isinstance(tags, list):
            return jsonify({'error': 'tags must be an array'}), 400
        
        # Create task
        new_task = Task(
            project_id=project_id,
            title=title,
            description=description,
            status=status,
            priority=priority,
            assignee_id=assigned_to_id,
            due_date=due_date,
            tags=tags,
            reporter_id=user_id
        )
        
        db.session.add(new_task)
        db.session.commit()
        
        return jsonify({
            'message': 'Task created successfully',
            'task': new_task.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Failed to create task: {str(e)}'}), 500


@tasks_bp.route('/<task_id>', methods=['GET'])
@jwt_required()
def get_task(task_id):
    """
    Get task details with comments and attachments
    
    Headers:
        Authorization: Bearer <access_token>
    
    Returns:
    - 200: Task data with comments and attachments
    - 403: No access to project
    - 404: Task not found
    """
    try:
        user_id = get_jwt_identity()
        
        # Get task
        task = Task.query.get(task_id)
        
        if not task:
            return jsonify({'error': 'Task not found'}), 404
        
        # Check project access
        if not has_project_access(task.project_id, user_id):
            return jsonify({'error': 'You do not have access to this task'}), 403
        
        # Build response with comments and attachments
        task_dict = task.to_dict()
        
        # Add comments with user details
        comments_data = []
        for comment in task.comments:
            comment_data = {
                'id': str(comment.id),
                'content': comment.content,
                'created_at': comment.created_at.isoformat(),
                'updated_at': comment.updated_at.isoformat() if comment.updated_at else None,
                'user': {
                    'id': str(comment.user.id),
                    'full_name': comment.user.full_name,
                    'email': comment.user.email
                },
                'parent_id': str(comment.parent_comment_id) if comment.parent_comment_id else None
            }
            comments_data.append(comment_data)
        
        task_dict['comments'] = comments_data
        
        # Add attachments
        attachments_data = []
        for attachment in task.attachments:
            attachment_data = {
                'id': str(attachment.id),
                'file_name': attachment.file_name,
                'file_path': attachment.file_path,
                'file_size': attachment.file_size,
                'uploaded_at': attachment.uploaded_at.isoformat(),
                'uploaded_by': {
                    'id': str(attachment.uploaded_by.id),
                    'full_name': attachment.uploaded_by.full_name
                }
            }
            attachments_data.append(attachment_data)
        
        task_dict['attachments'] = attachments_data
        
        return jsonify({
            'task': task_dict
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Failed to get task: {str(e)}'}), 500


@tasks_bp.route('/<task_id>', methods=['PUT'])
@jwt_required()
def update_task(task_id):
    """
    Update task details
    
    Task creator, project owner, and managers can update
    
    Request Body:
    {
        "title": "Updated title",
        "description": "Updated description",
        "status": "IN_PROGRESS",
        "priority": "HIGH",
        "assigned_to_id": "user-uuid",
        "due_date": "2024-12-31",
        "tags": ["updated", "tags"]
    }
    
    Headers:
        Authorization: Bearer <access_token>
    
    Returns:
    - 200: Task updated successfully
    - 403: Insufficient permissions
    - 404: Task not found
    """
    try:
        user_id = get_jwt_identity()
        
        # Get task
        task = Task.query.get(task_id)
        
        if not task:
            return jsonify({'error': 'Task not found'}), 404
        
        # Check permission
        if not can_modify_task(task, user_id):
            return jsonify({'error': 'You do not have permission to update this task'}), 403
        
        data = request.get_json()
        if not data:
            return jsonify({'error': 'Request body is required'}), 400
        
        # Update title
        if 'title' in data:
            title = data['title'].strip()
            if len(title) < 3:
                return jsonify({'error': 'Task title must be at least 3 characters'}), 400
            task.title = title
        
        # Update description
        if 'description' in data:
            task.description = data['description'].strip() or None
        
        # Update status
        if 'status' in data:
            status_str = data['status'].upper()
            try:
                task.status = TaskStatus[status_str]
            except KeyError:
                return jsonify({
                    'error': f'Invalid status. Must be one of: {", ".join([s.name for s in TaskStatus])}'
                }), 400
        
        # Update priority
        if 'priority' in data:
            priority_str = data['priority'].upper()
            try:
                task.priority = TaskPriority[priority_str]
            except KeyError:
                return jsonify({
                    'error': f'Invalid priority. Must be one of: {", ".join([p.name for p in TaskPriority])}'
                }), 400
        
        # Update assignee
        if 'assigned_to_id' in data:
            assigned_to_id = data['assigned_to_id']
            
            if assigned_to_id:
                # Verify user exists and is project member
                assignee = User.query.get(assigned_to_id)
                if not assignee:
                    return jsonify({'error': 'Assigned user not found'}), 404
                
                if not has_project_access(task.project_id, assigned_to_id):
                    return jsonify({'error': 'Assigned user is not a project member'}), 400
                
                task.assignee_id = assigned_to_id
            else:
                task.assignee_id = None
        
        # Update due date
        if 'due_date' in data:
            if data['due_date']:
                try:
                    task.due_date = datetime.strptime(data['due_date'], '%Y-%m-%d').date()
                except ValueError:
                    return jsonify({'error': 'Invalid due_date format. Use YYYY-MM-DD'}), 400
            else:
                task.due_date = None
        
        # Update tags
        if 'tags' in data:
            tags = data['tags']
            if not isinstance(tags, list):
                return jsonify({'error': 'tags must be an array'}), 400
            task.tags = tags
        
        db.session.commit()
        
        return jsonify({
            'message': 'Task updated successfully',
            'task': task.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Failed to update task: {str(e)}'}), 500


@tasks_bp.route('/<task_id>', methods=['DELETE'])
@jwt_required()
def delete_task(task_id):
    """
    Delete task
    
    Only task creator, project owner, and managers can delete
    
    Headers:
        Authorization: Bearer <access_token>
    
    Returns:
    - 200: Task deleted successfully
    - 403: Insufficient permissions
    - 404: Task not found
    """
    try:
        user_id = get_jwt_identity()
        
        # Get task
        task = Task.query.get(task_id)
        
        if not task:
            return jsonify({'error': 'Task not found'}), 404
        
        # Check permission
        if not can_modify_task(task, user_id):
            return jsonify({'error': 'You do not have permission to delete this task'}), 403
        
        # Delete task (will cascade to comments and attachments)
        db.session.delete(task)
        db.session.commit()
        
        return jsonify({
            'message': 'Task deleted successfully'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Failed to delete task: {str(e)}'}), 500


# ============================================================
# COMMENT ROUTES
# ============================================================

@tasks_bp.route('/<task_id>/comments', methods=['POST'])
@jwt_required()
def add_comment(task_id):
    """
    Add a comment to a task
    
    Request Body:
    {
        "content": "Comment text",
        "parent_id": "uuid"  (optional, for threaded replies)
    }
    
    Headers:
        Authorization: Bearer <access_token>
    
    Returns:
    - 201: Comment added successfully
    - 400: Validation error
    - 403: No access to project
    - 404: Task not found
    """
    try:
        user_id = get_jwt_identity()
        
        # Get task
        task = Task.query.get(task_id)
        
        if not task:
            return jsonify({'error': 'Task not found'}), 404
        
        # Check project access
        if not has_project_access(task.project_id, user_id):
            return jsonify({'error': 'You do not have access to this task'}), 403
        
        data = request.get_json()
        if not data:
            return jsonify({'error': 'Request body is required'}), 400
        
        # Validate content
        content = data.get('content', '').strip()
        if not content:
            return jsonify({'error': 'Comment content is required'}), 400
        
        # Validate parent comment (if provided)
        parent_id = data.get('parent_id')
        if parent_id:
            parent_comment = Comment.query.get(parent_id)
            if not parent_comment:
                return jsonify({'error': 'Parent comment not found'}), 404
            
            if str(parent_comment.task_id) != task_id:
                return jsonify({'error': 'Parent comment belongs to different task'}), 400
        
        # Create comment
        new_comment = Comment(
            task_id=task_id,
            user_id=user_id,
            content=content,
            parent_comment_id=parent_id
        )
        
        db.session.add(new_comment)
        db.session.commit()
        
        # Return comment with user details
        comment_dict = {
            'id': str(new_comment.id),
            'content': new_comment.content,
            'created_at': new_comment.created_at.isoformat(),
            'updated_at': None,
            'user': {
                'id': str(new_comment.user.id),
                'full_name': new_comment.user.full_name,
                'email': new_comment.user.email
            },
            'parent_id': str(new_comment.parent_comment_id) if new_comment.parent_comment_id else None
        }
        
        return jsonify({
            'message': 'Comment added successfully',
            'comment': comment_dict
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Failed to add comment: {str(e)}'}), 500


# ============================================================
# ATTACHMENT ROUTES (Placeholder)
# ============================================================

@tasks_bp.route('/<task_id>/attachments', methods=['POST'])
@jwt_required()
def upload_attachment(task_id):
    """
    Upload file attachment to task
    
    Note: This is a placeholder. Full implementation requires:
    - File upload handling (multipart/form-data)
    - File storage (local filesystem or cloud storage like S3)
    - File size/type validation
    - Security measures (virus scanning, etc.)
    
    Request:
        Content-Type: multipart/form-data
        file: <binary file data>
    
    Headers:
        Authorization: Bearer <access_token>
    
    Returns:
    - 501: Not implemented yet
    """
    return jsonify({
        'error': 'File upload not implemented yet',
        'message': 'This endpoint requires file storage setup (local or cloud)'
    }), 501
