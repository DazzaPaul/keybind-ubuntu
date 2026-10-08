#!/usr/bin/env python3
"""Main keyboard automation daemon for Ubuntu (like AutoHotkey).

Listens for global hotkeys and executes configured actions.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
import time
from pathlib import Path
from typing import Any, Callable

from pynput.keyboard import Controller, Key, KeyCode, Listener
from pynput.mouse import Button, Controller as MouseController

CONFIG_PATH = Path.home() / ".keybind" / "config.json"
LOG_PATH = Path.home() / ".keybind" / "keybind.log"

# Key mapping for hotkey parsing
KEY_MAP = {
    "ctrl": Key.ctrl,
    "control": Key.ctrl,
    "alt": Key.alt,
    "shift": Key.shift,
    "super": Key.cmd,
    "cmd": Key.cmd,
    "meta": Key.cmd,
    "win": Key.cmd,
    "enter": Key.enter,
    "return": Key.enter,
    "tab": Key.tab,
    "space": Key.space,
    "esc": Key.esc,
    "escape": Key.esc,
    "up": Key.up,
    "down": Key.down,
    "left": Key.left,
    "right": Key.right,
    "home": Key.home,
    "end": Key.end,
    "pageup": Key.page_up,
    "pagedown": Key.page_down,
    "delete": Key.delete,
    "backspace": Key.backspace,
    "insert": Key.insert,
    "printscreen": Key.print_screen,
    "print": Key.print_screen,
    "pause": Key.pause,
    "scrolllock": Key.scroll_lock,
}


def log_message(message: str) -> None:
    """Write message to log file."""
    LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
    with open(LOG_PATH, "a", encoding="utf-8") as f:
        f.write(f"[{timestamp}] {message}\n")
    print(message)


def load_config() -> dict:
    """Load configuration from JSON file."""
    if not CONFIG_PATH.exists():
        log_message(f"❌ Config not found: {CONFIG_PATH}")
        log_message("   Run: python3 gui.py to create a profile")
        sys.exit(1)

    try:
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            config = json.load(f)
        log_message(f"✅ Loaded config from {CONFIG_PATH}")
        return config
    except json.JSONDecodeError as e:
        log_message(f"❌ Invalid JSON in config: {e}")
        sys.exit(1)
    except Exception as e:
        log_message(f"❌ Error loading config: {e}")
        sys.exit(1)


def parse_hotkey(hotkey_str: str) -> list[str]:
    """Parse hotkey string like 'ctrl+alt+f' into list of key names."""
    if not isinstance(hotkey_str, str):
        return []
    parts = [p.strip().lower() for p in hotkey_str.split("+")]
    return [p for p in parts if p]


def key_to_name(key) -> str:
    """Convert pynput key to string name."""
    try:
        if isinstance(key, KeyCode):
            if key.char:
                return key.char.lower()
            return ""
        key_name = key.name if hasattr(key, "name") else str(key)
        key_name = key_name.lower().replace("key.", "")
        return key_name
    except:
        return ""


def get_active_window_name() -> str:
    """Get the currently active window's name/class."""
    try:
        result = subprocess.run(
            ["xdotool", "getactivewindow", "getwindowname"],
            capture_output=True,
            text=True,
            timeout=1,
        )
        return result.stdout.strip().lower()
    except:
        return ""


