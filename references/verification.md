# Phase 3: verification (CAS, numerics, certificates)

The aim is that every computational claim of the paper is either re-done here or explicitly
tagged `[paper]`. A disagreement is a finding, not a nuisance.

## 1. The verification table

Before computing anything, list in `PLAN.md`:

| claim (paper ref) | method | script / Lean name | status |
|---|---|---|---|
| Thm 1.1 count | CAS + Lean | `cas/02_….m`, `Foo.ncard_…` | ⬜ |

Sources of rows: every number, list, matrix, rank, discriminant, factorization, count, every
"one checks", "clearly", "a computation shows", and every cited computation that the proof uses.

## 2. Numeric screens (cheap, first)

`artifacts/computational/check_*.py` evaluates the paper's explicit objects in high precision
(mpmath with 50 digits) to catch transcription errors in the paper or in your own transcription.
Examples: an explicit list of curves really lies on the surface; claimed intersection numbers;
the rank of a Gram matrix by exact rational elimination. State in the script's docstring that it
is a screen and where the exact verification lives. Run it with
`uv run --no-project --with mpmath python -I artifacts/computational/check_….py`.

## 3. CAS scripts and transcripts

Layout: `cas/NN_topic.<ext>` (or `magma/`, `sage/`), with transcripts in `cas/out/NN_topic.out`,
both committed. Conventions:
- the first lines say what is checked and which claim of the paper it serves;
- each check prints one line `CHECK <what>: true` and also asserts it, so that a failure stops
  the script;
- record the CAS version in the transcript (Magma: `GetVersion()`; Sage: `version()`);
- keep each script under a few minutes; split long ones;
- Magma wraps output at 80 columns unless the script starts with `SetColumns(0);`, and a wrapped
  polynomial breaks every parser downstream.

A CAS on a remote host needs a runner that uploads the script, runs it in batch mode with stdin
closed (otherwise an error leaves Magma waiting at its prompt forever), enforces a timeout,
recognizes errors in the text (Magma exits 0 even when a script fails; look for lines starting
with `>>`, `User error`, `Runtime error`), and returns a clean transcript.
`templates/cas/remote_run.sh` does this; configure it with `CAS_HOST` and `CAS_BIN`.

When the CAS disagrees with the paper: re-check your transcription first (the LaTeX source), then
the conventions (normalizations, signs, the field), then report it in the findings register with
the script that shows it.

## 4. Certificates: the CAS finds, Lean checks

A CAS can find an identity that proves a step (an ideal-membership representation, an extended
gcd, an elimination). Lean checks the identity by `linear_combination`, which reduces it to
`ring`. Nothing is trusted from the CAS: a wrong certificate fails to compile.

The pipeline:
1. The CAS script prints `CERT` blocks (format below) into its transcript.
2. `python3 "$SKILL/tools/cert2lean.py" cas/out/*.out --namespace <Proj>.Cert > formal/<Proj>/Cert.lean`.
3. Build. Never edit the generated file; change the script and regenerate.

The block format (one field per line; polynomials in the common syntax `* ^ / + -`, rational
literals, variables named as in Lean):

```
CERT R_simple
KIND linear_combination
VARS r
DOC R(r) = r^4 - 6r^2 - 3 has only simple roots.
HYP h := r^4 - 6*r^2 - 3
HYP h' := 4*r^3 - 12*r
GOAL := 1
COEF h := 1/12*r^2 - 1/3
COEF h' := -1/48*r^3 + 7/48*r
END
```

This becomes a theorem with hypotheses `h : r^4 - 6*r^2 - 3 = 0` and `h' : …`. If `GOAL` is a
nonzero constant, the conclusion is `False`; otherwise it is `GOAL = 0`. The proof is
`linear_combination (COEF h) * h + (COEF h') * h'`. `KIND ring` takes `LHS :=` and `RHS :=` and
proves `LHS = RHS` by `ring` (useful for expansions such as "the restriction of F to a line is
this binary form"). `examples/cert/sample.out` has one block of each kind.

Emitters: `templates/cas/cert_emit.m` (Magma) and `templates/cas/cert_emit.py` (SymPy) show how
to compute a certificate and print the block.

Keep certificates small: use a fixed basis (`IdealWithFixedBasis` and `Coordinates` in Magma);
eliminate variables that occur linearly before computing coordinates; take a resultant first and
certify the smaller identity. In the first use, one certificate shrank from 19 KB to 0.5 KB this
way.

## 5. The internal route: Lean's own automation

Lean's `grind` has a commutative-ring solver in the spirit of Gröbner-basis completion. It often
proves the same elimination steps with no external certificate. Showing both routes side by side
(a CAS certificate checked by `linear_combination`, and `grind` alone) is a strong moment in a
talk: both end in ordinary proof terms checked by the kernel. Other internal tools: `polyrith`
(asks an external service for the coefficients), `nlinarith` and `positivity` (Positivstellensatz-
style certificates), `decide` for finite checks (but `native_decide` is not allowed in a
Palomar-class development), `norm_num` for numerals.

## 6. The re-verification report

`artifacts/mathematical/cas-verification.md` lists each claim, the script, the result, and whether
it agrees with the paper, and points each disagreement to its row in the findings register. The
digest's tags point to this report.

