"""PRAnalyzer model for analyzing pull request diffs."""

import json
import logging
import os
from typing import Dict, Any

from ..models.git_diff import GitDiff
from ..models.mistral_api import MistralAPI
from ..utils.github_api import GitHubAPI


class PRAnalyzer:
    """Class to analyze pull request diffs."""

    def __init__(self):
        self.diff = None
        self.mistral_api = None

    def analyze_pr_diff(self) -> Dict[str, Any]:
        """Analyze the PR diff and return metrics."""
        event = self._load_event()
        if isinstance(event, dict) and "error" in event:
            return event

        self.diff = self._create_diff(event)
        if isinstance(self.diff, dict) and "error" in self.diff:
            return self.diff

        self._analyze_diff()

        outputs = self._build_outputs()
        return outputs

    def _load_event(self) -> Dict[str, Any]:
        """Load the GitHub event payload."""
        event_path = os.environ.get("GITHUB_EVENT_PATH", "")
        if not event_path:
            logging.debug("GITHUB_EVENT_PATH not set")
            return {"error": "GITHUB_EVENT_PATH not set"}

        logging.debug(f"Reading event from {event_path}")
        with open(event_path, "r") as f:
            event = json.load(f)

        return event

    def _create_diff(self, event: Dict[str, Any]) -> Dict[str, Any]:
        """Create GitDiff object from event data."""
        base_sha = event.get("pull_request", {}).get("base", {}).get("sha", "")
        head_sha = event.get("pull_request", {}).get("head", {}).get("sha", "")

        logging.debug(f"Base SHA: {base_sha}")
        logging.debug(f"Head SHA: {head_sha}")

        if not base_sha or not head_sha:
            logging.debug("Could not determine base or head SHA")
            return {"error": "Could not determine base or head SHA"}

        diff = GitDiff(base_sha, head_sha)
        diff.configure_git()
        diff.get_diff_stats()

        return diff

    def _analyze_diff(self) -> None:
        """Analyze the diff and get Mistral review if available."""
        risk_level = self.diff.determine_risk_level()
        logging.debug(f"Risk level determined: {risk_level}")

        self.diff.get_diff_content()

        if os.environ.get("MISTRAL_API_KEY"):
            logging.debug("Sending diff to Mistral API for review")
            self.mistral_api = MistralAPI(os.environ.get("MISTRAL_API_KEY"))
            mistral_review = self.mistral_api.review_diff(
                self.diff.diff_content, risk_level
            )
            mistral_review = mistral_review.replace('"', "'")
            logging.debug(f"Mistral review: {mistral_review}")
            self.diff.mistral_review = mistral_review

    def _build_outputs(self) -> Dict[str, Any]:
        """Build the outputs dictionary and post comment to PR."""
        outputs = {
            "risk-level": self.diff.determine_risk_level(),
            "files-changed": self.diff.files_changed,
            "has-tests": str(self.diff.has_tests).lower(),
            "total-additions": self.diff.total_additions,
            "total-deletions": self.diff.total_deletions,
        }

        if hasattr(self.diff, "mistral_review"):
            outputs["message"] = self.diff.mistral_review

        # Post comment to PR if this is a pull request event
        self._post_pr_comment(outputs)

        return outputs

    def _post_pr_comment(self, outputs: Dict[str, Any]) -> None:
        """Post a comment to the PR using GitHub API."""
        event = self._load_event()
        if not isinstance(event, dict) or "pull_request" not in event:
            logging.debug("Not a pull request event, skipping comment")
            return

        # Extract PR information
        pr_number = event.get("pull_request", {}).get("number")
        owner = event.get("repository", {}).get("owner", {}).get("login")
        repo = event.get("repository", {}).get("name")

        if not all([pr_number, owner, repo]):
            logging.debug("Missing PR information, skipping comment")
            return

        # Build comment body
        comment_body = (
            f"🎯 Vibe Review: **{outputs['risk-level']}** risk\n\n"
            f"- Files changed: {outputs['files-changed']}\n"
            f"- Lines added: {outputs['total-additions']}\n"
            f"- Lines deleted: {outputs['total-deletions']}\n"
            f"- Tests included: {outputs['has-tests']}"
        )

        # Add AI review message if available
        if "message" in outputs:
            decoded_message = (
                outputs["message"].replace("%0A", "\n").replace("%0D", "\r")
            )
            comment_body += f"\n\n🤖 **AI Review:**\n\n{decoded_message}"

        # Post comment using GitHub API
        GitHubAPI.post_comment(
            owner=owner,
            repo=repo,
            issue_number=pr_number,
            comment_body=comment_body,
        )
