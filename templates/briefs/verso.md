# Brief: the Verso document

Build a Verso document that presents and *controls* the Lean formalization of <PAPER>, for the
speaker's seminar. Work only in `verso/` of `<REPO>` (a new Lake project that depends on `../formal`
by path); put the build instructions in `verso/README.md`.

## What exists
- `formal/`: Lean <VERSION> + Mathlib <VERSION>, library `<Proj>` (<module list and what each
  proves>), `Challenge.lean`, `Solution.lean`, `comparator.json`, `formalization.yaml`,
  `verification/logs/`. The full build succeeds; the audit and the comparator pass.
- The digest `artifacts/mathematical/digest.md` (the mathematics and the findings register).
- Templates: the skill's `templates/verso/` (lakefile pinned to the Verso tag matching the
  toolchain, `DocMain.lean`, `Doc/Render.lean`, `scripts/remote-setup.sh`, `scripts/remote-build.sh`).

## What the document must do
- Part I: the paper in order; next to each result its formal statement as a `signature` block
  (compared with the library at build time) or the sentence "not formalized, because …".
- Part II: the formalization: architecture, the Palomar contract (read `Challenge.lean` and
  `comparator.json` from disk at build time, not transcribed), how certificates enter, a guided
  tour of the key proofs (verbatim excerpts of the library, re-elaborated).
- Part III: correctness control: what is proved and what is assumed (the explicit hypotheses),
  `#print axioms` with `leanOutput` checked, the audit and comparator logs read from disk, a
  claim-by-claim status table.
- Part IV: the findings register, only if the speaker decided to publish it.

## Control mechanisms to use
`signature` blocks; `{docstring X}` (add missing docstrings in the library, do not silence the
warning); `lean` + `leanOutput` blocks; `libcode` verbatim excerpts after a hidden `lean -show`
block that opens a tour namespace with the library file's variables, followed by an `rfl` check
against the library statement; `{sourceFile}` for files read at build time; `{moduleTable}`.
Helpers: `templates/verso/Doc/Meta.lean`; excerpt refresher: `scripts/refresh_excerpts.py`.
Statements depending on a classical `DecidableEq`: show them with `{docstring}`.

## Environment
<Where `formal/` is built; how to run: e.g. `tools/cluster.sh run 'cd ../verso && bash scripts/remote-setup.sh'`
then `… remote-build.sh`; fetch `_out/` with `tools/cluster.sh fetch verso/_out`.> Never download
Mathlib a second time (the setup script hard-links the formalization's packages). Fetch the
`lake-manifest.json` written by `lake update` back at once and commit it (the next sync deletes
remote-only files). Do not use Verso's literate whole-module loader where `ELAN_HOME` matters.
Check the generator's exit status.

## Report
The build command and its result, the HTML entry points (`_out/html-multi/index.html`,
`_out/html-single/index.html`), what the build checks, and what is pending.
