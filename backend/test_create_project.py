"""
Test script to create a project via API
Run this to test project creation
"""

import requests
import json

BASE_URL = "http://localhost:5000/api"

# First, login to get a token
print("=" * 60)
print("STEP 1: LOGIN")
print("=" * 60)

login_data = {
    "email": "john.doe@example.com",
    "password": "SecurePass123"
}

try:
    response = requests.post(f"{BASE_URL}/auth/login", json=login_data)
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        login_result = response.json()
        token = login_result['access_token']
        print("[SUCCESS] Login successful!")
        print(f"Token: {token[:50]}...")
    else:
        print(f"[FAILED] Login failed: {response.text}")
        exit(1)
except Exception as e:
    print(f"[ERROR] Error during login: {e}")
    exit(1)

# Now try to create a project
print("\n" + "=" * 60)
print("STEP 2: CREATE PROJECT")
print("=" * 60)

project_data = {
    "name": "Test Project from Script",
    "description": "This is a test project created from the test script",
    "status": "ACTIVE",
    "color": "#3B82F6",
    "start_date": "2025-01-01",
    "end_date": "2025-12-31"
}

headers = {
    "Authorization": f"Bearer {token}",
    "Content-Type": "application/json"
}

try:
    print(f"Sending data: {json.dumps(project_data, indent=2)}")
    response = requests.post(f"{BASE_URL}/projects", json=project_data, headers=headers)
    print(f"\nStatus: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    
    if response.status_code == 201:
        print("\n[SUCCESS] Project created successfully!")
    else:
        print(f"\n[FAILED] Failed to create project")
        
except Exception as e:
    print(f"[ERROR] Error during project creation: {e}")
    print(f"Response text: {response.text if 'response' in locals() else 'No response'}")

# List projects to verify
print("\n" + "=" * 60)
print("STEP 3: LIST PROJECTS")
print("=" * 60)

try:
    response = requests.get(f"{BASE_URL}/projects", headers=headers)
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        projects = result.get('projects', [])
        print(f"\n[SUCCESS] Found {len(projects)} projects:")
        for project in projects[:5]:  # Show first 5
            print(f"  - {project['name']} (Status: {project['status']})")
    else:
        print(f"[FAILED] Failed to list projects: {response.text}")
        
except Exception as e:
    print(f"[ERROR] Error listing projects: {e}")
