# Brief: the landing page (dashboard), the computed hero image, and the vault

Build (1) the landing page and (2) the Obsidian knowledge base for the seminar project in
`<REPO>`. Write only `index.html`, `assets/`, `scripts/generate_hero.py` and `vault/`.

## Context
<SEMINAR>, <DATE>, <LENGTH> (time and room: <KNOWN or "to be announced" — never invent>). Speaker
<SPEAKER>. Topic: <PAPER>; the formalization (`formal/`), the CAS re-verification (`cas/`), a Verso
document (`verso/`, being built), notes (`book/`, being written), slides (`slides/seminar.html`,
being written). Language: <LANGUAGE>.

Sources of truth (read first): the digest, `formal/Challenge.lean`, `formal/comparator.json`,
`formal/verification/logs/`, `cas/out/`. Facts you may state: <the exact list>. Never invent
other facts.

## 1. The landing page `index.html`
Start from the skill's `templates/site/index.html` <or: imitate the format of <REFERENCE PAGE>
exactly (read it fully; read-only)>: a dark hero with a COMPUTED image (`assets/hero.webp`,
`assets/hero.jpg` fallback, plus `assets/og.png` and `assets/favicon.png`); the title, speaker,
seminar, date and time/room; cards (digest, notes, slides, formalization, Verso document, CAS);
boxed sections: the talk, the result, the plan of the minutes, verification status (numbers copied
from the logs), findings (only if the speaker agreed), how to reproduce, references (check the
URLs), about the image. Relative links only; system-font fallbacks so that it works offline.
Do not deploy anything.

The hero image is computed by `scripts/generate_hero.py` from the paper's mathematics (for
example, a graph or configuration of the explicit objects, coloured by family), with assertions
that stop the script if the picture would show something false, and the left edge blending into
the background colour. Describe exactly what is drawn in "About the image".

Visual QA: headless Chrome (`--headless=new --screenshot=OUT.png --window-size=1280,900
file:///…/index.html`; the window must be at least 500 px wide; for phone width, wrap the page in
a 390 px iframe). Look at the screenshots and fix layout problems.

## 2. The vault `vault/`
Start from the skill's `templates/vault/`. `Home.md` is the map of content; folders `Paper/` (each
result: statement, proof idea, status tag, links), `Concepts/`, `Formalization/` (module map,
hypothesis register, certificate pipeline, how it is built), `Verification/`, `Talk/`,
`Decisions/` (one dated note per decision), `Infrastructure/`. Wiki links generously; every note
starts with a one-paragraph summary; only facts from the sources.

## Report
Files created, screenshots taken, and anything you could not verify.
