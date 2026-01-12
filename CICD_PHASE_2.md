# Phase 2: GitHub Actions CI (Continuous Integration)

## 📋 Overview
Now that we have tests working locally (Phase 1), Phase 2 automates them to run on GitHub every time you push code. This ensures code quality is checked automatically before merging.

**Duration:** 1-2 hours  
**Difficulty:** Beginner-friendly  
**Prerequisites:** Phase 1 complete

---

## 🎯 Goals
By the end of this phase, you will:
1. ✅ Have GitHub Actions automatically run tests on every push
2. ✅ Run tests on every pull request
3. ✅ Check code quality (linting) automatically
4. ✅ Display build status badges in your README
5. ✅ Prevent merging broken code
6. ✅ Understand how CI/CD pipelines work

---

## 🤔 What is GitHub Actions?

### The Problem
Right now, you have to remember to:
- Run `pytest` before committing backend changes
- Run `npm test` before committing frontend changes
- Run linters manually
- Hope everyone on your team does the same

**What if you forget?** Broken code gets merged! 😱

### The Solution: Automation
GitHub Actions is like having a robot that:
1. Watches your repository 24/7
2. When you push code, it automatically:
   - Downloads your code
   - Sets up the environment
   - Runs all tests
   - Runs all linters
   - Reports success/failure
3. Stops you from merging if tests fail

---

## 🏗️ Architecture: How It Works

```
┌─────────────────────────────────────────────────────────────┐
│  Developer Workflow                                         │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  1. You write code locally                                 │
│     ↓                                                       │
│  2. git add . && git commit -m "Add feature"               │
│     ↓                                                       │
│  3. git push origin your-branch                            │
│     ↓                                                       │
│  ┌──────────────────────────────────────────┐             │
│  │  🤖 GitHub Actions (Automated)           │             │
│  ├──────────────────────────────────────────┤             │
│  │  4. Detects push event                   │             │
│  │  5. Starts workflow runner (Ubuntu VM)   │             │
│  │  6. Checks out your code                 │             │
│  │  7. Sets up Python 3.11                  │             │
│  │  8. Installs backend dependencies        │             │
│  │  9. Runs pytest                          │  ← Backend  │
│  │ 10. Runs flake8                          │             │
│  │ 11. Sets up Node.js 18                   │             │
│  │ 12. Installs frontend dependencies       │             │
│  │ 13. Runs npm test                        │  ← Frontend │
│  │ 14. Runs npm run lint                    │             │
│  │ 15. Reports ✅ Success or ❌ Failure     │             │
│  └──────────────────────────────────────────┘             │
│     ↓                                                       │
│  16. You see results in GitHub UI                         │
│  17. Green checkmark = Safe to merge ✅                   │
│      Red X = Fix the issues ❌                            │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## 📦 What We're Creating

### File Structure
```
task-management-app/
├── .github/                          # ← NEW: GitHub configuration folder
│   └── workflows/                    # ← NEW: CI/CD workflow definitions
│       └── ci.yml                    # ← NEW: Main CI workflow
│
├── README.md                         # ← UPDATED: Add status badges
├── CICD_PHASE_2.md                  # ← NEW: This documentation
└── PHASE_2_COMPLETE.md              # ← NEW: Summary when done
```

---

## 🔧 Step-by-Step Implementation

### Step 1: Create Workflow Directory

First, we need to create the `.github/workflows` directory:

```bash
# From project root
mkdir -p .github/workflows
```

**What this does:** 
- `.github/` is a special folder GitHub looks for
- `workflows/` contains YAML files that define automated workflows
- GitHub automatically detects and runs these workflows

---

### Step 2: Create CI Workflow File

Create `.github/workflows/ci.yml`:

```yaml
name: CI Pipeline

# When to run this workflow
on:
  push:
    branches: [ main, develop, CICD ]  # Run on pushes to these branches
  pull_request:
    branches: [ main, develop ]        # Run on PRs to these branches

