@echo off
setlocal enabledelayedexpansion

echo ============================================
echo  MDviewer Release Script
echo ============================================
echo.

REM Always build with the project venv, not whatever pyinstaller is on PATH.
REM Checked up front so a missing venv aborts before anything is pushed or tagged.
cd /d "%~dp0"
set "VENV_PY=%~dp0venv\Scripts\python.exe"
if not exist "%VENV_PY%" (
    echo ERROR: Project venv not found at venv\
    echo Create it with: python -m venv venv
    exit /b 1
)

REM --- Step 1: Read version from version.py ---
for /f "tokens=2 delims==" %%a in ('findstr /R "__version__ =" version.py') do (
    set "RAW=%%a"
)
REM Trim quotes and spaces
set "VERSION=%RAW: =%"
set "VERSION=%VERSION:"=%"
echo [1/7] Version detected: v%VERSION%
echo.

REM --- Step 2: Check for uncommitted changes ---
echo [2/7] Checking for uncommitted changes...
git diff --quiet 2>nul
if errorlevel 1 (
    echo WARNING: You have uncommitted changes!
    echo Commit or stash them before releasing.
    echo.
    git status --short
    echo.
    set /p CONTINUE="Continue anyway? (y/N): "
    if /i not "!CONTINUE!"=="y" (
        echo Aborted.
        exit /b 1
    )
)
echo       Working tree is clean.
echo.

REM --- Step 3: Push latest commits ---
echo [3/7] Pushing latest commits to GitHub...
git push origin main
echo.

REM --- Step 4: Build the executable ---
echo [4/7] Building executable with PyInstaller...
"%VENV_PY%" -m pip install -q -r requirements.txt pyinstaller
if errorlevel 1 (
    echo ERROR: Dependency install failed.
    exit /b 1
)
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist
"%VENV_PY%" -m PyInstaller --clean --noconfirm MDviewer.spec
if errorlevel 1 (
    echo ERROR: PyInstaller build failed.
    exit /b 1
)
if not exist dist\MDviewer.exe (
    echo ERROR: Build failed! dist\MDviewer.exe not found.
    exit /b 1
)
echo       Build successful.
echo.

REM --- Step 5: Create git tag ---
echo [5/7] Creating git tag v%VERSION%...
git tag -a v%VERSION% -m "Release v%VERSION%"
if errorlevel 1 (
    echo WARNING: Tag v%VERSION% may already exist.
    set /p OVERWRITE="Delete and recreate tag? (y/N): "
    if /i "!OVERWRITE!"=="y" (
        git tag -d v%VERSION%
        git push origin :refs/tags/v%VERSION%
        git tag -a v%VERSION% -m "Release v%VERSION%"
    ) else (
        echo Continuing with existing tag...
    )
)
git push origin v%VERSION%
echo.

REM --- Step 6: Extract changelog and create GitHub Release ---
echo [6/7] Creating GitHub Release with binary...

REM Extract changelog section for this version into a temp file.
REM PowerShell copies lines verbatim (cmd's echo mangles !, |, <, > and drops blank lines).
powershell -NoProfile -Command "$h = '## MDviewer [%VERSION%]'; $in = $false; $out = foreach ($l in Get-Content -Encoding UTF8 '%~dp0CHANGELOG.md') { if ($l -match '^## MDviewer \[') { $in = $l.StartsWith($h) } elseif ($in -and $l -ne '---') { $l } }; [IO.File]::WriteAllLines('%~dp0release_notes_temp.md', [string[]]$out)"

REM Create the release
gh release create v%VERSION% ^
    --title "MDviewer v%VERSION%" ^
    --notes-file release_notes_temp.md ^
    dist\MDviewer.exe

del release_notes_temp.md 2>nul
echo.

REM --- Step 7: Deploy to local bin ---
echo [7/7] Deploying to ~\bin\MDviewer.exe...
copy /y dist\MDviewer.exe "%USERPROFILE%\bin\MDviewer.exe"
echo.

echo ============================================
echo  Release v%VERSION% complete!
echo ============================================
echo.
echo  Tag:     v%VERSION%
echo  Release: https://github.com/juren53/MDviewer/releases/tag/v%VERSION%
echo  Binary:  %USERPROFILE%\bin\MDviewer.exe
echo.
pause
