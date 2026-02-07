# MDviewer Codebase Analysis

## Module Architecture & Line Counts

### Core Application Layer (44 lines)
**main.py** - Application entry point
- Initializes PyQt6 application with Fusion style
- Sets up dark theme palette
- Handles command-line file arguments
- Creates and shows MainWindow

### Version Management (25 lines)
**version.py** - Centralized version info
- Defines current version (v0.0.7)
- Provides version utility functions
- Single source of truth for all version strings

### Update System (695 lines total)
**github_version_checker.py** (283 lines)
- Checks GitHub releases API for updates
- Async version comparison with semantic versioning
- Returns VersionCheckResult with update info

**git_updater.py** (412 lines)  
- Performs local git repository updates
- Uses "force update" strategy (fetch + reset --hard)
- 30-second timeout on git operations
- Returns GitUpdateResult with success/failure status

### Viewer Components (2,824 lines total)
**viewer/main_window.py** (1,644 lines) - Main application hub
- MainWindow class with menu system
- ThemeManager for UI theming (dark/light)
- File operations and recent files management
- Integration with update system
- AboutDialog and QuickReferenceDialog
- QSettings persistence for preferences

**viewer/markdown_renderer.py** (537 lines)
- MarkdownRenderer class with GitHub-style rendering
- Python-markdown extensions (tables, code highlighting, TOC)
- Pygments syntax highlighting for code blocks
- Theme-aware CSS generation
- Default color definitions for dark/light themes

**viewer/update_dialogs.py** (427 lines)
- Collection of update-related dialog components
- VersionCompareDialog for showing available updates
- UpdateProgressDialog with progress tracking
- UpdateResultDialog for displaying results
- ErrorDialog for handling update failures

**viewer/color_settings_dialog.py** (216 lines)
- ColorSettingsDialog for customizing theme colors
- Visual color swatches for document elements
- Real-time color preview
- Theme-specific color management

### Testing (80 lines)
**tests/test_renderer.py** - Unit tests for MarkdownRenderer
- Tests basic markdown rendering
- Validates syntax highlighting
- Checks theme switching functionality

## How Modules Work Together

### Startup Flow
```
main.py → MainWindow → MarkdownRenderer
```

### Theme System
```
ThemeManager (in main_window.py) + MarkdownRenderer themes
```

### Update Flow
```
MainWindow → GitHubVersionChecker → GitUpdater → UpdateDialogs
```

### Settings & Persistence
```
QSettings throughout + ColorSettingsDialog for customization
```

### Version Management
```
All modules reference version.py for consistent version info
```

## Key Design Patterns

1. **Layered Architecture**: Clear separation between UI, rendering, and infrastructure
2. **Centralized Configuration**: Single source of truth for themes and versions
3. **Async Operations**: Version checking uses threading to avoid UI blocking
4. **Theme Consistency**: Dual-layer theming (UI + content) with coordinated switching
5. **Modular Updates**: Separate checking and updating modules for flexibility

## Total Code Metrics

- **Core Application**: 69 lines (main.py + version.py)
- **Update System**: 695 lines
- **Viewer Components**: 2,824 lines  
- **Testing**: 80 lines
- **Total**: 3,668 lines of Python code

## Dependencies & External Libraries

### UI Framework
- **PyQt6**: Complete Qt6 binding for Python
- Uses Fusion style for consistent cross-platform appearance

### Markdown Processing
- **python-markdown**: Core markdown parsing with extensions
- **Pygments**: Syntax highlighting for code blocks
- Custom extensions for enhanced GitHub-style rendering

### Version Control
- **git**: Native git operations via subprocess
- **urllib**: GitHub API communication (no external HTTP clients)

### Build & Deployment
- **PyInstaller**: Single-file executable generation
- Custom spec file with optimized imports and compression

## File Structure
```
MDviewer/
├── main.py                    # Application entry point (44 lines)
├── version.py                 # Version management (25 lines)
├── github_version_checker.py  # Update checking (283 lines)
├── git_updater.py            # Git operations (412 lines)
├── viewer/                   # Main UI components
│   ├── main_window.py        # Main window & themes (1,644 lines)
│   ├── markdown_renderer.py  # Markdown processing (537 lines)
│   ├── update_dialogs.py     # Update UI components (427 lines)
│   └── color_settings_dialog.py # Theme customization (216 lines)
└── tests/                    # Unit tests
    └── test_renderer.py      # Renderer tests (80 lines)
```

Generated: 2026-01-30
Lines of code calculated using `find . -name "*.py" -exec wc -l {} \;`