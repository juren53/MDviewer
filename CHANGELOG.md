# Changelog

All notable changes to MDviewer will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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