@echo off
echo Building MDviewer executable...
echo.

REM Always build with the project venv, not whatever pyinstaller is on PATH
cd /d "%~dp0"
set "VENV_PY=%~dp0venv\Scripts\python.exe"
if not exist "%VENV_PY%" (
    echo ERROR: Project venv not found at venv\
    echo Create it with: python -m venv venv
    pause
    exit /b 1
)

REM Ensure dependencies and PyInstaller are installed in the venv
"%VENV_PY%" -m pip install -q -r requirements.txt pyinstaller
if errorlevel 1 (
    echo ERROR: Dependency install failed.
    pause
    exit /b 1
)

REM Clean previous builds
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist

REM Build executable
"%VENV_PY%" -m PyInstaller --clean --noconfirm MDviewer.spec
if errorlevel 1 (
    echo.
    echo ERROR: Build failed.
    pause
    exit /b 1
)

echo.
echo Build complete!
echo Executable location: dist\MDviewer.exe
echo File size:
dir dist\MDviewer.exe | findstr MDviewer.exe
pause
