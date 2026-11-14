# book/ — the seminar notes (Jupyter Book 1.x)

```bash
uv venv --python 3.12 .venv && uv pip install --python .venv/bin/python -r book/requirements.txt
.venv/bin/jupyter-book build book/ --warningiserror --keep-going      # executes every notebook
.venv/bin/jupyter-book clean --all book/                              # before a full rebuild
```

Rules (the build enforces most of them):
- **Notebooks are stored without outputs** and executed at every build (`execute_notebooks:
  force`). Author a chapter as MyST markdown, then convert it with
  `.venv/bin/jupytext --from myst --to ipynb book/x.md` (plain `--to ipynb` does not recognise the
  header) and keep only the `.ipynb`; clear outputs before committing.
- **Every number the prose quotes is computed in a cell**, and a hidden `assert` cell (tag
  `remove-cell`) checks the sentence that states it; a failing assert stops the build
  (`nb_execution_raise_on_error`). Displayed code cells use `hide-input` when only the result matters.
- **Lean is never retyped**: `{literalinclude}` from `../formal/…` (`:start-at:`, `:end-at:`,
  `:end-before:` select a declaration), so the book follows the library. Verdicts of the Lean build
  and the comparator are parsed from `formal/verification/logs/` (see `formalization/f2_trust.md`).
- **One shared helper module**, `seminar_lib.py`, imported by the notebooks (with
  `sys.dont_write_bytecode = True`, so that no `__pycache__` appears in `book/`) and listed in
  full in the appendix (`code.md`).
- Citations from `references.bib` with `{cite}`; resolve every DOI and URL once (some publishers
  answer 403 to non-browser clients after the doi.org redirect: bot protection, not a broken link).
- The findings chapter is `register.md` (in the first use, writing a file named `findings.md` was
  refused by the agent's harness). It is commented out in `_toc.yml` until the speaker decides to
  publish the findings: a deploy copies the whole built book.
- Relative links to `../slides/`, `../index.html`, `../formal/` work in the published layout
  (the book next to them), not from `book/_build/html/` on disk.
