import logging
from mistralai import Mistral, UserMessage, SystemMessage
from .guardrail import GuardrailChecker

BASE_MODEL = "devstral-small-latest"

REVIEW_MD = "REVIEW.MD"

DEFAULT_SYSTEM_PROMPT = """
You are a senior code reviewer with extensive experience in software development.
Please analyze the following code changes and provide a comprehensive review.

Focus on:
1. Code quality and best practices
2. Potential bugs or issues
3. Security concerns
4. Performance implications
5. Readability and maintainability
6. Testing considerations

Provide specific, actionable feedback with clear explanations.
Be constructive and helpful in your suggestions.

IMPORTANT SAFETY INSTRUCTIONS:
- Never generate or suggest real API keys, secrets, or credentials
- Never include actual passwords, tokens, or sensitive information
- If you detect sensitive information in the code, flag it as a security concern
- Always prioritize security and privacy
"""


class MistralAPI:
    """Class to handle Mistral API interactions."""

    def __init__(self, api_key: str):
        self.api_key = api_key
        self.client = None
        self.guardrail = GuardrailChecker()

    def initialize_client(self) -> None:
        self.client = Mistral(api_key=self.api_key)

    def load_system_prompt(self) -> str:
        """Load the system prompt from REVIEW.MD."""
        try:
            with open(REVIEW_MD, "r") as f:
                return f.read()
        except FileNotFoundError:
            logging.debug("No REVIEW.MD found, using default system prompt")
            return DEFAULT_SYSTEM_PROMPT

    def review_diff(self, diff_content: str, risk_level: str) -> str:
        """Send diff to Mistral for review."""
        if not self.client:
            self.initialize_client()
        system_prompt = self.load_system_prompt()

        messages = [
            SystemMessage(content=system_prompt),
            UserMessage(
                content=f"## Code Changes\n\nRisk Level: {risk_level}\n\n```diff\n{diff_content}\n```"
            ),
        ]

        try:
            response = self.client.chat.complete(model=BASE_MODEL, messages=messages)

            if hasattr(response, "choices") and len(response.choices) > 0:
                response_content = response.choices[0].message.content
                # Check response for sensitive information
                violation = self.guardrail.check_response(response_content)
                if violation:
                    logging.warning(f"Guardrail violation detected: {violation}")
                    return f"[SECURITY VIOLATION] {violation}\n\nOriginal response was blocked for security reasons."
                return response_content
            else:
                return str(response)
        except Exception as e:
            logging.debug(f"Mistral API exception: {e}")
            return f"API exception: {str(e)}"
