#!/usr/bin/env bash
# Runs on a compute node (via srun) inside $SEM_ROOT/formal: toolchain + shallow dependency clones.
set -euo pipefail
elan toolchain install "$(cat lean-toolchain)" >/dev/null 2>&1 || true
elan toolchain list
mkdir -p .lake/packages
python3 "$(dirname "$0")/shallow_deps.py" lake-manifest.json .lake/packages
du -sh .lake/packages
