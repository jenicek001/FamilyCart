# 🤖 GitHub MCP Server Setup Guide

## What is GitHub MCP Server?

The GitHub MCP (Model Context Protocol) Server connects AI tools directly to GitHub, enabling:
- 🔍 **Repository Management** via natural language
- 🐛 **Issue/PR Automation** with AI assistance  
- 🔄 **CI/CD Intelligence** for workflow insights
- 🔍 **Code Analysis** across repositories
- 👥 **Team Collaboration** enhancement

## Installation Options

### Option 1: VS Code (Recommended)

1. **Add to VS Code settings.json**:
```json
{
  "mcp": {
    "servers": {
      "github": {
        "type": "http",
        "url": "https://api.githubcopilot.com/mcp/",
        "headers": {
          "Authorization": "Bearer ${input:github_mcp_pat}"
        }
      }
    },
    "inputs": [
      {
        "type": "promptString",
        "id": "github_mcp_pat",
        "description": "GitHub Personal Access Token",
        "password": true
      }
    ]
  }
}
```

### Option 2: Docker (Local)

```bash
# Run GitHub MCP Server via Docker
docker run -i --rm \
  -e GITHUB_PERSONAL_ACCESS_TOKEN="$GITHUB_TOKEN" \
  ghcr.io/github/github-mcp-server
```

### Option 3: Claude Desktop

1. **Add to claude_desktop_config.json**:
```json
{
  "mcpServers": {
    "github": {
      "command": "docker",
      "args": [
        "run", "-i", "--rm", 
        "-e", "GITHUB_PERSONAL_ACCESS_TOKEN",
        "ghcr.io/github/github-mcp-server"
      ],
      "env": {
        "GITHUB_PERSONAL_ACCESS_TOKEN": "YOUR_GITHUB_TOKEN"
      }
    }
  }
}
```

### Option 4: Cursor IDE

```json
{
  "mcpServers": {
    "github": {
      "url": "https://api.githubcopilot.com/mcp/",
      "headers": {
        "Authorization": "Bearer YOUR_GITHUB_TOKEN"
      }
    }
  }
}
```

## Available MCP Toolsets

Enable specific toolsets based on your needs:

```bash
# Enable specific toolsets
GITHUB_TOOLSETS="repos,issues,pull_requests,actions,code_security" ./github-mcp-server

# Enable all toolsets  
GITHUB_TOOLSETS="all" ./github-mcp-server
```

### Core Toolsets:
- **repos**: Repository management
- **issues**: Issue tracking and management
- **pull_requests**: PR creation, review, merging
- **actions**: GitHub Actions workflow access
- **code_security**: Security scanning and advisories
- **users**: User and team management
- **packages**: Package/container management

## Usage Examples

### Repository Operations:
```
"List all repositories in jenicek001 organization"
"Create a new repository called 'test-repo'"  
"Get the latest commit from main branch"
```

### Issue Management:
```
"Show all open issues in FamilyCart repository"
"Create an issue for SSL certificate renewal"
"Assign issue #123 to @jenicek001"
```

### Pull Request Workflow:
```
"Create a PR from feature/nginx-modular to main"
"Review PR #45 and check for conflicts"  
"Merge PR #67 using squash merge"
```

### Actions & CI/CD:
```
"Show latest workflow runs for FamilyCart"
"Trigger manual deployment to UAT environment"
"Check status of current CI pipeline"
```

## Security & Authentication

### Token Permissions Required:
- ✅ `repo` - Full repository access
- ✅ `read:user` - User profile information  
- ✅ `read:org` - Organization membership
- ✅ `workflow` - GitHub Actions access
- ✅ `read:packages` - Package registry access

### Best Practices:
1. **Use environment variables** for token storage
2. **Enable SSO enforcement** if using organization repositories
3. **Regular token rotation** (90-day expiration recommended)
4. **Monitor token usage** via GitHub Settings > Developer settings

## Testing Your Setup

```bash
# Test MCP server connection
curl -H "Authorization: Bearer $GITHUB_TOKEN" \
     https://api.githubcopilot.com/mcp/

# Test with specific toolset
curl -H "Authorization: Bearer $GITHUB_TOKEN" \
     -H "X-MCP-Toolsets: repos,issues" \
     https://api.githubcopilot.com/mcp/x/repos
```

## Integration with FamilyCart

Once configured, you can use natural language for:

### Development Workflow:
- "Show me the latest commits on feature/workflow-test-demo"
- "Create an issue for implementing SSL auto-renewal"
- "Check if there are any failing tests in recent PRs"

### Deployment Management:
- "List all Docker images in GHCR for FamilyCart"
- "Show workflow runs for UAT deployment"
- "Create a release for version 2.1.0"

### Team Collaboration:
- "Assign the nginx configuration issue to the DevOps team"
- "Schedule a review for the database migration PR"
- "Notify team about successful production deployment"

