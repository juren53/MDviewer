#!/usr/bin/env python3
"""
Update Dialog Components for MDviewer

Collection of dialogs for the version update feature.
Matches MDviewer's dark theme styling and PyQt6 architecture.

Author: MDviewer Project
v1.0.0
Created: 2026-01-25
"""

import sys
from PyQt6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QTextEdit,
    QProgressBar,
    QMessageBox,
    QWidget,
)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal, QThread
from PyQt6.QtGui import QFont, QTextCharFormat, QPalette, QColor
from github_version_checker import VersionCheckResult
from git_updater import GitUpdateResult


class VersionCompareDialog(QDialog):
    """Dialog for comparing current and latest versions"""

    def __init__(self, check_result: VersionCheckResult, parent=None, update_method: str = "git"):
        super().__init__(parent)
        self.check_result = check_result
        self.should_update = False
        self.update_method = update_method

        self.setWindowTitle("Update Available")
        self.setModal(True)
        self.setFixedSize(500, 400)
        self.setup_ui()
        self.apply_theme()

    def setup_ui(self):
        layout = QVBoxLayout()

        # Title
        title_label = QLabel("Update Available")
        title_label.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Version comparison
        version_label = QLabel(
            f"Current: {self.check_result.current_version} → Latest: {self.check_result.latest_version}"
        )
        version_label.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        version_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        version_label.setStyleSheet("color: #4CAF50;")  # Green

        # Update method info
        method_text = "via git pull" if self.update_method == "git" else "via GitHub release download"
        method_label = QLabel(f"Update method: {method_text}")
        method_label.setFont(QFont("Arial", 9))
        method_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        method_label.setStyleSheet("color: #8b949e;")  # Gray

        # Release notes
        notes_label = QLabel("Release Notes:")
        notes_label.setFont(QFont("Arial", 11, QFont.Weight.Bold))

        release_notes = QTextEdit()
        release_notes.setReadOnly(True)
        release_notes.setPlainText(
            self.check_result.release_notes or "No release notes available."
        )
        release_notes.setMaximumHeight(150)

        # Buttons
        button_layout = QHBoxLayout()

        update_button = QPushButton("Update Now")
        update_button.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        update_button.clicked.connect(self.accept_update)

        cancel_button = QPushButton("Cancel")
        cancel_button.clicked.connect(self.reject)

        button_layout.addWidget(update_button)
        button_layout.addWidget(cancel_button)

        # Add all widgets
        layout.addWidget(title_label)
        layout.addWidget(version_label)
        layout.addWidget(method_label)
        layout.addWidget(notes_label)
        layout.addWidget(release_notes)
        layout.addLayout(button_layout)

        self.setLayout(layout)

    def apply_theme(self):
        """Apply MDviewer dark theme"""
        self.setStyleSheet("""
            QDialog {
                background-color: #0d1117;
                color: #c9d1d9;
            }
            QLabel {
                color: #c9d1d9;
            }
            QTextEdit {
                background-color: #161b22;
                color: #c9d1d9;
                border: 1px solid #30363d;
                border-radius: 4px;
                padding: 8px;
            }
            QPushButton {
                background-color: #238636;
                color: white;
                border: none;
                padding: 8px 16px;
                font-weight: bold;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #2ea043;
            }
            QPushButton:pressed {
                background-color: #1a7f37;
            }
        """)

        # Style cancel button differently
        cancel_button = self.findChild(QPushButton, "cancel_button")
        if cancel_button:
            cancel_button.setStyleSheet("""
                QPushButton {
                    background-color: #30363d;
                    color: #c9d1d9;
                    border: 1px solid #6e7681;
                    padding: 8px 16px;
                    font-weight: bold;
                    border-radius: 4px;
                }
                QPushButton:hover {
                    background-color: #484f58;
                }
            """)

    def accept_update(self):
        self.should_update = True
        self.accept()


class UpToDateDialog(QDialog):
    """Dialog for when no update is available"""

    def __init__(self, current_version: str, parent=None):
        super().__init__(parent)
        self.current_version = current_version

        self.setWindowTitle("Up to Date")
        self.setModal(True)
        self.setFixedSize(400, 200)
        self.setup_ui()
        self.apply_theme()

    def setup_ui(self):
        layout = QVBoxLayout()

        # Title
        title_label = QLabel("You're Up to Date!")
        title_label.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setStyleSheet("color: #4CAF50;")  # Green

        # Version info
        version_label = QLabel(f"Current version: {self.current_version}")
        version_label.setFont(QFont("Arial", 11))
        version_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Description
        desc_label = QLabel("MDviewer is already running the latest version.")
        desc_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Close button
        close_button = QPushButton("OK")
        close_button.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        close_button.clicked.connect(self.accept)

        layout.addWidget(title_label)
        layout.addWidget(version_label)
        layout.addWidget(desc_label)
        layout.addStretch()
        layout.addWidget(close_button)

        self.setLayout(layout)

    def apply_theme(self):
        """Apply MDviewer dark theme"""
        self.setStyleSheet("""
            QDialog {
                background-color: #0d1117;
                color: #c9d1d9;
            }
            QLabel {
                color: #c9d1d9;
            }
            QPushButton {
                background-color: #238636;
                color: white;
                border: none;
                padding: 8px 16px;
                font-weight: bold;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #2ea043;
            }
        """)


