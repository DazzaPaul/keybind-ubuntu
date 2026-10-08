#!/usr/bin/env python3
"""
GUI configuration editor for Keybind Ubuntu.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

from PyQt6.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QComboBox,
    QPushButton,
    QLineEdit,
    QDialog,
    QFormLayout,
    QMessageBox,
    QDoubleSpinBox,
    QSpinBox,
    QInputDialog,
    QCheckBox,
)
from pynput.keyboard import Listener as KeyListener, Key

CONFIG_PATH = Path.home() / ".keybind" / "config.json"
AUTO_START_PATH = Path.home() / ".config" / "autostart" / "keybind-ubuntu.desktop"


def load_config():
    if not CONFIG_PATH.exists():
        return {
            "default_profile": "default",
            "profiles": {"default": {"name": "Default", "hotkeys": {}}},
        }

    try:
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {
            "default_profile": "default",
            "profiles": {"default": {"name": "Default", "hotkeys": {}}},
        }


def save_config(config):
    CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(CONFIG_PATH, "w", encoding="utf-8") as f:
        json.dump(config, f, indent=2)


class HotkeyRecorder(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Record Hotkey")
        self.resize(350, 180)
        self.setModal(True)

        layout = QVBoxLayout()
        self.label = QLabel("Press the desired hotkey combination.")
        self.hotkey_label = QLabel("Waiting...")
        self.hotkey_label.setStyleSheet("font-size: 20px; font-weight: bold; color: #0055cc;")
        layout.addWidget(self.label)
        layout.addWidget(self.hotkey_label)

        buttons = QHBoxLayout()
        ok_btn = QPushButton("OK")
        ok_btn.clicked.connect(self.accept)
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        buttons.addWidget(ok_btn)
        buttons.addWidget(cancel_btn)
        layout.addLayout(buttons)

        self.setLayout(layout)
        self.pressed = set()
        self.recorded = ""

        self.listener = KeyListener(on_press=self.on_press, on_release=self.on_release)
        self.listener.start()

    def on_press(self, key):
        try:
            if isinstance(key, Key):
                name = key.name.lower()
            else:
                name = key.char.lower() if key.char else str(key).lower()
            self.pressed.add(name)
            self.recorded = "+".join(sorted(self.pressed))
            self.hotkey_label.setText(self.recorded)
        except Exception:
            pass

    def on_release(self, key):
        try:
            if isinstance(key, Key):
                name = key.name.lower()
            else:
                name = key.char.lower() if key.char else str(key).lower()
            self.pressed.discard(name)
        except Exception:
            pass

    def closeEvent(self, event):
        self.listener.stop()
        super().closeEvent(event)


class ActionEditor(QDialog):
    def __init__(self, action=None, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Edit Action")
        self.resize(500, 320)
        self.setModal(True)

        self.action = action or {"type": "type", "text": ""}
        form = QFormLayout()

        self.type_combo = QComboBox()
        self.type_combo.addItems(["type", "key", "delay", "click", "move", "launch"])
        self.type_combo.setCurrentText(self.action.get("type", "type"))
        form.addRow("Type:", self.type_combo)

        self.text_edit = QLineEdit(self.action.get("text", ""))
        self.text_label = QLabel("Text:")
        form.addRow(self.text_label, self.text_edit)

        self.key_edit = QLineEdit(self.action.get("key", ""))
        self.key_label = QLabel("Key:")
        form.addRow(self.key_label, self.key_edit)

        self.delay_spin = QDoubleSpinBox()
        self.delay_spin.setMinimum(0.05)
        self.delay_spin.setMaximum(10.0)
        self.delay_spin.setValue(float(self.action.get("duration", 0.2)))
        self.delay_label = QLabel("Delay:")
        form.addRow(self.delay_label, self.delay_spin)

        self.button_combo = QComboBox()
        self.button_combo.addItems(["left", "right"])
        self.button_combo.setCurrentText(self.action.get("button", "left"))
        self.button_label = QLabel("Button:")
        form.addRow(self.button_label, self.button_combo)

        self.x_spin = QSpinBox()
        self.x_spin.setValue(int(self.action.get("x", 0)))
        self.x_label = QLabel("X:")
        form.addRow(self.x_label, self.x_spin)

        self.y_spin = QSpinBox()
        self.y_spin.setValue(int(self.action.get("y", 0)))
        self.y_label = QLabel("Y:")
        form.addRow(self.y_label, self.y_spin)

        self.app_edit = QLineEdit(self.action.get("app", ""))
        self.app_label = QLabel("App:")
        form.addRow(self.app_label, self.app_edit)

        buttons = QHBoxLayout()
        ok_btn = QPushButton("Save")
        ok_btn.clicked.connect(self.accept)
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        buttons.addWidget(ok_btn)
        buttons.addWidget(cancel_btn)
        form.addRow(buttons)

        self.setLayout(form)
        self.update_visibility()
        self.type_combo.currentTextChanged.connect(self.update_visibility)

    def update_visibility(self):
        t = self.type_combo.currentText()

        self.text_label.setVisible(t == "type")
        self.text_edit.setVisible(t == "type")

        self.key_label.setVisible(t == "key")
        self.key_edit.setVisible(t == "key")

        self.delay_label.setVisible(t == "delay")
        self.delay_spin.setVisible(t == "delay")

        self.button_label.setVisible(t == "click")
        self.button_combo.setVisible(t == "click")

        self.x_label.setVisible(t in ["click", "move"])
        self.x_spin.setVisible(t in ["click", "move"])

        self.y_label.setVisible(t in ["click", "move"])
        self.y_spin.setVisible(t in ["click", "move"])

        self.app_label.setVisible(t == "launch")
        self.app_edit.setVisible(t == "launch")

    def get_action(self):
        t = self.type_combo.currentText()
        action = {"type": t}

        if t == "type":
            action["text"] = self.text_edit.text()
        elif t == "key":
            action["key"] = self.key_edit.text()
        elif t == "delay":
            action["duration"] = self.delay_spin.value()
        elif t == "click":
            action["button"] = self.button_combo.currentText()
            action["x"] = self.x_spin.value()
            action["y"] = self.y_spin.value()
        elif t == "move":
            action["x"] = self.x_spin.value()
            action["y"] = self.y_spin.value()
        elif t == "launch":
            action["app"] = self.app_edit.text()

        return action


class HotkeyEditor(QDialog):
    def __init__(self, hotkey="", config=None, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Edit Hotkey")
        self.resize(550, 420)
        self.setModal(True)

        self.config = config or {"actions": []}
        layout = QVBoxLayout()

        row = QHBoxLayout()
        row.addWidget(QLabel("Hotkey:"))
        self.hotkey_input = QLineEdit(hotkey)
        row.addWidget(self.hotkey_input)
        record_btn = QPushButton("Record")
        record_btn.clicked.connect(self.record_hotkey)
        row.addWidget(record_btn)
        layout.addLayout(row)

        app_row = QHBoxLayout()
        app_row.addWidget(QLabel("App Filter (optional):"))
        self.app_filter_input = QLineEdit(self.config.get("app_filter", ""))
        app_row.addWidget(self.app_filter_input)
        layout.addLayout(app_row)

        layout.addWidget(QLabel("Actions:"))
        self.action_list = QListWidget()
        self.refresh_actions()
        layout.addWidget(self.action_list)

        actions_buttons = QHBoxLayout()
        add_btn = QPushButton("Add")
        add_btn.clicked.connect(self.add_action)
        edit_btn = QPushButton("Edit")
        edit_btn.clicked.connect(self.edit_action)
        del_btn = QPushButton("Delete")
        del_btn.clicked.connect(self.delete_action)
        actions_buttons.addWidget(add_btn)
        actions_buttons.addWidget(edit_btn)
        actions_buttons.addWidget(del_btn)
        layout.addLayout(actions_buttons)

        delay_row = QHBoxLayout()
        delay_row.addWidget(QLabel("Delay:"))
        self.delay_box = QDoubleSpinBox()
        self.delay_box.setMinimum(0.05)
        self.delay_box.setMaximum(5.0)
        self.delay_box.setValue(float(self.config.get("delay", 0.1)))
        delay_row.addWidget(self.delay_box)
        layout.addLayout(delay_row)

        finish_row = QHBoxLayout()
        save_btn = QPushButton("Save")
        save_btn.clicked.connect(self.accept)
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        finish_row.addWidget(save_btn)
        finish_row.addWidget(cancel_btn)
        layout.addLayout(finish_row)

        self.setLayout(layout)

    def record_hotkey(self):
        dlg = HotkeyRecorder(self)
        if dlg.exec() == QDialog.DialogCode.Accepted:
            self.hotkey_input.setText(dlg.recorded)

    def refresh_actions(self):
        self.action_list.clear()
        for action in self.config.get("actions", []):
            label = action.get("type", "unknown")
            text = action.get("text", "")
            if text:
                label += f" - {text[:30]}"
            self.action_list.addItem(QListWidgetItem(label))

    def add_action(self):
        dlg = ActionEditor(parent=self)
        if dlg.exec() == QDialog.DialogCode.Accepted:
            self.config.setdefault("actions", []).append(dlg.get_action())
            self.refresh_actions()

    def edit_action(self):
        row = self.action_list.currentRow()
        if row < 0:
            QMessageBox.warning(self, "Warning", "Select an action first.")
            return
        action = self.config["actions"][row]
        dlg = ActionEditor(action, parent=self)
        if dlg.exec() == QDialog.DialogCode.Accepted:
            self.config["actions"][row] = dlg.get_action()
            self.refresh_actions()

    def delete_action(self):
        row = self.action_list.currentRow()
        if row < 0:
            QMessageBox.warning(self, "Warning", "Select an action first.")
            return
        del self.config["actions"][row]
        self.refresh_actions()

    def get_result(self):
        hotkey = self.hotkey_input.text().strip()
        cfg = {"actions": self.config.get("actions", []), "delay": self.delay_box.value()}
        filter_text = self.app_filter_input.text().strip()
        if filter_text:
            cfg["app_filter"] = filter_text.lower()
        return hotkey, cfg


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Keybind Ubuntu")
        self.resize(800, 500)

        self.config = load_config()
        self.build_ui()
        self.refresh_profiles()
        self.refresh_hotkeys()

    def build_ui(self):
        central = QWidget()
        layout = QVBoxLayout()

        profile_row = QHBoxLayout()
        profile_row.addWidget(QLabel("Profile:"))
        self.profile_combo = QComboBox()
        self.profile_combo.currentTextChanged.connect(self.on_profile_changed)
        profile_row.addWidget(self.profile_combo)
        add_profile_btn = QPushButton("New Profile")
        add_profile_btn.clicked.connect(self.add_profile)
        delete_profile_btn = QPushButton("Delete Profile")
        delete_profile_btn.clicked.connect(self.delete_profile)
        profile_row.addWidget(add_profile_btn)
        profile_row.addWidget(delete_profile_btn)
        layout.addLayout(profile_row)

        layout.addWidget(QLabel("Hotkeys:"))
        self.hotkey_list = QListWidget()
        layout.addWidget(self.hotkey_list)

        hotkey_buttons = QHBoxLayout()
        add_hotkey_btn = QPushButton("Add Hotkey")
        add_hotkey_btn.clicked.connect(self.add_hotkey)
        edit_hotkey_btn = QPushButton("Edit Hotkey")
        edit_hotkey_btn.clicked.connect(self.edit_hotkey)
        delete_hotkey_btn = QPushButton("Delete Hotkey")
        delete_hotkey_btn.clicked.connect(self.delete_hotkey)
        hotkey_buttons.addWidget(add_hotkey_btn)
        hotkey_buttons.addWidget(edit_hotkey_btn)
        hotkey_buttons.addWidget(delete_hotkey_btn)
        layout.addLayout(hotkey_buttons)

        self.autostart_checkbox = QCheckBox("Auto-start on login")
        self.autostart_checkbox.setChecked(AUTO_START_PATH.exists())
        self.autostart_checkbox.stateChanged.connect(self.toggle_autostart)
        layout.addWidget(self.autostart_checkbox)

        save_btn = QPushButton("Save")
        save_btn.clicked.connect(self.save_config)
        layout.addWidget(save_btn)

        central.setLayout(layout)
        self.setCentralWidget(central)

    def on_profile_changed(self):
        self.config["default_profile"] = self.profile_combo.currentText()
        self.refresh_hotkeys()

    def refresh_profiles(self):
        self.profile_combo.clear()
        for name in self.config.get("profiles", {}).keys():
            self.profile_combo.addItem(name)

        default_name = self.config.get("default_profile")
        if default_name and default_name in self.config.get("profiles", {}):
            self.profile_combo.setCurrentText(default_name)

    def refresh_hotkeys(self):
        self.hotkey_list.clear()
        current_profile = self.profile_combo.currentText()
        profile = self.config.get("profiles", {}).get(current_profile, {})
        for hotkey, hotkey_cfg in profile.get("hotkeys", {}).items():
            count = len(hotkey_cfg.get("actions", []))
            self.hotkey_list.addItem(f"{hotkey}  ({count} actions)")

    def add_profile(self):
        name, ok = QInputDialog.getText(self, "New Profile", "Profile name:")
        if not ok or not name.strip():
            return

        name = name.strip()
        self.config.setdefault("profiles", {})[name] = {"name": name, "hotkeys": {}}
        self.config["default_profile"] = name
        self.refresh_profiles()
        self.profile_combo.setCurrentText(name)
        self.refresh_hotkeys()

    def delete_profile(self):
        profile = self.profile_combo.currentText()
        if not profile:
            return

        reply = QMessageBox.question(self, "Delete?", f"Delete profile '{profile}'?")
        if reply == QMessageBox.StandardButton.Yes:
            del self.config["profiles"][profile]
            if self.config.get("default_profile") == profile:
                self.config["default_profile"] = next(iter(self.config["profiles"]), "default")
            self.refresh_profiles()
            self.refresh_hotkeys()

    def add_hotkey(self):
        dlg = HotkeyEditor(parent=self)
        if dlg.exec() == QDialog.DialogCode.Accepted:
            hotkey, cfg = dlg.get_result()
            if not hotkey:
                QMessageBox.warning(self, "Warning", "Hotkey is required.")
                return
            current = self.profile_combo.currentText()
            self.config["profiles"][current]["hotkeys"][hotkey] = cfg
            self.refresh_hotkeys()

    def edit_hotkey(self):
        current = self.profile_combo.currentText()
        row = self.hotkey_list.currentRow()
        if row < 0:
            QMessageBox.warning(self, "Warning", "Select a hotkey.")
            return

        hotkey = list(self.config["profiles"][current]["hotkeys"].keys())[row]
        cfg = self.config["profiles"][current]["hotkeys"][hotkey]

        dlg = HotkeyEditor(hotkey, cfg, parent=self)
        if dlg.exec() == QDialog.DialogCode.Accepted:
            new_hotkey, new_cfg = dlg.get_result()
            if not new_hotkey:
                return
            del self.config["profiles"][current]["hotkeys"][hotkey]
            self.config["profiles"][current]["hotkeys"][new_hotkey] = new_cfg
            self.refresh_hotkeys()

    def delete_hotkey(self):
        current = self.profile_combo.currentText()
        row = self.hotkey_list.currentRow()
        if row < 0:
            QMessageBox.warning(self, "Warning", "Select a hotkey.")
            return

        hotkey = list(self.config["profiles"][current]["hotkeys"].keys())[row]
        del self.config["profiles"][current]["hotkeys"][hotkey]
        self.refresh_hotkeys()

    def toggle_autostart(self):
        if self.autostart_checkbox.isChecked():
            self.enable_autostart()
        else:
            self.disable_autostart()

    def enable_autostart(self):
        AUTO_START_PATH.parent.mkdir(parents=True, exist_ok=True)
        script = str(Path(__file__).resolve())
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
        AUTO_START_PATH.write_text(content, encoding="utf-8")

    def disable_autostart(self):
        if AUTO_START_PATH.exists():
            AUTO_START_PATH.unlink()

    def save_config(self):
        save_config(self.config)
        QMessageBox.information(self, "Saved", "Configuration saved successfully.")
        self.close()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = MainWindow()
    win.show()
    sys.exit(app.exec())
