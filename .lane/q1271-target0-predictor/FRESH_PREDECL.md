# Q1271 target0/sign-alias fresh F16 predeclaration

Status: `FROZEN_BEFORE_ORACLE_OR_MODEL_OUTPUT`.

This final holdout is a new deterministic, domain-separated set of 16 fixture
nonces. It was defined after the H64, D32, and negative-matrix evidence was
sealed, and before either the trusted oracle or predictor produced output for
any row. No score, mask, survivor, or search result influenced the selection.

## Deterministic fixture derivation

- negative-matrix evidence commit:
  `2cfdd9e5be17a73d08eccdc10a1dc9becf201abd`;
- ASCII domain plus NUL:
  `q1271-target0-sign-alias/fresh-f16/v1\0`;
- seed bytes: domain bytes followed by the 20 raw bytes of the negative seal;
- seed-material SHA-256:
  `2f523d2176f634223f8b6c173771b59e6f49ae2a9c50c5dd12c07999153b8d19`;
- for counter `i = 0,1,...`, calculate
  `SHA256(seed || little_endian_u64(i))` and interpret its first six bytes as
  a little-endian unsigned 48-bit integer;
- reject inherited nonce `65700024945645`, H64, frozen D32, and any duplicate;
  take the first 16 accepted values;
- counters consumed: exactly `16`;
- frozen `F16.nonces` SHA-256:
  `bbfdbf0372f73855519c100bd5aa52c39f5f1fe5e6f966e7726b2a43c008819e`.

The committed runner independently regenerates the list and proves all 16
rows are canonical, unique, below 2^48, and disjoint from inherited, H64, and
D32 before opening output.

## One-shot gate

After this predeclaration and runner are committed and pushed, run the exact
trusted mirror and the unchanged source-bound CPU model once for every row.
Require all of:

- Q1271, exactly 9,024 shots, and ancilla zero on each trusted row;
- exact complete classical-mask equality, with zero false negatives and zero
  false positives;
- exact complete `raw_phase & ~classical` mask equality, with zero false
  negatives and zero false positives;
- canonical sorted unique shot indices in `[0,9024)`;
- byte-identical inherited and final-row deterministic repeats;
- unchanged source, operation, schedule, binary, oracle, and negative-receipt
  identities throughout.

Any mismatch is terminal `KILL`. A full `16/16` pass yields local
`CPU_PREDICTOR_GO` only. It grants no CUDA, provider, scan, range, hunt, fleet,
submission, or public-note authority. Generated outputs remain outside Git.
