# Use the official Python image
FROM python:3.11-slim

# Set the working directory
WORKDIR /app

# Install git (required for git diff operations)
RUN apt-get update && apt-get install -y git && rm -rf /var/lib/apt/lists/*

# Copy the project files
COPY pyproject.toml ./
COPY src/ ./src/
COPY action.yml ./

# Install the project and dependencies using uv
RUN pip install uv && \
    uv pip install --system --no-deps -e .

# Run the action by default
CMD ["python", "-m", "vibe_reviewer"]
