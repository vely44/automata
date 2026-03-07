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
   - **Other providers**: Ollama, Groq, Together.ai, or any custom LLM endpoint

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
   - Choose Anthropic (Claude), OpenAI, or a custom provider
   - Paste your API key
   - At least one is required
   - Custom providers: Ollama (local), Groq, Together.ai, etc.

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

## Understanding the Architecture

### Two Bots, Two Jobs

**Nanobot** (the AI agent):
- Connects to Discord and listens for mentions (e.g., `@Nanobot hello`)
- Sends messages to a cloud LLM (Claude or GPT-4)
- Can execute commands: bash scripts, git operations, file management
- Runs in a **sandbox** — only allowed commands work, dangerous paths are blocked
- Has **memory** — remembers your last 100 interactions in SQLite database
- Can be **autonomous** or **supervised** (you control how much it can do)

**Dashboard Bot** (the helper):
- Shows system health and status (`/status` command)
- Manages a task list (`/tasks`, `/add`, `/done`, `/delete`)
- Runs independently from Nanobot

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

## What Can Nanobot Actually Do?

Nanobot is more than just a chatbot — it can execute real commands on your system.

### Nanobot Capabilities

Nanobot has access to these tools (in a **sandboxed** environment):

| Tool | What it can do | Examples |
|------|---|---|
| **bash** | Run shell commands safely | `ls`, `cat`, `grep`, `mkdir`, `cp`, `mv` |
| **git** | Clone, commit, push repos | `git clone`, `git status`, `git commit -m "msg"` |
| **file_operations** | Create, read, edit files | Can't access `/etc`, `/root`, `/proc`, `/sys` (forbidden) |

### Real Examples

**Example 1: Clone a repo and show its structure**
```
@Nanobot clone https://github.com/example/project and show me the file structure
```
Nanobot will:
1. Run `git clone https://github.com/example/project`
2. Run `ls -la project/` to show the structure
3. Report back in Discord

**Example 2: Count lines of code**
```
@Nanobot count lines of Python code in the repo you just cloned
```
Nanobot will:
1. Run `find project -name "*.py" -type f`
2. Run `wc -l` on each file
3. Give you a summary

**Example 3: Search for something**
```
@Nanobot grep for "TODO" in the project and tell me what needs to be done
```
Nanobot will:
1. Run `grep -r "TODO" project/`
2. Analyze the results
3. Summarize what needs fixing

### Sandbox Security Model

Nanobot **cannot**:
- Access system files (`/etc`, `/root`, `/proc`, `/sys`)
- Run dangerous commands directly (only allowed list works)
- Access files outside the workspace
- Write to protected directories

This keeps your system safe while still being powerful.

---

## Customizing Nanobot

After installation, you can customize how Nanobot behaves by editing `nanobot/config.yaml`.

### Edit the Configuration File

```bash
nano nanobot/config.yaml
```

### Configuration Options Explained

#### **LLM Provider** (which AI model to use)

```yaml
llm:
  provider: "anthropic"  # "anthropic", "openai", or custom provider name
  model: "claude-sonnet-4-6"  # Change to gpt-4o for OpenAI or your custom model
  temperature: 0.7       # 0=deterministic, 1=creative (0-1)
  max_tokens: 4096       # Max response length
```

**What these mean:**
- `provider`: Which service to call (Anthropic's Claude, OpenAI's GPT, or custom provider)
- `model`: Specific version (e.g., `claude-sonnet-4-6`, `gpt-4o`, or custom model name)
- `temperature`: How "creative" the responses are. 0 = always the same, 1 = random. **0.7 is recommended**
- `max_tokens`: Character limit per response (more = slower, costs more)

**Examples:**
```yaml
# Fast, cheap, deterministic
provider: "anthropic"
model: "claude-haiku-4-5-20251001"
temperature: 0.3
max_tokens: 2048

# Slow, expensive, creative
provider: "openai"
model: "gpt-4o"
temperature: 0.9
max_tokens: 8000
```

#### **Memory** (remembering past conversations)

```yaml
memory:
  backend: "sqlite"
  db_path: "/app/workspace/memory.db"
  max_history: 100  # Remember last 100 messages
```

**What this does:**
- Nanobot remembers your last 100 interactions
- Older messages are forgotten (memory is cleared)
- Useful for multi-turn conversations
- Change `max_history` to remember more (uses more disk) or less

#### **Tools** (what commands Nanobot can run)

```yaml
tools:
  enabled_tools:
    - "bash"
    - "git"
    - "file_operations"
  sandbox_mode: true  # Keep this ON for safety
  allowed_commands:
    - "git"
    - "npm"
    - "ls"
    - "cat"
    - "grep"
    - "mkdir"
    - "cp"
    - "mv"
  forbidden_paths:
    - "/etc"
    - "/root"
    - "/proc"
    - "/sys"
```

