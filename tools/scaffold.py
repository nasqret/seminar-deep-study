#!/usr/bin/env python3
"""Scaffold a seminar deep-study project from this skill's templates.

    python3 tools/scaffold.py PROJECT_DIR --title "…" [--speaker "…"] [--date YYYY-MM-DD]
        [--paper "Authors, Title, arXiv:…"] [--seminar "…"] [--length "90 minutes"]
        [--language English] [--lean LeanName] [--cas magma|sage|sympy|pari|none]
        [--cluster] [--site] [--slides] [--book] [--vault] [--verso] [--all]
        [--force] [--dry-run]

Always written: CLAUDE.md, MEMORY.md, JOURNAL.md, PLAN.md, MAINTENANCE.md, README.md, .gitignore,
source/SOURCE.md, artifacts/mathematical/digest.md, artifacts/computational/.
Options add: formal/ (Palomar-format Lean project, `--lean`), cas/ + tools/cert2lean.py +
tools/remote_run.sh (`--cas`), tools/cluster.sh + tools/remote/ (`--cluster`), index.html +
scripts/ + tools/leak_scan.py (`--site`), slides/ (`--slides`), book/ (`--book`), vault/
(`--vault`), verso/ (`--verso`, needs `--lean`). `--all` = all of them.

Placeholders {{TITLE}}, {{SPEAKER}}, {{DATE}}, {{PAPER}}, {{SEMINAR}}, {{LENGTH}}, {{LANGUAGE}},
{{TIME_AND_ROOM}} ("to be announced" unless given — never invented), {{PROJECT}}, {{TODAY}},
{{YEAR}}, {{LEAN_NAME}}, {{CAS}} are filled; every other {{PLACEHOLDER}} is listed at the end for
the agent to fill by hand. Build-time placeholders of the slides ({{SNIP:…}}, {{TIME}}, …) are left
alone. Existing files are never overwritten without --force.
"""
from __future__ import annotations

import argparse
import datetime as dt
import re
import shutil
import sys
from pathlib import Path

SKILL = Path(__file__).resolve().parents[1]
T = SKILL / "templates"
BUILD_TIME = {"TIME", "TM", "NSLIDES", "OPTIONAL", "OPTMIN"}
CAS_NAMES = {"magma": "Magma", "sage": "SageMath", "sympy": "SymPy", "pari": "PARI/GP", "none": "none"}


