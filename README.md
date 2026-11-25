# config

My personal dotfiles and tool configuration.

| File | Goes to | What it is |
|---|---|---|
| `zsh/.zshrc` | `~/.zshrc` | Zsh config (Oh My Zsh) |
| `claude/settings.json` | `~/.claude/settings.json` | Claude Code settings |
| `claude/statusline.py` | `~/.claude/statusline.py` | Claude Code status line script |
| `npm/.npmrc` | `~/.npmrc` | npm config |

To use any of these, copy the file to the path in the "Goes to" column.

## Syncing (for me)

```sh
./sync.sh            # copy, scan, review diff, commit, push
./sync.sh -m "msg"   # same, with a custom commit message
```

- The files to sync are listed in `paths.env.example`. To change paths or set a `MACHINE_NAME` on one machine, copy that file to `paths.env` (gitignored).
- [gitleaks](https://github.com/gitleaks/gitleaks) is required (`sudo apt install gitleaks`). If it finds anything, the sync stops before any files are copied.
- The script shows the full diff and asks before committing. gitleaks catches credentials but not personal info, so read the diff.
