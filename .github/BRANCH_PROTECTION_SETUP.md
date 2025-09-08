# Branch Protection Setup Guide

This document provides instructions for configuring branch protection rules to enforce the FamilyCart development workflow.

## 🛡️ Branch Protection Configuration

### Main Branch Protection Rules

Configure the following protection rules for the `main` branch:

#### Required Status Checks
- ✅ **Require status checks to pass before merging**
- ✅ **Require branches to be up to date before merging**
- **Required status checks**:
  - `code-quality`
  - `security-scan`
  - `architecture-compliance`

#### Pull Request Requirements
- ✅ **Require a pull request before merging**
- ✅ **Require approvals**: 1 reviewer minimum
- ✅ **Dismiss stale PR approvals when new commits are pushed**
- ✅ **Require review from code owners** (if CODEOWNERS file exists)

#### Additional Restrictions
- ✅ **Restrict pushes that create new files**
- ✅ **Require signed commits** (recommended for production)
- ✅ **Include administrators** (apply rules to repo admins)
- ✅ **Allow force pushes**: ❌ Disabled
- ✅ **Allow deletions**: ❌ Disabled

### Develop Branch Protection Rules

Configure the following protection rules for the `develop` branch:

#### Required Status Checks
- ✅ **Require status checks to pass before merging**
- ✅ **Require branches to be up to date before merging**
- **Required status checks**:
  - `code-quality`
  - `security-scan`
  - `architecture-compliance`

#### Pull Request Requirements
- ✅ **Require a pull request before merging**
- ✅ **Require approvals**: 1 reviewer minimum (can be reduced to 0 for solo development)
- ✅ **Dismiss stale PR approvals when new commits are pushed**

#### Additional Restrictions
- ✅ **Include administrators** (apply rules to repo admins)
- ✅ **Allow force pushes**: ❌ Disabled
- ✅ **Allow deletions**: ❌ Disabled

## 🔧 GitHub CLI Configuration

Use GitHub CLI to configure branch protection programmatically:

```bash
# Install GitHub CLI if not already installed
# Visit: https://cli.github.com/

# Login to GitHub
gh auth login

# Configure main branch protection
gh api repos/:owner/:repo/branches/main/protection \
  --method PUT \
  --field required_status_checks='{"strict":true,"contexts":["code-quality","security-scan","architecture-compliance"]}' \
  --field enforce_admins=true \
  --field required_pull_request_reviews='{"required_approving_review_count":1,"dismiss_stale_reviews":true}' \
  --field restrictions=null

# Configure develop branch protection
gh api repos/:owner/:repo/branches/develop/protection \
  --method PUT \
  --field required_status_checks='{"strict":true,"contexts":["code-quality","security-scan","architecture-compliance"]}' \
  --field enforce_admins=true \
  --field required_pull_request_reviews='{"required_approving_review_count":1,"dismiss_stale_reviews":true}' \
  --field restrictions=null
```

## 🌐 Web Interface Configuration

### Step 1: Navigate to Branch Protection
1. Go to your repository on GitHub
2. Click **Settings** tab
3. Click **Branches** in the left sidebar
4. Click **Add rule** or edit existing rule

### Step 2: Configure Main Branch Rule
1. **Branch name pattern**: `main`
2. Check **Require a pull request before merging**
   - **Required number of reviewers**: 1
   - Check **Dismiss stale PR approvals when new commits are pushed**
3. Check **Require status checks to pass before merging**
   - Check **Require branches to be up to date before merging**
   - Add required status checks:
     - `code-quality`
     - `security-scan` 
     - `architecture-compliance`
4. Check **Include administrators**
5. Uncheck **Allow force pushes**
6. Uncheck **Allow deletions**
7. Click **Create** or **Save changes**

### Step 3: Configure Develop Branch Rule
Repeat Step 2 with:
- **Branch name pattern**: `develop`
- Same settings as main branch
- Consider reducing required reviewers to 0 for solo development

## 📋 Verification Checklist

After configuring branch protection, verify the following:

### Main Branch Verification
- [ ] Cannot push directly to main branch
- [ ] PR required to merge into main
- [ ] Status checks must pass before merge
- [ ] At least 1 reviewer approval required
- [ ] Stale reviews dismissed on new commits
- [ ] Force pushes blocked
- [ ] Branch deletions blocked

### Develop Branch Verification
- [ ] Cannot push directly to develop branch
- [ ] PR required to merge into develop
- [ ] Status checks must pass before merge
- [ ] Reviewer approval required (or waived for solo dev)
- [ ] Stale reviews dismissed on new commits
- [ ] Force pushes blocked
- [ ] Branch deletions blocked

### Workflow Integration Verification
- [ ] Branch protection CI workflow triggers on PRs
- [ ] Code quality checks run automatically
- [ ] Security scans complete successfully
- [ ] Architecture compliance checks pass
- [ ] PR templates appear for different branch types

## 🚨 Emergency Procedures

### Hotfix Emergency Access
For critical production issues, temporarily disable branch protection:

```bash
# Disable main branch protection (EMERGENCY ONLY)
gh api repos/:owner/:repo/branches/main/protection --method DELETE

# Re-enable after hotfix
gh api repos/:owner/:repo/branches/main/protection \
  --method PUT \
  --field required_status_checks='{"strict":true,"contexts":["code-quality","security-scan","architecture-compliance"]}' \
  --field enforce_admins=true \
  --field required_pull_request_reviews='{"required_approving_review_count":1,"dismiss_stale_reviews":true}' \
  --field restrictions=null
```

### Override Procedures
Repository administrators can override protection rules:
1. Use "Merge without waiting for requirements" option
2. Document override reason in PR comments
3. Follow up with post-merge review and testing

## 🔄 Maintenance

### Regular Reviews
- **Weekly**: Review failed status checks and patterns
- **Monthly**: Analyze PR metrics and review bottlenecks
- **Quarterly**: Update protection rules based on team growth

### Status Check Maintenance
- Monitor CI/CD pipeline reliability
- Update required status checks as workflows evolve
- Remove deprecated status checks promptly

### Team Scaling
- Adjust required reviewer count as team grows
- Consider code owner assignments for specific areas
- Update protection rules for new branch patterns

---

## 📖 Related Documentation
- [DEVELOPMENT_WORKFLOW_PROPOSAL.md](../../DEVELOPMENT_WORKFLOW_PROPOSAL.md) - Complete development workflow
- [.github/copilot-instructions.md](../copilot-instructions.md) - Branch naming conventions
- [Branch Protection CI](.github/workflows/branch-protection.yml) - Automated quality checks

For questions or issues with branch protection setup, refer to the [GitHub Branch Protection documentation](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/defining-the-mergeability-of-pull-requests/about-protected-branches).
