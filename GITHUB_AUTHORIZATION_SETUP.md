# GitHub Actions Authorization Setup

## 1. Create GitHub Personal Access Token (PAT)

Go to GitHub Settings → Developer settings → Personal access tokens → Tokens (classic):
https://github.com/settings/tokens

### Required Scopes:
- ✅ **repo** - Full control of private repositories
- ✅ **workflow** - Update GitHub Action workflows  
- ✅ **admin:org** - Full control of orgs and teams, read and write org projects
- ✅ **admin:public_key** - Full control of user public keys

### Token Name Suggestion:
`FamilyCart-SelfHosted-Runners-Production`

## 2. Repository Settings

### Enable Actions:
1. Go to your repository: https://github.com/jenicek001/FamilyCart
2. Settings → Actions → General
3. Enable "Allow all actions and reusable workflows"

### Runner Groups (if Organization):
1. Settings → Actions → Runner groups
2. Create group "FamilyCart-Production" 
3. Allow access to selected repositories

## 3. Deploy Runners with Token

Once you have the PAT token, run:

```bash
cd /home/honzik/GitHub/FamilyCart/FamilyCart/deploy
./deploy-github-runners.sh --token YOUR_GITHUB_PAT_TOKEN
```

## 4. Deployment Command Options

```bash
# Basic deployment
./deploy-github-runners.sh --token ghp_xxxxxxxxxxxxxxxxxxxx

# Deploy with specific configuration
./deploy-github-runners.sh \
  --token ghp_xxxxxxxxxxxxxxxxxxxx \
  --runners 2 \
  --github-url https://github.com/jenicek001/FamilyCart \
  --runner-group default \
  --labels "ubuntu-latest,familycart,uat"

# Deploy to production environment
./deploy-github-runners.sh \
  --token ghp_xxxxxxxxxxxxxxxxxxxx \
  --environment production \
  --runners 3 \
  --labels "production,familycart,high-performance"
```

## 5. Verify Deployment

After successful deployment, check:

1. **GitHub Repository Settings**:
   - Go to Settings → Actions → Runners
   - You should see your self-hosted runners listed as "Online"

2. **Local Docker Status**:
   ```bash
   docker ps | grep github-runner
   docker logs github-runner-1
   ```

3. **Runner Logs**:
   ```bash
   # Check runner registration
   docker exec github-runner-1 cat /actions-runner/_diag/Runner_*.log
   
   # Monitor runner activity
   docker logs -f github-runner-1
   ```

## 6. Test Your Runners

Push a commit to trigger the CI/CD pipeline and verify:
- Jobs run on your self-hosted runners
- Performance is better than GitHub-hosted runners
- All tests pass with your hardware configuration

## 7. Current Workflow Analysis

Your `.github/workflows/ci.yml` is already configured with:
- ✅ `runs-on: self-hosted`
- ✅ Comprehensive CI/CD pipeline
- ✅ Multi-environment deployment (UAT → Production)
- ✅ Security scanning with Trivy
- ✅ Container registry integration (ghcr.io)

## 8. Enhanced Performance Benefits

With self-hosted runners you'll get:
- 🚀 **Faster builds**: 16 CPU cores vs 2 on GitHub-hosted
- 💾 **Better caching**: Persistent Docker layer cache
- 🔒 **Network security**: Direct access to your UAT environment
- 💰 **Cost savings**: No GitHub Actions minutes usage
- ⚡ **Hardware control**: Latest Docker 28.3.3, Node.js 22.17.0, Python 3.12

## 9. Security Best Practices

- Store PAT token securely (use environment variable)
- Rotate tokens every 90 days
- Monitor runner logs for suspicious activity
- Keep runners updated with latest versions
- Use runner groups for access control

## 10. Troubleshooting

If runners don't connect:
```bash
# Check token permissions
curl -H "Authorization: token YOUR_TOKEN" https://api.github.com/user

# Verify network connectivity
curl -I https://github.com/jenicek001/FamilyCart

# Check runner logs
docker logs github-runner-1 --tail 100

# Restart runners
cd /home/honzik/GitHub/FamilyCart/FamilyCart/deploy
./deploy-github-runners.sh --restart --token YOUR_TOKEN
```

---

**Next Step**: Create your GitHub PAT token and run the deployment command!
