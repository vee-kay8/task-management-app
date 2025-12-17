"""
============================================================
API ENDPOINT TESTING SCRIPT
============================================================

This script tests all implemented API endpoints in sequence:
1. Authentication (register, login)
2. User management
3. Project management
4. Task management

Run this while the Flask server is running:
    python test_api.py
"""

import requests
import json
from datetime import datetime, timedelta

# ============================================================
# CONFIGURATION
# ============================================================
BASE_URL = "http://localhost:5000/api"
HEADERS = {"Content-Type": "application/json"}

# Store tokens and IDs for subsequent requests
tokens = {}
ids = {}


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def print_section(title):
    """Print a section header"""
    print("\n" + "=" * 60)
    print(f"  {title}")
    print("=" * 60)


def print_test(name, success=True):
    """Print test result"""
    status = "✅ PASS" if success else "❌ FAIL"
    print(f"{status} - {name}")


def print_response(response, show_body=True):
    """Print response details"""
    print(f"   Status: {response.status_code}")
    if show_body and response.text:
        try:
            data = response.json()
            print(f"   Body: {json.dumps(data, indent=2)[:200]}...")
        except:
            print(f"   Body: {response.text[:200]}...")


def make_request(method, endpoint, data=None, token=None, params=None):
    """Make HTTP request with optional authentication"""
    url = f"{BASE_URL}{endpoint}"
    headers = HEADERS.copy()
    
    if token:
        headers["Authorization"] = f"Bearer {token}"
    
    try:
        if method == "GET":
            response = requests.get(url, headers=headers, params=params)
        elif method == "POST":
            response = requests.post(url, headers=headers, json=data)
        elif method == "PUT":
            response = requests.put(url, headers=headers, json=data)
        elif method == "DELETE":
            response = requests.delete(url, headers=headers)
        else:
            raise ValueError(f"Unsupported method: {method}")
        
        return response
    except requests.exceptions.ConnectionError:
        print("❌ ERROR: Cannot connect to server. Is it running?")
        exit(1)


# ============================================================
# TEST FUNCTIONS
# ============================================================

def test_health_check():
    """Test basic connectivity"""
    print_section("HEALTH CHECK")
    
    response = requests.get("http://localhost:5000/health")
    print_test("Health endpoint", response.status_code == 200)
    print_response(response)
    
    response = requests.get("http://localhost:5000/")
    print_test("Root endpoint", response.status_code == 200)
    print_response(response)


