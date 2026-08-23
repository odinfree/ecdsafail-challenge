# Q1272 selector-eviction three-stream H64 gate

Predeclared: 2026-08-23, before any H64 build, candidate aggregate, exact-set
model output, or holdout result in this lane.

## Scope and current decision

`HOLD_H64 / HOLD_MODEL / HOLD_SCAN / HOLD_HUNT / HOLD_PROVIDER / HOLD_SUBMIT`

This lane measures whether the Q1272 selector-eviction architecture preserves
the fault density of both protected b523 and its immediate Q1273 parent. It
does not authorize a predictor range, nonce hunt, provider or remote action,
spend, submission, public note, source-default change, or incumbent edit.

The benchmark was reopened at 2026-08-23T07:00Z: source `b523ecf`, score
1,169,101,620. The strict rounded-T ceilings are 918,383 at Q1273 and 919,105
at Q1272. Score margin never excuses a density or exact-model failure.

## Frozen source identities

All three streams are independent Fiat-Shamir ensembles even when they use the
same numeric tail nonce. Per-nonce mismatch indices therefore are not paired
across streams.

### Protected b523 reference

- exact source commit: `b523ecf`;
- default geometry, no experimental environment flags;
- inherited artifact: 12,876,472 operations, SHA-256
  `4cb1787b181417c1e180ddf362fd7e44430ef2d422bb4184d73d7fe1924fdf7e`;
- inherited full result: Q1278/T914789.886, `0/0/0`;
- prior H64 totals on the frozen corpus below: classical 1,069, phase 848,
  ancilla 0.

The prior protected H64 may be reused only if its exact source/artifact
identity and receipt are verifiable. Known durable receipt anchors are compact
audit SHA-256
`f08e13023d9cb02990aeed7c16994b654672cd08aa894e72082331b813b28799`,
protected serial-ledger SHA-256
`c569756de2fd4ca7aacd7f900fb0624bb9a0ec4ec957f7979e2a884368c95837`,
and paired raw-receipt SHA-256
`10ecb3139f4280bdf61b44a4416fc6ce301119f259f1e2a343ed283b7862b947`.
If the underlying receipt cannot be rehashed and structurally audited, rerun
all 64 protected rows unchanged; never copy totals alone into a new receipt.

### Q1273 parent

- source/evidence parent: `e1cfd3aab6831a92cff00703a8be287e1cb92065`;
- build from the sealed candidate source commit below with
  `SUB4_PP_PEAK=1273`, `SUB4_SQUARE_LADDER=243`, and
  `SUB4_PP_FOLD_SELECTOR_EVICT` unset;
- every other knob remains at the hard-coded B1=24 source defaults;
- inherited artifact must reproduce 12,892,399 operations, SHA-256
  `f225dae80d6d81a5e1d61d9ac32b74df48ca1b40d9ff5905bb61acf66c9ceb15`;
- inherited full result: Q1273/T914207.834, `29/15/0`.

### Q1272 selector-eviction candidate

- exact sealed source/evidence commit:
  `14608572e84daf89397768c43ac0d812c714c3bd`;
- source tree: `d56979a2d5b4ac32bb429dd5858211d3bb7eb196`;
- geometry: `SUB4_PP_PEAK=1272`, `SUB4_SQUARE_LADDER=242`,
  `SUB4_PP_FOLD_SELECTOR_EVICT=1`;
- every other knob remains at the hard-coded B1=24 source defaults;
- inherited artifact: 12,908,488 operations, SHA-256
  `678c149f65ce00cd44caada6a534817e8b69f993913c509a8b396b6f526c22f0`;
- inherited full result: Q1272/T914727.660, `18/13/0`;
- circuit source hashes:
  `de5e347383a9bab4d76a2776b3bcee4bebda4fecb65beb3dd1ad4c1cbf4c1095`
  (`src/point_add/pingpong_div.rs`) and
  `3106691965fbd0002fc0dc427e07f28f30654be49b748beb08d93b30c21db490`
  (`src/point_add/mod.rs`).

Before the first H64 row, independently clean-build and reproduce all three
inherited identities above. A count, SHA, Q, T, channel, source, or environment
deviation stops the run before corpus measurement.

## Frozen H64 corpus and evaluator

Use exactly the 64 tail nonces `444000000000..444000000063`, in order, for
every stream. For each nonce:

1. force a fresh source-bound circuit build with only that stream's declared
   environment and `SUB4_PINGPONG_TAIL_NONCE`;
2. record operation count and full operation SHA-256 before evaluation;
3. run the challenge's unchanged full evaluator over all 9,024 shots;
4. record measured Q, exact average T, classical count, phase-batch count,
   ancilla-batch count, and complete classical mismatch set in a raw receipt;
