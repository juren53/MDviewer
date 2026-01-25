#!/usr/bin/env python3

import sys
import os
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt
from viewer.main_window import MainWindow


def main():
    app = QApplication(sys.argv)
    app.setApplicationName("MDviewer")
    app.setApplicationVersion("0.0.2")
    app.setOrganizationName("MDviewer")

    # Apply Fusion style for consistent theming
    app.setStyle("Fusion")

    # Apply dark theme palette during initialization
    from viewer.main_window import ThemeManager

    palette = ThemeManager.get_fusion_dark_palette()
    app.setPalette(palette)

    # High DPI support is enabled by default in PyQt6

    # Check if a file path was provided as a command line argument
    file_to_open = None
    if len(sys.argv) > 1:
        file_to_open = sys.argv[1]
        # Convert relative paths to absolute
        if not os.path.isabs(file_to_open):
            file_to_open = os.path.abspath(file_to_open)

    window = MainWindow(file_to_open)
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
