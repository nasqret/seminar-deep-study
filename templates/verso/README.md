# verso/ — the controlled reading (Verso document)

A [Verso](https://github.com/leanprover/verso) book compiled against the formalization in
`../formal`. It is a separate Lake project (the same toolchain; Verso pinned to the tag matching
it; `../formal` as a path dependency) and **not** part of a Palomar submission.

| part | content |
|---|---|
| `Doc.lean` | title page, main theorem, `#print axioms`, reading guide |
| I `Doc/Paper*.lean` | the paper rewritten, each result next to its formal statement (or "not formalized, because …") |
| II `Doc/Formal*.lean` | architecture (module table computed from the sources), the Palomar contract quoted from disk, certificates vs `grind`, a guided tour of the key proofs |
| III `Doc/Control.lean` | hypothesis register, `#print axioms` with checked outputs, the axiom audit run inside the document, the comparator log read from disk, a claim-by-claim table |
| IV `Doc/Findings.lean` | the findings register, only if the speaker decided to publish it |
| `Doc/Meta.lean` | helpers: `{sourceFile}`, `libcode`, `{moduleTable}` |

## What "controlled" means
- ```` ```signature ```` blocks are compared with the compiled declaration (names, binders, type).
- `{docstring X}` renders the declaration and its docstring from the library. A missing docstring
  is a warning; add it in the library rather than silencing it.
- ```` ```lean ```` blocks are re-elaborated; ```` ```leanOutput ```` must match Lean's message.
- ```` ```libcode "FILE" ```` blocks must be verbatim excerpts of the library source and are then
  re-elaborated (`scripts/refresh_excerpts.py` refreshes them when the library changes).
- `{sourceFile "FILE" (from := …) (to := …)}` inserts a file read at build time (Challenge,
  comparator.json, logs, CAS transcripts copied into `evidence/`).

## Build
Where `../formal` is built (on a cluster: prefix with `tools/cluster.sh run '…'`):

```bash
cd ../verso && bash scripts/remote-setup.sh      # once: no second Mathlib download (hard links)
cd ../verso && bash scripts/remote-build.sh      # each time: lake build Doc, render to _out/
```

Open `_out/html-single/index.html` (one large page; works from `file://`); the multi-page
`_out/html-multi/` needs a web server (`python3 -m http.server -d _out/html-multi 8000`).

## Hazards met in the first use
- **Commit `lake-manifest.json`.** A sync with `rsync --delete` from the laptop deletes a manifest
  that exists only on the cluster (written by `lake update`); fetch it back at once and commit it.
- Verso's literate whole-module loader unsets `ELAN_HOME`, so on a cluster with a full home it
  would try to install a toolchain there: quote proofs with `libcode` excerpt checks instead.
- Statements whose types depend on a classical `DecidableEq` render reliably only through
  `{docstring}` boxes, not `signature` blocks.
- Lake does not track files read at build time: `remote-build.sh` always re-elaborates the
  document itself (`rm -rf .lake/build` of this package only).
- The generator can exit non-zero after writing a complete-looking site; check its exit status.