5. continue through all 64 rows regardless of intermediate totals.

No missing, short, duplicated, reordered, malformed, or early-aborted row is
admitted. The unchanged evaluator source must reproduce SHA-256
`b35314bc47a5f8eecbf60459e6c76c9b43aa034eeb9b7ec3421655d74f9e890b`.
Any temporary no-write/index exposure must be a scratch copy, preserve the
operation stream, Fiat-Shamir derivation, RNG consumption, simulation, and
channel accounting, and be hashed; the unchanged evaluator remains the only
authority for the gate. Restore tracked `results.tsv` to
`eea840222afd2424445550252f25795d63eb4bc3904b8c87f0213b5f22abc810`.

Raw operations, binaries, logs, complete mismatch sets, and generated result
rows stay outside Git. Commit only source-independent compact aggregates,
receipt hashes, and durable evidence.

## Structural gates

Every Q1273 row must have 12,892,399 operations, measured Q1273, zero ancilla,
and rounded T at most 918,383. Every Q1272 row must have 12,908,488 operations,
measured Q1272, zero ancilla, and rounded T at most 919,105. The operation SHA
must be unique per nonce within each stream and deterministic on an independent
rebuild. Protected rows must reproduce their exact declared identity and prior
totals if rerun.

Any structural violation fails the affected stream. It cannot be averaged
away by the other 63 rows.

## Frozen density gates

For each stream compute aggregate classical, phase, and combined
`classical + phase` counts across all 577,536 shots, plus mean exact T and
descriptive clean-row and first-mismatch quantiles. Quantiles and numeric
per-nonce differences are not paired tests because each source SHA defines a
different ensemble.

### Non-inferiority to protected b523

Using the already-frozen protected totals and the independent-Poisson
three-sigma rule `floor(P + 3*sqrt(2P))`, both Q1273 and Q1272 must separately
meet all of:

- classical <= 1,207 from protected 1,069;
- phase <= 971 from protected 848;
- combined <= 2,102 from protected 1,917;
- ancilla exactly zero on every row.

### Q1272 versus its Q1273 parent

The comparison formula is frozen before either new total exists. Q1272 is
"not materially worse than Q1273" only if all three hold, with each allowance
floor-rounded after the Q1273 total is inserted:

```text
C1272 - C1273 <= floor(3*sqrt(2*C1273))
P1272 - P1273 <= floor(3*sqrt(2*P1273))
(C+P)1272 - (C+P)1273 <= floor(3*sqrt(2*(C+P)1273))
```

This rule cannot be amended after seeing Q1273. Report a separate strict
superiority label only if Q1272 is no higher than Q1273 in classical, phase,
and combined totals; that label does not replace non-inferiority.

### Selection

1. Carry Q1272 only to exact source-bound model qualification if it passes
   structural gates, protected non-inferiority, and all three Q1273-relative
   materiality gates.
2. Otherwise carry Q1273 only to its own model qualification if it passes the
   structural and protected gates.
3. Otherwise hold both architectures.

No branch in this rule opens a hunt.

## Frozen exact-model gates before any future hunt

The inherited B1=24 Q1278 predictor evidence is not candidate qualification.
Any Q1272 model must be freshly bound to the sealed candidate source, exact
operation count, per-nonce operation SHA, selector-eviction lifecycle, and
Q1272/ladder242 geometry. It must reject wrong-count streams and same-count,
wrong-SHA streams.

After a density pass, the next lane must predeclare and commit its model port
before opening the H64 complete mismatch sets. The classical model must then
match the unchanged evaluator's complete classical shot set exactly on all 64
H64 rows: 64/64 set equality, zero false negatives, zero false positives, and
per-cause totals from a fixed vocabulary with zero unclassified events. Phase
and ancilla remain authoritative only from the unchanged evaluator unless a
separately predeclared phase model proves exact batch-set equality.

The disjoint holdout is frozen now as every nonce
`444000100000..444000100031`, in order. Run the committed model first and the
unchanged full evaluator second on all 32; require 32/32 complete classical
set equality, exact stream count/SHA guards, Q1272, and ancilla zero. A model
that underpredicts or overpredicts even one shot is blocked from scanning.

Before any remote or GPU use, CPU/GPU implementations must also prove exact
parity on the full H64 and holdout outputs they claim to support, including two
wrong-count and two same-count/wrong-SHA rejection fixtures. Even passing all
these gates only permits a separately authorized bounded canary; it does not
itself authorize a range, hunt, provider action, or submission.

## Stop conditions

Stop and freeze evidence on the first identity, evaluator, structural, or
ancilla failure. Once a complete H64 block has started, preserve completed
receipts and finish the declared block unless evaluator integrity fails; never
adapt the corpus, threshold, source, classifier, or a fourth stream from an
intermediate result.
