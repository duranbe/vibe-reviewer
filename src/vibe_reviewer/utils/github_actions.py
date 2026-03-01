"""GitHub Actions utilities for handling outputs."""

import os
from typing import Dict, Any


class GitHubActionsOutput:
    """Class to handle GitHub Actions outputs."""

    @staticmethod
    def set_outputs(outputs: Dict[str, Any]) -> None:
        """Set GitHub Actions outputs."""
        github_output = os.environ.get("GITHUB_OUTPUT", "")
        if not github_output:
            print("DEBUG: GITHUB_OUTPUT not set, skipping output writing")
            return

        print(f"DEBUG: Writing outputs to {github_output}")
        print(f"DEBUG: Outputs: {outputs}")

        with open(github_output, "a") as f:
            for key, value in outputs.items():
                if isinstance(value, str) and ("\n" in value or "\r" in value):
                    escaped_value = value.replace("\n", "%0A").replace("\r", "%0D")
                    f.write(f"{key}={escaped_value}\n")
                else:
                    f.write(f"{key}={value}\n")
        print("DEBUG: Outputs written successfully")
