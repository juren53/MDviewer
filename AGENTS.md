# AGENTS.md

This file provides guidance to AI coding assistants when working with code in this repository.

## Project Overview

MDviewer is a PyQt6-based Markdown viewer with GitHub-style rendering. The application features a modular architecture with separated concerns: the entry point (`main.py`), viewer components (`viewer/`), version management (`version.py`), and update infrastructure (`github_version_checker.py`, `git_updater.py`).

## Common Commands

### Development
```bash
# Run the application
python main.py

# Open a specific file
python main.py yourfile.md

# Run as a module
python -m viewer.main_window
```

### Testing
```bash
# Run renderer tests
python tests/test_renderer.py

# Test GitHub version checker (standalone module test)
python github_version_checker.py

# Test Git updater (standalone module test)
python git_updater.py

# Test Release downloader
python release_downloader.py
python test_release_downloader.py

# Test update dialogs
python test_update_dialog.py
```

### Building
```bash
# Linux: Build executable
./build.sh

# Windows: Build executable (use Windows shell)
.\build.bat

# Linux: Build AppImage (portable Linux executable)
./build_appimage.sh

# Both scripts clean build/dist directories and run:
pyinstaller --clean MDviewer.spec
```

Note: The PyInstaller spec file (`MDviewer.spec`) is dynamically generated - not tracked in version control. Create it via `pyinstaller --onefile main.py` then customize as needed.

#### AppImage Build Details
The AppImage build process creates a portable Linux executable:
- **Script**: `build_appimage.sh` - Complete build automation
- **Spec**: `MDviewer_linux.spec` - Linux-specific PyInstaller configuration
- **Output**: `appimage_build/MDviewer.AppDir/` (without appimagetool) or `MDviewer-x86_64.AppImage` (with appimagetool)

**Prerequisites for AppImage:**
```bash
# Install required tools
sudo apt install python3 python3-pip python3-venv

# Download appimagetool for final AppImage creation
wget https://github.com/AppImage/appimagetool/releases/download/continuous/appimagetool-x86_64.AppImage
chmod +x appimagetool-x86_64.AppImage
```

**Build Process:**
1. Creates isolated Python environment
2. Installs dependencies from requirements.txt
3. Builds with PyInstaller using Linux spec
4. Creates AppDir structure with desktop integration
5. Sets up Qt libraries and plugins
6. Generates final AppImage (if appimagetool available)

The AppImage bundles all dependencies including PyQt6, ensuring compatibility across Linux distributions without requiring system-wide package installations.

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
The application has a sophisticated update system with three complementary modules:

1. **GitHubVersionChecker** (`github_version_checker.py`): Checks GitHub releases API for new versions
   - Designed as reusable module for PyQt5/PyQt6 applications
   - Performs async version checks via threading with callbacks
   - Compares semantic versions with prerelease support (alpha, beta, rc)
   - 10-second network timeout by default
   - Returns `VersionCheckResult` dataclass with update information
   - Uses urllib only (no external dependencies)

2. **GitUpdater** (`git_updater.py`): Performs local git repository updates (for git installations)
   - Uses "force update" strategy: `git fetch` + `git reset --hard origin/main`
   - 30-second timeout on all git operations
   - Reads version from `version.py` before and after update via regex
   - Returns `GitUpdateResult` dataclass with success/failure information
   - Repository detection via `.git` directory check

3. **ReleaseDownloader** (`release_downloader.py`): Downloads and installs release archives (for non-git installations)
   - Downloads release archives (ZIP on Windows, tar.gz on Linux) from GitHub
   - Creates timestamped backups before updates (keeps last 3)
   - Validates archive integrity and version.py existence
   - Provides automatic rollback on failure
   - 30-second timeout on download operations
   - Returns `ReleaseDownloadResult` with update information

The main window automatically detects installation type (git vs non-git) and uses the appropriate updater. Update dialogs (`viewer/update_dialogs.py`) provide UI for version comparison, progress tracking, and results for both update methods.

### Settings Persistence
QSettings is used throughout the application with organization name "MDviewer":
- Recent files list (max 10)
- Window geometry and position
- Last opened file path
- Theme preference ("dark" or "light")
- Paragraph marks visibility ("hide_paragraph_marks" boolean)

Settings are stored in platform-specific locations:
- Linux: `~/.config/MDviewer/MDviewer.conf`
- Windows: Registry under `HKEY_CURRENT_USER\Software\MDviewer\MDviewer`
- macOS: `~/Library/Preferences/com.MDviewer.MDviewer.plist`

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
- `codehilite`: Pygments syntax highlighting with "highlight" CSS class
- `toc`: Table of contents generation with permalink support
- `nl2br`: Newline to `<br>` conversion
- `attr_list`: Attribute lists for custom styling

Code highlighting uses Pygments. Extension configs are defined in `MarkdownRenderer.__init__()` including permalink generation and CSS class names.

### PyQt6 Specifics
- High DPI support is enabled by default in PyQt6 (no manual configuration needed)
- All imports use `PyQt6.QtWidgets`, `PyQt6.QtCore`, `PyQt6.QtGui`
- Signal/slot connections use modern PyQt6 syntax: `signal.connect(slot)`
- Enums use fully qualified names: `Qt.AlignmentFlag.AlignCenter`, `QFont.Weight.Bold`

## Additional Features

### Find/Search Functionality
- Search dialog is theme-aware (recreated on theme changes)
- Highlighting: Current match in yellow, other matches in orange (dark theme) or blue (light theme)
- Uses `QTextCursor` for selection management
- Search state preserved across document navigation

### Refresh
- Reload current document from disk via View → Refresh (F5)
- Calls `_refresh_current_document()` which re-reads and re-renders the file
- Useful for dynamic or externally-edited markdown files

### Paragraph Marks
- Toggle visibility via View → Hide Paragraph Marks (Ctrl+P)
- Pilcrow (¶) symbols on headers, period (.) marks on content
- Uses CSS class `.paragraph-mark` for styling
- Protected from insertion into code blocks
- Headerlinks (`.headerlink`) removed when marks hidden (workaround for QTextBrowser CSS limitation)

## File Size Optimization
The application is optimized for small markdown files (<1MB). Large files may experience slower rendering due to syntax highlighting overhead from Pygments.

## Build Configuration
Note: The `MDviewer.spec` file is not in version control. When building, the spec file should include:
- Hidden imports for PyQt6 modules, markdown extensions, and Pygments
- Icon configuration (uses `assets/icons/icon.ico` if available)
- Console disabled for GUI-only mode
- UPX compression enabled
- Single-file executable output (`--onefile`)
