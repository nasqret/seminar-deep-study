#!/usr/bin/env python3
"""Find candidate papers for a seminar on arXiv: profile, scan, rank, count pages.

    python3 -I arxiv_scan.py author LASTNAME [--max 100]
    python3 -I arxiv_scan.py scan --profile profile.json --out hits.json [--since D --until D]
    python3 -I arxiv_scan.py rank hits.json --profile profile.json [--out ranked.json] [--top 40]
    python3 -I arxiv_scan.py pages ID [ID ...] [--keep DIR]

Standard library only (`pages` uses pypdf when it is installed, for example via
`uv run --no-project --with pypdf python -I arxiv_scan.py pages ...`).

author   lists an author's arXiv papers with categories, co-authors and frequent title words:
         the raw material for an interest profile. The query is arXiv's `au:` field.
scan     queries the arXiv API once per topic of the profile, restricted to its categories and a
         date window, pausing between calls as the API asks, and writes the de-duplicated hits.
rank     scores the hits against the profile and prints a table (score, date, id, pages,
         categories, title, authors).
pages    downloads PDFs and counts pages (pypdf, else a heuristic over the PDF's streams; the
         method is printed). Pages stated in the comments field are only a hint.

Profile (JSON):
    {
      "categories": ["math.NT", "math.AG"],      arXiv categories to search
      "window_days": 60,                          recency window, ending today (UTC)
      "max_pages": 15,                            page limit (bonus within, penalty beyond)
      "topics": {"elliptic surface": 3, ...},     phrase -> weight; each phrase is searched as
                                                  abs:"phrase"; a key containing ':' is used as
                                                  a raw arXiv query (e.g. 'abs:x AND abs:y')
      "keywords": {"Mordell.Weil lattice": 3},    regex -> weight, matched in title + abstract
      "cross_list_bonus": 1.5                     bonus when listed in 2+ of the categories
    }

Score = sum of weights of the topics whose query found the paper + sum of weights of matching
keywords + cross-list bonus + page term (+2 within max_pages, +0.5 within max_pages + 5,
-3 beyond, 0 if unknown). Read the top of the list yourself; the score only orders the reading.

Network etiquette: one API call every 3 seconds (arXiv's request), a generic User-Agent, and no
personal data in requests.
"""
from __future__ import annotations

import argparse
import collections
import datetime as dt
import io
import json
import re
import sys
import time
import urllib.parse
import urllib.request
import zlib
from pathlib import Path

API = "http://export.arxiv.org/api/query?"
NS = {"a": "http://www.w3.org/2005/Atom", "x": "http://arxiv.org/schemas/atom"}
UA = "seminar-deep-study/1.0 (arxiv_scan.py)"
PAUSE = 3.0
STOP = set("""a an and the of on in for to with by from at as is are be its their this that
these those via over under into new some any all one two three non using towards toward between
about without within than""".split())


def fetch(url: str, timeout: int = 90) -> bytes:
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read()


def api(query: str, n: int = 200) -> list[dict]:
    import xml.etree.ElementTree as ET
    url = API + urllib.parse.urlencode({"search_query": query, "sortBy": "submittedDate",
                                        "sortOrder": "descending", "max_results": n})
    root = ET.fromstring(fetch(url))
    out = []
    for e in root.findall("a:entry", NS):
        cmt = e.find("x:comment", NS)
        prim = e.find("x:primary_category", NS)
        comment = " ".join(cmt.text.split()) if cmt is not None and cmt.text else ""
        out.append({
            "id": e.find("a:id", NS).text.rsplit("/", 1)[-1],
            "published": e.find("a:published", NS).text[:10],
            "updated": e.find("a:updated", NS).text[:10],
            "title": " ".join(e.find("a:title", NS).text.split()),
            "authors": [a.find("a:name", NS).text for a in e.findall("a:author", NS)],
            "cats": [c.attrib["term"] for c in e.findall("a:category", NS)],
            "primary": prim.attrib.get("term") if prim is not None else None,
            "comment": comment,
            "pages": pages_from_comment(comment),
            "abstract": " ".join(e.find("a:summary", NS).text.split()),
        })
    return out


def pages_from_comment(comment: str) -> int | None:
    m = re.search(r"(\d+)\s*(?:pp\b|pages?\b)", comment, re.I)
    return int(m.group(1)) if m else None


