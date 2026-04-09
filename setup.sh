#!/bin/bash
# ============================================================
#  TaskNest — One-command setup script
# ============================================================
set -e

BOLD="\033[1m"
PINK="\033[35m"
GREEN="\033[32m"
RESET="\033[0m"

echo -e "${PINK}${BOLD}"
echo "  ████████╗ █████╗ ███████╗██╗  ██╗███╗   ██╗███████╗███████╗████████╗"
echo "     ██╔══╝██╔══██╗██╔════╝██║ ██╔╝████╗  ██║██╔════╝██╔════╝╚══██╔══╝"
echo "     ██║   ███████║███████╗█████╔╝ ██╔██╗ ██║█████╗  ███████╗   ██║   "
echo "     ██║   ██╔══██║╚════██║██╔═██╗ ██║╚██╗██║██╔══╝  ╚════██║   ██║   "
echo "     ██║   ██║  ██║███████║██║  ██╗██║ ╚████║███████╗███████║   ██║   "
echo "     ╚═╝   ╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝╚═╝  ╚═══╝╚══════╝╚══════╝   ╚═╝   "
echo -e "${RESET}"
echo -e "${PINK}🌸  Task Manager System — Setup${RESET}"
echo "============================================================"
echo ""

# ── 1. Check Python ──────────────────────────────────────────
echo -e "${BOLD}[1/6] Checking Python...${RESET}"
python3 --version || { echo "❌ Python 3 not found. Install Python 3.10+ first."; exit 1; }

# ── 2. Create virtual environment ────────────────────────────
echo -e "${BOLD}[2/6] Creating virtual environment...${RESET}"
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo "  ✅ Virtual environment created"
else
    echo "  ℹ️  Virtual environment already exists"
fi

# ── 3. Activate and install dependencies ─────────────────────
echo -e "${BOLD}[3/6] Installing dependencies...${RESET}"
source venv/bin/activate
pip install --upgrade pip -q
pip install -r requirements.txt -q
echo "  ✅ Django and dependencies installed"

# ── 4. Run migrations ────────────────────────────────────────
echo -e "${BOLD}[4/6] Running database migrations...${RESET}"
python manage.py makemigrations accounts tasks groups_app --no-input
python manage.py migrate --no-input
echo "  ✅ Database ready"

# ── 5. Create superuser ──────────────────────────────────────
echo -e "${BOLD}[5/6] Create admin superuser${RESET}"
echo "  (You can skip this and use /admin/ later)"
echo ""
python manage.py createsuperuser

# ── 6. Start server ──────────────────────────────────────────
echo ""
echo -e "${GREEN}${BOLD}✅ Setup complete!${RESET}"
echo "============================================================"
echo -e "  🌸  TaskNest is running at: ${BOLD}http://127.0.0.1:8000${RESET}"
echo -e "  🔑  Admin panel:            ${BOLD}http://127.0.0.1:8000/admin${RESET}"
echo "============================================================"
echo ""
echo -e "${BOLD}[6/6] Starting development server...${RESET}"
python manage.py runserver
