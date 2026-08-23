# b523ecf B1=24 prefilter port

Bound circuit source:
`/Users/olifreuler/Documents/Codex/2026-08-21/par/work/b523-b1-24-predictor`

- Base commit: `b523ecf`
- Semantic edit: `value_width` `BREAK_1=30 -> 24`
- Operations: 12,822,408
- Operation SHA-256:
  `af28dbc49471651c3e856c62c1fd97cb429469cde4b66fe7fe082a0d23fe1ad7`
- Divider rounds: 700
- Multiply rounds: 696
- Replay fold window: 53
- Endpoint fold window: 20
- Replay flag and chunk compare widths: 20/20
- Width schedule: breakpoints 24/304, slopes 17/34/40, margin 4

The Rust CPU port exactly matched the unchanged 9,024-shot evaluator's
classical counts on the predeclared nonces 81327465284 through 81327465287:
17, 24, 17, and 21. This is only the first local gate. The CUDA build must
still pass complete per-shot parity on a frozen fixture manifest before any
range scan. Every retained nonce requires an unchanged full 9,024-shot
classical/phase/ancilla evaluation.
