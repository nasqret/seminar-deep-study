// Emitting CERT blocks from Magma for tools/cert2lean.py (format: see its docstring).
// Magma FINDS the identity; Lean CHECKS it with linear_combination. Run in batch mode, e.g.
//   tools/remote_run.sh cas/02_certs.m --timeout 1200 > cas/out/02_certs.out
SetColumns(0);   // never wrap long polynomials: a wrapped line breaks the parser
printf "MAGMA %o\n", GetVersion();

// One linear_combination certificate: hyps[i] = 0 for all i implies goal = 0, because
// goal = &+[ coefs[i] * hyps[i] ] (checked below before printing).
procedure EmitLC(name, vars, doc, hnames, hyps, goal, coefs)
  assert goal eq &+[ coefs[i] * hyps[i] : i in [1..#hyps] ];
  printf "CERT %o\nKIND linear_combination\nVARS %o\nDOC %o\n", name, &cat[ v cat " " : v in vars ], doc;
  for i in [1..#hyps] do printf "HYP %o := %o\n", hnames[i], hyps[i]; end for;
  printf "GOAL := %o\n", goal;
  for i in [1..#hyps] do printf "COEF %o := %o\n", hnames[i], coefs[i]; end for;
  printf "END\n";
end procedure;

// Example 1 (univariate): R has only simple roots, from the extended gcd 1 = a R + b R'.
P<r> := PolynomialRing(Rationals());
R := r^4 - 6*r^2 - 3;
g, a, b := XGCD(R, Derivative(R));
assert g eq 1;
printf "CHECK gcd(R, R') = 1: %o\n", g eq 1;
EmitLC("R_simple", ["r"], "R(r) = r^4 - 6r^2 - 3 has only simple roots.",
       ["h", "h'"], [R, Derivative(R)], P!1, [a, b]);

// Example 2 (multivariate, ideal membership with a fixed basis):
// Coordinates needs an ideal created by IdealWithFixedBasis. Eliminate variables that occur
// linearly first, or certify a resultant: raw coordinates can be huge.
Q<x, y> := PolynomialRing(Rationals(), 2);
I := IdealWithFixedBasis([x - y]);
f := x^2 - y^2;
assert f in I;
c := Coordinates(I, f);
printf "CHECK x^2 - y^2 in (x - y): true\n";
EmitLC("sq_eq_of_eq", ["x", "y"], "If x = y then x^2 = y^2.", ["h"], [x - y], f, c);
quit;
