#!/usr/bin/env bash
# Run a CAS script on a remote host and print a clean transcript with a meaningful exit status.
#
#   tools/remote_run.sh SCRIPT [--timeout SECONDS] [--keep]
#   CAS_HOST=myhost CAS_BIN=/opt/magma/current/magma tools/remote_run.sh cas/02_certs.m > cas/out/02_certs.out
#
# Configuration: CAS_HOST (ssh alias; passwordless SSH with keys or an agent), CAS_BIN (the remote
# binary; default `magma`), CAS_ARGS (default `-b`, Magma's batch mode; e.g. empty for `gp -q`).
#
# Mechanics: the script is copied to a temporary file on the host and run there in a login shell
# (where the CAS is usually on PATH) with stdin CLOSED (`ssh -n`): a CAS that hits an error falls
# back to its interactive prompt, and with an open stdin it would wait forever. A timeout is
# enforced on both sides. Magma exits 0 even when a script fails, so errors are recognised in the
# text: lines starting with `>>`, or containing `User error` / `Runtime error`.
#
# Exit status: 0 ok · 1 usage · 2 the CAS reported an error · 3 ssh/scp failure · 124 timeout.
set -u
HOST="${CAS_HOST:?set CAS_HOST to the ssh alias of the CAS host}"
BIN="${CAS_BIN:-magma}"
ARGS="${CAS_ARGS--b}"
TIMEOUT=600; KEEP=0; SRC=""
while [ $# -gt 0 ]; do
  case "$1" in
    --timeout) TIMEOUT="${2:?}"; shift 2 ;;
    --keep) KEEP=1; shift ;;
    -h|--help) sed -n '2,17p' "$0"; exit 0 ;;
    -*) echo "remote_run: unknown option $1" >&2; exit 1 ;;
    *) SRC="$1"; shift ;;
  esac
done
[ -f "$SRC" ] || { echo "remote_run: no such script: $SRC" >&2; exit 1; }
case "$TIMEOUT" in ''|*[!0-9]*) echo "remote_run: --timeout wants seconds" >&2; exit 1 ;; esac

REMOTE="/tmp/cas_$(basename "$SRC" | tr -c 'A-Za-z0-9._-' '_')_$$"
OUT="$(mktemp "${TMPDIR:-/tmp}/remote_run.XXXXXX")"; trap 'rm -f "$OUT"' EXIT
OPTS=(-o BatchMode=yes -o ConnectTimeout=15)

scp -q "${OPTS[@]}" "$SRC" "$HOST:$REMOTE" || { echo "remote_run: could not copy to $HOST (try: ssh $HOST true)" >&2; exit 3; }
RM="rm -f $REMOTE"; [ "$KEEP" = 1 ] && RM=":"
CMD="cd /tmp && if command -v timeout >/dev/null 2>&1; then timeout -k 5 $((TIMEOUT + 10)) $BIN $ARGS $REMOTE; else $BIN $ARGS $REMOTE; fi; rc=\$?; $RM; exit \$rc"

ssh -n "${OPTS[@]}" "$HOST" "bash -lc $(printf '%q' "$CMD")" > "$OUT" 2>&1 &
pid=$!; start=$(date +%s); rc=0
while kill -0 "$pid" 2>/dev/null; do
  if [ $(( $(date +%s) - start )) -ge "$TIMEOUT" ]; then
    kill "$pid" 2>/dev/null; sleep 1; kill -9 "$pid" 2>/dev/null
    cat "$OUT"; echo "remote_run: TIMEOUT after ${TIMEOUT}s" >&2; exit 124
  fi
  sleep 0.5
done
wait "$pid"; rc=$?
cat "$OUT"
[ "$rc" -eq 255 ] && { echo "remote_run: ssh failure talking to $HOST" >&2; exit 3; }
if grep -qE '^>>|User error|Runtime error' "$OUT"; then
  echo "remote_run: the CAS reported an error:" >&2
  grep -E '^>>|User error|Runtime error|^In file ' "$OUT" | sed 's/^/  | /' >&2
  exit 2
fi
[ "$rc" -eq 124 ] && { echo "remote_run: remote timeout" >&2; exit 124; }
[ "$rc" -ne 0 ] && { echo "remote_run: remote exit status $rc" >&2; exit "$rc"; }
exit 0
