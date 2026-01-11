"""
============================================================
UNIT TESTS FOR USER MODEL
============================================================

What are unit tests?
- Test ONE small piece of code in isolation
- Fast to run (no database, external APIs, etc.)
- Test a single function, method, or class

What we're testing:
- User model methods (password hashing, serialization, etc.)
- User validation (email format, required fields)
- User relationships (projects, tasks)

How to run:
- All tests: pytest
- This file only: pytest tests/unit/test_models.py
- One test: pytest tests/unit/test_models.py::TestUserModel::test_create_user
"""

import pytest
from app.models.user import User, UserRole
from datetime import datetime


# ============================================================
# USER MODEL TESTS
# ============================================================


class TestUserModel:
    """
    Test suite for User model.

    Groups related tests together.
    All methods starting with 'test_' will be run by pytest.
    """

    def test_create_user(self, db_session):
        """
        Test: Can we create a user with valid data?

        What we're checking:
        1. User object is created successfully
        2. Database saves the user
        3. User gets an ID assigned
        4. Email and full_name are stored correctly

        Fixtures used:
        - db_session: Database connection for this test

        Arrange-Act-Assert pattern:
        - Arrange: Set up test data
        - Act: Perform the action
        - Assert: Check if it worked
        """
        # ARRANGE: Set up test data
        email = "newuser@example.com"
        full_name = "New User"

        # ACT: Create and save user
        user = User(email=email, full_name=full_name, role=UserRole.MEMBER)
        user.set_password("password123")

        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)

        # ASSERT: Verify expectations
        assert user.id is not None  # Database assigned an ID
        assert user.email == email
        assert user.full_name == full_name
        assert user.role == UserRole.MEMBER
        assert user.created_at is not None
        assert isinstance(user.created_at, datetime)

    def test_password_hashing(self, db_session):
        """
        Test: Are passwords hashed (encrypted) properly?

        Security requirement:
        - Never store passwords in plain text!
        - If database is stolen, passwords are unreadable

        What we're checking:
        1. Password is hashed (not same as original)
        2. Can verify correct password
        3. Cannot verify wrong password
        """
        # ARRANGE: Create user with password
        user = User(email="test@example.com", full_name="Test User")
        password = "mysecretpassword"

        # ACT: Hash the password
        user.set_password(password)

        # ASSERT: Password is hashed
        assert user.password_hash != password  # Not stored in plain text
        assert len(user.password_hash) > 50  # Hash is long string

        # ASSERT: Can verify correct password
        assert user.check_password(password) is True

        # ASSERT: Cannot verify wrong password
        assert user.check_password("wrongpassword") is False

    def test_unique_email(self, db_session, user):
        """
        Test: Can two users have the same email?

        Answer: NO! Emails must be unique.

        What we're checking:
        - Database rejects duplicate emails
        - Raises appropriate error

        Fixtures used:
        - db_session: Database connection
        - user: Existing user (from fixture)
        """
        from sqlalchemy.exc import IntegrityError

        # ACT: Try to create user with same email
        duplicate_user = User(
            email=user.email, full_name="Different User"  # Same email as existing user!
        )

        db_session.add(duplicate_user)

        # ASSERT: Database rejects this
        with pytest.raises(IntegrityError):
            db_session.commit()

    def test_user_to_dict(self, user):
        """
        Test: Can we convert user to dictionary?

        Why needed:
        - API returns JSON (JavaScript Object Notation)
        - Need to convert User object → dictionary → JSON

        What we're checking:
        - to_dict() method works
        - Contains all expected fields
        - Password is NOT included (security!)
        """
        # ACT: Convert to dictionary (with email included)
        user_dict = user.to_dict(include_email=True)

        # ASSERT: Check structure
        assert isinstance(user_dict, dict)
        assert "id" in user_dict
        assert "email" in user_dict
        assert "full_name" in user_dict
        assert "role" in user_dict
        assert "created_at" in user_dict

        # ASSERT: Values match
        assert user_dict["email"] == user.email
        assert user_dict["full_name"] == user.full_name

        # ASSERT: Password not included (security!)
        assert "password" not in user_dict
        assert "password_hash" not in user_dict

    def test_user_repr(self, user):
        """
        Test: Does __repr__ provide useful string representation?

        Why needed:
        - When debugging, print(user) shows useful info
        - Instead of: <User object at 0x7f8b8c0d4a90>
        - Shows: <User testuser@example.com>

        What we're checking:
        - __repr__ returns string
        - Contains email (identifies the user)
        """
        # ACT: Get string representation
        repr_string = repr(user)

        # ASSERT: Check format
        assert isinstance(repr_string, str)
        assert user.email in repr_string
        assert "User" in repr_string

    @pytest.mark.parametrize(
        "role", [UserRole.ADMIN, UserRole.MANAGER, UserRole.MEMBER, UserRole.VIEWER]
    )
    def test_user_roles(self, db_session, role):
        """
        Test: Can users have different roles?

        @pytest.mark.parametrize:
        - Runs same test with different inputs
        - Instead of writing 4 separate tests
        - One test runs 4 times with different roles

        What we're checking:
        - All role types work
        - Role is stored correctly
        """
        # ARRANGE & ACT: Create user with specific role
        user = User(
            email=f"{role.value.lower()}@example.com",
            full_name=f"{role.value.title()} User",
            role=role,
        )
        user.set_password("testpass123")  # Password required

        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)

        # ASSERT: Role is set correctly
        assert user.role == role
        assert user.role.value in ["ADMIN", "MANAGER", "MEMBER", "VIEWER"]


