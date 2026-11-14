# Phase 4: materials, built by parallel subagents

Start the materials once the digest is stable (its claims tagged, its findings register started).
They are then written in parallel while you keep verifying.

## 1. Who writes what

| agent | owns | sources of truth | brief |
|---|---|---|---|
| CAS re-verification | `cas/` (new scripts), `artifacts/mathematical/cas-verification.md` | the paper's LaTeX, the digest | `templates/briefs/cas-verification.md` |
| Lean file (one per file) | `formal/<Proj>/<File>.lean` | `Challenge.lean`, the digest, the certificates | `templates/briefs/lean-file.md` |
| Verso document | `verso/` | the compiled library, the digest | `templates/briefs/verso.md` |
| Notes | `book/` (and a local `.venv/`) | the digest, the Lean files, the transcripts | `templates/briefs/notes-book.md` |
| Slides and board plan | `slides/` | the same | `templates/briefs/slides-board.md` |
| Landing page and vault | `index.html`, `assets/`, `scripts/generate_hero.py`, `vault/` | the same, plus the logs | `templates/briefs/landing-vault.md` |

You, the coordinator, own the digest, `PLAN.md`, `JOURNAL.md`, `MEMORY.md`, `CLAUDE.md`,
`MAINTENANCE.md`, `README.md` and all commits. Agents never commit.

## 2. Writing a brief

A subagent knows only its brief. Every brief states:
1. the goal, the audience and the talk (date, length, setup), the language;
2. the paper (citation) and the repository path;
3. **sources of truth, to be read fully first**, and the rule: every mathematical claim comes from
   them or is computed in the deliverable; Lean code is quoted only by copying from the files;
   numbers, names, dates, times and rooms are never invented ("to be announced" when unknown);
4. what it may write (its directory) and what it must not touch;
5. the environment: which tools exist locally, which commands run remotely, the disk situation,
   and a ban on `lake update`, full builds or installs outside its scope;
6. the quality bar: builds with warnings as errors, executed notebooks, screenshots checked;
7. what other agents are producing in parallel, and that a missing input gets a clearly marked
   placeholder ("pending: …");
8. the report it must return: files written, how to build, what it verified, what is pending.

## 3. While they run: updates with SendMessage

When a fact changes, send each running agent that is affected a short, self-contained message:

```
New verified result to add to <deliverable>: <what>, in <file> (<how it was checked>).
Please add <exactly what: one slide / one section / one line>, quoting only from <file>.
(Optional, keep your current plan.)
```

Send one message per agent, tailored to its deliverable, each time a fact changes: a new theorem
proved, a new finding, a count updated in the audit, a demo command ready. Do not ask them to
re-derive it.

## 4. When they finish

For each deliverable: build it yourself (book, Verso, slides), open it, take headless Chrome
screenshots (`--headless=new --screenshot`, with a throwaway `--user-data-dir`; the window must be
at least 500 px wide, so check a phone width with a 390 px iframe), check every number against the
digest and the logs, link the deliverables to each other (the landing page links all of them; the
slides link the notes; the notes link the Verso document), update `PLAN.md`, and commit.

**Agents are referees of the digest.** Materials agents re-derive numbers while they write. In
the first use, one of them caught a wrong constant in the digest itself. Ask every agent to
*report* a disagreement with the digest rather than silently "fixing" its own copy; then correct
the digest (with the date, and a line in the journal), and send the correction to every running
agent that quotes it.

**Watch the disk.** Several agents at once fill it quickly (uv caches, notebook outputs, browser
caches, vendored libraries). Check `df -h ~` while they run, and tell them the budget in the brief.

## 5. Deliverable notes

**Landing page / dashboard** (`templates/site/index.html`). It is the entry point and the status
board in one page. The hero image is **a result, not a drawing**: `scripts/generate_hero.py`
computes it from the paper's explicit data, asserts every fact the picture shows (counts,
degrees, symmetries), cross-checks it against the CAS transcript when one exists, and stops on
any failure; the "about the image" section says exactly what is drawn. Then: the title, speaker,
seminar, date, and time and room (or "to be announced"); cards for the digest, notes, slides,
formalization, Verso document and CAS scripts; boxed sections — the talk (abstract), the result
with a records table, the plan of the minutes, the verification status claim by claim (Lean / CAS
/ numerical columns), the Lean build evidence (lines quoted from the logs), the findings register
(only if the user agreed), how to reproduce, references (URLs checked), about the image. Use one
accent colour, and one colour per kind of computation (numerics, symbolic CAS, formal proof), the
same on the page, the slides and the notes. Fonts and MathJax load from a CDN; give system-font
fallbacks so that a local-only page works offline. `og:image` must be an absolute URL once
deployed.

