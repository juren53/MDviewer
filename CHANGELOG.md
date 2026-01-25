# Changelog

All notable changes to MDviewer will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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

### Project Structure
- Modular architecture with separated concerns
- Unit tests for markdown renderer
- Comprehensive README documentation
- Sample markdown file for testing features