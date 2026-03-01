try:
    from mistralai import Mistral, UserMessage, SystemMessage
except ImportError:
    # Mock classes for testing when mistralai is not installed
    class Mistral:
        def __init__(self, api_key: str):
            self.api_key = api_key
            self.chat = MockChat()

    class UserMessage:
        def __init__(self, content: str):
            self.content = content

    class SystemMessage:
        def __init__(self, content: str):
            self.content = content

    class MockChat:
        def complete(self, model: str, messages: list):
            return type("obj", (object,), {"choices": []})()


REVIEW_MD = "review.md"


class MistralAPI:
    """Class to handle Mistral API interactions."""

    def __init__(self, api_key: str):
        self.api_key = api_key
        self.client = None

    def initialize_client(self) -> None:
        self.client = Mistral(api_key=self.api_key)

    def load_system_prompt(self) -> str:
        """Load the system prompt from review.md."""
        try:
            with open(REVIEW_MD, "r") as f:
                return f.read()
        except FileNotFoundError:
            print("DEBUG: No review.md found")
            return "You are a code reviewer. Please review the following code changes."

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
            response = self.client.chat.complete(
                model="devstral-small-latest", messages=messages
            )

            if hasattr(response, "choices") and len(response.choices) > 0:
                return response.choices[0].message.content
            else:
                return str(response)
        except Exception as e:
            print(f"DEBUG: Mistral API exception: {e}")
            return f"API exception: {str(e)}"
