# Briefs for materials and verification agents

Fill a brief, launch one background agent per deliverable, and keep each agent inside its own
directory. A subagent knows only its brief: give it the goal, the sources of truth, the facts it
may state, the commands it may run, what to return, and what other agents are doing at the same
time. Every brief keeps these rules:

- read the sources of truth fully before writing anything;
- every mathematical claim comes from them or is computed in the deliverable;
- Lean code is quoted only by copying it from the library files;
- numbers, names, dates, times and rooms are never invented ("to be announced" when unknown);
- write only in your own directory; never commit, push, deploy or publish;
- no `lake update`, no full builds and no installs outside the brief's scope; respect the disk;
- end with a report: files written, how to build or open them, what was verified, what is
  pending, and anything that could not be verified.

| brief | deliverable |
|---|---|
| `cas-verification.md` | independent CAS re-verification of the paper's computational claims |
| `lean-file.md` | one Lean file of the development |
| `verso.md` | the Verso document |
| `notes-book.md` | the notes as a Jupyter Book |
| `slides-board.md` | the slides and the board plan |
| `landing-vault.md` | the landing page / dashboard, the computed hero image and the vault |
| `update-message.md` | SendMessage updates to running agents |
