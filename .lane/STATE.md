# Burn pp_div_replay paired re-descent

Updated: 2026-08-22
Status: `HOLD_PAIRED_LOW5`; production promotion withheld

## Frozen source

- Exact base: `6b5c82cbe723b33c296c8926876f14f1ac3307a8`.
- Branch: `research/burn-pp-div-replay-redescent-6b5c82c`.
- Protected normal path: 12,950,916 operations, SHA-256
  `88706a40300b7f019202f65a0f28e86dbfe27fda65ad5ed33b0482ff9b14b7eb`.

## Teddy Pender credit

Teddy Pender supplied the low-five sufficient statistic, the tape-removal
architecture, and the Burn-the-House-Down discipline that required a paired
reference instead of charging the incumbent's residual to the candidate.

## Result

- Candidate selected: exact low-five reconstruction for signs one through
  three; the streamed-history lane has no completed measured candidate.
- Strict 64-lane oracle: candidate/reference logical midpoint, replay reverse,
  and final deltas all zero; both final classical/ancilla `0/0`.
- Exact-live 4,096-case gate: candidate/reference midpoint, replay reverse,
  final logical, and ancilla deltas all zero despite the shared live residual.
- Exact-live cost: Q `1120 -> 1123` (+3); emitted T `4960 -> 4960`;
  deterministic executed T totals `19770648 -> 19773178`, or
  `+2530/4096 = +0.61767578125` average T; operations `+76`.
- Bounded component product worsens by `15174.104980469`, so this is a
  representation hold, not a four-round score win or a production claim.
- One PIP remeasurement reproduced the live receipt exactly.

## Next saddle

Compose a compact 280-`u/v` checkpoint with a fixed-scratch, non-growing
history reconstruction to lower `pp_div_replay`. Then combine it with Teddy
Pender's exact sparse square and the symmetric multiply teardown. Require all
co-binders below Q1182 and rounded whole-circuit T at or below 992945 before
any hunt.

Full commands, receipts, arithmetic, and shipping audit:
`.lane/TEDDY-PP-DIV-REPLAY-REDESCENT-6B5C82C.md`.
