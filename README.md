# Keybind Ubuntu - AutoHotkey for Linux

A full-featured keyboard automation tool for Ubuntu with GUI configuration. Like AutoHotkey for Windows, but built for Linux.

## Features

- 🎯 **Global Hotkeys** - Trigger actions from anywhere with custom keyboard shortcuts
- 🔐 **Credential Auto-Fill** - Multiple profiles for different websites/apps
- 🖥️ **GUI Configuration** - Map hotkeys visually, no config file editing needed
- 📋 **Multiple Profiles** - Different shortcuts for work, personal, banking, etc.
- 🚀 **Auto-Start on Login** - Runs automatically with your system
- ⚡ **Lightweight** - Minimal resource usage
- 🔄 **Action Macros** - Type text, press keys, click, move mouse, etc.

## What It Can Do

- Type usernames and passwords automatically
- Trigger different actions based on active window
- Simulate keyboard presses (Tab, Enter, arrow keys, etc.)
- Mouse movements and clicks
- Launch applications
- Insert text snippets

## Installation

```bash
git clone https://github.com/DazzaPaul/keybind-ubuntu.git
cd keybind-ubuntu
chmod +x install.sh
./install.sh
```

## Usage

### GUI Configuration (Recommended)

```bash
source .venv/bin/activate
python3 gui.py
```

This opens the graphical interface where you can:
- Create/edit profiles
- Map hotkeys visually
- Configure actions for each hotkey
- Test hotkeys in real-time
- Save and auto-apply settings

### Command Line

```bash
source .venv/bin/activate
python3 keybind.py
```

Press your configured hotkeys to trigger actions.

## Profile Structure

Each profile can have multiple hotkeys, and each hotkey can perform multiple actions:

```json
{
  "default_profile": "work",
  "profiles": {
    "work": {
      "name": "Work Profiles",
      "hotkeys": {
        "ctrl+alt+f": {
          "app_filter": "firefox",
          "actions": [
            {"type": "type", "text": "work_email@company.com"},
            {"type": "key", "key": "tab"},
            {"type": "type", "text": "WorkPassword123"},
            {"type": "key", "key": "enter"}
          ],
          "delay": 0.1
        },
        "ctrl+alt+g": {
          "app_filter": "gmail",
          "actions": [
            {"type": "type", "text": "personal_email@gmail.com"},
            {"type": "key", "key": "tab"},
            {"type": "type", "text": "GmailPassword456"},
            {"type": "key", "key": "enter"}
          ]
        }
      }
    },
    "personal": {
      "name": "Personal Profiles",
      "hotkeys": {
        "ctrl+alt+p": {
          "actions": [
            {"type": "type", "text": "my_username"},
            {"type": "key", "key": "tab"},
            {"type": "type", "text": "PersonalPass789"}
          ]
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
| `key` | `{"type": "key", "key": "tab"}` | Press a key (tab, enter, etc.) |
| `delay` | `{"type": "delay", "duration": 0.5}` | Wait N seconds |
| `click` | `{"type": "click", "button": "left", "x": 100, "y": 200}` | Click at coordinates |
| `move` | `{"type": "move", "x": 500, "y": 500}` | Move mouse |
| `launch` | `{"type": "launch", "app": "firefox"}` | Launch application |
| `hotstring` | `{"type": "hotstring", "trigger": "@@", "replace": "myemail@example.com"}` | Text expansion |

## Supported Keys

- Modifiers: `ctrl`, `alt`, `shift`, `super` (Windows key)
- Navigation: `up`, `down`, `left`, `right`, `home`, `end`, `pageup`, `pagedown`
- Editing: `enter`, `tab`, `backspace`, `delete`, `escape`
- Function: `f1` through `f20`
- System: `print`, `pause`, `scrolllock`

## Auto-Start on Login

After installation, the app can be set to auto-start:

```bash
# Via GUI settings (recommended)
python3 gui.py  # Check "Auto-start on login"

# Or manually:
mkdir -p ~/.config/autostart
cat > ~/.config/autostart/keybind-ubuntu.desktop <<EOF
[Desktop Entry]
Type=Application
Name=Keybind Ubuntu
Comment=Keyboard automation tool
Exec=/home/YOUR_USER/keybind-ubuntu/.venv/bin/python3 /home/YOUR_USER/keybind-ubuntu/keybind.py
Hidden=false
NoDisplay=false
X-GNOME-Autostart-enabled=true
EOF
chmod +x ~/.config/autostart/keybind-ubuntu.desktop
```

## Requirements

- Ubuntu 20.04+
- Python 3.10+
- X11 session (not Wayland-only)
- PyQt6 (for GUI)
- pynput (for hotkey listening)
- pyperclip (for clipboard operations)

## Security & Privacy

⚠️ **Important**: 
- Credentials are stored in JSON files. Encrypt them or use your system keyring for sensitive data.
- Never share your config files.
- Use strong, unique passwords in practice—this tool is for convenience, not security.

## Troubleshooting

**Hotkeys don't work?**
- Ensure app is running: `python3 keybind.py`
- Check if hotkey conflicts with system shortcuts
- Try a different hotkey combination
- Make sure you're using X11: `echo $XDG_SESSION_TYPE`

**GUI won't launch?**
- Install PyQt6: `pip install PyQt6`
- Check Qt libraries: `sudo apt install libqt6core6`

**Credential auto-fill fails?**
- Ensure the hotkey is correctly mapped
- Check delay settings (may need to increase)
- Verify app_filter matches the window title if using window-specific triggers

## GUI Screenshots

The GUI provides:
- Profile manager
- Hotkey mapper (press key to record)
- Action builder (add type, key press, delays, etc.)
- Action test panel
- Auto-start toggle
- Logging viewer

## License

MIT

## Contributing

Contributions welcome! Please submit PRs for:
- Additional action types
- Better GUI features
- Window-specific filtering
- More sophisticated automation
