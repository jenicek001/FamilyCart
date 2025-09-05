# GitHub Runners Latest Versions Update

## Overview
Updated all GitHub runner infrastructure to use the latest stable versions of tools and dependencies as of September 2025.

## Version Updates Applied

### Core Runtime Versions
- **GitHub Actions Runner**: v2.317.0 ✅ (already latest)
- **Base OS**: Ubuntu 22.04 LTS ✅ (already latest LTS)
- **Docker**: Latest stable from official Docker repository (28.x+)
- **Node.js**: v22.17.0 (upgraded from v20, latest LTS)
- **Python**: 3.12 (upgraded from 3.11, latest stable)
- **Poetry**: 2.x (latest stable, auto-detects latest version)

### Development Tools (Latest @latest versions)
- **TypeScript**: Latest stable
- **ESLint**: Latest stable  
- **Prettier**: Latest stable
- **Playwright**: Latest stable
- **Python tools**: black, isort, pylint, bandit, pytest, pytest-cov

### Security & Testing Tools
- **Trivy**: Latest from GitHub releases (security scanning)
- **k6**: Latest from GitHub releases (load testing)

### Infrastructure Improvements
- **Docker installation**: Switched from convenience script to official APT repository for better version control
- **Package management**: Updated to use official repositories with proper GPG keys
- **Health check**: Extended startup time to 60s for more reliable container health detection
- **Labels**: Added proper OCI image labels with creation timestamp and source

## Files Updated

### `/deploy/github-runners/Dockerfile`
- Updated base system packages and installation methods
- Switched to Node.js 22 (LTS)
- Upgraded to Python 3.12 with proper virtual environment support
- Updated Poetry installation to use latest 2.x version
- Enhanced security scanning and testing tools
- Improved Docker layer caching with proper package cleanup

### `/deploy/github-runners/configure-runner.sh`
- Created missing configuration script referenced in Dockerfile
- Added proper error handling and logging
- Supports flexible configuration options

### `/deploy/deploy-github-runners.sh`
- Enhanced system information display
- Added Node.js and Poetry version checks
- Improved deployment reliability

## Context7 MCP Integration
Used Context7 MCP server to verify latest versions for:
- GitHub Actions Runner (from /actions/runner)
- Docker (from /docker/docs) 
- Node.js (from /nodejs/node)
- Poetry (from /websites/python-poetry)

## Security Considerations
- All tools installed from official sources with proper verification
- GPG keys validated for package repositories  
- Latest security patches included via updated base packages
- Container runs with proper user permissions (non-root where possible)

## Performance Optimizations
- Multi-layer Docker build with optimized caching
- Latest npm packages for improved build performance
- Updated k6 for better load testing capabilities
- Enhanced health check timing for reliable startup detection

## Next Steps
1. Deploy updated GitHub runners to UAT server
2. Test CI/CD pipeline with new runner versions
3. Monitor performance improvements vs GitHub-hosted runners
4. Validate all development tools work correctly with latest versions

## Rollback Plan
- Previous Dockerfile configuration preserved in git history
- Can quickly revert to stable versions if issues arise
- Deployment script supports version pinning for emergency rollbacks

---
**Updated**: September 5, 2025  
**Context7 Verified**: All versions checked against latest official documentation
