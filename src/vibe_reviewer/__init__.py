"""Vibe Reviewer for GitHub Actions."""

import json
import os
import subprocess
from typing import Dict, Any


def analyze_pr_diff() -> Dict[str, Any]:
    """Analyze the PR diff and return metrics."""
    # Configure git to trust the workspace directory
    subprocess.run(
        ["git", "config", "--global", "--add", "safe.directory", "*"],
        capture_output=True,
    )

    # Get the event payload from GitHub Actions
    event_path = os.environ.get("GITHUB_EVENT_PATH", "")
    if not event_path:
        print("DEBUG: GITHUB_EVENT_PATH not set")
        return {"error": "GITHUB_EVENT_PATH not set"}

    print(f"DEBUG: Reading event from {event_path}")
    with open(event_path, "r") as f:
        event = json.load(f)

    # Extract PR details
    base_sha = event.get("pull_request", {}).get("base", {}).get("sha", "")
    head_sha = event.get("pull_request", {}).get("head", {}).get("sha", "")

    print(f"DEBUG: Base SHA: {base_sha}")
    print(f"DEBUG: Head SHA: {head_sha}")

    if not base_sha or not head_sha:
        print("DEBUG: Could not determine base or head SHA")
        return {"error": "Could not determine base or head SHA"}

    # Get git diff - use HEAD as the new commit and base_sha as the old
    try:
        print(f"DEBUG: Running git diff HEAD {base_sha}")
        diff_result = subprocess.run(
            ["git", "diff", "--numstat", base_sha, "HEAD"],
            capture_output=True,
            text=True,
            check=True,
        )
        print(f"DEBUG: Git diff output: {diff_result.stdout}")
    except subprocess.CalledProcessError as e:
        print(f"DEBUG: Failed to get git diff: {e}")
        print(f"DEBUG: Git stderr: {e.stderr}")
        return {"error": f"Failed to get git diff: {e}"}

    # Parse diff output
    lines = diff_result.stdout.strip().split("\n")
    total_additions = 0
    total_deletions = 0
    files_changed = 0
    has_tests = False

    for line in lines:
        if line.strip() == "":
            continue

        parts = line.split("\t")
        if len(parts) >= 3:
            additions = int(parts[0]) if parts[0] != "-" else 0
            deletions = int(parts[1]) if parts[1] != "-" else 0
            file_path = parts[2]

            total_additions += additions
            total_deletions += deletions
            files_changed += 1

            if "test" in file_path.lower():
                has_tests = True

    print(f"DEBUG: Found {files_changed} files changed")
    print(f"DEBUG: Total additions: {total_additions}")
    print(f"DEBUG: Total deletions: {total_deletions}")
    print(f"DEBUG: Has tests: {has_tests}")

    # Determine risk level
    if files_changed <= 5 and total_additions + total_deletions <= 50:
        risk_level = "LOW"
    elif files_changed <= 15 and total_additions + total_deletions <= 200:
        risk_level = "MEDIUM"
    else:
        risk_level = "HIGH"

    print(f"DEBUG: Risk level determined: {risk_level}")

    # Get the actual diff content for Mistral API
    try:
        diff_content = subprocess.run(
            ["git", "diff", base_sha, "HEAD"],
            capture_output=True,
            text=True,
            check=True,
        ).stdout

        # Send to Mistral API if API key is available
        if os.environ.get("MISTRAL_API_KEY"):
            print("DEBUG: Sending diff to Mistral API for review")
            mistral_review = send_to_mistral_api(diff_content, risk_level)
            print(f"DEBUG: Mistral review: {mistral_review}")
    except subprocess.CalledProcessError as e:
        print(f"DEBUG: Failed to get full diff: {e}")

    return {
        "risk-level": risk_level,
        "files-changed": files_changed,
        "has-tests": str(has_tests).lower(),
        "total-additions": total_additions,
        "total-deletions": total_deletions,
    }


def send_to_mistral_api(diff_content: str, risk_level: str) -> str:
    """Send the diff content to Mistral API for review."""
    from mistralai import Mistral
    import os

    api_key = os.environ.get("MISTRAL_API_KEY", "")
    if not api_key:
        print("DEBUG: MISTRAL_API_KEY not set")
        return "No API key provided"

    # Load the system prompt
    try:
        with open("review.md", "r") as f:
            system_prompt = f.read()
    except FileNotFoundError:
        print("DEBUG: review.md not found")
        system_prompt = (
            "You are a code reviewer. Please review the following code changes."
        )

    # Prepare the messages
    messages = [
        {
            "content": system_prompt,
            "role": "system",
        },
        {
            "content": f"## Code Changes\n\nRisk Level: {risk_level}\n\n```diff\n{diff_content}\n```",
            "role": "user",
        },
    ]

    # Call Mistral API using the official client
    try:
        with Mistral(api_key=api_key) as mistral:
            res = mistral.chat.complete(
                model="mistral-small-latest",
                messages=messages,
                stream=False,
            )

            # Extract the content from the response
            if hasattr(res, "choices") and len(res.choices) > 0:
                return res.choices[0].message.content
            else:
                return str(res)

    except Exception as e:
        print(f"DEBUG: Mistral API exception: {e}")
        return f"API exception: {str(e)}"


def set_outputs(outputs: Dict[str, Any]) -> None:
    """Set GitHub Actions outputs."""
    github_output = os.environ.get("GITHUB_OUTPUT", "")
    if not github_output:
        print("DEBUG: GITHUB_OUTPUT not set, skipping output writing")
        return

    print(f"DEBUG: Writing outputs to {github_output}")
    print(f"DEBUG: Outputs: {outputs}")

    with open(github_output, "a") as f:
        for key, value in outputs.items():
            f.write(f"{key}={value}\n")
    print("DEBUG: Outputs written successfully")


def main() -> None:
    """Main entry point for the GitHub Action."""
    results = analyze_pr_diff()
    set_outputs(results)


if __name__ == "__main__":
    main()
