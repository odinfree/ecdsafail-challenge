# Q1271 selector + split-replay predeclaration

## Frozen inputs

- Live frontier at lane open: score `1,163,831,339`, Q1273 / rounded
  T914243, source `4eb93cb`.
- Strict Q1271 ceiling: rounded `T <= 915681`.
- Inherited composition at `b32c2d0`: selector eviction plus
  `doubled_out` eviction, `SUB4_PP_PEAK=1271`, square ladder 241.  It measured
  Q1271 / exact T915692.673 and was 12 rounded Toffolis over the ceiling.

## One new lever

The global 1271 replay budget prices both directions and the multiply
walkback.  This lane changes only multiply replay ladder selection: allow it
to select against 1272 while retaining the global 1271 budget everywhere
else.  The already-present selector and `doubled_out` lifecycle evictions must
absorb the wider cell so measured global Q remains 1271.

Frozen candidate:

```text
SUB4_PP_FOLD_SELECTOR_EVICT=1
SUB4_PP_EVICT_DOUBLED_OUT=1
SUB4_PP_PEAK=1271
SUB4_PP_MUL_REPLAY_PEAK=1272
SUB4_SQUARE_LADDER=241
```

No carry-window, selector-width, fold-window, round-count, square arithmetic,
nonce, evaluator, or phase-check modification is permitted.

## Gates

1. The new override is default-off; absent it, the inherited Q1271 operation
   stream must remain byte-identical.
2. The existing selector lifecycle selftest, full 64-lane affine selfcheck,
   and square component selfcheck must all pass with values, phase, and
   ancillas clean.
3. Allocation tracing and profile must prove every phase stays at Q1271.
4. Diagnostic rounded T must be `<= 915681`; otherwise KILL before the trusted
   evaluator.
5. If the score gate passes, run the unchanged 9,024-shot evaluator exactly
   once at the inherited nonce.  Dirty channels are a predictor handoff, not a
   valid result and not hunt authority.

## Bounds

No provider spend, fleet, range, hunt, submission, or public note.  Commit and
push source and compact evidence only; exclude `ops.bin`, generated results,
logs, and helper binaries.
