# Plan: Docker + ZeroClaw + Cloud API + Dashboard Bot (v4)

## Context
Build a portable 2-container stack:
- **ZeroClaw** — Rust AI agent connected to Discord, calling cloud LLM APIs
- **Dashboard Bot** — Python bot for status monitoring and task management

No local LLM — ZeroClaw calls Anthropic, OpenAI, or other cloud APIs directly.

## Architecture

```
┌──────────────────────────────────────────────────┐
│  Docker Compose Stack                            │
│                                                  │
│  ┌───────────┐       ┌─────────────────┐        │
│  │ ZeroClaw  │──────►│ Cloud LLM API   │        │
│  │  :8080    │       │ (Anthropic/OAI) │        │
│  └───────────┘       └─────────────────┘        │
│        │                                         │
│        │                                         │
│  ┌─────────────────────────────┐                │
│  │  Dashboard Bot (Python)     │                │
│  │  - /status, /tasks, /add    │                │
│  │  - tasks.db (SQLite)        │                │
│  └─────────────────────────────┘                │
│                   │                              │
│                   ▼                              │
│               Discord                            │
└──────────────────────────────────────────────────┘
```

## Project structure

```
├── PLAN.md
├── README.md
├── docker-compose.yml          # 2 services: zeroclaw + dashbot
├── .env                        # Discord tokens, API keys, ports
├── setup.sh                    # automated installer
├── zeroclaw/
│   ├── Dockerfile              # prebuilt binary from GitHub releases
│   ├── config.toml             # API provider config + Discord
│   └── workspace/              # persistent workspace for agent projects
└── dashbot/
    ├── Dockerfile              # Python slim image
    ├── bot.py                  # Discord bot with slash commands
    ├── requirements.txt        # discord.py, aiosqlite, httpx
    └── data/                   # persistent storage (tasks.db created here)
```

## Services

| Service | Image | Ports | Purpose |
|---------|-------|-------|---------|
| zeroclaw | Custom Dockerfile | 8080 (webhook) | AI agent, Discord channel |
| dashbot | Custom Dockerfile | none | Status & task management bot |

- ZeroClaw calls cloud APIs (Anthropic/OpenAI) — API keys passed via env vars
- ZeroClaw mounts config.toml (read-only) + workspace/ (read-write)
- Dashboard bot mounts data/ for persistent SQLite

## ZeroClaw Dockerfile

- Base image: `ubuntu:24.04`
- Downloads prebuilt binary from GitHub releases (v0.1.6, x86_64)
- Installs runtime dependencies (`ca-certificates`, `libssl3`, `git`, `curl`)

## Dashboard Bot

Simple Discord bot with slash commands (`/status`, `/tasks`, `/add`, `/done`, `/delete`).

Uses: `discord.py`, `aiosqlite`, `httpx`.

## Portability

Copy folder to any Docker machine → update `.env` → `docker compose up -d --build`.
