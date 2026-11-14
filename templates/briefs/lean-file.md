# Brief: one Lean file

You are writing ONE Lean 4 file in an existing project: a complete, `sorry`-free
`formal/<Proj>/<File>.lean` in `<REPO>`. It is part of a formalization of <PAPER> (<format: light
| Palomar class: only the axioms propext, Classical.choice, Quot.sound; no `sorry`, no
`native_decide`, no new `axiom`; deep facts as explicit hypotheses>).

## Mathematics
<The statements to prove, in mathematical form, with the paper's numbering, the proof idea step by
step, and the certificates available in `<Proj>.Cert` (name → what it states).>

## Statements (fixed; do not change them)
```lean
<copy the exact statements, or the definitions they rely on, from Challenge.lean / Defs.lean>
```

## Environment (read carefully)
- Lean <VERSION> + Mathlib <VERSION>. <Local: `cd formal && lake env lean <Proj>/<File>.lean`. |
  Remote: there is NO local Lean; check the file with
  `SEM_CPUS=8 SEM_MEM=24G SEM_TIME=60 tools/cluster.sh lean <Proj>/<File>.lean` (it syncs
  `formal/` and runs on a compute node; silence = success; 1–3 minutes per check).>
- Its imports are already built: <list>. Do NOT run full builds, `lake update` or cache commands.
- Known traps: `references/traps.md` of the skill (module system: `omit … in` before docstrings,
  `import all` only in the audit; pass implicit arguments of certificate lemmas by name; prefer
  `obtain ⟨x, …, rfl⟩` to `set`; numerals in simp lemmas need `no_index`).

## Done means
The file elaborates with no errors and no warnings; `#print axioms` of each main statement shows
only the three standard axioms. Report the final statement names, the check output, and any
statement that turned out false or needed a hypothesis (with a counterexample if you have one):
that is a finding.
