# Use the official Python image
FROM python:3.11-slim

# Set the working directory
WORKDIR /app

# Copy the project files
COPY pyproject.toml ./
COPY src/ ./src/
COPY action.yml ./

# Install the project and dependencies using uv
RUN pip install uv && \
    uv pip install --system --no-deps -e .

# Run the action by default
CMD ["python", "-m", "vibe_reviewer"]
