#!/usr/bin/env python3
"""Regenerate CHANGELOG.md from GitHub milestones, releases and pull requests.

Usage: GITHUB_TOKEN=... python3 dev-tools/create_changelog.py <release version> [output path]

A milestone titled with a version collects the pull requests shipped in that version.
"""
import json
import os
import sys
import urllib.request
from datetime import datetime

API = "https://api.github.com/repos/kyuridenamida/atcoder-tools"
# 1.1.8 is pending for a special reason. 1.1.7.1 was mistakenly released, so it is ordered as 1.1.71.
IGNORED_MILESTONES = {"1.1.8"}
VERSION_ALIASES = {"1.1.7.1": "1.1.71"}


def fetch_all(path):
    items = []
    for page in range(1, 51):
        request = urllib.request.Request(
            "{}/{}&per_page=100&page={}".format(API, path, page))
        if os.environ.get("GITHUB_TOKEN"):
            request.add_header(
                "Authorization", "Bearer " + os.environ["GITHUB_TOKEN"])
        with urllib.request.urlopen(request) as response:
            partial = json.load(response)
        if not partial:
            return items
        items.extend(partial)
    raise RuntimeError("Unexpectedly too many pages: " + path)


def version_key(version):
    # Raises ValueError for a title which is not a version.
    major, minor, patch = VERSION_ALIASES.get(version, version).split(".")
    return int(major), int(minor), int(patch)


def label_cell(label):
    return "![#{0}](https://via.placeholder.com/15/{0}/000000?text=+) **{1}**".format(
        label["color"], label["name"])


def create_changelog(latest_version):
    milestones = sorted(
        (m for m in fetch_all("milestones?state=all")
         if m["title"] not in IGNORED_MILESTONES
         and version_key(m["title"]) <= version_key(latest_version)),
        key=lambda m: version_key(m["title"]), reverse=True)
    release_by_tag = {r["tag_name"]: r for r in fetch_all("releases?")}
    pull_requests = fetch_all("pulls?state=all")
    if latest_version not in release_by_tag:
        raise RuntimeError("No latest version released: " + latest_version)

    lines = ["# Change Log"]
    for milestone in milestones:
        # KeyError here means the milestone has no corresponding release.
        release = release_by_tag[milestone["title"]]
        published_at = datetime.strptime(
            release["published_at"], "%Y-%m-%dT%H:%M:%SZ")
        lines.append("## {} / {}-{}-{}".format(
            milestone["title"], published_at.year, published_at.month, published_at.day))
        if (release["body"] or "").strip():
            lines.append(release["body"].strip())
        lines.append("|PR|Change Summary|Label|Author|")
        lines.append("|:---|:---|:---|:---:|")
        for pr in pull_requests:
            if (pr["milestone"] or {}).get("id") != milestone["id"]:
                continue
            if any(label["name"] == "release" for label in pr["labels"]):
                # Release PRs are useless to show
                continue
            lines.append("|[#{}]({})|{}|{}|[{}]({})|".format(
                pr["number"], pr["html_url"], pr["title"].replace("|", " "),
                "<br/>".join(map(label_cell, pr["labels"])) or " ",
                pr["user"]["login"], pr["user"]["html_url"]))
    return "\n".join(lines)


if __name__ == "__main__":
    output_path = sys.argv[2] if len(sys.argv) > 2 else "CHANGELOG.md"
    changelog = create_changelog(sys.argv[1])
    with open(output_path, "w") as f:
        f.write(changelog)
