#!/usr/bin/env bash
# After a deploy: check that the key URLs answer with HTTP 200.
#   SITE_URL=https://example.org/<project> scripts/check_site.sh [path ...]
# e.g. scripts/check_site.sh book/intro.html slides/seminar.html verso/index.html
set -uo pipefail
BASE="${SITE_URL:?set SITE_URL to the public URL of the site}"
fail=0
for path in "" index.html assets/hero.webp assets/og.png assets/favicon.png "$@"; do
  code=$(curl -s -o /dev/null -w '%{http_code}' "$BASE/$path")
  printf '%s  %s\n' "$code" "$BASE/$path"
  [[ "$code" == "200" ]] || fail=1
done
exit $fail
