#!/usr/bin/env python3
"""
Test script for theme system without requiring PyQt6
"""

import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(__file__))


# Test basic theme registry functionality
def test_theme_registry():
    """Test theme registry without PyQt6 dependencies"""
    try:
        # Mock PyQt6 classes for testing
        class MockColor:
            def __init__(self, r, g, b):
                self.r = r
                self.g = g
                self.b = b

        class MockPalette:
            def __init__(self):
                pass

            def setColor(self, role, color):
                pass

        class MockSettings:
            def __init__(self):
                pass

            def value(self, key):
                return None

            def setValue(self, key, value):
                pass

        # Mock PyQt6 imports
        sys.modules["PyQt6"] = type(sys)("PyQt6")
        sys.modules["PyQt6.QtGui"] = type(sys)("PyQt6.QtGui")
        sys.modules["PyQt6.QtCore"] = type(sys)("PyQt6.QtCore")

        sys.modules["PyQt6.QtGui"].QColor = MockColor
        sys.modules["PyQt6.QtGui"].QPalette = MockPalette
        sys.modules["PyQt6.QtCore"].QSettings = MockSettings

        # Now test theme manager
        from viewer.theme_manager import (
            get_theme_registry,
            Theme,
            ThemeColors,
            UIPalette,
        )

        registry = get_theme_registry()
        themes = registry.get_all_themes()

        print("SUCCESS: Theme registry created successfully")
        print(f"SUCCESS: Available themes: {list(themes.keys())}")

        # Test dark theme
        dark_theme = registry.get_theme("dark")
        if dark_theme:
            print(f"SUCCESS: Dark theme: {dark_theme.display_name}")
            print(f"  - Background: {dark_theme.content_colors.background_color}")
            print(f"  - Text: {dark_theme.content_colors.body_text_color}")

        # Test new themes
        for theme_name in ["solarized_light", "dracula", "github"]:
            theme = registry.get_theme(theme_name)
            if theme:
                print(f"SUCCESS: {theme.display_name} theme: {theme.description}")
                print(f"  - Background: {theme.content_colors.background_color}")
                print(f"  - Category: {theme.category}")

        # Test theme categories
        popular_themes = registry.get_themes_by_category("Popular")
        print(f"SUCCESS: Popular themes: {[t.display_name for t in popular_themes]}")

        print("")
        print("SUCCESS: All theme system tests passed!")
        return True

    except Exception as e:
        print(f"ERROR: {e}")
        import traceback

        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = test_theme_registry()
    sys.exit(0 if success else 1)