def test_authentication():
    """Test authentication endpoints"""
    print_section("AUTHENTICATION TESTS")
    
    # Test 1: Register new user
    user1_data = {
        "email": "john.doe@example.com",
        "password": "SecurePass123",
        "full_name": "John Doe",
        "role": "ADMIN"
    }
    
    response = make_request("POST", "/auth/register", user1_data)
    print_test("Register user 1 (admin)", response.status_code == 201)
    print_response(response)
    
    if response.status_code == 201:
        ids['user1'] = response.json()['user']['id']
    elif response.status_code == 409:
        # User already exists, login to get ID
        print("   Note: User already exists, logging in instead")
    
    # Test 2: Register another user
    user2_data = {
        "email": "jane.smith@example.com",
        "password": "SecurePass123",
        "full_name": "Jane Smith",
        "role": "MEMBER"
    }
    
    response = make_request("POST", "/auth/register", user2_data)
    print_test("Register user 2 (member)", response.status_code == 201)
    print_response(response)
    
    if response.status_code == 201:
        ids['user2'] = response.json()['user']['id']
    elif response.status_code == 409:
        # User already exists, login to get ID
        print("   Note: User already exists, logging in instead")
    
    # Test 3: Duplicate email (should fail)
    response = make_request("POST", "/auth/register", user1_data)
    print_test("Duplicate email rejected", response.status_code == 409)
    print_response(response)
    
    # Test 4: Weak password (should fail)
    weak_password_data = {
        "email": "weak@example.com",
        "password": "weak",
        "full_name": "Weak Password"
    }
    
    response = make_request("POST", "/auth/register", weak_password_data)
    print_test("Weak password rejected", response.status_code == 400)
    print_response(response)
    
    # Test 5: Login user 1
    login_data = {
        "email": "john.doe@example.com",
        "password": "SecurePass123"
    }
    
    response = make_request("POST", "/auth/login", login_data)
    print_test("Login user 1", response.status_code == 200)
    print_response(response)
    
    if response.status_code == 200:
        data = response.json()
        tokens['user1_access'] = data['access_token']
        tokens['user1_refresh'] = data['refresh_token']
        if 'user' in data:
            ids['user1'] = data['user']['id']
    
    # Test 6: Login user 2
    login_data = {
        "email": "jane.smith@example.com",
        "password": "SecurePass123"
    }
    
    response = make_request("POST", "/auth/login", login_data)
    print_test("Login user 2", response.status_code == 200)
    print_response(response)
    
    if response.status_code == 200:
        data = response.json()
        tokens['user2_access'] = data['access_token']
        if 'user' in data:
            ids['user2'] = data['user']['id']
    
    # Test 7: Get current user (/me)
    response = make_request("GET", "/auth/me", token=tokens['user1_access'])
    print_test("Get current user info", response.status_code == 200)
    print_response(response)
    
    if response.status_code == 200 and 'user1' not in ids:
        ids['user1'] = response.json()['user']['id']
    
    # Get user2 ID if not already set
    if 'user2' not in ids:
        response = make_request("GET", "/auth/me", token=tokens['user2_access'])
        if response.status_code == 200:
            ids['user2'] = response.json()['user']['id']
    
    # Test 8: Validate token
    response = make_request("GET", "/auth/validate-token", token=tokens['user1_access'])
    print_test("Validate token", response.status_code == 200)
    print_response(response)
    
    # Test 9: Access without token (should fail)
    response = make_request("GET", "/auth/me")
    print_test("Unauthorized access rejected", response.status_code == 401)
    print_response(response)


def test_user_management():
    """Test user management endpoints"""
    print_section("USER MANAGEMENT TESTS")
    
    # Test 1: List all users (admin only)
    response = make_request("GET", "/users", token=tokens['user1_access'])
    print_test("Admin list all users", response.status_code == 200)
    print_response(response)
    
    # Test 2: Non-admin list users (should fail)
    response = make_request("GET", "/users", token=tokens['user2_access'])
    print_test("Non-admin cannot list users", response.status_code == 403)
    print_response(response)
    
    # Test 3: Get own profile
    response = make_request("GET", f"/users/{ids['user2']}", token=tokens['user2_access'])
    print_test("User get own profile", response.status_code == 200)
    print_response(response)
    
    # Test 4: Update own profile
    update_data = {
        "full_name": "Jane Smith Updated",
        "current_password": "SecurePass123"
    }
    
    response = make_request("PUT", f"/users/{ids['user2']}", update_data, token=tokens['user2_access'])
    print_test("User update own profile", response.status_code == 200)
    print_response(response)
    
    # Test 5: User try to view other profile (should fail)
    response = make_request("GET", f"/users/{ids['user1']}", token=tokens['user2_access'])
    print_test("User cannot view other profile", response.status_code == 403)
    print_response(response)
    
    # Test 6: Admin view any profile
    response = make_request("GET", f"/users/{ids['user2']}", token=tokens['user1_access'])
    print_test("Admin view any profile", response.status_code == 200)
    print_response(response)


