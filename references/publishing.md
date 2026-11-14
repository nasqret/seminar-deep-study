# Phase 7: publishing (only on an explicit request)

Everything is built and checked locally first. Publishing, deploying, pushing and creating a
remote repository each need an explicit request from the user in the current session; an earlier
"publish it" does not carry over to a later session. Show a dry run first, then publish, then
check the result.

## 1. What may go out

Assemble the published site from an **allow-list** into `_site/`: the landing page and its
assets, the built book (`book/_build/html/`), the slides, the rendered Verso document, and
optionally the Lean and CAS sources. Never publish:
- `source/` (the paper's PDF and TeX: the arXiv licence usually forbids redistribution);
- the findings register about an unpublished paper, unless the user decided to publish it;
- `vault/`, `MEMORY.md`, `JOURNAL.md`, `CLAUDE.md` and other working files, unless asked;
- anything with hostnames, user names, home paths or tokens (run `tools/leak_scan.py` with the
  project's own pattern file on `_site/`).

## 2. The options (phase 0 decided which)

### Local only
Open `index.html` from disk. All links are relative; fonts fall back to system fonts offline.
Nothing leaves the machine. This is the default until the user asks for more.

### A private Claude artifact
With a Claude artifacts connector, publish the page and its assets as one multi-file artifact.
Give each file its served path, with `index.html` at the root. The artifact starts private to the
user; sharing it is the user's decision, made in Claude's interface. Limits: 256 files and 20 MiB
per file per call, so a large book goes in later republishes or stays a link. Republishing needs
the current version id; keep the artifact link in `README.md` and `MAINTENANCE.md`.

### GitHub Pages
Pages serves a branch folder (`/docs` or the root) or the output of an Actions workflow. The site
is public even when the repository is private, except on plans with access-controlled Pages, so
treat it as public: everything on it passes the allow-list and the leak scan. Steps: assemble
`_site/` into the publishing branch or folder; `gh repo create … --private|--public --source .`;
enable Pages (`gh api -X POST repos/OWNER/REPO/pages -f "source[branch]=main" -f
"source[path]=/docs"`); wait for the build; check the URL with `curl -sI`.

### Your own web server via rsync
`templates/site/scripts/deploy.sh`, configured by environment variables:
`SITE_REMOTE` (`user@host`), `SITE_DEST` (a directory relative to the remote home, for example
`public_html/<project>`), and `SITE_URL` (the public URL, used by the link checker and the final
message). It:
1. refuses to run if the book is not built or a required file is missing;
2. assembles `_site/` from the allow-list;
3. refuses if any private path ended up in `_site/`;
4. checks the links (`scripts/check_links.py`: relative links resolve, no nested `<a>`);
5. runs the leak scan with the project's pattern file, if there is one;
6. sets permissions locally (directories 755, files 644), because macOS's `/usr/bin/rsync` is
   openrsync and does not support `--chmod=D…,F…`;
7. `--dry-run` lists what would change; `--assemble-only` stops before uploading;
8. otherwise `rsync -rltvz --delete --perms _site/ "$SITE_REMOTE:$SITE_DEST/"`. The `--delete`
   applies only to the project's own directory on the server.

Afterwards run `scripts/check_site.sh` (HTTP 200 for the key URLs). A `.htaccess` (Apache) can
set `DirectoryIndex index.html` and serve `.lean`, `.m` and `.py` files as UTF-8 plain text.

## 3. Repositories

- **Local only**: the default.
- **Private GitHub repository**: `gh repo create OWNER/NAME --private --source . --push`. Check
  the visibility afterwards (`gh repo view --json visibility`).
- **Public repository**: never push a private history. Generate a clean tree, give it a fresh
  history (`git init`, one commit), and scan it with `tools/leak_scan.py` and the project's
  patterns (user names, hosts, home paths, emails, private project names, findings that are not
  yet public). Let the user review it and push it.
- Commit identity: if the user keeps their email private, use the hosting service's no-reply
  address in the repository's local git config.

## 4. After publishing

Record the URL, the date and what was published in `JOURNAL.md` and `MAINTENANCE.md`. Check every
key URL (`curl -s -o /dev/null -w '%{http_code}'`), and look at the page in a browser or with a
headless screenshot.

