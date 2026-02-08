"""
File Information Dialog for MDviewer
Displays detailed file metadata for the currently loaded document.
"""

import os
import stat
import datetime
import platform

from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel,
                              QPushButton, QFormLayout, QGroupBox, QFrame)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont


def _format_size(size_bytes):
    """Format file size in human-readable form"""
    if size_bytes < 1024:
        return f"{size_bytes} bytes"
    elif size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.1f} KB ({size_bytes:,} bytes)"
    elif size_bytes < 1024 * 1024 * 1024:
        return f"{size_bytes / (1024*1024):.2f} MB ({size_bytes:,} bytes)"
    else:
        return f"{size_bytes / (1024*1024*1024):.2f} GB ({size_bytes:,} bytes)"


def _format_permissions(mode):
    """Format file permissions as rwx string"""
    perms = ""
    for who in ("USR", "GRP", "OTH"):
        for what in ("R", "W", "X"):
            flag = getattr(stat, f"S_I{what}{who}")
            perms += what.lower() if mode & flag else "-"
    # Also show octal
    octal = oct(stat.S_IMODE(mode))
    return f"{perms}  ({octal})"


def _format_timestamp(ts):
    """Format a timestamp in a readable way with timezone"""
    dt = datetime.datetime.fromtimestamp(ts)
    return dt.strftime("%Y-%m-%d  %I:%M:%S %p")


class FileInfoDialog(QDialog):
    """Dialog showing detailed file information"""

    def __init__(self, file_path, parent=None):
        super().__init__(parent)
        self.setWindowTitle("File Information")
        self.setModal(True)
        self.setMinimumWidth(550)

        layout = QVBoxLayout()

        try:
            st = os.stat(file_path)
        except OSError as e:
            layout.addWidget(QLabel(f"Error reading file info:\n{e}"))
            close_btn = QPushButton("Close")
            close_btn.clicked.connect(self.accept)
            layout.addWidget(close_btn)
            self.setLayout(layout)
            return

        # --- File Identity ---
        identity_group = QGroupBox("File")
        identity_form = QFormLayout()

        name_label = QLabel(os.path.basename(file_path))
        name_label.setFont(QFont("", -1, QFont.Weight.Bold))
        identity_form.addRow("Name:", name_label)
        identity_form.addRow("Directory:", self._selectable_label(os.path.dirname(os.path.abspath(file_path))))
        identity_form.addRow("Full Path:", self._selectable_label(os.path.abspath(file_path)))

        # File type / extension
        _, ext = os.path.splitext(file_path)
        file_type = ext.lstrip('.').upper() if ext else "No extension"
        identity_form.addRow("Type:", QLabel(f"{file_type} file"))

        identity_group.setLayout(identity_form)
        layout.addWidget(identity_group)

        # --- Size ---
        size_group = QGroupBox("Size")
        size_form = QFormLayout()
        size_form.addRow("File Size:", QLabel(_format_size(st.st_size)))

        # Line/word/char count
        try:
            with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
                content = f.read()
            lines = content.count('\n') + (1 if content and not content.endswith('\n') else 0)
            words = len(content.split())
            chars = len(content)
            size_form.addRow("Lines:", QLabel(f"{lines:,}"))
            size_form.addRow("Words:", QLabel(f"{words:,}"))
            size_form.addRow("Characters:", QLabel(f"{chars:,}"))
        except Exception:
            pass

        size_group.setLayout(size_form)
        layout.addWidget(size_group)

        # --- Timestamps ---
        time_group = QGroupBox("Timestamps")
        time_form = QFormLayout()
        time_form.addRow("Modified:", QLabel(_format_timestamp(st.st_mtime)))
        time_form.addRow("Accessed:", QLabel(_format_timestamp(st.st_atime)))

        # st_ctime is creation time on Windows, metadata change time on Linux
        if platform.system() == "Windows":
            time_form.addRow("Created:", QLabel(_format_timestamp(st.st_ctime)))
        else:
            time_form.addRow("Changed:", QLabel(_format_timestamp(st.st_ctime)))
            # Try to get birth time on Linux (Python 3.12+ / some filesystems)
            if hasattr(st, 'st_birthtime'):
                time_form.addRow("Created:", QLabel(_format_timestamp(st.st_birthtime)))

        time_group.setLayout(time_form)
        layout.addWidget(time_group)

        # --- Permissions / Ownership ---
        perms_group = QGroupBox("Permissions")
        perms_form = QFormLayout()
        perms_form.addRow("Permissions:", QLabel(_format_permissions(st.st_mode)))

        if platform.system() != "Windows":
            try:
                import pwd
                import grp
                owner = pwd.getpwuid(st.st_uid).pw_name
                group = grp.getgrgid(st.st_gid).gr_name
                perms_form.addRow("Owner:", QLabel(f"{owner}  (uid: {st.st_uid})"))
                perms_form.addRow("Group:", QLabel(f"{group}  (gid: {st.st_gid})"))
            except (ImportError, KeyError):
                perms_form.addRow("Owner UID:", QLabel(str(st.st_uid)))
                perms_form.addRow("Group GID:", QLabel(str(st.st_gid)))

        # Symlink check
        if os.path.islink(file_path):
            target = os.path.realpath(file_path)
            perms_form.addRow("Symlink Target:", self._selectable_label(target))

        perms_group.setLayout(perms_form)
        layout.addWidget(perms_group)

        # --- Close button ---
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.accept)
        close_btn.setDefault(True)
        button_layout.addWidget(close_btn)
        layout.addLayout(button_layout)

        self.setLayout(layout)

    def _selectable_label(self, text):
        """Create a label whose text can be selected/copied"""
        label = QLabel(text)
        label.setTextInteractionFlags(
            Qt.TextInteractionFlag.TextSelectableByMouse |
            Qt.TextInteractionFlag.TextSelectableByKeyboard
        )
        label.setWordWrap(True)
        return label
