# SendMessage updates to running agents

Send one message per affected agent, tailored to its deliverable, whenever a fact changes. It
must be self-contained (the agent has no other channel), say where the evidence is, say exactly
what to add, and leave the agent's plan alone.

```
New verified result to add to <deliverable>: <what>, in <file> (<how it was checked: built on …,
audit now N declarations, #print axioms = [propext, Classical.choice, Quot.sound]>).
Please add <one slide / one section / one line / one note> "<title>", quoting only from <file>.
(Optional, keep your current plan.)
```

Examples of facts worth an update: a new theorem proved; a new module (and a changed audit count);
a new finding in the digest; a demo command that is ready and its measured timing; a change in
the library that requires the Verso document to re-sync before its final build.
