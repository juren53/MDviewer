# MDviewer Crash Analysis: GTK PNG Loading Failure on LMDE

**Date:** 2026-02-27
**Platform:** Linux Mint Debian Edition (LMDE) / Cinnamon desktop
**App:** MDviewer v0.3.0 (PyQt6)
**Status:** Root cause identified and fixed

---

## Symptom

Running `./run.sh` produces:

```
(python:116661): Gtk-WARNING **: 09:14:21.896: Could not load a pixbuf from icon theme.
This may indicate that pixbuf loaders or the mime database could not be found.
**
Gtk:ERROR:../../../gtk/gtkiconhelper.c:495:ensure_surface_for_gicon: assertion failed (error == NULL):
  Failed to load /usr/share/icons/Mint-Y/legacy/16/image-missing.png:
  Unrecognized image file format (gdk-pixbuf-error-quark, 3)
Bail out! Gtk:ERROR:...
./run.sh: line 88: 116661 Aborted (core dumped) python "$ENTRY_POINT" "$@"
```

The application aborts immediately on startup with a fatal GTK error.

---

## Why a PyQt6 App Gets a GTK Error

MDviewer is a **PyQt6** application — it uses Qt, not GTK. So why does a GTK error crash it?

On LMDE/Cinnamon, Qt6 ships a GTK3 platform theme plugin:

```
/usr/lib/x86_64-linux-gnu/qt6/plugins/platformthemes/libqgtk3.so
```

When Qt6 cannot identify a valid Qt-native platform theme (the global `QT_QPA_PLATFORMTHEME=qt5ct` setting is for Qt5 and is ignored by Qt6), Qt6 auto-detects the GNOME/Cinnamon desktop and loads the GTK3 platform theme. This causes GTK libraries to be initialized inside the Qt6 process in order to:

- Match the system GTK theme and font settings
- Use GTK's native file dialogs
- Resolve GTK icon names for toolbar/menu icons

When GTK initializes, it needs to load pixbuf icons from the current icon theme (Mint-Y). If that fails, GTK attempts to display a `image-missing.png` fallback icon. If that *also* fails, GTK calls `g_error()` — a fatal, unrecoverable assertion — which aborts the process.

---

## Root Cause Chain

The failure propagates through four layers:

```
XDG_DATA_DIRS is empty
        │
        ▼
GIO cannot find /usr/share/mime → all MIME detection returns "application/octet-stream"
        │
        ▼
gdk-pixbuf cannot identify any image format (PNG, BMP, GIF, etc.)
        │
        ▼
GTK cannot load icon theme → cannot load image-missing.png fallback
        │
        ▼
GTK calls g_error() → process aborts
```

### Layer 1: `XDG_DATA_DIRS` Is Empty

The `XDG_DATA_DIRS` environment variable was **set to an empty string** in the shell session:

```bash
$ env | grep XDG_DATA_DIRS
XDG_DATA_DIRS=
```

