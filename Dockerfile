# Use the official Python image
FROM python:3.11-slim

# Set the working directory
WORKDIR /app

# Copy the project files
COPY pyproject.toml ./
COPY src/ ./src/
COPY tests/ ./tests/

# Install the project and dependencies using uv
RUN pip install uv && \
    uv pip install --system --no-deps -e . && \
    uv pip install --system pytest black ruff

# Run tests by default
CMD ["pytest", "tests/"]
