# container-automata v5

A lightweight 2-container AI agent stack: **Nanobot** (Python AI agent) + **Dashboard Bot** (Python status/task manager). Nanobot calls cloud LLM APIs (Anthropic, OpenAI, etc.). All connected through Discord.

## Why Nanobot?

- **Python-based** — ~4,000 lines of code, fully readable and auditable
- **No compilation** — runs instantly with Python pip install (vs. Rust compilation)
- **Model-agnostic** — works with any LLM API (Anthropic, OpenAI, etc.)
- **Lightweight** — minimal dependencies, fast startup, small Docker images
- **Discord-native** — built-in Discord integration out of the box
- **Portable** — copy folder to any Docker machine and run — no platform dependencies

```
┌─────────────────────────────────────────┐
│  Docker Network                         │
│                                         │
│  Nanobot ────► Cloud LLM API           │
│      │         (Anthropic / OpenAI)     │
│      │                                  │
│      ├──────► Discord                   │
│      │                                  │
│  Dashboard Bot ──► Discord             │
│      │                                  │
│      ▼                                  │
│  tasks.db                               │
└─────────────────────────────────────────┘
```

---

## Prerequisites

- **Docker** with Compose plugin installed
- A **Discord bot token** (see [Discord Developer Portal](https://discord.com/developers/applications) — create an app, enable Message Content Intent, invite to your server with `Send Messages`, `Use Slash Commands`, `Read Message History`, `Embed Links`)
- At least one **LLM API key** (Anthropic or OpenAI)

## Project structure

```
container-automata/
├── README.md
├── docker-compose.yml          # 2 services: nanobot + dashbot
├── .env                        # Discord tokens, API keys
├── .env.example                # Template for .env
├── setup.sh                    # Automated installer
├── nanobot/
│   ├── Dockerfile              # Python 3.12 slim base, installs nanobot via pip
│   ├── config.yaml             # LLM provider config + Discord settings
│   └── workspace/              # Persistent workspace for agent projects
└── dashbot/
    ├── Dockerfile              # Python 3.12 slim image
    ├── bot.py                  # Discord bot with slash commands
    ├── requirements.txt        # Discord.py, aiosqlite
    └── data/                   # Persistent SQLite database (tasks.db)
```

## Services

| Service | Language | Purpose | Config |
|---------|----------|---------|--------|
| **nanobot** | Python 3.12 | AI agent connected to Discord, calls cloud LLMs | `nanobot/config.yaml` |
| **dashbot** | Python 3.12 | Status monitoring and task management | `.env` |

**Details:**
- Nanobot calls cloud APIs (Anthropic/OpenAI) — API keys via `DISCORD_BOT_TOKEN`, `ANTHROPIC_API_KEY`, `OPENAI_API_KEY` env vars
- Nanobot mounts `config.yaml` (read-only) + `workspace/` (persistent)
- Dashboard bot mounts `data/` for persistent SQLite database
- Both connected to shared Docker network (`automata-network`)

## Quick install (automated)

```bash
git clone https://github.com/vely44/container-automata.git
cd container-automata
bash setup.sh
```

Handles Docker install (Ubuntu/Debian), `.env` setup, build, and verification in one shot.

## Manual install

### 1. Clone and configure

```bash
git clone https://github.com/vely44/container-automata.git
cd container-automata
cp .env.example .env
```

Edit `.env` with your tokens and API keys:
```
DISCORD_BOT_TOKEN=your_nanobot_token_here
DASHBOT_TOKEN=your_dashbot_token_here
ANTHROPIC_API_KEY=sk-ant-...
OPENAI_API_KEY=sk-...
```

### 2. Build and launch

```bash
docker compose up -d --build
```

### 3. Verify

Test in Discord:
- Message Nanobot — it should respond via the cloud LLM
- `/status` — Dashboard Bot shows system health
- `/tasks`, `/add`, `/done`, `/delete` — task management

## Switching providers / models

Edit `nanobot/config.yaml`:
- Change `provider` to `"anthropic"` or `"openai"`
- Change `model` to the model you want (e.g. `claude-sonnet-4-6`, `gpt-4o`)
- Make sure the matching API key is set in `.env`

Then restart: `docker compose restart nanobot`

## Dashboard Bot commands

| Command | Description |
|---------|-------------|
| `/status` | Show Nanobot config, provider, system info |
| `/tasks` | List all tasks (pending and completed) |
| `/add <task>` | Add a new task |
| `/done <id>` | Mark a task as completed |
| `/delete <id>` | Delete a task |

## Portability

Copy the entire `container-automata/` folder to any Docker machine → update `.env` → `docker compose up -d --build`. That's it.
