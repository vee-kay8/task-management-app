# 🚀 Phase 1 Quick Start Guide

## Installation & Verification Steps

Follow these steps in order to set up and verify your testing infrastructure.

---

## Part 1: Backend Setup (Python/Flask)

### Step 1: Navigate to Backend Directory
```bash
cd backend
```

### Step 2: Install Dependencies
```bash
# Windows
python -m pip install -r requirements.txt

# macOS/Linux
pip3 install -r requirements.txt
```

**Expected Output:**
```
Successfully installed pytest-7.4.3 pytest-flask-1.3.0 pytest-cov-4.1.0 ...
```

**Common Issues:**
- ❌ "pip: command not found" → Use `python -m pip install -r requirements.txt`
- ❌ Permission denied → Use `python -m pip install --user -r requirements.txt`

---

### Step 3: Verify Pytest Installation
```bash
# Windows
python -m pytest --version

# macOS/Linux
pytest --version
```

**Expected Output:**
```
pytest 7.4.3
```

---

### Step 4: Run Tests
```bash
# Windows
python -m pytest

# macOS/Linux
pytest
```

**Expected Output:**
```
======================== test session starts ========================
collected 10 items

tests/unit/test_models.py::TestUserModel::test_create_user PASSED
tests/unit/test_models.py::TestUserModel::test_password_hashing PASSED
tests/unit/test_models.py::TestUserModel::test_unique_email PASSED
...

----------- coverage: platform win32, python 3.11 -----------
Name                    Stmts   Miss  Cover   Missing
-----------------------------------------------------
app/models/user.py        45      2    95%    23, 67
-----------------------------------------------------

======================== 10 passed in 0.45s ==========================
```

**What if tests fail?**
- Check database configuration in `app/config.py`
- Ensure PostgreSQL is running (if using real database)
- Check error message for specific issue

---

### Step 5: Check Code with Flake8
```bash
# Windows
python -m flake8

# macOS/Linux
flake8
```

**Expected Output:**
```
(No output means no errors - perfect!)
```

**If you see errors:**
```
app/models/user.py:45:80: E501 line too long (85 > 79 characters)
```
This tells you exactly where to fix the issue.

---

### Step 6: Format Code with Black
```bash
# Windows - Check what would be formatted (dry run)
python -m black --check .

# Windows - Actually format the code
python -m black .

# macOS/Linux
black --check .  # dry run
black .          # format
```

**Expected Output:**
```
All done! ✨ 🍰 ✨
15 files left unchanged.
```

---

### Step 7: Generate Coverage Report
```bash
# Windows
python -m pytest --cov=app --cov-report=html

# macOS/Linux
pytest --cov=app --cov-report=html
```

**Expected Output:**
```
Wrote HTML report to htmlcov/index.html
```

**View the report:**
1. Open `backend/htmlcov/index.html` in your browser
2. See which lines are tested (green) vs not tested (red)
3. Click on filenames to see line-by-line coverage

---

## Part 2: Frontend Setup (Next.js/React)

### Step 1: Navigate to Frontend Directory
```bash
cd ../frontend
```

### Step 2: Install Dependencies
```bash
npm install
```

**Expected Output:**
```
added 324 packages in 45s
```

**This installs:**
- Jest (testing framework)
- Testing Library (React testing utilities)
- Prettier (code formatter)
- All other dependencies

---

### Step 3: Verify Jest Installation
```bash
npm test -- --version
```

**Expected Output:**
```
29.7.0
```

---

### Step 4: Run Tests
```bash
npm test
```

**Expected Output:**
```
 PASS  __tests__/components/TaskBoard.test.tsx
  TaskBoard Component
    ✓ renders without crashing (45ms)
    ✓ displays all four status columns (23ms)
    ✓ displays tasks in correct status columns (18ms)
    ✓ shows correct task count for each column (15ms)
    ✓ handles empty task list (12ms)
  TaskBoard Interactions
    ✓ calls onTaskClick when task is clicked (34ms)
    ✓ can click multiple tasks (28ms)

Test Suites: 1 passed, 1 total
Tests:       7 passed, 7 total
Snapshots:   0 total
Time:        2.341 s
```

**What if tests fail?**
- Check that all dependencies installed: `npm install`
- Clear Jest cache: `npm test -- --clearCache`
- Check for TypeScript errors: `npm run build`

---

### Step 5: Run Tests with Coverage
```bash
npm test -- --coverage
```

**Expected Output:**
```
----------------------|---------|----------|---------|---------|
File                  | % Stmts | % Branch | % Funcs | % Lines |
----------------------|---------|----------|---------|---------|
All files             |   78.12 |    62.50 |   75.00 |   78.12 |
 TaskBoard.tsx        |   85.71 |    70.00 |   80.00 |   85.71 |
----------------------|---------|----------|---------|---------|
```

**Coverage meanings:**
- **Stmts (Statements):** % of code statements executed
- **Branch:** % of if/else branches taken
- **Funcs (Functions):** % of functions called
- **Lines:** % of lines executed

**Good coverage:** 70-80%+

---

### Step 6: Format Code with Prettier
```bash
# Check formatting
npx prettier --check .

# Fix formatting
npx prettier --write .
```

**Expected Output:**
```
Checking formatting...
All matched files use Prettier code style!
```

---

### Step 7: Run ESLint
```bash
npm run lint
```

**Expected Output:**
```
✔ No ESLint warnings or errors
```

---

## Part 3: Verification Checklist

Before moving to Phase 2, verify everything works:

