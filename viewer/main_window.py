import os
import sys
from PyQt6.QtWidgets import (
    QMainWindow,
    QTextBrowser,
    QMenuBar,
    QStatusBar,
    QVBoxLayout,
    QWidget,
    QFileDialog,
    QMessageBox,
    QDialog,
    QVBoxLayout,
    QLabel,
    QPushButton,
    QHBoxLayout,
    QListWidget,
    QListWidgetItem,
)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal, QSettings
from PyQt6.QtGui import QAction, QIcon, QFont
from .markdown_renderer import MarkdownRenderer


class AboutDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("About MDviewer")
        self.setModal(True)
        self.setFixedSize(400, 300)

        layout = QVBoxLayout()

        title_label = QLabel("MDviewer")
        title_label.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        version_label = QLabel("v0.0.2 2026-01-24 2030 CST")
        version_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        desc_label = QLabel(
            "A simple PyQt6 Markdown viewer with GitHub-style rendering"
        )
        desc_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        desc_label.setWordWrap(True)

        close_button = QPushButton("Close")
        close_button.clicked.connect(self.accept)

        layout.addWidget(title_label)
        layout.addWidget(version_label)
        layout.addWidget(desc_label)
        layout.addStretch()
        layout.addWidget(close_button)

        self.setLayout(layout)


class QuickReferenceDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Quick Reference - MDviewer")
        self.setModal(True)
        self.setFixedSize(600, 500)

        layout = QVBoxLayout()

        # Create a text browser for the reference content
        text_browser = QTextBrowser()
        text_browser.setReadOnly(True)
        text_browser.setFont(QFont("Consolas", 10))

        # Quick reference content
        reference_content = """
        <div style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Helvetica, Arial, sans-serif; padding: 20px; color: #24292e;">
            <h1 style="color: #24292e; border-bottom: 1px solid #e1e4e8; padding-bottom: 0.3em;">MDviewer Quick Reference</h1>
            
            <h2 style="color: #24292e;">Keyboard Shortcuts</h2>
            <table style="border-collapse: collapse; width: 100%; margin-bottom: 20px;">
                <tr style="border-bottom: 1px solid #e1e4e8;">
                    <td style="padding: 8px; font-weight: bold; width: 200px;"><kbd style="background-color: #f6f8fa; padding: 2px 6px; border-radius: 3px; font-family: monospace;">Ctrl+O</kbd></td>
                    <td style="padding: 8px;">Open a markdown file</td>
                </tr>
                <tr style="border-bottom: 1px solid #e1e4e8;">
                    <td style="padding: 8px; font-weight: bold;"><kbd style="background-color: #f6f8fa; padding: 2px 6px; border-radius: 3px; font-family: monospace;">Ctrl+C</kbd></td>
                    <td style="padding: 8px;">Copy selected text</td>
                </tr>
                <tr style="border-bottom: 1px solid #e1e4e8;">
                    <td style="padding: 8px; font-weight: bold;"><kbd style="background-color: #f6f8fa; padding: 2px 6px; border-radius: 3px; font-family: monospace;">Ctrl+A</kbd></td>
                    <td style="padding: 8px;">Select all text</td>
                </tr>
                <tr style="border-bottom: 1px solid #e1e4e8;">
                    <td style="padding: 8px; font-weight: bold;"><kbd style="background-color: #f6f8fa; padding: 2px 6px; border-radius: 3px; font-family: monospace;">Ctrl++</kbd></td>
                    <td style="padding: 8px;">Zoom in</td>
                </tr>
                <tr style="border-bottom: 1px solid #e1e4e8;">
                    <td style="padding: 8px; font-weight: bold;"><kbd style="background-color: #f6f8fa; padding: 2px 6px; border-radius: 3px; font-family: monospace;">Ctrl+-</kbd></td>
                    <td style="padding: 8px;">Zoom out</td>
                </tr>
                <tr style="border-bottom: 1px solid #e1e4e8;">
                    <td style="padding: 8px; font-weight: bold;"><kbd style="background-color: #f6f8fa; padding: 2px 6px; border-radius: 3px; font-family: monospace;">Ctrl+0</kbd></td>
                    <td style="padding: 8px;">Reset zoom</td>
                </tr>
                <tr style="border-bottom: 1px solid #e1e4e8;">
                    <td style="padding: 8px; font-weight: bold;"><kbd style="background-color: #f6f8fa; padding: 2px 6px; border-radius: 3px; font-family: monospace;">Ctrl+Q</kbd></td>
                    <td style="padding: 8px;">Exit application</td>
                </tr>
            </table>

            <h2 style="color: #24292e;">Markdown Syntax</h2>
            <table style="border-collapse: collapse; width: 100%; margin-bottom: 20px;">
                <tr style="border-bottom: 1px solid #e1e4e8;">
                    <td style="padding: 8px; font-weight: bold; width: 200px;">Headers</td>
                    <td style="padding: 8px;"><code style="background-color: #f6f8fa; padding: 2px 4px; border-radius: 3px; font-family: monospace;"># H1, ## H2, ### H3</code></td>
                </tr>
                <tr style="border-bottom: 1px solid #e1e4e8;">
                    <td style="padding: 8px; font-weight: bold;">Bold</td>
                    <td style="padding: 8px;"><code style="background-color: #f6f8fa; padding: 2px 4px; border-radius: 3px; font-family: monospace;">**text**</code></td>
                </tr>
                <tr style="border-bottom: 1px solid #e1e4e8;">
                    <td style="padding: 8px; font-weight: bold;">Italic</td>
                    <td style="padding: 8px;"><code style="background-color: #f6f8fa; padding: 2px 4px; border-radius: 3px; font-family: monospace;">*text*</code></td>
                </tr>
                <tr style="border-bottom: 1px solid #e1e4e8;">
                    <td style="padding: 8px; font-weight: bold;">Code</td>
                    <td style="padding: 8px;"><code style="background-color: #f6f8fa; padding: 2px 4px; border-radius: 3px; font-family: monospace;">`code`</code></td>
                </tr>
                <tr style="border-bottom: 1px solid #e1e4e8;">
                    <td style="padding: 8px; font-weight: bold;">Code Block</td>
                    <td style="padding: 8px;"><code style="background-color: #f6f8fa; padding: 2px 4px; border-radius: 3px; font-family: monospace;">```python<br>code<br>```</code></td>
                </tr>
                <tr style="border-bottom: 1px solid #e1e4e8;">
                    <td style="padding: 8px; font-weight: bold;">Link</td>
                    <td style="padding: 8px;"><code style="background-color: #f6f8fa; padding: 2px 4px; border-radius: 3px; font-family: monospace;">[text](url)</code></td>
                </tr>
                <tr style="border-bottom: 1px solid #e1e4e8;">
                    <td style="padding: 8px; font-weight: bold;">Image</td>
                    <td style="padding: 8px;"><code style="background-color: #f6f8fa; padding: 2px 4px; border-radius: 3px; font-family: monospace;">![alt](url)</code></td>
                </tr>
                <tr style="border-bottom: 1px solid #e1e4e8;">
                    <td style="padding: 8px; font-weight: bold;">List</td>
                    <td style="padding: 8px;"><code style="background-color: #f6f8fa; padding: 2px 4px; border-radius: 3px; font-family: monospace;">- item</code> or <code style="background-color: #f6f8fa; padding: 2px 4px; border-radius: 3px; font-family: monospace;">1. item</code></td>
                </tr>
                <tr style="border-bottom: 1px solid #e1e4e8;">
                    <td style="padding: 8px; font-weight: bold;">Blockquote</td>
                    <td style="padding: 8px;"><code style="background-color: #f6f8fa; padding: 2px 4px; border-radius: 3px; font-family: monospace;">> quote</code></td>
                </tr>
                <tr style="border-bottom: 1px solid #e1e4e8;">
                    <td style="padding: 8px; font-weight: bold;">Table</td>
                    <td style="padding: 8px;"><code style="background-color: #f6f8fa; padding: 2px 4px; border-radius: 3px; font-family: monospace;">|col1|col2|</code></td>
                </tr>
            </table>

            <h2 style="color: #24292e;">Features</h2>
            <ul style="color: #24292e;">
                <li>GitHub-style markdown rendering</li>
                <li>Syntax highlighting for code blocks</li>
                <li>Support for tables, headers, lists, and more</li>
                <li>Recent files tracking</li>
                <li>Session restore (opens last viewed file)</li>
                <li>Command-line file loading</li>
            </ul>
        </div>
        """

        text_browser.setHtml(reference_content)

        close_button = QPushButton("Close")
        close_button.clicked.connect(self.accept)

        layout.addWidget(text_browser)
        layout.addWidget(close_button)

        self.setLayout(layout)


