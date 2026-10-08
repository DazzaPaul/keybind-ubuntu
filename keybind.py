#!/usr/bin/env python3
"""Global keyboard shortcut auto-fill tool for Ubuntu (like AutoHotkey for Windows).

This script listens for a hotkey and types a configured username and password
into the currently focused input field.
"""

from __future__ import annotations

import json
import sys
import time
from pathlib import Path

from pynput.keyboard import Controller, Key, KeyCode, Listener

CONFIG_PATH = Path(__file__).with_name("credentials.json")

# Map config hotkey names to pynput Key objects
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
}


def load_config() -> dict:
    """Load configuration from credentials.json."""
    if not CONFIG_PATH.exists():
        print(f"❌ Config file not found: {CONFIG_PATH}")
        print(f"   Create credentials.json first using the example in README.md")
        sys.exit(1)

    try:
        with CONFIG_PATH.open("r", encoding="utf-8") as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        print(f"❌ Invalid JSON in credentials.json: {e}")
        sys.exit(1)

    if not data.get("profiles"):
        print("❌ No 'profiles' found in credentials.json")
        sys.exit(1)

    return data


def parse_hotkey(hotkey_str: str) -> list:
    """Parse hotkey string like 'ctrl+alt+f' into list of key names."""
    if not isinstance(hotkey_str, str):
        return []
    
    parts = [p.strip().lower() for p in hotkey_str.split("+")]
    return [p for p in parts if p]


def get_pynput_key(key_name: str) -> Key | KeyCode | None:
    """Convert key name to pynput Key object."""
    key_name = key_name.lower().strip()
    
    # Check KEY_MAP first
    if key_name in KEY_MAP:
        return KEY_MAP[key_name]
    
    # Try function keys
    if key_name.startswith("f") and len(key_name) > 1:
        try:
            fn = int(key_name[1:])
            if 1 <= fn <= 20:
                return getattr(Key, f"f{fn}")
        except (ValueError, AttributeError):
            pass
    
    # Single character
    if len(key_name) == 1 and key_name.isalpha():
        return KeyCode(char=key_name)
    
    return None


def key_to_name(key) -> str:
    """Convert pynput key object back to name string."""
    try:
        if isinstance(key, KeyCode):
            if key.char:
                return key.char.lower()
            return ""
        
        # It's a Key enum
        key_name = key.name if hasattr(key, "name") else str(key)
        key_name = key_name.lower().replace("key.", "")
        return key_name
    except:
        return ""


def trigger_profile(profile: dict) -> None:
    """Type the configured username and password."""
    keyboard = Controller()
    
    username = str(profile.get("username", "")).strip()
    password = str(profile.get("password", "")).strip()
    delay = float(profile.get("delay", 0.1))
    tab_after_user = profile.get("tab_after_username", True)
    enter_after_pass = profile.get("enter_after_password", False)
    
    if not username and not password:
        print("⚠️  Profile has no username/password configured")
        return
    
    try:
        # Type username
        if username:
            time.sleep(delay)
            keyboard.type(username)
            print(f"✓ Typed username")
        
        # Press Tab if configured
        if tab_after_user and (username and password):
            time.sleep(delay)
            keyboard.press(Key.tab)
            keyboard.release(Key.tab)
            print(f"✓ Pressed Tab")
        
        # Type password
        if password:
            time.sleep(delay)
            keyboard.type(password)
            print(f"✓ Typed password")
        
        # Press Enter if configured
        if enter_after_pass:
            time.sleep(delay)
            keyboard.press(Key.enter)
            keyboard.release(Key.enter)
            print(f"✓ Pressed Enter")
    except Exception as e:
        print(f"❌ Error typing: {e}")


def main() -> int:
    """Main event loop listening for hotkeys."""
    config = load_config()
    
    # Get default profile
    default_name = config.get("default_profile")
    profiles = config.get("profiles", {})
    
    if not profiles:
        print("❌ No profiles configured")
        return 1
    
    if default_name and default_name in profiles:
        profile_name = default_name
        profile = profiles[default_name]
    else:
        profile_name = next(iter(profiles))
        profile = profiles[profile_name]
    
    hotkey_str = profile.get("hotkey", "ctrl+alt+f")
    hotkey_parts = parse_hotkey(hotkey_str)
    
    if not hotkey_parts:
        print(f"❌ Invalid hotkey format: {hotkey_str}")
        return 1
    
    # Convert to pynput keys
    hotkey_keys = set()
    for part in hotkey_parts:
        key = get_pynput_key(part)
        if key:
            hotkey_keys.add(part)
        else:
            print(f"⚠️  Unknown key: {part}")
    
    print(f"\n🎯 Keybind Ubuntu started")
    print(f"📌 Hotkey: {hotkey_str}")
    print(f"👤 Profile: {profile_name}")
    print(f"\nListening... Press your hotkey to trigger auto-fill.\nPress Ctrl+C to exit.\n")
    
    pressed_keys = set()
    
    def on_press(key):
        try:
            key_name = key_to_name(key)
            if key_name:
                pressed_keys.add(key_name)
                
                # Check if all hotkey parts are pressed
                if hotkey_keys.issubset(pressed_keys):
                    print(f"\n🔓 Hotkey triggered!")
                    trigger_profile(profile)
                    pressed_keys.clear()
        except Exception as e:
            print(f"Error in on_press: {e}")
    
    def on_release(key):
        try:
            key_name = key_to_name(key)
            if key_name:
                pressed_keys.discard(key_name)
        except Exception as e:
            print(f"Error in on_release: {e}")
    
    try:
        with Listener(on_press=on_press, on_release=on_release) as listener:
            listener.join()
    except KeyboardInterrupt:
        print("\n\n👋 Keybind Ubuntu stopped")
        return 0
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
