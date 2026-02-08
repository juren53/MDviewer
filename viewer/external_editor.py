"""
External Editor Launcher for MDviewer
Detects installed text editors and markdown editors, lets the user pick one,
remembers the choice.
"""

import configparser
import glob
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

# Skip these apps — they're viewers, not editors
_SKIP_DESKTOP_IDS = {
    "MDviewer.desktop",
    "calibre-ebook-viewer.desktop",
    "calibre-gui.desktop",
}


def _parse_desktop_file(filepath):
    """Parse a .desktop file and return (exec_cmd, name) or None.

    Uses configparser with a fallback to manual parsing for files
    that don't conform strictly to INI format.
    """
    try:
        # Try configparser first (handles most .desktop files)
        cp = configparser.ConfigParser(interpolation=None)
        cp.read(filepath, encoding='utf-8')
        if not cp.has_section('Desktop Entry'):
            return None
        name = cp.get('Desktop Entry', 'Name', fallback=None)
        exec_line = cp.get('Desktop Entry', 'Exec', fallback=None)
        app_type = cp.get('Desktop Entry', 'Type', fallback='Application')
    except (configparser.Error, UnicodeDecodeError):
        # Fallback: manual line parsing
        name = None
        exec_line = None
        app_type = 'Application'
        try:
            with open(filepath, 'r', encoding='utf-8', errors='replace') as f:
                in_desktop_entry = False
                for line in f:
                    line = line.strip()
                    if line == '[Desktop Entry]':
                        in_desktop_entry = True
                        continue
                    if line.startswith('[') and in_desktop_entry:
                        break  # next section
                    if not in_desktop_entry:
                        continue
                    if line.startswith('Name='):
                        name = line.split('=', 1)[1]
                    elif line.startswith('Exec='):
                        exec_line = line.split('=', 1)[1]
                    elif line.startswith('Type='):
                        app_type = line.split('=', 1)[1]
        except (OSError, IOError):
            return None

    if not name or not exec_line or app_type != 'Application':
        return None

    # Extract the base command from Exec line (strip %f, %F, %u, %U, etc.)
    cmd = exec_line.split()[0] if exec_line else None
    if not cmd:
        return None

    # Resolve to just the binary name if it's an absolute path
    cmd_base = os.path.basename(cmd)

    return cmd_base, name


def _find_markdown_editors():
    """Scan .desktop files for apps that handle text/markdown MIME type.

    Returns list of (command, display_name) for installed markdown-capable apps.
    """
    # Directories to scan for .desktop files
    desktop_dirs = [
        os.path.expanduser("~/.local/share/applications"),
        "/usr/share/applications",
        "/usr/local/share/applications",
    ]

    # Also check XDG_DATA_DIRS
    xdg_data = os.environ.get("XDG_DATA_DIRS", "")
    for d in xdg_data.split(":"):
        apps_dir = os.path.join(d, "applications")
        if apps_dir not in desktop_dirs:
            desktop_dirs.append(apps_dir)

    markdown_mimes = {"text/markdown", "text/x-markdown"}
    found = []
    seen_cmds = set()

    for apps_dir in desktop_dirs:
        if not os.path.isdir(apps_dir):
            continue
        for desktop_file in glob.glob(os.path.join(apps_dir, "*.desktop")):
            basename = os.path.basename(desktop_file)

            # Skip our own app and non-editors
            if basename in _SKIP_DESKTOP_IDS:
                continue

            # Check if this .desktop file mentions markdown MIME types
            try:
                with open(desktop_file, 'r', encoding='utf-8', errors='replace') as f:
                    content = f.read()
            except (OSError, IOError):
                continue

            if not any(mime in content for mime in markdown_mimes):
                continue

            result = _parse_desktop_file(desktop_file)
            if not result:
                continue

            cmd, name = result

            # Verify it's actually installed
            if cmd in seen_cmds:
                continue
            if not shutil.which(cmd):
                continue

            seen_cmds.add(cmd)
            found.append((cmd, f"{name} (markdown editor)"))

    return found


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


def _find_all_editors():
    """Return markdown editors first, then general text editors, no duplicates."""
    md_editors = _find_markdown_editors()
    md_cmds = {cmd for cmd, _ in md_editors}

    text_editors = _find_installed_editors()
    # Filter out any text editors already listed as markdown editors
    text_editors = [(cmd, name) for cmd, name in text_editors if cmd not in md_cmds]

    return md_editors, text_editors


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

    def __init__(self, md_editors, text_editors, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Select Text Editor")
        self.setModal(True)
        self.setMinimumWidth(450)
        self.setMinimumHeight(400)
        self.selected_editor = None

        layout = QVBoxLayout()

        label = QLabel("Choose an editor to open documents with:")
        label.setWordWrap(True)
        layout.addWidget(label)

        self.editor_list = QListWidget()
        self.editor_list.setAlternatingRowColors(True)

        # Add markdown editors section
        if md_editors:
            header = QListWidgetItem("── Markdown Editors ──")
            header.setFlags(Qt.ItemFlag.NoItemFlags)
            header_font = header.font()
            header_font.setBold(True)
            header.setFont(header_font)
            self.editor_list.addItem(header)

            for cmd, name in md_editors:
                item = QListWidgetItem(f"  {name}")
                item.setData(Qt.ItemDataRole.UserRole, cmd)
                self.editor_list.addItem(item)

        # Add text editors section
        if text_editors:
            header = QListWidgetItem("── Text Editors ──")
            header.setFlags(Qt.ItemFlag.NoItemFlags)
            header_font = header.font()
            header_font.setBold(True)
            header.setFont(header_font)
            self.editor_list.addItem(header)

            for cmd, name in text_editors:
                item = QListWidgetItem(f"  {name}")
                item.setData(Qt.ItemDataRole.UserRole, cmd)
                self.editor_list.addItem(item)

        # Pre-select the first selectable item
        for i in range(self.editor_list.count()):
            item = self.editor_list.item(i)
            if item.flags() & Qt.ItemFlag.ItemIsSelectable:
                self.editor_list.setCurrentRow(i)
                break

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
        if item and item.data(Qt.ItemDataRole.UserRole):
            self.selected_editor = item.data(Qt.ItemDataRole.UserRole)
            self.accept()

    def _on_double_click(self, item):
        if item.data(Qt.ItemDataRole.UserRole):
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
    md_editors, text_editors = _find_all_editors()
    if not md_editors and not text_editors:
        QMessageBox.warning(
            parent, "No Editors Found",
            "No supported text editors were found on this system.\n\n"
            "Please install a text editor and try again."
        )
        return False

    # Show picker
    dialog = EditorPickerDialog(md_editors, text_editors, parent)
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

    md_editors, text_editors = _find_all_editors()
    if not md_editors and not text_editors:
        QMessageBox.warning(
            parent, "No Editors Found",
            "No supported text editors were found on this system."
        )
        return None

    dialog = EditorPickerDialog(md_editors, text_editors, parent)
    if dialog.exec() == QDialog.DialogCode.Accepted and dialog.selected_editor:
        if dialog.remember:
            settings.setValue("external_editor", dialog.selected_editor)
        return dialog.selected_editor

    return None
