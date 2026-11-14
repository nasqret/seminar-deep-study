#!/usr/bin/env bash
# Runs on a compute node inside $SEM_ROOT/formal: fetch Mathlib oleans for the given modules only
# (module names such as Mathlib.Algebra.Field.Defs, not file paths), then drop the compressed copies.
set -euo pipefail
lake exe cache get "$@" 2>&1 | tail -5
rm -f "${MATHLIB_CACHE_DIR:?}"/*.ltar
du -sh .lake/packages/mathlib/.lake 2>/dev/null || true
