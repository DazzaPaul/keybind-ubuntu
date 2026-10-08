#!/usr/bin/env python3
"""GUI for Keybind Ubuntu - Configure hotkeys and profiles visually."""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path
from typing import Any, Optional

from PyQt6.QtCore import Qt, QTimer, QEvent
from PyQt6.QtGui import QKeySequence
from PyQt6.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QLabel,
    QLineEdit,
    QComboBox,
    QListWidget,
    QListWidgetItem,
    QDialog,
    QSpinBox,
    QDoubleSpinBox,
    QCheckBox,
    QMessageBox,
    QTabWidget,
    QScrollArea,
    QFrame,
    QFormLayout,
    QTextEdit,
)
from pynput.keyboard import Listener as KeyListener, Key

CONFIG_PATH = Path.home() / ".keybind" / "config.json"
AUTOSTART_PATH = Path.home() / ".config" / "autostart" / "keybind-ubuntu.desktop"


def load_config() -> dict:
    """Load config or return empty template."""
    if not CONFIG_PATH.exists():
        return {
            "default_profile": "default",
            "profiles": {
                "default": {
                    "name": "Default Profile",
                    "hotkeys": {},
                }
            },
        }

    try:
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading config: {e}")
        return {}


def save_config(config: dict) -> bool:
    """Save config to JSON file."""
    try:
        CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
        with open(CONFIG_PATH, "w", encoding="utf-8") as f:
            json.dump(config, f, indent=2)
        return True
    except Exception as e:
        print(f"Error saving config: {e}")
        return False


