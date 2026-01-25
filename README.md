# MDviewer

A simple PyQt6-based Markdown viewer with GitHub-style rendering capabilities.

## Features

- **GitHub-style markdown rendering** with authentic CSS styling
- **Syntax highlighting** for code blocks using Pygments
- **Conventional menu system**: File, Edit, View, Help
- **Recent files** support with persistent storage
- **Zoom controls** for better readability
- **Session restore**: Opens last viewed file on startup
- **Command-line support**: Load files directly from terminal
- **Quick reference dialog**: Keyboard shortcuts and markdown syntax
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

## Version

**v0.0.2 2026-01-24 2030 CST**

## Usage

Run the application:
```bash
python main.py
```

Or open a file directly:
```bash
python main.py yourfile.md
```

Or use it as a module:
```bash
python -m viewer.main_window
```

## Menu Structure

### File
- **Open** (Ctrl+O): Open a markdown file
- **Open Recent**: Recent files list (max 10)
- **Exit** (Ctrl+Q): Close the application

### Edit
- **Copy** (Ctrl+C): Copy selected text
- **Select All** (Ctrl+A): Select all text in the viewer

### View
- **Zoom In** (Ctrl++): Increase font size
- **Zoom Out** (Ctrl+-): Decrease font size
- **Reset Zoom** (Ctrl+0): Reset font to default size

### Help
- **Quick Reference**: Keyboard shortcuts and markdown syntax
- **Changelog**: View version history and changes
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
├── main.py                 # Application entry point
├── requirements.txt        # Python dependencies
├── viewer/
│   ├── __init__.py
│   ├── main_window.py      # Main application window
│   └── markdown_renderer.py # Markdown parsing and rendering
├── tests/
│   └── test_renderer.py    # Unit tests for renderer
└── README.md               # This file
```

## Testing

Run the test suite:
```bash
python tests/test_renderer.py
```

## License

MIT License