**What this does:**
- `enabled_tools`: Which tool categories are available
- `sandbox_mode`: **Keep this TRUE** — it prevents dangerous operations
- `allowed_commands`: Whitelist of commands Nanobot can run
- `forbidden_paths`: Directories Nanobot cannot access

**⚠️ Security Note:** Don't disable `sandbox_mode` — it protects your system.

#### **Autonomy** (how independent Nanobot can be)

```yaml
autonomy:
  level: "supervised"  # "supervised" or "autonomous"
  max_actions_per_hour: 20
  max_cost_per_day_cents: 500
```

**What this does:**
- `level: "supervised"`: Nanobot asks before taking actions (safer)
- `level: "autonomous"`: Nanobot acts on its own (faster, riskier)
- `max_actions_per_hour`: Prevents runaway commands (20 per hour default)
- `max_cost_per_day_cents`: Stops if API costs exceed $5/day (prevents bill shock)

**Recommended:** Keep `"supervised"` until you trust Nanobot.

### Apply Changes

After editing `config.yaml`, restart Nanobot:

```bash
docker compose restart nanobot
```

The changes take effect immediately.

---

## Common Customization Examples

### Make Nanobot Faster (Cheaper)

Edit `nanobot/config.yaml`:
```yaml
llm:
  provider: "anthropic"
  model: "claude-haiku-4-5-20251001"  # Smallest, fastest model
  temperature: 0.5
  max_tokens: 2048
```

### Make Nanobot Smarter (Slower, More Expensive)

```yaml
llm:
  provider: "anthropic"
  model: "claude-opus-4-6"  # Largest, smartest model
  temperature: 0.7
  max_tokens: 8000
```

### Switch to OpenAI GPT-4

```yaml
llm:
  provider: "openai"
  model: "gpt-4o"
  temperature: 0.7
  max_tokens: 4096
```

Make sure your `.env` has `OPENAI_API_KEY=sk-...` set.

### Use a Custom LLM Provider (Ollama, Groq, etc.)

If you're using a custom LLM provider (local Ollama, Groq, Together.ai, etc.):

1. Set environment variables in `.env`:
```
LLM_PROVIDER=ollama
LLM_API_KEY=http://localhost:11434  # For Ollama, or your provider's endpoint
```

2. Update `nanobot/config.yaml`:
```yaml
llm:
  provider: "ollama"  # Your custom provider name
  model: "mistral"    # Your model name
  temperature: 0.7
  max_tokens: 4096
```

3. Restart:
```bash
docker compose restart nanobot
```

**Note:** For local providers like Ollama, ensure the service is running and accessible from the Docker container.

### Allow More Commands (⚠️ less safe)

If you need specific commands, add them to `allowed_commands`:

```yaml
tools:
  allowed_commands:
    - "git"
    - "npm"
    - "ls"
    - "cat"
    - "grep"
    - "mkdir"
    - "cp"
    - "mv"
    - "python"  # Add this if you want Python script execution
    - "node"    # Add this if you want Node.js scripts
```

Then restart: `docker compose restart nanobot`

### Let Nanobot Act Autonomously (⚠️ less safe)

Only do this if you fully trust it:

```yaml
autonomy:
  level: "autonomous"  # Be careful!
  max_actions_per_hour: 50
  max_cost_per_day_cents: 1000
```

---

## Next Steps & What To Try

After customizing Nanobot, here are things you can try:

### 1. Start Simple
```
@Nanobot hello, what can you do?
```
Let it explain its capabilities.

### 2. Give It a Project Task
```
@Nanobot clone https://github.com/example/repo and summarize what it does
```

### 3. Use It For Code Tasks
```
@Nanobot create a Python script that converts CSV to JSON
```

### 4. Combine With Task Manager
```
/add Learn Docker basics
```
Then:
```
@Nanobot help me understand Docker, and add relevant resources to the task list
```

### 5. Monitor Its Performance
```
/status
```
Check which LLM model is running, and how much cost you've incurred.

---

## Where Are the Workspace Files?

Nanobot saves all its work in `nanobot/workspace/`:

```
nanobot/
├── workspace/
│   ├── memory.db      # Past conversations (searchable)
│   ├── projects/      # Any projects Nanobot creates
│   └── artifacts/     # Generated files
├── config.yaml        # ← You can edit this
└── ...
```

You can manually browse or edit files in `workspace/` if needed.

---

## Advanced: Checking Logs

To see what Nanobot is actually doing:

```bash
docker compose logs -f nanobot
```

This shows:
- Every message received
- Which LLM was called
- What commands were executed
- Any errors

Useful for debugging or learning how it works.

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
LLM_PROVIDER=<custom provider name, if using custom LLM>
LLM_API_KEY=<custom provider API key or endpoint>
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
