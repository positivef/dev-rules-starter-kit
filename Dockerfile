# Multi-stage build for Tier 1 Integration System
# Stage 1: Builder
FROM python:3.11-slim as builder

# Set working directory
WORKDIR /build

# Install build dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    make \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements*.txt ./

# Create virtual environment and install dependencies
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Stage 2: Runtime
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/opt/venv/bin:$PATH" \
    TIER1_HOME="/app" \
    OBSIDIAN_VAULT_PATH="/data/vault"

# Create non-root user
RUN useradd -m -u 1000 tier1user && \
    mkdir -p /app /data/vault /logs && \
    chown -R tier1user:tier1user /app /data /logs

# Copy virtual environment from builder
COPY --from=builder /opt/venv /opt/venv

# Set working directory
WORKDIR /app

# Copy application code
COPY --chown=tier1user:tier1user scripts/ ./scripts/
COPY --chown=tier1user:tier1user tests/ ./tests/
COPY --chown=tier1user:tier1user contracts/ ./contracts/
COPY --chown=tier1user:tier1user templates/ ./templates/
COPY --chown=tier1user:tier1user config/ ./config/
COPY --chown=tier1user:tier1user README_TIER1.md ./

# Switch to non-root user
USER tier1user

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "from scripts.tag_extractor_lite import TagExtractorLite; print('OK')" || exit 1

# Create volumes for data persistence
VOLUME ["/data/vault", "/logs", "/app/contracts"]

# Default command
CMD ["python", "-m", "scripts.tier1_cli"]

# Labels
LABEL maintainer="Tier 1 Integration Team" \
      version="1.0.0" \
      description="Tier 1 Integration System - TAG-based development with Obsidian integration" \
      org.opencontainers.image.source="https://github.com/yourusername/dev-rules-starter-kit"
