#!/bin/bash
set -e

echo "🔧 Installing Keybind Ubuntu..."

cd "$(dirname "$0")"

# Create Python virtual environment
echo "📦 Setting up Python environment..."
python3 -m venv .venv

# Activate and install dependencies
echo "📥 Installing dependencies..."
. .venv/bin/activate
pip install --upgrade pip > /dev/null 2>&1
pip install -r requirements.txt > /dev/null 2>&1

# Make keybind.py executable
chmod +x keybind.py

echo ""
echo "✅ Installation complete!"
echo ""
echo "📝 Next steps:"
echo "  1. Edit credentials.json with your username and password"
echo "  2. Run the app:"
echo "     source .venv/bin/activate"
echo "     python3 keybind.py"
echo ""
echo "⌨️  Press Ctrl+Alt+F to trigger auto-fill (or your configured hotkey)"
echo ""
