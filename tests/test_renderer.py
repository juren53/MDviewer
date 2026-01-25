#!/usr/bin/env python3
"""
Test script for the MarkdownRenderer class
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from viewer.markdown_renderer import MarkdownRenderer


def test_markdown_renderer():
    """Test basic markdown rendering functionality."""

    renderer = MarkdownRenderer()

    # Test basic markdown
    test_markdown = """
# Welcome to MDviewer

This is a **test** markdown document with *italic* text and `inline code`.

## Features

- GitHub-style rendering
- Syntax highlighting
- Tables and more

### Code Example

```python
def hello_world():
    print("Hello, World!")
    return True
```

| Name | Age | City |
|------|-----|------|
| John | 30  | NYC  |
| Jane | 25  | LA   |

> This is a blockquote
> with multiple lines
"""

    print("Testing MarkdownRenderer...")

    try:
        html = renderer.render(test_markdown)

        # Check if basic elements are present
        assert "<h1" in html, "H1 tags not found"
        assert "<h2" in html, "H2 tags not found"
        assert "<strong>test</strong>" in html, "Bold text not found"
        assert "<em>italic</em>" in html, "Italic text not found"
        assert "<code>inline code</code>" in html, "Inline code not found"
        assert "<table>" in html, "Table not found"
        assert "<blockquote>" in html, "Blockquote not found"
        assert "highlight" in html, "Code highlighting not found"

        print("All tests passed!")
        print(f"Generated HTML length: {len(html)} characters")

        # Optionally save to file for manual inspection
        with open("test_output.html", "w", encoding="utf-8") as f:
            f.write(html)
        print("Test output saved to test_output.html")

        return True

    except Exception as e:
        print(f"Test failed: {str(e)}")
        return False


if __name__ == "__main__":
    success = test_markdown_renderer()
    sys.exit(0 if success else 1)
