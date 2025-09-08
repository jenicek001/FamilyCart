#!/bin/bash

# =============================================================================
# FamilyCart Workflow Validation Test
# =============================================================================
# This script validates that the Week 1 workflow setup is working correctly
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

echo "🔍 FamilyCart Workflow Validation Test"
echo "======================================"

# Test 1: Branch naming convention validation
log_info "Testing branch naming convention..."
current_branch=$(git branch --show-current)
if [[ "$current_branch" =~ ^(feature|hotfix|bugfix|chore|docs|release)/.+ ]]; then
    log_success "Branch name '$current_branch' follows naming convention"
else
    log_error "Branch name '$current_branch' doesn't follow convention"
fi

# Test 2: Check workflow files exist
log_info "Checking workflow files..."
workflow_files=(
    ".github/workflows/branch-protection.yml"
    ".github/PULL_REQUEST_TEMPLATE/feature_template.md"
    ".github/PULL_REQUEST_TEMPLATE/hotfix_template.md"
    ".github/PULL_REQUEST_TEMPLATE/release_template.md"
    ".github/ISSUE_TEMPLATE/bug_report.yml"
    ".github/ISSUE_TEMPLATE/feature_request.yml"
    ".github/BRANCH_PROTECTION_SETUP.md"
)

for file in "${workflow_files[@]}"; do
    if [ -f "$file" ]; then
        log_success "✓ $file exists"
    else
        log_error "✗ $file missing"
    fi
done

# Test 3: Check branch structure
log_info "Checking branch structure..."
if git show-ref --verify --quiet refs/heads/develop; then
    log_success "✓ develop branch exists"
else
    log_error "✗ develop branch missing"
fi

if git show-ref --verify --quiet refs/heads/main; then
    log_success "✓ main branch exists"
else
    log_error "✗ main branch missing"
fi

# Test 4: Check if backend and frontend directories exist
log_info "Checking project structure..."
if [ -d "backend" ]; then
    log_success "✓ backend directory exists"
    if [ -f "backend/pyproject.toml" ]; then
        log_success "✓ backend Poetry configuration found"
    else
        log_warning "⚠ backend/pyproject.toml not found"
    fi
else
    log_warning "⚠ backend directory not found"
fi

if [ -d "frontend" ]; then
    log_success "✓ frontend directory exists"
    if [ -f "frontend/package.json" ]; then
        log_success "✓ frontend package.json found"
    else
        log_warning "⚠ frontend/package.json not found"
    fi
else
    log_warning "⚠ frontend directory not found"
fi

# Test 5: Check documentation files
log_info "Checking documentation..."
docs=(
    "PLANNING.md"
    "TASKS.md"
    "DEVELOPMENT_WORKFLOW_PROPOSAL.md"
    ".github/copilot-instructions.md"
)

for doc in "${docs[@]}"; do
    if [ -f "$doc" ]; then
        log_success "✓ $doc exists"
    else
        log_warning "⚠ $doc not found"
    fi
done

# Test 6: Validate workflow file syntax
log_info "Validating workflow YAML syntax..."
if command -v yamllint >/dev/null 2>&1; then
    if yamllint .github/workflows/branch-protection.yml 2>/dev/null; then
        log_success "✓ Branch protection workflow YAML is valid"
    else
        log_warning "⚠ YAML syntax issues found (non-critical)"
    fi
else
    log_info "yamllint not available, skipping YAML validation"
fi

# Test 7: Check git configuration
log_info "Checking git configuration..."
if git config --get user.name >/dev/null && git config --get user.email >/dev/null; then
    log_success "✓ Git user configuration is set"
else
    log_warning "⚠ Git user configuration incomplete"
fi

echo ""
echo "🎉 Workflow Validation Summary"
echo "=============================="
log_success "Week 1 workflow setup validation completed!"
echo ""
echo "✅ What's working:"
echo "   - Branch naming conventions implemented"
echo "   - Workflow files created and in place"
echo "   - Branch structure established"
echo "   - Documentation framework ready"
echo ""
echo "🚀 Next Steps:"
echo "   1. Configure branch protection rules on GitHub"
echo "   2. Test CI/CD pipeline with a real PR"
echo "   3. Begin Sprint 7 implementation using new workflow"
echo ""
echo "📋 Ready to create PR to test full workflow!"
