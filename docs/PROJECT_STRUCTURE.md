# Project Structure

This document explains the organized structure of the Turtle Species Identification App.

## Directory Layout

```
Proof-Of-Concept-Demo/
├── main.py                     # Main entry point
├── Dockerfile                  # Container configuration
├── .github/                    # GitHub configuration
│   ├── workflows/
│   │   └── ci.yml             # CI/CD pipeline
│   ├── ISSUE_TEMPLATE/        # Issue templates
│   └── PULL_REQUEST_TEMPLATE/ # PR templates
├── config/                     # Configuration files
│   ├── env.example            # Environment variables template
│   ├── pytest.ini            # Test configuration
│   └── .gitignore            # Git ignore rules
├── docs/                      # Documentation
│   ├── README.md             # Main documentation
│   ├── TESTING.md            # Testing guide
│   └── PROJECT_STRUCTURE.md  # This file
├── scripts/                   # Utility scripts
│   ├── Makefile              # Build and test commands
│   └── run_tests.py          # Test runner script
├── src/                       # Source code
│   ├── api/                  # API layer
│   │   ├── __init__.py
│   │   └── app.py            # Flask application
│   ├── utils/                # Utility modules
│   │   ├── __init__.py
│   │   ├── file_utils.py     # File handling utilities
│   │   └── image_utils.py    # Image processing utilities
│   ├── templates/            # HTML templates
│   │   └── index.html        # Main web interface
│   └── run.py                # Alternative entry point
├── tests/                     # Test suite
│   ├── unit/                 # Unit tests
│   │   ├── __init__.py
│   │   ├── test_app.py       # Application tests
│   │   └── test_utils.py     # Utility function tests
│   └── integration/          # Integration tests (future)
├── uploads/                   # Temporary file storage
└── venv/                     # Virtual environment (local)
```

## Directory Descriptions

### **Root Level**
- `main.py` - Main entry point for the application
- `Dockerfile` - Container configuration for deployment
- `.github/` - GitHub-specific configuration and workflows

### **config/**
Configuration files and environment setup:
- `env.example` - Template for environment variables
- `pytest.ini` - Test configuration and settings
- `.gitignore` - Files to ignore in version control

### **docs/**
All project documentation:
- `README.md` - Main project documentation
- `TESTING.md` - Comprehensive testing guide
- `PROJECT_STRUCTURE.md` - This file

### **scripts/**
Utility scripts for development and deployment:
- `Makefile` - Build, test, and deployment commands
- `run_tests.py` - Advanced test runner with options

### **src/**
Main source code organized by functionality:

#### **src/api/**
API layer and Flask application:
- `app.py` - Main Flask application with routes and business logic

#### **src/utils/**
Reusable utility modules:
- `file_utils.py` - File validation, security, and handling
- `image_utils.py` - Image processing and encoding utilities

#### **src/templates/**
HTML templates for the web interface:
- `index.html` - Main user interface

### **tests/**
Comprehensive test suite:

#### **tests/unit/**
Unit tests for individual components:
- `test_app.py` - Tests for Flask application and API endpoints
- `test_utils.py` - Tests for utility functions

#### **tests/integration/**
Integration tests (future expansion):
- Reserved for end-to-end testing

## File Organization Principles

### **1. Separation of Concerns**
- **API layer** (`src/api/`) - Handles HTTP requests and responses
- **Utils layer** (`src/utils/`) - Reusable business logic
- **Templates** (`src/templates/`) - Presentation layer

### **2. Configuration Management**
- All configuration files in `config/`
- Environment-specific settings separated
- Test configuration isolated

### **3. Documentation Structure**
- All documentation in `docs/`
- Clear separation of concerns
- Easy to find and maintain

### **4. Test Organization**
- Tests mirror source structure
- Unit tests separated from integration tests
- Clear test categories and purposes

## Import Structure

### **Main Application**
```python
# main.py
from src.api.app import app
```

### **API Module**
```python
# src/api/app.py
from utils.file_utils import allowed_file, get_secure_filename
from utils.image_utils import encode_image_to_base64, validate_image
```

### **Tests**
```python
# tests/unit/test_app.py
import sys
sys.path.insert(0, 'src')
from api.app import app
```

## Benefits of This Structure

### **1. Scalability**
- Easy to add new modules and features
- Clear separation allows independent development
- Modular design supports team collaboration

### **2. Maintainability**
- Related files grouped together
- Clear naming conventions
- Easy to locate specific functionality

### **3. Testing**
- Tests mirror source structure
- Easy to add new test categories
- Clear test organization

### **4. Deployment**
- Configuration files separated
- Easy to manage environment-specific settings
- Container-ready structure

## Development Workflow

### **Adding New Features**
1. Add utility functions to `src/utils/`
2. Add API endpoints to `src/api/app.py`
3. Update templates in `src/templates/`
4. Add tests to `tests/unit/`
5. Update documentation in `docs/`

### **Running the Application**
```bash
# Main entry point
python main.py

# Alternative entry point
python src/run.py
```

### **Running Tests**
```bash
# All tests
python scripts/run_tests.py

# Backend tests only
python scripts/run_tests.py --type backend

# Using Make
make test
make test-backend
```

### **Configuration**
```bash
# Copy environment template
cp config/env.example .env

# Edit with your API keys
nano .env
```

## Future Expansion

This structure supports easy expansion for:
- **Frontend testing** - Add to `tests/integration/`
- **API versioning** - Add `src/api/v2/`
- **Database layer** - Add `src/database/`
- **Authentication** - Add `src/auth/`
- **Monitoring** - Add `src/monitoring/`

The modular design ensures that new features can be added without disrupting existing functionality.
