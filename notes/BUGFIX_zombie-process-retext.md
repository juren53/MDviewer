# Bug: Zombie Process from External Editor Launch

**Date:** 2026-03-25
**File:** `viewer/external_editor.py`
**Function:** `_launch_editor()` (line 233)

---

## Symptom

`top` reported one zombie process. Inspection via `ps aux` revealed:

```
juren  1400601  0.0  0.0  0  0  ?  Z  Mar24  0:03  [retext] <defunct>
```

The process had been sitting as a zombie since the previous day.

## Root Cause

`_launch_editor()` spawns the external editor using `subprocess.Popen()` but immediately discards the returned process object:

```python
def _launch_editor(editor_cmd, file_path):
    try:
        if editor_cmd in _TERMINAL_EDITORS and platform.system() != "Windows":
            subprocess.Popen([term, "-e", editor_cmd, file_path])
        else:
            subprocess.Popen([editor_cmd, file_path])   # ← object discarded
        return True, None
```

When a child process exits, the kernel retains its entry in the process table until the parent calls `wait()` to collect the exit status. Because the `Popen` object was discarded, Python never called `wait()`, and the kernel kept `retext` as a zombie indefinitely.

The full process chain at the time of discovery was:

```
run.sh  (PID 763354)
  └── python main.py  (PID 763363)   ← parent that never reaped the child
        └── [retext] <defunct>  (PID 1400601)   ← zombie
```

## Fix

Since external editors are meant to run independently (fire-and-forget), the correct fix is to pass `start_new_session=True` to `Popen`. This detaches the child into its own process group, making the OS responsible for reaping it when it exits — no `wait()` needed.

```python
def _launch_editor(editor_cmd, file_path):
    try:
        if editor_cmd in _TERMINAL_EDITORS and platform.system() != "Windows":
            term = _find_terminal_emulator()
            if not term:
                return False, "No terminal emulator found to run terminal-based editor."
            subprocess.Popen([term, "-e", editor_cmd, file_path], start_new_session=True)
        else:
            subprocess.Popen([editor_cmd, file_path], start_new_session=True)
        return True, None
    except Exception as e:
        return False, str(e)
```

## Why `start_new_session=True` and not `.wait()`

Calling `.wait()` would block the MDviewer UI until the editor closes — unacceptable for a GUI app. `start_new_session=True` (which calls `setsid()` under the hood on Linux) fully detaches the editor child from MDviewer's process group, so:

- The editor runs independently with no parent dependency.
- MDviewer does not block.
- No zombie is left when the editor exits.
