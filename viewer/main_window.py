import os
import sys
from PyQt6.QtWidgets import (
    QMainWindow,
    QTextBrowser,
    QTextEdit,
    QMenuBar,
    QStatusBar,
    QVBoxLayout,
    QWidget,
    QFileDialog,
    QMessageBox,
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QLineEdit,
    QCheckBox,
    QListWidget,
    QListWidgetItem,
)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal, QSettings
from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import (
    QAction,
    QIcon,
    QFont,
    QTextCursor,
    QTextCharFormat,
    QPalette,
    QColor,
    QTextDocument,
)
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

        version_label = QLabel("v0.0.3 2026-01-25 0525 CST")
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
                    <td style="padding: 8px; font-weight: bold; width: 200px;"><kbd style="background-color: #f6f8fa; padding: 2px 6px; border-radius: 3px; font-family: monospace;">Ctrl+F</kbd></td>
                    <td style="padding: 8px;">Find text in document</td>
                </tr>
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
                    <td style="padding: 8px; font-weight: bold;"><kbd style="background-color: #f6f8fa; padding: 2px 6px; border-radius: 3px; font-family: monospace;">↑</kbd> / <kbd style="background-color: #f6f8fa; padding: 2px 6px; border-radius: 3px; font-family: monospace;">↓</kbd></td>
                    <td style="padding: 8px;">Navigate to previous/next match</td>
                </tr>
                <tr style="border-bottom: 1px solid #e1e4e8;">
                    <td style="padding: 8px; font-weight: bold;"><kbd style="background-color: #f6f8fa; padding: 2px 6px; border-radius: 3px; font-family: monospace;">Enter</kbd></td>
                    <td style="padding: 8px;">Find next occurrence</td>
                </tr>
                <tr style="border-bottom: 1px solid #e1e4e8;">
                    <td style="padding: 8px; font-weight: bold;"><kbd style="background-color: #f6f8fa; padding: 2px 6px; border-radius: 3px; font-family: monospace;">Esc</kbd></td>
                    <td style="padding: 8px;">Close Find dialog</td>
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


class ThemeManager:
    """Centralized theme management for Fusion style"""

    @staticmethod
    def get_fusion_dark_palette():
        """Create dark theme palette for Fusion style"""
        palette = QPalette()
        # Window colors
        palette.setColor(QPalette.ColorRole.Window, QColor(45, 45, 45))
        palette.setColor(QPalette.ColorRole.WindowText, QColor(187, 187, 187))
        # Base colors (text input areas)
        palette.setColor(QPalette.ColorRole.Base, QColor(30, 30, 30))
        palette.setColor(QPalette.ColorRole.AlternateBase, QColor(45, 45, 45))
        # Text colors
        palette.setColor(QPalette.ColorRole.Text, QColor(187, 187, 187))
        # Button colors
        palette.setColor(QPalette.ColorRole.Button, QColor(45, 45, 45))
        palette.setColor(QPalette.ColorRole.ButtonText, QColor(187, 187, 187))
        # Highlight colors (for search functionality)
        palette.setColor(QPalette.ColorRole.Highlight, QColor(255, 215, 0))  # Gold
        palette.setColor(QPalette.ColorRole.HighlightedText, QColor(0, 0, 0))  # Black

        return palette

    @staticmethod
    def get_fusion_light_palette():
        """Create light theme palette for Fusion style"""
        palette = QPalette()
        # Window colors
        palette.setColor(QPalette.ColorRole.Window, QColor(240, 240, 240))
        palette.setColor(QPalette.ColorRole.WindowText, QColor(0, 0, 0))
        # Base colors
        palette.setColor(QPalette.ColorRole.Base, QColor(255, 255, 255))
        palette.setColor(QPalette.ColorRole.AlternateBase, QColor(245, 245, 245))
        # Text colors
        palette.setColor(QPalette.ColorRole.Text, QColor(0, 0, 0))
        # Button colors
        palette.setColor(QPalette.ColorRole.Button, QColor(240, 240, 240))
        palette.setColor(QPalette.ColorRole.ButtonText, QColor(0, 0, 0))
        # Highlight colors
        palette.setColor(QPalette.ColorRole.Highlight, QColor(3, 102, 216))  # Blue
        palette.setColor(
            QPalette.ColorRole.HighlightedText, QColor(255, 255, 255)
        )  # White

        return palette

    @staticmethod
    def get_search_css(theme_name="dark"):
        """Generate CSS for search highlighting that works with Fusion"""
        if theme_name == "dark":
            return """
                QTextBrowser {
                    selection-background-color: #ffd700 !important;
                    selection-color: #000000 !important;
                    font-weight: bold !important;
                    border-radius: 2px !important;
                }
                /* Additional highlighting for multiple matches */
                .search-current {
                    background-color: #ffd700 !important;
                    color: #000000 !important;
                    font-weight: bold !important;
                }
                .search-other {
                    background-color: #ff8c00 !important;
                    color: #000000 !important;
                }
            """
        else:  # light theme
            return """
                QTextBrowser {
                    selection-background-color: #0366d8 !important;
                    selection-color: #ffffff !important;
                    font-weight: bold !important;
                    border-radius: 2px !important;
                }
                .search-current {
                    background-color: #0366d8 !important;
                    color: #ffffff !important;
                    font-weight: bold !important;
                }
                .search-other {
                    background-color: #91a7ff !important;
                    color: #000000 !important;
                }
            """


