from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QSpinBox,
)
from PyQt6.QtCore import Qt, QPointF, pyqtSignal
from PyQt6.QtPdf import QPdfDocument
from PyQt6.QtPdfWidgets import QPdfView


class PdfViewerWidget(QWidget):
    """Widget that wraps QPdfView with a compact navigation bar."""

    page_changed = pyqtSignal(int, int)  # (current_1based, total)

    def __init__(self, parent=None):
        super().__init__(parent)

        self._document = QPdfDocument(self)
        self._zoom = 1.0  # current zoom factor

        self._view = QPdfView(self)
        self._view.setPageMode(QPdfView.PageMode.MultiPage)
        self._view.setZoomMode(QPdfView.ZoomMode.Custom)
        self._view.setZoomFactor(self._zoom)
        self._view.setDocument(self._document)

        # Navigation bar
        self._nav_bar = QWidget(self)
        self._nav_bar.setFixedHeight(36)
        nav_layout = QHBoxLayout(self._nav_bar)
        nav_layout.setContentsMargins(4, 2, 4, 2)
        nav_layout.setSpacing(4)

        self._btn_prev = QPushButton("◀ Prev", self._nav_bar)
        self._btn_prev.setFixedWidth(64)
        self._btn_prev.clicked.connect(self._go_prev)

        self._btn_next = QPushButton("Next ▶", self._nav_bar)
        self._btn_next.setFixedWidth(64)
        self._btn_next.clicked.connect(self._go_next)

        self._spin_page = QSpinBox(self._nav_bar)
        self._spin_page.setMinimum(1)
        self._spin_page.setMaximum(1)
        self._spin_page.setFixedWidth(60)
        self._spin_page.editingFinished.connect(self._on_spin_editing_finished)

        self._label_total = QLabel("/ 0", self._nav_bar)

        # Zoom controls
        self._btn_zoom_out = QPushButton("−", self._nav_bar)
        self._btn_zoom_out.setFixedWidth(28)
        self._btn_zoom_out.clicked.connect(self.zoom_out)

        self._btn_zoom_in = QPushButton("+", self._nav_bar)
        self._btn_zoom_in.setFixedWidth(28)
        self._btn_zoom_in.clicked.connect(self.zoom_in)

        self._label_zoom = QLabel("100%", self._nav_bar)
        self._label_zoom.setFixedWidth(48)
        self._label_zoom.setAlignment(Qt.AlignmentFlag.AlignCenter)

        nav_layout.addWidget(self._btn_prev)
        nav_layout.addWidget(self._btn_next)
        nav_layout.addSpacing(8)
        nav_layout.addWidget(QLabel("Page:"))
        nav_layout.addWidget(self._spin_page)
        nav_layout.addWidget(self._label_total)
        nav_layout.addStretch()
        nav_layout.addWidget(self._btn_zoom_out)
        nav_layout.addWidget(self._label_zoom)
        nav_layout.addWidget(self._btn_zoom_in)

        # Main layout: nav bar on top, view fills rest
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.addWidget(self._nav_bar)
        layout.addWidget(self._view)

        self._nav_bar.hide()

        # Connect document signals
        self._document.pageCountChanged.connect(self._on_page_count_changed)

        # Connect navigator signals after view has a navigator
        nav = self._view.pageNavigator()
        nav.currentPageChanged.connect(self._on_page_changed)

    # ------------------------------------------------------------------ #
    # Public API                                                           #
    # ------------------------------------------------------------------ #

    def load_pdf(self, path: str) -> bool:
        """Load a PDF file. Returns True on success."""
        self._document.close()
        self._document.load(path)
        if self._document.status() == QPdfDocument.Status.Ready:
            self._nav_bar.show()
            # Jump to first page
            self._view.pageNavigator().jump(0, QPointF(), 0)
            return True
        else:
            self._nav_bar.hide()
            return False

    def close_document(self):
        """Close the current document and reset controls."""
        self._document.close()
        self._nav_bar.hide()
        self._spin_page.setValue(1)
        self._label_total.setText("/ 0")

    def apply_theme(self, theme_name: str, renderer) -> None:
        """Re-style the viewer and nav bar to match the current theme."""
        colors = renderer.get_effective_colors(theme_name)
        bg = colors["background_color"]
        text = colors["body_text_color"]
        scrollbar_bg = colors["code_bg_color"]
        scrollbar_handle = colors["border_color"]

        self._view.setStyleSheet(f"""
            QPdfView {{
                background-color: {bg};
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
            QScrollBar:horizontal {{
                background-color: {scrollbar_bg};
                height: 12px;
                border: none;
            }}
            QScrollBar::handle:horizontal {{
                background-color: {scrollbar_handle};
                min-width: 20px;
                border-radius: 6px;
            }}
            QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{
                border: none;
                background: none;
            }}
        """)

        btn_css = (
            f"QPushButton {{ background-color: {scrollbar_bg}; color: {text}; "
            f"border: 1px solid {scrollbar_handle}; border-radius: 3px; padding: 2px 4px; }}"
            f"QPushButton:hover {{ background-color: {scrollbar_handle}; }}"
        )
        label_css = f"QLabel {{ color: {text}; }}"
        spin_css = (
            f"QSpinBox {{ background-color: {scrollbar_bg}; color: {text}; "
            f"border: 1px solid {scrollbar_handle}; border-radius: 3px; }}"
        )
        self._nav_bar.setStyleSheet(
            f"QWidget {{ background-color: {bg}; }} {btn_css} {label_css} {spin_css}"
        )

    def zoom_in(self):
        self._set_zoom(min(4.00, round(self._zoom + 0.10, 2)))

    def zoom_out(self):
        self._set_zoom(max(0.25, round(self._zoom - 0.10, 2)))

    def reset_zoom(self):
        self._set_zoom(1.0)

    # ------------------------------------------------------------------ #
    # Private helpers                                                      #
    # ------------------------------------------------------------------ #

    def _set_zoom(self, factor: float):
        self._zoom = factor
        self._view.setZoomFactor(factor)
        self._label_zoom.setText(f"{int(factor * 100)}%")

    def _go_prev(self):
        nav = self._view.pageNavigator()
        current = nav.currentPage()
        if current > 0:
            nav.jump(current - 1, QPointF(), 0)

    def _go_next(self):
        nav = self._view.pageNavigator()
        current = nav.currentPage()
        if current < self._document.pageCount() - 1:
            nav.jump(current + 1, QPointF(), 0)

    def _on_spin_editing_finished(self):
        page_0based = self._spin_page.value() - 1
        page_0based = max(0, min(page_0based, self._document.pageCount() - 1))
        self._view.pageNavigator().jump(page_0based, QPointF(), 0)

    def _on_page_changed(self, page: int):
        total = self._document.pageCount()
        # Sync spin box without triggering editingFinished
        self._spin_page.blockSignals(True)
        self._spin_page.setValue(page + 1)
        self._spin_page.blockSignals(False)

        self._btn_prev.setEnabled(page > 0)
        self._btn_next.setEnabled(page < total - 1)

        self.page_changed.emit(page + 1, total)

    def _on_page_count_changed(self, count: int):
        self._spin_page.setMaximum(max(1, count))
        self._label_total.setText(f"/ {count}")
