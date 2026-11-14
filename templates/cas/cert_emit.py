"""Emitting CERT blocks from SymPy for tools/cert2lean.py (format: see its docstring).

SymPy FINDS the identity; Lean CHECKS it with linear_combination.

    uv run --no-project --with sympy python -I cert_emit.py > cas/out/02_certs.out
"""
import sympy as sp


def emit_lc(name, vars_, doc, hnames, hyps, goal, coefs):
    """hyps[i] = 0 for all i implies goal = 0, since goal = sum coefs[i] * hyps[i]."""
    assert sp.expand(goal - sum(c * h for c, h in zip(coefs, hyps))) == 0, name
    fmt = lambda e: str(sp.expand(e)).replace("**", "^")  # noqa: E731 - Lean uses ^
    print(f"CERT {name}\nKIND linear_combination\nVARS {' '.join(vars_)}\nDOC {doc}")
    for h, p in zip(hnames, hyps):
        print(f"HYP {h} := {fmt(p)}")
    print(f"GOAL := {fmt(goal)}")
    for h, c in zip(hnames, coefs):
        print(f"COEF {h} := {fmt(c)}")
    print("END")


r = sp.symbols("r")
R = r**4 - 6 * r**2 - 3
a, b, g = sp.gcdex(R, sp.diff(R, r))          # a*R + b*R' = g
assert g == 1
print("CHECK gcd(R, R') = 1: true")
emit_lc("R_simple", ["r"], "R(r) = r^4 - 6r^2 - 3 has only simple roots.",
        ["h", "h'"], [R, sp.diff(R, r)], sp.Integer(1), [a, b])

x, y = sp.symbols("x y")
G = sp.groebner([x - y], x, y, order="lex")
q, rem = sp.reduced(x**2 - y**2, list(G.exprs), x, y, order="lex")
assert rem == 0 and list(G.exprs) == [x - y]
print("CHECK x^2 - y^2 in (x - y): true")
emit_lc("sq_eq_of_eq", ["x", "y"], "If x = y then x^2 = y^2.", ["h"], [x - y], x**2 - y**2, q)
