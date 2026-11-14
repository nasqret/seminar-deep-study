#!/usr/bin/env bash
# Deploy the seminar site to a web server with rsync — only on an explicit request.
#   scripts/deploy.sh                  # assemble _site/, check it, upload
#   scripts/deploy.sh --dry-run        # assemble and check, then show what rsync would change
#   scripts/deploy.sh --assemble-only  # assemble and check only (e.g. to look at _site/ locally)
#
# Configuration (environment; record the values in MAINTENANCE.md):
#   SITE_REMOTE   user@host (passwordless SSH: keys or an agent; never a stored password)
#   SITE_DEST     destination directory relative to the remote home, e.g. public_html/<project>
#   SITE_URL      public URL of the destination (used by the link checker and the final message)
#   SITE_LEAK_PATTERNS  optional file of regexes that must not appear in _site/ (tools/leak_scan.py)
#
# _site/ is assembled from an explicit ALLOW-LIST below; private material (the paper's PDF/TeX,
# the vault, working notes, unpublished findings) never enters it. rsync --delete acts only
# inside SITE_DEST.
set -euo pipefail
cd "$(dirname "$0")/.."
MODE="${1:-}"
SITE="_site"

need() { [[ -e "$1" ]] || { echo "missing: $1 — $2"; exit 1; }; }
need index.html "write the landing page first"
need assets/hero.webp "run scripts/generate_hero.py"

rm -rf "$SITE" && mkdir -p "$SITE/assets"
# ---- allow-list: edit to match the project --------------------------------------------------
cp index.html "$SITE"/
cp assets/hero.webp assets/hero.jpg assets/og.png assets/favicon.png "$SITE"/assets/
cp scripts/generate_hero.py "$SITE"/assets/                    # the picture's source is public
[[ -f .htaccess ]] && cp .htaccess "$SITE"/
[[ -d book/_build/html ]] && { mkdir -p "$SITE/book"; rsync -a book/_build/html/ "$SITE"/book/; }
[[ -d slides ]] && { mkdir -p "$SITE/slides"; cp slides/*.html "$SITE"/slides/; [[ -d slides/vendor ]] && rsync -a slides/vendor "$SITE"/slides/; }
[[ -d verso/_out/html-multi ]] && { mkdir -p "$SITE/verso"; rsync -a verso/_out/html-multi/ "$SITE"/verso/; }
# optional, only if the speaker wants the sources online (the landing page's cards link them; the
# link check below fails until each linked directory is either published here or unlinked):
# mkdir -p "$SITE/formal" && rsync -a --exclude .lake formal/ "$SITE"/formal/
# mkdir -p "$SITE/cas" && rsync -a cas/ "$SITE"/cas/
# mkdir -p "$SITE/artifacts" && rsync -a artifacts/computational "$SITE"/artifacts/
# ----------------------------------------------------------------------------------------------

# Guard: nothing private may be in _site/.
if find "$SITE" \( -path '*vault*' -o -path '*source/*' -o -name '*.pdf' -o -name 'MEMORY.md' \
     -o -name 'JOURNAL.md' -o -name 'CLAUDE.md' -o -name 'digest.md' -o -path '*_remote*' \) | grep -q .; then
  echo "ERROR: private files ended up in $SITE/:"; find "$SITE" \( -path '*vault*' -o -path '*source/*' -o -name '*.pdf' \
     -o -name 'MEMORY.md' -o -name 'JOURNAL.md' -o -name 'CLAUDE.md' -o -name 'digest.md' -o -path '*_remote*' \); exit 1
fi
python3 -I scripts/check_links.py "$SITE" --base "${SITE_URL:-}" || { echo "Fix the links before deploying."; exit 1; }
if [[ -n "${SITE_LEAK_PATTERNS:-}" ]]; then
  python3 -I tools/leak_scan.py "$SITE" --patterns "$SITE_LEAK_PATTERNS" || { echo "Leak scan failed."; exit 1; }
fi
[[ "$MODE" == "--assemble-only" ]] && { echo "Assembled $SITE/"; exit 0; }

REMOTE="${SITE_REMOTE:?set SITE_REMOTE=user@host}"
DEST="${SITE_DEST:?set SITE_DEST, e.g. public_html/<project>}"
# Permissions are set locally: macOS /usr/bin/rsync (openrsync) has no --chmod=D…,F…
find "$SITE" -type d -exec chmod 755 {} + && find "$SITE" -type f -exec chmod 644 {} +
RSYNC_OPTS=(-rltvz --delete --perms)
if [[ "$MODE" == "--dry-run" ]]; then
  rsync "${RSYNC_OPTS[@]}" --dry-run "$SITE"/ "$REMOTE:$DEST/"
  exit 0
fi
ssh -o BatchMode=yes "$REMOTE" "mkdir -p $(printf '%q' "$DEST")"
rsync "${RSYNC_OPTS[@]}" "$SITE"/ "$REMOTE:$DEST/"
echo "Deployed: ${SITE_URL:-$REMOTE:$DEST}"
