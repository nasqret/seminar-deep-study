# Compute: local disk, Mathlib, clusters, remote CAS

## 1. Local first, but measure

- `df -h ~` before installing anything. A Lean toolchain takes a few GB, and a full Mathlib
  cache more than that. On a nearly full disk, decide with the user (phase 0) between a partial
  local install and remote builds.
- **Never run `lake update` in a Mathlib project without `MATHLIB_NO_CACHE_ON_UPDATE=1`.**
  Mathlib's post-update hook otherwise downloads the entire cache. In the first use this filled
  the laptop's disk in one command, leaving 120 MB free.
- Fetch prebuilt oleans only for the modules you import: `lake exe cache get Mathlib.A.B
  Mathlib.C.D`. Use module names: in a downstream project, file paths are resolved against the
  project root and fail.
- Pin Mathlib to the release tag that matches `lean-toolchain` (for example `rev = "v4.35.0"`), so
  that `lake exe cache get` finds the oleans.
- Never run `lake`, `lake env` or builds inside the user's other Lean projects: elan silently
  installs their pinned toolchains.
- Downloaded compressed cache files (`*.ltar`) can be deleted after unpacking.

## 2. A SLURM cluster (when the user allows it)

`templates/cluster/cluster.sh` is the driver, copied into the project as `tools/cluster.sh`.
It syncs the sources with rsync (never `.lake`) and runs everything on a compute node via `srun`.

| command | does |
|---|---|
| `tools/cluster.sh setup` | once: toolchain into the project's remote root, shallow dependency clones at the manifest revisions |
| `tools/cluster.sh cache Mathlib.X …` | Mathlib oleans for the import closure of these modules |
| `tools/cluster.sh lean Proj/File.lean` | elaborate one file (its project imports must be built) |
| `tools/cluster.sh demo [demo/LiveDemo.lean]` | the live demo: a small allocation, a round trip of seconds |
| `tools/cluster.sh build [targets]` | `lake build` |
| `tools/cluster.sh run 'CMD'` | any command inside `formal/` on a compute node |
| `tools/cluster.sh fetch PATH` | copy a remote path back into `_remote/` (git-ignored) |

Configuration (environment variables; put the values in the project's `MAINTENANCE.md`):
`SEM_HOST` (ssh alias of the gateway), `SEM_ROOT` (remote project root on a work or scratch file
system), `SEM_PARTITION`, `SEM_JOB` (job-name prefix), `SEM_CPUS`, `SEM_MEM`, `SEM_TIME`
(minutes), `SEM_TAIL` (lines of output to show).

Etiquette (copy these into every agent brief that computes):
- compute only through `srun`/`sbatch`, never on the gateway; the gateway is for file transfer;
- one remote root per project; never touch other directories, other projects or other jobs;
- `ELAN_HOME`, `XDG_CACHE_HOME` and `MATHLIB_CACHE_DIR` live under the project root when home
  directories have small quotas (bytes and file counts);
- shallow, depth-1 clones of the dependencies save the full Mathlib history
  (`templates/cluster/remote/shallow_deps.py`); Lake accepts a checkout whose HEAD equals the
  manifest revision;
- name jobs with the project prefix, so that `squeue --me` shows whose they are;
- keep foreground ssh commands short; anything long goes through the batch system;
- if the cluster is unreachable, diagnose (VPN? DNS?), never change network settings, and ask;
- hosts without `bubblewrap`: run the comparator unsandboxed for your own project only.

A second project on the same cluster (for example a Verso document) can reuse the formalization's
dependency checkouts: copy the sources and hard-link the build directories (`cp -al`) instead of
downloading Mathlib again (`templates/verso/scripts/remote-setup.sh`).

The driver mirrors the laptop with `rsync --delete`: anything created only on the cluster inside
the synced directories (a `lake-manifest.json` written by `lake update`, generated files) is
deleted by the next sync. Fetch such files back at once (`tools/cluster.sh fetch …`) and commit
them; keep remote-only outputs outside the synced directories (logs under `$SEM_ROOT/logs`).

## 3. A remote CAS

`templates/cas/remote_run.sh` uploads a script, runs it in batch mode with stdin closed and a
timeout, detects errors in the text and returns the transcript, with meaningful exit codes. Set
`CAS_HOST` (ssh alias) and `CAS_BIN` (the remote binary). It needs passwordless SSH (keys or an
agent), never a stored password.

## 4. Budgets and records

Ask before anything that runs for more than a few minutes locally or uses many cluster CPU-hours.
Record where each computation ran (laptop, cluster, CAS host) in `MAINTENANCE.md` and in the
transcript headers. Subagents share the session's local limit; split it in their briefs.

