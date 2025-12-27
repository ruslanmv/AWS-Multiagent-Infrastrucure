# Multi-stage Dockerfile for AWS Orchestrator
# Optimized for production with minimal image size

# Stage 1: Builder
FROM python:3.11-slim as builder

# Install uv for fast dependency resolution
RUN pip install --no-cache-dir uv

# Set working directory
WORKDIR /build

# Copy dependency files
COPY pyproject.toml ./

# Install dependencies to a virtual environment
RUN uv venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"
RUN uv pip install --no-cache .

# Stage 2: Runtime
FROM python:3.11-slim

# Set labels
LABEL maintainer="Ruslan Magana <contact@ruslanmv.com>"
LABEL description="AWS Orchestrator - Multi-Agent Orchestration Framework"
LABEL version="0.1.0"

# Install runtime dependencies
RUN apt-get update && apt-get install -y \
    --no-install-recommends \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user for security
RUN useradd -m -u 1000 orchestrator && \
    mkdir -p /app && \
    chown -R orchestrator:orchestrator /app

# Copy virtual environment from builder
COPY --from=builder /opt/venv /opt/venv

# Set working directory
WORKDIR /app

# Copy application code
COPY --chown=orchestrator:orchestrator src/ /app/src/

# Set environment variables
ENV PATH="/opt/venv/bin:$PATH" \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    AWS_REGION=us-east-1

# Switch to non-root user
USER orchestrator

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "from aws_orchestrator import __version__; print(__version__)" || exit 1

# Set entrypoint
ENTRYPOINT ["aws-orchestrator"]

# Default command
CMD ["--help"]
