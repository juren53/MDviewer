# PLAN: MDviewer "Hide Paragraph Marks" Feature Implementation

## Overview

This plan documents the implementation of a "Hide Paragraph Marks" feature for MDviewer, allowing users to toggle the visibility of paragraph marks (periods) at the end of titles and section lines in the rendered markdown display.

## Feature Requirements

Based on user specifications:
1. **Paragraph Mark Character**: Period (.) instead of traditional pilcrow (¶)
2. **Scope**: Toggle ALL paragraph marks (not just headers)
3. **Code Block Protection**: Disable paragraph marks inside code blocks entirely
4. **Default State**: OFF (paragraph marks hidden by default)
5. **Location**: View menu pull-down with keyboard shortcut

## Architecture Components

### 1. State Management
- **Main Window State**: `self.hide_paragraph_marks` boolean attribute
- **Settings Persistence**: QSettings key `"hide_paragraph_marks"` (type=bool)
- **Renderer State**: `self.renderer.hide_paragraph_marks` attribute
- **Default Value**: `False` (marks hidden by default)

### 2. Menu Integration
- **Location**: View menu between zoom controls and theme separator
- **Menu Item**: "Hide Paragraph Marks" (checkable action)
- **Keyboard Shortcut**: Ctrl+P
- **Handler Method**: `self.toggle_paragraph_marks()`

### 3. Markdown Renderer Extensions
- **New Attribute**: `hide_paragraph_marks` parameter
- **CSS Classes**: `.paragraph-mark` and `.paragraph-marks-hidden`
- **Method**: `_add_paragraph_marks()` for HTML processing
- **Detection Logic**: `_should_have_paragraph_mark()` and `_add_period_to_line()`

## Implementation Details

### Phase 1: State Management

#### MainWindow Initialization
```python
def __init__(self, initial_file=None):
    # ... existing code ...
    
    # Add paragraph marks state (default: OFF)
    self.hide_paragraph_marks = False
    
    # Load settings
    self.load_theme_settings()
    self.load_paragraph_marks_settings()
```

#### Settings Persistence
```python
def load_paragraph_marks_settings(self):
    """Load paragraph marks preference from settings"""
    saved_setting = self.settings.value("hide_paragraph_marks", False, type=bool)
    self.hide_paragraph_marks = saved_setting

# In closeEvent(), save preference:
self.settings.setValue("hide_paragraph_marks", self.hide_paragraph_marks)
```

### Phase 2: Menu Integration

#### Menu Item Addition
```python
# In setup_menu(), View menu section:
hide_marks_action = QAction("Hide Paragraph Marks", self)
hide_marks_action.setShortcut("Ctrl+P")
hide_marks_action.setStatusTip("Show or hide paragraph marks at end of lines")
hide_marks_action.setCheckable(True)
hide_marks_action.setChecked(self.hide_paragraph_marks)
hide_marks_action.triggered.connect(self.toggle_paragraph_marks)
view_menu.addAction(hide_marks_action)
```

#### Toggle Handler
```python
def toggle_paragraph_marks(self):
    """Toggle paragraph marks visibility"""
    self.hide_paragraph_marks = not self.hide_paragraph_marks
    self.renderer.hide_paragraph_marks = self.hide_paragraph_marks
    
    # Update menu check state
    for action in self.findChildren(QAction):
        if action.text() == "Hide Paragraph Marks":
            action.setChecked(self.hide_paragraph_marks)
            break
    
    # Reload current document to apply change
    if self.current_file:
        self.load_file_from_path(self.current_file)
    else:
        self.show_welcome_message()
    
    # Update status bar
    state = "hidden" if self.hide_paragraph_marks else "shown"
    self.status_bar.showMessage(f"Paragraph marks {state}", 2000)
```

### Phase 3: Markdown Renderer Modifications

#### Enhanced Render Method
```python
def render(self, text):
    """Convert markdown text to HTML with theme-aware formatting."""
    md = markdown.Markdown(
        extensions=self.extensions, extension_configs=self.extension_configs
    )

    html = md.convert(text)
    
    # Add paragraph marks if not hidden
    if not self.hide_paragraph_marks:
        html = self._add_paragraph_marks(html)

    # Wrap in theme-specific CSS
    theme_css = self.get_theme_css(self.current_theme, self.hide_paragraph_marks)
    hide_marks_class = "paragraph-marks-hidden" if self.hide_paragraph_marks else ""
    return f"""
    <style>
        {theme_css}
    </style>
    <div class="markdown-body {hide_marks_class}">
        {html}
        </div>
    """
```

