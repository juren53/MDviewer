@echo off
echo Building MDviewer executable...
echo.

REM Clean previous builds
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist

REM Build executable
pyinstaller --clean MDviewer.spec

echo.
echo Build complete! 
echo Executable location: dist\MDviewer.exe
echo File size: 
dir dist\MDviewer.exe | findstr MDviewer.exe
pause