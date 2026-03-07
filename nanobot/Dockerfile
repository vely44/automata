FROM python:3.11-slim

WORKDIR /app

# Install dependencies
RUN apt-get update && apt-get install -y \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Clone and install nanobot
RUN git clone https://github.com/HKUDS/nanobot.git /tmp/nanobot && \
    cd /tmp/nanobot && \
    pip install --no-cache-dir -e . && \
    rm -rf /tmp/nanobot

# Create workspace directory
RUN mkdir -p /app/workspace

# Set environment
ENV PYTHONUNBUFFERED=1

# Run nanobot
CMD ["nanobot"]
