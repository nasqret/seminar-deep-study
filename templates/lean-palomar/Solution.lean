module

public import {{LEAN_NAME}}

/-!
# Proved solution

The declarations named in `comparator.json` are proved in the development `{{LEAN_NAME}}`,
imported here. This module does not import `Challenge`. Comparator compares the types of the
advertised theorems and the definitions they use with the Mathlib-only `Challenge.lean`, then
checks the proofs with Lean's kernel and the toolchain's independent kernels, allowing only the
axioms `propext`, `Classical.choice` and `Quot.sound`.
-/
