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

## Installation

Works on any Linux machine — local PC ((needed only for local testing/real app will go directly to a hosted server)) or remote server. Pick your scenario and follow along.

### Quick install (automated)

If you're on Ubuntu/Debian and just want to go fast, run the setup script after cloning — it handles Docker, `.env`, build, model pull, and verification in one shot:

```bash
git clone https://github.com/vely44/container-automata.git
cd container-automata
bash setup.sh
```

Or follow the manual steps below for more control.

---

### 1. Connect to your machine

**Local PC** — Open a terminal. You're ready.

**Remote server (VPS/Cloud)** — SSH in:
```bash
ssh user@your-server-ip
# Or with a key:
ssh -i ~/.ssh/your-key.pem user@your-server-ip
```

### 2. Install Docker

**Already have Docker?** Some cloud providers (like Hetzner Cloud with a "Docker CE" app image) come with Docker pre-installed. Check first:
```bash
docker --version && docker compose version
```
If both commands print a version number, skip ahead to **Step 3**.

**Ubuntu / Linux Mint / Debian:**
```bash
# Remove old versions if any
sudo apt-get remove -y docker docker-engine docker.io containerd runc 2>/dev/null

# Install prerequisites
sudo apt-get update
sudo apt-get install -y ca-certificates curl gnupg

# Add Docker's official GPG key
sudo install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
sudo chmod a+r /etc/apt/keyrings/docker.gpg

# Add the repository
# For Ubuntu / Mint (uses Ubuntu repos):
echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu $(. /etc/os-release && echo "${UBUNTU_CODENAME:-$VERSION_CODENAME}") stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

# Install Docker Engine + Compose plugin
sudo apt-get update
sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

# Let your user run Docker without sudo
sudo usermod -aG docker $USER
```

Log out and back in (or run `newgrp docker`) for the group change to take effect.

**Verify Docker works:**
```bash
docker --version
docker compose version
```

### 3. Create a Discord Bot

