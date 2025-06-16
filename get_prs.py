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
import json
from dotenv import load_dotenv
from requests.auth import HTTPBasicAuth

# === Load .env file ===
load_dotenv()
USERNAME = os.getenv("BITBUCKET_USERNAME")
TOKEN = os.getenv("BITBUCKET_TOKEN")
BITBUCKET_BASE_URL = os.getenv("BITBUCKET_BASE_URL")

# Filter: comma-separated list → Python list (all lowercase)
IGNORE_PROJECTS = [p.strip().lower() for p in os.getenv("IGNORE_PROJECTS", "").split(",") if p.strip()]
IGNORE_USERS = [u.strip().lower() for u in os.getenv("IGNORE_USERS", "").split(",") if u.strip()]

if not USERNAME or not TOKEN:
    print("❌ BITBUCKET_USERNAME or BITBUCKET_TOKEN missing in .env")
    exit(1)

# === Fetch Pull Requests ===
def get_assigned_prs():
    url = f"{BITBUCKET_BASE_URL}/rest/api/latest/inbox/pull-requests"
    res = requests.get(url, auth=HTTPBasicAuth(USERNAME, TOKEN)) # type: ignore

    if res.status_code != 200:
        print(f"❌ Error while fetching: {res.status_code}")
        print(res.text)
        return []

    data = res.json()
    return data.get("values", [])

# === Filter PRs by Project & Author ===
def filter_prs(prs):
    filtered = []
    for pr in prs:
        project = pr["toRef"]["repository"]["project"]["key"].lower()
        author_name = pr["author"]["user"]["displayName"].lower()

        if project in IGNORE_PROJECTS:
            continue
        if author_name in IGNORE_USERS:
            continue

        filtered.append(pr)
    return filtered

def get_prs()-> list:
    prs = get_assigned_prs()
    filtered_prs = filter_prs(prs)

    if not filtered_prs:
        return []

    return filtered_prs


# === Display ===
def main():
    prs = get_assigned_prs()
    filtered_prs = filter_prs(prs)

    if not filtered_prs:
        print("📭 No open PRs found for you (after filtering).")
    else:
        print(f"📌 You have {len(filtered_prs)} open PR(s) to review:\n")
        for pr in filtered_prs:
            title = pr['title']
            author = pr['author']['user']['displayName']
            link = pr['links']['self'][0]['href']
            print(f"📝 {title}\n👤 {author}\n📁 Project: {pr['toRef']['repository']['project']['key']}\n🔗 {link}\n")


if __name__ == "__main__":
    main()