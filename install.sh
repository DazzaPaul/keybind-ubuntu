#!/bin/bash
set -e

echo "Installing Keybind Ubuntu..."

echo "Creating virtual environment..."
python3 -m venv .venv

source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

chmod +x keybind.py gui.py tray_daemon.py

echo "Installation complete."
echo "Run with:"
echo "  source .venv/bin/activate"
echo "  python3 tray_daemon.py"
