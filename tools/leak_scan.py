#!/usr/bin/env python3
"""Scan a directory tree for strings that must not be published.

    python3 tools/leak_scan.py DIR [--patterns FILE ...] [--no-builtin] [--quiet]

Exit status 0 if nothing was found, 1 if anything was found, 2 on usage errors.

Built-in checks (always on unless --no-builtin):
  * secrets: private-key blocks, GitHub and other well-known token formats, password or token
    assignments with a literal value;
  * split markers: the begin/end markers that delimit private blocks in a working copy
    (a public tree must contain none).

Pattern files hold one Python regular expression per line, matched case-insensitively against
every line of every text file; empty lines and lines starting with '#' are ignored. Keep project
specific patterns (user names, hosts, home paths, private project names, unpublished results) in
such a file, outside the tree you publish.

Use it before deploying a site (`_site/`), before pushing a public repository, and when
generating a public edition of a working copy. Files under .git/ are skipped; binary files are
skipped.
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

SECRETS = [
    ("private key", r"-----BEGIN [A-Z0-9 ]*PRIVATE KEY-----"),
    ("GitHub token", r"\b(?:gh[pousr]_[A-Za-z0-9]{30,}|github_pat_[A-Za-z0-9_]{40,})\b"),
    ("AWS access key", r"\bAKIA[0-9A-Z]{16}\b"),
    ("Slack token", r"\bxox[abprs]-[A-Za-z0-9-]{10,}\b"),
    ("Anthropic or OpenAI key", r"\bsk-(?:ant-)?[A-Za-z0-9_-]{20,}\b"),
    ("secret assignment",
     r"(?i)\b(?:password|passwd|secret|api[_-]?key|access[_-]?token|auth[_-]?token)\b"
     r"\s*[:=]\s*['\"][^'\"\s]{6,}['\"]"),
]
# Case-sensitive, and written so that this file does not match itself.
MARKERS = [("private-block marker", r"(?-i:PRIVATE\s*:\s*(?:BEGIN|END))\b")]


def load_patterns(path: Path) -> list[tuple[str, str]]:
    out = []
    for n, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        s = line.strip()
        if not s or s.startswith("#"):
            continue
        try:
            re.compile(s)
        except re.error as exc:
            raise SystemExit(f"{path}:{n}: bad pattern {s!r}: {exc}")
        out.append((f"{path.name}:{n}", s))
    return out


def text_of(path: Path) -> str | None:
    try:
        data = path.read_bytes()
    except OSError:
        return None
    if b"\0" in data[:8192]:
        return None
    try:
        return data.decode("utf-8")
    except UnicodeDecodeError:
        return data.decode("latin-1")


def scan(root: Path, rules: list[tuple[str, re.Pattern]]) -> list[tuple[str, int, str, str]]:
    hits = []
    for path in sorted(root.rglob("*")):
        if not path.is_file() or ".git" in path.relative_to(root).parts:
            continue
        rel = str(path.relative_to(root))
        # the path itself may leak (for example a directory named after a private project)
        for name, rx in rules:
            if rx.search(rel):
                hits.append((rel, 0, name, rel))
        text = text_of(path)
        if text is None:
            continue
        for n, line in enumerate(text.splitlines(), 1):
            for name, rx in rules:
                m = rx.search(line)
                if m:
                    a = max(0, m.start() - 30)
                    hits.append((rel, n, name, line[a:m.end() + 30].strip()))
    return hits


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("root", type=Path)
    ap.add_argument("--patterns", type=Path, action="append", default=[],
                    help="file with one regular expression per line (repeatable)")
    ap.add_argument("--no-builtin", action="store_true", help="skip the secret and marker checks")
    ap.add_argument("--quiet", action="store_true", help="print only the summary line")
    args = ap.parse_args(argv)
    if not args.root.is_dir():
        print(f"leak_scan: no such directory: {args.root}", file=sys.stderr)
        return 2
    specs: list[tuple[str, str]] = []
    if not args.no_builtin:
        specs += SECRETS + MARKERS
    for p in args.patterns:
        if not p.is_file():
            print(f"leak_scan: no such pattern file: {p}", file=sys.stderr)
            return 2
        specs += load_patterns(p)
    if not specs:
        print("leak_scan: nothing to check (no patterns)", file=sys.stderr)
        return 2
    rules = [(name, re.compile(rx, re.IGNORECASE)) for name, rx in specs]
    hits = scan(args.root, rules)
    if not args.quiet:
        for rel, n, name, excerpt in hits:
            print(f"{rel}:{n}: [{name}] {excerpt}")
    files = len({h[0] for h in hits})
    status = "FAIL" if hits else "ok"
    print(f"leak_scan: {status}: {len(hits)} hit(s) in {files} file(s); "
          f"{len(rules)} pattern(s) checked under {args.root}")
    return 1 if hits else 0


if __name__ == "__main__":
    sys.exit(main())