# Define the jobs to run
jobs:
  # Job 1: Backend Testing
  backend-tests:
    name: Backend Tests & Linting
    runs-on: ubuntu-latest  # Use Ubuntu virtual machine
    
    steps:
      # Step 1: Get the code
      - name: Checkout code
        uses: actions/checkout@v4
      
      # Step 2: Set up Python
      - name: Set up Python 3.11
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      
      # Step 3: Cache dependencies (faster builds)
      - name: Cache Python dependencies
        uses: actions/cache@v3
        with:
          path: ~/.cache/pip
          key: ${{ runner.os }}-pip-${{ hashFiles('backend/requirements.txt') }}
          restore-keys: |
            ${{ runner.os }}-pip-
      
      # Step 4: Install dependencies
      - name: Install dependencies
        working-directory: ./backend
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements.txt
          pip install pytest pytest-cov flake8 black
      
      # Step 5: Run linting
      - name: Lint with flake8
        working-directory: ./backend
        run: |
          # Stop the build if there are Python syntax errors or undefined names
          flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics
          # Exit-zero treats all errors as warnings
          flake8 . --count --exit-zero --max-complexity=10 --max-line-length=100 --statistics
      
      # Step 6: Check code formatting
      - name: Check code formatting with black
        working-directory: ./backend
        run: |
          black --check .
      
      # Step 7: Run tests
      - name: Run tests with pytest
        working-directory: ./backend
        run: |
          pytest --cov=app --cov-report=xml --cov-report=term-missing
      
      # Step 8: Upload coverage report
      - name: Upload coverage to Codecov
        uses: codecov/codecov-action@v3
        with:
          file: ./backend/coverage.xml
          flags: backend
          name: backend-coverage
          fail_ci_if_error: false

  # Job 2: Frontend Testing
  frontend-tests:
    name: Frontend Tests & Linting
    runs-on: ubuntu-latest
    
    steps:
      # Step 1: Get the code
      - name: Checkout code
        uses: actions/checkout@v4
      
      # Step 2: Set up Node.js
      - name: Set up Node.js 18
        uses: actions/setup-node@v4
        with:
          node-version: '18'
          cache: 'npm'
          cache-dependency-path: frontend/package-lock.json
      
      # Step 3: Install dependencies
      - name: Install dependencies
        working-directory: ./frontend
        run: npm ci  # Use 'ci' for faster, deterministic installs
      
      # Step 4: Run linting
      - name: Lint with ESLint
        working-directory: ./frontend
        run: npm run lint
      
      # Step 5: Check code formatting
      - name: Check formatting with Prettier
        working-directory: ./frontend
        run: npx prettier --check .
      
      # Step 6: Run tests
      - name: Run tests with Jest
        working-directory: ./frontend
        run: npm test -- --coverage --passWithNoTests
      
      # Step 7: Upload coverage report
      - name: Upload coverage to Codecov
        uses: codecov/codecov-action@v3
        with:
          file: ./frontend/coverage/coverage-final.json
          flags: frontend
          name: frontend-coverage
          fail_ci_if_error: false

  # Job 3: Build Check (ensures code compiles)
  build-check:
    name: Build Check
    runs-on: ubuntu-latest
    needs: [backend-tests, frontend-tests]  # Only run if tests pass
    
    steps:
      - name: Checkout code
        uses: actions/checkout@v4
      
      - name: Set up Node.js
        uses: actions/setup-node@v4
        with:
          node-version: '18'
          cache: 'npm'
          cache-dependency-path: frontend/package-lock.json
      
      - name: Install frontend dependencies
        working-directory: ./frontend
        run: npm ci
      
      - name: Build frontend
        working-directory: ./frontend
        run: npm run build
      
      - name: Check build size
        working-directory: ./frontend
        run: |
          echo "Build completed successfully!"
          du -sh .next
```

---

## 📖 Understanding the Workflow File

### Workflow Structure

A GitHub Actions workflow has 3 main parts:

#### 1. Triggers (`on`)
```yaml
on:
  push:
    branches: [ main, develop, CICD ]
  pull_request:
    branches: [ main, develop ]
