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
from PyQt6.QtCore import Qt, QThread, QTimer, pyqtSignal, QSettings, QObject
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
from .color_settings_dialog import ColorSettingsDialog
from .theme_manager import get_theme_registry
from .update_dialogs import (
    VersionCompareDialog,
    UpToDateDialog,
    UpdateProgressDialog,
    UpdateResultDialog,
    ErrorDialog,
)
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from github_version_checker import GitHubVersionChecker
from git_updater import GitUpdater
from release_downloader import ReleaseDownloader
from version import get_semver
from version import __version__, __version_date__
from pyqt_app_info import AppIdentity, gather_info
from pyqt_app_info.qt import AboutDialog


class QuickReferenceDialog(QDialog):
    def __init__(self, parent=None, theme="dark", custom_colors=None):
        super().__init__(parent)
        self.setWindowTitle("Quick Reference - MDviewer")
        self.setModal(True)
        self.setFixedSize(600, 500)

        # Theme colors - match Fusion palette from ThemeManager
        if theme == "dark":
            bg_color = "#2d2d2d"  # Window color (45, 45, 45)
            text_color = "#bbbbbb"  # Text color (187, 187, 187)
            heading_color = "#6db3f2"  # Softer blue for headings
            border_color = "#444444"  # Subtle border
            code_bg = "#1e1e1e"  # Base color (30, 30, 30)
            btn_bg = "#3d3d3d"
            btn_hover = "#4d4d4d"
        else:  # light theme
            bg_color = "#f0f0f0"  # Window color (240, 240, 240)
            text_color = "#000000"  # Text color
            heading_color = "#0366d8"  # Blue for headings
            border_color = "#cccccc"  # Subtle border
            code_bg = "#e8e8e8"  # Slightly darker than background
            btn_bg = "#e0e0e0"
            btn_hover = "#d0d0d0"

        # Apply custom heading color if provided
        if custom_colors and "heading_color" in custom_colors:
            heading_color = custom_colors["heading_color"]

        # Style the dialog itself
        self.setStyleSheet(f"""
            QDialog {{
                background-color: {bg_color};
            }}
            QPushButton {{
                background-color: {btn_bg};
                color: {text_color};
                border: 1px solid {border_color};
                padding: 8px 16px;
                border-radius: 4px;
            }}
            QPushButton:hover {{
                background-color: {btn_hover};
            }}
        """)

        layout = QVBoxLayout()

        # Create a text browser for the reference content
        text_browser = QTextBrowser()
        text_browser.setReadOnly(True)
        text_browser.setFont(QFont("Consolas", 10))
        text_browser.setStyleSheet(
            f"background-color: {bg_color}; color: {text_color}; border: none;"
        )

        # Quick reference content - theme aware
        reference_content = f"""
        <div style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Helvetica, Arial, sans-serif; padding: 20px; color: {text_color}; background-color: {bg_color};">
            <h1 style="color: {heading_color}; border-bottom: 1px solid {border_color}; padding-bottom: 0.3em;">MDviewer Quick Reference</h1>

            <h2 style="color: {heading_color};">Keyboard Shortcuts</h2>
            <table style="border-collapse: collapse; width: 100%; margin-bottom: 20px;">
                <tr style="border-bottom: 1px solid {border_color};">
                    <td style="padding: 8px; font-weight: bold; width: 200px; color: {text_color};"><kbd style="background-color: {code_bg}; color: {text_color}; padding: 2px 6px; border-radius: 3px; font-family: monospace; border: 1px solid {border_color};">Ctrl+O</kbd></td>
                    <td style="padding: 8px; color: {text_color};">Open a markdown file</td>
                </tr>
                <tr style="border-bottom: 1px solid {border_color};">
                    <td style="padding: 8px; font-weight: bold; color: {text_color};"><kbd style="background-color: {code_bg}; color: {text_color}; padding: 2px 6px; border-radius: 3px; font-family: monospace; border: 1px solid {border_color};">Ctrl+F</kbd></td>
                    <td style="padding: 8px; color: {text_color};">Find text in document</td>
                </tr>
                <tr style="border-bottom: 1px solid {border_color};">
                    <td style="padding: 8px; font-weight: bold; color: {text_color};"><kbd style="background-color: {code_bg}; color: {text_color}; padding: 2px 6px; border-radius: 3px; font-family: monospace; border: 1px solid {border_color};">F5</kbd></td>
                    <td style="padding: 8px; color: {text_color};">Refresh current document</td>
                </tr>
                <tr style="border-bottom: 1px solid {border_color};">
                    <td style="padding: 8px; font-weight: bold; color: {text_color};"><kbd style="background-color: {code_bg}; color: {text_color}; padding: 2px 6px; border-radius: 3px; font-family: monospace; border: 1px solid {border_color};">Ctrl+C</kbd></td>
                    <td style="padding: 8px; color: {text_color};">Copy selected text</td>
                </tr>
                <tr style="border-bottom: 1px solid {border_color};">
                    <td style="padding: 8px; font-weight: bold; color: {text_color};"><kbd style="background-color: {code_bg}; color: {text_color}; padding: 2px 6px; border-radius: 3px; font-family: monospace; border: 1px solid {border_color};">Ctrl+A</kbd></td>
                    <td style="padding: 8px; color: {text_color};">Select all text</td>
                </tr>
                <tr style="border-bottom: 1px solid {border_color};">
                    <td style="padding: 8px; font-weight: bold; color: {text_color};"><kbd style="background-color: {code_bg}; color: {text_color}; padding: 2px 6px; border-radius: 3px; font-family: monospace; border: 1px solid {border_color};">Ctrl+T</kbd></td>
                    <td style="padding: 8px; color: {text_color};">Toggle dark/light theme</td>
                </tr>
                <tr style="border-bottom: 1px solid {border_color};">
                    <td style="padding: 8px; font-weight: bold; color: {text_color};"><kbd style="background-color: {code_bg}; color: {text_color}; padding: 2px 6px; border-radius: 3px; font-family: monospace; border: 1px solid {border_color};">Ctrl+P</kbd></td>
                    <td style="padding: 8px; color: {text_color};">Toggle paragraph marks</td>
                </tr>
                <tr style="border-bottom: 1px solid {border_color};">
                    <td style="padding: 8px; font-weight: bold; color: {text_color};"><kbd style="background-color: {code_bg}; color: {text_color}; padding: 2px 6px; border-radius: 3px; font-family: monospace; border: 1px solid {border_color};">Ctrl+U</kbd></td>
                    <td style="padding: 8px; color: {text_color};">Check for updates</td>
                </tr>
                <tr style="border-bottom: 1px solid {border_color};">
                    <td style="padding: 8px; font-weight: bold; color: {text_color};"><kbd style="background-color: {code_bg}; color: {text_color}; padding: 2px 6px; border-radius: 3px; font-family: monospace; border: 1px solid {border_color};">Ctrl++</kbd> / <kbd style="background-color: {code_bg}; color: {text_color}; padding: 2px 6px; border-radius: 3px; font-family: monospace; border: 1px solid {border_color};">Ctrl+-</kbd></td>
                    <td style="padding: 8px; color: {text_color};">Zoom in / out</td>
                </tr>
                <tr style="border-bottom: 1px solid {border_color};">
                    <td style="padding: 8px; font-weight: bold; color: {text_color};"><kbd style="background-color: {code_bg}; color: {text_color}; padding: 2px 6px; border-radius: 3px; font-family: monospace; border: 1px solid {border_color};">Ctrl+0</kbd></td>
                    <td style="padding: 8px; color: {text_color};">Reset zoom</td>
                </tr>
                <tr style="border-bottom: 1px solid {border_color};">
                    <td style="padding: 8px; font-weight: bold; color: {text_color};"><kbd style="background-color: {code_bg}; color: {text_color}; padding: 2px 6px; border-radius: 3px; font-family: monospace; border: 1px solid {border_color};">Ctrl+Q</kbd></td>
                    <td style="padding: 8px; color: {text_color};">Exit application</td>
                </tr>
                <tr style="border-bottom: 1px solid {border_color};">
                    <td style="padding: 8px; font-weight: bold; color: {text_color};"><kbd style="background-color: {code_bg}; color: {text_color}; padding: 2px 6px; border-radius: 3px; font-family: monospace; border: 1px solid {border_color};">Space</kbd></td>
                    <td style="padding: 8px; color: {text_color};">Page forward</td>
                </tr>
                <tr style="border-bottom: 1px solid {border_color};">
                    <td style="padding: 8px; font-weight: bold; color: {text_color};"><kbd style="background-color: {code_bg}; color: {text_color}; padding: 2px 6px; border-radius: 3px; font-family: monospace; border: 1px solid {border_color};">b</kbd></td>
                    <td style="padding: 8px; color: {text_color};">Page backward</td>
                </tr>
            </table>

            <h2 style="color: {heading_color};">Markdown Syntax</h2>
            <table style="border-collapse: collapse; width: 100%; margin-bottom: 20px;">
                <tr style="border-bottom: 1px solid {border_color};">
                    <td style="padding: 8px; font-weight: bold; width: 200px; color: {text_color};">Headers</td>
                    <td style="padding: 8px; color: {text_color};"><code style="background-color: {code_bg}; color: {text_color}; padding: 2px 4px; border-radius: 3px; font-family: monospace;"># H1, ## H2, ### H3</code></td>
                </tr>
                <tr style="border-bottom: 1px solid {border_color};">
                    <td style="padding: 8px; font-weight: bold; color: {text_color};">Bold / Italic</td>
                    <td style="padding: 8px; color: {text_color};"><code style="background-color: {code_bg}; color: {text_color}; padding: 2px 4px; border-radius: 3px; font-family: monospace;">**bold**</code> / <code style="background-color: {code_bg}; color: {text_color}; padding: 2px 4px; border-radius: 3px; font-family: monospace;">*italic*</code></td>
                </tr>
                <tr style="border-bottom: 1px solid {border_color};">
                    <td style="padding: 8px; font-weight: bold; color: {text_color};">Code</td>
                    <td style="padding: 8px; color: {text_color};"><code style="background-color: {code_bg}; color: {text_color}; padding: 2px 4px; border-radius: 3px; font-family: monospace;">`inline`</code> or <code style="background-color: {code_bg}; color: {text_color}; padding: 2px 4px; border-radius: 3px; font-family: monospace;">```block```</code></td>
                </tr>
                <tr style="border-bottom: 1px solid {border_color};">
                    <td style="padding: 8px; font-weight: bold; color: {text_color};">Link / Image</td>
                    <td style="padding: 8px; color: {text_color};"><code style="background-color: {code_bg}; color: {text_color}; padding: 2px 4px; border-radius: 3px; font-family: monospace;">[text](url)</code> / <code style="background-color: {code_bg}; color: {text_color}; padding: 2px 4px; border-radius: 3px; font-family: monospace;">![alt](url)</code></td>
                </tr>
                <tr style="border-bottom: 1px solid {border_color};">
                    <td style="padding: 8px; font-weight: bold; color: {text_color};">Lists</td>
                    <td style="padding: 8px; color: {text_color};"><code style="background-color: {code_bg}; color: {text_color}; padding: 2px 4px; border-radius: 3px; font-family: monospace;">- item</code> or <code style="background-color: {code_bg}; color: {text_color}; padding: 2px 4px; border-radius: 3px; font-family: monospace;">1. item</code></td>
                </tr>
                <tr style="border-bottom: 1px solid {border_color};">
                    <td style="padding: 8px; font-weight: bold; color: {text_color};">Blockquote</td>
                    <td style="padding: 8px; color: {text_color};"><code style="background-color: {code_bg}; color: {text_color}; padding: 2px 4px; border-radius: 3px; font-family: monospace;">&gt; quote</code></td>
                </tr>
                <tr style="border-bottom: 1px solid {border_color};">
                    <td style="padding: 8px; font-weight: bold; color: {text_color};">Table</td>
                    <td style="padding: 8px; color: {text_color};"><code style="background-color: {code_bg}; color: {text_color}; padding: 2px 4px; border-radius: 3px; font-family: monospace;">| col1 | col2 |</code></td>
                </tr>
            </table>

            <h2 style="color: {heading_color};">Features</h2>
            <ul style="color: {text_color};">
                <li>GitHub-style markdown rendering</li>
                <li>Syntax highlighting for code blocks</li>
                <li>Dark and light theme support</li>
                <li>Recent files tracking</li>
                <li>Session restore</li>
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
    """Centralized theme management for Fusion style using the theme registry"""

    @staticmethod
    def get_fusion_palette(theme_name="dark"):
        """Get Fusion style palette for the specified theme"""
        from .theme_manager import get_fusion_palette

        return get_fusion_palette(theme_name)

    @staticmethod
    def get_fusion_dark_palette():
        """Backward compatibility: Get dark theme palette"""
        return ThemeManager.get_fusion_palette("dark")

    @staticmethod
    def get_fusion_light_palette():
        """Backward compatibility: Get light theme palette"""
        return ThemeManager.get_fusion_palette("light")

    @staticmethod
    def get_search_css(theme_name="dark"):
        """Generate CSS for search highlighting that works with Fusion"""
        from .theme_manager import get_search_css

        return get_search_css(theme_name)

    @staticmethod
    def get_available_themes():
        """Get list of available theme names"""
        from .theme_manager import get_theme_registry

        registry = get_theme_registry()
        return registry.get_theme_names()

    @staticmethod
    def get_theme_display_name(theme_name):
        """Get display name for a theme"""
        from .theme_manager import get_theme_registry

        registry = get_theme_registry()
        theme = registry.get_theme(theme_name)
        return theme.display_name if theme else theme_name.capitalize()

    @staticmethod
    def get_themes_by_category(category):
        """Get themes filtered by category"""
        from .theme_manager import get_theme_registry

        registry = get_theme_registry()
        return registry.get_themes_by_category(category)


class FindDialog(QDialog):
    """Simple Find dialog similar to Windows Notepad"""

    def __init__(self, parent=None, theme="dark"):
        super().__init__(parent)
        self.setWindowTitle("Find")
        self.setModal(True)
        self.setFixedSize(350, 200)
        self.theme = theme

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
        # Theme colors
        if self.theme == "dark":
            bg_color = "#2d2d2d"
            text_color = "#bbbbbb"
            input_bg = "#1e1e1e"
            border_color = "#444444"
            btn_bg = "#3d3d3d"
            btn_hover = "#4d4d4d"
            counter_bg = "#3d3d00"
            counter_border = "#5d5d00"
        else:
            bg_color = "#f0f0f0"
            text_color = "#000000"
            input_bg = "#ffffff"
            border_color = "#cccccc"
            btn_bg = "#e0e0e0"
            btn_hover = "#d0d0d0"
            counter_bg = "#fff3cd"
            counter_border = "#ffeaa7"

        # Apply dialog-level stylesheet
        self.setStyleSheet(f"QDialog {{ background-color: {bg_color}; }}")

        layout = QVBoxLayout()

        # Find what label and input
        find_label = QLabel("Find what:")
        find_label.setStyleSheet(f"font-weight: bold; color: {text_color};")

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Enter search text...")
        self.search_input.setStyleSheet(f"""
            QLineEdit {{
                border: 2px solid {border_color};
                border-radius: 4px;
                padding: 6px 8px;
                font-size: 12px;
                background-color: {input_bg};
                color: {text_color};
            }}
            QLineEdit:focus {{
                border-color: #007acc;
            }}
        """)

        # Search options
        self.case_checkbox = QCheckBox("Match case")
        self.case_checkbox.setStyleSheet(f"""
            QCheckBox {{
                spacing: 8px;
                font-weight: bold;
                color: {text_color};
            }}
            QCheckBox::indicator {{
                width: 18px;
                height: 18px;
                border: 2px solid {border_color};
                border-radius: 4px;
                background-color: {input_bg};
            }}
            QCheckBox::indicator:checked {{
                background-color: #007acc;
                border-color: #007acc;
            }}
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
        self.cancel_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {btn_bg};
                color: {text_color};
                border: 1px solid {border_color};
                padding: 8px 16px;
                border-radius: 4px;
            }}
            QPushButton:hover {{
                background-color: {btn_hover};
            }}
        """)

        self.match_counter = QLabel("0/0 matches")
        self.match_counter.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.match_counter.setStyleSheet(f"""
            QLabel {{
                color: {text_color};
                background-color: {counter_bg};
                border: 1px solid {counter_border};
                border-radius: 4px;
                padding: 4px 8px;
                font-size: 11px;
                font-weight: bold;
            }}
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
            found_cursor = document.find(
                self.search_text, cursor, self.build_find_flags()
            )
            if found_cursor.isNull():
                break

            # Store a copy of the cursor with its selection intact
            matches.append(QTextCursor(found_cursor))
            # Move search position past this match
            cursor = found_cursor
            cursor.setPosition(found_cursor.selectionEnd())

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

            fmt = QTextCharFormat()
            if i == self.current_match_index:
                # Current match: maximum visibility
                fmt.setBackground(current_highlight)
                fmt.setForeground(current_text)
                fmt.setFontWeight(QFont.Weight.Bold)
                fmt.setFontUnderline(True)
            else:
                # Other matches: clear but less prominent
                fmt.setBackground(other_highlight)
                fmt.setForeground(other_text)

            selection.format = fmt  # Apply the format to the selection
            extra_selections.append(selection)

        # Apply selections
        self.text_browser.setExtraSelections(extra_selections)

        # Force visual update
        self.text_browser.viewport().update()

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


