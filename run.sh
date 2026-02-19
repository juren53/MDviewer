#!/bin/bash
# MDviewer launcher — creates/activates venv and installs dependencies if needed

set -e

VENV_DIR="venv"
REQUIREMENTS="requirements.txt"
ENTRY_POINT="main.py"

# Resolve project directory (where this script lives)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Check if an existing venv's base Python is still present.
# Reads pyvenv.cfg directly — never runs the (potentially broken) venv Python.
test_venv_valid() {
    local venv_path="$1"
    local cfg="$venv_path/pyvenv.cfg"
    [ -f "$cfg" ] || return 1

    local home_line
    home_line=$(grep -E "^home\s*=" "$cfg" 2>/dev/null) || return 1
    local python_home
    python_home=$(echo "$home_line" | sed 's/^home\s*=\s*//')

    [ -x "$python_home/python3" ] || [ -x "$python_home/python" ]
}

# Find a working system Python, bypassing any currently activated (possibly broken) venv.
find_python() {
    if command -v python3 &>/dev/null; then
        python3 --version &>/dev/null && echo "python3" && return
    fi
    if command -v python &>/dev/null; then
        python --version &>/dev/null && echo "python" && return
    fi
    for candidate in \
        /usr/bin/python3 \
        /usr/local/bin/python3 \
        "$HOME/.pyenv/shims/python3"; do
        if [ -x "$candidate" ]; then
            "$candidate" --version &>/dev/null && echo "$candidate" && return
        fi
    done
    return 1
}

# Wipe venv if it exists but points to a missing Python
if [ -d "$VENV_DIR" ] && ! test_venv_valid "$VENV_DIR"; then
    echo "Existing venv has a broken Python reference, recreating..."
    rm -rf "$VENV_DIR"
fi

# Create venv if it doesn't exist
if [ ! -d "$VENV_DIR" ]; then
    echo "Creating virtual environment..."
    PYTHON_EXE=$(find_python) || {
        echo "Error: no working Python found. Install Python 3 from https://python.org" >&2
        exit 1
    }
    "$PYTHON_EXE" -m venv "$VENV_DIR" || {
        echo "Error: Failed to create venv. You may need to install python3-venv:" >&2
        echo "  sudo apt install python3-venv" >&2
        exit 1
    }
fi

# Activate venv (works on Linux/macOS and Git Bash on Windows)
if [ -f "$VENV_DIR/bin/activate" ]; then
    source "$VENV_DIR/bin/activate"
elif [ -f "$VENV_DIR/Scripts/activate" ]; then
    source "$VENV_DIR/Scripts/activate"
else
    echo "Error: cannot find venv activate script" >&2
    exit 1
fi

# Install/update dependencies if requirements.txt is newer than the marker
MARKER="$VENV_DIR/.deps_installed"
if [ ! -f "$MARKER" ] || [ "$REQUIREMENTS" -nt "$MARKER" ]; then
    echo "Installing dependencies..."
    pip install --upgrade pip -q
    pip install -r "$REQUIREMENTS" -q
    touch "$MARKER"
fi

# Launch the application, passing through any command-line arguments
python "$ENTRY_POINT" "$@"
