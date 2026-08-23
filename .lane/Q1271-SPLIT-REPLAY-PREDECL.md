# Q1271 split replay-peak predeclaration

## Frozen frontier

- Source: `4eb93cb33bbf6a93229fe166b8d511c5e52ee253`.
- Live score at lane open: `1,163,831,339` (`Q=1273`, rounded
  `T=914243`).
- A strict Q1271 beat requires rounded `T <= 915681`.

## Single architectural family

The known Q1271 route uses one `SUB4_PP_PEAK=1271` budget for divide replay,
multiply replay, and multiply walkback.  That couples three distinct peak
sites and misses the live ceiling by only five rounded Toffolis.

This lane tests one resource-accounting split: keep divide replay and
walkback at 1271, but allow multiply replay to choose its ladder as if its
budget were 1272 while `doubled_out` is cleared, freed, and exactly
rematerialized across the fused fold.  The freed cell must pay for the extra
replay-ladder wire, so the measured global peak must remain 1271.

Default-off controls:

- `SUB4_PP_EVICT_DOUBLED_OUT=1`
- `SUB4_PP_MUL_REPLAY_PEAK=1272`

Candidate configuration:

```text
SUB4_PP_PEAK=1271
SUB4_PP_MUL_REPLAY_PEAK=1272
SUB4_PP_EVICT_DOUBLED_OUT=1
SUB4_SQUARE_LADDER=241
```

No selector-width, fused-fold-width, round-count, nonce, phase-check, or
evaluator change belongs to this family.

## Gates

1. With both new variables absent, the emitted operation stream must remain
   byte-identical to the frozen source.
2. The clear/free/rematerialize identity must pass a focused value,
   forward/inverse, relative-phase, and ancilla check before pricing.
3. The unchanged ping-pong and square component checks must pass.
4. Peak tracing must show every phase at `Q <= 1271`.
5. Rounded full-run Toffoli must be `<= 915681`; otherwise this family is a
   score KILL even if its component tests pass.
6. Exactly one unchanged 9,024-shot run at the inherited nonce is allowed
   after the preceding gates.  A dirty score-go is only a handoff; it is not
   valid and does not authorize a nonce hunt.

## Operational bounds

No provider spend, fleet, range allocation, submission, public note, or
evaluator edit.  Commit and push source plus compact evidence; never commit
`ops.bin`, helper binaries, logs, or generated results.
