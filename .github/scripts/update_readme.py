#!/usr/bin/env python3
"""Auto-update the 'Recent Repositories' section of the GitHub profile README."""

import json
import os
import urllib.request

USERNAME = "ramathankigozi8-glitch"
README_PATH = "README.md"
MARKER_START = "<!-- PROJECTS:START -->"
MARKER_END = "<!-- PROJECTS:END -->"

TOKEN = os.environ.get("GH_TOKEN") or os.environ.get("GITHUB_TOKEN")


def fetch_repositories():
    headers = {
        "Accept": "application/vnd.github+json",
        "User-Agent": "readme-updater",
        "X-GitHub-Api-Version": "2022-11-28",
    }
    if TOKEN:
        headers["Authorization"] = f"Bearer {TOKEN}"

    url = f"https://api.github.com/users/{USERNAME}/repos?per_page=100&sort=pushed"
    request = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(request) as response:
        return json.load(response)


def build_repo_list(repos):
    lines = []
    for repo in repos:
        if repo.get("fork"):
            continue
        if repo["name"].lower() == USERNAME.lower():
            continue

        name = repo["name"]
        url = repo["html_url"]
        description = repo.get("description") or "No description provided"
        language = repo.get("language") or "Various"
        stars = repo["stargazers_count"]
        topics = " · ".join(repo.get("topics", [])[:4])

        line = f"- **[{name}]({url})** — {description}"
        meta = f"  `{language}` ⭐ {stars}"
        if topics:
            meta += f" · `{topics}`"
        line += f"<br>{meta}"
        lines.append(line)

    if not lines:
        lines.append(
            "_No public repositories yet — check back soon as I publish my "
            "data analytics projects!_"
        )

    return "\n".join(lines)


def update_readme(markdown):
    with open(README_PATH, "r", encoding="utf-8") as f:
        content = f.read()

    if MARKER_START not in content or MARKER_END not in content:
        raise SystemExit(
            f"Markers {MARKER_START} / {MARKER_END} not found in {README_PATH}."
        )

    start = content.index(MARKER_START) + len(MARKER_START)
    end = content.index(MARKER_END)

    new_section = f"\n{markdown}\n"
    updated = content[:start] + new_section + content[end:]

    with open(README_PATH, "w", encoding="utf-8") as f:
        f.write(updated)


def main():
    repos = fetch_repositories()
    markdown = build_repo_list(repos)
    update_readme(markdown)
    print("README updated successfully.")


if __name__ == "__main__":
    main()
