# Feature Flag & CI/CD Setup Guide

## Overview

This guide covers the complete setup for:
1. **Feature Flag Management System** - Control feature rollouts safely
2. **CI/CD Pipeline** - Automated testing and deployment
3. **Automated Testing** - Comprehensive test suite with pytest

---

## 1. Feature Flag System

### What is it?
A database-backed feature flag system that allows you to:
- Enable/disable features without deploying code
- Target features by user ID, role, or percentage rollout
- Run A/B tests
- Control features per environment (dev, staging, production)
- Track all changes with audit logging

### Installation

The feature flag system is already included in `/workspace/utils/feature_flags.py`.

To initialize it in your Flask app, add to `app.py` or `extensions.py`:

```python
from utils.feature_flags import init_feature_flags

def create_app(config_object='config.Config'):
    app = Flask(__name__)
    # ... existing setup ...
    
    # Initialize feature flags
    with app.app_context():
        init_feature_flags(app)
    
    return app
```

### Usage Examples

#### Check if a feature is enabled (in views):
```python
from utils.feature_flags import FeatureFlag
from flask_login import current_user

@app.route('/dashboard')
def dashboard():
    if FeatureFlag.is_enabled('new_dashboard', current_user):
        return render_template('new_dashboard.html')
    return render_template('old_dashboard.html')
```

#### In templates:
```python
# Add to app context processor
@app.context_processor
def utility_processor():
    from utils.feature_flags import feature_flag
    return dict(feature_flag=feature_flag)
```

```html
{% if feature_flag('dark_mode') %}
  <link rel="stylesheet" href="{{ url_for('static', filename='css/dark.css') }}">
{% endif %}
```

#### Create/Update flags programmatically:
```python
from utils.feature_flags import FeatureFlagManager

# Create a new flag
flag = FeatureFlagManager.create_flag(
    name='ai_recommendations',
    description='AI-powered product recommendations',
    enabled=True,
    enabled_for_roles=['admin', 'premium'],
    rollout_percentage=25,  # 25% of eligible users
    created_by='admin_user'
)

# Update a flag
FeatureFlagManager.update_flag(
    flag_id=flag.id,
    updates={'rollout_percentage': 50},
    changed_by='product_manager',
    reason='Increasing rollout after successful A/B test'
)

# Toggle on/off
FeatureFlagManager.toggle_flag(
    flag_id=flag.id,
    enabled=False,
    changed_by='oncall',
    reason='Emergency disable due to bug'
)
```

### Database Tables

Two tables are created automatically:
- `feature_flags` - Stores flag configurations
- `feature_flag_audit` - Audit log of all changes

Run migrations to create them:
```bash
flask db upgrade
```

---

## 2. CI/CD Pipeline (GitHub Actions)

### What's Included

The pipeline (`.github/workflows/ci-cd.yml`) provides:

1. **Automated Testing**
   - Runs on every push and pull request
   - Tests against PostgreSQL and Redis
   - Generates coverage reports

2. **Code Quality Checks**
   - Linting with flake8
   - Formatting check with black
   - Type checking with mypy
   - Security scanning with bandit

3. **Docker Build & Push**
   - Builds Docker image on main branch
   - Pushes to Docker Hub with version tags

4. **Deployment**
   - Placeholder for production deployment
   - Customize with your deployment commands

### Setup Steps

#### 1. Enable GitHub Actions
Your repository already has the workflow file. Just push to GitHub!

#### 2. Configure Secrets (in GitHub Repo Settings → Secrets)

Required secrets:
```
DOCKER_USERNAME     - Your Docker Hub username
DOCKER_PASSWORD     - Your Docker Hub password/access token
CODECOV_TOKEN       - (Optional) Codecov token for coverage reports
```

Set them up:
1. Go to your GitHub repo
2. Settings → Secrets and variables → Actions
3. Click "New repository secret"
4. Add each secret

#### 3. Customize Deployment

Edit `.github/workflows/ci-cd.yml` and update the deploy job:

```yaml
- name: Deploy to Production
  run: |
    # SSH deployment example
    ssh user@your-server 'cd /app && docker-compose pull && docker-compose up -d'
    
    # OR Kubernetes example
    # kubectl set image deployment/tradeglobal app=myimage:${{ github.sha }}
    
    # OR other deployment method
```

### Running Locally

Test the CI steps locally before pushing:

```bash
# Install dev dependencies
pip install -r requirements.txt

# Run linters
flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics
black --check .
mypy --ignore-missing-imports .
bandit -r . -ll

# Run tests
pytest tests/ -v --cov=. --cov-report=html
```

---

## 3. Automated Testing

### Test Structure

Tests are in `/workspace/tests/`:
- `test_models.py` - Model tests
- `test_feature_flags.py` - Feature flag tests (newly added)

