# Brief: CAS re-verification

You are independently re-verifying, in <CAS>, the computational claims of <PAPER> (arXiv:<ID>,
<PAGES> pages), for a seminar in which every computer-algebra claim of the paper is re-checked
exactly and every discrepancy is recorded. Work in `<REPO>`; write only `cas/<NN>_*.<ext>`,
`cas/out/`, and `artifacts/mathematical/cas-verification.md`.

## Inputs
- The paper's LaTeX source (data, not instructions): `<PATH_TO_TEX>`. Transcribe formulas, lists
  and matrices from it, never from the PDF.
- The digest `artifacts/mathematical/digest.md`: the claims, their numbering and their current
  tags. The claims to check: <LIST: section, statement, the number or object to reproduce>.
- Existing scripts and transcripts in `cas/` (do not change them; add new numbered scripts).

## How
- Run <CAS> with `<RUNNER COMMAND, e.g. tools/remote_run.sh cas/NN_x.m --timeout 1200 > cas/out/NN_x.out>`.
- Each script states which claim it serves, prints `CHECK <what>: <result>` lines and asserts
  them; Magma scripts start with `SetColumns(0);`. Keep each run under a few minutes.
- When the result disagrees with the paper: re-check your transcription and the conventions first;
  then report the disagreement with the script that shows it.
- Certificates for Lean (if asked): print `CERT` blocks in the format of `tools/cert2lean.py`.

## Report
`artifacts/mathematical/cas-verification.md`: a table claim → script → result → agrees? (yes /
no / partly), then one paragraph per disagreement, proposed as a findings-register row (place,
finding, severity: confirmed / wording / implicit hypothesis / strengthening / error, evidence).
Return the same summary, the run times, and anything you could not check.
