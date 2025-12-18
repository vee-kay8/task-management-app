"""
============================================================
APPLICATION ENTRY POINT - START THE SERVER HERE
============================================================

This is the main file that starts our Flask application.
Think of it as the "power button" for our backend server.

Usage:
    python run.py

The server will start on: http://localhost:5000
"""

# Import the create_app function from our app package
# This function creates and configures the Flask application
from app import create_app

# Import environment variables support
import os

# Create the Flask application instance
# The create_app() function is defined in app/__init__.py
app = create_app()

# This block only runs when we execute this file directly
# (not when it's imported by another file)
if __name__ == '__main__':
    """
    Start the Flask development server
    
    Parameters explained:
    - host='0.0.0.0': Listen on all network interfaces
                      '127.0.0.1' = only localhost
                      '0.0.0.0' = accessible from other devices
    
    - port=5000: The port number (default Flask port)
                 Access at: http://localhost:5000
    
    - debug=True: Enable debug mode
                  - Auto-reloads when code changes
                  - Shows detailed error messages
                  - NEVER use in production!
    """
    
    # Get port from environment variable or use default 5000
    port = int(os.getenv('FLASK_PORT', 5000))
    
    # Get debug mode from environment variable or use default True
    debug = os.getenv('DEBUG', 'True') == 'True'
    
    # Print startup message
    print("=" * 60)
    print("Task Management API Server Starting...")
    print(f"Running on: http://localhost:{port}")
    print(f"Debug mode: {debug}")
    print(f"Database: {os.getenv('DATABASE_URL', 'Not configured')}")
    print("=" * 60)
    print("\nPress CTRL+C to stop the server\n")
    
    # Start the server!
    app.run(
        host='0.0.0.0',
        port=port,
        debug=debug
    )