class FindDialog(QDialog):
    """Simple Find dialog similar to Windows Notepad"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Find")
        self.setModal(True)
        self.setFixedSize(350, 200)

        # Search state
        self.search_text = ""
        self.current_match_index = 0
        self.total_matches = 0
        self.case_sensitive = False
        self.whole_word = False

        # Store reference to parent's text browser for search operations
        self.text_browser = None

        self.setup_ui()
        self.connect_signals()

    def setup_ui(self):
        """Create the dialog UI components"""
        layout = QVBoxLayout()

        # Find what label and input
        find_label = QLabel("Find what:")
        find_label.setStyleSheet("font-weight: bold; color: #000;")

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Enter search text...")
        self.search_input.setStyleSheet("""
            QLineEdit {
                border: 2px solid #ccc;
                border-radius: 4px;
                padding: 6px 8px;
                font-size: 12px;
                background-color: #fff;
                color: #000;
            }
            QLineEdit:focus {
                border-color: #007acc;
                outline: none;
            }
        """)

        # Search options
        self.case_checkbox = QCheckBox("Match case")
        self.case_checkbox.setStyleSheet("""
            QCheckBox {
                spacing: 8px;
                font-weight: bold;
                color: #000;
            }
            QCheckBox::indicator {
                width: 18px;
                height: 18px;
                border: 2px solid #666;
                border-radius: 4px;
                background-color: #fff;
            }
            QCheckBox::indicator:checked {
                background-color: #007acc;
                border-color: #007acc;
            }
        """)

        self.whole_checkbox = QCheckBox("Whole word")
        self.whole_checkbox.setStyleSheet(self.case_checkbox.styleSheet())

        # Buttons and counter layout
        button_layout = QHBoxLayout()

        self.find_next_btn = QPushButton("Find Next")
        self.find_next_btn.setStyleSheet("""
            QPushButton {
                background-color: #007acc;
                color: white;
                border: none;
                padding: 8px 16px;
                font-weight: bold;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #005a9e;
            }
            QPushButton:pressed {
                background-color: #004578;
            }
        """)

        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.setStyleSheet("""
            QPushButton {
                background-color: #f8f9fa;
                color: #000;
                border: 1px solid #ccc;
                padding: 8px 16px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #e9ecef;
                border-color: #adb5bd;
            }
            QPushButton:pressed {
                background-color: #dee2e6;
            }
        """)

        self.match_counter = QLabel("0/0 matches")
        self.match_counter.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.match_counter.setStyleSheet("""
            QLabel {
                color: #000;
                background-color: #fff3cd;
                border: 1px solid #ffeaa7;
                border-radius: 4px;
                padding: 4px 8px;
                font-size: 11px;
                font-weight: bold;
            }
        """)

        button_layout.addWidget(self.find_next_btn)
        button_layout.addWidget(self.cancel_btn)

        # Add all components to main layout
        layout.addWidget(find_label)
        layout.addWidget(self.search_input)
        layout.addWidget(self.case_checkbox)
        layout.addWidget(self.whole_checkbox)
        layout.addLayout(button_layout)
        layout.addWidget(self.match_counter)

        self.setLayout(layout)

        # Set focus to search input when dialog opens
        self.search_input.setFocus()
        self.search_input.selectAll()

    def connect_signals(self):
        """Connect dialog signals to handlers"""
        self.find_next_btn.clicked.connect(self.find_next)
        self.cancel_btn.clicked.connect(self.reject)
        self.search_input.textChanged.connect(self.on_search_text_changed)
        self.case_checkbox.toggled.connect(self.on_options_changed)
        self.whole_checkbox.toggled.connect(self.on_options_changed)

    def keyPressEvent(self, event):
        """Handle keyboard navigation"""
        if event.key() == Qt.Key.Key_Up:
            self.find_previous()
        elif event.key() == Qt.Key.Key_Down:
            self.find_next()
        elif event.key() == Qt.Key.Key_Enter or event.key() == Qt.Key.Key_Return:
            self.find_next()
        elif event.key() == Qt.Key.Key_Escape:
            self.reject()
        else:
            super().keyPressEvent(event)

    def set_text_browser(self, text_browser):
        """Set reference to the main window's text browser"""
        self.text_browser = text_browser

    def on_search_text_changed(self):
        """Handle search text changes"""
        self.search_text = self.search_input.text()
        if self.search_text:
            self.perform_search()
        else:
            self.clear_highlights()
            self.update_match_counter(0, 0)

    def on_options_changed(self):
        """Handle search option changes"""
        self.case_sensitive = self.case_checkbox.isChecked()
        self.whole_word = self.whole_checkbox.isChecked()
        if self.search_text:
            self.perform_search()

    def build_find_flags(self):
        """Build QTextDocument.FindFlags based on options"""
        flags = QTextDocument.FindFlag(0)
        if self.case_sensitive:
            flags |= QTextDocument.FindFlag.FindCaseSensitively
        if self.whole_word:
            flags |= QTextDocument.FindFlag.FindWholeWords
        return flags

    def perform_search(self):
        """Find all occurrences of search text"""
        if not self.text_browser or not self.search_text:
            return

        # Clear previous highlights
        self.clear_highlights()

        # Find all matches
        document = self.text_browser.document()
        cursor = QTextCursor(document)
        cursor.movePosition(QTextCursor.MoveOperation.Start)

        matches = []
        while True:
            cursor = document.find(self.search_text, cursor, self.build_find_flags())
            if cursor.isNull():
                break

            matches.append(cursor)
            cursor.setPosition(cursor.selectionEnd())

        self.matches = matches
        self.total_matches = len(matches)

        if self.total_matches > 0:
            self.current_match_index = 0
            self.highlight_all_matches()
            self.navigate_to_match(0)

        self.update_match_counter(self.current_match_index + 1, self.total_matches)

    def find_next(self):
        """Navigate to next match"""
        if self.total_matches == 0:
            return

        self.current_match_index = (self.current_match_index + 1) % self.total_matches
        self.navigate_to_match(self.current_match_index)
        self.update_match_counter(self.current_match_index + 1, self.total_matches)

    def find_previous(self):
        """Navigate to previous match"""
        if self.total_matches == 0:
            return

        self.current_match_index = (
            self.current_match_index - 1 + self.total_matches
        ) % self.total_matches
        self.navigate_to_match(self.current_match_index)
        self.update_match_counter(self.current_match_index + 1, self.total_matches)

    def highlight_all_matches(self):
        """Highlight all search matches with maximum contrast colors"""
        if not self.text_browser:
            return

        # Use pure, bright colors that should be impossible to miss
        current_highlight = QColor(255, 255, 0)  # Pure yellow
        other_highlight = QColor(255, 165, 0)  # Pure orange
        current_text = QColor(0, 0, 0)  # Black text
        other_text = QColor(0, 0, 0)  # Black text

        extra_selections = []
        for i, match in enumerate(self.matches):
            selection = QTextEdit.ExtraSelection()
            selection.cursor = match

            format = QTextCharFormat()
            if i == self.current_match_index:
                # Current match: maximum visibility
                format.setBackground(current_highlight)
                format.setForeground(current_text)
                format.setFontWeight(QFont.Weight.Bold)
                format.setFontUnderline(True)
            else:
                # Other matches: clear but less prominent
                format.setBackground(other_highlight)
                format.setForeground(other_text)

            extra_selections.append(selection)

        # Apply selections multiple times to override CSS
        self.text_browser.setExtraSelections(extra_selections)

        # Force immediate visual update
        self.text_browser.viewport().update()
        self.text_browser.update()

        # Additional delayed update to ensure persistence
        QTimer.singleShot(100, self.force_highlight_update)

    def force_highlight_update(self):
        """Force highlights to reapply"""
        if hasattr(self, "matches") and self.matches:
            # Reapply selections after CSS processing
            self.highlight_all_matches()

        # Delayed update to ensure CSS doesn't override
        QTimer.singleShot(10, self.force_highlight_update)

    def force_highlight_update(self):
        """Force another update to ensure highlights are visible"""
        print("DEBUG: Force updating highlights")
        self.text_browser.viewport().update()
        self.text_browser.update()

    def navigate_to_match(self, index):
        """Navigate to specific match and highlight it"""
        if not self.matches or index >= len(self.matches):
            return

        # Clear previous selection and set new one
        self.text_browser.setTextCursor(self.matches[index])
        self.highlight_all_matches()

    def clear_highlights(self):
        """Clear all search highlights"""
        if self.text_browser:
            self.text_browser.setExtraSelections([])

    def update_match_counter(self, current, total):
        """Update the match counter display"""
        if total == 0:
            self.match_counter.setText("No matches")
        else:
            self.match_counter.setText(f"{current}/{total} matches")

    def showEvent(self, event):
        """Handle dialog show event"""
        super().showEvent(event)
        # Focus on search input and select any existing text
        self.search_input.setFocus()
        if self.search_input.text():
            self.search_input.selectAll()
        # Trigger initial search if there's text
        self.on_search_text_changed()

    def closeEvent(self, event):
        """Handle dialog close event"""
        self.clear_highlights()
        super().closeEvent(event)


