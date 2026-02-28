# Plan: Add PDF Viewing to MDviewer

## Context
MDviewer currently renders only Markdown files via `QTextBrowser` (HTML). Users want to open PDFs in the same app. `PyQt6.QtPdf` and `PyQt6.QtPdfWidgets` are already available in the environment — no new dependencies needed.

## Approach

Replace the single `QTextBrowser` central widget with a `QStackedWidget` (index 0 = markdown, index 1 = PDF). A new `PdfViewerWidget` wraps `QPdfView` plus a compact navigation bar. File routing by extension happens inside `load_file_from_path()`. Markdown-only menu items are disabled when a PDF is active.

---

## Step 1 — Create `viewer/pdf_viewer.py` (new file)

**Class:** `PdfViewerWidget(QWidget)`

**Imports needed:**
```python
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QSpinBox
from PyQt6.QtCore import Qt, QPointF, pyqtSignal
from PyQt6.QtPdf import QPdfDocument
from PyQt6.QtPdfWidgets import QPdfView
```

**Instance attributes:**
- `self._document = QPdfDocument(self)` — owns lifetime
- `self._view = QPdfView(self)` — PageMode.MultiPage, ZoomMode.Custom
- `self._nav_bar` — QWidget (height=36) with Prev/Next buttons, QSpinBox page selector, `/ N` label, zoom −/+/label
- layout: nav_bar (top) + view (fill)

**Signal:** `page_changed = pyqtSignal(int, int)` — emits (current_1based, total)

**Public methods:**
| Method | Behaviour |
|---|---|
| `load_pdf(path) -> bool` | `self._document.close()` then `self._document.load(path)`. Show nav bar on success. |
| `close_document()` | `self._document.close()`, hide nav bar, reset controls |
| `apply_theme(theme_name, renderer)` | `renderer.get_effective_colors(theme_name)` → stylesheet on `self._view` (background, scrollbars) and `self._nav_bar` (buttons, spinbox, labels) |
| `zoom_in()` / `zoom_out()` / `reset_zoom()` | Clamp between 0.25–4.00, step 0.10; update zoom label |

**Private slots:**
- `_go_prev()` / `_go_next()` — `pageNavigator().jump(page ± 1, QPointF(), 0)`
- `_on_spin_editing_finished()` — jump to spin value - 1 (0-based)
- `_on_page_changed(page)` — sync spin box (blockSignals), update nav button states, emit `page_changed`
- `_on_page_count_changed(count)` — update spin max, page count label

**QPdfDocument.Error note:** `QPdfDocument.Error.None_` (trailing underscore) is the no-error sentinel. Check `self._document.status() == QPdfDocument.Status.Ready` to confirm success.

---

## Step 2 — Modify `viewer/main_window.py`

### 2a. Imports
Add to the `QtWidgets` import block:
```python
QStackedWidget,
```
Add after existing viewer imports:
```python
from .pdf_viewer import PdfViewerWidget
```

### 2b. `setup_ui()` — lines 807–820
Replace bare `QTextBrowser` layout with a stacked layout:
```python
self.content_stack = QStackedWidget()
self.text_browser = QTextBrowser()          # index 0
self.pdf_viewer = PdfViewerWidget(self)     # index 1
self.content_stack.addWidget(self.text_browser)
self.content_stack.addWidget(self.pdf_viewer)
self.content_stack.setCurrentIndex(0)
layout.addWidget(self.content_stack)
```
Wire signal: `self.pdf_viewer.page_changed.connect(self._on_pdf_page_changed)`

### 2c. Add `_is_pdf_mode()` helper (new method)
```python
def _is_pdf_mode(self) -> bool:
    return self.content_stack.currentIndex() == 1
```

### 2d. Refactor `load_file_from_path()` — line 1037
Split into three methods:

**`load_file_from_path(file_path)`** — validates existence, dispatches by `os.path.splitext(file_path)[1].lower()`:
- `.pdf` → `self._load_pdf_file(file_path)`
- anything else → `self._load_markdown_file(file_path)`

**`_load_markdown_file(file_path)`** — existing body of `load_file_from_path` + `self.content_stack.setCurrentIndex(0)` + `self._update_pdf_menu_states()`

**`_load_pdf_file(file_path)`** — calls `self.pdf_viewer.load_pdf(file_path)`, on success: sets stack index 1, title, status bar (shows page count), adds to recent files, calls `self._update_pdf_menu_states()`; on failure: shows `QMessageBox.critical`

