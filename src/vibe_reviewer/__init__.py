"""Vibe Reviewer for GitHub Actions."""

from typing import Dict, Any

from .models.pr_analyzer import PRAnalyzer
from .utils.github_actions import GitHubActionsOutput


def analyze_pr_diff() -> Dict[str, Any]:
    """Analyze the PR diff and return metrics (legacy function)."""
    analyzer = PRAnalyzer()
    return analyzer.analyze_pr_diff()


def set_outputs(outputs: Dict[str, Any]) -> None:
    """Set GitHub Actions outputs (legacy function)."""
    GitHubActionsOutput.set_outputs(outputs)


def main() -> None:
    """Main entry point for the GitHub Action."""
    results = analyze_pr_diff()
    set_outputs(results)


if __name__ == "__main__":
    main()
