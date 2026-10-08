# Keybind Ubuntu

A lightweight keyboard automation app for Ubuntu focused on browser login workflows.

## Features
- Global hotkeys
- Multiple profiles
- App filtering by active window name
- Type login credentials and send keys
- Delay, click, move mouse, launch apps
- Tray icon support
- GUI configuration editor
- Auto-start on Ubuntu login

## Requirements
- Ubuntu 20.04+
- Python 3.10+
- X11 session recommended
- pynput
- PyQt6

## Installation
```bash
chmod +x install.sh
./install.sh
```

## Run
```bash
source .venv/bin/activate
python3 tray_daemon.py
```

Or open the GUI:
```bash
source .venv/bin/activate
python3 gui.py
```

## Example config
```json
{
  "default_profile": "browser_logins",
  "profiles": {
    "browser_logins": {
      "name": "Browser Logins",
      "hotkeys": {
        "ctrl+alt+f": {
          "app_filter": "firefox",
          "actions": [
            { "type": "type", "text": "user@example.com" },
            { "type": "key", "key": "tab" },
            { "type": "delay", "duration": 0.2 },
            { "type": "type", "text": "Password123" },
            { "type": "key", "key": "enter" }
          ],
          "delay": 0.1
        }
      }
    }
  }
}
```

## Security note
Credentials are stored in plain JSON for simplicity. For real usage, protect them with a password manager or OS keyring.

## License
MIT
