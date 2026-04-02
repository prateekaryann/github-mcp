#!/usr/bin/env python3
"""
GitHub MCP Server

An MCP server that wraps the GitHub CLI (gh) to provide GitHub operations
directly from Claude Desktop/Code.

Prerequisites:
    1. Install GitHub CLI: https://cli.github.com/
    2. Authenticate: gh auth login
    
Usage:
    python server.py
"""

import asyncio
import subprocess
import json
import os
import shutil
from typing import Optional
from pathlib import Path

from mcp.server.fastmcp import FastMCP

# Initialize MCP server
mcp = FastMCP("github-cli")

# Default working directory for git operations
WORK_DIR = Path.home() / "projects"


def run_gh(args: list[str], cwd: Optional[str] = None) -> dict:
    """
    Run a gh CLI command and return the result.
    
    Args:
        args: List of arguments to pass to gh
        cwd: Working directory for the command
        
    Returns:
        Dict with 'success', 'output', and 'error' keys
    """
    try:
        result = subprocess.run(
            ["gh"] + args,
            capture_output=True,
            text=True,
            cwd=cwd or str(WORK_DIR),
            timeout=60,
        )
        
        return {
            "success": result.returncode == 0,
            "output": result.stdout.strip(),
            "error": result.stderr.strip() if result.returncode != 0 else None,
        }
    except FileNotFoundError:
        return {
            "success": False,
            "output": "",
            "error": "GitHub CLI (gh) not found. Install from https://cli.github.com/",
        }
    except subprocess.TimeoutExpired:
        return {
            "success": False,
            "output": "",
            "error": "Command timed out after 60 seconds",
        }
    except Exception as e:
        return {
            "success": False,
            "output": "",
            "error": str(e),
        }


def run_git(args: list[str], cwd: Optional[str] = None) -> dict:
    """Run a git command and return the result."""
    try:
        result = subprocess.run(
            ["git"] + args,
            capture_output=True,
            text=True,
            cwd=cwd or str(WORK_DIR),
            timeout=120,
        )
        
        return {
            "success": result.returncode == 0,
            "output": result.stdout.strip(),
            "error": result.stderr.strip() if result.returncode != 0 else None,
        }
    except Exception as e:
        return {
            "success": False,
            "output": "",
            "error": str(e),
        }


# =============================================================================
# AUTHENTICATION & STATUS
# =============================================================================

@mcp.tool()
def auth_status() -> str:
    """
    Check GitHub CLI authentication status.
    Shows which account is logged in and what scopes are available.
    """
    result = run_gh(["auth", "status"])
    
    if result["success"]:
        return f"✅ Authenticated\n\n{result['output']}"
    else:
        return f"❌ Not authenticated\n\n{result['error']}\n\nRun: gh auth login"


@mcp.tool()
def whoami() -> str:
    """Get the currently authenticated GitHub username."""
    result = run_gh(["api", "user", "--jq", ".login"])
    
    if result["success"]:
        return f"Logged in as: {result['output']}"
    else:
        return f"Error: {result['error']}"


# =============================================================================
# REPOSITORY OPERATIONS
# =============================================================================

@mcp.tool()
def create_repo(
    name: str,
    description: str = "",
    public: bool = True,
    clone: bool = True,
) -> str:
    """
    Create a new GitHub repository.
    
    Args:
        name: Repository name (e.g., 'my-project')
        description: Repository description
        public: Whether the repo should be public (default: True)
        clone: Whether to clone the repo locally after creation (default: True)
        
    Returns:
        Success message with repo URL or error
    """
    args = ["repo", "create", name]
    
    if description:
        args.extend(["--description", description])
    
    if public:
        args.append("--public")
    else:
        args.append("--private")
    
    if clone:
        args.append("--clone")
    
    result = run_gh(args)
    
    if result["success"]:
        return f"✅ Repository created!\n\n{result['output']}"
    else:
        return f"❌ Failed to create repository\n\n{result['error']}"


@mcp.tool()
def list_repos(
    owner: Optional[str] = None,
    limit: int = 10,
    visibility: str = "all",
) -> str:
    """
    List repositories for a user or organization.
    
    Args:
        owner: GitHub username or org (default: authenticated user)
        limit: Maximum number of repos to list (default: 10)
        visibility: Filter by visibility - 'all', 'public', 'private' (default: 'all')
        
    Returns:
        List of repositories
    """
    args = ["repo", "list"]
    
    if owner:
        args.append(owner)
    
    args.extend(["--limit", str(limit)])
    
    if visibility != "all":
        args.extend(["--visibility", visibility])
    
    result = run_gh(args)
    
    if result["success"]:
        return f"📁 Repositories:\n\n{result['output']}"
    else:
        return f"Error: {result['error']}"


