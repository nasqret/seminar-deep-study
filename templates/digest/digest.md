# {{PAPER}} — a digest

*Source:* {{PAPER}}, {{ARXIV_ID}}, {{SUBMITTED}}, {{PAGES}} pp. (version followed: {{VERSION}}).
*This digest* is the single mathematical source of truth for the notes, the slides, the Verso
document and the landing page. Every statement marked **[Lean]** is proved in `formal/` (name the
declaration; axioms: `propext`, `Classical.choice`, `Quot.sound` only); **[CAS]** means
re-computed exactly ({{CAS}}, script in `cas/`, transcript in `cas/out/`); **[num]** means a
high-precision numerical screen (`artifacts/computational/`), evidence and not a proof; **[exp]**
means an experiment or benchmark re-run; **[paper]** means taken from the paper and not re-checked
here.


<!-- Write mathematics as $…$ / $$…$$ LaTeX; publish the PDF made by scripts/digest_pdf.py. -->

---

## 0. The result in three lines

* What is proved, in one sentence a colleague can repeat.
* Why it is new: the previous record, bound or state of knowledge (with references).
* The key idea of the proof.

## 1. Background

| question | what was known | reference |
|---|---|---|
| | | |

Why the audience should care, in a paragraph. Every number here has a reference.

## 2. Setup and notation

The objects, with the paper's numbering. One worked example by hand.

## 3. Theorem X.Y: <name> [tags]

**Statement.** (as in the paper; then in the form that was formalized, if different)

**Proof architecture.**
1. Step — what it uses — [tag] (`cas/NN_….m`, Lean `Proj.foo`).
2. Step — … — [tag].

**What goes on the board / on the screen.**

## 4. Theorem X.Z: …

## N. Findings register (formalization and re-computation)

| # | place | finding | severity | evidence | found by |
|---|---|---|---|---|---|
| F1 | | | confirmed / wording / implicit hypothesis / strengthening / error | | |

*Confidential until the speaker decides (unpublished paper).*

## N+1. Two routes to the same algebra [Lean]

Which steps are checked by CAS certificates (`linear_combination`) and which by Lean's own
automation (`grind`), with the file names. Both end in ordinary proof terms checked by the kernel.

## N+2. Exercises for the seminar

1. A check by hand of the smallest case.
2. Why a hypothesis is needed (or, using a finding, why it is not).
3. A computation to try in the CAS during the break.