class UpdateCheckWorker(QThread):
    """Worker thread for checking updates using QThread for proper signal delivery"""

    no_version_info = pyqtSignal()
    up_to_date = pyqtSignal(str)  # current_version
    update_available = pyqtSignal(object)  # check_result
    check_error = pyqtSignal(str)  # error_message

    def __init__(self, version_checker, git_updater, is_git_install, parent=None):
        super().__init__(parent)
        self.version_checker = version_checker
        self.git_updater = git_updater
        self.is_git_install = is_git_install

    def run(self):
        try:
            print("[DEBUG] Starting update check...")
            from github_version_checker import VersionCheckResult

            check_result = self.version_checker.get_latest_version()
            print(
                f"[DEBUG] GitHub check result: error={check_result.error_message}, has_update={check_result.has_update}"
            )

            if check_result.error_message:
                # Fall back to git-based checking if GitHub releases fail
                print(f"GitHub releases check failed: {check_result.error_message}")
                print("Falling back to git-based version checking...")

                has_update, current_version, latest_version = (
                    self.git_updater.get_update_info()
                )
                print(
                    f"[DEBUG] Git check result: has_update={has_update}, current={current_version}, latest={latest_version}"
                )

                if not latest_version:
                    print("[DEBUG] No version info - emitting signal")
                    self.no_version_info.emit()
                    return

                if not has_update:
                    print("[DEBUG] Up to date - emitting signal")
                    current_version = (
                        current_version or self.git_updater.get_current_version()
                    )
                    self.up_to_date.emit(current_version)
                    return

                print("[DEBUG] Update available - emitting signal")
                # Create check result for dialog
                check_result = VersionCheckResult()
                check_result.has_update = True
                check_result.current_version = current_version
                check_result.latest_version = latest_version
                check_result.release_notes = f"Update available via git repository:\n{current_version} → {latest_version}"
                self.update_available.emit(check_result)

            else:
                print("[DEBUG] GitHub check succeeded")
                # GitHub releases check succeeded
                if not check_result.has_update:
                    print("[DEBUG] Up to date - emitting signal")
                    self.up_to_date.emit(check_result.current_version)
                    return

                print("[DEBUG] Update available via GitHub - emitting signal")
                self.update_available.emit(check_result)

        except Exception as e:
            print(f"[DEBUG] Exception occurred: {e}")
            import traceback

            traceback.print_exc()
            self.check_error.emit(str(e))