@mcp.tool()
def repo_view(repo: str) -> str:
    """
    View details of a GitHub repository.
    
    Args:
        repo: Repository in 'owner/repo' format (e.g., 'prateekaryann/freelance-job-mcp')
        
    Returns:
        Repository details including description, stars, forks, etc.
    """
    result = run_gh(["repo", "view", repo])
    
    if result["success"]:
        return result["output"]
    else:
        return f"Error: {result['error']}"


@mcp.tool()
def clone_repo(repo: str, directory: Optional[str] = None) -> str:
    """
    Clone a GitHub repository.
    
    Args:
        repo: Repository in 'owner/repo' format
        directory: Local directory name (default: repo name)
        
    Returns:
        Success message or error
    """
    args = ["repo", "clone", repo]
    
    if directory:
        args.append(directory)
    
    result = run_gh(args)
    
    if result["success"]:
        clone_path = directory or repo.split("/")[-1]
        return f"✅ Cloned to {WORK_DIR / clone_path}"
    else:
        return f"❌ Clone failed\n\n{result['error']}"


@mcp.tool()
def delete_repo(repo: str, confirm: bool = False) -> str:
    """
    Delete a GitHub repository. USE WITH CAUTION!
    
    Args:
        repo: Repository in 'owner/repo' format
        confirm: Must be True to actually delete (safety check)
        
    Returns:
        Confirmation or error
    """
    if not confirm:
        return "⚠️ Safety check: Set confirm=True to actually delete the repository. This cannot be undone!"
    
    result = run_gh(["repo", "delete", repo, "--yes"])
    
    if result["success"]:
        return f"✅ Repository {repo} deleted"
    else:
        return f"❌ Failed to delete\n\n{result['error']}"


# =============================================================================
# GIT OPERATIONS (Push, Pull, Commit)
# =============================================================================

@mcp.tool()
def git_status(repo_path: str) -> str:
    """
    Get git status for a local repository.
    
    Args:
        repo_path: Path to the local repository
        
    Returns:
        Git status output
    """
    result = run_git(["status"], cwd=repo_path)
    
    if result["success"]:
        return result["output"]
    else:
        return f"Error: {result['error']}"


@mcp.tool()
def git_add_commit_push(
    repo_path: str,
    message: str,
    add_all: bool = True,
    branch: str = "main",
) -> str:
    """
    Add, commit, and push changes in one operation.
    
    Args:
        repo_path: Path to the local repository
        message: Commit message
        add_all: Whether to add all changes (default: True)
        branch: Branch to push to (default: 'main')
        
    Returns:
        Success message or error
    """
    results = []
    
    # Add
    if add_all:
        add_result = run_git(["add", "."], cwd=repo_path)
        if not add_result["success"]:
            return f"❌ Git add failed: {add_result['error']}"
        results.append("✅ Added changes")
    
    # Commit
    commit_result = run_git(["commit", "-m", message], cwd=repo_path)
    if not commit_result["success"]:
        if "nothing to commit" in commit_result["error"]:
            return "ℹ️ Nothing to commit - working tree clean"
        return f"❌ Git commit failed: {commit_result['error']}"
    results.append(f"✅ Committed: {message}")
    
    # Push
    push_result = run_git(["push", "-u", "origin", branch], cwd=repo_path)
    if not push_result["success"]:
        return f"❌ Git push failed: {push_result['error']}"
    results.append(f"✅ Pushed to origin/{branch}")
    
    return "\n".join(results)