def test_project_management():
    """Test project management endpoints"""
    print_section("PROJECT MANAGEMENT TESTS")
    
    # Test 1: Create project
    project_data = {
        "name": "Website Redesign",
        "description": "Redesign company website with modern UI",
        "status": "ACTIVE",
        "start_date": "2024-12-01",
        "end_date": "2025-03-31"
    }
    
    response = make_request("POST", "/projects", project_data, token=tokens['user1_access'])
    print_test("Create project", response.status_code == 201)
    print_response(response)
    
    if response.status_code == 201:
        ids['project1'] = response.json()['project']['id']
    
    # Test 2: List user's projects
    response = make_request("GET", "/projects", token=tokens['user1_access'])
    print_test("List user projects", response.status_code == 200)
    print_response(response)
    
    # Test 3: Get project details
    response = make_request("GET", f"/projects/{ids['project1']}", token=tokens['user1_access'])
    print_test("Get project details", response.status_code == 200)
    print_response(response)
    
    # Test 4: Update project
    update_data = {
        "name": "Website Redesign v2",
        "status": "ACTIVE"
    }
    
    response = make_request("PUT", f"/projects/{ids['project1']}", update_data, token=tokens['user1_access'])
    print_test("Update project", response.status_code == 200)
    print_response(response)
    
    # Test 5: Add team member
    member_data = {
        "user_id": ids['user2'],
        "role": "MEMBER"
    }
    
    response = make_request("POST", f"/projects/{ids['project1']}/members", member_data, token=tokens['user1_access'])
    print_test("Add team member", response.status_code == 201)
    print_response(response)
    
    # Test 6: User2 now has access to project
    response = make_request("GET", f"/projects/{ids['project1']}", token=tokens['user2_access'])
    print_test("Member access project", response.status_code == 200)
    print_response(response)
    
    # Test 7: Filter projects by status
    response = make_request("GET", "/projects", token=tokens['user1_access'], params={"status": "ACTIVE"})
    print_test("Filter projects by status", response.status_code == 200)
    print_response(response)


def test_task_management():
    """Test task management endpoints"""
    print_section("TASK MANAGEMENT TESTS")
    
    # Test 1: Create task
    task_data = {
        "project_id": ids['project1'],
        "title": "Design homepage mockup",
        "description": "Create initial mockup for new homepage design",
        "status": "TODO",
        "priority": "HIGH",
        "assigned_to_id": ids['user2'],
        "due_date": "2024-12-31",
        "tags": ["design", "frontend", "urgent"]
    }
    
    response = make_request("POST", "/tasks", task_data, token=tokens['user1_access'])
    print_test("Create task", response.status_code == 201)
    print_response(response)
    
    if response.status_code == 201:
        ids['task1'] = response.json()['task']['id']
    
    # Test 2: Create another task
    task2_data = {
        "project_id": ids['project1'],
        "title": "Setup development environment",
        "description": "Configure dev environment with all dependencies",
        "status": "IN_PROGRESS",
        "priority": "MEDIUM",
        "assigned_to_id": ids['user1'],
        "due_date": "2024-12-25",
        "tags": ["backend", "setup"]
    }
    
    response = make_request("POST", "/tasks", task2_data, token=tokens['user1_access'])
    print_test("Create another task", response.status_code == 201)
    print_response(response)
    
    if response.status_code == 201:
        ids['task2'] = response.json()['task']['id']
    
    # Test 3: List tasks for project
    response = make_request("GET", "/tasks", token=tokens['user1_access'], params={"project_id": ids['project1']})
    print_test("List project tasks", response.status_code == 200)
    print_response(response)
    
    # Test 4: Filter tasks by status
    response = make_request("GET", "/tasks", token=tokens['user1_access'], 
                          params={"project_id": ids['project1'], "status": "TODO"})
    print_test("Filter tasks by status", response.status_code == 200)
    print_response(response)
    
    # Test 5: Filter tasks by assignee
    response = make_request("GET", "/tasks", token=tokens['user1_access'], 
                          params={"project_id": ids['project1'], "assigned_to": ids['user2']})
    print_test("Filter tasks by assignee", response.status_code == 200)
    print_response(response)
    
    # Test 6: Get task details
    response = make_request("GET", f"/tasks/{ids['task1']}", token=tokens['user1_access'])
    print_test("Get task details", response.status_code == 200)
    print_response(response)
    
    # Test 7: Update task
    update_data = {
        "status": "IN_PROGRESS",
        "priority": "URGENT"
    }
    
    response = make_request("PUT", f"/tasks/{ids['task1']}", update_data, token=tokens['user1_access'])
    print_test("Update task", response.status_code == 200)
    print_response(response)
    
    # Test 8: Add comment to task
    comment_data = {
        "content": "Started working on the mockup. Will share initial version tomorrow."
    }
    
    response = make_request("POST", f"/tasks/{ids['task1']}/comments", comment_data, token=tokens['user2_access'])
    print_test("Add comment to task", response.status_code == 201)
    print_response(response)
    
    if response.status_code == 201:
        ids['comment1'] = response.json()['comment']['id']
    
    # Test 9: Add reply to comment (threaded)
    reply_data = {
        "content": "Great! Looking forward to seeing it.",
        "parent_id": ids['comment1']
    }
    
    response = make_request("POST", f"/tasks/{ids['task1']}/comments", reply_data, token=tokens['user1_access'])
    print_test("Add threaded reply", response.status_code == 201)
    print_response(response)
    
    # Test 10: Get task with comments
    response = make_request("GET", f"/tasks/{ids['task1']}", token=tokens['user1_access'])
    print_test("Get task with comments", response.status_code == 200)
    print_response(response)
    
    # Test 11: Search tasks
    response = make_request("GET", "/tasks", token=tokens['user1_access'], 
                          params={"project_id": ids['project1'], "search": "mockup"})
    print_test("Search tasks", response.status_code == 200)
    print_response(response)