According to the [XDG Base Directory Specification](https://specifications.freedesktop.org/basedir-spec/latest/), if `XDG_DATA_DIRS` is unset the default is `/usr/local/share:/usr/share`. However, when the variable is explicitly *set to empty*, GLib/GIO does **not** fall back to the default — it treats the empty string as a valid (empty) search path.

### Layer 2: GIO MIME Detection Fails

GIO uses `XDG_DATA_DIRS` to locate the shared MIME database. With an empty list it only checks:

```
~/.local/share/mime/
```

That directory does not exist on this system. The system MIME database at `/usr/share/mime/mime.cache` — which correctly contains entries for `image/png`, `image/jpeg`, etc. — is **never consulted**.

This was confirmed with `strace`:

```
openat(AT_FDCWD, "/home/juren/.local/share/mime//mime.cache", ...) = -1 ENOENT
openat(AT_FDCWD, "/home/juren/.local/share/mime//globs",      ...) = -1 ENOENT
openat(AT_FDCWD, "/home/juren/.local/share/mime//magic",      ...) = -1 ENOENT
# /usr/share/mime/ is never opened
```

And confirmed programmatically:

```python
# XDG_DATA_DIRS=""  (empty)
gio.g_content_type_guess(b'test.png', None, 0, ...)
# → b'application/octet-stream'  (WRONG)

# XDG_DATA_DIRS="/usr/local/share:/usr/share"
gio.g_content_type_guess(b'test.png', None, 0, ...)
# → b'image/png'  (CORRECT)
```

### Layer 3: gdk-pixbuf Cannot Identify Any Format

`gdk_pixbuf_new_from_file()` uses GIO internally to determine a file's MIME type before selecting the appropriate image loader. Since GIO returns `application/octet-stream` for every file, no loader is matched and every load attempt fails with:

```
Couldn't recognize the image file format for file "..."
```

This affects **all** formats — PNG, BMP, GIF, JPEG, etc. — not just PNG.

Key observations:
- The PNG file itself is valid (`file` command confirms `PNG image data, 16x16, 8-bit/color RGBA`)
- The gdk-pixbuf library (`libgdk_pixbuf-2.0.so.0.4200.10`) correctly links against `libpng16.so.16`
- `gdk_pixbuf_get_formats()` returns 16 formats including `png` and `jpeg` (built-in loaders)
- The loaders.cache at `/usr/lib/x86_64-linux-gnu/gdk-pixbuf-2.0/2.10.0/loaders.cache` is valid and up to date
- All loader `.so` files exist in the loaders directory
- Despite all of the above, format detection always fails when `XDG_DATA_DIRS` is empty

### Layer 4: GTK Fatal Abort

GTK handles icon load failures by showing a `image-missing.png` placeholder — but that PNG also fails to load (same root cause). When the fallback image itself cannot be loaded, GTK calls:

```c
// gtk/gtkiconhelper.c:495
g_error("Failed to load %s: %s", path, error->message);
```

`g_error()` is unconditional and terminates the process immediately.

---

## Why `XDG_DATA_DIRS` Is Empty

### The Guix Installation

`~/.bashrc` contains a Guix package manager setup block (lines 266–289):

```bash
# Guix environment setup - Fixed to prevent XDG_DATA_DIRS duplication
if [ -f /etc/profile.d/guix.sh ]; then
    . /etc/profile.d/guix.sh

    # Remove duplicate entries from XDG_DATA_DIRS
    if [ -n "$XDG_DATA_DIRS" ]; then
        IFS=':' read -ra DIRS <<< "$XDG_DATA_DIRS"
        declare -A seen
        new_dirs=""
        for dir in "${DIRS[@]}"; do
            if [ -n "$dir" ] && [ -z "${seen[$dir]}" ]; then
                seen[$dir]=1
                new_dirs="${new_dirs:+$new_dirs:}$dir"
            fi
        done
        export XDG_DATA_DIRS="$new_dirs"
    fi
fi
```

`/etc/profile.d/guix.sh` appends Guix paths to `XDG_DATA_DIRS`:

```bash
export XDG_DATA_DIRS="$GUIX_PROFILE/share:${XDG_DATA_DIRS:-/usr/local/share/:/usr/share/}"
```

The `:-` operator handles both unset and empty, so `guix.sh` itself produces a correct, non-empty value.

### The Session Startup Gap

The Cinnamon session startup script `/etc/X11/Xsession.d/55cinnamon-session_gnomerc` sets `XDG_DATA_DIRS` during the X11 session:

```bash
if [ -z "$XDG_DATA_DIRS" ]; then
    XDG_DATA_DIRS=/usr/share/gnome:/usr/local/share/:/usr/share/
else
    XDG_DATA_DIRS=/usr/share/gnome:"$XDG_DATA_DIRS"
fi
export XDG_DATA_DIRS
```

However, `env` output at runtime shows `XDG_DATA_DIRS=` — explicitly **set but empty**. This means the session startup scripts ran with an initially-empty `XDG_DATA_DIRS` and the `else` branch produced `XDG_DATA_DIRS=/usr/share/gnome:` (a trailing colon with an empty second element). Subsequent processing or deduplication then collapsed this to an empty string.

The deduplication code in `.bashrc`, while logically correct, does not *add* `/usr/share` if it is missing — it only deduplicates what is already there. If `XDG_DATA_DIRS` arrives empty (or effectively empty after the session startup edge case), the deduplication block's guard `[ -n "$XDG_DATA_DIRS" ]` may prevent it from running at all, leaving `XDG_DATA_DIRS` empty.

Note: `~/.bashrc` line 297 already contains a manual workaround for related gdk-pixbuf issues:
```bash
export GDK_PIXBUF_MODULE_FILE=/usr/lib/x86_64-linux-gnu/gdk-pixbuf-2.0/2.10.0/loaders.cache
```
This reflects a pre-existing, known instability in the `XDG_DATA_DIRS`/GIO/gdk-pixbuf chain.

---

## System Environment (for reference)

| Component | Version |
|-----------|---------|
| OS | LMDE (Debian Bookworm base) |
| Desktop | Cinnamon / X11 |
| gdk-pixbuf | `2.42.10+dfsg-1+deb12u3` |
| shared-mime-info | `2.2-1` |
| MIME cache updated | 2026-02-25 |
| Qt | PyQt6 ≥ 6.5 |
| Qt GTK3 theme | `/usr/lib/x86_64-linux-gnu/qt6/plugins/platformthemes/libqgtk3.so` |

### Installed gdk-pixbuf packages

```
ii  libgdk-pixbuf-2.0-0       2.42.10+dfsg-1+deb12u3   (actual library)
ii  libgdk-pixbuf2.0-0        2.40.2-2                  (transitional)
ii  libgdk-pixbuf-xlib-2.0-0  2.40.2-2
ii  libgdk-pixbuf2.0-bin      2.42.10+dfsg-1+deb12u3
ii  libgdk-pixbuf2.0-common   2.42.10+dfsg-1+deb12u3
```

### Loader status (gdk-pixbuf 2.42)

PNG and JPEG are **built-in** loaders in gdk-pixbuf 2.42 — they are compiled directly into `libgdk_pixbuf-2.0.so` and do not have separate `.so` files in the loaders directory. This is expected and correct. The loaders directory contains 14 external loaders (ANI, BMP, GIF, HEIF, ICNS, ICO, PNM, QTIF, SVG, TGA, TIFF, WebP, XBM, XPM).

The failure is **not** a missing loader issue — it is a MIME detection issue caused by the empty `XDG_DATA_DIRS`.

---

## The Fix

### Applied: `run.sh` defensive guard (immediate fix)

Added to `run.sh` immediately before the `python "$ENTRY_POINT"` launch line:

```bash
# Ensure XDG_DATA_DIRS includes system paths required for GIO MIME detection.
# Without /usr/share, gdk-pixbuf cannot identify image formats and GTK crashes.
if [ -z "$XDG_DATA_DIRS" ]; then
    export XDG_DATA_DIRS="/usr/local/share:/usr/share"
fi
```

The condition `[ -z "$XDG_DATA_DIRS" ]` is true for both **unset** and **set-to-empty** cases, which covers the observed failure mode. This does not override a correctly-populated `XDG_DATA_DIRS` from a healthy session.

### Verification

Confirmed in isolation that setting `XDG_DATA_DIRS=/usr/local/share:/usr/share` fully resolves:

```python
# Before fix
g_content_type_guess("test.png") → "application/octet-stream"  (wrong)
gdk_pixbuf_new_from_file("image-missing.png") → NULL (fails)

# After fix
g_content_type_guess("test.png") → "image/png"  (correct)
gdk_pixbuf_new_from_file("image-missing.png") → valid pixbuf (success)
```

---

## Recommended Follow-up (System-Level)

The `run.sh` fix is a defensive workaround scoped to MDviewer. The underlying `XDG_DATA_DIRS` problem affects the entire session and will cause the same failures in any GTK application launched from a shell where `XDG_DATA_DIRS` is empty.

### Option A: Fix `.bashrc` Guix block

Ensure the Guix deduplication block *always* includes standard system paths, even if they were not present before it ran:

```bash
if [ -f /etc/profile.d/guix.sh ]; then
    . /etc/profile.d/guix.sh

    # Guarantee system paths are always present
    for sys_dir in /usr/local/share /usr/share; do
        case ":$XDG_DATA_DIRS:" in
            *":$sys_dir:"*) ;;  # already present
            *) export XDG_DATA_DIRS="${XDG_DATA_DIRS:+$XDG_DATA_DIRS:}$sys_dir" ;;
        esac
    done
fi
```

### Option B: Set `XDG_DATA_DIRS` in `~/.profile` or `~/.xprofile`

Add an unconditional baseline before any session overrides:

```bash
# ~/.xprofile  (sourced by LightDM before the Cinnamon session)
export XDG_DATA_DIRS="${XDG_DATA_DIRS:-/usr/local/share:/usr/share}"
```

### Option C: Use `qt6ct` for Qt6 theming

Install `qt6ct` and set `QT_QPA_PLATFORMTHEME=qt6ct` to give Qt6 a non-GTK platform theme. This avoids loading GTK entirely for Qt6 apps, eliminating the dependency on gdk-pixbuf at Qt startup (though GTK apps themselves would still be affected):

```bash
sudo apt install qt6ct
# Then configure: QT_QPA_PLATFORMTHEME=qt6ct in ~/.profile
```

---

## Diagnostic Commands Used

```bash
# Confirm XDG_DATA_DIRS state
env | grep XDG_DATA_DIRS
if [ -z "${XDG_DATA_DIRS+x}" ]; then echo UNSET; elif [ -z "$XDG_DATA_DIRS" ]; then echo EMPTY; else echo "$XDG_DATA_DIRS"; fi

# List gdk-pixbuf loaders
ls /usr/lib/x86_64-linux-gnu/gdk-pixbuf-2.0/2.10.0/loaders/

# Check loaders.cache for PNG entry
grep -i png /usr/lib/x86_64-linux-gnu/gdk-pixbuf-2.0/2.10.0/loaders.cache

# Confirm the problematic PNG file is valid
file /usr/share/icons/Mint-Y/legacy/16/image-missing.png

# Test GIO MIME detection with/without XDG_DATA_DIRS
python3 -c "
import ctypes, os
os.environ['XDG_DATA_DIRS'] = '/usr/local/share:/usr/share'
gobject = ctypes.CDLL('/usr/lib/x86_64-linux-gnu/libgobject-2.0.so.0')
gobject.g_type_init()
gio = ctypes.CDLL('/lib/x86_64-linux-gnu/libgio-2.0.so.0')
gio.g_content_type_guess.restype = ctypes.c_char_p
gio.g_content_type_guess.argtypes = [ctypes.c_char_p, ctypes.c_char_p, ctypes.c_size_t, ctypes.POINTER(ctypes.c_int)]
uncertain = ctypes.c_int()
print(gio.g_content_type_guess(b'test.png', None, 0, ctypes.byref(uncertain)))
"

# Find Qt6 platform theme plugins
find /usr/lib -path '*/qt6/platformthemes/*.so'

# Trace MIME database access
strace -e trace=openat python3 -c "..." 2>&1 | grep mime
```

---

## Summary

| | |
|---|---|
| **Symptom** | App aborts with GTK fatal error on startup |
| **Error** | `Unrecognized image file format` for `image-missing.png` |
| **Why GTK?** | Qt6's GTK3 platform theme loads GTK inside the PyQt6 process |
| **Root cause** | `XDG_DATA_DIRS` is empty → GIO can't find `/usr/share/mime/` → MIME detection broken → gdk-pixbuf can't identify any image format |
| **Origin of empty XDG_DATA_DIRS** | Interaction between session startup edge case and Guix `.bashrc` deduplication |
| **Fix applied** | Guard in `run.sh` sets `XDG_DATA_DIRS=/usr/local/share:/usr/share` when empty |
| **Scope of fix** | MDviewer only; system-level `XDG_DATA_DIRS` issue persists for other apps |
