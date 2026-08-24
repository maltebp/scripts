# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this repo is

A personal collection of Windows developer shell shortcuts. There is no build, no
test suite, no linter and no package manifest — every script is run directly by
the shell. "Testing" a change means invoking the command in a real shell and
checking the behaviour.

**`cmd/` is the only maintained front-end.** One `.cmd` file per command in
`cmd/commands/`, which is expected to be on `PATH`; there is no installer tracked
in the repo. Python helpers live in `cmd/python/`.

`bash/` is dead code — a Git Bash port (`import.sh` defining shell *functions*,
sourced from `~/.bashrc`) that was last touched in June 2023 and has not been
tested, developed or used since. Do not mirror changes into it, and do not treat
`import.sh` as a reference for how a command should behave. It duplicates rather
than shares code (`bash/ds.py` is a stale byte-identical copy of
`cmd/python/ds.py`), so it has drifted freely.

## Config pattern (important)

Machine-specific paths never live in tracked files:

- `cmd/_config.cmd` is the **tracked template**, listing every available
  variable with an empty value.
- Each machine copies it to `cmd/config.cmd`, which is gitignored and holds the
  real paths.

When adding a new config variable, add it to `_config.cmd` as well, or other
machines silently inherit a stale value.

Commands pull config in with `call "%~dp0..\config.cmd"` and then reference the
`%s_path_*%` variables. (`bash/_config.sh` is the unmaintained equivalent.)

## Local overrides

`cmd/local/`, `bash/local/` and `local/` are gitignored, for scripts that should
stay on one machine.

## Python helpers

`cmd/python/*.py` are launched from `.cmd` wrappers as
`%s_path_python% "%~dp0..\python\<name>.py" <config paths> %*` — the tool path
comes from config and is passed as the *first* argv, so these scripts hard-code
`sys.argv[1]` as the executable and `sys.argv[2]` as the target.

`cmd/python/scripts_core.py` holds the shared helpers: `expect()` (internal
invariant, prints `[Internal Error]`) and `user_error_and_exit()` (prints
`[Error]` to stderr, exit 1).

GUI apps are started with `subprocess.Popen(..., close_fds=True,
creationflags=DETACHED_PROCESS)` (`0x00000008`) so the app survives the shell
closing.

## The `ds` (directory shortcut) mechanism

`ds` is the one non-obvious design in the repo. A child process cannot change the
parent shell's directory, so `ds.py` *prints* the resolved directory and the
wrapper performs the `cd`:

`ds.cmd` redirects the Python output to a temp file, then `cd /d` to its contents
on exit 0.

Exit codes are inverted from the usual meaning: a **non-zero** exit means "this
was informational output (a listing, an error), print it instead of cd-ing" —
so `ds -l` and `ds -s` intentionally `sys.exit(1)`. Keep that contract when
editing `ds.py`.

`ds.cmd` ends with `cmd /c exit %failed%` rather than `exit /b` because
`exit /b` does not propagate an exit code that a caller's `&&` will respect —
that line must stay last.

Shortcuts are persisted as `name "path"` lines in
`%USERPROFILE%\AppData\Local\cds\shortcuts`.

## Bundled third-party binaries

`external/` holds vendored tools committed to the repo (currently Hourglass,
used by `timer.cmd`). Its generated `.config` file is gitignored.
