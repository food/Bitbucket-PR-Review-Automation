#!/usr/bin/env python3
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

from get_prs import get_prs
import subprocess

# === Chose prs to review ===
def select_prs(prs) -> list:
    print("📋 Open PRs to review:\n")
    for i, pr in enumerate(prs, 1):
        title = pr['title']
        author = pr['author']['user']['displayName']
        link = pr['links']['self'][0]['href']
        print(f"{i}. {title}  👤 {author}\n   🔗 {link}\n")

    selection = input("🔢 Which PRs do you like to review? (1,2,3): ").strip()
    indices = [int(x) - 1 for x in selection.split(",") if x.strip().isdigit()]
    return [prs[i] for i in indices if 0 <= i < len(prs)]

# === Pass to pr_review.py ===
def review_selected_prs(selected):
    for pr in selected:
        pr_url = pr['links']['self'][0]['href']
        print(f"\n🚀 Start review for: {pr_url}")
        subprocess.run(["python", "review_pr.py", pr_url])

def main():
    prs = get_prs()
    selected_prs = select_prs(prs)

    if not selected_prs:
        print("⚠️ No PRs to review.")
        return

    review_selected_prs(selected_prs)


if __name__ == "__main__":
    main()