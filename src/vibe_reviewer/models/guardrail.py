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
            "Slack Token": r"(xox[pborsa]-[0-9]{12}-[0-9]{12}-[0-9]{12}-[a-z0-9]{32})",
            "RSA private key": r"-----BEGIN RSA PRIVATE KEY-----",
            "SSH (DSA) private key": r"-----BEGIN DSA PRIVATE KEY-----",
            "SSH (EC) private key": r"-----BEGIN EC PRIVATE KEY-----",
            "PGP private key block": r"-----BEGIN PGP PRIVATE KEY BLOCK-----",
            "AWS API Key": r"AKIA[0-9A-Z]{16}",
            "AWS AppSync GraphQL Key": r"da2-[a-z0-9]{26}",
            "Facebook Access Token": r"EAACEdEose0cBA[0-9A-Za-z]+",
            "Facebook OAuth": r"[fF][aA][cC][eE][bB][oO][oO][kK].*['|\"][0-9a-f]{32}['|\"]",
            "GitHub": r"[gG][iI][tT][hH][uU][bB].*['|\"][0-9a-zA-Z]{35,40}['|\"]",
            "Generic API Key": r"[aA][pP][iI]_?[kK][eE][yY].*['|\"][0-9a-zA-Z]{32,45}['|\"]",
            "Generic Secret": r"[sS][eE][cC][rR][eE][tT].*['|\"][0-9a-zA-Z]{32,45}['|\"]",
            "Google API Key": r"AIza[0-9A-Za-z\\-_]{35}",
            "Google Cloud Platform API Key": r"AIza[0-9A-Za-z\\-_]{35}",
            "Google Cloud Platform OAuth": r"[0-9]+-[0-9A-Za-z_]{32}\\.apps\\.googleusercontent\\.com",
            "Google Drive API Key": r"AIza[0-9A-Za-z\\-_]{35}",
            "Google Drive OAuth": r"[0-9]+-[0-9A-Za-z_]{32}\\.apps\\.googleusercontent\\.com",
            "Google (GCP) Service-account": r'"type": "service_account"',
            "Google Gmail API Key": r"AIza[0-9A-Za-z\\-_]{35}",
            "Google Gmail OAuth": r"[0-9]+-[0-9A-Za-z_]{32}\\.apps\\.googleusercontent\\.com",
            "Google OAuth Access Token": r"ya29\\.[0-9A-Za-z\\-_]+",
            "Google YouTube API Key": r"AIza[0-9A-Za-z\\-_]{35}",
            "Google YouTube OAuth": r"[0-9]+-[0-9A-Za-z_]{32}\\.apps\\.googleusercontent\\.com",
            "Heroku API Key": r"[hH][eE][rR][oO][kK][uU].*[0-9A-F]{8}-[0-9A-F]{4}-[0-9A-F]{4}-[0-9A-F]{4}-[0-9A-F]{12}",
            "MailChimp API Key": r"[0-9a-f]{32}-us[0-9]{1,2}",
            "Mailgun API Key": r"key-[0-9a-zA-Z]{32}",
            "Password in URL": r"[a-zA-Z]{3,10}://[^/\\s:@]{3,20}:[^/\\s:@]{3,20}@.{1,100}[\"'\\s]",
            "PayPal Braintree Access Token": r"access_token\\$production\\$[0-9a-z]{16}\\\[0-9a-f]{32}",
            "Picatic API Key": r"sk_live_[0-9a-z]{32}",
            "Slack Webhook": r"https://hooks\\.slack\\.com/services/T[a-zA-Z0-9_]{8}/B[a-zA-Z0-9_]{8}/[a-zA-Z0-9_]{24}",
            "Stripe API Key": r"sk_live_[0-9a-zA-Z]{24}",
            "Stripe Restricted API Key": r"rk_live_[0-9a-zA-Z]{24}",
            "Square Access Token": r"sq0atp-[0-9A-Za-z\\-_]{22}",
            "Square OAuth Secret": r"sq0csp-[0-9A-Za-z\\-_]{43}",
            "Telegram Bot API Key": r"[0-9]+:AA[0-9A-Za-z\\-_]{33}",
            "Twilio API Key": r"SK[0-9a-fA-F]{32}",
            "Twitter Access Token": r"[tT][wW][iI][tT][tT][eE][rR].*[1-9][0-9]+-[0-9a-zA-Z]{40}",
            "Twitter OAuth": r"[tT][wW][iI][tT][tT][eE][rR].*['|\"][0-9a-zA-Z]{35,44}['|\"]",
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
