#!/usr/bin/env python3
"""Generate slides/board-plan.md and slides/board-plan.html from board-plan.tpl.md.

    uv run --no-project --with markdown python -I slides/build/boardplan.py

It rebuilds slides/seminar.html first (via build.py) and takes the minute marks from the slides'
data-timing, so the board plan and the deck can never disagree about the timing.

Placeholders in the template:
  {{NSLIDES}}               number of slides
  {{S:n}} {{E:n}} {{T:n}}   start, end, "start–end" of slide n
  {{OPTIONAL}} {{OPTMIN}}   the slides marked OPTIONAL, and their total minutes
  {{LN:name}} {{LNEND:name}}  first / last line of a snippet defined in build.py
  {{COUNT:name}}            a count defined in build.py
"""
import html as htmlmod
import importlib.util
import pathlib
import re
import sys

import markdown

sys.dont_write_bytecode = True  # no __pycache__ next to the slides

HERE = pathlib.Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('deckbuild', HERE / 'build.py')
deck = importlib.util.module_from_spec(spec)
spec.loader.exec_module(deck)
ROOT = deck.ROOT

_, timeline, _ = deck.build()
T = {x['n']: x for x in timeline}
opt = [x for x in timeline if any(c.startswith('opt') for c in x['cues'])]

src = (HERE / 'board-plan.tpl.md').read_text(encoding='utf-8')
src = src.replace('{{NSLIDES}}', str(len(timeline)))
src = src.replace('{{OPTIONAL}}', ', '.join(str(x['n']) for x in opt) or 'none')
src = src.replace('{{OPTMIN}}', f"{sum(x['sec'] for x in opt) / 60:g}")


def slide(n):
    if int(n) not in T:
        sys.exit(f'the deck has no slide {n}')
    return T[int(n)]


src = re.sub(r'\{\{S:(\d+)\}\}', lambda m: slide(m.group(1))['start'], src)
src = re.sub(r'\{\{E:(\d+)\}\}', lambda m: slide(m.group(1))['end'], src)
src = re.sub(r'\{\{T:(\d+)\}\}', lambda m: f"{slide(m.group(1))['start']}–{slide(m.group(1))['end']}", src)
src = re.sub(r'\{\{LN:(\w+)\}\}', lambda m: str(deck.extract(m.group(1))[1]), src)
src = re.sub(r'\{\{LNEND:(\w+)\}\}', lambda m: str(deck.extract(m.group(1))[2]), src)
src = re.sub(r'\{\{COUNT:(\w+)\}\}', lambda m: deck.count(m.group(1)), src)
left = re.findall(r'\{\{[^}]+\}\}', src)
if left:
    sys.exit(f'unresolved placeholders: {sorted(set(left))}')
(ROOT / 'slides' / 'board-plan.md').write_text(src, encoding='utf-8')

title = htmlmod.escape(src.splitlines()[0].lstrip('# ').strip())
body = markdown.markdown(src, extensions=['tables', 'fenced_code'])
page = f'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title}</title>
<style>
  body {{ font-family: 'Inter', system-ui, sans-serif; color: #1e293b; background: #fafbfc; margin: 0; line-height: 1.5; }}
  main {{ max-width: 1120px; margin: 0 auto; padding: 2rem 2rem 4rem; background: #fff; }}
  h1 {{ font-size: 1.7rem; font-weight: 800; color: #0f172a; }}
  h2 {{ font-size: 1.25rem; color: #0f172a; margin-top: 2rem; padding-top: 0.4rem; border-top: 3px solid #4f46e5; }}
  p, li {{ font-size: 0.92rem; }}
  code {{ font-family: 'JetBrains Mono', ui-monospace, monospace; font-size: 0.86em; background: #f1f5f9; padding: 0.05em 0.3em; border-radius: 4px; }}
  pre {{ background: #1e293b; color: #f1f5f9; border-left: 6px solid #facc15; border-radius: 8px; padding: 0.9rem 1.1rem; overflow-x: auto; font-size: 0.8rem; }}
  pre code {{ background: none; color: inherit; padding: 0; }}
  table {{ border-collapse: collapse; width: 100%; font-size: 0.84rem; }}
  th {{ background: #0f172a; color: #fff; text-align: left; padding: 0.4rem 0.55rem; }}
  td {{ padding: 0.35rem 0.55rem; border-bottom: 1px solid #e2e8f0; vertical-align: top; }}
  td:first-child {{ white-space: nowrap; font-variant-numeric: tabular-nums; }}
  @media print {{ @page {{ size: A4; margin: 12mm 11mm; }} main {{ padding: 0; max-width: none; }}
    pre {{ background: #fff; color: #000; border: 1px solid #94a3b8; break-inside: avoid; }} tr {{ break-inside: avoid; }} }}
</style>
</head>
<body><main>
{body}
</main></body>
</html>
'''
(ROOT / 'slides' / 'board-plan.html').write_text(page, encoding='utf-8')
print(f'board plan written: slides/board-plan.md and .html; optional slides: {[x["n"] for x in opt]}')
