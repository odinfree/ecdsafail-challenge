# Q1272 predictor H64 independent audit

Updated: 2026-08-23

## Decision

`H64_EXACT_64_OF_64 / 1457_OF_1457_FAULTS / HOLD_DISJOINT`

This audit ran only after the independently frozen paired-density gate passed
and was sealed at density commit
`9e50f6e59fb25670b9e50575e2af4a33530fcc3d`.  It used the already-public H64
nonces `444000000000..444000000063`; no blinded or disjoint holdout was read.

## Bound inputs

```text
candidate source commit         14608572e84daf89397768c43ac0d812c714c3bd
predictor source commit         b3f71f7
predictor source SHA-256        b2a4d44c89b5340c7cc7d2db8a11b8cebc9207537a0f6883445d9dd85799e9b4
local release binary SHA-256    767d89df2f3385ce6da3e8bb3c510c89462a926499bbe0fc1c93f9a77115fcc4
H64 nonce-list SHA-256          f8d1cfb4d281c08f69778c7e634ebd4fc9addf2870816cc4ef2bad23800bcf57
raw 128-row density SHA-256     90a8d5c33fa62413befd337667bbe272f8bc7fe9e6e4f397df0192b2955efe9d
evaluator-log manifest SHA-256  671f85777ab23261e909ee2c2d656650ebdf812ed10e855344948900e1379330
operation manifest SHA-256      6e1963431b41539cf131384f68e50de84a1b171ce0d707e2e25fed4786e460fa
```

Exact model environment:

```text
SUB4_PP_PEAK=1272
SUB4_SQUARE_LADDER=242
SUB4_PP_FOLD_SELECTOR_EVICT=1
```

The predictor emitted one 141-word, 9,024-bit classical-fault mask for every
H64 nonce.  A read-only independent comparator rebuilt the expected mask from
each unchanged evaluator log's `EVAL_CLASSICAL_SHOT` records and compared the
complete bit string, not only its popcount.

## Result

```text
rows                 64
predictor faults     1457
evaluator faults     1457
exact masks          64/64
mask mismatches      0
```

This closes the H64 classical-model gate independently.  It does not qualify
the blinded disjoint set, Linux portability, CUDA parity, phase rejection,
range economics, a nonce hunt, or a submission.  Those gates remain fail
closed in the sibling qualification lane.
