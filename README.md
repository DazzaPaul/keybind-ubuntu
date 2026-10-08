# Keybind Ubuntu

A lightweight Ubuntu automation app for browser logins and repeated desktop actions.

## Features

- global hotkeys
- multiple saved profiles
- app/window filtering
- text typing and key simulation
- delays, click, move, and launch actions
- tray icon support
- GUI configuration editor
- auto-start on login

## Requirements

- Ubuntu 20.04 or newer
- Python 3.10+
- X11 session recommended
- `xdotool` for active window detection

## Quick start

```bash
chmod +x install.sh
./install.sh
```

Then:

```bash
source .venv/bin/activate
python3 tray_daemon.py
```

Or start the configuration GUI:

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
            { "type": "type", "text": "your_email@example.com" },
            { "type": "key", "key": "tab" },
            { "type": "delay", "duration": 0.2 },
            { "type": "type", "text": "your_password_here" },
            { "type": "key", "key": "enter" }
          ],
          "delay": 0.1
        }
      }
    }
  }
}
```

## Action types

- `type`: type text
- `key`: press a key
- `delay`: wait for a number of seconds
- `click`: click at coordinates
- `move`: move mouse to coordinates
- `launch`: run an app

## Security note

This app stores credentials locally in plain JSON by default for simplicity. For real-world use, keep the file private and consider using a password manager or OS keyring.

## License

MIT
