# Changelog

All notable changes to MDviewer will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.2] - 2026-02-02

### Fixed
- **Blank icons on Linux (LMDE / Cinnamon)** — all icons (app launcher, taskbar, window switcher) were blank after the Icon_Manager_Module integration
  - Root cause: the installed `.desktop` file had a broken absolute path for `Icon=` (missing `icons/` subdirectory)
  - Installed multi-resolution PNGs into the XDG hicolor icon theme (`~/.local/share/icons/hicolor/<size>/apps/mdviewer.png`)
  - Changed `.desktop` `Icon=` from an absolute path to the theme name `mdviewer` — portable and resilient to directory changes
  - Installed updated `.desktop` file to `~/.local/share/applications/`

### Added
- `app.setDesktopFileName("MDviewer")` in `main.py` — required for Linux desktop environments to associate the running window with its `.desktop` file (fixes blank taskbar and Alt+Tab icons)

---

## [0.1.1] - 2026-02-01

### Added
- **Icon Manager Module integration** — cross-platform icon support via [Icon_Manager_Module](https://github.com/juren53/Icon_Manager_Module)
  - `icon_loader.py` and generated icon assets in `resources/icons/`
  - Application icon set on `QApplication` (appears in Alt-Tab, dock, etc.)
  - Window icon set on `MainWindow` (appears in title bar)
  - Windows taskbar icon fix via `set_taskbar_icon()` — resolves the long-standing issue of Python's generic icon appearing on the Windows taskbar instead of the MDviewer icon
  - Platform-aware icon selection: `.ico` on Windows, `.icns` on macOS, multi-resolution PNGs on Linux
  - Silent no-op on non-Windows platforms, so the taskbar fix call is safe in cross-platform code

### Technical
- 3 new lines in `main.py`: import, `app.setWindowIcon()`, `icons.set_taskbar_icon()`
- 2 new lines in `viewer/main_window.py`: import and `self.setWindowIcon()`
- 10 generated icon files in `resources/icons/` (app.ico, app.icns, app.png, 7 sized PNGs)
- AppUserModelID set to `com.mdviewer.mdviewer` for Windows taskbar grouping

---

## [0.1.0] - 2026-01-30 2047 CST

### Added
- **Open Recent Directories** - Quick access to directories of previously opened files
  - New "Open Recent Directories" submenu in File menu (up to 5 entries)
  - Selecting a directory opens a file dialog starting in that location
  - Directories automatically tracked whenever a file is opened
  - "Clear Recent Directories" option to reset the list
  - Persisted across sessions via QSettings
- **Renamed "Open Recent" to "Open Recent Files"** for clarity alongside the new directories submenu
- **Factory Reset for Themes** - Complete theme customization reset capability
  - **Factory Reset All Themes Button**: New prominent red button in Color Settings dialog
  - **Confirmation Dialog**: Warns users before clearing ALL theme customizations
  - **Complete Reset**: Clears custom colors for all themes in one action
  - **Immediate Effect**: Restores all themes to factory defaults instantly
  - **Safety Warning**: "This action cannot be undone" confirmation required

### New Themes
- **Monokai**: Classic warm dark theme with vibrant colors (`#272822` background, `#66d9ef` cyan links)
- **Nord**: Arctic, north-bluish clean and elegant theme (`#2e3440` polar night background, `#88c0d0` frost accents)
- **One Dark**: Atom's iconic dark theme (`#282c34` background, `#61afef` blue headings/links)
- **Solarized Dark**: Dark variant of the Solarized palette (`#002b36` background, `#268bd2` blue links)

### Enhanced
- **Color Settings Dialog** - Improved theme reset controls
  - **Two Reset Options**: "Reset to Defaults" (current theme) and "Factory Reset All Themes" (all themes)
  - **Visual Distinction**: Factory reset button styled in red to indicate destructive action
  - **Clear Tooltips**: Users understand the difference between reset options
  - **Better Organization**: Reset buttons grouped together in dialog footer
- **Theme Library** - Expanded from 5 to 9 total themes
  - Built-in: Dark, Light
  - Popular: Solarized Dark, Solarized Light, Dracula, GitHub, Monokai, Nord, One Dark

### Technical
- **New MainWindow Method**: `reset_all_themes_to_factory()` clears all QSettings theme groups
  - Iterates through all available themes from theme registry
  - Removes all custom color settings from QSettings
  - Clears in-memory custom_colors dictionary
  - Re-applies renderer settings and refreshes display
- **Enhanced ColorSettingsDialog**: `_factory_reset_all_themes()` method with user confirmation
- **QSettings Cleanup**: Comprehensive removal of custom_colors/{theme} groups

---

## [0.0.9] - 2026-01-30 1840 CST

### Added
- **Non-Git Update Support** - Automatic updates now work for both git and non-git installations
  - **ReleaseDownloader Module**: New standalone module for downloading GitHub releases
  - **Archive Support**: Downloads ZIP files on Windows, tar.gz on Linux/macOS
  - **Installation Detection**: Automatically detects git vs non-git installations
  - **Dual Update Paths**: Uses GitUpdater for git repos, ReleaseDownloader for archives
  - **Update Method Display**: Version comparison dialog shows update method ("via git pull" or "via GitHub release download")
- **Backup System** - Safe updates with automatic backup and rollback
  - **Timestamped Backups**: Creates backup_{version}_{timestamp} before each update
  - **Backup Retention**: Automatically keeps last 3 backups, removes older ones
  - **Automatic Rollback**: Restores from backup if update fails
  - **Smart Exclusions**: Excludes .git, .backups, __pycache__ from backups

### Enhanced
- **Update Dialogs** - Enhanced for both update methods
  - **Progress Tracking**: New set_download_progress() method for download progress
  - **Method Indication**: Shows "via git pull" or "via GitHub release download" in dialogs
  - **Unified Experience**: Both git and non-git updates use same dialog system

### Technical
- **New ReleaseDownloader Class** (`release_downloader.py`) - Complete release download system
  - **download_release()**: Downloads release archives from GitHub with 30s timeout
  - **extract_archive()**: Safely extracts ZIP/tarball with validation
  - **backup_installation()**: Creates timestamped backups with retention policy
  - **apply_update()**: Replaces application files preserving permissions
  - **rollback()**: Restores from backup on failure
  - **cleanup()**: Removes temporary files after update
- **Enhanced Main Window**: Installation type detection and update method branching
- **Cross-Platform**: Automatic platform detection for archive format selection
- **Test Suite**: New test_release_downloader.py for validation
- **Documentation**: Updated AGENTS.md with complete update system architecture

### Safety Features
- Archive integrity validation (file size > 0)
- Version file existence check in extracted archives
- Network timeout handling (30 seconds)
- Automatic error recovery with rollback
- Detailed error messages for debugging

---

## [0.0.8] - 2026-01-30 2230 CST

### Added
- **Multi-Theme System** - Complete theme architecture overhaul supporting unlimited themes
  - **5 Built-in Themes**: Dark, Light, Solarized Light, Dracula, GitHub
  - **Theme Categories**: Organized by Built-in and Popular themes
  - **Dynamic Menus**: Theme lists auto-populate from registry (View → Theme)
  - **Theme Registry**: Centralized theme management with validation
  - **Extensible Architecture**: Easy to add new themes without code changes

### Enhanced
- **Color Settings Dialog** - Completely redesigned for multi-theme support
  - **Theme Selector**: Dropdown to switch between themes while customizing
  - **Live Theme Switching**: Change themes without closing dialog
  - **Per-Theme Customization**: Independent color overrides for each theme
  - **Better Organization**: Themes grouped by category in color settings

### New Themes
- **Solarized Light**: Eye-friendly reading theme with warm tones
- **Dracula**: Popular vibrant color scheme with high contrast
- **GitHub**: Official GitHub theme colors matching current GitHub UI

### Technical
- **New Theme Manager** (`viewer/theme_manager.py`) - Complete theme infrastructure
  - **Theme Data Classes**: Structured theme definitions with validation
  - **Theme Registry**: Central storage and discovery system
  - **Backward Compatibility**: Existing themes and settings preserved
  - **Performance**: Efficient theme switching with cached definitions
- **Updated Architecture**: All components now use dynamic theme system
  - **Markdown Renderer**: Migrated from hardcoded colors to registry
  - **Main Window**: Enhanced ThemeManager with registry integration
  - **Color Settings**: Multi-theme support with live preview

---

## [0.0.7] - 2026-01-29 2215 CST

### Added
- **Color Settings Preview Column** - Live preview samples next to each color swatch
  - Headings shown in bold, links shown underlined, blockquotes with left border
  - Code blocks in monospace font, background as filled rectangle, borders as horizontal line
  - Previews update instantly when picking a new color or resetting to defaults
  - Dialog widened from 340px to 520px to accommodate the new column
- **Page Backward with 'b' key** - Press `b` to scroll back one page, matching Unix `less` navigation
  - Complements the existing spacebar page-forward behavior

---

## [0.0.6] - 2026-01-29 2044 CST

### Added
- **Element Color Customization** - Customize colors for key document elements per theme
  - View → Element Colors... menu item opens color configuration dialog
  - 7 customizable elements: Headings, Body Text, Background, Links, Blockquotes, Code Blocks, Borders/Rules
  - Click color swatches to open native OS color picker
  - Live preview: changes apply immediately to the document
  - Independent color overrides for dark and light themes
  - Colors persist across application sessions via QSettings
  - "Reset to Defaults" button restores original theme colors
  - Only colors that differ from defaults are stored

### Technical
- Added `DEFAULT_THEME_COLORS` constant dictionary as single source of truth for theme colors
- Refactored `get_theme_css()` to use color dictionary instead of hardcoded hex values
- New `ColorSettingsDialog` class with grid layout and `colors_changed` signal
- Dynamic stylesheet generation for QTextBrowser replaces hardcoded stylesheet
- Quick Reference dialog reflects custom heading color

---

## [0.0.5] - 2026-01-25 1645 CST

### Added
- **Hide Paragraph Marks** - Toggle visibility of paragraph marks in rendered markdown
  - View → Hide Paragraph Marks menu item with Ctrl+P keyboard shortcut
  - Toggles visibility of pilcrow (¶) symbols on headers and period (.) marks on all content
  - Setting persists across application sessions
  - Status bar feedback shows current state
  - Code blocks protected from paragraph mark insertion

### Fixed
- **Find/Search Highlighting** - Search results now properly highlighted in document
  - Fixed critical bug where format was not applied to text selections
  - Fixed cursor handling that was clearing selections before highlighting
  - Current match shown in yellow, other matches in orange
- **Quick Reference Dialog** - Now theme-aware and readable
  - Colors adapt to current dark/light theme setting
  - Added new keyboard shortcuts (Ctrl+T, Ctrl+P, Ctrl+U)
  - Consolidated and updated shortcut list
- **Find Dialog** - Now theme-aware
  - Dialog colors adapt to current theme setting
  - Recreates with correct theme when theme changes

### Technical
- Paragraph marks use CSS class `.paragraph-mark` for consistent styling
- Header permalinks (`.headerlink`) removed from HTML when marks hidden (QTextBrowser CSS limitation workaround)
- Fixed `QTextCursor` copy issue in search - selections now preserved correctly
- Removed duplicate `force_highlight_update` method definitions

---

## [0.0.4] - 2026-01-25 1120 CST

### Fixed
- **Update Checker** - Resolved critical issues preventing update detection
  - Fixed version number mismatch (corrected 0.3.0 to 0.0.3)
  - Created GitHub Release tag (v0.0.3) for proper version tracking
  - Fixed indentation error in main_window.py causing application crash
  - Fixed update checker freezing due to Qt GUI operations from background thread
  - Implemented proper Qt signal/slot mechanism for thread-safe communication
  - Added 15-second timeout to prevent indefinite hanging
  - Update checker now responds within 5 seconds as expected

### Added
- **AGENTS.md** - Comprehensive guide for Warp AI agents working in this repository
  - Common development, testing, and build commands
  - Architecture documentation including startup flow and theme system
  - Version management and update system details
  - Project-specific conventions and requirements

### Technical
- Introduced UpdateCheckSignals class for proper thread communication
- All dialog operations now run on main GUI thread via signals
- Enhanced error handling with debugging output
- Improved reliability of GitHub release detection

---

## [0.0.3] - 2026-01-25 0525 CST

### Added
- **Theme Selection System** - Complete user-accessible theming controls
  - View → Theme submenu with Dark/Light theme options
  - Ctrl+T keyboard shortcut for quick theme toggling
  - Theme persistence across application sessions
  - Visual feedback via menu check marks and status bar messages
  - Immediate theme switching without application restart
  - Professional Fusion-based theming system fully unlocked
- **Enhanced User Experience**
  - Theme-aware search highlighting (gold for dark, blue for light)
  - Theme-aware markdown rendering with GitHub-style CSS
  - Complete document reload on theme change for full visual refresh
  - Settings integration using QSettings for theme persistence

### Technical
- Leverages existing ThemeManager infrastructure (0 new dependencies)
- Enhanced MainWindow with theme switching methods
- Integration with existing Fusion styling system
- Zero architectural changes - pure feature enhancement

---

## [0.0.2b] - 2026-01-24 2030 CST

### Added
- Linux desktop integration
  - Added MDviewer.desktop file for system menu integration
  - Application appears in Office/Utilities menu category
  - Supports file association with markdown files (.md)
- Application icon (512x512 PNG) in assets directory

---

## [0.0.2] - 2026-01-24

### Added
- Session restore: reopens last viewed file on startup
- CLI support: open files via command line argument
- Quick Reference dialog (Help menu) with markdown syntax guide

---

## [0.0.1] - 2025-01-24

### Added
- Initial release of MDviewer PyQt6 application
- GitHub-style markdown rendering with authentic CSS styling
- Syntax highlighting for code blocks using Pygments
- Conventional menu system (File, Edit, View, Help)
- File operations: Open markdown files via dialog or drag-drop
- Recent files support with persistent storage (max 10 files)
- Zoom controls (In/Out/Reset) for better readability
- Edit functionality: Copy, Select All
- Welcome screen with usage instructions
- About dialog with application information
- Support for all standard markdown features:
  - Headers (H1-H6) with proper styling
  - Bold, italic, and bold-italic text formatting
  - Inline code and fenced code blocks with language detection
  - Tables with GitHub-style formatting
  - Ordered and unordered lists with nested support
  - Blockquotes with nested blockquote support
  - Links with hover effects
  - Horizontal rules
  - Line breaks (GitHub-style)

### Technical Details
- PyQt6-based GUI application
- python-markdown library for parsing
- Pygments for syntax highlighting
- QSettings for persistent recent files storage
- Optimized for small files (<1MB) with fast loading
- Cross-platform compatibility (Windows, Linux, macOS)

### Added
- Dark theme support throughout the application
  - Dark background (#0d1117) with light text (#c9d1d9)
  - VS Code-style syntax highlighting for code blocks
  - Dark scrollbars and UI components
  - Consistent dark theme across welcome screen and documents
- Persistent window position and size settings
  - Saves window geometry on close
  - Restores window position and size on startup
  - Uses QSettings for cross-platform persistence
- Git repository initialization
  - Complete version control setup
  - Comprehensive .gitignore configuration
  - Initial commit with all project files

### Project Structure
- Modular architecture with separated concerns
- Unit tests for markdown renderer
- Comprehensive README documentation
- Sample markdown file for testing features
- Git repository with proper version control