FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    curl \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

# Upgrade pip
RUN pip install --no-cache-dir --upgrade pip setuptools wheel

# Clone and install nanobot from HKUDS GitHub
RUN git clone https://github.com/HKUDS/nanobot.git /tmp/nanobot && \
    cd /tmp/nanobot && \
    pip install --no-cache-dir -e . && \
    cd / && \
    rm -rf /tmp/nanobot

# Create workspace directory for persistent data
RUN mkdir -p /app/workspace && \
    chmod 755 /app/workspace

# Set Python to run in unbuffered mode (for real-time logs)
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Health check: verify Python can be imported
HEALTHCHECK --interval=30s --timeout=10s --start-period=10s --retries=3 \
    CMD python -c "import sys; sys.exit(0)" || exit 1

# Run nanobot (defaults to daemon mode if available)
CMD ["python", "-m", "nanobot"]
