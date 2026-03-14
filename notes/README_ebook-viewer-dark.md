The ebook-viewer-simple script is working! It successfully launched ebook-viewer without the segmentation fault. 

Summary

The segmentation fault was caused by GPU/OpenGL context issues. The solution was to:

1. Use software rendering instead of hardware GPU acceleration
2. Disable WebEngine sandbox to avoid memory issues  
3. Set proper Qt environment variables to force software mode

Working Scripts

You now have several options:

•  ~/.local/bin/ebook-viewer-simple - The working version that bypasses GPU issues
•  ~/.local/bin/ebook-viewer-dark - The enhanced version with error handling (you can update it with the same environment variables from the simple version)
•  ~/.local/bin/ebook-viewer-monitor-dark - The monitoring script for automatic theme enforcement

Usage
bash
