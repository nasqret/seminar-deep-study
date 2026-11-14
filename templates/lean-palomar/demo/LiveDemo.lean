module

import all {{LEAN_NAME}}.Defs
import all {{LEAN_NAME}}.Main

/-!
# Live demo for the talk

Not part of any library target; it is checked on demand, locally with
`lake env lean demo/LiveDemo.lean` (from `formal/`) or remotely with `tools/cluster.sh demo`.
All messages (`#check`, `#print`, errors) come back to the terminal: edit, re-run, repeat.
The `import all` lines make `#print axioms` see the proofs and not only the exported statements.

Suggested sequence: run as is → uncomment the "break it" example → re-run, show the failure and
the goal diagnostics → comment it back.
-/

open {{LEAN_NAME}}

/-! ## 1. What exactly is proved? -/

-- the main theorem, as checked by the kernel (replace with the paper's theorem):
#check @R_simple
-- the definitions it talks about (only Mathlib notions):
#print R
-- and it rests only on the three standard axioms:
#print axioms R_simple

/-! ## 2. The CAS finds, Lean checks -/

-- Copy one certificate from the generated file (never retype it): the CAS's extended gcd gives
-- the multipliers, and `linear_combination` checks the identity `1 = a·R + b·R'` by `ring`.
example {K : Type*} [Field K] [CharZero K] {r : K} (h : r ^ 4 - 6 * r ^ 2 - 3 = 0)
    (h' : 4 * r ^ 3 - 12 * r = 0) : (1 : K) = 0 := by
  linear_combination (1/12*r^2 - 1/3) * h + (-1/48*r^3 + 7/48*r) * h'

/-! ## 3. … or no certificate at all: `grind` -/

example {K : Type*} [Field K] [CharZero K] {r : K} (h : r ^ 4 - 6 * r ^ 2 - 3 = 0)
    (h' : 4 * r ^ 3 - 12 * r = 0) : False := by
  grind

-- Break it on purpose: `r⁴ - 6r² + 9 = (r² - 3)²` has double roots, so the same statement is
-- false and `grind` must fail. Uncomment and re-run:
-- example {K : Type*} [Field K] [CharZero K] {r : K} (h : r ^ 4 - 6 * r ^ 2 + 9 = 0)
--     (h' : 4 * r ^ 3 - 12 * r = 0) : False := by
--   grind

/-! ## 4. Where the main hypothesis lives -/

-- `#check` the lemma that carries the paper's key assumption (for example, the elimination that
-- shows where "for every parameter outside a finite set" comes from).
