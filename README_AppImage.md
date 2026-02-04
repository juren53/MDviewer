# MDviewer AppImage Build Instructions

This document explains how to build a portable AppImage for MDviewer on Linux.

## Quick Start

```bash
# Build complete AppImage (requires appimagetool)
./build_appimage.sh

# If appimagetool is missing, the script will create an AppDir
# which you can manually convert to AppImage later
```

## Prerequisites

### Required Packages
```bash
sudo apt install python3 python3-pip python3-venv
```

### AppImage Tool
Download `appimagetool` from GitHub releases:
```bash
wget https://github.com/AppImage/appimagetool/releases/download/continuous/appimagetool-x86_64.AppImage
chmod +x appimagetool-x86_64.AppImage

# Place it in the project root directory for automatic detection
```

## Build Process

### Automated Build
```bash
# Full automated build with AppImage creation
./build_appimage.sh build

# Clean previous builds
./build_appimage.sh clean

# Test existing AppImage
./build_appimage.sh test
```

### Manual Steps
If you prefer manual control:

1. **Create build directory**
   ```bash
   mkdir -p appimage_build && cd appimage_build
   ```

2. **Set up virtual environment**
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   pip install -r ../requirements.txt
   pip install pyinstaller
   ```

3. **Build with PyInstaller**
   ```bash
   cd .. && pyinstaller --clean MDviewer_linux.spec
   ```

4. **Create AppImage**
   ```bash
   cd appimage_build
   ../appimagetool-x86_64.AppImage MDviewer.AppDir MDviewer-x86_64.AppImage
   ```

## Output Files

### AppImage (Final Product)
- **Location**: `appimage_build/MDviewer-x86_64.AppImage`
- **Size**: ~93MB
- **Portable**: Works on any modern Linux distribution

### AppDir (Intermediate)
- **Location**: `appimage_build/MDviewer.AppDir/`
- **Contains**: Application, dependencies, desktop integration files
- **Purpose**: Can be used for debugging or manual AppImage creation

## Usage

### Running the AppImage
```bash
# Make executable (if needed)
chmod +x appimage_build/MDviewer-x86_64.AppImage

# Run application
./appimage_build/MDviewer-x86_64.AppImage

# Open specific file
./appimage_build/MDviewer-x86_64.AppImage README.md
```

### Desktop Integration
The AppImage includes desktop file and icons for integration:
- **Categories**: Office
- **Supported mimetypes**: text/markdown, text/x-markdown
- **Icons**: Multiple sizes (64x64, 128x128, 256x256)

## Architecture

### Bundled Dependencies
- PyQt6 (GUI framework)
- Python 3.11 runtime
- markdown (Markdown parser)
- Pygments (syntax highlighting)
- Qt platform plugins (X11/Wayland support)

### File Structure
```
MDviewer.AppDir/
├── AppRun                    # Executable wrapper
├── mdviewer.desktop          # Desktop entry
├── .DirIcon                 # AppImage icon
└── usr/
    ├── bin/MDviewer         # Main executable
    ├── lib/                # Shared libraries
    ├── plugins/            # Qt plugins
    └── share/
        ├── applications/    # Desktop integration
        └── icons/          # Application icons
```

## Troubleshooting

### Common Issues

**"No such file or directory" error**
- Ensure the AppImage has execute permissions
- Check if your system supports x86_64 architecture

**Application fails to start**
- Verify X11/Wayland display server is running
- Check for missing graphics libraries on older systems

**Icon not showing**
- Icons are embedded in the AppImage
- Some desktop environments may need a restart to recognize new applications

### Debug Mode
For debugging, run the AppImage directly:
```bash
# Extract AppImage (for debugging)
./MDviewer-x86_64.AppImage --appimage-extract
# Look in squashfs-root/ directory
```

## Technical Details

### Build Specifications
- **Target Architecture**: x86_64
- **Python Version**: 3.11
- **Qt Version**: 6.10.2
- **Compression**: SquashFS with zstd
- **Runtime**: AppImage type 2 runtime

### Platform Support
- Ubuntu 20.04+
- Fedora 35+
- Arch Linux
- Debian 11+
- Most other modern Linux distributions

### Exclusions
- No system dependencies required
- No Python installation needed on target system
- No Qt packages required on target system

## Comparison to Other Builds

| Feature | AppImage | Windows EXE | Linux Native |
|---------|----------|--------------|--------------|
| Portable | ✅ | ✅ | ❌ |
| Self-contained | ✅ | ✅ | ❌ |
| Desktop Integration | ✅ | ✅ | ✅ |
| System Dependencies | None | None | Python + Qt |
| File Size | ~93MB | ~80MB | N/A |
| Cross-distro | ✅ | N/A | N/A |

## Maintenance

### Updating the Build
When updating MDviewer:
1. Update version in `version.py`
2. Re-run the build script
3. Test the new AppImage

### Release Process
For official releases:
1. Test on multiple distributions
2. Verify file associations work
3. Update changelog and documentation
4. Upload AppImage to GitHub Releases

## Support

For issues with the AppImage:
1. Check this document for troubleshooting
2. Verify your system meets requirements
3. File an issue on the MDviewer GitHub repository