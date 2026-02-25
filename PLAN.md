# Plan: Docker + ZeroClaw + Ollama + Dashboard Bot (v3)

## Context
Build a portable 3-container stack:
- **Ollama** — Local LLM inference
- **ZeroClaw** — Rust AI agent connected to Discord
- **Dashboard Bot** — Python bot for status monitoring and task management

Ollama is internal-only (used by ZeroClaw, not exposed separately). Models are swappable without rebuilding.

## Architecture

```
┌──────────────────────────────────────────────────┐
│  Docker Compose Stack                            │
│                                                  │
│  ┌───────────┐       ┌───────────┐              │
│  │  Ollama   │◄──────│ ZeroClaw  │              │
│  │  :11434   │       │  :8080    │              │
│  └───────────┘       └───────────┘              │
│        │                   │                     │
│        │   ┌───────────────┘                     │
│        │   │                                     │
│        ▼   ▼                                     │
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
├── docker-compose.yml          # 3 services: ollama + zeroclaw + dashbot
├── .env                        # Discord token, model name, ports
├── setup.sh                    # automated installer
├── zeroclaw/
│   ├── Dockerfile              # prebuilt binary from GitHub releases
│   ├── config.toml             # Ollama provider + Discord
│   └── workspace/              # persistent workspace for agent projects
├── dashbot/
│   ├── Dockerfile              # Python slim image
│   ├── bot.py                  # Discord bot with slash commands
│   ├── requirements.txt        # discord.py, aiosqlite, httpx
│   └── data/                   # persistent storage (tasks.db created here)
└── ollama/
    └── models/                 # persistent model storage (bind mount)
```

## Services

| Service | Image | Ports | Purpose |
|---------|-------|-------|---------|
| ollama | `ollama/ollama:latest` | none exposed | Internal LLM engine |
| zeroclaw | Custom Dockerfile | 8080 (webhook) | AI agent, Discord channel |
| dashbot | Custom Dockerfile | none | Status & task management bot |

- Ollama internal only (`http://ollama:11434` within Docker network)
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
