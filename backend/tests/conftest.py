"""
============================================================
PYTEST FIXTURES - SHARED TEST DATA
============================================================

What are fixtures?
- Reusable test data/setup that multiple tests can use
- Prevents copying the same code in every test
- Creates a clean database for each test
- Provides mock objects (users, projects, tasks)

How to use:
- Add fixture name as function parameter
- Pytest automatically passes the fixture value

Example:
    def test_something(app, db_session):
        # 'app' and 'db_session' are fixtures defined below
        # Pytest automatically provides them!
"""

import pytest
from app import create_app, db as _db
from app.models.user import User, UserRole
from app.models.project import Project
from app.models.task import Task, TaskStatus, TaskPriority
from datetime import datetime


# ============================================================
# APPLICATION FIXTURES
# ============================================================


@pytest.fixture(scope="session")
def app():
    """
    Create Flask application for testing.

    Scope: 'session'
    - Created once per test session
    - Shared across all tests
    - More efficient than creating app for each test

    Why we need this:
    - Tests need a Flask app to work with
    - Configured differently than production (test database, etc.)

    Returns:
        Flask app instance configured for testing
    """
    # Create app in testing mode
    app = create_app("testing")

    # Push application context
    # This makes 'current_app' available in tests
    ctx = app.app_context()
    ctx.push()

    # Provide app to tests
    yield app

    # Cleanup: Remove app context after all tests
    ctx.pop()


@pytest.fixture(scope="session")
def db(app):
    """
    Create test database.

    Scope: 'session'
    - Created once, used by all tests
    - Faster than creating DB for each test

    Why we need this:
    - Tests need a database to store test data
    - Each test run gets a fresh, empty database

    Returns:
        SQLAlchemy database instance
    """
    # Create all tables in test database
    _db.create_all()

    # Provide database to tests
    yield _db

    # Cleanup: Drop all tables after tests complete
    _db.drop_all()


@pytest.fixture(scope="function")
def db_session(db):
    """
    Create a database session for a single test.

    Scope: 'function'
    - New session for EACH test
    - Changes are rolled back after each test
    - Tests don't affect each other (isolation)

    Why we need this:
    - Each test starts with a clean database
    - Test data doesn't leak between tests
    - If test fails, database is still clean for next test

    Returns:
        SQLAlchemy session
    """
    # Start a new nested transaction
    connection = db.engine.connect()
    transaction = connection.begin()

    # Override db.session to use this connection
    # Flask-SQLAlchemy 3.x: use session maker directly
    from sqlalchemy.orm import sessionmaker

    Session = sessionmaker(bind=connection)
    session = Session()

    # Replace the app's session with our test session
    old_session = db.session
    db.session = session

    # Provide session to test
    yield session

    # Cleanup: Rollback changes after test
    try:
        session.close()
    except Exception:
        pass  # Ignore cleanup errors

    try:
        transaction.rollback()
    except Exception:
        pass  # Transaction might already be rolled back

    try:
        connection.close()
    except Exception:
        pass

    # Restore original session
    db.session = old_session


# ============================================================
# USER FIXTURES
# ============================================================


@pytest.fixture
def user(db_session):
    """
    Create a basic test user.

    Why we need this:
    - Many tests need a user (login tests, task creation, etc.)
    - Instead of creating user in each test, use this fixture

    Usage:
        def test_user_login(user):
            # 'user' is automatically created and provided
            assert user.email == 'testuser@example.com'

    Returns:
        User object saved in database
    """
    # Create user instance
    user = User(
        email="testuser@example.com", full_name="Test User", role=UserRole.MEMBER
    )

    # Set password (will be hashed automatically)
    user.set_password("testpassword123")

    # Save to database
    db_session.add(user)
    db_session.commit()

    # Refresh to get database-generated fields (id, created_at)
    db_session.refresh(user)

    return user


@pytest.fixture
def admin_user(db_session):
    """
    Create an admin user for permission testing.

    Why we need this:
    - Testing admin-only features (delete all projects, etc.)
    - Testing permission checks (can admin do X?)

    Returns:
        Admin user object
    """
    admin = User(email="admin@example.com", full_name="Admin User", role=UserRole.ADMIN)
    admin.set_password("adminpass123")

    db_session.add(admin)
    db_session.commit()
    db_session.refresh(admin)

    return admin


# ============================================================
# PROJECT FIXTURES
# ============================================================


@pytest.fixture
def project(db_session, user):
    """
    Create a test project owned by test user.

    Why we need this:
    - Tasks belong to projects
    - Testing project-related features

    Note: Requires 'user' fixture (dependency)

    Returns:
        Project object
    """
    project = Project(
        name="Test Project",
        description="A project for testing purposes",
        owner_id=user.id,
    )

    db_session.add(project)
    db_session.commit()
    db_session.refresh(project)

    return project


# ============================================================
# TASK FIXTURES
# ============================================================


