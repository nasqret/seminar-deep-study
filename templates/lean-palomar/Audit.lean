module

import all {{LEAN_NAME}}
import all {{LEAN_NAME}}.Defs
import all {{LEAN_NAME}}.Main
meta import AxiomAudit

/-!
# Build-time axiom audit

Fails the build if any declaration of the namespace `{{LEAN_NAME}}` is an axiom or uses an axiom
other than `propext`, `Classical.choice`, `Quot.sound` (see `AxiomAudit.lean`). Every module is
imported with `import all`, so that the audit sees the implementation and not the proof-erased
public interface (in which theorems look like axioms). Add an `import all` line for every new
module of the development.
-/

#audit_project_axioms

-- the advertised results, as they are named in `comparator.json`
#check @{{LEAN_NAME}}.R_simple
