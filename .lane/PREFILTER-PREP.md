# Q1272 E007 exact-model preparation audit

Date: 2026-08-23 (Europe/Zurich)

## Verdict

`PASS_GPU_PARITY / HOLD_OVERCOUNT_BOUND / NO_SCAN`

The exact E007 stream was byte-reproduced from clean committed source. A
source-bound CPU model was assembled from the previously qualified Q1272
rescale model, the measured fold55 correction, and the E007 final-y boundary
semantics. It matches all four frozen full-evaluator totals and first failures;
the inherited fixture also matches all 11 exact failing shot indices and cause
labels each failure into the existing five-way vocabulary.

Local preparation had no CUDA host. The frozen packet later passed Linux CPU
equals CUDA comb8 equals CUDA comb16 on all four fixtures and the inherited
complete set, plus both loader negatives. `PARITY-RESULT.md` records the exact
receipts. No scan, hunt, provider mutation, submission, or incumbent mutation
occurred.

## Live and source anchors

The benchmark was reopened during the audit. Live best remained score
`1,170,580,266`, Q1278/T915947, source `bdf4845`. At Q1272 the strict rounded-T
ceiling is `920267`. E007's inherited exact T is `918104.700`, but its full
result is dirty and the stream is not a candidate.

E007 identity:

- source commit: `ea93a131e2bc488bff6fa12010d1f3606c7771b0`;
- tree: `6acba67d2bc5dc64d9df11b0ddefc3f6a6c1ab83`;
- operations: `12,943,345`;
- inherited operation SHA-256:
  `4618d4af86c23c06cc72fef26f8a8e5986c7a9de5f804891541a8ce6eb189f37`;
- state digest: `963a662d2e392804`;
- Q/T/full: Q1272, T918104.700, `11/12/0`.

The digest derivation was cross-checked against the older Q1272 stream: the
same independent loader reproduced its recorded `af3009421e598669` digest.

## Exact geometry delta from Q1276 g1000

The trusted comparison packet is commit `c639abedfee8931d84fad282b6d128865b597bc4`,
candidate source `0b6ac181c46bd24ad6a5f8cd3d36b69bc040d73f`,
12,929,346 operations, SHA
`d1461959eac52b19b644f1f97a3b44a3ea249a109f14a406d19e872cd17c5422`.

| geometry | Q1276 g1000 | Q1272 E007 | predictor consequence |
|---|---:|---:|---|
| divide/multiply rounds | 698/696 | 696/696 | replace both round constants |
| width map | g1000 direct table | sampled base at `floor(r*703/695)` | replace table/index rule and retain wrapped-overflow fallback |
| R1/R2 | 356/625 | 340/628 | hash binding only; value recurrence is unchanged |
| replay peak | 1276 | 1272 | hash binding only |
| square ladder | 246 | 242 | hash binding only |
| replay chunk compare | 22 | 20 | phase-only; classical model unchanged |
| fused replay fold | low54 | low55 | change only fused divide/multiply fold mask and carry threshold |
| multiply `plus_2f` | materialized | `routed XOR minus_f` | no value delta; proven Boolean identity |
| final-y subtraction | low53 borrow dropped | exact post-low predicate and high203 decrement | add final-y-only model; leave initial x/y subtraction unchanged |

The Q/T scheduling fields still alter the operation stream and Fiat-Shamir
corpus, so they are never portable by configuration label alone. The full SHA,
count, and state digest are mandatory even where the value model has no branch.

## Smallest model changes

Starting from the Q1276 packet, the minimum safe port is:

1. import the Q1272 `696/696` rescaled width map and its wrapped-overflow path;
2. preserve the fold55 walkback loss check: a non-sign-extension bit removed
   by `shrink_to` cannot be assumed recoverable during reverse walkback;
