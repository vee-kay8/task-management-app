# Phase 1: Project Setup & Testing Infrastructure

## 📋 Overview
This phase establishes the foundation for CI/CD by setting up automated testing and code quality tools. Before we can automate anything in GitHub Actions, we need to make sure our tests work locally.

**Duration:** 1-2 hours  
**Difficulty:** Beginner-friendly

---

## 🎯 Goals
By the end of this phase, you will:
1. ✅ Have automated tests for your backend (Python/Flask)
2. ✅ Have automated tests for your frontend (Next.js/React)
3. ✅ Have code linting to maintain clean, consistent code
4. ✅ Be able to run all tests with a single command
5. ✅ Understand what each tool does and why we need it

---

## 🛠️ What We're Installing

### Backend Testing Tools
| Tool | Purpose | Example |
|------|---------|---------|
| **pytest** | Python test framework | Runs your test functions automatically |
| **pytest-cov** | Code coverage | Shows which code is tested (aim for 80%+) |
| **pytest-flask** | Flask testing helpers | Makes testing Flask routes easier |
| **flake8** | Python linter | Catches style issues (unused imports, etc.) |
| **black** | Python formatter | Auto-formats code to look consistent |

### Frontend Testing Tools
| Tool | Purpose | Example |
|------|---------|---------|
| **Jest** | JavaScript test framework | Runs your test files |
| **@testing-library/react** | React testing | Tests components from user's perspective |
| **@testing-library/jest-dom** | Jest matchers | Adds helpful assertions like `toBeInTheDocument()` |
| **eslint** | JavaScript linter | Already installed, we'll configure it better |
| **prettier** | Code formatter | Auto-formats JavaScript/TypeScript |

---

## 📦 Installation Steps

### Step 1: Backend Dependencies
We'll add testing tools to your `requirements.txt`:

```bash
# Navigate to backend folder
cd backend

# Install new packages
pip install pytest pytest-cov pytest-flask flake8 black
```

**What happens:** These packages get installed in your Python environment and will be available when running tests.

---

### Step 2: Frontend Dependencies
We'll add testing tools to your `package.json`:

```bash
# Navigate to frontend folder
cd ../frontend

# Install testing libraries
npm install --save-dev jest @testing-library/react @testing-library/jest-dom @testing-library/user-event jest-environment-jsdom prettier eslint-config-prettier
```

**What happens:** NPM downloads these packages into `node_modules/` folder.

---

## 📁 File Structure (What We're Creating)

```
task-management-app/
├── backend/
│   ├── pytest.ini                    # ← NEW: Pytest configuration
│   ├── .flake8                       # ← NEW: Flake8 rules
│   ├── requirements.txt              # ← UPDATED: Added test dependencies
│   └── tests/
│       ├── __init__.py              # Makes tests a package
│       ├── conftest.py              # ← NEW: Shared test fixtures
│       └── unit/
│           ├── __init__.py
│           └── test_models.py       # ← NEW: Sample tests
│
└── frontend/
    ├── jest.config.js               # ← NEW: Jest configuration
    ├── jest.setup.js                # ← NEW: Test environment setup
    ├── .prettierrc                  # ← NEW: Prettier rules
    ├── package.json                 # ← UPDATED: Added test scripts
    └── __tests__/
        └── components/
            └── TaskBoard.test.tsx   # ← NEW: Sample component test
```

---

## 🔍 Understanding Each Configuration File

### `pytest.ini` - Backend Test Configuration
```ini
[pytest]
# Where pytest should look for tests
testpaths = tests

# Pattern for test files (must start with "test_")
python_files = test_*.py

# Pattern for test functions
python_functions = test_*

# Show detailed output
addopts = 
    -v                          # Verbose (show each test name)
    --cov=app                   # Measure code coverage for "app" folder
    --cov-report=term-missing   # Show which lines aren't tested
    --cov-report=html           # Generate HTML coverage report
```

**Why we need this:** Tells pytest how to find and run your tests.

