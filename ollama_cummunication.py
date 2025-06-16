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
from dotenv import load_dotenv
import requests
import sys

# === Load .env file ===
load_dotenv()
OLLAMA_HOST = os.getenv("OLLAMA_HOST")

def generate_ollama_response(prompt: str, model: str | None = "codellama"):
    """
    Send prompt to Ollama and return its response.
    """
    payload = {
        "model": model,
        "prompt": prompt,
        "stream": False
    }
    res = requests.post(f"{OLLAMA_HOST}/api/generate", json=payload)
    if res.status_code != 200:
        print("❌ Error in request to Ollama.")
        print(res.text)
        sys.exit(1)
    return res.json()["response"].strip()
