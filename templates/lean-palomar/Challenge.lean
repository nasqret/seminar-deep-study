module

public import Mathlib.Algebra.Field.Defs
public import Mathlib.Algebra.CharZero.Defs
public import Mathlib.Tactic.TypeStar

@[expose] public section

/-!
# {{PAPER}} — statements

Source: {{PAPER}}. This file is the audit surface: every definition used by an advertised
theorem is spelled out here (byte-identical to `{{LEAN_NAME}}/Defs.lean`), and every advertised
theorem is stated with a deliberate `sorry`. The proofs are in `Solution.lean`, which imports the
development `{{LEAN_NAME}}` and not this file; Comparator checks that names, types and
definitions agree. Mathlib-only imports.

## Conventions
State how the paper's objects are encoded (coordinates, points, lines, the base field), and every
divergence from the paper (for example: "over any algebraically closed field of characteristic
zero; ℂ is an instance").

## Advertised results
* `{{LEAN_NAME}}.R_simple` — example (replace with the paper's results, one bullet each, with
  the paper's numbering).
-/

namespace {{LEAN_NAME}}

variable {K : Type*} [Field K]

/-- Example: the quartic `R(r) = r⁴ - 6r² - 3`. -/
def R (r : K) : K := r ^ 4 - 6 * r ^ 2 - 3

/-- Example statement: `R` has only simple roots in characteristic zero. -/
theorem R_simple [CharZero K] {r : K} (h : R r = 0) (h' : 4 * r ^ 3 - 12 * r = 0) : False := by
  sorry

end {{LEAN_NAME}}
