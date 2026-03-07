# container-automata v4

A portable 2-container AI agent stack: **ZeroClaw** (Rust AI agent) + **Dashboard Bot** (Python status/task manager). ZeroClaw calls cloud LLM APIs (Anthropic, OpenAI, etc.) instead of running models locally. All connected through Discord.

```
┌─────────────────────────────────────────┐
│  Docker Network                         │
│                                         │
│  ZeroClaw ───► Cloud LLM API           │
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
DISCORD_BOT_TOKEN=your_zeroclaw_token_here
DASHBOT_TOKEN=your_dashbot_token_here
ZEROCLAW_PORT=8080
ANTHROPIC_API_KEY=sk-ant-...
OPENAI_API_KEY=sk-...
```

### 2. Build and launch

```bash
docker compose up -d --build
```

### 3. Verify

Test in Discord:
- Message ZeroClaw — it should respond via the cloud LLM
- `/status` — Dashboard Bot shows system health
- `/tasks`, `/add`, `/done`, `/delete` — task management

## Switching providers / models

Edit `zeroclaw/config.toml`:
- Change `default_provider` to `"anthropic"` or `"openai"`
- Change `default_model` to the model you want (e.g. `claude-sonnet-4-6`, `gpt-4o`)
- Make sure the matching API key is set in `.env`

Then restart: `docker compose restart zeroclaw`

## Dashboard Bot commands

| Command | Description |
|---------|-------------|
| `/status` | Show ZeroClaw config, provider, system info |
| `/tasks` | List all tasks (pending and completed) |
| `/add <task>` | Add a new task |
| `/done <id>` | Mark a task as completed |
| `/delete <id>` | Delete a task |

## Portability

Copy the entire `container-automata/` folder to any Docker machine → update `.env` → `docker compose up -d --build`. That's it.
