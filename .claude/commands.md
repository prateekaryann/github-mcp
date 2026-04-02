# Common Commands

## Prerequisites

```bash
# Install GitHub CLI
brew install gh          # macOS
sudo apt install gh      # Ubuntu
winget install GitHub.cli  # Windows

# Authenticate
gh auth login
gh auth status
```

## Setup

```bash
# First time setup
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Development

```bash
# Activate environment
source venv/bin/activate

# Run MCP server (stdio mode)
python server.py

# Test imports
python -c "from server import mcp; print('OK')"
```

## Testing gh Commands

```bash
# Auth
gh auth status
gh api user --jq '.login'

# Repos
gh repo list --limit 5
gh repo view owner/repo

# Create test repo (delete after)
gh repo create test-repo --public --clone
gh repo delete prateekaryann/test-repo --yes

# Issues
gh issue list --repo owner/repo
gh issue create --repo owner/repo --title "Test" --body "Testing"

# PRs
gh pr list --repo owner/repo

# Search
gh search repos "fastapi language:python stars:>100"
```

## Git Operations

```bash
# Init and push existing project
cd /path/to/project
git init
git add .
git commit -m "Initial commit"
gh repo create my-repo --public --source . --push

# Quick commit and push
git add .
git commit -m "fix: description"
git push
```

## Adding New Tools

1. Add `@mcp.tool()` decorated function to `server.py`
2. Test the underlying `gh` command manually
3. Restart Claude Desktop to pick up new tool
