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

## Step 1: Install Docker on Linux Mint 22 (LATER)

Install Docker Engine + Compose plugin from Docker's official Ubuntu Noble repo, add user to docker group.

## Step 2: Create Discord Bot (LATER)

Create Discord application, get bot token, enable Message Content Intent, invite bot to server.

**Note:** You need ONE Discord bot token. Both ZeroClaw and Dashboard Bot can use the same token OR you can create two separate bots.

## Step 3: Create project structure and files (START HERE)

```
~/Documents/aiclaudeprojects/zeroclaw-stack/
├── PLAN.md                     # this plan (v3)
├── README.md                   # progress tracker with checkboxes
├── docker-compose.yml          # 3 services: ollama + zeroclaw + dashbot
├── .env                        # Discord token, model name, ports
├── zeroclaw/
│   ├── Dockerfile              # multi-stage build from GitHub source
│   ├── config.toml             # ZeroClaw config: Ollama provider + Discord
│   └── workspace/              # persistent workspace for agent projects
├── dashbot/
│   ├── Dockerfile              # Python slim image
│   ├── bot.py                  # Discord bot with slash commands
│   ├── requirements.txt        # discord.py, aiosqlite, httpx
│   └── data/                   # persistent storage (tasks.db created here)
└── ollama/
    └── models/                 # persistent model storage (bind mount)
```

### 3a. docker-compose.yml (3 services)

| Service | Image | Ports | Purpose |
|---------|-------|-------|---------|
| ollama | `ollama/ollama:latest` | none exposed | Internal LLM engine |
| zeroclaw | Custom Dockerfile | 8080 (webhook) | AI agent, Discord channel |
| dashbot | Custom Dockerfile | none | Status & task management bot |

- Ollama internal only (`http://ollama:11434` within Docker network)
- ZeroClaw mounts config.toml (read-only) + workspace/ (read-write)
- Dashboard bot mounts data/ for persistent SQLite
- Both bots connect to Discord

### 3b. ZeroClaw Dockerfile (multi-stage)

- **Stage 1 (builder):** `rust:1.83-slim-bookworm`, clone repo, `cargo build --release --locked`
- **Stage 2 (runtime):** `debian:bookworm-slim` + ~3.4MB binary + dev tools
- Final image ~100MB

### 3c. Dashboard Bot (Python)

Simple Discord bot with slash commands:
- `/status` — Ollama health, ZeroClaw config, container info
- `/tasks` — List all tasks
- `/add <task>` — Add new task
- `/done <id>` — Mark task complete
- `/delete <id>` — Remove task

Uses:
- `discord.py` for Discord integration
- `aiosqlite` for async SQLite
- `httpx` for health checks

### 3d. Config files

- `.env` — Discord token, model name, ports
- `zeroclaw/config.toml` — Ollama provider + Discord channel + workspace path

## Step 4: Build and launch (after Steps 1 & 2)

```bash
cd ~/Documents/aiclaudeprojects/zeroclaw-stack
docker compose up -d --build
docker compose exec ollama ollama pull llama3.2:3b
```

## Step 5: Verify

1. `docker compose ps` — all 3 containers running
2. `docker compose logs zeroclaw` — agent connected
3. `docker compose logs dashbot` — bot connected
4. Message ZeroClaw in Discord — should respond via LLM
5. Use `/status` command — should show dashboard
6. `docker compose exec ollama ollama list` — see models

## Swapping models (no rebuild needed)

```bash
docker compose exec ollama ollama pull mistral:7b
# Edit zeroclaw/config.toml → change model name
docker compose restart zeroclaw
```

## Portability

Copy `zeroclaw-stack/` folder to any Docker machine → update `.env` → `docker compose up -d`.

## RAM note

16GB RAM. Comfortable with 3B-7B models. 13B would be tight. Dashboard bot adds ~50MB.
