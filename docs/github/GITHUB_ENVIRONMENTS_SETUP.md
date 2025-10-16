# GitHub Environments and Secrets Setup Guide

This guide explains how to configure GitHub Environments and Secrets for the FamilyCart CI/CD pipeline.

## 🚀 Quick Setup Overview

The CI/CD pipeline uses **environment-specific secrets** for better security isolation:
- **UAT Environment**: For testing and staging deployments
- **Production Environment**: For production deployments

## 📋 Step 1: Create GitHub Environments

1. Go to your repository on GitHub
2. Click **Settings** → **Environments**
3. Click **New environment**

### Create UAT Environment
- **Name**: `uat`
- **Protection rules** (optional):
  - Required reviewers: Add team members who should approve UAT deployments
  - Wait timer: Set deployment delays if needed
  - Deployment branches: Restrict to `develop` branch

### Create Production Environment  
- **Name**: `production`
- **Protection rules** (recommended):
  - Required reviewers: Add team leads/ops team for production approvals
  - Wait timer: Consider a brief delay for rollback window
  - Deployment branches: Restrict to `main` branch only

## 🔐 Step 2: Configure Environment Secrets

### UAT Environment Secrets
Navigate to **Settings** → **Environments** → **uat** → **Add secret**

**Optional Secrets** (for remote UAT deployment):
- `UAT_HOST`: Hostname/IP of remote UAT server (e.g., `uat.familycart.com`)
- `UAT_USER`: Username for UAT server (e.g., `ubuntu` or `familycart`)  
- `UAT_SSH_KEY`: Private SSH key for UAT server access
- `UAT_BASE_URL`: UAT frontend URL (e.g., `https://uat.familycart.com`)
- `UAT_API_URL`: UAT backend URL (e.g., `https://uat-api.familycart.com`)

**Note**: If these secrets are not configured, UAT deployment will run locally on the self-hosted runner.

### Production Environment Secrets
Navigate to **Settings** → **Environments** → **production** → **Add secret**

**Required Secrets**:
- `PRODUCTION_SSH_KEY`: Private SSH key for production server
- `PRODUCTION_HOST`: Production server hostname/IP (e.g., `prod.familycart.com`)
- `PRODUCTION_USER`: Username for production server (e.g., `ubuntu`)
- `PRODUCTION_URL`: Production application URL (e.g., `https://familycart.com`)

## 🔧 Step 3: Generate SSH Keys (If Needed)

If you need to create SSH keys for server access:

```bash
# Generate SSH key pair
ssh-keygen -t ed25519 -C "familycart-ci-cd" -f familycart-deploy-key

# Add public key to target server
ssh-copy-id -i familycart-deploy-key.pub user@your-server.com

# Use private key content as GitHub secret
cat familycart-deploy-key  # Copy this content to GitHub secret
```

## 🏗️ Step 4: Server Preparation

### UAT Server Setup (if using remote UAT)
```bash
# Create deployment directory
sudo mkdir -p /opt/familycart-uat
sudo chown $USER:$USER /opt/familycart-uat

# Ensure Docker and Docker Compose are installed
docker --version
docker-compose --version

# Place docker-compose.uat.yml in /opt/familycart-uat/
```

### Production Server Setup
```bash
# Create deployment directory  
sudo mkdir -p /opt/familycart
sudo chown $USER:$USER /opt/familycart

# Ensure Docker and Docker Compose are installed
docker --version
docker-compose --version

# Place docker-compose.app.yml in /opt/familycart/
```

## ✅ Step 5: Verify Configuration

### Test UAT Deployment
1. Create a pull request to `develop` branch
2. Check that UAT deployment job runs without secret errors
3. Verify UAT application is accessible

### Test Production Deployment
1. Merge to `main` branch  
2. Check that production deployment requires approval (if configured)
3. Approve deployment and verify success
4. Verify production application is accessible

## 🔍 Troubleshooting

### "Context access might be invalid" Errors
- **Cause**: Secrets not configured in the specified environment
- **Solution**: Add the missing secrets to the correct environment in GitHub settings

### SSH Connection Failures
- **Check**: SSH key format (should be private key, not public)
- **Check**: Server firewall allows SSH connections
- **Check**: Username and hostname are correct
- **Test manually**: `ssh -i key user@host`

### Docker Compose Errors on Server
- **Check**: Docker daemon is running: `sudo systemctl status docker`
- **Check**: User has Docker permissions: `docker ps`
- **Check**: Compose file exists in expected location

## 🔒 Security Best Practices

1. **Principle of Least Privilege**: Only grant minimum required permissions
2. **Environment Isolation**: Use different SSH keys for UAT vs Production
3. **Key Rotation**: Regularly rotate SSH keys and update secrets
4. **Audit Access**: Monitor who has access to production environment
5. **Approval Gates**: Require manual approval for production deployments

## 📚 Additional Resources

- [GitHub Environments Documentation](https://docs.github.com/en/actions/deployment/targeting-different-environments/using-environments-for-deployment)
- [GitHub Secrets Documentation](https://docs.github.com/en/actions/security-guides/encrypted-secrets)
- [SSH Key Management Best Practices](https://docs.github.com/en/authentication/connecting-to-github-with-ssh)
