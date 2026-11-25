# Agent notes

## Synced files

Each file under `zsh/`, `claude/` and `npm/` is a copy. Its source of truth is the machine path listed in `FILES` in `paths.env.example` (e.g. `~/.claude/statusline.py`). Edit the machine path; `sync.sh` copies it over the repo copy.

`sync.sh` asks for confirmation on `/dev/tty`, so the user runs it from their own terminal.

To add a synced file, add it to `FILES` in `paths.env.example` and to the table in `README.md`.

## Docs

Docs say what a file is for and point to it. Settings values, plugin lists, sample output and other details live only in the file they describe, so a change there never leaves a doc stale. README table descriptions stay a few words long.
