# slides/ — the deck and the board plan

| file | what |
|---|---|
| `seminar.html` | the reveal.js deck, **generated** by `build/build.py` from `build/NN_*.html` (do not edit it) |
| `board-plan.md`, `board-plan.html` | the board plan (panels, timeline, computer run sheet), **generated** by `build/boardplan.py` from `build/board-plan.tpl.md` |
| `build/` | the parts, the generators, the render check, the vendoring script |
| `vendor/` | reveal.js, a highlight.js style and MathJax, fetched by `build/vendor.sh` (sha512-verified npm tarballs, licences inside): the deck works offline |

## Build (from the project root)

```bash
bash slides/build/vendor.sh                                               # once (or after a version bump)
python3 -I slides/build/build.py                                          # seminar.html + timeline
uv run --no-project --with markdown python -I slides/build/boardplan.py   # board-plan.{md,html}
slides/build/check_render.sh                                              # layout check in headless Chrome
```

## Rules the build enforces
- Every `<section>` has `data-timing` (seconds); the total must equal `TALK_MINUTES` (build.py).
  Speaker notes start with `{{TIME}}`; footers carry `{{TM}}` (key **T** shows them).
- Code on slides is only `{{SNIP:name}}`, located in repository files by text anchors (`SNIPS`);
  every code block of the result must be a verbatim excerpt, or the build fails.
- Numbers come from files (`{{COUNT:…}}`, `{{GREP:…}}`, `{{WC:…}}`), never typed.
- Cues say what the speaker does: `cue-board` (✎ which panel), `cue-live` (▶ with the command),
  `cue-opt` (optional, skip when late), `cue-pending` (waiting for another deliverable).
- No placeholder may survive (`{{…}}`): a missing fact stops the build instead of reaching the room.
