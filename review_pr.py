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

import requests
import os
import sys
import re
from dotenv import load_dotenv
from datetime import datetime

from ollama_cummunication import generate_ollama_response

# === Load .env file ===
load_dotenv()
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL")
OLLAMA_PROMT = os.getenv("OLLAMA_PROMT_REVIEW")
BITBUCKET_BASE_URL = os.getenv("BITBUCKET_BASE_URL")
TOKEN = os.getenv("BITBUCKET_TOKEN")


# ==== Convert PR-URL to API-Link ====
def pr_to_diff_url(pr_url):
    match = re.match(
        r"https://[^/]+/projects/([^/]+)/repos/([^/]+)/pull-requests/(\d+)",
        pr_url
    )
    if not match:
        print("❌ Invalid Bitbucket Server PR link.")
        sys.exit(1)
    project_key, repo_slug, pr_id = match.groups()
    return f"{BITBUCKET_BASE_URL}/rest/api/latest/projects/{project_key}/repos/{repo_slug}/pull-requests/{pr_id}/diff"


# ==== Download Diff ====
def fetch_pr_diff(diff_url, token):
    print(f"🔗 Fetching diff from: {diff_url}")
    print(f"🔑 Using token: {token}")
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "text/plain"
    }
    res = requests.get(diff_url, headers=headers)
    if res.status_code != 200:
        print(f"❌ Error retrieving diff: {res.status_code}")
        print(res.text)
        sys.exit(1)
    return res.text


# ==== Save Markdown ====
def sanitize_filename(text):
    return re.sub(r'[^a-zA-Z0-9_\-]', '_', text)[:60]


def save_markdown(pr_url, response_text, diff_text):
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M")
    pr_id_match = re.search(r"/pull-requests/(\d+)", pr_url)
    pr_id = pr_id_match.group(1) if pr_id_match else "unknown"

    title = f"Review_PR_{pr_id}_{timestamp}"
    filename = sanitize_filename(title) + ".md"
    os.makedirs("reviews", exist_ok=True)

    with open(os.path.join("reviews", filename), "w", encoding="utf-8") as f:
        f.write(f"# Review from Pull Request 🔗 [#{pr_id}]({pr_url})\n")
        f.write(f"- 📅 Date: {timestamp}\n")
        f.write(f"## 💡 Summarise from AI (model: {OLLAMA_MODEL})\n\n")
        f.write(response_text.strip() + "\n\n")
        f.write("<details>\n<summary>📄 show Diff</summary>\n\n")
        f.write("```diff\n")
        #f.write(diff_text[:5000])  # first 5k characters
        f.write(diff_text)  # first 5k characters
        f.write("\n```\n</details>\n")

    print(f"📝 Review gespeichert unter: reviews/{filename}")


def main():
    # ==== Arg check ====
    if len(sys.argv) != 2:
        print("❌ Usage: python pr_review.py <bitbucket-pr-link>")
        sys.exit(1)

    pr_url = sys.argv[1]

    diff_url = pr_to_diff_url(pr_url)
    print(f"🔍 Get PR diff from:: {diff_url}")
    diff_text = fetch_pr_diff(diff_url, TOKEN)

    # Prompt creation
    prompt = f"""
    {OLLAMA_PROMT}

    Diff:
    {diff_text}
    """

    print("🤖 Send to Ollama...")

    response = generate_ollama_response(prompt, OLLAMA_MODEL)
    print("\n📘 Explain and Review:\n")
    print(response)

    save_markdown(pr_url, response, diff_text)


if __name__ == "__main__":
    main()