def base_id(arxiv_id: str) -> str:
    return re.sub(r"v\d+$", "", arxiv_id)


# ----------------------------------------------------------------------------------- author ---
def cmd_author(args) -> int:
    papers = api(f"au:{args.name}", args.max)
    if not papers:
        print("no papers found (try another spelling, e.g. without diacritics)")
        return 1
    cats, coauthors, words = collections.Counter(), collections.Counter(), collections.Counter()
    for p in papers:
        print(f"{p['published']} {p['id']:<16} [{','.join(p['cats'][:3])}] {p['title']}")
        print(f"    {', '.join(p['authors'])}")
        cats.update(p["cats"])
        coauthors.update(a for a in p["authors"] if args.name.lower() not in a.lower())
        title = re.sub(r"\$[^$]*\$", " ", p["title"].lower())
        toks = [t for t in re.findall(r"[a-z][a-z'-]+", title) if t not in STOP and len(t) > 2]
        words.update(toks)
        words.update(" ".join(pair) for pair in zip(toks, toks[1:]))
    print(f"\n{len(papers)} papers")
    print("categories:", ", ".join(f"{c} ({k})" for c, k in cats.most_common(8)))
    print("co-authors:", ", ".join(f"{c} ({k})" for c, k in coauthors.most_common(12)))
    print("title terms:", ", ".join(f"{w} ({k})" for w, k in words.most_common(40) if k > 1))
    return 0


# ------------------------------------------------------------------------------------- scan ---
def load_profile(path: Path) -> dict:
    prof = json.loads(path.read_text(encoding="utf-8"))
    for key in ("categories", "topics"):
        if not prof.get(key):
            raise SystemExit(f"profile {path}: '{key}' is required")
    return prof


def topic_query(topic: str) -> str:
    return topic if ":" in topic else f'abs:"{topic}"'


def cmd_scan(args) -> int:
    prof = load_profile(args.profile)
    until = dt.date.fromisoformat(args.until) if args.until else dt.datetime.now(dt.timezone.utc).date()
    since = dt.date.fromisoformat(args.since) if args.since else until - dt.timedelta(
        days=int(prof.get("window_days", 60)))
    window = f"submittedDate:[{since:%Y%m%d}0000 TO {until:%Y%m%d}2359]"
    cats = "(" + " OR ".join(f"cat:{c}" for c in prof["categories"]) + ")"
    hits: dict[str, dict] = {}
    topics = list(prof["topics"])
    for i, topic in enumerate(topics):
        q = f"{cats} AND ({topic_query(topic)}) AND {window}"
        try:
            res = api(q, args.max)
        except Exception as exc:  # noqa: BLE001 - report and continue with the next topic
            print(f"ERR  {topic}: {exc}", file=sys.stderr)
            res = []
        for r in res:
            h = hits.setdefault(base_id(r["id"]), r)
            h["topics"] = sorted(set(h.get("topics", [])) | {topic})
        print(f"{len(res):4d}  {topic}", file=sys.stderr)
        if i + 1 < len(topics):
            time.sleep(PAUSE)
    rows = sorted(hits.values(), key=lambda r: r["published"], reverse=True)
    args.out.write_text(json.dumps(rows, indent=1, ensure_ascii=False), encoding="utf-8")
    short = [r for r in rows if r["pages"] is None or r["pages"] <= int(prof.get("max_pages", 15))]
    print(f"{len(rows)} unique papers {since}..{until} in {', '.join(prof['categories'])}; "
          f"{len(short)} within the page limit or of unknown length -> {args.out}")
    return 0


# ------------------------------------------------------------------------------------- rank ---
def topic_weight(prof: dict, topic: str) -> float:
    """Weight of a topic; hits written by older scans store the raw query abs:"phrase"."""
    if topic in prof["topics"]:
        return float(prof["topics"][topic])
    m = re.fullmatch(r'abs:"([^"]+)"', topic)
    return float(prof["topics"].get(m.group(1), 0)) if m else 0.0


def score(paper: dict, prof: dict) -> float:
    s = sum(topic_weight(prof, t) for t in paper.get("topics", []))
    text = paper["title"] + " " + paper["abstract"]
    s += sum(float(w) for k, w in prof.get("keywords", {}).items() if re.search(k, text, re.I))
    if len(set(paper["cats"]) & set(prof["categories"])) >= 2:
        s += float(prof.get("cross_list_bonus", 0))
    p = paper.get("pages") or pages_from_comment(paper.get("comment", ""))
    limit = int(prof.get("max_pages", 15))
    if p is not None:
        s += 2 if p <= limit else 0.5 if p <= limit + 5 else -3
    return round(s, 1)


