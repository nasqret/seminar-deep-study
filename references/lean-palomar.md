# Lean formalization: light or Palomar-class

## 1. Choose the depth with the user

| depth | what it is | when |
|---|---|---|
| **light** | the main statements and the computational lemmas, proved where cheap; `sorry` allowed in drafts; a demo file | a talk with live Lean but little time |
| **Palomar-class** | complete proofs in the Palomar registry format, only the standard axioms, deep standard facts as explicit hypotheses, an axiom audit, `lake comparator` | when the formalization is itself part of the message ("control the paper's logic") |

Palomar (palomar-registry.org) registers formalizations in a fixed layout and judges them with
`lake comparator`, which ships with Lean toolchains from v4.35.0-rc2 on. The layout fits any
serious formalization, submitted or not.

## 2. The Palomar layout (templates in `templates/lean-palomar/`)

| file | role |
|---|---|
| `Challenge.lean` | the audit surface: imports Mathlib only; every definition an advertised theorem uses, spelled out; each advertised theorem stated with a deliberate `sorry` |
| `Solution.lean` | imports the development (not `Challenge`) |
| `<Proj>/Defs.lean` | the same definitions, byte-identical to `Challenge.lean` |
| `<Proj>/*.lean` | the development |
| `comparator.json` | `challenge_module`, `solution_module`, `theorem_names`, `definition_names`, `permitted_axioms` (`propext`, `Quot.sound`, `Classical.choice`), `enable_nanoda` |
| `formalization.yaml` | metadata, schema v0.4: project, sources (with `relationship: formalizes` and a note on what is and is not formalized), status and scope, automation (models, tools, cost), fidelity (every divergence from the paper), review, alignment (paper statement to Lean name) |
| `AxiomAudit.lean`, `Audit.lean` | the build-time axiom audit |
| `scripts/verify-comparator.sh` | runs `lake comparator --paranoid` with the toolchain's own kernels |
| `verification/logs/` | `versions.txt`, `build.log`, `comparator.log` of the last full run, and a README saying what to look for |
| `LICENSE` | at the project root of `formal/` (it may become its own repository) |

Rules of the contract: every `.lean` file starts with `module`; at most 10 000 lines per file;
`Challenge.lean` imports Mathlib only; only the three standard axioms; no `sorry` outside
`Challenge.lean`, no `native_decide`, no new `axiom`.

## 3. Statements first

1. Write `Challenge.lean` and `Defs.lean` before any proof, and have them elaborate with exactly
   the intended `sorry` warnings. Statements are the part a human must audit, so keep them short
   and in Mathlib's own vocabulary (`MvPolynomial`, `Submodule`, `finrank`, `Set.ncard`).
2. State in the generality that avoids heavy imports when the proof allows it. For example,
   "any algebraically closed field of characteristic zero" instead of ℂ, which avoids the whole
   analysis library; ℂ is an instance.
3. Advertise only the paper's results. By-products may live in the development and in the audit.

## 4. Deep facts as explicit hypotheses

Results that are standard but out of reach (Hodge theory, a cited classification, a bound from
another paper) enter as **parameters** of the theorem that uses them, never as axioms:

```lean
/-- **Corollary 4.2** of the paper. Its two deep inputs, Proposition 4.1 (a bound proved in a
cited paper) and Lemma 3.5 (a classification), enter as the explicit hypotheses `hBound` and
`hClass`. -/
theorem cor_4_2 (L : Lattice) (hBound : ∀ x ∈ L.roots, bound x) (hClass : classified L) :
    L.IsSaturated := by
```

Each hypothesis gets a docstring sentence saying what it is in the paper. List them under
`fidelity.divergences` in `formalization.yaml`, and in the digest. Formalizing an abstract
version can expose a hypothesis the paper uses silently; that is a finding (implicit hypothesis).

## 5. Building the development

- Split the work into files of one theme each, so that subagents can own one file each:
  definitions, the generated certificates, root counting, normal forms, families, the main count,
  lattice theory, and so on. Each subagent gets the exact check command, for example
  `tools/cluster.sh lean <Proj>/Spans.lean`, and the rule "no `sorry`, no `native_decide`, no
  `axiom`; do not run full builds".
- Certificates come from the CAS through `tools/cert2lean.py` (`references/verification.md`).
- Root counting over an algebraically closed field: a nonzero polynomial with only simple roots
  has `natDegree` distinct roots (`Polynomial.nodup_roots`, `IsAlgClosed.splits`,
  `Multiset.toFinset_card_of_nodup`). Simple roots follow from a Bezout certificate
  `a·p + b·p' = 1`.
