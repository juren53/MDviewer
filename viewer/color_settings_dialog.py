from PyQt6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QGridLayout,
    QLabel,
    QPushButton,
    QColorDialog,
    QComboBox,
)
from PyQt6.QtGui import QFont
from PyQt6.QtCore import Qt, pyqtSignal

from .theme_manager import get_theme_registry


# For backward compatibility, define DEFAULT_THEME_COLORS from theme registry
def get_default_theme_colors():
    """Get default theme colors for backward compatibility"""
    registry = get_theme_registry()
    return {
        theme_name: dict(theme.content_colors.__dict__)
        for theme_name, theme in registry.get_all_themes().items()
    }


DEFAULT_THEME_COLORS = get_default_theme_colors()


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
        self.original_theme = theme

        # Get available themes
        self.registry = get_theme_registry()
        self.available_themes = self.registry.get_theme_names()

        self.setWindowTitle("Element Colors - Customize Themes")
        self.setModal(False)
        self.setFixedSize(520, 420)

        self._setup_ui()
        self._apply_dialog_theme()
        self._populate_theme_selector()

    def _setup_ui(self):
        main_layout = QVBoxLayout()

        title = QLabel("Customize Theme Colors")
        title.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(title)
        main_layout.addSpacing(8)

        # Theme selector
        theme_selector_layout = QHBoxLayout()
        theme_label = QLabel("Select Theme:")
        theme_label.setFont(QFont("Arial", 10, QFont.Weight.Bold))

        self.theme_combo = QComboBox()
        self.theme_combo.setMinimumWidth(150)

        theme_selector_layout.addWidget(theme_label)
        theme_selector_layout.addWidget(self.theme_combo)
        theme_selector_layout.addStretch()

        main_layout.addLayout(theme_selector_layout)
        main_layout.addSpacing(5)

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
        reset_btn.setToolTip("Restore all colors to their default values for current theme")
        reset_btn.clicked.connect(self._reset_to_defaults)

        factory_reset_btn = QPushButton("Factory Reset All Themes")
        factory_reset_btn.setToolTip("Clear ALL customizations for ALL themes and restore factory defaults")
        factory_reset_btn.clicked.connect(self._factory_reset_all_themes)
        factory_reset_btn.setStyleSheet("""
            QPushButton {
                background-color: #8b0000;
                color: white;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #a52a2a;
            }
        """)

        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.accept)

        button_layout.addWidget(reset_btn)
        button_layout.addWidget(factory_reset_btn)
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

    def _populate_theme_selector(self):
        """Populate the theme selector combo box"""
        self.theme_combo.clear()

        # Group themes by category
        categories = {}
        for theme_name in self.available_themes:
            theme = self.registry.get_theme(theme_name)
            if theme:
                category = theme.category
                if category not in categories:
                    categories[category] = []
                categories[category].append(theme)

        # Add themes in category order
        for category in ["Built-in", "Popular"]:
            if category in categories:
                for theme in sorted(categories[category], key=lambda t: t.display_name):
                    self.theme_combo.addItem(theme.display_name, theme.name)

        # Select current theme
        for i in range(self.theme_combo.count()):
            if self.theme_combo.itemData(i) == self.theme:
                self.theme_combo.setCurrentIndex(i)
                break

        # Connect signal after initial selection
        self.theme_combo.currentTextChanged.connect(self._on_theme_changed)

    def _on_theme_changed(self):
        """Handle theme selection change"""
        selected_theme = self.theme_combo.currentData()
        if selected_theme and selected_theme != self.theme:
            # Switch to new theme
            self.theme = selected_theme
            self._load_theme_colors()

            # Update window title
            theme_obj = self.registry.get_theme(self.theme)
            display_name = (
                theme_obj.display_name if theme_obj else self.theme.capitalize()
            )
            self.setWindowTitle(f"Element Colors - {display_name} Theme")

            # Emit colors changed signal with new theme colors
            self.colors_changed.emit(dict(self.current_colors))

    def _load_theme_colors(self):
        """Load colors for the current theme"""
        theme_obj = self.registry.get_theme(self.theme)
        if theme_obj:
            self.current_colors = dict(theme_obj.content_colors.__dict__)
        else:
            # Fallback to DEFAULT_THEME_COLORS for backward compatibility
            defaults = DEFAULT_THEME_COLORS.get(
                self.theme, DEFAULT_THEME_COLORS["dark"]
            )
            self.current_colors = dict(defaults)

        # Update UI elements with new colors
        for key, _ in COLOR_SETTINGS:
            if key in self.current_colors:
                self._update_button_color(
                    self.color_buttons[key], self.current_colors[key]
                )
                self._update_preview(key, self.current_colors[key])

    def _reset_to_defaults(self):
        """Reset all colors to theme defaults."""
        self._load_theme_colors()
        self.colors_changed.emit(dict(self.current_colors))

    def _factory_reset_all_themes(self):
        """Factory reset all themes - clear ALL custom color settings."""
        from PyQt6.QtWidgets import QMessageBox
        
        # Confirm with user
        reply = QMessageBox.question(
            self,
            "Factory Reset All Themes",
            "This will clear ALL color customizations for ALL themes and restore factory defaults.\n\n"
            "This action cannot be undone.\n\n"
            "Are you sure you want to continue?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            # Signal to parent window to perform factory reset
            if self.parent():
                self.parent().reset_all_themes_to_factory()
                # Reload current theme colors
                self._load_theme_colors()
                self.colors_changed.emit(dict(self.current_colors))
                
                QMessageBox.information(
                    self,
                    "Factory Reset Complete",
                    "All theme customizations have been cleared.\n"
                    "All themes have been restored to factory defaults."
                )

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
                f"background-color: {hex_color}; border-radius: 3px; padding: 2px 6px;"
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
