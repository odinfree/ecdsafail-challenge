# Q1272 selector-eviction classical model port

Date: 2026-08-23

## Frozen scope

This lane starts from exact structural commit
`14608572e84daf89397768c43ac0d812c714c3bd` and may port only the generic
classical nonce predictor already qualified on the separate Q1274 control
branch.  The source circuit is the Q1272 selector-eviction candidate with:

- 12,908,488 emitted operations;
- operation SHA-256
  `678c149f65ce00cd44caada6a534817e8b69f993913c509a8b396b6f526c22f0`;
- measured peak Q1272;
- inherited diagnostic result `18/13/0` over the unchanged 9,024-shot
  evaluator.

The first model check is restricted to the already-known inherited nonce and
must predict exactly 18 classical mismatches.  It may not read, generate, or
evaluate the frozen H64 or disjoint holdout owned by the density/model lane.

## Allowed adaptation

Port `src/bin/pingpong_filter.rs` from qualified Q1274 model commit
`b537c63e38d38249de006a6082310a9c803c0c26`.  Adapt only generic constants or
state transitions required by the exact Q1272 source, including its B1=24
schedule, paired peak/square caps, and selector reconstruction.  Do not add a
nonce-specific correction, fixture table, or evaluator-derived exception.

Before any model result, bind the predictor to the candidate operation count,
operation digest, relevant source digests, and tail nonce extracted from the
artifact.  A wrong-stream negative must fail closed.

## Promotion gates

This port is implementation preparation only.  It may compile, fingerprint
the exact stream, and check the already-known inherited nonce.  Promotion to
range screening remains forbidden until the sibling lane independently:

1. passes its frozen paired H64 density gate;
2. proves complete 9,024-bit classical mismatch-set equality on H64;
3. proves the predeclared disjoint holdout equality;
4. proves Linux CPU and CUDA full-mask parity;
5. qualifies phase rejection or an unchanged trusted confirmation path; and
6. authorizes a bounded, non-overlapping canary explicitly.

Every survivor still requires the unchanged full 9,024-shot evaluator with
classical, phase, and ancilla `0/0/0`.  This lane has no provider, hunt,
submission, or public-note authority.