class MainWindow(QMainWindow):
    def __init__(self, initial_file=None):
        super().__init__()
        self.current_file = None
        self.renderer = MarkdownRenderer()
        self.settings = QSettings("MDviewer", "MDviewer")
        self.recent_files = []
        self.initial_file = initial_file

        self.setWindowTitle("MDviewer")

        # Load window geometry and state from settings
        self.load_window_settings()

        # Load recent files from settings
        self.load_recent_files()

        self.setup_ui()
        self.setup_menu()
        self.setup_status_bar()

        # Set up markdown browser with dark theme
        self.text_browser.setFont(QFont("Consolas", 11))
        self.text_browser.setReadOnly(True)

        # Apply dark theme to the text browser
        self.text_browser.setStyleSheet("""
            QTextBrowser {
                background-color: #0d1117;
                color: #c9d1d9;
                border: none;
            }
            QScrollBar:vertical {
                background-color: #161b22;
                width: 12px;
                border: none;
            }
            QScrollBar::handle:vertical {
                background-color: #30363d;
                min-height: 20px;
                border-radius: 6px;
            }
            QScrollBar::handle:vertical:hover {
                background-color: #484f58;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                border: none;
                background: none;
            }
        """)

        # Load file based on priority: command-line arg > last opened file > welcome message
        if self.initial_file:
            self.load_file_from_path(self.initial_file)
        else:
            self.load_last_opened_file()

    def setup_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        layout = QVBoxLayout()
        layout.setContentsMargins(5, 5, 5, 5)

        self.text_browser = QTextBrowser()
        layout.addWidget(self.text_browser)

        central_widget.setLayout(layout)

    def setup_menu(self):
        menubar = self.menuBar()

        # File Menu
        file_menu = menubar.addMenu("&File")

        open_action = QAction("&Open", self)
        open_action.setShortcut("Ctrl+O")
        open_action.setStatusTip("Open a markdown file")
        open_action.triggered.connect(self.open_file)
        file_menu.addAction(open_action)

        # Recent Files submenu
        self.recent_menu = file_menu.addMenu("Open &Recent")
        self.update_recent_files_menu()

        file_menu.addSeparator()

        exit_action = QAction("E&xit", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.setStatusTip("Exit the application")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        # Edit Menu
        edit_menu = menubar.addMenu("&Edit")

        copy_action = QAction("&Copy", self)
        copy_action.setShortcut("Ctrl+C")
        copy_action.setStatusTip("Copy selected text")
        copy_action.triggered.connect(self.text_browser.copy)
        edit_menu.addAction(copy_action)

        select_all_action = QAction("Select &All", self)
        select_all_action.setShortcut("Ctrl+A")
        select_all_action.setStatusTip("Select all text")
        select_all_action.triggered.connect(self.text_browser.selectAll)
        edit_menu.addAction(select_all_action)

        # View Menu
        view_menu = menubar.addMenu("&View")

        zoom_in_action = QAction("Zoom &In", self)
        zoom_in_action.setShortcut("Ctrl++")
        zoom_in_action.setStatusTip("Increase font size")
        zoom_in_action.triggered.connect(self.zoom_in)
        view_menu.addAction(zoom_in_action)

        zoom_out_action = QAction("Zoom &Out", self)
        zoom_out_action.setShortcut("Ctrl+-")
        zoom_out_action.setStatusTip("Decrease font size")
        zoom_out_action.triggered.connect(self.zoom_out)
        view_menu.addAction(zoom_out_action)

        reset_zoom_action = QAction("&Reset Zoom", self)
        reset_zoom_action.setShortcut("Ctrl+0")
        reset_zoom_action.setStatusTip("Reset font size")
        reset_zoom_action.triggered.connect(self.reset_zoom)
        view_menu.addAction(reset_zoom_action)

        # Help Menu
        help_menu = menubar.addMenu("&Help")

        quick_ref_action = QAction("&Quick Reference", self)
        quick_ref_action.setStatusTip("Show keyboard shortcuts and markdown syntax")
        quick_ref_action.triggered.connect(self.show_quick_reference)
        help_menu.addAction(quick_ref_action)

        changelog_action = QAction("&Changelog", self)
        changelog_action.setStatusTip("View the changelog")
        changelog_action.triggered.connect(self.show_changelog)
        help_menu.addAction(changelog_action)

        help_menu.addSeparator()

        about_action = QAction("&About", self)
        about_action.setStatusTip("About MDviewer")
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)

    def setup_status_bar(self):
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Ready")

        # Add version label to the right side of status bar
        version_label = QLabel("v0.0.2 2026-01-24 2030 CST")
        version_label.setStyleSheet("color: #666; font-size: 11px;")
        self.status_bar.addPermanentWidget(version_label)

    def load_file_from_path(self, file_path):
        """Load a markdown file from the given path."""
        if os.path.exists(file_path) and os.path.isfile(file_path):
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()

                # Render markdown to HTML
                html_content = self.renderer.render(content)
                self.text_browser.setHtml(html_content)

                self.current_file = file_path
                self.setWindowTitle(f"MDviewer - {os.path.basename(file_path)}")
                self.status_bar.showMessage(f"Opened: {file_path}")

                # Add to recent files
                self.add_to_recent_files(file_path)
                return True
            except Exception as e:
                # If loading fails, show error
                self.status_bar.showMessage(f"Error loading {file_path}: {str(e)}")
                QMessageBox.critical(self, "Error", f"Could not open file: {str(e)}")
                return False
        else:
            self.status_bar.showMessage(f"File not found: {file_path}")
            QMessageBox.warning(
                self, "File Not Found", f"The file {file_path} does not exist."
            )
            return False

    def load_last_opened_file(self):
        """Load the last opened file from settings."""
        last_file = self.settings.value("last_opened_file")
        if last_file and os.path.exists(last_file):
            try:
                with open(last_file, "r", encoding="utf-8") as f:
                    content = f.read()

                # Render markdown to HTML
                html_content = self.renderer.render(content)
                self.text_browser.setHtml(html_content)

                self.current_file = last_file
                self.setWindowTitle(f"MDviewer - {os.path.basename(last_file)}")
                self.status_bar.showMessage(f"Restored: {last_file}")

                # Add to recent files
                self.add_to_recent_files(last_file)
                return
            except Exception as e:
                # If loading fails, fall back to welcome message
                pass

        # Show welcome message if no last file or loading failed
        self.show_welcome_message()

    def show_welcome_message(self):
        welcome_html = """
        <div style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Helvetica, Arial, sans-serif; text-align: center; padding: 50px; color: #c9d1d9; background-color: #0d1117;">
            <h1 style="color: #c9d1d9; border-bottom: 1px solid #30363d; padding-bottom: 0.3em;">Welcome to MDviewer</h1>
            <p>A simple PyQt6 Markdown viewer with GitHub-style rendering</p>
            <p>Use <strong>File → Open</strong> to open a markdown file, or press <kbd style="background-color: #30363d; padding: 2px 4px; border-radius: 3px; font-family: monospace;">Ctrl+O</kbd></p>
            <br>
            <p>Supported features:</p>
            <ul style="text-align: left; display: inline-block; color: #8b949e;">
                <li>GitHub-style markdown rendering</li>
                <li>Syntax highlighting for code blocks</li>
                <li>Tables, headers, and standard markdown features</li>
            </ul>
        </div>
        """
        self.text_browser.setHtml(welcome_html)

    def open_file(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Open Markdown File",
            "",
            "Markdown Files (*.md *.markdown);;All Files (*)",
        )

        if file_path:
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()

                # Render markdown to HTML
                html_content = self.renderer.render(content)
                self.text_browser.setHtml(html_content)

                self.current_file = file_path
                self.setWindowTitle(f"MDviewer - {os.path.basename(file_path)}")
                self.status_bar.showMessage(f"Opened: {file_path}")

                # Add to recent files
                self.add_to_recent_files(file_path)

            except Exception as e:
                QMessageBox.critical(self, "Error", f"Could not open file: {str(e)}")
                self.status_bar.showMessage("Error opening file")

    def zoom_in(self):
        current_font = self.text_browser.font()
        current_size = current_font.pointSize()
        if current_size < 24:
            current_font.setPointSize(current_size + 1)
            self.text_browser.setFont(current_font)

    def zoom_out(self):
        current_font = self.text_browser.font()
        current_size = current_font.pointSize()
        if current_size > 6:
            current_font.setPointSize(current_size - 1)
            self.text_browser.setFont(current_font)

    def reset_zoom(self):
        font = QFont("Consolas", 11)
        self.text_browser.setFont(font)

    def load_recent_files(self):
        """Load recent files from QSettings."""
        recent_files = self.settings.value("recent_files", [])
        if isinstance(recent_files, list):
            self.recent_files = recent_files
        else:
            self.recent_files = []

    def save_window_settings(self):
        """Save window geometry and state to QSettings."""
        self.settings.setValue("geometry", self.saveGeometry())
        self.settings.setValue("window_state", self.saveState())

    def load_window_settings(self):
        """Load window geometry and state from QSettings."""
        # Restore geometry
        geometry = self.settings.value("geometry")
        if geometry:
            self.restoreGeometry(geometry)
        else:
            # Default size and position if no saved settings
            self.setGeometry(100, 100, 1000, 700)

        # Restore window state (for toolbars, dock widgets, etc.)
        window_state = self.settings.value("window_state")
        if window_state:
            self.restoreState(window_state)

    def save_recent_files(self):
        """Save recent files to QSettings."""
        self.settings.setValue(
            "recent_files", self.recent_files[:10]
        )  # Keep max 10 files

    def add_to_recent_files(self, file_path):
        """Add a file to the recent files list."""
        # Remove if already exists
        if file_path in self.recent_files:
            self.recent_files.remove(file_path)

        # Add to beginning
        self.recent_files.insert(0, file_path)

        # Keep only the most recent 10
        self.recent_files = self.recent_files[:10]

        # Update menu and save
        self.update_recent_files_menu()
        self.save_recent_files()

    def update_recent_files_menu(self):
        """Update the recent files menu."""
        self.recent_menu.clear()

        if not self.recent_files:
            no_files_action = QAction("No recent files", self)
            no_files_action.setEnabled(False)
            self.recent_menu.addAction(no_files_action)
        else:
            for i, file_path in enumerate(self.recent_files):
                if os.path.exists(file_path):
                    action = QAction(f"{i + 1}. {os.path.basename(file_path)}", self)
                    action.setData(file_path)
                    action.setStatusTip(file_path)
                    action.triggered.connect(
                        lambda checked, path=file_path: self.open_recent_file(path)
                    )
                    self.recent_menu.addAction(action)

        if self.recent_files:
            self.recent_menu.addSeparator()
            clear_action = QAction("Clear Recent Files", self)
            clear_action.triggered.connect(self.clear_recent_files)
            self.recent_menu.addAction(clear_action)

    def open_recent_file(self, file_path):
        """Open a recent file."""
        if os.path.exists(file_path):
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()

                # Render markdown to HTML
                html_content = self.renderer.render(content)
                self.text_browser.setHtml(html_content)

                self.current_file = file_path
                self.setWindowTitle(f"MDviewer - {os.path.basename(file_path)}")
                self.status_bar.showMessage(f"Opened: {file_path}")

                # Move to top of recent files
                self.add_to_recent_files(file_path)

            except Exception as e:
                QMessageBox.critical(self, "Error", f"Could not open file: {str(e)}")
                self.status_bar.showMessage("Error opening file")
        else:
            QMessageBox.warning(
                self, "File Not Found", f"The file {file_path} no longer exists."
            )
            # Remove from recent files
            if file_path in self.recent_files:
                self.recent_files.remove(file_path)
                self.update_recent_files_menu()
                self.save_recent_files()

    def clear_recent_files(self):
        """Clear the recent files list."""
        self.recent_files.clear()
        self.update_recent_files_menu()
        self.save_recent_files()

    def closeEvent(self, event):
        """Handle window close event."""
        # Save window settings when closing
        self.save_window_settings()
        self.save_recent_files()
        # Save current file for restore on startup
        if self.current_file:
            self.settings.setValue("last_opened_file", self.current_file)
        super().closeEvent(event)

    def show_quick_reference(self):
        dialog = QuickReferenceDialog(self)
        dialog.exec()

    def show_changelog(self):
        changelog_path = os.path.join(
            os.path.dirname(os.path.dirname(__file__)), "CHANGELOG.md"
        )
        if os.path.exists(changelog_path):
            self.load_file_from_path(changelog_path)
        else:
            QMessageBox.warning(
                self, "File Not Found", f"Changelog file not found: {changelog_path}"
            )

    def show_about(self):
        dialog = AboutDialog(self)
        dialog.exec()
