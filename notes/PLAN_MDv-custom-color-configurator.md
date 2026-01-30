# Plan: Add Element Color Customization to MDviewer

## Summary

Add a "Element Colors..." dialog accessible from the View menu that lets users customize colors for key document elements. Each theme (dark/light) stores its own independent color overrides via QSettings. Changes apply immediately. Includes "Reset to Defaults".

## Customizable Elements (7 total)

- Headings (h1-h6)
- Body Text
- Background
- Links
- Blockquotes
- Code Blocks
- Borders/Rules

## Files to Modify

### 1. `viewer/markdown_renderer.py`
- Add `DEFAULT_THEME_COLORS` constant dictionary (single source of truth for defaults)
- Add `custom_colors` dict attribute to `MarkdownRenderer.__init__()`
- Add `get_effective_colors(theme)` method that merges defaults with overrides
- Refactor `get_theme_css()` to use color dictionary instead of hardcoded hex values (eliminates the dark/light if/else branching - both themes use one template)

### 2. `viewer/color_settings_dialog.py` (new file)
- `ColorSettingsDialog` class with grid layout: element label + color swatch button per row
- No hex codes shown to the user - the UI is purely visual
- Clicking a color swatch opens the native OS color picker (`QColorDialog.getColor()`)
- The swatch button displays the currently selected color as its background fill
- Emits `colors_changed` signal for live preview after each color pick
- "Reset to Defaults" and "Close" buttons at bottom
- Theme-aware dialog styling (dark/light chrome to match app)

### 3. `viewer/main_window.py`
- Import `ColorSettingsDialog` and `DEFAULT_THEME_COLORS`
- Add `custom_colors` dict to `MainWindow.__init__()`
- Add `load_custom_colors()` / `save_custom_colors()` using QSettings groups (`custom_colors/dark/...`, `custom_colors/light/...`)
- Add `show_color_settings()` to launch dialog and handle result
- Add `_on_colors_changed()` for live preview during color picking
- Add `_apply_text_browser_stylesheet()` to dynamically generate widget stylesheet from current colors (replaces hardcoded dark-only stylesheet at line 721)
- Add `_refresh_current_document()` helper (consolidates reload logic)
- Add "Element Colors..." menu item to View menu (after "Hide Paragraph Marks")
- Modify `switch_theme()` to apply per-theme custom colors
- Modify `apply_theme()` to use dynamic stylesheet
- Update `show_welcome_message()` to use effective colors
- Update `QuickReferenceDialog` to accept and use custom heading color
- Save custom colors in `closeEvent()`

## Menu Placement

```
View
  Zoom In           Ctrl++
  Zoom Out          Ctrl+-
  Reset Zoom        Ctrl+0
  ───────────────────
  Theme >
  Toggle Theme      Ctrl+T
  Hide Paragraph Marks  Ctrl+P
  ───────────────────
  Element Colors...        <-- NEW
```

## Settings Storage

Only colors that differ from defaults are persisted in QSettings (under `custom_colors/dark/...` and `custom_colors/light/...` groups). Missing keys use the built-in default. Reset clears the group.

## Verification

1. Launch app, open a markdown file
2. View > Element Colors... opens dialog showing current colors
3. Click a color swatch, pick a new color, document updates immediately
4. Close dialog, close app, reopen - colors persist
5. Switch to other theme - it has its own independent colors
6. Reset to Defaults restores original colors
7. Quick Reference dialog also reflects custom heading color
