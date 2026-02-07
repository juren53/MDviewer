#!/bin/bash
echo "Building MDviewer executable..."
echo ""

# Clean previous builds
if [ -d "build" ]; then
    rm -rf build
fi
if [ -d "dist" ]; then
    rm -rf dist
fi

# Build executable
pyinstaller --clean MDviewer.spec

echo ""
echo "Build complete!"
echo "Executable location: dist/MDviewer"
echo "File size: "
ls -lh dist/MDviewer