@mcp.tool()
def git_init_and_push(
    repo_path: str,
    repo_name: str,
    description: str = "",
    public: bool = True,
    commit_message: str = "Initial commit",
) -> str:
    """
    Initialize a local directory as a git repo, create GitHub repo, and push.
    Perfect for pushing an existing project to GitHub.
    
    Args:
        repo_path: Path to the local project directory
        repo_name: Name for the GitHub repository
        description: Repository description
        public: Whether the repo should be public
        commit_message: Initial commit message
        
    Returns:
        Success message with repo URL or error
    """
    path = Path(repo_path).expanduser().resolve()
    
    if not path.exists():
        return f"❌ Directory not found: {path}"
    
    results = []
    
    # Check if already a git repo
    git_dir = path / ".git"
    if not git_dir.exists():
        # Init
        init_result = run_git(["init"], cwd=str(path))
        if not init_result["success"]:
            return f"❌ Git init failed: {init_result['error']}"
        results.append("✅ Initialized git repository")
        
        # Set branch to main
        run_git(["branch", "-M", "main"], cwd=str(path))
    else:
        results.append("ℹ️ Already a git repository")
    
    # Add and commit if needed
    status_result = run_git(["status", "--porcelain"], cwd=str(path))
    if status_result["output"]:  # Has changes
        run_git(["add", "."], cwd=str(path))
        commit_result = run_git(["commit", "-m", commit_message], cwd=str(path))
        if commit_result["success"]:
            results.append(f"✅ Committed: {commit_message}")
    
    # Create GitHub repo
    visibility = "--public" if public else "--private"
    create_args = ["repo", "create", repo_name, visibility, "--source", str(path), "--push"]
    
    if description:
        create_args.extend(["--description", description])
    
    create_result = run_gh(create_args)
    
    if create_result["success"]:
        results.append(f"✅ Created and pushed to GitHub!")
        results.append(f"\n🔗 https://github.com/{repo_name}")
        return "\n".join(results)
    else:
        # Maybe repo already exists, try just adding remote and pushing
        if "already exists" in create_result["error"]:
            results.append("ℹ️ Repository already exists, trying to push...")
            
            # Get username
            user_result = run_gh(["api", "user", "--jq", ".login"])
            if user_result["success"]:
                username = user_result["output"]
                remote_url = f"git@github.com:{username}/{repo_name}.git"
                
                # Add remote if not exists
                run_git(["remote", "add", "origin", remote_url], cwd=str(path))
                
                # Push
                push_result = run_git(["push", "-u", "origin", "main"], cwd=str(path))
                if push_result["success"]:
                    results.append(f"✅ Pushed to existing repo!")
                    results.append(f"\n🔗 https://github.com/{username}/{repo_name}")
                    return "\n".join(results)
                else:
                    return f"❌ Push failed: {push_result['error']}"
        
        return f"❌ Failed to create repo: {create_result['error']}"


@mcp.tool()
def git_pull(repo_path: str, branch: str = "main") -> str:
    """
    Pull latest changes from remote.
    
    Args:
        repo_path: Path to the local repository
        branch: Branch to pull (default: 'main')
    """
    result = run_git(["pull", "origin", branch], cwd=repo_path)
    
    if result["success"]:
        return f"✅ Pulled latest from origin/{branch}\n\n{result['output']}"
    else:
        return f"❌ Pull failed: {result['error']}"


# =============================================================================
# ISSUES
# =============================================================================

@mcp.tool()
def create_issue(
    repo: str,
    title: str,
    body: str = "",
    labels: Optional[str] = None,
) -> str:
    """
    Create a new GitHub issue.
    
    Args:
        repo: Repository in 'owner/repo' format
        title: Issue title
        body: Issue body/description
        labels: Comma-separated labels (e.g., 'bug,help wanted')
        
    Returns:
        Issue URL or error
    """
    args = ["issue", "create", "--repo", repo, "--title", title]
    
    if body:
        args.extend(["--body", body])
    
    if labels:
        args.extend(["--label", labels])
    
    result = run_gh(args)
    
    if result["success"]:
        return f"✅ Issue created!\n\n{result['output']}"
    else:
        return f"❌ Failed to create issue: {result['error']}"


@mcp.tool()
def list_issues(
    repo: str,
    state: str = "open",
    limit: int = 10,
) -> str:
    """
    List issues for a repository.
    
    Args:
        repo: Repository in 'owner/repo' format
        state: Filter by state - 'open', 'closed', 'all' (default: 'open')
        limit: Maximum number of issues to list
        
    Returns:
        List of issues
    """
    args = ["issue", "list", "--repo", repo, "--state", state, "--limit", str(limit)]
    
    result = run_gh(args)
    
    if result["success"]:
        return f"📋 Issues ({state}):\n\n{result['output']}"
    else:
        return f"Error: {result['error']}"


# =============================================================================
# PULL REQUESTS
# =============================================================================

