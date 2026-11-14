#!/usr/bin/env bash
# Resolve the dependencies of the Verso document next to an already built ../formal (run it where
# ../formal is built, e.g. on a compute node: tools/cluster.sh run 'cd ../verso && bash scripts/remote-setup.sh').
#
# Mathlib and its dependencies are NOT downloaded a second time: ../formal/.lake/packages already
# holds checkouts at exactly the needed revisions, with their oleans. The sources are copied and
# the build directories HARD-LINKED (no extra disk space on a quota-limited file system); then
# `lake update` adds Verso and its own dependencies.
set -euo pipefail
cd "$(dirname "$0")/.."
src=../formal/.lake/packages
dst=.lake/packages
mkdir -p "$dst"
for d in "$src"/*/; do
  p=$(basename "$d")
  if [ -d "$dst/$p" ]; then echo "present $p"; continue; fi
  mkdir -p "$dst/$p"
  (cd "$src/$p" && tar --exclude=./.lake/build -cf - .) | (cd "$dst/$p" && tar -xf -)
  if [ -d "$src/$p/.lake/build" ]; then
    mkdir -p "$dst/$p/.lake"
    cp -al "$src/$p/.lake/build" "$dst/$p/.lake/build"
  fi
  echo "copied  $p $(git -C "$dst/$p" rev-parse --short HEAD 2>/dev/null || echo '?')"
done
# Never let Mathlib's post-update hook download the full cache.
export MATHLIB_NO_CACHE_ON_UPDATE=1
lake update 2>&1 | tail -n 40
# Mathlib must stay at the revision of ../formal.
python3 - <<'PY'
import json, sys
rev = lambda f: next((p["rev"] for p in json.load(open(f))["packages"] if p["name"] == "mathlib"), None)
a, b = rev("lake-manifest.json"), rev("../formal/lake-manifest.json")
print(f"mathlib here {str(a)[:12]}, in ../formal {str(b)[:12]}")
sys.exit(0 if a == b else 1)
PY
du -sh .lake/packages/* 2>/dev/null | sort -h | tail -n 15