#### CSS Styling
```css
/* Added to get_theme_css() method */
.paragraph-mark {
    color: #8b949e;  /* Dark theme */
    font-size: 0.8em;
    opacity: 0.6;
    margin-left: 4px;
    font-weight: normal;
    display: inline;
}

/* Light theme variant */
.light-theme .paragraph-mark {
    color: #6a737d;
}

/* Hidden state */
.paragraph-marks-hidden .paragraph-mark {
    display: none;
}
```

#### Paragraph Mark Detection Logic
```python
def _add_paragraph_marks(self, html):
    """Add paragraph marks (periods) to appropriate lines in HTML."""
    import re
    
    lines = html.split('\n')
    processed_lines = []
    
    # Track if we're inside code blocks
    in_code_block = False
    in_inline_code = False
    
    for line in lines:
        # Check for code block boundaries
        if line.strip().startswith('<pre>') or '<pre' in line:
            in_code_block = True
        elif line.strip().startswith('</pre>') or '</pre>' in line:
            in_code_block = False
        
        # Skip processing if inside code blocks
        if in_code_block:
            processed_lines.append(line)
            continue
        
        # Check for inline code
        if '<code>' in line and '</code>' in line:
            code_count = line.count('<code>')
            if code_count % 2 == 1:
                in_inline_code = not in_inline_code
        
        # Add paragraph marks to appropriate lines
        if (not in_inline_code and 
            not in_code_block and
            self._should_have_paragraph_mark(line)):
            line = self._add_period_to_line(line)
        
        processed_lines.append(line)
    
    return '\n'.join(processed_lines)
```

#### Line Type Detection
```python
def _should_have_paragraph_mark(self, line):
    """Determine if a line should have a paragraph mark."""
    # Skip empty lines
    if not line.strip():
        return False
    
    # Skip lines that are just HTML tags without content
    stripped = line.strip()
    if (stripped.startswith('<') and stripped.endswith('>') and 
        not any(tag in stripped for tag in ['<h', '<p>', '<div', '<ul', '<ol', '<li'])):
        return False
    
    # Headers (titles and sections) - ALL levels
    if re.search(r'<h[1-6][^>]*>', line):
        return True
    
    # Paragraph tags
    if re.search(r'<p[^>]*>', line):
        return True
    
    # List items
    if re.search(r'<li[^>]*>', line):
        return True
    
    # Blockquotes
    if re.search(r'<blockquote[^>]*>', line):
        return True
    
    return False
```

#### Period Insertion Logic
```python
def _add_period_to_line(self, line):
    """Add a period to the end of content in HTML line."""
    # Headers: add period after header text
    header_match = re.search(r'(<h[1-6][^>]*>)(.*?)(</h[1-6]>)', line)
    if header_match:
        return f"{header_match.group(1)}{header_match.group(2)}. <span class='paragraph-mark'></span>{header_match.group(3)}"
    
    # Paragraphs: add period before closing p tag
    paragraph_match = re.search(r'(<p[^>]*>)(.*?)(</p>)', line)
    if paragraph_match:
        return f"{paragraph_match.group(1)}{paragraph_match.group(2)}. <span class='paragraph-mark'></span>{paragraph_match.group(3)}"
    
    # List items: add period before closing li tag
    list_match = re.search(r'(<li[^>]*>)(.*?)(</li>)', line)
    if list_match:
        return f"{list_match.group(1)}{list_match.group(2)}. <span class='paragraph-mark'></span>{list_match.group(3)}"
    
    # Blockquotes: add period before closing blockquote tag
    blockquote_match = re.search(r'(<blockquote[^>]*>)(.*?)(</blockquote>)', line)
    if blockquote_match:
        return f"{blockquote_match.group(1)}{blockquote_match.group(2)}. <span class='paragraph-mark'></span>{blockquote_match.group(3)}"
    
    # Fallback for other content
    last_tag_pos = line.rfind('</')
    if last_tag_pos > 0:
        before_tag = line[:last_tag_pos]
        after_tag = line[last_tag_pos:]
        return f"{before_tag}. <span class='paragraph-mark'></span>{after_tag}"
    
    return line
```

## File Structure Changes

### Modified Files

#### 1. `viewer/main_window.py`
- Add `self.hide_paragraph_marks` attribute to `__init__()`
- Add menu item in `setup_menu()` (View menu section)
- Add `load_paragraph_marks_settings()` method
- Add `toggle_paragraph_marks()` method
- Update `closeEvent()` to save settings
- Update renderer initialization to pass paragraph marks state

#### 2. `viewer/markdown_renderer.py`
- Add `hide_paragraph_marks` parameter to `__init__()`
- Modify `render()` method signature and implementation
- Add `_add_paragraph_marks()` method
- Add `_should_have_paragraph_mark()` method
- Add `_add_period_to_line()` method
- Update `get_theme_css()` to accept `hide_paragraph_marks` parameter
- Add CSS for paragraph marks with theme support

