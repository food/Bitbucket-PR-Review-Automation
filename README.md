# Bitbucket PR Review Automation

Automate code review and pull request workflows for Bitbucket Server using Python and Ollama AI.

## Features

- **List and filter open PRs** assigned to you, with project/user ignore lists.
- **Interactive PR selection** for review.
- **Automated code review**: Fetches PR diffs and generates structured AI reviews using Ollama.
- **Commit and PR automation**: Stages, commits (with AI-generated messages), pushes, and opens PRs.
- **Markdown review reports**: Saves AI review results in the `reviews/` directory.

## Requirements

- Python 3.10+
- [Ollama](https://ollama.com/) running and accessible
- Bitbucket Server access with API token
- [GitPython](https://gitpython.readthedocs.io/en/stable/)

Install dependencies:

```sh
pip install -r requirements.txt
```

## Setup

1. Copy `.env.example` to `.env` and fill in your Bitbucket and Ollama credentials.
2. Ensure your Bitbucket token has API access.
3. Start your Ollama server and load the required models.

## Usage

### 1. List and Review PRs

```sh
python pr_manager.py
```

- Lists open PRs (filtered).
- Select PRs to review (e.g., `1,3`).
- For each, fetches the diff and generates an AI review, saving results in `reviews/`.

### 2. Commit and Create PR

```sh
python commit_and_pr.py /path/to/your/repo target-branch
```

- Runs code checks (AI review of staged changes).
- Stages all changes, generates commit message with AI, commits, pushes, and opens a PR.

### 3. Manual PR Review

```sh
python review_pr.py <bitbucket-pr-link>
```

- Fetches the PR diff and generates an AI review.

## Environment Variables

Configure these in your `.env` file:

- `BITBUCKET_BASE_URL` - Bitbucket Server URL
- `BITBUCKET_USERNAME` - Your Bitbucket username
- `BITBUCKET_TOKEN` - Bitbucket API token
- `IGNORE_PROJECTS` - Comma-separated list of project keys to ignore
- `IGNORE_USERS` - Comma-separated list of usernames to ignore
- `OLLAMA_HOST` - Ollama server URL
- `OLLAMA_MODEL` - Model for code review
- `OLLAMA_MODEL_GIT` - Model for commit message generation
- `OLLAMA_PROMT_REVIEW` - Prompt template for code review

See `.env.example` for details.

## Directory Structure

```
.
├── commit_and_pr.py
├── get_prs.py
├── ollama_cummunication.py
├── pr_manager.py
├── review_pr.py
├── requirements.txt
├── .env
├── .env.example
├── reviews/
│   └── *.md
```

## Notes

- Review markdown files are saved in the `reviews/` directory.
- Only Bitbucket Server (self-hosted) is supported.
- Make sure your Ollama models are available and running.

## TODO

- improve docs and comments
- using lib dir and add file to remove redundancies

## License

This project is licensed under the GNU General Public License v3.0 - see the [LICENSE](LICENSE) file for details.