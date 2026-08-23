# Q1273 replay-square predictor predeclaration

Date: 2026-08-23. Frozen before predictor source is copied, edited, built, or
run on either the inherited shot set or H64.

## Exact target and authority boundary

- structural source commit:
  `093d85d64de87aa5006a94868172f642daacf136`;
- source tree: `f6fd9d8b151a84fd886835ff3a818d3c1c9ef072`;
- inherited nonce: `100000045835813`;
- target operation count: `12,933,805`;
- inherited `ops.bin` SHA-256:
  `ee6448dbb23aa877123733724b109266e584f1ba14abf5c38b43b9ab6aa26cd1`;
- full trusted receipt: Q1273 / T917103.815 / classical-phase-ancilla
  `12/12/0`, first classical mismatch shot 93;
- trusted evaluator source SHA-256:
  `b35314bc47a5f8eecbf60459e6c76c9b43aa034eeb9b7ec3421655d74f9e890b`;
- external inherited receipt SHA-256:
  `f65aad34d8392d2c273349aa06f50beb8a8cc0a01c04892e801455081840ce17`;
- inherited evaluator log/result hashes:
  `bf93954845fcb8e13a38f108f4a7d28332ed29ce357d7f633a47794a2bf38400` /
  `dc515b01994fc32eeba8485990910972bf0bbf908ff69092515a6973d718bd64`.

This lane is CPU-only. It may build circuits, run the unchanged evaluator,
instrument a temporary evaluator solely to emit classical mismatch shot
indices, and build/run a bounded CPU predictor. It may not start a range,
scan, hunt, provider, fleet action, submission, or incumbent mutation.

## Frozen donor selection

The nearest source-semantic predictor is the Q1274 repair-r100 packet at
`research/fable-q1274-repair-qualify@a7326a9541623cdca7912bcefe88ca9a4242dd78`.
Its underlying circuit source is `fe0b7bac6348fb35b7680784d4295899e498d0e3`.
Relative to that circuit, the target changes exactly three production defaults:

1. tail nonce `251000962439 -> 100000045835813`;
2. replay peak `1274 -> 1273`;
3. square ladder `244 -> 243`.

The donor already models the identical repaired/rescaled width schedule,
divide/multiply rounds `698/696`, walk and replay channels, low-53/high-203
coordinate shell, product-register square, and result channel. Frozen donor
payload hashes:

- `pp_host.h`: `67055b7e2d43b3abfb53eae255cbc7c592f4502a7ee1c3d52e608ac3b7544b8c`;
- `pp_model.h`: `68aa572a4fd84742b258560f3629798cf65849aed461af266642bde99d05432f`;
- `ppcpu.cpp`: `f25a1d8a459810b02ce071e8bef1334f1abddac9e49dd013a8744b089b04a79a`.

Port these three files first, hard-disable the donor's range-scan mode, and
change only target identity/geometry needed by the exact circuit. Do not add a
nonce, shot, expected-count, or corpus exception. Derive the target checkpoint
state digest once from the exact bound inherited artifact before revealing a
predictor outcome, then bake it into the loader.

## Frozen corpora and mask contract

The qualification corpus is:

- inherited nonce `100000045835813`;
- H64 inclusive range `444000000000..444000000063`, committed as
  `.lane/q1273-predictor-h64.tsv`, SHA-256
  `010a0599b98bd6b1ad4a78b6e7f036dcd72aa2043a1d1bb7f5d5dd50ec85374f`.

For each nonce, force-generate the circuit from the exact target source with
only `SUB4_PINGPONG_TAIL_NONCE=<nonce>` changed. The unchanged evaluator must
observe exactly Q1273, 12,933,805 operations, 9,024 shots, and zero ancilla
garbage. Record each operation SHA and all channel counts outside Git.

The temporary trusted-evaluator instrumentation may only expose the complete
ordered set of classical mismatch shot indices and suppress result-file writes.
It must preserve the trusted source, circuit simulation, shot derivation,
counts, failure ordering, and return semantics. On the inherited stream its
Q/count/channels/first mismatch must equal the already frozen receipt before
its shot set is accepted.

The predictor's `faultshots` result is the set of all 0-based shot indices for
which its circuit-exact classical fault mask is nonzero. Qualification requires
byte-for-byte equality of that complete set with the evaluator set, not merely
equal counts:

- inherited: `1/1` set equality and exactly 12 evaluator faults;
- H64: `64/64` set equality;
- aggregate evaluator-only shots: zero;
- aggregate predictor-only shots: zero.

Any inherited discrepancy is localized by first differing shot and cause
before H64 is opened. A general source-semantic correction may be made and
committed; no fixture-specific correction is allowed. Once H64 evaluator masks
are revealed, any model mismatch is terminal for this lane: localize the first
mechanism and stop rather than tune on H64.

## Fail-closed and terminal gates

Before qualification, require:

1. inherited artifact framing, exact op count, full SHA-256, and derived
   checkpoint/tail state digest;
2. wrong-count rejection with exit 2;
3. same-count/wrong-SHA rejection with exit 2;
4. wrong-state rejection with exit 2;
5. SHAKE/corpus KATs and exact 9,024-shot output framing;
6. range/scan mode unavailable in the CPU binary.

If inherited plus H64 are exact, freeze source/binary/fixture/result hashes and
write a CUDA handoff packet containing the qualified shared model, target
identity, masks kept outside Git, comparator contract, and negatives. This
authorizes only a later isolated CUDA parity lane. If any classical channel
cannot be exact, record `HOLD_MODEL` with the first semantic divergence. In
either case, generated operations, binaries, masks, and logs remain outside
Git; only durable source, scripts, hashes, and evidence are committed.