---

### `.flake8` - Python Linting Rules
```ini
[flake8]
# Maximum line length (default is 79, we use 100 for modern screens)
max-line-length = 100

# Folders to ignore
exclude = 
    .git,
    __pycache__,
    migrations,
    venv,
    env

# Error codes to ignore
ignore = 
    E203,  # Whitespace before ':' (conflicts with black)
    W503   # Line break before binary operator (old style)
```

**Why we need this:** Keeps your Python code clean and catches common mistakes.

---

### `jest.config.js` - Frontend Test Configuration
```javascript
const nextJest = require('next/jest')

// Load Next.js configuration for Jest
const createJestConfig = nextJest({
  dir: './',  // Path to Next.js app
})

const customJestConfig = {
  // Setup file runs before each test
  setupFilesAfterEnv: ['<rootDir>/jest.setup.js'],
  
  // Test environment (jsdom simulates a browser)
  testEnvironment: 'jest-environment-jsdom',
  
  // Where to find tests
  testMatch: [
    '**/__tests__/**/*.[jt]s?(x)',
    '**/?(*.)+(spec|test).[jt]s?(x)'
  ],
  
  // Coverage configuration
  collectCoverageFrom: [
    'app/**/*.{js,jsx,ts,tsx}',
    'components/**/*.{js,jsx,ts,tsx}',
    '!**/*.d.ts',
    '!**/node_modules/**',
  ],
}

module.exports = createJestConfig(customJestConfig)
```

**Why we need this:** Configures Jest to work with Next.js and TypeScript.

---

## 🧪 Sample Tests Explained

### Backend Test Example: `test_models.py`
```python
"""
Unit tests for database models.
These tests verify that our User, Project, and Task models work correctly.
"""
import pytest
from app.models.user import User
from app.models.project import Project

class TestUserModel:
    """Test suite for User model"""
    
    def test_user_creation(self):
        """
        Test that we can create a user with valid data.
        
        What we're testing:
        1. User object is created successfully
        2. Password gets hashed (not stored in plain text)
        3. Email is stored correctly
        """
        # Arrange: Set up test data
        email = "test@example.com"
        password = "securepassword123"
        
        # Act: Create a user
        user = User(email=email, username="testuser")
        user.set_password(password)
        
        # Assert: Verify expectations
        assert user.email == email
        assert user.password_hash != password  # Password should be hashed
        assert user.check_password(password) is True  # Can verify password
        assert user.check_password("wrongpassword") is False
```

**Key Concepts:**
- **Arrange-Act-Assert:** Standard test structure
- **Unit test:** Tests one small piece (User model) in isolation
- **assert:** Checks if something is true, test fails if not

---

### Frontend Test Example: `TaskBoard.test.tsx`
```typescript
/**
 * Unit tests for TaskBoard component.
 * Tests that the component renders correctly and handles user interactions.
 */
import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import TaskBoard from '@/components/TaskBoard'

// Mock data for testing
const mockTasks = [
  {
    id: 1,
    title: 'Test Task',
    description: 'Test Description',
    status: 'todo',
    priority: 'high'
  }
]

describe('TaskBoard Component', () => {
  it('renders task board with columns', () => {
    // Render the component
    render(<TaskBoard tasks={mockTasks} />)
    
    // Check if "To Do" column exists
    expect(screen.getByText('To Do')).toBeInTheDocument()
    expect(screen.getByText('In Progress')).toBeInTheDocument()
    expect(screen.getByText('Done')).toBeInTheDocument()
  })
  
  it('displays tasks in correct column', () => {
    render(<TaskBoard tasks={mockTasks} />)
    
    // Check if our test task appears
    expect(screen.getByText('Test Task')).toBeInTheDocument()
  })
})
```

**Key Concepts:**
- **render():** Mounts the component in a test environment
- **screen.getByText():** Finds elements by their text content
- **expect():** Makes an assertion about what should be true
- **Mock data:** Fake data used for testing (not real database)

