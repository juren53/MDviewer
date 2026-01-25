#!/usr/bin/env python3

import sys
import os
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt
from viewer.main_window import MainWindow


def main():
    app = QApplication(sys.argv)
    app.setApplicationName("MDviewer")
    app.setApplicationVersion("1.0.0")
    app.setOrganizationName("MDviewer")

    # High DPI support is enabled by default in PyQt6

    window = MainWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
