#!/usr/bin/env bash
# Vendor the deck's JavaScript libraries into slides/vendor/, so the talk works without network:
# reveal.js (core, white theme, notes and highlight plugins), a highlight.js style, and MathJax.
# Each package comes from the npm registry tarball and is checked against the registry's sha512
# integrity before anything is unpacked. Licences are copied next to the files.
#   slides/build/vendor.sh            (needs curl, python3, openssl, tar; about 5 MB on disk)
set -euo pipefail
SLIDES="$(cd "$(dirname "$0")/.." && pwd)"
VENDOR="$SLIDES/vendor"
TMP="$(mktemp -d "${TMPDIR:-/tmp}/vendor.XXXXXX")"; trap 'rm -rf "$TMP"' EXIT

fetch() {  # fetch NAME VERSION -> unpacked into $TMP/NAME/package
  local name=$1 ver=$2 meta url integrity got
  meta="$(curl -sfL "https://registry.npmjs.org/$name/$ver")"
  url="$(printf '%s' "$meta" | python3 -c 'import json,sys; print(json.load(sys.stdin)["dist"]["tarball"])')"
  integrity="$(printf '%s' "$meta" | python3 -c 'import json,sys; print(json.load(sys.stdin)["dist"]["integrity"])')"
  curl -sfL -o "$TMP/$name.tgz" "$url"
  got="sha512-$(openssl dgst -sha512 -binary "$TMP/$name.tgz" | openssl base64 -A)"
  [[ "$got" == "$integrity" ]] || { echo "integrity mismatch for $name@$ver" >&2; exit 1; }
  mkdir -p "$TMP/$name" && tar -xzf "$TMP/$name.tgz" -C "$TMP/$name"
  echo "ok  $name@$ver  $integrity" | cut -c1-80
}

R=reveal.js; RV=5.1.0
H=highlight.js; HV=11.9.0
M=mathjax; MV=3.2.2
fetch $R $RV; fetch $H $HV; fetch $M $MV

rm -rf "$VENDOR" && mkdir -p "$VENDOR"
d="$VENDOR/$R-$RV"; p="$TMP/$R/package"
mkdir -p "$d/dist/theme" "$d/plugin"
cp "$p/LICENSE" "$p/dist/reveal.css" "$p/dist/reveal.js" "$d/" 2>/dev/null || true
mv "$d/reveal.css" "$d/reveal.js" "$d/dist/"
cp "$p/dist/theme/white.css" "$d/dist/theme/"
[[ -d "$p/dist/theme/fonts" ]] && cp -R "$p/dist/theme/fonts" "$d/dist/theme/"
cp -R "$p/plugin/notes" "$p/plugin/highlight" "$d/plugin/"
d="$VENDOR/$H-$HV"; p="$TMP/$H/package"
mkdir -p "$d/styles" && cp "$p/LICENSE" "$d/" && cp "$p/styles/github.min.css" "$d/styles/"
d="$VENDOR/$M-$MV"; p="$TMP/$M/package"
mkdir -p "$d/es5" && cp "$p/LICENSE" "$d/" && cp "$p/es5/tex-mml-chtml.js" "$d/es5/"
cp -R "$p/es5/input" "$p/es5/output" "$d/es5/"
du -sh "$VENDOR"/*
