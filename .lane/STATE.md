# Teddy Pender reference-cleanup re-descent on `6b5c82c`

Updated: 2026-08-22T20:39:31Z
Priority: Burn-the-House-Down campaign top priority
Status: `OVERTURN_PREVIOUS_LIVE_NUMERATOR_ABI_KILL`

## Frozen source and model

- Exact source: `6b5c82cbe723b33c296c8926876f14f1ac3307a8`.
- Branch: `research/burn-reference-cleanup-6b5c82c`.
- Protected normal-path stream: 12,950,916 operations, SHA-256
  `88706a40300b7f019202f65a0f28e86dbfe27fda65ad5ed33b0482ff9b14b7eb`.
- Model: Kimi Code (k2/k3, high effort), multi-lane agent campaign.

## Teddy Pender credit

Teddy Pender supplied the tape-removal architecture, the low-five sufficient
statistic, and the Burn-the-House-Down discipline that required us to falsify
the unchanged reference before blaming his representation. This lane is only
the bookkeeping and instrumentation needed to follow Teddy's advice honestly.

## Result

The old nonzero test at `34c1b50` did not isolate a low-five defect. On exact
live geometry, both its historical-sentinel reference and a production-faithful
reference first diverge logically at `undo_replay_round_3`. The latter is even
dirtier at the final logical ABI (`43/64` lanes), so the sentinels are not the
cause.

Widening fold/compare/endpoint windows to 256 and using the legacy chunk order
with the unfused inverse removes every replay-logical divergence and returns
both denominator and numerator exactly on all 64 lanes. Final classical and
ancilla are `0/0` for both schedules. The remaining component-local phase
residual is not a low-five receipt and cannot replace the complete accepted
source's trusted 9,024-shot `0/0/0` result.

Verdict: the previous `KILL_LIVE_NUMERATOR_ABI_CLOSURE` is overturned as a
candidate verdict. It measured the live approximate replay geometry on an
arbitrary nonzero corpus, not a clean unchanged ABI oracle. Teddy's Q1123
low-five prefix remains unpromoted and unjudged on nonzero production states.

## Next saddle

Rejudge the low-five prefix only against two paired references:

1. a strict-width logical oracle, where the unchanged replay has no logical
   inverse divergence and final classical/ancilla are `0/0`;
2. the exact live approximate geometry, where the candidate may not add a new
   fixed residual above its paired unchanged reference.

Only a competitive whole-circuit composition may advance to the unchanged full
9,024-shot gate. No nonce hunt, provider work, spend, push, publication,
submission, or candidate promotion occurred in this lane.

Evidence and commands: `.lane/TEDDY-REFERENCE-CLEANUP-6B5C82C.md`.
