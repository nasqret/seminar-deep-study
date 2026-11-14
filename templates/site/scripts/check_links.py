#!/usr/bin/env python3
"""Check the local links of an assembled site (`_site/`) and find nested <a> elements.

    python3 -I scripts/check_links.py _site [--base https://example.org/<project>/]

For every HTML page, each href/src that points inside the site must exist (http(s), mailto,
javascript and pure anchors are skipped; absolute URLs under --base are treated as local).
A nested <a> (a card wrapped in a link that contains other links) is invalid HTML: the browser
closes the outer link early and the layout breaks. Exit status 1 if anything is wrong.
"""
from __future__ import annotations

import argparse
import re
import sys
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit

ATTR = re.compile(r'\b(?:href|src)\s*=\s*"([^"]+)"', re.I)


class NestedA(HTMLParser):
    """Collects the line numbers where an <a> opens inside another <a>."""

    def __init__(self) -> None:
        super().__init__()
        self.depth, self.lines = 0, []

    def handle_starttag(self, tag, attrs):
        if tag == "a":
            if self.depth:
                self.lines.append(self.getpos()[0])
            self.depth += 1

    def handle_endtag(self, tag):
        if tag == "a" and self.depth:
            self.depth -= 1


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("site", type=Path)
    ap.add_argument("--base", default="", help="public URL of the site root (optional)")
    args = ap.parse_args(argv)
    site, base = args.site, args.base
    if base and not base.endswith("/"):
        base += "/"
    missing, nested, checked = [], [], 0
    for page in sorted(site.rglob("*.html")):
        if "_static" in page.parts:          # Sphinx theme templates, not pages
            continue
        text = page.read_text(encoding="utf-8", errors="replace")
        parser = NestedA()
        parser.feed(text)
        nested += [(str(page.relative_to(site)), n) for n in parser.lines]
        for url in ATTR.findall(text):
            if "{{" in url:
                continue
            if base and url.startswith(base):
                target = site / unquote(urlsplit(url[len(base):]).path)
            elif re.match(r"^[a-z][a-z0-9+.-]*:", url, re.I) or url.startswith(("#", "//")):
                continue
            else:
                path = unquote(urlsplit(url).path)
                if not path or path.startswith("/"):
                    continue
                target = page.parent / path
            checked += 1
            if target.is_dir():
                target = target / "index.html"
            if not target.exists():
                missing.append((str(page.relative_to(site)), url))
    for page, url in missing:
        print(f"MISSING  {page}  ->  {url}")
    for page, line in nested:
        print(f"NESTED <a>  {page}:{line}")
    print(f"checked {checked} links: {len(missing)} missing, {len(nested)} nested <a>")
    return 1 if missing or nested else 0


if __name__ == "__main__":
    sys.exit(main())
