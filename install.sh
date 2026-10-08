#!/bin/bash
set -e

echo "🔧 Installing Keybind Ubuntu..."
echo ""

cd "$(dirname "$0")"

if ! command -v python3 >/dev/null 2>&1; then
  echo "❌ Python 3 is required."
  exit 1
fi

echo "📦 Creating Python virtual environment..."
python3 -m venv .venv

echo "📥 Installing dependencies..."
. .venv/bin/activate
pip install --upgrade pip > /dev/null 2>&1
pip install -r requirements.txt > /dev/null 2>&1

echo "🔑 Making scripts executable..."
chmod +x keybind.py gui.py tray_daemon.py

echo ""
echo "✅ Installation complete!"
echo ""
echo "🚀 To get started:"
echo ""
echo "  1. Activate virtual environment:"
echo "     source .venv/bin/activate"
echo ""
echo "  2. Option A: Run with system tray (recommended):"
echo "     python3 tray_daemon.py &"
echo ""
echo "  2. Option B: Run GUI to configure:"
echo "     python3 gui.py"
echo ""
echo "  2. Option C: Run daemon directly:"
echo "     python3 keybind.py &"
echo ""
echo "📖 Check README.md for more info"
echo ""
