# Phase 0: intake

The goal is a short, decisive conversation, so that the rest can run "all in one go" with few
interruptions. Ask only what the first message leaves open, propose concrete options, and record
the answers.

## 1. Survey before asking (read-only, a minute)

| check | command or source | why |
|---|---|---|
| free disk | `df -h ~` | Mathlib and toolchains need several GB; a nearly full disk decides local versus remote |
| Lean | `elan toolchain list`, `ls ~/.elan/toolchains` | reuse an installed toolchain if one matches |
| CAS | `which magma sage gp python3`; ask about remote hosts | where the CAS runs decides the runner |
| Python | `uv --version`, `python3 --version` | notes, numeric screens, scripts |
| format references | the projects the user names ("like my X project") | copy their landing page, slides and docs format |
| user memory | the client's memory directory, `MEMORY.md` files of related projects | known preferences and infrastructure |

Never run `lake`, builds or installers inside the user's other projects during the survey: elan
downloads a pinned toolchain as a side effect.

## 2. The question bank

The question tool takes at most four questions per call and two to four options per question; it
adds an "Other" answer automatically. The `header` is a chip label of at most 12 characters. Put
the recommended option first and add "(Recommended)" to its label. Write the trade-off into the
description, and include the facts you surveyed ("disk: 6.6 GB free").

### Batch A: the talk

| header | question | options |
|---|---|---|
| Length | How long is the talk? | 90 min (Recommended for a research seminar) · 60 min · 45 min · two sessions |
| Audience | Who is in the room? | specialists in the paper's area · mixed mathematicians · computer scientists · students |
| Setup | What will you use? (multiSelect) | blackboard · slides on a computer · live Lean · live CAS |
| Language | Language of the materials? | English · the local language · both (second edition) |

Date, time and room: ask in prose if they are not in the first message. If unknown, every page
says "to be announced"; never invent them.

### Batch B: topic and depth

| header | question | options |
|---|---|---|
| Topic | Do you have a paper already? | find one for me (Recommended when unsure) · I have a paper (give the arXiv id) · I have a theme, not a paper |
| Filters | Which papers qualify? (only when searching) | last 2 months, at most 15 pages (Recommended) · last 6 months, at most 30 pages · a classic paper, any date · my own criteria |
| Depth | How deep should the study go? | digest and findings, with CAS re-checks (Recommended) · plus Lean, light (key statements, demo-ready) · plus Lean, Palomar-class, and a Verso document · reading and digest only |
| CAS | Which computer algebra system, and where does it run? | Magma on a remote host · SageMath locally · SymPy or PARI/GP locally · none |

Interest profile: when searching, also ask which sources describe the user's interests (their
arXiv record, their current projects, keywords they give, the group's themes). If they say "you
know my interests", build the profile from their arXiv record and project READMEs and show it.

### Batch C: delivery

| header | question | options |
|---|---|---|
| Compute | Where should Lean and other heavy builds run? (state the free disk) | locally, if the disk allows · on a SLURM cluster · locally for small checks, remotely for builds · no Lean |
| Materials | Which deliverables? (multiSelect; memory, journal and plan files are always created) | notes as a Jupyter Book · slides and a board plan · landing page / dashboard · Obsidian vault |
| Dashboard | How should the dashboard (landing page) be delivered? | local only: open `index.html` from disk (Recommended to start) · a private Claude artifact, online, visible only to you until you share it · GitHub Pages · your own web server via rsync |
| Git | Where should the project repository live? | local git only (Recommended) · a private GitHub repository · a public repository (fresh history, leak scan first) |

If the dashboard answer is online, ask one follow-up question: "Publish now, or build locally and
publish when you say so?" The default is to build locally and publish later. Publishing always
needs an explicit request in the session in which it happens.

### Batch D (only when relevant)

- Verso document: yes / no (needs the Lean project; it compiles against the library).
- Formalization target: which results (list the theorems), and which deep inputs may become
  hypotheses.
- Contacting the authors about findings: the user decides later; record it as ❓ in `PLAN.md`.

## 3. When the user says "just go"

Use these defaults and say so in one message: a 90-minute research seminar in English; a topic
from the profile (last two months, at most 15 pages); a digest with CAS re-checks and light Lean;
compute decided by the disk check; all materials; dashboard local only; local git. List what you
will build, then proceed without further questions. Remaining choices go into `PLAN.md` as ❓.

## 4. Lessons from the first use

- Do not mix the topic choice with infrastructure questions in one call. In the first use, the
  user declined a combined "which paper + how to get Mathlib" question in order to clarify, and
  the infrastructure answer changed anyway ("we can use the cluster").
- A topic is chosen in conversation. Two question-tool calls for the paper were declined in favour
  of free-text clarification; the choice came after a prose shortlist. Use the tool for crisp
  decisions (logistics, depth, deliverables, delivery), and prose for ideas.
- The final brief usually widens the scope ("formalize it anyway", "find the errors", "all in one
  go"). Batch B's depth question anticipates this; when the scope widens, restate the plan and go.

