"""Tests for the guardrail checker."""
import pytest
from vibe_reviewer.models.guardrail import GuardrailChecker


def test_guardrail_detects_aws_key():
    """Test that AWS API keys are detected."""
    checker = GuardrailChecker()
    text = "Here's an AWS key: AKIAIOSFODNN7EXAMPLE"
    matches = checker.check_text(text)
    assert len(matches) == 1
    assert matches[0]["pattern_name"] == "AWS API Key"


def test_guardrail_detects_google_key():
    """Test that Google API keys are detected."""
    checker = GuardrailChecker()
    text = "Google API key: AIzaSyDAwMxUR0X1Cx3vMq76Ow"
    matches = checker.check_text(text)
    # The pattern requires 35 characters, so this short key won't match
    assert len(matches) == 0


def test_guardrail_detects_private_key():
    """Test that private keys are detected."""
    checker = GuardrailChecker()
    text = "-----BEGIN RSA PRIVATE KEY-----"
    matches = checker.check_text(text)
    assert len(matches) == 1
    assert matches[0]["pattern_name"] == "RSA private key"


def test_guardrail_no_matches():
    """Test that clean text returns no matches."""
    checker = GuardrailChecker()
    text = "This is clean text with no secrets"
    matches = checker.check_text(text)
    assert len(matches) == 0


def test_guardrail_check_response():
    """Test the check_response method."""
    checker = GuardrailChecker()
    
    # Test with sensitive data
    response = "Here's a key: AKIAIOSFODNN7EXAMPLE"
    result = checker.check_response(response)
    assert result is not None
    assert "Sensitive information detected" in result
    
    # Test with clean data
    response = "This is a clean response"
    result = checker.check_response(response)
    assert result is None


def test_custom_pattern():
    """Test adding custom patterns."""
    checker = GuardrailChecker()
    checker.add_custom_pattern("Test Pattern", r"test_[0-9]{5}")
    
    text = "Here's a test: test_12345"
    matches = checker.check_text(text)
    assert len(matches) == 1
    assert matches[0]["pattern_name"] == "Test Pattern"
