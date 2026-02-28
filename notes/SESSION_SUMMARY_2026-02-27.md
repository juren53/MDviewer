# Git Divergence Resolution — 2026-02-27

## What Happened

After the v0.3.0 release was committed and pushed from Windows, two additional
commits were made on the Linux machine (fixing a startup crash and a `.desktop`
launch bug, tagged v0.3.1). Meanwhile, one more commit was made on Windows (adding
the PDF plan notes file). Neither machine had the other's commit, so the two
branches **diverged** from the common ancestor `e1acece`.

```
e1acece  ← shared base (Add PDF viewing support v0.3.0)
   |
   ├── Windows: 3271784  added Plan for adding PDF viewing MDviewer
   │
   └── Remote:  1355540  Fix startup crash caused by empty XDG_DATA_DIRS (v0.3.1)
                ecedd06  Fix system menu launch: use run.sh instead of python3 directly
```

## Diagnosis

```bash
git status
# "Your branch and 'origin/main' have diverged,
#  and have 1 and 2 different commits each, respectively."

git fetch origin
git log --oneline origin/main -5   # see what remote has
git log --oneline -5               # see what local has
```

This confirmed:
- **Local only:** `3271784` — adds `notes/PLAN_MDv-adding-PDF-viewing.md` (a notes file, no code)
- **Remote only:** `1355540` and `ecedd06` — two Linux bug-fix commits touching `run.sh`,
  `CHANGELOG.md`, `version.py`, and `MDviewer.desktop.template`

## Why Rebase Instead of Merge

A `git pull` (merge) would have created a merge commit, adding noise to the history
for a trivial notes file. Since the local commit only added a documentation file
with no overlap with the remote bug-fix commits, a **rebase** was safe and kept
the history linear.

**Rule of thumb:** use rebase when your local commits are simple and haven't been
shared with anyone else. Use merge when multiple people may have based work on
your local commits.

## Steps Taken

### 1. Inspect the divergence

```bash
git status
git log --oneline -5
git fetch origin
git log --oneline origin/main -5
```

Confirmed 1 local commit and 2 remote commits, all diverging from `e1acece`.

### 2. Examine what each side changed

```bash
git log --oneline e1acece..HEAD          # local-only commits
git log --oneline e1acece..origin/main   # remote-only commits
git show --stat HEAD                     # what the local commit touched
git log --stat e1acece..origin/main      # what the remote commits touched
```

No file overlap between local (`notes/PLAN_MDv-adding-PDF-viewing.md`) and
remote (`run.sh`, `CHANGELOG.md`, `version.py`, `MDviewer.desktop.template`) —
rebase would be conflict-free.

### 3. Rebase local commit on top of remote

```bash
git pull --rebase origin main
```

This fetched the two remote commits, replayed them onto the local branch, then
re-applied the local notes commit on top. Result:

```
1856025  added Plan for adding PDF viewing MDviewer   ← local commit (rebased)
ecedd06  Fix system menu launch: use run.sh ...       ← from remote
1355540  Fix startup crash caused by empty XDG...     ← from remote
e1acece  Add PDF viewing support (v0.3.0)             ← shared base
```

### 4. Push the rebased history

```bash
git push origin main
```

Local and remote now point to the same commit (`1856025`). Sync complete.

## Key Commands Reference

| Command | Purpose |
|---|---|
| `git fetch origin` | Download remote refs without changing local branch |
| `git log --oneline origin/main -5` | See what remote has |
| `git log --oneline e1acece..HEAD` | Commits local has that remote doesn't |
| `git log --oneline e1acece..origin/main` | Commits remote has that local doesn't |
| `git show --stat HEAD` | What files a commit touched |
| `git pull --rebase origin main` | Fetch + rebase local commits on top of remote |
| `git push origin main` | Push the resolved history |
