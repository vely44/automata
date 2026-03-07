# Plan: Docker + Nanobot + Cloud API + Dashboard Bot (v5)

## Context
Build a portable 2-container stack:
- **Nanobot** — Ultra-lightweight Python AI agent connected to Discord, calling cloud LLM APIs
- **Dashboard Bot** — Python bot for status monitoring and task management

No local LLM — Nanobot calls Anthropic, OpenAI, or other cloud APIs directly.

## Why Nanobot over alternatives?

- **Python-based** — ~4,000 lines of code, fully readable and auditable
- **No compilation** — runs instantly with Python pip install
- **Model-agnostic** — works with any LLM API
- **Lightweight** — minimal dependencies, fast startup
- **Discord-native** — built-in Discord integration
- **Portable** — copy folder to any Docker machine and run

## Architecture

```
┌──────────────────────────────────────────────────┐
│  Docker Compose Stack                            │
│                                                  │
│  ┌───────────┐       ┌─────────────────┐        │
│  │ Nanobot   │──────►│ Cloud LLM API   │        │
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
├── docker-compose.yml          # 2 services: nanobot + dashbot
├── .env                        # Discord tokens, API keys, ports
├── setup.sh                    # automated installer
├── nanobot/
│   ├── Dockerfile              # Python slim base, pip install nanobot
│   ├── config.yaml             # API provider config + Discord
│   └── workspace/              # persistent workspace for agent projects
└── dashbot/
    ├── Dockerfile              # Python slim image
    ├── bot.py                  # Discord bot with slash commands
    ├── requirements.txt        # discord.py, aiosqlite, httpx
    └── data/                   # persistent storage (tasks.db created here)
```

## Services

| Service | Language | Ports | Purpose |
|---------|----------|-------|---------|
| nanobot | Python | 8080 (webhook) | AI agent, Discord channel |
| dashbot | Python | none | Status & task management bot |

- Nanobot calls cloud APIs (Anthropic/OpenAI) — API keys passed via env vars
- Nanobot mounts config.yaml (read-only) + workspace/ (read-write)
- Dashboard bot mounts data/ for persistent SQLite

## Nanobot Dockerfile

- Base image: `python:3.11-slim`
- Clones HKUDS nanobot from GitHub and installs via pip
- Minimal runtime dependencies (git, curl for git clone)
- Startup time is instant (no compilation)

## Dashboard Bot

Simple Discord bot with slash commands (`/status`, `/tasks`, `/add`, `/done`, `/delete`).

Uses: `discord.py`, `aiosqlite`, `httpx`.

## Portability

Copy folder to any Docker machine → update `.env` → `docker compose up -d --build`.

No Rust compilation, no prebuilt binary downloads. Just Python + pip.
