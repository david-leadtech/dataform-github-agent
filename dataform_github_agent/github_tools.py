# Copyright 2025 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""This module provides tools for interacting with GitHub repositories.

It includes functionality for reading/writing files, creating branches,
making commits, and creating pull requests in GitHub repositories.
"""

from typing import Any, Dict, List, Optional
from google.adk.tools import agent_tool
from github import Github, GithubException
import sys
import os

# Add parent directory to path to import config
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import config


def _get_github_client() -> Optional[Github]:
    """Get GitHub client instance using token from config."""
    github_token = config.github_token
    if not github_token:
        return None
    return Github(github_token)


def _get_repo() -> Optional[Any]:
    """Get GitHub repository instance."""
    github_client = _get_github_client()
    if not github_client:
        return None
    
    repo_path = config.github_repo_path
    if not repo_path:
        return None
    
    try:
        return github_client.get_repo(repo_path)
    except GithubException as e:
        print(f"Error getting repository '{repo_path}': {e}")
        return None


@agent_tool
def create_github_repository(
    repo_name: str,
    description: Optional[str] = None,
    private: bool = False,
    organization: Optional[str] = None,
    auto_init: bool = True,
    gitignore_template: Optional[str] = None,
    license_template: Optional[str] = None,
) -> Dict[str, Any]:
    """Create a new GitHub repository.

    Args:
        repo_name (str): Name of the repository to create.
        description (Optional[str]): Repository description.
        private (bool): Whether the repository should be private (default: False).
        organization (Optional[str]): Organization or user name where to create the repo.
                                     If None, creates in the authenticated user's account.
        auto_init (bool): Whether to initialize the repository with a README (default: True).
        gitignore_template (Optional[str]): Gitignore template to use (e.g., 'Python', 'Node').
        license_template (Optional[str]): License template to use (e.g., 'mit', 'apache-2.0').

    Returns:
        Dict with repository creation status and URL.
    """
    github_client = _get_github_client()
    if not github_client:
        return {
            "status": "error",
            "error_message": "GitHub token not configured. Please set GITHUB_TOKEN environment variable.",
        }

    try:
        # Determine where to create the repo
        if organization:
            # Create in organization
            org = github_client.get_organization(organization)
            repo = org.create_repo(
                name=repo_name,
                description=description,
                private=private,
                auto_init=auto_init,
                gitignore_template=gitignore_template,
                license_template=license_template,
            )
        else:
            # Create in user's account
            user = github_client.get_user()
            repo = user.create_repo(
                name=repo_name,
                description=description,
                private=private,
                auto_init=auto_init,
                gitignore_template=gitignore_template,
                license_template=license_template,
            )

        return {
            "status": "success",
            "message": f"Repository '{repo_name}' created successfully",
            "repository_url": repo.html_url,
            "clone_url": repo.clone_url,
            "ssh_url": repo.ssh_url,
            "full_name": repo.full_name,
            "private": repo.private,
        }

    except GithubException as e:
        error_msg = f"Error creating repository '{repo_name}': {e}"
        print(error_msg)
        return {
            "status": "error",
            "error_message": error_msg,
        }
    except Exception as e:
        error_msg = f"Unexpected error creating repository: {e}"
        print(error_msg)
        return {
            "status": "error",
            "error_message": error_msg,
        }


@agent_tool
def read_file_from_github(file_path: str, branch: Optional[str] = None) -> str:
    """Read a file from the GitHub repository.

    Args:
        file_path (str): The path to the file in the repository (e.g., 'definitions/sources/apple_ads.sqlx').
        branch (Optional[str]): The branch to read from. Defaults to the configured default branch.

    Returns:
        str: The content of the file, or an error message if the file cannot be read.
    """
    repo = _get_repo()
    if not repo:
        return "Error: GitHub repository not configured. Please set GITHUB_TOKEN and GITHUB_REPO_PATH environment variables."
    
    if not branch:
        branch = config.github_default_branch
    
    try:
        file_content = repo.get_contents(file_path, ref=branch)
        if file_content.encoding == "base64":
            import base64
            decoded_content = base64.b64decode(file_content.content).decode("utf-8")
            return decoded_content
        return file_content.decoded_content.decode("utf-8")
    except GithubException as e:
        error_msg = f"Error reading file '{file_path}' from branch '{branch}': {e}"
        print(error_msg)
        return error_msg


@agent_tool
def write_file_to_github(
    file_path: str,
    file_content: str,
    commit_message: str,
    branch: Optional[str] = None,
) -> Dict[str, Any]:
    """Write or update a file in the GitHub repository.

    Args:
        file_path (str): The path to the file in the repository.
        file_content (str): The content to write to the file.
        commit_message (str): The commit message for this change.
        branch (Optional[str]): The branch to write to. Defaults to the configured default branch.

    Returns:
        Dict[str, Any]: Result of the write operation including status and commit SHA.
    """
    repo = _get_repo()
    if not repo:
        return {
            "status": "error",
            "error_message": "GitHub repository not configured. Please set GITHUB_TOKEN and GITHUB_REPO_PATH environment variables.",
        }
    
    if not branch:
        branch = config.github_default_branch
    
    try:
        # Check if file exists
        try:
            existing_file = repo.get_contents(file_path, ref=branch)
            # File exists, update it
            result = repo.update_file(
                path=file_path,
                message=commit_message,
                content=file_content,
                sha=existing_file.sha,
                branch=branch,
            )
            return {
                "status": "success",
                "message": f"File '{file_path}' updated successfully",
                "commit_sha": result["commit"].sha,
                "commit_url": result["commit"].html_url,
            }
        except GithubException as e:
            if e.status == 404:
                # File doesn't exist, create it
                result = repo.create_file(
                    path=file_path,
                    message=commit_message,
                    content=file_content,
                    branch=branch,
                )
                return {
                    "status": "success",
                    "message": f"File '{file_path}' created successfully",
                    "commit_sha": result["commit"].sha,
                    "commit_url": result["commit"].html_url,
                }
            else:
                raise
    except GithubException as e:
        error_msg = f"Error writing file '{file_path}' to branch '{branch}': {e}"
        print(error_msg)
        return {"status": "error", "error_message": error_msg}


@agent_tool
def create_github_branch(
    branch_name: str, source_branch: Optional[str] = None
) -> Dict[str, Any]:
    """Create a new branch in the GitHub repository.

    Args:
        branch_name (str): The name of the new branch (e.g., 'feature/add-apple-ads-source').
        source_branch (Optional[str]): The branch to create from. Defaults to the configured default branch.

    Returns:
        Dict[str, Any]: Result of the branch creation operation.
    """
    repo = _get_repo()
    if not repo:
        return {
            "status": "error",
            "error_message": "GitHub repository not configured.",
        }
    
    if not source_branch:
        source_branch = config.github_default_branch
    
    try:
        # Get the source branch reference
        source_ref = repo.get_git_ref(f"heads/{source_branch}")
        
        # Create new branch
        repo.create_git_ref(
            ref=f"refs/heads/{branch_name}",
            sha=source_ref.object.sha,
        )
        
        return {
            "status": "success",
            "message": f"Branch '{branch_name}' created successfully from '{source_branch}'",
            "branch_name": branch_name,
        }
    except GithubException as e:
        error_msg = f"Error creating branch '{branch_name}': {e}"
        print(error_msg)
        return {"status": "error", "error_message": error_msg}


@agent_tool
def create_github_pull_request(
    title: str,
    body: str,
    head_branch: str,
    base_branch: Optional[str] = None,
) -> Dict[str, Any]:
    """Create a pull request in the GitHub repository.

    Args:
        title (str): The title of the pull request.
        body (str): The description/body of the pull request.
        head_branch (str): The branch containing the changes (source branch).
        base_branch (Optional[str]): The branch to merge into. Defaults to the configured default branch.

    Returns:
        Dict[str, Any]: Result of the pull request creation including PR number and URL.
    """
    repo = _get_repo()
    if not repo:
        return {
            "status": "error",
            "error_message": "GitHub repository not configured.",
        }
    
    if not base_branch:
        base_branch = config.github_default_branch
    
    try:
        pr = repo.create_pull(
            title=title,
            body=body,
            head=head_branch,
            base=base_branch,
        )
        
        return {
            "status": "success",
            "message": f"Pull request created successfully",
            "pr_number": pr.number,
            "pr_url": pr.html_url,
            "pr_title": pr.title,
        }
    except GithubException as e:
        error_msg = f"Error creating pull request: {e}"
        print(error_msg)
        return {"status": "error", "error_message": error_msg}


@agent_tool
def list_github_files(
    path: str = "", branch: Optional[str] = None
) -> List[str]:
    """List files in a directory in the GitHub repository.

    Args:
        path (str): The directory path to list (empty string for root).
        branch (Optional[str]): The branch to list from. Defaults to the configured default branch.

    Returns:
        List[str]: A list of file and directory paths.
    """
    repo = _get_repo()
    if not repo:
        return ["Error: GitHub repository not configured."]
    
    if not branch:
        branch = config.github_default_branch
    
    try:
        contents = repo.get_contents(path, ref=branch)
        if isinstance(contents, list):
            return [item.path for item in contents]
        else:
            return [contents.path]
    except GithubException as e:
        error_msg = f"Error listing files in '{path}': {e}"
        print(error_msg)
        return [error_msg]


@agent_tool
def get_github_file_history(
    file_path: str, branch: Optional[str] = None, limit: int = 10
) -> Dict[str, Any]:
    """Get the commit history for a specific file.

    Args:
        file_path (str): The path to the file.
        branch (Optional[str]): The branch to check. Defaults to the configured default branch.
        limit (int): Maximum number of commits to return (default: 10).

    Returns:
        Dict[str, Any]: Commit history with commit messages, authors, and dates.
    """
    repo = _get_repo()
    if not repo:
        return {
            "status": "error",
            "error_message": "GitHub repository not configured.",
        }
    
    if not branch:
        branch = config.github_default_branch
    
    try:
        commits = repo.get_commits(path=file_path, sha=branch)
        history = []
        
        for i, commit in enumerate(commits):
            if i >= limit:
                break
            history.append({
                "sha": commit.sha[:7],
                "message": commit.commit.message,
                "author": commit.commit.author.name,
                "date": commit.commit.author.date.isoformat(),
                "url": commit.html_url,
            })
        
        return {
            "status": "success",
            "file_path": file_path,
            "branch": branch,
            "commits": history,
        }
    except GithubException as e:
        error_msg = f"Error getting file history for '{file_path}': {e}"
        print(error_msg)
        return {"status": "error", "error_message": error_msg}


@agent_tool
def sync_dataform_to_github(
    file_path: str,
    commit_message: Optional[str] = None,
    branch: Optional[str] = None,
) -> Dict[str, Any]:
    """Sync a file from Dataform to GitHub.

    This tool reads a file from Dataform and writes it to GitHub,
    ensuring both repositories are in sync.

    Args:
        file_path (str): The path to the file in both Dataform and GitHub.
        commit_message (Optional[str]): Custom commit message. If not provided, a default message is used.
        branch (Optional[str]): The GitHub branch to sync to. Defaults to the configured default branch.

    Returns:
        Dict[str, Any]: Result of the sync operation.
    """
    from .dataform_tools import read_file_from_dataform
    
    # Read from Dataform
    dataform_content = read_file_from_dataform(file_path)
    if dataform_content.startswith("Error"):
        return {
            "status": "error",
            "error_message": f"Failed to read from Dataform: {dataform_content}",
        }
    
    # Write to GitHub
    if not commit_message:
        commit_message = f"Sync {file_path} from Dataform"
    
    result = write_file_to_github(
        file_path=file_path,
        file_content=dataform_content,
        commit_message=commit_message,
        branch=branch,
    )
    
    return result


@agent_tool
def delete_github_branch(branch_name: str) -> Dict[str, Any]:
    """Delete a branch from the GitHub repository.

    This is typically used after a pull request has been merged to clean up feature branches.

    Args:
        branch_name (str): The name of the branch to delete (e.g., 'feature/add-apple-ads-source').

    Returns:
        Dict[str, Any]: Result of the branch deletion operation.
    """
    repo = _get_repo()
    if not repo:
        return {
            "status": "error",
            "error_message": "GitHub repository not configured.",
        }
    
    # Prevent deletion of default branch
    if branch_name == config.github_default_branch:
        return {
            "status": "error",
            "error_message": f"Cannot delete default branch '{branch_name}'. This is a safety measure.",
        }
    
    try:
        # Get the branch reference
        ref = repo.get_git_ref(f"heads/{branch_name}")
        
        # Delete the branch
        ref.delete()
        
        return {
            "status": "success",
            "message": f"Branch '{branch_name}' deleted successfully",
            "branch_name": branch_name,
        }
    except GithubException as e:
        if e.status == 404:
            return {
                "status": "error",
                "error_message": f"Branch '{branch_name}' not found. It may have already been deleted.",
            }
        error_msg = f"Error deleting branch '{branch_name}': {e}"
        print(error_msg)
        return {"status": "error", "error_message": error_msg}


@agent_tool
def get_merged_pull_requests(
    base_branch: Optional[str] = None, limit: int = 10
) -> Dict[str, Any]:
    """Get a list of merged pull requests.

    Useful for identifying branches that can be safely deleted after merging.

    Args:
        base_branch (Optional[str]): The base branch to check merged PRs for. Defaults to the configured default branch.
        limit (int): Maximum number of PRs to return (default: 10).

    Returns:
        Dict[str, Any]: List of merged pull requests with their branch names.
    """
    repo = _get_repo()
    if not repo:
        return {
            "status": "error",
            "error_message": "GitHub repository not configured.",
        }
    
    if not base_branch:
        base_branch = config.github_default_branch
    
    try:
        # Get merged pull requests
        prs = repo.get_pulls(
            state="closed", base=base_branch, sort="updated", direction="desc"
        )
        
        merged_prs = []
        for i, pr in enumerate(prs):
            if i >= limit:
                break
            if pr.merged:
                merged_prs.append({
                    "number": pr.number,
                    "title": pr.title,
                    "head_branch": pr.head.ref,
                    "merged_at": pr.merged_at.isoformat() if pr.merged_at else None,
                    "url": pr.html_url,
                })
        
        return {
            "status": "success",
            "base_branch": base_branch,
            "merged_prs": merged_prs,
        }
    except GithubException as e:
        error_msg = f"Error getting merged pull requests: {e}"
        print(error_msg)
        return {"status": "error", "error_message": error_msg}


@agent_tool
def cleanup_merged_branches(
    base_branch: Optional[str] = None, dry_run: bool = True
) -> Dict[str, Any]:
    """Delete all merged branches (feature branches from merged PRs).

    This tool finds all merged pull requests and deletes their corresponding branches.
    Useful for keeping the repository clean after PRs are merged.

    Args:
        base_branch (Optional[str]): The base branch to check merged PRs for. Defaults to the configured default branch.
        dry_run (bool): If True, only lists branches that would be deleted without actually deleting them (default: True).

    Returns:
        Dict[str, Any]: Result of the cleanup operation with list of deleted/would-be-deleted branches.
    """
    repo = _get_repo()
    if not repo:
        return {
            "status": "error",
            "error_message": "GitHub repository not configured.",
        }
    
    if not base_branch:
        base_branch = config.github_default_branch
    
    try:
        # Get merged PRs
        merged_prs_result = get_merged_pull_requests(base_branch, limit=50)
        if merged_prs_result.get("status") != "success":
            return merged_prs_result
        
        merged_prs = merged_prs_result.get("merged_prs", [])
        branches_to_delete = [pr["head_branch"] for pr in merged_prs]
        
        if dry_run:
            return {
                "status": "success",
                "mode": "dry_run",
                "message": f"Found {len(branches_to_delete)} branches that would be deleted",
                "branches": branches_to_delete,
                "note": "Run with dry_run=False to actually delete these branches",
            }
        
        # Actually delete branches
        deleted_branches = []
        failed_branches = []
        
        for branch_name in branches_to_delete:
            # Skip default branch
            if branch_name == base_branch:
                continue
            
            result = delete_github_branch(branch_name)
            if result.get("status") == "success":
                deleted_branches.append(branch_name)
            else:
                failed_branches.append({
                    "branch": branch_name,
                    "error": result.get("error_message"),
                })
        
        return {
            "status": "success",
            "mode": "delete",
            "message": f"Deleted {len(deleted_branches)} branches",
            "deleted_branches": deleted_branches,
            "failed_branches": failed_branches,
        }
    except Exception as e:
        error_msg = f"Error during branch cleanup: {e}"
        print(error_msg)
        return {"status": "error", "error_message": error_msg}