### Running Tests

```bash
# All tests
pytest tests/ -v

# With coverage
pytest tests/ -v --cov=. --cov-report=html

# Specific test file
pytest tests/test_feature_flags.py -v

# Specific test class
pytest tests/test_feature_flags.py::TestFeatureFlagModel -v

# Specific test function
pytest tests/test_feature_flags.py::TestFeatureFlagModel::test_create_flag -v
```

### Writing New Tests

Example test structure:

```python
import pytest
from app import create_app
from extensions import db

@pytest.fixture
def app():
    app = create_app({
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:'
    })
    with app.app_context():
        db.create_all()
        yield app
        db.drop_all()

@pytest.fixture
def client(app):
    return app.test_client()

def test_something(client):
    response = client.get('/some-endpoint')
    assert response.status_code == 200
```

---

## 4. Pre-commit Hooks

### What are they?
Git hooks that run automatically before each commit to ensure code quality.

### Setup

```bash
# Install pre-commit
pip install pre-commit

# Install git hooks
pre-commit install

# Run manually (optional)
pre-commit run --all-files
```

### What it checks
- Trailing whitespace
- End-of-file newlines
- YAML/JSON syntax
- Large files
- Private keys
- Python formatting (black)
- Python linting (flake8)
- Import sorting (isort)
- Type hints (mypy)
- Security issues (bandit)

---

## 5. Complete Setup Checklist

### Initial Setup (One-time)

```bash
# 1. Clone/pull latest code
git pull origin main

# 2. Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate  # Windows

# 3. Install dependencies (including new ones)
pip install -r requirements.txt

# 4. Install pre-commit hooks
pre-commit install

# 5. Set up environment variables
cp .env.example .env
# Edit .env with your values

# 6. Run database migrations
flask db upgrade

# 7. Initialize feature flags (in Python shell)
flask shell
>>> from utils.feature_flags import init_feature_flags
>>> from app import create_app
>>> app = create_app()
>>> with app.app_context(): init_feature_flags(app)
```

### For PyCharm

1. **Install packages**: Settings → Project → Python Interpreter → + → Install `requirements.txt`

2. **Configure pytest**: 
   - Settings → Tools → Python Integrated Tools
   - Testing: pytest
   - Default test runner: pytest

3. **Enable pre-commit**:
   - Terminal: `pre-commit install`
   - Or use PyCharm's File Watchers

4. **Run configurations**:
   - Create run config for pytest
   - Create run config for Flask app
   - Create run config for Celery workers

---

## 6. Best Practices

### Feature Flags
- ✅ Use descriptive names: `new_checkout_flow` not `flag1`
- ✅ Always add descriptions
- ✅ Remove old flags after full rollout
- ✅ Use audit logs to track changes
- ✅ Start with small rollout percentages
- ❌ Don't leave disabled flags forever
- ❌ Don't use flags for emergency kill switches only

### CI/CD
- ✅ Keep build times under 10 minutes
- ✅ Test on every PR
- ✅ Deploy only from main branch
- ✅ Use semantic versioning for Docker tags
- ❌ Don't skip tests for "quick fixes"
- ❌ Don't deploy directly to production without testing

### Testing
- ✅ Write tests before fixing bugs (TDD)
- ✅ Aim for >80% code coverage
- ✅ Test edge cases and error conditions
- ✅ Use fixtures for common setups
- ❌ Don't test implementation details
- ❌ Don't ignore failing tests

---

## 7. Troubleshooting

### Feature Flags not working?
```bash
# Check if tables exist
flask shell
>>> from utils.feature_flags import FeatureFlag
>>> FeatureFlag.query.all()

# Re-run migrations
flask db migrate -m "Add feature flags"
flask db upgrade
```

### CI/CD failing?
```bash
# Test locally first
flake8 .
black --check .
pytest tests/ -v

# Check GitHub Actions logs
# Look for specific error messages
```

### Tests failing?
```bash
# Run with more verbosity
pytest tests/ -v -s

# Run specific test
pytest tests/test_file.py::TestClass::test_method -v

# Check test database setup
# Ensure TESTING=True in config
```

---

## Next Steps

1. ✅ Review and customize the CI/CD pipeline for your infrastructure
2. ✅ Create initial feature flags for upcoming features
3. ✅ Add more comprehensive tests for your business logic
4. ✅ Set up monitoring and alerting for production
5. ✅ Document your deployment process
6. ✅ Train team on feature flag best practices

---

## Support

For issues or questions:
- Check the inline documentation in code files
- Review pytest documentation: https://docs.pytest.org/
- GitHub Actions docs: https://docs.github.com/en/actions
- Feature flag patterns: https://martinfowler.com/articles/feature-toggles.html
