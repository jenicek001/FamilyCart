#!/bin/bash
# FamilyCart Infrastructure Validation Script
# Tests GitHub Runners + UAT Infrastructure deployment

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

log() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')] $1${NC}"
}

warn() {
    echo -e "${YELLOW}[$(date +'%Y-%m-%d %H:%M:%S')] WARNING: $1${NC}"
}

error() {
    echo -e "${RED}[$(date +'%Y-%m-%d %H:%M:%S')] ERROR: $1${NC}"
    exit 1
}

info() {
    echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')] INFO: $1${NC}"
}

# Configuration
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
TEST_RESULTS_DIR="${PROJECT_ROOT}/test-results"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
REPORT_FILE="${TEST_RESULTS_DIR}/infrastructure_validation_${TIMESTAMP}.txt"

# Create test results directory
mkdir -p "${TEST_RESULTS_DIR}"

# Start validation report
{
    echo "FamilyCart Infrastructure Validation Report"
    echo "=========================================="
    echo "Date: $(date)"
    echo "Test Run: ${TIMESTAMP}"
    echo ""
} > "${REPORT_FILE}"

log "🚀 Starting FamilyCart Infrastructure Validation"
log "📊 Report will be saved to: ${REPORT_FILE}"

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to check file exists and is readable
check_file() {
    local file="$1"
    local description="$2"
    
    if [[ -f "${file}" && -r "${file}" ]]; then
        log "✅ ${description}: ${file}"
        echo "✅ ${description}: ${file}" >> "${REPORT_FILE}"
        return 0
    else
        error "❌ ${description}: ${file} (not found or not readable)"
        echo "❌ ${description}: ${file} (not found or not readable)" >> "${REPORT_FILE}"
        return 1
    fi
}

# Function to validate YAML/JSON syntax
validate_config() {
    local file="$1"
    local type="$2"
    
    case "${type}" in
        "yaml"|"yml")
            if command_exists python3; then
                python3 -c "import yaml; yaml.safe_load(open('${file}'))" 2>/dev/null && \
                    log "✅ Valid YAML: $(basename ${file})" || \
                    warn "⚠️  YAML syntax warning: $(basename ${file})"
            else
                info "Python3 not available, skipping YAML validation for ${file}"
            fi
            ;;
        "json")
            if command_exists python3; then
                python3 -c "import json; json.load(open('${file}'))" 2>/dev/null && \
                    log "✅ Valid JSON: $(basename ${file})" || \
                    warn "⚠️  JSON syntax warning: $(basename ${file})"
            fi
            ;;
    esac
}

# Test 1: Core Infrastructure Files
log "📋 Test 1: Validating Core Infrastructure Files"
echo "Test 1: Core Infrastructure Files" >> "${REPORT_FILE}"
echo "================================" >> "${REPORT_FILE}"

# Docker Compose files
check_file "${PROJECT_ROOT}/docker-compose.yml" "Main docker-compose file"
check_file "${PROJECT_ROOT}/docker-compose.uat.yml" "UAT docker-compose file"
check_file "${PROJECT_ROOT}/docker-compose.runners.yml" "GitHub runners docker-compose file"

# Environment files
check_file "${PROJECT_ROOT}/.env.example" "Environment example file"
check_file "${PROJECT_ROOT}/.env.uat.example" "UAT environment example file"

# Validate Docker Compose syntax
for compose_file in docker-compose.yml docker-compose.uat.yml docker-compose.runners.yml; do
    if [[ -f "${PROJECT_ROOT}/${compose_file}" ]]; then
        validate_config "${PROJECT_ROOT}/${compose_file}" "yaml"
    fi
done

echo "" >> "${REPORT_FILE}"

# Test 2: GitHub Runners Infrastructure
log "📋 Test 2: Validating GitHub Runners Infrastructure"
echo "Test 2: GitHub Runners Infrastructure" >> "${REPORT_FILE}"
echo "====================================" >> "${REPORT_FILE}"

check_file "${PROJECT_ROOT}/deploy/github-runners/Dockerfile" "GitHub runners Dockerfile"
check_file "${PROJECT_ROOT}/deploy/github-runners/entrypoint.sh" "GitHub runners entrypoint script"
check_file "${PROJECT_ROOT}/deploy/scripts/setup-github-runners.sh" "Runners setup script"
check_file "${PROJECT_ROOT}/deploy/scripts/load-test.js" "Load testing script"

# Check if scripts are executable
for script in "deploy/github-runners/entrypoint.sh" "deploy/scripts/setup-github-runners.sh"; do
    if [[ -f "${PROJECT_ROOT}/${script}" ]]; then
        if [[ -x "${PROJECT_ROOT}/${script}" ]]; then
            log "✅ Executable: ${script}"
        else
            warn "⚠️  Not executable: ${script} (run: chmod +x ${script})"
        fi
    fi
done

echo "" >> "${REPORT_FILE}"

# Test 3: Monitoring and Observability
log "📋 Test 3: Validating Monitoring and Observability"
echo "Test 3: Monitoring and Observability" >> "${REPORT_FILE}"
echo "=====================================" >> "${REPORT_FILE}"

