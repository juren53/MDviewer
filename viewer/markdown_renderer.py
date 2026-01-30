import markdown
from pygments import highlight
from pygments.lexers import get_lexer_by_name, guess_lexer
from pygments.formatters import HtmlFormatter
import re
import os

# Import theme manager for centralized theme handling
from .theme_manager import get_theme_registry


class CodeBlockExtension(markdown.extensions.Extension):
    """Extension to handle code blocks with syntax highlighting using Pygments."""

    def extendMarkdown(self, md):
        pattern = re.compile(r"```(\w+)?\n(.*?)\n```", re.DOTALL)
        md.treeprocessors.register(CodeBlockProcessor(pattern), "codeblock", 200)


class CodeBlockProcessor(markdown.treeprocessors.Treeprocessor):
    """Process code blocks and add syntax highlighting."""

    def __init__(self, pattern):
        super().__init__(md=None)
        self.pattern = pattern

    def run(self, doc):
        # This is a simplified approach - we'll handle code blocks in post-processing
        pass


class MarkdownRenderer:
    """Handles markdown to HTML conversion with GitHub-style formatting."""

    def __init__(self, theme="dark"):
        # Set up markdown extensions
        self.extensions = [
            "markdown.extensions.tables",
            "markdown.extensions.fenced_code",
            "markdown.extensions.codehilite",
            "markdown.extensions.toc",
            "markdown.extensions.nl2br",
            "markdown.extensions.attr_list",
        ]

        # Current theme
        self.current_theme = theme
        # Paragraph marks state
        self.hide_paragraph_marks = False
        # Custom color overrides (populated from QSettings)
        self.custom_colors = {}

        # Configure code highlighting
        self.extension_configs = {
            "markdown.extensions.codehilite": {
                "css_class": "highlight",
                "use_pygments": True,
            },
            "markdown.extensions.toc": {
                "permalink": True,
                "permalink_class": "headerlink",
            },
        }

        self.md = markdown.Markdown(
            extensions=self.extensions, extension_configs=self.extension_configs
        )

    def get_effective_colors(self, theme):
        """Return the color dictionary for the given theme, with custom overrides applied."""
        registry = get_theme_registry()
        theme_obj = registry.get_theme(theme)

        if not theme_obj:
            # Fallback to dark theme
            theme_obj = registry.get_theme("dark")

        base = dict(theme_obj.content_colors.__dict__)
        base.update(self.custom_colors)
        return base

    def get_theme_css(self, theme, hide_paragraph_marks=False):
        """Get theme-specific CSS"""
        colors = self.get_effective_colors(theme)
        paragraph_mark_color = colors["blockquote_color"]

        return f"""
                body {{
                    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Helvetica, Arial, sans-serif;
                    font-size: 16px;
                    line-height: 1.5;
                    word-wrap: break-word;
                    color: {colors["body_text_color"]};
                    background-color: {colors["background_color"]};
                    margin: 0;
                    padding: 20px;
                }}

                .markdown-body {{
                    max-width: 980px;
                    margin: 0 auto;
                }}

                .markdown-body h1, .markdown-body h2, .markdown-body h3, .markdown-body h4, .markdown-body h5, .markdown-body h6 {{
                    color: {colors["heading_color"]};
                    border-bottom: 1px solid {colors["border_color"]};
                    padding-bottom: 0.3em;
                }}

                .markdown-body table th, .markdown-body table td {{
                    padding: 6px 13px;
                    border: 1px solid {colors["border_color"]};
                }}

                .markdown-body table th {{
                    font-weight: 600;
                    background-color: {colors["code_bg_color"]};
                }}

                .markdown-body table tr:nth-child(2n) {{
                    background-color: {colors["background_color"]};
                }}

                .markdown-body hr {{
                    height: 0.25em;
                    padding: 0;
                    border: 0;
                    background-color: {colors["border_color"]};
                }}

                .paragraph-mark {{
                    color: {paragraph_mark_color};
                    font-size: 0.8em;
                    opacity: 0.6;
                    margin-left: 4px;
                    font-weight: normal;
                    display: inline;
                }}

                .headerlink {{
                    color: {paragraph_mark_color};
                    font-size: 0.8em;
                    opacity: 0.6;
                    margin-left: 4px;
                    text-decoration: none;
                }}

                .paragraph-marks-hidden .paragraph-mark,
                .paragraph-marks-hidden .headerlink {{
                    display: none;
                }}
            """

    def render(self, text):
        """Convert markdown text to HTML with theme-aware formatting."""
        md = markdown.Markdown(
            extensions=self.extensions, extension_configs=self.extension_configs
        )

        html = md.convert(text)

        # Handle paragraph marks visibility
        if self.hide_paragraph_marks:
            # Remove headerlink (pilcrow) elements from HTML since CSS hiding
            # doesn't work reliably in QTextBrowser
            html = re.sub(r'<a[^>]*class="headerlink"[^>]*>.*?</a>', "", html)
        else:
            # Add paragraph marks (periods) when visible
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

    def _add_paragraph_marks(self, html):
        """Add paragraph marks (periods) to appropriate lines in HTML."""
        import re

        # Split HTML into lines
        lines = html.split("\n")
        processed_lines = []

        # Track if we're inside code blocks
        in_code_block = False
        in_inline_code = False

        for line in lines:
            # Check for code block boundaries
            if line.strip().startswith("<pre>") or "<pre" in line:
                in_code_block = True
            elif line.strip().startswith("</pre>") or "</pre>" in line:
                in_code_block = False

            # Skip processing if inside code blocks
            if in_code_block:
                processed_lines.append(line)
                continue

            # Check for inline code
            if "<code>" in line and "</code>" in line:
                # Count code tags to handle multiple inline codes
                code_count = line.count("<code>")
                if code_count % 2 == 1:
                    in_inline_code = not in_inline_code

            # Add paragraph marks to appropriate lines
            if (
                not in_inline_code
                and not in_code_block
                and self._should_have_paragraph_mark(line)
            ):
                line = self._add_period_to_line(line)

            processed_lines.append(line)

        return "\n".join(processed_lines)

    def _should_have_paragraph_mark(self, line):
        """Determine if a line should have a paragraph mark."""
        # Skip empty lines
        if not line.strip():
            return False

        # Skip lines that are just HTML tags without content
        stripped = line.strip()
        if (
            stripped.startswith("<")
            and stripped.endswith(">")
            and not any(
                tag in stripped for tag in ["<h", "<p>", "<div", "<ul", "<ol", "<li"]
            )
        ):
            return False

        # Headers (titles and sections)
        if re.search(r"<h[1-6][^>]*>", line):
            return True

        # Paragraph tags
        if re.search(r"<p[^>]*>", line):
            return True

        # List items
        if re.search(r"<li[^>]*>", line):
            return True

        # Blockquotes
        if re.search(r"<blockquote[^>]*>", line):
            return True

        return False

    def _add_period_to_line(self, line):
        """Add a period to the end of content in HTML line."""
        # Find the closing of the last tag before the content ends
        # We want to add the period after the text content but before the closing tag
        # IMPORTANT: The period must be INSIDE the span so CSS can hide it

        # For headers: add period after header text
        header_match = re.search(r"(<h[1-6][^>]*>)(.*?)(</h[1-6]>)", line)
        if header_match:
            return f"{header_match.group(1)}{header_match.group(2)}<span class='paragraph-mark'>.</span>{header_match.group(3)}"

        # For paragraphs: add period before closing p tag
        paragraph_match = re.search(r"(<p[^>]*>)(.*?)(</p>)", line)
        if paragraph_match:
            return f"{paragraph_match.group(1)}{paragraph_match.group(2)}<span class='paragraph-mark'>.</span>{paragraph_match.group(3)}"

        # For list items: add period before closing li tag
        list_match = re.search(r"(<li[^>]*>)(.*?)(</li>)", line)
        if list_match:
            return f"{list_match.group(1)}{list_match.group(2)}<span class='paragraph-mark'>.</span>{list_match.group(3)}"

        # For blockquotes: add period before closing blockquote tag
        blockquote_match = re.search(r"(<blockquote[^>]*>)(.*?)(</blockquote>)", line)
        if blockquote_match:
            return f"{blockquote_match.group(1)}{blockquote_match.group(2)}<span class='paragraph-mark'>.</span>{blockquote_match.group(3)}"

        # For other content, try to add period before the last closing tag
        # This is a fallback for edge cases
        if not line.strip().endswith("</"):
            return line

        # Find the last closing tag position
        last_tag_pos = line.rfind("</")
        if last_tag_pos > 0:
            # Insert period before the last closing tag
            before_tag = line[:last_tag_pos]
            after_tag = line[last_tag_pos:]
            return f"{before_tag}<span class='paragraph-mark'>.</span>{after_tag}"

        return line

    def _get_github_css(self):
        """Get GitHub-style CSS for markdown rendering."""
        colors = self.get_effective_colors(self.current_theme)

        return f"""
        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Helvetica, Arial, sans-serif;
            font-size: 16px;
            line-height: 1.5;
            word-wrap: break-word;
            color: {colors["body_text_color"]};
            background-color: {colors["background_color"]};
            margin: 0;
            padding: 20px;
        }}

        .markdown-body {{
            max-width: 980px;
            margin: 0 auto;
        }}

        .markdown-body h1, .markdown-body h2, .markdown-body h3,
        .markdown-body h4, .markdown-body h5, .markdown-body h6 {{
            margin-top: 24px;
            margin-bottom: 16px;
            font-weight: 600;
            line-height: 1.25;
            position: relative;
        }}

        .markdown-body h1 {{
            font-size: 2em;
            border-bottom: 1px solid {colors["border_color"]};
            padding-bottom: 0.3em;
        }}

        .markdown-body h2 {{
            font-size: 1.5em;
            border-bottom: 1px solid {colors["border_color"]};
            padding-bottom: 0.3em;
        }}

        .markdown-body h3 {{
            font-size: 1.25em;
        }}

        .markdown-body h4 {{
            font-size: 1em;
        }}

        .markdown-body h5 {{
            font-size: 0.875em;
        }}

        .markdown-body h6 {{
            font-size: 0.85em;
            color: {colors["blockquote_color"]};
        }}

        .markdown-body p {{
            margin-bottom: 16px;
        }}

        .markdown-body a {{
            color: {colors["link_color"]};
            text-decoration: none;
        }}

        .markdown-body a:hover {{
            text-decoration: underline;
        }}

        .markdown-body ul, .markdown-body ol {{
            padding-left: 2em;
            margin-bottom: 16px;
        }}

        .markdown-body li {{
            margin-bottom: 0.25em;
        }}

        .markdown-body blockquote {{
            padding: 0 1em;
            color: {colors["blockquote_color"]};
            border-left: 0.25em solid {colors["border_color"]};
            margin-bottom: 16px;
        }}

        .markdown-body code {{
            padding: 0.2em 0.4em;
            margin: 0;
            font-size: 85%;
            background-color: rgba(110, 118, 129, 0.4);
            border-radius: 3px;
            font-family: "SFMono-Regular", Consolas, "Liberation Mono", Menlo, monospace;
        }}

        .markdown-body pre {{
            padding: 16px;
            overflow: auto;
            font-size: 85%;
            line-height: 1.45;
            background-color: {colors["code_bg_color"]};
            border-radius: 6px;
            margin-bottom: 16px;
        }}

        .markdown-body pre code {{
            display: inline;
            max-width: auto;
            padding: 0;
            margin: 0;
            overflow: visible;
            line-height: inherit;
            word-wrap: normal;
            background-color: transparent;
            border: 0;
        }}

        .markdown-body table {{
            border-spacing: 0;
            border-collapse: collapse;
            margin-bottom: 16px;
        }}

        .markdown-body table th, .markdown-body table td {{
            padding: 6px 13px;
            border: 1px solid {colors["border_color"]};
        }}

        .markdown-body table th {{
            font-weight: 600;
            background-color: {colors["code_bg_color"]};
        }}

        .markdown-body table tr:nth-child(2n) {{
            background-color: {colors["background_color"]};
        }}

        .markdown-body hr {{
            height: 0.25em;
            padding: 0;
            margin: 24px 0;
            background-color: {colors["border_color"]};
            border: 0;
        }}

        .highlight {{
            background-color: {colors["code_bg_color"]};
            border-radius: 6px;
            padding: 16px;
            margin-bottom: 16px;
            overflow-x: auto;
        }}

        .highlight pre {{
            background-color: transparent;
            padding: 0;
            margin: 0;
            overflow: visible;
        }}

        /* Syntax highlighting */
        .hll {background - color: #404040 }
        .c {color: #6a9955; font-style: italic }
        .err {color: #f44747 }
        .k {color: #569cd6 }
        .o {color: #d4d4d4 }
        .cm {color: #6a9955; font-style: italic }
        .cp {color: #9cdcfe }
        .c1 {color: #6a9955; font-style: italic }
        .cs {color: #6a9955; font-style: italic }
        .gd {color: #f44747 }
        .ge {color: #d4d4d4; font-style: italic }
        .gr {color: #f44747 }
        .gh {color: #569cd6 }
        .gi {color: #4ec9b0 }
        .go {color: #d4d4d4 }
        .gp {color: #6a9955 }
        .gs {font - weight: bold }
        .gu {color: #ce9178 }
        .gt {color: #f44747 }
        .kc {color: #569cd6 }
        .kd {color: #569cd6 }
        .kn {color: #569cd6 }
        .kp {color: #569cd6 }
        .kr {color: #569cd6 }
        .kt {color: #4ec9b0 }
        .m {color: #b5cea8 }
        .s {color: #ce9178 }
        .na {color: #9cdcfe }
        .nb {color: #dcdcaa }
        .nc {color: #4ec9b0 }
        .no {color: #4fc1ff }
        .ni {color: #dcdcaa }
        .ne {color: #f44747 }
        .nf {color: #dcdcaa }
        .nn {color: #4ec9b0 }
        .nt {color: #569cd6 }
        .nv {color: #9cdcfe }
        .ow {color: #569cd6 }
        .w {color: #d4d4d4 }
        .mf {color: #b5cea8 }
        .mh {color: #b5cea8 }
        .mi {color: #b5cea8 }
        .mo {color: #b5cea8 }
        .sb {color: #ce9178 }
        .sc {color: #ce9178 }
        .sd {color: #6a9955; font-style: italic }
        .s2 {color: #ce9178 }
        .se {color: #d7ba7d }
        .sh {color: #ce9178 }
        .si {color: #9cdcfe }
        .sx {color: #4ec9b0 }
        .sr {color: #d16969 }
        .s1 {color: #ce9178 }
        .ss {color: #9cdcfe }
        .bp {color: #569cd6 }
        .vc {color: #9cdcfe }
        .vg {color: #9cdcfe }
        .vi {color: #9cdcfe }
        .il {color: #b5cea8 }
        """
