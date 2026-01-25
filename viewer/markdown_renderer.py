import markdown
from pygments import highlight
from pygments.lexers import get_lexer_by_name, guess_lexer
from pygments.formatters import HtmlFormatter
import re
import os


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

    def get_theme_css(self, theme):
        """Get theme-specific CSS"""
        if theme == "dark":
            return """
                body {
                    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Helvetica, Arial, sans-serif;
                    font-size: 16px;
                    line-height: 1.5;
                    word-wrap: break-word;
                    color: #c9d1d9;
                    background-color: #0d1117;
                    margin: 0;
                    padding: 20px;
                }
                
                .markdown-body {
                    max-width: 980px;
                    margin: 0 auto;
                }
                
                .markdown-body h1, .markdown-body h2, .markdown-body h3, .markdown-body h4, .markdown-body h5, .markdown-body h6 {
                    color: #58a6ff;
                    border-bottom: 1px solid #30363d;
                    padding-bottom: 0.3em;
                }
                
                .markdown-body table th, .markdown-body table td {
                    padding: 6px 13px;
                    border: 1px solid #30363d;
                }
                
                .markdown-body table th {
                    font-weight: 600;
                    background-color: #161b22;
                }
                
                .markdown-body table tr:nth-child(2n) {
                    background-color: #0d1117;
                }
                
                .markdown-body hr {
                    height: 0.25em;
                    padding: 0;
                    border: 0;
                    background-color: #30363d;
                }
            """
        else:  # light theme
            return """
                body {
                    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Helvetica, Arial, sans-serif;
                    font-size: 16px;
                    line-height: 1.5;
                    word-wrap: break-word;
                    color: #24292e;
                    background-color: #ffffff;
                    margin: 0;
                    padding: 20px;
                }
                
                .markdown-body {
                    max-width: 980px;
                    margin: 0 auto;
                }
                
                .markdown-body h1, .markdown-body h2, .markdown-body h3, .markdown-body h4, .markdown-body h5, .markdown-body h6 {
                    color: #0366d8;
                    border-bottom: 1px solid #e1e4e8;
                    padding-bottom: 0.3em;
                }
                
                .markdown-body table th, .markdown-body table td {
                    padding: 6px 13px;
                    border: 1px solid #d0d7de;
                }
                
                .markdown-body table th {
                    font-weight: 600;
                    background-color: #f6f8fa;
                }
                
                .markdown-body table tr:nth-child(2n) {
                    background-color: #f8f9fa;
                }
                
                .markdown-body hr {
                    height: 0.25em;
                    padding: 0;
                    border: 0;
                    background-color: #e1e4e8;
                }
            """

    def render(self, text):
        """Convert markdown text to HTML with theme-aware formatting."""
        md = markdown.Markdown(
            extensions=self.extensions, extension_configs=self.extension_configs
        )

        html = md.convert(text)

        # Wrap in theme-specific CSS
        theme_css = self.get_theme_css(self.current_theme)
        return f"""
        <style>
            {theme_css}
        </style>
        <div class="markdown-body">
            {html}
        </div>
        """

    def _get_github_css(self):
        """Get GitHub-style CSS for markdown rendering."""

        # Dark theme GitHub markdown CSS
        return """
        body {
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Helvetica, Arial, sans-serif;
            font-size: 16px;
            line-height: 1.5;
            word-wrap: break-word;
            color: #c9d1d9;
            background-color: #0d1117;
            margin: 0;
            padding: 20px;
        }
        
        .markdown-body {
            max-width: 980px;
            margin: 0 auto;
        }
        
        .markdown-body h1, .markdown-body h2, .markdown-body h3, 
        .markdown-body h4, .markdown-body h5, .markdown-body h6 {
            margin-top: 24px;
            margin-bottom: 16px;
            font-weight: 600;
            line-height: 1.25;
            position: relative;
        }
        
        .markdown-body h1 {
            font-size: 2em;
            border-bottom: 1px solid #30363d;
            padding-bottom: 0.3em;
        }
        
        .markdown-body h2 {
            font-size: 1.5em;
            border-bottom: 1px solid #30363d;
            padding-bottom: 0.3em;
        }
        
        .markdown-body h3 {
            font-size: 1.25em;
        }
        
        .markdown-body h4 {
            font-size: 1em;
        }
        
        .markdown-body h5 {
            font-size: 0.875em;
        }
        
        .markdown-body h6 {
            font-size: 0.85em;
            color: #8b949e;
        }
        
        .markdown-body p {
            margin-bottom: 16px;
        }
        
        .markdown-body a {
            color: #58a6ff;
            text-decoration: none;
        }
        
        .markdown-body a:hover {
            text-decoration: underline;
        }
        
        .markdown-body ul, .markdown-body ol {
            padding-left: 2em;
            margin-bottom: 16px;
        }
        
        .markdown-body li {
            margin-bottom: 0.25em;
        }
        
        .markdown-body blockquote {
            padding: 0 1em;
            color: #8b949e;
            border-left: 0.25em solid #30363d;
            margin-bottom: 16px;
        }
        
        .markdown-body code {
            padding: 0.2em 0.4em;
            margin: 0;
            font-size: 85%;
            background-color: rgba(110, 118, 129, 0.4);
            border-radius: 3px;
            font-family: "SFMono-Regular", Consolas, "Liberation Mono", Menlo, monospace;
        }
        
        .markdown-body pre {
            padding: 16px;
            overflow: auto;
            font-size: 85%;
            line-height: 1.45;
            background-color: #161b22;
            border-radius: 6px;
            margin-bottom: 16px;
        }
        
        .markdown-body pre code {
            display: inline;
            max-width: auto;
            padding: 0;
            margin: 0;
            overflow: visible;
            line-height: inherit;
            word-wrap: normal;
            background-color: transparent;
            border: 0;
        }
        
        .markdown-body table {
            border-spacing: 0;
            border-collapse: collapse;
            margin-bottom: 16px;
        }
        
        .markdown-body table th, .markdown-body table td {
            padding: 6px 13px;
            border: 1px solid #30363d;
        }
        
        .markdown-body table th {
            font-weight: 600;
            background-color: #161b22;
        }
        
        .markdown-body table tr:nth-child(2n) {
            background-color: #0d1117;
        }
        
        .markdown-body hr {
            height: 0.25em;
            padding: 0;
            margin: 24px 0;
            background-color: #30363d;
            border: 0;
        }
        
        .highlight {
            background-color: #161b22;
            border-radius: 6px;
            padding: 16px;
            margin-bottom: 16px;
            overflow-x: auto;
        }
        
        .highlight pre {
            background-color: transparent;
            padding: 0;
            margin: 0;
            overflow: visible;
        }
        
        /* Dark theme syntax highlighting */
        .hll { background-color: #404040 }
        .c { color: #6a9955; font-style: italic }
        .err { color: #f44747 }
        .k { color: #569cd6 }
        .o { color: #d4d4d4 }
        .cm { color: #6a9955; font-style: italic }
        .cp { color: #9cdcfe }
        .c1 { color: #6a9955; font-style: italic }
        .cs { color: #6a9955; font-style: italic }
        .gd { color: #f44747 }
        .ge { color: #d4d4d4; font-style: italic }
        .gr { color: #f44747 }
        .gh { color: #569cd6 }
        .gi { color: #4ec9b0 }
        .go { color: #d4d4d4 }
        .gp { color: #6a9955 }
        .gs { font-weight: bold }
        .gu { color: #ce9178 }
        .gt { color: #f44747 }
        .kc { color: #569cd6 }
        .kd { color: #569cd6 }
        .kn { color: #569cd6 }
        .kp { color: #569cd6 }
        .kr { color: #569cd6 }
        .kt { color: #4ec9b0 }
        .m { color: #b5cea8 }
        .s { color: #ce9178 }
        .na { color: #9cdcfe }
        .nb { color: #dcdcaa }
        .nc { color: #4ec9b0 }
        .no { color: #4fc1ff }
        .ni { color: #dcdcaa }
        .ne { color: #f44747 }
        .nf { color: #dcdcaa }
        .nn { color: #4ec9b0 }
        .nt { color: #569cd6 }
        .nv { color: #9cdcfe }
        .ow { color: #569cd6 }
        .w { color: #d4d4d4 }
        .mf { color: #b5cea8 }
        .mh { color: #b5cea8 }
        .mi { color: #b5cea8 }
        .mo { color: #b5cea8 }
        .sb { color: #ce9178 }
        .sc { color: #ce9178 }
        .sd { color: #6a9955; font-style: italic }
        .s2 { color: #ce9178 }
        .se { color: #d7ba7d }
        .sh { color: #ce9178 }
        .si { color: #9cdcfe }
        .sx { color: #4ec9b0 }
        .sr { color: #d16969 }
        .s1 { color: #ce9178 }
        .ss { color: #9cdcfe }
        .bp { color: #569cd6 }
        .vc { color: #9cdcfe }
        .vg { color: #9cdcfe }
        .vi { color: #9cdcfe }
        .il { color: #b5cea8 }
        """
