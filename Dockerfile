# Use the official Python image
FROM python:3.11-slim

# Copy uv binary from official image
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/

# Set the working directory to the GitHub workspace
WORKDIR /github/workspace

# Install git (required for git diff operations)
RUN apt-get update && apt-get install -y git && rm -rf /var/lib/apt/lists/*

# Copy the project files
COPY pyproject.toml uv.lock ./
COPY src/ ./src/
COPY action.yml ./

# Install the project and dependencies using uv
RUN uv pip install --system -e .

# Configure git to work in the GitHub workspace
RUN git config --global --add safe.directory "*"

# Run the action by default
CMD ["python", "-m", "vibe_reviewer"]