---

## 🏃 Running Tests

### Backend Tests
```bash
# Run all tests
cd backend
pytest

# Run with coverage report
pytest --cov=app --cov-report=term-missing

# Run specific test file
pytest tests/unit/test_models.py

# Run specific test function
pytest tests/unit/test_models.py::TestUserModel::test_user_creation
```

**Expected Output:**
```
======================== test session starts ========================
tests/unit/test_models.py::TestUserModel::test_user_creation PASSED

----------- coverage: platform win32, python 3.11.0 -----------
Name                    Stmts   Miss  Cover   Missing
-----------------------------------------------------
app/models/user.py        45      2    95%    23, 67
-----------------------------------------------------
TOTAL                     45      2    95%

======================== 1 passed in 0.23s ==========================
```

---

### Frontend Tests
```bash
# Run all tests
cd frontend
npm test

# Run with coverage
npm test -- --coverage

# Run in watch mode (re-runs on file changes)
npm test -- --watch
```

**Expected Output:**
```
 PASS  __tests__/components/TaskBoard.test.tsx
  TaskBoard Component
    ✓ renders task board with columns (45ms)
    ✓ displays tasks in correct column (12ms)

Test Suites: 1 passed, 1 total
Tests:       2 passed, 2 total
Time:        2.341s
```

---

## ✨ Code Formatting

### Format Backend Code
```bash
cd backend

# Check what would be formatted
black --check .

# Auto-format all Python files
black .

# Check linting issues
flake8
```

---

### Format Frontend Code
```bash
cd frontend

# Check what would be formatted
npx prettier --check .

# Auto-format all files
npx prettier --write .

# Run ESLint
npm run lint
```

---

## ✅ Verification Checklist

Before moving to Phase 2, verify:

- [ ] Backend tests run successfully: `cd backend && pytest`
- [ ] Frontend tests run successfully: `cd frontend && npm test`
- [ ] Code coverage is generated (HTML report in `backend/htmlcov/`)
- [ ] Black formats Python code: `cd backend && black .`
- [ ] Flake8 shows no errors: `cd backend && flake8`
- [ ] Prettier formats frontend code: `cd frontend && npx prettier --write .`
- [ ] All commands complete without errors

---

## 🤔 Common Issues & Solutions

### Issue: "pytest: command not found"
**Solution:** Make sure you're in the correct Python environment and pytest is installed:
```bash
pip install pytest
```

---

### Issue: "Cannot find module 'jest'"
**Solution:** Install frontend dependencies:
```bash
cd frontend
npm install
```

---

### Issue: Tests fail with "No module named 'app'"
**Solution:** Make sure you're running pytest from the `backend/` directory, not the root.

---

## 📚 What You've Learned

1. **Testing frameworks:** pytest (Python) and Jest (JavaScript)
2. **Code coverage:** Measuring how much of your code is tested
3. **Linting:** Automatically checking code for style and errors
4. **Formatting:** Automatically making code look consistent
5. **Unit tests:** Testing individual pieces of code in isolation

---

## ➡️ Next Steps

Once you've verified everything works:
1. ✅ All tests pass
2. ✅ Code can be formatted automatically
3. ✅ You understand what each tool does

**You're ready for Phase 2!** 🚀

In Phase 2, we'll create a GitHub Actions workflow that automatically runs these tests every time you push code.

---

## 💡 Pro Tips

1. **Write tests as you code:** Don't wait until the end
2. **Aim for 80%+ coverage:** But don't obsess over 100%
3. **Test behavior, not implementation:** Test what users care about
4. **Keep tests fast:** Slow tests won't get run
5. **Use descriptive test names:** `test_user_login_with_invalid_password` is better than `test_login2`

---

## 📞 Need Help?

Review this document carefully. Each section explains:
- **What** we're doing
- **Why** we're doing it
- **How** to do it
- **What** the expected result looks like

Take your time to understand each concept before moving forward!
