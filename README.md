# MDviewer

**Version:** v0.2.6 (2026-02-22)

A PyQt6-based Markdown viewer with GitHub-style rendering, 9 themes, and cross-platform icon support.

## Features

- **GitHub-style rendering** with authentic CSS styling
- **Syntax highlighting** for code blocks using Pygments
- **9 themes** across Built-in and Popular categories
  - Built-in: Dark, Light
  - Popular: Solarized Dark, Solarized Light, Dracula, GitHub, Monokai, Nord, One Dark
  - Live theme switching without restart; `Ctrl+T` toggles dark/light
- **Theme customization**: Per-theme color overrides with live preview for 7 elements (headings, body, background, links, blockquotes, code blocks, borders); factory reset per-theme or all at once
- **Copy to clipboard** button on code blocks — one-click copy with status bar confirmation
- **File info dialog** (`Ctrl+I`): metadata, line/word/character counts, permissions, timestamps
- **Open in external editor** (`Ctrl+E`): detects installed editors, remembers preference; supports GUI and terminal editors
- **Find in document** (`Ctrl+F`) with match highlighting and navigation
- **Recent files and directories** with persistent storage
- **Session restore**: Opens last viewed file on startup
- **Zoom controls**: `Ctrl++`, `Ctrl+-`, `Ctrl+0`
- **Hide paragraph marks** toggle (`Ctrl+P`)
- **Update checker**: Check for and install latest version from GitHub (`Ctrl+U`)
- **Command-line support**: Load files directly from terminal
- **Cross-platform icons**: Platform-aware icon loading (Windows `.ico`, macOS `.icns`, Linux `.png`)
- **Optimized for small files** (<1MB) with fast loading

## Requirements

- Python 3.8+
- PyQt6
- python-markdown
- Pygments

## Installation

### Quick Start

**Linux / macOS / AppImage (no Python needed):**
```bash
# AppImage — portable, no dependencies required
wget https://github.com/juren53/MDviewer/releases/download/v0.2.0/MDviewer-x86_64.AppImage
chmod +x MDviewer-x86_64.AppImage
./MDviewer-x86_64.AppImage

# Or from source with auto-setup
git clone https://github.com/juren53/MDviewer.git
cd MDviewer
./run.sh
```

**Windows (PowerShell):**
```powershell
git clone https://github.com/juren53/MDviewer.git
cd MDviewer
.\run.ps1
```

Both `run.sh` and `run.ps1` auto-create a virtual environment, install dependencies, and launch the app. If PowerShell blocks `run.ps1`, run `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser` once first.

### Manual Setup
```bash
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
python main.py
```

## Usage

```bash
# Open the app
./run.sh                   # Linux/macOS
.\run.ps1                  # Windows PowerShell

# Open a file directly
./run.sh yourfile.md
.\run.ps1 yourfile.md
python main.py yourfile.md
```

## Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| `Ctrl+O` | Open file |
| `Ctrl+F` | Find in document |
| `Ctrl+T` | Toggle dark/light theme |
| `Ctrl+P` | Hide/show paragraph marks |
| `Ctrl++` / `Ctrl+-` / `Ctrl+0` | Zoom in / out / reset |
| `Ctrl+E` | Open in external editor |
| `Ctrl+I` | File info |
| `Ctrl+U` | Check for updates |
| `F5` | Refresh current document |
| `Ctrl+C` | Copy selected text |
| `Ctrl+A` | Select all |
| `Ctrl+Q` | Quit |

## Supported Markdown

- Headers (H1–H6), bold, italic
- Inline code and fenced code blocks with syntax highlighting
- Tables, blockquotes, lists (ordered and unordered)
- Links, horizontal rules, line breaks

## Project Structure

```
MDviewer/
├── main.py                      # Application entry point
├── version.py                   # Centralized version management
├── icon_loader.py               # Cross-platform icon loader
├── requirements.txt             # Python dependencies
├── run.sh                       # Linux/macOS/Git Bash launcher
├── run.ps1                      # Windows PowerShell launcher
├── MDviewer.spec                # PyInstaller build configuration
├── MDviewer.desktop             # Linux desktop integration
├── git_updater.py               # Git-based update system
├── github_version_checker.py    # GitHub release version checker
├── release_downloader.py        # GitHub release download/install
├── viewer/
│   ├── main_window.py           # Main application window
│   ├── markdown_renderer.py     # Markdown parsing and rendering
│   ├── theme_manager.py         # Theme registry and palette management
│   ├── external_editor.py       # Editor detection, picker, and launcher
│   ├── file_info_dialog.py      # File metadata and info dialog
│   ├── color_settings_dialog.py # Color customization dialog
│   └── update_dialogs.py        # Update checker UI dialogs
├── resources/
│   └── icons/                   # Generated cross-platform icon assets
│       ├── app.ico              # Windows taskbar/window icon
│       ├── app.icns             # macOS dock icon
│       └── app.png              # Linux default icon
├── assets/
│   └── icons/                   # Original source icon files
├── tests/
│   └── test_renderer.py         # Unit tests for renderer
└── CHANGELOG.md
```

## Testing

```bash
python tests/test_renderer.py
```

## Version History

See [CHANGELOG.md](CHANGELOG.md) for full version history.

## License

MIT License
