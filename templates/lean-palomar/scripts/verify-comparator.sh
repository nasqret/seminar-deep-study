#!/usr/bin/env bash
# Judge Solution against Challenge as Palomar does, with the `lake comparator` shipped in this
# project's own toolchain (Lean kernel + bundled NanoDa and con-ron kernels). Adapted from the
# Palomar template; unlike the template it does NOT run `lake exe cache get` (the needed oleans
# are already built). Run from anywhere: it changes into the project root.
set -euo pipefail
cd "$(dirname "$0")/.."
prefix=$(lean --print-prefix)
for tool in lake leanexport leanchecker nanoda_bin con-ron; do
  [ -x "$prefix/bin/$tool" ] || { echo "error: toolchain lacks $tool (needs Lean >= v4.35.0-rc2)" >&2; exit 1; }
done
# Palomar's CI runs the comparator inside a bwrap sandbox. On hosts without bubblewrap (many
# clusters) set SEM_NO_SANDBOX=1 to run it unsandboxed: acceptable for checking one's OWN
# project, never for judging untrusted code.
flags=(--paranoid)
if ! command -v bwrap >/dev/null; then
  if [ "${SEM_NO_SANDBOX:-0}" = 1 ]; then flags+=(--inadvisably-no-sandbox)
  else echo "error: bwrap (bubblewrap) is required by lake comparator (or set SEM_NO_SANDBOX=1)" >&2; exit 2; fi
fi
config=$(mktemp "${TMPDIR:-/tmp}/palomar-comparator.XXXXXX")
trap 'rm -f "$config"' EXIT
python3 - comparator.json "$config" "$prefix" <<'PY'
import json, pathlib, sys
src, dst, prefix = sys.argv[1:]
c = json.loads(pathlib.Path(src).read_text())
c.pop("enable_nanoda", None)
c["external_kernels"] = {"nanoda": [f"{prefix}/bin/nanoda_bin"], "con-ron": [f"{prefix}/bin/con-ron"]}
pathlib.Path(dst).write_text(json.dumps(c, indent=2) + "\n")
PY
lake comparator --config "$config" "${flags[@]}"