```

**Meaning:** Run this workflow when:
- Code is pushed to `main`, `develop`, or `CICD` branches
- A pull request is opened targeting `main` or `develop`

#### 2. Jobs
```yaml
jobs:
  backend-tests:    # Job name
    runs-on: ubuntu-latest  # Operating system
    steps: [...]    # What to do
```

**Jobs run in parallel** by default (faster!)
- `backend-tests` and `frontend-tests` run at the same time
- `build-check` waits for both to finish (`needs:` keyword)

#### 3. Steps
```yaml
steps:
  - name: Checkout code
    uses: actions/checkout@v4
```

**Each step** is either:
- `uses:` - Use a pre-made action (like LEGO blocks)
- `run:` - Run shell commands

---

## 🔍 Deep Dive: Each Step Explained

### Backend Job Breakdown

#### Step 1: Checkout Code
```yaml
- name: Checkout code
  uses: actions/checkout@v4
```
**What it does:** Downloads your repository code to the runner  
**Why:** The runner starts empty; it needs your code first

---

#### Step 2: Set Up Python
```yaml
- name: Set up Python 3.11
  uses: actions/setup-python@v4
  with:
    python-version: '3.11'
```
**What it does:** Installs Python 3.11  
**Why:** Your backend needs Python to run tests

---

#### Step 3: Cache Dependencies
```yaml
- name: Cache Python dependencies
  uses: actions/cache@v3
  with:
    path: ~/.cache/pip
    key: ${{ runner.os }}-pip-${{ hashFiles('backend/requirements.txt') }}
```
**What it does:** Saves installed packages, reuses them next time  
**Why:** Speeds up builds (30 seconds → 5 seconds)  
**How:** Creates a cache key from `requirements.txt` content

---

#### Step 4: Install Dependencies
```yaml
- name: Install dependencies
  working-directory: ./backend
  run: |
    python -m pip install --upgrade pip
    pip install -r requirements.txt
    pip install pytest pytest-cov flake8 black
```
**What it does:** Installs your Python packages  
**Why:** Need these to run tests and linters

---

#### Step 5: Lint with Flake8
```yaml
- name: Lint with flake8
  working-directory: ./backend
  run: |
    flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics
    flake8 . --count --exit-zero --max-complexity=10 --max-line-length=100 --statistics
```
**What it does:**
- First line: Check for **critical errors** (syntax errors, undefined names) → **FAIL build**
- Second line: Check for **style warnings** → **DON'T fail build** (`--exit-zero`)

**Why:** Catches code quality issues automatically

---

#### Step 6: Check Formatting
```yaml
- name: Check code formatting with black
  working-directory: ./backend
  run: black --check .
```
**What it does:** Verifies code is formatted consistently  
**Why:** Ensures all code follows the same style  
**Note:** `--check` only checks, doesn't modify files

---

#### Step 7: Run Tests
```yaml
- name: Run tests with pytest
  working-directory: ./backend
  run: pytest --cov=app --cov-report=xml --cov-report=term-missing
```
**What it does:** Runs all your tests with coverage  
**Outputs:**
- `coverage.xml` - Machine-readable coverage report
- Terminal output - Human-readable results

---

#### Step 8: Upload Coverage
```yaml
- name: Upload coverage to Codecov
  uses: codecov/codecov-action@v3
  with:
    file: ./backend/coverage.xml
    flags: backend
```
**What it does:** Sends coverage report to Codecov (optional service)  
**Why:** Track coverage trends over time  
**Note:** `fail_ci_if_error: false` means it won't break the build if upload fails

---

### Frontend Job Breakdown

#### npm ci vs npm install
```yaml
run: npm ci
```
**Why `npm ci` instead of `npm install`?**
- `npm ci` is faster (skips certain checks)
- Requires `package-lock.json` (deterministic installs)
- Deletes `node_modules/` first (clean install)
- Perfect for CI environments

---

#### Node.js Caching
```yaml
- uses: actions/setup-node@v4
  with:
    node-version: '18'
    cache: 'npm'
    cache-dependency-path: frontend/package-lock.json
