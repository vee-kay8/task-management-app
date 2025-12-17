"""
============================================================
ERROR HANDLERS
============================================================

Centralized error handling for consistent API responses.

This module provides custom exception classes and handlers
for common error scenarios in the API.
"""

from flask import jsonify
from werkzeug.exceptions import HTTPException
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from jwt.exceptions import InvalidTokenError


# ============================================================
# CUSTOM EXCEPTION CLASSES
# ============================================================

class APIError(Exception):
    """Base class for API errors"""
    
    def __init__(self, message, status_code=400, payload=None):
        super().__init__()
        self.message = message
        self.status_code = status_code
        self.payload = payload
    
    def to_dict(self):
        """Convert error to dictionary"""
        rv = {'error': self.message}
        if self.payload:
            rv.update(self.payload)
        return rv


class ValidationError(APIError):
    """Raised when request validation fails"""
    
    def __init__(self, message, errors=None):
        super().__init__(message, status_code=400, payload={'errors': errors} if errors else None)


class AuthenticationError(APIError):
    """Raised when authentication fails"""
    
    def __init__(self, message='Authentication required'):
        super().__init__(message, status_code=401)


class AuthorizationError(APIError):
    """Raised when user lacks permission"""
    
    def __init__(self, message='You do not have permission to perform this action'):
        super().__init__(message, status_code=403)


class NotFoundError(APIError):
    """Raised when resource is not found"""
    
    def __init__(self, message='Resource not found', resource_type=None):
        payload = {'resource_type': resource_type} if resource_type else None
        super().__init__(message, status_code=404, payload=payload)


class ConflictError(APIError):
    """Raised when there's a conflict (e.g., duplicate entry)"""
    
    def __init__(self, message='Resource already exists'):
        super().__init__(message, status_code=409)


class RateLimitError(APIError):
    """Raised when rate limit is exceeded"""
    
    def __init__(self, message='Rate limit exceeded. Please try again later.'):
        super().__init__(message, status_code=429)


# ============================================================
# ERROR HANDLER REGISTRATION
# ============================================================

