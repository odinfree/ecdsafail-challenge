# Q1271 operandless fused-fold — terminal falsification

Updated: 2026-08-23. Candidate source commit measured:
`f1615aabd7637cfe52f8f63d60e5f28185410ebb`.

## Decision

`KILL_OPERANDLESS / Q1271_LANDS / T_PRICE_FAILS / NO_RESCUE`

The single predeclared operandless family removes the roving fold qubit and
lands the requested complete-circuit Q1271 row. It fails the frozen price gate
by 156,904 rounded T and is terminally killed. No rescue tuning, narrower
activation, second family, square/point-add composition work, predictor,
network/provider action, range, hunt, submission, or public note followed.

Per `.lane/TASK.md`, the failed candidate source is removed from the terminal
tree. Its exact implementation and passing Gates 1–2 remain reproducible at
`f1615aa`; the terminal branch retains only durable evidence.

## Candidate identity

The only enabled candidate geometry was:

```text
SUB4_PP_PEAK=1271
SUB4_SQUARE_LADDER=241
SUB4_PP_FOLD_SELECTOR_EVICT=1
SUB4_PP_FOLD_OPERANDLESS=1
```

After a clean release build, it emitted 12,493,879 operations. Compressed
`ops.bin` was 51,604,981 bytes (699,657,240 bytes uncompressed) with SHA-256
`491367eccb25a27de49f1f9b7b2cab50079313a9fe3ae5bb738b5d7fdd9ef0d0`.

Measured source and evaluator identities were:

- candidate `src/point_add/pingpong_div.rs`:
  `134a495bc9dea6c3bd1da802cb2f95e5634089a0fe808784696852e5a5918332`;
- candidate `src/point_add/mod.rs`:
  `674b2c6e1ae6adac4c4f71cba0bc7a0c76c7c3e4a44509221c0c164d01089c70`;
- unchanged `src/bin/eval_circuit.rs`:
  `b35314bc47a5f8eecbf60459e6c76c9b43aa034eeb9b7ec3421655d74f9e890b`;
- candidate-path `build_circuit` binary:
  `fd7b223b81f93efbd0e0d33e08ce260439422cb8f39eec3d3883ec52613e78f6`;
- unchanged-path `eval_circuit` binary:
  `0c98954b433639ea2d88a4182bc61a7bc358c152fb38a7b9df470a000c694b47`.

## Q and owner gate — PASS

The complete owner profile reported Q1271, first reached at operation index
2,142,110 in `pp_div_replay`. All required owner maxima passed:

| owner | peak Q |
|---|---:|
| `pp_div_replay` | 1271 |
| `square_product_register` | 1271 |
| `pp_mul_replay` | 1271 |
| `pp_mul_walkback` | 1271 |

The new fold cannot exceed Q1271 because the allocator's complete-stream
global maximum is Q1271. The profile composition independently passed 64/64
values exact, phase mask zero, and zero dirty non-register qubits.

A bounded B0 census over `[2142050,2142180]` reproduced the first binding
instant exactly. Its nine source-owner groups sum to 1,271:

| live | measured candidate owner | role |
|---:|---|---|
| 297 | `pingpong_div.rs:1084`, `pp_div_walk` | pre-replay walk signs |
| 256 | `pingpong_div.rs:2048`, `init` | caller numerator register |
| 256 | `pingpong_div.rs:261`, `pp_div_replay` | replay coefficient register |
| 163 | `pingpong_div.rs:2047`, `init` | walk register u |
| 163 | `arith/adder.rs:341`, `tlm_inverse` | walk register v |
| 133 | `pingpong_div.rs:770`, `pp_div_replay` | split walk-add high carries |
| 1 | `pingpong_div.rs:729`, `pp_div_replay` | split boundary carry |
| 1 | `pingpong_div.rs:1084`, `pp_div_replay` | interleaved walk sign |
| 1 | `pingpong_div.rs:536`, `pp_div_walk` | fused round-zero sign |

Thus removing the fold operand exposes the already budgeted walk-split region
as the first Q1271 co-binder; it does not leave a hidden Q1272 owner.

## Exact price attribution

The profile emitted 1,119,153 CCX and 28 CCZ and executed T1,076,846.56 on
its independent 64-lane corpus. Relative to the frozen Stage-A stream at the
same `PEAK1271/LADDER241` geometry, emitted CCX increased by exactly 161,472.

This corrects the predeclared first-order call-count estimate. The shared
`fused_fold_maskfree` family executes in both division and multiplication:

| phase | fused calls | exact CCX delta |
|---|---:|---:|
| `pp_div_replay` | 698 | +80,968 |
| `pp_mul_replay` | 82 | +9,512 |
| `pp_mul_walkback` | 612 | +70,992 |
| **total** | **1,392** | **+161,472** |

Each call still matches the focused miter's exact `+116 CCX` price. The
original ~80,968-T estimate counted only the 698 division calls; exact
measurement found the additional 694 multiply calls.

The full emitted-operation delta is also exact:

- fused cells: 1,392 × −307 operations = −427,344;
- shifted free-pool restore sequences: +1 `pp_div_restore`,
  +7 `pp_mul_restore`;
- complete artifact: −427,336 operations, from 12,921,215 to 12,493,879.

Equivalently, fused Clifford operations fall by 423 × 1,392 = 588,816,
while the two restore phases add eight Clifford operations. That large
Clifford reduction cannot pay for the 161,472 added CCX under the objective.

## Frozen T and full evaluator gate — FAIL

The unchanged full 9,024-shot evaluator measured:

| Q | average T | rounded T | frozen ceiling | gap | class/phase/anc |
|---:|---:|---:|---:|---:|---|
| 1271 | 1,076,731.802 | 1,076,732 | 919,828 | **+156,904** | `19/16/0` |

The first reported failure was phase mask `0x0200000000000000`. The dirty
channels are retained as requested characterization, but the price gate
already kills the family regardless of nonce. At rounded convention the
candidate product is 1,368,526,372, which is 199,424,752 worse than the
dispatch anchor 1,169,101,620.

The full T increase versus the Stage-A same-geometry baseline is
161,469.500, within 2.5 of the exact emitted-CCX increase; measurement-stream
changes account for the small executed-T difference. This is not near the
gate, so no calibration rerun is authorized.

The generated evaluator row was removed after capture and `results.tsv` was
restored to SHA-256
`eea840222afd2424445550252f25795d63eb4bc3904b8c87f0213b5f22abc810`.
Generated operations, build products, logs, binaries, score artifacts, and
failed candidate source are excluded from the terminal commit.

## Critique → fix → verify

- **Critique:** the predeclared static price multiplied +116 CCX by only 698
  calls. **Fix:** attribute emitted counts phase-by-phase on the complete
  operation stream. **Verify:** 698 division plus 82 multiply-replay plus 612
  multiply-walkback calls equal 1,392, and all three CCX deltas divide exactly
  by 116.
- **Critique:** landing Q1271 could hide a different allocator binder.
  **Fix:** run the complete active timeline and source-owner census.
  **Verify:** every required phase peaks at Q1271 or below; the exact nine-row
  first-peak census sums to 1,271 and identifies the walk-split co-binder.
- **Critique:** a large static failure still needed the one frozen exact
  measurement. **Fix:** run the unchanged full evaluator once, with no source
  response. **Verify:** rounded T1,076,732 misses by 156,904; the source is
  removed and the lane terminates.
