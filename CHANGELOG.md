# Changelog

All notable changes to MDviewer will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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