class UpdatePerformWorker(QThread):
    """Worker thread for performing updates using QThread for proper signal delivery"""

    update_completed = pyqtSignal(object)  # update_result
    update_error = pyqtSignal(str)  # error_message

    def __init__(self, is_git_install, git_updater, release_downloader, update_version=None, parent=None):
        super().__init__(parent)
        self.is_git_install = is_git_install
        self.git_updater = git_updater
        self.release_downloader = release_downloader
        self.update_version = update_version

    def run(self):
        try:
            if self.is_git_install:
                # Use git updater
                update_result = self.git_updater.force_update()
            else:
                # Use release downloader
                if self.update_version:
                    update_result = self.release_downloader.perform_update(self.update_version)
                else:
                    from git_updater import GitUpdateResult
                    update_result = GitUpdateResult()
                    update_result.success = False
                    update_result.message = "Unable to determine update version"

            self.update_completed.emit(update_result)

        except Exception as e:
            self.update_error.emit(str(e))


class MainWindow(QMainWindow):
    def __init__(self, initial_file=None):
        super().__init__()
        self.current_file = None
        self.renderer = MarkdownRenderer()
        self.settings = QSettings("MDviewer", "MDviewer")
        self.recent_files = []
        self.recent_directories = []
        self.initial_file = initial_file
        self.find_dialog = None
        self.current_theme = (
            "dark"  # Default theme (will be overwritten by load_theme_settings)
        )
        self.hide_paragraph_marks = False  # Default: marks shown (unchecked = visible)

        # Initialize update components
        self.version_checker = GitHubVersionChecker("juren53/MDviewer", get_semver())
        self.git_updater = GitUpdater(
            "https://github.com/juren53/MDviewer.git", "version.py"
        )
        self.release_downloader = ReleaseDownloader(
            "juren53/MDviewer", "version.py"
        )

        self.setWindowTitle("MDviewer")

        # Set window icon via IconLoader
        from icon_loader import icons
        self.setWindowIcon(icons.app_icon())

        # Load window geometry and state from settings
        self.load_window_settings()

        # Load theme from settings
        self.load_theme_settings()

        # Load paragraph marks preference from settings
        self.load_paragraph_marks_settings()

        # Load custom color overrides for both themes
        self.custom_colors = {"dark": {}, "light": {}}
        self.load_custom_colors()

        # Load recent files from settings
        self.load_recent_files()

        # Load recent directories from settings
        self.load_recent_directories()

        self.setup_ui()
        self.setup_menu()
        self.setup_status_bar()

        # Set up markdown browser with dark theme
        self.text_browser.setFont(QFont("Consolas", 11))
        self.text_browser.setReadOnly(True)

        # Apply theme-aware stylesheet to text browser
        self._apply_text_browser_stylesheet()

        # Set theme in renderer
        self.renderer.current_theme = self.current_theme
        self.renderer.hide_paragraph_marks = self.hide_paragraph_marks

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
        self.recent_menu = file_menu.addMenu("Open Recent &Files")
        self.update_recent_files_menu()

        # Recent Directories submenu
        self.recent_dirs_menu = file_menu.addMenu("Open Recent &Directories")
        self.update_recent_dirs_menu()

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

        refresh_action = QAction("&Refresh", self)
        refresh_action.setShortcut("F5")
        refresh_action.setStatusTip("Reload the current document")
        refresh_action.triggered.connect(self._refresh_current_document)
        view_menu.addAction(refresh_action)

        view_menu.addSeparator()

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
        self.theme_actions = {}

        # Get available themes and create menu actions
        available_themes = ThemeManager.get_available_themes()

        # Group themes by category for better organization
        built_in_themes = []
        popular_themes = []

        for theme_name in sorted(available_themes):
            theme_obj = get_theme_registry().get_theme(theme_name)
            if theme_obj:
                if theme_obj.category == "Built-in":
                    built_in_themes.append(theme_obj)
                else:
                    popular_themes.append(theme_obj)

        # Add Built-in themes submenu
        if built_in_themes:
            built_in_menu = theme_menu.addMenu("&Built-in")
            for theme_obj in built_in_themes:
                action = QAction(f"&{theme_obj.display_name}", self)
                action.setCheckable(True)
                action.setChecked(self.current_theme == theme_obj.name)
                action.setStatusTip(f"Switch to {theme_obj.display_name} theme")
                action.triggered.connect(
                    lambda checked, name=theme_obj.name: self.switch_theme(name)
                )
                built_in_menu.addAction(action)
                self.theme_actions[theme_obj.name] = action

        # Add Popular themes submenu
        if popular_themes:
            popular_menu = theme_menu.addMenu("&Popular")
            for theme_obj in popular_themes:
                action = QAction(f"&{theme_obj.display_name}", self)
                action.setCheckable(True)
                action.setChecked(self.current_theme == theme_obj.name)
                action.setStatusTip(f"Switch to {theme_obj.display_name} theme")
                action.triggered.connect(
                    lambda checked, name=theme_obj.name: self.switch_theme(name)
                )
                popular_menu.addAction(action)
                self.theme_actions[theme_obj.name] = action

        # Theme toggle action with keyboard shortcut (toggles between dark and light)
        toggle_theme_action = QAction("&Toggle Dark/Light", self)
        toggle_theme_action.setShortcut("Ctrl+T")
        toggle_theme_action.setStatusTip("Toggle between dark and light themes")
        toggle_theme_action.triggered.connect(self.toggle_theme)
        theme_menu.addAction(toggle_theme_action)

        view_menu.addSeparator()

        color_settings_action = QAction("&Customize Colors...", self)
        color_settings_action.setStatusTip("Customize document element colors")
        color_settings_action.triggered.connect(self.show_color_settings)
        view_menu.addAction(color_settings_action)

        # Hide paragraph marks action
        hide_marks_action = QAction("Hide Paragraph Marks", self)
        hide_marks_action.setShortcut("Ctrl+P")
        hide_marks_action.setStatusTip("Show or hide paragraph marks at end of lines")
        hide_marks_action.setCheckable(True)
        hide_marks_action.setChecked(self.hide_paragraph_marks)
        hide_marks_action.triggered.connect(self.toggle_paragraph_marks)
        view_menu.addAction(hide_marks_action)

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

        get_latest_action = QAction("Get Latest Version", self)
        get_latest_action.setShortcut("Ctrl+U")
        get_latest_action.setStatusTip("Check for and install latest version")
        get_latest_action.triggered.connect(self._on_get_latest_updates)
        help_menu.addAction(get_latest_action)

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
        from version import get_version_string

        version_label = QLabel(get_version_string())
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
        colors = self.renderer.get_effective_colors(self.current_theme)
        welcome_html = f"""
        <div style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Helvetica, Arial, sans-serif; text-align: center; padding: 50px; color: {colors["body_text_color"]}; background-color: {colors["background_color"]};">
            <h1 style="color: {colors["body_text_color"]}; border-bottom: 1px solid {colors["border_color"]}; padding-bottom: 0.3em;">Welcome to MDviewer</h1>
            <p>A simple PyQt6 Markdown viewer with GitHub-style rendering</p>
            <p>Use <strong>File &rarr; Open</strong> to open a markdown file, or press <kbd style="background-color: {colors["border_color"]}; padding: 2px 4px; border-radius: 3px; font-family: monospace;">Ctrl+O</kbd></p>
            <br>
            <p>Supported features:</p>
            <ul style="text-align: left; display: inline-block; color: {colors["blockquote_color"]};">
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

        # Also track the directory
        self.add_to_recent_directories(os.path.dirname(file_path))

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

    def load_recent_directories(self):
        """Load recent directories from QSettings."""
        recent_dirs = self.settings.value("recent_directories", [])
        if isinstance(recent_dirs, list):
            self.recent_directories = recent_dirs
        else:
            self.recent_directories = []

    def save_recent_directories(self):
        """Save recent directories to QSettings."""
        self.settings.setValue(
            "recent_directories", self.recent_directories[:5]
        )

    def add_to_recent_directories(self, dir_path):
        """Add a directory to the recent directories list."""
        if not dir_path:
            return

        # Remove if already exists
        if dir_path in self.recent_directories:
            self.recent_directories.remove(dir_path)

        # Add to beginning
        self.recent_directories.insert(0, dir_path)

        # Keep only the most recent 5
        self.recent_directories = self.recent_directories[:5]

        # Update menu and save
        self.update_recent_dirs_menu()
        self.save_recent_directories()

    def update_recent_dirs_menu(self):
        """Update the recent directories menu."""
        self.recent_dirs_menu.clear()

        if not self.recent_directories:
            no_dirs_action = QAction("No recent directories", self)
            no_dirs_action.setEnabled(False)
            self.recent_dirs_menu.addAction(no_dirs_action)
        else:
            for i, dir_path in enumerate(self.recent_directories):
                if os.path.isdir(dir_path):
                    action = QAction(f"{i + 1}. {dir_path}", self)
                    action.setData(dir_path)
                    action.setStatusTip(dir_path)
                    action.triggered.connect(
                        lambda checked, path=dir_path: self.open_from_recent_directory(path)
                    )
                    self.recent_dirs_menu.addAction(action)

        if self.recent_directories:
            self.recent_dirs_menu.addSeparator()
            clear_action = QAction("Clear Recent Directories", self)
            clear_action.triggered.connect(self.clear_recent_directories)
            self.recent_dirs_menu.addAction(clear_action)

    def open_from_recent_directory(self, dir_path):
        """Open a file dialog starting in the selected recent directory."""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Open Markdown File",
            dir_path,
            "Markdown Files (*.md *.markdown);;All Files (*)",
        )

        if file_path:
            self.load_file_from_path(file_path)

    def clear_recent_directories(self):
        """Clear the recent directories list."""
        self.recent_directories.clear()
        self.update_recent_dirs_menu()
        self.save_recent_directories()

    def keyPressEvent(self, event):
        """Handle keyboard shortcuts — 'b' pages backward (like less)."""
        if event.key() == Qt.Key.Key_B and not event.modifiers():
            scrollbar = self.text_browser.verticalScrollBar()
            scrollbar.setValue(
                scrollbar.value() - self.text_browser.viewport().height()
            )
        else:
            super().keyPressEvent(event)

    def closeEvent(self, event):
        """Handle window close event."""
        # Save window settings when closing
        self.save_window_settings()
        self.save_recent_files()
        self.save_recent_directories()

        # Save current theme preference
        self.settings.setValue("current_theme", self.current_theme)
        # Save paragraph marks preference
        self.settings.setValue("hide_paragraph_marks", self.hide_paragraph_marks)

        # Save custom color overrides
        self.save_custom_colors()

        # Save current file for restore on startup
        if self.current_file:
            self.settings.setValue("last_opened_file", self.current_file)
        super().closeEvent(event)

    def show_quick_reference(self):
        effective = self.renderer.get_effective_colors(self.current_theme)
        dialog = QuickReferenceDialog(
            self, theme=self.current_theme, custom_colors=effective
        )
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
        # Get theme-specific palette from theme manager
        palette = ThemeManager.get_fusion_palette(theme_name)
        search_css = ThemeManager.get_search_css(theme_name)

        # Apply palette globally via QSettings (works during initialization)
        self.settings.setValue("theme_palette", palette)
        self.settings.setValue("theme_css", search_css)

        # Apply to current text browser if it exists
        if hasattr(self, "text_browser"):
            self._apply_text_browser_stylesheet()

    def switch_theme(self, theme_name):
        """Switch between dark and light themes"""
        if theme_name == self.current_theme:
            return

        # Update current theme
        self.current_theme = theme_name

        # Apply theme via existing apply_theme method
        self.apply_theme(theme_name)

        # Update renderer theme and apply per-theme custom colors
        self.renderer.current_theme = theme_name
        self._apply_custom_colors_to_renderer()

        # Reload current document
        self._refresh_current_document()

        # Save theme preference
        self.settings.setValue("current_theme", theme_name)

        # Update menu check states
        self.update_theme_menu_states()

    def toggle_theme(self):
        """Toggle between dark and light themes"""
        new_theme = "light" if self.current_theme == "dark" else "dark"
        self.switch_theme(new_theme)

    def update_theme_menu_states(self):
        """Update the check states of theme menu actions"""
        if hasattr(self, "theme_actions"):
            for theme_name, action in self.theme_actions.items():
                action.setChecked(self.current_theme == theme_name)

    def toggle_paragraph_marks(self):
        """Toggle paragraph marks visibility"""
        self.hide_paragraph_marks = not self.hide_paragraph_marks
        self.renderer.hide_paragraph_marks = self.hide_paragraph_marks

        # Update menu check state
        for action in self.findChildren(QAction):
            if action.text() == "Hide Paragraph Marks":
                action.setChecked(self.hide_paragraph_marks)
                break

        # Reload current document to apply change
        if self.current_file:
            self.load_file_from_path(self.current_file)
        else:
            # Reload welcome message
            self.show_welcome_message()

        # Update status bar
        state = "hidden" if self.hide_paragraph_marks else "shown"
        self.status_bar.showMessage(f"Paragraph marks {state}", 2000)

    def load_theme_settings(self):
        """Load theme preference from settings"""
        saved_theme = self.settings.value("current_theme", "dark")
        self.current_theme = saved_theme
        self.apply_theme(self.current_theme)
        self.renderer.current_theme = self.current_theme

    def load_paragraph_marks_settings(self):
        """Load paragraph marks preference from settings"""
        saved_setting = self.settings.value("hide_paragraph_marks", False, type=bool)
        self.hide_paragraph_marks = saved_setting

    def load_custom_colors(self):
        """Load custom color overrides from QSettings."""
        registry = get_theme_registry()
        available_themes = registry.get_theme_names()

        for theme in available_themes:
            if theme not in self.custom_colors:
                self.custom_colors[theme] = {}

            self.settings.beginGroup(f"custom_colors/{theme}")
            theme_obj = registry.get_theme(theme)
            if theme_obj:
                for key in theme_obj.content_colors.__dict__:
                    val = self.settings.value(key)
                    if val is not None:
                        self.custom_colors[theme][key] = val
            self.settings.endGroup()
        self._apply_custom_colors_to_renderer()

    def save_custom_colors(self):
        """Save custom color overrides to QSettings."""
        for theme in ("dark", "light"):
            self.settings.beginGroup(f"custom_colors/{theme}")
            self.settings.remove("")
            for key, val in self.custom_colors[theme].items():
                self.settings.setValue(key, val)
            self.settings.endGroup()

    def reset_all_themes_to_factory(self):
        """Factory reset - clear ALL custom color settings for ALL themes."""
        # Get all available themes from registry
        registry = get_theme_registry()
        available_themes = registry.get_theme_names()
        
        # Clear QSettings for all themes
        for theme in available_themes:
            self.settings.beginGroup(f"custom_colors/{theme}")
            self.settings.remove("")  # Remove all keys in this group
            self.settings.endGroup()
        
        # Clear in-memory custom colors
        self.custom_colors = {theme: {} for theme in available_themes}
        
        # Re-apply renderer settings with no custom colors
        self._apply_custom_colors_to_renderer()
        
        # Refresh display
        self._refresh_current_document()
        self._apply_text_browser_stylesheet()

    def _apply_custom_colors_to_renderer(self):
        """Push the current theme's custom colors into the renderer."""
        self.renderer.custom_colors = dict(
            self.custom_colors.get(self.current_theme, {})
        )

    def _apply_text_browser_stylesheet(self):
        """Update the QTextBrowser widget stylesheet to match current colors."""
        colors = self.renderer.get_effective_colors(self.current_theme)
        bg = colors["background_color"]
        text = colors["body_text_color"]
        scrollbar_bg = colors["code_bg_color"]
        scrollbar_handle = colors["border_color"]

        self.text_browser.setStyleSheet(f"""
            QTextBrowser {{
                background-color: {bg};
                color: {text};
                border: none;
            }}
            QScrollBar:vertical {{
                background-color: {scrollbar_bg};
                width: 12px;
                border: none;
            }}
            QScrollBar::handle:vertical {{
                background-color: {scrollbar_handle};
                min-height: 20px;
                border-radius: 6px;
            }}
            QScrollBar::handle:vertical:hover {{
                background-color: #484f58;
            }}
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
                border: none;
                background: none;
            }}
        """)

    def _refresh_current_document(self):
        """Re-render and display the current document or welcome message."""
        if self.current_file:
            self.load_file_from_path(self.current_file)
        else:
            self.show_welcome_message()

    def show_color_settings(self):
        """Open the color customization dialog."""
        # Get effective colors (theme defaults + custom overrides)
        registry = get_theme_registry()
        theme_obj = registry.get_theme(self.current_theme)
        if theme_obj:
            effective = dict(theme_obj.content_colors.__dict__)
        else:
            effective = dict(
                DEFAULT_THEME_COLORS.get(
                    self.current_theme, DEFAULT_THEME_COLORS["dark"]
                )
            )
        effective.update(self.custom_colors.get(self.current_theme, {}))

        dialog = ColorSettingsDialog(self.current_theme, effective, self)
        dialog.colors_changed.connect(self._on_colors_changed)
        dialog.exec()

        # After dialog closes, save final state
        final_colors = dialog.current_colors
        final_theme = dialog.theme

        # Get theme defaults for comparison
        registry = get_theme_registry()
        theme_obj = registry.get_theme(final_theme)
        if theme_obj:
            defaults = dict(theme_obj.content_colors.__dict__)
        else:
            # Fallback to old method for backward compatibility
            defaults = DEFAULT_THEME_COLORS.get(
                final_theme, DEFAULT_THEME_COLORS["dark"]
            )

        # Only store keys that differ from defaults
        overrides = {}
        for key, val in final_colors.items():
            if val != defaults.get(key):
                overrides[key] = val

        self.custom_colors[final_theme] = overrides

        # If user switched to a different theme in the dialog, switch to it
        if final_theme != self.current_theme:
            self.switch_theme(final_theme)
        else:
            self._apply_custom_colors_to_renderer()
            self.save_custom_colors()
            self._refresh_current_document()
            self._apply_text_browser_stylesheet()

    def _on_colors_changed(self, colors_dict):
        """Handle live color changes from dialog."""
        # Get theme defaults for comparison
        registry = get_theme_registry()
        theme_obj = registry.get_theme(self.current_theme)
        if theme_obj:
            defaults = dict(theme_obj.content_colors.__dict__)
        else:
            # Fallback to old method for backward compatibility
            defaults = DEFAULT_THEME_COLORS.get(
                self.current_theme, DEFAULT_THEME_COLORS["dark"]
            )

        overrides = {}
        for key, val in colors_dict.items():
            if val != defaults.get(key):
                overrides[key] = val

        self.renderer.custom_colors = overrides
        self._refresh_current_document()
        self._apply_text_browser_stylesheet()

    def setup_find_dialog(self):
        """Create find dialog instance"""
        self.find_dialog = FindDialog(self, theme=self.current_theme)
        self.find_dialog.set_text_browser(self.text_browser)

    def show_find_dialog(self):
        """Show Find dialog"""
        # Recreate dialog if theme changed or doesn't exist
        if not self.find_dialog or self.find_dialog.theme != self.current_theme:
            self.setup_find_dialog()

        # Position dialog relative to main window
        self.find_dialog.show()
        self.find_dialog.raise_()
        self.find_dialog.activateWindow()

    def _on_get_latest_updates(self):
        """Handler for 'Get Latest Version' menu action"""
        # Show progress dialog
        progress_dialog = UpdateProgressDialog(self)
        progress_dialog.update_status("Checking for updates...")
        progress_dialog.show()

        # Add safety timeout (15 seconds)
        QTimer.singleShot(15000, lambda: self._check_timeout(progress_dialog))

        # Detect installation type (git vs non-git)
        self.is_git_install = self.git_updater.is_git_repository()
        update_method = "git" if self.is_git_install else "download"
        print(f"[DEBUG] Installation type: {update_method}")

        # Update progress message based on method
        if self.is_git_install:
            progress_dialog.update_status("Checking for updates (git)...")
        else:
            progress_dialog.update_status("Checking for updates (GitHub releases)...")

        # Create QThread worker for update check (proper Qt thread for signal delivery)
        self._update_check_worker = UpdateCheckWorker(
            self.version_checker, self.git_updater, self.is_git_install, parent=self
        )
        self._update_check_worker.no_version_info.connect(
            lambda: self._show_no_version_info_dialog(progress_dialog)
        )
        self._update_check_worker.up_to_date.connect(
            lambda v: self._show_up_to_date_dialog(progress_dialog, v)
        )
        self._update_check_worker.update_available.connect(
            lambda r: self._show_comparison_dialog(progress_dialog, r)
        )
        self._update_check_worker.check_error.connect(
            lambda e: self._show_check_error(progress_dialog, e)
        )
        self._update_check_worker.start()

    def _check_timeout(self, progress_dialog):
        """Handle timeout if check takes too long"""
        if progress_dialog.isVisible():
            print("[DEBUG] Update check timed out")
            progress_dialog.close()
            error_dialog = ErrorDialog(
                "Update check timed out.\n\n"
                "This may be due to network issues.\n"
                "Please check your internet connection and try again.",
                self,
            )
            error_dialog.exec()

    def _show_no_version_info_dialog(self, progress_dialog):
        """Show dialog when no version information is available (runs on main thread)"""
        progress_dialog.close()

        info_dialog = QDialog(self)
        info_dialog.setWindowTitle("Update Information")
        info_dialog.setModal(True)
        info_dialog.setFixedSize(450, 250)

        layout = QVBoxLayout()
        title_label = QLabel("Update Check")
        title_label.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        info_text = QLabel(
            "No version information available yet.\n\n"
            "This is normal for new installations.\n\n"
            "You are running the latest available version.\n\n"
            "Future updates will be detected automatically."
        )
        info_text.setAlignment(Qt.AlignmentFlag.AlignCenter)
        info_text.setWordWrap(True)

        ok_button = QPushButton("OK")
        ok_button.clicked.connect(info_dialog.accept)

        layout.addWidget(title_label)
        layout.addWidget(info_text)
        layout.addWidget(ok_button)

        info_dialog.setLayout(layout)
        info_dialog.setStyleSheet("""
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
        """)

        info_dialog.exec()

    def _show_up_to_date_dialog(self, progress_dialog, current_version):
        """Show up-to-date dialog (runs on main thread)"""
        progress_dialog.close()
        up_to_date_dialog = UpToDateDialog(current_version, self)
        up_to_date_dialog.exec()

    def _show_comparison_dialog(self, progress_dialog, check_result):
        """Show version comparison dialog (runs on main thread)"""
        progress_dialog.close()
        update_method = "git" if self.is_git_install else "download"
        comparison_dialog = VersionCompareDialog(check_result, self, update_method)

        if (
            comparison_dialog.exec() == QDialog.DialogCode.Accepted
            and comparison_dialog.should_update
        ):
            # Store version for download-based updates
            self._update_version = check_result.latest_version
            # Perform update
            self._perform_update()

    def _show_check_error(self, progress_dialog, error_message):
        """Show error dialog for update check failures (runs on main thread)"""
        progress_dialog.close()
        error_dialog = ErrorDialog(f"Error checking for updates: {error_message}", self)
        error_dialog.exec()

    def _perform_update(self):
        """Perform the actual update process"""
        progress_dialog = UpdateProgressDialog(self)

        # Update message based on installation type
        if self.is_git_install:
            progress_dialog.update_status("Updating via git...")
        else:
            progress_dialog.update_status("Downloading update...")

        progress_dialog.show()

        # Create QThread worker for update (proper Qt thread for signal delivery)
        update_version = getattr(self, '_update_version', None)
        self._update_perform_worker = UpdatePerformWorker(
            self.is_git_install, self.git_updater, self.release_downloader,
            update_version=update_version, parent=self
        )
        self._update_perform_worker.update_completed.connect(
            lambda r: self._show_update_result(r, progress_dialog)
        )
        self._update_perform_worker.update_error.connect(
            lambda e: self._show_update_error(e, progress_dialog)
        )
        self._update_perform_worker.start()

    def _show_update_result(self, update_result, progress_dialog):
        """Show update result dialog"""
        progress_dialog.close()

        # Convert ReleaseDownloadResult to GitUpdateResult format for dialog compatibility
        from git_updater import GitUpdateResult
        from release_downloader import ReleaseDownloadResult
        
        if isinstance(update_result, ReleaseDownloadResult):
            # Convert to GitUpdateResult for dialog display
            git_result = GitUpdateResult()
            git_result.success = update_result.success
            git_result.message = update_result.message
            git_result.current_version = update_result.current_version
            git_result.new_version = update_result.new_version
            git_result.command_output = update_result.message
            git_result.error_output = update_result.error_message
            result_dialog = UpdateResultDialog(git_result, self)
        else:
            result_dialog = UpdateResultDialog(update_result, self)
        
        result_dialog.exec()

        # If update was successful, suggest restart
        if update_result.success:
            QMessageBox.information(
                self,
                "Restart Required",
                "MDviewer has been successfully updated.\n\n"
                "Please restart the application to use the new version.",
            )

    def _show_update_error(self, error_message, progress_dialog):
        """Show update error dialog"""
        progress_dialog.close()
        error_dialog = ErrorDialog(f"Update failed: {error_message}", self)
        error_dialog.exec()

    def show_about(self):
        identity = AppIdentity(
            name="MDviewer",
            version=__version__,
            commit_date=f"{__version_date__} CST",
            description="A PyQt6 Markdown viewer with GitHub-style rendering and multi-theme support.",
            features=[
                "GitHub-style Markdown rendering",
                "Multi-theme support with custom colors",
                "Live file watching and auto-reload",
                "Find and replace",
            ],
        )
        info = gather_info(identity, caller_file=__file__)
        AboutDialog(info, parent=self).exec()
