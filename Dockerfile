# MCP-PBA-TUNNEL Dockerfile
FROM python:3.13-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app

# Set work directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    redis-tools \
    && rm -rf /var/lib/apt/lists/*

# Copy dependency files
COPY pyproject.toml requirements.txt ./

# Install Python dependencies
RUN pip install --no-cache-dir -e .

# Copy project files
COPY . .

# Create non-root user
RUN useradd --create-home --shell /bin/bash mcp-user && \
    chown -R mcp-user:mcp-user /app
USER mcp-user

# Expose port
EXPOSE 9001

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:9001/health || exit 1

# Run the application
CMD ["uvicorn", "server.fastapi_mcp_server:app", "--host", "0.0.0.0", "--port", "9001"]
