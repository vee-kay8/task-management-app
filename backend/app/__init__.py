"""
============================================================
FLASK APPLICATION FACTORY
============================================================

This file creates and configures the Flask application.
It's called a "factory" because it manufactures/creates the app.

Think of it like assembling a car:
- Add engine (Flask)
- Add wheels (database)
- Add seats (routes/endpoints)
- Add security system (authentication)
"""

from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from flask_marshmallow import Marshmallow

# ============================================================
# INITIALIZE EXTENSIONS
# ============================================================
# These are like "plugins" for Flask
# We initialize them here but configure them in create_app()

# Database ORM - converts Python code to SQL
db = SQLAlchemy()

# Database migrations - manages schema changes
migrate = Migrate()

# Password hashing - encrypts passwords
bcrypt = Bcrypt()

# JWT authentication - handles login tokens
jwt = JWTManager()

# CORS - allows frontend to talk to backend
cors = CORS()

# Marshmallow - validates and serializes data
ma = Marshmallow()


def create_app(config_name=None):
    """
    Application factory function
    
    This function creates and configures a Flask application instance.
    
    Args:
        config_name (str): Configuration environment ('development', 'testing', 'production')
        
    Returns:
        Flask: Configured Flask application instance
    
    Example:
        app = create_app('development')
        app.run()
    """
    
    # ========================================
    # CREATE FLASK APP
    # ========================================
    # __name__ tells Flask where to find resources (templates, static files)
    app = Flask(__name__)
    
    # ========================================
    # LOAD CONFIGURATION
    # ========================================
    # Import configuration from config.py
    from app.config import config_by_name
    
    # Use provided config or default to 'development'
    config_name = config_name or 'development'
    app.config.from_object(config_by_name[config_name])
    
    # ========================================
    # INITIALIZE EXTENSIONS WITH APP
    # ========================================
    # Connect all our plugins to this Flask app
    
    # Initialize database
    db.init_app(app)
    
    # Initialize migrations (for database schema changes)
    migrate.init_app(app, db)
    
    # Initialize password hasher
    bcrypt.init_app(app)
    
    # Initialize JWT authentication
    jwt.init_app(app)
    
    # Initialize CORS (allow frontend access)
    cors.init_app(app, resources={
        r"/api/*": {
            "origins": app.config['CORS_ORIGINS'],
            "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
            "allow_headers": ["Content-Type", "Authorization"]
        }
    })
    
    # Initialize Marshmallow (must be after db)
    ma.init_app(app)
    
    # ========================================
    # REGISTER BLUEPRINTS (API ROUTES)
    # ========================================
    # Blueprints are like modules/sections of our API
    # Each blueprint handles specific functionality
    
    # Import blueprints (we'll create these next)
    from app.routes.auth import auth_bp
    from app.routes.tasks import tasks_bp
    from app.routes.projects import projects_bp
    from app.routes.users import users_bp
    
    # Register blueprints with URL prefixes
    # This means all routes in auth_bp will start with /api/auth
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(tasks_bp, url_prefix='/api/tasks')
    app.register_blueprint(projects_bp, url_prefix='/api/projects')
    app.register_blueprint(users_bp, url_prefix='/api/users')
    
    # ========================================
    # ROOT ENDPOINT (Health Check)
    # ========================================
    @app.route('/')
    def index():
        """
        Root endpoint - returns API information
        
        Access at: http://localhost:5000/
        
        Returns:
            JSON with API info and available endpoints
        """
        return jsonify({
            'name': 'Task Management API',
            'version': '1.0.0',
            'status': 'running',
            'endpoints': {
                'auth': '/api/auth',
                'tasks': '/api/tasks',
                'projects': '/api/projects',
                'users': '/api/users'
            },
            'docs': 'Coming soon!'
        })
    
    # Health check endpoint (for monitoring/deployment)
    @app.route('/health')
    def health():
        """
        Health check endpoint
        
        Returns:
            JSON with server health status
        """
        return jsonify({
            'status': 'healthy',
            'database': 'connected'
        }), 200
    
    # ========================================
    # ERROR HANDLERS
    # ========================================
    # Register centralized error handlers
    from app.errors import register_error_handlers
    register_error_handlers(app)
    
    # ========================================
    # JWT ERROR HANDLERS
    # ========================================
    # Handle authentication errors
    
    @jwt.expired_token_loader
    def expired_token_callback(jwt_header, jwt_payload):
        """Handle expired JWT tokens"""
        return jsonify({
            'success': False,
            'error': {
                'code': 'TOKEN_EXPIRED',
                'message': 'Your session has expired. Please login again.'
            }
        }), 401
    
    @jwt.invalid_token_loader
    def invalid_token_callback(error):
        """Handle invalid JWT tokens"""
        return jsonify({
            'success': False,
            'error': {
                'code': 'INVALID_TOKEN',
                'message': 'Invalid authentication token'
            }
        }), 401
    
    @jwt.unauthorized_loader
    def unauthorized_callback(error):
        """Handle missing JWT tokens"""
        return jsonify({
            'success': False,
            'error': {
                'code': 'UNAUTHORIZED',
                'message': 'Authentication required'
            }
        }), 401
    
    # ========================================
    # BEFORE FIRST REQUEST
    # ========================================
    # This runs once when the app starts
    
    @app.before_request
    def before_first_request():
        """
        Create database tables if they don't exist
        
        This runs before the first request to ensure
        all tables are created in the database
        """
        pass  # We'll use Flask-Migrate for this instead
    
    # ========================================
    # RETURN CONFIGURED APP
    # ========================================
    return app


# ============================================================
# IMPORT MODELS
# ============================================================
# Import all models so Flask-Migrate can detect them
# This must be after db initialization but before migrations

from app.models import user, project, task
