"""Tests for the vibe_reviewer module."""

from vibe_reviewer import greet


def test_greet():
    """Test the greet function."""
    assert greet("World") == "Hello, World!"