def register_error_handlers(app):
    """
    Register all error handlers with the Flask app
    
    Args:
        app: Flask application instance
    """
    
    # ========================================
    # CUSTOM API ERRORS
    # ========================================
    
    @app.errorhandler(APIError)
    def handle_api_error(error):
        """Handle custom API errors"""
        response = jsonify(error.to_dict())
        response.status_code = error.status_code
        return response
    
    @app.errorhandler(ValidationError)
    def handle_validation_error(error):
        """Handle validation errors"""
        response = jsonify(error.to_dict())
        response.status_code = error.status_code
        return response
    
    @app.errorhandler(AuthenticationError)
    def handle_authentication_error(error):
        """Handle authentication errors"""
        response = jsonify(error.to_dict())
        response.status_code = error.status_code
        return response
    
    @app.errorhandler(AuthorizationError)
    def handle_authorization_error(error):
        """Handle authorization errors"""
        response = jsonify(error.to_dict())
        response.status_code = error.status_code
        return response
    
    @app.errorhandler(NotFoundError)
    def handle_not_found_error(error):
        """Handle not found errors"""
        response = jsonify(error.to_dict())
        response.status_code = error.status_code
        return response
    
    @app.errorhandler(ConflictError)
    def handle_conflict_error(error):
        """Handle conflict errors"""
        response = jsonify(error.to_dict())
        response.status_code = error.status_code
        return response
    
    # ========================================
    # HTTP ERRORS
    # ========================================
    
    @app.errorhandler(400)
    def bad_request(error):
        """Handle 400 Bad Request"""
        return jsonify({
            'error': 'Bad request',
            'message': 'The request could not be understood or was missing required parameters',
            'code': 'BAD_REQUEST'
        }), 400
    
    @app.errorhandler(401)
    def unauthorized(error):
        """Handle 401 Unauthorized"""
        return jsonify({
            'error': 'Unauthorized',
            'message': 'Authentication is required to access this resource',
            'code': 'UNAUTHORIZED'
        }), 401
    
    @app.errorhandler(403)
    def forbidden(error):
        """Handle 403 Forbidden"""
        return jsonify({
            'error': 'Forbidden',
            'message': 'You do not have permission to access this resource',
            'code': 'FORBIDDEN'
        }), 403
    
    @app.errorhandler(404)
    def not_found(error):
        """Handle 404 Not Found"""
        return jsonify({
            'error': 'Not found',
            'message': 'The requested resource could not be found',
            'code': 'NOT_FOUND'
        }), 404
    
    @app.errorhandler(405)
    def method_not_allowed(error):
        """Handle 405 Method Not Allowed"""
        return jsonify({
            'error': 'Method not allowed',
            'message': 'The method is not allowed for the requested URL',
            'code': 'METHOD_NOT_ALLOWED'
        }), 405
    
    @app.errorhandler(409)
    def conflict(error):
        """Handle 409 Conflict"""
        return jsonify({
            'error': 'Conflict',
            'message': 'The request conflicts with the current state of the resource',
            'code': 'CONFLICT'
        }), 409
    
    @app.errorhandler(422)
    def unprocessable_entity(error):
        """Handle 422 Unprocessable Entity"""
        return jsonify({
            'error': 'Unprocessable entity',
            'message': 'The request was well-formed but contains semantic errors',
            'code': 'UNPROCESSABLE_ENTITY'
        }), 422
    
    @app.errorhandler(429)
    def too_many_requests(error):
        """Handle 429 Too Many Requests"""
        return jsonify({
            'error': 'Too many requests',
            'message': 'Rate limit exceeded. Please try again later',
            'code': 'RATE_LIMIT_EXCEEDED'
        }), 429
    
    @app.errorhandler(500)
    def internal_server_error(error):
        """Handle 500 Internal Server Error"""
        # Rollback database session on error
        from app import db
        db.session.rollback()
        
        return jsonify({
            'error': 'Internal server error',
            'message': 'An unexpected error occurred. Please try again later',
            'code': 'INTERNAL_SERVER_ERROR'
        }), 500
    
    @app.errorhandler(503)
    def service_unavailable(error):
        """Handle 503 Service Unavailable"""
        return jsonify({
            'error': 'Service unavailable',
            'message': 'The service is temporarily unavailable. Please try again later',
            'code': 'SERVICE_UNAVAILABLE'
        }), 503
    
    # ========================================
    # DATABASE ERRORS
    # ========================================
    
    @app.errorhandler(IntegrityError)
    def handle_integrity_error(error):
        """Handle database integrity errors (unique constraint, foreign key, etc.)"""
        from app import db
        db.session.rollback()
        
        # Try to extract meaningful error message
        error_str = str(error.orig) if hasattr(error, 'orig') else str(error)
        
        # Check for common integrity violations
        if 'unique constraint' in error_str.lower():
            message = 'This resource already exists'
        elif 'foreign key constraint' in error_str.lower():
            message = 'Referenced resource does not exist'
        elif 'not null constraint' in error_str.lower():
            message = 'Required field is missing'
        else:
            message = 'Database constraint violation'
        
        return jsonify({
            'error': message,
            'code': 'INTEGRITY_ERROR',
            'details': error_str if app.config.get('DEBUG') else None
        }), 409
    
    @app.errorhandler(SQLAlchemyError)
    def handle_sqlalchemy_error(error):
        """Handle general SQLAlchemy errors"""
        from app import db
        db.session.rollback()
        
        return jsonify({
            'error': 'Database error',
            'message': 'A database error occurred',
            'code': 'DATABASE_ERROR',
            'details': str(error) if app.config.get('DEBUG') else None
        }), 500
    
    # ========================================
    # JWT ERRORS
    # ========================================
    
    @app.errorhandler(InvalidTokenError)
    def handle_invalid_token(error):
        """Handle invalid JWT tokens"""
        return jsonify({
            'error': 'Invalid token',
            'message': 'The provided authentication token is invalid',
            'code': 'INVALID_TOKEN'
        }), 401
    
    # ========================================
    # GENERAL ERRORS
    # ========================================
    
    @app.errorhandler(HTTPException)
    def handle_http_exception(error):
        """Handle all HTTP exceptions"""
        return jsonify({
            'error': error.name,
            'message': error.description,
            'code': error.name.upper().replace(' ', '_')
        }), error.code
    
    @app.errorhandler(Exception)
    def handle_unexpected_error(error):
        """Handle all unexpected errors"""
        from app import db
        db.session.rollback()
        
        # Log the error (in production, use proper logging)
        print(f"Unexpected error: {error}")
        
        # Don't expose internal error details in production
        if app.config.get('DEBUG'):
            return jsonify({
                'error': 'Unexpected error',
                'message': str(error),
                'type': type(error).__name__,
                'code': 'UNEXPECTED_ERROR'
            }), 500
        else:
            return jsonify({
                'error': 'Internal server error',
                'message': 'An unexpected error occurred. Please try again later',
                'code': 'INTERNAL_SERVER_ERROR'
            }), 500


# ============================================================
# RESPONSE HELPERS
# ============================================================

def success_response(data=None, message=None, status_code=200):
    """
    Create a standardized success response
    
    Args:
        data: Response data (dict, list, or None)
        message: Optional success message
        status_code: HTTP status code (default: 200)
    
    Returns:
        Flask response tuple (json, status_code)
    
    Example:
        return success_response({'user': user_data}, 'User created', 201)
    """
    response = {'success': True}
    
    if message:
        response['message'] = message
    
    if data is not None:
        response['data'] = data
    
    return jsonify(response), status_code


def error_response(message, status_code=400, **kwargs):
    """
    Create a standardized error response
    
    Args:
        message: Error message
        status_code: HTTP status code (default: 400)
        **kwargs: Additional error details
    
    Returns:
        Flask response tuple (json, status_code)
    
    Example:
        return error_response('User not found', 404, user_id=user_id)
    """
    response = {
        'success': False,
        'error': message
    }
    
    if kwargs:
        response.update(kwargs)
    
    return jsonify(response), status_code


def paginated_response(items, pagination, message=None):
    """
    Create a standardized paginated response
    
    Args:
        items: List of items to return
        pagination: SQLAlchemy pagination object
        message: Optional message
    
    Returns:
        Flask response tuple (json, status_code)
    
    Example:
        pagination = User.query.paginate(page=1, per_page=20)
        return paginated_response(
            [u.to_dict() for u in pagination.items],
            pagination
        )
    """
    response = {
        'success': True,
        'data': items,
        'pagination': {
            'page': pagination.page,
            'per_page': pagination.per_page,
            'total': pagination.total,
            'pages': pagination.pages,
            'has_next': pagination.has_next,
            'has_prev': pagination.has_prev
        }
    }
    
    if message:
        response['message'] = message
    
    return jsonify(response), 200
