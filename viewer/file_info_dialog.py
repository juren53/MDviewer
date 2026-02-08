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


# File extension to human-readable description
_FILE_TYPE_DESCRIPTIONS = {
    '.md':        'Markdown document',
    '.markdown':  'Markdown document',
    '.mkd':       'Markdown document',
    '.txt':       'Plain text file',
    '.text':      'Plain text file',
    '.log':       'Log file',
    '.csv':       'Comma-separated values file',
    '.tsv':       'Tab-separated values file',
    '.json':      'JSON data file',
    '.xml':       'XML document',
    '.yaml':      'YAML configuration file',
    '.yml':       'YAML configuration file',
    '.toml':      'TOML configuration file',
    '.ini':       'INI configuration file',
    '.cfg':       'Configuration file',
    '.conf':      'Configuration file',
    '.html':      'HTML document',
    '.htm':       'HTML document',
    '.css':       'CSS stylesheet',
    '.js':        'JavaScript source file',
    '.ts':        'TypeScript source file',
    '.py':        'Python source file',
    '.pyw':       'Python windowed script',
    '.rb':        'Ruby source file',
    '.java':      'Java source file',
    '.c':         'C source file',
    '.h':         'C/C++ header file',
    '.cpp':       'C++ source file',
    '.hpp':       'C++ header file',
    '.cs':        'C# source file',
    '.go':        'Go source file',
    '.rs':        'Rust source file',
    '.sh':        'Shell script',
    '.bash':      'Bash shell script',
    '.zsh':       'Zsh shell script',
    '.bat':       'Windows batch file',
    '.cmd':       'Windows command script',
    '.ps1':       'PowerShell script',
    '.sql':       'SQL database script',
    '.r':         'R statistical script',
    '.tex':       'LaTeX document',
    '.bib':       'BibTeX bibliography file',
    '.rst':       'reStructuredText document',
    '.adoc':      'AsciiDoc document',
    '.org':       'Org-mode document',
    '.pdf':       'PDF document',
    '.doc':       'Microsoft Word document',
    '.docx':      'Microsoft Word document',
    '.xls':       'Microsoft Excel spreadsheet',
    '.xlsx':      'Microsoft Excel spreadsheet',
    '.ppt':       'Microsoft PowerPoint presentation',
    '.pptx':      'Microsoft PowerPoint presentation',
    '.odt':       'OpenDocument text file',
    '.ods':       'OpenDocument spreadsheet',
    '.odp':       'OpenDocument presentation',
    '.rtf':       'Rich Text Format file',
    '.png':       'PNG image',
    '.jpg':       'JPEG image',
    '.jpeg':      'JPEG image',
    '.gif':       'GIF image',
    '.svg':       'SVG vector image',
    '.bmp':       'Bitmap image',
    '.webp':      'WebP image',
    '.ico':       'Icon file',
    '.icns':      'macOS icon file',
    '.mp3':       'MP3 audio file',
    '.wav':       'WAV audio file',
    '.mp4':       'MP4 video file',
    '.avi':       'AVI video file',
    '.mkv':       'Matroska video file',
    '.zip':       'ZIP archive',
    '.tar':       'TAR archive',
    '.gz':        'Gzip compressed file',
    '.bz2':       'Bzip2 compressed file',
    '.xz':        'XZ compressed file',
    '.7z':        '7-Zip archive',
    '.rar':       'RAR archive',
    '.deb':       'Debian package',
    '.rpm':       'RPM package',
    '.exe':       'Windows executable',
    '.dll':       'Windows dynamic library',
    '.so':        'Shared object library',
    '.AppImage':  'Linux AppImage application',
    '.desktop':   'Linux desktop entry file',
    '.spec':      'PyInstaller spec file',
    '.env':       'Environment variables file',
    '.gitignore': 'Git ignore rules',
    '.dockerignore': 'Docker ignore rules',
    '.lock':      'Lock file',
    '.pid':       'Process ID file',
}


def _describe_file_type(ext):
    """Return a human-readable file type description"""
    if not ext:
        return "File (no extension)"

    # Try exact match first, then case-insensitive
    desc = _FILE_TYPE_DESCRIPTIONS.get(ext)
    if not desc:
        desc = _FILE_TYPE_DESCRIPTIONS.get(ext.lower())
    if desc:
        return f"{ext.lstrip('.').upper()} — {desc}"

    # Fallback: just the extension
    return f"{ext.lstrip('.').upper()} file"


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
        file_type = _describe_file_type(ext)
        identity_form.addRow("Type:", QLabel(file_type))

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