### Backend ✅
- [ ] `pytest` runs successfully with all tests passing
- [ ] `flake8` shows no errors (or only acceptable warnings)
- [ ] `black .` formats code consistently
- [ ] Coverage report generated at `backend/htmlcov/index.html`
- [ ] Coverage is at least 70%

### Frontend ✅
- [ ] `npm test` runs successfully with all tests passing
- [ ] `npm run lint` shows no errors
- [ ] `npx prettier --check .` shows files are formatted
- [ ] Coverage report shows at least 70% coverage
- [ ] You can see test results in terminal

### Understanding ✅
- [ ] I know what pytest does (runs Python tests)
- [ ] I know what Jest does (runs JavaScript tests)
- [ ] I know what flake8 does (checks Python code quality)
- [ ] I know what Prettier does (formats code)
- [ ] I know what code coverage means (% of code tested)
- [ ] I can run tests for a specific file
- [ ] I can read test output and understand pass/fail

---

## Part 4: Common Commands Reference

### Backend Commands
```bash
# Run all tests
pytest

# Run specific file
pytest tests/unit/test_models.py

# Run specific test
pytest tests/unit/test_models.py::TestUserModel::test_create_user

# Run with verbose output
pytest -v

# Run with coverage
pytest --cov=app

# Check code quality
flake8

# Format code
black .

# Check formatting without changing
black --check .
```

### Frontend Commands
```bash
# Run all tests
npm test

# Run in watch mode (re-runs on changes)
npm test -- --watch

# Run with coverage
npm test -- --coverage

# Run specific file
npm test -- TaskBoard.test.tsx

# Check formatting
npx prettier --check .

# Fix formatting
npx prettier --write .

# Lint code
npm run lint

# Fix linting issues
npm run lint -- --fix
```

---

## Part 5: What Each File Does

### Backend Files Created
| File | Purpose |
|------|---------|
| `backend/pytest.ini` | Configures how pytest finds and runs tests |
| `backend/.flake8` | Configures code quality rules |
| `backend/requirements.txt` | ✏️ Updated with test dependencies |
| `backend/tests/conftest.py` | Shared test fixtures (reusable test data) |
| `backend/tests/unit/test_models.py` | Sample tests for User model |
| `backend/htmlcov/` | Coverage report (after running tests) |

### Frontend Files Created
| File | Purpose |
|------|---------|
| `frontend/jest.config.js` | Configures Jest testing framework |
| `frontend/jest.setup.js` | Runs before tests (sets up environment) |
| `frontend/.prettierrc` | Configures code formatting rules |
| `frontend/package.json` | ✏️ Updated with test scripts |
| `frontend/__tests__/components/TaskBoard.test.tsx` | Sample component test |

---

## Part 6: Troubleshooting

### Backend Issues

**Issue: Tests fail with "No module named 'app'"**
```bash
# Solution: Make sure you're in backend/ directory
cd backend
pytest
```

**Issue: "pytest: command not found"**
```bash
# Solution: Install pytest
pip install pytest
```

**Issue: Database errors in tests**
```bash
# Solution: Check if you have a test database configured
# In app/config.py, should have TestingConfig with test database
```

**Issue: Import errors**
```bash
# Solution: Make sure __init__.py files exist
touch tests/__init__.py
touch tests/unit/__init__.py
```

---

### Frontend Issues

**Issue: "Cannot find module 'jest'"**
```bash
# Solution: Install dependencies
npm install
```

**Issue: Tests fail with "ReferenceError: fetch is not defined"**
```bash
# Solution: Add fetch polyfill to jest.setup.js
# Already included in our setup
```

**Issue: "SyntaxError: Unexpected token 'export'"**
```bash
# Solution: Clear Jest cache
npm test -- --clearCache
```

**Issue: TypeScript errors**
```bash
# Solution: Check tsconfig.json and ensure types are installed
npm install --save-dev @types/jest @types/testing-library__jest-dom
```

---

## Part 7: Understanding Test Output

### Pytest Output Explained
```
tests/unit/test_models.py::TestUserModel::test_create_user PASSED [10%]
     ↑                      ↑               ↑                  ↑      ↑
     File path          Test class    Test function        Result  Progress
```

### Jest Output Explained
```
 PASS  __tests__/components/TaskBoard.test.tsx
   ↑         ↑
  Status   File path

  TaskBoard Component
    ✓ renders without crashing (45ms)
      ↑                          ↑
   Passed                    Time taken
```

### Coverage Output Explained
```
Name                    Stmts   Miss  Cover   Missing
app/models/user.py        45      2    95%    23, 67
     ↑                    ↑       ↑     ↑       ↑
  File name          Total    Not    %      Line numbers
                   statements tested covered  not covered
```

---

## ✅ Ready for Phase 2?

If you've completed all verification steps and understand:
- ✅ How to run tests (backend and frontend)
- ✅ How to read test output
- ✅ What code coverage means
- ✅ How to format and lint code
- ✅ What each configuration file does

**You're ready for Phase 2: GitHub Actions CI!** 🎉

In Phase 2, we'll automate all these commands to run automatically on GitHub whenever you push code.

---

## 📞 Need Help?

Review the detailed explanations in:
- [CICD_PHASE_1.md](CICD_PHASE_1.md) - Complete phase documentation
- `backend/pytest.ini` - Pytest configuration (heavily commented)
- `backend/.flake8` - Flake8 configuration (heavily commented)
- `frontend/jest.config.js` - Jest configuration (heavily commented)
- `frontend/jest.setup.js` - Test setup (heavily commented)

All configuration files have extensive comments explaining every setting!
