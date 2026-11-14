# CLAUDE.md — operating instructions for `{{PROJECT}}`

Seminar project: **{{PAPER}}** — a deep study for a talk: the paper rewritten as a digest,
computations re-done ({{CAS}}), the logic formalized in Lean, findings recorded, and the talk
materials (notes, slides, board plan, landing page). Talk: {{TITLE}}, {{SEMINAR}}, {{DATE}}
(time and room: {{TIME_AND_ROOM}}). Speaker: {{SPEAKER}}. Materials are in {{LANGUAGE}}.

## 0. Start of every session
1. Read `MEMORY.md` (durable facts, decisions), then the top entry of `JOURNAL.md`, then `PLAN.md`.
2. Skim `vault/Home.md` (the knowledge base).
3. The mathematical source of truth is `artifacts/mathematical/digest.md`; the verification status
   of every claim is there (tags `[Lean]`, `[CAS]`, `[num]`, `[exp]`, `[paper]`).

## 1. Hard rules
* Every number shown in notes, slides or pages is computed (executed notebooks, CAS transcripts,
  Lean output, logs), never recalled.
* The CAS finds, Lean checks: certificates go from `cas/out/` through `tools/cert2lean.py` into the
  generated Lean file; never edit generated files by hand.
* Deep but standard facts enter the formalization as explicit hypotheses, never as axioms.
* Findings about the paper stay in this repository until the speaker decides otherwise.
* Never run `lake update` without `MATHLIB_NO_CACHE_ON_UPDATE=1`; fetch Mathlib oleans by module
  name only. Never run `lake` inside the speaker's other projects.
* Do not deploy, push or publish anything without an explicit request in the current session.
* {{MORE_RULES}}

## 2. Layout
| path | what |
|---|---|
| `artifacts/mathematical/` | `digest.md` (paper rewritten + findings register), `cas-verification.md` |
| `artifacts/computational/` | numeric screens and independent checks |
| `cas/` | CAS scripts (`NN_topic.*`) and transcripts (`out/`) |
| `formal/` | Lean project (light or Palomar format: Challenge/Solution/comparator.json/formalization.yaml, AxiomAudit + Audit) |
| `verso/` | Verso document (a separate Lake project depending on `../formal`) |
| `tools/` | `cert2lean.py`, cluster and CAS runners |
| `book/` | notes (Jupyter Book); `slides/` the deck and the board plan; `index.html` the landing page |
| `vault/` | Obsidian knowledge base; `source/` the paper (pdf/tex git-ignored, `SOURCE.md` tracked) |

## 3. Known traps (found the hard way)
* {{TRAPS}}

## 4. End of every session
Append a dated entry to `JOURNAL.md`, update `PLAN.md`, add or adjust vault notes, commit
(Conventional Commits, English).
