#!/usr/bin/env python3
"""
Keybind Ubuntu - Tray Daemon with GUI.
Runs as a background tray application with settings.
"""

import json
import subprocess
import sys
from pathlib import Path

from PyQt6.QtWidgets import (
    QApplication,
    QSystemTrayIcon,
    QMenu,
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QCheckBox,
    QMessageBox,
)
from PyQt6.QtGui import QIcon, QColor
from PyQt6.QtCore import QThread, pyqtSignal, Qt, QTimer

from keybind import load_config, parse_hotkey, key_to_name, execute_hotkey, get_key_object
from pynput.keyboard import Controller, Listener as KeyListener

CONFIG_PATH = Path.home() / ".keybind" / "config.json"

class KeybindDaemon(QThread):
    """Background thread that listens for hotkeys."""
    
    triggered = pyqtSignal(str)  # emits hotkey name
    
    def __init__(self):
        super().__init__()
        self.is_running = True
        self.config = load_config()
        self.hotkey_map = {}
        self.pressed = set()
        self.load_hotkeys()
    
    def load_hotkeys(self):
        """Load hotkeys from config."""
        profiles = self.config.get("profiles", {})
        default = self.config.get("default_profile")
        
        if default and default in profiles:
            profile = profiles[default]
        else:
            profile = next(iter(profiles.values())) if profiles else {}
        
        self.hotkey_map = {}
        for hotkey_text, hotkey_cfg in profile.get("hotkeys", {}).items():
            self.hotkey_map[frozenset(parse_hotkey(hotkey_text))] = (hotkey_text, hotkey_cfg)
    
    def on_press(self, key):
        if not self.is_running:
            return
        
        name = key_to_name(key)
        if name:
            self.pressed.add(name)
            
            for hotkey_set, (hotkey_text, hotkey_cfg) in self.hotkey_map.items():
                if hotkey_set.issubset(self.pressed):
                    self.triggered.emit(hotkey_text)
                    execute_hotkey(hotkey_cfg)
                    self.pressed.clear()
                    break
    
    def on_release(self, key):
        name = key_to_name(key)
        if name:
            self.pressed.discard(name)
    
    def run(self):
        """Main loop."""
        with KeyListener(on_press=self.on_press, on_release=self.on_release) as listener:
            listener.join()
    
    def stop(self):
        """Stop the daemon."""
        self.is_running = False

