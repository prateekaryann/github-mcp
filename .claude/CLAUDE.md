# GitHub MCP Server

## Project Overview

This is a **Model Context Protocol (MCP)** server that wraps the GitHub CLI (`gh`) to provide 39 GitHub operations directly from Claude Desktop/Code/Web. It supports local (stdio) and remote (SSE + OAuth 2.0) transport modes with comprehensive security hardening.

**Owner**: Prateek Aryan (@prateekaryann)  
**Stack**: Python 3.10+, MCP SDK (`mcp[cli]`), GitHub CLI (`gh`), uvicorn, starlette  
**Repo**: github.com/prateekaryann/github-mcp  
**Purpose**: Seamless GitHub integration for Claude — push code, manage repos, PRs, issues, workflows without leaving the chat

---

## Quick Start (Local Development)

```bash
# 1. Ensure GitHub CLI is installed and authenticated
gh --version && gh auth status

# 2. Navigate to project
cd ~/projects/github-mcp

# 3. Create/activate virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 4. Install dependencies
pip install -r requirements.txt

# 5. Run the server (stdio mode for Claude Desktop/Code)
python server.py

# 6. Run in remote mode (SSE + OAuth for Claude.ai)
MCP_TRANSPORT=sse MCP_PORT=9000 MCP_SERVER_URL=https://your-tunnel.ngrok-free.dev python server.py
```

---

## Architecture

```
github-mcp/
├── server.py              # Main MCP server — 39 tools, security, transport (1773 lines)
├── oauth_provider.py      # In-memory OAuth 2.0 provider for Claude.ai (214 lines)
├── requirements.txt       # mcp[cli], uvicorn>=0.27.0, starlette>=0.36.0
├── .env.example           # Configuration template (all env vars documented)
├── tunnel.sh              # Bash: start server + ngrok tunnel
├── tunnel.ps1             # PowerShell: start server + ngrok tunnel
├── README.md              # Public documentation
├── LICENSE                # MIT
├── .gitignore
└── .claude/
    └── CLAUDE.md          # This file
```

**Design Philosophy**: Single-file server (`server.py`) wrapping `gh` CLI commands via subprocess. OAuth provider is separate (`oauth_provider.py`). All tools in one file for simplicity.

---

## Key Components

### Helper Functions

```python
def run_gh(args: list[str], cwd: Optional[str] = None) -> dict:
    """Run gh CLI command, return {success, output, error}"""

def run_git(args: list[str], cwd: Optional[str] = None) -> dict:
    """Run git command, return {success, output, error}"""
```

### Security Functions

```python
def validate_path(repo_path: str) -> str:       # Sandbox to WORK_DIR
def validate_repo_name(repo: str) -> str:        # Regex: owner/repo format
def validate_branch_name(branch: str) -> str:    # Regex: safe branch chars
def validate_username(username: str) -> str:      # Regex: safe username chars
def validate_file_path(path: str) -> str:         # Block query injection (?&=#)
def log_tool_call(tool_name, **kwargs):           # Audit logging
def require_write_access(tool_name):              # Read-only mode guard
```

### MCP Tools (39 total)

| Category | Tool | Description |
|----------|------|-------------|
| **Auth** | `auth_status` | Check gh auth status |
| | `whoami` | Get authenticated username |
| | `switch_account` | Switch active gh account |
| **Repos** | `create_repo` | Create new GitHub repo |
| | `list_repos` | List repos (JSON formatted) |
| | `repo_view` | View repo details |
| | `clone_repo` | Clone repo locally |
| | `delete_repo` | Delete repo (with confirmation) |
| **Git** | `git_status` | Get local repo status |
| | `git_add_commit_push` | Add, commit, push in one command |
| | `git_init_and_push` | Init local dir + create GitHub repo + push |
| | `git_pull` | Pull latest changes |
| **Branches** | `create_branch` | Create new branch |
| | `list_branches` | List local branches |
| | `switch_branch` | Checkout a branch |
| | `delete_branch` | Delete local branch |
| **Forks** | `fork_repo` | Fork a repository |
| | `sync_fork` | Sync fork with upstream |
| **Issues** | `create_issue` | Create new issue |
| | `list_issues` | List repo issues (JSON formatted) |
| | `comment_on_issue` | Comment on an issue |
| **PRs** | `create_pr` | Create pull request |
| | `list_prs` | List pull requests (JSON formatted) |
| | `comment_on_pr` | Comment on a PR |
| | `merge_pr` | Merge a PR (merge/squash/rebase) |
| | `review_pr` | Review a PR (approve/comment/request-changes) |
| | `pr_diff` | View PR diff |
| **Collaborators** | `list_collaborators` | List repo collaborators |
| | `add_collaborator` | Add collaborator (pull/push/admin) |
| **File Ops** | `get_file_contents` | Get file from GitHub repo via API |
| | `create_or_update_file` | Create/update file via API |
| **Gists** | `create_gist` | Create GitHub gist |
| **Workflows** | `list_workflows` | List GitHub Actions workflows |
| | `run_workflow` | Trigger a workflow run |
| | `list_workflow_runs` | List recent workflow runs |
| | `view_workflow_run` | View specific run details |
| **Search** | `search_repos` | Search GitHub repositories |
| **Releases** | `create_release` | Create GitHub release |
| | `list_releases` | List releases |

