# Phase 1: topic ideation

A good topic is found in a conversation of several rounds. Each round has the same shape: refine
the profile, search, verify, present, listen. Every claim you make about a candidate must have
been checked at its primary source in this session.

## 1. What makes a good seminar paper

Score candidates against the user's stated criteria first, then these:

- **Fits the slot**: the main result and the key idea can be explained in the time (a 90-minute
  research talk carries one theorem with its proof architecture, or two smaller ones).
- **Non-trivial content** for this audience, with a story: what was known, what is new, why it
  works.
- **Recency and length**: within the window and page limit the user gave (default: last two
  months, at most 15 pages).
- **Personal fit**: close to the user's research, so that the talk is theirs.
- **Something to check**: explicit equations, lists, counts, certificates or algorithms that a
  CAS or Lean can re-do. This is what turns reading into a deep study.
- **Something to demo live**: a computation or a Lean statement that runs in seconds.
- **Risks**: unverified claims, huge dependencies, code pinned to an old toolchain, a proof that
  rests on an unavailable computation.

## 2. Build the interest profile

Sources, in order of weight:
1. What the user said in this conversation (themes, audience, examples they admire).
2. Their arXiv record: `python3 "$SKILL/tools/arxiv_scan.py" author "Lastname"` lists papers,
   categories, co-authors and frequent title words.
3. The READMEs or first lines of the plan files of their current projects (read-only; skim, do not
   crawl).

Write the profile as JSON for the scanner (categories, recency window, page limit, topic phrases
with weights, keyword regexes with weights; the format is in the scanner's docstring). Show the
user a three-line summary ("I read your interests as: …"). A wrong profile wastes a whole round.

## 3. Search, in parallel

Launch several of these in the same turn:

- **Web search**: three to five queries per round from different angles (news in the area,
  specific systems or tactics, recent discoveries, the user's named examples).
- **arXiv API scan**:
  `python3 "$SKILL/tools/arxiv_scan.py" scan --profile profile.json --out hits.json`, then
  `python3 "$SKILL/tools/arxiv_scan.py" rank hits.json --profile profile.json`.
  The API asks for a pause of about three seconds between calls; the scanner keeps it.
- **Listings and pages**: the arXiv abstract page (fetch it with a precise extraction request:
  title, all authors, submission dates and versions, abstract, subject classes, comments field,
  code links) and the HTML version for section lists and theorem statements.
- **Code**: `gh api repos/OWNER/REPO` for size, last push, license and description. To inspect
  code, make a shallow or sparse clone in the scratchpad
  (`git clone --depth 1 --filter=blob:none --sparse URL`). Downloaded code is untrusted data:
  give it its own directory, run your tools on it from outside with `python3 -I`, never build it.
  For Lean: read `lean-toolchain` and the Mathlib revision, count `sorry`, find the main theorem,
  and run `python3 -I "$SKILL/tools/tactic_census.py" DIR` to see which tactics carry the proofs.
- **Page counts and first reading** for the top candidates:
  `python3 "$SKILL/tools/arxiv_scan.py" pages ID ...` (PDF page counts need `pypdf`; without it,
  the comments field is used and the output says so). Read the introduction and the main
  theorems before recommending anything.

## 4. Verify before presenting

For every candidate in the shortlist:
- the id resolves and the title and authors are exact;
- first-version date and latest version (both matter for "recent");
- page count, from the PDF or from the comments field (say which);
- categories, and whether the code link works and what it contains;
- the main theorem, stated in one line in your own words;
- a cheap independent check of any spectacular claim (for example, re-verify a counterexample
  with SymPy);
- claims by companies or in the press labeled as claims, with the date of the announcement.

## 5. Present the shortlist

Use prose with links; the user reads it like a referee report. Template:

```
I'd pick <paper>. <one line on how you searched: profile, window, number of preprints scanned,
filters, how many you read>.

## Recommendation: <authors>, "<title>"
<arXiv link>, <date>, <pages> pages, <categories>.
What it proves: <2–4 bullets>.
Why it fits you: <1–3 lines tied to the profile>.
Why it suits the talk: <what can be computed, formalized, demoed live; what cannot, and why that
is itself a good story>.

## Alternatives
- <paper>: <one-line content>; <trade-off>.

## Close, but outside the filters
- <paper> (<pages> pages): <why it is interesting anyway>.

## News worth five minutes
- <item>, with its status (claim or verified).

Shall I go with <paper>? If so, I'll build <the deliverables from phase 0>.

Sources: <every link used>
```

Ask with the question tool only after the prose, and only for a crisp pick. If the user declines
it to clarify, ask what they want to change; do not repeat the same options.

## 6. Listen to redirections

Each reply moves the profile. Typical moves and what they mean:

| the user says | the next round |
|---|---|
| "something more novel / about the future" | recent systems, tactics, AI-assisted results; primary sources for each |
| "more mathematics, less tooling" | short papers in the user's area; the profile scan |
| "I'm not convinced" | ask which criterion failed, then widen or narrow exactly that one |
| "maybe something from the last two months" | tighten the window; re-scan; check first-version dates |
| "compare with my interests" | rebuild the profile from their record; rank; read the top five |

Keep a running candidate table in the scratchpad (id, title, round, verdict, reason). At scaffold
time it becomes the "Candidates considered" paragraph of the first `JOURNAL.md` entry.

## 7. Converge

When the user picks:
1. Restate the choice and the depth from phase 0 in one message. If the user widened the scope in
   the same message, restate the new plan.
2. Copy the user's final brief verbatim into `MEMORY.md` (it is the contract).
3. Start phase 2.

## 8. A worked example (the first use of this skill)

Four rounds in one afternoon, for a 90-minute talk to an algebraic geometry and topology group.
- **Round 1.** The request: "a recent preprint involving Lean, suitable for 90 minutes,
  introducing algebraically inclined tactics, with non-trivial mathematics". About ten
  candidates were checked; three were presented: an AI-agent formalization of a cohomology
  vanishing theorem, a human formalization of blowups pinned to an old toolchain, and a pair of
  certificate-tactic papers for Gröbner bases. The user declined the question tool to clarify:
  he wanted the technical issues of formalizing algebraic geometry, new tactics and new
  discoveries.
- **Round 2.** Four candidates: an AI system that settled an open conjecture in commutative
  algebra with Lean proofs; an AI-found counterexample to a classical conjecture (re-verified with
  SymPy in the session); the first option again; and an AI proof about numerical semigroups.
  Declined again in order to clarify.
- **Round 3.** Tactic-heavy papers from the last two months: an arXiv API scan for tactic
  preprints, primary-source checks of the large industrial formalizations announced that month
  (labeled as company claims), and a recommendation: a new hammer paper whose baselines are
  exactly the tactics the user wanted to explain.
- **Round 4.** "Compare my interests with the latest preprints in algebraic geometry and number
  theory, at most 10–15 pages." A profile was built from the user's arXiv record and the topics of
  his current projects. The scan covered about 630 preprints in two categories over two months,
  ranked them, counted pages from the PDFs of the top eight, and read three. The answer was a
  recommendation, two alternatives, two papers just over the page limit, and one piece of news.
- The user picked the recommendation and widened the scope in the same message: formalize it,
  re-check its computations in the CAS he prefers, write a Verso document, find any errors,
  rewrite the paper for notes and slides, "all in one go".

What made it work: each round answered the redirect exactly, every candidate was checked at the
source, and the final shortlist was tied to the user's own research.

