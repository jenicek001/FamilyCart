#!/bin/bash

# =============================================================================
# FamilyCart Code Quality Debug and Fix Script
# =============================================================================
# This script identifies and fixes common code quality issues that cause 
# CI/CD pipeline failures
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

echo "🔧 FamilyCart Code Quality Debug & Fix"
echo "====================================="

# Check current directory
if [ ! -f "pyproject.toml" ]; then
    log_error "Not in backend directory. Run from backend/ folder."
    exit 1
fi

log_info "Current directory: $(pwd)"

# Function to run and show results
run_check() {
    local check_name="$1"
    local command="$2"
    local fix_command="${3:-}"
    
    echo ""
    log_info "🔍 Running $check_name..."
    
    if eval "$command"; then
        log_success "✅ $check_name passed"
        return 0
    else
        log_error "❌ $check_name failed"
        
        if [ -n "$fix_command" ]; then
            log_info "🔧 Attempting to fix with: $fix_command"
            if eval "$fix_command"; then
                log_success "✅ $check_name fixed successfully"
                # Re-run the check
                if eval "$command"; then
                    log_success "✅ $check_name now passes"
                    return 0
                else
                    log_error "❌ $check_name still failing after fix attempt"
                    return 1
                fi
            else
                log_error "❌ Fix command failed"
                return 1
            fi
        else
            log_warning "⚠️  No automatic fix available for $check_name"
            return 1
        fi
    fi
}

# Main debugging sequence
main() {
    log_info "Starting comprehensive code quality debugging..."
    
    # 1. Black formatting check
    run_check "Black Formatting" \
        "poetry run black --check . --quiet" \
        "poetry run black ."
    
    # 2. Import sorting check
    run_check "Import Sorting (isort)" \
        "poetry run isort --check-only . --quiet" \
        "poetry run isort ."
    
    # 3. PyLint code quality check
    log_info "🔍 Running PyLint Code Quality..."
    if poetry run pylint app/ --disable=C0114,C0116,R0903,W0613 --fail-under=8.0 --score=y; then
        log_success "✅ PyLint passed"
    else
        log_error "❌ PyLint failed - score below 8.0"
        log_warning "⚠️  Check specific PyLint issues above"
    fi
    
    # 4. Bandit security check
    log_info "🔍 Running Bandit Security Scan..."
    if poetry run bandit -r app/ -f json -o bandit-report.json --quiet; then
        # Check for high/medium severity issues
        high_issues=$(poetry run bandit -r app/ -f json --quiet | jq '.results[] | select(.issue_severity == "HIGH" or .issue_severity == "MEDIUM")' 2>/dev/null | wc -l || echo "0")
        if [ "$high_issues" -gt 0 ]; then
            log_error "❌ Bandit found $high_issues high/medium security issues"
        else
            log_success "✅ Bandit security scan passed"
        fi
    else
        log_error "❌ Bandit security scan failed"
    fi
    
    # 5. Test discovery
    log_info "🔍 Checking PyTest Test Discovery..."
    if poetry run pytest --collect-only --quiet >/dev/null 2>&1; then
        log_success "✅ PyTest can discover tests"
    else
        log_error "❌ PyTest test discovery failed"
    fi
    
    # 6. Check for common issues
    log_info "🔍 Checking for common code issues..."
    
    # Check for files over 500 lines
    large_files=$(find app/ -name "*.py" | xargs wc -l | awk '$1 > 500 {print $2 " (" $1 " lines)"}' | grep -v total || true)
    if [ -n "$large_files" ]; then
        log_warning "⚠️  Files over 500 lines found:"
        echo "$large_files"
    else
        log_success "✅ All files under 500 lines"
    fi
    
    # Summary
    echo ""
    log_info "🎯 Code Quality Debug Summary"
    echo "=========================="
    
    # Re-run all checks for final status
    local all_passed=true
    
    if ! poetry run black --check . --quiet >/dev/null 2>&1; then
        log_error "❌ Black formatting issues remain"
        all_passed=false
    fi
    
    if ! poetry run isort --check-only . --quiet >/dev/null 2>&1; then
        log_error "❌ Import sorting issues remain"
        all_passed=false
    fi
    
    if ! poetry run pylint app/ --disable=C0114,C0116,R0903,W0613 --fail-under=8.0 >/dev/null 2>&1; then
        log_error "❌ PyLint issues remain"
        all_passed=false
    fi
    
    if [ "$all_passed" = true ]; then
        log_success "🎉 All code quality checks now pass!"
        echo ""
        echo "Your code is ready for PR submission. The CI/CD pipeline should now pass."
        echo ""
        echo "Next steps:"
        echo "1. Commit the formatting fixes: git add . && git commit -m 'style: fix code formatting and imports'"
        echo "2. Push changes: git push"
        echo "3. Check CI/CD pipeline status on GitHub"
    else
        log_error "❌ Some issues remain - check output above"
        echo ""
        echo "Manual fixes may be required for:"
        echo "- PyLint code quality issues (complex logic, long functions, etc.)"
        echo "- Security issues identified by Bandit"
        echo "- Test discovery problems"
    fi
}

# Run main function
main "$@"
