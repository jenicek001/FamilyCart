# CI Code Quality Standards

This document describes the balanced code quality standards implemented in our GitHub Actions CI pipeline.

## 🎯 Quality Standards Overview

### ✅ **Black Code Formatting**
- **Standard**: Strict formatting with 88-character line length
- **Exclusions**: None - all code must be properly formatted
- **Command**: `poetry run black --check .`

### ✅ **Isort Import Organization**
- **Standard**: Black-compatible import sorting
- **Exclusions**: None - all imports must be properly organized  
- **Command**: `poetry run isort --check-only .`

### ✅ **Pylint Code Quality (9.56/10 target)**
- **Standard**: High-quality code with practical exclusions
- **Score Target**: 9.5+ out of 10
- **Command**: `poetry run pylint app/ --score=y`

**Excluded Rules (Balanced Approach):**
- Documentation (C0114, C0116, C0115) - rapid development
- SQLAlchemy patterns (E1101) - ORM false positives
- Test patterns (W0621, W0613, R0801) - pytest fixtures
- FastAPI patterns (R0903, W0718, C0415) - framework conventions
- Complex business logic (R0913, R0914, R0915) - domain complexity
- Configuration naming (C0103, W0622) - framework standards

**Still Catching Important Issues:**
- Unused imports and variables
- Poor logging practices  
- Missing exception chaining
- Unnecessary code patterns

### ✅ **Bandit Security Scanning**
- **Standard**: Comprehensive security scan with test exclusions
- **Target**: Zero production security issues
- **Command**: `poetry run bandit -c pyproject.toml -r app/`

**Excluded Patterns:**
- B101: Assert statements (legitimate in tests)
- B104: Bind all interfaces (containers)
- B105/B106: Hardcoded passwords (test fixtures only)

## 🔧 Local Development

### Run All Quality Checks
```bash
cd backend

# Format code
poetry run black .
poetry run isort .

# Check quality  
poetry run black --check .
poetry run isort --check-only .
poetry run pylint app/ --score=y
poetry run bandit -c pyproject.toml -r app/

# Run tests with coverage
poetry run pytest --cov=app --cov-report=html
```

### Fix Common Issues
```bash
# Fix formatting
poetry run black .
poetry run isort .

# Remove unused imports (manual review recommended)
poetry run autoflake --in-place --remove-all-unused-imports --recursive app/
```

## 📊 CI Pipeline Features

### Code Quality Reports
- Pylint detailed analysis (JSON + text)
- Security scan results
- Test coverage reports
- Artifacts retained for 30 days

### Quality Summary
The CI provides a summary including:
- Pylint score (target: 9.5+/10)
- Security issues count (target: 0)
- Test coverage percentage

### Fail-Safe Design
- Code quality issues fail the build
- Security issues fail the build  
- Test failures fail the build
- Reports generated even on failure

## 🎯 Why These Standards?

### Balanced Approach
- **Strict on important issues**: Security, unused code, poor patterns
- **Flexible on conventions**: Documentation, framework patterns
- **Practical for teams**: Reasonable complexity thresholds

### Quality vs. Productivity
- Catches real bugs and maintainability issues
- Doesn't slow development with over-strict rules
- Focuses on security and correctness
- Allows framework-specific patterns

## 📈 Continuous Improvement

### Monitoring
- Track pylint scores over time
- Monitor security issue trends
- Review coverage reports

### Adjustments
- Rules can be refined based on team feedback
- Thresholds can be adjusted for complexity
- New tools can be added as needed

### Team Guidelines
- Address quality issues before merging
- Security issues are non-negotiable
- Coverage should trend upward
- Document any rule exceptions
