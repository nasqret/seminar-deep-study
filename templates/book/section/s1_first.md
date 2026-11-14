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

# Step 1: <name>

The statement, the idea, then the computation.

```{code-cell} ipython3
:tags: [hide-input]
import sys, pathlib

BOOK = next(p for p in [pathlib.Path.cwd(), *pathlib.Path.cwd().parents] if (p / "seminar_lib.py").exists())
sys.path.insert(0, str(BOOK))
sys.dont_write_bytecode = True
import seminar_lib as lib
from fractions import Fraction

# Example (replace): the rank of an intersection matrix, exactly over Q.
M = [[-3, 1, 1], [1, -3, 1], [1, 1, -3]]
rank = lib.rank_exact(M)
print("rank:", rank, " det:", lib.det_exact(M))
```

```{code-cell} ipython3
:tags: [remove-cell]
assert rank == 3          # the sentence below states the rank
```

The matrix has full rank **[num]**.
