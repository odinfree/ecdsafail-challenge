# Teddy Pender paired low-five re-descent on `6b5c82c`

Created: 2026-08-22
Verdict: `HOLD_PAIRED_LOW5`
Promotion status: `NO_PRODUCTION_PROMOTION`
Shipping status: production source restored exactly to `6b5c82c`

## Credit and bounded question

Teddy Pender supplied the tape-removal architecture, the exact five-bit
sufficient statistic for signs one through three, and the
Burn-the-House-Down rule that forced the unchanged replay to survive its own
falsifier before it could judge the replacement.

The bounded question was whether the cheapest measured representation, Teddy's
five-bit prefix, adds a new logical or ancilla residual relative to the
unchanged four-round replay on exact source `6b5c82c`. It was judged under
both the strict logical oracle and the exact-live approximate geometry.

Model: Kimi Code (k2/k3, high effort), multi-lane agent campaign.

## Source and candidate selection

- Exact source: `6b5c82cbe723b33c296c8926876f14f1ac3307a8`.
- Branch: `research/burn-pp-div-replay-redescent-6b5c82c`.
- Low-five source provenance: `34c1b50`.
- Strict/reference-localization provenance: `2bff9dc`.
- Exact paired evaluator and receipt commit:
  `2d2eeb255929cc7ee610f18765445836fe280f60`.
- The `fable-burn-6b5c-stream` branch had a committed descent plan and an
  uncommitted reference/collision harness, but no measured streamed-history
  candidate. It therefore could not displace the already measured low-five
  splice as the cheapest falsifier.
- The low-five candidate keeps sign zero, snapshots denominator bits zero
  through four, clears generated signs one through three, reconstructs one
  sign at a time for replay and walkback, and uses no oracle scratch.
- No hunt, provider change, spend, submission, push, or publication occurred.

The paired harness uses the same deterministic SHAKE draw for candidate and
reference, compares the replay midpoint, inverse replay boundary, final
denominator/numerator, and all ancillas, and reports phase separately. The
short component's phase masks are diagnostic only; unchanged full-circuit
acceptance remains the sole phase authority.

## Strict logical oracle

Command:

```bash
SUB4_PP_RETAINED_PRODUCTION_PREFIX_SELFTEST=1 \
SUB4_PP_RETAINED_PRODUCTION_PREFIX_LIVE_NUMERATOR_STRESS=1 \
SUB4_PP_RETAINED_PRODUCTION_PREFIX_PRODUCTION_FAITHFUL=1 \
SUB4_PP_RETAINED_PRODUCTION_PREFIX_FIRST_BATCH_ONLY=1 \
SUB4_PP_REPLAY_FOLD_WINDOW=256 \
SUB4_PP_REPLAY_FLAG_COMPARE=256 \
SUB4_PP_ENDPOINT_FOLD_WINDOW=256 \
SUB4_PP_LEGACY_CHUNK_ORDER=1 \
SUB4_PINGPONG_UNFUSED_INVERSE=1 \
  ./target/release/build_circuit
```

Deterministic 64-lane receipt:

```text
paired_verdict=HOLD_PAIRED_LOW5
schedule=production_faithful
candidate_peak_q=1298
reference_peak_q=1295
peak_width_growth=3
candidate_ops=81102
reference_ops=81026
operation_delta=76
candidate_emitted_t=8030
reference_emitted_t=8030
emitted_t_delta=0
candidate_executed_t_total=474042
reference_executed_t_total=475052
executed_t_delta_total=-1010
continuation_mismatch=0
paired_replay_reverse_mismatch=0
candidate_classical=0
reference_classical=0
paired_final_classical_mismatch=0
candidate_ancilla=0
reference_ancilla=0
```

The strict reference and candidate both return denominator/numerator exactly.
Every paired logical boundary is equal, and no ancilla is left live. The
component-local phase masks remain nonzero and are recorded, but the prior
reference-cleanup lane already established that this short slice cannot replace
the frozen whole-circuit phase gate.

## Exact-live residual gate

Command:

