module

public meta import Lean

public meta section

/-!
# Axiom audit (build-time inspection only)

`#audit_project_axioms` walks every declaration of the namespace `{{LEAN_NAME}}` in the current
environment and fails the build if any of them is an `axiom`, is `unsafe` or `partial`, or depends
transitively on an axiom other than `propext`, `Classical.choice`, `Quot.sound` (so no `sorryAx`,
and no `Lean.ofReduceBool` from `native_decide`). It supplies no mathematics. Run by `Audit.lean`.
-/

open Lean Elab Command

elab "#audit_project_axioms" : command => do
  let env ← getEnv
  let allowed : Array Name := #[`propext, `Classical.choice, `Quot.sound]
  let mut checked : Nat := 0
  for (name, ci) in env.constants.toList do
    if name.toString.startsWith "{{LEAN_NAME}}." then
      if ci.isUnsafe || ci.isPartial then
        throwError "Unsafe or partial project declaration: {name}"
      match ci with
      | .axiomInfo _ => throwError "Project axiom declaration: {name}"
      | _ => pure ()
      for ax in (← collectAxioms name) do
        unless allowed.contains ax do
          throwError "Unexpected axiom {ax} in {name}"
      checked := checked + 1
  if checked == 0 then
    throwError "Axiom audit found no {{LEAN_NAME}} declarations"
  logInfo m!"Axiom allowlist passed for {checked} {{LEAN_NAME}} declarations: \
    propext, Classical.choice, Quot.sound"
