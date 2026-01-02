# ============================================================
# MULTI-STAGE DOCKERFILE FOR FLASK BACKEND
# ============================================================
# This Dockerfile uses a multi-stage build approach to create
# an optimized production image for our Flask application.
#
# WHAT IS A MULTI-STAGE BUILD?
# Instead of one large image with all build tools, we create
# multiple "stages" and only keep what we need in the final image.
# This dramatically reduces the final image size.
#
# STAGE 1: Builder - Installs dependencies and compiles packages
# STAGE 2: Runtime - Only includes what's needed to run the app
# ============================================================

# ============================================================
# STAGE 1: BUILDER
# ============================================================
# Purpose: Install and compile Python dependencies
# This stage will be discarded, keeping only the compiled packages

FROM python:3.9-slim as builder

# ============================================================
# IMAGE METADATA (OCI Labels)
# ============================================================
# Following Open Container Initiative (OCI) annotation standards
# https://github.com/opencontainers/image-spec/blob/main/annotations.md

LABEL org.opencontainers.image.title="Task Management Backend"
LABEL org.opencontainers.image.description="Flask REST API for Task Management Application"
LABEL org.opencontainers.image.version="1.0.0"
LABEL org.opencontainers.image.authors="vee-kay8"
LABEL org.opencontainers.image.vendor="Task Management Project"
LABEL org.opencontainers.image.licenses="MIT"
LABEL org.opencontainers.image.source="https://github.com/vee-kay8/task-management-app"
LABEL org.opencontainers.image.documentation="https://github.com/vee-kay8/task-management-app/blob/main/README.md"

# Custom labels for internal metadata
LABEL app.name="task-management-backend"
LABEL app.component="api"
LABEL app.tier="backend"
LABEL app.runtime="python"
LABEL app.runtime.version="3.9"
LABEL app.framework="flask"
LABEL maintainer="vee-kay8"
LABEL stage="builder"

# WORKDIR: Sets the working directory inside the container
# All subsequent commands will run from this directory
# Think of it like 'cd /app' but permanent
WORKDIR /app

# WHY python:3.9-slim?
# - python:3.9: Matches our development Python version
# - slim: Smaller base image (removes unnecessary packages)
# - alpine: Even smaller but can cause issues with some Python packages
# We use 'slim' for compatibility with packages like psycopg2

# ============================================================
# INSTALL SYSTEM DEPENDENCIES
# ============================================================
# Some Python packages need system libraries to compile
# For example, psycopg2 needs PostgreSQL development libraries

