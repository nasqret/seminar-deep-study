"""Consistency tests for the skill: frontmatter, paths, links, tools, scaffold, installer.

    python3 -m unittest discover -s tests -v

Standard library only; nothing touches the network.
"""
import importlib.util
import json
import os
import re
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
TOOLS = REPO / "tools"
PY = sys.executable
TEXTS = ["SKILL.md", "README.md", "MAINTAINING.md", "CHANGELOG.md", "examples/README.md",
         "examples/prompts.md", *[str(p.relative_to(REPO)) for p in sorted((REPO / "references").glob("*.md"))],
         *[str(p.relative_to(REPO)) for p in sorted((REPO / "templates" / "briefs").glob("*.md"))]]
# paths that live in the user's project (copied there by tools/scaffold.py), not in this repository
PROJECT_SIDE = {"tools/cluster.sh", "tools/remote_run.sh", "tools/remote", "tools/remote/shallow_deps.py"}


def load(name):
    spec = importlib.util.spec_from_file_location(name, TOOLS / f"{name}.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def frontmatter():
    """Parse the frontmatter strictly enough to catch what YAML parsers reject (stdlib only)."""
    text = (REPO / "SKILL.md").read_text(encoding="utf-8")
    m = re.match(r"^---\n(.*?)\n---\n", text, re.S)
    assert m, "SKILL.md must start with a frontmatter block"
    out = {}
    for line in m.group(1).splitlines():
        k, _, v = line.partition(": ")
        v = v.strip()
        if v[:1] == "'":
            assert v.endswith("'") and "'" not in v[1:-1].replace("''", ""), f"{k}: bad single quoting"
            v = v[1:-1].replace("''", "'")
        elif v[:1] == '"':
            assert v.endswith('"'), f"{k}: bad double quoting"
            v = v[1:-1]
        else:
            assert ": " not in v and " #" not in v, f"{k}: quote this value"
        out[k.strip()] = v
    return out


class Frontmatter(unittest.TestCase):
    def test_name_and_description(self):
        fm = frontmatter()
        self.assertEqual(fm.get("name"), "seminar-deep-study")
        d = fm.get("description", "")
        self.assertTrue(0 < len(d) <= 1024, f"description has {len(d)} characters (limit 1024)")
        self.assertNotRegex(d, r"[<>]", "no angle brackets in the description")
        for word in ("seminar", "topic", "Lean", "computer algebra", "slides", "dashboard"):
            self.assertIn(word, d)

    def test_skill_md_length(self):
        self.assertLess(len((REPO / "SKILL.md").read_text(encoding="utf-8").splitlines()), 300)


class References(unittest.TestCase):
    def test_paths_mentioned_exist(self):
        pat = re.compile(r"`((?:references|templates|examples|tools|tests|private)/[A-Za-z0-9_./-]+)`")
        for f in TEXTS:
            for path in pat.findall((REPO / f).read_text(encoding="utf-8")):
                path = path.split("#")[0].rstrip("/.")
                if any(c in path for c in "<*{…") or path in PROJECT_SIDE:
                    continue
                self.assertTrue((REPO / path).exists(), f"{f} mentions {path}, which does not exist")

    def test_relative_links_resolve(self):
        link = re.compile(r"\]\(([^)\s]+)\)")
        for f in TEXTS:
            base = (REPO / f).parent
            for target in link.findall((REPO / f).read_text(encoding="utf-8")):
                if re.match(r"^(https?:|mailto:|#)", target):
                    continue
                self.assertTrue((base / target.split("#")[0]).exists(), f"{f} links to {target}")

    def test_no_secrets_anywhere(self):
        leak = load("leak_scan")
        rules = [(n, re.compile(rx)) for n, rx in leak.SECRETS]
        hits = leak.scan(REPO, rules)
        self.assertEqual(hits, [], f"secrets found: {hits[:3]}")


class Tools(unittest.TestCase):
    def test_cert2lean_reproduces_the_example(self):
        out = subprocess.run([PY, "-I", str(TOOLS / "cert2lean.py"), str(REPO / "examples/cert/sample.out"),
                              "--namespace", "Demo.Cert"], capture_output=True, text=True, check=True).stdout
        self.assertEqual(out, (REPO / "examples/cert/Sample.lean").read_text(encoding="utf-8"))
        self.assertIn("linear_combination (1/12*r^2 - 1/3) * h + (-1/48*r^3 + 7/48*r) * h'", out)
        self.assertIn("    False := by", out)

    def test_cert2lean_rejects_bad_input(self):
        c2l = load("cert2lean")
        bad = ["CERT x\nVARS r\nHYP h := r^2 + s\nGOAL := 1\nCOEF h := 1\nEND\n",            # undeclared
               "CERT x\nVARS r\nHYP h := r := by sorry\nGOAL := 1\nCOEF h := 1\nEND\n",       # injection
               "CERT x\nVARS r\nHYP h := r\nGOAL := 0\nCOEF h := 1\nEND\n",                   # nothing to prove
               "CERT x\nVARS r\nHYP h := r\nGOAL := 1\nCOEF h := 1\n"]                         # no END
        for text in bad:
            with tempfile.TemporaryDirectory() as d:
                p = Path(d) / "t.out"
                p.write_text(text)
                with self.assertRaises(c2l.CertError, msg=text):
                    for b in c2l.parse([p]):
                        c2l.render(b)

    def test_arxiv_rank_scores(self):
        ax = load("arxiv_scan")
        prof = {"categories": ["math.NT", "math.AG"], "max_pages": 15, "cross_list_bonus": 1.5,
                "topics": {"elliptic surface": 3}, "keywords": {"Mordell.Weil": 2}}
        paper = {"title": "Mordell-Weil lattices", "abstract": "an elliptic surface", "cats": ["math.NT", "math.AG"],
                 "comment": "12 pages", "topics": ['abs:"elliptic surface"']}
        self.assertEqual(ax.score(paper, prof), 3 + 2 + 1.5 + 2)
        paper["comment"] = "45 pages"
        self.assertEqual(ax.score(paper, prof), 3 + 2 + 1.5 - 3)
        self.assertEqual(ax.pages_from_comment("10 pages, 2 figures"), 10)
        self.assertIsNone(ax.pages_from_comment("comments welcome"))

    def test_leak_scan(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            (root / "ok.md").write_text("A public note about private repositories.\n")
            pat = root.parent / f"{root.name}-patterns.txt"
            pat.write_text("# demo\nsecret-host\\.example\n")
            run = lambda *a: subprocess.run([PY, "-I", str(TOOLS / "leak_scan.py"), str(root), *a],  # noqa: E731
                                            capture_output=True, text=True)
            self.assertEqual(run("--patterns", str(pat)).returncode, 0)
            (root / "bad.md").write_text("deploy to secret-host.example\n")
            self.assertEqual(run("--patterns", str(pat)).returncode, 1)
            (root / "bad.md").unlink()
            marker = "<!-- " + "PRIVATE" + ":BEGIN -->"
            (root / "m.md").write_text(marker + "\n")
            self.assertEqual(run().returncode, 1)
            (root / "m.md").unlink()
            (root / "k.txt").write_text("-----BEGIN OPENSSH " + "PRIVATE KEY-----\n")
            self.assertEqual(run().returncode, 1)
            pat.unlink()


class Scaffold(unittest.TestCase):
    def test_scaffold_all(self):
        with tempfile.TemporaryDirectory() as d:
            proj = Path(d) / "talk"
            r = subprocess.run([PY, "-I", str(TOOLS / "scaffold.py"), str(proj), "--title", "T", "--speaker", "S",
                                "--date", "2026-12-01", "--paper", "P", "--seminar", "Sem", "--lean", "Toy",
                                "--cas", "sympy", "--all"], capture_output=True, text=True)
            self.assertEqual(r.returncode, 0, r.stderr)
            for f in ["CLAUDE.md", "MEMORY.md", "JOURNAL.md", "PLAN.md", "MAINTENANCE.md", ".gitignore",
                      "source/SOURCE.md", "artifacts/mathematical/digest.md", "formal/Toy/Defs.lean",
                      "formal/Toy.lean", "formal/demo/LiveDemo.lean", "formal/comparator.json",
                      "tools/cert2lean.py", "tools/cluster.sh", "index.html", "slides/build/build.py",
                      "book/_config.yml", "book/seminar_lib.py", "book/formalization/f2_trust.md",
                      "vault/Home.md", "verso/Doc/Meta.lean", "verso/.gitignore"]:
                self.assertTrue((proj / f).exists(), f)
            text = "".join(p.read_text(encoding="utf-8") for p in proj.rglob("*") if p.is_file())
            for key in ["TITLE", "SPEAKER", "LEAN_NAME", "PROJECT", "TODAY", "SEMINAR"]:
                self.assertNotIn("{{" + key + "}}", text)
            self.assertTrue(os.access(proj / "tools/cluster.sh", os.X_OK))
            # the deck builds and passes its verbatim check once the demo command is filled in
            for f in ["slides/build/10_talk.html", "slides/build/board-plan.tpl.md"]:
                p = proj / f
                p.write_text(p.read_text(encoding="utf-8").replace("{{DEMO_COMMAND}}", "lake env lean demo/LiveDemo.lean"))
            r = subprocess.run([PY, "-I", str(proj / "slides/build/build.py")], capture_output=True, text=True)
            self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
            self.assertIn("0 not verbatim", r.stdout)
            # refuses to overwrite
            r = subprocess.run([PY, "-I", str(TOOLS / "scaffold.py"), str(proj), "--title", "T"],
                               capture_output=True, text=True)
            self.assertEqual(r.returncode, 1)


class Installer(unittest.TestCase):
    def test_install_uninstall(self):
        with tempfile.TemporaryDirectory() as d:
            sh = lambda *a: subprocess.run(["bash", str(REPO / "install.sh"), "--target", d, *a],  # noqa: E731
                                           capture_output=True, text=True)
            link = Path(d) / "seminar-deep-study"
            self.assertEqual(sh("--dry-run").returncode, 0)
            self.assertFalse(link.exists())
            self.assertEqual(sh().returncode, 0)
            self.assertTrue(link.is_symlink() and link.resolve() == REPO.resolve())
            self.assertIn("already installed", sh().stdout)
            self.assertEqual(sh("--uninstall").returncode, 0)
            self.assertFalse(link.exists())
            link.mkdir()                          # a real directory is never replaced
            self.assertEqual(sh().returncode, 1)
            self.assertEqual(sh("--force").returncode, 1)
            self.assertTrue(link.is_dir() and not link.is_symlink())



if __name__ == "__main__":
    unittest.main()
