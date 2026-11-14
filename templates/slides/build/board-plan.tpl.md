# Board plan — {{TITLE}}

{{SEMINAR}}, {{DATE}}. {{NSLIDES}} slides; times from the slides' `data-timing` (key **T** in the
deck shows them in the footers). Optional slides: {{OPTIONAL}} ({{OPTMIN}} min) — skip them when late.

## The boards

| panel | content | written at | erased at |
|---|---|---|---|
| 1 | the setup and notation | {{S:3}} | never |
| 2 | the proof steps | {{S:3}} | {{E:3}} |

## Timeline

| time | slide | board | screen | live |
|---|---|---|---|---|
| {{T:1}} | 1 | — | title | — |
| {{T:2}} | 2 | — | the result in three lines | — |
| {{T:3}} | 3 | panels 1–2 | the proof | — |
| {{T:4}} | 4 | — | the Lean statement (`formal/Challenge.lean`, lines {{LN:challenge_stmt}}–{{LNEND:challenge_stmt}}) | — |
| {{T:5}} | 5 | — | the certificate and `grind` | `{{DEMO_COMMAND}}` |
| {{T:6}} | 6 | — | outlook | — |

## Computer run sheet

1. Before the talk: open the deck (offline-capable), the demo terminal, and the fallback (the
   Verso page or screenshots) in separate windows.
2. Live demo at {{S:5}}: run `{{DEMO_COMMAND}}`; uncomment the "break it" example; re-run; comment
   it back. Without network: show the fallback.

## The day before

- [ ] demo run twice from the room's network; timing noted
- [ ] VPN or gateway login works on the presentation laptop (if the demo is remote)
- [ ] the board plan printed (`board-plan.html`, print to A4)
