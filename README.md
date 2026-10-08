# Keybind Ubuntu - Keyboard Automation with System Tray

A lightweight AutoHotkey-style keyboard automation tool for Ubuntu with **system tray integration**.

## Features

- 🎯 **Global Hotkeys** - Trigger actions from anywhere with custom keyboard shortcuts
- 🔐 **Credential Auto-Fill** - Multiple profiles for different websites/apps
- 🖥️ **GUI Configuration** - Map hotkeys visually, no config file editing needed
- 📋 **Multiple Profiles** - Different shortcuts for work, personal, banking, etc.
- 🚀 **Auto-Start on Login** - Runs automatically with your system
- 🎨 **System Tray Icon** - Minimize to tray, quick access to settings
- ⚡ **Lightweight** - Minimal resource usage
- 🔄 **Action Macros** - Type text, press keys, click, move mouse, etc.

## Requirements

- Ubuntu 20.04+
- Python 3.10+
- X11 session (recommended)
- pynput
- PyQt6

## Installation

```bash
chmod +x install.sh
./install.sh
```

## Usage

### Quick Start with System Tray (Recommended)

```bash
source .venv/bin/activate
python3 tray_daemon.py &
```

This runs the app in the system tray with:
- Settings menu
- Hotkey editor
- Auto-start toggle
- Status notifications

### GUI Configuration

```bash
source .venv/bin/activate
python3 gui.py
```

Create profiles, add hotkeys, and configure actions.

### Run Daemon Directly

```bash
source .venv/bin/activate
python3 keybind.py
```

## Configuration

Hotkeys are stored in `~/.keybind/config.json`:

```json
{
  "default_profile": "quick_logins",
  "profiles": {
    "quick_logins": {
      "name": "Quick Logins",
      "hotkeys": {
        "ctrl+alt+f": {
          "app_filter": "firefox",
          "actions": [
            {"type": "type", "text": "user@example.com"},
            {"type": "key", "key": "tab"},
            {"type": "delay", "duration": 0.2},
            {"type": "type", "text": "Password123"},
            {"type": "key", "key": "enter"}
          ],
          "delay": 0.1
        }
      }
    }
  }
}
```

## Supported Actions

| Action | Example | Description |
|--------|---------|-------------|
| `type` | `{"type": "type", "text": "hello"}` | Type text |
| `key` | `{"type": "key", "key": "tab"}` | Press a key |
| `delay` | `{"type": "delay", "duration": 0.5}` | Wait N seconds |
| `click` | `{"type": "click", "x": 100, "y": 200}` | Click at coordinates |
| `move` | `{"type": "move", "x": 500, "y": 500}` | Move mouse |
| `launch` | `{"type": "launch", "app": "firefox"}` | Launch app |

## Supported Keys

- Modifiers: `ctrl`, `alt`, `shift`, `super`
- Navigation: `up`, `down`, `left`, `right`, `home`, `end`, `pageup`, `pagedown`
- Editing: `enter`, `tab`, `backspace`, `delete`, `escape`
- Function: `f1` through `f20`
- System: `print`, `pause`, `scrolllock`

## System Tray Features

- **Settings** - View active profile and hotkeys
- **Edit Hotkeys** - Launch GUI editor
- **Auto-start** - Enable/disable auto-start on login
- **Status** - See last triggered hotkey
- **Quit** - Stop the daemon

## Auto-Start on Login

Enable via:

1. System tray > Settings > Check "Auto-start on login"

or

2. GUI > Check "Auto-start on login"

This creates a `.desktop` file in `~/.config/autostart/`

## Security & Privacy

⚠️ **Important**:
- Credentials are stored in JSON files. Encrypt them or use your system keyring for sensitive data.
- Never share your config files.
- This tool is for convenience, not security.

## Troubleshooting

**Hotkeys don't work?**
- Ensure app is running: `python3 tray_daemon.py`
- Check if hotkey conflicts with system shortcuts
- Try a different hotkey combination
- Make sure you're using X11: `echo $XDG_SESSION_TYPE`

**GUI won't launch?**
- Install PyQt6: `pip install PyQt6`

**Tray icon doesn't show?**
- On some desktops, the tray might be hidden. Right-click the panel to show it.

## Files

- `keybind.py` - Core daemon that listens for hotkeys
- `tray_daemon.py` - System tray wrapper with GUI integration
- `gui.py` - Hotkey editor and configuration tool
- `config.json` - Configuration file (auto-generated)
- `install.sh` - Setup script
- `requirements.txt` - Python dependencies

## License

MIT

## Examples

### Auto-fill Gmail

Hotkey: `ctrl+alt+g`

```json
{
  "app_filter": "google-chrome",
  "actions": [
    {"type": "type", "text": "your_email@gmail.com"},
    {"type": "key", "key": "tab"},
    {"type": "type", "text": "your_password"},
    {"type": "key", "key": "enter"}
  ]
}
```

### Open Terminal

Hotkey: `ctrl+alt+t`

```json
{
  "actions": [
    {"type": "launch", "app": "gnome-terminal"}
  ]
}
```

### Click and Type

Hotkey: `ctrl+alt+c`

```json
{
  "actions": [
    {"type": "click", "x": 500, "y": 300},
    {"type": "delay", "duration": 0.2},
    {"type": "type", "text": "Hello World"}
  ]
}
```

## Contributing

Contributions welcome! Submit PRs for:
- Additional action types
- Better GUI features
- Window-specific filtering
- More sophisticated automation
