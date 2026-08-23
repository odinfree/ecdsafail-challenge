# B1=24 CPU model gate

The hard-coded B1=24 source reproduced the predeclared sweep identity exactly:
12,822,408 operations with SHA-256
`af28dbc49471651c3e856c62c1fd97cb429469cde4b66fe7fe082a0d23fe1ad7`.

The source-bound Rust classical model was updated only for the circuit's exact
defaults: divider/multiply rounds 700/696, replay fold 53, endpoint fold 20,
flag/chunk compare 20/20, and first value-width breakpoint 24. It reported
classical counts `17,24,17,21` for the four predeclared nonces. The unchanged
full 9,024-shot evaluator reported the same four counts exactly:

| nonce | model classical | evaluator classical/phase/ancilla | T average |
| ---: | ---: | ---: | ---: |
| 81327465284 | 17 | 17/13/0 | 911310.414 |
| 81327465285 | 24 | 24/17/0 | 911307.799 |
| 81327465286 | 17 | 17/15/0 | 911307.037 |
| 81327465287 | 21 | 21/10/0 | 911302.523 |

Verdict: local CPU classical gate passes with zero disagreement across 36,096
shots. This does not authorize a hunt. A Linux CPU/CUDA build must pass a
frozen complete per-shot parity manifest first. Temporary evaluator source,
generated result rows, operations, logs, and binaries are excluded from Git.
