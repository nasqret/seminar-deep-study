# MAINTENANCE — runbook

| | |
|---|---|
| Repository | `{{PROJECT}}` (local git; remote: {{GIT}}) |
| Lean | {{LEAN_TOOLCHAIN}} + Mathlib {{MATHLIB_REV}} — {{COMPUTE}} |
| CAS | {{CAS}} ({{CAS_WHERE}}) |
| Python | `uv` (`.venv` for the Jupyter Book) |

## Lean
```bash
# local:   cd formal && MATHLIB_NO_CACHE_ON_UPDATE=1 lake update && lake exe cache get Mathlib.X ...
#          lake build
# cluster: tools/cluster.sh setup | cache Mathlib.X ... | lean Proj/File.lean | demo | build | run 'CMD' | fetch PATH
#          (SEM_HOST, SEM_ROOT, SEM_PARTITION, SEM_JOB, SEM_CPUS, SEM_MEM, SEM_TIME: values below)
SEM_NO_SANDBOX=1 bash formal/scripts/verify-comparator.sh   # only on hosts without bwrap
```
Cluster values: {{CLUSTER_VALUES}}

## Certificates (CAS → Lean)
```bash
tools/remote_run.sh cas/02_certs.m --timeout 1200 > cas/out/02_certs.out     # remote CAS
python3 -I tools/cert2lean.py cas/out/02_certs.out --namespace {{LEAN_NAME}}.Cert \
  > formal/{{LEAN_NAME}}/Cert.lean
```

## Notes, slides, landing page
```bash
uv venv --python 3.12 .venv && uv pip install --python .venv/bin/python -r book/requirements.txt
.venv/bin/jupyter-book build book/ --warningiserror --keep-going
uv run --no-project --with numpy --with pillow python -I scripts/generate_hero.py
```
Visual QA: headless Chrome screenshots (`--headless=new --screenshot`, minimum width 500 px).

## Publishing (only on an explicit request in the current session)
{{PUBLISHING}}
