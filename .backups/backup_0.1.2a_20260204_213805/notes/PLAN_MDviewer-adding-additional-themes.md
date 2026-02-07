# Plan: Adding Additional Themes to MDviewer

## Current Theme Architecture Limitations

The current implementation only supports hardcoded "dark" and "light" themes:
- UI palettes are hardcoded in `ThemeManager.get_fusion_dark_palette()` and `get_fusion_light_palette()`
- Content colors are hardcoded in `DEFAULT_THEME_COLORS` dictionary  
- Theme switching logic assumes binary dark/light toggle

## Required Changes for Additional Themes

### A. UI Layer (`viewer/main_window.py` - ThemeManager class)

**Current structure**:
```python
def get_fusion_dark_palette(): ...
def get_fusion_light_palette(): ...
```

**Proposed structure**:
```python
UI_THEMES = {
    "dark": {...dark palette...},
    "light": {...light palette...},
    "solarized": {...solarized palette...},
    "dracula": {...dracula palette...}
}

def get_theme_palette(theme_name):
    return UI_THEMES.get(theme_name, UI_THEMES["dark"])
```

### B. Content Layer (`viewer/markdown_renderer.py`)

**Current structure**:
```python
DEFAULT_THEME_COLORS = {
    "dark": {...},
    "light": {...}
}
```

**Proposed structure**:
```python
THEME_COLORS = {
    "dark": {...},
    "light": {...},
    "solarized": {...solarized colors...},
    "dracula": {...dracula colors...},
    "github": {...github colors...}
}
```

### C. Theme Management System

**Current QSettings keys**:
- `"current_theme"`: stores "dark" or "light"

**Enhanced storage**:
- `"available_themes"`: list of all theme names
- `"current_theme"`: current theme name
- `"custom_colors_{theme_name}"`: per-theme customizations

## Implementation Strategy

### Phase 1: Theme Registry System
1. Create `Theme` dataclass to define theme properties
2. Implement theme registry to manage available themes
3. Add theme discovery from JSON files or built-in definitions

### Phase 2: UI Updates
1. Update View menu to dynamically populate theme list
2. Replace binary theme toggle with theme selection
3. Add keyboard shortcuts for common themes

### Phase 3: Theme Management
1. Create theme import/export functionality
2. Add theme creation wizard
3. Implement theme validation and conflict resolution

## New Theme Examples

### Solarized Light Theme
```python
"solarized_light": {
    "heading_color": "#586e75",
    "body_text_color": "#657b83", 
    "background_color": "#fdf6e3",
    "link_color": "#268bd2",
    "blockquote_color": "#93a1a1",
    "code_bg_color": "#eee8d5",
    "border_color": "#93a1a1"
}
```

### Dracula Theme
```python
"dracula": {
    "heading_color": "#f8f8f2",
    "body_text_color": "#e2e2e2",
    "background_color": "#282a36",
    "link_color": "#8be9fd", 
    "blockquote_color": "#6272a4",
    "code_bg_color": "#44475a",
    "border_color": "#6272a4"
}
```

### GitHub Theme
```python
"github": {
    "heading_color": "#24292f",
    "body_text_color": "#24292f",
    "background_color": "#ffffff",
    "link_color": "#0969da",
    "blockquote_color": "#57606a",
    "code_bg_color": "#f6f8fa",
    "border_color": "#d0d7de"
}
```

## Files to Modify

### 1. **`viewer/main_window.py`** (lines 254-341)
- Refactor ThemeManager class
- Add dynamic theme loading
- Update menu generation
- Modify theme switching logic
- Update keyboard shortcuts

### 2. **`viewer/markdown_renderer.py`** (lines 10-29)
- Expand DEFAULT_THEME_COLORS to THEME_COLORS
- Update get_theme_css() method
- Add theme validation
- Modify color resolution logic

### 3. **`viewer/color_settings_dialog.py`**
- Update to handle multiple themes
- Add theme selection dropdown
- Per-theme color management
- Update dialog layout for theme switching

### 4. **New File: `viewer/theme_manager.py`**
- Centralized theme registry
- Theme validation and discovery
- Import/export functionality
- Theme creation helpers

## Backward Compatibility Plan

- Maintain existing dark/light theme functionality
- Preserve existing QSettings format with migration
- Keep current API for custom colors
- Ensure no breaking changes for existing users

## Advanced Features

### Theme Packs
- Allow importing theme collections
- Support for community themes
- Theme validation and security

### Auto-switching
- Time-based theme switching
- System theme detection
- Environment-based themes

### Enhanced UI
- Theme preview before applying
- Live theme switching
- Theme favorites/recents

### User Themes
- Save/export custom themes
- Theme sharing capabilities
- Theme versioning

## Technical Considerations

### Performance
- Efficient theme switching without document reload
- Cached theme CSS generation
- Lazy loading of theme definitions

### Security
- Validate theme imports for malicious content
- Sanitize user-provided colors
- Secure theme file parsing

### Accessibility
- High contrast themes
- Colorblind-friendly options
- Text size coordination with themes

## Migration Strategy

1. **Phase 1**: Implement core theme registry without breaking existing functionality
2. **Phase 2**: Add UI enhancements and new built-in themes
3. **Phase 3**: Implement advanced features and user theme management

## Testing Plan

- Unit tests for theme registry
- UI tests for theme switching
- Integration tests for settings persistence
- Performance tests for theme switching speed

---

*Plan generated from codebase analysis on January 30, 2026*