- Build warning-free. Read linter warnings as possible mathematics: in the first use, the linter
  flagged an unused `[IsAlgClosed K]`, which showed that the classification of the objects holds
  over any field of characteristic zero (a strengthening), with algebraic closure needed only for
  the count.

## 6. The axiom audit

`AxiomAudit.lean` defines a command that walks every declaration whose name starts with the
project's namespace. It fails the build if a declaration is an `axiom`, is `unsafe` or `partial`,
or depends on an axiom other than `propext`, `Classical.choice`, `Quot.sound`; this catches
`sorryAx` and the `Lean.ofReduceBool` that `native_decide` introduces. `Audit.lean` imports every
module with **`import all`** and runs the command. A plain import exposes the proof-erased public
interface of each module, in which theorems look like axioms. Add the audit to the default build
targets so that it runs on every build.

## 7. The comparator

`scripts/verify-comparator.sh` checks that the toolchain has `lake`, `leanexport`,
`leanchecker`, `nanoda_bin` and `con-ron`. It writes the comparator configuration with the
external kernels and runs `lake comparator --paranoid`. The verdict comes from six kernels: Lean's
default and paranoid checkers, lean4lean, nanoda, con-leche and con-ron. Expect
`Your solution is okay!`. Palomar runs the comparator inside a `bwrap` sandbox. On a host without
bubblewrap, `SEM_NO_SANDBOX=1` adds `--inadvisably-no-sandbox`, which is acceptable for checking
your own project, never for judging untrusted code.

## 8. Verification logs

After the last change of a session, regenerate `verification/logs/`: the UTC time, the
`lean --version` output and the Mathlib commit actually checked out (`versions.txt`); the full
build (`build.log`, ending with `build exit 0`); the comparator (`comparator.log`, ending with
`comparator exit 0`). Numbers on the landing page (declarations audited, kernels) are copied from
these logs.

## 9. Submitting to Palomar (only when the user decides)

1. The user reviews the statements in `Challenge.lean` against the paper and fills `review` in
   `formalization.yaml`.
2. `formal/` becomes its own public repository (LICENSE at its root).
3. The full commit SHA is submitted at palomar-registry.org/how-to-submit; Palomar's CI runs the
   sandboxed comparator.

## 10. The Verso document (optional)

A Verso document compiled against the library turns the formalization into a readable,
self-checking text. It is a separate Lake project that depends on `../formal` by path and uses
the same toolchain and Mathlib (its setup hard-links the formalization's package builds, so
Mathlib is not downloaded twice). Templates: `templates/verso/`; brief: `templates/briefs/verso.md`.

A structure that worked: Part I rewrites the paper, each result next to its formal statement (or
"not formalized, because …"); Part II explains the formalization (an architecture table computed
from the sources, the Palomar contract quoted from disk, certificates versus `grind`, a guided
tour of the key proofs); Part III is the correctness control (the hypothesis register,
`#print axioms` with checked outputs, the project's axiom audit run inside the document, the
comparator log read from disk, a claim-by-claim table); Part IV is the findings register, if the
user decided to publish it.

The control mechanisms, all of them build errors when they fail:
- `signature` blocks are compared with the compiled declarations;
- `{docstring X}` renders a declaration with its docstring from the library (a missing docstring
  is a warning: add it in the library instead of silencing it);
- `lean` blocks are re-elaborated and `leanOutput` must match Lean's actual message;
- `libcode` blocks (`templates/verso/Doc/Meta.lean`) must be verbatim excerpts of the library,
  are re-elaborated, and are shown by `rfl` to prove exactly the library's statement;
  `scripts/refresh_excerpts.py` refreshes them when the library changes;
- `{sourceFile "FILE" (from := …) (to := …)}` quotes files read at build time;
  `{moduleTable}` computes the module table from the sources.

Hazards: commit `lake-manifest.json` (a laptop-to-cluster sync with `rsync --delete` deletes a
manifest that exists only remotely); Verso's literate whole-module loader unsets `ELAN_HOME` (on
a cluster with a full home it would install a toolchain there), so use excerpt checks instead;
statements that depend on a classical `DecidableEq` render reliably only through docstring boxes;
the single-page HTML opens from `file://`, the multi-page site needs a web server. A rebuild of
the document took about a minute on 16 CPUs in the first use.
