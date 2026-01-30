# MDviewer Theme Implementation Analysis

## Overview

MDviewer uses a sophisticated dual-layer theme system that separates UI theming from content rendering, providing comprehensive dark/light mode support with user customization capabilities.

## Dual-Layer Theme Architecture

### 1. UI Theme Layer (Fusion Style)

The UI layer uses Qt's Fusion style with custom palettes to theme the application interface components:

**Location**: `viewer/main_window.py` - `ThemeManager` class (lines 254-341)

**Key Components**:
- `get_fusion_dark_palette()`: Creates dark theme with gray color scheme and gold highlights
- `get_fusion_light_palette()`: Creates light theme with white background and blue highlights
- `get_search_css()`: Provides theme-specific search highlighting CSS

**Color Specifications**:

#### Dark Theme Palette
- **Window**: RGB(45, 45, 45) - Dark gray
- **WindowText**: RGB(187, 187, 187) - Light gray text
- **Base**: RGB(30, 30, 30) - Very dark gray (text input areas)
- **Text**: RGB(187, 187, 187) - Light gray
- **Button**: RGB(45, 45, 45) - Dark gray
- **Highlight**: RGB(255, 215, 0) - Gold for search
- **HighlightedText**: RGB(0, 0, 0) - Black

#### Light Theme Palette
- **Window**: RGB(240, 240, 240) - Light gray
- **WindowText**: RGB(0, 0, 0) - Black text
- **Base**: RGB(255, 255, 255) - White (text input areas)
- **Text**: RGB(0, 0, 0) - Black
- **Button**: RGB(240, 240, 240) - Light gray
- **Highlight**: RGB(3, 102, 216) - Blue for search
- **HighlightedText**: RGB(255, 255, 255) - White

**Application**: Applied globally via `QApplication.setPalette()` at startup (`main.py:23-24`)

### 2. Content Theme Layer (CSS-Based)

The content layer handles markdown rendering colors through CSS injection:

**Location**: `viewer/markdown_renderer.py` - `MarkdownRenderer` class

**Centralized Color Definitions**: `DEFAULT_THEME_COLORS` (lines 10-29)

#### Dark Theme Colors
- **heading_color**: `#58a6ff` (Soft blue)
- **body_text_color**: `#c9d1d9` (Light gray)
- **background_color**: `#0d1117` (Very dark blue-gray)
- **link_color**: `#58a6ff` (Soft blue)
- **blockquote_color**: `#8b949e` (Medium gray)
- **code_bg_color**: `#161b22` (Dark blue-gray)
- **border_color**: `#30363d` (Gray)

#### Light Theme Colors
- **heading_color**: `#0366d8` (Blue)
- **body_text_color**: `#24292e` (Dark gray)
- **background_color**: `#ffffff` (White)
- **link_color**: `#0366d8` (Blue)
- **blockquote_color**: `#6a737d` (Gray)
- **code_bg_color**: `#f6f8fa` (Very light gray)
- **border_color**: `#e1e4e8` (Light gray)

**CSS Generation**: `get_theme_css()` method creates comprehensive GitHub-style CSS including:
- Typography and layout
- Header styling with borders
- Table formatting with alternating rows
- Code block styling
- Blockquote formatting
- Syntax highlighting (lines 315-537)

## Theme Management & Persistence

### Settings Storage
- **Location**: QSettings with organization name "MDviewer"
- **Keys**: 
  - `"current_theme"`: Stores "dark" or "light"
  - `"custom_colors_dark"`: Dark theme customizations
  - `"custom_colors_light"`: Light theme customizations

### Loading/Saving Methods
- `load_theme_settings()`: Loads theme preference at startup
- `save_theme_settings()`: Persists theme preference on exit
- `load_custom_colors()`: Loads user color overrides
- `save_custom_colors()`: Saves color customizations

