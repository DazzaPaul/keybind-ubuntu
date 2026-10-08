#!/usr/bin/env python3
"""System tray app for Keybind Ubuntu."""

from __future__ import annotations

import subprocess
import sys

from PyQt6.QtWidgets import QApplication, QSystemTrayIcon, QMenu, QMessageBox
from PyQt6.QtGui import QIcon, QPixmap, QColor, QPainter
from PyQt6.QtCore import QTimer

from pynput.keyboard import Listener as KeyListener

from keybind import load_config, parse_hotkey, key_to_name, execute_hotkey


class TrayApp(QApplication):
    def __init__(self, args):
        super().__init__(args)

        self.tray_icon = QSystemTrayIcon(self)
        self.tray_icon.setIcon(self.create_icon())
        self.tray_icon.setVisible(True)

        menu = QMenu()
        menu.addAction("Open GUI", self.open_gui)
        menu.addAction("Settings", self.show_settings)
        menu.addSeparator()
        menu.addAction("Quit", self.quit_app)
        self.tray_icon.setContextMenu(menu)

        self.status = "Ready"
        self.pressed = set()
        self.hotkey_map = {}
        self.reload_hotkeys()

        self.listener = KeyListener(on_press=self.on_press, on_release=self.on_release)
        self.listener.start()

        self.timer = QTimer()
        self.timer.timeout.connect(self.update_tooltip)
        self.timer.start(2000)

    def create_icon(self):
        pixmap = QPixmap(64, 64)
        pixmap.fill(QColor(72, 114, 255))
        painter = QPainter(pixmap)
        painter.setPen(QColor(255, 255, 255))
        painter.drawText(18, 40, "⌨")
        painter.end()
        return QIcon(pixmap)

    def reload_hotkeys(self):
        config = load_config()
        profiles = config.get("profiles", {})
        default_profile = config.get("default_profile", "default")
        profile = profiles.get(default_profile, {})
        self.hotkey_map = {}

        for hotkey_text, hotkey_cfg in profile.get("hotkeys", {}).items():
            self.hotkey_map[frozenset(parse_hotkey(hotkey_text))] = hotkey_cfg

    def on_press(self, key):
        name = key_to_name(key)
        if not name:
            return
        self.pressed.add(name)

        for hotkey_set, hotkey_cfg in self.hotkey_map.items():
            if hotkey_set.issubset(self.pressed):
                self.status = f"Triggered: {'+'.join(sorted(hotkey_set))}"
                execute_hotkey(hotkey_cfg)
                self.pressed.clear()
                break

    def on_release(self, key):
        name = key_to_name(key)
        if name:
            self.pressed.discard(name)

    def update_tooltip(self):
        config = load_config()
        default_profile = config.get("default_profile", "default")
        profile = config.get("profiles", {}).get(default_profile, {})
        hotkeys_count = len(profile.get("hotkeys", {}))
        self.tray_icon.setToolTip(
            f"Keybind Ubuntu\nProfile: {default_profile}\nHotkeys: {hotkeys_count}\nStatus: {self.status}"
        )

    def open_gui(self):
        subprocess.Popen([sys.executable, "gui.py"])

    def show_settings(self):
        QMessageBox.information(
            None,
            "Keybind Ubuntu",
            "Use the GUI to edit profiles, hotkeys, and app filters.",
        )

    def quit_app(self):
        self.listener.stop()
        self.quit()


if __name__ == "__main__":
    app = TrayApp(sys.argv)
    sys.exit(app.exec())
