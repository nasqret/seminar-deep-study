#!/usr/bin/env bash
# Run all Lean/Lake work for this project on a SLURM cluster (no Mathlib needed on the laptop).
#
#   tools/cluster.sh setup            # toolchain + shallow dependency clones (once)
#   tools/cluster.sh sync             # rsync formal/ and verso/ to the cluster (sources only)
#   tools/cluster.sh build [TARGETS]  # sync, then `lake build TARGETS` on a compute node
#   tools/cluster.sh lean FILE        # sync, then `lake env lean FILE` on a compute node (one file)
#   tools/cluster.sh demo [FILE]      # live demo: like `lean`, small allocation (default demo/LiveDemo.lean)
#   tools/cluster.sh cache MOD...     # fetch the Mathlib cache for these modules (and their closure)
#   tools/cluster.sh run 'CMD'        # sync, then run CMD inside formal/ on a compute node
#   tools/cluster.sh fetch PATH       # copy a remote path (relative to SEM_ROOT) back into ./_remote/
#
# Configuration (environment; record the values in MAINTENANCE.md):
#   SEM_HOST       ssh alias of the cluster gateway (passwordless: keys or an agent)
#   SEM_ROOT       remote project root on a work/scratch file system (NOT a small-quota home)
#   SEM_PARTITION  SLURM partition (default: cpu)
#   SEM_JOB        job-name prefix, so that `squeue --me` shows whose jobs these are (default: sem)
#   SEM_CPUS, SEM_MEM, SEM_TIME   resources for build/lean/run (defaults 16, 48G, 120 minutes)
#   SEM_TAIL       lines of output to show (default 60-120)
#
# Etiquette: computation only via srun/sbatch, never on the gateway (it is for file transfer);
# nothing outside $SEM_ROOT is touched; never cancel jobs you did not submit. ELAN_HOME and all
# caches live under $SEM_ROOT because home directories on clusters often have small quotas.
set -euo pipefail

HOST="${SEM_HOST:?set SEM_HOST to the ssh alias of the cluster gateway}"
W="${SEM_ROOT:?set SEM_ROOT to the remote project root (work or scratch file system)}"
PART="${SEM_PARTITION:-cpu}"
JOB="${SEM_JOB:-sem}"
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
SRUN="srun -p $PART --cpus-per-task=${SEM_CPUS:-16} --mem=${SEM_MEM:-48G} -t ${SEM_TIME:-120}"
ENVSET="export ELAN_HOME=$W/elan; export PATH=$W/elan/bin:\$PATH; export MATHLIB_NO_CACHE_ON_UPDATE=1; export XDG_CACHE_HOME=$W/xdg-cache; export MATHLIB_CACHE_DIR=$W/xdg-cache/mathlib"

remote() { ssh -o BatchMode=yes -o ConnectTimeout=15 "$HOST" "bash -lc $(printf '%q' "$1")"; }

sync() {
  remote "mkdir -p $W/formal $W/verso $W/tools/remote"
  rsync -az --delete --exclude .lake --exclude '.DS_Store' "$ROOT/formal/" "$HOST:$W/formal/"
  rsync -az --delete "$ROOT/tools/remote/" "$HOST:$W/tools/remote/"
  if [[ -d "$ROOT/verso" ]]; then
    rsync -az --delete --exclude .lake --exclude '_out' --exclude '.DS_Store' "$ROOT/verso/" "$HOST:$W/verso/"
  fi
}

cmd="${1:-}"; shift || true
case "$cmd" in
  setup)
    sync
    # elan: use the cluster's elan if it has one, otherwise install it into $W/elan (no PATH edits).
    remote "mkdir -p $W/elan/bin $W/xdg-cache/mathlib; if [ -x \$HOME/.elan/bin/elan ]; then for b in elan lake lean leanc; do ln -sf \$HOME/.elan/bin/elan $W/elan/bin/\$b; done; elif [ ! -x $W/elan/bin/elan ]; then curl -sSfL https://raw.githubusercontent.com/leanprover/elan/master/elan-init.sh | ELAN_HOME=$W/elan sh -s -- -y --no-modify-path --default-toolchain none; fi"
    remote "$ENVSET; cd $W/formal && $SRUN -J $JOB-setup bash $W/tools/remote/setup.sh"
    ;;
  sync) sync ;;
  cache)
    sync
    remote "$ENVSET; cd $W/formal && $SRUN -J $JOB-cache bash $W/tools/remote/cache.sh $*"
    ;;
  build)
    sync
    remote "$ENVSET; cd $W/formal && $SRUN -J $JOB-build lake build $* 2>&1 | tail -${SEM_TAIL:-60}"
    ;;
  lean)
    sync
    f="$1"
    remote "$ENVSET; cd $W/formal && $SRUN -J $JOB-lean lake env lean $(printf '%q' "$f") 2>&1 | tail -${SEM_TAIL:-80}"
    ;;
  demo)
    sync
    f="${1:-demo/LiveDemo.lean}"
    remote "$ENVSET; cd $W/formal && srun -p $PART --cpus-per-task=4 --mem=16G -t 20 -J $JOB-demo lake env lean $(printf '%q' "$f") 2>&1 | tail -${SEM_TAIL:-120}"
    ;;
  run)
    sync
    remote "$ENVSET; cd $W/formal && $SRUN -J $JOB-run bash -c $(printf '%q' "$1") 2>&1 | tail -${SEM_TAIL:-80}"
    ;;
  fetch)
    mkdir -p "$ROOT/_remote"
    rsync -az "$HOST:$W/$1" "$ROOT/_remote/"
    ;;
  *) sed -n '2,11p' "$0"; exit 1 ;;
esac