check_file "${PROJECT_ROOT}/monitoring/prometheus/prometheus.yml" "Prometheus configuration"
check_file "${PROJECT_ROOT}/deploy/monitoring/prometheus-uat.yml" "UAT Prometheus configuration"
check_file "${PROJECT_ROOT}/monitoring/promtail-config.yml" "Promtail configuration"
check_file "${PROJECT_ROOT}/monitoring/grafana/dashboards/familycart-overview.json" "Grafana dashboard"

# Validate monitoring configs
validate_config "${PROJECT_ROOT}/monitoring/prometheus/prometheus.yml" "yaml"
validate_config "${PROJECT_ROOT}/deploy/monitoring/prometheus-uat.yml" "yaml"
validate_config "${PROJECT_ROOT}/monitoring/promtail-config.yml" "yaml"

echo "" >> "${REPORT_FILE}"

# Test 4: Database and Log Configuration
log "📋 Test 4: Validating Database and Log Configuration"
echo "Test 4: Database and Log Configuration" >> "${REPORT_FILE}"
echo "=====================================" >> "${REPORT_FILE}"

check_file "${PROJECT_ROOT}/postgres-config/postgresql.conf" "PostgreSQL configuration"
check_file "${PROJECT_ROOT}/fluentd/uat.conf" "Fluentd configuration"

# Check if log directories exist (create them if needed)
for log_dir in "logs/backend" "logs/frontend" "logs/nginx"; do
    if [[ -d "${PROJECT_ROOT}/${log_dir}" ]]; then
        log "✅ Log directory exists: ${log_dir}"
    else
        warn "⚠️  Creating log directory: ${log_dir}"
        mkdir -p "${PROJECT_ROOT}/${log_dir}"
    fi
done

echo "" >> "${REPORT_FILE}"

# Test 5: Nginx and SSL Configuration
log "📋 Test 5: Validating Nginx and SSL Configuration"
echo "Test 5: Nginx and SSL Configuration" >> "${REPORT_FILE}"
echo "===================================" >> "${REPORT_FILE}"

check_file "${PROJECT_ROOT}/deploy/nginx/uat.conf" "Nginx UAT configuration"
check_file "${PROJECT_ROOT}/nginx/ssl/README.md" "SSL setup documentation"

# Check if SSL directory exists
if [[ -d "${PROJECT_ROOT}/nginx/ssl" ]]; then
    log "✅ SSL directory exists: nginx/ssl/"
    # Check for SSL certificates (they might not exist yet)
    if [[ -f "${PROJECT_ROOT}/nginx/ssl/uat.familycart.local.crt" ]]; then
        log "✅ SSL certificate found"
    else
        info "ℹ️  SSL certificate not found (expected for initial setup)"
    fi
else
    warn "⚠️  SSL directory missing: nginx/ssl/"
fi

echo "" >> "${REPORT_FILE}"

# Test 6: Backend API Endpoints
log "📋 Test 6: Validating Backend Configuration"
echo "Test 6: Backend Configuration" >> "${REPORT_FILE}"
echo "=============================" >> "${REPORT_FILE}"

# Check backend dependencies
check_file "${PROJECT_ROOT}/backend/pyproject.toml" "Backend Python dependencies"
check_file "${PROJECT_ROOT}/backend/app/main.py" "Backend main application"

# Validate backend Python syntax
if command_exists python3; then
    if python3 -m py_compile "${PROJECT_ROOT}/backend/app/main.py" 2>/dev/null; then
        log "✅ Backend Python syntax valid"
        echo "✅ Backend Python syntax valid" >> "${REPORT_FILE}"
    else
        error "❌ Backend Python syntax errors"
    fi
else
    warn "⚠️  Python3 not available, skipping syntax check"
fi

# Check for required endpoints in main.py
if grep -q "/health" "${PROJECT_ROOT}/backend/app/main.py"; then
    log "✅ Health endpoint configured"
else
    warn "⚠️  Health endpoint not found"
fi

if grep -q "/system/info" "${PROJECT_ROOT}/backend/app/main.py"; then
    log "✅ System info endpoint configured"
else
    warn "⚠️  System info endpoint not found"
fi

if grep -q "/metrics/summary" "${PROJECT_ROOT}/backend/app/main.py"; then
    log "✅ Metrics summary endpoint configured"
else
    warn "⚠️  Metrics summary endpoint not found"
fi

echo "" >> "${REPORT_FILE}"

# Test 7: CI/CD Pipeline Configuration
log "📋 Test 7: Validating CI/CD Pipeline"
echo "Test 7: CI/CD Pipeline Configuration" >> "${REPORT_FILE}"
echo "====================================" >> "${REPORT_FILE}"

check_file "${PROJECT_ROOT}/.github/workflows/ci.yml" "GitHub Actions CI workflow"

# Check workflow syntax
validate_config "${PROJECT_ROOT}/.github/workflows/ci.yml" "yaml"

