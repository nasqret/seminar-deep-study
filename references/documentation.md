# Phase 6: project documentation and the end-of-session routine

The project must be resumable by a fresh session, or by the user alone, without reading the
conversation. Templates are in `templates/project/`; `tools/scaffold.py` copies them.

## 1. The files

| file | content | rule |
|---|---|---|
| `CLAUDE.md` | operating instructions: what to read at the start of a session, hard rules, layout, known traps, the end-of-session routine | short; hard rules first; every trap found the hard way is added the same day |
| `MEMORY.md` | durable facts and decisions, each dated | "if the user says otherwise now, the user wins": update the entry and keep the date of the change |
| `JOURNAL.md` | dated entries, newest first: requests (verbatim where they are a contract), candidates considered, what was done, incidents, what is open | appended at the end of every session |
| `PLAN.md` | status tables: ✅ done · 🟡 in progress · ⬜ to do · ❓ user's decision | every ❓ names the decision needed |
| `MAINTENANCE.md` | the runbook: environment, every command to build, check, verify, deploy | commands copy-pasteable, with expected outputs |
| `README.md` | what is here and where to start | for a colleague who finds the repository |
| `source/SOURCE.md` | citation, version, checksums | the source files themselves are not committed |
| `vault/` | the knowledge base (Obsidian) | one note per concept or decision |

`CLAUDE.md` should start with "Read `MEMORY.md`, the top entry of `JOURNAL.md`, then `PLAN.md`;
skim `vault/Home.md`; the mathematical source of truth is the digest."

## 2. Client memory

The client's own memory directory (outside the project) keeps only facts that should outlive the
project: the user's infrastructure, standing preferences ("prefers Magma"; "no local Mathlib"),
and pointers to the project. Write one file per topic and an index line for each. Update it only
with facts the user stated or confirmed, and only when the user wants persistent memory.

## 3. End of every session

1. Append a dated entry to `JOURNAL.md`: requests, what was done, incidents, what is open.
2. Update `PLAN.md` statuses and ❓ items.
3. Add or adjust vault notes for new concepts, decisions and findings.
4. If the formalization changed, regenerate `verification/logs/`.
5. Check that every number on the page and the slides still matches the logs and transcripts.
6. Commit with Conventional Commits in English (`feat(formal): …`, `docs(digest): …`,
   `chore: …`), with the attribution line your client requires.

## 4. Commits

- Small commits per deliverable and per verified result; the journal names them.
- Never commit `source/*.pdf`, `source/*.tex`, `.lake/`, `_remote/`, `book/_build/`, `.venv/`,
  `verso/_out/`, `.DS_Store`, or Obsidian workspace files (the template `.gitignore` covers them).
- Before any push, check the remote's visibility. Findings and unpublished material go only to
  private remotes unless the user decides otherwise.
