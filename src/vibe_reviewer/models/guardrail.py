"""Guardrail checker to prevent information leakage in Mistral AI API responses."""

import re
from typing import List, Dict, Optional


class GuardrailChecker:
    """Checks API responses for sensitive information using regex patterns."""

    def __init__(self):
        """Initialize with sensitive data patterns."""
        self.patterns = self._load_default_patterns()

    def _load_default_patterns(self) -> Dict[str, str]:
        """Load default sensitive data patterns."""
        return {
            "RSA private key": r"-----BEGIN RSA PRIVATE KEY-----",
            "SSH (DSA) private key": r"-----BEGIN DSA PRIVATE KEY-----",
            "SSH (EC) private key": r"-----BEGIN EC PRIVATE KEY-----",
            "AWS API Key": r"AKIA[0-9A-Z]{16}",
            "GitHub": r"[gG][iI][tT][hH][uU][bB].*['|\\\"][0-9a-zA-Z]{35,40}['|\\\"]",
        }

    def add_custom_pattern(self, name: str, pattern: str) -> None:
        """Add a custom regex pattern to check."""
        self.patterns[name] = pattern

    def check_text(self, text: str) -> List[Dict[str, str]]:
        """Check text for sensitive information.

        Args:
            text: The text to check for sensitive information.

        Returns:
            List of matches found, each containing 'pattern_name' and 'match'.
        """
        matches = []
        for name, pattern in self.patterns.items():
            try:
                compiled = re.compile(pattern)
                found = compiled.findall(text)
                if found:
                    for match in found:
                        matches.append({"pattern_name": name, "match": match})
            except re.error:
                # Skip invalid regex patterns
                continue
        return matches

    def check_response(self, response: str) -> Optional[str]:
        """Check API response for sensitive information.

        Args:
            response: The API response to check.

        Returns:
            None if no sensitive information found, otherwise an error message.
        """
        matches = self.check_text(response)
        if matches:
            match_details = ", ".join(
                [f"{m['pattern_name']}: {m['match']}" for m in matches]
            )
            return f"Sensitive information detected: {match_details}"
        return None