1. Go to https://discord.com/developers/applications
2. Click **New Application** — give it a name
3. Go to **Bot** tab → click **Reset Token** → copy the token (save it, you won't see it again)
4. Under **Privileged Gateway Intents**, enable **Message Content Intent**
5. Go to **OAuth2 → URL Generator**:
   - Scopes: `bot`, `applications.commands`
   - Bot Permissions: `Send Messages`, `Use Slash Commands`, `Read Message History`, `Embed Links`
6. Copy the generated URL → open it in your browser → invite the bot to your server

You can create one bot for both ZeroClaw and Dashboard, or two separate bots.

### 4. Clone and configure

```bash
git clone https://github.com/vely44/container-automata.git
cd container-automata

# Create your .env from the template
cp .env.example .env
```

Edit `.env` with your token(s):
```bash
nano .env
```

Fill in:
```
DISCORD_BOT_TOKEN=your_zeroclaw_token_here
DASHBOT_TOKEN=your_dashbot_token_here
ZEROCLAW_PORT=8080
```

### 5. Build and launch

```bash
docker compose up -d --build
```

First build takes a minute or two (downloading the ZeroClaw prebuilt binary + Python dependencies for Dashboard Bot).

Pull the default LLM model:
```bash
docker compose exec ollama ollama pull mistral:7b
```

### 6. Verify

```bash
# All 3 containers should show "Up"
docker compose ps

# Check ZeroClaw connected to Discord
docker compose logs zeroclaw

# Check Dashboard Bot connected
docker compose logs dashbot

# Confirm model is loaded
docker compose exec ollama ollama list
```

Then test in Discord:
- Message ZeroClaw — it should respond via the LLM
- Type `/status` — Dashboard Bot shows system health
- Type `/tasks`, `/add`, `/done`, `/delete` — task management works

---

## Remote server — extra considerations

**Firewall:** Only port 8080 (ZeroClaw gateway) needs to be open if you want external webhook access. All Discord communication happens outbound, so the bots work behind firewalls with no inbound ports open.

```bash
# If using UFW (Ubuntu/Mint):
sudo ufw allow OpenSSH
sudo ufw allow 8080/tcp    # Only if you need external webhook access
sudo ufw enable
```

**Running in a screen/tmux session** (so it survives SSH disconnect):
```bash
# Docker containers already run detached (-d flag), so they persist
# after SSH disconnect. No screen/tmux needed for the stack itself.

# But if you want a persistent terminal for monitoring:
tmux new -s zeroclaw
docker compose logs -f
# Detach: Ctrl+B then D
# Reattach later: tmux attach -t zeroclaw
```

**Auto-start on reboot:** The `restart: unless-stopped` policy in docker-compose.yml already handles this — containers come back after a server reboot as long as Docker itself starts (which it does by default).

---

## Hardware & model guide

Ollama loads LLM models into memory. How much memory and what kind determines which models you can run and how fast they respond.

### Base test configuration

This project is developed and tested on the following reference hardware:

| Component | Spec |
|-----------|------|
| CPU | Intel i5-9600 (6 cores) |
| RAM | 16 GB DDR4 |
| GPU | NVIDIA GTX 1060 6GB VRAM |
| OS | Ubuntu / Docker Desktop |

**Base test model: `mistral:7b`** — Q4 quantization weighs ~4.1 GB, fits entirely in 6 GB VRAM. This is the default model shipped with the project. If the stack runs `mistral:7b` and responds coherently, everything works.

### How it works: RAM vs GPU

- **CPU-only (RAM)** — Ollama loads the model into system RAM and runs inference on the CPU. This works on any machine. Slower response times, but no special hardware needed.
- **GPU-accelerated (VRAM)** — If an NVIDIA GPU is available, Ollama offloads the model to GPU VRAM. Much faster inference (5–20x). The model must fit in VRAM, otherwise it spills to RAM and slows down.

### Rented server (VPS/Cloud) — typically CPU-only

Most standard VPS plans (Hetzner Cloud, DigitalOcean, Linode, Vultr) are **CPU-only**. There is no GPU. Ollama runs entirely on CPU using system RAM.

| VPS RAM | Model size | Example models | Response speed |
|---------|------------|----------------|----------------|
| 4 GB | Not recommended | — | Stack alone needs ~1.5 GB |
| 8 GB | Up to 3B | `llama3.2:3b`, `phi3:3b` | ~5–15 tokens/sec |
| 16 GB | Up to 7B | `mistral:7b`, `llama3.1:8b` | ~3–10 tokens/sec |
| 32 GB | Up to 13B | `llama2:13b`, `codellama:13b` | ~2–6 tokens/sec |

> **On a VPS, Ollama uses only RAM — no GPU.** A 16 GB VPS can run the base test model (`mistral:7b`) on CPU at ~3–10 tokens/sec. Slower than GPU but perfectly functional.

**Can you get GPU on a rented server?** Yes, but it costs more:
- **Hetzner** — Dedicated GPU servers exist (not on Cloud VPS). Pricier, requires application.
- **GPU cloud providers** — RunPod, Vast.ai, Lambda Cloud rent GPU instances by the hour. Great for testing bigger models.
- **Big cloud** — AWS (p3/g5 instances), GCP, Azure all offer GPU VMs.

For this stack, a standard **8–16 GB CPU VPS is enough** to run 3B–7B models. GPU is a nice-to-have, not a requirement.

### Local PC

Your local machine can use CPU-only or GPU — depending on your hardware.

**CPU-only (no NVIDIA GPU or GPU disabled):**

| System RAM | Model size | Example models | Response speed |
|------------|------------|----------------|----------------|
| 8 GB | Up to 3B | `llama3.2:3b` | ~5–15 tokens/sec |
| 16 GB | Up to 7B | `mistral:7b` | ~3–10 tokens/sec |
| 32 GB | Up to 13B | `llama2:13b` | ~2–6 tokens/sec |
| 64 GB | Up to 30B+ | `codellama:34b` | ~1–3 tokens/sec |

**With NVIDIA GPU (uses VRAM — much faster):**

| GPU VRAM | Model size | Example models | Response speed |
|----------|------------|----------------|----------------|
| 4 GB (GTX 1650) | Up to 3B | `llama3.2:3b` | ~20–40 tokens/sec |
| **6 GB (GTX 1060)** | **Up to 7B** | **`mistral:7b` (base test model)** | **~15–30 tokens/sec** |
| 8 GB (RTX 3060/4060) | Up to 7B | `mistral:7b`, `llama3.1:8b` | ~30–60 tokens/sec |
| 12 GB (RTX 3060 12GB) | Up to 13B | `llama2:13b` | ~20–40 tokens/sec |
| 24 GB (RTX 3090/4090) | Up to 30B+ | `codellama:34b` | ~15–30 tokens/sec |

> When the model doesn't fully fit in VRAM, Ollama splits it between GPU and RAM automatically. Performance lands somewhere between the two tables above.

**On the reference PC (GTX 1060 6GB + 16GB RAM):** `mistral:7b` loads fully into VRAM. Expect ~15–30 tokens/sec with GPU enabled, or ~3–10 tokens/sec CPU-only.

**Dashboard Bot + ZeroClaw overhead:** ~200 MB RAM total. Negligible compared to the LLM model.

### Enabling GPU support

Only needed if you have an NVIDIA GPU (local PC or GPU-equipped server). AMD/Intel GPUs are not supported by Ollama at this time.

**Step 1 — Install NVIDIA Container Toolkit:**
```bash
curl -fsSL https://nvidia.github.io/libnvidia-container/gpgkey | sudo gpg --dearmor -o /usr/share/keyrings/nvidia-container-toolkit-keyring.gpg
curl -s -L https://nvidia.github.io/libnvidia-container/stable/deb/nvidia-container-toolkit.list | sed 's#deb https://#deb [signed-by=/usr/share/keyrings/nvidia-container-toolkit-keyring.gpg] https://#g' | sudo tee /etc/apt/sources.list.d/nvidia-container-toolkit.list
sudo apt-get update
sudo apt-get install -y nvidia-container-toolkit
sudo nvidia-ctk runtime configure --runtime=docker
sudo systemctl restart docker
```

**Step 2 — Uncomment the GPU block** in `docker-compose.yml` under the `ollama` service:
```yaml
deploy:
  resources:
    reservations:
      devices:
        - driver: nvidia
          count: all
          capabilities: [gpu]
```

**Step 3 — Verify GPU is detected:**
```bash
docker compose up -d --build
docker compose exec ollama nvidia-smi
```

If `nvidia-smi` shows your GPU, Ollama will use it automatically.

---

## Swapping models

No rebuild needed — just pull and point:

```bash
# Pull a new model
docker compose exec ollama ollama pull mistral:7b

# List available models
docker compose exec ollama ollama list
```

Then edit `zeroclaw/config.toml` and change `default_model`:
```toml
default_model = "mistral:7b"
```

Restart ZeroClaw to pick it up:
```bash
docker compose restart zeroclaw
```

---

## Quick reference

| Action | Command |
|--------|---------|
| Start stack | `docker compose up -d` |
| Stop stack | `docker compose down` |
| Rebuild | `docker compose up -d --build` |
| View all logs | `docker compose logs -f` |
| ZeroClaw logs | `docker compose logs -f zeroclaw` |
| Dashboard logs | `docker compose logs -f dashbot` |
| Pull model | `docker compose exec ollama ollama pull <model>` |
| List models | `docker compose exec ollama ollama list` |
| Restart ZeroClaw | `docker compose restart zeroclaw` |

## Dashboard Bot commands

| Command | Description |
|---------|-------------|
| `/status` | Show Ollama health, ZeroClaw config, system info |
| `/tasks` | List all tasks (pending and completed) |
| `/add <task>` | Add a new task |
| `/done <id>` | Mark a task as completed |
| `/delete <id>` | Delete a task |

---

## Portability

Copy the entire `container-automata/` folder to any Docker machine → update `.env` → `docker compose up -d --build`. That's it.

## Progress tracker 

- [x] Project structure created
- [x] docker-compose.yml (3 services)
- [x] ZeroClaw Dockerfile (prebuilt binary)
- [x] zeroclaw/config.toml
- [x] .env template
- [x] Dashboard Bot Dockerfile
- [x] dashbot/bot.py
- [x] dashbot/requirements.txt
- [ ] Install Docker on target machine
- [ ] Create Discord Bot and get token
- [ ] Build containers
- [ ] Pull Ollama model
- [ ] Verify all services running
- [x] `setup.sh` — automated installer covering all steps above