def test_error_handling():
    """Test error handling"""
    print_section("ERROR HANDLING TESTS")
    
    # Test 1: Invalid endpoint (404)
    response = make_request("GET", "/invalid-endpoint", token=tokens['user1_access'])
    print_test("404 error handling", response.status_code == 404)
    print_response(response)
    
    # Test 2: Invalid token (401)
    response = make_request("GET", "/auth/me", token="invalid-token-12345")
    print_test("Invalid token handling", response.status_code == 401)
    print_response(response)
    
    # Test 3: Missing required field (400)
    invalid_data = {"title": ""}  # Missing project_id
    response = make_request("POST", "/tasks", invalid_data, token=tokens['user1_access'])
    print_test("Validation error handling", response.status_code == 400)
    print_response(response)
    
    # Test 4: Access forbidden resource (403)
    response = make_request("DELETE", f"/users/{ids['user1']}", token=tokens['user2_access'])
    print_test("Forbidden access handling", response.status_code == 403)
    print_response(response)


# ============================================================
# MAIN EXECUTION
# ============================================================

def main():
    """Run all tests"""
    print("\n" + "=" * 60)
    print("  TASK MANAGEMENT API - ENDPOINT TESTING")
    print("=" * 60)
    print(f"  Base URL: {BASE_URL}")
    print(f"  Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    try:
        test_health_check()
        test_authentication()
        test_user_management()
        test_project_management()
        test_task_management()
        test_error_handling()
        
        print("\n" + "=" * 60)
        print("  ✅ ALL TESTS COMPLETED")
        print("=" * 60)
        print("\n📊 Test Summary:")
        print(f"   Registered Users: {len([k for k in ids if 'user' in k])}")
        print(f"   Created Projects: {len([k for k in ids if 'project' in k])}")
        print(f"   Created Tasks: {len([k for k in ids if 'task' in k])}")
        print(f"   Access Tokens: {len([k for k in tokens if 'access' in k])}")
        print("\n💡 Tip: Check the database to see all created records!")
        print("   psql $DATABASE_URL -c 'SELECT * FROM users;'")
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Tests interrupted by user")
    except Exception as e:
        print(f"\n\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
