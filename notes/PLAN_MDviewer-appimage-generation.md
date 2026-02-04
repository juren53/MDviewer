# Plan: Create AppImage for MDviewer

## Overview
This plan outlines the process for creating a portable AppImage for the MDviewer PyQt6-based Markdown viewer. The AppImage will bundle all dependencies, ensuring the application runs on any Linux distribution without requiring system-wide package installations.

## Project Analysis
Based on the current MDviewer project structure:
- **Main executable**: `main.py`
- **Core components**: `viewer/` package with PyQt6 GUI
- **Dependencies**: PyQt6, markdown, Pygments (from requirements.txt)
- **Icons**: Available in `resources/icons/` with multiple sizes
- **Existing build**: Has Windows `.exe` build via `MDviewer.spec` and `build.sh`

## Prerequisites

### Required Tools
```bash
# Install required system packages
sudo apt update
sudo apt install -y python3-pip python3-venv appimagetool
sudo apt install -y libgl1-mesa-dev libxkbcommon-x11-0 libxcb-icccm4
sudo apt install -y libxcb-image0 libxcb-keysyms1 libxcb-randr0
sudo apt install -y libxcb-render-util0 libxcb-xinerama0 libxcb-xfixes0
```

### Python Dependencies
- PyQt6 >= 6.5.0
- markdown >= 3.4.0
- Pygments >= 2.15.0
- pyinstaller (for bundling)

## Step-by-Step Process

### Step 1: Environment Setup
1. **Create build directory structure**
   ```bash
   mkdir -p appimage_build/{AppDir,build}
   cd appimage_build
   ```