**Slides** (`templates/slides/`): a reveal.js deck at a fixed 1280×720, **generated** from parts
(`slides/build/NN_*.html`) by `build/build.py`. Code on slides is only `{{SNIP:name}}`, located in
the repository files by text anchors, and the build refuses any code block that is not a verbatim
excerpt. Counts come from files (`{{COUNT:…}}`, `{{GREP:…}}`). Every section carries
`data-timing` (seconds); the build checks that the total equals the slot and writes minute marks
into the speaker notes and footers. Cues show what the speaker does: BOARD (which panel), LIVE
(with the command), OPTIONAL (skip when late), PENDING (waiting for another deliverable). The
libraries are vendored (`build/vendor.sh`: npm tarballs checked against their sha512 integrity),
so the deck works with no network; `build/check_render.sh` renders every slide in headless Chrome
and reports overflowing content and formulas wider than their column. The structure follows the
board plan: title; the result in three lines; background; the objects; the proof architecture
(one slide per step, the board taking the details); the formalization (statement as checked,
axioms, two routes); the CAS re-verification; findings (if agreed); live demo; outlook;
references.

**Board plan** (`templates/slides/build/board-plan.tpl.md` → `slides/board-plan.{md,html}` by
`build/boardplan.py`): the board panels (what is written where, when it is erased), the timeline
with minute marks taken from the deck, a computer run sheet with the live demo and the
no-network fallback, and a checklist for the day before. Printable on A4.

**Notes** (`templates/book/`, read its `README.md`): a Jupyter Book 1.x. Computational chapters
are notebooks stored without outputs and executed at every build (`execute_notebooks: force`,
`nb_execution_raise_on_error`), authored as MyST and converted with `jupytext --from myst --to
ipynb`. Every number the prose quotes is computed in a cell and guarded by a hidden `assert` cell
(`remove-cell`): in the first use, 13 notebooks carried 53 such guards, and a clean build with
`--warningiserror` took 42 s. Lean code enters only by `{literalinclude}` from `formal/`; the audit
count, the kernels and the comparator verdict are parsed from `formal/verification/logs/`. A shared
helper module (`seminar_lib.py`: the paper's objects transcribed once, high-precision numerics
with a recorded zero/nonzero gap, exact linear algebra) is imported by the notebooks with
`sys.dont_write_bytecode = True` and printed in full in an appendix. Citations come from
`references.bib`. Chapters: intro (results in three lines, a reading table with the minutes of the
talk), the paper in one sitting, one chapter per section of the paper with sub-notebooks, the
formalization (contract, proofs, certificates re-checked independently, `grind`, what is assumed),
the findings register (`register.md`, in the table of contents only once the user decides to
publish findings), exercises with computed answers, references, appendix.

**Verso document** (`templates/verso/`): see `references/lean-palomar.md`, section 10. Build it
where the library is built (on the cluster when Lean is remote), and check the generator's exit
status: it can exit non-zero after writing a site that looks complete.

**Obsidian vault** (`templates/vault/`): `Home.md` is the map of content. Folders: `Paper/` (one
note per statement of the paper), `Concepts/`, `People/` (authors and cited mathematicians, facts
from the sources only), `Formalization/` (module map, hypothesis register, certificate pipeline),
`Verification/`, `Findings/` (one note per row of the register, private until decided), `Talk/`,
`Decisions/` (one dated note per decision), `Project/`, `Tools/`, `Infrastructure/`. Every note
starts with a one-paragraph summary; wiki links generously; repository files by their path in
backticks (Obsidian links do not leave the vault). `.obsidian/app.json` and `core-plugins.json`
are part of the template; workspace files stay git-ignored. `vault/check_vault.py` reports broken
wiki links and orphans.

