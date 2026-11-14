# Changelog

All notable changes to this skill. Versions follow [semantic versioning](https://semver.org).

## Unreleased

- Digest PDF: `templates/digest/digest_pdf.py` + `digest_preamble.tex` (pandoc → LuaLaTeX); the digest's
  mathematics in `$…$`; publish the PDF, never the raw Markdown.

## [Unreleased]

- Notes: the Jupyter Book template follows the finished notes of the first use: MyST notebooks
  executed at every build with guard asserts, `literalinclude` from `formal/`, verdicts parsed
  from the verification logs, a shared helper module with an appendix, a bibliography, a
  findings chapter (`register.md`) kept out of the table of contents until published; the notes
  brief and the "Notes" part of `references/materials.md` are rewritten accordingly; new traps.

## [1.0.0] — 2026-11-14

First version, extracted from one long working session in which a seminar talk on a recent
algebraic geometry preprint was chosen, studied, formalized and prepared.

- **Method** (`SKILL.md`): phases 0–7 (intake, topic ideation, digest, verification, materials by
  parallel agents, live demo, documentation, publishing) and the principles behind them.
- **Intake** (`references/intake.md`): a question bank for the question tool, including how the
  dashboard is delivered (local, private artifact, GitHub Pages, own server) and when.
- **Ideation** (`references/ideation.md`, `tools/arxiv_scan.py`): interest profiles, arXiv scans
  with ranking and page counts, verification at the source, the shortlist format, redirections.
- **Digest and findings register** (`references/digest.md`, `templates/digest/digest.md`): status tags
  and severities.
- **Verification** (`references/verification.md`, `references/lean-palomar.md`): CAS transcripts,
  numeric screens, the certificate pipeline (`tools/cert2lean.py`), `grind` as a second route,
  Palomar-format Lean templates with an axiom audit and `lake comparator`.
- **Compute** (`references/compute.md`, `templates/cluster/`): disk rules for Mathlib, a SLURM
  driver, a remote CAS runner.
- **Materials** (`references/materials.md`, `templates/`): briefs for subagents; a landing page
  and dashboard with a computed, checked header image; a reveal.js deck built from parts with
  verbatim code checks, minute marks, vendored libraries and a render check; a generated board
  plan; a Jupyter Book with build-time computations; a Verso document with excerpt checks; an
  Obsidian vault with a link checker.
- **Publishing** (`references/publishing.md`, `templates/site/scripts/deploy.sh`,
  `tools/leak_scan.py`): allow-list deploys, link checks, leak scans, fresh-history public repos.
- `tools/scaffold.py`, `install.sh`, consistency tests.

[Unreleased]: ./CHANGELOG.md
[1.0.0]: ./CHANGELOG.md