### 2e. Consolidate duplicate file-loading in `open_file()`, `open_recent_file()`, `load_last_opened_file()`

All three currently duplicate the read→render→setHtml logic. Simplify:

**`open_file()`** — only changes the dialog filter and calls `self.load_file_from_path(file_path)`:
```python
"Supported Files (*.md *.markdown *.pdf);;Markdown Files (*.md *.markdown);;PDF Files (*.pdf);;All Files (*)"
```

**`open_recent_file(file_path)`** — existence check + `self.load_file_from_path(file_path)` (error handling stays)

**`load_last_opened_file()`** — change inner `try` block to call `self.load_file_from_path(last_file)` (set status message to "Restored: …" after call)

Also update the file dialog in `open_from_recent_directory()` with the same extended filter.

### 2f. Menu state management

In `setup_menu()`, initialise a list and append actions that should be disabled for PDFs:
```python
self._md_only_actions = []
# After creating each relevant action, append it:
self._md_only_actions.append(find_action)          # Ctrl+F
self._md_only_actions.append(zoom_in_action)       # Ctrl++
self._md_only_actions.append(zoom_out_action)      # Ctrl+-
self._md_only_actions.append(reset_zoom_action)    # Ctrl+0
self._md_only_actions.append(refresh_action)       # F5
self._md_only_actions.append(hide_marks_action)    # Ctrl+P
self._md_only_actions.append(edit_external_action) # Ctrl+E
self._md_only_actions.append(copy_action)
self._md_only_actions.append(select_all_action)
```

New method:
```python
def _update_pdf_menu_states(self):
    is_md = not self._is_pdf_mode()
    for action in self._md_only_actions:
        action.setEnabled(is_md)
```

### 2g. Guard markdown-only methods

**`show_find_dialog()`** — add `if self._is_pdf_mode(): return` at top

**`zoom_in()` / `zoom_out()` / `reset_zoom()`** — delegate to PDF viewer when active:
```python
def zoom_in(self):
    if self._is_pdf_mode():
        self.pdf_viewer.zoom_in(); return
    # existing code...
```

**`_refresh_current_document()` / F5 handler** — add `if self._is_pdf_mode(): return` at top

**`keyPressEvent()` — line 1423** — guard `b`-key scroll against `self.text_browser`:
```python
if event.key() == Qt.Key.Key_B and not event.modifiers():
    if self._is_pdf_mode():
        super().keyPressEvent(event); return
    scrollbar = self.text_browser.verticalScrollBar()
    ...
```

### 2h. Add `_on_pdf_page_changed()` slot (new method)
```python
def _on_pdf_page_changed(self, current_page: int, page_count: int):
    self.status_bar.showMessage(
        f"Page {current_page} of {page_count}  —  {os.path.basename(self.current_file)}"
    )
```

### 2i. Extend `apply_theme()` to cover PDF viewer
Add at the end of the existing `apply_theme()` method:
```python
if hasattr(self, "pdf_viewer"):
    self.pdf_viewer.apply_theme(theme_name, self.renderer)
```

---

## Files Modified
| File | Change |
|---|---|
| `viewer/pdf_viewer.py` | **New file** — PdfViewerWidget |
| `viewer/main_window.py` | `setup_ui`, `load_file_from_path` (split), `open_file`, `open_recent_file`, `load_last_opened_file`, `apply_theme`, `zoom_*`, `keyPressEvent`, new `_load_markdown_file`, `_load_pdf_file`, `_is_pdf_mode`, `_update_pdf_menu_states`, `_on_pdf_page_changed` |

No changes to `requirements.txt`, `main.py`, `theme_manager.py`, or `markdown_renderer.py`.

---

## Verification

1. **Run the app** — open a `.md` file: renders as before, nav bar hidden
2. **Open a PDF** (`File > Open`, pick a `.pdf`) — nav bar appears, page count shown
3. **Navigate pages** — Prev/Next buttons, spin box page jump
4. **Zoom** — Ctrl++/Ctrl-/Ctrl+0 work in both modes
5. **Theme switch** (`Ctrl+T`) while PDF open — nav bar and background re-colour
6. **Recent files** — PDF appears in list; clicking restores PDF view
7. **Markdown-only actions** — greyed out in PDF mode; re-enable on switching back to markdown
8. **Session restore** — close with PDF open; reopen app → PDF restored
9. **Edge cases** — corrupt/password-protected PDF shows error dialog, no crash