def plan(args) -> list[tuple[Path, Path]]:
    """(template file, destination relative path) pairs."""
    pairs: list[tuple[Path, Path]] = []

    def tree(src: Path, dst: Path, rename=None):
        for f in sorted(src.rglob("*")):
            if f.is_file() and "__pycache__" not in f.parts and f.name != ".DS_Store":
                rel = f.relative_to(src)
                parts = [rename(p) if rename else p for p in rel.parts]
                pairs.append((f, dst.joinpath(*parts)))

    proj = T / "project"
    for name in ["CLAUDE.md", "MEMORY.md", "JOURNAL.md", "PLAN.md", "MAINTENANCE.md", "README.md"]:
        pairs.append((proj / name, Path(name)))
    pairs.append((proj / "gitignore", Path(".gitignore")))
    pairs.append((proj / "source" / "SOURCE.md", Path("source/SOURCE.md")))
    pairs.append((T / "digest" / "digest.md", Path("artifacts/mathematical/digest.md")))
    pairs.append((T / "digest" / "digest_pdf.py", Path("scripts/digest_pdf.py")))
    pairs.append((T / "digest" / "digest_preamble.tex", Path("scripts/digest_preamble.tex")))
    if args.lean:
        def ren(p: str) -> str:
            return p.replace("LEANNAME", args.lean)
        tree(T / "lean-palomar", Path("formal"), ren)
    if args.cas and args.cas != "none":
        pairs.append((T / "cas" / "remote_run.sh", Path("tools/remote_run.sh")))
        ext = {"magma": "m", "sympy": "py", "sage": "py", "pari": "py"}[args.cas]
        pairs.append((T / "cas" / f"cert_emit.{ext}", Path(f"cas/00_cert_example.{ext}")))
        pairs.append((SKILL / "tools" / "cert2lean.py", Path("tools/cert2lean.py")))
    if args.cluster:
        pairs.append((T / "cluster" / "cluster.sh", Path("tools/cluster.sh")))
        tree(T / "cluster" / "remote", Path("tools/remote"))
    if args.site:
        pairs.append((T / "site" / "index.html", Path("index.html")))
        pairs.append((T / "site" / "htaccess", Path(".htaccess")))
        tree(T / "site" / "scripts", Path("scripts"))
        pairs.append((SKILL / "tools" / "leak_scan.py", Path("tools/leak_scan.py")))
    if args.slides:
        tree(T / "slides", Path("slides"))
    if args.book:
        tree(T / "book", Path("book"))
    if args.vault:
        tree(T / "vault", Path("vault"))
    if args.verso:
        tree(T / "verso", Path("verso"), lambda p: ".gitignore" if p == "gitignore" else p)
    return pairs


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Scaffold a seminar deep-study project.")
    ap.add_argument("project", type=Path)
    ap.add_argument("--title", required=True)
    ap.add_argument("--speaker", default="{{SPEAKER}}")
    ap.add_argument("--date", default="{{DATE}}", help="date of the talk")
    ap.add_argument("--paper", default="{{PAPER}}")
    ap.add_argument("--seminar", default="{{SEMINAR}}")
    ap.add_argument("--length", default="90 minutes")
    ap.add_argument("--language", default="English")
    ap.add_argument("--time-and-room", default="to be announced")
    ap.add_argument("--lean", metavar="LeanName", help="Lean library name, e.g. Lines85")
    ap.add_argument("--cas", choices=sorted(CAS_NAMES), default=None)
    for flag in ["cluster", "site", "slides", "book", "vault", "verso", "all"]:
        ap.add_argument(f"--{flag}", action="store_true")
    ap.add_argument("--force", action="store_true", help="overwrite existing files")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args(argv)
    if args.all:
        args.cluster = args.site = args.slides = args.book = args.vault = True
        args.verso = bool(args.lean)
        args.cas = args.cas or "magma"
    if args.lean and not re.fullmatch(r"[A-Z][A-Za-z0-9_]*", args.lean):
        print("scaffold: --lean must be a Lean identifier starting with a capital letter", file=sys.stderr)
        return 2
    if args.lean and args.lean.lower() in {"demo", "scripts", "verification", "challenge", "solution",
                                           "audit", "axiomaudit"}:
        # formal/ already has these names; on a case-insensitive file system they would collide
        print(f"scaffold: --lean {args.lean} clashes with a file or directory of formal/", file=sys.stderr)
        return 2
    if args.verso and not args.lean:
        print("scaffold: --verso needs --lean (the document compiles against the library)", file=sys.stderr)
        return 2

    today = dt.date.today()
    values = {
        "TITLE": args.title, "SPEAKER": args.speaker, "DATE": args.date, "PAPER": args.paper,
        "SEMINAR": args.seminar, "LENGTH": args.length, "LANGUAGE": args.language,
        "TIME_AND_ROOM": args.time_and_room, "PROJECT": args.project.name,
        "TODAY": today.isoformat(), "YEAR": str(today.year),
        "CAS": CAS_NAMES.get(args.cas or "none", "none"),
    }
    if args.lean:
        values["LEAN_NAME"] = args.lean

    pairs = plan(args)
    root = args.project.expanduser()
    clashes = [dst for _, dst in pairs if (root / dst).exists()]
    if clashes and not args.force:
        print("scaffold: these files exist (use --force to overwrite):", file=sys.stderr)
        for c in clashes:
            print("  ", c, file=sys.stderr)
        return 1

    left: dict[str, set[str]] = {}
    for src, dst in pairs:
        target = root / dst
        data = src.read_bytes()
        try:
            text = data.decode("utf-8")
        except UnicodeDecodeError:
            text = None
        if text is not None:
            for k, v in values.items():
                text = text.replace("{{" + k + "}}", v)
            for name in re.findall(r"\{\{([A-Z_]+)\}\}", text):
                if name not in BUILD_TIME:
                    left.setdefault(name, set()).add(str(dst))
            data = text.encode("utf-8")
        if args.dry_run:
            print("would write", dst)
            continue
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(data)
        shutil.copymode(src, target)
    if not args.dry_run:
        for d in ["artifacts/computational", "cas/out"] if args.cas else ["artifacts/computational"]:
            (root / d).mkdir(parents=True, exist_ok=True)
            keep = root / d / ".gitkeep"
            if not any((root / d).iterdir()):
                keep.touch()
    print(f"scaffold: {len(pairs)} file(s) {'planned' if args.dry_run else 'written'} in {root}")
    if left:
        print("placeholders left for you to fill:")
        for name in sorted(left):
            files = sorted(left[name])
            more = f" (+{len(files) - 3} more)" if len(files) > 3 else ""
            print(f"  {{{{{name}}}}}: {', '.join(files[:3])}{more}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
