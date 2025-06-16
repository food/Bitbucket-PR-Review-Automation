# get_prs.py - Bitbucket PR Fetcher
#
# This file is part of pr_review.
#
# pr_review is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# pr_review is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with pr_review.  If not, see <https://www.gnu.org/licenses/>.
#
# Copyright (C) 2025 Tibor Helmig

import os
import sys
import re
import requests
from git import Repo
from dotenv import load_dotenv
from ollama_cummunication import generate_ollama_response

# === Load .env file ===
load_dotenv()
BITBUCKET_BASE_URL = os.getenv("BITBUCKET_BASE_URL")
BITBUCKET_TOKEN = os.getenv("BITBUCKET_TOKEN")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL")
OLLAMA_MODEL_GIT = os.getenv("OLLAMA_MODEL_GIT")

# === ENV CHECKS ===
def check_env_variables():
    required_vars = [
        "BITBUCKET_BASE_URL",
        "BITBUCKET_TOKEN",
        "OLLAMA_HOST",
        "OLLAMA_MODEL",
        "OLLAMA_MODEL_GIT"
    ]
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    if missing_vars:
        print(
            f"❌ Missing required environment variables: {', '.join(missing_vars)}")
        sys.exit(1)

# === CODE CHECK ===


def run_code_check(repo_path):
    print("🔍 Running Code checks...")
    diff_text = get_local_diff(repo_path, staged=True)

    # Prompt creation
    prompt = f"""
    Find security issues and codesmell violations in the following code diff.
    If you find any, please provide a detailed review of the issues found.
    If you find no issues, simply respond with "No issues found".
    Please provide your review in the following format:
    - If issues are found:
      - "Issues found"
      - Detailed description of each issue
      - Code snippets with issues highlighted
    - If no issues are found:
      - "No issues found"

    Diff:
    {diff_text}
    """

    response = generate_ollama_response(prompt, OLLAMA_MODEL)
    print("\n👀 Review:\n")
    print(response)


def get_local_diff(repo_path, staged=False):
    repo = Repo(repo_path)
    if staged:
        diff = repo.git.diff('--cached')  # nur staged changes
    else:
        diff = repo.git.diff()  # nur ungestaged changes
    return diff.strip()


def extract_project_and_slug_from_origin(repo):
    """
    Extract project key and repo slug from the 'origin' remote URL.
    """
    origin_url = repo.remotes.origin.url
    match = re.search(r"/([^/]+)/([^/.]+)(?:\.git)?$", origin_url)
    if not match:
        print("❌ Could not extract project key and repo slug from origin URL.")
        sys.exit(1)
    project_key = match.group(1)
    repo_slug = match.group(2)
    print(f"📦 Project: {project_key}, Repo: {repo_slug}")
    return project_key, repo_slug


def get_diff_for_ai(repo: Repo):
    """
    Get staged diff or full diff if nothing staged.
    """
    diff = repo.git.diff('--cached', '--unified=0')
    if not diff:
        diff = repo.git.diff('--unified=0')
    return diff.strip()


def stage_all_and_commit(repo_path):
    """
    Stage all changes, ask Ollama for commit message, and commit.
    """
    repo = Repo(repo_path)
    repo.git.add(A=True)

    diff = get_diff_for_ai(repo)
    if not diff:
        print("✅ No changes to commit.")
        sys.exit(0)

    prompt = f"""
You are a helpful Git assistant.

Here is a Git diff:

{diff}

Please generate a meaningful Git commit message using the Conventional Commits format.
- First line: short title (e.g. feat: Add login handler)
- Following lines: optional body (why/what changed).
"""
    response = generate_ollama_response(prompt, OLLAMA_MODEL_GIT)
    lines = response.strip().splitlines()
    if lines[0] != "```":
        title = lines[0]
        body = "\n".join(lines[1:]).strip()
    else:
        title = lines[1]
        body = "\n".join(lines[2:]).strip()

    repo.index.commit(title + ("\n\n" + body if body else ""))
    print(f"✅ Commit created: {title}")
    return [repo, title, body]


def push_branch(repo):
    """
    Push the current branch to the remote.
    """
    branch = repo.active_branch.name
    repo.remotes.origin.push(refspec=f"{branch}:{branch}")
    print(f"🚀 Pushed branch: {branch}")
    return branch


def create_pull_request(repo, branch, target_branch, title, description):
    project_key, repo_slug = extract_project_and_slug_from_origin(repo)

    url = f"{BITBUCKET_BASE_URL}/rest/api/latest/projects/{project_key}/repos/{repo_slug}/pull-requests"
    headers = {
        "Authorization": f"Bearer {BITBUCKET_TOKEN}",
        "Content-Type": "application/json"
    }
    payload = {
        "title": title,
        "description": description,
        "state": "OPEN",
        "open": True,
        "closed": False,
        "fromRef": {
            "id": f"refs/heads/{branch}",
            "repository": {
                "slug": repo_slug,
                "project": {"key": project_key}
            }
        },
        "toRef": {
            "id": f"refs/heads/{target_branch}",
            "repository": {
                "slug": repo_slug,
                "project": {"key": project_key}
            }
        },
        "reviewers": []
    }

    res = requests.post(url, headers=headers, json=payload)
    if res.status_code != 201:
        print(f"❌ Failed to create PR: {res.status_code}")
        print(res.text)
        sys.exit(1)

    pr_url = res.json()["links"]["self"][0]["href"]
    print(f"✅ Pull request created: {pr_url}")


def main():
    if len(sys.argv) != 3:
        print("❌ Usage: python auto_commit_pr.py /path/to/repo target-branch")
        sys.exit(1)

    check_env_variables()

    repo_path = sys.argv[1]
    target_branch = sys.argv[2]

    if not os.path.isdir(os.path.join(repo_path, ".git")):
        print("❌ Provided path is not a Git repository.")
        sys.exit(1)

    # --- Code Check ---
    if not run_code_check(repo_path):
        answer = input("❓ Would you like proceed? (y/n): ").strip().lower()
        if answer != 'y':
            print("🚫 Canceled by user.")
            sys.exit(0)

    [repo, title, body] = stage_all_and_commit(repo_path)
    branch = push_branch(repo)
    create_pull_request(repo, branch, target_branch, title, body)


if __name__ == "__main__":
    main()