@mcp.tool()
def create_pr(
    repo: str,
    title: str,
    body: str = "",
    base: str = "main",
    head: Optional[str] = None,
    draft: bool = False,
) -> str:
    """
    Create a pull request.
    
    Args:
        repo: Repository in 'owner/repo' format
        title: PR title
        body: PR description
        base: Base branch (default: 'main')
        head: Head branch (default: current branch)
        draft: Create as draft PR
        
    Returns:
        PR URL or error
    """
    args = ["pr", "create", "--repo", repo, "--title", title, "--base", base]
    
    if body:
        args.extend(["--body", body])
    
    if head:
        args.extend(["--head", head])
    
    if draft:
        args.append("--draft")
    
    result = run_gh(args)
    
    if result["success"]:
        return f"✅ Pull request created!\n\n{result['output']}"
    else:
        return f"❌ Failed to create PR: {result['error']}"


@mcp.tool()
def list_prs(
    repo: str,
    state: str = "open",
    limit: int = 10,
) -> str:
    """
    List pull requests for a repository.
    
    Args:
        repo: Repository in 'owner/repo' format
        state: Filter by state - 'open', 'closed', 'merged', 'all'
        limit: Maximum number of PRs to list
    """
    args = ["pr", "list", "--repo", repo, "--state", state, "--limit", str(limit)]
    
    result = run_gh(args)
    
    if result["success"]:
        return f"🔀 Pull Requests ({state}):\n\n{result['output']}"
    else:
        return f"Error: {result['error']}"


# =============================================================================
# GISTS
# =============================================================================

@mcp.tool()
def create_gist(
    filename: str,
    content: str,
    description: str = "",
    public: bool = False,
) -> str:
    """
    Create a GitHub Gist.
    
    Args:
        filename: Name for the gist file (e.g., 'script.py')
        content: File content
        description: Gist description
        public: Whether the gist should be public
        
    Returns:
        Gist URL or error
    """
    import tempfile
    
    # Write content to temp file
    with tempfile.NamedTemporaryFile(mode='w', suffix=f"_{filename}", delete=False) as f:
        f.write(content)
        temp_path = f.name
    
    try:
        args = ["gist", "create", temp_path]
        
        if description:
            args.extend(["--desc", description])
        
        if public:
            args.append("--public")
        
        result = run_gh(args)
        
        if result["success"]:
            return f"✅ Gist created!\n\n{result['output']}"
        else:
            return f"❌ Failed to create gist: {result['error']}"
    finally:
        os.unlink(temp_path)


# =============================================================================
# SEARCH
# =============================================================================

@mcp.tool()
def search_repos(
    query: str,
    limit: int = 10,
) -> str:
    """
    Search GitHub repositories.
    
    Args:
        query: Search query (e.g., 'fastapi language:python stars:>100')
        limit: Maximum number of results
        
    Returns:
        List of matching repositories
    """
    args = ["search", "repos", query, "--limit", str(limit)]
    
    result = run_gh(args)
    
    if result["success"]:
        return f"🔍 Search results:\n\n{result['output']}"
    else:
        return f"Error: {result['error']}"


# =============================================================================
# RELEASES
# =============================================================================

@mcp.tool()
def create_release(
    repo: str,
    tag: str,
    title: str,
    notes: str = "",
    draft: bool = False,
    prerelease: bool = False,
) -> str:
    """
    Create a GitHub release.
    
    Args:
        repo: Repository in 'owner/repo' format
        tag: Tag name (e.g., 'v1.0.0')
        title: Release title
        notes: Release notes
        draft: Create as draft
        prerelease: Mark as prerelease
        
    Returns:
        Release URL or error
    """
    args = ["release", "create", tag, "--repo", repo, "--title", title]
    
    if notes:
        args.extend(["--notes", notes])
    
    if draft:
        args.append("--draft")
    
    if prerelease:
        args.append("--prerelease")
    
    result = run_gh(args)
    
    if result["success"]:
        return f"✅ Release created!\n\n{result['output']}"
    else:
        return f"❌ Failed to create release: {result['error']}"


# =============================================================================
# RUN SERVER
# =============================================================================

if __name__ == "__main__":
    # Ensure work directory exists
    WORK_DIR.mkdir(parents=True, exist_ok=True)
    
    # Check if gh is installed
    if not shutil.which("gh"):
        print("⚠️  GitHub CLI (gh) not found!")
        print("   Install from: https://cli.github.com/")
        print("   Then run: gh auth login")
    
    mcp.run()
