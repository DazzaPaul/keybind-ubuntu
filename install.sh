#!/bin/bash
set -e

echo "🔧 Installing Keybind Ubuntu..."
echo ""

cd "$(dirname "$0")"

# Check for Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install it first."
    exit 1
fi

echo "📦 Creating Python virtual environment..."
python3 -m venv .venv

echo "📥 Installing dependencies..."
. .venv/bin/activate
pip install --upgrade pip > /dev/null 2>&1
pip install -r requirements.txt > /dev/null 2>&1

echo "🔓 Making scripts executable..."
chmod +x keybind.py gui.py

echo ""
echo "✅ Installation complete!"
echo ""
echo "🚀 To get started:"
echo ""
echo "  1. Launch the GUI to configure hotkeys:"
echo "     source .venv/bin/activate"
echo "     python3 gui.py"
echo ""
echo "  2. Create profiles and map hotkeys"
echo ""
echo "  3. Run the daemon in background:"
echo "     python3 keybind.py &"
echo ""
echo "  Or enable auto-start via the GUI."
echo ""
echo "📖 Check README.md for more info"
echo ""
