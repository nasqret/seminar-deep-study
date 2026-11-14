#!/usr/bin/env bash
# Build the Verso document and render it to HTML (run where ../formal is built, e.g.
#   SEM_CPUS=16 SEM_MEM=64G SEM_TIME=180 tools/cluster.sh run 'cd ../verso && bash scripts/remote-build.sh').
#
# 1. `lake build Doc` elaborates every chapter against the compiled library: each `signature` block
#    is compared with the declaration of the same name, each `lean` block is re-checked, each
#    `leanOutput` must match Lean's actual message. Any mismatch is a build error.
# 2. `lake exe generate-doc` renders HTML (multi-page and single-page) into `_out/`. Its exit status
#    is checked: it can exit non-zero after writing a complete-looking site.
set -uo pipefail
cd "$(dirname "$0")/.."
t0=$(date +%s); stamp() { echo "[$(( $(date +%s) - t0 ))s] $*"; }

# If ../formal gained imports since remote-setup.sh ran, its Mathlib cache was extended with new
# oleans: hard-link the new files into our copies (existing files are left alone), so that Lake
# finds them here instead of compiling those Mathlib modules from source.
for d in ../formal/.lake/packages/*/; do
  p=$(basename "$d"); src="$d.lake/build"; dst=".lake/packages/$p/.lake/build"
  if [ -d "$src" ] && [ -d "$dst" ]; then cp -aln "$src/." "$dst/" 2>/dev/null || true; fi
done
stamp "dependency builds refreshed from ../formal"
# Files the document quotes from outside ../formal (e.g. CAS transcripts) are copied into
# evidence/ by a laptop-side step before syncing: rsync -a --delete cas/out/ verso/evidence/cas-out/
# The document may read ../formal files at elaboration time, which Lake does not track: always
# re-elaborate the document itself from scratch (dependencies keep their builds).
rm -rf .lake/build
stamp "lake build Doc"
lake build Doc 2>&1 | grep -v '^✔' | tail -n "${SEM_DOC_TAIL:-150}"; rc=${PIPESTATUS[0]}
stamp "lake build Doc: exit $rc"; [ "$rc" -eq 0 ] || exit "$rc"
lake build generate-doc 2>&1 | grep -v '^✔' | tail -n 40; rc=${PIPESTATUS[0]}
[ "$rc" -eq 0 ] || exit "$rc"
rm -rf _out
stamp "lake exe generate-doc"
lake exe generate-doc --with-html-single --output _out 2>&1 | tail -n 80; rc=${PIPESTATUS[0]}
stamp "generate-doc: exit $rc"
du -sh _out _out/* 2>/dev/null
exit "$rc"
