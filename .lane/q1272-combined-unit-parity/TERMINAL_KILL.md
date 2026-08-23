# Q1272 combined local unit-parity terminal report

Date: 2026-08-23

Verdict: `TERMINAL_KILL / CONDITIONAL_PHASE_MISMATCH / HOLD`.

The sealed checker at commit `d4cfb6b` exited fail-closed with:

```text
TERMINAL KILL: complete conditional-phase mask mismatch for D32/154123680082395
```

No model source changed after the fresh F32 corpus was frozen.  The run was
entirely local and performed no CUDA, range, search, provider, network, or
submission action.

## Bound identities

- qualified classical base:
  `f308df4f1ab054b204dec050bc8b9f452e7c49ee`;
- conditional-phase donor:
  `83ad631e1a99db3db1c3886b4d61ff9ded94b0f5`;
- checker commit: `d4cfb6b`;
- structural source: `73422709ed70ba9725b3cb592770bcf197df4cdb`;
- operation count / SHA-256: `12,904,643` /
  `ea19759d80a4bc1492a5e98c966e70ee79d5aa40211e6cc480b08cf032c8a0f1`;
- state digest: `e9b2d20ecd1169a8`;
- local evaluator source / binary SHA-256:
  `26d2a045d048025ce086b099b41fdfc7c42a2657426c59d5fdb95be9cacd8d98` /
  `90e4db8669c03b259c13b259018134b754faa94adfbc1e491a601f1052cd6402`.

## Exact failing row

Frozen corpus `D32`, nonce `154123680082395`, retained the expected geometry:
Q1272, 9,024 shots, and ancilla zero.  The qualified and combined classical
implementations produced byte-identical complete cause rows: 15 faults, output
SHA-256
`7b71edff31e4ac4470643db7c1bd1a4db4f51bf07c21dd8ae2bb9d711a824418`.
Those 15 indices also equal the unchanged evaluator's complete classical mask.

The conditional-phase masks differ by one shot:

- combined implementation: `{304, 4238, 7668}`;
- unchanged evaluator: `{304, 4238, 7668, 8833}`.

The combined phase output SHA-256 is
`c4d84f768ec0ca9e934e5aa5ad4011bbe5ed41988ab15389321c0b279534471e`.
The evaluator output SHA-256 is
`b2df6188e6c01bc2eec66442ca907eb03b8626ab53452cfbff135620b5a875aa`.
The evaluator summary reports 14 raw phase shots and four conditional clean
phase shots; the combined checker reports three conditional clean phase shots.

## Coverage before terminal exit

The checker writes `SHA256SUMS` only after classical and conditional-phase
equality for a row.  The local output tree contains:

| corpus | expected rows | exact sealed rows |
| --- | ---: | ---: |
| inherited | 1 | 1 |
| H64 | 64 | 64 |
| D32 | 32 | 31 |
| V64 | 64 | 64 |
| fresh F32 | 32 | 32 |

Thus the qualified and combined classical masks agree with the evaluator on
all 193 rows, while the conditional-phase gate is exact on 192/193 and fails
on the row above.  The checker aborted before its post-corpus malformed-input
matrix and deterministic repeats, so those terminal requirements are also
unfulfilled.  It created no `RESULTS.tsv`, `NEGATIVES.tsv`, or `TERMINAL_GO`.

Generated binaries, masks, attribution, and evaluator logs remain outside Git
under
`/Users/olifreuler/ecdsa-ops/q1272-combined-unit-parity-d4cfb6b/`.

This lane is closed as `HOLD`.  No partial GO, source repair, rerun, or further
action is inferred from the 192 passing rows.
