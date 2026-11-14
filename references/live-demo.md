# Phase 5: the live demo

A live demo earns its minutes when it shows something the slides cannot: the checker accepting a
statement, a certificate being checked, an automation tactic finding a proof, and a broken variant
failing in front of the audience.

## 1. Where Lean runs during the talk

| option | needs | notes |
|---|---|---|
| local Lean and Mathlib | disk for the toolchain and the import closure | the most robust in the room; set it up days before |
| remote elaboration through the cluster driver | network (VPN off campus), the project built remotely | `tools/cluster.sh demo` sends the demo file to a compute node and prints all messages; a round trip of about 6 s in the first use |
| an editor over SSH | a compute node reachable by SSH | never run a Lean server on a cluster gateway |
| the rendered Verso document | nothing at talk time | static hovers and proof states; the fallback |
| screenshots of the outputs | nothing | the last resort; take them during the rehearsal |
| a web editor | network | its Mathlib version may differ from the project's; check every line beforehand |

## 2. The demo file

`templates/lean-palomar/demo/LiveDemo.lean` is the pattern. It is not part of any library target
and is checked on demand. Sections:
1. **What exactly is proved**: `#check @mainTheorem`, `#print` of the key definition (only
   Mathlib notions), `#print axioms mainTheorem` (only `propext`, `Classical.choice`,
   `Quot.sound`). Use `import all` so that `#print axioms` sees the proofs and not the proof-erased
   interface.
2. **The CAS finds, Lean checks**: one certificate from the transcript, checked by
   `linear_combination` (copy it from the generated file; never retype it).
3. **The same without a certificate**: the same statement proved by `grind`.
4. **Break it**: a commented-out variant that is false (for example, a polynomial with a double
   root in place of one with simple roots). Uncomment it, re-run, show the failure and the goal
   diagnostics, and comment it back.
5. **Where the hypothesis lives**: `#check` of the lemma that carries the main assumption (for
   example, the elimination showing where "for every parameter outside a finite set" comes from).

## 3. Rehearse

- Run the file twice on the day before the talk, from the room's network if possible, and time
  it.
- Put the command, the expected output, and what to say while it runs into the board plan.
- Keep the fallback open in a browser tab (the Verso page or the screenshots).
- If the demo is remote, check the VPN and the gateway login on the presentation laptop.

## 4. Other live moments

- A CAS one-liner that reproduces a number from the paper (a discriminant, a rank).
- A numeric screen that catches a deliberately introduced typo.
- For computer science: running the algorithm on a small input, an SMT query, a property-based
  test finding a counterexample to a weakened invariant.
