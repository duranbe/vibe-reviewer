"""GitDiff model for handling git diff operations and parsing."""

import logging
import subprocess
from typing import Dict, Any


class GitDiff:
    """Class to handle git diff operations and parsing."""

    def __init__(self, base_sha: str, head_sha: str):
        self.base_sha = base_sha
        self.head_sha = head_sha
        self.total_additions = 0
        self.total_deletions = 0
        self.files_changed = 0
        self.has_tests = False
        self.diff_content = ""

    def configure_git(self) -> None:
        """Configure git to trust the workspace directory."""
        subprocess.run(
            ["git", "config", "--global", "--add", "safe.directory", "*"],
            capture_output=True,
        )

    def get_diff_stats(self) -> None:
        """Get git diff statistics."""
        try:
            diff_result = subprocess.run(
                ["git", "diff", "--numstat", self.base_sha, self.head_sha],
                capture_output=True,
                text=True,
                check=True,
            )
            self._parse_diff_stats(diff_result.stdout)
        except subprocess.CalledProcessError as e:
            logging.debug(f"Failed to get git diff: {e}")
            raise

    def get_diff_content(self) -> None:
        """Get the full diff content."""
        try:
            result = subprocess.run(
                ["git", "diff", self.base_sha, self.head_sha],
                capture_output=True,
                text=True,
                check=True,
            )
            self.diff_content = result.stdout
        except subprocess.CalledProcessError as e:
            logging.debug(f"Failed to get full diff: {e}")
            raise

    def _parse_diff_stats(self, diff_output: str) -> None:
        """Parse git diff output to extract statistics."""
        lines = diff_output.strip().split("\n")

        for line in lines:
            if line.strip() == "":
                continue

            parts = line.split("\t")
            if len(parts) >= 3:
                additions = int(parts[0]) if parts[0] != "-" else 0
                deletions = int(parts[1]) if parts[1] != "-" else 0
                file_path = parts[2]

                self.total_additions += additions
                self.total_deletions += deletions
                self.files_changed += 1

                if "test" in file_path.lower():
                    self.has_tests = True

    def determine_risk_level(self) -> str:
        """Determine risk level based on diff statistics."""
        if (
            self.files_changed <= 10
            and self.total_additions + self.total_deletions <= 80
        ):
            return "LOW"
        elif (
            self.files_changed <= 25
            and self.total_additions + self.total_deletions <= 150
        ):
            return "MEDIUM"
        else:
            return "HIGH"

    def to_dict(self) -> Dict[str, Any]:
        """Convert diff statistics to dictionary."""
        return {
            "files_changed": self.files_changed,
            "total_additions": self.total_additions,
            "total_deletions": self.total_deletions,
            "has_tests": self.has_tests,
        }
