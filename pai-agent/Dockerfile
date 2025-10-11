FROM python:3.12-slim

LABEL maintainer="PAI Agent <pai@example.com>"
LABEL description="Personal AI Infrastructure Agent with PydanticAI"

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install uv
RUN pip install uv

# Set working directory
WORKDIR /app

# Copy dependency files
COPY pyproject.toml uv.lock ./

# Install Python dependencies
RUN uv sync --no-dev

# Copy application code
COPY . .

# Create non-root user
RUN useradd -m -u 1000 pai && chown -R pai:pai /app
USER pai

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8181/ || exit 1

# Expose port
EXPOSE 8181

# Start the application
CMD ["uv", "run", "python", "main.py"]