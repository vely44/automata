#!/usr/bin/env bash
# setup.sh — ZeroClaw Stack installer (API mode)
# Run this once on a fresh Linux server or local machine.
# Usage: bash setup.sh
set -euo pipefail

# ── colours ──────────────────────────────────────────────────────────────────
RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'
CYAN='\033[0;36m'; BOLD='\033[1m'; RESET='\033[0m'

info()    { echo -e "${CYAN}[INFO]${RESET}  $*"; }
ok()      { echo -e "${GREEN}[OK]${RESET}    $*"; }
warn()    { echo -e "${YELLOW}[WARN]${RESET}  $*"; }
error()   { echo -e "${RED}[ERROR]${RESET} $*" >&2; exit 1; }
section() { echo -e "\n${BOLD}═══ $* ═══${RESET}"; }

# ── Step 1: Docker check / install ───────────────────────────────────────────
section "Step 1 — Docker"

if docker --version &>/dev/null && docker compose version &>/dev/null; then
    ok "Docker $(docker --version | awk '{print $3}' | tr -d ',') already installed"
else
    warn "Docker not found. Installing now (Ubuntu/Debian)..."

    # Remove legacy packages silently
    sudo apt-get remove -y docker docker-engine docker.io containerd runc 2>/dev/null || true

    sudo apt-get update -qq
    sudo apt-get install -y -qq ca-certificates curl gnupg

    sudo install -m 0755 -d /etc/apt/keyrings
    curl -fsSL https://download.docker.com/linux/ubuntu/gpg \
        | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
    sudo chmod a+r /etc/apt/keyrings/docker.gpg

    # Support both Ubuntu and Linux Mint (which reports UBUNTU_CODENAME)
    CODENAME=$(. /etc/os-release && echo "${UBUNTU_CODENAME:-${VERSION_CODENAME:-$(lsb_release -cs)}}")
    echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] \
https://download.docker.com/linux/ubuntu ${CODENAME} stable" \
        | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

    sudo apt-get update -qq
    sudo apt-get install -y -qq \
        docker-ce docker-ce-cli containerd.io \
        docker-buildx-plugin docker-compose-plugin

    # Add current user to docker group so sudo isn't needed next time
    sudo usermod -aG docker "$USER" 2>/dev/null || true

    ok "Docker installed."
    warn "You may need to log out and back in (or run 'newgrp docker') for"
    warn "group changes to take effect. For this session, commands will use sudo."
fi

# ── Step 2: .env setup ───────────────────────────────────────────────────────
section "Step 2 — Environment (.env)"

if [[ -f .env ]]; then
    ok ".env already exists — skipping. Edit it manually if tokens need updating."
else
    info "Creating .env from template..."
    cp .env.example .env

    echo ""
    echo "  You need Discord bot token(s) and at least one LLM API key."
    echo "  See README.md for details."
    echo ""

    read -rp "  ZeroClaw bot token (DISCORD_BOT_TOKEN): " TOKEN_ZC
    read -rp "  Dashboard Bot token (DASHBOT_TOKEN) [press Enter to reuse ZeroClaw token]: " TOKEN_DASH
    [[ -z "$TOKEN_DASH" ]] && TOKEN_DASH="$TOKEN_ZC"

    read -rp "  Anthropic API key (ANTHROPIC_API_KEY) [press Enter to skip]: " API_ANTHROPIC
    read -rp "  OpenAI API key (OPENAI_API_KEY) [press Enter to skip]: " API_OPENAI

    # Write values into .env
    sed -i "s|your_discord_bot_token_here|${TOKEN_ZC}|" .env
    sed -i "s|your_dashbot_token_here|${TOKEN_DASH}|" .env
    [[ -n "$API_ANTHROPIC" ]] && sed -i "s|your_anthropic_api_key_here|${API_ANTHROPIC}|" .env
    [[ -n "$API_OPENAI" ]] && sed -i "s|your_openai_api_key_here|${API_OPENAI}|" .env

    ok ".env configured."
fi

# ── Step 3: Verify .env has real tokens ──────────────────────────────────────
section "Step 3 — Token check"

if grep -qE "your_(discord_bot|dashbot)_token_here" .env; then
    warn ".env still contains placeholder Discord tokens."
    warn "Edit .env and replace the placeholder values, then re-run this script."
    exit 1
fi

if grep -qE "your_(anthropic|openai)_api_key_here" .env && \
   ! grep -qvE "your_(anthropic|openai)_api_key_here|^#" .env | grep -q "API_KEY"; then
    warn "No LLM API key set. ZeroClaw needs at least one (Anthropic or OpenAI)."
    warn "Edit .env and add your API key, then re-run this script."
    exit 1
fi

ok "Tokens look set."

# ── Step 4: Build containers ─────────────────────────────────────────────────
section "Step 4 — Build & launch"

info "Running: docker compose up -d --build"
docker compose up -d --build

ok "Containers started."

# ── Step 5: Verify ───────────────────────────────────────────────────────────
section "Step 5 — Verify"

echo ""
docker compose ps
echo ""

for svc in zeroclaw dashbot; do
    STATE=$(docker compose ps "$svc" --format '{{.State}}' 2>/dev/null || echo "unknown")
    if [[ "$STATE" == "running" ]]; then
        ok "${svc}: running"
    else
        warn "${svc}: ${STATE} — check logs with: docker compose logs ${svc}"
    fi
done

echo ""
echo -e "${BOLD}════════════════════════════════════════${RESET}"
echo -e "${GREEN}  Installation complete!${RESET}"
echo -e "${BOLD}════════════════════════════════════════${RESET}"
echo ""
echo "  Useful commands:"
echo "    docker compose ps                         # container status"
echo "    docker compose logs -f zeroclaw           # ZeroClaw logs"
echo "    docker compose logs -f dashbot            # Dashboard logs"
echo ""
echo "  Test in Discord:"
echo "    - Send a message to your ZeroClaw bot — it should respond via the LLM"
echo "    - Type /status — Dashboard Bot shows system health"
echo "    - Type /tasks, /add <task>, /done <id>, /delete <id>"
echo ""