@pytest.fixture
def task(db_session, project, user):
    """
    Create a test task in test project.

    Why we need this:
    - Most tests involve tasks
    - Prevents repeating task creation code

    Note: Requires both 'project' and 'user' fixtures

    Returns:
        Task object
    """
    task = Task(
        title="Test Task",
        description="A task for testing",
        status=TaskStatus.TODO,
        priority=TaskPriority.MEDIUM,
        project_id=project.id,
        assignee_id=user.id,
        reporter_id=user.id,  # Required field
    )

    db_session.add(task)
    db_session.commit()
    db_session.refresh(task)

    return task


@pytest.fixture
def completed_task(db_session, project, user):
    """
    Create a completed task.

    Why we need this:
    - Testing "show only completed tasks" filters
    - Testing statistics (how many tasks done?)

    Returns:
        Completed task object
    """
    task = Task(
        title="Completed Task",
        description="This task is done!",
        status=TaskStatus.DONE,
        priority=TaskPriority.HIGH,
        project_id=project.id,
        assignee_id=user.id,
        reporter_id=user.id,
        completed_at=datetime.utcnow(),
    )

    db_session.add(task)
    db_session.commit()
    db_session.refresh(task)

    return task


# ============================================================
# MULTIPLE OBJECTS FIXTURES
# ============================================================


@pytest.fixture
def multiple_tasks(db_session, project, user):
    """
    Create multiple tasks with different statuses.

    Why we need this:
    - Testing task lists
    - Testing filters (show only TODO tasks)
    - Testing sorting (order by priority)

    Returns:
        List of 5 task objects with varying properties
    """
    tasks = []

    # Task 1: High priority, TODO
    tasks.append(
        Task(
            title="Urgent Task",
            status=TaskStatus.TODO,
            priority=TaskPriority.HIGH,
            project_id=project.id,
            assignee_id=user.id,
            reporter_id=user.id,
        )
    )

    # Task 2: Medium priority, IN_PROGRESS
    tasks.append(
        Task(
            title="Current Task",
            status=TaskStatus.IN_PROGRESS,
            priority=TaskPriority.MEDIUM,
            project_id=project.id,
            assignee_id=user.id,
            reporter_id=user.id,
        )
    )

    # Task 3: Low priority, DONE
    tasks.append(
        Task(
            title="Finished Task",
            status=TaskStatus.DONE,
            priority=TaskPriority.LOW,
            project_id=project.id,
            assignee_id=user.id,
            reporter_id=user.id,
        )
    )

    # Task 4: High priority, IN_REVIEW
    tasks.append(
        Task(
            title="Review Task",
            status=TaskStatus.IN_REVIEW,
            priority=TaskPriority.HIGH,
            project_id=project.id,
            assignee_id=user.id,
            reporter_id=user.id,
        )
    )

    # Task 5: Medium priority, TODO
    tasks.append(
        Task(
            title="Another TODO",
            status=TaskStatus.TODO,
            priority=TaskPriority.MEDIUM,
            project_id=project.id,
            assignee_id=user.id,
            reporter_id=user.id,
        )
    )

    # Save all tasks
    for task in tasks:
        db_session.add(task)

    db_session.commit()

    # Refresh to get IDs
    for task in tasks:
        db_session.refresh(task)

    return tasks


# ============================================================
# AUTHENTICATION FIXTURES
# ============================================================


@pytest.fixture
def auth_headers(user):
    """
    Create authentication headers for API requests.

    Why we need this:
    - Most API endpoints require authentication
    - JWT token in Authorization header
    - Prevents generating token in each test

    Usage:
        def test_get_tasks(client, auth_headers):
            response = client.get('/api/tasks', headers=auth_headers)

    Returns:
        Dictionary with Authorization header
    """
    from flask_jwt_extended import create_access_token

    # Generate JWT token for user
    access_token = create_access_token(identity=user.id)

    # Return headers dictionary
    return {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
    }


# ============================================================
# CLIENT FIXTURE
# ============================================================


@pytest.fixture
def client(app):
    """
    Create test client for making API requests.

    Why we need this:
    - Simulates HTTP requests to your API
    - No need to run actual server
    - Can test endpoints directly

    Usage:
        def test_endpoint(client):
            response = client.get('/api/users')
            assert response.status_code == 200

    Returns:
        Flask test client
    """
    return app.test_client()


# ============================================================
# FIXTURE DEPENDENCY CHAIN
# ============================================================
# Understanding how fixtures depend on each other:
#
# app (session)
#  └─> db (session)
#       └─> db_session (function)
#            ├─> user (function)
#            │    ├─> project (function)
#            │    │    └─> task (function)
#            │    │    └─> completed_task (function)
#            │    │    └─> multiple_tasks (function)
#            │    └─> auth_headers (function)
#            └─> admin_user (function)
#
# When you use 'task' fixture, pytest automatically creates:
# 1. app
# 2. db
# 3. db_session
# 4. user
# 5. project
# 6. task
# ============================================================
