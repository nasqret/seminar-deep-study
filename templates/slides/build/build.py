#!/usr/bin/env python3
"""Assemble slides/seminar.html from the parts slides/build/NN_*.html (in name order).

    python3 -I slides/build/build.py            # from anywhere; re-run whenever sources change

Placeholders in the parts:
  {{SNIP:name}}    exact, HTML-escaped lines of a repository file, located by TEXT ANCHORS
                   (SNIPS below), so the snippet follows the file when its line numbers change
  {{LN:name}}      first line number of that snippet;  {{LINES:name}} -> "a–b"
  {{GREP:name}}    the lines of a file that match a regex (GREPS), e.g. the comparator verdicts
  {{COUNT:name}}   a number captured by a regex from a file (COUNTS), e.g. the audit count
  {{WC:path}}      "N lines" of a repository file (path relative to the project root)
  {{TIME}} {{TM}}  minute marks computed from the sections' data-timing attributes (seconds)

Checks (exit status 1 if any fails): every <section> has data-timing; the total is
TALK_MINUTES; no placeholder is left; every <pre><code> block is a verbatim excerpt of a file
matched by VERBATIM_SOURCES. So no number is typed by hand and no code is retyped.
The timeline (slide, minutes, cues) is printed and returned for boardplan.py.
"""
import html
import pathlib
import re
import sys

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parent.parent                      # the project root (slides/build/ -> project)
OUT = ROOT / 'slides' / 'seminar.html'
TALK_MINUTES = 90

# name: (file, start anchor, end anchor or number of lines [, line offset from the start anchor])
SNIPS = {
    'challenge_stmt': ('formal/Challenge.lean', '/-- Example statement', '  sorry'),
    'demo_cert': ('formal/demo/LiveDemo.lean', 'example {K : Type*} [Field K] [CharZero K] {r : K}', 3),
}
# name: (file, regex) -> every matching line
GREPS = {
    'comparator': ('formal/verification/logs/comparator.log', r'WARNING|accepts|okay'),
}
# name: (file, regex with one group) -> the captured text of the first match
COUNTS = {
    'AUDIT_N': ('formal/verification/logs/build.log', r'Axiom allowlist passed for (\d+)'),
}
# files whose lines may appear in code blocks
VERBATIM_SOURCES = ['formal/**/*.lean', 'formal/*.json', 'formal/*.yaml', 'formal/verification/logs/*',
                    'cas/*', 'cas/out/*', 'magma/*', 'magma/out/*', 'tools/*.py', 'tools/*.sh']


def lines_of(path):
    p = ROOT / path
    if not p.is_file():
        sys.exit(f'missing file {path} (needed by a placeholder)')
    return p.read_text(encoding='utf-8').split('\n')


def extract(name):
    if name not in SNIPS:
        sys.exit(f'unknown snippet {name!r}: add it to SNIPS')
    spec = SNIPS[name]
    path, start = spec[0], spec[1]
    end = spec[2] if len(spec) > 2 else 1
    offset = spec[3] if len(spec) > 3 else 0
    L = lines_of(path)
    try:
        s0 = next(i for i, l in enumerate(L) if start in l)
    except StopIteration:
        sys.exit(f'snippet {name}: start anchor not found in {path}: {start!r}')
    s = s0 + offset
    if isinstance(end, int):
        e = s + end - 1
    else:
        try:
            e = next(i for i in range(s0, len(L)) if end in L[i])
        except StopIteration:
            sys.exit(f'snippet {name}: end anchor not found in {path}: {end!r}')
    return path, s + 1, e + 1, L[s:e + 1]


def grep(name):
    path, rx = GREPS[name]
    return [l for l in lines_of(path) if re.search(rx, l)]


def count(name):
    if name not in COUNTS:
        sys.exit(f'unknown count {name!r}: add it to COUNTS')
    path, rx = COUNTS[name]
    m = re.search(rx, '\n'.join(lines_of(path)))
    if not m:
        sys.exit(f'count {name}: no match for {rx!r} in {path}')
    return m.group(1)


def fmt(s):
    return f'{s // 60}:{s % 60:02d}'


