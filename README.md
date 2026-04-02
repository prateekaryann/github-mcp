# 🐙 GitHub MCP Server

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![MCP](https://img.shields.io/badge/MCP-Compatible-green.svg)](https://modelcontextprotocol.io/)
[![Tools](https://img.shields.io/badge/Tools-39-orange.svg)](#-tools-reference)

A **Model Context Protocol (MCP)** server that wraps the GitHub CLI (`gh`) to provide **39 tools** across 12 categories — manage repos, branches, issues, PRs, workflows, collaborators, and more, directly from Claude Desktop or Claude Code.

## 🚀 Features

- **Repository Management** — Create, clone, list, view, and delete repos
- **Git Operations** — Add, commit, push, pull, init + push in one command
- **Branch Management** — Create, list, switch, and delete branches
- **Forking** — Fork repos and sync forks with upstream
- **Issues** — Create, list, and comment on issues
- **Pull Requests** — Create, list, comment, merge, review, and diff PRs
- **Collaborators** — List and add collaborators to repos
- **File Operations** — Read and create/update files via the GitHub API
- **Workflows** — List, trigger, and inspect GitHub Actions workflow runs
- **Releases** — Create and list releases
- **Gists** — Create gists from content
- **Search** — Search repositories across GitHub
- **Security** — Path sandboxing, input validation, read-only mode, audit logging
- **Remote Access** — SSE transport with OAuth 2.0 authentication via ngrok tunnel

## 📦 Prerequisites

### 1. Install GitHub CLI

```bash
# macOS
brew install gh

# Ubuntu/Debian
sudo apt install gh

# Windows
winget install GitHub.cli
```

### 2. Authenticate

```bash
gh auth login
gh auth status   # Verify you're logged in
```

### 3. Python 3.10+

```bash
python --version  # Must be 3.10 or higher
```

## 🔧 Installation

```bash
# Clone the repository
git clone https://github.com/prateekaryann/github-mcp.git
cd github-mcp

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

## 🔌 Usage — Local (stdio)

This is the simplest setup. Claude Desktop or Claude Code launches the server as a subprocess.

### Claude Desktop

Add to your `claude_desktop_config.json`:

| OS | Config path |
|----|-------------|
| macOS | `~/Library/Application Support/Claude/claude_desktop_config.json` |
| Windows | `%APPDATA%\Claude\claude_desktop_config.json` |
| Linux | `~/.config/claude/claude_desktop_config.json` |

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

Restart Claude Desktop after adding the configuration.

### Claude Code

```bash
claude mcp add github -- python /path/to/github-mcp/server.py
```

## 🌐 Usage — Remote (SSE + OAuth)

For remote access, the server runs an SSE endpoint with OAuth 2.0 authentication, exposed via an ngrok tunnel.

### Step 1: Start an ngrok tunnel

```bash
ngrok http 8080
# Note the HTTPS forwarding URL, e.g. https://abc123.ngrok-free.app
```

Or use the included helper scripts:

```bash
# Linux/macOS
./tunnel.sh

# Windows (PowerShell)
.\tunnel.ps1
```

### Step 2: Start the server in SSE mode

```bash
export MCP_TRANSPORT=sse
export MCP_PORT=8080
export MCP_SERVER_URL=https://abc123.ngrok-free.app  # Your ngrok URL
python server.py
```

### Step 3: Connect from Claude Desktop

```json
{
  "mcpServers": {
    "github-remote": {
      "url": "https://abc123.ngrok-free.app/sse"
    }
  }
}
```

The OAuth flow will prompt you to authorize when you first connect.

## 🛠️ Tools Reference

### Auth (3)

| Tool | Description |
|------|-------------|
| `auth_status` | Check GitHub CLI authentication status |
| `whoami` | Get currently authenticated username |
| `switch_account` | Switch between GitHub accounts |

### Repos (5)

| Tool | Description |
|------|-------------|
| `create_repo` | Create a new GitHub repository |
| `list_repos` | List repositories for a user/org |
| `repo_view` | View repository details |
| `clone_repo` | Clone a repository locally |
| `delete_repo` | Delete a repository (requires `confirm=True`) |

### Git (4)

| Tool | Description |
|------|-------------|
| `git_status` | Get status of a local repository |
| `git_add_commit_push` | Add, commit, and push in one command |
| `git_init_and_push` | Initialize local dir, create GitHub repo, and push |
| `git_pull` | Pull latest changes from remote |

### Branches (4)

| Tool | Description |
|------|-------------|
| `create_branch` | Create a new branch |
| `list_branches` | List branches in a repository |
| `switch_branch` | Switch to a different branch |
| `delete_branch` | Delete a branch |

### Forks (2)

| Tool | Description |
|------|-------------|
| `fork_repo` | Fork a repository |
| `sync_fork` | Sync a fork with its upstream repository |

### Issues (3)

| Tool | Description |
|------|-------------|
| `create_issue` | Create a new issue |
| `list_issues` | List repository issues |
| `comment_on_issue` | Add a comment to an issue |

### Pull Requests (6)

| Tool | Description |
|------|-------------|
| `create_pr` | Create a pull request |
| `list_prs` | List pull requests |
| `comment_on_pr` | Add a comment to a PR |
| `merge_pr` | Merge a pull request |
| `review_pr` | Submit a review on a PR |
| `pr_diff` | View the diff of a pull request |

### Collaborators (2)

| Tool | Description |
|------|-------------|
| `list_collaborators` | List collaborators on a repository |
| `add_collaborator` | Add a collaborator to a repository |

### File Operations (2)

| Tool | Description |
|------|-------------|
| `get_file_contents` | Get the contents of a file from a repository |
| `create_or_update_file` | Create or update a file in a repository |

### Gists (1)

| Tool | Description |
|------|-------------|
| `create_gist` | Create a GitHub gist |

### Workflows (4)

| Tool | Description |
|------|-------------|
| `list_workflows` | List GitHub Actions workflows for a repo |
| `run_workflow` | Trigger a workflow dispatch event |
| `list_workflow_runs` | List recent workflow runs |
| `view_workflow_run` | View details of a specific workflow run |

### Search (1)

| Tool | Description |
|------|-------------|
| `search_repos` | Search GitHub repositories |

### Releases (2)

| Tool | Description |
|------|-------------|
| `create_release` | Create a new GitHub release |
| `list_releases` | List releases for a repository |

## 🔒 Security

### Path Sandboxing

All local file operations are restricted to the `WORK_DIR` directory (default: `~/projects`). Any path outside this directory is rejected, preventing unauthorized filesystem access.

### Input Validation

Repository names, usernames, branch names, and file paths are validated against strict regex patterns to prevent injection attacks.

### Read-Only Mode

Set `READ_ONLY=true` to restrict the server to safe, non-destructive operations only (list, view, search). All write operations will be blocked.

### Audit Logging

Every tool invocation is logged with parameters to `mcp_audit.log` (configurable via `LOG_FILE`), providing a full audit trail of all operations.

### OAuth 2.0 (Remote Mode)

When running in SSE mode, the server requires OAuth 2.0 authentication with configurable scopes (`read`, `write`). Client registration and token revocation are supported.

### Dangerous Operation Confirmation

Destructive operations like `delete_repo` require an explicit `confirm=True` parameter to prevent accidental data loss.

## ⚙️ Configuration

| Variable | Description | Default |
|----------|-------------|---------|
| `WORK_DIR` | Base directory for git operations (path sandbox root) | `~/projects` |
| `READ_ONLY` | Block all write operations when `true` | `false` |
| `LOG_FILE` | Path to the audit log file | `mcp_audit.log` |
| `MCP_TRANSPORT` | Transport mode: `stdio` or `sse` | `stdio` |
| `MCP_PORT` | Port for SSE server | `8080` |
| `MCP_SERVER_URL` | Public URL for OAuth issuer (ngrok URL) | `http://localhost:8080` |

## 🏗️ Architecture

```
github-mcp/
├── server.py           # Main MCP server — all 39 tools
├── oauth_provider.py   # In-memory OAuth 2.0 provider (SSE mode)
├── requirements.txt    # mcp[cli], uvicorn, starlette
├── tunnel.sh           # ngrok tunnel helper (Linux/macOS)
├── tunnel.ps1          # ngrok tunnel helper (Windows)
├── README.md
├── LICENSE
└── .claude/
    └── CLAUDE.md       # Claude Code project instructions
```

## 📝 License

MIT License — See [LICENSE](LICENSE) for details.

## 👤 Author

**Prateek Aryan** — [@prateekaryann](https://github.com/prateekaryann)

---

Built for seamless GitHub integration with Claude.
