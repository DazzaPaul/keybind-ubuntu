#!/usr/bin/env python3
set -e

cd "$(dirname "$0")"

python3 -m venv .venv
. .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

cat <<'EOF'

Installation complete.

Edit credentials.json with your username/password and then run:

    source .venv/bin/activate
    python3 keybind.py

Use a hotkey like Ctrl+Alt+F to trigger the login entry.
EOF