def execute_action(action: dict) -> bool:
    """Execute a single action. Returns True on success."""
    keyboard = Controller()
    mouse = MouseController()

    try:
        action_type = action.get("type", "")

        if action_type == "type":
            text = str(action.get("text", ""))
            keyboard.type(text)
            log_message(f"  → Typed: {len(text)} characters")
            return True

        elif action_type == "key":
            key_name = action.get("key", "").lower().strip()
            
            # Try to get key from KEY_MAP
            if key_name in KEY_MAP:
                key = KEY_MAP[key_name]
            # Try function keys
            elif key_name.startswith("f") and len(key_name) > 1:
                try:
                    fn = int(key_name[1:])
                    if 1 <= fn <= 20:
                        key = getattr(Key, f"f{fn}")
                    else:
                        return False
                except (ValueError, AttributeError):
                    return False
            # Single character
            elif len(key_name) == 1:
                key = KeyCode(char=key_name)
            else:
                log_message(f"  ⚠️ Unknown key: {key_name}")
                return False

            keyboard.press(key)
            keyboard.release(key)
            log_message(f"  → Pressed: {key_name}")
            return True

        elif action_type == "delay":
            duration = float(action.get("duration", 0.5))
            time.sleep(duration)
            log_message(f"  → Delayed: {duration}s")
            return True

        elif action_type == "click":
            button_name = action.get("button", "left").lower()
            x = int(action.get("x", 0))
            y = int(action.get("y", 0))

            button = Button.left if button_name == "left" else Button.right
            mouse.position = (x, y)
            mouse.click(button)
            log_message(f"  → Clicked {button_name} at ({x}, {y})")
            return True

        elif action_type == "move":
            x = int(action.get("x", 0))
            y = int(action.get("y", 0))
            mouse.position = (x, y)
            log_message(f"  → Moved mouse to ({x}, {y})")
            return True

        elif action_type == "launch":
            app = action.get("app", "").strip()
            if app:
                subprocess.Popen([app], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                log_message(f"  → Launched: {app}")
            return True

        elif action_type == "hotstring":
            trigger = action.get("trigger", "")
            replace = action.get("replace", "")
            # This would require tracking typed characters, skipping for now
            log_message(f"  ⚠️ Hotstring not yet implemented")
            return False

        else:
            log_message(f"  ⚠️ Unknown action type: {action_type}")
            return False

    except Exception as e:
        log_message(f"  ❌ Error executing action: {e}")
        return False


def execute_hotkey(hotkey_config: dict) -> None:
    """Execute all actions for a hotkey."""
    try:
        # Check app filter if present
        app_filter = hotkey_config.get("app_filter", "").lower()
        if app_filter:
            active_window = get_active_window_name()
            if app_filter not in active_window:
                log_message(f"⏭️  Skipping (app filter '{app_filter}' not matched)")
                return

        actions = hotkey_config.get("actions", [])
        if not actions:
            log_message("⚠️ No actions configured for this hotkey")
            return

        log_message(f"🎯 Executing {len(actions)} action(s)...")
        default_delay = float(hotkey_config.get("delay", 0.1))

        for i, action in enumerate(actions, 1):
            if not execute_action(action):
                log_message(f"⚠️ Action {i} failed")
                return
            if i < len(actions):
                time.sleep(default_delay)

        log_message("✅ Hotkey executed successfully")
    except Exception as e:
        log_message(f"❌ Error in execute_hotkey: {e}")


def main() -> int:
    """Main event loop."""
    config = load_config()

    # Get default profile
    default_profile_name = config.get("default_profile")
    profiles = config.get("profiles", {})

    if not profiles:
        log_message("❌ No profiles configured")
        return 1

    if default_profile_name and default_profile_name in profiles:
        profile_name = default_profile_name
        profile = profiles[default_profile_name]
    else:
        profile_name = next(iter(profiles))
        profile = profiles[profile_name]

    hotkeys_config = profile.get("hotkeys", {})
    if not hotkeys_config:
        log_message(f"❌ No hotkeys in profile '{profile_name}'")
        return 1

    log_message("\n" + "=" * 60)
    log_message("🎹 Keybind Ubuntu - Daemon Started")
    log_message(f"📋 Profile: {profile_name}")
    log_message(f"🔑 Hotkeys: {len(hotkeys_config)}")
    log_message("=" * 60 + "\n")

    for hotkey_str in hotkeys_config.keys():
        log_message(f"  • {hotkey_str}")
    log_message("\nListening for hotkeys... Press Ctrl+C to stop.\n")

    # Build hotkey set map
    hotkey_map: dict[frozenset, dict] = {}
    for hotkey_str, hotkey_config in hotkeys_config.items():
        parts = parse_hotkey(hotkey_str)
        if parts:
            hotkey_map[frozenset(parts)] = hotkey_config

    pressed_keys: set[str] = set()

    def on_press(key):
        key_name = key_to_name(key)
        if key_name:
            pressed_keys.add(key_name)

            # Check all hotkeys
            for hotkey_set, hotkey_config in hotkey_map.items():
                if hotkey_set.issubset(pressed_keys):
                    log_message(f"\n🔓 Hotkey triggered: {' + '.join(sorted(hotkey_set))}")
                    execute_hotkey(hotkey_config)
                    pressed_keys.clear()
                    break

    def on_release(key):
        key_name = key_to_name(key)
        if key_name:
            pressed_keys.discard(key_name)

    try:
        with Listener(on_press=on_press, on_release=on_release) as listener:
            listener.join()
    except KeyboardInterrupt:
        log_message("\n👋 Daemon stopped")
        return 0
    except Exception as e:
        log_message(f"❌ Fatal error: {e}")
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
