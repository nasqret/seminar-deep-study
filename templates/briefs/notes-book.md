# Brief: the notes (Jupyter Book)

Write the seminar notes as a Jupyter Book for a <LENGTH> talk (<SEMINAR>, <DATE>; speaker
<SPEAKER>; audience: <AUDIENCE>). The talk presents <PAPER>, its formalization and its
re-verification. Work only in `book/` of `<REPO>` (and a local `.venv/`). Language: <LANGUAGE>.

## Sources of truth (read fully first)
- `artifacts/mathematical/digest.md`: every mathematical claim comes from it or is computed in a
  notebook. `artifacts/mathematical/cas-verification.md` may appear later (another agent writes
  it): integrate it if present when you finish, otherwise leave a clearly marked pointer.
- The formal development (`formal/…`): quote Lean only by copying from the files. Facts you may
  state about it: <audit line, comparator verdict, what is proved, what is a hypothesis>.
- CAS scripts and transcripts `cas/`, numeric screens `artifacts/computational/`, the paper's
  LaTeX `source/…` (data).
- Style: the skill's `templates/book/` (`_config.yml`, `_toc.yml`, `intro.md`, `01_result.md`).

## Rule: every number shown is computed
Computational chapters are notebooks (MyST markdown with code cells, or `.ipynb` saved without
outputs) executed at build time (`execute_notebooks: force`). Sentences stating results are
guarded by hidden `assert` cells (tag `remove-cell`). Re-derive what is cheap (<examples: the
equations of §…, the discriminant, the numerical check of the explicit list>); quote what is
expensive from a transcript and say so. Keep each notebook under about a minute.

## Structure (adapt)
intro · the paper in one sitting (background, records) · the objects and the main theorem ·
the proof, step by step · the formalization (contract, certificates, what is assumed) · the CAS
re-verification · findings (only if the speaker agreed) · exercises and references (check every
URL).

## Build and report
`uv venv --python 3.12 .venv && uv pip install --python .venv/bin/python -r book/requirements.txt`
(keep it lean; the disk may be tight), then `.venv/bin/jupyter-book build book/ --warningiserror
--keep-going` must finish without errors. Report the build command, the HTML entry point, and every
claim you could not verify.