2. **Set up Python virtual environment**
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   pip install --upgrade pip
   pip install -r ../requirements.txt
   pip install pyinstaller
   ```

### Step 2: Create Linux-specific PyInstaller Spec
1. **Create `MDviewer_linux.spec`** based on existing Windows spec
2. **Key modifications for Linux:**
   - Update icon paths to use PNG files from `resources/icons/`
   - Add Linux-specific hidden imports for PyQt6
   - Include Qt platform plugins and libraries
   - Add system library dependencies

### Step 3: Build Process
1. **Clean previous builds**
   ```bash
   rm -rf build dist
   ```

2. **Run PyInstaller with Linux spec**
   ```bash
   pyinstaller --clean MDviewer_linux.spec
   ```

3. **Verify executable**
   ```bash
   ./dist/MDviewer --version
   ```

### Step 4: Create AppDir Structure
```
MDviewer.AppDir/
├── usr/
│   ├── bin/
│   │   └── MDviewer (executable)
│   ├── lib/
│   ├── share/
│   │   ├── applications/
│   │   │   └── mdviewer.desktop
│   │   └── icons/
│   │       └── hicolor/
│   │           ├── 256x256/
│   │           │   └── apps/
│   │           │       └── mdviewer.png
│   │           ├── 128x128/
│   │           │   └── apps/
│   │           │       └── mdviewer.png
│   │           └── 64x64/
│   │               └── apps/
│   │                   └── mdviewer.png
├── AppRun (executable wrapper)
├── mdviewer.desktop
└── .DirIcon
```

### Step 5: Desktop Entry and Icons
1. **Create `mdviewer.desktop` file:**
   ```ini
   [Desktop Entry]
   Name=MDviewer
   Comment=A PyQt6-based Markdown viewer with GitHub-style rendering
   Exec=MDviewer
   Icon=mdviewer
   Type=Application
   Categories=Office;TextEditor;Development;
   Terminal=false
   StartupNotify=true
   MimeType=text/markdown;
   ```

2. **Copy and setup icons:**
   ```bash
   cp ../resources/icons/app_256x256.png MDviewer.AppDir/.DirIcon
   mkdir -p MDviewer.AppDir/usr/share/icons/hicolor/{256x256,128x128,64x64}/apps/
   cp ../resources/icons/app_256x256.png MDviewer.AppDir/usr/share/icons/hicolor/256x256/apps/mdviewer.png
   cp ../resources/icons/app_128x128.png MDviewer.AppDir/usr/share/icons/hicolor/128x128/apps/mdviewer.png
   cp ../resources/icons/app_64x64.png MDviewer.AppDir/usr/share/icons/hicolor/64x64/apps/mdviewer.png
   ```

### Step 6: Runtime Dependencies
1. **Copy PyQt6 runtime libraries:**
   ```bash
   cp -r ../venv/lib/python3.*/site-packages/PyQt6/Qt/lib/* MDviewer.AppDir/usr/lib/
   ```

2. **Include Qt platform plugins:**
   ```bash
   mkdir -p MDviewer.AppDir/usr/plugins
   cp -r ../venv/lib/python3.*/site-packages/PyQt6/Qt/plugins/* MDviewer.AppDir/usr/plugins/
   ```

3. **Create AppRun wrapper:**
   ```bash
   cat > MDviewer.AppDir/AppRun << 'EOF'
   #!/bin/bash
   HERE="$(dirname "$(readlink -f "${0}")")"
   export QT_PLUGIN_PATH="${HERE}/usr/plugins"
   export LD_LIBRARY_PATH="${HERE}/usr/lib:${LD_LIBRARY_PATH}"
   export QT_QPA_PLATFORM_PLUGIN_PATH="${HERE}/usr/plugins/platforms"
   exec "${HERE}/usr/bin/MDviewer" "$@"
   EOF
   chmod +x MDviewer.AppDir/AppRun
   ```

### Step 7: Create AppImage
1. **Build the AppImage:**
   ```bash
   ./appimagetool-x86_64.AppImage MDviewer.AppDir MDviewer-x86_64.AppImage
   ```

2. **Verify the AppImage:**
   ```bash
   ./MDviewer-x86_64.AppImage --version
   ./MDviewer-x86_64.AppImage --help
   ```

### Step 8: Build Script Creation
Create `build_appimage.sh` that automates the entire process with error handling.

## Key Technical Considerations

### Icon Integration
- **Primary icon**: `resources/icons/app_256x256.png`
- **Fallback sizes**: Include 128x128 and 64x64 for desktop integration
- **Icon formats**: PNG format for Linux compatibility
- **Symlinks**: Create proper icon symlinks for theme integration

### PyQt6 Runtime Issues
- **Platform plugins**: Bundle `platforms/`, `xcbglintegrations/`, `imageformats/`
- **Environment variables**: Set `QT_PLUGIN_PATH`, `LD_LIBRARY_PATH` in AppRun
- **Display server**: Handle both Wayland and X11 compatibility
- **OpenGL**: Include necessary OpenGL libraries

### Dependency Management
- **Library extraction**: Only include necessary runtime libraries
- **Size optimization**: Exclude development files and debug symbols
- **UPX compression**: Apply where beneficial for size reduction
- **Conflict avoidance**: Use isolated environment to prevent library conflicts

### File Handling
- **Relative paths**: Ensure all paths are relative within AppImage
- **Temporary files**: Handle temp file creation properly
- **Configuration**: Store config in user home directory, not within AppImage
- **File associations**: Register for `.md` file type handling

## Files to Create/Modify

### New Files
1. `MDviewer_linux.spec` - Linux-specific PyInstaller configuration
2. `build_appimage.sh` - Main build automation script
3. `mdviewer.desktop` - Desktop entry file template
4. `AppRun` - AppImage executable wrapper
5. `appimage_build/` - Build directory structure

### Files to Update
- `AGENTS.md` - Add AppImage build instructions
- `README.md` - Document AppImage usage and installation

## Expected Output

### Deliverables
- **Primary**: `MDviewer-x86_64.AppImage` - Portable executable
- **Size estimate**: 80-120MB (depending on compression)
- **Compatibility**: Modern Linux distributions (Ubuntu 20.04+, Fedora 35+, etc.)

### Testing Strategy
1. **Functional testing**:
   - Application launches without errors
   - Markdown files render correctly
   - Theme switching works
   - File associations functional

2. **Platform testing**:
   - Ubuntu/Debian-based systems
   - Fedora/RHEL-based systems
   - Arch Linux and derivatives
   - Systems with different graphics drivers (NVIDIA, AMD, Intel)

3. **Integration testing**:
   - Desktop environment integration
   - File manager integration
   - Command-line argument handling
   - Update system functionality

## Troubleshooting Common Issues

### Runtime Errors
- **Qt plugin errors**: Check plugin paths and permissions
- **Library loading failures**: Verify LD_LIBRARY_PATH settings
- **Display issues**: Test both X11 and Wayland sessions

### Build Issues
- **Missing dependencies**: Ensure all system packages are installed
- **Path problems**: Use absolute paths in build scripts
- **Permission errors**: Check executable permissions on AppRun

### Size Optimization
- **Remove unnecessary files**: Exclude docs, examples, debug symbols
- **Compress libraries**: Use UPX where appropriate
- **Strip binaries**: Remove debug information from compiled libraries

## Integration with Existing Build System

### Preserving Windows Builds
- Keep `MDviewer.spec` unchanged for Windows builds
- Separate build scripts for different platforms
- Shared dependencies management through requirements.txt

### Build Automation
- Integrate AppImage build into CI/CD pipeline
- Separate build stages for different platforms
- Automated testing of generated AppImages

## Success Criteria
1. ✅ AppImage runs on multiple Linux distributions without additional dependencies
2. ✅ All MDviewer features work correctly in AppImage format
3. ✅ File associations and desktop integration function properly
4. ✅ AppImage size is reasonable (<150MB)
5. ✅ Build process is reproducible and documented
6. ✅ Existing Windows build process remains unaffected

## Next Steps
1. Create the Linux-specific PyInstaller spec file
2. Develop the build_appimage.sh script
3. Set up the AppDir structure and templates
4. Test the complete build process
5. Validate on multiple Linux distributions
6. Document final procedures and update project documentation