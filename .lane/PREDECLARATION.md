# Predeclaration: b523 Q1274 control predictor

Date: 2026-08-23

## Frozen source and objective

- starting commit: `b523ecf`;
- protected stream: `SUB4_PP_PEAK=1278`,
  `SUB4_SQUARE_LADDER=248`, all other architecture variables unset;
- Q1274 control stream: `SUB4_PP_PEAK=1274`,
  `SUB4_SQUARE_LADDER=244`, all other architecture variables unset;
- `SUB4_PP_BREAK_1` remains unset, so this lane does not mix in the separate
  B1=24 composition;
- inherited candidate identity: 12,935,433 operations, SHA-256
  `61a57ce6e167b64663288ade584785b26562f61ff197f6ae0c11c85ea098ee8e`,
  Q1274, T917227.881, full `14/9/0` at nonce `81327465284`.

At the frozen score anchor `1,169,101,620`, Q1274 must round to at most 917662
Toffolis.  The measured control rounds to 917228, leaving only 553,148 score
points.  Density and exact-model work therefore precede any statistical search;
no grinding is authorized by this packet.

## Bake gate

Change only the default replay peak from 1278 to 1274 and the default product
square ladder from 248 to 244.  The candidate default must reproduce exactly
12,935,433 operations and SHA-256 `61a57ce6...` at the inherited nonce.  The
explicit protected opt-out (`SUB4_PP_PEAK=1278 SUB4_SQUARE_LADDER=248`) must
reproduce b523's 12,876,472 operations and SHA-256 `4cb1787b...` byte-for-byte.
Any other circuit-source change fails the bake.

## Paired H64 density gate

The 64 fixed tail nonces are committed in `.lane/paired-h64.tsv`: the inclusive
range `444000000000..444000000063`.  For every nonce, force-rebuild and run the
unchanged full 9,024-shot trusted evaluator on both the protected and Q1274
streams.  Bind every row to its operation count and SHA.

Required structural guards:

- protected: Q1278 and 12,876,472 operations on all 64 rows;
- candidate: Q1274 and 12,935,433 operations on all 64 rows;
- ancilla-garbage count zero on every row in both streams;
- exactly 64 complete receipts per stream.

This is a bounded engineering non-inferiority gate, frozen before outcomes:

- candidate aggregate classical faults must be no more than 110% of protected;
- candidate aggregate phase-garbage batches must be no more than 110% of
  protected;
- report the exact aggregate ratios and per-nonce deltas regardless of verdict.

Passing these margins permits source-bound predictor work but does not prove
equal zero density and does not authorize a scan.  A ratio above 1.10 holds the
model port for a density diagnosis; any ancilla fault kills the control stream.

## CPU-model gate

Start with the current-source ping-pong classical model at exact b523 defaults:
rounds 700/696, replay fold53, B1=30.  Port the already-qualified generic
low53/high203 coordinate subtraction and fused reverse-subtraction cells from
`research/b523-q1276-model-qualify@3be0bf0`, without nonce, shot, expected-count,
or corpus branches.  The port must remain geometry-parameterized rather than
hard-coded to Q1274 fixture identities.

Require complete classical mismatch-shot-set equality on all Q1274 H64 rows,
not count-only equality.  Any predictor-only fault blocks scan use.  Any
underprediction is canary-only and fails exact qualification.

## Blinded disjoint32 gate

The 32 nonces in `.lane/model-disjoint-v1.tsv` are frozen before any Q1274 H64
outcome or model edit.  Each is the integer represented by the first 12 hex
digits of:

`SHA256("b523-q1274-control-model-disjoint-v1:%02d" % index)`.

Trusted-evaluator outcomes for this corpus must not be generated or inspected
until the generic correction is committed.  Then require 32/32 complete
classical shot-set equality, Q1274, 12,935,433 operations, and ancilla zero.

## Downstream holds

Linux/CUDA full-mask parity, a phase screen, and wrong-stream negatives remain
downstream of exact CPU qualification.  No range, scan, hunt, provider action,
submission, public note, incumbent mutation, or ecdsa-ops retarget is
authorized here.  Generated operations, binaries, logs, and evaluator results
stay outside Git.
