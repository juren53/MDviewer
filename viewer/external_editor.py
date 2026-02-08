"""
External Editor Launcher for MDviewer
Detects installed text editors, lets the user pick one, remembers the choice.
"""

import os
import shutil
import subprocess
import platform

from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel,
                              QPushButton, QListWidget, QListWidgetItem,
                              QMessageBox, QCheckBox)
from PyQt6.QtCore import Qt, QSettings
from PyQt6.QtGui import QFont


# (command, display name) — order determines display order
_KNOWN_EDITORS = [
    # GUI editors — Linux
    ("xed",           "Xed (Cinnamon text editor)"),
    ("gedit",         "gedit (GNOME text editor)"),
    ("kate",          "Kate (KDE advanced editor)"),
    ("kwrite",        "KWrite (KDE text editor)"),
    ("mousepad",      "Mousepad (Xfce text editor)"),
    ("pluma",         "Pluma (MATE text editor)"),
    ("featherpad",    "FeatherPad (lightweight editor)"),
    ("xedit",         "Xedit (X11 text editor)"),
    ("leafpad",       "Leafpad (simple text editor)"),
    ("geany",         "Geany (lightweight IDE)"),
    ("sublime_text",  "Sublime Text"),
    ("subl",          "Sublime Text"),
    ("code",          "Visual Studio Code"),
    ("codium",        "VSCodium"),
    ("atom",          "Atom"),
    # GUI editors — cross-platform
    ("notepadqq",     "Notepadqq"),
    ("emacs",         "GNU Emacs"),
    ("gvim",          "GVim (graphical Vim)"),
    # GUI editors — Windows
    ("notepad++",     "Notepad++"),
    ("notepad",       "Notepad (Windows)"),
    ("wordpad",       "WordPad (Windows)"),
    ("write",         "WordPad (Windows)"),
    # Terminal editors (launched in terminal)
    ("nano",          "nano (terminal editor)"),
    ("vim",           "Vim (terminal editor)"),
    ("vi",            "vi (terminal editor)"),
    ("nvim",          "Neovim (terminal editor)"),
    ("micro",         "micro (terminal editor)"),
]

# Terminal editors need a terminal emulator wrapper on Linux
_TERMINAL_EDITORS = {"nano", "vim", "vi", "nvim", "micro", "emacs"}

# Known terminal emulators to try
_TERMINAL_EMULATORS = [
    "x-terminal-emulator",  # Debian/Ubuntu default
    "gnome-terminal",
    "mate-terminal",
    "xfce4-terminal",
    "konsole",
    "xterm",
    "alacritty",
    "kitty",
    "tilix",
    "terminator",
    "lxterminal",
    "sakura",
    "st",
]


def _find_installed_editors():
    """Return list of (command, display_name) for editors found on the system"""
    found = []
    seen_names = set()
    for cmd, name in _KNOWN_EDITORS:
        if cmd in seen_names:
            continue
        if shutil.which(cmd):
            found.append((cmd, name))
            seen_names.add(cmd)
    return found


def _find_terminal_emulator():
    """Find an available terminal emulator"""
    for term in _TERMINAL_EMULATORS:
        if shutil.which(term):
            return term
    return None


def _launch_editor(editor_cmd, file_path):
    """Launch the editor with the given file. Returns (success, error_msg)."""
    try:
        if editor_cmd in _TERMINAL_EDITORS and platform.system() != "Windows":
            term = _find_terminal_emulator()
            if not term:
                return False, "No terminal emulator found to run terminal-based editor."
            # Most terminal emulators accept -e command
            subprocess.Popen([term, "-e", editor_cmd, file_path])
        else:
            subprocess.Popen([editor_cmd, file_path])
        return True, None
    except Exception as e:
        return False, str(e)


class EditorPickerDialog(QDialog):
    """Dialog for selecting a text editor from installed editors"""

    def __init__(self, editors, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Select Text Editor")
        self.setModal(True)
        self.setMinimumWidth(450)
        self.setMinimumHeight(350)
        self.selected_editor = None

        layout = QVBoxLayout()

        label = QLabel("Choose a text editor to open documents with:")
        label.setWordWrap(True)
        layout.addWidget(label)

        self.editor_list = QListWidget()
        self.editor_list.setAlternatingRowColors(True)
        for cmd, name in editors:
            item = QListWidgetItem(f"{name}")
            item.setData(Qt.ItemDataRole.UserRole, cmd)
            self.editor_list.addItem(item)

        # Pre-select the first item
        if self.editor_list.count() > 0:
            self.editor_list.setCurrentRow(0)

        self.editor_list.itemDoubleClicked.connect(self._on_double_click)
        layout.addWidget(self.editor_list)

        self.remember_check = QCheckBox("Remember my choice")
        self.remember_check.setChecked(True)
        layout.addWidget(self.remember_check)

        # Buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()

        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)

        select_btn = QPushButton("Open in Editor")
        select_btn.setDefault(True)
        select_btn.clicked.connect(self._on_select)
        button_layout.addWidget(select_btn)

        layout.addLayout(button_layout)
        self.setLayout(layout)

    def _on_select(self):
        item = self.editor_list.currentItem()
        if item:
            self.selected_editor = item.data(Qt.ItemDataRole.UserRole)
            self.accept()

    def _on_double_click(self, item):
        self.selected_editor = item.data(Qt.ItemDataRole.UserRole)
        self.accept()

    @property
    def remember(self):
        return self.remember_check.isChecked()


def open_in_external_editor(file_path, parent=None, settings=None):
    """
    Open file_path in an external editor.
    - If a preferred editor is saved in settings and still installed, use it.
    - Otherwise show the picker dialog.
    - Returns True if editor was launched.
    """
    if settings is None:
        settings = QSettings("MDviewer", "MDviewer")

    # Check for saved preference
    saved_editor = settings.value("external_editor", "")
    if saved_editor and shutil.which(saved_editor):
        success, error = _launch_editor(saved_editor, file_path)
        if success:
            return True
        else:
            QMessageBox.warning(
                parent, "Editor Error",
                f"Could not launch {saved_editor}:\n{error}\n\n"
                "Please select a different editor."
            )
            # Fall through to picker

    # Detect installed editors
    editors = _find_installed_editors()
    if not editors:
        QMessageBox.warning(
            parent, "No Editors Found",
            "No supported text editors were found on this system.\n\n"
            "Please install a text editor and try again."
        )
        return False

    # Show picker
    dialog = EditorPickerDialog(editors, parent)
    if dialog.exec() != QDialog.DialogCode.Accepted:
        return False

    editor_cmd = dialog.selected_editor
    if not editor_cmd:
        return False

    # Save preference if requested
    if dialog.remember:
        settings.setValue("external_editor", editor_cmd)

    success, error = _launch_editor(editor_cmd, file_path)
    if not success:
        QMessageBox.critical(
            parent, "Editor Error",
            f"Could not launch {editor_cmd}:\n{error}"
        )
        return False

    return True


def change_preferred_editor(parent=None, settings=None):
    """
    Force the editor picker dialog regardless of saved preference.
    Useful for changing the editor from a menu option.
    """
    if settings is None:
        settings = QSettings("MDviewer", "MDviewer")

    editors = _find_installed_editors()
    if not editors:
        QMessageBox.warning(
            parent, "No Editors Found",
            "No supported text editors were found on this system."
        )
        return None

    dialog = EditorPickerDialog(editors, parent)
    if dialog.exec() == QDialog.DialogCode.Accepted and dialog.selected_editor:
        if dialog.remember:
            settings.setValue("external_editor", dialog.selected_editor)
        return dialog.selected_editor

    return None
