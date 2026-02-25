# ZeroClaw Dockerfile - Prebuilt Binary
FROM ubuntu:24.04

RUN apt-get update && apt-get install -y \
    ca-certificates \
    libssl3 \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

RUN curl -L -o /tmp/zeroclaw.tar.gz \
    https://github.com/zeroclaw-labs/zeroclaw/releases/download/v0.1.6/zeroclaw-x86_64-unknown-linux-gnu.tar.gz \
    && tar xzf /tmp/zeroclaw.tar.gz -C /usr/local/bin/ \
    && rm /tmp/zeroclaw.tar.gz \
    && chmod +x /usr/local/bin/zeroclaw

WORKDIR /app
RUN mkdir -p /app/workspace

CMD ["zeroclaw", "daemon"]
