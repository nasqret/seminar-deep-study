import VersoManual
import {{LEAN_NAME}}
import Doc.Meta

open Verso.Genre Manual
open Verso.Genre.Manual.InlineLean
open DocMeta

set_option pp.rawOnError true
set_option verso.code.warnLineLength 100

#doc (Manual) "{{TITLE}}: a controlled reading" =>
%%%
authors := ["{{SPEAKER}}"]
shortTitle := "{{SHORT_TITLE}}"
%%%

These notes accompany a seminar reading of {{PAPER}}. The reading is _controlled_: next to the
mathematics stands a Lean formalization (`formal/`), and this document is compiled against it.
Every `signature` block is compared with the declaration of the same name in the compiled library;
every Lean code block is re-elaborated while the page is built; every Lean output shown here is
compared with the output Lean actually produces; quoted proofs must be verbatim excerpts of the
library; quoted files are read from disk at build time. A mismatch is a build error, so this page
cannot silently drift from the proofs.

Here is the main theorem as it stands in the library (replace the example):

```signature
{{LEAN_NAME}}.R_simple {K : Type*} [Field K] [CharZero K] {r : K} (h : {{LEAN_NAME}}.R r = 0)
    (h' : 4 * r ^ 3 - 12 * r = 0) : False
```

With its documentation, read from the library:

{docstring {{LEAN_NAME}}.R_simple}

Its axiom footprint, as Lean reports it during the build of this page:

```lean (name := axHeadline)
#print axioms {{LEAN_NAME}}.R_simple
```

```leanOutput axHeadline
'{{LEAN_NAME}}.R_simple' depends on axioms: [propext, Classical.choice, Quot.sound]
```

The proof, quoted from the library (the build fails if this is no longer a verbatim excerpt;
`scripts/refresh_excerpts.py` refreshes such blocks mechanically). A hidden block first opens a
tour namespace with the variables of the library file, so that the excerpt re-elaborates as is:

```lean -show
namespace {{LEAN_NAME}}.Tour
open {{LEAN_NAME}}
variable {K : Type*} [Field K]
```

```libcode "../formal/{{LEAN_NAME}}/Main.lean"
theorem R_simple [CharZero K] {r : K} (h : R r = 0) (h' : 4 * r ^ 3 - 12 * r = 0) : False := by
  unfold R at h
  have key : (1 : K) = 0 := by
    linear_combination (1/12*r^2 - 1/3) * h + (-1/48*r^3 + 7/48*r) * h'
  norm_num at key
```

```lean -show
-- the re-elaborated excerpt proves exactly the library's statement
example : @{{LEAN_NAME}}.Tour.R_simple = @{{LEAN_NAME}}.R_simple := rfl
end {{LEAN_NAME}}.Tour
```

The Palomar contract, read from disk while this page is built:

{sourceFile "../formal/comparator.json"}

The modules of the formalization, computed from the sources:

{moduleTable}

*How to read the document.* Part I rewrites the paper, putting next to each result its formal
statement or saying that there is none; Part II explains the formalization (architecture, the
contract, certificates versus `grind`, a guided tour of the key proofs); Part III is the
correctness control (the hypothesis register, `#print axioms` with checked outputs, the axiom
audit run inside the document, the comparator log, a claim-by-claim table); Part IV is the
findings register, if the speaker decided to publish it. Add each part as its own module
(`Doc/Paper.lean`, …) and include it with `{include 1 Doc.Paper}`.
