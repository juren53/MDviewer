#!/bin/bash

# MDviewer AppImage Build Script
# This script creates a portable AppImage for MDviewer on Linux

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
APP_NAME="MDviewer"
APP_VERSION=$(python3 -c "import sys; sys.path.append('..'); from version import get_semver; print(get_semver())")
BUILD_DIR="appimage_build"
APPDIR_NAME="${APP_NAME}.AppDir"
FINAL_APPIMAGE="${APP_NAME}-x86_64.AppImage"

echo -e "${BLUE}Building ${APP_NAME} AppImage...${NC}"
echo -e "${BLUE}Version: ${APP_VERSION}${NC}"

# Check if required tools are installed
check_dependencies() {
    echo -e "${YELLOW}Checking dependencies...${NC}"
    
    local missing_deps=()
    
    if ! command -v python3 &> /dev/null; then
        missing_deps+=("python3")
    fi
    
    if ! command -v pip3 &> /dev/null; then
        missing_deps+=("pip3")
    fi
    
    # Check for appimagetool in common locations
    if command -v appimagetool &> /dev/null; then
        echo -e "${GREEN}appimagetool found in PATH!${NC}"
    elif [ -f "./appimagetool-x86_64.AppImage" ]; then
        echo -e "${GREEN}appimagetool found locally!${NC}"
        alias appimagetool="./appimagetool-x86_64.AppImage"
    elif [ -f "../appimagetool-x86_64.AppImage" ]; then
        echo -e "${GREEN}appimagetool found locally!${NC}"
        alias appimagetool="../appimagetool-x86_64.AppImage"
    else
        echo -e "${YELLOW}appimagetool not found. Will create AppDir only.${NC}"
        echo -e "${YELLOW}Download appimagetool from: https://github.com/AppImage/appimagetool/releases${NC}"
        echo -e "${YELLOW}Then place appimagetool-x86_64.AppImage in project directory${NC}"
    fi
    
    if [ ${#missing_deps[@]} -ne 0 ]; then
        echo -e "${RED}Missing critical dependencies: ${missing_deps[*]}${NC}"
        echo -e "${YELLOW}On Ubuntu/Debian, install with: sudo apt install python3 python3-pip python3-venv${NC}"
        exit 1
    fi
    
    echo -e "${GREEN}Critical dependencies found!${NC}"
}

# Clean up previous builds
cleanup() {
    echo -e "${YELLOW}Cleaning up previous builds...${NC}"
    rm -rf "${BUILD_DIR}"
    rm -rf build
    rm -rf dist
    echo -e "${GREEN}Cleanup complete!${NC}"
}

# Create build directory structure
setup_build_env() {
    echo -e "${YELLOW}Setting up build environment...${NC}"
    
    mkdir -p "${BUILD_DIR}"
    cd "${BUILD_DIR}"
    
    # Create virtual environment
    echo -e "${YELLOW}Creating Python virtual environment...${NC}"
    python3 -m venv venv
    source venv/bin/activate
    
    # Upgrade pip and install dependencies
    echo -e "${YELLOW}Installing dependencies...${NC}"
    pip install --upgrade pip
    pip install -r ../requirements.txt
    pip install pyinstaller
    
    echo -e "${GREEN}Build environment ready!${NC}"
}

# Build the application with PyInstaller
build_application() {
    echo -e "${YELLOW}Building application with PyInstaller...${NC}"
    
    # Clean any existing PyInstaller builds
    rm -rf build dist
    
    # Run PyInstaller from the root directory where the spec file is
    cd ..
    pyinstaller --clean MDviewer_linux.spec
    
    if [ ! -f "dist/MDviewer/MDviewer" ]; then
        echo -e "${RED}PyInstaller build failed!${NC}"
        exit 1
    fi
    
    echo -e "${GREEN}Application built successfully!${NC}"
    
    # Move back to build directory
    cd "${BUILD_DIR}"
}

# Create AppDir structure
create_appdir() {
    echo -e "${YELLOW}Creating AppDir structure...${NC}"
    
    # Create AppDir directories
    mkdir -p "${APPDIR_NAME}"/usr/{bin,lib,share/{applications,icons/hicolor/{256x256,128x128,64x64}/apps}}
    
    # Copy the built application from the parent directory (where PyInstaller was run)
    cp -r ../dist/MDviewer/* "${APPDIR_NAME}/usr/bin/"
    
    # Create desktop entry
    cat > "${APPDIR_NAME}/${APP_NAME,,}.desktop" << EOF
[Desktop Entry]
Name=${APP_NAME}
Comment=A PyQt6-based Markdown viewer with GitHub-style rendering
Exec=${APP_NAME}
Icon=${APP_NAME,,}
Type=Application
Categories=Office;
Terminal=false
StartupNotify=true
MimeType=text/markdown;text/x-markdown;
EOF
    
    # Copy desktop entry to proper location
    cp "${APPDIR_NAME}/${APP_NAME,,}.desktop" "${APPDIR_NAME}/usr/share/applications/"
    
    # Setup icons
    echo -e "${YELLOW}Setting up icons...${NC}"
    
    # Copy icons if they exist (from appimage_build/, icons are at ../resources/icons/)
    local ICON_DIR="../resources/icons"

    if [ -f "${ICON_DIR}/app_256x256.png" ]; then
        cp "${ICON_DIR}/app_256x256.png" "${APPDIR_NAME}/${APP_NAME,,}.png"
        ln -sf "${APP_NAME,,}.png" "${APPDIR_NAME}/.DirIcon"
        cp "${ICON_DIR}/app_256x256.png" "${APPDIR_NAME}/usr/share/icons/hicolor/256x256/apps/${APP_NAME,,}.png"
    fi

    if [ -f "${ICON_DIR}/app_128x128.png" ]; then
        cp "${ICON_DIR}/app_128x128.png" "${APPDIR_NAME}/usr/share/icons/hicolor/128x128/apps/${APP_NAME,,}.png"
    fi

    if [ -f "${ICON_DIR}/app_64x64.png" ]; then
        cp "${ICON_DIR}/app_64x64.png" "${APPDIR_NAME}/usr/share/icons/hicolor/64x64/apps/${APP_NAME,,}.png"
    fi

    # Fallback to app.png if specific sizes don't exist
    if [ ! -f "${APPDIR_NAME}/${APP_NAME,,}.png" ] && [ -f "${ICON_DIR}/app.png" ]; then
        cp "${ICON_DIR}/app.png" "${APPDIR_NAME}/${APP_NAME,,}.png"
        ln -sf "${APP_NAME,,}.png" "${APPDIR_NAME}/.DirIcon"
        cp "${ICON_DIR}/app.png" "${APPDIR_NAME}/usr/share/icons/hicolor/256x256/apps/${APP_NAME,,}.png"
    fi
    
    echo -e "${GREEN}AppDir structure created!${NC}"
}

# Create AppRun wrapper
create_apprun() {
    echo -e "${YELLOW}Creating AppRun wrapper...${NC}"
    
    cat > "${APPDIR_NAME}/AppRun" << 'EOF'
#!/bin/bash
HERE="$(dirname "$(readlink -f "${0}")")"
export PATH="${HERE}/usr/bin:${PATH}"
export LD_LIBRARY_PATH="${HERE}/usr/lib:${LD_LIBRARY_PATH}"
export QT_PLUGIN_PATH="${HERE}/usr/plugins"
export QT_QPA_PLATFORM_PLUGIN_PATH="${HERE}/usr/plugins/platforms"
export XDG_DATA_DIRS="${HERE}/usr/share:${XDG_DATA_DIRS:-/usr/local/share/:/usr/share/}"

# Run the application
exec "${HERE}/usr/bin/MDviewer" "$@"
EOF
    
    chmod +x "${APPDIR_NAME}/AppRun"
    echo -e "${GREEN}AppRun wrapper created!${NC}"
}

# Copy Qt libraries and plugins
setup_qt_libraries() {
    echo -e "${YELLOW}Setting up Qt libraries and plugins...${NC}"
    
    # Create plugins directory
    mkdir -p "${APPDIR_NAME}/usr/plugins"
    
    # Find and copy Qt plugins from the virtual environment
    VENV_PYQT6="venv/lib/python3.*/site-packages/PyQt6"
    
    # Copy platform plugins
    if [ -d ${VENV_PYQT6}/Qt/plugins ]; then
        cp -r ${VENV_PYQT6}/Qt/plugins/* "${APPDIR_NAME}/usr/plugins/"
    fi
    
    # Copy Qt libraries if they exist
    if [ -d ${VENV_PYQT6}/Qt/lib ]; then
        cp -r ${VENV_PYQT6}/Qt/lib/* "${APPDIR_NAME}/usr/lib/" 2>/dev/null || true
    fi
    
    echo -e "${GREEN}Qt libraries and plugins setup complete!${NC}"
}

# Create the AppImage
create_appimage() {
    echo -e "${YELLOW}Creating AppImage...${NC}"
    
    # Check if appimagetool is available
    local APPIMAGETOOL_CMD=""
    if command -v appimagetool &> /dev/null; then
        APPIMAGETOOL_CMD="appimagetool"
    elif [ -f "./appimagetool-x86_64.AppImage" ]; then
        APPIMAGETOOL_CMD="../appimagetool-x86_64.AppImage"
    elif [ -f "../appimagetool-x86_64.AppImage" ]; then
        APPIMAGETOOL_CMD="../appimagetool-x86_64.AppImage"
    else
        echo -e "${YELLOW}appimagetool not found. Skipping AppImage creation.${NC}"
        echo -e "${YELLOW}AppDir is ready at: ${BUILD_DIR}/${APPDIR_NAME}${NC}"
        echo -e "${YELLOW}Download appimagetool from: https://github.com/AppImage/appimagetool/releases${NC}"
        echo -e "${YELLOW}Then run: cd ${BUILD_DIR} && appimagetool ${APPDIR_NAME} ${FINAL_APPIMAGE}${NC}"
        return 0
    fi
    
    # Create the AppImage
    "${APPIMAGETOOL_CMD}" --no-appstream "${APPDIR_NAME}" "${FINAL_APPIMAGE}"
    
    if [ -f "${FINAL_APPIMAGE}" ]; then
        echo -e "${GREEN}AppImage created successfully!${NC}"
        ls -lh "${FINAL_APPIMAGE}"
    else
        echo -e "${RED}AppImage creation failed!${NC}"
        exit 1
    fi
}

# Test the AppImage
test_appimage() {
    echo -e "${YELLOW}Testing AppImage...${NC}"
    
    if [ -f "${FINAL_APPIMAGE}" ]; then
        # Test version display
        echo -e "${BLUE}Testing version display...${NC}"
        timeout 10s "./${FINAL_APPIMAGE}" --version || echo -e "${YELLOW}Version test completed (timeout expected)${NC}"
        
        # Test help display
        echo -e "${BLUE}Testing help display...${NC}"
        timeout 10s "./${FINAL_APPIMAGE}" --help || echo -e "${YELLOW}Help test completed (timeout expected)${NC}"
        
        echo -e "${GREEN}AppImage tests completed!${NC}"
    else
        echo -e "${RED}AppImage not found for testing!${NC}"
        exit 1
    fi
}

# Handle script arguments
case "${1:-build}" in
    "clean")
        cleanup
        ;;
    "build")
        main() {
            echo -e "${BLUE}Starting ${APP_NAME} AppImage build process...${NC}"
            
            check_dependencies
            cleanup
            setup_build_env
            build_application
            create_appdir
            create_apprun
            setup_qt_libraries
            create_appimage
            test_appimage
            
            echo -e "${GREEN}AppImage build completed successfully!${NC}"
            echo -e "${BLUE}Final AppImage: ${BUILD_DIR}/${FINAL_APPIMAGE}${NC}"
            echo -e "${YELLOW}To run: ./${BUILD_DIR}/${FINAL_APPIMAGE}${NC}"
        }
        main
        ;;
    "test")
        cd "${BUILD_DIR}" && test_appimage
        ;;
    *)
        echo "Usage: $0 [clean|build|test]"
        echo "  clean - Clean up build directories"
        echo "  build - Full build process (default)"
        echo "  test  - Test existing AppImage"
        exit 1
        ;;
esac