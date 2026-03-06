#!/usr/bin/env bash
# =============================================================================
# setup-server.sh
# รันครั้งเดียวบน Docker Server เพื่อเตรียม environment ครั้งแรก
#
# Usage:
#   chmod +x setup-server.sh
#   ./setup-server.sh
# =============================================================================
set -e

REPO_URL="https://github.com/apiwat1229/YTRC-FastAPI-Backend.git"
DEPLOY_DIR="$HOME/ytrc-backend"
SERVER_IP="10.51.10.21"

echo ""
echo "╔══════════════════════════════════════════╗"
echo "║   YTRC Backend — Server First-Time Setup ║"
echo "╚══════════════════════════════════════════╝"
echo ""

# ─── 1. Install dependencies ─────────────────────────────────────────────────
echo ">>> [1/6] Checking dependencies..."
command -v docker >/dev/null 2>&1 || { echo "ERROR: docker not found. Install Docker first."; exit 1; }
command -v git    >/dev/null 2>&1 || { echo "ERROR: git not found."; exit 1; }
echo "    docker: OK"
echo "    git:    OK"

# ─── 2. Generate SSH key for GitHub Actions ───────────────────────────────────
echo ""
echo ">>> [2/6] Generating SSH key for GitHub Actions..."
KEY_PATH="$HOME/.ssh/github_actions_deploy"
if [ -f "$KEY_PATH" ]; then
  echo "    Key already exists at $KEY_PATH — skipping."
else
  ssh-keygen -t ed25519 -C "github-actions-deploy@$SERVER_IP" -f "$KEY_PATH" -N ""
  echo "    Key created: $KEY_PATH"
fi

# Add public key to authorized_keys
mkdir -p "$HOME/.ssh"
chmod 700 "$HOME/.ssh"
PUB_KEY=$(cat "${KEY_PATH}.pub")
if ! grep -qF "$PUB_KEY" "$HOME/.ssh/authorized_keys" 2>/dev/null; then
  echo "$PUB_KEY" >> "$HOME/.ssh/authorized_keys"
  chmod 600 "$HOME/.ssh/authorized_keys"
  echo "    Public key added to authorized_keys ✓"
else
  echo "    Public key already in authorized_keys — skipping."
fi

echo ""
echo "────────────────────────────────────────────────────────────"
echo "  ACTION REQUIRED — Add this PRIVATE KEY to GitHub Secrets:"
echo "  (GitHub → Settings → Secrets → Actions → SERVER_SSH_KEY)"
echo "────────────────────────────────────────────────────────────"
cat "$KEY_PATH"
echo "────────────────────────────────────────────────────────────"
echo ""

# ─── 3. Clone repo ───────────────────────────────────────────────────────────
echo ">>> [3/6] Cloning repository..."
if [ -d "$DEPLOY_DIR/.git" ]; then
  echo "    Repo already exists — skipping clone."
else
  git clone "$REPO_URL" "$DEPLOY_DIR"
  echo "    Cloned to $DEPLOY_DIR ✓"
fi

cd "$DEPLOY_DIR"

# ─── 4. Check for .env files ─────────────────────────────────────────────────
echo ""
echo ">>> [4/6] Checking .env files..."
MISSING_ENV=0

if [ ! -f ".env.production" ]; then
  echo "    ⚠  .env.production NOT FOUND"
  echo "       Copy from .env.example and fill in production values:"
  echo "       cp .env.example .env.production && nano .env.production"
  MISSING_ENV=1
else
  echo "    .env.production: OK"
fi

if [ ! -f ".env.staging" ]; then
  echo "    ⚠  .env.staging NOT FOUND"
  echo "       Copy from .env.example and fill in staging values:"
  echo "       cp .env.example .env.staging && nano .env.staging"
  MISSING_ENV=1
else
  echo "    .env.staging: OK"
fi

if [ "$MISSING_ENV" = "1" ]; then
  echo ""
  echo "  Create the missing .env files first, then run:"
  echo "    make deploy-staging"
  echo "    make deploy-prod"
  echo ""
fi

# ─── 5. Create uploads directory ─────────────────────────────────────────────
echo ">>> [5/6] Ensuring uploads/ directory exists..."
mkdir -p uploads/avatars uploads/it-asset uploads/knowledge-books
echo "    uploads/: OK"

# ─── 6. Summary ──────────────────────────────────────────────────────────────
echo ""
echo ">>> [6/6] GitHub Secrets to add:"
echo ""
echo "   SECRET NAME     │ VALUE"
echo "   ─────────────── │ ────────────────────────────────"
echo "   SERVER_HOST     │ $SERVER_IP"
echo "   SERVER_USER     │ $(whoami)"
echo "   SERVER_SSH_KEY  │ (private key printed above)"
echo ""
echo "╔══════════════════════════════════════════════════╗"
echo "║  Setup complete!                                 ║"
echo "║                                                  ║"
echo "║  Next steps:                                     ║"
echo "║  1. Copy private key → GitHub SECRET             ║"
echo "║  2. Create .env.production and .env.staging      ║"
echo "║  3. make deploy-staging   (test build)           ║"
echo "║  4. make deploy-prod      (production)           ║"
echo "╚══════════════════════════════════════════════════╝"
echo ""
