# Verification evidence

The files in `logs/` record the last full verification run (where it ran: {{WHERE}}).

| file | content |
|---|---|
| `versions.txt` | UTC time of the run, `lean --version`, the Mathlib commit actually checked out |
| `build.log` | `lake build` of all default targets; ends with `build exit 0` |
| `comparator.log` | `bash scripts/verify-comparator.sh`; ends with `comparator exit 0` |

What to look for:

* `build.log`: the only warnings are the deliberate `sorry`s of `Challenge.lean`; the axiom audit
  line `Axiom allowlist passed for N {{LEAN_NAME}} declarations: propext, Classical.choice,
  Quot.sound`.
* `comparator.log`: `… kernel accepts the solution` for each kernel (Lean default and paranoid,
  lean4lean, nanoda, con-leche, con-ron), then `Your solution is okay!`. A first line
  `WARNING: Sandbox disabled` is expected where `bubblewrap` is missing (own project only).

To regenerate (from `formal/`; prefix with `tools/cluster.sh run '…'` on a cluster):

```bash
mkdir -p verification/logs && (date -u +%FT%TZ; lean --version; git -C .lake/packages/mathlib rev-parse HEAD) > verification/logs/versions.txt 2>&1
lake build > verification/logs/build.log 2>&1; echo "build exit $?" >> verification/logs/build.log
bash scripts/verify-comparator.sh > verification/logs/comparator.log 2>&1; echo "comparator exit $?" >> verification/logs/comparator.log
```
