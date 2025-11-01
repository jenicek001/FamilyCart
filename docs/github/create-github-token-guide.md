# 🔐 GitHub Personal Access Token Setup Guide

## Step 1: Create the Token

1. **Go to GitHub Settings**:
   ```
   https://github.com/settings/tokens/new
   ```

2. **Token Configuration**:
   - **Token name**: `FamilyCart-Full-Access-2025`
   - **Expiration**: `90 days` (or `No expiration` for development)
   - **Description**: `Full access for FamilyCart development, GHCR, and MCP`

3. **Select Required Scopes**:

### Core Repository Access
- ✅ **repo** (Full control of private repositories)
  - ✅ repo:status
  - ✅ repo_deployment  
  - ✅ public_repo
  - ✅ repo:invite
  - ✅ security_events

### Package Management (GHCR)
- ✅ **write:packages** (Upload packages to GitHub Package Registry)
- ✅ **read:packages** (Download packages from GitHub Package Registry)
- ✅ **delete:packages** (Delete packages from GitHub Package Registry)

### GitHub Actions & Workflows
- ✅ **workflow** (Update GitHub Action workflows)

### Webhooks & Integration
- ✅ **admin:repo_hook** (Full control of repository hooks)
- ✅ **admin:org_hook** (Full control of organization hooks)

### User & Organization Access (for MCP)
- ✅ **read:user** (Read ALL user profile data)
- ✅ **user:email** (Access user email addresses)
- ✅ **read:org** (Read org and team membership, read org projects)

### Additional MCP Features
- ✅ **gist** (Create gists)
- ✅ **notifications** (Access notifications)
- ✅ **read:project** (Read access to user and public projects)

### Optional (if using GitHub Apps)
- ✅ **read:gpg_key** (View GPG keys)
- ✅ **read:ssh_signing_key** (View SSH signing keys)

## Step 2: Save the Token Securely

### Environment Variable Method:
```bash
# Add to ~/.bashrc or ~/.zshrc
export GITHUB_TOKEN="ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
export CR_PAT="$GITHUB_TOKEN"  # For container registry
```

### .env File Method:
```bash
# Create .env file in project root
echo "GITHUB_TOKEN=ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx" > .env
echo "CR_PAT=\$GITHUB_TOKEN" >> .env
echo ".env" >> .gitignore
```

## Step 3: Test Token Access

### Test Repository Access:
```bash
curl -H "Authorization: token $GITHUB_TOKEN" \
     https://api.github.com/user
```

### Test GHCR Access:
```bash
echo $CR_PAT | docker login ghcr.io -u USERNAME --password-stdin
```

### Test Package Push:
```bash
docker tag local-image ghcr.io/jenicek001/test:latest
docker push ghcr.io/jenicek001/test:latest
```

## Security Best Practices

1. **Store securely**: Never commit tokens to git
2. **Use environment variables**: Avoid hardcoding in scripts
3. **Regular rotation**: Update tokens every 90 days
4. **Minimal scope**: Only grant necessary permissions
5. **Monitor usage**: Check token activity regularly

## Troubleshooting

### "denied: permission_denied" errors:
- Verify token has `write:packages` scope
- Check repository visibility settings
- Ensure organization allows package publishing

### MCP Server authentication failures:
- Verify token has `read:user` and `read:org` scopes
- Check token expiration date
- Test token with GitHub API directly

