"""Tests for the vibe_reviewer module."""

import os
from unittest.mock import patch, mock_open, MagicMock, PropertyMock
from vibe_reviewer import analyze_pr_diff, set_outputs
from vibe_reviewer.models.mistral_api import MistralAPI, DEFAULT_SYSTEM_PROMPT


def test_analyze_pr_diff():
    """Test the analyze_pr_diff function."""
    mock_event = {
        "number": 1,
        "pull_request": {
            "base": {"sha": "base123"},
            "head": {"sha": "head456"},
        },
    }

    mock_diff = "10\t5\tsrc/file1.py\n20\t10\ttests/test_file1.py\n"

    with patch("builtins.open", mock_open(read_data="{}")):
        with patch("json.load") as mock_json_load:
            mock_json_load.return_value = mock_event

            with patch("subprocess.run") as mock_run:
                mock_run.return_value.stdout = mock_diff
                mock_run.return_value.check_returncode.return_value = None

                with patch.dict(os.environ, {"GITHUB_EVENT_PATH": "mock_path"}):
                    with patch.dict(os.environ, {"MISTRAL_API_KEY": "test_key"}):
                        # Mock the MistralAPI class methods without affecting the real class
                        with patch(
                            "vibe_reviewer.models.mistral_api.MistralAPI.review_diff"
                        ) as mock_review_diff:
                            mock_review_diff.return_value = "Review comment"

                            result = analyze_pr_diff()

                            assert result["risk-level"] == "LOW"
                            assert result["files-changed"] == 2
                            assert result["has-tests"] == "true"
                            assert result["total-additions"] == 30
                            assert result["total-deletions"] == 15
                            assert result["message"] == "Review comment"


def test_set_outputs():
    """Test the set_outputs function."""
    mock_outputs = {"key1": "value1", "key2": "value2"}

    with patch.dict(os.environ, {"GITHUB_OUTPUT": "test_output"}):
        with patch("builtins.open", mock_open()) as mock_file:
            set_outputs(mock_outputs)
            mock_file.assert_called_once_with("test_output", "a")


def test_default_system_prompt():
    """Test that the default system prompt is used when review.md is not found."""
    api = MistralAPI("test_key")

    # Mock the file not found scenario
    with patch("builtins.open", side_effect=FileNotFoundError):
        prompt = api.load_system_prompt()
        assert prompt == DEFAULT_SYSTEM_PROMPT


def test_custom_system_prompt():
    """Test that a custom system prompt is loaded from review.md when available."""
    api = MistralAPI("test_key")
    custom_prompt = "Custom prompt for testing"

    # Mock the file read scenario
    m = mock_open(read_data=custom_prompt)
    with patch("builtins.open", m):
        prompt = api.load_system_prompt()
        assert prompt == custom_prompt