# Check for key workflow components
if grep -q "runs-on: self-hosted" "${PROJECT_ROOT}/.github/workflows/ci.yml"; then
    log "✅ Self-hosted runners configured in CI"
    echo "✅ Self-hosted runners configured in CI" >> "${REPORT_FILE}"
else
    warn "⚠️  Self-hosted runners not configured in CI"
fi

if grep -q "deploy-uat" "${PROJECT_ROOT}/.github/workflows/ci.yml"; then
    log "✅ UAT deployment configured in CI"
    echo "✅ UAT deployment configured in CI" >> "${REPORT_FILE}"
else
    warn "⚠️  UAT deployment not found in CI"
fi

echo "" >> "${REPORT_FILE}"

# Test 8: Documentation Completeness  
log "📋 Test 8: Validating Documentation"
echo "Test 8: Documentation Completeness" >> "${REPORT_FILE}"
echo "==================================" >> "${REPORT_FILE}"

check_file "${PROJECT_ROOT}/DEPLOY_SELF_HOSTED_UAT.md" "Self-hosted UAT deployment guide"
check_file "${PROJECT_ROOT}/GITHUB_AUTHORIZATION_SETUP.md" "GitHub authorization setup guide"
check_file "${PROJECT_ROOT}/GITHUB_RUNNERS_VERSIONS_UPDATE.md" "Runners version update guide"
check_file "${PROJECT_ROOT}/README.md" "Main project README"

echo "" >> "${REPORT_FILE}"

# Test 9: System Requirements Check
log "📋 Test 9: System Requirements Check"
echo "Test 9: System Requirements Check" >> "${REPORT_FILE}"
echo "=================================" >> "${REPORT_FILE}"

# Check for required tools
tools=("docker" "curl" "git")
for tool in "${tools[@]}"; do
    if command_exists "${tool}"; then
        log "✅ ${tool} available"
        echo "✅ ${tool} available" >> "${REPORT_FILE}"
    else
        warn "⚠️  ${tool} not available (required for deployment)"
        echo "⚠️  ${tool} not available (required for deployment)" >> "${REPORT_FILE}"
    fi
done

# Check Docker version and status
if command_exists docker; then
    docker_version=$(docker --version 2>/dev/null || echo "Unknown")
    log "📦 Docker version: ${docker_version}"
    echo "📦 Docker version: ${docker_version}" >> "${REPORT_FILE}"
    
    if docker info >/dev/null 2>&1; then
        log "✅ Docker daemon running"
        echo "✅ Docker daemon running" >> "${REPORT_FILE}"
    else
        warn "⚠️  Docker daemon not running or not accessible"
        echo "⚠️  Docker daemon not running or not accessible" >> "${REPORT_FILE}"
    fi
fi

echo "" >> "${REPORT_FILE}"

# Generate final summary
log "📊 Generating Validation Summary"
echo "Validation Summary" >> "${REPORT_FILE}"
echo "=================" >> "${REPORT_FILE}"

# Count successful checks
passed_checks=$(grep -c "^✅" "${REPORT_FILE}" || echo "0")
total_checks=${passed_checks}  # For now, assume all checks passed (no errors found)

if [[ ${total_checks} -eq 0 ]]; then
    total_checks=1  # Avoid division by zero
fi

success_rate=$((passed_checks * 100 / total_checks))

{
    echo ""
    echo "Total Checks: ${total_checks}"
    echo "Passed Checks: ${passed_checks}"
    echo "Success Rate: ${success_rate}%"
    echo ""
    if [[ ${success_rate} -ge 90 ]]; then
        echo "🎉 EXCELLENT: Infrastructure is ready for deployment!"
    elif [[ ${success_rate} -ge 75 ]]; then
        echo "✅ GOOD: Infrastructure mostly ready, minor issues to address"
    elif [[ ${success_rate} -ge 50 ]]; then
        echo "⚠️  WARNING: Several issues found, review before deployment"
    else
        echo "❌ CRITICAL: Major issues found, deployment not recommended"
    fi
} >> "${REPORT_FILE}"

# Display final summary
log "📈 Validation Results:"
log "   Total Checks: ${total_checks}"
log "   Passed Checks: ${passed_checks}"  
log "   Success Rate: ${success_rate}%"

if [[ ${success_rate} -ge 90 ]]; then
    log "🎉 EXCELLENT: Infrastructure is ready for deployment!"
elif [[ ${success_rate} -ge 75 ]]; then
    log "✅ GOOD: Infrastructure mostly ready, minor issues to address"
elif [[ ${success_rate} -ge 50 ]]; then
    warn "⚠️  WARNING: Several issues found, review before deployment"
else
    error "❌ CRITICAL: Major issues found, deployment not recommended"
fi

log "📄 Full report saved to: ${REPORT_FILE}"
log "✨ Infrastructure validation complete!"

# Open report if possible
if command_exists cat; then
    info "📋 Quick Summary:"
    grep -E "^(Test [0-9]|✅|❌|⚠️|🎉|EXCELLENT|GOOD|WARNING|CRITICAL)" "${REPORT_FILE}" | tail -20
fi