### Theme Switching
- **Method**: `switch_theme()` in MainWindow class
- **Process**:
  1. Update `current_theme` variable
  2. Apply Fusion palette via `apply_theme()`
  3. Update MarkdownRenderer theme
  4. Reload current document to refresh rendering
  5. Update menu check states

## User Customization System

### Color Configuration Dialog
**Location**: `viewer/color_settings_dialog.py` - `ColorSettingsDialog` class

**Features**:
- Visual color picker with native QColorDialog
- Live preview of color changes
- Reset to defaults functionality
- Theme-aware dialog styling

**Color Elements** (7 customizable):
1. **Headings**: Text color for all header levels
2. **Body Text**: Main paragraph text color
3. **Background**: Document background color
4. **Links**: Hyperlink text color
5. **Blockquotes**: Quoted text color
6. **Code Blocks**: Background for inline and block code
7. **Borders**: Table borders, header underlines, etc.

**Color Override Logic**:
```python
def get_effective_colors(self, theme):
    """Return the color dictionary for the given theme, with custom overrides applied."""
    base = dict(DEFAULT_THEME_COLORS.get(theme, DEFAULT_THEME_COLORS["dark"]))
    base.update(self.custom_colors)
    return base
```

## Integration Points

### 1. Application Startup (`main.py`)
```python
# Apply Fusion style for consistent theming
app.setStyle("Fusion")

# Apply dark theme palette during initialization
palette = ThemeManager.get_fusion_dark_palette()
app.setPalette(palette)
```

### 2. Menu Integration
- **Theme submenu** in View menu with checkable actions
- **Keyboard shortcut**: Ctrl+T for theme toggle
- **Customize Colors**: Opens ColorSettingsDialog

### 3. Dialog Theming
All dialogs are theme-aware:
- **QuickReferenceDialog**: Theme-aware HTML content and styling
- **FindDialog**: Theme-aware search highlighting
- **UpdateDialogs**: Theme-aware UI elements

### 4. Search Highlighting
Theme-specific search CSS ensures visibility:
- **Dark**: Gold background (#ffd700) with black text
- **Light**: Blue background (#0366d8) with white text

## Technical Implementation Details

### CSS Injection Strategy
The MarkdownRenderer wraps all content in theme-specific CSS:
```html
<style>
    {theme_css}
</style>
<div class="markdown-body {hide_marks_class}">
    {html_content}
</div>
```

### Paragraph Marks Feature
- Toggleable paragraph marks (periods) for document structure
- CSS class `.paragraph-marks-hidden` controls visibility
- HTML injection adds `<span class='paragraph-mark'>.</span>` to appropriate elements

### Syntax Highlighting
Pygments-based syntax highlighting with theme-aware colors:
- Dark theme uses VS Code Dark Plus color scheme
- Light theme uses GitHub's default syntax colors
- CSS classes `.hll`, `.c`, `.k`, `.s`, etc. for different token types

## Architecture Benefits

1. **Separation of Concerns**: UI and content theming are independent but coordinated
2. **Consistency**: Fusion style ensures native Qt widgets match the overall theme
3. **Customizability**: Users can override any of the 7 color elements per theme
4. **Performance**: CSS-based content rendering is efficient
5. **Maintainability**: Centralized color definitions make updates straightforward
6. **User Experience**: Real-time preview and persistence enhance usability

## Files Involved

- `main.py`: Application startup and initial theme application
- `viewer/main_window.py`: ThemeManager class, theme switching logic, dialog theming
- `viewer/markdown_renderer.py`: Content theming, CSS generation, default colors
- `viewer/color_settings_dialog.py`: User customization interface
- `viewer/update_dialogs.py`: Theme-aware update dialogs

## Conclusion

The MDviewer theme implementation demonstrates a mature, well-architected approach to application theming that balances flexibility, performance, and user experience. The dual-layer system ensures comprehensive theme coverage while the centralized management makes maintenance and updates straightforward.

---

*Analysis generated from codebase examination on January 30, 2026*