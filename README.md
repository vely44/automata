# container-automata (old name — ZeroClaw Stack) v3

A portable 3-container AI agent stack: **Ollama** (local LLM inference) + **ZeroClaw** (Rust AI agent) + **Dashboard Bot** (Python status/task manager). All connected through Discord.

```
┌─────────────────────────────────────────┐
│  Docker Network                         │
│                                         │
│  Ollama ◄─── ZeroClaw ───► Discord     │
│    ▲              │                     │
│    │              │                     │
│    └──── Dashboard Bot ──► Discord     │
│              │                          │
│              ▼                          │
│          tasks.db                       │
└─────────────────────────────────────────┘
```

---

## Prerequisites

- **Docker** with Compose plugin installed
- A **Discord bot token** (see [Discord Developer Portal](https://discord.com/developers/applications) — create an app, enable Message Content Intent, invite to your server with `Send Messages`, `Use Slash Commands`, `Read Message History`, `Embed Links`)

## Quick install (automated)

```bash
git clone https://github.com/vely44/container-automata.git
cd container-automata
bash setup.sh
```

Handles Docker install (Ubuntu/Debian), `.env` setup, build, model pull, and verification in one shot.

## Manual install

### 1. Clone and configure

```bash
git clone https://github.com/vely44/container-automata.git
cd container-automata
cp .env.example .env
```

Edit `.env` with your token(s):
```
DISCORD_BOT_TOKEN=your_zeroclaw_token_here
DASHBOT_TOKEN=your_dashbot_token_here
ZEROCLAW_PORT=8080
```

### 2. Build and launch

```bash
docker compose up -d --build
docker compose exec ollama ollama pull mistral:7b
```

### 3. Verify

Test in Discord:
- Message ZeroClaw — it should respond via the LLM
- `/status` — Dashboard Bot shows system health
- `/tasks`, `/add`, `/done`, `/delete` — task management

## Swapping models

No rebuild needed — just pull and point:

```bash
docker compose exec ollama ollama pull <model-name>
```

Edit `zeroclaw/config.toml` → change `default_model` → `docker compose restart zeroclaw`.

## GPU support

If you have an NVIDIA GPU, uncomment the GPU block in `docker-compose.yml` under the `ollama` service and install the [NVIDIA Container Toolkit](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/install-guide.html). Ollama will use the GPU automatically.

## Dashboard Bot commands

| Command | Description |
|---------|-------------|
| `/status` | Show Ollama health, ZeroClaw config, system info |
| `/tasks` | List all tasks (pending and completed) |
| `/add <task>` | Add a new task |
| `/done <id>` | Mark a task as completed |
| `/delete <id>` | Delete a task |

## Portability

Copy the entire `container-automata/` folder to any Docker machine → update `.env` → `docker compose up -d --build`. That's it.
