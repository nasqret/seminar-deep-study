---
jupytext:
  text_representation:
    extension: .md
    format_name: myst
kernelspec:
  display_name: Python 3
  language: python
  name: python3
---

# The paper in one sitting

The context, the theorems as stated in the paper (with its numbering), and a map of the proofs
that the next chapters follow. Every claim carries its tag.

```{code-cell} ipython3
import sys, pathlib

BOOK = next(p for p in [pathlib.Path.cwd(), *pathlib.Path.cwd().parents] if (p / "seminar_lib.py").exists())
sys.path.insert(0, str(BOOK))
sys.dont_write_bytecode = True   # keep book/ free of __pycache__
import seminar_lib as lib        # shared helpers of these notes, listed in the appendix

# Example computation (replace): the discriminant of r^4 - 6r^2 - 3 from the formula for a
# biquadratic r^4 + p r^2 + q, namely 16 q (p^2 - 4q)^2.
p, q = -6, -3
disc = 16 * q * (p * p - 4 * q) ** 2
print("discriminant:", disc)
```

```{code-cell} ipython3
:tags: [remove-cell]
# Guard: the sentence below says the discriminant is nonzero. If a change makes that false, the
# build stops here instead of publishing a wrong sentence.
assert disc != 0
```

The discriminant is nonzero, so the four roots are simple **[num]**; the same fact is proved in
Lean from a certificate **[Lean]** (see {doc}`formalization/f1_contract`).
