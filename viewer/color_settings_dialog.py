from PyQt6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QGridLayout,
    QLabel,
    QPushButton,
    QColorDialog,
)
from PyQt6.QtGui import QFont
from PyQt6.QtCore import Qt, pyqtSignal

from .markdown_renderer import DEFAULT_THEME_COLORS


# Human-readable labels and display order for color settings
COLOR_SETTINGS = [
    ("heading_color", "Headings"),
    ("body_text_color", "Body Text"),
    ("background_color", "Background"),
    ("link_color", "Links"),
    ("blockquote_color", "Blockquotes"),
    ("code_bg_color", "Code Blocks"),
    ("border_color", "Borders"),
]


class ColorSettingsDialog(QDialog):
    """Dialog for customizing document element colors using visual color swatches."""

    colors_changed = pyqtSignal(dict)

    def __init__(self, theme, current_colors, parent=None):
        super().__init__(parent)
        self.theme = theme
        self.current_colors = dict(current_colors)
        self.color_buttons = {}

        self.setWindowTitle(f"Element Colors - {theme.capitalize()} Theme")
        self.setModal(False)
        self.setFixedSize(340, 360)

        self._setup_ui()
        self._apply_dialog_theme()

    def _setup_ui(self):
        main_layout = QVBoxLayout()

        title = QLabel(f"Customize {self.theme.capitalize()} Theme Colors")
        title.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(title)
        main_layout.addSpacing(8)

        grid = QGridLayout()
        grid.setSpacing(10)

        for row, (key, label_text) in enumerate(COLOR_SETTINGS):
            label = QLabel(label_text)
            label.setFixedWidth(120)

            color_btn = QPushButton()
            color_btn.setFixedSize(60, 28)
            color_btn.setCursor(Qt.CursorShape.PointingHandCursor)
            color_btn.setToolTip(f"Click to change {label_text.lower()} color")
            self._update_button_color(color_btn, self.current_colors[key])
            color_btn.clicked.connect(lambda checked, k=key: self._pick_color(k))

            grid.addWidget(label, row, 0)
            grid.addWidget(color_btn, row, 1)

            self.color_buttons[key] = color_btn

        main_layout.addLayout(grid)
        main_layout.addStretch()

        button_layout = QHBoxLayout()

        reset_btn = QPushButton("Reset to Defaults")
        reset_btn.setToolTip("Restore all colors to their default values")
        reset_btn.clicked.connect(self._reset_to_defaults)

        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.accept)

        button_layout.addWidget(reset_btn)
        button_layout.addStretch()
        button_layout.addWidget(close_btn)

        main_layout.addLayout(button_layout)
        self.setLayout(main_layout)

    def _pick_color(self, key):
        """Open the native color picker for the given element."""
        from PyQt6.QtGui import QColor

        label = dict(COLOR_SETTINGS)[key]
        current = QColor(self.current_colors[key])
        chosen = QColorDialog.getColor(current, self, f"Choose {label} Color")

        if chosen.isValid():
            hex_val = chosen.name()
            self.current_colors[key] = hex_val
            self._update_button_color(self.color_buttons[key], hex_val)
            self.colors_changed.emit(dict(self.current_colors))

    def _reset_to_defaults(self):
        """Reset all colors to theme defaults."""
        defaults = DEFAULT_THEME_COLORS[self.theme]
        self.current_colors = dict(defaults)

        for key, _ in COLOR_SETTINGS:
            self._update_button_color(self.color_buttons[key], defaults[key])

        self.colors_changed.emit(dict(self.current_colors))

    def _update_button_color(self, button, hex_color):
        """Set a button's background to display the given color as a swatch."""
        button.setStyleSheet(
            f"background-color: {hex_color}; "
            f"border: 2px solid #888888; border-radius: 4px; "
            f"min-width: 56px; min-height: 24px;"
        )

    def _apply_dialog_theme(self):
        """Style the dialog to match the current MDviewer theme."""
        if self.theme == "dark":
            self.setStyleSheet("""
                QDialog { background-color: #2d2d2d; }
                QLabel { color: #bbbbbb; }
                QPushButton {
                    background-color: #3d3d3d; color: #bbbbbb;
                    border: 1px solid #555555; padding: 6px 12px; border-radius: 4px;
                }
                QPushButton:hover { background-color: #4d4d4d; }
            """)
        else:
            self.setStyleSheet("""
                QDialog { background-color: #f0f0f0; }
                QLabel { color: #000000; }
                QPushButton {
                    background-color: #e0e0e0; color: #000000;
                    border: 1px solid #cccccc; padding: 6px 12px; border-radius: 4px;
                }
                QPushButton:hover { background-color: #d0d0d0; }
            """)

    def get_colors(self):
        """Return the current color settings."""
        return dict(self.current_colors)
