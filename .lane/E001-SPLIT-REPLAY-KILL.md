# E001 — split multiply-replay peak: KILL_Q

## Identity control

With both new variables absent, the modified binary emitted `12,887,894`
operations and `ops.bin` SHA-256
`d21eff47434a95fe6f1036a59ddda830cf261a269b1d5eb387bde7ae7b6346b2`,
byte-identical to an independently rebuilt frozen `4eb93cb` control.

## Frozen candidate

```text
SUB4_PP_PEAK=1271
SUB4_PP_MUL_REPLAY_PEAK=1272
SUB4_PP_EVICT_DOUBLED_OUT=1
SUB4_SQUARE_LADDER=241
```

The unchanged 64-lane full affine component selfcheck exited zero with exact
values, phase zero, and clean ancillas.  It reported `956,699` emitted,
`915,224.828` executed Toffoli and **Q1272**.  The square component separately
exited zero at Q1271 / T58738.531.

`PP_PROFILE=1` reproduced the full circuit at Q1272 / diagnostic
T915251.50.  Allocation tracing shows Q1272 in both `pp_mul_replay` and
`pp_mul_walkback`.  The wider replay ladder allocates its extra wire before
the current post-add `doubled_out` loan begins, so the loan cannot pay for the
split budget.  At Q1272 the rounded score is already worse than the frozen
frontier; no 9,024-shot run can rescue the family.

## Verdict

`KILL_Q`: stop before trusted evaluation.  No nonce, provider, range, hunt,
submission, or public-note action.  A composition with the independently
validated fused selector eviction is a distinct lane and must be declared
before testing.
