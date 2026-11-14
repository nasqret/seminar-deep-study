# {{TITLE}}

**Seminar notes.** {{SEMINAR}} — {{DATE}}. Speaker: {{SPEAKER}}. Audience: {{AUDIENCE}}.

The talk presents {{PAPER}} {cite}`Paper`, together with a **Lean formalization** of its core and a
**re-verification of its computations** ({{CAS}}).

```{admonition} The results in three lines
:class: important
* {{RESULT_LINE_1}}
* {{RESULT_LINE_2}}
* {{RESULT_LINE_3}}
```

## How to read these notes

| chapter | content | for the talk |
|---|---|---|
| 1. {doc}`paper` | context, the theorems, a map of the proofs | 0–10 min |
| 2. {doc}`section/section` | one chapter per section of the paper | … |
| 3. {doc}`formalization/formalization` | the Lean development: contract, certificates, `grind`, what is assumed | … |
| 4. findings register (`register.md`, in the book once the speaker decides to publish it) | what the formalization and the recomputation found | … |
| 5. {doc}`exercises` | exercises, several with computed answers | questions |

```{admonition} Every number on these pages is computed
:class: tip
The computational chapters are notebooks stored **without outputs** and executed every time the
book is built. Hidden `assert` cells stop the build if a recomputed value ever disagrees with the
text. Lean code is never retyped: every Lean snippet is included verbatim from `formal/` at build
time, and the verdicts of the Lean build and of the comparator are parsed from the committed logs.
```

Provenance tags, as in the project's digest: **[Lean]** proved in `formal/`; **[CAS]** recomputed
exactly ({{CAS}}, `cas/`); **[num]** a high-precision numerical computation; **[paper]** taken from
the paper and not rechecked.

* <a href="../slides/seminar.html">Slides of the talk</a> · <a href="../index.html">project page</a>
  (these relative links assume the published layout, in which the book sits next to `slides/` and
  `index.html`).
