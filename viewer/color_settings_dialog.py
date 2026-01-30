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
        self.preview_labels = {}

        self.setWindowTitle(f"Element Colors - {theme.capitalize()} Theme")
        self.setModal(False)
        self.setFixedSize(520, 360)

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

            preview = QLabel()
            preview.setFixedHeight(28)
            self.preview_labels[key] = preview
            self._init_preview(preview, key, self.current_colors[key])

            grid.addWidget(label, row, 0)
            grid.addWidget(color_btn, row, 1)
            grid.addWidget(preview, row, 2)

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
            self._update_preview(key, hex_val)
            self.colors_changed.emit(dict(self.current_colors))

    def _reset_to_defaults(self):
        """Reset all colors to theme defaults."""
        defaults = DEFAULT_THEME_COLORS[self.theme]
        self.current_colors = dict(defaults)

        for key, _ in COLOR_SETTINGS:
            self._update_button_color(self.color_buttons[key], defaults[key])
            self._update_preview(key, defaults[key])

        self.colors_changed.emit(dict(self.current_colors))

    def _update_button_color(self, button, hex_color):
        """Set a button's background to display the given color as a swatch."""
        button.setStyleSheet(
            f"background-color: {hex_color}; "
            f"border: 2px solid #888888; border-radius: 4px; "
            f"min-width: 56px; min-height: 24px;"
        )

    def _init_preview(self, label, key, hex_color):
        """Set up a preview label's text and initial style for the given element key."""
        if key == "heading_color":
            label.setText("Heading")
            label.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        elif key == "body_text_color":
            label.setText("Sample text")
        elif key == "background_color":
            label.setText("")
        elif key == "link_color":
            font = QFont()
            font.setUnderline(True)
            label.setFont(font)
            label.setText("Link")
        elif key == "blockquote_color":
            label.setText("Quote")
        elif key == "code_bg_color":
            label.setText("`code`")
            label.setFont(QFont("Consolas", 9))
        elif key == "border_color":
            label.setText("")
        self._update_preview(key, hex_color)

    def _update_preview(self, key, hex_color):
        """Re-style the preview label for a given key with the current color."""
        label = self.preview_labels.get(key)
        if label is None:
            return

        if key == "heading_color":
            label.setStyleSheet(f"color: {hex_color}; background: transparent;")
        elif key == "body_text_color":
            label.setStyleSheet(f"color: {hex_color}; background: transparent;")
        elif key == "background_color":
            label.setStyleSheet(
                f"background-color: {hex_color}; "
                f"border: 1px solid #888888; border-radius: 3px;"
            )
        elif key == "link_color":
            label.setStyleSheet(f"color: {hex_color}; background: transparent;")
        elif key == "blockquote_color":
            label.setStyleSheet(
                f"color: {hex_color}; background: transparent; "
                f"border-left: 3px solid {hex_color}; padding-left: 6px;"
            )
        elif key == "code_bg_color":
            label.setStyleSheet(
                f"background-color: {hex_color}; "
                f"border-radius: 3px; padding: 2px 6px;"
            )
        elif key == "border_color":
            label.setStyleSheet(
                f"background: transparent; "
                f"border-top: 2px solid {hex_color}; "
                f"margin-top: 12px;"
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
