---
name: seminar-deep-study
description: 'Prepare a research seminar talk as a deep study of one paper, starting from the choice of topic. Use whenever someone needs a paper or preprint to present at a seminar, reading group, journal club, colloquium or invited talk (interactive topic ideation: profile their interests, scan recent arXiv and code repositories, verify candidates at the source, discuss a shortlist over several rounds), and whenever they want to go deep into a chosen paper: rewrite it as a digest with a findings register, re-check its computations with computer algebra, numerics or experiments, formalize key results in Lean (light or Palomar-registry class), and track errors in the paper. Also builds the talk materials and project memory: notes (Jupyter Book), slides and a board plan, live Lean demos, a Verso document, a landing page or dashboard (local or online), an Obsidian vault, memory, journal and plan files. Mathematics and computer science. Not for writing your own paper or for a one-paragraph summary.'
---

# Seminar deep study

A seminar talk prepared as a **deep study** of one paper. First the agent helps the user choose
the paper in an interactive discussion backed by evidence. Then it rewrites the paper as a
digest in which every claim carries its verification status. It re-does the computations with a
computer algebra system (CAS), formalizes the logic in Lean, and records what it finds in the
paper. Finally it builds the talk materials from that single source of truth. The user decides;
the agent proposes with evidence and checks everything it states.

Bundled files are relative to this skill's base directory (shown when the skill loads); below it
is called `$SKILL`. Project files go into the user's project directory, never into `$SKILL`.

## Phases and what to read

| phase | read first | leaves behind |
|---|---|---|
| 0 intake | `references/intake.md` | answers in `MEMORY.md`, open decisions in `PLAN.md` |
| 1 topic ideation | `references/ideation.md` | the chosen paper; every candidate in `JOURNAL.md` |
| 2 source, scaffold, digest | `references/digest.md` | repository, `source/SOURCE.md`, digest with findings register |
| 3 verification | `references/verification.md`, `references/lean-palomar.md`, `references/compute.md` | CAS transcripts, numeric screens, Lean library, audit, logs |
| 4 materials | `references/materials.md`, `templates/briefs/` | notes, slides, board plan, Verso document, landing page, vault |
| 5 live demo | `references/live-demo.md` | a rehearsed demo file and a fallback |
| 6 documentation | `references/documentation.md` | journal, plan, memory, vault notes, commits |
| 7 publishing | `references/publishing.md` | nothing, unless the user asks in this session |
| any | `references/traps.md` | read before Lean, cluster, CAS or site work |
| CS paper | `references/computer-science.md` | the computer-science reading of phases 1–5 |

Phases are a menu, not a march. A reading-only talk is phases 0–2 plus the materials it needs; a
user who arrives with a paper starts at phase 0 and skips phase 1.

## Principles

1. **The user chooses; you propose with evidence.** Never pick the paper, the depth or the
   publication target silently. A redirection ("not convinced", "something more recent") is
   normal: it refines the profile, so start a new round instead of defending the last one.
2. **Primary sources only.** Check the title, authors, dates, version, page count and code
   availability at the source: the arXiv abstract page or API, the PDF itself, the repository.
   Label announcements by companies or the press as claims.
3. **Every number shown is computed, never recalled.** Numbers on slides, pages and in the notes
   come from executed notebooks, CAS transcripts, Lean output or build logs.
4. **One source of truth.** The digest is the mathematical source of truth. Each of its claims is
   tagged `[Lean]`, `[CAS]`, `[num]`, `[exp]` or `[paper]`. The notes, slides, Verso document and
   page derive from it and never contradict it.
5. **The CAS finds, the proof assistant checks.** Certificates go from CAS transcripts through a
   generator (`tools/cert2lean.py`) into Lean. Generated files are rebuilt, never edited by hand.
6. **Hard but standard facts become explicit hypotheses, never axioms.** Record each one in the
   digest and in the formalization metadata.
7. **Findings are confidential by default.** Findings about someone else's unpublished paper stay
   in the project until the user decides. For a real error, suggest telling the authors first.
8. **Protect the machine and shared resources.** Check free disk space before installing
   toolchains, never run `lake update` without `MATHLIB_NO_CACHE_ON_UPDATE=1`, and never build
   inside the user's other projects. Follow the cluster etiquette in `references/compute.md`.
9. **One owner per file.** Each subagent writes only its own directory; you integrate, review and
   commit.
10. **Outward-facing actions need an explicit request in the current session.** This covers
    deploying, pushing, creating a remote repository and publishing an artifact. Never write a
    secret (password, token, private key) into any file.
