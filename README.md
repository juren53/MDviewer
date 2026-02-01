# MDviewer

**v0.1.1 2026-02-01**

A PyQt6-based Markdown viewer with GitHub-style rendering, multi-theme support,
and cross-platform icon management.

## Features

- **GitHub-style markdown rendering** with authentic CSS styling
- **Syntax highlighting** for code blocks using Pygments
- **Multi-theme system**: 9 themes across Built-in and Popular categories
  - Built-in: Dark, Light
  - Popular: Solarized Dark, Solarized Light, Dracula, GitHub, Monokai, Nord, One Dark
  - Ctrl+T toggle between dark and light
  - Live theme switching without application restart
- **Theme customization**: Per-theme color overrides with live preview
  - 7 customizable elements: headings, body text, background, links, blockquotes, code blocks, borders
  - Factory reset for individual themes or all themes at once
- **Cross-platform icon support** via [Icon_Manager_Module](https://github.com/juren53/Icon_Manager_Module)
  - Platform-aware icon selection (`.ico`, `.icns`, `.png`)
  - Windows taskbar icon fix (no more generic Python icon)
- **Find in document** (Ctrl+F) with match highlighting and navigation
- **Recent files** and **recent directories** with persistent storage
- **Hide paragraph marks** toggle (Ctrl+P)
- **Session restore**: Opens last viewed file on startup
- **Command-line support**: Load files directly from terminal
- **Zoom controls** (Ctrl++, Ctrl+-, Ctrl+0)
- **Update checker**: Check for and install latest version from GitHub
- **Optimized for small files** (<1MB) with fast loading

## Requirements

- Python 3.8+
- PyQt6
- python-markdown
- Pygments

## Installation

1. Clone or download this repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

Run the application:
```bash
python main.py
```

Or open a file directly:
```bash
python main.py yourfile.md
```

## Menu Structure

### File
- **Open** (Ctrl+O): Open a markdown file
- **Open Recent Files**: Recent files list (max 10)
- **Open Recent Directories**: Quick access to previously used directories
- **Exit** (Ctrl+Q): Close the application

### Edit
- **Find...** (Ctrl+F): Search text in document
- **Copy** (Ctrl+C): Copy selected text
- **Select All** (Ctrl+A): Select all text

### View
- **Zoom In/Out/Reset** (Ctrl++, Ctrl+-, Ctrl+0)
- **Theme**: Select from 9 themes organized by category
- **Toggle Dark/Light** (Ctrl+T)
- **Hide Paragraph Marks** (Ctrl+P)
- **Customize Colors...**: Per-theme color customization dialog

### Help
- **Quick Reference**: Keyboard shortcuts and markdown syntax
- **Changelog**: View version history
- **Get Latest Version** (Ctrl+U): Check for and install updates
- **About**: Application information

## Supported Markdown Features

- Headers (H1-H6)
- Bold and italic text
- Inline code and code blocks with syntax highlighting
- Tables
- Blockquotes
- Lists (ordered and unordered)
- Links
- Horizontal rules
- Line breaks

## Project Structure

```
MDviewer/
├── main.py                      # Application entry point
├── version.py                   # Centralized version management
├── icon_loader.py               # Cross-platform icon loader (from Icon_Manager_Module)
├── requirements.txt             # Python dependencies
├── MDviewer.spec                # PyInstaller build configuration
├── MDviewer.desktop             # Linux desktop integration
├── git_updater.py               # Git-based update system
├── github_version_checker.py    # GitHub release version checker
├── release_downloader.py        # GitHub release download/install
├── viewer/
│   ├── __init__.py
│   ├── main_window.py           # Main application window
│   ├── markdown_renderer.py     # Markdown parsing and rendering
│   ├── theme_manager.py         # Theme registry and palette management
│   ├── color_settings_dialog.py # Color customization dialog
│   └── update_dialogs.py        # Update checker UI dialogs
├── resources/
│   └── icons/                   # Generated cross-platform icon assets
│       ├── app.ico              # Windows taskbar/window icon
│       ├── app.icns             # macOS dock icon
│       ├── app.png              # Linux default icon
│       └── app_16x16.png … app_256x256.png
├── assets/
│   └── icons/                   # Original source icon files
├── tests/
│   └── test_renderer.py         # Unit tests for renderer
├── CHANGELOG.md
├── AGENTS.md                    # Guide for AI agents working in this repo
└── README.md
```

## Testing

Run the test suite:
```bash
python tests/test_renderer.py
```

## License

MIT License
