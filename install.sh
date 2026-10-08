#!/usr/bin/env python3
"""Install dependencies and prepare the project for Ubuntu."""

set -e

echo "Installing Keybind Ubuntu dependencies..."

if ! command -v python3 >/dev/null 2>&1; then
  echo "Python 3 is required."
  exit 1
fi

cd "$(dirname "$0")"

python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
chmod +x keybind.py gui.py tray_daemon.py

cat <<'EOF'

✅ Installation complete.

Run the GUI:
  source .venv/bin/activate
  python3 gui.py

Run the tray app:
  source .venv/bin/activate
  python3 tray_daemon.py

Run the daemon directly:
  source .venv/bin/activate
  python3 keybind.py
EOF
