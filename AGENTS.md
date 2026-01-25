# AGENTS.md

This file provides guidance to WARP (warp.dev) when working with code in this repository.

## Project Overview

MDviewer is a PyQt6-based Markdown viewer with GitHub-style rendering. The application features a modular architecture with separated concerns: the entry point (`main.py`), viewer components (`viewer/`), version management (`version.py`), and update infrastructure (`github_version_checker.py`, `git_updater.py`).

## Common Commands

### Development
```powershell
# Run the application
python main.py

# Open a specific file
python main.py yourfile.md

# Run as a module
python -m viewer.main_window
```

### Testing
```powershell
# Run renderer tests
python tests/test_renderer.py

# Test GitHub version checker
python github_version_checker.py

# Test Git updater
python git_updater.py

# Test update dialogs
python test_update_dialog.py
```

### Building
```powershell
# Windows: Build executable
.\build.bat

# Linux/macOS: Build executable
./build.sh

# Manual PyInstaller build
pyinstaller --clean MDviewer.spec
```

The build process uses PyInstaller with a spec file that bundles all dependencies including PyQt6, markdown, and Pygments. The output is a single executable in `dist/MDviewer.exe` (Windows) or `dist/MDviewer` (Linux/macOS).

### Installation
```powershell
# Install dependencies
pip install -r requirements.txt
```

## Code Architecture

### Application Startup Flow
1. `main.py` initializes QApplication with Fusion style
2. Theme palette is applied (dark theme by default from QSettings)
3. Command-line arguments are parsed for file paths
4. `MainWindow` is instantiated with optional file path
5. Window is shown and event loop starts

### Theme System
The application uses a dual-layer theming approach:
- **UI Theme**: Qt Fusion style with custom dark/light palettes (`ThemeManager.get_fusion_dark_palette()` / `get_fusion_light_palette()`)
- **Content Theme**: CSS-based markdown rendering with GitHub-style themes (`MarkdownRenderer.get_theme_css()`)

Theme changes require reloading the current document to update both UI and content rendering. Theme preference persists via QSettings.

### Version Management
All version information is centralized in `version.py`:
- `__version__`: Semantic version string (e.g., "0.3.0")
- `__version_date__`: Date in YYYY-MM-DD format
- `get_version_string()`: Returns "v{version} {date} CST" format

The timezone MUST always be CST/CDT per project rules. When updating versions, modify `version.py` and update the README.md file.

### Update System Architecture
The application has a sophisticated update system with two complementary modules:

1. **GitHubVersionChecker** (`github_version_checker.py`): Checks GitHub releases API for new versions
   - Performs async version checks via threading
   - Compares semantic versions with prerelease support (alpha, beta, rc)
   - Returns `VersionCheckResult` with update information

2. **GitUpdater** (`git_updater.py`): Performs local git repository updates
   - Uses "force update" strategy: `git fetch` + `git reset --hard origin/main`
   - 30-second timeout on all git operations
   - Reads version from `version.py` before and after update
   - Returns `GitUpdateResult` with success/failure information

Update dialogs (`viewer/update_dialogs.py`) provide UI for version comparison, progress tracking, and results.

### Settings Persistence
QSettings is used throughout the application with organization name "MDviewer":
- Recent files list (max 10)
- Window geometry and position
- Last opened file path
- Theme preference ("dark" or "light")

## Important Conventions

### Timezone Requirements
**CRITICAL**: All timestamps must use Central Time USA (CST/CDT), never UTC or other timezones.
- Version strings: `v0.0.3 2026-01-25 0525 CST`
- Changelog entries: `[0.0.3] - 2026-01-25 0525 CST` (date AND time in HHMM format required!)
- Always include timezone indicator (CST or CDT)
- Time format: 24-hour HHMM (e.g., 1120 for 11:20 AM, 1645 for 4:45 PM)

### Version Format
- Releases: `v0.0.X` (e.g., v0.0.3)
- Point releases: `v0.0.Xa`, `v0.0.Xb`, `v0.0.Xc` (e.g., v0.0.2b)
- Update version info in: `version.py`, README.md, About dialog, and UI labels

### Module Structure
```
viewer/
├── __init__.py
├── main_window.py          # MainWindow class, ThemeManager, AboutDialog, QuickReferenceDialog
├── markdown_renderer.py    # MarkdownRenderer with theme-aware CSS
├── update_dialogs.py       # Version/update dialog components
└── styles/                 # Future: Additional CSS resources
```

### Markdown Extensions
The `MarkdownRenderer` uses these python-markdown extensions:
- `tables`: GitHub-style tables
- `fenced_code`: Fenced code blocks with language specifiers
- `codehilite`: Pygments syntax highlighting
- `toc`: Table of contents generation
- `nl2br`: Newline to `<br>` conversion
- `attr_list`: Attribute lists

Code highlighting uses Pygments with the "highlight" CSS class.

### PyQt6 Specifics
- High DPI support is enabled by default in PyQt6 (no manual configuration needed)
- All imports use `PyQt6.QtWidgets`, `PyQt6.QtCore`, `PyQt6.QtGui`
- Signal/slot connections use modern PyQt6 syntax: `signal.connect(slot)`
- Enums use fully qualified names: `Qt.AlignmentFlag.AlignCenter`, `QFont.Weight.Bold`

## File Size Optimization
The application is optimized for small markdown files (<1MB). Large files may experience slower rendering due to syntax highlighting overhead from Pygments.

## Build Configuration
The `MDviewer.spec` file includes:
- Hidden imports for PyQt6 modules, markdown extensions, and Pygments
- Icon configuration (uses `assets/icons/icon.ico` if available)
- Console disabled for GUI-only mode
- UPX compression enabled
- Single-file executable output