```bash
SUB4_PP_RETAINED_PRODUCTION_PREFIX_SELFTEST=1 \
SUB4_PP_RETAINED_PRODUCTION_PREFIX_LIVE_NUMERATOR_STRESS=1 \
SUB4_PP_RETAINED_PRODUCTION_PREFIX_PRODUCTION_FAITHFUL=1 \
  ./target/release/build_circuit
```

Deterministic 4,096-case receipt:

```text
paired_verdict=HOLD_PAIRED_LOW5
schedule=production_faithful
candidate_peak_q=1123
reference_peak_q=1120
peak_width_growth=3
candidate_ops=52526
reference_ops=52450
operation_delta=76
candidate_emitted_t=4960
reference_emitted_t=4960
emitted_t_delta=0
candidate_executed_t_total=19773178
reference_executed_t_total=19770648
executed_t_delta_total=2530
candidate_executed_t=4827.436035
reference_executed_t=4826.818359
continuation_mismatch=0
paired_replay_reverse_mismatch=0
candidate_classical=2491
reference_classical=2491
paired_final_classical_mismatch=0
candidate_ancilla=0
reference_ancilla=0
```

The unchanged live geometry is still dirty on the arbitrary nonzero corpus,
as expected. The low-five candidate adds no logical residual: midpoint,
inverse-replay, and final candidate/reference mismatches are all zero, and
both ancilla counts are zero. A single PIP remeasurement reproduced the entire
receipt exactly, including both executed-Toffoli totals.

Exact live delta:

```text
delta_Q = +3
delta_emitted_T = 0
delta_executed_T = 2530 / 4096 = +0.61767578125
delta_ops = +76
```

At this four-round component boundary, the metric product is deliberately not
a win:

```text
candidate = 1123 * (19773178 / 4096) = 5421210.667480469
reference = 1120 * (19770648 / 4096) = 5406036.562500000
delta = +15174.104980469
```

That arithmetic blocks promotion but does not kill the fixed-state premise.
The four-round reference retains only four signs, so a five-bit payload pays a
three-qubit startup cost. The candidate's only useful claim is that its
retained state stays fixed across these rounds while the literal tape grows.
The formulas are proven only through sign three; extrapolating a production
win would be false.

## Gate-off identity

With every diagnostic gate absent:

```bash
./target/release/build_circuit
shasum -a 256 ops.bin
```

Observed:

```text
emitted operations: 12950916
88706a40300b7f019202f65a0f28e86dbfe27fda65ad5ed33b0482ff9b14b7eb  ops.bin
```

The generated stream was written only under a temporary directory and is not
retained in this worktree.

## PIP shipping audit

The paired evaluator at `2d2eeb2` was verified but is not durable production
source. It is a 1,862-line, environment-gated campaign diagnostic that imports
the historical low-five and reference harnesses, hard-codes the four-round
`6b5c82c` geometry, and has no production callsite. Keeping it at shipping
HEAD would make later source changes appear covered by a source-bound test.

The follow-up shipping commit therefore removes the evaluator and restores
`src/point_add/mod.rs` and `src/point_add/pingpong_div.rs` byte-for-byte to
`6b5c82c`. The exact evaluator remains reproducible at `2d2eeb2`; this note
is the durable result.

## Decision and next composition saddle

Overturn the old `KILL_LIVE_NUMERATOR_ABI_CLOSURE` as a low-five verdict.
The paired candidate is logically identical to its unchanged reference under
both geometries. Hold Q1123 as a bounded component receipt only.

Do not call it a Q1278-to-Q1123 production reduction. It covers four signs,
adds three qubits at that boundary, and has no full-depth decoder or
whole-circuit acceptance receipt.

The immediate saddle is:

```text
{compact 280-u/v checkpoint + fixed-scratch history reconstruction}
    -> lower pp_div_replay without round-growing retained state
```

The next complete composition must then include Teddy's exact sparse square
and symmetric multiply teardown, re-profile `pp_div_replay`,
`square_product_register`, `pp_mul_walkback`, and `pp_mul_replay`, and
meet Q <= 1182 with rounded T <= 992945 before any grind.