class HotkeyRecorder(QDialog):
    """Dialog to record a hotkey by pressing keys."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Record Hotkey")
        self.setModal(True)
        self.setGeometry(100, 100, 400, 200)

        layout = QVBoxLayout()
        layout.addWidget(QLabel("Press your desired hotkey combination..."))
        layout.addWidget(QLabel("(e.g., Ctrl+Alt+F)"))

        self.hotkey_label = QLabel("Waiting...")
        self.hotkey_label.setStyleSheet("font-size: 16px; font-weight: bold; color: blue;")
        layout.addWidget(self.hotkey_label)

        self.recorded_hotkey = None
        self.pressed_keys = set()
        self.listener = KeyListener(on_press=self.on_key_press, on_release=self.on_key_release)
        self.listener.start()

        button_layout = QHBoxLayout()
        ok_btn = QPushButton("OK")
        ok_btn.clicked.connect(self.accept)
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(ok_btn)
        button_layout.addWidget(cancel_btn)

        layout.addLayout(button_layout)
        self.setLayout(layout)

    def on_key_press(self, key):
        try:
            if isinstance(key, Key):
                key_name = key.name.lower()
            else:
                key_name = key.char.lower() if key.char else str(key).lower()

            self.pressed_keys.add(key_name)
            hotkey = "+".join(sorted(self.pressed_keys))
            self.hotkey_label.setText(hotkey)
            self.recorded_hotkey = hotkey
        except:
            pass

    def on_key_release(self, key):
        try:
            if isinstance(key, Key):
                key_name = key.name.lower()
            else:
                key_name = key.char.lower() if key.char else str(key).lower()
            self.pressed_keys.discard(key_name)
        except:
            pass

    def closeEvent(self, event):
        self.listener.stop()
        super().closeEvent(event)


class ActionEditor(QDialog):
    """Dialog to edit an action."""

    def __init__(self, action: dict = None, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Edit Action")
        self.setModal(True)
        self.setGeometry(100, 100, 500, 400)
        self.action = action or {}

        layout = QFormLayout()

        # Action type
        self.type_combo = QComboBox()
        self.type_combo.addItems(["type", "key", "delay", "click", "move", "launch"])
        self.type_combo.currentTextChanged.connect(self.update_fields)
        layout.addRow("Action Type:", self.type_combo)

        # Text field (for type action)
        self.text_input = QLineEdit()
        self.text_label = QLabel("Text:")
        layout.addRow(self.text_label, self.text_input)

        # Key field (for key action)
        self.key_input = QLineEdit()
        self.key_label = QLabel("Key:")
        layout.addRow(self.key_label, self.key_input)

        # Duration field (for delay action)
        self.duration_spin = QDoubleSpinBox()
        self.duration_spin.setMinimum(0.1)
        self.duration_spin.setMaximum(10.0)
        self.duration_spin.setValue(0.5)
        self.duration_label = QLabel("Duration:")
        layout.addRow(self.duration_label, self.duration_spin)

        # Button field (for click action)
        self.button_combo = QComboBox()
        self.button_combo.addItems(["left", "right", "middle"])
        self.button_label = QLabel("Button:")
        layout.addRow(self.button_label, self.button_combo)

        # X coordinate
        self.x_spin = QSpinBox()
        self.x_spin.setMinimum(0)
        self.x_spin.setMaximum(9999)
        self.x_label = QLabel("X:")
        layout.addRow(self.x_label, self.x_spin)

        # Y coordinate
        self.y_spin = QSpinBox()
        self.y_spin.setMinimum(0)
        self.y_spin.setMaximum(9999)
        self.y_label = QLabel("Y:")
        layout.addRow(self.y_label, self.y_spin)

        # App field (for launch action)
        self.app_input = QLineEdit()
        self.app_label = QLabel("App:")
        layout.addRow(self.app_label, self.app_input)

        # Load existing action
        if action:
            action_type = action.get("type", "type")
            self.type_combo.setCurrentText(action_type)
            self.text_input.setText(action.get("text", ""))
            self.key_input.setText(action.get("key", ""))
            self.duration_spin.setValue(action.get("duration", 0.5))
            self.button_combo.setCurrentText(action.get("button", "left"))
            self.x_spin.setValue(action.get("x", 0))
            self.y_spin.setValue(action.get("y", 0))
            self.app_input.setText(action.get("app", ""))

        self.update_fields()

        # Buttons
        button_layout = QHBoxLayout()
        ok_btn = QPushButton("Save")
        ok_btn.clicked.connect(self.accept)
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(ok_btn)
        button_layout.addWidget(cancel_btn)
        layout.addRow(button_layout)

        self.setLayout(layout)

    def update_fields(self):
        """Show/hide fields based on action type."""
        action_type = self.type_combo.currentText()
        self.text_label.setVisible(action_type == "type")
        self.text_input.setVisible(action_type == "type")
        self.key_label.setVisible(action_type == "key")
        self.key_input.setVisible(action_type == "key")
        self.duration_label.setVisible(action_type == "delay")
        self.duration_spin.setVisible(action_type == "delay")
        self.button_label.setVisible(action_type == "click")
        self.button_combo.setVisible(action_type == "click")
        self.x_label.setVisible(action_type in ["click", "move"])
        self.x_spin.setVisible(action_type in ["click", "move"])
        self.y_label.setVisible(action_type in ["click", "move"])
        self.y_spin.setVisible(action_type in ["click", "move"])
        self.app_label.setVisible(action_type == "launch")
        self.app_input.setVisible(action_type == "launch")

    def get_action(self) -> dict:
        """Get the configured action."""
        action_type = self.type_combo.currentText()
        action = {"type": action_type}

        if action_type == "type":
            action["text"] = self.text_input.text()
        elif action_type == "key":
            action["key"] = self.key_input.text()
        elif action_type == "delay":
            action["duration"] = self.duration_spin.value()
        elif action_type == "click":
            action["button"] = self.button_combo.currentText()
            action["x"] = self.x_spin.value()
            action["y"] = self.y_spin.value()
        elif action_type == "move":
            action["x"] = self.x_spin.value()
            action["y"] = self.y_spin.value()
        elif action_type == "launch":
            action["app"] = self.app_input.text()

        return action


class HotkeyEditor(QDialog):
    """Dialog to edit a hotkey and its actions."""

    def __init__(self, hotkey_str: str = "", hotkey_config: dict = None, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Edit Hotkey")
        self.setModal(True)
        self.setGeometry(100, 100, 600, 500)

        self.hotkey_str = hotkey_str
        self.hotkey_config = hotkey_config or {"actions": []}

        layout = QVBoxLayout()

        # Hotkey input
        hotkey_layout = QHBoxLayout()
        hotkey_layout.addWidget(QLabel("Hotkey:"))
        self.hotkey_input = QLineEdit(hotkey_str)
        hotkey_layout.addWidget(self.hotkey_input)
        record_btn = QPushButton("Record")
        record_btn.clicked.connect(self.record_hotkey)
        hotkey_layout.addWidget(record_btn)
        layout.addLayout(hotkey_layout)

        # App filter
        filter_layout = QHBoxLayout()
        filter_layout.addWidget(QLabel("App Filter (optional):"))
        self.app_filter_input = QLineEdit(self.hotkey_config.get("app_filter", ""))
        filter_layout.addWidget(self.app_filter_input)
        layout.addLayout(filter_layout)

        # Actions list
        layout.addWidget(QLabel("Actions:"))
        self.actions_list = QListWidget()
        self.refresh_actions_list()
        layout.addWidget(self.actions_list)

        # Action buttons
        action_btn_layout = QHBoxLayout()
        add_action_btn = QPushButton("Add Action")
        add_action_btn.clicked.connect(self.add_action)
        edit_action_btn = QPushButton("Edit Action")
        edit_action_btn.clicked.connect(self.edit_action)
        delete_action_btn = QPushButton("Delete Action")
        delete_action_btn.clicked.connect(self.delete_action)
        action_btn_layout.addWidget(add_action_btn)
        action_btn_layout.addWidget(edit_action_btn)
        action_btn_layout.addWidget(delete_action_btn)
        layout.addLayout(action_btn_layout)

        # Delay setting
        delay_layout = QHBoxLayout()
        delay_layout.addWidget(QLabel("Default Delay (seconds):"))
        self.delay_spin = QDoubleSpinBox()
        self.delay_spin.setMinimum(0.01)
        self.delay_spin.setMaximum(5.0)
        self.delay_spin.setValue(self.hotkey_config.get("delay", 0.1))
        delay_layout.addWidget(self.delay_spin)
        layout.addLayout(delay_layout)

        # Save/Cancel buttons
        button_layout = QHBoxLayout()
        save_btn = QPushButton("Save")
        save_btn.clicked.connect(self.accept)
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(save_btn)
        button_layout.addWidget(cancel_btn)
        layout.addLayout(button_layout)

        self.setLayout(layout)

    def record_hotkey(self):
        """Open hotkey recorder."""
        dialog = HotkeyRecorder(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            if dialog.recorded_hotkey:
                self.hotkey_input.setText(dialog.recorded_hotkey)

    def refresh_actions_list(self):
        """Refresh the actions list display."""
        self.actions_list.clear()
        for i, action in enumerate(self.hotkey_config.get("actions", [])):
            action_type = action.get("type", "unknown")
            text = action.get("text", "")[:30]
            label = f"{i+1}. [{action_type}] {text}"
            item = QListWidgetItem(label)
            self.actions_list.addItem(item)

    def add_action(self):
        """Add a new action."""
        dialog = ActionEditor(parent=self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            action = dialog.get_action()
            self.hotkey_config.setdefault("actions", []).append(action)
            self.refresh_actions_list()

    def edit_action(self):
        """Edit the selected action."""
        current_row = self.actions_list.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, "Warning", "Please select an action to edit")
            return

        action = self.hotkey_config["actions"][current_row]
        dialog = ActionEditor(action, parent=self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.hotkey_config["actions"][current_row] = dialog.get_action()
            self.refresh_actions_list()

    def delete_action(self):
        """Delete the selected action."""
        current_row = self.actions_list.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, "Warning", "Please select an action to delete")
            return

        del self.hotkey_config["actions"][current_row]
        self.refresh_actions_list()

    def get_hotkey_config(self) -> tuple[str, dict]:
        """Get the updated hotkey string and config."""
        config = {
            "actions": self.hotkey_config.get("actions", []),
            "delay": self.delay_spin.value(),
        }
        if self.app_filter_input.text():
            config["app_filter"] = self.app_filter_input.text().lower()

        return self.hotkey_input.text(), config


class MainWindow(QMainWindow):
    """Main GUI window."""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Keybind Ubuntu - Hotkey Manager")
        self.setGeometry(100, 100, 900, 700)

        self.config = load_config()
        self.setup_ui()
        self.refresh_profiles()

    def setup_ui(self):
        """Set up the user interface."""
        main_widget = QWidget()
        main_layout = QVBoxLayout()

        # Profile selection
        profile_layout = QHBoxLayout()
        profile_layout.addWidget(QLabel("Profile:"))
        self.profile_combo = QComboBox()
        self.profile_combo.currentTextChanged.connect(self.on_profile_changed)
        profile_layout.addWidget(self.profile_combo)

        add_profile_btn = QPushButton("New Profile")
        add_profile_btn.clicked.connect(self.add_profile)
        profile_layout.addWidget(add_profile_btn)

        delete_profile_btn = QPushButton("Delete Profile")
        delete_profile_btn.clicked.connect(self.delete_profile)
        profile_layout.addWidget(delete_profile_btn)

        main_layout.addLayout(profile_layout)

        # Hotkeys list
        main_layout.addWidget(QLabel("Hotkeys:"))
        self.hotkeys_list = QListWidget()
        main_layout.addWidget(self.hotkeys_list)

        # Hotkey buttons
        hotkey_btn_layout = QHBoxLayout()
        add_hotkey_btn = QPushButton("Add Hotkey")
        add_hotkey_btn.clicked.connect(self.add_hotkey)
        hotkey_btn_layout.addWidget(add_hotkey_btn)

        edit_hotkey_btn = QPushButton("Edit Hotkey")
        edit_hotkey_btn.clicked.connect(self.edit_hotkey)
        hotkey_btn_layout.addWidget(edit_hotkey_btn)

        delete_hotkey_btn = QPushButton("Delete Hotkey")
        delete_hotkey_btn.clicked.connect(self.delete_hotkey)
        hotkey_btn_layout.addWidget(delete_hotkey_btn)

        main_layout.addLayout(hotkey_btn_layout)

        # Auto-start checkbox
        self.autostart_checkbox = QCheckBox("Auto-start on login")
        self.autostart_checkbox.setChecked(AUTOSTART_PATH.exists())
        self.autostart_checkbox.stateChanged.connect(self.toggle_autostart)
        main_layout.addWidget(self.autostart_checkbox)

        # Save button
        save_btn = QPushButton("Save & Close")
        save_btn.clicked.connect(self.save_and_close)
        main_layout.addWidget(save_btn)

        main_widget.setLayout(main_layout)
        self.setCentralWidget(main_widget)

    def refresh_profiles(self):
        """Refresh profile list."""
        self.profile_combo.blockSignals(True)
        self.profile_combo.clear()
        for profile_name in self.config.get("profiles", {}).keys():
            self.profile_combo.addItem(profile_name)
        self.profile_combo.blockSignals(False)

        default = self.config.get("default_profile")
        if default:
            index = self.profile_combo.findText(default)
            if index >= 0:
                self.profile_combo.setCurrentIndex(index)

        self.refresh_hotkeys()

    def on_profile_changed(self):
        """Handle profile selection change."""
        self.config["default_profile"] = self.profile_combo.currentText()
        self.refresh_hotkeys()

    def refresh_hotkeys(self):
        """Refresh hotkeys list for current profile."""
        self.hotkeys_list.clear()
        profile_name = self.profile_combo.currentText()
        if not profile_name:
            return

        profile = self.config["profiles"].get(profile_name, {})
        hotkeys = profile.get("hotkeys", {})

        for hotkey_str, hotkey_config in hotkeys.items():
            actions = hotkey_config.get("actions", [])
            label = f"{hotkey_str} → {len(actions)} action(s)"
            item = QListWidgetItem(label)
            self.hotkeys_list.addItem(item)

    def add_profile(self):
        """Add a new profile."""
        name, ok = self._get_text_input("New Profile Name:")
        if ok and name:
            self.config["profiles"][name] = {"name": name, "hotkeys": {}}
            self.refresh_profiles()
            self.profile_combo.setCurrentText(name)

    def delete_profile(self):
        """Delete the current profile."""
        profile_name = self.profile_combo.currentText()
        if not profile_name:
            return

        reply = QMessageBox.question(
            self,
            "Confirm",
            f"Delete profile '{profile_name}'?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if reply == QMessageBox.StandardButton.Yes:
            del self.config["profiles"][profile_name]
            self.refresh_profiles()

    def add_hotkey(self):
        """Add a new hotkey to current profile."""
        dialog = HotkeyEditor(parent=self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            hotkey_str, hotkey_config = dialog.get_hotkey_config()
            if hotkey_str:
                profile_name = self.profile_combo.currentText()
                self.config["profiles"][profile_name]["hotkeys"][hotkey_str] = hotkey_config
                self.refresh_hotkeys()

    def edit_hotkey(self):
        """Edit the selected hotkey."""
        current_row = self.hotkeys_list.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, "Warning", "Please select a hotkey to edit")
            return

        profile_name = self.profile_combo.currentText()
        hotkeys = self.config["profiles"][profile_name]["hotkeys"]
        hotkey_str = list(hotkeys.keys())[current_row]
        hotkey_config = hotkeys[hotkey_str]

        dialog = HotkeyEditor(hotkey_str, hotkey_config, parent=self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            new_hotkey_str, new_config = dialog.get_hotkey_config()
            del hotkeys[hotkey_str]
            hotkeys[new_hotkey_str] = new_config
            self.refresh_hotkeys()

    def delete_hotkey(self):
        """Delete the selected hotkey."""
        current_row = self.hotkeys_list.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, "Warning", "Please select a hotkey to delete")
            return

        profile_name = self.profile_combo.currentText()
        hotkeys = self.config["profiles"][profile_name]["hotkeys"]
        hotkey_str = list(hotkeys.keys())[current_row]

        reply = QMessageBox.question(
            self,
            "Confirm",
            f"Delete hotkey '{hotkey_str}'?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if reply == QMessageBox.StandardButton.Yes:
            del hotkeys[hotkey_str]
            self.refresh_hotkeys()

    def toggle_autostart(self):
        """Toggle auto-start on login."""
        if self.autostart_checkbox.isChecked():
            self.enable_autostart()
        else:
            self.disable_autostart()

    def enable_autostart(self):
        """Enable auto-start."""
        AUTOSTART_PATH.parent.mkdir(parents=True, exist_ok=True)
        script_path = Path(__file__).absolute()
        content = f"""[Desktop Entry]
Type=Application
Name=Keybind Ubuntu
Comment=Keyboard automation tool
Exec={sys.executable} {script_path}
Hidden=false
NoDisplay=false
X-GNOME-Autostart-enabled=true
"""
        try:
            AUTOSTART_PATH.write_text(content)
            QMessageBox.information(self, "Success", "Auto-start enabled")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to enable auto-start: {e}")

    def disable_autostart(self):
        """Disable auto-start."""
        try:
            if AUTOSTART_PATH.exists():
                AUTOSTART_PATH.unlink()
            QMessageBox.information(self, "Success", "Auto-start disabled")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to disable auto-start: {e}")

    def save_and_close(self):
        """Save config and close."""
        if save_config(self.config):
            QMessageBox.information(self, "Success", "Configuration saved")
            self.close()
        else:
            QMessageBox.critical(self, "Error", "Failed to save configuration")

    def _get_text_input(self, prompt: str) -> tuple[str, bool]:
        """Get text input from user."""
        from PyQt6.QtWidgets import QInputDialog
        text, ok = QInputDialog.getText(self, "Input", prompt)
        return text, ok


def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