11. **Look up the user's jargon in the user's own files first.** An unfamiliar term ("register
    class", a seminar acronym) is often defined in their notes or projects. Search there, then
    the web, then ask.

## Phase 0: intake

Survey the environment read-only first, so that the questions offer concrete options. Check free
disk space (`df -h ~`), installed Lean toolchains, the available CAS (local or remote), Python and
`uv`, and any project the user named as a format to copy. Then ask with the question tool
(AskUserQuestion in Claude Code): at most
four questions per call, two to four options each, the recommended option first and marked
"(Recommended)". The question bank is in `references/intake.md`; it covers the talk, the topic
and depth, the CAS and compute, the deliverables, **how the dashboard is delivered (local only or
online, and where; now or later)**, and git. Skip whatever the user's first message already
answers and confirm it in one line instead. Record answers as dated decisions in `MEMORY.md`; open
ones go into `PLAN.md` as ❓.

## Phase 1: topic ideation (when the paper is not given)

Run rounds until the user picks (`references/ideation.md`):
1. Build an interest profile from the user's arXiv record (`tools/arxiv_scan.py author`), the
   READMEs of their current projects, and what they said. Show it in three lines so they can
   correct it.
2. Search in parallel: web search for news; the arXiv API over categories × topics × a recency
   window (`tools/arxiv_scan.py scan`, then `rank`); code repositories through the GitHub API and
   shallow clones in the scratchpad (`tools/tactic_census.py` for Lean code).
3. Verify every candidate you will present (id, title, authors, dates, versions, pages from the
   PDF, code link). Re-check a spectacular claim yourself when that is cheap.
4. Present the shortlist in prose: one recommendation with why it fits the user and the format,
   two or three alternatives with trade-offs, papers just outside the filters, news worth five
   minutes, and the sources. End with one direct question. The question tool is a convenience for
   a crisp final pick; if the user declines it to clarify, they want to talk, so ask what they
   want to change.
5. Log every candidate and the reason it was dropped; it goes into `JOURNAL.md` at scaffold time.

## Phase 2: source, scaffold, digest

Fetch the PDF and the LaTeX source into `source/` (git-ignored). Record the version and the
SHA-256 checksums in `source/SOURCE.md`. Transcribe formulas and lists from the LaTeX, never from
the PDF text layer. Scaffold the project with `tools/scaffold.py` (documentation templates, the
digest, and optionally the Lean, CAS, cluster, site, slides, book, Verso and vault skeletons).
Then write the digest (`templates/digest/digest.md`): the result in three lines, background, setup, one
section per theorem with its proof architecture and status tags, the **findings register**
(severities: confirmed / wording / implicit hypothesis / strengthening / error), and exercises.
Details: `references/digest.md`.

## Phase 3: verification

Turn every computational claim and every "one checks" into a row of a verification table in
`PLAN.md`, then work through it:
- numeric screens first (high precision; they catch transcription errors, they prove nothing);
- CAS scripts with committed transcripts, whose `CHECK` lines must be true; disagreements go to
  the findings register (`references/verification.md`);
- certificates: the CAS prints `CERT` blocks, `tools/cert2lean.py` writes the Lean file, and
  `linear_combination` or `ring` checks each identity; `grind` can re-prove the same steps with no
  certificate, which is worth showing;
- Lean: statements first, then proofs; light or Palomar-class (`Challenge.lean`/`Solution.lean`/
  `comparator.json`, standard axioms only, axiom audit with `import all`, `lake comparator
  --paranoid`, warning-free build, logs). See `references/lean-palomar.md`, and
  `references/compute.md` for local versus cluster builds and the disk-space rules.

Treat linter warnings as possible findings: an unused instance argument can mean the theorem holds
more generally than the paper states.

## Phase 4: materials, by parallel subagents

Launch one background agent per deliverable, each owning its directory: CAS re-verification, the
Verso document, notes (Jupyter Book), slides with a board plan, and the landing page with its hero
image and the vault. Fill the briefs in `templates/briefs/`. Each brief names the sources of truth
(the digest, the Lean files, the transcripts), the facts it may state, the commands it may run,
and that it must never invent numbers, names, times or rooms. Keep verifying while they run. When
a fact changes (a new result, a new count, a new demo), send each running agent a short
self-contained update with SendMessage: what changed, where it is, what to add, "optional, keep
your current plan". Agents re-derive numbers, so they also referee the digest: ask them to report
any disagreement, then correct the digest (dated) and tell the others. Watch the free disk while
several agents run. When an agent finishes, review its output (build it, open it, take headless
screenshots), link the deliverables to each other, and commit. Generated materials are rebuilt
from their sources: the slides refuse code that is not a verbatim excerpt, and they carry vendored
libraries so that the talk works offline. Details: `references/materials.md`.

## Phase 5: live demo

Build one demo file that runs in seconds: `#check` and `#print axioms` of the main theorem, one
certificate checked by `linear_combination`, the same fact proved by `grind`, and a commented-out
"break it" variant that fails visibly. Run it locally, or remotely through the cluster driver's
`demo` command. Rehearse it twice and keep a fallback (the rendered Verso document or
screenshots). Details: `references/live-demo.md`.

## Phase 6: documentation and end of session

The project carries `CLAUDE.md` (operating instructions), `MEMORY.md` (dated facts and
decisions), `JOURNAL.md` (dated entries), `PLAN.md` (✅ done · 🟡 in progress · ⬜ to do ·
❓ user's decision), `MAINTENANCE.md` (runbook), `README.md` and the vault. At the end of every
session: append a journal entry, update the plan, add vault notes for new concepts and decisions,
and commit (Conventional Commits). Client memory files hold only facts that should outlive the
project. Details: `references/documentation.md`.

## Phase 7: publishing (only on explicit request)

Build everything locally first. Publish only what the user asked for, in this session, to the
target chosen in phase 0: a private Claude artifact, GitHub Pages, or a web server through an
allow-list deploy script with a dry run, a link check and a leak scan (`tools/leak_scan.py`).
A public repository gets a fresh history and a leak scan before the user pushes it. Details:
`references/publishing.md`.

## Starting checklist

1. Phase 0 questions answered, decisions recorded.
2. Paper chosen (phase 1) or given; source fetched and checksummed.
3. `python3 "$SKILL/tools/scaffold.py" <project> ...`; `git init`; first commit.
4. Digest written, claims tagged, verification table in `PLAN.md`.
5. Verification and formalization started; materials agents launched once the digest is stable.
6. End of session: journal, plan, vault, commit.
