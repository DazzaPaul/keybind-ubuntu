#!/usr/bin/env python3
"""
Keybind Ubuntu - global hotkey automation for Ubuntu.
Supports multiple profiles and app filtering.
"""

from __future__ import annotations

import json
import subprocess
import sys
import time
from pathlib import Path

from pynput.keyboard import Controller, Key, KeyCode, Listener
from pynput.mouse import Button, Controller as MouseController

CONFIG_PATH = Path.home() / ".keybind" / "config.json"

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


def ensure_config():
    CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
    if not CONFIG_PATH.exists():
        config = {
            "default_profile": "default",
            "profiles": {
                "default": {
                    "name": "Default",
                    "hotkeys": {
                        "ctrl+alt+f": {
                            "actions": [
                                {"type": "type", "text": "user@example.com"},
                                {"type": "key", "key": "tab"},
                                {"type": "delay", "duration": 0.2},
                                {"type": "type", "text": "password123"},
                                {"type": "key", "key": "enter"},
                            ],
                            "delay": 0.1,
                        }
                    }
                }
            }
        }
        with open(CONFIG_PATH, "w", encoding="utf-8") as f:
            json.dump(config, f, indent=2)
        print(f"Created config at {CONFIG_PATH}")


def load_config():
    ensure_config()
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def parse_hotkey(hotkey):
    if not isinstance(hotkey, str):
        return []
    return [p.strip().lower() for p in hotkey.split("+") if p.strip()]


def key_to_name(key):
    try:
        if isinstance(key, KeyCode):
            if key.char:
                return key.char.lower()
            return ""
        if hasattr(key, "name"):
            return key.name.lower().replace("key.", "")
        return str(key).lower()
    except Exception:
        return ""


def get_active_window_name():
    try:
        result = subprocess.run(
            ["xdotool", "getactivewindow", "getwindowname"],
            capture_output=True,
            text=True,
            timeout=1,
        )
        return result.stdout.strip().lower()
    except Exception:
        return ""


def get_key_object(key_name):
    key_name = key_name.lower().strip()

    if key_name in KEY_MAP:
        return KEY_MAP[key_name]

    if key_name.startswith("f") and len(key_name) > 1:
        try:
            num = int(key_name[1:])
            if 1 <= num <= 20:
                return getattr(Key, f"f{num}")
        except Exception:
            pass

    if len(key_name) == 1:
        return KeyCode(char=key_name)

    return None


def execute_action(action):
    action_type = action.get("type", "")
    keyboard = Controller()
    mouse = MouseController()

    if action_type == "type":
        keyboard.type(str(action.get("text", "")))
        return True

    if action_type == "key":
        key_name = str(action.get("key", "")).lower()
        key_obj = get_key_object(key_name)
        if key_obj is None:
            print(f"Unknown key: {key_name}")
            return False
        keyboard.press(key_obj)
        keyboard.release(key_obj)
        return True

    if action_type == "delay":
        time.sleep(float(action.get("duration", 0.2)))
        return True

    if action_type == "click":
        x = int(action.get("x", 0))
        y = int(action.get("y", 0))
        mouse.position = (x, y)
        button_name = str(action.get("button", "left")).lower()
        button = Button.left if button_name == "left" else Button.right
        mouse.click(button)
        return True

    if action_type == "move":
        x = int(action.get("x", 0))
        y = int(action.get("y", 0))
        mouse.position = (x, y)
        return True

    if action_type == "launch":
        app = str(action.get("app", "")).strip()
        if app:
            subprocess.Popen([app])
        return True

    print(f"Unsupported action type: {action_type}")
    return False


def execute_hotkey(config):
    app_filter = str(config.get("app_filter", "")).lower()
    if app_filter:
        active_name = get_active_window_name()
        if app_filter not in active_name:
            print(f"Skipping hotkey because app filter '{app_filter}' does not match active app '{active_name}'")
            return

    actions = config.get("actions", [])
    if not actions:
        print("No actions configured for this hotkey.")
        return

    default_delay = float(config.get("delay", 0.1))
    for index, action in enumerate(actions, start=1):
        ok = execute_action(action)
        if not ok:
            print(f"Action {index} failed.")
            return
        if index < len(actions):
            time.sleep(default_delay)

    print("Hotkey executed successfully.")


def main():
    config = load_config()
    profiles = config.get("profiles", {})
    if not profiles:
        print("No profiles configured.")
        return 1

    default_profile = config.get("default_profile")
    if default_profile and default_profile in profiles:
        profile = profiles[default_profile]
    else:
        profile_name = next(iter(profiles))
        profile = profiles[profile_name]

    hotkeys = profile.get("hotkeys", {})
    if not hotkeys:
        print("No hotkeys configured.")
        return 1

    hotkey_map = {}
    for hotkey_text, hotkey_cfg in hotkeys.items():
        hotkey_map[frozenset(parse_hotkey(hotkey_text))] = hotkey_cfg

    print("Keybind Ubuntu running...")
    print(f"Profile: {default_profile or next(iter(profiles))}")
    for hotkey in hotkeys:
        print(f"  - {hotkey}")

    pressed = set()

    def on_press(key):
        name = key_to_name(key)
        if not name:
            return
        pressed.add(name)

        for hotkey_set, action_config in hotkey_map.items():
            if hotkey_set.issubset(pressed):
                print(f"Triggered hotkey: {'+'.join(sorted(hotkey_set))}")
                execute_hotkey(action_config)
                pressed.clear()
                break

    def on_release(key):
        name = key_to_name(key)
        if name:
            pressed.discard(name)

    try:
        with Listener(on_press=on_press, on_release=on_release) as listener:
            listener.join()
    except KeyboardInterrupt:
        print("Stopped.")

    return 0


if __name__ == "__main__":
    sys.exit(main())
