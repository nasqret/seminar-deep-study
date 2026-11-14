#!/usr/bin/env bash
# Render the deck in headless Chrome and report slides whose content overflows the 1280×720 box,
# comes too close to the footer, or has formulas or text wider than their column.
#   slides/build/check_render.sh [slides/seminar.html]
# CHROME may point to the browser binary. A throwaway profile (--user-data-dir) is used, so no
# headless-Chrome caches pile up in the user's Library.
set -euo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
SLIDES="$(dirname "$HERE")"
DECK="$(cd "$(dirname "${1:-$SLIDES/seminar.html}")" && pwd)/$(basename "${1:-$SLIDES/seminar.html}")"
if [[ -z "${CHROME:-}" ]]; then
  for c in "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" google-chrome chromium chromium-browser; do
    if command -v "$c" >/dev/null 2>&1 || [[ -x "$c" ]]; then CHROME="$c"; break; fi
  done
fi
[[ -n "${CHROME:-}" ]] || { echo "no Chrome found; set CHROME" >&2; exit 2; }
TMP="$(mktemp -d "${TMPDIR:-/tmp}/deckcheck.XXXXXX")"
CHECK="$(dirname "$DECK")/_check.html"
trap 'rm -rf "$TMP"; rm -f "$CHECK"' EXIT
python3 - "$DECK" "$HERE/check_harness.js" "$CHECK" <<'PY'
import sys, pathlib
src, js, dst = sys.argv[1:]
s = pathlib.Path(src).read_text()
pathlib.Path(dst).write_text(s.replace('</body>', '<script>' + pathlib.Path(js).read_text() + '</script>\n</body>'))
PY
"$CHROME" --headless=new --disable-gpu --no-first-run --user-data-dir="$TMP/profile" \
  --window-size=1280,720 --virtual-time-budget=120000 --dump-dom "file://$CHECK" 2>/dev/null > "$TMP/dom.html"
python3 - "$TMP/dom.html" <<'PY'
import sys, re, json, html
d = open(sys.argv[1]).read()
m = re.search(r'<pre id="overflow-report">(.*?)</pre>', d, re.S)
if not m:
    sys.exit('no report: did the page load? (vendor/ present? run slides/build/vendor.sh)')
rows = json.loads(html.unescape(m.group(1)))
bad = 0
for r in rows:
    flags = []
    if r['sh'] > 722: flags.append(f"overflow: scrollHeight {r['sh']}")
    if r['maxBottom'] > 675 and not r['worst'].startswith('DIV.vc'): flags.append(f"content bottom {r['maxBottom']} ({r['worst']})")
    if r['wide']: flags.append(f"wide math {r['wide']}")
    if r['hov']: flags.append(f"wide text {r['hov']}")
    if flags:
        bad += 1
        print(f"slide {r['i']}: " + '; '.join(flags))
print(f"{len(rows)} slides rendered, {bad} with layout problems")
sys.exit(1 if bad else 0)
PY
