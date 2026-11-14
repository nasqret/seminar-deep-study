"""Shallow (depth-1) clones of every Lake dependency at the exact manifest revision.

Lake accepts an existing git checkout whose HEAD equals the manifest revision, so this saves
the full history (about half a gigabyte for Mathlib) on a quota-limited file system.

Usage: python3 shallow_deps.py lake-manifest.json .lake/packages
(`lake-manifest.json` must exist: run `MATHLIB_NO_CACHE_ON_UPDATE=1 lake update` once, locally or
remotely, and commit the manifest.)
"""
import json
import os
import subprocess
import sys

manifest, root = sys.argv[1], sys.argv[2]
for p in json.load(open(manifest))["packages"]:
    if p.get("type", "git") != "git":
        continue
    d = os.path.join(root, p["name"])
    if os.path.isdir(os.path.join(d, ".git")):
        head = subprocess.run(["git", "-C", d, "rev-parse", "HEAD"], capture_output=True, text=True).stdout.strip()
        if head == p["rev"]:
            print("ok     ", p["name"], p["rev"][:12])
            continue
    os.makedirs(d, exist_ok=True)
    run = lambda *a: subprocess.run(["git", "-C", d, *a], check=True)  # noqa: E731
    if not os.path.isdir(os.path.join(d, ".git")):
        run("init", "-q")
        run("remote", "add", "origin", p["url"])
    run("fetch", "-q", "--depth", "1", "origin", p["rev"])
    run("-c", "advice.detachedHead=false", "checkout", "-q", "FETCH_HEAD")
    print("cloned ", p["name"], p["rev"][:12])