```
**Built-in caching!** This action automatically:
- Caches `node_modules/`
- Invalidates cache when `package-lock.json` changes
- Restores cache on next run

---

#### Tests with Coverage
```yaml
run: npm test -- --coverage --passWithNoTests
```
**Flags explained:**
- `--coverage` - Generate coverage report
- `--passWithNoTests` - Don't fail if no tests found yet (useful during development)

---

### Build Check Job

```yaml
build-check:
  needs: [backend-tests, frontend-tests]
```

**Why this job?**
1. Ensures code actually builds for production
2. Catches build-only errors (not caught by tests)
3. Only runs if tests pass (saves time)

---

## 🚀 Deployment Steps

### Step 1: Create the Workflow File

```bash
# From project root
mkdir -p .github/workflows

# Create the file (copy the YAML from above)
# Windows (PowerShell):
New-Item -Path ".github/workflows/ci.yml" -ItemType File -Force

# Mac/Linux:
touch .github/workflows/ci.yml
```

Then copy the complete YAML workflow into this file.

---

### Step 2: Add Status Badges to README

Update your `README.md` to show build status:

```markdown
# Task Management Application

![CI Pipeline](https://github.com/vee-kay8/task-management-app/workflows/CI%20Pipeline/badge.svg)
[![codecov](https://codecov.io/gh/vee-kay8/task-management-app/branch/main/graph/badge.svg)](https://codecov.io/gh/vee-kay8/task-management-app)

A full-stack task management application...
```

**What this does:**
- Shows a green badge when tests pass ✅
- Shows a red badge when tests fail ❌
- Visible on your repository homepage

---

### Step 3: Commit and Push

```bash
# Stage changes
git add .github/workflows/ci.yml README.md

# Commit
git commit -m "Add GitHub Actions CI workflow"

# Push to trigger the workflow
git push origin CICD
```

---

### Step 4: Watch It Run!

1. Go to GitHub: `https://github.com/vee-kay8/task-management-app`
2. Click **"Actions"** tab
3. See your workflow running in real-time!

---

## 📊 Understanding the GitHub Actions UI

### Workflow Dashboard
When you click "Actions", you'll see:

```
┌─────────────────────────────────────────────────────────┐
│  CI Pipeline                                  ●  Active │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  ✓  Add GitHub Actions CI workflow       3m 24s       │
│     main - #abc123 - by vee-kay8                       │
│     ├── ✓ Backend Tests & Linting       1m 45s       │
│     ├── ✓ Frontend Tests & Linting      2m 12s       │
│     └── ✓ Build Check                    1m 03s       │
│                                                         │
│  ✗  Previous commit                       2m 15s       │
│     main - #def456 - by vee-kay8                       │
│     ├── ✓ Backend Tests & Linting       1m 30s       │
│     ├── ✗ Frontend Tests & Linting      Failed!       │
│     └── ⊘ Build Check                    Skipped       │
└─────────────────────────────────────────────────────────┘
```

**Legend:**
- ✓ = Success (green)
- ✗ = Failed (red)
- ⊘ = Skipped (gray)
- ● = Running (yellow)

---

### Clicking Into a Run

Click on a workflow run to see details:

```
CI Pipeline #123
────────────────────────────────────────

Jobs:
├─ Backend Tests & Linting (1m 45s)
│  ├─ ✓ Checkout code (2s)
│  ├─ ✓ Set up Python 3.11 (5s)
│  ├─ ✓ Cache Python dependencies (1s)
│  ├─ ✓ Install dependencies (45s)
│  ├─ ✓ Lint with flake8 (3s)
│  ├─ ✓ Check code formatting (2s)
│  ├─ ✓ Run tests with pytest (40s)
│  └─ ✓ Upload coverage (7s)
│
├─ Frontend Tests & Linting (2m 12s)
│  └─ [Similar steps...]
│
└─ Build Check (1m 03s)
   └─ [Similar steps...]
```

Click on any step to see its output!

---

## 🐛 Debugging Failed Workflows

### Common Failure: Test Failed

**Symptoms:**
```
❌ Run tests with pytest
   FAILED tests/unit/test_models.py::TestUserModel::test_user_creation
```

**How to debug:**
1. Click the failed step
2. Read the error message
3. Fix locally: `cd backend && pytest`
4. Commit and push again

---

### Common Failure: Linting Error

**Symptoms:**
```
❌ Lint with flake8
   ./app/models/user.py:45:80: E501 line too long (105 > 100 characters)
```

**How to fix:**
```bash
cd backend
flake8 .  # See the error locally
black .   # Auto-fix formatting
git add .
git commit -m "Fix linting issues"
git push
```

---

### Common Failure: Missing Dependency

**Symptoms:**
```
❌ Run tests
   ModuleNotFoundError: No module named 'pytest_flask'
```

**How to fix:**
Add missing package to `requirements.txt`:
```bash
cd backend
echo "pytest-flask==1.2.0" >> requirements.txt
git add requirements.txt
git commit -m "Add missing test dependency"
git push
```

---

## ⚙️ Advanced Configuration

### Running Workflows on Multiple Python Versions

```yaml
backend-tests:
  strategy:
    matrix:
      python-version: ['3.9', '3.10', '3.11']
  
  steps:
    - name: Set up Python ${{ matrix.python-version }}
      uses: actions/setup-python@v4
      with:
        python-version: ${{ matrix.python-version }}
```

**What this does:** Runs tests on Python 3.9, 3.10, AND 3.11 (in parallel)

---

### Setting Timeout Limits

```yaml
jobs:
  backend-tests:
    timeout-minutes: 10  # Fail if job takes > 10 minutes
```

**Why:** Prevents infinite loops from consuming all your free minutes

---

### Environment Variables

```yaml
jobs:
  backend-tests:
    env:
      DATABASE_URL: postgresql://test:test@localhost:5432/testdb
      FLASK_ENV: testing
```

**Use case:** Set environment variables for tests

---

### Running on Multiple Operating Systems

```yaml
jobs:
  backend-tests:
    strategy:
      matrix:
        os: [ubuntu-latest, windows-latest, macos-latest]
    runs-on: ${{ matrix.os }}
```

**What this does:** Tests on Linux, Windows, AND macOS

---

## 📈 Monitoring & Optimization

### GitHub Actions Usage Limits

**Free tier:**
- 2,000 minutes/month for private repos
- Unlimited for public repos

**Your workflow uses:**
- ~5 minutes per run
- ~400 runs per month possible

**Tips to save minutes:**
1. Use caching (already included)
2. Only run on important branches
3. Skip build check on draft PRs

---

### Caching Strategy

```yaml
- uses: actions/cache@v3
  with:
    path: ~/.cache/pip
    key: ${{ runner.os }}-pip-${{ hashFiles('backend/requirements.txt') }}
    restore-keys: |
      ${{ runner.os }}-pip-
```

**How it works:**
1. First run: No cache → Full install (45s)
2. Second run: Cache hit → Restore cache (5s)
3. After changing `requirements.txt`: New cache → Full install (45s)

---

## ✅ Verification Checklist

Before considering Phase 2 complete:

- [ ] `.github/workflows/ci.yml` file created
- [ ] Workflow file has no syntax errors (YAML is picky about indentation!)
- [ ] README updated with status badges
- [ ] Pushed to GitHub and workflow triggered
- [ ] All jobs pass successfully (green checkmarks)
- [ ] Can see workflow results in Actions tab
- [ ] Status badge shows in README
- [ ] Understand what each job does
- [ ] Know how to debug failures

---

## 🎓 Key Concepts Learned

### 1. Continuous Integration (CI)
**Definition:** Automatically testing code changes as soon as they're pushed

**Benefits:**
- Catch bugs early
- Ensure code quality
- Give confidence to merge
- Document that tests pass

### 2. GitHub Actions
**What:** GitHub's built-in CI/CD platform

**Key components:**
- **Workflows:** Automated processes
- **Jobs:** Groups of steps (run in parallel)
- **Steps:** Individual tasks
- **Runners:** Virtual machines that execute jobs
- **Actions:** Reusable units of code

### 3. YAML Syntax
**Key rules:**
- Indentation matters (2 spaces)
- Use `-` for lists
- Use `:` for key-value pairs
- `|` for multi-line strings

### 4. CI Best Practices
✅ Run tests on every push  
✅ Fail fast (catch errors early)  
✅ Keep builds fast (<5 minutes)  
✅ Use caching  
✅ Parallelize jobs  
✅ Clear error messages  

---

## 🔒 Security Best Practices

### Never Commit Secrets
```yaml
# ❌ WRONG
env:
  API_KEY: "sk_live_abc123..."

# ✅ RIGHT
env:
  API_KEY: ${{ secrets.API_KEY }}
```

**How to add secrets:**
1. GitHub repo → Settings → Secrets → Actions
2. Click "New repository secret"
3. Name: `API_KEY`, Value: `your-secret-here`

---

### Use Minimal Permissions

```yaml
permissions:
  contents: read  # Only read access to code
  pull-requests: write  # Can comment on PRs
```

**Why:** Limits damage if action is compromised

---

## 🎯 Next Steps

### Immediate Actions
1. ✅ Create workflow file
2. ✅ Push and verify it works
3. ✅ Fix any failing tests
4. ✅ Add status badge to README

### Optional Enhancements
- Set up Codecov account for coverage tracking
- Add Slack/Discord notifications
- Create PR comment with test results
- Add deployment preview links

### Prepare for Phase 3
Phase 3 will cover:
- Docker image building in CI
- Pushing to container registry
- Multi-stage builds
- Security scanning

---

## 📚 Additional Resources

### Official Documentation
- [GitHub Actions Docs](https://docs.github.com/en/actions)
- [Workflow Syntax](https://docs.github.com/en/actions/using-workflows/workflow-syntax-for-github-actions)
- [Actions Marketplace](https://github.com/marketplace?type=actions)

### Useful Actions
- `actions/checkout@v4` - Clone repository
- `actions/setup-python@v4` - Install Python
- `actions/setup-node@v4` - Install Node.js
- `actions/cache@v3` - Cache dependencies
- `codecov/codecov-action@v3` - Upload coverage

---

## 🆘 Troubleshooting Guide

### Issue: "Invalid workflow file"
**Cause:** YAML syntax error  
**Solution:** 
1. Check indentation (must be 2 spaces)
2. Use YAML validator: https://www.yamllint.com/
3. Look for missing colons or dashes

---

### Issue: "No workflows found"
**Cause:** Wrong directory or branch  
**Solution:**
1. Verify path: `.github/workflows/ci.yml`
2. Check file is committed and pushed
3. Check you're on the right branch

---

### Issue: "Action not found"
**Cause:** Action version doesn't exist  
**Solution:** Use `@v4` not `@v4.0.0` (more flexible)

---

### Issue: "Resource not accessible"
**Cause:** Private repository with Actions disabled  
**Solution:**
1. Settings → Actions → General
2. Enable "Allow all actions and reusable workflows"

---

## 🎉 Congratulations!

You now have:
- ✅ Fully automated testing pipeline
- ✅ Code quality checks on every push
- ✅ Protection against broken code
- ✅ Professional CI/CD setup
- ✅ Foundation for deployment automation

**This is the same CI/CD approach used by major tech companies!** 🚀

---

## 📞 Ready for Phase 3?

When you've:
1. ✅ Created and pushed workflow file
2. ✅ Seen successful workflow runs
3. ✅ Fixed any failing tests
4. ✅ Understood the workflow structure
5. ✅ Added status badges

Let me know and we'll proceed to **Phase 3: Docker & Container Registry**! 🐳