class SettingsWindow(QMainWindow):
    """Settings window for the tray app."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Keybind Ubuntu - Settings")
        self.resize(500, 300)
        
        central = QWidget()
        layout = QVBoxLayout()
        
        # Title
        title = QLabel("Keybind Ubuntu Settings")
        title.setStyleSheet("font-size: 16px; font-weight: bold;")
        layout.addWidget(title)
        
        # Load config
        self.config = load_config()
        profiles = self.config.get("profiles", {})
        default_name = self.config.get("default_profile", "default")
        profile = profiles.get(default_name, {})
        hotkeys = profile.get("hotkeys", {})
        
        # Hotkeys info
        info_layout = QHBoxLayout()
        info_layout.addWidget(QLabel(f"Profile: {default_name}"))
        info_layout.addWidget(QLabel(f"Hotkeys: {len(hotkeys)}"))
        layout.addLayout(info_layout)
        
        # List hotkeys
        layout.addWidget(QLabel("Active hotkeys:"))
        for hotkey in hotkeys:
            layout.addWidget(QLabel(f"  • {hotkey}"))
        
        # Auto-start checkbox
        auto_start_path = Path.home() / ".config" / "autostart" / "keybind-ubuntu-tray.desktop"
        self.autostart_check = QCheckBox("Auto-start on login")
        self.autostart_check.setChecked(auto_start_path.exists())
        self.autostart_check.stateChanged.connect(lambda: self.toggle_autostart(auto_start_path))
        layout.addWidget(self.autostart_check)
        
        # Buttons
        button_layout = QHBoxLayout()
        edit_btn = QPushButton("Edit Hotkeys")
        edit_btn.clicked.connect(self.edit_hotkeys)
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.close)
        button_layout.addWidget(edit_btn)
        button_layout.addWidget(close_btn)
        layout.addLayout(button_layout)
        
        layout.addStretch()
        central.setLayout(layout)
        self.setCentralWidget(central)
    
    def toggle_autostart(self, path):
        """Toggle auto-start."""
        path.parent.mkdir(parents=True, exist_ok=True)
        
        if self.autostart_check.isChecked():
            script = Path(__file__).resolve()
            content = (
                "[Desktop Entry]\n"
                "Type=Application\n"
                "Name=Keybind Ubuntu\n"
                "Comment=Keyboard automation tool\n"
                f"Exec={sys.executable} {script}\n"
                "Hidden=false\n"
                "NoDisplay=false\n"
                "X-GNOME-Autostart-enabled=true\n"
            )
            path.write_text(content, encoding="utf-8")
            QMessageBox.information(self, "Success", "Auto-start enabled.")
        else:
            if path.exists():
                path.unlink()
            QMessageBox.information(self, "Success", "Auto-start disabled.")
    
    def edit_hotkeys(self):
        """Launch GUI editor."""
        try:
            subprocess.Popen([sys.executable, "gui.py"])
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to launch GUI: {e}")

class TrayApp(QApplication):
    """Main tray application."""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Create tray icon
        self.tray_icon = QSystemTrayIcon(self)
        self.setWindowIcon(self.create_icon())
        self.tray_icon.setIcon(self.create_icon())
        
        # Create menu
        self.tray_menu = QMenu()
        self.tray_menu.addAction("Settings", self.show_settings)
        self.tray_menu.addAction("Open GUI", self.open_gui)
        self.tray_menu.addSeparator()
        self.tray_menu.addAction("Quit", self.quit_app)
        
        self.tray_icon.setContextMenu(self.tray_menu)
        self.tray_icon.show()
        
        # Start daemon
        self.daemon = KeybindDaemon()
        self.daemon.triggered.connect(self.on_hotkey_triggered)
        self.daemon.start()
        
        # Settings window
        self.settings_window = None
        
        # Status label
        self.status_label = "Ready"
        self.update_tooltip()
        
        # Auto-update tooltip
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_tooltip)
        self.timer.start(2000)
    
    def create_icon(self):
        """Create a simple icon."""
        from PyQt6.QtGui import QPixmap, QPainter
        pixmap = QPixmap(64, 64)
        pixmap.fill(QColor(200, 200, 200))
        painter = QPainter(pixmap)
        painter.drawText(10, 50, "⌨")
        painter.end()
        return QIcon(pixmap)
    
    def update_tooltip(self):
        """Update tray tooltip."""
        config = load_config()
        default = config.get("default_profile", "default")
        profiles = config.get("profiles", {})
        profile = profiles.get(default, {})
        hotkeys_count = len(profile.get("hotkeys", {}))
        self.tray_icon.setToolTip(f"Keybind Ubuntu\nProfile: {default}\nHotkeys: {hotkeys_count}\n{self.status_label}")
    
    def on_hotkey_triggered(self, hotkey_name):
        """Handle hotkey trigger."""
        self.status_label = f"Triggered: {hotkey_name}"
        self.update_tooltip()
        self.tray_icon.showMessage(
            "Keybind Ubuntu",
            f"Hotkey triggered: {hotkey_name}",
            QSystemTrayIcon.MessageIcon.Information,
            2000
        )
    
    def show_settings(self):
        """Show settings window."""
        if self.settings_window is None:
            self.settings_window = SettingsWindow()
        self.settings_window.show()
        self.settings_window.raise_()
        self.settings_window.activateWindow()
    
    def open_gui(self):
        """Open the hotkey editor GUI."""
        try:
            subprocess.Popen([sys.executable, str(Path(__file__).parent / "gui.py")])
        except Exception as e:
            self.tray_icon.showMessage(
                "Error",
                f"Failed to launch GUI: {e}",
                QSystemTrayIcon.MessageIcon.Critical,
                2000
            )
    
    def quit_app(self):
        """Quit the application."""
        self.daemon.stop()
        self.quit()

def main():
    app = TrayApp(sys.argv)
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
