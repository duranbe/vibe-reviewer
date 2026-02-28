"""PR Diff Analyzer for GitHub Actions."""

import json
import os
import subprocess
from typing import Dict, Any


def analyze_pr_diff() -> Dict[str, Any]:
    """Analyze the PR diff and return metrics."""
    # Get the event payload from GitHub Actions
    event_path = os.environ.get("GITHUB_EVENT_PATH", "")
    if not event_path:
        return {"error": "GITHUB_EVENT_PATH not set"}

    with open(event_path, "r") as f:
        event = json.load(f)

    # Extract PR details
    base_sha = event.get("pull_request", {}).get("base", {}).get("sha", "")
    head_sha = event.get("pull_request", {}).get("head", {}).get("sha", "")

    if not base_sha or not head_sha:
        return {"error": "Could not determine base or head SHA"}

    # Get git diff
    try:
        diff_result = subprocess.run(
            ["git", "diff", "--numstat", base_sha, head_sha],
            capture_output=True,
            text=True,
            check=True,
        )
    except subprocess.CalledProcessError as e:
        return {"error": f"Failed to get git diff: {e}"}

    # Parse diff output
    lines = diff_result.stdout.strip().split("\n")
    total_additions = 0
    total_deletions = 0
    files_changed = len(lines)
    has_tests = False

    for line in lines:
        parts = line.split("\t")
        if len(parts) >= 3:
            additions = int(parts[0]) if parts[0] != "-" else 0
            deletions = int(parts[1]) if parts[1] != "-" else 0
            file_path = parts[2]

            total_additions += additions
            total_deletions += deletions

            if "test" in file_path.lower():
                has_tests = True

    # Determine risk level
    if files_changed <= 5 and total_additions + total_deletions <= 50:
        risk_level = "LOW"
    elif files_changed <= 15 and total_additions + total_deletions <= 200:
        risk_level = "MEDIUM"
    else:
        risk_level = "HIGH"

    return {
        "risk-level": risk_level,
        "files-changed": files_changed,
        "has-tests": str(has_tests).lower(),
        "total-additions": total_additions,
        "total-deletions": total_deletions,
    }


def set_outputs(outputs: Dict[str, Any]) -> None:
    """Set GitHub Actions outputs."""
    with open(os.environ.get("GITHUB_OUTPUT", ""), "a") as f:
        for key, value in outputs.items():
            f.write(f"{key}={value}\n")


def main() -> None:
    """Main entry point for the GitHub Action."""
    results = analyze_pr_diff()
    set_outputs(results)


if __name__ == "__main__":
    main()