class UpdateProgressDialog(QDialog):
    """Dialog for showing update progress"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Updating MDviewer")
        self.setModal(True)
        self.setFixedSize(400, 150)
        self.setup_ui()
        self.apply_theme()

    def setup_ui(self):
        layout = QVBoxLayout()

        # Status label
        self.status_label = QLabel("Checking for updates...")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 0)  # Indeterminate progress

        layout.addWidget(self.status_label)
        layout.addWidget(self.progress_bar)

        self.setLayout(layout)

    def apply_theme(self):
        """Apply MDviewer dark theme"""
        self.setStyleSheet("""
            QDialog {
                background-color: #0d1117;
                color: #c9d1d9;
            }
            QLabel {
                color: #c9d1d9;
            }
            QProgressBar {
                border: 1px solid #30363d;
                border-radius: 4px;
                text-align: center;
                background-color: #161b22;
            }
            QProgressBar::chunk {
                background-color: #58a6ff;
                border-radius: 3px;
            }
        """)

    def update_status(self, message: str):
        """Update status message"""
        self.status_label.setText(message)

    def set_download_progress(self, percent: int):
        """Set download progress percentage (0-100)"""
        if percent >= 0:
            self.progress_bar.setRange(0, 100)
            self.progress_bar.setValue(percent)
        else:
            # Indeterminate progress
            self.progress_bar.setRange(0, 0)


class UpdateResultDialog(QDialog):
    """Dialog for showing update results"""

    def __init__(self, update_result: GitUpdateResult, parent=None):
        super().__init__(parent)
        self.update_result = update_result

        self.setWindowTitle("Update Result")
        self.setModal(True)
        self.setFixedSize(500, 400)
        self.setup_ui()
        self.apply_theme()

    def setup_ui(self):
        layout = QVBoxLayout()

        if self.update_result.success:
            # Success
            title_label = QLabel("Update Successful!")
            title_label.setFont(QFont("Arial", 16, QFont.Weight.Bold))
            title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            title_label.setStyleSheet("color: #4CAF50;")  # Green

            version_info = QLabel(
                f"Updated: {self.update_result.current_version} → {self.update_result.new_version}"
            )
            version_info.setAlignment(Qt.AlignmentFlag.AlignCenter)

        else:
            # Failed
            title_label = QLabel("Update Failed")
            title_label.setFont(QFont("Arial", 16, QFont.Weight.Bold))
            title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            title_label.setStyleSheet("color: #f85149;")  # Red

            version_info = QLabel(self.update_result.message)
            version_info.setAlignment(Qt.AlignmentFlag.AlignCenter)
            version_info.setWordWrap(True)

        # Output
        output_label = QLabel("Details:")
        output_label.setFont(QFont("Arial", 11, QFont.Weight.Bold))

        output_text = QTextEdit()
        output_text.setReadOnly(True)

        if self.update_result.success:
            output_text.setPlainText(self.update_result.command_output)
        else:
            output_text.setPlainText(self.update_result.error_output)

        output_text.setMaximumHeight(150)

        # Close button
        close_button = QPushButton("OK")
        close_button.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        close_button.clicked.connect(self.accept)

        layout.addWidget(title_label)
        layout.addWidget(version_info)
        layout.addWidget(output_label)
        layout.addWidget(output_text)
        layout.addWidget(close_button)

        self.setLayout(layout)

    def apply_theme(self):
        """Apply MDviewer dark theme"""
        self.setStyleSheet("""
            QDialog {
                background-color: #0d1117;
                color: #c9d1d9;
            }
            QLabel {
                color: #c9d1d9;
            }
            QTextEdit {
                background-color: #161b22;
                color: #c9d1d9;
                border: 1px solid #30363d;
                border-radius: 4px;
                padding: 8px;
            }
            QPushButton {
                background-color: #238636;
                color: white;
                border: none;
                padding: 8px 16px;
                font-weight: bold;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #2ea043;
            }
        """)


class ErrorDialog(QDialog):
    """Dialog for showing errors"""

    def __init__(self, error_message: str, parent=None):
        super().__init__(parent)
        self.error_message = error_message

        self.setWindowTitle("Error")
        self.setModal(True)
        self.setFixedSize(400, 200)
        self.setup_ui()
        self.apply_theme()

    def setup_ui(self):
        layout = QVBoxLayout()

        # Error icon and message
        title_label = QLabel("An Error Occurred")
        title_label.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setStyleSheet("color: #f85149;")  # Red

        error_label = QLabel(self.error_message)
        error_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        error_label.setWordWrap(True)

        # Close button
        close_button = QPushButton("OK")
        close_button.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        close_button.clicked.connect(self.accept)

        layout.addWidget(title_label)
        layout.addWidget(error_label)
        layout.addStretch()
        layout.addWidget(close_button)

        self.setLayout(layout)

    def apply_theme(self):
        """Apply MDviewer dark theme"""
        self.setStyleSheet("""
            QDialog {
                background-color: #0d1117;
                color: #c9d1d9;
            }
            QLabel {
                color: #c9d1d9;
            }
            QPushButton {
                background-color: #30363d;
                color: #c9d1d9;
                border: 1px solid #6e7681;
                padding: 8px 16px;
                font-weight: bold;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #484f58;
            }
        """)
