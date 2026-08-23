# b523 Q1276 classical-model qualification

Date: 2026-08-23

## Verdict

`FAIL_MODEL` at the predeclared complete-H64 equality gate.

The hard-coded circuit bake is exact, the imported predictor builds, and its
built-in Fiat-Shamir/model self-test passes.  However, the predictor is not an
exact classical classifier for this circuit.  It matches 61 of the 64 frozen
full-evaluator counts and underpredicts three rows by one fault each.  This is a
demonstrated false-negative mechanism, so neither strict `pred0` nor a scan may
be authorized from this model.  The Linux/CUDA fixture packet is intentionally
not frozen or advanced.

## Frozen identities

- circuit base: `b523ecf`;
- hard-coded bake commit: `1adf7573101a3f8e9af2e7f7e2505faa9c6bea20`;
- circuit operations: `12,901,678`;
- circuit operations SHA-256:
  `d460c3968659b6bbbf5615268d73df210df55f9cd4cbca330de1ef960c6dd4c0`;
- measured geometry: Q1276, divide/multiply rounds `700/696`, replay fold
  `53`, value-width break `30`;
- upstream predictor repository commit:
  `da0e5721f14f5d956aa703b38311f4087388a7b1`;
- untouched upstream Rust source SHA-256:
  `bc01d12729be766a2a385e65db1c36df31904ee2e9afd3772828e7c9cb9d1593`;
- qualified port source SHA-256:
  `7f0373926fa313453f6e349703c3f89d63b6f7d52bf0bff94258479fe609bf42`;
- local release binary SHA-256:
  `e38577d3bc815229a5b4390bab9bd0d75c86f88ae5984fcf87e0bc4843b97f3d`.

The complete diff from the untouched upstream Rust source is limited to the
predeclared geometry/default changes: displayed operation scale, multiply
rounds `-2 -> -4`, replay fold `54 -> 53`, `BREAK_1 40 -> 30`, and validated
operation count `13,324,385 -> 12,901,678`.

## Calibration

The fixed corpus is the already-frozen candidate full-evaluator H64 at nonces
`444000000000..444000000063`, each evaluated with all 9,024 shots.  The
evaluator rows are from the immutable paired ledger whose candidate-row hash is
`84cdef5cc22bdde9c85210b28dab4dcfb767fec47463eadd7a21d761349febe2`.

The predictor was built from the hard-coded candidate and absorbed all
`12,901,678` operations before evaluating precisely those 64 fixed nonces.  Its
runtime receipt confirmed `rounds_div=700`, `rounds_mul=696`,
`replay_fold=53`, and `endpoint_fold=20`.

- frozen evaluator input TSV SHA-256:
  `d0cef57d82a0b54d6457fac11d85f7c257abfc76b4216bfeb560537bbaf2202e`;
- raw predictor output TSV SHA-256:
  `1ed13f4230c6842dd09cd828073f75a7c50664a7fdd538686b773131c82222d1`;
- predictor stderr receipt SHA-256:
  `9c1b6eb5865c61c46e0648868f9e88b99e2a74579555eaf654d959d9def10f63`;
- durable normalized comparison:
  `.lane/model-calibration-h64.tsv`;
- durable comparison SHA-256:
  `2e580159693cdbfedc09cb972c71672837e773ee219bb8facda1d6eb4448de37`.

Aggregate evaluator count is `1048`; aggregate predictor count is `1045`.
The exact failures are:

| nonce | evaluator | predictor | delta |
| ---: | ---: | ---: | ---: |
| 444000000002 | 14 | 13 | +1 |
| 444000000040 | 22 | 21 | +1 |
| 444000000042 | 20 | 19 | +1 |

Every other row is exactly equal.  The mismatch direction is the unsafe one:
the model misses evaluator faults.

## Focused checks

The imported binary's built-in self-test exits zero against the baked circuit:

- SHAKE256 empty-string known-answer test: pass;
- baked operation count: `12,901,678`;
- four fixed nonce-XOF outputs: pass;
- scalar/point-model known-answer test: pass.

No provider was contacted.  No CUDA host was used.  No range, hunt,
submission, or incumbent mutation occurred.  Generated operations, binaries,
and logs remain outside Git.

## Consequence

This receipt closes only the exact-port hypothesis.  A separate, predeclared
structural audit may localize the three evaluator-only fault shots and search
for a source-semantic missing channel.  It must not tune against these H64
counts, and any correction must pass a disjoint corpus before model parity can
be reconsidered.

