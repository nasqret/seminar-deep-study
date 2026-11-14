# Examples

| file | what |
|---|---|
| `prompts.md` | opening prompts for mathematics and computer science, and the follow-ups that steer the ideation rounds |
| `cert/sample.out` | a transcript with three `CERT` blocks (two `linear_combination` certificates, one `ring` identity) |
| `cert/Sample.lean` | what `tools/cert2lean.py examples/cert/sample.out --namespace Demo.Cert` produces from it |

The certificate `R_simple` is the one used in the live demo of the first use, where it was checked
by Lean; regenerate `Sample.lean` after changing the generator (a test compares them).
