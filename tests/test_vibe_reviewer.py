"""Tests for the vibe_reviewer module."""

import os
from unittest.mock import patch, mock_open
from vibe_reviewer import analyze_pr_diff, set_outputs


def test_analyze_pr_diff():
    """Test the analyze_pr_diff function."""
    # Mock the event payload
    mock_event = {
        "number": 1,
        "pull_request": {
            "base": {"sha": "base123"},
            "head": {"sha": "head456"},
        },
    }

    # Mock git diff output
    mock_diff = "10\t5\tsrc/file1.py\n20\t10\ttests/test_file1.py\n"

    with patch("builtins.open", mock_open(read_data=mock_diff)):
        with patch("subprocess.run") as mock_run:
            mock_run.return_value.stdout = mock_diff
            mock_run.return_value.check_returncode.return_value = None

            with patch.dict(os.environ, {"GITHUB_EVENT_PATH": "mock_path"}):
                result = analyze_pr_diff()

                assert result["risk-level"] == "LOW"
                assert result["files-changed"] == 2
                assert result["has-tests"] == "true"
                assert result["total-additions"] == 30
                assert result["total-deletions"] == 15


def test_set_outputs():
    """Test the set_outputs function."""
    mock_outputs = {"key1": "value1", "key2": "value2"}

    with patch("builtins.open", mock_open()) as mock_file:
        set_outputs(mock_outputs)
        mock_file.assert_called_once_with(os.environ.get("GITHUB_OUTPUT", ""), "a")
