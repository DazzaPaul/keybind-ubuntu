# Keybind Ubuntu - AutoHotkey for Ubuntu

A lightweight keyboard shortcut tool for Ubuntu that auto-fills usernames and passwords with a hotkey. No more typing credentials repeatedly.

## What It Does

Press a hotkey (like `Ctrl+Alt+F`) and the app instantly types your username and password into the active field.

## Features

- ⌨️ Global hotkey listener (even when window is unfocused)
- 🔐 Store and auto-type credentials
- ⚡ Lightweight & fast
- 💾 Simple JSON config
- 🚀 Auto-start on login (optional)

## Quick Start

```bash
git clone https://github.com/DazzaPaul/keybind-ubuntu.git
cd keybind-ubuntu
chmod +x install.sh
./install.sh
```

## Configure

Edit `credentials.json`:

```json
{
  "default_profile": "work",
  "profiles": {
    "work": {
      "hotkey": "ctrl+alt+f",
      "username": "your_email@example.com",
      "password": "your_password",
      "tab_after_username": true,
      "enter_after_password": false,
      "delay": 0.1
    }
  }
}
```

## Run

```bash
source .venv/bin/activate
python3 keybind.py
```

Press `Ctrl+Alt+F` when focused on a login field.

## Configuration Options

| Option | Type | Description |
|--------|------|-------------|
| `hotkey` | string | Keyboard shortcut (e.g., `ctrl+alt+f`, `shift+super+p`) |
| `username` | string | Text to type first |
| `password` | string | Text to type second |
| `tab_after_username` | bool | Press Tab between username and password |
| `enter_after_password` | bool | Press Enter after typing password |
| `delay` | float | Delay in seconds between actions (default: 0.1) |

## Supported Hotkeys

- Modifiers: `ctrl`, `alt`, `shift`, `super` (Windows key)
- Keys: `a-z`, `0-9`, `f1-f12`, `enter`, `tab`, `space`, `esc`, `up`, `down`, `left`, `right`
- Format: `ctrl+alt+f` or `shift+super+p`

## Security

⚠️ **Important**: Credentials are stored in plain text. This is convenient but not secure.

- Keep `credentials.json` private
- Use only on personal machines
- For sensitive work, consider using a password manager instead

## Requirements

- Ubuntu 20.04+
- Python 3.10+
- X11 session (most Ubuntu systems)

## Troubleshooting

**Hotkey doesn't work?**
- Make sure the app is running: `python3 keybind.py`
- Check if hotkey is already used by your system
- Try a different hotkey combination
- Ensure you're using X11 (not Wayland-only)

**App crashes on start?**
- Install requirements: `pip install -r requirements.txt`
- Check that `credentials.json` exists and is valid JSON

## Auto-start on Login

Create a systemd user service or add to your startup:

```bash
mkdir -p ~/.config/autostart
cat > ~/.config/autostart/keybind-ubuntu.desktop <<EOF
[Desktop Entry]
Type=Application
Name=Keybind Ubuntu
Exec=/home/YOUR_USER/keybind-ubuntu/keybind.py
Hidden=false
NoDisplay=false
X-GNOME-Autostart-enabled=true
EOF
```

## License

MIT
