"""Refresh the verbatim library excerpts in the Verso document.

Every ```libcode "PATH"``` block in Doc/**/*.lean starts with a line `theorem NAME ...` (or
`set_option ... in` followed by such a line).  This script replaces the body of each block with the
current text of declaration NAME in PATH (relative to verso/): from its `theorem` line down to the
last line of its proof, verbatim.  The document build then re-checks (Doc/Meta.lean, `libcode`) that
the block is still a verbatim excerpt, and re-elaborates it.

Usage (from verso/):  python3 -I scripts/refresh_excerpts.py [--check]
With --check nothing is written; the exit status is 1 if some excerpt is out of date.
"""
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
BLOCK = re.compile(r'^```libcode "([^"]+)"([^\n]*)\n(.*?)^```$', re.S | re.M)
STARTS = ("/--", "theorem", "omit", "end", "/-!", "noncomputable", "def", "set_option", "@[",
          "lemma", "instance", "structure", "namespace", "section", "variable", "open")


def extract(path: pathlib.Path, name: str) -> str:
    lines = path.read_text().split("\n")
    try:
        start = next(i for i, l in enumerate(lines) if re.match(rf"^theorem {re.escape(name)}\b", l))
    except StopIteration:
        sys.exit(f"error: theorem {name} not found in {path}")
    end = start + 1
    while end < len(lines):
        if lines[end] == "" and (end + 1 >= len(lines) or lines[end + 1].startswith(STARTS)):
            break
        end += 1
    return "\n".join(lines[start:end]).rstrip() + "\n"


def main() -> int:
    check = "--check" in sys.argv
    stale = 0
    for doc in sorted((ROOT / "Doc").rglob("*.lean")):
        text = doc.read_text()

        def repl(m: re.Match) -> str:
            nonlocal stale
            src, opts, body = m.group(1), m.group(2), m.group(3)
            head = re.search(r"^theorem (\S+)", body, re.M)
            if not head:
                sys.exit(f"error: {doc}: libcode block without a `theorem NAME` line")
            new = extract((ROOT / src).resolve(), head.group(1))
            if new != body:
                stale += 1
                print(f"{'stale' if check else 'refreshed'}: {doc.relative_to(ROOT)}: {head.group(1)}")
            return f'```libcode "{src}"{opts}\n{new}```'

        new_text = BLOCK.sub(repl, text)
        if not check and new_text != text:
            doc.write_text(new_text)
    return 1 if (check and stale) else 0


if __name__ == "__main__":
    sys.exit(main())
