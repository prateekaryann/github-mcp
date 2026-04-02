# GitHub MCP Server

## Project Overview

This is a **Model Context Protocol (MCP)** server that wraps the GitHub CLI (`gh`) to provide GitHub operations directly from Claude Desktop/Code. It enables Claude to create repos, push code, manage issues, and more.

**Owner**: Prateek Aryan (@prateekaryann)  
**Stack**: Python 3.10+, FastMCP, GitHub CLI (gh)  
**Purpose**: Seamless GitHub integration for Claude - push code, manage repos without leaving the chat

---

## Quick Start (Local Development)

```bash
# 1. Ensure GitHub CLI is installed
gh --version  # Should show version

# 2. Authenticate if not already
gh auth login
gh auth status  # Verify: ✓ Logged in to github.com as prateekaryann

# 3. Navigate to project
cd ~/projects/github-mcp

# 4. Create/activate virtual environment
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 5. Install dependencies
pip install -r requirements.txt

# 6. Run the server
python server.py
```

---

## Architecture

```
github-mcp/
├── server.py         # Main MCP server - all tools in one file
├── requirements.txt  # Just fastmcp>=2.0.0
├── README.md
├── LICENSE
└── .claude/
    └── CLAUDE.md     # This file
```

**Design Philosophy**: Single-file server wrapping `gh` CLI commands via subprocess.

---

## Key Components

### Helper Functions

```python
def run_gh(args: list[str], cwd: Optional[str] = None) -> dict:
    """Run gh CLI command, return {success, output, error}"""

def run_git(args: list[str], cwd: Optional[str] = None) -> dict:
    """Run git command, return {success, output, error}"""
```

### MCP Tools

| Category | Tool | Description |
|----------|------|-------------|
| **Auth** | `auth_status` | Check gh auth status |
| | `whoami` | Get authenticated username |
| **Repos** | `create_repo` | Create new GitHub repo |
| | `list_repos` | List user/org repos |
| | `repo_view` | View repo details |
| | `clone_repo` | Clone repo locally |
| | `delete_repo` | Delete repo (with confirmation) |
| **Git** | `git_status` | Get local repo status |
| | `git_add_commit_push` | Add, commit, push in one command |
| | `git_init_and_push` | Init local dir + create GitHub repo + push |
| | `git_pull` | Pull latest changes |
| **Issues** | `create_issue` | Create new issue |
| | `list_issues` | List repo issues |
| **PRs** | `create_pr` | Create pull request |
| | `list_prs` | List pull requests |
| **Other** | `create_gist` | Create GitHub gist |
| | `search_repos` | Search GitHub repos |
| | `create_release` | Create GitHub release |

---

## Common Tasks

### Add a New Tool

1. Add function with `@mcp.tool()` decorator:
```python
@mcp.tool()
def my_new_tool(param1: str, param2: int = 10) -> str:
    """
    Tool description shown to Claude.
    
    Args:
        param1: Description of param1
        param2: Description with default
        
    Returns:
        What the tool returns
    """
    result = run_gh(["some", "command", param1])
    
    if result["success"]:
        return f"✅ Success\n\n{result['output']}"
    else:
        return f"❌ Failed: {result['error']}"
```

2. Test it manually:
```bash
gh some command test_value  # Verify the underlying command works
```

### Add GitHub API Endpoint

For operations not supported by `gh` CLI directly, use `gh api`:
```python
@mcp.tool()
def get_repo_languages(repo: str) -> str:
    """Get languages used in a repository."""
    result = run_gh(["api", f"repos/{repo}/languages"])
    # result["output"] will be JSON
    return result["output"] if result["success"] else result["error"]
```

### Handle User Confirmation for Dangerous Operations

```python
@mcp.tool()
def dangerous_operation(target: str, confirm: bool = False) -> str:
    """Do something dangerous."""
    if not confirm:
        return "⚠️ Set confirm=True to proceed. This cannot be undone!"
    
    # Proceed with operation
```

---

## Prerequisites

### GitHub CLI Installation

```bash
# macOS
brew install gh

# Ubuntu/Debian
sudo apt install gh

# Windows
winget install GitHub.cli

# Verify
gh --version
```

### Authentication

```bash
# Interactive login
gh auth login

# Check status
gh auth status

# Re-authenticate if needed
gh auth refresh
```

---

## Claude Desktop Integration

```json
{
  "mcpServers": {
    "github": {
      "command": "python",
      "args": ["/path/to/github-mcp/server.py"],
      "cwd": "/path/to/github-mcp"
    }
  }
}
```

**Config locations**:
- macOS: `~/Library/Application Support/Claude/claude_desktop_config.json`
- Windows: `%APPDATA%\Claude\claude_desktop_config.json`
- Linux: `~/.config/claude/claude_desktop_config.json`

---

## Environment

| Variable | Description | Default |
|----------|-------------|---------|
| `WORK_DIR` | Base directory for git operations | `~/projects` |

The server uses your existing `gh` authentication - no additional credentials needed.

---

## Coding Conventions

- **Single file**: Keep all tools in `server.py` for simplicity
- **Type hints**: All functions must have type hints
- **Docstrings**: Every tool needs a docstring (shown to Claude)
- **Error handling**: Always return user-friendly messages, never raw exceptions
- **Emojis**: Use ✅ ❌ ⚠️ ℹ️ 📁 🔀 📋 for visual feedback

---

## Testing

```bash
# Test gh CLI works
gh auth status
gh repo list --limit 3

# Test server imports
python -c "from server import mcp; print('OK')"

# Run server in stdio mode (Claude will connect)
python server.py
```

---

## Security Notes

- Runs `gh` and `git` commands via subprocess on your machine
- Uses your existing GitHub CLI authentication
- `delete_repo` requires explicit `confirm=True` parameter
- No credentials stored - relies entirely on `gh auth`

---

## Known Limitations

- Requires `gh` CLI installed and authenticated
- Commands timeout after 60-120 seconds
- Some operations require push access to repos
- Rate limited by GitHub API (5000 requests/hour authenticated)

---

## Memory Context

**Created by**: Prateek Aryan (Senior Software Engineer)  
**Primary use case**: Push MCP servers and projects to GitHub from Claude  
**Workflow**: Build in Claude → Push via this MCP → Iterate  
**GitHub username**: prateekaryann
