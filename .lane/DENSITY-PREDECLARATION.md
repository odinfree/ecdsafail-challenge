# Q1272 selector-eviction paired H64 predeclaration

Date: 2026-08-23

## Frozen source and question

- exact starting commit:
  `14608572e84daf89397768c43ac0d812c714c3bd`;
- exact starting tree: `d56979a2d5b4ac32bb429dd5858211d3bb7eb196`;
- source provenance branch: `research/b523-q1272-selector-eviction-fable`;
- this isolated branch: `research/b523-q1272-selector-density-model`;
- source default first width breakpoint: B1=`24`;
- unchanged evaluator source SHA-256:
  `b35314bc47a5f8eecbf60459e6c76c9b43aa034eeb9b7ec3421655d74f9e890b`;
- tracked `results.tsv` protected SHA-256:
  `eea840222afd2424445550252f25795d63eb4bc3904b8c87f0213b5f22abc810`.

The question is whether the one-qubit selector eviction preserves usable
classical and phase fault density relative to its immediate Q1273 parent while
retaining its strict score headroom across a fixed 64-nonce corpus.

## Frozen streams

All variables not named below are unset.  Each row rebuilds its own operation
stream with `SUB4_PINGPONG_TAIL_NONCE` set to the committed nonce.

Q1273 parent:

- `SUB4_PP_PEAK=1273`;
- `SUB4_SQUARE_LADDER=243`;
- `SUB4_PP_FOLD_SELECTOR_EVICT` unset;
- inherited identity at nonce `81327465284`: 12,892,399 operations, operation
  SHA-256
  `f225dae80d6d81a5e1d61d9ac32b74df48ca1b40d9ff5905bb61acf66c9ceb15`,
  Q1273, full average T914207.834, channels `29/15/0`.

Q1272 candidate:

- `SUB4_PP_PEAK=1272`;
- `SUB4_SQUARE_LADDER=242`;
- `SUB4_PP_FOLD_SELECTOR_EVICT=1`;
- inherited identity at nonce `81327465284`: 12,908,488 operations, operation
  SHA-256
  `678c149f65ce00cd44caada6a534817e8b69f993913c509a8b396b6f526c22f0`,
  Q1272, full average T914727.660, channels `18/13/0`.

The corpus is exactly the inclusive range `444000000000..444000000063`, frozen
in `.lane/paired-h64.tsv`.  No nonce may be added, removed, or substituted
after either stream reveals an outcome.

## Trusted evaluator and exact-T receipt

Use the full 9,024-shot trusted evaluator for every row.  A temporary,
output-only instrumentation is allowed to:

- emit each existing classical mismatch shot index;
- emit integer `tot_tof`, integer `tot_cliff`, and `n_shots` before the normal
  failure exit;
- suppress `results.tsv` writes.

It must not change operation loading, Fiat-Shamir absorption, RNG consumption,
inputs, simulation, value comparison, phase accounting, ancilla accounting,
gate statistics, or exit status.  Freeze its source and binary hashes, restore
the evaluator source byte-for-byte before the evidence commit, and require the
protected `results.tsv` SHA before and after.

Each compact row must bind stream, nonce, operation count, full operation SHA,
Q, integer Toffoli numerator, shot denominator, derived average T, classical,
phase, ancilla, and complete classical shot list.

## Frozen gates

Require exactly 64 complete rows per stream and no structural violation:

- parent: Q1273 and 12,892,399 operations on every row;
- candidate: Q1272 and 12,908,488 operations on every row;
- both: 9,024 evaluated shots and ancilla zero on every row;
- every candidate rounded average T must be at most `919105`, the frozen
  Q1272 strict-beat ceiling at score anchor `1,169,101,620`;
- every parent rounded average T must be at most `918383`, the corresponding
  Q1273 ceiling.

The density gate is frozen before outcomes:

- candidate aggregate classical faults <= 110% of parent;
- candidate aggregate phase-garbage batches <= 110% of parent;
- report both exact ratios, the combined ratio, and per-nonce deltas whether
  the gate passes or fails.

Passing is an engineering non-inferiority result, not proof of equal zero
density and not permission to search.

## Protected b523 reuse boundary

The existing protected b523 H64 may be cited only if its on-disk raw receipt
reproduces SHA-256
`10ecb3139f4280bdf61b44a4416fc6ce301119f259f1e2a343ed283b7862b947`
and its 64 protected rows each bind the same nonce, Q1278, 12,876,472
operations, ancilla zero, and their recorded per-nonce operation SHA.  If any
identity check fails or the raw receipt is unavailable, omit the protected
comparison; do not reconstruct it from a summary.

## Model-port inventory boundary

After density adjudication, perform a read-only source/model delta inventory
between:

- the exact Q1272 selector source above;
- the B1=24 source-bound predictor at `6f6da43`;
- the Q1274 circuit-exact predictor at `b537c63`.

Name the smallest value-model, checkpoint, operation-count, and digest changes
needed for a Q1272 CPU port.  Do not implement the port, freeze or reveal a
model holdout, build CUDA, scan a nonce, contact a provider, hunt, submit, or
mutate an incumbent in this lane.

