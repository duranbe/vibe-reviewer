"""GitHub API utilities for interacting with GitHub's REST API."""

import logging
import os
from typing import Optional
import requests


class GitHubAPI:
    """Class to handle GitHub API interactions."""

    @staticmethod
    def post_comment(
        owner: str,
        repo: str,
        issue_number: int,
        comment_body: str,
        token: Optional[str] = None,
    ) -> bool:
        """Post a comment to a GitHub issue or PR using the GitHub API.

        Args:
            owner: Repository owner (e.g., "octocat")
            repo: Repository name (e.g., "Hello-World")
            issue_number: Issue or PR number
            comment_body: The comment text to post
            token: GitHub personal access token. If None, will try to get from GITHUB_TOKEN env var.

        Returns:
            bool: True if comment was posted successfully, False otherwise
        """
        # Get token from environment if not provided
        if token is None:
            token = os.environ.get("GITHUB_TOKEN")
            if token is None:
                logging.error("No GitHub token provided and GITHUB_TOKEN not set in environment")
                return False

        # GitHub API endpoint
        url = f"https://api.github.com/repos/{owner}/{repo}/issues/{issue_number}/comments"

        # Headers
        headers = {
            "Accept": "application/vnd.github+json",
            "Authorization": f"Bearer {token}",
            "X-GitHub-Api-Version": "2022-11-28",
        }

        # Payload
        payload = {"body": comment_body}

        try:
            response = requests.post(url, headers=headers, json=payload)
            response.raise_for_status()
            logging.info(f"Successfully posted comment to {owner}/{repo}#{issue_number}")
            return True
        except requests.exceptions.RequestException as e:
            logging.error(f"Failed to post comment: {e}")
            return False