class MainWindow(QMainWindow):
    def __init__(self, initial_file=None):
        super().__init__()
        self.current_file = None
        self.renderer = MarkdownRenderer()
        self.settings = QSettings("MDviewer", "MDviewer")
        self.recent_files = []
        self.initial_file = initial_file
        self.find_dialog = None
        self.current_theme = (
            "dark"  # Default theme (will be overwritten by load_theme_settings)
        )

        self.setWindowTitle("MDviewer")

        # Load window geometry and state from settings
        self.load_window_settings()

        # Load theme from settings
        self.load_theme_settings()

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

        # Set theme in renderer
        self.renderer.current_theme = self.current_theme

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

        find_action = QAction("&Find...", self)
        find_action.setShortcut("Ctrl+F")
        find_action.setStatusTip("Find text in document")
        find_action.triggered.connect(self.show_find_dialog)
        edit_menu.addAction(find_action)

        edit_menu.addSeparator()

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

        view_menu.addSeparator()

        # Theme submenu
        theme_menu = view_menu.addMenu("&Theme")

        # Dark theme action
        self.dark_theme_action = QAction("&Dark Theme", self)
        self.dark_theme_action.setCheckable(True)
        self.dark_theme_action.setChecked(self.current_theme == "dark")
        self.dark_theme_action.setStatusTip("Switch to dark theme")
        self.dark_theme_action.triggered.connect(lambda: self.switch_theme("dark"))
        theme_menu.addAction(self.dark_theme_action)

        # Light theme action
        self.light_theme_action = QAction("&Light Theme", self)
        self.light_theme_action.setCheckable(True)
        self.light_theme_action.setChecked(self.current_theme == "light")
        self.light_theme_action.setStatusTip("Switch to light theme")
        self.light_theme_action.triggered.connect(lambda: self.switch_theme("light"))
        theme_menu.addAction(self.light_theme_action)

        # Theme toggle action with keyboard shortcut
        toggle_theme_action = QAction("&Toggle Theme", self)
        toggle_theme_action.setShortcut("Ctrl+T")
        toggle_theme_action.setStatusTip("Toggle between dark and light themes")
        toggle_theme_action.triggered.connect(self.toggle_theme)
        view_menu.addAction(toggle_theme_action)

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
        version_label = QLabel("v0.0.3 2026-01-25 0525 CST")
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

        # Save current theme preference
        self.settings.setValue("current_theme", self.current_theme)

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

    def apply_theme(self, theme_name):
        """Apply Fusion style with theme-specific palette"""
        # Get theme-specific palette
        if theme_name == "dark":
            palette = ThemeManager.get_fusion_dark_palette()
            search_css = ThemeManager.get_search_css("dark")
        else:  # light theme
            palette = ThemeManager.get_fusion_light_palette()
            search_css = ThemeManager.get_search_css("light")

        # Apply palette globally via QSettings (works during initialization)
        self.settings.setValue("theme_palette", palette)
        self.settings.setValue("theme_css", search_css)

        # Apply to current text browser if it exists
        if hasattr(self, "text_browser"):
            self.text_browser.setStyleSheet(search_css)

    def switch_theme(self, theme_name):
        """Switch between dark and light themes"""
        if theme_name == self.current_theme:
            return

        # Update current theme
        self.current_theme = theme_name

        # Apply theme via existing apply_theme method
        self.apply_theme(theme_name)

        # Update renderer theme
        self.renderer.current_theme = theme_name

        # Reload current document if open
        if self.current_file:
            self.load_file_from_path(self.current_file)
        else:
            # Reload welcome message
            self.show_welcome_message()

        # Save theme preference
        self.settings.setValue("current_theme", theme_name)

        # Update menu check states
        self.update_theme_menu_states()

        # Update status bar
        self.status_bar.showMessage(f"Theme changed to {theme_name}", 2000)

    def toggle_theme(self):
        """Toggle between dark and light themes"""
        new_theme = "light" if self.current_theme == "dark" else "dark"
        self.switch_theme(new_theme)

    def update_theme_menu_states(self):
        """Update menu action check states based on current theme"""
        if hasattr(self, "dark_theme_action") and hasattr(self, "light_theme_action"):
            self.dark_theme_action.setChecked(self.current_theme == "dark")
            self.light_theme_action.setChecked(self.current_theme == "light")

    def load_theme_settings(self):
        """Load theme preference from settings"""
        saved_theme = self.settings.value("current_theme", "dark")
        self.current_theme = saved_theme
        self.apply_theme(self.current_theme)
        self.renderer.current_theme = self.current_theme

    def setup_find_dialog(self):
        """Create find dialog instance"""
        self.find_dialog = FindDialog(self)
        self.find_dialog.set_text_browser(self.text_browser)

    def show_find_dialog(self):
        """Show Find dialog"""
        if not self.find_dialog:
            self.setup_find_dialog()

        # Position dialog relative to main window
        self.find_dialog.show()
        self.find_dialog.raise_()
        self.find_dialog.activateWindow()

    def show_about(self):
        dialog = AboutDialog(self)
        dialog.exec()
