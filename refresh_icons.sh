#!/bin/bash
# Script to refresh icon caches and desktop environment

echo "Clearing icon caches..."
rm -rf ~/.cache/thumbnails/* 2>/dev/null
rm -rf ~/.cache/icon-cache.kcache 2>/dev/null

echo "Updating desktop database..."
update-desktop-database ~/.local/share/applications/ 2>/dev/null

echo "Updating GTK icon cache..."
gtk-update-icon-cache -f ~/.local/share/icons/hicolor/ 2>/dev/null || true

echo ""
echo "Icon caches cleared!"
echo ""
echo "To fully refresh icons, you need to:"
echo "1. Close all running MDviewer instances"
echo "2. Restart your desktop environment:"
echo "   - For Cinnamon: cinnamon --replace &"
echo "   - Or simply log out and log back in"
echo "   - Or reboot your system"
echo ""
echo "After restarting, the new icon should appear in:"
echo "  - System Menu (taskbar)"
echo "  - System Tray"
echo "  - Window title bar"
echo "  - Help > About dialog"
