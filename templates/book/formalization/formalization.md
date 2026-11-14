# The formalization

The core of the paper is formalized in Lean 4 with Mathlib, in the format of the
[Palomar registry](https://palomar-registry.org/). The development lives in `formal/` of the
project repository.

| paper | Lean | status |
|---|---|---|
| Theorem … | `{{LEAN_NAME}}.…` | proved / proved with explicit hypotheses / not formalized (recomputed instead) |

The toolchain and the Mathlib version are pinned in the repository (read at build time):

```{literalinclude} ../../formal/lean-toolchain
:language: text
```

```{literalinclude} ../../formal/lakefile.toml
:language: toml
:start-at: "[[require]]"
:end-at: rev =
```

```{rubric} Sections
```

```{tableofcontents}
```