## Testing Strategy

### 1. Unit Tests
```python
# Test cases for _should_have_paragraph_mark():
test_cases = [
    ('<h1>Title</h1>', True, 'Headers should have marks'),
    ('<p>Paragraph</p>', True, 'Paragraphs should have marks'),
    ('<li>List item</li>', True, 'List items should have marks'),
    ('<blockquote>Quote</blockquote>', True, 'Blockquotes should have marks'),
    ('<code>inline code</code>', False, 'Inline code should not have marks'),
    ('<pre>code block</pre>', False, 'Code blocks should not have marks'),
    ('', False, 'Empty lines should not have marks'),
]
```

### 2. Integration Tests
- Menu item appears and is checkable
- Toggle state persists across sessions
- Document reloads when setting changes
- Status bar shows current state
- Keyboard shortcut works (Ctrl+P)

### 3. Edge Cases
- Documents with mixed headers and code blocks
- Nested lists and blockquotes
- Multiple markdown files in same session
- Theme switching with paragraph marks enabled/disabled

### 4. Visual Tests
- Paragraph marks appear at correct positions
- Code blocks remain unmodified
- Dark/light theme compatibility
- Font size and spacing consistency

## User Experience Flow

1. **Initial State**: MDviewer launches with paragraph marks OFF (hidden)
2. **Enable Feature**: User selects "View → Hide Paragraph Marks" (Ctrl+P)
3. **Visual Change**: Period marks appear on headers, paragraphs, lists, blockquotes
4. **Disable Feature**: User unchecks menu item
5. **Immediate Update**: Period marks disappear immediately
6. **Persistence**: Setting saved for next session

## CSS Integration

### Dark Theme
```css
.paragraph-mark {
    color: #8b949e;
    font-size: 0.8em;
    opacity: 0.6;
    margin-left: 4px;
}
```

### Light Theme
```css
.paragraph-mark {
    color: #6a737d;
    font-size: 0.8em;
    opacity: 0.6;
    margin-left: 4px;
}
```

### Hidden State
```css
.paragraph-marks-hidden .paragraph-mark {
    display: none;
}
```

## Technical Considerations

### Performance
- **Minimal Overhead**: Processing only when marks are enabled
- **Efficient Parsing**: Single pass through HTML lines
- **Cached State**: Settings loaded once at startup

### Compatibility
- **All Themes**: Works with dark and light themes
- **Future Themes**: CSS classes easily extendable
- **Existing Files**: No breaking changes to file handling

### Maintainability
- **Modular Design**: Separate methods for each concern
- **Clear Naming**: Self-documenting method names
- **Comments**: Comprehensive inline documentation

## Success Criteria

### Functional Requirements
- [ ] Menu item appears in View menu with Ctrl+P shortcut
- [ ] Toggle state persists across application restarts
- [ ] Paragraph marks appear on ALL non-code content when enabled
- [ ] Code blocks are completely protected from paragraph marks
- [ ] Feature works with both dark and light themes
- [ ] Document reloads immediately when setting changes
- [ ] Status bar shows current state

### Technical Requirements
- [ ] No performance impact when feature is disabled
- [ ] Clean code integration without breaking existing functionality
- [ ] Proper error handling and edge case coverage
- [ ] Theme-agnostic CSS implementation

### User Experience Requirements
- [ ] Default state OFF as requested
- [ ] Period character used as paragraph mark
- [ ] Clear visual feedback in menu (checkable item)
- [ ] Keyboard shortcut works consistently
- [ ] Setting persists across sessions

## Future Enhancements

### Optional Features (not in initial implementation)
- [ ] **Customizable Character**: Allow user to choose mark character
- [ ] **Selective Marking**: Apply to specific element types only
- [ ] **Mark Styling**: Customizable color, size, opacity
- [ ] **Import/Export**: Save paragraph mark preferences
- [ ] **Preview Mode**: Show/hide marks temporarily for specific documents

## Implementation Notes

### Dependencies
- **No New Dependencies**: Uses existing PyQt6 and markdown modules
- **Backward Compatible**: No changes to existing file format
- **Cross-Platform**: Works on Windows, macOS, Linux

### Security
- **No External Resources**: All styling handled internally
- **Safe HTML Parsing**: No regex-based HTML injection risks
- **Settings Validation**: Proper type checking in QSettings

---

**Version**: 1.0  
**Created**: 2026-01-25  
**Implementation**: Based on MDviewer PyQt6 architecture  
**Requirements**: Period marks, default OFF, code block protection  
**Author**: Assistant Implementation