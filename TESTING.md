# Testing Guide

This document explains how to run the test suite for the Mergington High School Activities Management System.

## Project Structure

Tests are organized by type in the `tests/` directory:

```
tests/
├── conftest.py              # Shared pytest fixtures and configuration
├── unit/
│   ├── __init__.py
│   └── test_api.py          # Unit tests for API endpoints
├── integration/
│   ├── __init__.py
│   └── test_workflows.py    # Integration tests for complete workflows
└── frontend/
    ├── __init__.py
    └── app.test.js          # Frontend tests for JavaScript functionality
```

## Backend Tests (Python)

### Setup

1. **Install Python dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Run all tests:**
   ```bash
   pytest
   ```

### Running Specific Test Suites

**Unit Tests Only:**
```bash
pytest tests/unit/ -v
```

**Integration Tests Only:**
```bash
pytest tests/integration/ -v
```

**Specific Test File:**
```bash
pytest tests/unit/test_api.py -v
```

**Specific Test Class:**
```bash
pytest tests/unit/test_api.py::TestGetActivities -v
```

**Specific Test Method:**
```bash
pytest tests/unit/test_api.py::TestGetActivities::test_get_activities_returns_200 -v
```

### Test Coverage

**Generate Coverage Report:**
```bash
pytest --cov=src --cov-report=html --cov-report=term-missing
```

This generates:
- Terminal output showing coverage percentages
- HTML report in `htmlcov/index.html`

**View Coverage in HTML:**
```bash
# After running coverage report
open htmlcov/index.html
```

### Pytest Options

- `-v`: Verbose output (shows each test)
- `-s`: Show print statements
- `-x`: Stop on first failure
- `-k <pattern>`: Run tests matching pattern (e.g., `-k signup`)
- `--tb=short`: Shorter traceback format
- `--tb=no`: No traceback
- `-m <marker>`: Run tests with specific marker (e.g., `-m unit`)

## Frontend Tests (JavaScript)

### Setup

1. **Install Node dependencies:**
   ```bash
   npm install
   ```

2. **Run all frontend tests:**
   ```bash
   npm test
   ```

### Running Frontend Tests with Options

**Watch Mode (re-run on file changes):**
```bash
npm run test:watch
```

**UI Mode (visual test runner):**
```bash
npm run test:ui
```

**Coverage Report:**
```bash
npm run test:coverage
```

## Running All Tests

**Run entire test suite (backend + frontend):**
```bash
# Backend
pytest tests/ -v

# Frontend
npm test

# Or run both in sequence
pytest tests/ -v && npm test
```

## Test Coverage Goals

- **Target Coverage**: 80%+
- **Unit Tests**: Core API functionality and edge cases
- **Integration Tests**: Complete workflows and multi-step operations
- **Frontend Tests**: DOM manipulation, form submission, event handling

## What Tests Cover

### Backend Tests

#### Unit Tests (`tests/unit/test_api.py`)
- **GET /activities**
  - Returns 200 status code
  - Returns valid activity data structure
  - Shows correct number of activities
  - Maintains accurate participant lists
  
- **POST /activities/{activity_name}/signup**
  - Successful signup returns 200
  - Adds participant to activity
  - Prevents duplicate signup (400)
  - Rejects non-existent activity (404)
  - Handles special characters in emails
  
- **DELETE /activities/{activity_name}/unregister**
  - Successful unregister returns 200
  - Removes participant from activity
  - Prevents unregistering non-existent participant (400)
  - Rejects non-existent activity (404)
  - Prevents double unregister

#### Integration Tests (`tests/integration/test_workflows.py`)
- Complete signup → verify → unregister workflow
- Multiple sequential operations
- Participant count accuracy
- Availability calculation
- Multi-activity signup
- Cross-activity operations
- Edge cases (long emails, special characters, etc.)

### Frontend Tests (`tests/frontend/app.test.js`)
- Activity list fetching and rendering
- Activity card display with correct data
- Participant list display
- "No participants" message display
- Form submission with email and activity
- Success message display
- Error message display

## Continuous Integration

To integrate tests into CI/CD:

```bash
# Run all tests with exit code 0 on success, 1 on failure
pytest tests/ -v && npm test
```

## Common Issues

### Python Tests

**ImportError: cannot import app**
- Ensure `sys.path` includes the `src/` directory
- Check that `conftest.py` is correctly configured

**ModuleNotFoundError: No module named 'fastapi'**
- Run `pip install -r requirements.txt`

### Frontend Tests

**Cannot find module 'vitest'**
- Run `npm install`

**jsdom is not defined**
- Ensure jsdom is installed: `npm install jsdom --save-dev`

## Debugging Tests

### Backend

**Print Debug Information:**
```bash
pytest tests/unit/test_api.py -v -s
```

**Run with PDB Debugger:**
```bash
pytest tests/unit/test_api.py --pdb
```

**Stop on First Failure:**
```bash
pytest tests/unit/test_api.py -x
```

### Frontend

**Debug in VS Code:**
- Set breakpoints in test file
- Run with VS Code debugger

**Console Output:**
- Use `console.log()` in tests
- View with `npm run test:watch`

## Adding New Tests

1. **Backend**: Add to `tests/unit/test_api.py` or `tests/integration/test_workflows.py`
2. **Frontend**: Add to `tests/frontend/app.test.js`
3. Update test docstrings explaining what's being tested

## Test Naming Conventions

- Test functions start with `test_`
- Test classes start with `Test`
- Use descriptive names: `test_signup_duplicate_returns_400`
- Group related tests in classes

## Example: Running Tests from Command Line

```bash
# Install dependencies
pip install -r requirements.txt
npm install

# Run all backend tests with coverage
pytest tests/ --cov=src --cov-report=term-missing

# Run all frontend tests
npm test

# Run specific test
pytest tests/unit/test_api.py::TestSignup::test_signup_success -v

# Run tests matching pattern
pytest -k "signup" -v

# Run with watch mode (frontend)
npm run test:watch
```
