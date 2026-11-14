# The computer-science reading of the phases

The method is the same: choose with evidence, rewrite the paper as a digest with status tags,
re-do what can be re-done, formalize what carries the argument, and record findings. Only the
tools and the kinds of claims change.

## Phase 1: where to look

- arXiv `cs.*` listings (for example `cs.LO`, `cs.PL`, `cs.DS`, `cs.CC`, `cs.CR`, `cs.LG`,
  `cs.AI`). The scanner takes any categories in its profile.
- Proceedings and their artifact tracks (artifact-evaluation badges mean the code exists and was
  run by someone else), DBLP for an author's record, and the paper's repository (GitHub, Zenodo,
  Software Heritage).
- Criteria to add: is there an artifact (code, data, container)? Can a small instance run in
  seconds for a live demo? Is there a theorem whose proof is short enough to formalize?

## Phase 2: the digest's claim types

| claim | tag after checking | how |
|---|---|---|
| a theorem (correctness, a bound, an impossibility) | `[Lean]` or `[paper]` | formalize the key lemma or invariant |
| an algorithm (pseudocode) | `[exp]` | implement it or run the artifact; property-based tests against a reference |
| a complexity claim | `[exp]` plus `[paper]` | scaling experiments (fit the exponent on a log-log plot), adversarial inputs; never a proof by plot |
| an experiment (tables, figures) | `[exp]` | re-run with the recorded environment; compare within the reported variance |
| a decision-procedure result | `[SMT]` | re-run the solver and check its certificate (DRAT or LRAT proofs, unsat cores, models) |

Findings typical of CS papers: pseudocode that differs from the artifact, an off-by-one in a loop
bound, a complexity claim that holds only on average, results that depend on an unreported seed
or machine, a benchmark subset that differs from the one described.

## Phase 3: verification tools

- **Re-running artifacts**: a container or a Nix shell; record the commit, the hardware, the
  seeds and the wall time; keep raw outputs in `artifacts/computational/` and a script that
  rebuilds every table and plot.
- **Property-based testing** (Hypothesis, QuickCheck) against a naive reference implementation:
  cheap and very effective at finding wrong invariants.
- **SMT and model checking**: Z3 or cvc5 for arithmetic and bit-vector claims; TLA+ or Alloy for
  protocol invariants on small instances.
- **Lean 4**: functional implementations with correctness proofs, `decide` for finite cases,
  `omega` for linear integer arithmetic, `grind` for algebraic and congruence reasoning. The
  Palomar format and its axiom discipline apply unchanged to mathematical statements about
  algorithms. Note that `native_decide` is not allowed there.
- **Certificates**: the same idea as in mathematics. An untrusted solver finds, a small checker
  verifies (SAT proofs checked by a verified checker, certificates of optimality, witnesses).

## Phases 4–5: materials and demo

Same deliverables. Good live moments: the algorithm on a small input with a visualization; an SMT
query that finds a counterexample to a weakened invariant; a property-based test shrinking a
failing case; a Lean `#eval` next to the theorem about the function evaluated.

## Scenarios

- *An algorithms paper with a new bound*: formalize the potential-function lemma in Lean; run the
  implementation on adversarial families; plot the scaling; record where the constant hides.
- *A programming-languages paper*: mechanize the progress and preservation lemmas for the core
  calculus; run the artifact's test suite; check the paper's examples against the
  implementation.
- *A cryptography or protocol paper*: model the protocol in TLA+ for small parameters; check
  algebraic identities with a CAS and Lean certificates; re-run the benchmarks.
- *A machine-learning theory paper*: check the inequalities symbolically and numerically; re-run
  the small experiments; formalize the key lemma when it is elementary.
