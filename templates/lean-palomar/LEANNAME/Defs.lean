module

public import Mathlib.Algebra.Field.Defs
public import Mathlib.Tactic.TypeStar

@[expose] public section

/-!
# Definitions shared with `Challenge.lean`

Every definition that an advertised theorem uses lives here and is repeated **byte-identically**
in `Challenge.lean`; Comparator checks that the two agree. Use Mathlib's own vocabulary
(`MvPolynomial`, `Submodule`, `Module.finrank`, `Set.ncard`, …) so that a reader can audit the
statements without reading the development.

The example below (a quartic with simple roots) is a placeholder: replace it with the paper's
objects.
-/

namespace {{LEAN_NAME}}

variable {K : Type*} [Field K]

/-- Example: the quartic `R(r) = r⁴ - 6r² - 3`. -/
def R (r : K) : K := r ^ 4 - 6 * r ^ 2 - 3

end {{LEAN_NAME}}
