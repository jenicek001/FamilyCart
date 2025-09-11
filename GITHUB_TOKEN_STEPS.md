# 🔐 GitHub Token Creation Steps

## Quick Steps:

### 1. Open URL:
```
https://github.com/settings/tokens/new
```

### 2. Token Settings:
- **Name**: `FamilyCart-Full-Access-2025`
- **Expiration**: `90 days` (or No expiration)
- **Description**: `Full access for FamilyCart, GHCR, and MCP`

### 3. Required Scopes (check ALL of these):

#### Core Repository Access:
- ✅ `repo` (Full control of private repositories)
  - ✅ `repo:status` (Access commit status)
  - ✅ `repo_deployment` (Access deployment status)
  - ✅ `public_repo` (Access public repositories)
  - ✅ `repo:invite` (Access repository invitations)
  - ✅ `security_events` (Read and write security events)

#### Package Management (GHCR):
- ✅ `write:packages` (Upload packages to GitHub Package Registry)
- ✅ `read:packages` (Download packages from GitHub Package Registry)
- ✅ `delete:packages` (Delete packages from GitHub Package Registry)

#### GitHub Actions & Workflows:
- ✅ `workflow` (Update GitHub Action workflows)

#### Webhooks & Integration:
- ✅ `admin:repo_hook` (Full control of repository hooks)
- ✅ `admin:org_hook` (Full control of organization hooks)

#### User & Organization Access (for GitHub MCP):
- ✅ `read:user` (Read ALL user profile data)
- ✅ `user:email` (Access user email addresses)
- ✅ `read:org` (Read org and team membership, read org projects)

#### Additional GitHub MCP Features:
- ✅ `gist` (Create gists)
- ✅ `notifications` (Access notifications)
- ✅ `read:project` (Read access to user and public projects)

#### Optional (for enhanced features):
- ✅ `read:gpg_key` (View GPG keys)
- ✅ `read:ssh_signing_key` (View SSH signing keys)

### 4. Generate & Copy Token
- Click **"Generate token"**
- Copy the token immediately (starts with `ghp_`)
- ⚠️ **You can't see it again!**

### 5. Update Your System
```bash
./update-github-token.sh 'ghp_your_actual_token_here'
```

## Next Steps After Token:
1. `./push-docker-images.sh` - Push to GHCR
2. `cd /opt/familycart-uat-repo && ./deploy-uat.sh` - Deploy UAT
