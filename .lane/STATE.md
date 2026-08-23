# b523 B1 paired-cap descent below Q1274 — terminal result

Updated: 2026-08-23

## Decision

`GO_D1273 / HOLD_HUNT / KILL_D1272 / FLOOR_EXPOSED / NO_DEFAULT_CHANGE`

The frozen B1=24 paired-cap descent reaches Q1273 with a strict score beat.
The next row does not reach Q1272: lowering `SUB4_PP_PEAK` and
`SUB4_SQUARE_LADDER` together exposes `pp_div_replay` at Q1273 while the square
and multiply owners reach Q1272. The predeclared stop gate fired. No rescue
tuning, third row, predictor work, hunt, provider action, submission, source
default change, or incumbent edit followed.

Both rows use the exact hard-coded B1=24 source at `6f6da43`; this branch's
starting evidence commit is `a68e1f0`. Every setting other than the two frozen
caps remained at that source's defaults.

## Live gate

The frontier was reopened with `ecdsafail benchmark` at
`2026-08-23T06:22:20Z`, after both rows and before the score comparisons below:

- current best: `1,169,101,620`;
- promoted source: `b523ecf`;
- benchmark status: open.

This matches the dispatch anchor. All score products below use the benchmark's
rounded average Toffoli convention.

## Frozen matrix result

| row | PEAK | LADDER | emitted ops | operation SHA-256 | measured Q | full avg T | round(T) | score at measured Q | margin vs live | class/phase/anc | verdict |
|---|---:|---:|---:|---|---:|---:|---:|---:|---:|---|---|
| D1273 | 1273 | 243 | 12,892,399 | `f225dae80d6d81a5e1d61d9ac32b74df48ca1b40d9ff5905bb61acf66c9ceb15` | 1273 | 914207.834 | 914208 | 1,163,786,784 | 5,314,836 | 29/15/0 | strict structural beat; dirty, no hunt |
| D1272 | 1272 | 242 | 12,904,991 | `0ce4aac781957c12b2fb2217cb116a68fe77e74ad810a73cfd1a1f4450fa0e20` | **1273** | 914726.434 | 914726 | 1,164,446,198 | 4,655,422 | 25/20/0 | Q gate failed; dominated by D1273; stop |

D1273 clears its frozen rounded-T ceiling of 918383 by 4,175 T. It is an
architecture result only: its inherited nonce is dirty, so neither the score
beat nor the selftests authorize a predictor, scan, hunt, or submission.

D1272's unchanged evaluator was already running when its header disclosed
Q1273 and it completed the same fixed 9,024-shot evaluation. Its T and fault
counts are retained as non-promoting characterization. The Q gate controls the
verdict: this row did not produce Q1272, regardless of its score at Q1273.

## D1273 exact gates

Clean release build completed before artifact generation. Binary identities:

- `target/release/build_circuit`:
  `03cf2592ae33942bc3674664c024a9b3b23b8085c0c7269f73a64b20f4653a95`;
- `target/release/eval_circuit`:
  `f47f6faeab332d6e9f1feef57d6eb9abfeda6c16a99b5aa6fc404b438422b67c`.

Artifact build with `SUB4_PP_PEAK=1273 SUB4_SQUARE_LADDER=243` emitted
12,892,399 operations and reproduced the operation SHA in the table. The
unchanged full evaluator measured Q1273 and T914207.834 over all 9,024 shots.
Its first classical mismatch was shot 884; x was exact and y was:

- got:
  `e5b85b03e50aa88ac52783f9b84c3f86b0532a5ac40be69a7ee9f38e3a3e77e5`;
- expected:
  `e5b85b03e50aa88ac52783f9b84c3f86b052f422eaf212a29229f38e3a3e77e5`.

Because the row strictly beat the frozen ceiling, both authorized focused
selftests ran:

- product-square: 64/64 values exact, phase 0, ancilla 0; 58,963 emitted /
  58,726.125 executed T, peak Q1273;
- complete point-add: 64/64 affine additions exact, phase 0, ancilla 0;
  955,609 emitted / 914,135.750 executed T, peak Q1273.

The selftest implementations assert every value, the full phase mask, and every
non-register ancilla before printing these resource receipts; both processes
exited 0.

## D1272 owner gate

A second clean release build completed before D1272. The binary hashes were
identical to D1273. Artifact build with
`SUB4_PP_PEAK=1272 SUB4_SQUARE_LADDER=242` emitted 12,904,991 operations and
reproduced the operation SHA in the table. The unchanged evaluator measured
Q1273 at load time, so gate 2 failed.

The already-running full evaluation finished with T914726.434 and 25/20/0.
The first failure exposed by the unchanged evaluator was phase mask
`0x0008000000000000`; because phase was encountered before its first classical
failure, the stock output did not expose a first classical shot index. No
instrumented evaluator was introduced to pursue a killed row.

The bounded owner profile on the same operation stream identified the new
floor exactly:

- allocator peak: Q1273 at operation index 4,257,060;
- peak phase: `pp_div_replay`;
- `pp_div_replay`: Q1273;
- `square_product_register`: Q1272;
- `pp_mul_replay`: Q1272;
- `pp_mul_walkback`: Q1272;
- profile composition check: 64/64 values exact, phase 0, dirty qubits 0.

Thus the former `Q = 1030 + SQUARE_LADDER = PP_PEAK` co-binder law is no
longer exact at the D1272 setting. The square descends as predicted, but the
division replay remains one qubit above its requested cap. D1272 also adds
12,592 emitted operations and 518.600 average executed T versus D1273 while
delivering no Q reduction, so it is strictly dominated within this matrix.

## Protected identities and cleanup

- `src/point_add/pingpong_div.rs`:
  `92ffe2f17886334e9db863e81683ef31911c46b759b7b7acac65017591e6c66d`;
- `src/point_add/trailmix_ludicrous/square/product_register.rs`:
  `872f9a18929cc576dcdbfd05735bc3243b756488ce6acc70ce705f46e2b302ee`;
- unchanged evaluator `src/bin/eval_circuit.rs`:
  `b35314bc47a5f8eecbf60459e6c76c9b43aa034eeb9b7ec3421655d74f9e890b`;
- predeclared task `.lane/TASK.md`:
  `cc4d8f157ae9c846ff9b6468deb6dbdbaa735c4bbdb0be0641bbcd199282c5f1`.

The two generated `results.tsv` rows were used only as exact T receipts and
then removed; its protected SHA is restored to
`eea840222afd2424445550252f25795d63eb4bc3904b8c87f0213b5f22abc810`.
`ops.bin`, binaries, caches, logs, and score artifacts are excluded from the
commit.

## Next structural action (not executed)

Any attempt below Q1273 requires a fresh predeclaration aimed at the division
replay allocator's one-qubit overshoot. It must first explain why the requested
1272 cap realizes Q1273 and price a structural owner change; lowering the same
two caps again would be an unpriced third row and is explicitly outside this
lane.
