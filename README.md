# Keybind Ubuntu

A lightweight keyboard shortcut tool for Ubuntu that fills usernames and passwords automatically so you do not have to type them repeatedly.

This project is intentionally small and focused on a single use case:
- press a hotkey
- the app types your username and password into the currently focused field
- optionally tabs between fields and presses Enter

## What it does

- listens for a global keyboard shortcut such as `Ctrl+Alt+F`
- types a configured username into the current text field
- tabs to the next field
- types the configured password
- optionally presses Enter

## Install

```bash
cd keybind-ubuntu
chmod +x install.sh
./install.sh
```

## Run

```bash
source .venv/bin/activate
python3 keybind.py
```

You can also start it directly via:

```bash
./install.sh
```

## Configuration

Edit `credentials.json` before starting the app.

Example:

```json
{
  "default_profile": "work",
  "profiles": {
    "work": {
      "hotkey": "ctrl+alt+f",
      "username": "alice@example.com",
      "password": "SuperSecretPassword123",
      "tab_after_username": true,
      "enter_after_password": false,
      "delay": 0.1
    }
  }
}
```

### Notes

- Use a hotkey that is not already used elsewhere on Ubuntu.
- This is designed to work with X11 sessions.
- Save credentials locally only if you understand the security tradeoff.
- For production use, prefer a proper password manager or OS keyring.

## Security note

This app stores credentials in a plain JSON file for simplicity. That is convenient but not secure for production use. For real-world work, consider storing secrets in your OS keyring or in a dedicated password manager.

## Requirements

- Ubuntu 20.04+ or similar Linux desktop
- Python 3.10+
- X11 session
- `pynput`

## Troubleshooting

If the hotkey does not trigger:

- make sure the app is running in your active desktop session
- ensure you are using X11, not Wayland-only sessions
- try a different hotkey
- check that the terminal is not swallowing the hotkey combination