def cmd_rank(args) -> int:
    prof = load_profile(args.profile)
    rows = json.loads(args.hits.read_text(encoding="utf-8"))
    for r in rows:
        r["pages"] = r.get("pages") or pages_from_comment(r.get("comment", ""))
        r["score"] = score(r, prof)
    rows.sort(key=lambda r: (-r["score"], r["published"]))
    if args.out:
        args.out.write_text(json.dumps(rows, indent=1, ensure_ascii=False), encoding="utf-8")
    for r in rows[:args.top]:
        a = ", ".join(r["authors"][:3]) + (" et al." if len(r["authors"]) > 3 else "")
        cats = ",".join(c for c in r["cats"] if "." in c)[:28]
        print(f"{r['score']:5.1f} {r['published']} {r['id']:<15} p={str(r.get('pages')):>4} "
              f"[{cats}] {r['title'][:100]} — {a}")
    return 0


# ------------------------------------------------------------------------------------ pages ---
def count_pages(data: bytes) -> tuple[int | None, str]:
    try:
        import pypdf  # type: ignore
        return len(pypdf.PdfReader(io.BytesIO(data)).pages), "pypdf"
    except ImportError:
        pass
    except Exception:  # noqa: BLE001 - fall back to the heuristic
        pass
    chunks = [data]
    for m in re.finditer(rb"stream\r?\n(.*?)\r?\nendstream", data, re.S):
        try:
            chunks.append(zlib.decompress(m.group(1)))
        except zlib.error:
            continue
    blob = b"\n".join(chunks)
    counts = [int(x) for x in re.findall(rb"/Type\s*/Pages\b[^>]*?/Count\s+(\d+)", blob)]
    counts += [int(x) for x in re.findall(rb"/Count\s+(\d+)[^>]*?/Type\s*/Pages\b", blob)]
    if counts:
        return max(counts), "heuristic (/Pages /Count)"
    n = len(re.findall(rb"/Type\s*/Page(?![s\w])", blob))
    return (n or None), "heuristic (/Type /Page)"


def cmd_pages(args) -> int:
    keep = args.keep
    if keep:
        keep.mkdir(parents=True, exist_ok=True)
    for i, aid in enumerate(args.ids):
        try:
            data = fetch(f"https://arxiv.org/pdf/{aid}")
        except Exception as exc:  # noqa: BLE001
            print(f"{aid}: download failed: {exc}")
            continue
        if keep:
            (keep / f"{aid.replace('/', '_')}.pdf").write_bytes(data)
        n, how = count_pages(data)
        print(f"{aid}: {n} pages ({how})")
        if i + 1 < len(args.ids):
            time.sleep(PAUSE)
    return 0


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="arXiv profile, scan, rank and page counts")
    sub = ap.add_subparsers(dest="cmd", required=True)
    a = sub.add_parser("author", help="an author's papers, categories, co-authors, title terms")
    a.add_argument("name")
    a.add_argument("--max", type=int, default=100)
    s = sub.add_parser("scan", help="query arXiv for every topic of a profile")
    s.add_argument("--profile", type=Path, required=True)
    s.add_argument("--out", type=Path, required=True)
    s.add_argument("--since", help="YYYY-MM-DD (default: today minus window_days)")
    s.add_argument("--until", help="YYYY-MM-DD (default: today, UTC)")
    s.add_argument("--max", type=int, default=200, help="results per topic query")
    r = sub.add_parser("rank", help="score hits against a profile")
    r.add_argument("hits", type=Path)
    r.add_argument("--profile", type=Path, required=True)
    r.add_argument("--out", type=Path)
    r.add_argument("--top", type=int, default=40)
    p = sub.add_parser("pages", help="download PDFs and count pages")
    p.add_argument("ids", nargs="+")
    p.add_argument("--keep", type=Path, help="directory to keep the PDFs in")
    args = ap.parse_args(argv)
    return {"author": cmd_author, "scan": cmd_scan, "rank": cmd_rank, "pages": cmd_pages}[args.cmd](args)


if __name__ == "__main__":
    sys.exit(main())
