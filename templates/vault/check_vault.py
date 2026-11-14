#!/usr/bin/env python3
r"""Check an Obsidian vault: every [[wikilink]] resolves to a note, and no note is an orphan.

    python3 -I vault/check_vault.py [vault]      (default: the directory of this script)

A link [[Name]], [[Name|alias]], [[Name\|alias]] (inside tables) or [[Name#heading]] resolves
when some note is called Name.md (anywhere in the vault; Obsidian's "shortest" link format). An orphan is a note that no other
note links to (Home.md and templates are exempt). Exit status 1 if a link is broken.
"""
import re
import sys
from pathlib import Path

root = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).resolve().parent
notes = {p.stem: p for p in root.rglob("*.md") if ".obsidian" not in p.parts and ".trash" not in p.parts}
LINK = re.compile(r"\[\[([^\]|#]+)(?:#[^\]|]*)?(?:\|[^\]]*)?\]\]")
broken, linked = [], set()
for name, path in sorted(notes.items()):
    if "template" in name.lower():          # templates hold placeholder links
        continue
    for target in LINK.findall(path.read_text(encoding="utf-8")):
        t = target.strip().rstrip("\\")   # inside tables the alias bar is escaped: [[Note\|alias]]
        if t.endswith(".md"):
            t = t[:-3]
        t = t.split("/")[-1]
        if t in notes:
            linked.add(t)
        else:
            broken.append((str(path.relative_to(root)), target))
orphans = [n for n in sorted(notes) if n not in linked and n != "Home" and "template" not in n.lower()]
for page, target in broken:
    print(f"BROKEN  {page} -> [[{target}]]")
for n in orphans:
    print(f"ORPHAN  {notes[n].relative_to(root)}")
print(f"{len(notes)} notes, {len(broken)} broken links, {len(orphans)} orphans")
sys.exit(1 if broken else 0)