3. change only the fused replay correction from low54 to low55;
4. add `pp_coord_sub_final_model`, calling the existing low53 subtract model
   and subtracting `2^53` iff `coord > reg` and
   `post_low53 >= 2^53 - (2^32+977)`;
5. call that function only for `tlm_coord_y_sub_final`, including the wrapped
   fallback; keep both initial coordinate subtractions untouched;
6. bind the loader to `12,943,345` plus digest `963a662d2e392804`, and require
   the full operation SHA in the launcher before either binary runs.

The retained fold55 loss check is fail-closed. It exactly repaired three H64
false negatives in the prior held stream and matches this audit's four E007
fixtures, but it may reject a rare benign wrapped overflow. The older Q1272
suite contains one such example (F5 shot 7834). Therefore this packet is safe
for bounded parity preparation, not yet a globally exact count oracle. A
production qualification must either prove that branch absent on its frozen
corpus or replace it with an exact reverse-walk restoration model.

## Frozen four-fixture calibration

The E007 inherited nonce replaces Q1276's inherited fixture; the other three
nonces are deliberately identical to the Q1276 qualification packet for a
cross-architecture comparison. All four were frozen before predictor output.

| nonce | model `walkD/replayD/walkM/replayM/result` | model total/first | unchanged full `cls/phase/anc`, first |
|---:|---:|---:|---:|
| 251000962439 | 8/0/3/0/0 | 11/2582 | 11/12/0, 2582 |
| 0 | 6/2/6/0/0 | 14/151 | 14/13/0, 151 |
| 7 | 10/2/6/1/0 | 19/90 | 19/12/0, 90 |
| 2500069332 | 4/0/8/0/0 | 12/911 | 12/9/0, 911 |

For nonce `251000962439`, CPU `faultshots` exactly reproduced the committed
E007 set:

```text
2582:1 3967:1 4145:1 4670:4 5353:1 5757:1
6422:1 7544:4 8028:4 8239:1 8443:1
```

The fixed GPU gate is CPU = CUDA comb8 = CUDA comb16 for every row, including
total, first, and all five cause counts. It must also confirm one state digest
across all eight GPU invocations and reject a wrong-count stream plus a
same-count/wrong-digest stream. This is fixture evaluation, not a range run.

## Source receipts and remaining gate

Committed packet hashes:

- `src/pp_host.h`: `ff609173d16d2cb6d3d69f81b22a1361b42772c3d58c8b83ac836222028ccbaa`;
- `src/pp_model.h`: `609d21cab5ad8dd40180f1a20311d1578b2b6d243133a0137951d3f2dddcc81d`;
- `src/ppcpu.cpp`: `47061664fa5365793e01427c0834dcbee9e01daca16981ba980b9c4f22bbc460`;
- `src/ppgpu.cu`: `bc3acb5867a477d8d50b00a997b38fcab78d92267f9e8906bba9ddff5ab28872`;
- scan-disabled `build.sh`: `349287129102bc97aec491c2e0fd6cc7470cbc9ebef64fa567770f94547b2cd7`.

The CPU/CUDA source change after local calibration is confined to bounded
`max_faults=0..3` range retention and an independent compile-time range
disable. Fixture `breakdown`, `faultshots`, shared model arithmetic, loader,
operation count, and state digest paths are unchanged. The parity build sets
`PP_DISABLE_SCAN=1`, so this source packet cannot launch a range during the
prepared fixture stage.

These hashes are pre-commit file hashes and are independently reproducible.
Generated ops, evaluator rows, binaries, logs, temporary digest tools, and
CUDA artifacts are excluded from Git. `PARITY-STAGE.md` freezes the dedicated
and unarmed incumbent-borrow receipts, four fixture rows, inherited complete
set, and two negative streams. A successful parity receipt still does not
authorize a scan. Strict predicted-zero filtering remains unsafe until a
global fail-closed overcount bound is proven; the tolerant pilot is committed
unarmed and requires `max_faults >= bound` with `bound <= 3`.