---

## Common Tasks

### Add a New Tool

1. Add function with `@mcp.tool()` decorator in the appropriate section of `server.py`:
```python
@mcp.tool()
def my_new_tool(param1: str, param2: int = 10) -> str:
    """Tool description shown to Claude."""
    log_tool_call("my_new_tool", param1=param1, param2=param2)
    try:
        require_write_access("my_new_tool")  # if it's a write operation
        param1 = validate_repo_name(param1)  # validate inputs as needed
    except (PermissionError, ValueError) as e:
        return str(e)
    
    result = run_gh(["some", "command", param1])
    if result["success"]:
        return f"Success\n\n{result['output']}"
    else:
        return f"Failed: {result['error']}"
```

2. Security checklist for new tools:
   - Add `log_tool_call()` at the start
   - Add `require_write_access()` if tool modifies state
   - Add `validate_path()` for `repo_path` params
   - Add `validate_repo_name()` for `repo` params
   - Add `validate_branch_name()` for branch params
   - Add `validate_username()` for username params
   - Add `validate_file_path()` for file path params in API URLs

### Add GitHub API Endpoint

For operations not supported by `gh` CLI directly, use `gh api`:
```python
@mcp.tool()
def get_repo_languages(repo: str) -> str:
    """Get languages used in a repository."""
    log_tool_call("get_repo_languages", repo=repo)
    try:
        repo = validate_repo_name(repo)
    except ValueError as e:
        return str(e)
    result = run_gh(["api", f"repos/{repo}/languages"])
    return result["output"] if result["success"] else result["error"]
```

---

## Transport Modes

### stdio (default) — Local Use
```bash
python server.py
```
Used by Claude Desktop and Claude Code. No network exposure, no auth needed.

### SSE — Remote Use (Claude.ai)
```bash
MCP_TRANSPORT=sse MCP_PORT=9000 MCP_SERVER_URL=https://your-tunnel.ngrok-free.dev python server.py
```
Enables OAuth 2.0 automatically:
- `/.well-known/oauth-authorization-server` — OAuth metadata
- `/.well-known/oauth-protected-resource` — Protected resource metadata
- `/register` — Dynamic client registration (RFC 7591)
- `/authorize` — Authorization endpoint (redirects to `/consent`)
- `/consent` — Password-based consent page
- `/token` — Token exchange endpoint
- `/revoke` — Token revocation

---

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `WORK_DIR` | Base directory for git operations | `~/projects` |
| `READ_ONLY` | Block all write tools when `true` | `false` |
| `LOG_FILE` | Audit log file path | `mcp_audit.log` |
| `MCP_TRANSPORT` | `stdio` or `sse` | `stdio` |
| `MCP_PORT` | Port for SSE transport | `8080` |
| `MCP_SERVER_URL` | Public URL for OAuth metadata (required for SSE) | `http://localhost:8080` |
| `MCP_AUTH_PASSWORD` | Password for OAuth consent page | `approve` |

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

## Coding Conventions

- **Single file for tools**: Keep all tools in `server.py`
- **Separate file for OAuth**: OAuth provider logic in `oauth_provider.py`
- **Type hints**: All functions must have type hints
- **Docstrings**: Every tool needs a docstring (shown to Claude)
- **Security first**: Every tool must have `log_tool_call`, input validation, and write guards where applicable
- **Error handling**: Always return user-friendly messages, never raw exceptions

---

## Testing

```bash
# Test gh CLI works
gh auth status
gh repo list --limit 3

# Test server imports and tool count
python -c "from server import mcp; print(len(mcp._tool_manager._tools), 'tools loaded')"

# Test security - path sandboxing
python -c "from server import validate_path; validate_path('C:/Windows')"  # Should raise ValueError

# Run server in stdio mode
python server.py

# Run server in SSE mode with OAuth
MCP_TRANSPORT=sse MCP_PORT=9000 MCP_SERVER_URL=http://localhost:9000 python server.py
```

---

## Security Notes

- **Path sandboxing**: All `repo_path` params validated against `WORK_DIR` (prevents directory traversal)
- **Input validation**: Regex checks on repo names, branch names, usernames, file paths
- **Read-only mode**: `READ_ONLY=true` blocks all write operations (19+ tools)
- **Audit logging**: Every tool call logged with truncated params to `mcp_audit.log`
- **OAuth 2.0**: SSE transport uses full OAuth flow (dynamic registration, PKCE, consent page)
- **No credentials stored**: Relies entirely on `gh auth` — no tokens in config
- **Subprocess safety**: All commands use list args (no `shell=True`)

---

## Known Limitations

- Requires `gh` CLI installed and authenticated
- Commands timeout after 60-120 seconds
- Some operations require push access to repos
- Rate limited by GitHub API (5000 requests/hour authenticated)
- OAuth tokens are in-memory (lost on server restart — Claude.ai re-authenticates automatically)
- ngrok free tier URLs change on restart (use Cloudflare Tunnel or paid ngrok for permanent URLs)

---

## Memory Context

**Created by**: Prateek Aryan (Senior Software Engineer / Tech Lead)  
**Primary use case**: Push MCP servers and projects to GitHub from Claude  
**Workflow**: Build in Claude -> Push via this MCP -> Iterate  
**GitHub username**: prateekaryann
