# 🐙 GitHub MCP Server

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![MCP](https://img.shields.io/badge/MCP-Compatible-green.svg)](https://modelcontextprotocol.io/)

A **Model Context Protocol (MCP)** server that wraps the GitHub CLI (`gh`) to provide GitHub operations directly from Claude Desktop/Code.

## 🚀 Features

- **Repository Management**: Create, clone, list, view, and delete repos
- **Git Operations**: Add, commit, push, pull — all in one command
- **Issues**: Create and list issues
- **Pull Requests**: Create and list PRs
- **Releases**: Create GitHub releases
- **Gists**: Create gists from content
- **Search**: Search repositories across GitHub

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
```

Follow the prompts to authenticate with your GitHub account.

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

## 🔌 Claude Desktop Integration

Add to your `claude_desktop_config.json`:

**macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`  
**Windows**: `%APPDATA%\Claude\claude_desktop_config.json`

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

## 🛠️ Available Tools

### Authentication
| Tool | Description |
|------|-------------|
| `auth_status` | Check GitHub CLI authentication status |
| `whoami` | Get currently authenticated username |

### Repository Operations
| Tool | Description |
|------|-------------|
| `create_repo` | Create a new GitHub repository |
| `list_repos` | List repositories for a user/org |
| `repo_view` | View repository details |
| `clone_repo` | Clone a repository locally |
| `delete_repo` | Delete a repository (with confirmation) |

### Git Operations
| Tool | Description |
|------|-------------|
| `git_status` | Get status of local repo |
| `git_add_commit_push` | Add, commit, and push in one command |
| `git_init_and_push` | Initialize local dir and push to new GitHub repo |
| `git_pull` | Pull latest changes |

### Issues & PRs
| Tool | Description |
|------|-------------|
| `create_issue` | Create a new issue |
| `list_issues` | List repository issues |
| `create_pr` | Create a pull request |
| `list_prs` | List pull requests |

### Other
| Tool | Description |
|------|-------------|
| `create_gist` | Create a GitHub gist |
| `search_repos` | Search GitHub repositories |
| `create_release` | Create a GitHub release |

## 📊 Example Usage

Once connected to Claude Desktop:

**Create a new repo and push local project:**
```
"Push my ~/projects/my-app folder to GitHub as a public repo called my-awesome-app"
```
Claude uses `git_init_and_push` → Creates repo, initializes git, pushes code

**Quick commit and push:**
```
"Commit all changes in ~/projects/my-app with message 'fix: resolve login bug' and push"
```
Claude uses `git_add_commit_push` → Stages, commits, pushes

**Create an issue:**
```
"Create an issue on prateekaryann/my-app titled 'Add dark mode support' with label 'enhancement'"
```
Claude uses `create_issue` → Creates the issue

**Search for repos:**
```
"Find popular FastAPI projects with more than 1000 stars"
```
Claude uses `search_repos` with query `fastapi stars:>1000`

## 🏗️ Project Structure

```
github-mcp/
├── server.py         # Main MCP server
├── requirements.txt  # Python dependencies
├── README.md
└── LICENSE
```

## 🔒 Security Notes

- This server runs `gh` CLI commands on your machine
- It uses your existing GitHub CLI authentication
- The `delete_repo` command requires explicit confirmation
- No credentials are stored by this server — it relies on `gh auth`

## 📝 License

MIT License - See [LICENSE](LICENSE) for details.

## 👤 Author

**Prateek Aryan** - [@prateekaryann](https://github.com/prateekaryann)

---

Built for seamless GitHub integration with Claude! 🚀
