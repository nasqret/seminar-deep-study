#!/usr/bin/env python3
"""Turn CERT blocks printed by a computer algebra system into a Lean file of checked identities.

    python3 -I cert2lean.py TRANSCRIPT.out [...] [--namespace Proj.Cert] [--no-module] > Cert.lean

The CAS *finds* each identity; Lean *checks* it with `linear_combination` or `ring` when the
generated file is compiled. Nothing is trusted from the CAS: a wrong certificate fails to compile.
Never edit the generated file; change the CAS script and regenerate.

Block format (one field per line; text outside blocks, such as CHECK lines, is ignored):

    CERT <lean_name>
    KIND linear_combination          (default) or: ring
    VARS <v1> <v2> ...               variables, named as in Lean
    DOC <one line>                   optional docstring
    HYP <h> := <poly>                linear_combination: hypothesis  h : poly = 0  (repeatable)
    GOAL := <poly>                   linear_combination: the conclusion  poly = 0;
                                     a nonzero constant goal (e.g. 1) means the conclusion False
    COEF <h> := <poly>               linear_combination: the coefficient of h (missing = 0)
    EXP := <k>                       optional: linear_combination (exp := k), i.e. GOAL^k is in
                                     the ideal of the hypotheses (radical membership)
    LHS := <poly>                    ring: prove LHS = RHS by ring
    RHS := <poly>
    END

Polynomials use `+ - * / ^`, parentheses, integer and rational literals and the declared
variables only (this is checked, so no other Lean syntax can be injected). Magma, Sage, SymPy and
PARI print polynomials in this syntax; in Magma call SetColumns(0) so that long lines are not
wrapped.

The generated theorems are stated over any field of characteristic zero:
`{K : Type*} [Field K] [CharZero K]`, with the variables implicit for linear_combination
certificates (pass them by name when you apply a lemma to `by` blocks) and explicit for ring
identities.
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

IDENT = re.compile(r"[A-Za-z_][A-Za-z0-9_']*")
POLY_CHARS = re.compile(r"[A-Za-z0-9_'\s()+\-*/^]+")
NUMBER = re.compile(r"\s*-?\s*\d+(\s*/\s*\d+)?\s*")
FIELD = re.compile(r"^(HYP|COEF)\s+(\S+)\s*:=\s*(.*)$|^(GOAL|LHS|RHS|EXP)\s*:=\s*(.*)$")


class CertError(Exception):
    pass


def parse(paths: list[Path]) -> list[dict]:
    blocks, cur, where = [], None, ""
    for path in paths:
        for n, raw in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
            line = raw.strip()
            here = f"{path}:{n}"
            if cur is None:
                if line.startswith("CERT "):
                    name = line[5:].strip()
                    if not IDENT.fullmatch(name):
                        raise CertError(f"{here}: bad certificate name {name!r}")
                    cur = {"name": name, "kind": "linear_combination", "vars": [], "doc": "",
                           "hyps": [], "coefs": {}, "where": here}
                continue
            if line == "END":
                blocks.append(cur)
                cur = None
                continue
            if not line:
                continue
            if line.startswith("KIND "):
                cur["kind"] = line[5:].strip()
            elif line.startswith("VARS"):
                cur["vars"] = line[4:].split()
            elif line.startswith("DOC "):
                cur["doc"] = line[4:].strip()
            else:
                m = FIELD.match(line)
                if not m:
                    raise CertError(f"{here}: cannot read line {line!r}")
                if m.group(1) == "HYP":
                    cur["hyps"].append((m.group(2), m.group(3).strip()))
                elif m.group(1) == "COEF":
                    cur["coefs"][m.group(2)] = m.group(3).strip()
                else:
                    cur[m.group(4).lower()] = m.group(5).strip()
        if cur is not None:
            raise CertError(f"{cur['where']}: CERT {cur['name']} has no END")
    names = [b["name"] for b in blocks]
    dup = {x for x in names if names.count(x) > 1}
    if dup:
        raise CertError(f"duplicate certificate names: {', '.join(sorted(dup))}")
    return blocks


def check_poly(s: str, allowed: set[str], what: str) -> str:
    if not s or not POLY_CHARS.fullmatch(s):
        raise CertError(f"{what}: not a polynomial in the allowed syntax: {s[:80]!r}")
    for tok in IDENT.findall(s):
        if tok not in allowed:
            raise CertError(f"{what}: unknown identifier {tok!r} (declare it in VARS)")
    return " ".join(s.split())


def lean_doc(text: str) -> str:
    return text.replace("-/", "- /").replace("/-", "/ -")


def render(block: dict) -> str:
    name, kind, vars_ = block["name"], block["kind"], block["vars"]
    where = f"{block['where']} ({name})"
    for v in vars_:
        if not IDENT.fullmatch(v):
            raise CertError(f"{where}: bad variable name {v!r}")
    allowed = set(vars_)
    doc = f"/-- {lean_doc(block['doc'])} -/\n" if block["doc"] else ""
    if kind == "ring":
        lhs = check_poly(block.get("lhs", ""), allowed, f"{where} LHS")
        rhs = check_poly(block.get("rhs", ""), allowed, f"{where} RHS")
        binders = f" ({' '.join(vars_)} : K)" if vars_ else ""
        return f"{doc}theorem {name}{binders} :\n    {lhs} =\n      {rhs} := by\n  ring\n"
    if kind != "linear_combination":
        raise CertError(f"{where}: unknown KIND {kind!r} (linear_combination or ring)")
    if not block["hyps"]:
        raise CertError(f"{where}: a linear_combination certificate needs at least one HYP")
    goal = check_poly(block.get("goal", ""), allowed, f"{where} GOAL")
    hyp_names = [h for h, _ in block["hyps"]]
    for h in hyp_names:
        if not IDENT.fullmatch(h):
            raise CertError(f"{where}: bad hypothesis name {h!r}")
    unknown = set(block["coefs"]) - set(hyp_names)
    if unknown:
        raise CertError(f"{where}: COEF for unknown hypotheses {sorted(unknown)}")
    terms = [f"({check_poly(block['coefs'][h], allowed, f'{where} COEF {h}')}) * {h}"
             for h in hyp_names if h in block["coefs"]]
    if not terms:
        raise CertError(f"{where}: no COEF given")
    exp = block.get("exp")
    if exp is not None and not re.fullmatch(r"[1-9]\d*", exp):
        raise CertError(f"{where}: EXP must be a positive integer, got {exp!r}")
    lc = "linear_combination " + ("" if exp in (None, "1") else f"(exp := {exp}) ") + " + ".join(terms)
    binders = f" {{{' '.join(vars_)} : K}}" if vars_ else ""
    hyps = "".join(
        f"\n    ({h} : {check_poly(p, allowed, f'{where} HYP {h}')} = 0)" for h, p in block["hyps"])
    constant = NUMBER.fullmatch(goal) is not None
    if constant:
        if re.fullmatch(r"\s*-?\s*0+(\s*/\s*\d+)?\s*", goal):
            raise CertError(f"{where}: GOAL is zero, nothing to prove")
        body = (f"  have key : ({goal} : K) = 0 := by\n    {lc}\n  norm_num at key\n")
        return f"{doc}theorem {name}{binders}{hyps} :\n    False := by\n{body}"
    return f"{doc}theorem {name}{binders}{hyps} :\n    {goal} = 0 := by\n  {lc}\n"


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="CERT blocks -> Lean (checked by linear_combination/ring)")
    ap.add_argument("transcripts", nargs="+", type=Path)
    ap.add_argument("--namespace", default="Cert", help="Lean namespace (default: Cert)")
    ap.add_argument("--no-module", action="store_true",
                    help="plain imports instead of the module-system header")
    args = ap.parse_args(argv)
    if not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_']*(\.[A-Za-z_][A-Za-z0-9_']*)*", args.namespace):
        print(f"cert2lean: bad namespace {args.namespace!r}", file=sys.stderr)
        return 2
    try:
        blocks = parse(args.transcripts)
        if not blocks:
            raise CertError("no CERT blocks found")
        theorems = [render(b) for b in blocks]
    except (CertError, OSError) as exc:
        print(f"cert2lean: {exc}", file=sys.stderr)
        return 1
    sources = ", ".join(f"`{p.name}`" for p in args.transcripts)
    if args.no_module:
        header = "import Mathlib.Tactic.LinearCombination\nimport Mathlib.Tactic.Ring\n" \
                 "import Mathlib.Tactic.NormNum\n"
    else:
        header = "module\n\npublic import Mathlib.Tactic.LinearCombination\n" \
                 "public import Mathlib.Tactic.Ring\npublic import Mathlib.Tactic.NormNum\n\n" \
                 "@[expose] public section\n"
    out = [header,
           "set_option linter.unusedVariables false\nset_option linter.unusedSectionVars false\n",
           "/-!\n# Algebraic certificates (generated)\n\n"
           f"**Do not edit by hand.** Generated by `cert2lean.py` from {sources}.\n"
           "Each identity was *found* by a computer algebra system and is *checked* here by\n"
           "`linear_combination` or `ring`: a wrong certificate fails to compile.\n-/\n",
           f"namespace {args.namespace}\n",
           "variable {K : Type*} [Field K] [CharZero K]\n"]
    out += theorems
    out.append(f"end {args.namespace}\n")
    sys.stdout.write("\n".join(out))
    print(f"cert2lean: {len(blocks)} certificate(s) from {len(args.transcripts)} file(s)",
          file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
