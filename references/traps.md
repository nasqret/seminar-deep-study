# Known traps (each one was hit in practice)

Add a trap to the project's `CLAUDE.md` the day you hit it, and to this file when it is general.

## Disk, Lake and Mathlib

- `lake update` in a Mathlib project runs Mathlib's post-update hook, which downloads the
  **entire** cache. Always `MATHLIB_NO_CACHE_ON_UPDATE=1 lake update`. In the first use it filled
  the disk in one command.
- `lake exe cache get Mathlib/X.lean` fails in a downstream project, because paths are resolved
  against the project root. Use module names: `lake exe cache get Mathlib.X`.
- Running `lake` inside another Lean project makes elan download that project's pinned toolchain
  (gigabytes). Never do it in the user's other projects.
- On clusters, home quotas count bytes and files. Put `ELAN_HOME`, `XDG_CACHE_HOME` and
  `MATHLIB_CACHE_DIR` under the project's work directory.
- The cluster may lack `bubblewrap`; `lake comparator` then needs `--inadvisably-no-sandbox`
  (acceptable for your own project only).

## The Lean module system

- Every file of a Palomar-class development starts with `module`; definitions meant to be seen
  need `public import` and `@[expose] public section`.
- An axiom audit must use `import all` for each module. Plain imports expose proof-erased
  interfaces, in which every theorem looks like an axiom.
- `omit [Inst] in` must come **before** a declaration's docstring, not between the docstring and
  `theorem`.
- Metaprograms used at build time need `meta import` (and `public meta import Lean` in the audit
  file).

## Lean and Mathlib in proofs

- `ring` is not imported by `Mathlib.Tactic.LinearCombination`; import `Mathlib.Tactic.Ring`.
- A simp lemma about numerals needs `no_index (OfNat.ofNat n)` on the left-hand side.
- `set x := e` also rewrites `e` inside hypotheses, after which `field_simp` cannot see `e ≠ 0`.
  Prefer reparametrizing with `obtain ⟨x, …, rfl⟩ : ∃ x, … := ⟨…, by field_simp⟩`.
- Implicit arguments of certificate lemmas used as `foo (by …) (by …)` stay metavariables; pass
  them by name: `foo (x := a) (t := t) …`.
- A `Finset` built in a file with `open scoped Classical` carries the classical `DecidableEq`.
  Restating its membership over ℚ picks `instDecidableEqRat`, and the two instances clash ("type
  mismatch … Classical.propDecidable"). State such lemmas about the underlying `Multiset` (for
  example `p.roots = 0`) instead of `p.roots.toFinset`.
- Deprecations move: in recent Mathlib, `push_neg` became `push Not`; check the deprecation
  warnings of the pinned version and fix them, since a warning-free build is part of the bar.
- `compute_degree!` can close the goal itself; a following tactic then fails with "no goals".
- `native_decide` adds the axiom `Lean.ofReduceBool`; it is not allowed in a Palomar-class
  development.

## CAS

- Magma wraps output lines at 80 columns unless the script calls `SetColumns(0)`; wrapped
  polynomials break the certificate parser.
- Magma exits with status 0 even when the script fails; detect errors in the text.
- In batch mode with stdin open, an error leaves Magma at its interactive prompt forever; run it
  with stdin closed (`ssh -n`).
- `Coordinates(I, f)` in Magma needs an ideal created with `IdealWithFixedBasis`. Raw coordinates
  can be huge: eliminate the variables that occur linearly first, or certify a resultant.
- `Evaluate` between polynomial rings over different base rings fails; build objects directly
  over the target ring (for example, a reduction mod p defined over the finite field from the
  start).

## Shell and tools

- zsh does not split an unquoted `$var` into words. Use `${=var}`, an array, or run the loop under
  `bash -c`.
- In zsh, a word that starts with `=` (`echo =====`) triggers command lookup; quote it.
- macOS `/usr/bin/rsync` is openrsync: no `--chmod=D…,F…`. Set permissions locally and use
  `--perms`.
- Headless Chrome screenshots have a minimum window width of 500 px; check phone widths with the
  page inside a 390 px iframe. Give every headless run a throwaway `--user-data-dir`; otherwise
  the default profile's cache (on macOS under `~/Library/Caches/Google/`) fills with junk.
- Several agents at once can eat the free disk quickly (uv caches, browser caches, notebook
  outputs); watch `df -h ~` and give each brief a budget.
- Downloaded repositories and archives are untrusted: their own directory, your scripts elsewhere,
  and `python3 -I` for anything that reads them.

## Materials

- Every number shown is computed (notebooks executed at build time, CAS transcripts, Lean, logs),
  never recalled. Hidden `assert` cells keep the prose honest.
- In MyST, display math `$$ … $$` needs blank lines around it, or it renders inline and breaks
  the paragraph.
- MyST `linkify` with fuzzy links turns abbreviations with dots into links; set
  `myst_linkify_fuzzy_links: false`.
- Never wrap a card in `<a>` when it contains other links: nested `<a>` is invalid, and the
  browser splits the card. Use a stretched link (`.card-link::after`) and check with
  `check_links.py`.
- A CSS width given to both `<picture>` and its `<img>` shrinks the image twice (64 % of 64 %): give
  it to `<picture>` and let the `<img>` fill it.
- `og:image` must be an absolute URL on a deployed page; relative ones are ignored by previews.
- Talks need offline robustness: vendor reveal.js, MathJax and highlight.js instead of loading
  them from a CDN in the room (`templates/slides/build/vendor.sh`).
- In Obsidian tables the alias bar of a link is escaped, `[[Note\|alias]]`; link checkers must
  strip the backslash.
- A materials agent may find a wrong number in the digest; correct the digest (dated) and tell the
  other agents, instead of letting copies diverge.
- A `print(label, slow())` call can reach the notebook as two stream chunks, and the book then
  shows the line broken in two. Compute first, then print once.
- `jupytext --to ipynb` does not recognise a MyST header; convert with
  `jupytext --from myst --to ipynb`.
- A helper module imported by notebooks leaves `__pycache__` in `book/` unless the notebooks set
  `sys.dont_write_bytecode = True` before the import.
- Relative links from the book to `../slides/` or `../index.html` work in the published layout,
  not from `book/_build/html/` on disk.
- Some publishers answer 403 to non-browser clients after the doi.org redirect: bot protection,
  not a broken link. Record the date on which the references were resolved.
- In the first use the agent's harness refused to write a file named `findings.md`; the findings
  chapter is `register.md`.
- The Verso generator can exit with a non-zero status after writing a complete-looking site (for
  example on a dangling cross-reference); check its exit status.
- A document that reads files from disk at elaboration time (Verso) is not rebuilt by Lake when
  those files change; rebuild it from scratch.
- Commit every `lake-manifest.json`. The cluster driver mirrors the laptop with `rsync --delete`,
  so a manifest written remotely by `lake update` disappears at the next sync unless it was
  fetched back and committed.
- Verso's literate whole-module loader unsets `ELAN_HOME`; on a cluster whose home is full it
  tries to install a toolchain there. Quote proofs with verbatim-excerpt checks instead.
- Verso `signature` blocks cannot show statements that depend on a classical `DecidableEq`
  reliably; use `{docstring}` boxes for those.
- Time and room unknown: write "to be announced"; never invent them.
