#!/usr/bin/env python3
"""Count tactic-name occurrences in the .lean files of a directory tree (a rough census).

Usage: python3 -I tactic_census.py <root> [<root> ...]

Use it when judging a candidate paper's Lean code ("which tactics carry these proofs?") or to
describe your own development in the talk. Comments (`--` line comments and nested `/- -/` block
comments, including docstrings) are stripped first; `.lake/` is skipped. The counts are tokens,
not tactic invocations: `show`, `have` and `calc` also occur in terms. Add names to TACTICS for
project-specific tactics. Also reports `sorry` and `native_decide` occurrences.
"""
import re
import sys
from collections import Counter
from pathlib import Path

TACTICS = [
    "simp", "simp_all", "simpa", "dsimp", "rw", "rwa", "erw", "exact", "apply", "refine",
    "intro", "intros", "rintro", "obtain", "rcases", "use", "constructor", "ext", "funext",
    "aesop", "aesop_cat", "grind", "ring", "ring_nf", "linear_combination", "field_simp",
    "omega", "linarith", "nlinarith", "positivity", "decide", "norm_num", "infer_instance",
    "inferInstanceAs", "exact?", "apply?", "fun_prop", "abel", "module", "algebraize",
    "tauto", "cases", "induction", "calc", "congr", "gcongr", "convert", "subst",
    "by_contra", "push_neg", "contrapose", "exfalso", "trivial", "rfl", "elementwise",
    "reassoc", "simp_rw", "nth_rw", "unfold", "change", "show", "have", "let", "set",
    "specialize", "split", "split_ifs", "by_cases", "choose", "lift", "norm_cast", "push_cast",
    "exact_mod_cast", "polyrith", "noncomm_ring", "compute_degree", "monicity", "bound",
    "field", "algebra", "module_nf", "push", "sorry", "native_decide", "nlinarith", "lia",
]

TOKEN = re.compile(r"(?<![A-Za-z0-9_.'])([A-Za-z_][A-Za-z0-9_']*\??)")


def strip_comments(src: str) -> str:
    # remove nested block comments /- ... -/ (including doc comments /-- -/ and /-! -/)
    out, depth, i = [], 0, 0
    while i < len(src):
        if src.startswith("/-", i):
            depth += 1
            i += 2
            continue
        if depth and src.startswith("-/", i):
            depth -= 1
            i += 2
            continue
        if not depth:
            out.append(src[i])
        i += 1
    text = "".join(out)
    return re.sub(r"--[^\n]*", "", text)


def census(root: Path) -> tuple[Counter, int, int]:
    counts: Counter = Counter()
    nfiles = nlines = 0
    for f in root.rglob("*.lean"):
        if ".lake" in f.parts:
            continue
        nfiles += 1
        src = f.read_text(encoding="utf-8", errors="replace")
        nlines += src.count("\n")
        for tok in TOKEN.findall(strip_comments(src)):
            if tok in TACTICS:
                counts[tok] += 1
    return counts, nfiles, nlines


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(2)
    for arg in sys.argv[1:]:
        c, nf, nl = census(Path(arg))
        print(f"== {arg}: {nf} files, {nl} lines")
        print("   " + "  ".join(f"{k}={v}" for k, v in c.most_common()))
