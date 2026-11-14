# Maintaining the skill

The installed skill is a link to a checkout of this repository, so an edit to the repository is an
edit to the skill. Keep the skill domain-neutral: no results, no findings about any paper, no
numbers from a particular project. Project-specific material belongs in that project's repository.

## Making a change

1. Edit `SKILL.md`, `references/`, `templates/`, `tools/` or `examples/`.
   - When the skill should trigger: the `description` in `SKILL.md` (at most 1024 characters, no
     angle brackets).
   - The method, the phases, the principles: `SKILL.md` (keep it under 300 lines).
   - Details read on demand: `references/*.md`.
   - What is copied into projects: `templates/` (placeholders `{{NAME}}`; `tools/scaffold.py`
     fills the ones it knows and lists the rest).
   - A trap met in practice: `references/traps.md` (and the project's `CLAUDE.md`).
2. Test: `python3 -m unittest discover -s tests -v`. The tests check the frontmatter, that every
   path mentioned in the skill exists, the relative links, the scaffold, the certificate
   generator, the arXiv ranking on a fixture, and the leak scanner.
3. Record the change under "Unreleased" in `CHANGELOG.md`.
4. Commit (Conventional Commits, English).

## Releasing

Move the "Unreleased" entries under a new version heading (patch: fixes and wording; minor: new
features; major: breaking changes to the templates or the method), commit, tag
(`git tag -a vX.Y.Z -m "…"`), push. Installed copies update with `git pull`.
