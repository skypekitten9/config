#!/usr/bin/env bash
# Copies local config files into this repo, scans them with gitleaks,
# shows the diff, then commits and pushes after confirmation.
# Usage: ./sync.sh [-m "commit message"]
set -euo pipefail

REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$REPO_DIR"

MESSAGE=""
while getopts "m:" opt; do
  case "$opt" in
    m) MESSAGE="$OPTARG" ;;
    *) echo "Usage: $0 [-m \"commit message\"]" >&2; exit 2 ;;
  esac
done

if ! command -v gitleaks >/dev/null 2>&1; then
  echo "gitleaks is not installed, so nothing will be synced." >&2
  echo "Install it with: sudo apt install gitleaks" >&2
  exit 1
fi

source ./paths.env.example
[[ -f ./paths.env ]] && source ./paths.env

# Find the source files that exist.
sources=() dests=()
for pair in "${FILES[@]}"; do
  dest="${pair%%:*}" src="${pair#*:}"
  if [[ ! -f "$src" ]]; then
    echo "skip: $src does not exist" >&2
    continue
  fi
  sources+=("$src") dests+=("$dest")
done
(( ${#sources[@]} )) || { echo "Nothing to sync." >&2; exit 1; }

# Scan the source files before anything is copied into the repo.
found=0
for src in "${sources[@]}"; do
  if ! gitleaks detect --no-git --no-banner --redact --source "$src" >/dev/null 2>&1; then
    echo "gitleaks found something in: $src" >&2
    gitleaks detect --no-git --no-banner --redact --verbose --source "$src" >&2 || true
    found=1
  fi
done
if (( found )); then
  echo "Aborted: remove the secrets above (or add them to .gitleaksignore if they're false positives)." >&2
  exit 1
fi

for i in "${!sources[@]}"; do
  mkdir -p "$(dirname "${dests[$i]}")"
  cp "${sources[$i]}" "${dests[$i]}"
done

git add -- "${dests[@]}"
if git diff --cached --quiet -- "${dests[@]}"; then
  echo "No changes."
  exit 0
fi

git --no-pager diff --cached --stat -- "${dests[@]}"
git --no-pager diff --cached -- "${dests[@]}"
read -r -p "Commit and push? [y/N] " answer </dev/tty
if [[ ! "$answer" =~ ^[Yy]$ ]]; then
  git reset -q -- "${dests[@]}"
  echo "Not committed. The copied files are left unstaged in the repo."
  exit 1
fi

if [[ -z "$MESSAGE" ]]; then
  MESSAGE="Sync${MACHINE_NAME:+ from $MACHINE_NAME}: $(date '+%Y-%m-%d %H:%M')"
fi
git commit -q -m "$MESSAGE" -- "${dests[@]}"
git push -q -u origin HEAD
echo "Pushed: $MESSAGE"