def build():
    parts = sorted(p for p in HERE.glob('[0-9][0-9]_*.html'))
    if not parts:
        sys.exit(f'no parts NN_*.html in {HERE}')
    src = ''.join(p.read_text(encoding='utf-8') for p in parts)
    used = {}

    def snip(m):
        path, a, b, L = extract(m.group(1))
        used[m.group(1)] = (path, a, b)
        return html.escape('\n'.join(L), quote=False)

    src = re.sub(r'\{\{SNIP:(\w+)\}\}', snip, src)
    src = re.sub(r'\{\{LN:(\w+)\}\}', lambda m: str(extract(m.group(1))[1]), src)

    def rng(m):
        _, a, b, _ = extract(m.group(1))
        return f'{a}' if a == b else f'{a}–{b}'

    src = re.sub(r'\{\{LINES:(\w+)\}\}', rng, src)
    src = re.sub(r'\{\{GREP:(\w+)\}\}', lambda m: html.escape('\n'.join(grep(m.group(1))), quote=False), src)
    src = re.sub(r'\{\{COUNT:(\w+)\}\}', lambda m: count(m.group(1)), src)
    src = re.sub(r'\{\{WC:([\w./-]+)\}\}', lambda m: f"{len(lines_of(m.group(1))) - 1} lines", src)

    # minute marks: sections are not nested
    head, sep, rest = src.partition('<div class="slides">')
    if not sep:
        sys.exit('no <div class="slides"> in the parts')
    pieces = re.split(r'(?=<section[\s>])', rest)
    t, timeline, out = 0, [], [head, sep]
    for piece in pieces:
        if not piece.startswith('<section'):
            out.append(piece)
            continue
        m = re.match(r'<section[^>]*data-timing="(\d+)"', piece)
        if not m:
            sys.exit(f'section without data-timing: {piece[:120]}')
        d = int(m.group(1))
        a, b = t, t + d
        t = b
        piece = piece.replace('{{TIME}}', f'<p><b>⏱ {fmt(a)}–{fmt(b)} ({d / 60:g} min)</b></p>')
        piece = piece.replace('{{TM}}', f' · {fmt(a)}–{fmt(b)}')
        title = re.search(r'<h[12][^>]*>(.*?)</h[12]>', piece, re.S)
        title = re.sub(r'<[^>]+>', '', re.sub(r'<br\s*/?>', ' ', title.group(1))) if title else '?'
        title = re.sub(r'\s+', ' ', html.unescape(title)).strip()
        cues = re.findall(r'class="cue cue-(board|live|opt|pending)[^"]*"[^>]*>([^<]*)', piece)
        timeline.append({'n': len(timeline) + 1, 'title': title, 'start': fmt(a), 'end': fmt(b), 'sec': d,
                         'cues': [c[0] + (':' + c[1].strip() if c[1].strip() else '') for c in cues]})
        out.append(piece)
    src = ''.join(out)
    if t != TALK_MINUTES * 60:
        sys.exit(f'total time {t / 60:g} min != {TALK_MINUTES} min: adjust data-timing')
    left = sorted(set(re.findall(r'\{\{[A-Z_]+(?::[\w./-]+)?\}\}', src)))
    if left:
        sys.exit(f'unresolved placeholders: {left}')
    OUT.write_text(src, encoding='utf-8')
    return src, timeline, used


def verify(src):
    """Every <pre><code> block must be a verbatim excerpt of a repository file."""
    files = {}
    for pat in VERBATIM_SOURCES:
        for p in ROOT.glob(pat):
            if p.is_file() and '.lake' not in p.parts:
                files[str(p.relative_to(ROOT))] = p.read_text(encoding='utf-8', errors='replace')
    all_lines = set()
    for content in files.values():
        all_lines.update(content.split('\n'))
    blocks = re.findall(r'<pre[^>]*>\s*<code[^>]*>(.*?)</code>\s*</pre>', src, re.S)
    bad = 0
    for blk in blocks:
        text = html.unescape(blk)
        if any(text in content for content in files.values()):
            continue
        if all(line in all_lines for line in text.split('\n')):
            continue
        bad += 1
        print('NOT VERBATIM:', text[:200].replace('\n', ' | '))
    print(f'{len(blocks)} code blocks checked, {bad} not verbatim')
    return bad == 0


if __name__ == '__main__':
    src, timeline, used = build()
    ok = verify(src)
    print(f'{len(timeline)} slides, total {sum(x["sec"] for x in timeline) / 60:g} min -> {OUT}')
    for x in timeline:
        print(f'{x["n"]:>2} {x["start"]:>5}–{x["end"]:<5} {x["sec"] / 60:>4g}  {x["title"][:70]:<70} {" ".join(x["cues"])}')
    sys.exit(0 if ok else 1)
