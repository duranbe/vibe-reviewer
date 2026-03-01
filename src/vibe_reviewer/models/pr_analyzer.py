"""PRAnalyzer model for analyzing pull request diffs."""

import json
import os
from typing import Dict, Any

from ..models.git_diff import GitDiff
from ..models.mistral_api import MistralAPI


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
            print("DEBUG: GITHUB_EVENT_PATH not set")
            return {"error": "GITHUB_EVENT_PATH not set"}

        print(f"DEBUG: Reading event from {event_path}")
        with open(event_path, "r") as f:
            event = json.load(f)

        return event

    def _create_diff(self, event: Dict[str, Any]) -> Dict[str, Any]:
        """Create GitDiff object from event data."""
        base_sha = event.get("pull_request", {}).get("base", {}).get("sha", "")
        head_sha = event.get("pull_request", {}).get("head", {}).get("sha", "")

        print(f"DEBUG: Base SHA: {base_sha}")
        print(f"DEBUG: Head SHA: {head_sha}")

        if not base_sha or not head_sha:
            print("DEBUG: Could not determine base or head SHA")
            return {"error": "Could not determine base or head SHA"}

        diff = GitDiff(base_sha, head_sha)
        diff.configure_git()
        diff.get_diff_stats()

        return diff

    def _analyze_diff(self) -> None:
        """Analyze the diff and get Mistral review if available."""
        risk_level = self.diff.determine_risk_level()
        print(f"DEBUG: Risk level determined: {risk_level}")

        self.diff.get_diff_content()

        if os.environ.get("MISTRAL_API_KEY"):
            print("DEBUG: Sending diff to Mistral API for review")
            self.mistral_api = MistralAPI(os.environ.get("MISTRAL_API_KEY"))
            mistral_review = self.mistral_api.review_diff(
                self.diff.diff_content, risk_level
            )
            mistral_review.replace("\"","\'")
            print(f"DEBUG: Mistral review: {mistral_review}")
            self.diff.mistral_review = mistral_review

    def _build_outputs(self) -> Dict[str, Any]:
        """Build the outputs dictionary."""
        outputs = {
            "risk-level": self.diff.determine_risk_level(),
            "files-changed": self.diff.files_changed,
            "has-tests": str(self.diff.has_tests).lower(),
            "total-additions": self.diff.total_additions,
            "total-deletions": self.diff.total_deletions,
        }

        if hasattr(self.diff, "mistral_review"):
            outputs["message"] = self.diff.mistral_review

        return outputs
