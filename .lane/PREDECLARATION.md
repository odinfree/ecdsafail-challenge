# Burn re-descent: multiply-fold `sign_xor_add` rematerialization

Date: 2026-08-23. Branch: `research/burn-q1270-target0-saddle`.
Predeclared before any semantic source edit or armed candidate measurement.

## Frozen ancestor and contract

- official ancestor: `4eb93cb33bbf6a93229fe166b8d511c5e52ee253`;
- exact composed Q1271 source: `a22090374a957d29a3331d6c876ad12ff45fea31`;
- tree: `018eb52de8ab3e6337864338683821c0cbb574a2`;
- `pingpong_div.rs` SHA-256:
  `943267f11183a8f028530a0be2cebb68dd39bfbd78b4a7df52d14be50b68efa0`;
- `mod.rs` SHA-256:
  `147d6a8f0ea029b254f97bf7b50d22064114004ad6d96b06fc0fccc159740796`;
- unchanged local evaluator SHA-256:
  `b35314bc47a5f8eecbf60459e6c76c9b43aa034eeb9b7ec3421655d74f9e890b`.

The trusted local contract is exact output values, equal relative phase, and
all non-ABI scratch returned to zero. The supplied component selfchecks and
64-lane profile are the only validation surfaces in this lane. No screening,
cloud, external connection, or submission is in scope.

Protected composed measurement from the ancestor evidence:

```text
SUB4_PP_FOLD_SELECTOR_EVICT=1
SUB4_PP_EVICT_DOUBLED_OUT=1
SUB4_PP_ALIAS_TARGET0_SIGN=1
SUB4_PP_PEAK=1271
SUB4_PP_MUL_REPLAY_PEAK=1272
SUB4_SQUARE_LADDER=241
Q1271, diagnostic T915100.86, component value/phase/scratch PASS
```

The current product reference is 1,163,831,339. The strict rounded-T ceiling
is 916,402 at Q1270 and 915,681 at Q1271.

## Adjacent-diff and duplicate-family audit

The accepted `2c79d2f -> 4eb93cb` change is a four-part geometry notch:
rounds 698 -> 696, sparse width repair disabled, replay peak 1274 -> 1273,
and square ladder 244 -> 243. Existing isolated lanes already cover:

- division fused-fold selector eviction;
- multiply `doubled_out` eviction after the main add;
- target[0]/sign alias across the multiply main add;
- full split-replay composition (Q kill);
- operandless fused fold (Q lands, +161,472 emitted CCX price kill).

No reviewed lane evidence found an eviction of `sign_xor_add` after `routed`
has captured it. This predeclaration therefore names a distinct lifetime.

## One falsifiable architecture family

Name: **routed-control checkpoint**.

Inside `signed_mod_double_add_pm_fused`, the clean wire
`sign_xor_add = sign XOR add_out` is used to create
`routed = doubled_out AND sign_xor_add`. Once `routed` exists, the fold reads
`routed` only through its derived selectors and does not read
`sign_xor_add`. The two parent wires `sign` and `add_out` stay live.

Candidate lifecycle, default off behind
`SUB4_PP_EVICT_SIGN_XOR_ADD=1`:

1. create `routed` exactly as the protected path does;
2. reverse the two CX that created `sign_xor_add`, prove/release zero;
3. execute the existing selector construction and fused fold unchanged;
4. reacquire one clean wire and reconstruct `sign XOR add_out`;
5. run the existing `and_uncompute(routed, doubled_out, sign_xor_add)` and
   remaining cleanup unchanged.

Expected per call: zero CCX/CCZ/HMR/CZ delta, `+4 CX +1 R`, and exactly one
fewer live wire over the correction-fold interval. Protected mode must emit
byte-identical operations.

## Composition and saddle budget

The structural lever is tested in this fixed order:

1. protected Q1271 geometry control;
2. geometry-only descent control at `PP_PEAK=1270`,
   `MUL_REPLAY_PEAK=1271`, `SQUARE_LADDER=240`;
3. the same descent with routed-control checkpoint enabled.

This separates a true structural contribution from a geometry-only result.
One focused exact miter and one implementation attempt are authorized. If the
geometry control already reaches Q1270, the new lifetime must still lower its
standalone or owning-phase peak by exactly one to remain a structural lemma;
otherwise it is peak-neutral and killed. If the control stays Q1271, the
candidate must reach Q1270 to continue.

## Gates and terminal rules

1. Protected flag-off operation stream must reproduce byte-for-byte.
2. Focused protected-vs-rematerialized miter must cover all eight
   `(sign, add_out, doubled_out)` arms and report identical values and phase,
   zero scratch, identical Toffoli, exact `+4 CX +1 R`, and local peak -1.
3. Existing target0/sign and selector miters must still pass.
4. Full affine and product-square component selfchecks must pass value,
   phase, and scratch cleanup.
5. Complete 64-lane profile must report every owner and no allocation above
   the measured global peak.
6. `GO_Q1270` requires Q <= 1270 and diagnostic rounded T <= 916402.
7. If Q stays 1271, a fallback `GO_T` requires a clean component contract and
   a measured Toffoli reduction; this lifecycle is expected to be count-flat,
   so absent an independent exact cut it is a kill.

Generated operations, binaries, logs, evaluator rows, and temporary tools are
never committed.
