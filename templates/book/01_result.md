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

# The result

State the main theorem as in the digest, §0, with its tag.

$$
\text{(the main statement)}
$$

The numbers below are computed here, at build time (never typed in).

```{code-cell} ipython3
# Example computation (replace): the discriminant of r^4 - 6r^2 - 3, from the formula for a
# biquadratic: for r^4 + p r^2 + q, disc = 16 q (p^2 - 4q)^2.
p, q = -6, -3
disc = 16 * q * (p * p - 4 * q) ** 2
print("discriminant:", disc)
```

```{code-cell} ipython3
:tags: [remove-cell]
# Guard: the sentence below states that the discriminant is nonzero (so the roots are simple).
# If a change makes it false, the build stops here instead of publishing a wrong sentence.
assert disc != 0, "the text claims the discriminant is nonzero"
```

The discriminant is nonzero, so the four roots are simple **[num]**; the same fact is proved in
Lean from a certificate **[Lean]**.
