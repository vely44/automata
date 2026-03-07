# Installation Guide — Nanobot + Dashboard Bot

This guide walks you through setting up Nanobot (an AI agent) on your Linux machine. No technical knowledge required.

## Quick Start

```bash
git clone https://github.com/vely44/container-automata.git
cd container-automata
./install
```

Follow the prompts. You'll be asked 4-5 questions, then everything is set up automatically.

---

## What You Need (Before Starting)

1. **Discord bot token(s)**
   - Go to [Discord Developer Portal](https://discord.com/developers/applications)
   - Create a new application (or use existing)
   - Go to "Bot" tab, click "Add Bot"
   - Click "Copy" under "TOKEN"
   - You can use the same token for both Nanobot and Dashboard Bot

2. **An LLM API key** (choose one)
   - **Anthropic (Claude)**: [https://console.anthropic.com/account/keys](https://console.anthropic.com/account/keys) — **Recommended**
   - **OpenAI (GPT-4)**: [https://platform.openai.com/account/api-keys](https://platform.openai.com/account/api-keys)

3. **~600 MB free disk space**

4. **Linux machine with internet** (Ubuntu, Debian, CentOS, Fedora, etc.)

---

## The Installation Process (Step-by-Step)

When you run `./install`, the script will guide you through these steps automatically:

### Step 1: Welcome
- Explains what Nanobot is (an AI agent connected to Discord)
- Shows what you need and what it will do
- Press Enter to continue

### Step 2: Docker Check
- Checks if Docker is installed
- If not, installs it automatically (no user interaction needed)
- Docker is a lightweight container system that runs Nanobot

**What's happening behind the scenes:**
- Detects your Linux distribution (Ubuntu, Fedora, etc.)
- Uses the appropriate package manager (apt or dnf)
- Installs Docker and enables it to start automatically
- No knowledge of Docker needed — the installer handles it all

### Step 3: Credentials
The script asks for:

1. **Nanobot Discord Token**
   - Paste the bot token from Discord Developer Portal
   - Required

2. **Dashboard Bot Token**
   - Can be the same as Nanobot's token
   - Press Enter to reuse the same one (recommended for simplicity)

3. **LLM API Key**
   - Choose Anthropic (Claude) or OpenAI
   - Paste your API key
   - At least one is required

### Step 4: Installation Location (Optional)
- Default: Current directory
- You can specify a different path if preferred
- The workspace will be created there

### Step 5: Review Configuration
- Shows a summary of what will happen
- Masks sensitive parts of tokens/keys for privacy
- Confirm with "yes" to proceed

### Step 6: Configuration File Setup
- Creates `.env` file with your credentials
- This file is in `.gitignore` so it won't be accidentally shared

### Step 7: Build and Start Services
- Downloads base software (~200 MB, one-time only)
- Builds Nanobot and Dashboard Bot images
- Starts both services automatically
- **Takes 1-2 minutes on first run**

### Step 8: Verification
- Checks if both bots are running
- Shows status summary

### Step 9: Success
- Prints next steps for using the system
- Shows useful Docker commands for troubleshooting

---

## After Installation

### Add Bot to Discord Server

1. Go to [Discord Developer Portal](https://discord.com/developers/applications)
2. Select your application
3. Go to "OAuth2" → "URL Generator"
4. Select these scopes: `bot`
5. Select these permissions:
   - `Send Messages`
   - `Use Slash Commands`
   - `Read Message History`
   - `Embed Links`
6. Copy the generated URL
7. Open the URL in your browser to invite the bot to your server

### Test It Works

Once the bot is in your Discord server:

1. **Send a message to Nanobot**
   - Mention the bot (e.g., `@Nanobot hello`)
   - It should respond with an AI-generated message
   - This means the LLM connection is working

2. **Type `/status`**
   - Dashboard Bot responds with system health
   - Shows which LLM provider you're using

3. **Type `/tasks`**
   - See all tasks
   - Use `/add <task>` to add new tasks
   - Use `/done <id>` to mark tasks complete
   - Use `/delete <id>` to remove tasks

---

## Troubleshooting

### "docker: command not found"
- Docker installation needs you to log out and back in
- Or run: `newgrp docker` (temporary for this session)

### One of the bots isn't running
```bash
cd container-automata
docker compose logs -f nanobot    # See Nanobot logs
docker compose logs -f dashbot    # See Dashboard logs
```

### Bot doesn't respond to messages
- Check the Discord token is correct in `.env`
- Verify bot has "Send Messages" permission in Discord server
- Check LLM API key is valid: `docker compose logs nanobot | tail -50`

### Restart Everything
```bash
docker compose restart
```

### Stop Services
```bash
docker compose down
```

### Start Again
```bash
docker compose up -d
```

---

## What's Actually Running?

Even though you don't need to know Docker to install this, here's what's happening:

- **Nanobot**: Python AI agent that connects to Discord and calls cloud LLMs (Anthropic or OpenAI)
- **Dashboard Bot**: Python bot that shows system status and manages tasks in Discord
- Both run in lightweight Docker containers
- They communicate through a private Docker network
- Your credentials and workspace data persist on disk

---

## What's in the `.env` File?

This file (created automatically) contains:
```
DISCORD_BOT_TOKEN=<your nanobot token>
DASHBOT_TOKEN=<your dashboard token>
ANTHROPIC_API_KEY=<your Anthropic key if using Claude>
OPENAI_API_KEY=<your OpenAI key if using GPT-4>
```

**Keep this file private** — it contains credentials. Never commit it to Git (it's in `.gitignore` by default).

---

## Switching LLM Providers

To switch from Claude to GPT-4 (or vice versa):

1. Edit `nanobot/config.yaml`
   - Change `provider:` to `"anthropic"` or `"openai"`
   - Change `model:` to the specific model (e.g., `claude-sonnet-4-6`, `gpt-4o`)

2. Restart Nanobot:
   ```bash
   docker compose restart nanobot
   ```

---

## Disk Space Used

- **First-time build**: ~200 MB (cached locally, only once)
- **Installed images**: ~510 MB
- **Persistent data**: ~50 MB (grows slowly with task history)
- **Total**: ~560 MB typical

---

## Updating or Reinstalling

To get the latest version:

```bash
git pull
docker compose down
./install
```

Or to just restart without reinstalling:
```bash
docker compose restart
```

---

## Need Help?

- **Logs**: `docker compose logs -f [nanobot|dashbot]`
- **Status**: `docker compose ps`
- **Restart**: `docker compose restart`
- **Stop everything**: `docker compose down`

For issues or feature requests, see [GitHub Issues](https://github.com/vely44/container-automata/issues).