RUN apt-get update && apt-get install -y \
    # PostgreSQL client and development files
    # Required for psycopg2 to connect to PostgreSQL
    postgresql-client \
    libpq-dev \
    # GCC compiler - needed to build Python packages from source
    gcc \
    # Python development headers - needed for C extensions
    python3-dev \
    # musl-dev - C library for compiling
    musl-dev \
    # Clean up apt cache to reduce layer size
    && rm -rf /var/lib/apt/lists/*

# WHY CLEAN UP APT CACHE?
# Each RUN command creates a new layer in the Docker image.
# Removing the apt cache reduces the layer size significantly.
# The && chains commands so they run in a single layer.

# ============================================================
# INSTALL PYTHON DEPENDENCIES
# ============================================================

# COPY requirements.txt first (before copying all code)
# WHY COPY requirements.txt SEPARATELY?
# Docker caches layers. If requirements.txt hasn't changed,
# Docker reuses the cached layer instead of reinstalling everything.
# This makes subsequent builds much faster.
COPY requirements.txt .

# Create a Python virtual environment
# WHY USE A VIRTUAL ENVIRONMENT IN A CONTAINER?
# While not strictly necessary (the container is already isolated),
# it's a best practice that makes the dependencies location explicit
# and easier to copy to the next stage.
RUN python -m venv /opt/venv

# Activate virtual environment by updating PATH
# This ensures pip and python commands use the virtual environment
ENV PATH="/opt/venv/bin:$PATH"

# Install Python dependencies
# --no-cache-dir: Don't cache pip downloads (saves space)
# --upgrade: Ensure pip is latest version
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# AT THIS POINT:
# We have all Python packages installed in /opt/venv
# We have system libraries that were needed for compilation
# This stage is about 800MB - but we won't keep all of it!

# ============================================================
# STAGE 2: RUNTIME
# ============================================================
# Purpose: Create the final, minimal image with only runtime needs
# This stage starts fresh and only copies what's needed

FROM python:3.9-slim

# Add metadata for the runtime stage
LABEL maintainer="vee-kay8"
LABEL description="Task Management Backend - Production Runtime"
LABEL version="1.0.0"
LABEL stage="runtime"

# ============================================================
# INSTALL ONLY RUNTIME DEPENDENCIES
# ============================================================
# We only need PostgreSQL client libraries to run (not build tools)

RUN apt-get update && apt-get install -y \
    # PostgreSQL client - needed at runtime to connect to database
    libpq5 \
    # curl - useful for health checks
    curl \
    && rm -rf /var/lib/apt/lists/*

# NOTICE: We don't install gcc, python3-dev, etc.
# Those were only needed to build/compile packages, not to run them.
# This significantly reduces the final image size.

# ============================================================
# CREATE APPLICATION USER
# ============================================================
# SECURITY BEST PRACTICE: Never run containers as root
# Create a dedicated user with limited permissions

RUN groupadd -r appuser && \
    useradd -r -g appuser -u 1000 -m -s /bin/bash appuser

# WHAT THIS DOES:
# groupadd -r appuser: Creates a system group named 'appuser'
# useradd -r: Creates a system user (not a regular user)
# -g appuser: Adds user to the appuser group
# -u 1000: Sets user ID to 1000 (consistent across containers)
# -m: Creates home directory
# -s /bin/bash: Sets shell to bash

# ============================================================
# SET UP APPLICATION DIRECTORY
# ============================================================

# Create app directory
WORKDIR /app

# Copy the virtual environment from builder stage
# COPY --from=builder: Takes files from the previous stage
# We only copy the compiled packages, not the build tools
COPY --from=builder /opt/venv /opt/venv

# ============================================================
# COPY APPLICATION CODE
# ============================================================

# Copy all application files
# This includes:
# - app/ directory (our Flask application)
# - migrations/ directory (database migrations)
# - run.py (application entry point)
# - Any other Python files
COPY --chown=appuser:appuser . .

# --chown=appuser:appuser: Sets ownership to our non-root user
# This ensures the appuser can read all files

# WHY COPY CODE LAST?
# Code changes frequently, dependencies don't.
# By copying code last, we maximize Docker layer cache hits.
# If only code changes, Docker reuses all previous layers.

# ============================================================
# ENVIRONMENT VARIABLES
# ============================================================

# Activate the virtual environment
ENV PATH="/opt/venv/bin:$PATH"

# Python environment variables for optimization
# PYTHONUNBUFFERED=1: Forces Python output to be unbuffered
# This ensures logs appear immediately (important for debugging)
ENV PYTHONUNBUFFERED=1

# PYTHONDONTWRITEBYTECODE=1: Prevents Python from writing .pyc files
# .pyc files are compiled Python files - not needed in containers
# This saves disk space and speeds up container startup
ENV PYTHONDONTWRITEBYTECODE=1

# Flask environment (will be overridden by docker-compose)
ENV FLASK_APP=run.py

# ============================================================
# SET CORRECT PERMISSIONS
# ============================================================

# Ensure appuser owns the app directory
# -R: Recursive (includes all subdirectories)
RUN chown -R appuser:appuser /app

# Switch to non-root user
# All subsequent commands (including CMD) will run as this user
USER appuser

# ============================================================
# EXPOSE PORT
# ============================================================

# EXPOSE: Documents which port the container listens on
# This is for documentation only - doesn't actually publish the port
# The actual port mapping happens in docker-compose.yml
EXPOSE 5000

# WHY PORT 5000?
# This is Flask's default development port.
# In production, we might use a different port or run behind nginx.

# ============================================================
# HEALTH CHECK
# ============================================================

# HEALTHCHECK: Tells Docker how to test if the container is working
# Docker will periodically run this command to check container health
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:5000/api/health || exit 1

# PARAMETERS EXPLAINED:
# --interval=30s: Check every 30 seconds
# --timeout=10s: Each check must complete within 10 seconds
# --start-period=40s: Don't check for first 40 seconds (app startup time)
# --retries=3: Mark unhealthy after 3 consecutive failures
# curl -f: Fail on HTTP errors
# || exit 1: Return error code if curl fails

# NOTE: This assumes you have a health check endpoint at /api/health
# We will create this endpoint in the Flask application

# ============================================================
# STARTUP COMMAND
# ============================================================

# CMD: The default command to run when container starts
# This can be overridden in docker-compose.yml or when running docker run

# For production, we use gunicorn (WSGI server) instead of Flask dev server
# Flask's built-in server is not suitable for production

# Development command (Flask dev server):
# CMD ["python", "run.py"]

# Production command (Gunicorn):
# Gunicorn is a production-grade WSGI server for Python web apps
CMD ["gunicorn", \
     # --bind 0.0.0.0:5000: Listen on all network interfaces, port 5000
     "--bind", "0.0.0.0:5000", \
     # --workers 4: Number of worker processes (rule of thumb: 2-4 x CPU cores)
     "--workers", "4", \
     # --threads 2: Number of threads per worker
     "--threads", "2", \
     # --timeout 60: Worker timeout in seconds
     "--timeout", "60", \
     # --access-logfile -: Log access logs to stdout (Docker captures this)
     "--access-logfile", "-", \
     # --error-logfile -: Log errors to stderr
     "--error-logfile", "-", \
     # --log-level info: Logging level
     "--log-level", "info", \
     # app:app: Import 'app' from 'app' module (app/__init__.py:create_app())
     "app:create_app()"]

# WHY GUNICORN?
# - Production-grade WSGI server
# - Handles multiple concurrent requests
# - Process management and auto-restart
# - Much more robust than Flask's development server

# ============================================================
# BUILD AND RUN INSTRUCTIONS
# ============================================================
# 
# BUILD THE IMAGE:
# docker build -t task-management-backend:latest ./backend
#
# RUN THE CONTAINER (standalone):
# docker run -d \
#   -p 5000:5000 \
#   -e DATABASE_URL=postgresql://user:pass@host:5432/db \
#   -e JWT_SECRET_KEY=your-secret-key \
#   --name backend \
#   task-management-backend:latest
#
# VIEW LOGS:
# docker logs -f backend
#
# STOP CONTAINER:
# docker stop backend
#
# REMOVE CONTAINER:
# docker rm backend
#
# ============================================================
# IMAGE SIZE COMPARISON
# ============================================================
# Without multi-stage build: ~800-900 MB
# With multi-stage build: ~200-250 MB
# Savings: ~70% reduction in image size
# ============================================================
