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

# What is proved, what is assumed, and how it was checked

## The hypothesis register

| statement | in Lean | status | assumptions |
|---|---|---|---|
| Theorem … | `{{LEAN_NAME}}.…` | **proved** | … |
| Corollary … | `{{LEAN_NAME}}.…` | **proved with hypotheses** | Proposition … of the paper, as an explicit hypothesis |

## The last verification run

The verdicts are parsed from the committed logs of the last run (`formal/verification/logs/`).
The build stops here if the logs are missing or say something else than this page.

```{code-cell} ipython3
:tags: [hide-input]
import re, json, pathlib

REPO = next(p for p in [pathlib.Path.cwd(), *pathlib.Path.cwd().parents] if (p / "formal" / "Challenge.lean").exists())
LOGS = REPO / "formal" / "verification" / "logs"
assert LOGS.is_dir(), "run the verification first (formal/verification/README.md), then build the notes"
when, lean_version, mathlib_commit = (LOGS / "versions.txt").read_text().splitlines()[:3]
build = (LOGS / "build.log").read_text()
comp = (LOGS / "comparator.log").read_text()
audit = re.search(r"Axiom allowlist passed for (\d+) \S+ declarations: (.+)", build)
kernels = re.findall(r"(\S[^\n]*?) kernel accepts the solution", comp)
comparator = json.loads((REPO / "formal" / "comparator.json").read_text())
print(f"run: {when}\n{lean_version}\nMathlib {mathlib_commit[:12]}")
print(f"axiom audit: {audit.group(1)} declarations, allowed axioms: {audit.group(2)}")
print(f"kernels accepting the solution ({len(kernels)}):", ", ".join(kernels))
```

```{code-cell} ipython3
:tags: [remove-cell]
assert "build exit 0" in build and audit
assert audit.group(2).strip() == "propext, Classical.choice, Quot.sound"
assert sorted(comparator["permitted_axioms"]) == ["Classical.choice", "Quot.sound", "propext"]
assert "Your solution is okay!" in comp and "comparator exit 0" in comp
```

So the last run built every target, the axiom audit passed with only the three standard axioms,
and `lake comparator --paranoid` accepted the solution.
