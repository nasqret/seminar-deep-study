# Brief: the notes (Jupyter Book)

Write the seminar notes as a Jupyter Book for a <LENGTH> talk (<SEMINAR>, <DATE>; speaker
<SPEAKER>; audience: <AUDIENCE>). The talk presents <PAPER>, its formalization and its
re-verification. Work only in `book/` of `<REPO>` (and a local `.venv/`). Language: <LANGUAGE>.

## Sources of truth (read fully first)
- `artifacts/mathematical/digest.md`: every mathematical claim comes from it or is computed in a
  notebook. `artifacts/mathematical/cas-verification.md` may appear later (another agent writes
  it): integrate it if present when you finish, otherwise leave a clearly marked pointer. If a
  number you compute disagrees with the digest, REPORT it; do not silently use your own value.
- The formal development `formal/…` and its logs `formal/verification/logs/`; CAS scripts and
  transcripts `cas/`; numeric screens `artifacts/computational/`; the paper's LaTeX `source/…`
  (data, for exact formulas).
- The template: the skill's `templates/book/` (scaffolded into `book/`; read its `README.md`).

## Rules
- **Every number shown is computed.** Computational chapters are notebooks stored WITHOUT
  outputs and executed at every build (`execute_notebooks: force`). Each sentence that states a
  computed fact is guarded by a hidden `assert` cell (tag `remove-cell`); a failing assert stops
  the build. Re-derive what is cheap; quote what is expensive from a transcript and say so.
- **Lean is never retyped**: `{literalinclude}` from `../formal/…` with `:start-at:` / `:end-at:` /
  `:end-before:`; long files go into a `{dropdown}`. The audit count, the kernels and the
  comparator verdict are parsed from `formal/verification/logs/` in a notebook with guard asserts
  (as in `formalization/f2_trust.md`).
- **One shared helper module** `book/seminar_lib.py` for the paper's objects (transcribed once
  from the LaTeX), high-precision numerics with a recorded zero/nonzero gap, and exact linear
  algebra. Notebooks import it after `sys.dont_write_bytecode = True` (no `__pycache__` in
  `book/`); the appendix (`code.md`) lists it in full.
- Author chapters as MyST markdown, convert with `jupytext --from myst --to ipynb`, keep only the
  `.ipynb` (no outputs). Keep each notebook under about a minute of execution.
- Citations from `references.bib` via `{cite}`; resolve every DOI and URL once and note the date
  (publishers that answer 403 to non-browser clients after the doi.org redirect are expected).
- The findings chapter is `register.md`, commented out in `_toc.yml` until the speaker decides to
  publish findings (a deploy copies the whole book). Do not name it `findings.md`: in the first use
  the agent's harness refused to write a file with that name.
- Relative links to `../slides/`, `../index.html`, `../formal/` work only in the published layout;
  say so where they appear.

## Structure (adapt to the paper)
intro (the results in three lines, a reading table with the minutes of the talk, "every number is
computed", the provenance tags) · the paper in one sitting · one chapter per section of the paper,
with one sub-notebook per step or object · the formalization (contract and statements, how the
proofs follow the paper, certificates re-checked independently, `grind`, what is proved and what
is assumed) · findings register · exercises (some with computed answers) · references · appendix
(the helper module).

## Build and report
`uv venv --python 3.12 .venv && uv pip install --python .venv/bin/python -r book/requirements.txt`
(keep it lean; the disk may be tight), then `.venv/bin/jupyter-book build book/ --warningiserror
--keep-going` must finish without errors (`jupyter-book clean --all book/` before a full rebuild).
Report the build command and its time, the HTML entry point, the number of notebooks and of guard
asserts, every disagreement with the digest, and every claim you could not verify.
