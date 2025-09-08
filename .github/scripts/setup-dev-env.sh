#!/bin/bash

# =============================================================================
# FamilyCart Development Environment Setup Script
# =============================================================================
# This script sets up a complete development environment following the
# workflow defined in DEVELOPMENT_WORKFLOW_PROPOSAL.md
# =============================================================================

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging functions
log_info() { echo -e "${BLUE}[INFO]${NC} $1"; }
log_success() { echo -e "${GREEN}[SUCCESS]${NC} $1"; }
log_warning() { echo -e "${YELLOW}[WARNING]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }

# Check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Main setup function
main() {
    log_info "Starting FamilyCart development environment setup..."
    
    # Check prerequisites
    check_prerequisites
    
    # Setup backend
    setup_backend
    
    # Setup frontend
    setup_frontend
    
    # Setup git hooks
    setup_git_hooks
    
    # Create development scripts
    create_dev_scripts
    
    # Final verification
    verify_setup
    
    log_success "Development environment setup complete!"
    show_next_steps
}

check_prerequisites() {
    log_info "Checking prerequisites..."
    
    # Check Python 3.11
    if ! command_exists python3.11; then
        log_error "Python 3.11 is required but not installed"
        exit 1
    fi
    
    # Check Poetry
    if ! command_exists poetry; then
        log_error "Poetry is required but not installed"
        log_info "Install Poetry: curl -sSL https://install.python-poetry.org | python3 -"
        exit 1
    fi
    
    # Check Node.js
    if ! command_exists node; then
        log_error "Node.js is required but not installed"
        exit 1
    fi
    
    # Check npm
    if ! command_exists npm; then
        log_error "npm is required but not installed"
        exit 1
    fi
    
    # Check Docker
    if ! command_exists docker; then
        log_warning "Docker is not installed - some features may not work"
    fi
    
    # Check Git
    if ! command_exists git; then
        log_error "Git is required but not installed"
        exit 1
    fi
    
    log_success "All prerequisites are satisfied"
}

setup_backend() {
    log_info "Setting up backend environment..."
    
    cd backend
    
    # Install dependencies
    log_info "Installing Python dependencies with Poetry..."
    poetry install --with dev,test
    
    # Setup pre-commit hooks
    log_info "Setting up pre-commit hooks..."
    poetry run pre-commit install
    
    # Create .env file if it doesn't exist
    if [ ! -f .env ]; then
        log_info "Creating .env file from template..."
        if [ -f .env.example ]; then
            cp .env.example .env
            log_warning "Please update .env file with your configuration"
        else
            log_warning ".env.example not found - create .env manually"
        fi
    fi
    
    cd ..
    log_success "Backend setup complete"
}

setup_frontend() {
    log_info "Setting up frontend environment..."
    
    cd frontend
    
    # Install dependencies
    log_info "Installing Node.js dependencies..."
    npm ci
    
    # Create .env.local if it doesn't exist
    if [ ! -f .env.local ]; then
        log_info "Creating .env.local file from template..."
        if [ -f .env.example ]; then
            cp .env.example .env.local
            log_warning "Please update .env.local file with your configuration"
        else
            log_warning ".env.example not found - create .env.local manually"
        fi
    fi
    
    cd ..
    log_success "Frontend setup complete"
}

setup_git_hooks() {
    log_info "Setting up Git hooks..."
    
    # Create pre-commit hook
    cat > .git/hooks/pre-commit << 'EOF'
#!/bin/bash

echo "Running pre-commit checks..."

# Backend checks
cd backend
echo "Running backend code quality checks..."
poetry run black --check . || (echo "Code formatting issues found. Run 'poetry run black .' to fix." && exit 1)
poetry run isort --check-only . || (echo "Import sorting issues found. Run 'poetry run isort .' to fix." && exit 1)

cd ../frontend
echo "Running frontend code quality checks..."
npm run lint || (echo "ESLint issues found. Run 'npm run lint:fix' to fix." && exit 1)
npm run typecheck || (echo "TypeScript errors found. Fix type issues." && exit 1)

echo "✅ Pre-commit checks passed"
EOF

    chmod +x .git/hooks/pre-commit
    
    # Create commit-msg hook for conventional commits
    cat > .git/hooks/commit-msg << 'EOF'
#!/bin/bash

commit_regex='^(feat|fix|docs|style|refactor|test|chore|hotfix|release)(\(.+\))?: .{1,50}'

if ! grep -qE "$commit_regex" "$1"; then
    echo "❌ Invalid commit message format!"
    echo "Commit message must follow conventional commit format:"
    echo "  feat: add new feature"
    echo "  fix: resolve bug issue"
    echo "  docs: update documentation"
    echo "  style: formatting changes"
    echo "  refactor: code restructuring"
    echo "  test: add or update tests"
    echo "  chore: maintenance tasks"
    echo "  hotfix: critical production fix"
    echo "  release: version release preparation"
    exit 1
fi
EOF

    chmod +x .git/hooks/commit-msg
    
    log_success "Git hooks configured"
}

create_dev_scripts() {
    log_info "Creating development scripts..."
    
    mkdir -p scripts
    
    # Create development start script
    cat > scripts/dev-start.sh << 'EOF'
#!/bin/bash

# Start development environment
echo "Starting FamilyCart development environment..."

# Start backend in background
echo "Starting backend..."
cd backend
poetry run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!

# Start frontend in background  
echo "Starting frontend..."
cd ../frontend
npm run dev &
FRONTEND_PID=$!

# Wait for Ctrl+C
echo "Development environment started!"
echo "Backend: http://localhost:8000"
echo "Frontend: http://localhost:3000"
echo "API Docs: http://localhost:8000/docs"
echo ""
echo "Press Ctrl+C to stop all services..."

trap "kill $BACKEND_PID $FRONTEND_PID; exit" INT

wait
EOF

    chmod +x scripts/dev-start.sh
    
    # Create test script
    cat > scripts/run-tests.sh << 'EOF'
#!/bin/bash

echo "Running FamilyCart test suite..."

# Backend tests
echo "Running backend tests..."
cd backend
poetry run pytest --cov=app --cov-report=term-missing
BACKEND_EXIT=$?

# Frontend tests
echo "Running frontend tests..."
cd ../frontend
npm test -- --coverage --watchAll=false
FRONTEND_EXIT=$?

# Summary
echo ""
if [ $BACKEND_EXIT -eq 0 ] && [ $FRONTEND_EXIT -eq 0 ]; then
    echo "✅ All tests passed!"
    exit 0
else
    echo "❌ Some tests failed!"
    exit 1
fi
EOF

    chmod +x scripts/run-tests.sh
    
    # Create quality check script
    cat > scripts/quality-check.sh << 'EOF'
#!/bin/bash

echo "Running code quality checks..."

# Backend quality checks
echo "Checking backend code quality..."
cd backend
poetry run black --check .
poetry run isort --check-only .
poetry run pylint app/ --disable=C0114,C0116,R0903,W0613 --fail-under=8.0
poetry run bandit -r app/
BACKEND_EXIT=$?

# Frontend quality checks
echo "Checking frontend code quality..."
cd ../frontend
npm run lint
npm run typecheck
npm run format:check
FRONTEND_EXIT=$?

# Summary
echo ""
if [ $BACKEND_EXIT -eq 0 ] && [ $FRONTEND_EXIT -eq 0 ]; then
    echo "✅ All quality checks passed!"
    exit 0
else
    echo "❌ Quality checks failed!"
    exit 1
fi
EOF

    chmod +x scripts/quality-check.sh
    
    log_success "Development scripts created"
}

verify_setup() {
    log_info "Verifying setup..."
    
    # Test backend setup
    cd backend
    if poetry run python -c "import app.main"; then
        log_success "Backend imports successfully"
    else
        log_error "Backend import failed"
        exit 1
    fi
    
    # Test frontend setup
    cd ../frontend
    if npm run typecheck > /dev/null 2>&1; then
        log_success "Frontend TypeScript compiles successfully"
    else
        log_warning "Frontend TypeScript has issues - check manually"
    fi
    
    cd ..
    log_success "Setup verification complete"
}

show_next_steps() {
    echo ""
    log_info "🎉 Development environment is ready!"
    echo ""
    echo "Next steps:"
    echo "1. Update .env files with your configuration"
    echo "2. Start development: ./scripts/dev-start.sh"
    echo "3. Run tests: ./scripts/run-tests.sh"
    echo "4. Check code quality: ./scripts/quality-check.sh"
    echo ""
    echo "Branch workflow:"
    echo "1. Create feature branch: git checkout -b feature/sprint-N-description"
    echo "2. Make changes and commit with conventional commit messages"
    echo "3. Push and create PR to develop branch"
    echo "4. After review, merge to develop"
    echo "5. Deploy to UAT for testing"
    echo ""
    echo "See DEVELOPMENT_WORKFLOW_PROPOSAL.md for complete workflow details."
}

# Run main function
main "$@"
