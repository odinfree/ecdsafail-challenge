# Q1270 routed predictor target rebuild

Date: 2026-08-23. Verdict:
`PASS_BYTE_EXACT / TRUSTED_FULL_REPRODUCED / MODEL UNOPENED`.

After the predeclaration commit `d71a4b7`, the exact circuit source was rebuilt
from an empty target with `--locked --offline`. The build used only the eight
frozen Q1270 controls and inherited nonce `65700024945645`.

## Rebuild identities

- exact circuit source / tree:
  `90770b10664fc89065b1d05ac792370efed4c629` /
  `944593de97d412f8b4c7242f7d0aff98002c0d04`;
- lane predeclaration: `d71a4b7`;
- rebuilt `build_circuit` SHA-256:
  `1011f82a46a034fff7c82307354e83b1d4a24d2c3c740bc3caa3449f93f555a4`;
- rebuilt unchanged `eval_circuit` SHA-256:
  `ee52b3968f50e182b356d7253ba580abbb4291264af6ca09a112ff025c746d23`;
- unchanged evaluator source SHA-256:
  `b35314bc47a5f8eecbf60459e6c76c9b43aa034eeb9b7ec3421655d74f9e890b`.

## Exact artifact

- operation magic: `QECCOPSZ`;
- emitted operations: `12,953,636`;
- compressed bytes: `49,316,215`;
- operation SHA-256:
  `ec4fadc0b5cd1c26ee5d81001b7a72692678b61a94c4091032dd93b8b62eb63a`.

This is byte-identical to the operation stream frozen by the Q1270 structural
and full-run receipts.

## Unchanged full evaluator reproduction

One unchanged local evaluator run reproduced:

- Q / bits / shots: `1270 / 961,070 / 9,024`;
- exact displayed average T / Clifford:
  `916366.972 / 10731503.349`;
- classical / conditional-phase / ancilla: `23/14/0`;
- first classical mismatch: shot `373`, with the same X and Y values as the
  terminal full-run receipt;
- appended evaluator-row SHA-256:
  `6d0fa15300bcfb51d278aeb6498e32cae6635c1fa3f4eabc69781dcced4ed281`.

The tracked result ledger was restored byte-exact to SHA-256
`eea840222afd2424445550252f25795d63eb4bc3904b8c87f0213b5f22abc810`.
The expected nonzero evaluator exit is the reproduced dirty validity result,
not an abort.

## Next gate

Derive a fresh operation-site trace, checkpoint, R/Hmr geometry, and
conditional-phase schedule from this exact source. No predictor source,
binary, table, checkpoint, schedule, or output has been imported or run.
