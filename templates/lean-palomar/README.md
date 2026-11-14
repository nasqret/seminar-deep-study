# {{LEAN_NAME}} — a Lean formalization of {{PAPER}} (Palomar format)

| paper | Lean | status |
|---|---|---|
| Theorem … | `{{LEAN_NAME}}.…` | proved / proved with hypotheses / not formalized |

* `Challenge.lean` — the audit surface (Mathlib-only imports, deliberate `sorry`s).
* `Solution.lean` — imports the development; `comparator.json` names the compared declarations.
* `{{LEAN_NAME}}/` — the development (`Defs` is shared byte-for-byte with `Challenge.lean`;
  `Cert` is generated from CAS transcripts by `tools/cert2lean.py`; never edit it by hand).
* `AxiomAudit.lean` + `Audit.lean` — the build fails unless every `{{LEAN_NAME}}.*` declaration uses
  only `propext`, `Classical.choice`, `Quot.sound`.
* `verification/logs/` — the build log, the comparator log and the exact versions of the last
  verification run (see `verification/README.md`).
* `scripts/verify-comparator.sh` — `lake comparator --paranoid` (six kernels).
* `demo/LiveDemo.lean` — the live demo (not a library target).

Toolchain: see `lean-toolchain`; Mathlib: the matching release tag in `lakefile.toml`. Palomar
requires Lean ≥ v4.35.0-rc2. The example declarations `R` and `R_simple` are placeholders that
mirror code that compiled in the skill's first use; build them once after scaffolding to check
the set-up, then replace them.

## Build and verify

```bash
MATHLIB_NO_CACHE_ON_UPDATE=1 lake update     # never without the variable
lake exe cache get Mathlib.Algebra.Field.Defs Mathlib.Tactic.LinearCombination   # module names
lake build                                   # includes the axiom audit
bash scripts/verify-comparator.sh            # SEM_NO_SANDBOX=1 only on hosts without bwrap
```

On a cluster, prefix each command with the driver: `tools/cluster.sh build`,
`tools/cluster.sh run 'SEM_NO_SANDBOX=1 bash scripts/verify-comparator.sh'`.

Add a `LICENSE` here before this directory becomes its own repository (a Palomar submission is a
public repository and a commit SHA).
