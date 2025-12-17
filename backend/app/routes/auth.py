"""
============================================================
AUTHENTICATION ROUTES
============================================================

Handles user authentication:
- POST /register - Create new user account
- POST /login - Authenticate user and return JWT token
- POST /logout - Invalidate user session (future: token blacklist)
- GET /me - Get current authenticated user info

Security features:
- Password hashing with bcrypt
- JWT tokens for stateless authentication
- Email validation
- Role-based access control ready
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    jwt_required,
    get_jwt_identity,
    get_jwt
)
from app import db
from app.models.user import User, UserRole
from sqlalchemy.exc import IntegrityError
from datetime import timedelta
import re

# ============================================================
# BLUEPRINT SETUP
# ============================================================
auth_bp = Blueprint('auth', __name__)


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def validate_email(email):
    """
    Validate email format using regex
    Returns True if valid, False otherwise
    """
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None


def validate_password(password):
    """
    Validate password strength
    Requirements:
    - At least 8 characters
    - Contains uppercase and lowercase
    - Contains at least one number
    """
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
# AUTHENTICATION ROUTES
# ============================================================

@auth_bp.route('/register', methods=['POST'])
def register():
    """
    Register a new user
    
    Request Body:
    {
        "email": "user@example.com",
        "password": "SecurePass123",
        "full_name": "John Doe",
        "role": "MEMBER"  (optional, defaults to MEMBER)
    }
    
    Returns:
    - 201: User created successfully with user data
    - 400: Validation error (invalid email, weak password)
    - 409: Email already exists
    """
    try:
        data = request.get_json()
        
        # Validate required fields
        if not data:
            return jsonify({'error': 'Request body is required'}), 400
        
        required_fields = ['email', 'password', 'full_name']
        missing_fields = [field for field in required_fields if field not in data]
        
        if missing_fields:
            return jsonify({
                'error': f'Missing required fields: {", ".join(missing_fields)}'
            }), 400
        
        email = data['email'].strip().lower()
        password = data['password']
        full_name = data['full_name'].strip()
        role = data.get('role', 'MEMBER').upper()
        
        # Validate email format
        if not validate_email(email):
            return jsonify({'error': 'Invalid email format'}), 400
        
        # Validate password strength
        is_valid, message = validate_password(password)
        if not is_valid:
            return jsonify({'error': message}), 400
        
        # Validate full name
        if len(full_name) < 2:
            return jsonify({'error': 'Full name must be at least 2 characters'}), 400
        
        # Validate role
        try:
            user_role = UserRole[role]
        except KeyError:
            return jsonify({
                'error': f'Invalid role. Must be one of: {", ".join([r.name for r in UserRole])}'
            }), 400
        
        # Check if email already exists
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            return jsonify({'error': 'Email already registered'}), 409
        
        # Create new user
        new_user = User(
            email=email,
            full_name=full_name,
            role=user_role
        )
        new_user.set_password(password)
        
        db.session.add(new_user)
        db.session.commit()
        
        # Return user data (without password hash)
        return jsonify({
            'message': 'User registered successfully',
            'user': new_user.to_dict()
        }), 201
        
    except IntegrityError:
        db.session.rollback()
        return jsonify({'error': 'Email already registered'}), 409
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Registration failed: {str(e)}'}), 500


@auth_bp.route('/login', methods=['POST'])
def login():
    """
    Authenticate user and return JWT tokens
    
    Request Body:
    {
        "email": "user@example.com",
        "password": "SecurePass123"
    }
    
    Returns:
    - 200: Login successful with access_token, refresh_token, and user data
    - 400: Missing email or password
    - 401: Invalid credentials or account disabled
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'Request body is required'}), 400
        
        email = data.get('email', '').strip().lower()
        password = data.get('password', '')
        
        if not email or not password:
            return jsonify({'error': 'Email and password are required'}), 400
        
        # Find user by email
        user = User.query.filter_by(email=email).first()
        
        # Check credentials
        if not user or not user.check_password(password):
            return jsonify({'error': 'Invalid email or password'}), 401
        
        # Check if account is active
        if not user.is_active:
            return jsonify({'error': 'Account is disabled. Contact administrator.'}), 401
        
        # Update last login timestamp
        user.update_last_login()
        db.session.commit()
        
        # Create JWT tokens
        # Access token: short-lived (1 hour) for API requests
        # Refresh token: long-lived (30 days) for getting new access tokens
        access_token = create_access_token(
            identity=str(user.id),
            additional_claims={
                'email': user.email,
                'role': user.role.value,
                'full_name': user.full_name
            },
            expires_delta=timedelta(hours=1)
        )
        
        refresh_token = create_refresh_token(
            identity=str(user.id),
            expires_delta=timedelta(days=30)
        )
        
        return jsonify({
            'message': 'Login successful',
            'access_token': access_token,
            'refresh_token': refresh_token,
            'token_type': 'Bearer',
            'expires_in': 3600,  # seconds
            'user': user.to_dict()
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Login failed: {str(e)}'}), 500


@auth_bp.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    """
    Get a new access token using refresh token
    
    Headers:
        Authorization: Bearer <refresh_token>
    
    Returns:
    - 200: New access token
    - 401: Invalid or expired refresh token
    """
    try:
        # Get user ID from refresh token
        user_id = get_jwt_identity()
        
        # Verify user still exists and is active
        user = User.query.get(user_id)
        if not user or not user.is_active:
            return jsonify({'error': 'Invalid user or account disabled'}), 401
        
        # Create new access token
        access_token = create_access_token(
            identity=str(user.id),
            additional_claims={
                'email': user.email,
                'role': user.role.value,
                'full_name': user.full_name
            },
            expires_delta=timedelta(hours=1)
        )
        
        return jsonify({
            'access_token': access_token,
            'token_type': 'Bearer',
            'expires_in': 3600
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Token refresh failed: {str(e)}'}), 500


@auth_bp.route('/me', methods=['GET'])
@jwt_required()
def get_current_user():
    """
    Get current authenticated user information
    
    Headers:
        Authorization: Bearer <access_token>
    
    Returns:
    - 200: User data
    - 401: Invalid or expired token
    - 404: User not found
    """
    try:
        # Get user ID from JWT token
        user_id = get_jwt_identity()
        
        # Get user from database
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        if not user.is_active:
            return jsonify({'error': 'Account is disabled'}), 401
        
        return jsonify({
            'user': user.to_dict()
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Failed to get user info: {str(e)}'}), 500


@auth_bp.route('/logout', methods=['POST'])
@jwt_required()
def logout():
    """
    Logout current user
    
    Note: Since we're using stateless JWT tokens, true logout would require
    token blacklisting (storing revoked tokens in Redis/database).
    For now, this is a placeholder that returns success.
    Client should discard the token on their side.
    
    Headers:
        Authorization: Bearer <access_token>
    
    Returns:
    - 200: Logout successful
    """
    try:
        # Get token JTI (JWT ID) for potential blacklisting
        jti = get_jwt()["jti"]
        user_id = get_jwt_identity()
        
        # TODO: Add token to blacklist (Redis recommended)
        # Example: redis_client.setex(f"blacklist:{jti}", 3600, "true")
        
        return jsonify({
            'message': 'Logout successful',
            'note': 'Please discard your tokens on the client side'
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Logout failed: {str(e)}'}), 500


# ============================================================
# UTILITY ROUTES (for testing/debugging)
# ============================================================

@auth_bp.route('/validate-token', methods=['GET'])
@jwt_required()
def validate_token():
    """
    Check if current token is valid
    Useful for frontend to verify token before making requests
    
    Headers:
        Authorization: Bearer <access_token>
    
    Returns:
    - 200: Token is valid with user info
    - 401: Token is invalid or expired
    """
    try:
        user_id = get_jwt_identity()
        jwt_data = get_jwt()
        
        user = User.query.get(user_id)
        if not user:
            return jsonify({'valid': False, 'error': 'User not found'}), 404
        
        return jsonify({
            'valid': True,
            'user_id': user_id,
            'email': jwt_data.get('email'),
            'role': jwt_data.get('role'),
            'expires_at': jwt_data.get('exp')
        }), 200
        
    except Exception as e:
        return jsonify({'valid': False, 'error': str(e)}), 401
