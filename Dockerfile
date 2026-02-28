# Use the official Python image
FROM python:3.11-slim

# Set the working directory to the GitHub workspace
WORKDIR /github/workspace

# Install git (required for git diff operations)
RUN apt-get update && apt-get install -y git && rm -rf /var/lib/apt/lists/*

# Copy the project files
COPY pyproject.toml ./
COPY src/ ./src/
COPY action.yml ./

# Install the project and dependencies using uv
RUN pip install uv && \
    uv pip install --system --no-deps -e .

# Fetch full git history and checkout the correct ref
RUN git config --global --add safe.directory /github/workspace

# Run the action by default
CMD ["python", "-m", "vibe_reviewer"]
