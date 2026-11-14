#!/usr/bin/env bash
# Install this skill for Claude Code by linking it into the skills directory.
#   ./install.sh                 # link ~/.claude/skills/seminar-deep-study -> this directory
#   ./install.sh --target DIR    # link DIR/seminar-deep-study instead (another skills directory)
#   ./install.sh --dry-run       # show what would happen
#   ./install.sh --uninstall     # remove the link, only if it points to this directory
#   ./install.sh --force         # replace a link that points elsewhere (never a real directory)
# It never deletes or overwrites a file or directory; it only creates or removes its own link.
set -euo pipefail
NAME="seminar-deep-study"
SRC="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd -P)"
DIR="${CLAUDE_SKILLS_DIR:-$HOME/.claude/skills}"
DRY=0; UNINSTALL=0; FORCE=0
while [[ $# -gt 0 ]]; do
  case "$1" in
    --target) DIR="${2:?--target needs a directory}"; shift 2 ;;
    --dry-run) DRY=1; shift ;;
    --uninstall) UNINSTALL=1; shift ;;
    --force) FORCE=1; shift ;;
    -h|--help) sed -n '2,8p' "$0"; exit 0 ;;
    *) echo "install.sh: unknown option $1" >&2; exit 2 ;;
  esac
done
[[ -f "$SRC/SKILL.md" ]] || { echo "install.sh: no SKILL.md in $SRC" >&2; exit 1; }
grep -q "^name: $NAME\$" "$SRC/SKILL.md" || { echo "install.sh: SKILL.md does not name '$NAME'" >&2; exit 1; }
LINK="$DIR/$NAME"
run() { if [[ $DRY -eq 1 ]]; then echo "would run: $*"; else "$@"; fi; }
points_here() { [[ -L "$LINK" ]] && [[ "$(cd "$LINK" 2>/dev/null && pwd -P)" == "$SRC" ]]; }

if [[ $UNINSTALL -eq 1 ]]; then
  if points_here; then run rm "$LINK"; echo "removed the link $LINK"; exit 0; fi
  echo "install.sh: $LINK is not a link to $SRC; nothing removed" >&2; exit 1
fi
if points_here; then echo "already installed: $LINK -> $SRC"; exit 0; fi
if [[ -L "$LINK" ]]; then
  if [[ $FORCE -eq 1 ]]; then run rm "$LINK"
  else echo "install.sh: $LINK is a link to $(readlink "$LINK"); use --force to replace it" >&2; exit 1; fi
elif [[ -e "$LINK" ]]; then
  echo "install.sh: $LINK exists and is not a link; move it away yourself" >&2; exit 1
fi
run mkdir -p "$DIR"
run ln -s "$SRC" "$LINK"
echo "installed: $LINK -> $SRC (start a new Claude Code session to load it)"