# ============================================================
# USER RELATIONSHIPS TESTS
# ============================================================


class TestUserRelationships:
    """
    Test user relationships with other models.

    Users can:
    - Own projects
    - Be assigned tasks
    - Create tasks
    """

    def test_user_projects(self, db_session, user, project):
        """
        Test: Can we access user's projects?

        Relationship: User → Projects (one user owns many projects)

        What we're checking:
        - user.owned_projects returns query (lazy='dynamic')
        - Query contains the project
        - Count is correct
        """
        # ASSERT: User has projects (use .count() for dynamic relationships)
        assert user.owned_projects.count() > 0
        assert project in user.owned_projects.all()
        assert user.owned_projects.first().owner_id == user.id

    def test_user_tasks(self, db_session, user, task):
        """
        Test: Can we access user's assigned tasks?

        Relationship: User → Tasks (user has many assigned tasks)

        What we're checking:
        - user.assigned_tasks returns query (lazy='dynamic')
        - Query contains the task
        """
        # ASSERT: User has assigned tasks (use .count() for dynamic relationships)
        assert user.assigned_tasks.count() > 0
        assert task in user.assigned_tasks.all()
        assert user.assigned_tasks[0].assignee_id == user.id


# ============================================================
# USER VALIDATION TESTS
# ============================================================


class TestUserValidation:
    """
    Test user data validation.

    What should be rejected:
    - Invalid emails
    - Missing required fields
    - Passwords that are too short
    """

    def test_missing_email(self, db_session):
        """
        Test: What happens if email is missing?

        Expected: Database rejects it (email is required)
        """
        from sqlalchemy.exc import IntegrityError

        # ACT: Create user without email
        user = User(full_name="No Mail User")
        db_session.add(user)

        # ASSERT: Database rejects
        with pytest.raises(IntegrityError):
            db_session.commit()

    def test_missing_username(self, db_session):
        """
        Test: What happens if full_name is missing?

        Expected: Database rejects it (full_name is required)
        """
        from sqlalchemy.exc import IntegrityError

        # ACT: Create user without full_name
        user = User(email="test@example.com")
        db_session.add(user)

        # ASSERT: Database rejects
        with pytest.raises(IntegrityError):
            db_session.commit()


# ============================================================
# RUNNING THESE TESTS
# ============================================================
#
# Run all tests in this file:
#   pytest tests/unit/test_models.py -v
#
# Run specific test class:
#   pytest tests/unit/test_models.py::TestUserModel -v
#
# Run specific test:
#   pytest tests/unit/test_models.py::TestUserModel::test_create_user -v
#
# Run with coverage:
#   pytest tests/unit/test_models.py --cov=app.models.user
#
# Expected output:
#   tests/unit/test_models.py::TestUserModel::test_create_user PASSED
#   tests/unit/test_models.py::TestUserModel::test_password_hashing PASSED
#   tests/unit/test_models.py::TestUserModel::test_unique_email PASSED
#   ...
#   ======================== 10 passed in 0.45s ========================
# ============================================================
